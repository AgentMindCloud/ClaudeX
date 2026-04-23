# Extract a shared grok-safety-rules package consumed by every safety-aware repo

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #1 (`audits/99-recommendations.md`)
- **Target repo (primary)**: AgentMindCloud/grok-install-cli *(primary — owns the most mature safety-rules implementation today; extraction happens here first)*. Alternative primary: a new `AgentMindCloud/grok-safety-rules` repo if the team prefers a separate home. The draft body below is written for the "extract from `grok-install-cli`" path and flags the new-repo alternative in §Notes.
- **Consumer repos (adoption follow-ups)**: AgentMindCloud/grok-build-bridge, AgentMindCloud/grok-agents-marketplace *(via the CI layer)*, AgentMindCloud/grok-agent-orchestra *(via §2 #17)*, AgentMindCloud/awesome-grok-agents *(via §2 #12's stub removal — already covered)*.
- **Filing strategy**: coordination issue in `grok-install-cli` describing extraction + release + consumer adoption. Consumer-repo adoption follow-ups open **only after** this primary merges AND the first release of the extracted package ships.
- **Risks closed**: UNV-4 (S3) outright *(the "three parallel implementations drift silently" underlying cause is resolved by the extraction)*; partial SEC-1 (S1) *(the bridge's LLM-audit prompt-injection fragility is unchanged; the static-scan layer that feeds it becomes shared + auditable, reducing the surface the LLM has to work around)*. From `audits/98-risk-register.md`.
- **Source audits**: `[→ 09 §9 row 4]`, `[→ 03 §9 row 3]`, `[→ 10 §9 row 5]`, `[→ 06 §9 row 2]`. Cross-cut evidence in `audits/00-ecosystem-overview.md §6.3` (three parallel implementations enumerated) + `§9.B` if present.
- **Effort (§2)**: L — extraction + packaging + three consumer-repo PRs + coordinated release. The rubric from §2 #5 gives the shared contract; this rec ships the shared *code* that implements it.
- **Blocked by (§2)**: #5 — the shared package needs the rubric as its behavioural contract. Without it, the extraction locks in three-way drift behind a single import name.

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md); not yet filed upstream; speculative.
- **Re-review trigger**: rewrite this draft if §2 #5's normative seven-axis rubric table is substantively changed during upstream review (e.g. axes added/removed, profile names changed). This draft's package API enumerates the seven axes; if the rubric's axis count shifts, the API shape shifts with it.

- **Suggested labels**: `extraction`, `shared-library`, `safety`, `ecosystem`, `phase-1b`

---

## Context

Three repos in the Grok ecosystem independently implement
"safety rules" — a pattern-based scanner that reads a
`grok-install.yaml` agent definition and flags hardcoded secrets,
over-broad permissions, unsafe external-write patterns, and the
other surface the Enhanced Safety & Verification 2.0 model calls
out:

- `grok-install-cli/src/grok_install/safety/rules.py` +
  `scanner.py` — the CLI's `grok-install scan` subcommand
  backend. Most mature implementation; sibling of
  `core/`, `deploy/`, `integrations/`, `runtime/`.
- `grok-build-bridge/_patterns.py` — static regex layer,
  one half of the bridge's "dual-layer safety" (the other
  half is the LLM audit in `xai_client.py`).
- `awesome-grok-agents/scripts/scan_template.py` — the
  gallery's CI-time scanner. §2 #12 (covered in an earlier
  Session-2 draft in this pass) removes this one by routing
  through the real CLI instead.

