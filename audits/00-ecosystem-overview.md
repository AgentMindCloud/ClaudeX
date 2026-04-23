# Ecosystem Overview — AgentMindCloud Grok + X Stack

- **Scope**: 12 repositories audited in Phase 1A (11 external + ClaudeX self-audit).
- **Snapshot date**: 2026-04-23.
- **Sources**: `audits/01-*.md` through `audits/12-*.md`. Every cross-cut claim below cross-references the source audit that verified it (e.g. *[→ 04, §6]*).
- **Honesty anchor**: `audits/97-methodology.md`. If a claim here is absent from a referenced source audit, it is wrong — please raise it.

This file is the cross-cut synthesis of the 12 per-repo audits. Its four companions:

- `audits/97-methodology.md` — how Phase 1A was run (reproducibility + evidence discipline).
- `audits/98-risk-register.md` — risks harvested from per-repo §6 / §10 / headline-finding sections, categorised.
- `audits/99-recommendations.md` — top-20 ecosystem-wide recommendations, merged from 12 × per-repo top-5 tables, ranked by leverage × cross-repo reach.
- `audits/_template.md` — the per-repo audit template.

The ecosystem described here is coherent at its ambition (spec-first, safety-aware, Grok-native, X-integrated) but fragmented at the seams: **four independent Grok API clients, two parallel safety-rule implementations, a draft-07/draft-2020 schema split between the two spec roots, and at least three documented version-number drifts**. No single finding is fatal; together they describe a young ecosystem where the next six-to-twelve weeks of coordination work has much higher leverage than the next new feature.

## 1. Dependency graph

Arrow semantics: `A --> B` means *B depends on / consumes A* (arrow points downstream). Every edge is sourced from a declaring file in the dependent repo's audit — see the `[→ NN, §3]` cross-reference on each edge.

### 1.1 ASCII (per-cluster)

```
Spec roots
----------
  grok-install (spec v2.14)                       [→ 01, §8]
      |
      +--> grok-install-cli (Py runtime)          [→ 03, §3 — pyproject `jsonschema>=4.21`]
      |       |
      |       +--> grok-install-action (JS/Sh)    [→ 04, §3 — `npm install -g grok-install-cli@2.14.0`*]
      |
      +--> grok-docs (MkDocs)                     [→ 05, §5 — sync-schemas.yml cron]
      |
      +--> grok-agents-marketplace (Next.js)      [→ 08, §3 — consumes featured-agents.json registry (inferred)]

  grok-yaml-standards (v1.2.0; 12 file types)      [→ 02, §8]
      |
      +--> vscode-grok-yaml (TS — see §9.C)        [→ 07, §3 (intended; repo is shell)]
      +--> awesome-grok-agents (Py templates)      [→ 06, §3 — schema references (inferred)]
      +--> grok-docs (schema republishing)         [→ 05, §5 — sync-schemas.yml cron]

xAI-SDK layer (parallel track; does NOT depend on grok-install)
---------------------------------------------------------------
  xAI SDK 4.20 ----> grok-build-bridge            [→ 09, §3 — xai-sdk>=1.0]
  xAI SDK 4.20 ----> grok-agent-orchestra         [→ 10, §3 (intended; repo is shell)]

X-platform surface (orthogonal to spec ecosystem)
-------------------------------------------------
  X API v2 + xAI Grok ----> x-platform-toolkit    [→ 11, §3 — shared/{grok-client,x-api-client}]

Registry flow
-------------
  awesome-grok-agents::featured-agents.json ----> grok-agents-marketplace
                                                  [→ 06, §8 & → 08, §3 — inferred; both ends unverified on WebFetch]

Self / meta
-----------
  ClaudeX ----(reads)----> all 11 external repos via WebFetch   [→ 12, §3]
```

`*` The `grok-install-action → grok-install-cli` edge via `npm install -g grok-install-cli@2.14.0` is **unresolved**: the CLI repo is Python (`pyproject.toml`, typer, ruff) with no npm package visible. Either an undocumented npm wrapper exists or the action pins a package that isn't the audited Python CLI. Full treatment in §9 and `audits/04-grok-install-action.md` headline risk.

### 1.2 Mermaid

