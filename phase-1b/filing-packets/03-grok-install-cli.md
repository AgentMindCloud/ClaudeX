# Filing packet — AgentMindCloud/grok-install-cli

- **Target repo**: https://github.com/AgentMindCloud/grok-install-cli
- **New issue URL**: https://github.com/AgentMindCloud/grok-install-cli/issues/new
- **Drafts primary-targeting this repo**: 4 (§2 #6, §2 #13 + §2 #7 and §2 #1 — latter two added Session 2, speculative)
- **Cross-ref / adopter follow-ups**: 2 (§2 #3 variant, §2 #18 adopter)

## Primaries to file

### Issue 1 — §2 #6: Resolve the npm-vs-Python mismatch in the grok-install-cli install path

- **Draft source**: [`phase-1b/drafts/06-cli-install-mechanism.md`](../drafts/06-cli-install-mechanism.md)
- **Title** (paste verbatim): `Resolve the npm-vs-Python mismatch in the grok-install-cli install path`
- **Suggested labels**: `bug`, `version-coherence`, `ecosystem`, `S1`, `phase-1b`
- **Body**: paste the content of `phase-1b/drafts/06-cli-install-mechanism.md` below the first `---` separator.
- **Filing note**: the draft's metadata recommends `grok-install-cli` as the primary target; a short pointer issue against `grok-install-action` (see `04-grok-install-action.md` cross-ref A) is the recommended companion so adopters on either side land on the same thread.

### Issue 2 — §2 #13: Make pip-audit blocking and add secret-scanning (gitleaks / trufflehog) in CI

- **Draft source**: [`phase-1b/drafts/13-blocking-pip-audit-plus-secret-scan.md`](../drafts/13-blocking-pip-audit-plus-secret-scan.md)
- **Title** (paste verbatim): `Make pip-audit blocking and add secret-scanning (gitleaks / trufflehog) in CI`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`
- **Body**: paste the content of `phase-1b/drafts/13-blocking-pip-audit-plus-secret-scan.md` below the first `---` separator.
- **Filing note**: the same body is filed independently in `grok-build-bridge` (see `09-grok-build-bridge.md` Issue 1); the two repos are pilots for the fix.

### Issue 3 — §2 #7: Publish tagged releases matching pyproject.toml; align action pin (speculative — Session 2)

- **Draft source**: [`phase-1b/drafts/07-grok-install-cli-releases-pyproject-alignment.md`](../drafts/07-grok-install-cli-releases-pyproject-alignment.md)
- **Title** (paste verbatim): `Publish grok-install-cli GitHub releases whose tag matches pyproject.toml; align grok-install-action's pin`
- **Suggested labels**: `release`, `version-coherence`, `packaging`, `S1`, `phase-1b`
- **Body**: paste the content of the draft below the first `---` separator.
- **Filing note (SPECULATIVE)**: this draft is speculative on Issue 1 above (§2 #6). Do NOT file until Issue 1 has merged upstream — the chosen install channel (Python / npm / both) determines which branch of the draft's Part B applies.
- **Filing note**: after this primary's first release ships, file a short cross-ref issue in `grok-install-action` updating the `cli-version` default pin. The three branches in Part B (Option A Python canonical / Option B npm canonical / Option C both) give the exact action-side body — pick the one matching #6's landed resolution, delete the other two before pasting.
- **Filing note**: Part A Step 1 offers two version-naming choices (A1 = `0.1.0` honestly matches current `pyproject.toml`; A2 = `2.14.0` matches spec). Recommendation: A1. Flag in the filed issue so reviewers can redirect if preferred.

### Issue 4 — §2 #1: Extract shared grok-safety-rules package (speculative — Session 2)

- **Draft source**: [`phase-1b/drafts/01-shared-grok-safety-rules-package.md`](../drafts/01-shared-grok-safety-rules-package.md)
- **Title** (paste verbatim): `Extract a shared grok-safety-rules package consumed by every safety-aware repo`
- **Suggested labels**: `extraction`, `shared-library`, `safety`, `ecosystem`, `phase-1b`
- **Body**: paste the content of the draft below the first `---` separator.
- **Filing note (SPECULATIVE)**: this draft is speculative on §2 #5 (the safety-profile rubric). Do NOT file until §2 #5 has merged upstream in `grok-yaml-standards` — the package's public API mirrors #5's seven-axis rubric shape.
- **Filing note**: Part A offers two ownership options (A1 = in-repo extraction from `grok-install-cli`; A2 = new `AgentMindCloud/grok-safety-rules` repo). Recommendation: A2. If A2, this packet's primary count above should shift — file as an issue on the new repo instead. If A1, file here; the primary count reads correctly as-is.
- **Filing note**: Part B's consumer-adoption follow-ups (CLI refactor, bridge refactor) open only after v0.1.0 of the package ships. Do NOT pre-file the follow-ups — the package's API may shift during v0.1.0 review.

## Cross-ref / adopter follow-ups

### Cross-ref A — §2 #3 variant: Pin every GitHub Action by commit SHA

- **Open only if**: you chose the per-repo-variant path for §2 #3. If you filed §2 #3 as a single coordination issue in `grok-install`, this is subsumed by the coordination issue's checklist.
- **Coordination issue URL (if coordinating)**: `<TODO: primary URL from grok-install>`
- **Draft source**: [`phase-1b/drafts/03-sha-pin-actions-ecosystem.md`](../drafts/03-sha-pin-actions-ecosystem.md)
- **Suggested title (variant path)**: `Pin GitHub Actions by commit SHA + Renovate/Dependabot config`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`
- **Suggested body (variant path)**: paste the content of `phase-1b/drafts/03-sha-pin-actions-ecosystem.md` below the first `---` separator. In the per-repo checklist keep only the row for `grok-install-cli`; delete the other 7 rows. If `security.yml`'s `pip-audit` is still `|| true` when this lands, either include the `|| true` drop in this PR or explicitly defer to §2 #13's issue (see Issue 2 above).

### Cross-ref B — §2 #18 adopter: Adopt the grok-build-bridge CI baseline template

- **Open only after**: §2 #18's primary issue lands in `grok-build-bridge`.
- **Primary issue URL (fill in once it lands)**: `<TODO: primary URL>`
- **Draft source**: [`phase-1b/drafts/18-ci-template-baseline.md`](../drafts/18-ci-template-baseline.md) — §Part 2, `grok-install-cli` row.
- **Suggested title**: `Adopt the grok-build-bridge CI baseline template (tracks <TODO: primary URL>)`
- **Suggested labels**: `ci`, `ecosystem`, `supply-chain`, `phase-1b`
- **Suggested body**:

  ```
  Tracking the ecosystem CI-template adoption requested in <TODO: primary URL>.

  Template adoption for this repo: merge the current security.yml's
  pip-audit + bandit jobs into the template's safety-scan job. Keep
  the publish.yml release workflow as repo-local.

  Gated on:
  - <TODO: primary URL> landing.
  - §2 #13 having landed here first (so the merged safety-scan inherits
    blocking pip-audit + secret-scan).
  ```