`grok-agent-orchestra` also plans to implement a safety layer
once bootstrapped (§2 #17); without this extraction, the
orchestra would make it *four* parallel implementations — a
degradation `audits/10-grok-agent-orchestra.md §9 row 5`
explicitly calls out as a failure mode to pre-empt.

The drift risk is concrete. Today, the three implementations are
"probably close" to each other — no one has systematically
diffed them. As the ecosystem evolves, each implementation drifts
against whichever axis its own repo cares about most (the CLI
cares about install-time scanning; the bridge cares about LLM
audit context; the gallery cares about CI speed). Nothing in the
ecosystem's current process flags the divergence.

The fix is extraction: one package, one source module, three (or
four) consumers. §2 #5 provides the behavioural contract (the
rubric's seven normative axes); this rec ships the code that
implements that contract. After both land:

- The rubric defines *what* a profile means.
- The shared package is *how* it's enforced.
- Consumers call into the package rather than re-implementing.

That's the only configuration in which UNV-4 ("safety surfaces
drifting apart unobserved") closes structurally rather than
situationally.

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch; paths stable).

**Implementation #1 — `grok-install-cli`** —
`audits/03-grok-install-cli.md §2, §11 row 4`:
- Module: `src/grok_install/safety/` with `__init__.py`,
  `rules.py`, `scanner.py`.
