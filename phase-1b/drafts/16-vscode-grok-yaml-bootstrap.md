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

---
