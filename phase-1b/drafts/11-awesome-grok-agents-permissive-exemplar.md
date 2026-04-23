# Add a permissive-profile exemplar template to awesome-grok-agents

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #11 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/awesome-grok-agents
- **Risks closed**: closes the "missing-exemplar" finding in `audits/00-ecosystem-overview.md §6.2` (the 6-strict / 4-standard / **0-permissive** distribution across the 10 featured agents). Contributes indirectly to full closure of the safety-profile contract `grok-yaml-standards` publishes under §2 #5.
- **Source audits**: `[→ 06 §9 row 1]`. Supporting: `audits/00-ecosystem-overview.md §6.1, §6.2` (tripartite model, distribution table).
- **Effort (§2)**: S — a single template + `featured-agents.json` entry + CI passes. The "wait on §5" is the blocker, not the work itself.
- **Blocked by (§2)**: #5 — the permissive template's `grok-install.yaml` needs to be honest against the published rubric. Before the rubric exists, "permissive" is prose; after, it is a seven-axis contract. The exemplar only means what it says once the contract exists.

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md); not yet filed upstream; speculative.
- **Re-review trigger**: rewrite this draft's §Acceptance Part A template fields if §2 #5's `permissive` row (Part A of that draft) is substantively changed during upstream review. The exemplar template's `grok-install.yaml` body has to match whatever the rubric's final `permissive` column says.

- **Suggested labels**: `template`, `safety-profile`, `permissive`, `phase-1b`

---

## Context

The Grok ecosystem advertises a tripartite safety model —
`strict` / `standard` / `permissive` — but `awesome-grok-agents`'
gallery of 10 featured templates has zero `permissive` examples.
Today's distribution, per `featured-agents.json` v1.0:

- `strict`: **6** (reply-engagement-bot, code-reviewer, …)
- `standard`: **4**
- `permissive`: **0**

The practical consequence, verbatim from
`audits/00-ecosystem-overview.md §6.2`:

> "The tripartite model needs a reference instance at each level
> for the profiles to be usable. With 0 permissive examples:
> - New adopters cannot calibrate what 'permissive' should look
>   like in practice.
> - There's no way to round-trip the `grok-install-cli` safety
>   scanner against a permissive-profile agent (any test
>   template is necessarily strict or standard).
> - The rubric in `grok-yaml-standards/grok-security` cannot be
>   verified against a shipped instance."

This rec adds **one** template that honestly exemplifies the
`permissive` profile — most useful as an *internal tool*
pattern (an agent running in a trusted CI environment where
open egress and host code execution are acceptable because
there is no external-write surface). The key design
constraint: `permissive` is not "anything goes". §2 #5's rubric
gives `permissive` a concrete seven-axis contract (open egress,
logs kept, operator-initiated halt). The exemplar has to match
that contract cell-for-cell so newcomers can see *what
permissive means*, not just *that permissive exists*.

Secondary benefit: once the template is in the gallery, §2 #12's
replace-the-stub work (already drafted in this Session 2 pass)
can validate the real CLI against a permissive agent — closing
a round-trip test that today has no fixture.

## Evidence

From `main` snapshot on 2026-04-23 (WebFetch; paths stable).

**Current gallery distribution** —
`audits/06-awesome-grok-agents.md §6, §11 row 3`
(`featured-agents.json` v1.0, updated 2026-04-21):

| Profile | Count | Notes |
|---------|:-:|---|
| `strict` | **6** | Every agent with external write access (X posting, code changes). |
| `standard` | **4** | Read-mostly agents. |
| `permissive` | **0** | **No exemplar.** |

**The 10 existing templates** —
`audits/06-awesome-grok-agents.md §2`:
- `code-reviewer/`, `hello-grok/`, `live-event-commentator/`,
  `personal-knowledge/`, `reply-engagement-bot/`,
  `research-swarm/`, `scientific-discovery/`,
  `thread-ghostwriter/`, `trend-to-thread/`, `voice-agent-x/`.

**Template shape** (consistent across the 10 per audit 06 §2):
- `README.md`, `.env.example`, `grok-install.yaml`,
  `.grok/` folder, optional `tools/`.

**CI that will exercise the new template** —
`audits/06-awesome-grok-agents.md §5`:
- `discover` auto-discovers new `templates/*`; no manual CI
  edit needed.
- `validate-matrix` runs `validate_template.py`,
  `scan_template.py` (fails on warnings), and
  `mock_run_template.py` per template.
- `spec-version` gate requires one of v2.12 / v2.13 / v2.14 in
  the template's `grok-install.yaml`.

**Prerequisite state**:
- §2 #5 draft: [`phase-1b/drafts/05-safety-profile-rubric.md`](05-safety-profile-rubric.md)
  — defines the seven-axis `permissive` contract. Not filed
  upstream.
- §2 #5 Part A's `permissive` column (summarised — authoritative
  copy in the #5 draft):
  - `external_writes: open`
  - `secret_access: read_passthrough`
  - `code_execution: host_bounded`
  - `approval_gate: none`
  - `scan_severity_threshold: error_log_only`
  - `network_egress: open`
  - `halt_on_anomaly: operator_only`

**Audit rec** —
`audits/06-awesome-grok-agents.md §9 row 1` (verbatim):

> "Add a `permissive` exemplar template (e.g. an internal-tool
> agent with no X write access) to fill the 3rd safety profile
> slot. *Rationale:* the tripartite profile model is referenced
> everywhere but has zero visible `permissive` example. New
> adopters can't calibrate what `permissive` should look like.
> *Blocked by:* safety-profile rubric from `grok-yaml-standards`."

**Related §2 cross-refs**:
- §2 #5 — the contract. Prerequisite.
- §2 #12 — replaces the `grok_install_stub` with the real CLI;
  the new exemplar is validated end-to-end once §12 lands.
- §2 #1 — the shared `grok-safety-rules` package (Session-2
  sibling); the exemplar transitively inherits the shared
  library via the CLI.
- `audits/06 §9 row 4` — "add a `safety_profile` distribution
  report to the CI summary" — naturally paired with this rec
  in §Part B below; surfaces the 2-of-3-gap closure
  automatically once the new template lands.
