# Filing packet — AgentMindCloud/vscode-grok-yaml

- **Target repo**: https://github.com/AgentMindCloud/vscode-grok-yaml
- **New issue URL**: https://github.com/AgentMindCloud/vscode-grok-yaml/issues/new
- **Drafts primary-targeting this repo**: 3 (§2 #14b, §2 #15a, §2 #16 — latter added Session 2, speculative)
- **Cross-ref / adopter follow-ups**: 0

Both primaries apply to the same README / repo description. They can be
filed independently in either order, or combined into a single PR by the
maintainer — §2 #14b is scoped narrowly to the "14 → 12" number, while
§2 #15a is the broader "downgrade the description to match the
LICENSE+README-only state" fix.

## Primaries to file

### Issue 1 — §2 #14b: Align landing-page "14 YAML standards" with grok-yaml-standards (12)

- **Draft source**: [`phase-1b/drafts/14b-vscode-grok-yaml-landing.md`](../drafts/14b-vscode-grok-yaml-landing.md)
- **Title** (paste verbatim): `Align landing-page "14 YAML standards" with grok-yaml-standards (12)`
- **Suggested labels**: `docs`, `version-coherence`, `ecosystem`, `good-first-issue`, `phase-1b`
- **Body**: paste the content of `phase-1b/drafts/14b-vscode-grok-yaml-landing.md` below the first `---` separator.
- **Filing note**: sibling draft `14a` is filed in `grok-install-action` (see `04-grok-install-action.md` Issue 1). DOC-1 fully closes only when both are filed.

### Issue 2 — §2 #15a: Downgrade landing-page / README description to reflect pre-alpha state

- **Draft source**: [`phase-1b/drafts/15a-vscode-grok-yaml-description.md`](../drafts/15a-vscode-grok-yaml-description.md)
- **Title** (paste verbatim): `Downgrade landing-page / README description to reflect pre-alpha state`
- **Suggested labels**: `docs`, `truthful-marketing`, `governance`, `phase-1b`
- **Body**: paste the content of `phase-1b/drafts/15a-vscode-grok-yaml-description.md` below the first `---` separator.
- **Filing note**: sibling draft `15b` is filed in `grok-agent-orchestra` (see `10-grok-agent-orchestra.md` Issue 1). GOV-3 + DOC-3 fully close only when both are filed.
- **Filing note**: this issue unblocks §2 #16 (bootstrap a real v0.1.0 extension). The §2 #16 speculative draft now exists (see Issue 3 below) but can only be filed after this issue merges upstream.

### Issue 3 — §2 #16: Bootstrap vscode-grok-yaml v0.1.0 (speculative — Session 2)

- **Draft source**: [`phase-1b/drafts/16-vscode-grok-yaml-bootstrap.md`](../drafts/16-vscode-grok-yaml-bootstrap.md)
- **Title** (paste verbatim): `Bootstrap vscode-grok-yaml v0.1.0 — read-only schema validation against grok-yaml-standards`
- **Suggested labels**: `bootstrap`, `v0.1.0`, `vscode`, `schema-validation`, `phase-1b`
- **Body**: paste the content of the draft below the first `---` separator.
- **Filing note (SPECULATIVE)**: this draft is speculative on §2 #15a. Do NOT file until Issue 2 above has merged upstream. The draft's metadata header carries the speculative-draft discipline ("drafted in `phase-1b/drafts/15a-vscode-grok-yaml-description.md`; not yet filed upstream; speculative") and a re-review trigger.
- **Filing note**: Part B of the draft offers two schema-fetch options (B1 = fetch from `grok-docs` daily mirror; B2 = bundle in this repo). Option B1 is recommended; if B1 is chosen, coordinate with `grok-docs` maintainers to confirm the `/assets/schemas/latest/` convention is live or easy to add. A one-liner comment on `grok-docs` after Issue 2 merges is enough.
- **Filing note**: Part A closes part of GOV-4 for this repo (`SECURITY.md` + `CONTRIBUTING.md` + `CODEOWNERS` ship with the bootstrap). No cross-ref to §2 #20's CODEOWNERS pattern needed — this repo is low-traffic and a one-line CODEOWNERS is enough.

## Cross-ref / adopter follow-ups

None for this repo. It is not a §2 #3 target and not a §2 #18 adopter
(no CI to promote to a template yet).
