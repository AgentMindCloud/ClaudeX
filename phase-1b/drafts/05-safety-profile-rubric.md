# Publish a unified safety-profile rubric (strict / standard / permissive) with conformance tests

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #5 (`audits/99-recommendations.md`)
- **Target repo (primary — owner of the rubric artefact)**: AgentMindCloud/grok-yaml-standards
- **Target repos (consumers / conformance-test adopters)**: AgentMindCloud/awesome-grok-agents, AgentMindCloud/grok-install-cli, AgentMindCloud/grok-build-bridge, AgentMindCloud/grok-agent-orchestra
- **Filing strategy**: one coordination issue in `grok-yaml-standards` (primary — owner of the rubric); consumer-repo checklist rows inside the acceptance criteria. The user may optionally file short cross-reference issues in the four consumer repos once this primary lands, pointing at its `rubric-v1.md` path.
- **Risks closed**: partial UNV-3 (S3) — enables UNV-4 (S3) closure once consumers adopt. From `audits/98-risk-register.md`.
- **Source audits**: `[→ 02 §9 row 3]`, `[→ 06 §9 row 1]`. Substantive cross-cut evidence in `audits/00-ecosystem-overview.md §6` (tripartite safety model, 6/4/0 distribution, three independent static-regex implementations).
- **Effort (§2)**: M — the rubric text itself is small; the conformance-test format + coordination across 4 consumer repos is what makes this M-effort.
- **Blocked by**: none
- **Unblocks**: §2 #1 (shared `grok-safety-rules` package), §2 #11 (permissive-profile exemplar), §2 #17 (`grok-agent-orchestra` bootstrap + Lucas behavioural contract)
- **Suggested labels**: `spec`, `safety`, `ecosystem`, `phase-1b`

---

## Context

The Grok ecosystem advertises a **tripartite safety model** —
`strict` / `standard` / `permissive` — across three repos that each
use the vocabulary but none of which publishes a machine-readable
rubric:

- `grok-install/SECURITY.md` defines "Enhanced Safety & Verification
  2.0" (pre-install file scan, minimum-keys, halt-on-anomaly,
  "Verified by Grok" badge) but leaves the three profile names
  undefined.
- `grok-yaml-standards/standards-overview.md` categorises the 12
  standards by security **level** (Low / Medium / High / Critical) —
  a separate axis that speaks about *what the standard touches*,
  not *how strict a consuming agent must be*. The strict/standard/
  permissive triplet is referenced in prose only.
- `grok-install-cli/src/grok_install/safety/` implements *some*
  ruleset under these names; whether it is a re-implementation of
  the `grok-security` schema or a divergent ruleset is undocumented
  (tracked as UNV-4, S3, in `audits/98-risk-register.md`).

The observable consequence is that the three profile names have no
behavioural contract. Concretely:

1. **The `awesome-grok-agents` gallery ships 6 strict, 4 standard,
   and 0 permissive templates** (source: `featured-agents.json`
   v1.0). There is no reference template for the loosest profile,
   so new adopters cannot calibrate what `permissive` should look
   like in practice. §2 #11 (add a permissive exemplar) is blocked
   on this rec; the exemplar cannot be honest without a rubric to
   point at.
2. **At least three independent static-regex implementations of
   "safety rules" live in the ecosystem** —
   `grok-install-cli/safety/rules.py`,
   `grok-build-bridge/_patterns.py`, and
   `awesome-grok-agents/scripts/scan_template.py` — with no shared
   source module. §2 #1 (extract a shared `grok-safety-rules`
   package) is blocked on this rec; a shared package needs a
   shared behavioural contract before extraction is meaningful.
3. **`grok-agent-orchestra`'s README advertises a "Lucas safety
   veto"** whose relationship to the three profiles is undefined
   (UNV-3, S3). §2 #17 (bootstrap the orchestra with a behavioural
   definition of the Lucas veto) is blocked on this rec.

