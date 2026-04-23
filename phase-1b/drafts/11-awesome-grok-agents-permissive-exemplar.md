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
