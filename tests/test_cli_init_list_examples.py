"""Tests for ``frok init --list-examples``."""

import ast
from pathlib import Path

import pytest

from frok.cli import build_parser, main
from frok.cli.init import (
    EXAMPLE_TEMPLATES,
    TEMPLATES,
    _example_summary,
    format_examples_list,
)


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------
def test_parser_list_examples_flag():
    parser = build_parser()
    ns = parser.parse_args(["init", "--list-examples"])
    assert ns.list_examples is True


def test_parser_list_examples_defaults_false():
    parser = build_parser()
    ns = parser.parse_args(["init"])
    assert ns.list_examples is False


# ---------------------------------------------------------------------------
# format_examples_list helper
# ---------------------------------------------------------------------------
def test_format_examples_list_includes_every_name():
    out = format_examples_list()
    for name in EXAMPLE_TEMPLATES:
        assert name in out


def test_format_examples_list_descriptions_match_docstrings():
    out = format_examples_list()
    for name, src in EXAMPLE_TEMPLATES.items():
        expected = ast.get_docstring(ast.parse(src)).strip().split("\n", 1)[0].strip()
        # Name and description both present on the same line.
        lines = [line for line in out.splitlines() if line.startswith(name)]
        assert lines, f"no line starts with {name}"
        assert expected in lines[0]


def test_format_examples_list_is_sorted_alphabetically():
    out = format_examples_list().splitlines()
    names_in_output = [line.split()[0] for line in out]
    assert names_in_output == sorted(EXAMPLE_TEMPLATES.keys())


def test_example_summary_parses_docstring_first_line():
    src = '"""First line.\n\nBody goes here.\n"""\n\nx = 1\n'
    assert _example_summary(src) == "First line."


def test_example_summary_handles_missing_docstring():
    assert _example_summary("x = 1\n") == ""


def test_example_summary_handles_syntax_error():
    assert _example_summary("def ???:") == ""


# ---------------------------------------------------------------------------
# CLI end-to-end
# ---------------------------------------------------------------------------
def test_cli_list_examples_prints_expected_output(capsys):
    assert main(["init", "--list-examples"]) == 0
    out = capsys.readouterr().out
    assert out == format_examples_list()


def test_cli_list_examples_writes_no_files(tmp_path, capsys):
    # Run inside an otherwise-empty target directory and verify nothing
    # landed on disk.
    assert (
        main(["init", str(tmp_path / "p"), "--list-examples"]) == 0
    )
    assert list(tmp_path.iterdir()) == []  # nothing created at all
    capsys.readouterr()  # drop stdout


def test_cli_list_examples_short_circuits_other_flags(tmp_path, capsys):
    # --example is ignored when --list-examples is set; no files written.
    code = main(
        [
            "init",
            str(tmp_path / "p"),
            "--example",
            "tools",
            "--example",
            "memory",
            "--force",
            "--list-examples",
        ]
    )
    assert code == 0
    assert list(tmp_path.iterdir()) == []
    out = capsys.readouterr().out
    # Still prints every example name.
    for name in EXAMPLE_TEMPLATES:
        assert name in out


def test_cli_list_examples_leaves_existing_files_untouched(tmp_path, capsys):
    target = tmp_path / "p"
    target.mkdir()
    (target / "CLAUDE.md").write_text("# mine", encoding="utf-8")

    assert main(["init", str(target), "--list-examples"]) == 0
    # Original file preserved.
    assert (target / "CLAUDE.md").read_text(encoding="utf-8") == "# mine"
    # No scaffolded file appeared.
    for rel in TEMPLATES:
        if rel == "CLAUDE.md":
            continue
        assert not (target / rel).exists()