This issue asks `grok-yaml-standards` to publish the rubric as a
versioned artefact (`rubric-v1.md` + machine-readable companion),
then ships a conformance-test format that each of the four consumer
repos can run in CI to prove its claimed profile mapping matches
the rubric. The rubric is the contract; the conformance tests are
what give it teeth.

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch; paths stable).

**Where the vocabulary appears today**

| Repo | Artefact | What it says | What is missing |
|------|----------|--------------|-----------------|
| `grok-install` | `SECURITY.md` — "Enhanced Safety & Verification 2.0" | Defines the overall safety stance (pre-install scan, halt-on-anomaly, "Verified by Grok" badge). | No definition of the three profile names. |
| `grok-yaml-standards` | `standards-overview.md` | Categorises the 12 standards by security **level** (Low / Medium / High / Critical). | Level ≠ profile. No rubric for strict / standard / permissive. |
| `grok-yaml-standards` | `grok-security/` | Operational catalogue entry for the security standard. | Does not enumerate profile semantics. |
| `grok-install-cli` | `src/grok_install/safety/rules.py`, `scanner.py` | Implements *a* ruleset used by `grok-install scan`. | Not documented whether it re-implements `grok-security` or diverges (UNV-4). |
| `awesome-grok-agents` | `featured-agents.json` v1.0 | Declares one of `strict` / `standard` / `permissive` per template. | **6 strict / 4 standard / 0 permissive** — no permissive exemplar. |
| `grok-build-bridge` | `_patterns.py` + LLM audit in `xai_client.py` | Implements its own dual-layer safety scan. | Parallel re-implementation of "safety rules" vocabulary. |
| `grok-agent-orchestra` | README | Advertises "Lucas safety veto". | No source defines Lucas or its relationship to the three profiles (UNV-3). |

*Sources: `audits/00-ecosystem-overview.md §6.1`, `§6.2`, `§6.3`;
`audits/01-grok-install.md §6`; `audits/02-grok-yaml-standards.md
§6`; `audits/03-grok-install-cli.md §6, §10`; `audits/06-awesome-
grok-agents.md §6, §11 row 3`; `audits/09-grok-build-bridge.md §6`;
`audits/10-grok-agent-orchestra.md §10`.*

**Risk register** — `audits/98-risk-register.md`:

- **UNV-3** (S3, L-med, `needs-info`): "'Lucas safety veto'
  (advertised on `grok-agent-orchestra`): no source defines what
  Lucas is, what veto authority it carries, or how it interacts
  with the strict / standard / permissive profiles. Branding
  without a behavioural contract."
- **UNV-4** (S3, L-med, `needs-info`): "Whether `grok-install-cli`'s
  safety rules are a re-implementation of the `grok-yaml-standards/
  grok-security` schema or a divergent ruleset is not stated —
  risks two safety surfaces drifting apart unobserved."

**Why `grok-yaml-standards` is the right home for the rubric.**
The repo already owns `standards-overview.md` (the ecosystem's
most authoritative cross-standard table) and
`version-reconciliation.md` (which established the "12 standards"
count against competing 8- and 14-counts — audit 02 §4). Publishing
the safety-profile rubric alongside those artefacts keeps the
ecosystem's single-source-of-truth discipline intact. The four
consumer repos already import this repo's schemas; adding a rubric
file is additive.

## Acceptance criteria

Four parts. Each part is independently testable; the issue closes
when all four are merged into `grok-yaml-standards` and a release
(candidate: v1.3.0 or v1.2.1) is cut carrying them.

### Part A — Rubric contents (behavioural definitions, not prose)

Publish `docs/safety-profile-rubric-v1.md` in `grok-yaml-standards`
root. For each of the three profiles, the file MUST define **all
seven** axes below. Every axis takes a concrete value; "left to the
agent" is not a valid value.

