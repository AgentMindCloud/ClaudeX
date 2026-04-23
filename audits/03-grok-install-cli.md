# Audit: grok-install-cli

- **Upstream**: https://github.com/AgentMindCloud/grok-install-cli
- **Date audited**: 2026-04-23
- **Auditor**: Claude (Phase 1A)
- **Access mode**: WebFetch
- **Refs inspected**: `main` branch snapshot on 2026-04-23 (version `0.1.0` in `pyproject.toml`, no GitHub releases tagged)

## 1. Summary

`grok-install-cli` is the primary Python runtime for `grok-install.yaml`: parses the YAML, runs agents against xAI SDK, generates deploy configs for Vercel/Railway/Docker, and performs pre-install safety scanning. Codebase is organised cleanly into five subpackages (`core`, `deploy`, `integrations`, `runtime`, `safety`) under `src/grok_install/`, with a matching tests directory of 7 test files (cli, deploy, integrations, parser, runtime, safety, validator). CI runs pytest with coverage across Python 3.10–3.12 and lints with ruff; a separate weekly-scheduled `security.yml` runs bandit + pip-audit. Headline risk: **`pyproject.toml` version is `0.1.0` and no GitHub releases are tagged**, yet `grok-install-action` is documented to pin "CLI v2.14.0" (per Phase 1 inventory). This is a version-coherence mismatch that needs reconciliation — either the CLI's `version` lags the spec it's named after, or the action pins a PyPI artefact the repo hasn't published from this tag.

## 2. Structural map

Top-level tree (2 levels):

```
.
├── .github/workflows/        # ci.yml, publish.yml, security.yml
├── examples/                 # hello-agent, reply-bot
├── src/grok_install/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py                # typer app, entry point
│   ├── core/
│   ├── deploy/
│   ├── integrations/
│   ├── runtime/
│   └── safety/
│       ├── __init__.py
│       ├── rules.py
│       └── scanner.py
├── tests/
│   ├── fixtures/
│   ├── conftest.py
│   └── test_cli.py, test_deploy.py, test_integrations.py,
│       test_parser.py, test_runtime.py, test_safety.py,
│       test_validator.py
├── CONTRIBUTING.md, LICENSE, README.md, SECURITY.md
└── pyproject.toml
```

**Entry points**
- CLI: `grok-install` → `grok_install.cli:app` (typer). Also runnable as `python -m grok_install` via `__main__.py`.
- Commands (from README): `init`, `validate`, `scan`, `run`, `deploy`.

**Language mix**: Python 100% (linguist bar).

## 3. Dependency graph

- **Inbound**:
  - `grok-install-action` — documented to pin CLI v2.14.0 per Phase 1 inventory `(needs verification — see §8 / §10)`.
  - `grok-build-bridge`, `grok-agent-orchestra` — likely consumers for agent wrapping `(inferred; not verified)`.

- **Outbound** (from `pyproject.toml`):
  - `typer>=0.12` (CLI framework)
  - `pydantic>=2.6` (data modelling)
  - `rich>=13.7` (terminal output)
  - `pyyaml>=6.0`
  - `httpx>=0.27`
  - `jsonschema>=4.21` — validates against grok-install schema `(inferred)`
  - Optional `xai` extra: `xai-sdk>=0.1.0` (the integration with xAI is opt-in)
  - Dev: `pytest>=8.0`, `pytest-asyncio>=0.23`, `pytest-cov>=5.0`, `responses>=0.25`, `ruff>=0.5`, `bandit>=1.7`

- **External runtime deps**: xAI SDK (optional), cloud-target tools (Vercel/Railway/Docker configs generated, not called at runtime `(inferred)`).

## 4. Documentation quality

- **README.md**: present; promotional tone ("npm install for Grok agents"); lists five core commands with a 3-step quick-start. Missing from visible content: detailed command reference per subcommand, configuration file reference, troubleshooting, PyPI install instructions, CI badges.
- **SECURITY.md**: present; content not fetched `(WebFetch-limited)`.
- **CONTRIBUTING.md**: present; content not fetched.
- **Inline docs**: docstrings not sampled this iteration `(WebFetch-limited — would need to fetch cli.py or safety/scanner.py directly)`.

