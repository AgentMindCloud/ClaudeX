# Risk Register — Phase 1A Ecosystem Audit

- **Scope**: risks harvested from each per-repo audit's §6 (Security & safety signals), §10 (Open questions), and headline-findings (§1). Cross-referenced as `[→ NN, §s]`.
- **Snapshot**: 2026-04-23. Re-assess at each phase boundary.
- **Severity scale**: S1 (critical — blocks reproducible use / introduces security exposure), S2 (high — causes drift or silent degradation), S3 (medium — hygiene / credibility), S4 (low — future-facing or cosmetic).
- **Likelihood scale**: L-high / L-med / L-low.
- **Status legend**: `open` · `mitigated-partial` · `deferred` · `needs-info`.

Companion files: `audits/00-ecosystem-overview.md` (for the cross-cutting context), `audits/99-recommendations.md` (for the fix pipeline).

Risks are grouped into six categories. Row IDs use a per-category prefix (`SEC-`, `SUP-`, `GOV-`, `VER-`, `DOC-`, `UNV-`) so they can be referenced from `99-recommendations.md`.

| § | Category | Why this grouping | Row count |
|---|----------|-------------------|:-:|
| 1 | Security & runtime safety | Static-scan gaps, LLM-audit fragility, secret-handling surfaces. | 5 |
| 2 | Supply chain & dependency hygiene | Pinning discipline, action-tag pinning, lockfile presence. | 5 |
| 3 | Governance & single-points-of-failure | Solo-maintainer channels, missing disclosure policies, unreviewed PR queues. | 5 |
| 4 | Version & schema coherence | Spec / CLI / schema-draft drifts; multi-version tolerance. | 5 |
| 5 | Documentation drift | Count mismatches, version-number lag, shell-repo descriptions. | 4 |
| 6 | Unverifiable or deferred claims | Capability claims that the audit couldn't confirm without clone / org MCP / maintainer input. | 5 |
| | **Total** | | **29** |

## 1. Security & runtime safety

| # | Risk | Severity | Likelihood | Affected repos | Source | Status |
|---|------|:-:|:-:|----------------|--------|:-:|
| SEC-1 | LLM-audit safety layer in `build-bridge` accepts untrusted YAML and feeds it to a model — prompt-injection can subvert or bypass the audit verdict. No prompt-isolation or output-shape validation documented. | S1 | L-med | grok-build-bridge | [→ 09, §1, §6] | open |
| SEC-2 | `pip-audit` runs in CI but is non-blocking (`continue-on-error: true`) — vulnerable transitive deps land in main without gating. | S2 | L-med | grok-install-cli, grok-build-bridge | [→ 03, §5, §6; → 09, §5] | open |
| SEC-3 | No secret-scanning (gitleaks / trufflehog / GitHub native) on any repo in the ecosystem — a committed token would not be caught at PR time. | S2 | L-med | all 12 repos | [→ 03, §5, §6; → 09, §6] | open |
| SEC-4 | `x-platform-toolkit` ships single-file HTML tools that take user-supplied X / Grok API tokens; storage scope (memory vs `localStorage`), lifetime, and exfiltration surface are undocumented. | S2 | L-low | x-platform-toolkit | [→ 11, §6] | open |
| SEC-5 | `grok-install-action` badge-commit bot pushes directly to `main` (no PR, no required-review gate) — a compromised action-token would have unmediated write access to the default branch. | S2 | L-low | grok-install-action | [→ 04, §6] | open |

## 2. Supply chain & dependency hygiene