```mermaid
flowchart TD
    classDef spec fill:#cfd,stroke:#060,color:#000
    classDef runtime fill:#ccf,stroke:#006,color:#000
    classDef consumer fill:#fec,stroke:#a60,color:#000
    classDef peer fill:#eee,stroke:#666,color:#000
    classDef shell fill:#fbb,stroke:#900,color:#000
    classDef external fill:#fff,stroke:#333,stroke-dasharray:4 2,color:#000

    GI["grok-install<br/>spec v2.14"]:::spec
    GYS["grok-yaml-standards<br/>v1.2.0 · 12 types"]:::spec
    GIC["grok-install-cli<br/>Py · v0.1.0*"]:::runtime
    GIA["grok-install-action<br/>v1.0.0 · JS"]:::runtime
    GD["grok-docs<br/>MkDocs"]:::consumer
    AGA["awesome-grok-agents<br/>10 templates"]:::consumer
    GAM["grok-agents-marketplace<br/>Next.js · grokagents.dev"]:::consumer
    VGY["vscode-grok-yaml<br/>(shell repo)"]:::shell
    GBB["grok-build-bridge<br/>Py · dual-safety"]:::peer
    GAO["grok-agent-orchestra<br/>(shell repo)"]:::shell
    XPT["x-platform-toolkit<br/>20 tools · 40% live"]:::peer
    CX["ClaudeX<br/>meta · this repo"]:::peer

    XAI["xAI SDK 4.20<br/>grok-4.20-0309"]:::external
    XAPI["X API v2"]:::external

    GI --> GIC
    GIC -.npm-vs-Py drift.-> GIA
    GI --> GD
    GI --> GAM
    GYS --> VGY
    GYS --> AGA
    GYS --> GD
    AGA -.featured-agents.json.-> GAM

    XAI --> GBB
    XAI --> GAO
    XAI --> XPT
    XAPI --> XPT

    CX -.WebFetch audit.-> GI
    CX -.WebFetch audit.-> GYS
    CX -.WebFetch audit.-> GIC
    CX -.WebFetch audit.-> GIA
    CX -.WebFetch audit.-> GD
    CX -.WebFetch audit.-> AGA
    CX -.WebFetch audit.-> VGY
    CX -.WebFetch audit.-> GAM
    CX -.WebFetch audit.-> GBB
    CX -.WebFetch audit.-> GAO
    CX -.WebFetch audit.-> XPT
```

`*` CLI version `0.1.0` in `pyproject.toml` vs. action's `2.14.0` pin — see §8 inventory corrections and `audits/03-grok-install-cli.md` §8.

### 1.3 Legend + counts

| Cluster | Repos | Role |
|---------|-------|------|
| Spec roots | `grok-install`, `grok-yaml-standards` | Define the vocabulary + schemas. |
| Runtime | `grok-install-cli`, `grok-install-action` | Execute / certify against the spec. |
| Consumers | `grok-docs`, `awesome-grok-agents`, `grok-agents-marketplace` | Publish, exemplify, or market the spec. |
| xAI-SDK peers | `grok-build-bridge`, `grok-agent-orchestra` | Parallel track; depend on xAI SDK, not grok-install. |
| Orthogonal | `x-platform-toolkit` | Consumes xAI + X API directly; no grok-install link. |
| Shell repos | `vscode-grok-yaml`, `grok-agent-orchestra` | LICENSE + README only at time of audit. |
| Meta | `ClaudeX` | Hosts the Phase 1A audits. |

Two repos appear in two clusters: `grok-agent-orchestra` is both an xAI-SDK peer (by intent) and a shell repo (by current state); `vscode-grok-yaml` is a shell repo targeting the consumer cluster.

## 2. Spec-version pin matrix

What each repo declares or pins, across the three version axes that matter: the **grok-install spec**, the **grok-install-cli package**, and the **grok-yaml-standards** file-type standards catalogue. "—" = not applicable to this repo's role.

