# Audit: awesome-grok-agents

- **Upstream**: https://github.com/AgentMindCloud/awesome-grok-agents
- **Date audited**: 2026-04-23
- **Auditor**: Claude (Phase 1A)
- **Access mode**: WebFetch
- **Refs inspected**: `main` branch snapshot on 2026-04-23 (`featured-agents.json` v1.0, updated 2026-04-21)

## 1. Summary

`awesome-grok-agents` is the curated template gallery — 10 production-ready agents installable via `grok-install install github.com/agentmindcloud/awesome-grok-agents/templates/<name>`. Each template has its own `README.md`, `.env.example`, `grok-install.yaml`, a `.grok/` folder, and optionally `tools/`. The `featured-agents.json` registry is a small, strict schema listing each agent's name, safety_profile, category, and description. CI is surprisingly strong: `validate-templates.yml` runs 7 jobs (discover / yamllint / registry / schema / spec-version / links / validate-matrix), matrix-validates each template individually with `validate_template.py`, `scan_template.py` (fails on warnings), and `mock_run_template.py`. Maturity is early (1★, 0 issues, 2 PRs, 10 commits). Headline findings: **safety-profile catalogue is 2-of-3** — all 10 templates use either `strict` or `standard`, no `permissive` exemplar exists to calibrate what the loosest profile should look like; and templates validate against a stub CLI (`grok_install_stub` in `scripts/`) rather than the real `grok-install-cli`, so template ↔ CLI behavioural drift won't be caught by this repo's CI.

## 2. Structural map

Top-level tree (2 levels):

```
.
├── .github/workflows/       # release.yml, validate-templates.yml
├── docs/
├── schemas/                 # JSON schema(s) for featured-agents.json
├── scripts/                 # validate_template.py, scan_template.py,
│                            # mock_run_template.py, grok_install_stub/
├── templates/
│   ├── code-reviewer/
│   ├── hello-grok/          # (sampled: .env.example, README.md,
│   │                        #  grok-install.yaml, .grok/, tools/)
│   ├── live-event-commentator/
│   ├── personal-knowledge/
│   ├── reply-engagement-bot/
│   ├── research-swarm/
│   ├── scientific-discovery/
│   ├── thread-ghostwriter/
│   ├── trend-to-thread/
│   └── voice-agent-x/
├── .yamllint.yml
├── CHANGELOG.md, CONTRIBUTING.md, LICENSE, README.md, SECURITY.md
└── featured-agents.json
```

**Entry points**
- Registry: `featured-agents.json` (consumed by `grok-agents-marketplace` per Phase 1 inventory).
- Per-template: `templates/<name>/grok-install.yaml` (the agent definition).
- CI: `.github/workflows/validate-templates.yml`.

**Language mix**: Python 100% (linguist; presumably the `scripts/` tooling dominates by byte count over YAML).

## 3. Dependency graph

- **Inbound**:
  - `grok-agents-marketplace` — consumes `featured-agents.json` registry `(inferred; not cross-verified this iteration)`.
  - Users installing via `grok-install install github.com/.../templates/<name>`.
- **Outbound**:
  - Spec: must produce YAML matching `grok-install` spec v2.12 / v2.13 / v2.14 (explicitly allowed by `spec-version` CI job).
  - Schemas: `grok-yaml-standards` schemas `(inferred — not confirmed from this repo's `schemas/` directory yet)`.
  - Registry consumers: `grok-agents-marketplace` reads the JSON.
- **External runtime deps** (from `validate-templates.yml`):
  - Python 3.12, PyYAML.
  - Node 20, `ajv-cli@5`, `ajv-formats@3`.
  - `lycheeverse/lychee-action@v1` (link check).

## 4. Documentation quality

- **README.md**: present; frames the repo as a gallery with one-command install and declares the safety framework (`strict`, `standard`). Missing: explicit `permissive` profile definition or example.
- **CHANGELOG.md**, **CONTRIBUTING.md**, **SECURITY.md**, **`docs/`**: present. Not fetched.
- **Per-template docs**: `hello-grok/README.md` confirmed to exist (from the tree view). Not sampled for content.
- **`featured-agents.json`**: authoritative and compact. Every agent has the same four fields; no slop.

