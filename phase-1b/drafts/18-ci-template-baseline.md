# Promote grok-build-bridge's CI workflow as the ecosystem baseline CI template

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #18 (`audits/99-recommendations.md`)
- **Primary target (extraction)**: AgentMindCloud/grok-build-bridge — owns the
  workflow being promoted; file the coordination issue here.
- **Adopter repos (7)**: AgentMindCloud/grok-install, grok-yaml-standards,
  grok-install-cli, grok-install-action, grok-docs, awesome-grok-agents,
  grok-agents-marketplace. Each gets a checkbox in the acceptance criteria;
  the user may optionally file linked per-adopter issues after this
  coordination issue lands.
- **Risks closed**: indirectly SEC-2 (S2) across adopters (propagates the
  §2 #13 blocking `pip-audit` posture once #13 lands); supports SUP-1
  (S2) closure (propagates the §2 #3 SHA-pin posture). Also propagates
  the ecosystem's strongest test-discipline baseline (`--cov-fail-under=85`,
  `mypy strict`, OS × Python matrix, Draft-2020-12 schema validation).
- **Source audits (per §2)**: `[→ 09 §9 row 5]`, `[→ 10 §9 row 3]`. Note:
  `[→ 09 §9 row 5]` as written in §2 points to audit 09's "Publish
  Codecov badges" row, which does **not** describe the template-promotion
  idea. The substantive evidence for this rec is in audit 09 §1 (headline
  "CI is the strongest in the ecosystem") and §5 (the 6-job breakdown).
  The audit 10 §9 row 3 citation is correct and describes the adoption
  side ("Adopt grok-build-bridge's CI template … from day one").
- **Effort (§2)**: M — the extraction itself is small; the coordination
  across 7 adopter repos is what makes this M-effort.
- **Blocked by**: none
- **Cross-refs**: §2 #3 (SHA-pin actions; the template inherits this
  once #3 lands), §2 #13 (blocking `pip-audit` + secret-scan; the
  template inherits this once #13 lands). Sequencing: #3 and #13
  should ideally land **before** the template is frozen, so adopters
  inherit the corrected posture in one cut.
- **Suggested labels**: `ci`, `ecosystem`, `supply-chain`, `test-coverage`, `phase-1b`

---

## Context

`grok-build-bridge/.github/workflows/ci.yml` has the strongest CI
posture in the Grok ecosystem today. Every other CI-enabled repo
trails it in one or more of:

- **Test-coverage floor** — `grok-build-bridge` gates with
  `pytest --cov-fail-under=85`. No other repo in the ecosystem
  enforces a coverage floor.
- **Cross-platform matrix** — `Ubuntu × macOS × Python 3.10 / 3.11 / 3.12`.
  Unique to this repo.
- **Strict typing** — `mypy grok_build_bridge` in strict mode. Also
  first in the ecosystem.
- **Schema validation** — `jsonschema Draft202012Validator`, aligned
  with `grok-install` v2.14 (so adoption here avoids the draft-07
  drift that persists in `grok-yaml-standards`; see §2 #8).
- **Build artefacts** — `python -m build` → wheel + sdist with 7-day
  artifact retention; build job depends on all prior jobs.
- **Concurrency discipline** — `cancel-in-progress` on same ref.

The proposal is to extract this workflow as a reusable template (a
published composite / reusable workflow, or a vendored file that
adopters copy) and adopt it across the 7 other CI-enabled repos in
the ecosystem. The effect is not only quality parity; it is the
*delivery vehicle* for §2 #3 (SHA-pin actions) and §2 #13 (blocking
`pip-audit` + secret-scanning) — both of which, once landed, become
part of the template and propagate automatically.

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch; paths stable).

**Source template — `grok-build-bridge/.github/workflows/ci.yml`**
*(audits/09-grok-build-bridge.md §5)*:

| Job | Purpose |
|-----|---------|
| `lint` | `ruff check .` + `ruff format --check .` + `mypy grok_build_bridge` (**strict**). |
| `test` | Matrix **py3.10 / 3.11 / 3.12 × Ubuntu / macOS**. `pytest --cov-fail-under=85`. Codecov upload non-blocking. |
| `schema-check` | Validates `templates/*.yaml` against `bridge.schema.json` using **jsonschema Draft202012Validator**. |
| `safety-scan` | `bandit -r grok_build_bridge -ll` + `pip-audit` *(currently non-blocking — §2 #13 fixes this)*. |
| `docs-link-check` | `lychee-action@v2` in offline mode on `*.md`. |
| `build` | `python -m build` → wheel + sdist; 7-day artifact retention; **depends on all prior jobs**. |

*(Characterisation "CI is the strongest in the ecosystem" is from
audit 09 §1 summary.)*

**Adopter-side call-out** — `audits/10-grok-agent-orchestra.md §9 row 3`:

> "Adopt `grok-build-bridge`'s CI template (lint + matrix test + mypy
> strict + Draft-2020 schema + safety-scan + build) from day one."
> *Rationale: "Instead of accreting CI later, stamp the ecosystem's
> best CI onto this repo before merging the first real PR."*

**Risk register** — `audits/98-risk-register.md`:

