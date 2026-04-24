# Migrate the remaining 5 examples to v2.14 schema and gate them in CI

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #9 (`audits/99-recommendations.md`)
- **Target repo**: AgentMindCloud/grok-install
- **Risks closed**: VER-1 (S1) — from `audits/98-risk-register.md`
- **Source audits**: `[→ 01 §1]`, `[→ 01 §5]`, `[→ 01 §9 row 1]`
- **Blocked by**: none
- **Suggested labels**: `bug`, `spec`, `ci`, `version-coherence`, `S1`, `phase-1b`

---

## Context

The v2.14 spec is shipped and advertised, but the `schema-v2-14`
validation job in `.github/workflows/validate.yml` covers only
**1 of 6** top-level examples (`examples/janvisuals/grok-install.yaml`).
The other five examples are still validated against the v2.13 schema
only.

Practical consequence: any downstream validator (CLI, action,
marketplace, standards conformance tests) that pins the v2.14 schema
inherits a validation corpus of size one. The contract is advertised
as v2.14; the evidence that real-world examples satisfy v2.14 is
effectively absent.

This is also the largest self-inflicted coherence gap in the spec
repo today. The v2.14 migration announced itself but did not finish;
closing it is hours of work plus a CI line.

## Evidence

From `main` on 2026-04-23 (WebFetch; line numbers omitted, paths are
stable):

- `examples/` tree (six top-level examples):
  - `examples/janvisuals/grok-install.yaml` — **already on v2.14**
  - `examples/minimal.yaml` — still v2.13
  - `examples/multi-agent.yaml` — still v2.13
  - `examples/research-swarm.yaml` — still v2.13
  - `examples/voice-agent.yaml` — still v2.13
  - `examples/x-reply-bot.yaml` — still v2.13
- `.github/workflows/validate.yml` job matrix:
  - `schema-v2-13` runs against all six examples (back-compat)
  - `schema-v2-14` runs against `examples/janvisuals/` only
- Schemas in the repo today:
  - `schemas/v2.14/schema.json` (JSON Schema draft-2020)
  - `schemas/grok-install-v2.13.schema.json` (draft-7, retained)
- Risk register — `98-risk-register.md`:
  - **VER-1** (S1, likelihood high): "`grok-install` v2.14 schema
    validates only **1 of 6** in-repo examples (`janvisuals`); the
    spec advertises a contract its own corpus violates. Downstream
    validators built against the spec will fail on official samples."

*(Sources: audit 01 §1 summary, audit 01 §5 Tests & CI, audit 01
§9 row 1.)*

## Reproduction

Clone `main` and run:

```
# existing v2.13 job — passes for all 6
ajv validate -s schemas/grok-install-v2.13.schema.json \
  -d 'examples/**/*.yaml' --spec=draft-07

# what v2.14 *should* cover — currently only the flagship passes
ajv validate -s schemas/v2.14/schema.json \
  -d 'examples/**/*.yaml' --spec=draft-2020
```

The second command fails on the five non-`janvisuals` examples,
typically on the v2.14-only additive fields (e.g. the optional
`visuals:` block) or on moved / renamed keys at the spec boundary.

## One-command migration

The v2.14 migration is additive; most examples need only:

1. Bump the top-level `grok_install_version:` field (or equivalent
   `apiVersion:` if the spec uses that name) to `v2.14`.
2. Add an explicit (possibly empty) `visuals:` block if the example
   benefits from it, or leave it unset (v2.14 makes `visuals:`
   optional).
3. Reconcile any renamed keys surfaced by `ajv validate` above.

A maintainer-runnable one-shot (pseudocode; adapt to taste):

```bash
for f in examples/minimal.yaml examples/multi-agent.yaml \
         examples/research-swarm.yaml examples/voice-agent.yaml \
         examples/x-reply-bot.yaml; do
  yq -i '.grok_install_version = "v2.14"' "$f"
done
ajv validate -s schemas/v2.14/schema.json \
  -d 'examples/**/*.yaml' --spec=draft-2020
```

Any remaining failures after the version bump are the actual
spec-conformance deltas per-example and must be resolved manually;
they're the signal this issue is trying to surface.

## Acceptance criteria

- [ ] All six top-level examples under `examples/` validate cleanly
      against `schemas/v2.14/schema.json` under JSON Schema
      draft-2020 (i.e. all five currently-v2.13 examples migrated).
- [ ] `.github/workflows/validate.yml` — `schema-v2-14` job
      expanded to the full `examples/**/*.yaml` glob. The v2.13
      back-compat job may remain; it is **not** the gating job.
- [ ] A new CI step (inside `validate.yml` or a new workflow)
      **fails the run** if any file under `examples/` does not
      validate against the current-canonical schema
      (`schemas/v2.14/schema.json`). This turns VER-1's underlying
      condition into a permanent regression gate.
- [ ] A one-line note in `CHANGELOG.md` (or `docs/changelog.md`)
      confirming the five migrated files + the new gate.
- [ ] Optional: split-schema matrix — every example is validated
      against **every retained schema version** for as long as the
      repo keeps v2.12 / v2.13 alongside v2.14; this closes the
      next VER-class risk if a v2.15 lands in the same posture.

## Notes

- §2 #10 (ship `grok-docs` v2.14 content) depends on the spec-side
  examples being v2.14-valid so docs can link to them without
  caveats; this issue should land first.
- §2 #8 (migrate `grok-yaml-standards` to draft-2020-12 for v1.3)
  is a sibling version-coherence fix but on the standards repo,
  not the spec repo — out of scope here.
- If v2.12 is being retained purely for back-compat, consider
  pairing this with §3.2's deferred v2.12→v2.13→v2.14 deprecation
  schedule (audit 01 §9 row 3) so the CI matrix doesn't grow
  unboundedly.
