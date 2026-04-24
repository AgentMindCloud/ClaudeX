"""Tests for `diff_event_streams` + `diff_to_markdown`."""

from frok.evals import diff_event_streams, diff_to_markdown
from frok.telemetry import SPAN_END, Event


def _chat(span_id, total_tokens=10, *, ts=0.0, duration=5.0, error=None):
    return Event(
        ts=ts,
        trace_id="t1",
        span_id=span_id,
        parent_span_id=None,
        kind=SPAN_END,
        name="grok.chat",
        duration_ms=duration,
        data={"total_tokens": total_tokens},
        error=error,
    )


def _invoke(span_id, tool, *, ts=0.0, duration=1.0, error=None):
    return Event(
        ts=ts,
        trace_id="t1",
        span_id=span_id,
        parent_span_id=None,
        kind=SPAN_END,
        name="tool.invoke",
        duration_ms=duration,
        data={"tool": tool},
        error=error,
    )


# ---------------------------------------------------------------------------
# diff_event_streams
# ---------------------------------------------------------------------------
def test_identical_streams_are_clean():
    events = [_chat("a"), _invoke("b", "add", ts=1.0)]
    diff = diff_event_streams(events, list(events))
    assert diff["tool_order_match"] is True
    assert diff["a_tools"] == diff["b_tools"] == ["add"]
    assert diff["token_delta"] == 0
    assert diff["new_errors"] == 0
    assert diff["span_delta"] == 0
    assert diff["regressed"] is False


def test_tool_order_divergence_regresses():
    a = [_invoke("1", "add", ts=1.0), _invoke("2", "search", ts=2.0)]
    b = [_invoke("1", "search", ts=1.0), _invoke("2", "add", ts=2.0)]
    diff = diff_event_streams(a, b)
    assert diff["tool_order_match"] is False
    assert diff["a_tools"] == ["add", "search"]
    assert diff["b_tools"] == ["search", "add"]
    assert diff["regressed"] is True


def test_token_delta_alone_does_not_regress():
    a = [_chat("a", total_tokens=20)]
    b = [_chat("a", total_tokens=80)]
    diff = diff_event_streams(a, b)
    assert diff["tool_order_match"] is True
    assert diff["token_delta"] == 60
    assert diff["new_errors"] == 0
    assert diff["regressed"] is False


def test_new_errors_in_b_regress():
    a = [_chat("a", total_tokens=10)]
    b = [_chat("a", total_tokens=10, error="boom")]
    diff = diff_event_streams(a, b)
    assert diff["tool_order_match"] is True
    assert diff["b_errors"] == 1
    assert diff["new_errors"] == 1
    assert diff["regressed"] is True


def test_new_errors_floor_at_zero_when_b_has_fewer():
    a = [_chat("a", error="boom")]
    b = [_chat("a")]  # fewer errors than baseline — not a regression
    diff = diff_event_streams(a, b)
    assert diff["a_errors"] == 1
    assert diff["b_errors"] == 0
    assert diff["new_errors"] == 0
    assert diff["regressed"] is False


def test_custom_labels_rename_keys():
    a = [_chat("a")]
    b = [_chat("a")]
    diff = diff_event_streams(a, b, a_label="baseline", b_label="observed")
    assert "baseline_tools" in diff
    assert "observed_tools" in diff
    assert "baseline_tokens" in diff
    assert "observed_tokens" in diff
    # Neutral keys still present regardless of labels.
    assert "tool_order_match" in diff
    assert "token_delta" in diff


def test_span_count_reflects_stream_sizes():
    a = [_chat("1"), _chat("2")]
    b = [_chat("x")]
    diff = diff_event_streams(a, b)
    assert diff["a_spans"] == 2
    assert diff["b_spans"] == 1
    assert diff["span_delta"] == -1


# ---------------------------------------------------------------------------
# diff_to_markdown
# ---------------------------------------------------------------------------
def test_markdown_includes_sections_and_verdict():
    diff = diff_event_streams(
        [_invoke("1", "add", ts=1.0), _chat("c", total_tokens=10)],
        [_invoke("1", "search", ts=1.0), _chat("c", total_tokens=15)],
    )
    md = diff_to_markdown(diff, a_label="a", b_label="b", a_path="/tmp/x", b_path="/tmp/y")
    assert "# Frok Eval Diff" in md
    assert "## Tool-call order" in md
    assert "## Tokens" in md
    assert "## Errors" in md
    assert "/tmp/x" in md and "/tmp/y" in md
    assert "**yes**" in md  # regressed
    assert "+5" in md  # token delta signed


def test_markdown_renders_clean_diff():
    same = [_chat("a", total_tokens=10)]
    md = diff_to_markdown(diff_event_streams(same, same), a_path="a", b_path="b")
    assert "Regressed: no" in md
    assert "Delta" in md  # section present
