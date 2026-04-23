# Bootstrap vscode-grok-yaml v0.1.0 — read-only schema validation against grok-yaml-standards

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #16 (`audits/99-recommendations.md`)
- **Target repo (primary + only)**: AgentMindCloud/vscode-grok-yaml
- **Risks closed**: partial GOV-3 (S3) — from `audits/98-risk-register.md`. Full GOV-3 closure also requires the sibling §2 #15 landing (description honesty) + an analogous bootstrap on `grok-agent-orchestra` (§2 #17).
- **Source audits**: `[→ 07 §9 row 2]`. Supporting: `audits/07-vscode-grok-yaml.md §1, §4, §8, §10`. Cross-cut: `audits/00-ecosystem-overview.md §7.2` (governance-file gap), `§4` (schema-draft matrix — relevant once the extension fetches schemas).
- **Effort (§2)**: M — "read-only schema validation against `grok-yaml-standards`" is the Minimum-Viable-Extension bar, and it's still non-trivial (VS Code extension scaffold + schema fetch + `yaml-language-server` integration + CI).
- **Blocked by (§2)**: #15 — `vscode-grok-yaml`'s landing description needs to be honest about the pre-alpha state before bootstrap begins, so contributors aren't confused mid-flight.

### Speculative-draft discipline (mandatory — this draft is Session 2)

- **Prerequisite status**: drafted in [`phase-1b/drafts/15a-vscode-grok-yaml-description.md`](15a-vscode-grok-yaml-description.md); not yet filed upstream; speculative.
- **Re-review trigger**: rewrite this draft if the prerequisite issue (§2 #15a) is substantially rewritten during upstream review. Both of #15a's options converge on "the description is honest about pre-alpha state" — either option leaves this bootstrap draft's assumptions intact. Only a rewrite that keeps #15a's description *promissory* (e.g. "supports all 14 standards today") would invalidate this draft's framing in §Context; surface that divergence here rather than silently editing.

- **Suggested labels**: `bootstrap`, `v0.1.0`, `vscode`, `schema-validation`, `phase-1b`

---

## Context

`vscode-grok-yaml` is advertised as "the VS Code extension for all
14 YAML standards" but the repo today contains LICENSE + README +
a `media/` directory — no source, no `package.json`, no CI. It is
the largest gap between marketing and substance in the Grok
ecosystem: a shell repo shaped like a shipped product.

§2 #15 (the prerequisite to this issue) downgrades the README and
GitHub description to honestly describe the current state. Once
that lands, contributors can onboard without surprise at the
empty repo. This issue is the next step: ship a v0.1.0 that
delivers the *minimum* visible value — **read-only schema
validation in the editor**, with no authoring features, no
IntelliSense beyond the schema-driven one that
`yaml-language-server` already provides for free, no linting
beyond what a schema can express.

The minimum-viable extension has three upsides:

1. **Grok YAML authors get immediate value.** Saving a malformed
   `.grok/grok-install.yaml` turns red in the editor without
   leaving VS Code. That is already more than every other
   ecosystem consumer currently offers.
2. **It sets a floor.** Later features (deeper IntelliSense,
   snippets, Quick Fix suggestions, cross-file validation) layer
   on top of a shipped extension. A shipped v0.1.0 is infinitely
   more maintainable than a "coming soon" shell.
3. **It pins a schema-consumption pattern the ecosystem can
   reuse.** §2 #8 (draft-2020-12 migration in
   `grok-yaml-standards`) has landed or is landing; this
   extension's schema-fetch contract becomes a reference
   implementation for other consumers.

The extension is built on top of the existing `redhat.vscode-yaml`
extension's `yaml-language-server` — the standard way VS Code
does YAML schema validation. This repo's contribution is a
*schema-association manifest* plus packaging, not a new language
server.
