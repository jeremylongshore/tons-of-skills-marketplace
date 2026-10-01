# aomi-transact Security Posture

This document maps the `aomi-transact` skill against [OWASP Agentic Skills Top 10 (v1.0, March 2026)](https://owasp.org/www-project-agentic-skills-top-10/) and records the controls in place for each risk. Reviewers can audit the per-control claims against the live SKILL.md frontmatter, the references, and the captured scanner reports under [`.scanner-reports/`](https://github.com/aomi-labs/skills/tree/main/.scanner-reports).

**Last reviewed:** 2026-08-07 against `@aomi-labs/client` v0.4.2 (published CLI bundle).

## Threat model

`aomi-transact` is a procedure for an AI agent to drive the [`@aomi-labs/client`](https://www.npmjs.com/package/@aomi-labs/client) CLI — composing natural-language intents into queued wallet requests, simulating them on a forked chain, and signing them via account-abstraction-first execution. The skill itself does not custody funds, sign without explicit user request, or write outside `~/.aomi/`. The CLI it drives, however, **does** execute on-chain transactions, so the skill is correctly classified as **risk_tier: L2** (elevated) under the OWASP universal manifest schema.

## Controls by AST risk

### AST01 — Malicious Skills

**Risk**: A skill is published that hides an exfiltration / drain payload behind benign-looking documentation.

**Controls in place:**

- The skill is published from [`aomi-labs/skills`](https://github.com/aomi-labs/skills) under MIT license; provenance is verifiable via `git log` and the GitHub repo signing keys.
- The skill body (`SKILL.md` plus `references/`, `templates/`, `agents/`) contains no executable code beyond the `templates/aomi-workflow.sh` shell wrapper and shell snippets in documentation. The wrapper is human-auditable (~263 lines, no minification, no eval/exec, no curl-pipe-bash).
- All shell snippets in `references/*.md` are documentation, not executed by the skill itself. The skill's actual operational scope is constrained to `aomi <subcommand>` and `npx @aomi-labs/client@latest <subcommand>` per the `permissions.shell` declaration.
- No network calls outside the declared `permissions.network.allow` list.
- **Open**: signed releases (sigstore / `gh attestation`) are not yet wired up. Tracked separately.

### AST02 — Skill Injection / Tampering

**Risk**: A modified skill is loaded from an untrusted source; tampering goes undetected.

**Controls in place:**

- Canonical source is the `aomi-labs/skills` GitHub repo. Tags are not yet signed; users who care about integrity should pin to a commit SHA and verify against the upstream repo.
- The `permissions.files.deny_write` list (`SOUL.md`, `MEMORY.md`, `AGENTS.md`) blocks the skill from rewriting agent identity files, which is the canonical injection target.
- **Open**: `gh skill` repo / ref / tree-SHA frontmatter pre-population is on the release checklist (see `docs/todo` item #8) but not yet landed.

### AST03 — Over-Privileged Skills

**Risk**: A skill declares broad permissions (`shell: true`, `network: true`) it doesn't actually need; an injection prompt later abuses the privilege.

**Controls in place:**

- A complete OWASP-format `permissions:` manifest is declared in `SKILL.md` frontmatter:
  - `files.read`: `~/.aomi/` only.
  - `files.write`: `~/.aomi/` only. The skill never writes files directly; the underlying CLI manages its own state dir.
  - `files.deny_write`: identity files (`SOUL.md`, `MEMORY.md`, `AGENTS.md`).
  - `network.allow`: `chat.aomi.dev` only (the CLI's default backend). `network.deny: "*"`.
  - `shell`: array form, two argv prefixes (`aomi`, `npx @aomi-labs/client@latest`). Spec example uses boolean; the array form is a least-privilege extension consistent with AST03 intent.
  - `tools: []` — no MCP / external tool surface.
- Claude Code's `allowed-tools` field is set to `Bash, Grep` (broad) so the skill can render diagnostic snippets in documentation; the OWASP manifest provides the actual operational lockdown as defense-in-depth.

**Verification**:

- [`Cisco AI Defense skill-scanner`](https://github.com/cisco-ai-defense/skill-scanner) v0.x — **0 findings**, `Status: SAFE`. Report: `.scanner-reports/cisco-ai-defense.md`.

### AST04 — Skill Confused Deputy

**Risk**: A skill's identity is reused for a privileged action the user didn't authorize.

**Controls in place:**

- The skill is **read-only by default**. Chat, simulation, session inspection, and app/model/chain introspection do not move funds. Signing is a separate, explicit step the user must request (see the "Hard Rules" section in `SKILL.md`).
- `aomi tx sign` is only invoked after `aomi tx list` shows a pending `tx-N` the user asked for.
- Drain-vector annotations on simulation (recipient ≠ msg.sender, etc.) cannot be bypassed by reformulating the prompt — the skill explicitly forbids this in the security section. See [`references/drain-vectors.md`](references/drain-vectors.md) for the full table.

### AST05 — Skill Side-Effects / Hidden Actions

**Risk**: A skill performs persistent state changes that survive the session without the user's knowledge.

**Controls in place:**

- Side-effect-producing commands (`aomi wallet set <key>`, `aomi secret add NAME=value`, `aomi config set-backend`, `aomi account link`/`unlink`) are **only** run when the user explicitly asks for that specific setup in the current turn and supplies the value themselves. The skill never runs them on its own initiative.
- Before running a credential-setup command the user asked for, the skill confirms what will be persisted and where (local CLI state vs. the aomi backend) so the user can abort.
- Read-side variants (`aomi wallet current`, `aomi account whoami`, `aomi account links`, `aomi config current`, `aomi secret list`) are skill-driven and safe — they expose handle names only, never raw values.

### AST06 — Insecure Skill Communication

**Risk**: A skill exfiltrates data through a side channel (logging, telemetry, off-domain HTTP).

**Controls in place:**

- The skill makes no direct network calls. The CLI it drives talks to `chat.aomi.dev` (the declared backend; `api.aomi.dev` is the legacy host) and to user-supplied RPC endpoints passed through `--rpc-url` at sign time.
- The skill **never echoes a credential value back to the user** after a setup command completes. Confirmation is by handle name or derived address only (see "Hard Rules" #2 in `SKILL.md`).
- `aomi secret add` transmits the credential value to the aomi backend; the skill surfaces this trust-boundary explicitly to the user before running the command (see `references/session.md` and the SKILL.md "Secret Ingestion" subsection).

### AST07 — Inadequate Logging / Auditability

**Risk**: A skill takes actions that cannot be reconstructed after the fact.

**Controls in place:**

- The CLI maintains a log per session (`aomi session log`, `aomi session events`) that replays the full conversation, all tool calls, and all system events from the backend.
- Local session JSON files (`~/.aomi/sessions/session-N.json`) mirror pending and signed transaction state with full calldata, gas estimates, and hashes — inspectable via `cat` + `jq` without a network round-trip.
- The skill's own actions are limited to invoking `aomi <subcommand>`; every invocation is observable in the user's shell history.

### AST08 — Skill Supply-Chain Attacks

**Risk**: A dependency the skill relies on is compromised; the skill picks up the compromise transitively.

**Controls in place:**

- The skill itself has **no runtime dependencies** beyond the `aomi` / `npx` binaries and an outbound HTTP path to `chat.aomi.dev`.
- The CLI (`@aomi-labs/client`) is published to npm by `aomi-labs`. The skill currently tracks the latest package and warns if the detected version is older than v0.4.2 because the command surface is still moving. Note that a global install is not upgraded by reinstalling the skill, so the version check is a required first step.
- The companion `templates/aomi-workflow.sh` shell wrapper depends only on POSIX shell + `jq`, both checked at startup.
- **Open**: npm package signing / sigstore attestation is not yet wired up.

### AST09 — Insufficient User Consent

**Risk**: A skill performs actions the user has not explicitly authorized.

**Controls in place:**

- Every state-changing CLI invocation requires explicit user consent in the same turn:
  - `aomi tx sign` — only after `aomi tx list` shows a pending `tx-N` the user requested.
  - `aomi wallet set` / `aomi secret add` / `aomi config set-backend` / `aomi account link` — only when the user has explicitly asked for that setup and supplied the value.
  - Multi-step batches (`approve` + `swap`) are reviewed by the user via `aomi tx simulate` before signing.
- Drain-vector annotations cannot be bypassed; the skill surfaces blocks rather than reformulating prompts.

### AST10 — Cross-Platform Reuse

**Risk**: A skill that's safe on one host (e.g. Claude Code) becomes unsafe when loaded on a different host (Codex, Cursor, OpenClaw) due to differing tool-permission semantics.

**Controls in place:**

- The OWASP `permissions:` manifest is declarative metadata that all OWASP-aware scanners and registries can read regardless of host. The Claude Code-specific `allowed-tools` field coexists as a sibling.
- An `agents/openai.yaml` is provided for Codex/OpenAI-host metadata (display name, default prompt, invocation policy).
- **Open**: end-to-end install verification across Claude Code + Codex + at least one community installer is on the release checklist (#9, #20). The skill is shaped for cross-platform reuse but has not yet been load-tested on every host.

## Captured scanner reports

All reports under [`.scanner-reports/`](https://github.com/aomi-labs/skills/tree/main/.scanner-reports). Re-run any scanner with the local commands documented in [`docs/todo`](https://github.com/aomi-labs/skills/tree/main/docs/todo).

| Scanner | Status | Findings | Report |
|---------|--------|----------|--------|
| Cisco AI Defense skill-scanner | **PASS** | 0 critical / 0 high / 0 medium / 0 low | [`cisco-ai-defense.md`](https://github.com/aomi-labs/skills/blob/main/.scanner-reports/cisco-ai-defense.md) |
| pors/skill-audit | **PASS** | 0 errors / 4 warns (documentation regex matches) | [`pors-skill-audit.txt`](https://github.com/aomi-labs/skills/blob/main/.scanner-reports/pors-skill-audit.txt) |
| NMitchem/SkillScan | **PASS** | Risk 2.0/10 (threshold 6.0), 1 HIGH = upstream regex bug | [`skillscan.txt`](https://github.com/aomi-labs/skills/blob/main/.scanner-reports/skillscan.txt) |
| Snyk agent-scan | **PASS (advisory)** | 4 HIGH characterizations of risk class — see analysis below | [`snyk-agent-scan.txt`](https://github.com/aomi-labs/skills/blob/main/.scanner-reports/snyk-agent-scan.txt), [`snyk-agent-scan.json`](https://github.com/aomi-labs/skills/blob/main/.scanner-reports/snyk-agent-scan.json) |

**Notes on findings**:

- The 4 pors WARN findings match documentation patterns (`access sensitive data`, `delete...` operations) that appear in `references/session.md` because the docs explain those CLI commands. They are documentation regex matches, not actual destructive code paths.
- The SkillScan HIGH finding (`MCP_001: MCP server launched via npx without version pinning`) is acknowledged. This skill intentionally uses `npx @aomi-labs/client@latest` so agent guidance tracks the current CLI contract; for locked-down environments, install `@aomi-labs/client` globally from a pinned version or npm lockfile and use the `aomi` binary path instead.
- The 4 Snyk HIGH findings (W007, W009, W011, W012) are taxonomic characterizations of the skill's intentional risk surface, not bugs. Each is acknowledged below with the in-place mitigation. Snyk's own exit code is 0 (advisory output), and the skill's `risk_tier: L2` declaration in the OWASP manifest already states this risk class up front.

### Snyk Agent Scan (W-codes) — finding-by-finding analysis

The Snyk Agent Scan rule pack characterizes a skill's risk surface, not just bugs. For a transaction-signing AI skill that uses third-party data sources to compose calldata, the following findings are **structural** — they describe what the skill does on purpose, with mitigations in place. Reviewers should evaluate them against the OWASP AST controls in this document.

| Code | Title | Status | Mitigation in place |
|------|-------|--------|---------------------|
| **W007** | Insecure credential handling | Acknowledged — by design | Skill frontmatter description explicitly forbids the LLM from fabricating, guessing, echoing, or logging credential values. `aomi secret add NAME=<value>` and `aomi wallet set <signing-key>` use placeholder syntax in all docs; the user supplies the real value. The "Hard Rules" and "Security Model" sections of SKILL.md, plus AST05 (Side-Effects) and AST06 (Insecure Communication) above, codify the no-unsolicited-setup posture. |
| **W009** | Direct money access | Acknowledged — by design | The skill is explicitly classified `risk_tier: L2` in the OWASP manifest because it signs and broadcasts on-chain transactions. AST04 (Confused Deputy) and AST09 (Insufficient User Consent) above codify the "read-only by default, signing requires explicit user request" posture. `aomi tx sign` is only invoked after `aomi tx list` shows a pending `tx-N` the user asked for, and multi-step batches go through `aomi tx simulate` on a forked chain first. |
| **W011** | Third-party content exposure | Acknowledged — by design | The agent uses 25+ apps (DefiLlama, 1inch, Khalani, Brave Search, X, Neynar, etc.) to fetch quotes, routes, and read-only data — that is the skill's purpose. Fund-moving calldata that the third-party content influences is gated by `aomi tx simulate` (drain-vector annotations block `recipient != msg.sender`) and an explicit user `aomi tx sign` step. AST04 above and [`references/drain-vectors.md`](references/drain-vectors.md) document the per-protocol guard rules. |
| **W012** | Potentially malicious external URL (npx) | Acknowledged — documented | `npx @aomi-labs/client@latest` is the on-demand fallback used to follow the live CLI. Users are explicitly directed to install globally with `npm install -g @aomi-labs/client@latest` for repeated use, or pin a version in their own environment. The OWASP `permissions.shell` array constrains the skill's actual operational scope to `aomi` and `npx @aomi-labs/client@latest` only. AST08 (Supply-Chain Attacks) above acknowledges that npm package signing / sigstore attestation is open. |

These four findings are inherent to **any** AI agent skill that signs on-chain transactions and reads third-party data. They cannot be eliminated without removing the skill's core capability. The combined posture — explicit risk_tier, OWASP permission manifest, drain-vector guards, simulate-before-sign, no-unsolicited-credential-setup — is what makes the skill safe to use despite these characterizations.

## Reporting issues

Security issues should be reported privately. Open a private security advisory at [https://github.com/aomi-labs/skills/security/advisories/new](https://github.com/aomi-labs/skills/security/advisories/new).
