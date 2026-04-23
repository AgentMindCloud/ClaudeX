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

## Acceptance criteria

Two parts. Part A is the new template itself. Part B is the
distribution-report CI companion that surfaces the gap closure
automatically (audit 06 §9 row 4). Both can land in one PR; the
distribution report is an S-effort add.

### Part A — Add one `permissive` template

Proposed template: **`internal-ci-assistant/`** — an agent that
runs inside a trusted CI environment (maintainer's own
organisation), consumes an internal code repository's diffs,
writes structured feedback to a private Slack/Discord channel,
and has no X write access. Internal-tool posture; open egress
+ operator-only halt make sense because the agent is sandboxed
by the CI runtime itself, not by an application-layer
`approval_gate`.

- [ ] **Create `templates/internal-ci-assistant/`** with the
      gallery's standard shape:
      - `README.md` — what the agent does, why permissive is
        honest for this use case, what it does NOT do
        (cross-reference to the rubric's `permissive` row).
      - `.env.example` — the env vars the agent reads
        (Slack/Discord webhook URL, internal git token,
        Grok API key).
      - `grok-install.yaml` — the installable unit. Must match
        §2 #5 Part A's `permissive` row cell-for-cell (see
        template body below).
      - `.grok/` — sample agent directory per ecosystem
        convention.
      - `tools/` — the one or two internal tools the agent
        uses (e.g. a git-diff reader + a webhook poster).

- [ ] **`grok-install.yaml` template body** — the parts that
      encode the profile claim:

      ```yaml
      grok_install_version: 2.14
      name: internal-ci-assistant
      description: >
        Internal CI assistant that reads private repo diffs,
        summarises via Grok, and posts to a private operator
        channel. Runs in a sandboxed CI environment.
      safety_profile: permissive
      permissions:
        external_writes:
          mode: open
          channels: [slack_webhook, discord_webhook]
        secret_access:
          mode: read_passthrough
          declared_secrets: [GROK_API_KEY, SLACK_WEBHOOK_URL, GIT_TOKEN]
        code_execution:
          mode: host_bounded
        network_egress:
          mode: open
          rationale: "Runs in trusted CI; egress governed by runner's network policy, not by agent."
        approval_gate:
          mode: none
        halt:
          mode: operator_only
      ```

      The field names track §2 #5's seven-axis rubric. If the
      rubric changes during upstream review, update this
      template to match (speculative-draft discipline).

- [ ] **Update `featured-agents.json`** to include the new
      template entry:

      ```json
      {
        "name": "internal-ci-assistant",
        "safety_profile": "permissive",
        "category": "internal-tooling",
        "description": "Internal CI assistant: private repo diffs → Grok summary → operator channel. Sandboxed; no external writes."
      }
      ```

- [ ] **Template README content checklist**:
      - One-sentence summary.
      - Why `permissive` is honest here (not a retreat from
        security, but a match between environment and claim).
      - Install instructions (standard `grok-install install ...`).
      - Expected environment (CI-only; not for X-facing deploy).
      - Link to §2 #5's rubric `docs/safety-profile-rubric-v1.md`
        (once that lands in `grok-yaml-standards`).
      - Explicit "What this is NOT": this template is NOT a
        reference for customer-facing permissive agents (that
        would be irresponsible); it is a reference for
        sandboxed-environment permissive agents.

- [ ] **CI signal**: the `discover` job auto-picks up the new
      template. The `validate-matrix` job exercises it
      (eventually against the real CLI, once §2 #12 lands).
      The `spec-version` gate passes because the template
      declares `2.14`.

- [ ] **CHANGELOG** entry under `[Unreleased]`: "Added
      permissive-profile exemplar `internal-ci-assistant`;
      distribution now 6 strict / 4 standard / 1 permissive."

### Part B — Add a `safety_profile` distribution report to CI

From `audits/06-awesome-grok-agents.md §9 row 4`: surfacing the
distribution in CI prevents the 2-of-3 gap from silently
reopening as the gallery grows. S-effort; pairs naturally with
Part A so the same PR both closes the gap and installs the
guard-rail that keeps it closed.

- [ ] **Add a `distribution` job** to
      `.github/workflows/validate-templates.yml`. The job:
      1. Reads `featured-agents.json`.
      2. Counts entries per `safety_profile` value.
      3. Writes a summary block to
         `$GITHUB_STEP_SUMMARY`:

         ```
         ## Safety-profile distribution
         | Profile | Count |
         |---------|:-----:|
         | strict     | 6 |
         | standard   | 4 |
         | permissive | 1 |
         ```

      4. **Does NOT fail** on zero-count profiles — this is a
         visibility job, not a gate. Adding a gate is a
         separate policy decision and out of scope for this
         rec.

- [ ] **Do NOT hardcode the three profile names.** Let the job
      iterate over the distinct values it finds in
      `featured-agents.json`. If a typo ("permisive") slips
      into a new entry, it appears in the summary as its own
      column, making the typo visible.

- [ ] **Cross-check against the rubric** (optional, ships if
      §2 #5 has landed upstream when this PR opens): the
      `distribution` job also reports "profiles present in
      gallery but missing from the published rubric" and "profiles
      in the rubric but zero-count in the gallery". Both are
      zero today (post-Part A) but the check future-proofs
      the report against silent drift.

- [ ] **Flag Part B as optional** — if the maintainer prefers
      to land Part A first and Part B as a follow-up PR, that
      is fine. Keeping them together is cheaper; landing Part
      A alone is still a net win.
