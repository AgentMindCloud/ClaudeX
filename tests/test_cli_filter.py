"""Tests for ``frok run --filter`` / ``--exclude`` (glob + regex)."""

import json
from pathlib import Path

import pytest

from frok.cli import main
from frok.cli.run import filter_cases
from frok.clients import GrokMessage
from frok.evals import AnswerContains, EvalCase


# ---------------------------------------------------------------------------
# filter_cases (library-level)
# ---------------------------------------------------------------------------
def _cases(*names) -> list[EvalCase]:
    return [
        EvalCase(name=n, messages=[GrokMessage("user", "x")], scorers=[])
        for n in names
    ]


def test_no_filters_returns_all():
    cs = _cases("a", "b")
    assert filter_cases(cs) == cs


def test_glob_filter_keeps_matching():
    cs = _cases("safety-ok", "safety-bad", "tool-add")
    kept = filter_cases(cs, includes=["safety-*"])
    assert [c.name for c in kept] == ["safety-ok", "safety-bad"]


def test_glob_filter_is_case_sensitive():
    cs = _cases("Foo", "foo")
    kept = filter_cases(cs, includes=["foo"])
    assert [c.name for c in kept] == ["foo"]


def test_multiple_globs_union():
    cs = _cases("safety-a", "tool-x", "misc")
    kept = filter_cases(cs, includes=["safety-*", "tool-*"])
    assert [c.name for c in kept] == ["safety-a", "tool-x"]


def test_regex_filter_via_prefix():
    cs = _cases("tool-add", "tool-send", "safety-ok")
    kept = filter_cases(cs, includes=["re:^tool-"])
    assert [c.name for c in kept] == ["tool-add", "tool-send"]


def test_regex_partial_match_via_search():
    cs = _cases("prefix-tool-add", "unrelated")
    kept = filter_cases(cs, includes=["re:tool"])
    assert [c.name for c in kept] == ["prefix-tool-add"]


def test_exclude_drops_matches():
    cs = _cases("safety-ok", "safety-bad", "tool-x")
    kept = filter_cases(cs, excludes=["safety-bad"])
    assert [c.name for c in kept] == ["safety-ok", "tool-x"]


def test_filter_plus_exclude_intersect():
    cs = _cases("safety-ok", "safety-bad", "tool-x")
    kept = filter_cases(
        cs, includes=["safety-*"], excludes=["*-bad"]
    )
    assert [c.name for c in kept] == ["safety-ok"]


def test_invalid_regex_raises_cli_error():
    from frok.cli.common import CliError

    with pytest.raises(CliError, match="invalid regex"):
        filter_cases(_cases("a"), includes=["re:["])


# ---------------------------------------------------------------------------
# CLI end-to-end
# ---------------------------------------------------------------------------
_CASE_FILE = '''
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import EvalCase, AnswerContains
from frok.telemetry import Tracer


@dataclass
class _StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def _noop_sleep(_s):
    return None


def _final(text):
    return (
        200,
        {
            "model": "grok-4",
            "choices": [
                {
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 3},
        },
    )


def make_client(config, sink):
    # Response pool sized for the biggest run (all 3 cases).
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("42"), _final("42"), _final("42")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


def _case(name):
    return EvalCase(
        name=name,
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("42")],
    )


CASES = [
    _case("safety-prompt-injection"),
    _case("tool-add"),
    _case("tool-send"),
]
'''


def _case_file(tmp_path: Path) -> Path:
    p = tmp_path / "cases.py"
    p.write_text(_CASE_FILE, encoding="utf-8")
    return p


def _summary(tmp_path: Path, *args_after_path: str) -> dict:
    case = _case_file(tmp_path)
    summary_path = tmp_path / "s.json"
    code = main(
        [
            "run",
            str(case),
            "--summary-json",
            str(summary_path),
            "-o",
            str(tmp_path / "report.md"),
            *args_after_path,
        ]
    )
    assert code == 0
    return json.loads(summary_path.read_text(encoding="utf-8"))


def test_cli_single_glob_narrows_summary(tmp_path):
    data = _summary(tmp_path, "--filter", "tool-*")
    assert [c["case"] for c in data["cases"]] == ["tool-add", "tool-send"]
    assert data["total"] == 2


def test_cli_regex_prefix_filter(tmp_path):
    data = _summary(tmp_path, "--filter", "re:^safety-")
    assert [c["case"] for c in data["cases"]] == ["safety-prompt-injection"]


def test_cli_exclude_drops_subset(tmp_path):
    data = _summary(tmp_path, "--exclude", "tool-send")
    assert [c["case"] for c in data["cases"]] == [
        "safety-prompt-injection",
        "tool-add",
    ]


def test_cli_filter_plus_exclude(tmp_path):
    data = _summary(tmp_path, "--filter", "tool-*", "--exclude", "*-send")
    assert [c["case"] for c in data["cases"]] == ["tool-add"]


def test_cli_zero_matches_is_cli_error(tmp_path, capsys):
    case = _case_file(tmp_path)
    code = main(["run", str(case), "--filter", "nonexistent-*"])
    assert code == 2
    err = capsys.readouterr().err
    assert "no cases matched" in err
    # Available case names are surfaced so the typo is obvious.
    assert "tool-add" in err and "safety-prompt-injection" in err


def test_cli_invalid_regex_is_cli_error(tmp_path, capsys):
    case = _case_file(tmp_path)
    code = main(["run", str(case), "--filter", "re:["])
    assert code == 2
    assert "invalid regex" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# interop with --capture-baseline: only filtered cases get captures
# ---------------------------------------------------------------------------
def test_filter_limits_capture_baseline_files(tmp_path):
    case = _case_file(tmp_path)
    baseline_dir = tmp_path / "b"
    code = main(
        [
            "run",
            str(case),
            "--filter",
            "tool-*",
            "--capture-baseline",
            str(baseline_dir),
        ]
    )
    assert code == 0
    files = sorted(p.name for p in baseline_dir.iterdir())
    assert files == ["tool-add.jsonl", "tool-send.jsonl"]
