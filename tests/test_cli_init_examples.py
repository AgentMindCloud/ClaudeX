"""Tests for ``frok init --example <NAME>`` variants."""

import json
from pathlib import Path

import pytest

from frok.cli import build_parser, main
from frok.cli.init import EXAMPLE_TEMPLATES, TEMPLATES


# ---------------------------------------------------------------------------
# parser shape
# ---------------------------------------------------------------------------
def test_parser_accepts_known_examples():
    parser = build_parser()
    ns = parser.parse_args(
        ["init", "--example", "tools", "--example", "memory"]
    )
    assert ns.example == ["tools", "memory"]


def test_parser_rejects_unknown_example_name(capsys):
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["init", "--example", "bogus"])
    err = capsys.readouterr().err
    assert "invalid choice" in err


def test_parser_defaults_example_to_empty_list():
    parser = build_parser()
    ns = parser.parse_args(["init"])
    assert ns.example == []


# ---------------------------------------------------------------------------
# scaffold composition
# ---------------------------------------------------------------------------
def test_init_without_example_matches_base_templates(tmp_path):
    target = tmp_path / "p"
    assert main(["init", str(target)]) == 0
    got = sorted(p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file())
    expected = sorted(TEMPLATES.keys())
    assert got == expected


@pytest.mark.parametrize("name", sorted(EXAMPLE_TEMPLATES.keys()))
def test_single_example_adds_matching_case_file(tmp_path, name):
    target = tmp_path / f"p-{name}"
    assert main(["init", str(target), "--example", name]) == 0
    case_file = target / "cases" / f"{name}.py"
    assert case_file.is_file()
    assert case_file.read_text(encoding="utf-8").strip() != ""
    # Base templates still written.
    for rel in TEMPLATES:
        assert (target / rel).is_file()


def test_multiple_examples_compose(tmp_path):
    target = tmp_path / "multi"
    code = main(
        [
            "init",
            str(target),
            "--example",
            "tools",
            "--example",
            "multimodal",
            "--example",
            "memory",
        ]
    )
    assert code == 0
    for name in ("tools", "multimodal", "memory"):
        assert (target / "cases" / f"{name}.py").is_file()


# ---------------------------------------------------------------------------
# existence abort still covers generated example paths
# ---------------------------------------------------------------------------
def test_existing_example_case_file_aborts_without_force(tmp_path, capsys):
    target = tmp_path / "p"
    target.mkdir()
    (target / "cases").mkdir()
    (target / "cases" / "tools.py").write_text("# custom", encoding="utf-8")

    code = main(["init", str(target), "--example", "tools"])
    assert code == 2
    err = capsys.readouterr().err
    assert "cases/tools.py" in err
    # Untouched.
    assert (target / "cases" / "tools.py").read_text(encoding="utf-8") == "# custom"


def test_force_overwrites_existing_example_file(tmp_path):
    target = tmp_path / "p"
    target.mkdir()
    (target / "cases").mkdir()
    (target / "cases" / "tools.py").write_text("# old", encoding="utf-8")
    assert (
        main(["init", str(target), "--example", "tools", "--force"]) == 0
    )
    assert (target / "cases" / "tools.py").read_text(encoding="utf-8") != "# old"


# ---------------------------------------------------------------------------
# each example runs green under `frok run`
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name", sorted(EXAMPLE_TEMPLATES.keys()))
def test_generated_example_case_runs_green(tmp_path, capsys, name):
    target = tmp_path / f"p-{name}"
    assert main(["init", str(target), "--example", name]) == 0
    capsys.readouterr()

    summary = tmp_path / f"{name}-summary.json"
    report = tmp_path / f"{name}-report.md"
    code = main(
        [
            "run",
            str(target / "cases" / f"{name}.py"),
            "-o",
            str(report),
            "--summary-json",
            str(summary),
            "--fail-on-regression",
        ]
    )
    assert code == 0, report.read_text(encoding="utf-8")
    data = json.loads(summary.read_text(encoding="utf-8"))
    assert data["passed"] == 1
    assert data["failed"] == 0


# ---------------------------------------------------------------------------
# tools example actually exercises the tool orchestrator
# ---------------------------------------------------------------------------
def test_tools_example_invokes_its_tool(tmp_path, capsys):
    target = tmp_path / "p"
    main(["init", str(target), "--example", "tools"])
    capsys.readouterr()
    summary = tmp_path / "s.json"
    main(
        [
            "run",
            str(target / "cases" / "tools.py"),
            "-o",
            str(tmp_path / "r.md"),
            "--summary-json",
            str(summary),
        ]
    )
    data = json.loads(summary.read_text(encoding="utf-8"))
    scores = data["cases"][0]["scores"]
    # The ToolCalled scorer passing proves the orchestrator ran the tool.
    assert any("tool_called" in name and passed for name, passed in scores.items())


# ---------------------------------------------------------------------------
# multimodal example sends an image_url content part over the wire
# ---------------------------------------------------------------------------
def test_multimodal_example_sends_image_content_part(tmp_path, capsys):
    target = tmp_path / "p"
    main(["init", str(target), "--example", "multimodal"])
    capsys.readouterr()
    # Run via a programmatic import to observe the stub transport's calls.
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "mm_example", target / "cases" / "multimodal.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    from frok.evals import EvalRunner
    from frok.telemetry import InMemorySink

    def factory(sink):
        return mod.make_client(None, sink)

    import asyncio

    runner = EvalRunner(client_factory=factory)
    report = asyncio.run(runner.run(mod.CASES))
    assert report.passed == 1


# ---------------------------------------------------------------------------
# memory example demonstrates both tool invocations
# ---------------------------------------------------------------------------
def test_memory_example_calls_remember_and_recall(tmp_path, capsys):
    target = tmp_path / "p"
    main(["init", str(target), "--example", "memory"])
    capsys.readouterr()
    summary = tmp_path / "s.json"
    main(
        [
            "run",
            str(target / "cases" / "memory.py"),
            "-o",
            str(tmp_path / "r.md"),
            "--summary-json",
            str(summary),
        ]
    )
    data = json.loads(summary.read_text(encoding="utf-8"))
    scores = data["cases"][0]["scores"]
    # Both ToolCalled scorers must have passed.
    called_scorers = [name for name, passed in scores.items() if "tool_called" in name and passed]
    assert len(called_scorers) == 2
