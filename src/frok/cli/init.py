"""``frok init [PATH]`` — scaffold a new Frok project.

Writes a minimal, runnable skeleton:

  * ``CLAUDE.md`` — project-scoped instructions stub.
  * ``frok.toml`` — config template with every section populated.
  * ``cases/smoke.py`` — a single `EvalCase` wired to a stub transport
    so ``frok run cases/smoke.py`` passes out of the box (no
    ``FROK_CLIENT_API_KEY`` needed yet).
  * ``.github/workflows/frok.yml`` — CI workflow demonstrating the
    capture / diff / fail-on-regression loop.

Aborts with ``CliError`` if any target file already exists, unless
``--force`` is passed. Errors enumerate the conflicting files so the
operator can decide case-by-case.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .common import CliError


_CLAUDE_MD = """# Project instructions

This project uses [Frok](../../../) for LLM eval regressions.

## Quick commands

- `frok run cases/smoke.py` — run the eval suite, print a Markdown report.
- `frok run cases/smoke.py --list` — preview resolved case names.
- `frok run cases/smoke.py --filter 'safety-*'` — run a subset.
- `frok config show` — inspect the resolved config.
- `frok trace inspect <file.jsonl>` — summarise a captured trace.

## Baseline workflow

```
# First time: record a reference baseline.
frok run cases/smoke.py --capture-baseline ./baselines/

# Later runs: diff against it.
frok run cases/smoke.py --use-baseline ./baselines/ --fail-on-regression
```

See `frok.toml` for config options and the `.github/workflows/frok.yml`
file for a CI template.
"""


_FROK_TOML = """# Frok configuration.
# Set a profile either here (`profile = "dev"`) or via FROK_PROFILE.

profile = "dev"

[client]
# Set via FROK_CLIENT_API_KEY in your environment, or uncomment:
# api_key = "sk-..."
model = "grok-4"
base_url = "https://api.x.ai/v1"
timeout_s = 60.0
max_retries = 4

[safety]
enabled = true
# Disable specific rules by name — see frok.safety.rules.BUILTIN_RULES.
disabled_rules = []

[telemetry]
# "null" (default), "memory" (tests), or "jsonl" (persistent).
sink = "null"
# path = "./traces/run.jsonl"   # required when sink = "jsonl"

[memory]
enabled = false
path = "./frok-memory.db"
embedder = "hash"
embedder_dim = 128

[multimodal]
vision_enabled = true
voice_enabled = false
audio_transcribe_path = "/audio/transcriptions"

# ---------------------------------------------------------------------------
# Profile overrides — merged on top of the base section when selected.
# ---------------------------------------------------------------------------
[profiles.prod.telemetry]
sink = "jsonl"
path = "/var/log/frok.jsonl"

[profiles.prod.safety]
disabled_rules = []
"""


_SMOKE_CASE = '''"""Starter smoke case.

Runs without a real API key via a stub transport so ``frok init && frok
run cases/smoke.py`` passes out of the box. Replace ``make_client`` with
``frok.clients.transports.urllib_transport`` (or your own) once you have
``FROK_CLIENT_API_KEY`` set and want to hit xAI for real.
"""

import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import AnswerContains, EvalCase, NoErrors
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


def _ok(text):
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
            "usage": {"prompt_tokens": 5, "completion_tokens": 3},
        },
    )


def make_client(config, sink):
    """Construct a GrokClient for this case. CI can stub the transport;
    production swaps in `urllib_transport` + a real api_key."""
    return GrokClient(
        api_key="stub",
        transport=_StubTransport([_ok("Hello from Frok!")]),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="smoke-greeting",
        messages=[GrokMessage("user", "Say hello.")],
        scorers=[AnswerContains("Hello"), NoErrors()],
    ),
]
'''


_GITHUB_WORKFLOW = """name: Frok Eval
on:
  pull_request:
  push:
    branches: [main]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install frok
        run: pip install frok

      - name: Run eval suite
        env:
          FROK_CLIENT_API_KEY: ${{ secrets.FROK_CLIENT_API_KEY }}
        run: |
          frok run cases/smoke.py \\
            --summary-json frok-summary.json \\
            --output frok-report.md \\
            --fail-on-regression

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: frok-report
          path: |
            frok-report.md
            frok-summary.json

  # Uncomment to record a trusted baseline on `main` and diff PRs against it.
  # baseline:
  #   if: github.ref == 'refs/heads/main'
  #   runs-on: ubuntu-latest
  #   steps:
  #     - uses: actions/checkout@v4
  #     - uses: actions/setup-python@v5
  #       with: { python-version: "3.11" }
  #     - run: pip install frok
  #     - env: { FROK_CLIENT_API_KEY: ${{ secrets.FROK_CLIENT_API_KEY }} }
  #       run: frok run cases/smoke.py --capture-baseline ./baselines/
  #     - uses: actions/upload-artifact@v4
  #       with: { name: baselines, path: baselines/ }
