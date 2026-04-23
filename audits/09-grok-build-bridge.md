# Audit: grok-build-bridge

- **Upstream**: https://github.com/AgentMindCloud/grok-build-bridge
- **Date audited**: 2026-04-23
- **Auditor**: Claude (Phase 1A)
- **Access mode**: WebFetch
- **Refs inspected**: `main` branch snapshot on 2026-04-23 (`pyproject.toml` v0.1.0; 13 commits)

## 1. Summary

`grok-build-bridge` is the first of two xAI-SDK-layer repos: a Python framework that takes Grok-4.20-generated code and turns it into production X agents via a single `bridge.yaml` config. Core differentiators: **dual-layer safety** (static regex `safety.py`/`_patterns.py` + a Grok-powered JSON-mode audit via `xai_client.py`), 5+1 templates (`hello-bot`, `x-trend-analyzer`, `truthseeker-daily`, `code-explainer-bot`, `research-thread-weekly`, `grok-build-coding-agent`), multi-target deploy (X, Vercel, Render, local). Package layout is disciplined: 11 top-level modules (`builder`, `cli`, `deploy`, `parser`, `runtime`, `safety`, `xai_client` + 4 underscore-prefixed internals) with dedicated `schema/` and `templates/` subpackages. **CI is the strongest in the ecosystem**: 6 jobs (lint / test / schema-check / safety-scan / docs-link-check / build) with matrix py3.10–3.12 × Ubuntu/macOS, **mypy strict**, **ruff format --check**, **`--cov-fail-under=85`**, **Draft 2020-12 schema validation**. Maturity is early (1★, 0 PRs, no releases). Headline risk: **the Grok-powered safety audit layer depends on the Grok API itself being available and honest** — a well-known failure mode for LLM-based security review (prompt injection from the audited code; cost blow-out; false negatives on novel attack patterns). The static layer alone (bandit + regex) is the only layer that fails deterministically.

## 2. Structural map

Top-level tree (2 levels):

```
.
├── .github/workflows/            # ci.yml, release.yml
├── docs/
├── examples/
├── grok_build_bridge/
│   ├── __init__.py
│   ├── _banner.py, _console.py   # CLI UX internals
│   ├── _patterns.py              # regex patterns for safety layer 1
│   ├── builder.py                # Grok-output → code translation
│   ├── cli.py                    # typer entry
│   ├── deploy.py                 # X/Vercel/Render/local deploy
│   ├── parser.py                 # bridge.yaml parser
│   ├── runtime.py                # agent execution loop
│   ├── safety.py                 # dual-layer safety (static + Grok-audit)
│   ├── xai_client.py             # xAI SDK wrapper
│   ├── schema/                   # bridge.schema.json
│   └── templates/
│       ├── INDEX.yaml, hello-bot/,
│       ├── code-explainer-bot.yaml,
│       ├── grok-build-coding-agent.yaml,
│       ├── research-thread-weekly.yaml,
│       ├── truthseeker-daily.yaml,
│       └── x-trend-analyzer.yaml
├── launch/
├── tests/
├── vscode/
├── .env.example, .gitignore
├── CHANGELOG.md, CONTRIBUTING.md, LICENSE, README.md, ROADMAP.md
└── pyproject.toml, requirements.txt
```

