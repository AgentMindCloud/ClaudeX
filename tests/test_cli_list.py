"""Tests for ``frok run --list``."""

from pathlib import Path

from frok.cli import main


# Case file WITH a stub client — for tests that want to prove --list doesn't
# trigger the stub.
_CASE_FILE_WITH_STUB = '''
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


_transport = _StubTransport([])  # intentionally empty: any call raises IndexError


async def _noop_sleep(_s):
    return None


def make_client(config, sink):
    return GrokClient(
        api_key="sk-t",
        transport=_transport,
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(name="safety-a", messages=[GrokMessage("user", "q")],
             scorers=[AnswerContains("x")]),
    EvalCase(name="safety-b", messages=[GrokMessage("user", "q")],
             scorers=[AnswerContains("x")]),
    EvalCase(name="tool-add", messages=[GrokMessage("user", "q")],
             scorers=[AnswerContains("x")]),
]
'''

# Case file WITHOUT make_client — forces the default factory path (which would
# normally require api_key). --list must still succeed because the factory is
# never called.
_BARE_CASE_FILE = '''
from frok.clients import GrokMessage
from frok.evals import EvalCase, AnswerContains


CASES = [
    EvalCase(name="hello", messages=[GrokMessage("user", "q")],
             scorers=[AnswerContains("x")]),
    EvalCase(name="world", messages=[GrokMessage("user", "q")],
             scorers=[AnswerContains("x")]),
]
'''


def _write_case_file(tmp_path: Path, body: str, *, name: str = "cases.py") -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# basic output
# ---------------------------------------------------------------------------
def test_list_prints_one_case_per_line(tmp_path, capsys):
    case = _write_case_file(tmp_path, _CASE_FILE_WITH_STUB)
    assert main(["run", str(case), "--list"]) == 0
    out = capsys.readouterr().out
    assert out.splitlines() == ["safety-a", "safety-b", "tool-add"]
    # Trailing newline so shell pipes are well-formed.
    assert out.endswith("\n")


def test_list_preserves_case_file_order(tmp_path, capsys):
    case = _write_case_file(tmp_path, _CASE_FILE_WITH_STUB)
    main(["run", str(case), "--list"])
    assert capsys.readouterr().out.splitlines() == [
        "safety-a",
        "safety-b",
        "tool-add",
    ]


# ---------------------------------------------------------------------------
# filter / exclude interop
# ---------------------------------------------------------------------------
def test_list_honours_filter(tmp_path, capsys):
    case = _write_case_file(tmp_path, _CASE_FILE_WITH_STUB)
    main(["run", str(case), "--list", "--filter", "safety-*"])
    assert capsys.readouterr().out.splitlines() == ["safety-a", "safety-b"]


def test_list_honours_exclude(tmp_path, capsys):
    case = _write_case_file(tmp_path, _CASE_FILE_WITH_STUB)
    main(["run", str(case), "--list", "--exclude", "tool-*"])
    assert capsys.readouterr().out.splitlines() == ["safety-a", "safety-b"]


def test_list_regex_filter(tmp_path, capsys):
    case = _write_case_file(tmp_path, _CASE_FILE_WITH_STUB)
    main(["run", str(case), "--list", "--filter", "re:^tool-"])
    assert capsys.readouterr().out.splitlines() == ["tool-add"]


def test_list_zero_match_filter_still_errors(tmp_path, capsys):
    case = _write_case_file(tmp_path, _CASE_FILE_WITH_STUB)
    code = main(["run", str(case), "--list", "--filter", "nothing-*"])
    assert code == 2
    assert "no cases matched" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# output flag
# ---------------------------------------------------------------------------
def test_list_output_writes_file_and_suppresses_stdout(tmp_path, capsys):
    case = _write_case_file(tmp_path, _CASE_FILE_WITH_STUB)
    dest = tmp_path / "nested" / "cases.txt"
    assert main(["run", str(case), "--list", "-o", str(dest)]) == 0
    assert capsys.readouterr().out == ""
    assert dest.read_text(encoding="utf-8").splitlines() == [
        "safety-a",
        "safety-b",
        "tool-add",
    ]


# ---------------------------------------------------------------------------
# --list does NOT execute cases
# ---------------------------------------------------------------------------
def test_list_does_not_hit_transport(tmp_path, capsys):
    # The stub transport is intentionally empty; if --list ran a case, the
    # transport would IndexError on responses.pop(0).
    case = _write_case_file(tmp_path, _CASE_FILE_WITH_STUB)
    assert main(["run", str(case), "--list"]) == 0


def test_list_without_api_key_still_works(tmp_path, monkeypatch, capsys):
    # No make_client override → default factory would require api_key when
    # called. --list must short-circuit before the factory is invoked.
    monkeypatch.delenv("FROK_CLIENT_API_KEY", raising=False)
    case = _write_case_file(tmp_path, _BARE_CASE_FILE)
    assert main(["run", str(case), "--list"]) == 0
    assert capsys.readouterr().out.splitlines() == ["hello", "world"]


# ---------------------------------------------------------------------------
# capture interop: --list + --capture-baseline writes nothing
# ---------------------------------------------------------------------------
def test_list_with_capture_baseline_writes_no_files(tmp_path, capsys):
    case = _write_case_file(tmp_path, _CASE_FILE_WITH_STUB)
    baseline_dir = tmp_path / "b"
    assert (
        main(
            [
                "run",
                str(case),
                "--list",
                "--capture-baseline",
                str(baseline_dir),
            ]
        )
        == 0
    )
    # --list short-circuits BEFORE any per-case JsonlSink is created.
    assert not baseline_dir.exists()
    # Case names still went to stdout.
    assert capsys.readouterr().out.splitlines() == [
        "safety-a",
        "safety-b",
        "tool-add",
    ]
