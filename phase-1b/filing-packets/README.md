# Filing packets — Phase 1B upstream issues

This folder converts the 9 Phase-1B drafts in `phase-1b/drafts/` into
per-upstream-repo filing instructions. Each file here lists what to file
(and when) against one AgentMindCloud repo the Phase-1B agent does **not**
have GitHub MCP access to.

The MCP-scope constraint is documented in `phase-1b/README.md §MCP-scope
constraint`. Bottom line: the Phase-1B agent's scope is
`agentmindcloud/claudex`-only and cannot call `mcp__github__issue_write`
against any of the 11 upstream repos. You have two paths to get the
drafts filed — see "Two paths" below.

## Folder contents

- `README.md` — this file (instructions).
- `01-grok-install.md` … `11-x-platform-toolkit.md` — one packet per
  upstream AgentMindCloud repo. Numbering matches `audits/NN-*.md`.
- `12-claudex.md` is intentionally absent — this repo is the Phase-1B
  agent's own MCP scope; no packet needed.

## Two paths

Pick one. Both end with the same 9 drafts filed upstream and
`phase-1b/ISSUES.md`'s **Filed** column back-filled.

### Path A — Widen MCP scope, let the next Claude session file the issues

Fast path. Requires one config change before you start the next session.

1. **Widen the GitHub App's repository access.** The harness restricts
   the agent's GitHub MCP to `agentmindcloud/claudex`. Expand this
   before a new session:
   - Likely location 1 — **GitHub org admin**:
     https://github.com/organizations/AgentMindCloud/settings/installations
     → find the Claude / Anthropic GitHub App → **Configure** →
     **Repository access** → add the 11 repos listed in this folder.
   - Likely location 2 — **Claude Code dashboard** (if you start
     sessions from a web UI): look for a "Connected repos" /
     "GitHub integration" panel in the session or project config
     and add the same 11 repos.
   - The app also needs `issues: write` permission on each repo. If
     the app is installed read-only, flip this too.
2. **Start a new session** with the kickoff prompt below. Include
   the widened scope explicitly so the new agent knows it can file.
3. **Paste** the kickoff prompt (next sub-section) into the new
   session.
4. **Back-fill** `phase-1b/ISSUES.md`'s **Filed** column as each
   issue is opened. The agent can do this in-session if it has
   write access to ClaudeX (it does — this repo is in its scope).

#### Kickoff prompt for the widened-scope session

```
You are resuming Phase 1B on ClaudeX at HEAD a0ded75 on branch
claude/phase-1b-issue-drafts-rzjg8. Your harness will assign a new
branch — branch from the current tip, not main.

GitHub MCP scope is now widened beyond agentmindcloud/claudex to include:
- agentmindcloud/grok-install
- agentmindcloud/grok-yaml-standards
- agentmindcloud/grok-install-cli
- agentmindcloud/grok-install-action
- agentmindcloud/grok-docs
- agentmindcloud/awesome-grok-agents
- agentmindcloud/vscode-grok-yaml
- agentmindcloud/grok-agents-marketplace
- agentmindcloud/grok-build-bridge
- agentmindcloud/grok-agent-orchestra
- agentmindcloud/x-platform-toolkit

Your task: file the 9 drafts in phase-1b/drafts/ against their upstream
repos, using phase-1b/filing-packets/*.md as the per-repo filing plan.

Per-draft filing protocol:
1. Read phase-1b/filing-packets/<target-repo>.md.
2. For each "Issue — <title>" entry, read the referenced draft in
   phase-1b/drafts/, extract the content below the `---` separator
   as the issue body, and call mcp__github__issue_write with:
   - title = draft H1
   - body = content below `---`
   - labels = the draft's "Suggested labels" (create any that don't
     exist in the target repo)
3. Back-fill phase-1b/ISSUES.md's **Filed** column with the issue
   URL; flip **Status** from `drafted` to `filed`.
4. Commit each filed issue as its own unit, conventional message
   `phase-1b: file §2 #N against <repo>`.
5. For cross-ref / adopter-follow-up entries: file ONLY after the
   referenced primary issue lands. Substitute the primary's URL
   into the cross-ref body where marked `<TODO: primary URL>`.

Verify first:
  git fetch --all --prune
  git log --oneline origin/claude/phase-1b-issue-drafts-rzjg8 -1
    # MUST start with: a0ded75
  git checkout -B "$(git branch --show-current)" \
      origin/claude/phase-1b-issue-drafts-rzjg8
  git status