**Score: 3/5** — standard-issue README; tests and modular structure are healthier than the docs. Missing: proper CLI reference, badge row, versioning/release notes.

## 5. Tests & CI

- **Test framework**: pytest with pytest-asyncio and pytest-cov.
- **Test files**: 7 files mirroring the subpackages (`test_cli`, `test_deploy`, `test_integrations`, `test_parser`, `test_runtime`, `test_safety`, `test_validator`). Plus `conftest.py` and a `fixtures/` directory. Coverage structure looks disciplined; absolute coverage % not visible `(needs clone)`.
- **CI (`ci.yml`)**: matrix of Python 3.10, 3.11, 3.12 on ubuntu-latest. Lint `ruff check .` + test `pytest --cov=grok_install --cov-report=term-missing`. No `fail-under` coverage threshold visible.
- **Security (`security.yml`)**: runs on push/PR + weekly Mon 07:00 UTC. Uses `bandit -r src -ll` and `pip-audit` (with `|| true` — **non-blocking**). No CodeQL, no secret scanning configured.
- **Publish (`publish.yml`)**: content not fetched `(WebFetch-limited — likely handles PyPI release)`.

## 6. Security & safety signals

- **Dependency pinning**: `>=` lower-bound ranges, no lockfile visible at repo root `(WebFetch-limited)`. Looser than the exact-version pins in `grok-yaml-standards` CI.
- **Secret handling**: `XAI_API_KEY` is the primary env var; README shows `export XAI_API_KEY=...` (standard pattern, but audit hasn't verified the CLI doesn't log it).
- **Safety module**: dedicated `src/grok_install/safety/` with `rules.py` + `scanner.py`. Called via `grok-install scan` subcommand. Pre-install checks per README: hard-coded keys, missing rate limits, unsafe tool combinations. Implementation details not sampled `(WebFetch-limited)`.
- **bandit** runs weekly + on-change; **`pip-audit`** runs but is non-blocking (`|| true`) — vulns won't fail CI, only surface as log lines.
- **No secret-scan on the CLI repo itself** — if a contributor accidentally commits a test key, CI won't catch it.
- **Runtime gates**: README describes CLI prompts gating tool calls pending user approval. Implementation not sampled.

## 7. Code quality signals

- **Linter**: ruff (rules E/F/W/I/B, ignoring B008; 100-char lines; target py3.10). Config in `pyproject.toml`.
- **Type-checking**: no mypy / pyright section in `pyproject.toml` — types are declared (pydantic present) but not statically enforced in CI.
- **Error handling**: not sampled this iteration.
- **Module cohesion**: good — 5 clear subpackages, each with a matching test file. Separation of concerns (runtime / deploy / safety / integrations / core) is explicit.
- **Optional-dep pattern**: xai-sdk is an `extras_require`, so the CLI can install for users who only want `validate`/`scan` without pulling the xAI SDK wheel.

## 8. Integration contract

