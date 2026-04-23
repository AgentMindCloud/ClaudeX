# Phase 1B — Upstream Issue Drafting

Phase 1B converts the `§2 top-20` table in `audits/99-recommendations.md` into
issue text that can be filed against the upstream AgentMindCloud Grok repos.

This is a **drafting phase, not a filing phase.** See the MCP-scope constraint
below.

## Purpose

- Turn §2 recommendations (and the risks they close in `audits/98-risk-register.md`)
  into self-contained issue bodies a maintainer can land without re-reading
  Phase 1A.
- Keep the mapping from draft → rec → risk → target repo explicit, so the
  user can file the drafts manually (or via a differently-scoped tool) and
  still trace each filed issue back to its audit source.
- Sequence drafts against the `Blocked by` column in §2 so dependencies are
  respected when the user files them.

## MCP-scope constraint — *drafts only*

The Phase 1B agent's GitHub MCP scope is restricted to
`agentmindcloud/claudex` only. It **cannot** open issues on upstream repos
like `AgentMindCloud/grok-install`, `AgentMindCloud/grok-install-cli`, etc.
Calling `mcp__github__issue_write` against any other repo will fail.

Therefore each upstream issue is written as a markdown file in
`phase-1b/drafts/`. The user files each draft manually via the GitHub UI
(or via a session with a widened MCP scope) and back-fills the `Filed`
column in `phase-1b/ISSUES.md` with the resulting issue URL.

If the scope is widened in a later session, the drafts in this directory
become the direct source for `mcp__github__issue_write` calls — no
intermediate translation required.

## Mapping rules

Every draft in `phase-1b/drafts/` carries four links back to its origin:

1. **§2 row** — e.g. *"§2 #6"* — pins the draft to one row of the top-20
   table in `audits/99-recommendations.md`. Exactly one row per draft,
   except where §2 calls out multiple target repos (#14, #15), in which
   case one draft per target repo, each citing the same §2 row.
2. **Risk IDs** — every §2 row cites at least one risk from
   `audits/98-risk-register.md` (`SEC-N`, `SUP-N`, `GOV-N`, `VER-N`,
   `DOC-N`, or `UNV-N`). Drafts carry the same IDs forward verbatim; do
   not invent new ones.
3. **Source audits** — the `[→ NN §M row K]` citations in the §2 row's
   `Source audits` column. The draft's *Evidence* section repeats those
   citations so the upstream maintainer can verify without reading Phase
   1A cover-to-cover.
4. **Target repo(s)** — the `Affected repos` column of the §2 row. The
   draft filename is prefixed with the §2 row number; where one §2 row
   maps to multiple target repos, suffix with `a` / `b` (e.g.
   `14a-…`, `14b-…`).

Drafts never invent rec numbers, risk IDs, or cross-refs that aren't in
§2 or the risk register. If Phase 1B discovers a new risk, it belongs
in a new audits/ entry — not smuggled into a draft.

## Draft file structure

Each draft is one markdown file written as a ready-to-paste GitHub issue
body, plus a small header block for the filer:

```
# <issue title — short, imperative>

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #N
- **Target repo**: AgentMindCloud/<repo>
- **Risks closed**: <IDs from 98-risk-register.md>
- **Source audits**: <[→ NN §M row K] citations from §2>
- **Blocked by**: <§2 rows this one depends on, or "none">
- **Suggested labels**: <comma-sep>

---

## Context
<why this matters, with citations into audits/>

## Reproduction / evidence
<minimal pointer the maintainer can verify themselves>

## Acceptance criteria
<one or more options — concrete, checkable>

## Notes
<optional: trade-offs, out-of-scope items, related §2 rows>
```

The `<!-- phase-1b metadata -->` block is a filing aid; the user should
paste **only the content below the `---` separator** into GitHub. The
metadata stays in this repo so the ISSUES.md index stays authoritative.

## Filing workflow (for the user)

For each draft in `phase-1b/drafts/`:

1. Read the metadata block to confirm target repo and required labels.
2. Copy the issue body (everything below the `---` separator) into the
   upstream repo's *New issue* form.
3. Paste the title from the draft's H1.
4. Apply the suggested labels (create them if missing in the target
   repo).
5. Once filed, edit `phase-1b/ISSUES.md` and fill in the **Filed**
   column for that row with the issue URL, and flip **Status** from
   `drafted` to `filed`.
6. If the upstream maintainer closes, relabels, or substantially
   rewrites the issue, note that under **Status** (e.g. `filed →
   closed wontfix`, `filed → merged as PR #N`).

Drafts are the audit trail of what Phase 1B asked for; the **Filed**
column is the audit trail of what happened upstream. Do not delete
drafts after filing — future phases may need to diff what was
proposed vs. what landed.

## Ordering (Blocked-by chains from §2)

The §2 `Blocked by` column encodes the one-way dependencies among recs;
drafts should be filed in an order that respects them:

- **#5 → {#1, #11, #17}** — file #5 first so the safety-profile rubric
  is in place before dependents need it.
- **#6 → {#7, #12}** — file #6 first so the CLI install mechanism is
  settled before dependents assume a specific path.
- **#10 → #4** — file #10 first so v2.14 docs exist before dispatch is
  wired.
- **#15 → #16** — file #15 first so the `vscode-grok-yaml` description
  is honest before bootstrap starts.

The first-pass batch (#6, #9, #14, #15) is deliberately chosen from
rows with **no** `Blocked by` entry, so nothing in this batch waits on
a draft outside it. Later passes must re-check this table before
filing.

## Scope of the first pass

Four §2 rows → six draft files (two §2 rows produce two drafts each for
two target repos):

| §2 # | Draft file(s) | Target repo(s) |
|:-:|---|---|
| 6 | `06-cli-install-mechanism.md` | grok-install-cli + grok-install-action (coordinated; filed against whichever the maintainer designates as primary) |
| 9 | `09-v2-14-examples-coverage.md` | grok-install |
| 14 | `14a-grok-install-action-readme.md`, `14b-vscode-grok-yaml-landing.md` | grok-install-action, vscode-grok-yaml |
| 15 | `15a-vscode-grok-yaml-description.md`, `15b-grok-agent-orchestra-description.md` | vscode-grok-yaml, grok-agent-orchestra |

Total: 4 §2 recs, 6 draft files, 6 target-repo touches (one of which
— the #6 coordinated issue — lands on two repos via cross-reference
from a single filed issue).

Next batch candidates (see `ISSUES.md §Next batch candidates`): §2 #3,
#13, #18 — all S-effort, all without `Blocked by` entries, all raise
the CI/supply-chain floor before any bootstrap rec depends on it.
