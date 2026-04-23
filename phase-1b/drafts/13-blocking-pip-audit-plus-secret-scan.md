# Make pip-audit blocking and add secret-scanning (gitleaks / trufflehog) in CI

<!-- phase-1b metadata (do not paste into the GitHub issue body) -->
- **§2 rec**: #13 (`audits/99-recommendations.md`)
- **Target repos (pilot, 2)**: AgentMindCloud/grok-install-cli, AgentMindCloud/grok-build-bridge
  - File the body below against **both** repos independently (one issue each). The two
    repos ship identical fixes against identical evidence; the body is written to stand
    alone in either.
  - Broader ecosystem rollout across all 12 repos is the delivery of §2 #18, not this
    issue — scope is kept narrow so the pilot can land fast.
- **Risks closed**: SEC-2 (S2) outright on both pilot repos; SEC-3 (S2) closed on both
  pilot repos and *partially* ecosystem-wide (full closure happens when §2 #18 propagates
  the template to the other 10 repos)
- **Source audits**: `[→ 03 §5]`, `[→ 03 §6]`, `[→ 03 §9 row 2]`, `[→ 03 §9 row 3]`, `[→ 09 §5]`, `[→ 09 §6]`, `[→ 09 §9 row 2]`
- **Effort (§2)**: S
- **Blocked by**: none
- **Cross-refs**: §2 #18 (CI template promotion — the delivery vehicle for the
  remaining 10 repos); §2 #3 (SHA-pin actions — orthogonal; can land in parallel)
- **Suggested labels**: `security`, `supply-chain`, `ci`, `phase-1b`

---

## Context

Two gaps exist in the current security posture of `grok-install-cli`
and `grok-build-bridge`:

1. **`pip-audit` runs in CI but is non-blocking.** Both repos run
   `pip-audit` as part of their security / safety-scan workflow, but
   with `continue-on-error: true` (or the `|| true` shell pattern).
   A vulnerable transitive dependency therefore lands on `main`
   silently; the scan is informational, not enforcing.
2. **No secret-scanning.** Neither repo runs `gitleaks`, `trufflehog`,
   or GitHub's native secret-scanning workflow. An accidentally
   committed API key (xAI, GitHub, npm, PyPI) is not caught at PR
   time.

Both gaps are particularly visible here because these two repos are
the ecosystem's *own* pre-install safety scanners. `grok-install-cli`
ships `grok_install/safety/` (static regex + pattern scan for
hard-coded secrets). `grok-build-bridge` ships a dual-layer safety
scan (deterministic + LLM-based) that is explicitly marketed as the
ecosystem's hardest security surface. When the safety scanners' own
CI posture is weaker than what they advertise to consumers, the
credibility gap is structural.

The fix is two flips and one new job per repo:

- Drop `continue-on-error: true` (or `|| true`) from the `pip-audit`
  step so a CVE in a transitive dep fails the run.
- Add a `secret-scan` job running gitleaks (or trufflehog) on every
  PR + push.

Both are well-trodden CI recipes; `grok-install-cli/.github/workflows/security.yml`
and `grok-build-bridge/.github/workflows/ci.yml` (the `safety-scan`
job) already exist and can be extended in place.

## Evidence

From `main` snapshots on 2026-04-23 (WebFetch; paths stable).

**`grok-install-cli`** — `audits/03-grok-install-cli.md §5`:

- `.github/workflows/security.yml` runs weekly (Mon 07:00 UTC) +
  on push/PR. Steps: `bandit -r src -ll`; `pip-audit || true`
  (**non-blocking**). No CodeQL, no secret scan. Read-only
  permissions.
- `audits/03 §9 row 2`: "Make `pip-audit` blocking in `security.yml`
  (drop the `|| true`). *Silent dependency vulnerabilities defeat
  the purpose of running the scan. Aligns posture with the
  'safety 2.0' ecosystem narrative.*"
- `audits/03 §9 row 3`: "Add gitleaks or trufflehog to
  `security.yml`. *Pre-install scanning for hardcoded keys is a
  headline product feature; the CLI's own CI should enforce the
  same against its repo.*"

**`grok-build-bridge`** — `audits/09-grok-build-bridge.md §5 / §6`:

- `.github/workflows/ci.yml` has a `safety-scan` job: `bandit -r
  grok_build_bridge -ll` + `pip-audit` (**non-blocking** — `|| true`
  pattern implied). No secret-scan job.
- `audits/09 §6`: "`pip-audit` still non-blocking"; "No secret-scan
  CI job (same gap as grok-install-cli)".
