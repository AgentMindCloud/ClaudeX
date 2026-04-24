"""Tests for ``frok run`` — case-file loader, factory wiring, exit codes."""

import json
from pathlib import Path

import pytest

from frok.cli import CliError, build_parser, load_case_file, main


# ---------------------------------------------------------------------------
# helpers — write a case file on disk and invoke the CLI against it
# ---------------------------------------------------------------------------
_STUB_CLIENT_PREAMBLE = '''
import json
from dataclasses import dataclass, field

from frok.clients import GrokClient
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
'''


def _write_case_file(tmp_path: Path, body: str, *, name: str = "cases.py") -> Path:
    path = tmp_path / name
    path.write_text(_STUB_CLIENT_PREAMBLE + "\n" + body, encoding="utf-8")
    return path


def _invoke(args: list[str]) -> int:
    return main(args)


# ---------------------------------------------------------------------------
# case-file loading
# ---------------------------------------------------------------------------
def test_cases_list_and_make_client_happy_path(tmp_path, capsys):
    case = _write_case_file(
        tmp_path,
        """
from frok.clients import GrokMessage
from frok.evals import EvalCase, AnswerContains


def make_client(config, sink):
    transport = _StubTransport([_final("42 is the answer.")])
    return GrokClient(
        api_key="sk-t",
        transport=transport,
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="smoke",
        messages=[GrokMessage("user", "what is 2+40?")],
        scorers=[AnswerContains("42")],
    ),
]
""",
    )
    code = _invoke(["run", str(case)])
    assert code == 0
    out = capsys.readouterr().out
    assert "# Frok Eval Report" in out
    assert "smoke" in out
    assert "PASS" in out


def test_build_cases_callable_receives_config(tmp_path, capsys):
    case = _write_case_file(
        tmp_path,
        """
from frok.clients import GrokMessage
from frok.evals import EvalCase, AnswerContains


def make_client(config, sink):
    transport = _StubTransport([_final("hi " + config.client.model)])
    return GrokClient(
        api_key="sk-t",
        transport=transport,
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


def build_cases(config):
    return [
        EvalCase(
            name="param",
            messages=[GrokMessage("user", "go")],
            scorers=[AnswerContains(config.client.model)],
        ),
    ]
""",
    )
    code = _invoke(["run", str(case)])
    assert code == 0
    out = capsys.readouterr().out
    assert "PASS" in out


def test_missing_cases_definition_raises_cli_error(tmp_path, capsys):
    case = _write_case_file(tmp_path, "def make_client(config, sink): ...")
    code = _invoke(["run", str(case)])
    assert code == 2
    err = capsys.readouterr().err
    assert "CASES" in err and "build_cases" in err


def test_missing_case_file_is_cli_error(tmp_path, capsys):
    code = _invoke(["run", str(tmp_path / "nope.py")])
    assert code == 2
    assert "not found" in capsys.readouterr().err


def test_empty_cases_list_raises(tmp_path, capsys):
    case = _write_case_file(
        tmp_path,
        """
CASES = []
""",
    )
    code = _invoke(["run", str(case)])
    assert code == 2
    assert "zero eval cases" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# exit codes: --fail-on-regression
# ---------------------------------------------------------------------------
def test_fail_on_regression_returns_1_when_any_case_fails(tmp_path, capsys):
    case = _write_case_file(
        tmp_path,
        """
from frok.clients import GrokMessage
from frok.evals import EvalCase, AnswerContains


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("wrong answer")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="should-fail",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("42")],
    ),
]
""",
    )
    assert _invoke(["run", str(case)]) == 0  # default: always 0
    assert _invoke(["run", str(case), "--fail-on-regression"]) == 1


def test_fail_on_regression_returns_0_when_all_pass(tmp_path):
    case = _write_case_file(
        tmp_path,
        """
from frok.clients import GrokMessage
from frok.evals import EvalCase, AnswerContains


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("42")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="pass",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("42")],
    ),
]
""",
    )
    assert _invoke(["run", str(case), "--fail-on-regression"]) == 0


# ---------------------------------------------------------------------------
# output + summary-json
# ---------------------------------------------------------------------------
def test_output_flag_writes_markdown_to_file(tmp_path, capsys):
    case = _write_case_file(
        tmp_path,
        """
from frok.clients import GrokMessage
from frok.evals import EvalCase, AnswerContains


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("42")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="smoke",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("42")],
    ),
]
""",
    )
    out_path = tmp_path / "nested" / "report.md"
    code = _invoke(["run", str(case), "-o", str(out_path)])
    assert code == 0
    assert capsys.readouterr().out == ""  # stdout empty when -o is set
    assert "# Frok Eval Report" in out_path.read_text(encoding="utf-8")


def test_summary_json_is_written(tmp_path):
    case = _write_case_file(
        tmp_path,
        """
from frok.clients import GrokMessage
from frok.evals import EvalCase, AnswerContains


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_StubTransport([_final("42")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="smoke",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("42")],
    ),
]
""",
    )
    summary_path = tmp_path / "summary.json"
    code = _invoke(
        [
            "run",
            str(case),
            "-o",
            str(tmp_path / "report.md"),
            "--summary-json",
            str(summary_path),
        ]
    )
    assert code == 0
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["passed"] == 1
    assert data["failed"] == 0
    assert data["cases"][0]["case"] == "smoke"


# ---------------------------------------------------------------------------
# default client factory — no make_client in the case file
# ---------------------------------------------------------------------------
def test_default_client_factory_requires_api_key(tmp_path, capsys, monkeypatch):
    case = _write_case_file(
        tmp_path,
        """
from frok.clients import GrokMessage
from frok.evals import EvalCase, AnswerContains


CASES = [
    EvalCase(
        name="smoke",
        messages=[GrokMessage("user", "q")],
        scorers=[AnswerContains("x")],
    ),
]
""",
    )
    monkeypatch.delenv("FROK_CLIENT_API_KEY", raising=False)
    code = _invoke(["run", str(case)])
    assert code == 2
    assert "api_key" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# parser contract
# ---------------------------------------------------------------------------
def test_build_parser_requires_subcommand():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_run_subcommand_args_shape():
    parser = build_parser()
    ns = parser.parse_args(
        [
            "run",
            "cases.py",
            "-c",
            "/tmp/conf.json",
            "-p",
            "prod",
            "-o",
            "/tmp/r.md",
            "--summary-json",
            "/tmp/s.json",
            "--fail-on-regression",
        ]
    )
    assert ns.command == "run"
    assert ns.case_file == Path("cases.py")
    assert ns.config == Path("/tmp/conf.json")
    assert ns.profile == "prod"
    assert ns.output == Path("/tmp/r.md")
    assert ns.summary_json == Path("/tmp/s.json")
    assert ns.fail_on_regression is True