| # | Risk | Severity | Likelihood | Affected repos | Source | Status |
|---|------|:-:|:-:|----------------|--------|:-:|
| SUP-1 | GitHub Actions pinned by major tag (`actions/checkout@v4`, etc.) rather than commit SHA across the entire ecosystem — a compromised or moved tag executes arbitrary code with workflow permissions on every consumer. | S2 | L-med | grok-install, grok-yaml-standards, grok-install-cli, grok-install-action, grok-docs, awesome-grok-agents, grok-agents-marketplace, grok-build-bridge | [→ 01, §6; → 02, §5, §6; → 03, §5; → 04, §6; → 05, §5; → 06, §6; → 08, §5; → 09, §5] | open |
| SUP-2 | `grok-agents-marketplace` runtime deps use caret ranges (`^x.y.z`) — minor-version drift on every install; the most-active repo in the ecosystem is also the loosest-pinned. | S2 | L-med | grok-agents-marketplace | [→ 08, §1, §6] | open |
| SUP-3 | `grok-install-cli` and `grok-build-bridge` declare `>=` lower bounds in `pyproject.toml` (no upper cap) — future major releases of transitive Python deps will silently break installs and reproducibility. | S2 | L-med | grok-install-cli, grok-build-bridge | [→ 03, §6; → 09, §6] | open |
| SUP-4 | `grok-install-action` invokes `npm install -g grok-install-cli@2.14.0` at runtime — the `2.14.0` pin is not guarded by a lockfile, and (separately, see VER-3) the underlying CLI is a Python project whose latest tag is `0.1.0`. | S2 | L-med | grok-install-action | [→ 04, §6] | open |
| SUP-5 | `x-platform-toolkit` has no CI of any kind — no dependency scanning, no lint, no build verification; supply-chain regressions are invisible. | S3 | L-high | x-platform-toolkit | [→ 11, §5] | open |

## 3. Governance & single-points-of-failure

