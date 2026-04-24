import pytest

from frok.team import (
    Role,
    TeamError,
    TeamMessage,
    TeamRuntime,
    callback_router,
    echo_role,
    loop_until,
    pipeline_router,
)
from frok.telemetry import InMemorySink, Tracer


def _terminate(reply, transcript):
    return None


def _initial(to: str, content: str = "go") -> TeamMessage:
    return TeamMessage(from_="user", to=to, content=content)


def _make(roles, router, *, sink=None, max_hops=20):
    tracer = Tracer(sink=sink) if sink is not None else Tracer()
    return TeamRuntime(
        roles={r.name: r for r in roles},
        router=router,
        tracer=tracer,
        max_hops=max_hops,
    )


# ---------------------------------------------------------------------------
# single-role termination
# ---------------------------------------------------------------------------
async def test_single_role_terminates_after_one_hop():
    runtime = _make([echo_role("bot")], _terminate)
    run = await runtime.run(_initial("bot", "hello"))
    assert run.hops == 1
    assert run.terminated == "router"
    assert run.final.from_ == "bot"
    assert run.final.content == "hello"
    assert len(run.transcript) == 2  # initial + reply


async def test_unknown_initial_role_raises_before_any_hop():
    runtime = _make([echo_role("bot")], _terminate)
    with pytest.raises(TeamError, match="unknown role"):
        await runtime.run(_initial("ghost"))


# ---------------------------------------------------------------------------
# pipeline routing
# ---------------------------------------------------------------------------
async def test_pipeline_router_walks_each_role_once():
    seen = []

    def tap(tag: str) -> Role:
        async def respond(transcript):
            seen.append(tag)
            return f"{tag}({transcript[-1].content})"

        return Role(name=tag, respond=respond)

    runtime = _make(
        [tap("a"), tap("b"), tap("c")],
        pipeline_router(["a", "b", "c"]),
    )
    run = await runtime.run(_initial("a", "seed"))
    assert seen == ["a", "b", "c"]
    assert run.hops == 3
    # Final content is the composition c(b(a(seed)))
    assert run.final.content == "c(b(a(seed)))"
    assert run.terminated == "router"


async def test_pipeline_router_rejects_empty_sequence():
    with pytest.raises(ValueError):
        pipeline_router([])


# ---------------------------------------------------------------------------
# loop_until + supervisor-style callback
# ---------------------------------------------------------------------------
async def test_loop_until_stops_when_predicate_matches():
    counter = {"n": 0}

    async def respond(transcript):
        counter["n"] += 1
        return "DONE" if counter["n"] >= 3 else "keep going"

    role = Role(name="worker", respond=respond)
    runtime = _make([role], loop_until(lambda r: "DONE" in r.content, next_="worker"))
    run = await runtime.run(_initial("worker", "start"))
    assert run.hops == 3
    assert "DONE" in run.final.content


async def test_loop_until_caps_rounds_when_predicate_never_fires():
    async def respond(transcript):
        return "nope"

    role = Role(name="worker", respond=respond)
    router = loop_until(lambda r: False, next_="worker", max_rounds=4)
    runtime = _make([role], router)
    run = await runtime.run(_initial("worker", "go"))
    assert run.hops == 4


async def test_callback_router_can_branch_between_roles():
    def supervisor(reply, transcript):
        # `transcript` at this point holds the initial plus all prior replies
        # but not this hop's reply. Terminate after the third reply lands.
        if len(transcript) >= 3:  # initial + 2 prior replies already
            return None
        return "b" if reply.from_ == "a" else "a"

    runtime = _make(
        [echo_role("a", prefix="A:"), echo_role("b", prefix="B:")],
        callback_router(supervisor),
    )
    run = await runtime.run(_initial("a", "seed"))
    # Pattern: user -> a -> b -> a (terminal)
    assert [m.from_ for m in run.transcript] == ["user", "a", "b", "a"]
    assert run.final.from_ == "a"
    assert run.final.to == "user"


# ---------------------------------------------------------------------------
# max_hops guard
# ---------------------------------------------------------------------------
async def test_max_hops_raises_teamerror():
    runtime = _make(
        [echo_role("w")],
        callback_router(lambda r, t: "w"),  # never terminates
        max_hops=5,
    )
    with pytest.raises(TeamError, match="max_hops=5"):
        await runtime.run(_initial("w"))


# ---------------------------------------------------------------------------
# telemetry: team.run wraps per-hop team.hop spans, shared trace_id
# ---------------------------------------------------------------------------
async def test_telemetry_emits_run_and_hop_spans():
    sink = InMemorySink()
    runtime = _make(
        [echo_role("a"), echo_role("b")],
        pipeline_router(["a", "b"]),
        sink=sink,
    )
    run = await runtime.run(_initial("a", "hello"))
    assert run.hops == 2

    run_spans = sink.spans(name="team.run")
    hop_spans = sink.spans(name="team.hop")
    assert len(run_spans) == 1
    assert len(hop_spans) == 2

    run_span = run_spans[0]
    assert run_span.data["team_size"] == 2
    assert run_span.data["hops"] == 2
    assert run_span.data["terminated"] == "router"

    # All hops are children of the run span and share its trace_id.
    for hop in hop_spans:
        assert hop.trace_id == run_span.trace_id
        assert hop.parent_span_id == run_span.span_id

    hop_roles = [h.data["role"] for h in hop_spans]
    assert hop_roles == ["a", "b"]
    assert all(h.data["reply_len"] > 0 for h in hop_spans)


async def test_telemetry_records_max_hops_on_failure():
    sink = InMemorySink()
    runtime = _make(
        [echo_role("w")],
        callback_router(lambda r, t: "w"),
        sink=sink,
        max_hops=3,
    )
    with pytest.raises(TeamError):
        await runtime.run(_initial("w"))
    run_span = sink.spans(name="team.run")[0]
    assert run_span.data["terminated"] == "max_hops"
    assert run_span.error is not None


# ---------------------------------------------------------------------------
# role sees only transcript addressed to it (or "all")
# ---------------------------------------------------------------------------
async def test_role_sees_only_messages_addressed_to_it():
    captured = {}

    async def respond(transcript):
        captured["received"] = [m.content for m in transcript]
        return "done"

    role = Role(name="observer", respond=respond)
    runtime = _make([role], _terminate)

    # Pre-seed a transcript-ish initial: this happens inside the run, but we
    # can verify by running a single hop and inspecting what the role saw.
    await runtime.run(TeamMessage(from_="user", to="observer", content="hello"))
    assert captured["received"] == ["hello"]
