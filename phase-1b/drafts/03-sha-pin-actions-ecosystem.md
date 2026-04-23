# Pin every GitHub Action by commit SHA across the ecosystem, with Renovate / Dependabot keeping them fresh

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #3 (`audits/99-recommendations.md`)
- **Target repos (8)**: AgentMindCloud/grok-install, grok-yaml-standards, grok-install-cli, grok-install-action, grok-docs, awesome-grok-agents, grok-agents-marketplace, grok-build-bridge
- **Filing strategy**: one coordination issue — recommended primary = **AgentMindCloud/grok-install** (spec root, most visible) — with a per-repo checklist. The user may file this body unchanged in all 8 repos as independent issues if coordination is not desired.
- **Risks closed**: SUP-1 (S2) — from `audits/98-risk-register.md`
- **Source audits**: `[→ 01 §6]`, `[→ 02 §5]`, `[→ 02 §6]`, `[→ 03 §5]`, `[→ 04 §6]`, `[→ 05 §5]`, `[→ 06 §6]`, `[→ 08 §5]`, `[→ 09 §5]`
- **Effort (§2)**: M — ecosystem-coordination, not per-repo difficulty
- **Blocked by**: none
- **Cross-refs**: §2 #18 (CI template promotion — the natural vehicle for propagating this change to adopters once the coordination issue is filed)
- **Suggested labels**: `security`, `supply-chain`, `ci`, `ecosystem`, `phase-1b`

---

## Context

Every repo in the Grok ecosystem CI pins third-party GitHub Actions
**by major tag** (e.g. `actions/checkout@v4`, `ibiqlik/action-yamllint@v3`)
rather than by commit SHA. A compromised or silently re-moved tag
executes arbitrary code with whatever `permissions:` each workflow
declares — on every consumer repo, on every run, on every push or PR.

The ecosystem already sets a strong precedent for exact pinning of
library dependencies (e.g. `grok-yaml-standards` exact-pins `yamllint
1.35.1` / `ajv-cli 5.0.0` / `js-yaml 4.1.0`; `grok-docs` uses `==`
pins in `requirements.txt`). Applying the same discipline to GitHub
Actions closes the remaining supply-chain surface that is visible to
an external attacker and well documented as a mitigation (GitHub's
own hardening guide recommends SHA pinning for third-party actions).

The fix is two-part:

1. **Replace every third-party `@vN` tag with a full 40-char commit
   SHA**, adding a trailing comment with the version for reviewer
   convenience.
2. **Land a Renovate (or Dependabot) config** so SHAs actually move
   with upstream — otherwise SHA pinning becomes a staleness trap.

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch, paths stable). Each
repo below shows at least one major-tag pin that SHOULD be a SHA:

| Repo | Workflow(s) | Example current pin | Notes |
|------|-------------|---------------------|-------|
| grok-install | `.github/workflows/validate.yml` | `ibiqlik/action-yamllint@v3`, `markdownlint-cli2-action@v16` | Audit 01 §6. No lockfile visible. |
| grok-yaml-standards | `.github/workflows/validate-schemas.yml` | actions pinned by major tag | Audit 02 §5+§6 — "same supply-chain pattern as grok-install". Library deps are already exact-pinned (good). |
| grok-install-cli | `.github/workflows/ci.yml`, `security.yml` | actions pinned by major tag | Audit 03 §5. Library deps use `>=` lower-bound ranges; out of scope for *this* issue but worth noting. |
| grok-install-action | `action.yml`, `.github/workflows/test.yml` | `actions/checkout@v4`, `actions/setup-node@v4` | Audit 04 §6. Also installs `grok-install-cli` via `npm install -g …@2.14.0` — a separate supply-chain hole tracked under §2 #6. |
| grok-docs | `.github/workflows/*` | `actions/checkout@v4` | Audit 05 §5. Library deps are exact-pinned — ecosystem best-in-class, just needs action-side parity. |
| awesome-grok-agents | `.github/workflows/*` | GitHub actions by major tag; `ajv-cli@5`, `ajv-formats@3` majors | Audit 06 §6. |
| grok-agents-marketplace | `.github/workflows/dependency-review.yml` etc. | `actions/checkout@v4`, `actions/setup-node@v4` | Audit 08 §5. Also caret-ranged runtime deps — separate issue (§3.2 per-repo deferral). |
| grok-build-bridge | `.github/workflows/*` | `lychee-action@v2` + others | Audit 09 §5. |

