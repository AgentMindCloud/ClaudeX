# Phase 1B — Issue Drafts Index

Authoritative tracker for Phase 1B upstream issue drafts. Each row maps one
draft in `phase-1b/drafts/` to its `audits/99-recommendations.md §2` source
and, once filed, to the resulting upstream issue URL.

Filing workflow: see `phase-1b/README.md §Filing workflow (for the user)`.

## Status legend

- `drafted` — markdown file exists in `phase-1b/drafts/`, not yet filed upstream.
- `filed` — issue opened on the target repo; **Filed** column carries the URL.
- `filed → <outcome>` — issue filed and then closed / merged / rewritten;
  annotate the outcome inline (e.g. `filed → closed wontfix`,
  `filed → merged as PR #N`).

## First-pass drafts (4 §2 recs, 6 files)

| # | §2 rec | Upstream repo | Draft file | Filed (link) | Status |
|:-:|:-:|---|---|---|---|
| 1 | #6 | AgentMindCloud/grok-install-cli *(+ cross-ref to grok-install-action)* | [`drafts/06-cli-install-mechanism.md`](drafts/06-cli-install-mechanism.md) | — | drafted |
| 2 | #9 | AgentMindCloud/grok-install | [`drafts/09-v2-14-examples-coverage.md`](drafts/09-v2-14-examples-coverage.md) | — | drafted |
| 3 | #14 | AgentMindCloud/grok-install-action | [`drafts/14a-grok-install-action-readme.md`](drafts/14a-grok-install-action-readme.md) | — | drafted |
| 4 | #14 | AgentMindCloud/vscode-grok-yaml | [`drafts/14b-vscode-grok-yaml-landing.md`](drafts/14b-vscode-grok-yaml-landing.md) | — | drafted |
| 5 | #15 | AgentMindCloud/vscode-grok-yaml | [`drafts/15a-vscode-grok-yaml-description.md`](drafts/15a-vscode-grok-yaml-description.md) | — | drafted |
| 6 | #15 | AgentMindCloud/grok-agent-orchestra | [`drafts/15b-grok-agent-orchestra-description.md`](drafts/15b-grok-agent-orchestra-description.md) | — | drafted |

## Next batch candidates

Chosen because each is S-effort in §2, carries no `Blocked by` entry, and
either raises the ecosystem CI floor or resolves a supply-chain concern
before any later rec can depend on it. All three should be eligible to
draft immediately after the first-pass batch lands.

| §2 # | Rec (short) | Target repos | Why this batch |
|:-:|---|---|---|
| #3 | Pin every GitHub Action by commit SHA; ship Renovate/Dependabot config to keep them moving. Closes SUP-1. | grok-install, grok-yaml-standards, grok-install-cli, grok-install-action, grok-docs, awesome-grok-agents, grok-agents-marketplace, grok-build-bridge | Raises supply-chain floor ecosystem-wide before #18 standardises a CI template that inherits it. |
| #13 | Make `pip-audit` blocking (drop `continue-on-error`); add `gitleaks` (or trufflehog) to every repo's CI, starting with the CLI + bridge templates. Closes SEC-2, SEC-3. | grok-install-cli, grok-build-bridge (template); rolled out via #18 | Same floor-raising argument as #3; also the lightest S-effort way to close two SEC rows. |
| #18 | Extract `grok-build-bridge`'s CI workflow as the ecosystem baseline template (mypy strict, `--cov-fail-under=85`, draft-2020-12 validation, OS × Python matrix) and adopt it across the eight CI-enabled repos. Closes SEC-2 across adopters; supports SUP-1. | grok-build-bridge, grok-install, grok-yaml-standards, grok-install-cli, grok-install-action, grok-docs, awesome-grok-agents, grok-agents-marketplace | Flagged M-effort in §2 distribution check but listed here because its CI template is the delivery vehicle for #3 + #13 across adopters — drafting #18 alongside them lets maintainers adopt all three in one PR. |

Blocked-by chains beyond the next batch (for reference when filing later
passes):

- `#5 → {#1, #11, #17}` — safety-profile rubric must land before its
  dependents.
- `#6 → {#7, #12}` — CLI install mechanism must settle before dependents.
- `#10 → #4` — v2.14 docs must exist before `repository_dispatch` is wired.
- `#15 → #16` — shell-repo description must be honest before `vscode-grok-yaml`
  bootstrap issue (#16) is filed.

## Filing audit trail

When a draft moves to `filed`, edit the row's **Filed** and **Status**
columns in-place. Do not delete the row. If an upstream maintainer
meaningfully rewrites the issue, add a one-line note under the row in
italics (GitHub renders a blank line above an italic note inside a
markdown table as a regular cell break).

Drafts themselves are append-only after filing: if the upstream issue
diverges, track the divergence here, not by editing the draft file.
