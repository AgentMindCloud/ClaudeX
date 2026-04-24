# Bootstrap grok-agent-orchestra with a working multi-agent pattern + a behavioural Lucas safety veto

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #17 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/grok-agent-orchestra
- **Risks closed**: partial GOV-3 (S3) — from `audits/98-risk-register.md`. Full GOV-3 closure also requires the sibling §2 #16 bootstrap (`vscode-grok-yaml`) + §2 #15 landing the honesty-fix on both shell repos. Also closes UNV-3 (S3) — Lucas safety veto becomes behaviourally defined once this rec lands.
- **Source audits**: `[→ 10 §9 row 2]`. Supporting: `audits/10-grok-agent-orchestra.md §1, §2, §10` (LICENSE-only repo + advertised-but-undefined "Lucas" veto), `audits/10 §9 rows 4, 5` (the Lucas definition + shared safety-layer recs this draft absorbs).
- **Effort (§2)**: L — bootstrap of a shell repo means source + CI + docs + tests + release from zero. The multi-agent pattern itself is the biggest chunk.
- **Blocked by (§2)**: #5 — Lucas's veto semantics can only be defined in terms of the published safety-profile rubric; without the rubric, "Lucas" is branding without a contract (UNV-3).

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md); not yet filed upstream; speculative. Also depends on [`phase-1b/drafts/01-shared-grok-safety-rules-package.md`](01-shared-grok-safety-rules-package.md) as a day-one dependency — that draft is itself speculative on #5, so this is two layers of speculation.
- **Re-review trigger**: rewrite this draft if either prerequisite is substantively rewritten during upstream review. Specifically: (a) §2 #5's seven-axis rubric shape drives the Lucas veto's normative definition in Part B; if axes are added/removed, the veto rule changes. (b) §2 #1's package API drives the orchestra's imports in Part A; if the package lands under a different name or with a different API, Part A's imports need updating. If §2 #1 is NOT filed or merged before this draft is filed, fall back to pinning `grok-install-cli`'s `safety/` module directly with a "TODO: migrate to grok-safety-rules once shipped" comment in Part A — marginal cost, easy to clean up.

- **Suggested labels**: `bootstrap`, `v0.1.0`, `multi-agent`, `lucas-veto`, `phase-1b`

---

## Context

`grok-agent-orchestra` is the multi-agent framework the
ecosystem advertises — README describes "5 patterns" and a
"Lucas safety veto". The repo today contains **only LICENSE**:
1 commit total, no README (the description lives on the GitHub
repo landing page), no source, no CI, no issues template. Like
`vscode-grok-yaml`, it is a shell. Unlike `vscode-grok-yaml`,
its advertised feature set is materially more ambitious — a
multi-agent orchestrator with a named safety veto is not a
one-afternoon extension; it is a framework.

Two concrete problems fall out:

1. **The repo's marketing outruns reality.** §2 #15b (already
   drafted + in repo) downgrades the description. This rec
   closes the other half: ship a real v0.1.0 with *one* working
   multi-agent pattern so "multi-agent framework" is a true
   statement.

2. **Lucas has no source.** The "Lucas safety veto" is named on
   the repo landing page but defined nowhere. UNV-3 in the risk
   register. Without a behavioural contract, Lucas is branding.
   This rec defines Lucas in terms of §2 #5's rubric — a named
   function that vetoes multi-agent actions violating the
   *strictest* safety profile claimed by any agent in the team.

The goal for v0.1.0 is **one pattern, done well**, not five
patterns half-done. Candidate: a **plan-execute-critique** loop
— three agents (planner, executor, critic) collaborating on a
single user task, with Lucas checking each proposed action
against the rubric before execution. This is the smallest
pattern that actually exercises multi-agent coordination +
safety-veto integration; the other four patterns the repo
advertised (per README) can layer on top in later releases.