**Score: 4/5** — strong registry + per-template structure; CI enforces shape. Loses a point because `permissive` profile has no exemplar and because per-template README content wasn't sampled.

## 5. Tests & CI

`.github/workflows/validate-templates.yml` jobs (matrix + fan-in):

| Job | Purpose |
|-----|---------|
| `discover` | Lists `templates/*`, emits JSON array for downstream matrix. |
| `yamllint` | Lint YAML in `templates/`, `.yamllint.yml`, `.github/workflows/*` against `.yamllint.yml`. |
| `registry` | Python-based validation of `featured-agents.json` (PyYAML). |
| `schema` | ajv-cli (Node 20) validation of `featured-agents.json` against JSON schema. |
| `spec-version` | Enforces template `grok-install.yaml` declares spec in {v2.12, v2.13, v2.14}. |
| `links` | Lychee link-checker on per-template README.md; accepts HTTP 200/204/206/403/429. |
| `validate` | Matrix over all templates. Each template runs: `validate_template.py`, `scan_template.py` (*fails on warnings*), `mock_run_template.py`. |

- **Strictest signal in the ecosystem**: `scan_template.py` fails on warnings (not just errors).
- **Matrix coverage**: discover → validate-matrix means adding a new template is zero-config; CI picks it up automatically.
- **Stub-based validation**: the `grok_install_stub` package in `scripts/` means templates are not validated against the actual CLI; drift between stub and real CLI goes undetected here `(tradeoff noted)`.
- **Link-check policy**: tolerant HTTP codes (403/429) — pragmatic for X/social links that rate-limit or block unauthenticated fetches.

## 6. Security & safety signals

- **Safety profiles**: every template declares one of `strict` | `standard`. Distribution (from `featured-agents.json`): **6 strict, 4 standard, 0 permissive**. Missing `permissive` exemplar is a policy gap — if the profile exists in the spec, at least one reference template should illustrate it.
- **Permission gates**: README references "approval gate" for templates with external write access (reply-engagement-bot, code-reviewer, etc.) — consistent with `strict` profile meaning.
- **Dependency pinning**: Node libs pinned by major (`ajv-cli@5`, `ajv-formats@3`); GitHub actions by major tag — same ecosystem pattern.
- **No secret-scan job** in CI, but `scan_template.py` (ecosystem-local) checks for hardcoded credentials in templates per the ecosystem safety model `(inferred)`.
- **Disclosure**: `SECURITY.md` present (not fetched).

## 7. Code quality signals

- **Linters**: yamllint via `.yamllint.yml`; Python scripts `(ruff/black not verified — not fetched)`.
- **Custom tooling**: `scripts/` contains `validate_template.py`, `scan_template.py`, `mock_run_template.py`, and a `grok_install_stub/` sub-package — indicates deliberate in-repo testing infra rather than depending on the CLI.
- **Module cohesion**: excellent per-template isolation; each `templates/<name>/` is self-contained.
- **Registry discipline**: `featured-agents.json` uses a strict flat schema; no nested dicts, no missing required fields.

## 8. Integration contract

- **Public surfaces**:
  - Template URL shape: `github.com/agentmindcloud/awesome-grok-agents/templates/<name>`.
  - Registry: `featured-agents.json` (v1.0, schema `featured-agents-v1.schema.json` lives in `grok-install` root).
  - Per-template: `grok-install.yaml` (the installable unit).
- **Spec-version tolerance**: accepts v2.12, v2.13, v2.14 simultaneously — softest posture in the ecosystem (useful for template authors; risky for version coherence).
- **Breaking-change posture**: no tags/releases yet; all 10 templates added over ~10 commits.

## 9. Top-5 high-impact improvements

