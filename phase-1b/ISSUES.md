# Phase 1B — Issue Drafts Index

Authoritative tracker for Phase 1B upstream issue drafts. Each row maps one
draft in `phase-1b/drafts/` to its `audits/99-recommendations.md §2` source
and, once filed, to the resulting upstream issue URL.

Filing workflow: see `phase-1b/README.md §Filing workflow (for the user)`.
Per-upstream-repo filing packets (paste-ready title / labels / body
pointers, ordered by recommended filing sequence): see
`phase-1b/filing-packets/` — `README.md` covers the two filing paths
(widened-scope agent session vs. manual GitHub UI) and the 11 per-repo
files carry the actual packet content.

## Status legend

- `drafted` — markdown file exists in `phase-1b/drafts/`, not yet filed upstream.
- `filed` — issue opened on the target repo; **Filed** column carries the URL.
- `filed → <outcome>` — issue filed and then closed / merged / rewritten;
  annotate the outcome inline (e.g. `filed → closed wontfix`,
  `filed → merged as PR #N`).

## First-pass drafts (4 §2 recs, 6 files)

Slice chosen because all four recs are S-effort in §2, carry no `Blocked by`
entry, and each closes at least one S1 / S3 risk. The six files have no
internal filing-order dependencies — they can be filed in any order. Across
the two `(a/b)` pairs, **filing both halves is required to fully close the
underlying risk row**; filing one half moves that risk to *partial*.

| # | §2 rec | Risks closed | Upstream repo | Draft file | Unblocks §2 | Filed (link) | Status |
|:-:|:-:|---|---|---|:-:|---|---|
| 1 | #6 | VER-3 (S1), UNV-1 (S1) | AgentMindCloud/grok-install-cli *(+ cross-ref to grok-install-action)* | [`drafts/06-cli-install-mechanism.md`](drafts/06-cli-install-mechanism.md) | #7, #12 | — | drafted |
| 2 | #9 | VER-1 (S1) | AgentMindCloud/grok-install | [`drafts/09-v2-14-examples-coverage.md`](drafts/09-v2-14-examples-coverage.md) | — | — | drafted |
| 3 | #14 | DOC-1 (partial — pair with row 4) | AgentMindCloud/grok-install-action | [`drafts/14a-grok-install-action-readme.md`](drafts/14a-grok-install-action-readme.md) | — | — | drafted |
| 4 | #14 | DOC-1 (partial — pair with row 3) | AgentMindCloud/vscode-grok-yaml | [`drafts/14b-vscode-grok-yaml-landing.md`](drafts/14b-vscode-grok-yaml-landing.md) | — | — | drafted |
| 5 | #15 | GOV-3 (S3) + DOC-3 (S3) (partial — pair with row 6) | AgentMindCloud/vscode-grok-yaml | [`drafts/15a-vscode-grok-yaml-description.md`](drafts/15a-vscode-grok-yaml-description.md) | #16 | — | drafted |
| 6 | #15 | GOV-3 (S3) + DOC-3 (S3) (partial — pair with row 5) | AgentMindCloud/grok-agent-orchestra | [`drafts/15b-grok-agent-orchestra-description.md`](drafts/15b-grok-agent-orchestra-description.md) | #17 *(still gated by §2 #5 — see below)* | — | drafted |

## Second-pass drafts (3 §2 recs, 3 files)

Slice chosen as the CI-and-supply-chain floor the rest of the ecosystem will
inherit. Effort is **not uniform** — §2 #13 is S, #3 and #18 are M (the
M-effort is coordination across 8 repos, not per-repo difficulty). All three
carry no `Blocked by` entry in §2, so the batch has no internal filing-order
dependency; in practice filing order **#3 → #13 → #18** is cheapest because
§2 #18 is written to freeze the template **after** #3 (SHA pins) and #13
(blocking pip-audit + secret-scan) land in `grok-build-bridge`, so adopters
inherit the corrected posture in one cut. Filing #18 first is valid — it
just triggers a follow-up template-bump PR once #3 and #13 merge.