"""


# Relative path → file contents. Directories are mkdir-p'd per file.
TEMPLATES: dict[str, str] = {
    "CLAUDE.md": _CLAUDE_MD,
    "frok.toml": _FROK_TOML,
    "cases/smoke.py": _SMOKE_CASE,
    ".github/workflows/frok.yml": _GITHUB_WORKFLOW,
}


# ---------------------------------------------------------------------------
# --example flavors
# ---------------------------------------------------------------------------
_TOOLS_CASE = '''"""Example tool-use case.

Shows how to expose a typed Python function as a Grok tool via
``frok.tools``, let the orchestrator drive the model ->
tool-call -> result loop, and assert on tool behavior with
``ToolCalled``. The stub transport emits exactly the two responses
the loop needs: one tool_call, then the final answer.
"""

import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import AnswerContains, EvalCase, NoErrors, ToolCalled
from frok.telemetry import Tracer
from frok.tools import tool


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


def _tool_call(name, args, *, call_id):
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
                                "id": call_id,
                                "type": "function",
                                "function": {
                                    "name": name,
                                    "arguments": json.dumps(args),
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 2},
        },
    )


def _final(text):
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
            "usage": {"prompt_tokens": 10, "completion_tokens": 3},
        },
    )


@tool
def add(a: int, b: int) -> int:
    """Return a + b."""
    return a + b


def make_client(config, sink):
    return GrokClient(
        api_key="stub",
        transport=_StubTransport(
            [
                _tool_call("add", {"a": 2, "b": 40}, call_id="c1"),
                _final("The answer is 42."),
            ]
        ),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="tools-arithmetic",
        messages=[GrokMessage("user", "what is 2 + 40?")],
        tools=[add],
        scorers=[
            AnswerContains("42"),
            ToolCalled("add", times=1),
            NoErrors(),
        ],
    ),
]
'''


_MULTIMODAL_CASE = '''"""Example multimodal case.

Shows how to send a mixed text + image message via the
``GrokMessage.parts`` field. Uses ``ImageRef`` to build the
OpenAI-compatible image content part and a stub transport to return
a canned description, so the case runs without real vision creds.

Production swap: drop the stub and use
``frok.clients.transports.urllib_transport`` + ``FROK_CLIENT_API_KEY``.
"""

import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import AnswerContains, EvalCase, NoErrors
from frok.multimodal import ImageRef
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


def _final(text):
    return (
        200,
        {
            "model": "grok-4-vision",
            "choices": [
                {
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 50, "completion_tokens": 10},
        },
    )


def make_client(config, sink):
    return GrokClient(
        api_key="stub",
        transport=_StubTransport(
            [_final("A small PNG image, roughly 4 bytes of sample data.")]
        ),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


# Tiny sample blob standing in for an actual image. In production use
# `ImageRef.from_path("/real/file.png")` or `ImageRef.from_url("https://...")`.
_IMAGE = ImageRef.from_bytes(b"\\x89PNG", mime="image/png")


CASES = [
    EvalCase(
        name="multimodal-describe-image",
        messages=[
            GrokMessage(
                role="user",
                content="",
                parts=(
                    {"type": "text", "text": "Describe this image."},
                    _IMAGE.to_content_part(),
                ),
            ),
        ],
        scorers=[AnswerContains("image"), NoErrors()],
    ),
]
'''


_MEMORY_CASE = '''"""Example persistent-memory case.

Shows how to expose ``MemoryStore`` read/write as typed tools so
Grok can stash a fact and recall it later. Uses an in-process
(``:memory:``) SQLite store so the case is hermetic.