| # | Risk | Severity | Likelihood | Affected repos | Source | Status |
|---|------|:-:|:-:|----------------|--------|:-:|
| GOV-1 | Solo maintainer (@JanSol0s) on the spec root; no `SECURITY.md`, no private disclosure channel — the only documented routes are filing a public repo issue or DMing on X. Bus-factor 1; security-issue exposure window starts public. | S2 | L-high | grok-install (and by reach, the entire downstream chain) | [→ 01, §4, §6] | open |
| GOV-2 | 12 open PRs on `grok-agents-marketplace`, none reviewed; no `CODEOWNERS`. The most-active repo has no triage capacity, so contributor PRs stall and forks proliferate. | S2 | L-high | grok-agents-marketplace | [→ 08, §1, §5, §9 row 2] | open |
| GOV-3 | `vscode-grok-yaml` and `grok-agent-orchestra` are LICENSE+README only — no source, no CI, no issues template. The marketing-polished surface implies a working product that does not exist. | S3 | L-high | vscode-grok-yaml, grok-agent-orchestra | [→ 07, §1, §2; → 10, §1, §2] | open |
| GOV-4 | Multiple repos lack one or more of `SECURITY.md` / `CONTRIBUTING.md` / `CODE_OF_CONDUCT.md` / `CODEOWNERS` (full breakdown in `audits/00-ecosystem-overview.md` §7.2). Disclosure path and contributor expectations are inconsistent. | S3 | L-high | most ecosystem repos | [→ 00, §7.2] | open |
| GOV-5 | `ClaudeX` (this very audit's host repo) has no `LICENSE`, and `CLAUDE.md` `§Primary Repos` is still the upstream template placeholder — the repo cannot be redistributed and its own context is partially fictional. | S3 | L-high | ClaudeX | [→ 12, §1, §6] | open |

## 4. Version & schema coherence

| # | Risk | Severity | Likelihood | Affected repos | Source | Status |
|---|------|:-:|:-:|----------------|--------|:-:|
| VER-1 | `grok-install` v2.14 schema validates only **1 of 6** in-repo examples (`janvisuals`); the spec advertises a contract its own corpus violates. Downstream validators built against the spec will fail on official samples. | S1 | L-high | grok-install (and every consumer that re-uses the examples) | [→ 01, §1, §5] | open |
| VER-2 | `grok-yaml-standards` is on JSON Schema **draft-07**; `grok-install` v2.14 is on **draft-2020-12**. The two spec roots disagree on the meta-schema; alignment explicitly deferred to v1.3 in `standards-overview.md`. | S2 | L-med | grok-yaml-standards, grok-install | [→ 02, §6; → 01, §7] | open |
| VER-3 | `grok-install-cli` `pyproject.toml` is at `0.1.0` and is a Python project; `grok-install-action` pins it via `npm install -g grok-install-cli@2.14.0`. Either the action installs an unrelated npm package, or the documented install path does not actually work. (See also UNV-1.) | S1 | L-high | grok-install-cli, grok-install-action | [→ 03, §1, §8; → 04, §1] | open |
| VER-4 | `grok-docs` advertises spec **v2.12**; current spec is **v2.14**. Two-minor-version lag in the canonical documentation site. | S2 | L-high | grok-docs | [→ 05, §1, §4] | open |
| VER-5 | `awesome-grok-agents` accepts entries declaring **v2.12, v2.13, or v2.14** simultaneously, with no migration policy or deprecation horizon — the registry normalises drift instead of resolving it. | S2 | L-med | awesome-grok-agents | [→ 06, §5, §8] | open |

## 5. Documentation drift

| # | Risk | Severity | Likelihood | Affected repos | Source | Status |
|---|------|:-:|:-:|----------------|--------|:-:|
| DOC-1 | "5 / 12 / 14 standards" phrasing inconsistency: `grok-install-action` README and `vscode-grok-yaml` landing claim "14 YAML specifications", `grok-docs` covers 5, `version-reconciliation.md` enumerates 12. New users cannot tell which number is canonical. | S2 | L-high | grok-yaml-standards, grok-install-action, grok-docs, vscode-grok-yaml | [→ 02, §4; → 04, §4; → 05, §4; → 07, §1] | open |
| DOC-2 | `grok-docs` documents **5 of 12** ratified standards; the remaining 7 have no published reference page. The "official documentation site" is structurally incomplete. | S2 | L-high | grok-docs | [→ 05, §4] | open |
| DOC-3 | `vscode-grok-yaml` ("Production-grade VS Code extension for Grok YAML") and `grok-agent-orchestra` ("Multi-agent orchestration with Lucas safety veto") describe products that don't exist — both repos are LICENSE+README only. Description-vs-reality mismatch. | S3 | L-high | vscode-grok-yaml, grok-agent-orchestra | [→ 07, §1, §6; → 10, §1, §6] | open |
| DOC-4 | `grok-install` README is salesy/marketing-style rather than a reference for the v2.14 contract — adopters read it expecting normative behaviour and instead get positioning copy. | S3 | L-med | grok-install | [→ 01, §4] | open |

## 6. Unverifiable or deferred claims

| # | Risk | Severity | Likelihood | Affected repos | Source | Status |
|---|------|:-:|:-:|----------------|--------|:-:|
| UNV-1 | The advertised install path (`npm install -g grok-install-cli@2.14.0`) does not match the underlying CLI's packaging (Python `pyproject.toml` at `0.1.0`). Without cloning and running both, the audit cannot confirm whether the action installs the documented tool. | S1 | L-high | grok-install-action, grok-install-cli | [→ 04, §1, §10; → 03, §1, §10] | needs-info |
| UNV-2 | "Verified by Grok" badge: rendering path, signing source, and revocation semantics are not documented in `grok-install` — adopters embed the badge without a verifiable assertion behind it. | S3 | L-med | grok-install | [→ 01, §10] | needs-info |
| UNV-3 | "Lucas safety veto" (advertised on `grok-agent-orchestra`): no source defines what Lucas is, what veto authority it carries, or how it interacts with the strict / standard / permissive profiles. Branding without a behavioural contract. | S3 | L-med | grok-agent-orchestra | [→ 10, §10] | needs-info |
| UNV-4 | Whether `grok-install-cli`'s safety rules are a re-implementation of the `grok-yaml-standards/grok-security` schema or a divergent ruleset is not stated — risks two safety surfaces drifting apart unobserved. | S3 | L-med | grok-install-cli, awesome-grok-agents | [→ 03, §10; → 06, §10] | needs-info |
| UNV-5 | `grok-install-cli` claims "high coverage" but no coverage % is published and CI does not enforce a `--cov-fail-under` threshold (contrast with `grok-build-bridge` at 85). The coverage claim is unverifiable from the public surface. | S3 | L-med | grok-install-cli | [→ 03, §10] | needs-info |
