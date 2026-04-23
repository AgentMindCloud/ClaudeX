# Ship grok-docs v2.14 content + reference pages for the 7 undocumented standards

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #10 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/grok-docs
- **Risks closed**: VER-4 (S2) outright, DOC-2 (S2) outright — both from `audits/98-risk-register.md`.
- **Source audits**: `[→ 05 §9 row 1]`. Supporting: `audits/05-grok-docs.md §1, §4, §11 row 2` (current v2.12 advertisement + 5-of-12 standards coverage + full nav); `audits/00-ecosystem-overview.md §4` (schema-draft matrix), `§5` (standards-count coherence — 12 is authoritative), `§7.1` (version-drift table).
- **Effort (§2)**: L — content-writing cost dominates. Spec-page rewrite from v2.12 → v2.14 is M in isolation; adding 7 new standard-reference pages (`grok-config` / `grok-update` / `grok-test` / `grok-docs` / `grok-tools` / `grok-deploy` / `grok-analytics` / `grok-ui` — minus `grok-docs` which is the repo itself, so 7 pages) is what pushes this to L. No coding required; all Markdown.
- **Blocked by (§2)**: none — content is ready to lift from `grok-yaml-standards/grok-*/` spec folders + `standards-overview.md` + `version-reconciliation.md`, plus the `grok-install` v2.14 spec + CHANGELOG.
- **Unblocks (§2)**: #4 — `repository_dispatch` from `grok-install` → `grok-docs`, `grok-install-action`, `grok-agents-marketplace`. Without v2.14 docs existing, a dispatch-on-release trigger fires into an empty target. Once this rec ships, #4 becomes drafteable.
- **Suggested labels**: `docs`, `v2.14`, `standards-reference`, `content`, `phase-1b`

---

## Context

`grok-docs` is the ecosystem's canonical documentation site at
`agentmindcloud.github.io/grok-docs/`. Every adopter lands here
first. Today it ships **two drift gaps** that compound:

1. **Spec-version lag.** The site advertises `grok-install` spec
   **v2.12**. The spec is currently at **v2.14** — two minor
   versions ahead. VER-4 in the risk register captures this
   directly.

2. **Catalogue-coverage gap.** The site's nav references **5**
   YAML file types (`grok-install`, `grok-agent`, `grok-workflow`,
   `grok-security`, `grok-prompts`). `grok-yaml-standards` v1.2.0
   ships **12** (8 core + 4 extensions). Seven standards are
   undocumented: `grok-config`, `grok-update`, `grok-test`,
   `grok-tools`, `grok-deploy`, `grok-analytics`, `grok-ui`.
   DOC-2 in the risk register captures this.

   (`grok-docs` the standard is self-documenting via the nav
   itself — the site IS its own `grok-docs` standard reference;
   no separate page is required.)

The two drifts reinforce each other. A new adopter reading the
v2.12 spec page sees 5 file types and assumes the ecosystem
has 5. Another adopter reading `grok-yaml-standards`'
`standards-overview.md` sees 12. `grok-install-action`'s README
advertises 14 (pre-reconciliation — addressed in §2 #14a). A
third adopter reading `vscode-grok-yaml`'s landing description
also sees 14 (addressed in §2 #14b). The ecosystem's official
documentation site is the place that should arbitrate between
these competing numbers, and today it fails that test.

The fix is entirely content-authoring — no code, no CI changes
required (the schema-sync workflow `sync-schemas.yml` already
republishes the 12 schemas daily; it is the nav + content pages
that haven't caught up). L-effort because the content volume is
real: one spec page rewrite + seven new reference pages, each
with conceptual overview + schema reference + usage example +
cross-links. A single motivated author can ship this in a week
of focused time; a reviewer + author pair in two weeks.

Secondary benefit: once v2.14 docs exist, §2 #4 (`repository_
dispatch` wiring from `grok-install` → `grok-docs`) becomes
drafteable. Without this rec, a dispatch-on-release fires into
an empty target; nothing useful rebuilds. This rec is the
only Phase-1B draft that unblocks §2 #4 — hence its inclusion
at this point in the drafting sequence.