| Repo | grok-install spec | grok-install-cli | grok-yaml-standards | Own version | Source |
|------|-------------------|------------------|---------------------|-------------|--------|
| `grok-install` | **v2.14** shipped; v2.13 + v2.12 retained side-by-side | — | — | tracks spec | [→ 01, §2 spec/v2.14/, §8] |
| `grok-yaml-standards` | extends grok-install.yaml | — | **v1.2.0** shipped | v1.2.0 (2026-04-17) | [→ 02, §8, CHANGELOG] |
| `grok-install-cli` | implicit v2.14 target (jsonschema>=4.21; schema URL usage unverified) | **`0.1.0`** in `pyproject.toml`; **no GitHub releases** | not directly referenced | 0.1.0 | [→ 03, §8, pyproject.toml] |
| `grok-install-action` | v2.14 (via CLI) | pins CLI **`2.14.0`** via `npm install -g grok-install-cli@${{ inputs.cli-version }}` | — | v1.0.0 (2026-04-21) | [→ 04, §3 action.yml, §8] |
| `grok-docs` | advertises **v2.12** (lags spec by 2 minor) | — | syncs v1.2.0 daily (03:00 UTC cron) | no version | [→ 05, §1, §5 sync-schemas.yml] |
| `awesome-grok-agents` | accepts **v2.12 OR v2.13 OR v2.14** in template `grok-install.yaml` (CI `spec-version` job) | validates via in-repo `grok_install_stub/`, not real CLI | implicit (templates use 12 file types) | no releases | [→ 06, §5, §8] |
| `vscode-grok-yaml` | (intended, not shipped) | (intended) | landing says "**14** standards" | repo = shell | [→ 07, §1 landing desc] |
| `grok-agents-marketplace` | v2.14 "Visuals Renderer" in README | — | — | v0.1.0 | [→ 08, §8, package.json] |
| `grok-build-bridge` | decoupled — own `bridge.schema.json` | not a consumer of grok-install-cli | — | v0.1.0; uses model ID `grok-4.20-0309` | [→ 09, §1, §8] |
| `grok-agent-orchestra` | (intended via xAI SDK) | — | — | 1-commit shell | [→ 10, §8] |
| `x-platform-toolkit` | — | — | — | no versioning; 4 commits | [→ 11, §8] |
| `ClaudeX` | — | — | — | no version | [→ 12, §8] |

### Version-coherence findings

1. **CLI version mismatch** — `grok-install-cli/pyproject.toml` says `version = "0.1.0"` and has no GitHub release tags, but `grok-install-action/action.yml` hard-defaults to pinning CLI `2.14.0`. One of three things is true, each blocking reproducible installs: (a) a separate PyPI artefact at 2.14.0 exists and the `main` branch's `pyproject.toml` lags; (b) the action pins a version the repo has never produced; (c) an npm package named `grok-install-cli@2.14.0` exists, separate from the Python CLI. Unresolved — needs PyPI + npm registry check. [→ 03, §1 & §10; → 04, §1 & §10]

2. **grok-docs lags 2 minor versions** — docs advertise v2.12; spec is at v2.14. 5 of 12 standards documented. [→ 05, §4]

3. **Multi-version tolerance in templates** — `awesome-grok-agents` CI accepts v2.12/v2.13/v2.14 simultaneously. Useful for contributors, but means templates never pressure-test the latest spec. [→ 06, §5, §8]

4. **grok-install's own v2.14 validation is 1-of-6** — the `schema-v2-14` CI job validates only `examples/janvisuals/grok-install.yaml`; the five other top-level examples are still validated against v2.13 (draft-07). The v2.14 migration is half-done at the source. [→ 01, §1, §5]

5. **xAI-SDK layer is decoupled** — `grok-build-bridge` and `grok-agent-orchestra` neither consume nor produce `grok-install.yaml`; they pin to xAI SDK model IDs like `grok-4.20-0309` instead. This is a *design* choice, not drift — but it means "ecosystem-wide" changes to `grok-install` have no leverage over the xAI-SDK cluster. [→ 09, §3; → 10, §3]

## 3. JSON Schema draft matrix

The ecosystem runs on two JSON Schema drafts simultaneously. Drift is acknowledged in `grok-yaml-standards/standards-overview.md` and deferred to v1.3; until then every validator in the chain has to tolerate both.

