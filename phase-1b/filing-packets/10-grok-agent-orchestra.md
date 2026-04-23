# Filing packet — AgentMindCloud/grok-agent-orchestra

- **Target repo**: https://github.com/AgentMindCloud/grok-agent-orchestra
- **New issue URL**: https://github.com/AgentMindCloud/grok-agent-orchestra/issues/new
- **Drafts primary-targeting this repo**: 1 (§2 #15b)
- **Cross-ref / adopter follow-ups**: 0

This repo is LICENSE-only (1 commit on `main`, no README, no source).
The sole Phase-1B primary for it is §2 #15b — the description
downgrade that matches the sibling §2 #15a fix in `vscode-grok-yaml`.

## Primaries to file

### Issue 1 — §2 #15b: Downgrade landing-page description to reflect skeleton state

- **Draft source**: [`phase-1b/drafts/15b-grok-agent-orchestra-description.md`](../drafts/15b-grok-agent-orchestra-description.md)
- **Title** (paste verbatim): `Downgrade landing-page description to reflect skeleton state`
- **Suggested labels**: `docs`, `truthful-marketing`, `governance`, `phase-1b`
- **Body**: paste the content of `phase-1b/drafts/15b-grok-agent-orchestra-description.md` below the first `---` separator.
- **Filing note**: sibling draft `15a` is filed in `vscode-grok-yaml` (see `07-vscode-grok-yaml.md` Issue 2). GOV-3 + DOC-3 fully close only when both are filed.
- **Filing note**: this repo currently has no README. The "Option A" acceptance criterion in the draft creates one as part of the fix. That's also a natural moment to establish issue / PR templates — consider pairing with `CONTRIBUTING.md` if the maintainer is open to it.

## Cross-ref / adopter follow-ups

None for this repo. It has no CI (so no §2 #3 or §2 #18 touch-point)
and is not an adopter of any ecosystem-wide coordination issue yet.

§2 #17 (bootstrap a single working multi-agent pattern + define the
"Lucas safety veto" behaviourally) is catalogued as a **post-filing
follow-up** in `phase-1b/ISSUES.md` — it is blocked by §2 #5 (unified
safety-profile rubric) rather than by Issue 1 above. Do **not** draft
§2 #17 until §2 #5 lands upstream; the safety-rubric's semantics
will shape what "Lucas veto" means in code, and drafting before
that creates rework.
