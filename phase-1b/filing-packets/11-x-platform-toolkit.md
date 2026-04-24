# Filing packet — AgentMindCloud/x-platform-toolkit

- **Target repo**: https://github.com/AgentMindCloud/x-platform-toolkit
- **New issue URL**: https://github.com/AgentMindCloud/x-platform-toolkit/issues/new
- **Drafts primary-targeting this repo**: 1 (§2 #19 — seventh pass 2026-04-23; non-speculative)
- **Cross-ref / adopter follow-ups**: 0 (not in §2 #3's 8-repo scope; not in §2 #18's adopter list)

The seventh-pass added §2 #19 as the primary for this repo:
adds minimum CI (html-validate + stylelint + lychee link-check
+ Live-vs-Spec consistency script). Closes SUP-5 (S3) outright.
M-effort; non-speculative.

## Primaries to file

### Issue 1 — §2 #19: Add minimum CI (html-validate + stylelint + link-check + Live-vs-Spec consistency)

- **Draft source**: [`phase-1b/drafts/19-x-platform-toolkit-minimum-ci.md`](../drafts/19-x-platform-toolkit-minimum-ci.md)
- **Title** (paste verbatim): `Add minimum CI to x-platform-toolkit (html-validate + stylelint + link-check + Live-vs-Spec consistency)`
- **Suggested labels**: `ci`, `supply-chain`, `quality`, `phase-1b`
- **Body**: paste the content of the draft below the first `---` separator.
- **Filing note**: two-part acceptance (A: three standard lint jobs; B: one repo-specific consistency script). Parts can land separately — Part A is close to S-effort once copied from the draft; Part B's Python consistency script is what pushes this to M because the README regex needs one iteration against the maintainer's actual Live/Spec table shape.
- **Filing note**: non-speculative — no in-repo prerequisite. File whenever convenient.
- **Filing note**: Part A pins every action by SHA from day one (matches §2 #3 ecosystem discipline). This repo IS in §2 #3's 8-repo checklist; landing §2 #19 first satisfies §2 #3's work for this repo as a side effect. Flag in the filed issue body so reviewers see the alignment.
- **Filing note**: expected first-run behaviour — CI may fail on the introducing PR if there is pre-existing Live/Spec drift. That's the point; fix the drift in the same PR (the draft's Part B last bullet spells this out).
- **Filing note**: SUP-5 closure is manual — `audits/98-risk-register.md` row SUP-5 flips to `mitigated` on PR merge. The Phase-1B review layer owns that flip; flagged in the draft's Part B and Notes.

## Cross-ref / adopter follow-ups

None.

## Future drafting notes

§2 #19 was the last §2 rec drafted in Phase 1B (seventh
pass, 2026-04-23). All 20 §2 recs now have ready-to-file
issue bodies under `phase-1b/drafts/`.

Per-repo deferrals catalogued in `audits/99-recommendations.md §3.2`
for this repo — including `[→ 11 §9 row 2]` (consolidate
`shared/grok-client` with `grok-install-cli`; candidate for §2
#2's "JS-second-or-never" path) and `[→ 11 §9 row 3]`
(token-handling docs; closes SEC-4) — are NOT drafted in Phase
1B. They sit in the §3 deferrals pile pending a future pass
if/when the user requests.