| # | §2 rec | Effort | Risks closed | Upstream repo(s) | Draft file | Unblocks §2 | Filed (link) | Status |
|:-:|:-:|:-:|---|---|---|:-:|---|---|
| 7 | #3 | M | SUP-1 (S2) ecosystem-wide | AgentMindCloud/grok-install *(coordinator — see draft metadata for 8-repo scope + optional per-repo filing)* | [`drafts/03-sha-pin-actions-ecosystem.md`](drafts/03-sha-pin-actions-ecosystem.md) | — *(but the SHA-pin posture is consumed by §2 #18 at template-freeze time)* | — | drafted |
| 8 | #13 | S | SEC-2 (S2), SEC-3 (S2) on both pilot repos; SEC-3 only *partial* ecosystem-wide (full closure rides on §2 #18) | AgentMindCloud/grok-install-cli + AgentMindCloud/grok-build-bridge *(file twice — same body stands against either)* | [`drafts/13-blocking-pip-audit-plus-secret-scan.md`](drafts/13-blocking-pip-audit-plus-secret-scan.md) | — *(consumed by §2 #18 at template-freeze time)* | — | drafted |
| 9 | #18 | M | SEC-2 (S2) across adopters indirectly; supports SUP-1 closure across adopters | AgentMindCloud/grok-build-bridge *(extraction — coordinator)*; 7 adopter repos in checklist | [`drafts/18-ci-template-baseline.md`](drafts/18-ci-template-baseline.md) | — *(delivery vehicle for #3 + #13 across 7 adopters once they land at the source)* | — | drafted |

## Third-pass drafts (3 §2 recs, 3 files)

