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

## Next-pass candidates

With the first-pass and second-pass slices covering §2 recs #3, #6, #9, #13,
#14, #15, #18, the remaining `Blocked by`-free §2 recs fall into two groups:
cross-ecosystem contracts (#5, #8) and repo-local governance with high local
leverage (#20). The three below are the natural next tranche — all three
unblock downstream §2 recs (explicit for #5), and none of them waits on
first-pass filings landing upstream. Effort is mixed (all M).

| §2 # | Rec (short) | Effort | Reach | Unblocks §2 | Why this batch |
|:-:|---|:-:|:-:|:-:|---|
| #5 | Publish a unified safety-profile rubric (strict / standard / permissive) with conformance tests in `grok-yaml-standards`. Closes partial UNV-3; enables UNV-4 closure. | M | 4 | #1, #11, #17 | Highest-fanout unblocker on the §2 graph — three downstream recs depend on it. Drafting it next lets the later passes run in parallel. |
| #8 | Migrate `grok-yaml-standards` to JSON Schema draft-2020-12 for v1.3, closing the draft-07 / draft-2020 split with `grok-install`. Closes VER-2. | M | 3 | — | Removes the only structural cross-spec drift. §2 #18's template adopters inherit cleaner schema-validate jobs once this lands (the template already uses draft-2020-12). |
| #20 | Triage the 12 open PRs on `grok-agents-marketplace`; publish `CODEOWNERS`; document a review SLA. Closes GOV-2. | M | 2 | — | Governance row with the highest local leverage (5) in §2. Reach-2 but closes the only S1-adjacent governance risk outright. |

### Post-filing follow-ups (not yet candidates — wait for upstream landing)

Drafts below become unblocked once the listed first-pass draft is **filed AND
merged/closed** upstream. Don't draft them before the unblocking merge lands;
the prerequisite's text may shift in review and invalidate the follow-up
assumptions.

| §2 # | Rec (short) | Waits on | Notes |
|:-:|---|:-:|---|
| #7 | Publish proper `grok-install-cli` GitHub releases whose tag matches `pyproject.toml`; align the action's pin. Closes VER-3. | #6 | #6's resolution determines whether "version" means PyPI tag, npm tag, or both. |
| #12 | Replace `awesome-grok-agents`'s `grok_install_stub` with a real CLI invocation in CI. Closes partial UNV-4. | #6, #7 | Needs a working install path (from #6) and a tagged release (from #7) to pin against. |
| #4 | Wire `repository_dispatch` from `grok-install` → `grok-docs`, `grok-install-action`, `grok-agents-marketplace`. Closes VER-4 trigger; partial DOC-1. | #10 | v2.14 docs (#10) must exist before dispatch is wired, else the dispatched event has no docs to rebuild. |
| #16 | Bootstrap `vscode-grok-yaml` v0.1.0 (read-only schema validation is enough). Closes partial GOV-3. | #15 | Description must be honest (#15) before bootstrap begins so contributors aren't confused mid-flight. |
| #1, #11, #17 | Shared `grok-safety-rules` (#1), permissive-profile exemplar (#11), `grok-agent-orchestra` bootstrap (#17). | #5 | All three depend on the unified safety-profile rubric; draft them as a coordinated trio after #5 lands. |

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
