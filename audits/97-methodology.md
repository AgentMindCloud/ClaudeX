# Audit Methodology — Phase 1A

> Reproducibility + honesty anchor. Started as a Phase-1A-opening skeleton; completed at phase close once the 12 per-repo audits and three other cross-cut files (`00`, `98`, `99`) had been written.

## Purpose

Audit 12 AgentMindCloud repos (11 external + this one, ClaudeX) at orientation-grade depth, producing:
- One audit per repo (`audits/01–12-<repo>.md`).
- Cross-cutting artefacts: ecosystem overview, risk register, top-20 recommendations.

## Access mode

**Primary: WebFetch** against `github.com/AgentMindCloud/<repo>/...` and `raw.githubusercontent.com/...`.
**Fallback: clone-on-demand** — user clones a specific repo into `/home/user/grok-ecosystem/<repo>/` only when WebFetch is insufficient for that repo.
**Not used: widening GitHub MCP scope** — would require a `settings.json` change the user has not authorised.

### Why WebFetch is enough for Phase 1A
- Every repo is public (Apache 2.0) and ≤1★ with <260 commits.
- Orientation-grade audit requires 8–15 targeted file reads per repo — tractable via WebFetch.
- Deep code quality / test coverage is deferred to later phases where it's actionable.

### What WebFetch cannot verify
- Full-tree grep / cross-repo symbol search.
- Commit archaeology beyond tree views.
- Issue/PR triage volume.
- Secret-scanning at scale (only line-of-sight observation in files actually fetched).

## Evidence discipline (non-negotiable)

Every per-repo audit must end with an **Evidence log** (§11) listing every URL fetched and what was read from it. Any claim in the audit that isn't traceable to that log must carry a tag:

- `(WebFetch-limited)` — could be verified with a clone but wasn't.
- `(needs clone)` — cannot be verified by WebFetch at all.
- `(needs org MCP)` — would require GitHub MCP scope widening.
- `(needs maintainer input)` — only the maintainer can resolve.
- `(inferred)` — based on adjacent signals, not direct observation.

Minimum 3 URLs per audit. Exception: `10-grok-agent-orchestra.md` (upstream has 1 commit; shallow is expected).

## Security disclosure policy

If a concrete security issue (hardcoded credential, vulnerability pattern, missing auth) is spotted during WebFetch:

1. **Stop** writing to the audit file.
2. Section §6 in the audit says `"Issue raised privately to user — details not published here."`.
3. Details are reported to the user in chat only.
4. No speculative disclosure or deep-fetch of the issue on the public branch.

This matches the user's instruction at plan-mode approval.

## Audit order rationale

Dependency-aware ordering so each audit benefits from the prior:
1. Spec roots (`grok-install`, `grok-yaml-standards`) define the vocabulary.
2. Runtime (`grok-install-cli`, `grok-install-action`) reveals how the spec executes.
3. Docs (`grok-docs`) surfaces drift between spec and published reference.
4. Consumers (`awesome-grok-agents`, `vscode-grok-yaml`, `grok-agents-marketplace`) show real-world use.
5. xAI-SDK layer (`grok-build-bridge`, `grok-agent-orchestra`) is a separate cluster.
6. `x-platform-toolkit` is largely orthogonal; audit late.
7. `ClaudeX` self-audit is last, local, cheap.

## Checkpoints

Three mandatory pauses surface to the user:
- **CP-A** after iter 3: spec vocabulary captured; early 404/private-repo detection.
- **CP-B** after iter 8: clone-on-demand decision for remaining 4 repos.
- **CP-C** after iter 13: reconcile audits vs. Phase 1 inventory before synthesis.

## What is NOT inspected in this phase

Deferred to later phases:
- Dynamic testing / execution of any code.
- Benchmarking performance or cost.
- Dependency CVE scanning via external DBs.
- Issue/PR backlog triage.
- Commit-by-commit provenance analysis.
- Cross-repo grep for duplicated safety-profile logic (would need clone).

## Evidence-log rows per repo

The column header is "Evidence-log rows" rather than "URLs fetched" because audit 12 (ClaudeX self-audit) cites local file paths and shell commands instead of URLs. For audits 01–11 the count is the number of distinct WebFetch URLs; for 12 it is the number of local-evidence rows.

| Audit | Evidence-log rows | Notes |
|-------|:-:|-------|
| 01-grok-install | 10 | Spec root; deepest fetch budget. |
| 02-grok-yaml-standards | 7 | |
| 03-grok-install-cli | 8 | Pulled in two CI workflow URLs + `pyproject.toml`. |
| 04-grok-install-action | 5 | Action surface is small. |
| 05-grok-docs | 5 | MkDocs config + sync workflow + landing pages. |
| 06-awesome-grok-agents | 6 | |
| 07-vscode-grok-yaml | 3 | Shell repo (LICENSE + README only); minimum-3 floor met exactly. |
| 08-grok-agents-marketplace | 5 | |
| 09-grok-build-bridge | 6 | |
| 10-grok-agent-orchestra | 1 | **Documented exception to the 3-URL floor**: upstream is a single commit (LICENSE + README only) — no third resource exists to fetch. |
| 11-x-platform-toolkit | 8 | Per-tool indexing pulled extra HTML files. |
| 12-claudex | 7 | Local file paths and `git`/`find` outputs (no WebFetch). |
| **Total** | **71** | Across 11 WebFetch audits + 1 local audit. |

## Reproducibility

A future auditor can reproduce this phase by:
1. Reading each audit's Evidence log.
2. Fetching the same URLs (all public).
3. Comparing claims to the fetched content.
4. Noting any content changes since 2026-04-23 (the audit snapshot date).