- **SEC-2** (S2): non-blocking `pip-audit` across the ecosystem.
  Template propagation closes this on the 7 adopters once §2 #13
  fixes it at the template source.
- **SUP-1** (S2): major-tag pinning of third-party actions.
  Template propagation closes this on the 7 adopters once §2 #3
  fixes it at the template source.

## Acceptance criteria

### Part 1 — Extract the template

Pick **one** of (A) or (B); either satisfies the "extract" half.

#### Option A — Reusable workflow (recommended)

- [ ] Copy `.github/workflows/ci.yml` to a new reusable workflow at
      e.g. `AgentMindCloud/grok-build-bridge/.github/workflows/baseline-ci.yml`
      with `on: workflow_call:` and parameterised inputs
      (`package-path`, `python-versions`, `os-matrix`,
      `cov-fail-under`, etc.).
- [ ] Adopters call it via `uses:
      AgentMindCloud/grok-build-bridge/.github/workflows/baseline-ci.yml@<SHA>`
      — SHA-pinned per §2 #3.

#### Option B — Vendored template directory

- [ ] Copy the workflow to `grok-build-bridge/templates/ci/` (or a
      similar location) with a short README describing the
      per-repo adaptation contract (what to rename, what to
      parametrise).
- [ ] Adopters copy the file and keep it in sync via Renovate /
      manual backport. Cheaper to set up, worse for long-term
      drift; use only if Option A is blocked on the workflow's
      matrix features.

### Part 2 — Adopt in each CI-enabled repo

One checkbox per adopter repo. Each adopter's CI should end up
with (at minimum): lint + mypy strict + matrix test + schema-check
(if applicable) + safety-scan + build. The template provides
these; adopters drop their bespoke CI in favour of the reusable
workflow or the vendored copy.

- [ ] `grok-install` — adopt for YAML/schema validation + markdown
      lint pipeline. Existing `validate.yml` rolls up into the
      template; `ci.yml` (currently not fetched — audit 01 §5)
      should point at the template.
- [ ] `grok-yaml-standards` — adopt. Existing `validate-schemas.yml`
      already uses an exact-pin discipline — the template adoption
      only adds the CI-level posture improvements (matrix, strict,
      coverage). Keep the schema-validate job; retire bespoke
      scaffolding that the template subsumes.
- [ ] `grok-install-cli` — adopt. Merge `security.yml` into the
      template's `safety-scan` job.
- [ ] `grok-install-action` — adopt the portions that apply to a
      Node/composite action (`test.yml` → template's test + build;
      `release.yml` stays bespoke).
- [ ] `grok-docs` — adopt for Python+MkDocs build + link check.
- [ ] `awesome-grok-agents` — adopt. Also a natural venue for a
      `grok_install_stub` → real CLI invocation hand-off once §2
      #12 lands.
- [ ] `grok-agents-marketplace` — Node/Next.js repo; adopt
      whichever jobs translate (lint, build, dependency-review).
      The template is Python-centric; a parallel JS-flavour
      reusable workflow may be warranted if adoption proves
      awkward — flag as a sub-issue.

### Part 3 — Sequencing with §2 #3 and §2 #13

- [ ] **Before** freezing the template for adoption: confirm
      §2 #3 (SHA-pin actions) has landed in `grok-build-bridge`
      itself, so the template inherits SHA pins at extraction
      time.
- [ ] **Before** freezing the template: confirm §2 #13 (blocking
      `pip-audit` + secret-scan) has landed in `grok-build-bridge`,
      so the `safety-scan` job in the promoted template is
      already correct.
- [ ] If §2 #3 or #13 are still in flight when this issue is
      ready to land, either:
      - wait for both to merge, or
      - land the template now and cut a follow-up
        template-bump PR once #3 and #13 merge.

## Notes

- **Why a reusable workflow (Option A) over a vendored template
  (Option B).** Reusable workflows centralise the template's
  evolution at a single pinned SHA. Adopters get template bumps
  via Renovate just like any other pinned action (see §2 #3).
  A vendored template relies on manual backport and drifts the
  moment the first adopter customises.
- **Node/JS adoption caveat.** `grok-agents-marketplace` (Next.js)
  and `grok-install-action` (composite / Node 20) will only
  inherit the matrix + coverage + strict-typing discipline in
  spirit; the template's Python-specific jobs don't port 1:1.
  A small JS-flavour sibling reusable workflow may be needed —
  scope that as a follow-up if the two repos prove awkward
  after the first adoption attempts.
- **What the template does NOT include.** Release/publish
  automation, pages deployment, and bespoke per-repo jobs
  (e.g. `grok-install`'s `anti-slop.yml`) stay per-repo. The
  template is the CI *floor*, not the full workflow list.
- **§2 #8 cross-cut.** The template validates with
  Draft-2020-12. `grok-yaml-standards` still targets draft-07;
  §2 #8 (migrate to draft-2020-12 for v1.3) is the surgical
  fix for that drift. Template adoption in `grok-yaml-standards`
  does not force #8 to land first — the template's
  `schema-check` job is configurable or can be skipped per-repo
  until #8 ships.
