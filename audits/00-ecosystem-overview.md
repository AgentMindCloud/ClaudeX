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

_(filled in unit 3)_

## 3. JSON Schema draft matrix

_(filled in unit 4)_

## 4. Standards-count coherence — 5 / 12 / 14

_(filled in unit 5)_

## 5. Release cadence snapshot

_(filled in unit 6)_

## 6. Safety-profile distribution

_(filled in unit 6)_

## 7. Docs drift observations

_(filled in unit 7)_

## 8. Phase 1 inventory corrections

_(filled in unit 7)_

## 9. Cross-cutting concerns

_(filled in unit 8)_