**Entry points**
- CLI: `grok-build-bridge` → `grok_build_bridge.cli:main` (typer).
- Template catalogue: `templates/INDEX.yaml` (likely the registry equivalent to `awesome-grok-agents`' `featured-agents.json`).

**Language mix**: Python 100% (linguist).

## 3. Dependency graph

- **Inbound**: users who invoke the CLI to materialise a Grok-output → X agent.
- **Outbound** (from `pyproject.toml`):
  - `xai-sdk>=1.0` — primary runtime; uses model IDs like `grok-4.20-0309` (SDK version ≠ model version).
  - `pyyaml>=6`, `typer>=0.12`, `rich>=13`, `httpx>=0.27`, `jsonschema>=4.21`, `tenacity>=8.2` (retries).
  - Dev: `pytest>=8`, `pytest-cov>=5`, `mypy>=1.10`, `ruff>=0.6`, `build>=1.2`, `types-PyYAML`, `types-jsonschema`.
- **Peer**: `grok-agent-orchestra` (the other xAI-SDK-layer repo — both depend on xai-sdk / grok-4.20 but don't appear to depend on each other directly).
- **Not depending on**: `grok-install-cli` or `grok-install` spec — this is a parallel track to the grok-install lineage.

## 4. Documentation quality

- **README.md**: present; clear "generated code → live agent" narrative; lists 5 certified templates + dual-layer safety + multi-target deploy.
- **CHANGELOG.md**, **CONTRIBUTING.md**, **ROADMAP.md**: all present at root (more governance files than most repos).
- **`docs/`**: present; content not sampled.
- **`examples/`**: separate from `templates/` — suggests a demos/walkthroughs split.
- **`.env.example`**: present at root (best-practice; flags expected env vars).

**Score: 4/5** — strong governance files; `.env.example` is a nice hygiene signal. Loses a point because README narrative wasn't verified against code and module-level docstrings weren't sampled.

## 5. Tests & CI

**CI (`ci.yml`) — best in the ecosystem:**

| Job | Purpose |
|-----|---------|
| `lint` | `ruff check .` + `ruff format --check .` + `mypy grok_build_bridge` (**strict**). |
| `test` | Matrix **py3.10 / 3.11 / 3.12 × Ubuntu / macOS**. `pytest --cov-fail-under=85`. Codecov upload non-blocking. |
| `schema-check` | Validates `templates/*.yaml` against `bridge.schema.json` using **jsonschema Draft202012Validator**. |
| `safety-scan` | `bandit -r grok_build_bridge -ll` + `pip-audit` (non-blocking). |
| `docs-link-check` | `lychee-action@v2` in offline mode on `*.md`. |
| `build` | `python -m build` → wheel + sdist; 7-day artifact retention; **depends on all prior jobs**. |

- **Concurrency**: cancel-in-progress on same ref.
- **Coverage discipline**: `--cov-fail-under=85` is enforced — first in the ecosystem.
- **Cross-platform**: Ubuntu + macOS matrix — unique to this repo in the ecosystem.
- **Strict typing in CI**: mypy strict (also first in the ecosystem).
- **Schema validator version**: Draft-2020-12 — aligned with `grok-install` v2.14 (so this repo avoids the draft-07 drift seen in `grok-yaml-standards`).

## 6. Security & safety signals

- **Dual-layer safety**:
  - Layer 1 (deterministic): `grok_build_bridge/_patterns.py` + `safety.py` — static regex + bandit in CI. Fails closed on hard-coded secrets / unsafe tool combos.
  - Layer 2 (LLM-based): Grok-powered JSON-mode audit via `xai_client.py`. *Risk*: LLM auditors are susceptible to prompt injection from the audited code, have false-negative rates on novel attack patterns, and add API cost. Should never be the only line of defence.
- **Dependency pinning**: `>=` ranges on runtime deps + dev deps; no lockfile visible `(WebFetch-limited)`.
- **Secrets**: `.env.example` at root signals the expected env-var surface.
- **`safety-scan` job**: `bandit -r grok_build_bridge -ll` on CI (same posture as grok-install-cli). `pip-audit` still non-blocking (`|| true` pattern implied since description said "non-blocking").
- **Template INDEX.yaml**: likely acts as the registry for the 5+1 templates, analogous to `featured-agents.json`. Worth cross-referencing with the marketplace.
- **No secret-scan CI job** (same gap as grok-install-cli).

## 7. Code quality signals

- **ruff** with rules E, F, I, UP (pyupgrade), B (bugbear), W; 100-char line; double quotes; lf line endings.
- **mypy strict** — first in the ecosystem. Also handles CLI decorators specifically (typer type-inference).
- **Module cohesion**: 11 top-level modules are functionally distinct; underscore-prefix for CLI UX internals (`_banner`, `_console`, `_patterns`) — good Python convention.
- **Test coverage ≥85%** enforced in CI.
- **Cross-platform tests** — surface area beyond what every other repo tests.
- **Coverage package**: `grok_build_bridge` package (matches the top-level module name).

## 8. Integration contract

- **Public surfaces**:
  - CLI: `grok-build-bridge` (typer).
  - Config: `bridge.yaml` parsed by `parser.py`, validated by `schema/bridge.schema.json`.
  - Templates: 5 YAMLs + 1 directory template (`hello-bot/`).
  - Deploy targets: X, Vercel, Render, local.
- **Version**: `0.1.0`; no GitHub releases; no PyPI release visible `(needs PyPI check)`.
- **Breaking-change posture**: pre-1.0; ROADMAP.md present at root (content not fetched).

## 9. Top-5 high-impact improvements

| # | Improvement | Effort | Lev | Rationale | Blocked by |
|---|-------------|:------:|:---:|-----------|------------|
| 1 | Document the LLM-audit layer's limitations + a "static-only" fallback mode | S | 4 | LLM-based security review can be prompt-injected by the audited code and is non-deterministic. Users deploying to production X need a deterministic fail-closed path. | None |
| 2 | Replace `pip-audit \|\| true` with blocking + add gitleaks/trufflehog for secret-scan | S | 4 | Same recommendation as grok-install-cli; here too the safety narrative is contradicted by non-blocking CI. | None |
| 3 | Pin `xai-sdk` and `tenacity` by exact version, publish `requirements.txt` (visible at repo root) with the pins | S | 3 | The SDK's model IDs drift with Grok upgrades; a bridge pinned to `grok-4.20-0309` should also pin the SDK. | None |
| 4 | Share `_patterns.py` with `grok-install-cli/src/grok_install/safety/rules.py` via a small `grok-safety-rules` package or git-submodule | M | 5 | Highest cross-ecosystem leverage. Both the CLI and the bridge implement static safety scanning; a shared rules module is the only way to prevent the two from drifting silently. | Ownership + packaging decision |
| 5 | Publish Codecov / coverage badges on README (currently not shown) | S | 2 | Test discipline is excellent; surfacing the 85%+ coverage earns trust and discourages regressions in review. | None |

## 10. Open questions / unknowns

- What's in `grok_build_bridge/schema/bridge.schema.json` — does it reuse anything from `grok-install/schemas/v2.14/schema.json`, or is it bespoke? `(needs content fetch)`
- How is the Grok-audit layer's system prompt / audit criteria specified, and how is prompt-injection mitigated? `(needs safety.py source)`
- Does the INDEX.yaml registry follow the same shape as `awesome-grok-agents/featured-agents.json`? `(needs content fetch)`
- What does `launch/` contain (launch-day assets / marketing / GitHub release automation)? `(not fetched)`
- What does `vscode/` at repo root do (launch helpers for `vscode-grok-yaml`)? `(not fetched)`
- How are the 5 templates validated beyond `schema-check` — is there a dry-run matrix in CI? `(partially verified — the `test` job runs pytest, but end-to-end template runs aren't visible)`
- Does the bridge actually install `grok-install.yaml` agents, or does it produce its own deployable artefact? `(architecture question — README suggests the latter)`

## 11. Evidence log

| # | URL | What was read / verified |
|---|-----|--------------------------|
| 1 | https://github.com/AgentMindCloud/grok-build-bridge | Repo landing: description (Grok-4.20 → X agent framework), 1★, 0 forks, 0 PRs, Apache 2.0 (Jan Solo), 13 commits, Python 100%, top-level tree. |
| 2 | https://raw.githubusercontent.com/AgentMindCloud/grok-build-bridge/main/pyproject.toml | Name `grok-build-bridge`, v0.1.0, py>=3.10, xai-sdk>=1.0 + pyyaml/rich/typer/httpx/jsonschema/tenacity, dev has mypy>=1.10 (strict) + ruff>=0.6 + build; ruff rules E/F/I/UP/B/W, 100-char, double quotes, lf. |
| 3 | https://github.com/AgentMindCloud/grok-build-bridge/tree/main/grok_build_bridge | Package has 11 top-level modules (`builder`, `cli`, `deploy`, `parser`, `runtime`, `safety`, `xai_client`, plus `__init__`, `_banner`, `_console`, `_patterns`) + `schema/` + `templates/`. |
| 4 | https://github.com/AgentMindCloud/grok-build-bridge/tree/main/.github/workflows | 2 workflows: `ci.yml`, `release.yml`. |
| 5 | https://raw.githubusercontent.com/AgentMindCloud/grok-build-bridge/main/.github/workflows/ci.yml | 6 jobs: lint (ruff check + format --check + mypy strict), test (matrix py3.10/3.11/3.12 × Ubuntu/macOS, `--cov-fail-under=85`), schema-check (Draft202012Validator), safety-scan (bandit + pip-audit), docs-link-check (lychee@v2 offline), build (wheel+sdist, 7-day artifact retention, depends on all prior); concurrency cancel; actions pinned by major tag. |
| 6 | https://github.com/AgentMindCloud/grok-build-bridge/tree/main/grok_build_bridge/templates | 5 template YAMLs (`code-explainer-bot`, `grok-build-coding-agent`, `research-thread-weekly`, `truthseeker-daily`, `x-trend-analyzer`) + 1 template directory (`hello-bot/`) + `INDEX.yaml` registry. |