Slice chosen as the "cross-ecosystem contracts + local-leverage
governance" tranche. All three are M-effort with no `Blocked by`
entry in §2; each closes (or fully enables closure of) at least
one `98-risk-register.md` row. §2 #5 is the highest-fanout item
in the §2 graph — three downstream recs (#1, #11, #17) depend on
it — so drafting it first unlocks the gated post-filing follow-ups.

| # | §2 rec | Effort | Risks closed | Upstream repo(s) | Draft file | Unblocks §2 | Filed (link) | Status |
|:-:|:-:|:-:|---|---|---|:-:|---|---|
| 10 | #5 | M | partial UNV-3 (S3); enables UNV-4 (S3) closure once consumers adopt | AgentMindCloud/grok-yaml-standards *(primary — owner of the rubric)*; consumer-repo checklist covers grok-install-cli, awesome-grok-agents, grok-build-bridge, grok-agent-orchestra | [`drafts/05-safety-profile-rubric.md`](drafts/05-safety-profile-rubric.md) | #1, #11, #17 | — | drafted |
| 11 | #8 | M | VER-2 (S2) outright | AgentMindCloud/grok-yaml-standards *(downstream validators inherit via `$schema`-keyword awareness — no cross-ref filings)* | [`drafts/08-grok-yaml-standards-draft-2020-12-migration.md`](drafts/08-grok-yaml-standards-draft-2020-12-migration.md) | — *(cleans up §2 #18's schema-check job once both land)* | — | drafted |
| 12 | #20 | M | GOV-2 (S2) outright | AgentMindCloud/grok-agents-marketplace | [`drafts/20-grok-agents-marketplace-pr-triage-codeowners.md`](drafts/20-grok-agents-marketplace-pr-triage-codeowners.md) | — *(makes §2 #3 and §2 #18 cross-ref adoptions in this repo cheaper via reviewer routing)* | — | drafted |

## Session-2 speculative drafts (6 §2 recs, 6 files)

Slice chosen because each prerequisite lives in this repo (first-
second- or third-pass drafts), not upstream. Per the Session-2
policy recorded in `phase-1b/README.md` and each draft's
metadata header, every draft below carries a **Prerequisite
status** flag ("drafted in `drafts/<prereq>.md`; not yet filed
upstream; speculative") + a **Re-review trigger** clause. Drafts
marked `speculative` in the Status column cannot file upstream
until their prerequisite merges upstream first.

Ordering below = strength of speculation (safest first). §2 #16
is safest (both #15 options converge). §2 #17 is most deeply
speculative (two prerequisites, one itself speculative).

| # | §2 rec | Effort | Speculative on | Risks closed (on prerequisite merge) | Upstream repo | Draft file | Status |
|:-:|:-:|:-:|:-:|---|---|---|---|
| 13 | #16 | M | #15a, #15b (both drafted) | partial GOV-3 | AgentMindCloud/vscode-grok-yaml | [`drafts/16-vscode-grok-yaml-bootstrap.md`](drafts/16-vscode-grok-yaml-bootstrap.md) | speculative |
| 14 | #7  | S | #6 (drafted) | VER-3 (pin layer) | AgentMindCloud/grok-install-cli *(+ cross-ref follow-up in grok-install-action after primary releases)* | [`drafts/07-grok-install-cli-releases-pyproject-alignment.md`](drafts/07-grok-install-cli-releases-pyproject-alignment.md) | speculative |
| 15 | #12 | S | #6, #7 (both drafted; #7 itself speculative) | partial UNV-4 | AgentMindCloud/awesome-grok-agents | [`drafts/12-awesome-grok-agents-replace-install-stub.md`](drafts/12-awesome-grok-agents-replace-install-stub.md) | speculative (deepest — transitive through #7) |
| 16 | #1  | L | #5 (drafted) | UNV-4 outright; partial SEC-1 | AgentMindCloud/grok-install-cli *(extraction primary; A2 new-repo alternative flagged in draft)* | [`drafts/01-shared-grok-safety-rules-package.md`](drafts/01-shared-grok-safety-rules-package.md) | speculative |
| 17 | #11 | S | #5 (drafted) | closes 00 §6.2 "missing-exemplar" finding | AgentMindCloud/awesome-grok-agents | [`drafts/11-awesome-grok-agents-permissive-exemplar.md`](drafts/11-awesome-grok-agents-permissive-exemplar.md) | speculative |
| 18 | #17 | L | #5, #1 (both drafted; #1 itself speculative) | UNV-3 outright; partial GOV-3 | AgentMindCloud/grok-agent-orchestra | [`drafts/17-grok-agent-orchestra-bootstrap.md`](drafts/17-grok-agent-orchestra-bootstrap.md) | speculative (deepest — transitive through #1) |

## Next-pass candidates

With first-, second-, and third-pass slices covering §2 recs #3,
#5, #6, #8, #9, #13, #14, #15, #18, #20 (10 of 20), the remaining
`Blocked by`-free §2 recs are the three below. Mixed effort;
drafting them pushes cumulative coverage to 13 of 20 without
waiting for any upstream landing.

| §2 # | Rec (short) | Effort | Reach | Unblocks §2 | Why this batch |
|:-:|---|:-:|:-:|:-:|---|
| #2 | Extract a shared Grok API client (auth, retries, streaming, rate-limit) — collapses the four parallel implementations in `00-ecosystem-overview.md §9.A`. | L | 5 | — | Highest reach in §2 (5). L-effort because it needs a coordination-plus-extraction write-up; the draft itself is a specification issue, not the implementation. |
| #10 | Ship `grok-docs` v2.14 content + reference pages for the 7 undocumented standards. Closes VER-4, DOC-2. | L | 4 | #4 | Unblocks §2 #4 (`repository_dispatch` wiring) — without this, #4 cannot be responsibly drafted. L-effort is content-writing cost. |
| #19 | Add minimum CI to `x-platform-toolkit` (html-validate, css-lint, broken-link, Live-vs-Spec consistency). Closes SUP-5. | M | 2 | — | Closes the only SUP-category risk outside the #3/#13/#18 coverage. Reach-2 but the toolkit publishes user-facing tools that read live spec versions. |

### Post-filing follow-ups (not yet candidates — wait for upstream landing)

Drafts below become unblocked once the listed prerequisite draft is **filed AND
merged/closed** upstream. Don't draft them before the unblocking merge lands;
the prerequisite's text may shift in review and invalidate the follow-up
assumptions.

Note: since none of the first-/second-/third-pass drafts has been filed upstream yet
(MCP-scope blocker — see `phase-1b/README.md §MCP-scope constraint`), drafts in this
table that reference a third-pass prerequisite (§2 #5) are eligible to be written as
**speculative drafts** against the in-repo prerequisite rather than waiting for
upstream merge. A speculative draft carries a metadata-header flag stating so. See
`phase-1b/README.md` and the §2 #5 draft itself for context.

| §2 # | Rec (short) | Waits on | Prerequisite status | Draft file | Notes |
|:-:|---|:-:|---|---|---|
| #7 | Publish proper `grok-install-cli` GitHub releases whose tag matches `pyproject.toml`; align the action's pin. Closes VER-3. | #6 | drafted in `drafts/06-cli-install-mechanism.md`; not yet filed upstream | [`drafts/07-…`](drafts/07-grok-install-cli-releases-pyproject-alignment.md) (Session 2) | Part B enumerates pin-alignment behaviour under each of #6's three acceptance options. Re-review trigger: rewrite if #6's landed resolution differs materially. |
| #12 | Replace `awesome-grok-agents`'s `grok_install_stub` with a real CLI invocation in CI. Closes partial UNV-4. | #6, #7 | both drafted (#7 itself speculative) | [`drafts/12-…`](drafts/12-awesome-grok-agents-replace-install-stub.md) (Session 2) | Deepest speculation (transitive through #7). File only after #6 AND #7 merge upstream. |
| #4 | Wire `repository_dispatch` from `grok-install` → `grok-docs`, `grok-install-action`, `grok-agents-marketplace`. Closes VER-4 trigger; partial DOC-1. | #10 | **#10 NOT drafted** (L-effort; in next-pass candidates below) | — | Deferred per Session-2 kickoff decision (user accepted defaults). Draft only after #10 is drafted; otherwise dispatch has no docs to rebuild. |
| #16 | Bootstrap `vscode-grok-yaml` v0.1.0 (read-only schema validation is enough). Closes partial GOV-3. | #15 | drafted in `drafts/15a-…` + `15b-…` | [`drafts/16-…`](drafts/16-vscode-grok-yaml-bootstrap.md) (Session 2) | Safest speculative draft — both #15 sibling options converge on "description is honest". |
| #1 | Extract shared `grok-safety-rules` package consumed by CLI + bridge + orchestra + gallery. Closes UNV-4 outright; partial SEC-1. | #5 | drafted in `drafts/05-safety-profile-rubric.md` | [`drafts/01-…`](drafts/01-shared-grok-safety-rules-package.md) (Session 2) | Trio member 1 of 3 (different repo per draft). Speculative against #5's Part-A rubric shape. |
| #11 | Add a permissive-profile exemplar template (`internal-ci-assistant`) to `awesome-grok-agents`. Closes 00 §6.2 missing-exemplar finding. | #5 | drafted in `drafts/05-safety-profile-rubric.md` | [`drafts/11-…`](drafts/11-awesome-grok-agents-permissive-exemplar.md) (Session 2) | Trio member 2 of 3. Template body mirrors #5's `permissive` row cell-for-cell. |
| #17 | Bootstrap `grok-agent-orchestra` v0.1.0 with a plan-execute-critique pattern + a behavioural Lucas veto. Closes UNV-3 outright; partial GOV-3. | #5, #1 | both drafted (#1 itself speculative) | [`drafts/17-…`](drafts/17-grok-agent-orchestra-bootstrap.md) (Session 2) | Trio member 3 of 3. Deepest speculation; Part A falls back to pinning `grok-install-cli/safety/` if #1 not yet shipped at filing time. |

Blocked-by chains (one-way; source of truth is the `Blocked by` column in
`audits/99-recommendations.md §2`):

- `#5 → {#1, #11, #17}` — safety-profile rubric.
- `#6 → {#7, #12}` — CLI install mechanism.
- `#10 → #4` — v2.14 docs before dispatch wiring.
- `#15 → #16` — shell-repo description before VS Code bootstrap.

## Filing audit trail

When a draft moves to `filed`, edit the row's **Filed** and **Status**
columns in-place. Do not delete the row. If an upstream maintainer
meaningfully rewrites the issue, add a one-line note under the row in
italics (GitHub renders a blank line above an italic note inside a
markdown table as a regular cell break).

Drafts themselves are append-only after filing: if the upstream issue
diverges, track the divergence here, not by editing the draft file.