| Repo | Schema(s) declared | Draft | Validator in CI | Source |
|------|--------------------|-------|-----------------|--------|
| `grok-install` | `schemas/v2.14/schema.json` | **draft-2020-12** | `ajv-cli` + `ajv-formats` (Node 20) — `schema-v2-14` job (**janvisuals only**) | [→ 01, §5 validate.yml, §7] |
| `grok-install` | `schemas/grok-install-v2.13.schema.json` (retained) | draft-07 | `ajv-cli` — `schema-v2-13` job (all 6 examples) | [→ 01, §5] |
| `grok-install` | `schemas/featured-agents-v1.schema.json`, `trending-v1.schema.json` | draft-07 (inferred from naming/adjacency) | (not audited) | [→ 01, §2] |
| `grok-yaml-standards` | 12 × `schemas/grok-<name>.json` | **draft-07** (all 12) | `ajv-cli@5.0.0 + ajv-formats` + Python schema-smoke asserting `$schema` = draft-07 | [→ 02, §5 validate-schemas.yml, §6] |
| `grok-install-cli` | (consumes external schemas at runtime) | not verified — `jsonschema>=4.21` supports both | pytest via `test_validator.py` (coverage unknown) | [→ 03, §3, §10] |
| `grok-install-action` | (delegates to CLI + uses ajv for internal report schema) | not verified | self-integration test on `tests/sample-agent` | [→ 04, §5] |
| `grok-docs` | mirrors `grok-yaml-standards/schemas/` to `docs/assets/schemas/` daily | draft-07 (mirror of upstream) | no schema validation in site CI | [→ 05, §5 sync-schemas.yml] |
| `awesome-grok-agents` | validates `featured-agents.json` against registry schema | draft-07 (schema from `grok-install` root) | `ajv-cli@5 + ajv-formats@3` — `schema` job | [→ 06, §3, §5] |
| `grok-build-bridge` | `grok_build_bridge/schema/bridge.schema.json` (own) | **draft-2020-12** | `jsonschema.Draft202012Validator` — `schema-check` job | [→ 09, §5 ci.yml, §7] |
| `grok-agents-marketplace` | runtime validation via `zod ^4.3.6` (not JSON Schema) | N/A | `vitest` (not schema-layer) | [→ 08, §3] |
| `vscode-grok-yaml` | (intended consumer; no code) | — | — | [→ 07, §1] |
| `grok-agent-orchestra` | (no code) | — | — | [→ 10, §1] |
| `x-platform-toolkit` | no schemas | — | no CI | [→ 11, §5] |

### Draft-split findings

1. **Two spec roots disagree on drafts.** `grok-install` v2.14 → draft-2020-12; `grok-yaml-standards` v1.2.0 → draft-07. The disagreement is documented and deferred: `grok-yaml-standards/standards-overview.md` plans migration to draft-2020-12 in v1.3. Until then, any tool validating *both* schema families (the hoped-for `vscode-grok-yaml` extension, a unified CLI validator) must run two draft engines. [→ 02, §1, §6; → 01, §7]

