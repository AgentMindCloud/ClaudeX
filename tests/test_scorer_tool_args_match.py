"""Tests for the ``ToolArgsMatch`` scorer."""

import re

import pytest

from frok.clients.grok import GrokResponse
from frok.evals import Observation, ToolArgsMatch
from frok.tools.orchestrator import ToolInvocation


def _inv(name: str, **args) -> ToolInvocation:
    return ToolInvocation(call_id="c", name=name, arguments=dict(args), result="r")


def _obs(*invocations: ToolInvocation) -> Observation:
    return Observation(
        final_response=GrokResponse(model="grok-4", content="", raw={}),
        messages=[],
        invocations=list(invocations),
        events=[],
    )


# ---------------------------------------------------------------------------
# field-specific matching
# ---------------------------------------------------------------------------
def test_field_match_passes_when_value_matches_regex():
    score = ToolArgsMatch("search", regex=r"frok", field="query")(
        None, _obs(_inv("search", query="tell me about frok"))
    )
    assert score.passed is True
    assert "frok" in score.measure  # actual haystack returned as measure


def test_field_match_fails_when_value_does_not_match():
    score = ToolArgsMatch("search", regex=r"missing", field="query")(
        None, _obs(_inv("search", query="some other query"))
    )
    assert score.passed is False
    assert "some other query" in score.detail
    assert "'missing'" in score.detail


def test_field_match_missing_field_reports_placeholder():
    score = ToolArgsMatch("search", regex=r".+", field="query")(
        None, _obs(_inv("search", other="ignored"))
    )
    assert score.passed is False
    assert "<missing>" in score.detail


def test_field_match_stringifies_non_string_values():
    # Integer / list fields — str() them before regex.
    score = ToolArgsMatch("add", regex=r"^42$", field="b")(
        None, _obs(_inv("add", a=1, b=42))
    )
    assert score.passed is True
    score = ToolArgsMatch("add", regex=r"42", field="items")(
        None, _obs(_inv("add", items=[1, 42, 3]))
    )
    assert score.passed is True


# ---------------------------------------------------------------------------
# whole-args matching (field=None)
# ---------------------------------------------------------------------------
def test_whole_args_match_anywhere_in_json():
    score = ToolArgsMatch("search", regex=r"frok")(
        None, _obs(_inv("search", query="what is frok", limit=5))
    )
    assert score.passed is True
    # Measure carries the JSON-encoded args.
    assert "frok" in score.measure


def test_whole_args_match_respects_sort_keys():
    # JSON is sorted, so a regex can safely anchor on key ordering.
    score = ToolArgsMatch("search", regex=r'^\{"a": 1, "b": 2\}$')(
        None, _obs(_inv("search", b=2, a=1))
    )
    assert score.passed is True


# ---------------------------------------------------------------------------
# tool-not-invoked
# ---------------------------------------------------------------------------
def test_tool_not_invoked_fails_cleanly():
    score = ToolArgsMatch("search", regex=r".")(
        None, _obs(_inv("other", query="x"))
    )
    assert score.passed is False
    assert "'search' not invoked" in score.detail


# ---------------------------------------------------------------------------
# multiple invocations: only one needs to match
# ---------------------------------------------------------------------------
def test_multi_invocation_any_match_wins():
    score = ToolArgsMatch("search", regex=r"yes", field="query")(
        None,
        _obs(
            _inv("search", query="no match here"),
            _inv("search", query="say yes to frok"),
            _inv("search", query="another no"),
        ),
    )
    assert score.passed is True


def test_multi_invocation_no_match_shows_all_seen():
    score = ToolArgsMatch("search", regex=r"xyz", field="query")(
        None,
        _obs(
            _inv("search", query="alpha"),
            _inv("search", query="beta"),
        ),
    )
    assert score.passed is False
    assert "alpha" in score.detail
    assert "beta" in score.detail


# ---------------------------------------------------------------------------
# flags (case-insensitive etc)
# ---------------------------------------------------------------------------
def test_case_insensitive_via_flags():
    score = ToolArgsMatch(
        "search", regex=r"FROK", field="query", flags=re.IGNORECASE
    )(None, _obs(_inv("search", query="tell me about frok")))
    assert score.passed is True

    score = ToolArgsMatch("search", regex=r"FROK", field="query")(
        None, _obs(_inv("search", query="tell me about frok"))
    )
    assert score.passed is False  # case-sensitive by default


# ---------------------------------------------------------------------------
# anchored regex
# ---------------------------------------------------------------------------
def test_anchored_regex_via_re_search():
    # re.search doesn't auto-anchor; operators opt in with ^ / $.
    score = ToolArgsMatch("search", regex=r"^exact$", field="query")(
        None, _obs(_inv("search", query="exact"))
    )
    assert score.passed is True
    score = ToolArgsMatch("search", regex=r"^exact$", field="query")(
        None, _obs(_inv("search", query="not exact"))
    )
    assert score.passed is False


# ---------------------------------------------------------------------------
# invalid regex
# ---------------------------------------------------------------------------
def test_invalid_regex_fails_cleanly_not_raises():
    score = ToolArgsMatch("search", regex=r"[", field="query")(
        None, _obs(_inv("search", query="x"))
    )
    assert score.passed is False
    assert "invalid regex" in score.detail
    assert "'['" in score.detail


# ---------------------------------------------------------------------------
# scorer name carries identifying info for aggregate reports
# ---------------------------------------------------------------------------
def test_scorer_name_includes_tool_name_and_field():
    score = ToolArgsMatch("search", regex=r"x", field="query")(
        None, _obs(_inv("search", query="x"))
    )
    assert "tool_args_match" in score.name
    assert "search" in score.name
    assert "query" in score.name


def test_scorer_name_omits_field_when_matching_whole_args():
    score = ToolArgsMatch("search", regex=r"x")(
        None, _obs(_inv("search", query="x"))
    )
    assert "tool_args_match" in score.name
    # No field colon when field=None.
    assert ":" not in score.name