Secondary constraint: the bootstrap must adopt §2 #1's shared
`grok-safety-rules` from day one. The orchestra is the one
repo where "day one" is still ahead of us; adopting the shared
package here avoids adding a fourth parallel safety
implementation that §2 #1 would then immediately retire.

## Evidence

From `main` snapshot on 2026-04-23 (WebFetch; paths stable).

**Current repo state** —
`audits/10-grok-agent-orchestra.md §1, §2, §11 row 1`:
- Repo contents: `LICENSE` only (Apache 2.0).
- **1 commit total**; 1★, 0 forks, 0 issues, 0 PRs.
- Landing page advertises: multi-agent framework, 5 patterns,
  "Lucas safety veto".
- No README file visible in the repo tree (description lives
  on the GitHub repo-landing page).
- No source, no `pyproject.toml` / `package.json`, no CI
  workflows.

**What the ecosystem already has** (so bootstrap does not need
to reinvent):
- `grok-install-cli` (Typer-based CLI with `safety/` layer) —
  `audits/03 §2`.
- `grok-build-bridge` (LLM audit + static scan; mature CI
  template §2 #18 is promoting) — `audits/09 §5`.
- `grok-yaml-standards` (the schema catalogue this orchestra's
  agents will emit) — `audits/02 §2`.
- `awesome-grok-agents` (gallery of 10 template agents the
  orchestra will orchestrate) — `audits/06 §2`.

**Risk register** — `audits/98-risk-register.md`:
- **GOV-3** (S3, L-high, `open`): "`vscode-grok-yaml` and
  `grok-agent-orchestra` are LICENSE+README only — no source,
  no CI, no issues template. The marketing-polished surface
  implies a working product that does not exist." *(This rec
  closes half; §2 #16 closes the other half for vscode-grok-yaml.)*
- **UNV-3** (S3, L-med, `needs-info`): "'Lucas safety veto'
  (advertised on `grok-agent-orchestra`): no source defines
  what Lucas is, what veto authority it carries, or how it
  interacts with the strict / standard / permissive profiles.
  Branding without a behavioural contract." *(This rec closes
  UNV-3 outright by defining Lucas.)*