2. **Only 1 of 3 active Python validators is explicit about draft-2020-12.** `grok-build-bridge` hard-binds to `Draft202012Validator` and aligns with `grok-install` v2.14 on purpose. `grok-install-cli` uses `jsonschema>=4.21` (supports both, but the CLI source doesn't document which is called). `awesome-grok-agents` uses `ajv-cli@5` which honours the schema's `$schema` keyword. Unverified whether `grok-install-cli` picks the draft from the schema file or hard-codes one. [→ 09, §5; → 03, §3, §10; → 06, §5]

3. **CI coverage of the draft-2020 migration is thin.** Only two CI jobs anywhere in the ecosystem actively exercise draft-2020-12: `grok-install/.github/workflows/validate.yml` (1 of 6 examples) and `grok-build-bridge/.github/workflows/ci.yml` (5 template YAMLs + 1 bridge.yaml). `grok-yaml-standards` and `grok-docs` are still pure draft-07. [→ 01, §5; → 09, §5; → 02, §5; → 05, §5]

## 4. Standards-count coherence — 5 / 12 / 14

Three different numbers for "how many Grok YAML standards are there" appear across the ecosystem. The authoritative count is **12**, established in `grok-yaml-standards/version-reconciliation.md` — which was created explicitly to retire earlier 8-count and 14-count claims.

| Claim | Where it appears | Count | Status |
|-------|------------------|-------|--------|
| "12 standards" (8 core + 4 extensions) | `grok-yaml-standards/standards-overview.md`, `version-reconciliation.md`, `README.md`, CHANGELOG v1.2.0 | **12** | **Authoritative.** grok-cache.yaml and grok-auth.yaml explicitly declined; process for future additions via `discussion/new-standard` issue. [→ 02, §4, §11 row 2] |
| "5 file types" (grok-install, grok-agent, grok-workflow, grok-security, grok-prompts) | `grok-docs/mkdocs.yml` nav → Spec reference | **5** | **Drift.** 7 of 12 standards (`grok-config`, `grok-update`, `grok-test`, `grok-docs`, `grok-tools`, `grok-deploy`, `grok-analytics`, `grok-ui` minus the 3 in the 5-list) are undocumented on the published docs site. [→ 05, §4, §11 row 2] |
| "14 YAML specifications / standards" | `grok-install-action/README.md` (validation claim); `vscode-grok-yaml` landing description ("all 14 YAML standards") | **14** | **Drift.** Predates or ignores `version-reconciliation.md`, which explicitly declined the 14-count. Reconciliation doc provides ready-to-use PR language. [→ 04, §4; → 07, §1] |

### Distribution of the drift

- **Internally consistent in grok-yaml-standards** (count = 12). Every artefact in the repo agrees.
- **grok-docs undercounts** at 5 (41.7% coverage on the user-facing docs site).
- **Two consumer surfaces overcount at 14** — notably the GitHub Marketplace action README and the VS Code extension's landing page, both of which are the primary adoption touchpoints. Credibility cost lands hardest here.
- **grok-install** itself says nothing about the 12-count (it's the outer spec, not the standards catalogue) — no drift, but no endorsement either.

The drift is cheap to fix: `version-reconciliation.md` already contains PR-ready wording. The cross-cutting recommendation (see `audits/99-recommendations.md`) is to sync all ecosystem surfaces to the canonical 12 and wire a release-dispatch so future bumps can't redrift.

## 5. Release cadence snapshot

Snapshot on 2026-04-23. Every number below is sourced from the repo's GitHub landing-page counters or release page; cross-references point to the audit row where the number was recorded.

| Repo | Commits | Releases | ★ / Forks | Issues / PRs (open) | Latest release | Source |
|------|:-:|:-:|:-:|:-:|---|---|
| `grok-install` | 259 | v2.14 (+ v2.13 & v2.12 retained) | 1 / 0 | 0 / 0 | v2.14 (recent; exact date not fetched) | [→ 01, §11 row 1] |
| `grok-yaml-standards` | (not recorded) | **3 in 2 days** (v1.0.0, v1.1.0 on 2026-04-16; v1.2.0 on 2026-04-17) | 1 / 0 | 2 / 2 | v1.2.0 (2026-04-17) | [→ 02, §11 row 1, row 6] |
| `grok-install-cli` | (not recorded) | **none** — `pyproject.toml` = 0.1.0 | 0 / 0 | 0 / 0 | — | [→ 03, §11 row 1, row 2] |
| `grok-install-action` | (not recorded) | v1.0.0 (2026-04-21) | 0 / 0 | 0 / 0 | v1.0.0 | [→ 04, §11 row 1] |
| `grok-docs` | **5 total** | none | 1 / 0 | 0 / 0 | — | [→ 05, §11 row 1] |
| `awesome-grok-agents` | 10 | none | 1 / 0 | 0 / 2 | — (registry `featured-agents.json v1.0` updated 2026-04-21) | [→ 06, §11 row 1, row 3] |
| `vscode-grok-yaml` | 7 | none | 0 / 0 | 0 / 1 | — (shell repo) | [→ 07, §11 row 1] |
| `grok-agents-marketplace` | 11 | none (`package.json` = 0.1.0) | 0 / 0 | 0 / **12** | — | [→ 08, §11 row 1] |
| `grok-build-bridge` | 13 | none (`pyproject.toml` = 0.1.0) | 1 / 0 | 0 / 0 | — | [→ 09, §11 row 1] |
| `grok-agent-orchestra` | **1 total** | none | 1 / 0 | 0 / 0 | — (shell repo) | [→ 10, §11 row 1] |
| `x-platform-toolkit` | 4 | none | 1 / 0 | 0 / 0 | — | [→ 11, §11 row 1] |
| `ClaudeX` | 16 (at self-audit) | none | (private-ish; local) | — | — | [→ 12, §11 row 6] |

### Cadence observations

- **Hottest repo by PR volume**: `grok-agents-marketplace` with **12 open PRs** — an order of magnitude more than any other ecosystem repo (next highest is 2 PRs). Suggests active external contribution or Copilot-driven automation; no visible reviewer cadence. [→ 08, §1, §9 row 2]
- **Hottest repo by release velocity**: `grok-yaml-standards` (3 releases in 2 days on 2026-04-16/17).
- **Stalest active repo**: `grok-install-cli` — positioned as the primary runtime, but no releases, version stuck at 0.1.0, 0 issues and 0 PRs despite the action and marketplace depending on it. Combined with the npm-vs-Python drift this is the ecosystem's single thinnest load-bearing repo.
- **"Shell repos"**: `vscode-grok-yaml` (7 commits, no source) and `grok-agent-orchestra` (1 commit, no source) are marketing-present but development-absent. Both describe shipped capabilities that don't exist yet.
- **Commit count as maturity signal**: `grok-install` (259) sits one to two orders of magnitude above the rest (1 to 16). The spec root was built before most of the downstream surfaces.

## 6. Safety-profile distribution

The ecosystem advertises a **tripartite safety model** — `strict` / `standard` / `permissive` — across `grok-install/SECURITY.md` ("Enhanced Safety & Verification 2.0"), `grok-yaml-standards/grok-security` (the catalogue entry that operationalises it), and `grok-install-cli/src/grok_install/safety/` (the CLI enforcement). The only repo that surfaces the distribution across real agents is `awesome-grok-agents` via `featured-agents.json`.

### 6.1 Distribution across the 10 featured agents

| Profile | Count | Example agents | Notes |
|---------|:-:|---|---|
| `strict` | **6** | `reply-engagement-bot`, `code-reviewer`, … (full list in `awesome-grok-agents/featured-agents.json`) | Used for every agent with external write access (X posting, code changes). Majority profile. |
| `standard` | **4** | (4 agents) | Used for read-mostly agents. |
| `permissive` | **0** | — | **No exemplar** in the gallery. |

Source: [→ 06, §6, §11 row 3 — `featured-agents.json` v1.0].

### 6.2 The "missing permissive exemplar" finding

The tripartite model needs a reference instance at each level for the profiles to be usable. With 0 permissive examples:

- New adopters cannot calibrate what "permissive" should look like in practice.
- There's no way to round-trip the `grok-install-cli` safety scanner against a permissive-profile agent (any test template is necessarily strict or standard).
- The rubric in `grok-yaml-standards/grok-security` cannot be verified against a shipped instance.

### 6.3 Where the safety-profile is defined vs. enforced

| Repo | Role | What it contributes |
|------|------|---------------------|
| `grok-install` (spec) | Defines the model | `SECURITY.md` — Enhanced Safety 2.0: pre-install file scan, minimum-keys, halt-on-anomaly, "Verified by Grok" badge. [→ 01, §6] |
| `grok-yaml-standards` (catalogue) | Categorises the 12 standards by security level (Low → Critical) in `standards-overview.md`; `grok-security.yaml` is the operational catalogue entry. [→ 02, §6] |
| `grok-install-cli` (runtime) | Enforces at scan/install time — `src/grok_install/safety/rules.py` + `scanner.py`, called via `grok-install scan` subcommand. [→ 03, §6] |
| `grok-build-bridge` (peer) | Implements its own dual-layer safety — `_patterns.py` (static regex) + Grok-powered LLM audit in `xai_client.py`. [→ 09, §1, §6] |
| `awesome-grok-agents` (gallery) | Asserts a profile per template via `featured-agents.json`; validates via in-repo `scan_template.py` (fails on warnings). [→ 06, §6] |
| `grok-install-action` (CI surface) | Surfaces `safety-score (0-100)` output on PR comments; delegates enforcement to the CLI. [→ 04, §8] |

At least **three independent static-regex / pattern implementations** exist: `grok-install-cli/safety/rules.py`, `grok-build-bridge/_patterns.py`, `awesome-grok-agents/scripts/scan_template.py`. None share a source module. See §9 for the "shared safety-rules package" cross-cutting concern.

## 7. Docs drift observations

_(filled in unit 7)_

## 8. Phase 1 inventory corrections

_(filled in unit 7)_

## 9. Cross-cutting concerns

_(filled in unit 8)_