Recommended filing order:
  1. First-pass primaries (any order):
     - §2 #9 → grok-install
     - §2 #6 → grok-install-cli
     - §2 #14a → grok-install-action
     - §2 #14b → vscode-grok-yaml
     - §2 #15a → vscode-grok-yaml
     - §2 #15b → grok-agent-orchestra
  2. Second-pass primaries (prefer #3 → #13 → #18):
     - §2 #3 → grok-install (coordinator)
     - §2 #13 → grok-install-cli + grok-build-bridge (file twice)
     - §2 #18 → grok-build-bridge (coordinator)
  3. Cross-refs / adopter follow-ups: only after the referenced
     primary lands.

Do not open issues on repos still outside your scope — the filing
packets document the expected scope. If a repo listed above returns
an auth error, STOP and report which.
```

### Path B — File manually via the GitHub UI

Slower but needs no config change. Suitable if you prefer human
authorship of the upstream issues.

For each packet file in this folder:

1. Open the repo's **New issue** URL (the packet lists it up top).
2. For each "Issue — <title>" entry:
   - Copy the title verbatim from the packet.
   - Paste it into GitHub's issue title field.
   - Open the referenced `phase-1b/drafts/<file>.md` in another tab.
     Copy everything **below** the first `---` separator — that is
     the issue body. Paste it into GitHub's issue body field.
   - Apply the suggested labels (create any that don't exist yet).
   - Submit.
3. Edit `phase-1b/ISSUES.md`: put the new issue URL in the **Filed**
   column for that row; flip **Status** from `drafted` to `filed`.
   Commit as `phase-1b: file §2 #N against <repo>`.
4. For cross-ref / adopter-follow-up entries: wait until the
   referenced primary issue exists, grab its URL, then file the
   cross-ref with the URL substituted in.

## Recommended filing order

Same as Path A's kickoff prompt. Within each pass, primaries are
independent and can be filed in any order; cross-refs / adopter
follow-ups wait for their referenced primary to land.

### Pass 1 — first-pass primaries (6 issues across 5 repos)

| # | §2 | Draft | Target repo |
|:-:|:-:|---|---|
| 1 | #9  | `09-v2-14-examples-coverage.md` | grok-install |
| 2 | #6  | `06-cli-install-mechanism.md` | grok-install-cli |
| 3 | #14 | `14a-grok-install-action-readme.md` | grok-install-action |
| 4 | #14 | `14b-vscode-grok-yaml-landing.md` | vscode-grok-yaml |
| 5 | #15 | `15a-vscode-grok-yaml-description.md` | vscode-grok-yaml |
| 6 | #15 | `15b-grok-agent-orchestra-description.md` | grok-agent-orchestra |

### Pass 2 — second-pass primaries (4 issues across 3 repos; prefer #3 → #13 → #18)

| # | §2 | Draft | Target repo |
|:-:|:-:|---|---|
| 7  | #3  | `03-sha-pin-actions-ecosystem.md` | grok-install (coordinator) |
| 8  | #13 | `13-blocking-pip-audit-plus-secret-scan.md` | grok-install-cli |
| 9  | #13 | `13-blocking-pip-audit-plus-secret-scan.md` (same body) | grok-build-bridge |
| 10 | #18 | `18-ci-template-baseline.md` | grok-build-bridge (coordinator) |

### Pass 3 — cross-refs / adopter follow-ups (open after primary lands)

Each per-repo packet lists its cross-refs at the bottom. File only
after the referenced primary has been opened (and ideally merged —
a primary's text can shift in review).

## Back-filling `phase-1b/ISSUES.md`

After each issue is filed:

1. Edit the matching row in the first-pass or second-pass table.
2. Replace the `—` in the **Filed** column with the new issue URL
   (as a markdown link, e.g. `[#42](https://github.com/.../issues/42)`).
3. Flip **Status** from `drafted` to `filed`. If the upstream
   maintainer later closes or rewrites the issue, amend the status
   in-place (e.g. `filed → closed wontfix`,
   `filed → merged as PR #N`).
4. Commit with a conventional message —
   `phase-1b: file §2 #N against <repo>` for primaries,
   `phase-1b: cross-ref §2 #N in <repo>` for cross-refs.

Do **not** delete rows, and do **not** edit the draft file in
`phase-1b/drafts/` after filing — if the upstream issue diverges
from the draft, track the divergence in `ISSUES.md` (amended
**Status**), not by editing the draft. The drafts are the
audit-trail artefacts of what Phase 1B asked for; `ISSUES.md` is
the audit trail of what happened upstream.

## Troubleshooting

- **Label doesn't exist in target repo.** Create it (the target
  repo's settings → Labels → "New label"). The suggested labels
  are deliberately ecosystem-generic (`security`, `docs`,
  `version-coherence`, `phase-1b`, etc.) so they're cheap to add.
- **Draft's body references a sibling draft that hasn't been
  filed yet** (e.g. 14a mentions 14b). Fine to file the body
  as-is; the sibling reference will resolve naturally when the
  sibling draft is also filed. If you'd like the upstream issue
  to carry a live link to the sibling issue, file both drafts
  first and then edit the body to insert the sibling issue's
  URL.
- **Maintainer rewrites the issue.** Note the rewrite in
  `ISSUES.md`'s **Status** column (e.g. `filed → rewritten by
  maintainer; see issue URL`). Do not edit the draft file —
  future audits should be able to see what Phase 1B originally
  asked for vs. what the maintainer converged on.
- **Coordination-issue alternative — 8 per-repo variants.**
  §2 #3 (SHA-pin actions) and §2 #18 (CI template) are drafted
  as single coordination issues filed against one primary repo
  with a per-repo checklist. If the maintainer prefers
  per-repo variants, the draft body stands unchanged against
  each variant repo; only the title needs a per-repo suffix.
  The trade-off is one large coordination thread vs. up to 8
  small threads — both are valid.
