"""Tests for ``frok run --capture-baseline`` + ``--use-baseline``."""

import json
from pathlib import Path

import pytest

from frok.cli import main
from frok.cli.run import case_slug
from frok.telemetry import SPAN_END, read_jsonl


# ---------------------------------------------------------------------------
# helpers — case file that always answers "42" under a stub transport
# ---------------------------------------------------------------------------
_CASE_FILE_TEMPLATE = '''
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


def _final(text, *, prompt=5, completion=3):
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
            "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
        },
    )


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("$ANSWER")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="$CASE_NAME",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("$ANSWER")],
    ),
]
'''


def _write_case_file(
    tmp_path: Path,
    *,
    case_name: str = "smoke",
    answer: str = "42",
    name: str = "cases.py",
) -> Path:
    path = tmp_path / name
    body = _CASE_FILE_TEMPLATE.replace("$CASE_NAME", case_name).replace("$ANSWER", answer)
    path.write_text(body, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# case_slug helper
# ---------------------------------------------------------------------------
def test_case_slug_keeps_alnum_and_dash_underscore_dot():
    assert case_slug("foo-bar_baz.txt") == "foo-bar_baz.txt"


def test_case_slug_replaces_spaces_and_symbols_with_underscore():
    assert case_slug("hello world!?") == "hello_world"
    assert case_slug("tool: search/grok") == "tool_search_grok"


def test_case_slug_empty_or_all_symbols_falls_back():
    assert case_slug("") == "case"
    assert case_slug("???") == "case"


# ---------------------------------------------------------------------------
# --capture-baseline writes per-case JsonlSink files
# ---------------------------------------------------------------------------
def test_capture_baseline_creates_directory_and_writes_file(tmp_path):
    case = _write_case_file(tmp_path, case_name="smoke")
    baseline_dir = tmp_path / "new" / "baselines"
    assert not baseline_dir.exists()
    assert main(["run", str(case), "--capture-baseline", str(baseline_dir)]) == 0
    assert baseline_dir.is_dir()
    captured = baseline_dir / "smoke.jsonl"
    assert captured.exists()
    events = list(read_jsonl(captured))
    # Expect at least one grok.chat end span in the capture.
    span_ends = [e for e in events if e.kind == SPAN_END]
    assert any(e.name == "grok.chat" for e in span_ends)


def test_capture_baseline_slugs_unsafe_case_names(tmp_path):
    case = _write_case_file(tmp_path, case_name="hello world!")
    baseline_dir = tmp_path / "baselines"
    assert main(["run", str(case), "--capture-baseline", str(baseline_dir)]) == 0
    assert (baseline_dir / "hello_world.jsonl").exists()


def test_capture_baseline_rejects_collisions(tmp_path, capsys):
    path = tmp_path / "cases.py"
    path.write_text(
        _CASE_FILE_TEMPLATE.replace("$ANSWER", "42").replace(
            "CASES = [",
            "CASES = [\n"
            "    EvalCase(name='a!', messages=[GrokMessage('user', 'q')],\n"
            "             scorers=[AnswerContains('42')]),\n"
            "    EvalCase(name='a?', messages=[GrokMessage('user', 'q')],\n"
            "             scorers=[AnswerContains('42')]),",
        ).replace("$CASE_NAME", "unused"),
        encoding="utf-8",
    )
    # Give the stub transport enough responses for both cases.
    text = path.read_text(encoding="utf-8").replace(
        "_StubTransport([_final(\"42\")])",
        "_StubTransport([_final(\"42\"), _final(\"42\")])",
    )
    path.write_text(text, encoding="utf-8")
    code = main(["run", str(path), "--capture-baseline", str(tmp_path / "b")])
    assert code == 2
    assert "collide" in capsys.readouterr().err


def test_capture_baseline_does_not_disturb_normal_report(tmp_path, capsys):
    case = _write_case_file(tmp_path)
    baseline_dir = tmp_path / "b"
    assert main(["run", str(case), "--capture-baseline", str(baseline_dir)]) == 0
    out = capsys.readouterr().out
    assert "PASS" in out
    assert "# Frok Eval Report" in out


# ---------------------------------------------------------------------------
# --use-baseline attaches matching files to cases without a baseline
# ---------------------------------------------------------------------------
def test_use_baseline_attaches_matching_file(tmp_path, capsys):
    # 1. Capture.
    case = _write_case_file(tmp_path, case_name="smoke")
    baseline_dir = tmp_path / "b"
    assert main(["run", str(case), "--capture-baseline", str(baseline_dir)]) == 0

    # 2. Re-run with --use-baseline; the same case should now carry its
    #    baseline path, and the summary should include a baseline_diff.
    summary_path = tmp_path / "summary.json"
    case2 = _write_case_file(tmp_path, case_name="smoke", name="cases2.py")
    assert (
        main(
            [
                "run",
                str(case2),
                "--use-baseline",
                str(baseline_dir),
                "--summary-json",
                str(summary_path),
            ]
        )
        == 0
    )
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    diff = data["cases"][0]["baseline_diff"]
    assert diff is not None
    assert diff["regressed"] is False
    # baseline path stored in the summary should match the captured file.
    assert Path(diff["path"]).name == "smoke.jsonl"


def test_use_baseline_leaves_cases_without_matching_file_untouched(tmp_path, capsys):
    case = _write_case_file(tmp_path, case_name="orphan")
    baseline_dir = tmp_path / "b"
    baseline_dir.mkdir()  # empty
    summary_path = tmp_path / "s.json"
    assert (
        main(
            [
                "run",
                str(case),
                "--use-baseline",
                str(baseline_dir),
                "--summary-json",
                str(summary_path),
            ]
        )
        == 0
    )
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["cases"][0]["baseline_diff"] is None


def test_use_baseline_requires_existing_directory(tmp_path, capsys):
    case = _write_case_file(tmp_path)
    code = main(
        ["run", str(case), "--use-baseline", str(tmp_path / "does-not-exist")]
    )
    assert code == 2
    assert "not a directory" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# capture + use together — regression surfaces when answer changes
# ---------------------------------------------------------------------------
def test_capture_then_use_detects_answer_regression(tmp_path, capsys):
    # Capture a baseline where the model answers "42".
    case_ok = _write_case_file(tmp_path, case_name="arith", answer="42", name="ok.py")
    baseline_dir = tmp_path / "b"
    assert (
        main(["run", str(case_ok), "--capture-baseline", str(baseline_dir)])
        == 0
    )

    # Re-run with a case file that now makes the wrong scorer: answer is
    # still "42" but the scorer expects "43". The case itself fails,
    # and with --fail-on-regression we get exit 1.
    bad_path = tmp_path / "bad.py"
    bad_path.write_text(
        _CASE_FILE_TEMPLATE.replace("$CASE_NAME", "arith")
        .replace("AnswerContains(\"$ANSWER\")", 'AnswerContains("43")')
        .replace("$ANSWER", "42"),
        encoding="utf-8",
    )
    code = main(
        [
            "run",
            str(bad_path),
            "--use-baseline",
            str(baseline_dir),
            "--fail-on-regression",
        ]
    )
    assert code == 1