- Called via `grok-install scan` subcommand.
- Mature (used by the CLI's own CI via `security.yml`).

**Implementation #2 — `grok-build-bridge`** —
`audits/09-grok-build-bridge.md §1, §6, §11 row 3`:
- Module: `grok_build_bridge/_patterns.py` (static regex layer).
- Paired with LLM audit in `xai_client.py` (the "dual-layer
  safety" model).
- Audit 09 §9 row 4 is the source of the "share with
  `grok-install-cli/src/grok_install/safety/rules.py` via a
  small `grok-safety-rules` package or git-submodule"
  recommendation — **the headline source of this §2 #1**.

**Implementation #3 — `awesome-grok-agents`** —
`audits/06-awesome-grok-agents.md §5, §7`:
- Script: `scripts/scan_template.py` (plus the
  `grok_install_stub/` package that §2 #12 removes).
- Fails on warnings in CI — the strictest signal in the
  ecosystem.

**Intended fourth consumer — `grok-agent-orchestra`** —
`audits/10-grok-agent-orchestra.md §9 row 5`:
- "Share safety-layer code with `grok-install-cli` and
  `grok-build-bridge` from the start — don't re-implement.
  Three ecosystem repos independently reimplementing safety
  rules would produce the worst kind of drift. Pre-adopt a
  shared `grok-safety-rules` package (see `grok-build-bridge`
  audit rec #4)." *(Verbatim.)*

**Cross-cut summary** —
`audits/00-ecosystem-overview.md §6.3`:
- "At least three independent static-regex / pattern
  implementations exist: `grok-install-cli/safety/rules.py`,
  `grok-build-bridge/_patterns.py`,
  `awesome-grok-agents/scripts/scan_template.py`. None share a
  source module." *(Verbatim.)*

**Risk register** — `audits/98-risk-register.md`:
- **UNV-4** (S3, L-med, `needs-info`): drift between the
  safety surfaces. Closed structurally by this extraction.
- **SEC-1** (S1, L-med, `open`): "LLM-audit safety layer in
  `build-bridge` accepts untrusted YAML and feeds it to a
  model — prompt-injection can subvert or bypass the audit
  verdict. No prompt-isolation or output-shape validation
  documented." This extraction partially addresses SEC-1:
  the *static* scan layer that feeds the LLM becomes
  auditable and rubric-disciplined. Does not replace the
  prompt-isolation / output-shape work that closes SEC-1
  fully (that is orthogonal to this rec).

**Prerequisite state**:
- §2 #5 draft: [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md)
  — seven-axis normative rubric + machine-readable companion
  schema + conformance-test format + consumer-repo contract
  layer. Not filed upstream at this writing.

**Related §2 cross-refs**:
- §2 #5 — the contract. See prerequisite above.
- §2 #12 — removes one of the three parallel implementations
  independently of this rec. Complements; does not block or
  unblock.
- §2 #17 — `grok-agent-orchestra` bootstrap. Should adopt this
  package from day one rather than adding a fourth
  implementation.
- §2 #11 — the permissive exemplar template. Consumes this
  package via the CLI's `scan` subcommand; no additional
  work required in this rec.

## Acceptance criteria

Two parts. Part A is the extraction + package shape + ownership
decisions. Part B is the consumer-adoption sequencing. The
issue closes when the package v0.1.0 ships to PyPI and at least
two consumer repos (primary targets: CLI + bridge) have
adopted it on `main`.

### Part A — Package shape + ownership

- [ ] **Pick the package home.** Two honest options:

      **A1 — Extract from `grok-install-cli` into a new
      top-level package in the same repo** (e.g.
      `src/grok_safety_rules/`), publish alongside
      `grok-install` on PyPI as a separate distribution
      (`grok-safety-rules`). CLI imports it as a library
      dependency.

      **A2 — Create a new dedicated repo**
      `AgentMindCloud/grok-safety-rules`. Extract the module,
      move it there, publish from there. CLI, bridge, etc.
      depend on it.

      Default recommendation: **A2**. The library's consumers
      span repos; a separate repo makes the ownership boundary
      explicit and prevents CLI-development cadence from
      leaking into shared-library cadence. A1 is cheaper
      short-term but creates circular governance between
      "this is a CLI change" and "this is a shared-rules
      change".

- [ ] **Package API** — module surface. One primary entry
      point plus strict data classes. Indicative signature
      (concrete implementation ships in Part A's PR):

      ```python
      from grok_safety_rules import (
          SafetyProfile,        # Enum: STRICT | STANDARD | PERMISSIVE
          RubricAxis,           # Enum: EXTERNAL_WRITES | SECRET_ACCESS | ...
          Finding,              # Dataclass: axis, severity, snippet, line
          ScanResult,           # Dataclass: findings, profile, conformant: bool
          scan,                 # (yaml_text: str, profile: SafetyProfile) -> ScanResult
          check_profile_conformance,  # (yaml_text, profile, rubric_values) -> ConformanceVerdict
          load_rubric_values,   # (path or URL) -> RubricValues
      )
      ```

      The seven `RubricAxis` members match §2 #5 Part A's seven
      normative axes verbatim. If §5's axis set changes during
      upstream review, this enum changes with it (re-review
      trigger — see metadata header).

- [ ] **Pin library deps.** The package depends only on
      Python stdlib + `PyYAML` + `jsonschema>=4.21`. No
      direct `grok-install-cli` dependency; the dependency
      flows the other direction (CLI depends on this package).
      Pin PyYAML and jsonschema at exact versions in
      `pyproject.toml` (matches `grok-yaml-standards`
      discipline).

- [ ] **Ship v0.1.0 to PyPI** via Trusted Publisher config
      (same pattern §2 #7 Part A establishes for
      `grok-install-cli`). Tag `v0.1.0`. Publish GitHub
      release with generated notes.

- [ ] **License**: Apache-2.0 to match the ecosystem's
      post-v1.2.0 relicensing.

- [ ] **Repo governance** (if A2): seed the new repo with
      `README.md`, `LICENSE`, `CHANGELOG.md`, `SECURITY.md`
      (points at `grok-install/SECURITY.md §Enhanced Safety
      2.0`), `CONTRIBUTING.md`, `.github/CODEOWNERS`,
      `.github/workflows/ci.yml` (adopt §2 #18's CI template
      from day one per the pattern §2 #17 uses for orchestra
      bootstrap).

- [ ] **Test discipline** — the package ships with conformance
      tests derived from §2 #5's `tests/conformance/` suite.
      `pytest --cov-fail-under=85` (matches
      `grok-build-bridge` discipline and §2 #18's template).

- [ ] **Maintainer roster**: name at least two maintainers in
      `CODEOWNERS`. If only one is available today, document
      "seeking second maintainer" in README. Single-maintainer
      shared libraries are a governance smell; make it visible
      so it gets addressed.
