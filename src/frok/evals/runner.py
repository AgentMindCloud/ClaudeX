"""Runs `EvalCase`s through a candidate `GrokClient`.

Each case gets a fresh `InMemorySink` via the user-supplied factory, so
runs are independent and evaluable in isolation. The runner always
installs the sink on the client's tracer before dispatching, then
collects the full event stream into an `Observation` for the scorers.

Streaming: pass ``stream_sink=callable`` to forward each content delta
as it arrives (used by ``frok run --stream``). Streaming is honoured
only on cases without tools — the orchestrator loop is its own beast.
Tools-enabled cases silently fall back to the non-stream path so
callers can pass ``stream_sink`` unconditionally.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Callable, Sequence

from ..clients.grok import GrokClient, GrokMessage, GrokResponse
from ..telemetry import InMemorySink
from ..tools.orchestrator import ToolOrchestrator
from ..tools.registry import ToolRegistry
from .baseline import diff_against_baseline
from .case import (
    EvalCase,
    EvalReport,
    EvalResult,
    Observation,
    Score,
)

ClientFactory = Callable[[InMemorySink], GrokClient]
StreamSink = Callable[[str], None]


@dataclass
class EvalRunner:
    client_factory: ClientFactory

    async def run(
        self, cases: Sequence[EvalCase], *, repeats: int = 1
    ) -> EvalReport:
        if repeats < 1:
            raise ValueError(f"repeats must be >= 1, got {repeats}")
        results: list[EvalResult] = []
        for case in cases:
            for i in range(repeats):
                result = await self.run_case(case, repeat=i, repeats=repeats)
                results.append(result)
        return EvalReport(results=results)

    async def run_case(
        self,
        case: EvalCase,
        *,
        repeat: int = 0,
        repeats: int = 1,
        stream_sink: StreamSink | None = None,
    ) -> EvalResult:
        sink = InMemorySink()
        client = self.client_factory(sink)
        obs = await _execute(case, client, sink, stream_sink=stream_sink)

        scores: list[Score] = []
        for scorer in case.scorers:
            raw = scorer(case, obs)
            if inspect.isawaitable(raw):
                raw = await raw  # type: ignore[assignment]
            scores.append(raw)  # type: ignore[arg-type]

        baseline_diff = None
        if case.baseline is not None:
            baseline_diff = diff_against_baseline(obs, case.baseline)

        passed = (
            obs.error is None
            and all(s.passed for s in scores)
            and (baseline_diff is None or not baseline_diff.get("regressed", False))
        )
        return EvalResult(
            case=case.name,
            passed=passed,
            scores=scores,
            observation=obs,
            baseline_diff=baseline_diff,
            repeat=repeat,
            repeats=repeats,
        )


async def _execute(
    case: EvalCase,
    client: GrokClient,
    sink: InMemorySink,
    *,
    stream_sink: StreamSink | None = None,
) -> Observation:
    try:
        if case.tools:
            reg = ToolRegistry().add(*case.tools)
            orch = ToolOrchestrator(
                client=client,
                registry=reg,
                max_steps=case.max_steps,
                dry_run=case.dry_run,
            )
            # The orchestrator honours stream_sink when the client has a
            # streaming_transport; otherwise it silently falls back to the
            # non-stream chat path — so callers can pass stream_sink
            # unconditionally.
            run = await orch.run(
                list(case.messages),
                system=case.system,
                stream_sink=stream_sink,
            )
            return Observation(
                final_response=run.final,
                messages=run.messages,
                invocations=run.invocations,
                events=list(sink.events),
            )

        # No tools → single chat call through the client directly.
        msgs: list[GrokMessage] = []
        if case.system:
            msgs.append(GrokMessage("system", case.system))
        msgs.extend(case.messages)

        if stream_sink is not None:
            final: GrokResponse | None = None
            async for chunk in client.chat_stream(msgs):
                if chunk.delta:
                    stream_sink(chunk.delta)
                if chunk.is_final:
                    final = chunk.response
            if final is None:
                raise RuntimeError(
                    "chat_stream ended without yielding a final chunk"
                )
            return Observation(
                final_response=final,
                messages=msgs,
                invocations=[],
                events=list(sink.events),
            )

        resp = await client.chat(msgs)
        return Observation(
            final_response=resp,
            messages=msgs,
            invocations=[],
            events=list(sink.events),
        )
    except Exception as exc:
        return Observation(
            final_response=None,
            messages=list(case.messages),
            invocations=[],
            events=list(sink.events),
            error=f"{type(exc).__name__}: {exc}",
        )