Risk register — `98-risk-register.md`:

- **SUP-1** (S2, likelihood medium): "GitHub Actions pinned by major
  tag (`actions/checkout@v4`, etc.) rather than commit SHA across
  the entire ecosystem — a compromised or moved tag executes
  arbitrary code with workflow permissions on every consumer."

## Reproduction

For any of the 8 repos above:

```bash
grep -RnE "uses:\s+[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@v[0-9]" .github/workflows/ action.yml 2>/dev/null
```

Any line that matches — except `actions/checkout` / `actions/setup-*`
/ etc. that is already a full SHA followed by `# v<tag>` — is in
scope for this issue.

## Acceptance criteria

### Per-repo checklist

(If filing as a coordinated issue in `grok-install`, leave all
checkboxes and let cross-repo PRs tick them one-by-one. If filing
per-repo, keep only the row for the target repo.)

- [ ] `grok-install` — every third-party action pinned by 40-char
      SHA, trailing `# v<tag>` comment for reviewer readability.
- [ ] `grok-yaml-standards` — same.
- [ ] `grok-install-cli` — same; also drop the `|| true` on
      `pip-audit` at the same time if §2 #13 hasn't landed yet
      (cross-ref).
- [ ] `grok-install-action` — same, including `action.yml`'s
      `setup-node@v4` and `checkout@v4`.
- [ ] `grok-docs` — same.
- [ ] `awesome-grok-agents` — same.
- [ ] `grok-agents-marketplace` — same; does not require
      touching the caret-ranged runtime deps (tracked as §3.2
      deferral row [→ 08 §9 row 1]).
- [ ] `grok-build-bridge` — same.

### Renovate / Dependabot configuration

Pick **one** of (A) or (B) per repo; either satisfies the
"SHAs actually move" half of the issue.

#### Option A — Renovate (recommended for cross-repo consistency)

- [ ] Add `renovate.json` to each repo with
      `"pinDigests": true`, `"pinDigestsAsSemver": true`, and
      `"matchManagers": ["github-actions"]` bumping on a weekly
      schedule.
- [ ] Run once in maintainer mode to rewrite existing `@vN`
      pins to SHAs; subsequent PRs keep them moving.
- [ ] Consider a shared `renovate.json` base config published
      from `grok-install` that other repos `extends` (fits the
      same "spec-root is the coordination point" pattern used
      for the rest of the ecosystem).

#### Option B — Dependabot

- [ ] Add `.github/dependabot.yml` with `package-ecosystem:
      "github-actions"`, `interval: "weekly"`, and leave
      Dependabot's default SHA-pin behaviour on.
- [ ] Accept the initial Dependabot PR as the SHA-rewrite PR.

## Notes

- **Landing order.** This issue is independent of §2 #13
  (blocking `pip-audit` + secret scanning) and §2 #18 (CI
  template promotion). They can all land in parallel. In
  practice §2 #18 makes the ongoing rollout cheaper because
  the promoted template inherits the SHA-pins in one place.
- **Out of scope here.** Runtime library dependency drift
  (e.g. `grok-agents-marketplace`'s caret ranges, audit 08
  §9 row 1) is tracked in `audits/99-recommendations.md §3.2`
  as a per-repo deferral. This issue is scoped narrowly to
  GitHub-Actions SHA pinning + the automation that keeps
  them moving.
- **Verification.** A single-line check to enforce the
  invariant in CI: `! grep -RnE "uses:\s+[^@]+@v[0-9]"
  .github/workflows action.yml 2>/dev/null`. Add it to each
  repo's lint workflow if convenient.
- **Filing strategy reminder** (from the metadata header at
  the top of this draft): if filing as a single coordination
  issue in `grok-install`, maintainers of each downstream
  repo can open a linked PR against the checkbox row for
  their repo. If filing 8 variants, each repo only needs the
  body with its own row; the Renovate/Dependabot section
  applies unchanged per-repo.
