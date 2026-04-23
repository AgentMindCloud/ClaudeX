# Filing packet — AgentMindCloud/grok-install-cli

- **Target repo**: https://github.com/AgentMindCloud/grok-install-cli
- **New issue URL**: https://github.com/AgentMindCloud/grok-install-cli/issues/new
- **Drafts primary-targeting this repo**: 2 (§2 #6, §2 #13)
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
