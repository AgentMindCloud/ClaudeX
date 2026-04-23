"""Shared stubs + payload helpers for eval tests."""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class StubTransport:
    responses: list
    calls: list = field(default_factory=list)

    async def __call__(self, *, method, url, headers, body, timeout):
        self.calls.append(json.loads(body.decode("utf-8")))
        status, payload = self.responses.pop(0)
        return status, {}, json.dumps(payload).encode("utf-8")


async def noop_sleep(_s):
    return None


def final_msg(content, *, prompt=5, completion=3, model="grok-4"):
    return (
        200,
        {
            "model": model,
            "choices": [
                {
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
        },
    )


def tool_call_msg(calls, *, finish="tool_calls", prompt=4, completion=2):
    return (
        200,
        {
            "model": "grok-4",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": c["id"],
                                "type": "function",
                                "function": {
                                    "name": c["name"],
                                    "arguments": json.dumps(c["args"]),
                                },
                            }
                            for c in calls
                        ],
                    },
                    "finish_reason": finish,
                }
            ],
            "usage": {"prompt_tokens": prompt, "completion_tokens": completion},
        },
    )