| Axis | `strict` | `standard` | `permissive` |
|------|----------|------------|--------------|
| **External writes** — may the agent post, comment, open PRs, or commit? | Allowed only after explicit per-action approval (human-in-the-loop gate). | Allowed for in-scope actions declared in `grok-install.yaml`; gated for anything outside scope. | Allowed without per-action gating. |
| **Secret access** — may the agent read API tokens, credentials, `.env` content? | Read-only; never echoed to model output or logs. | Read-only; may be referenced in outputs by name, never by value. | Read+pass-through; still never echoed to logs. |
| **Code execution** — may the agent run arbitrary shell / eval? | Denied. | Allowed in sandbox (container / nsjail / equivalent); outputs audited. | Allowed on host; still bounded by OS user perms. |
| **Approval gate** — who signs off before a write lands? | Human. | Rule-based: a declared allowlist in `grok-install.yaml` is sufficient. | None required. |
| **Scan severity threshold** — what does the pre-install scanner block on? | Any `warning` or higher. | `error` or higher; warnings surface but do not block. | `error` only; warnings logged. |
| **Network egress** — may the agent reach arbitrary hosts? | Denylist + allowlist: default-deny, explicit allowlist in the agent's YAML. | Allowlist only, but declared at install time rather than per-action. | Open egress. |
| **Halt-on-anomaly** — what triggers an auto-halt? | Any scanner finding ≥ warning. | Any finding ≥ error. | Scanner findings logged; halt is operator-initiated. |

Notes on the table:

- [ ] Each cell is a normative claim. No "should" / "may" / "etc.";
      an axis value either holds or the agent is out of profile.
- [ ] The `permissive` row is **not** "anything goes" — it still
      has a concrete contract (open egress; logs are kept; operator
      can halt). This is what makes the permissive exemplar in §2
      #11 drafteable without hedging.
- [ ] Axes are deliberately independent so consumers can
      partial-check: e.g. `awesome-grok-agents/scan_template.py`
      cares about the scan-severity and external-writes rows;
      `grok-build-bridge` cares about the code-execution and
      network-egress rows. A consumer that only implements a
      subset states so explicitly; it is not "conformant" until
      all seven apply.
- [ ] The table carries a `rubric-v1` SemVer tag (MAJOR.MINOR).
      Adding a new axis is a MAJOR bump; rewording an axis value
      is MINOR; typo / clarification is PATCH. Consumers pin to a
      rubric-v1.x range the way they already pin to
      `grok-install` v2.x.
- [ ] The rubric explicitly cross-references `grok-install/
      SECURITY.md` (Enhanced Safety 2.0) so the two live
      consistently; whichever artefact disagrees with the other
      loses (rubric is canonical for the three profile
      *definitions*; SECURITY.md is canonical for the overall
      stance).

### Part B — Location in the repo (human-readable + machine-readable)

Both artefacts live at the repo root of `grok-yaml-standards` so
consumers can pin them without spelunking nested paths.

- [ ] `docs/safety-profile-rubric-v1.md` — the canonical
      human-readable rubric. Contains §Part-A's seven-axis table
      plus short per-axis prose and the cross-reference back to
      `grok-install/SECURITY.md`. MUST carry the `rubric-v1`
      SemVer tag in its H1 and a top-of-file `Last-updated:`
      ISO-8601 date.
