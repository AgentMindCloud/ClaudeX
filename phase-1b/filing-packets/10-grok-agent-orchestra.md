# Filing packet — AgentMindCloud/grok-agent-orchestra

- **Target repo**: https://github.com/AgentMindCloud/grok-agent-orchestra
- **New issue URL**: https://github.com/AgentMindCloud/grok-agent-orchestra/issues/new
- **Drafts primary-targeting this repo**: 2 (§2 #15b, §2 #17 — latter added Session 2, deepest speculative)
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

### Issue 2 — §2 #17: Bootstrap v0.1.0 with plan-execute-critique pattern + behavioural Lucas veto (speculative — Session 2, deepest)

- **Draft source**: [`phase-1b/drafts/17-grok-agent-orchestra-bootstrap.md`](../drafts/17-grok-agent-orchestra-bootstrap.md)
- **Title** (paste verbatim): `Bootstrap grok-agent-orchestra with a working multi-agent pattern + a behavioural Lucas safety veto`
- **Suggested labels**: `bootstrap`, `v0.1.0`, `multi-agent`, `lucas-veto`, `phase-1b`
- **Body**: paste the content of the draft below the first `---` separator.
- **Filing note (SPECULATIVE, deepest)**: this draft is speculative on BOTH §2 #5 (rubric) AND §2 #1 (shared package). Do NOT file until §2 #5 has merged upstream in `grok-yaml-standards`. The §2 #1 prerequisite has an explicit fall-back in the draft — pin `grok-install-cli`'s `safety/` directly with a TODO migrate comment if #1 isn't shipped at filing time.
- **Filing note**: also file only after Issue 1 above (§2 #15b) has merged — the bootstrap's README rewrites the repo's honesty; doing that before #15b creates two conflicting README changes.
- **Filing note**: Part A adopts the §2 #18 CI template from day one (audit 10 §9 row 3). If §2 #18 has NOT landed in `grok-build-bridge` at filing time, the bootstrap can still ship `ci.yml` derived from the §2 #18 draft body — flag as a future-template-adoption migration once #18 lands.
- **Filing note**: Part B's Lucas definition uses the exact phrase "strictest claimed safety profile in the team" — this is a design decision (not a convention). The draft's Notes explicitly defend it against the alternative "proposing agent's profile only". Willing to revisit post-v0.1.0.

## Cross-ref / adopter follow-ups

None for this repo. It has no CI (so no §2 #3 or §2 #18 touch-point)
and is not an adopter of any ecosystem-wide coordination issue yet
— though §2 #17 Part A adopts the §2 #18 CI template pattern at
bootstrap time, so this repo becomes an adopter in spirit once §2 #17 ships.