- `audits/09 §9 row 2`: "Replace `pip-audit || true` with blocking
  + add gitleaks/trufflehog for secret-scan. *Same recommendation
  as grok-install-cli; here too the safety narrative is
  contradicted by non-blocking CI.*"

Risk register — `audits/98-risk-register.md`:

- **SEC-2** (S2, likelihood medium): "`pip-audit` runs in CI but is
  non-blocking (`continue-on-error: true`) — vulnerable transitive
  deps land in main without gating."
- **SEC-3** (S2, likelihood medium): "No secret-scanning (gitleaks /
  trufflehog / GitHub native) on any repo in the ecosystem — a
  committed token would not be caught at PR time."

## Reproduction

```bash
# In either repo, confirm current posture:
grep -RnE "pip-audit|continue-on-error:\s*true|\|\|\s*true" .github/workflows/
grep -RnE "gitleaks|trufflehog|secret-scanning" .github/workflows/
```

The first grep returns at least one non-blocking `pip-audit`
invocation; the second returns nothing.

## Acceptance criteria

### Part 1 — Make `pip-audit` blocking

- [ ] Remove `continue-on-error: true` from the `pip-audit` step
      (in `grok-install-cli/.github/workflows/security.yml`, and in
      `grok-build-bridge/.github/workflows/ci.yml`'s `safety-scan`
      job). If the step uses `|| true` in a shell `run:` block,
      drop the `|| true`.
- [ ] If the removal surfaces an existing known CVE, **do not
      re-silence it**. Either upgrade the affected dep (preferred)
      or add an explicit `--ignore-vuln VULN-ID` with a trailing
      comment pinning the decision to a tracked issue + sunset
      date. `pip-audit --ignore-vuln` is explicit per-CVE — no
      blanket bypass.
- [ ] Document the posture change in the repo's `SECURITY.md`
      (or `CONTRIBUTING.md` if there's no SECURITY.md yet) so
      the intent is legible to future contributors.

### Part 2 — Add secret-scanning

Pick **one** of (A), (B), or (C).

#### Option A — gitleaks (recommended for cross-repo consistency)

- [ ] Add a `secret-scan` job invoking `gitleaks/gitleaks-action@<SHA>`
      (SHA pin per §2 #3) with a `.gitleaks.toml` at repo root.
- [ ] Scope: full history on push to default branch; PR-diff-only
      on PRs to keep CI time manageable.
- [ ] Start with gitleaks' default ruleset; only allowlist known
      test-fixture strings via `.gitleaks.toml` if the default
      ruleset actually fires on them.

#### Option B — trufflehog

- [ ] Add a `secret-scan` job invoking `trufflesecurity/trufflehog@<SHA>`
      with the same scope (full-history on default-branch push,
      PR-diff-only on PRs).
- [ ] Equivalent outcome to Option A; prefer A if the ecosystem is
      settling on one tool.

#### Option C — GitHub native secret-scanning

- [ ] Enable **Settings → Security → Secret scanning** on the repo
      (requires public repo or GitHub Advanced Security on
      private).
- [ ] Add a `secret-scan` CI job as a CI-level backstop so the
      posture is visible in the workflow run list even for forks
      that don't inherit the Settings toggle. (Option C alone
      does not satisfy the issue — it does not run on PRs from
      forks.)

### Part 3 — Posture parity

- [ ] Once both parts land, each repo's workflow list shows a
      `secret-scan` job and a blocking `pip-audit` step. Both
      appear in the GitHub PR status checks and are required
      before merge.

## Notes

- **Pilot-then-propagate.** These two repos are chosen as pilots
  because they are the template sources §2 #18 extracts for
  ecosystem adoption. Once the fix lands here, §2 #18 propagates
  it to the remaining 10 repos without re-deciding tool choice
  or policy.
- **SEC-3 scope.** SEC-3 covers all 12 repos; this issue closes
  it on the two pilot repos and flags it as *partially closed*
  ecosystem-wide in `phase-1b/ISSUES.md`. Full closure is a §2
  #18 deliverable.
- **Landing alongside §2 #3.** §2 #3 (SHA-pin actions) is
  orthogonal; both can land in one PR per repo if the maintainer
  prefers. The SHA-pin policy in §2 #3 applies to the
  `gitleaks-action@<SHA>` / `trufflehog@<SHA>` pin cited in
  Options A and B.
- **Out of scope.** Ecosystem-wide rollout beyond the two pilots
  is §2 #18. Library exact-pinning (e.g. `grok-build-bridge` `>=`
  ranges on `xai-sdk` / `tenacity`) is audit 09 §9 row 3 and
  catalogued in `audits/99-recommendations.md §3.2`.
