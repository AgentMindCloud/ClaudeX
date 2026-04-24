"""Tests for the root ``frok --help`` UX polish."""

import argparse

import pytest

from frok.cli import build_parser


def _help_text() -> str:
    return build_parser().format_help()


# ---------------------------------------------------------------------------
# description: points operators at the onboarding triple
# ---------------------------------------------------------------------------
def test_description_identifies_frok_and_ecosystem():
    out = _help_text()
    assert "Super AI Frok" in out
    assert "xAI/Grok" in out


def test_description_lists_onboarding_triple():
    out = _help_text()
    assert "frok init" in out
    assert "frok doctor" in out
    assert "frok run" in out
    # And labels them as the intro path, not just any commands.
    assert "onboarding triple" in out


# ---------------------------------------------------------------------------
# epilog: actionable one-liners + version reporter
# ---------------------------------------------------------------------------
def test_epilog_includes_quick_start_and_everyday_ops():
    out = _help_text()
    assert "Quick start" in out
    assert "frok init && frok run" in out
    assert "frok config show" in out
    assert "frok trace inspect" in out
    assert "frok eval diff" in out


def test_epilog_mentions_version_for_bug_reports():
    out = _help_text()
    assert "frok version" in out
    assert "bug" in out.lower()


# ---------------------------------------------------------------------------
# formatter preserves multi-line description + epilog layout
# ---------------------------------------------------------------------------
def test_formatter_preserves_newlines_in_description():
    # The description contains a blank line + bulleted commands; a default
    # HelpFormatter would collapse them. Raw formatter keeps them intact.
    out = _help_text()
    assert "\n  frok init       scaffold" in out
    assert "\n  frok doctor     verify" in out


# ---------------------------------------------------------------------------
# subcommand ordering: init/doctor/run before the advanced ops
# ---------------------------------------------------------------------------
def test_subcommand_order_puts_onboarding_first():
    out = _help_text()

    def _at(name: str) -> int:
        # Match on the subparser's name followed by at least one space
        # and its help text — distinguishes it from the same word appearing
        # in the description or epilog.
        marker_a = f"\n    {name:<10}"
        marker_b = f"\n    {name} "
        idx = out.find(marker_a)
        if idx < 0:
            idx = out.find(marker_b)
        assert idx >= 0, f"subcommand {name!r} not found in help"
        return idx

    order = [_at(n) for n in (
        "init", "doctor", "run", "config", "eval", "trace", "version"
    )]
    assert order == sorted(order), f"help order broke: {order}"


def test_version_is_last_subcommand():
    out = _help_text()
    # All other subcommands should appear before `version` in the listing.
    for name in ("init", "doctor", "run", "config", "eval", "trace"):
        assert out.index(f"    {name}") < out.index("    version")


# ---------------------------------------------------------------------------
# regression: parsing + help semantics intact
# ---------------------------------------------------------------------------
def test_parser_still_requires_a_subcommand():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_parser_uses_raw_description_formatter():
    # Lock the formatter choice in — default HelpFormatter would silently
    # undo our multi-line layout, so regressing this matters.
    parser = build_parser()
    assert parser.formatter_class is argparse.RawDescriptionHelpFormatter