- [ ] `schemas/safety-profile-rubric.schema.json` — the
      machine-readable companion. Draft-2020-12 (aligns with
      §2 #8's target draft for the v1.3 migration; if this rec
      lands before §2 #8, the schema still uses draft-2020-12
      and the `schema-smoke` CI job treats it as the one
      exception to the repo-wide draft-07 rule until #8 lands).
      The schema defines an object shape like:

      ```json
      {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/AgentMindCloud/grok-yaml-standards/schemas/safety-profile-rubric.schema.json",
        "title": "Grok safety-profile rubric v1",
        "type": "object",
        "required": ["rubric_version", "profiles"],
        "properties": {
          "rubric_version": {"type": "string", "pattern": "^1\\.\\d+(\\.\\d+)?$"},
          "profiles": {
            "type": "object",
            "required": ["strict", "standard", "permissive"],
            "additionalProperties": false,
            "properties": {
              "strict":     {"$ref": "#/$defs/profile"},
              "standard":   {"$ref": "#/$defs/profile"},
              "permissive": {"$ref": "#/$defs/profile"}
            }
          }
        },
        "$defs": {
          "profile": {
            "type": "object",
            "required": [
              "external_writes", "secret_access", "code_execution",
              "approval_gate", "scan_severity_threshold",
              "network_egress", "halt_on_anomaly"
            ],
            "additionalProperties": false,
            "properties": {
              "external_writes":          {"enum": ["per_action_approval", "scoped_allowlist", "open"]},
              "secret_access":            {"enum": ["read_never_echo", "read_reference_only", "read_passthrough"]},
              "code_execution":           {"enum": ["denied", "sandboxed", "host_bounded"]},
              "approval_gate":            {"enum": ["human", "rule_based", "none"]},
              "scan_severity_threshold":  {"enum": ["warning", "error", "error_log_only"]},
              "network_egress":           {"enum": ["default_deny_allowlist", "install_time_allowlist", "open"]},
              "halt_on_anomaly":          {"enum": ["on_warning", "on_error", "operator_only"]}
            }
          }
        }
      }
      ```

      The concrete filled-in `strict`/`standard`/`permissive`
      values from §Part-A's table are published alongside as
      `schemas/safety-profile-rubric-v1.values.json` — the
      canonical rubric instance that validates against the
      schema above.
- [ ] Both files are added to `CHANGELOG.md` under the release
      that ships them (v1.3.0 if co-released with §2 #8;
      v1.2.1 otherwise).
- [ ] `README.md` gains a one-line pointer under the existing
      "12 standards" callout: *"Safety-profile rubric: see
      `docs/safety-profile-rubric-v1.md`."*
- [ ] `standards-overview.md` gets a cross-link so readers
      arriving at the Low/Medium/High/Critical-level discussion
      can jump to the strict/standard/permissive-profile
      discussion (they are orthogonal axes; the overview should
      say so).

### Part C — Conformance-test format (the teeth)

The rubric without conformance tests is prose. Ship a published
conformance-test format so a consumer repo's CI can answer, on
every PR, "does this agent actually honour the profile it claims
in its `grok-install.yaml`?".

- [ ] Add `tests/conformance/` to `grok-yaml-standards`. Each
      conformance case is a directory with:

      ```
      tests/conformance/<case_id>/
        claim.yaml        # excerpt of grok-install.yaml under test
        expected.json     # {"conformant": true|false, "violations": [...]}
        rationale.md      # why this case is in the suite
      ```

      `claim.yaml` is a minimal `grok-install.yaml` fragment that
      declares a `safety_profile:` plus whatever fields the seven
      axes evaluate against (`permissions:`, `network:`, `scan:`,
      `approval:`, etc.). `expected.json` is the ground truth
      verdict. `rationale.md` gives one paragraph explaining
      which axis the case targets.

- [ ] Publish at least **7 positive cases** (one canonical pass
      for each of the seven axes) × 3 profiles = 21 passing cases,
      and at least **7 negative cases** per profile = 21 failing
      cases. Minimum suite: 42 cases. Additional cases encouraged
      for well-known edge conditions (e.g. an agent claiming
      `permissive` while declaring `external_writes:
      per_action_approval` — should flag as *over-conformant*,
      not non-conformant; define the behaviour explicitly).

- [ ] Ship a reference validator at
      `tools/check_profile_conformance.py` (Python 3.10+, depends
      only on `jsonschema>=4.21` and `PyYAML`). Interface:

      ```
      check_profile_conformance \
          --rubric schemas/safety-profile-rubric-v1.values.json \
          --claim path/to/grok-install.yaml

      # Exit codes:
      #   0 — conformant
      #   1 — non-conformant (prints violation list)
      #   2 — over-conformant (prints which axes are stricter than claimed profile)
      #   3 — schema error (claim is malformed)
      ```

- [ ] Wire the reference validator into
      `.github/workflows/validate-schemas.yml` as a new
      `conformance` job: iterate over `tests/conformance/*` and
      compare `check_profile_conformance` output against
      `expected.json`. Matrix over the three profiles. Failing
      the matrix fails CI.

- [ ] Document the format in
      `docs/safety-profile-rubric-v1.md §Conformance tests` so
      consumers can author their own cases. Include an
      "authoring a new case" checklist (5 steps) and a note on
      how to interpret exit code 2 (over-conformance is not a
      bug — it means the agent is stricter than its stated
      profile; consumers may either downgrade the profile
      claim or accept the stricter behaviour).

- [ ] Add a CONTRIBUTING note that every new standard added to
      `grok-yaml-standards` (future additions via
      `discussion/new-standard` per `version-reconciliation.md`)
      must include at least one conformance case per profile
      that exercises the new standard's safety surface. Keeps
      the suite growing in lockstep with the catalogue.

### Part D — Consumer contract (how downstream repos adopt)

Four consumer repos are named in the `Affected repos` column of
§2 #5. Each adopts the rubric differently; the acceptance criteria
below name what "adopted" means per consumer. These checkboxes do
**not** need to merge in `grok-yaml-standards` for this issue to
close; they are the contract language this issue publishes so
consumer-repo maintainers know what to do once the rubric lands.
Linked follow-up issues in each consumer repo ticked these off.

- [ ] **`grok-install-cli`** — `src/grok_install/safety/rules.py`
      + `scanner.py` adopt the rubric as a loaded artefact
      (`safety-profile-rubric-v1.values.json`) rather than
      hard-coding profile semantics. `grok-install scan` gains a
      `--conformance-check` flag that runs
      `check_profile_conformance` against the target agent's
      `grok-install.yaml`. Closes UNV-4 (the cause of UNV-4 is
      *undocumented divergence*; making the CLI consume the
      published rubric resolves the ambiguity by construction).
      Dependency: §2 #1 (shared `grok-safety-rules` package)
      becomes a natural extraction once this adoption lands in
      both `grok-install-cli` and `grok-build-bridge`.

- [ ] **`awesome-grok-agents`** — CI's
      `validate_template.py` / `scan_template.py` adopt the
      reference validator. Each of the 10 gallery templates'
      `grok-install.yaml` is checked against the profile it
      declares in `featured-agents.json`. **This also unblocks
      §2 #11** (add a permissive exemplar): a new template
      declaring `safety_profile: permissive` can now be
      honestly checked against Part-A's `permissive` row.

- [ ] **`grok-build-bridge`** — `_patterns.py` adopts
      `safety-profile-rubric-v1.values.json` as the source of
      truth for the "severity threshold" and "external writes"
      axes. The LLM-audit layer in `xai_client.py` uses the
      rubric as part of its system prompt context (the LLM
      auditor is told which profile the agent claims, so it
      can flag behaviour inconsistent with that profile).

- [ ] **`grok-agent-orchestra`** — README's "Lucas safety
      veto" gains a behavioural contract defined *in terms of*
      the rubric: Lucas's veto is triggered when a proposed
      multi-agent action would violate the *strictest* profile
      claimed by any agent in the team. Closes UNV-3 partially;
      §2 #17 (orchestra bootstrap) closes the rest once an
      implementation ships.

- [ ] **Follow-up linkage**: once this primary issue lands,
      open four short follow-up issues (one per consumer) that
      cite this issue's URL as the rubric source and carry the
      consumer-specific checklist above. Do NOT open the
      follow-ups before this primary merges — the rubric's
      normative values may shift during review.
