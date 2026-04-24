# Filing packet — AgentMindCloud/awesome-grok-agents

- **Target repo**: https://github.com/AgentMindCloud/awesome-grok-agents
- **New issue URL**: https://github.com/AgentMindCloud/awesome-grok-agents/issues/new
- **Drafts primary-targeting this repo**: 2 (§2 #11, §2 #12 — both added Session 2, speculative)
- **Cross-ref / adopter follow-ups**: 2 (§2 #3 variant, §2 #18 adopter)

Session 2 added two speculative primaries here. Both are
independently gated on different prerequisite drafts (§2 #11 on
§2 #5; §2 #12 on §2 #6 + #7). File only after the relevant
prerequisites have merged upstream.

## Primaries to file

### Issue 1 — §2 #11: Add a permissive-profile exemplar template (speculative — Session 2)

- **Draft source**: [`phase-1b/drafts/11-awesome-grok-agents-permissive-exemplar.md`](../drafts/11-awesome-grok-agents-permissive-exemplar.md)
- **Title** (paste verbatim): `Add a permissive-profile exemplar template to awesome-grok-agents`
- **Suggested labels**: `template`, `safety-profile`, `permissive`, `phase-1b`
- **Body**: paste the content of the draft below the first `---` separator.
- **Filing note (SPECULATIVE)**: this draft is speculative on §2 #5 (the safety-profile rubric). Do NOT file until §2 #5 has merged upstream in `grok-yaml-standards` — the exemplar template's `grok-install.yaml` body mirrors #5's `permissive` row cell-for-cell.
- **Filing note**: proposed template name is `internal-ci-assistant/`; the draft calls out three alternative names ("local-dev helper", "scheduled data-export", "self-hosted dashboard") that are also honest. Pick the one that best matches an actual planned use case; the template's README/`grok-install.yaml` body adjusts accordingly.
- **Filing note**: Part B of the draft (CI distribution report) is optional; the draft explicitly flags that Part A alone is a net win if the maintainer wants to split the PR.

### Issue 2 — §2 #12: Replace grok_install_stub with a real grok-install-cli invocation (speculative — Session 2)

- **Draft source**: [`phase-1b/drafts/12-awesome-grok-agents-replace-install-stub.md`](../drafts/12-awesome-grok-agents-replace-install-stub.md)
- **Title** (paste verbatim): `Replace grok_install_stub with a real grok-install-cli invocation in validate-templates.yml`
- **Suggested labels**: `ci`, `validation`, `tooling`, `phase-1b`
- **Body**: paste the content of the draft below the first `---` separator.
- **Filing note (SPECULATIVE, deepest)**: this draft is speculative on BOTH §2 #6 AND §2 #7. Do NOT file until both have merged upstream. Part A's install command and pin are template forms until then.
- **Filing note**: Part A recommends Option A of §2 #6 (Python canonical) as the default example. Swap in the actually-landed option at filing time; delete the other two branches' references in Part A.
- **Filing note**: Part B (rubric conformance matrix) is optional; it only ships if §2 #5 has landed upstream when this PR opens. Otherwise defer Part B to a follow-up PR.
- **Filing note**: Part A deletes `scripts/grok_install_stub/`. Do NOT keep the stub as a fallback — a fallback path no one exercises rots. This is deliberate and called out in the draft's Notes.

## Cross-ref / adopter follow-ups

### Cross-ref A — §2 #3 variant: Pin every GitHub Action by commit SHA

- **Open only if**: you chose the per-repo-variant path for §2 #3.
- **Coordination issue URL (if coordinating)**: `<TODO: primary URL from grok-install>`
- **Draft source**: [`phase-1b/drafts/03-sha-pin-actions-ecosystem.md`](../drafts/03-sha-pin-actions-ecosystem.md)
- **Suggested title (variant path)**: `Pin GitHub Actions by commit SHA + Renovate/Dependabot config`
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`
- **Suggested body (variant path)**: paste the #3 draft content below the first `---` separator; keep only the `awesome-grok-agents` checklist row. Library deps here are major-pinned (`ajv-cli@5`, `ajv-formats@3`) — out of scope for *this* issue but worth mentioning so reviewers don't confuse the two.

### Cross-ref B — §2 #18 adopter: Adopt the grok-build-bridge CI baseline template

- **Open only after**: §2 #18's primary issue lands in `grok-build-bridge`.
- **Primary issue URL (fill in once it lands)**: `<TODO: primary URL>`
- **Draft source**: [`phase-1b/drafts/18-ci-template-baseline.md`](../drafts/18-ci-template-baseline.md) — §Part 2, `awesome-grok-agents` row.
- **Suggested title**: `Adopt the grok-build-bridge CI baseline template (tracks <TODO: primary URL>)`
- **Suggested labels**: `ci`, `ecosystem`, `phase-1b`
- **Suggested body**:

  ```
  Tracking the ecosystem CI-template adoption requested in <TODO: primary URL>.

  Template adoption here is also the natural moment to wire up §2 #12
  (replace `grok_install_stub` with a real CLI invocation) — once §2 #6
  + #7 land, the adopted safety-scan job can run the live CLI against
  templates in CI.

  Gated on:
  - <TODO: primary URL> landing.
  - §2 #6 + §2 #7 landing in grok-install-cli (if §2 #12 work is
    bundled into the same PR).
  ```