- **Public surface**:
  - CLI commands: `init`, `validate`, `scan`, `run`, `deploy` (each subcommand's flags not fully documented from README).
  - Python import path: `grok_install` (module-level API not explicitly documented as public; may need clarification).
  - Expected env var: `XAI_API_KEY`.
- **Version mismatch**: `pyproject.toml` says `version = "0.1.0"`; no GitHub releases published on the CLI repo. Yet the ecosystem (per Phase 1 inventory for `grok-install-action`) pins "CLI v2.14.0". This is a real inconsistency that downstream users encounter. Either:
  - The CLI version on PyPI is published at a different number (likely 2.14.x) and the `pyproject.toml` in `main` lags the published artefact; or
  - The action pins a CLI version that doesn't match the source repo's `main`.
  - `(needs clone / PyPI check / maintainer input)`
- **Compatibility statement**: Python >=3.10; CLI framework typer>=0.12 (stable); no explicit compat table against spec versions.

## 9. Top-5 high-impact improvements

| # | Improvement | Effort | Lev | Rationale | Blocked by |
|---|-------------|:------:|:---:|-----------|------------|
| 1 | Reconcile CLI version: publish GitHub releases matching `pyproject.toml` versions; align `grok-install-action`'s pin | M | 5 | Largest visible coherence gap in the ecosystem. Downstream tooling pins a version that has no GitHub release and may not match `main`. Fixing this unblocks reproducible installs. | Release decision |
| 2 | Make `pip-audit` blocking in `security.yml` (drop the `\|\| true`) | S | 4 | Silent dependency vulnerabilities defeat the purpose of running the scan. Aligns posture with the "safety 2.0" ecosystem narrative. | None |
| 3 | Add gitleaks or trufflehog to `security.yml` (secret scanning) | S | 4 | Pre-install scanning for hardcoded keys is a headline product feature; the CLI's own CI should enforce the same against its repo. | None |
| 4 | Add a coverage `fail-under` threshold (e.g. 80%) to `ci.yml` | S | 3 | `--cov-report=term-missing` prints coverage but doesn't fail on regression. A minimal threshold locks in the current discipline. | None |
| 5 | Publish a CLI command reference page (per subcommand, with flags) + link from README | M | 3 | README lists 5 commands without flag details. Real users will ask what `--strict`, `--profile`, etc. do. Auto-generatable from typer via `typer --help-doc`. | None |

## 10. Open questions / unknowns

- What CLI version is actually on PyPI? Does `pip install grok-install` pull 0.1.0 or 2.14.x? `(needs PyPI check)`
- Does `publish.yml` target PyPI or a private registry? `(WebFetch-limited — not fetched)`
- Does `rules.py` implement safety checks that duplicate `grok-yaml-standards/grok-security.json`, or does it load the schema? `(needs clone)`
- What's the coverage percentage today? `(needs clone or codecov badge)`
- Does the CLI pull from `grok-install`'s schema URL at runtime, vendor the schema, or both? `(needs clone)`
- Are there integration tests that actually hit xAI SDK, or all mocked with `responses`? `(needs clone)`
- Any deprecation policy for CLI command flags as the spec evolves? `(needs maintainer input)`

## 11. Evidence log

| # | URL | What was read / verified |
|---|-----|--------------------------|
| 1 | https://github.com/AgentMindCloud/grok-install-cli | Repo landing: description, stars (0), forks (0), issues (0), PRs (0), license (Apache 2.0), top-level tree, linguist bar (Python 100%). |
| 2 | https://raw.githubusercontent.com/AgentMindCloud/grok-install-cli/main/pyproject.toml | Project name `grok-install`, version `0.1.0`, Python `>=3.10`, 6 core deps + `xai` extra + dev deps; ruff config (E/F/W/I/B, B008 ignore, py3.10 target, 100-char). No black/mypy. |
| 3 | https://github.com/AgentMindCloud/grok-install-cli/tree/main/src/grok_install | Package layout: `__init__.py`, `__main__.py`, `cli.py`, plus `core/`, `deploy/`, `integrations/`, `runtime/`, `safety/` subpackages. |
| 4 | https://github.com/AgentMindCloud/grok-install-cli/tree/main/src/grok_install/safety | Safety module: `__init__.py`, `rules.py`, `scanner.py`. |
| 5 | https://github.com/AgentMindCloud/grok-install-cli/tree/main/.github/workflows | Three workflows: `ci.yml`, `publish.yml`, `security.yml`. |
| 6 | https://raw.githubusercontent.com/AgentMindCloud/grok-install-cli/main/.github/workflows/ci.yml | CI matrix py3.10/3.11/3.12; `ruff check .`; `pytest --cov=grok_install --cov-report=term-missing`; actions pinned by major tag. |
| 7 | https://raw.githubusercontent.com/AgentMindCloud/grok-install-cli/main/.github/workflows/security.yml | Weekly Mon 07:00 UTC + on push/PR. `bandit -r src -ll`; `pip-audit \|\| true` (non-blocking). No CodeQL / secret scan. Read-only permissions. |
| 8 | https://github.com/AgentMindCloud/grok-install-cli/tree/main/tests | 7 test files mirroring subpackages + `conftest.py` + `fixtures/`. |