| # | Improvement | Effort | Lev | Rationale | Blocked by |
|---|-------------|:------:|:---:|-----------|------------|
| 1 | Add a `permissive` exemplar template (e.g. an internal-tool agent with no X write access) to fill the 3rd safety profile slot | M | 4 | The tripartite profile model is referenced everywhere but has zero visible `permissive` example. New adopters can't calibrate what `permissive` should look like. | Safety-profile rubric from `grok-yaml-standards` |
| 2 | Replace the `grok_install_stub` with the real `grok-install-cli` in CI (or run both; stub-only is risky) | M | 5 | Template authors can pass local CI and still break when installed via the real CLI. Catches the widest class of template-runtime drift. | CLI packaging (depends on CLI npm-vs-Python resolution) |
| 3 | Tighten `spec-version` job: require templates to declare the *latest* supported version (v2.14) after a 1-release grace period | S | 3 | Accepting v2.12/v2.13/v2.14 forever means templates never migrate. A deprecation window forces movement. | Release coordination |
| 4 | Add a `safety_profile` distribution report to the CI summary (strict/standard/permissive counts) | S | 3 | Surfaces the 2-of-3 gap above so it doesn't silently persist as the gallery grows. | None |
| 5 | Publish the schema under `schemas/` (currently not enumerated in this audit) to `grok-yaml-standards` or link to it, to avoid a fourth schema location | S | 3 | Ecosystem already has schemas in `grok-install/schemas/` and `grok-yaml-standards/schemas/`; a third location in this repo would be drift. Clarify which is authoritative. | Schema ownership decision |

## 10. Open questions / unknowns

- What's actually in `schemas/` — is it a local copy of `featured-agents-v1.schema.json` or something distinct? `(WebFetch-limited — not enumerated)`
- What does `grok_install_stub/` implement (enough of the CLI surface to be meaningful)? `(needs clone)`
- Does `scan_template.py` reuse logic from `grok-install-cli/src/grok_install/safety/scanner.py`, or is it a parallel implementation? `(needs clone + grok-install-cli clone to compare)`
- What are the pass/fail criteria for `mock_run_template.py`? `(needs content fetch)`
- Are template READMEs generated or hand-written? `(not sampled)`
- Why does Lychee accept 403/429 — are there specific X.com / GitHub URLs hitting rate limits? `(CI log review)`
- Is the `release.yml` workflow currently cutting releases (none visible on repo)? `(not fetched)`

## 11. Evidence log

| # | URL | What was read / verified |
|---|-----|--------------------------|
| 1 | https://github.com/AgentMindCloud/awesome-grok-agents | Repo landing: description, 1★, 0 issues, 2 PRs, Apache 2.0, 10 commits, Python 100%, top-level tree including `featured-agents.json` at root. |
| 2 | https://github.com/AgentMindCloud/awesome-grok-agents/tree/main/templates | 10 template subdirs: `code-reviewer`, `hello-grok`, `live-event-commentator`, `personal-knowledge`, `reply-engagement-bot`, `research-swarm`, `scientific-discovery`, `thread-ghostwriter`, `trend-to-thread`, `voice-agent-x`. |
| 3 | https://raw.githubusercontent.com/AgentMindCloud/awesome-grok-agents/main/featured-agents.json | Registry v1.0 updated 2026-04-21; 10 agent entries each with `name/safety_profile/category/description`; safety distribution 6 strict / 4 standard / 0 permissive. |
| 4 | https://github.com/AgentMindCloud/awesome-grok-agents/tree/main/.github/workflows | 2 workflows: `release.yml`, `validate-templates.yml`. |
| 5 | https://raw.githubusercontent.com/AgentMindCloud/awesome-grok-agents/main/.github/workflows/validate-templates.yml | 7-job CI: discover → yamllint / registry / schema / spec-version (v2.12–v2.14) / links (Lychee, tolerant codes) → validate-matrix (validate/scan/mock_run); Python 3.12, Node 20, ajv 5, lychee v1; fails on warnings; uses `grok_install_stub` from `scripts/`. |
| 6 | https://github.com/AgentMindCloud/awesome-grok-agents/tree/main/templates/hello-grok | hello-grok layout: `.env.example`, `README.md`, `grok-install.yaml`, `.grok/`, `tools/`. |
