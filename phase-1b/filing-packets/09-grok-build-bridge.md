# Filing packet — AgentMindCloud/grok-build-bridge

- **Target repo**: https://github.com/AgentMindCloud/grok-build-bridge
- **New issue URL**: https://github.com/AgentMindCloud/grok-build-bridge/issues/new
- **Drafts primary-targeting this repo**: 2 (§2 #13, §2 #18)
- **Cross-ref / adopter follow-ups**: 1 (§2 #3 variant)

## Primaries to file

### Issue 1 — §2 #13: Make pip-audit blocking and add secret-scanning (gitleaks / trufflehog) in CI

- **Draft source**: [`phase-1b/drafts/13-blocking-pip-audit-plus-secret-scan.md`](../drafts/13-blocking-pip-audit-plus-secret-scan.md)
- **Title** (paste verbatim): `Make pip-audit blocking and add secret-scanning (gitleaks / trufflehog) in CI`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`
- **Body**: paste the content of `phase-1b/drafts/13-blocking-pip-audit-plus-secret-scan.md` below the first `---` separator.
- **Filing note**: the same body is filed independently in `grok-install-cli` (see `03-grok-install-cli.md` Issue 2); the two repos are co-pilots. In this repo, the fix lives in `.github/workflows/ci.yml`'s `safety-scan` job (merge rather than a separate `security.yml`).

### Issue 2 — §2 #18: Promote grok-build-bridge's CI workflow as the ecosystem baseline CI template

- **Draft source**: [`phase-1b/drafts/18-ci-template-baseline.md`](../drafts/18-ci-template-baseline.md)
- **Title** (paste verbatim): `Promote grok-build-bridge's CI workflow as the ecosystem baseline CI template`
- **Suggested labels**: `ci`, `ecosystem`, `supply-chain`, `test-coverage`, `phase-1b`
- **Body**: paste the content of `phase-1b/drafts/18-ci-template-baseline.md` below the first `---` separator.
- **Filing note**: this is the coordination issue — the 7 adopter repos (grok-install, grok-yaml-standards, grok-install-cli, grok-install-action, grok-docs, awesome-grok-agents, grok-agents-marketplace) each get a cross-ref issue against this primary once it lands. See the individual per-repo packet files' "Cross-ref B" sections for those follow-ups.
- **Filing note**: recommended to file §2 #3 + §2 #13 against this repo (Issue 1 above and §2 #3 variant below) **before** freezing the template here, so adopters inherit the corrected posture in one cut. If that ordering is not practical, the primary's draft body explicitly supports a "land the template now and cut a follow-up template-bump PR" path.

## Cross-ref / adopter follow-ups

### Cross-ref A — §2 #3 variant: Pin every GitHub Action by commit SHA

- **Open only if**: you chose the per-repo-variant path for §2 #3.
- **Coordination issue URL (if coordinating)**: `<TODO: primary URL from grok-install>`
- **Draft source**: [`phase-1b/drafts/03-sha-pin-actions-ecosystem.md`](../drafts/03-sha-pin-actions-ecosystem.md)
- **Suggested title (variant path)**: `Pin GitHub Actions by commit SHA + Renovate/Dependabot config`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`
- **Suggested body (variant path)**: paste the #3 draft content below the first `---` separator; keep only the `grok-build-bridge` checklist row. Land this **before** Issue 2 (template extraction) so the extracted template inherits SHA pins.

## Sequencing note

Ideal file-order for this repo's three Phase-1B interventions:

1. §2 #3 variant (SHA-pin actions) — or rely on the coordination
   issue in `grok-install` if you chose that path.
2. Issue 1 (§2 #13 blocking pip-audit + secret-scan).
3. Issue 2 (§2 #18 template extraction).

Landing #3 and #13 before the template is frozen lets step 3 capture
both posture fixes in one cut, so all 7 adopter repos inherit
correct posture on first adoption.