**Audit recs that this rec absorbs** —
`audits/10-grok-agent-orchestra.md §9`:
- **Row 2** (direct source for §2 #17): "Ship a v0.1.0 with one
  working multi-agent pattern + a behavioural Lucas definition."
- **Row 3**: "Adopt `grok-build-bridge`'s CI template from day
  one." Absorbed into Part A below.
- **Row 4**: "Document 'Lucas safety veto' concretely." Absorbed
  into Part B — Lucas's behavioural contract.
- **Row 5**: "Share safety-layer code with `grok-install-cli`
  and `grok-build-bridge` from the start." Absorbed into Part A
  as the day-one dependency on `grok-safety-rules` (§2 #1).

**Prerequisite state**:
- §2 #5 draft: [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md).
- §2 #1 draft: [`phase-1b/drafts/01-shared-grok-safety-rules-package.md`](01-shared-grok-safety-rules-package.md).
- §2 #15b draft: [`phase-1b/drafts/15b-grok-agent-orchestra-description.md`](15b-grok-agent-orchestra-description.md) — landing description
  honesty for this repo; this rec's Part A assumes that landed.

**Related §2 cross-refs**:
- §2 #15b (honest landing description — first-pass draft).
- §2 #5 (rubric — prerequisite).
- §2 #1 (shared safety-rules package — prerequisite for clean
  adoption; fall-back if #1 not yet merged is flagged in
  metadata header).
- §2 #18 (CI template — adopted from day one per audit 10 §9 row 3).

## Acceptance criteria

Two parts. Part A ships v0.1.0 with one real multi-agent pattern
plus the supporting repo scaffolding. Part B defines Lucas
behaviourally and wires it into the pattern. The issue closes
when v0.1.0 is published to PyPI, the sample pattern runs
end-to-end on a test fixture, and Lucas's veto can be
demonstrated both triggering (on violating input) and not
triggering (on conformant input).

### Part A — Ship v0.1.0 with one working multi-agent pattern

- [ ] **Package scaffolding**: create `src/grok_agent_orchestra/`
      with `pyproject.toml` at repo root:
      - `name = "grok-agent-orchestra"`, `version = "0.1.0"`.
      - Python ≥ 3.10 (matches `grok-install-cli`).
      - Exact-pinned runtime deps: `grok-safety-rules == 0.1.0`
        (from §2 #1), `PyYAML == 6.x`, `typer == <matched-to-CLI>`,
        `pydantic == 2.x`, `httpx == <pinned>` (Grok API client
        — or depend on §2 #2's shared client if that has
        shipped; flag in §Notes).
      - Dev deps + coverage floor matching §2 #18's CI template
        (`ruff`, `mypy` strict, `pytest --cov-fail-under=85`).

- [ ] **Canonical pattern: `plan_execute_critique`** — three
      agents collaborating on one user task.

      ```
      grok_agent_orchestra/
        __init__.py
        patterns/
          __init__.py
          plan_execute_critique.py      # the one shipped pattern
        agents/
          __init__.py
          base.py                        # shared Agent protocol
          planner.py                     # produces a step list
          executor.py                    # executes steps via tool calls
          critic.py                      # scores execution against plan
        safety/
          __init__.py
          lucas.py                       # the veto — see Part B
        orchestrator.py                  # wires the three agents + Lucas
        cli.py                           # `orchestra run <task>` entry
      ```

- [ ] **Agent protocol** (`agents/base.py`): dataclass
      `AgentDecl` with `name`, `role`, `safety_profile: SafetyProfile`
      (imported from `grok_safety_rules`), and an `async act()`
      method. Three profile claims (one per agent) drive
      Lucas's veto semantics (see Part B).

- [ ] **Orchestrator** (`orchestrator.py`): initialises the
      three agents from a user-supplied YAML manifest (one of
      `awesome-grok-agents`' templates, or a custom file),
      invokes the pattern, routes every proposed action
      through Lucas, records the result to a structured log.
      Failure modes: Lucas vetoes ⇒ orchestrator halts with a
      non-zero exit code + a human-readable reason. Agent
      errors ⇒ retry budget (configurable) then halt.

- [ ] **CLI** (`cli.py`, Typer): `orchestra run <manifest.yaml>
      [--dry-run] [--verbose]`. Dry-run mode runs planner +
      critic but not executor — useful for CI smoke tests.

- [ ] **Sample fixtures**: `examples/`:
      - `examples/ci-review/manifest.yaml` — three agents
        (planner, executor, critic), `safety_profile: standard`,
        task "review this diff and summarise findings".
      - `examples/ci-review/expected_output.json` — the
        expected critic score shape, for
        regression/smoke tests.

- [ ] **Adopt §2 #18's CI template** from day one:
      `.github/workflows/ci.yml` with lint + matrix test +
      mypy strict + Draft-2020 schema validation (for the
      orchestra's own `schema/` if it ships any) + safety-scan
      + build. Audit 10 §9 row 3 requires this; adopting it
      at bootstrap is cheaper than retrofitting.

- [ ] **Governance files** (close part of GOV-4 for this repo
      while we're here): `README.md` (rewrite from §2 #15b's
      honest description; expand with "what v0.1.0 does" +
      "roadmap to multi-pattern v1.0"), `CHANGELOG.md` (seed
      with v0.1.0 section), `CONTRIBUTING.md` (how to run
      tests, pattern-authoring guide), `SECURITY.md` (points
      at `grok-install/SECURITY.md`), `.github/CODEOWNERS`
      (bootstrap maintainer; §2 #20's pattern).

- [ ] **Publish v0.1.0 to PyPI** via Trusted Publisher (same
      pattern §2 #7 Part A establishes for `grok-install-cli`).

- [ ] **README roadmap section** — explicit: "v0.1.0 ships
      *one* pattern (plan-execute-critique). v0.2.0 adds
      <N2-pattern>; v0.3.0 adds <N3-pattern>; …". Do NOT
      promise five patterns up front. The original landing
      page's "5 patterns" number is marketing, not an
      engineering commitment.

### Part B — Lucas safety veto: behavioural contract

Define Lucas concretely, implement it, and demonstrate it in
CI. The definition is in terms of §2 #5's rubric — a scope the
rubric was built for.

- [ ] **Normative definition** (publish in `docs/LUCAS.md` and
      `README.md` §Safety):

      > **Lucas** is the orchestra's safety veto. For each
      > proposed action an agent wants to execute, Lucas:
      > 1. Collects the `safety_profile` claims of every agent
      >    currently active in the team.
      > 2. Takes the **strictest** of those profiles (in the
      >    ordering `strict > standard > permissive`).
      > 3. Runs the proposed action through
      >    `grok_safety_rules.check_profile_conformance` against
      >    that strictest profile.
      > 4. Vetoes the action (returns `VETO`, orchestrator
      >    halts) if the action would violate the strictest
      >    profile on any axis of §2 #5's seven-axis rubric.
      > 5. Records the veto outcome (veto reason, strictest
      >    profile, axis violated) to the structured log.
      >
      > Lucas is a *team-level* veto: the veto applies even if
      > the agent proposing the action claims a looser profile
      > than a teammate. This is the design choice that makes
      > multi-agent orchestration safe — a permissive
      > scratchpad agent cannot launder an action past the
      > strict executor via the critic.

- [ ] **Implementation** (`safety/lucas.py`):

      ```python
      from grok_safety_rules import (
          SafetyProfile, check_profile_conformance, load_rubric_values,
      )

      PROFILE_ORDER = [
          SafetyProfile.STRICT, SafetyProfile.STANDARD, SafetyProfile.PERMISSIVE,
      ]

      def strictest(profiles: list[SafetyProfile]) -> SafetyProfile:
          for p in PROFILE_ORDER:
              if p in profiles:
                  return p
          raise ValueError("empty team")

      def lucas_veto(
          team_profiles: list[SafetyProfile],
          proposed_action_yaml: str,
          rubric_values,
      ) -> LucasVerdict:
          target = strictest(team_profiles)
          verdict = check_profile_conformance(
              proposed_action_yaml, target, rubric_values,
          )
          return LucasVerdict(
              veto = (verdict.exit_code in (1, 3)),  # non-conformant or schema error
              target_profile = target,
              underlying = verdict,
          )
      ```

- [ ] **Veto demonstration in CI**: two fixtures in
      `tests/fixtures/lucas/`:
      - `no_veto/` — a team of three `standard` agents
        proposing a conformant action. Lucas returns
        `veto=False`. Orchestrator runs to completion.
      - `veto/` — a team of one `strict` + two `permissive`
        agents where the permissive agent proposes an
        `external_writes: open` action. Lucas sees strictest
        = `strict`, the action violates `strict.external_writes`,
        returns `veto=True`. Orchestrator halts with exit
        code 2 + reason string.

      Both fixtures run in `pytest` in the `test` CI job.

- [ ] **Veto override is NOT a v0.1.0 feature.** A later
      version may add an operator-override (with audit log),
      but v0.1.0 treats Lucas as fail-closed. Document this
      explicitly in `LUCAS.md §Override`.

- [ ] **Interaction with `grok-build-bridge`'s LLM audit**:
      Lucas is *static* (rubric-based). `grok-build-bridge`'s
      LLM audit layer is *dynamic* (model-based). They are
      complementary: Lucas catches static rubric violations
      deterministically; the LLM audit catches semantic issues
      Lucas cannot see. Document this in `LUCAS.md §Scope`.
      The orchestra does not ship its own LLM audit in v0.1.0;
      that layer lives in the bridge and is optionally
      consumed.

- [ ] **Lucas release coupling to §2 #5**: since Lucas's
      definition references §2 #5's rubric axes verbatim, the
      `LUCAS.md` document cites the rubric's version pin
      (`rubric-v1`). If the rubric bumps to `rubric-v2`
      (MAJOR), Lucas's implementation needs to re-audit the
      axis-mapping and may need to bump its own major
      version. Encode this relationship in the README.

## Notes

- **Why "strictest profile in team" over "proposing agent's
  profile".** If Lucas only checked the proposing agent's
  claimed profile, an attacker could construct a permissive
  scratchpad agent to launder actions past strict teammates.
  Team-level strictness is the conservative choice. Willing
  to revisit after one pattern ships and we have real-world
  experience; encoded as a design decision in `LUCAS.md`.

- **Why plan-execute-critique and not one of the other four
  patterns.** P-E-C is the smallest pattern that actually
  exercises multi-agent coordination (three roles, one
  control loop, one decision point). Single-agent patterns
  don't demonstrate the safety-veto value proposition;
  bigger patterns multiply implementation cost without
  increasing learning. Ship this one; measure; pick the next
  pattern based on what v0.1.0 users actually ask for.

- **Fall-back if §2 #1 hasn't shipped at filing time.** The
  speculative-draft metadata header spells this out: pin
  `grok-install-cli`'s `safety/` module directly, leave a
  `TODO: migrate to grok-safety-rules` comment in `lucas.py`,
  update the import + pin once §2 #1 ships v0.1.0. Cost of
  this migration is under an hour.

- **Fall-back if §2 #5 hasn't shipped at filing time.** The
  rubric is the prerequisite; without it, Lucas's normative
  contract cites undefined-behaviour terms. Do NOT file this
  rec upstream until §2 #5 has merged. (Unlike §2 #1 — whose
  fall-back is trivial — there is no sensible fall-back for
  #5; without the rubric, "the strictest profile" has no
  meaning beyond English prose.)

- **Interaction with §2 #2 (shared Grok API client).** §2 #2
  is in the next-pass candidates (not drafted yet).
  If #2 lands before this rec, the orchestra depends on the
  shared client. If not, the orchestra ships with its own
  thin httpx-based client (audit 00 §9.A names the orchestra
  as one of the four parallel clients this ecosystem has;
  adding a fifth is not worse than the status quo, and
  migration to a shared client is one PR). Flag in the README.

- **Out of scope for v0.1.0.**
  - The remaining four patterns from the landing page
    (names TBD; original list is marketing). Promise none;
    ship one.
  - Vector/episodic memory substrate (ROADMAP Phase 2; not
    this rec).
  - Multimodal (vision/voice) integration (ROADMAP Phase 4;
    not this rec).
  - An operator-override for Lucas vetoes (explicit: v0.2.0
    or later, with full audit trail).
  - Hosting / deployment recipes (the orchestra is a library,
    not a service).

- **Filing strategy.** Single primary issue in
  `grok-agent-orchestra`. File only after BOTH §2 #5 has
  merged upstream AND §2 #1 has merged (or §2 #1's fall-back
  is explicitly chosen). #15b should also land first so the
  repo's marketing matches the bootstrap ambition.

- **Speculative-draft honesty.** This draft has two prerequisite
  drafts in repo (§5 and §1), neither filed upstream. Part A's
  package imports and Part B's veto implementation both
  reference §1's package API. Part B's Lucas definition
  references §5's rubric axes. The re-review trigger in the
  metadata header explicitly lists both as rewrite conditions.

- **Closes UNV-3 + partial GOV-3.** UNV-3 closes outright
  (Lucas has a behavioural contract). GOV-3 closes partially
  — full GOV-3 closure requires §2 #16 (vscode-grok-yaml
  bootstrap) and §2 #15 (description honesty on both shell
  repos); all three together.