Production swap: point the store at a file path
(e.g. ``./frok-memory.db``) and share it across runs for durable
recall.
"""

import json
from dataclasses import dataclass, field

from frok.clients import GrokClient, GrokMessage
from frok.evals import AnswerContains, EvalCase, NoErrors, ToolCalled
from frok.memory import HashEmbedder, MemoryStore
from frok.telemetry import Tracer
from frok.tools import tool


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


def _tool_call(name, args, *, call_id):
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
                                "id": call_id,
                                "type": "function",
                                "function": {
                                    "name": name,
                                    "arguments": json.dumps(args),
                                },
                            }
                        ],
                    },
                    "finish_reason": "tool_calls",
                }
            ],
            "usage": {"prompt_tokens": 5, "completion_tokens": 2},
        },
    )


def _final(text):
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
            "usage": {"prompt_tokens": 10, "completion_tokens": 3},
        },
    )


# One shared store for the whole case so both tools see the same rows.
_STORE = MemoryStore(":memory:", HashEmbedder(dim=64))


@tool
async def remember(text: str) -> str:
    """Store a fact for later recall."""
    record = await _STORE.remember(text)
    return f"stored (id={record.id})"


@tool
async def recall(query: str, k: int = 3) -> str:
    """Retrieve facts similar to the query."""
    hits = await _STORE.recall(query, k=k)
    return "; ".join(h.content for h in hits) or "(no recall)"


def make_client(config, sink):
    return GrokClient(
        api_key="stub",
        transport=_StubTransport(
            [
                _tool_call(
                    "remember", {"text": "Grok seeks truth"}, call_id="c1"
                ),
                _tool_call("recall", {"query": "Grok truth"}, call_id="c2"),
                _final("Grok seeks truth — recalled from memory."),
            ]
        ),
        sleep=_noop_sleep,
        tracer=Tracer(sink=sink),
    )


CASES = [
    EvalCase(
        name="memory-stash-and-recall",
        messages=[
            GrokMessage(
                "user",
                "Remember 'Grok seeks truth', then recall it to confirm.",
            )
        ],
        tools=[remember, recall],
        scorers=[
            ToolCalled("remember", times=1),
            ToolCalled("recall", times=1),
            AnswerContains("truth"),
            NoErrors(),
        ],
    ),
]
'''


EXAMPLE_TEMPLATES: dict[str, str] = {
    "tools": _TOOLS_CASE,
    "multimodal": _MULTIMODAL_CASE,
    "memory": _MEMORY_CASE,
}


async def init_cmd(args: argparse.Namespace) -> int:
    target: Path = args.path

    # Compose base templates + any requested --example flavors.
    templates = dict(TEMPLATES)
    for name in args.example or ():
        templates[f"cases/{name}.py"] = EXAMPLE_TEMPLATES[name]

    existing = [rel for rel in templates if (target / rel).exists()]
    if existing and not args.force:
        raise CliError(
            f"{len(existing)} file(s) already exist at {target} "
            f"(pass --force to overwrite): {existing}"
        )

    target.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for rel, content in templates.items():
        dest = target / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        written.append(rel)

    writer = sys.stdout
    writer.write(f"Wrote {len(written)} file(s) to {target}:\n")
    for rel in written:
        writer.write(f"  {rel}\n")
    writer.write(
        "\nNext steps:\n"
        "  1. Review the generated files (especially frok.toml).\n"
        "  2. `frok run cases/smoke.py --list` to preview the case set.\n"
        "  3. `frok run cases/smoke.py` to run it — the bundled stub\n"
        "     transport means no API key is required yet.\n"
    )
    return 0


def register(sub: "argparse._SubParsersAction") -> None:
    init = sub.add_parser(
        "init",
        help="Scaffold a new Frok project.",
        description=(
            "Write a minimal, runnable project skeleton: CLAUDE.md, "
            "frok.toml, cases/smoke.py, and a GitHub Actions workflow "
            "stub. Aborts if any target already exists unless --force."
        ),
    )
    init.add_argument(
        "path",
        type=Path,
        nargs="?",
        default=Path("."),
        help="target directory (default: current directory)",
    )
    init.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing files",
    )
    init.add_argument(
        "--example",
        action="append",
        choices=sorted(EXAMPLE_TEMPLATES.keys()),
        default=[],
        metavar="NAME",
        help=(
            "also scaffold a reference case for one of: "
            f"{sorted(EXAMPLE_TEMPLATES.keys())}. Repeatable. Each "
            "example is self-contained and runs green out of the box."
        ),
    )
    init.set_defaults(fn=init_cmd)
