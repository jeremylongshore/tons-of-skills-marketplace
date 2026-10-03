# Aomi bundle — security posture

The `aomi` plugin bundle ships two skills with materially different risk profiles. This document maps each against the [OWASP Agentic Skills Top 10 (v1.0, March 2026)](https://owasp.org/www-project-agentic-skills-top-10/), records the controls in place, and points reviewers at the captured scanner reports.

**Last reviewed:** 2026-07-05.

## Bundle-level summary

| Skill | Risk tier | Sandbox | Network surface | Shell surface |
|-------|-----------|---------|-----------------|---------------|
| [`aomi-transact`](skills/transact/SKILL.md) | **L2** (signs/broadcasts) | Forked-chain simulation gate before every signing | `chat.aomi.dev` only (allowlist) | `aomi`, `npx @aomi-labs/client@latest` |
| [`aomi-build`](skills/build/SKILL.md) | **L1** (low — scaffolds code, no runtime side effects) | n/a (no execution; output is source code for the user to review) | none (offline) | `cargo`, `git` |

Both skills have full per-control walkthroughs against AST01–AST10 in their respective SECURITY.md files in this repo:

- [`aomi-transact/SECURITY.md`](https://github.com/aomi-labs/skills/blob/main/aomi-transact/SECURITY.md) (when the bundle is what's distributed, this lives at `aomi/skills/transact/SECURITY.md` — see "Migration" below)
- [`aomi-build/SECURITY.md`](https://github.com/aomi-labs/skills/blob/main/aomi-build/SECURITY.md)

For a high-leverage review, start with **`aomi-transact`** — that's where the signing risk lives.

## Captured scanner reports

| Scanner | `aomi-transact` | `aomi-build` |
|---------|----------------|--------------|
| [Cisco AI Defense skill-scanner](https://github.com/cisco-ai-defense/skill-scanner) | **PASS** (0 findings) | **PASS** (0 findings, SAFE) |
| [pors/skill-audit](https://github.com/pors/skill-audit) | **PASS** (0 errors / 4 doc-pattern WARNs) | **PASS** (0 errors / 2 doc-pattern WARNs) |
| [NMitchem/SkillScan](https://github.com/NMitchem/SkillScan) | **PASS** (Risk 2.0/10, 1 upstream-regex-bug HIGH) | **PASS** (Risk 0.0/10, 0 findings) |
| [Snyk agent-scan](https://github.com/snyk/agent-scan) | **PASS (advisory)** — 4 HIGH classifications of intentional risk surface (W007, W009, W011, W012); per-finding mitigations in `aomi-transact/SECURITY.md` | Pending |

Reports live at [`.scanner-reports/`](https://github.com/aomi-labs/skills/tree/main/.scanner-reports) in the repo root.

The CI workflow at [`.github/workflows/skill-audit.yml`](https://github.com/aomi-labs/skills/blob/main/.github/workflows/skill-audit.yml) runs Cisco + pors against **both** skills on every PR and uploads SARIF to the GitHub Security tab.

## Bundle-level hard rules

These apply across every skill in the bundle:

- **No unsolicited credential setup.** The skills never run `aomi wallet set`, `aomi secret add`, `--api-key`, `--private-key`, or any other credential-persisting command on their own initiative — only when the user has explicitly asked for that specific setup *in the current turn* and supplied the value themselves.
- **No echoing credential values.** Confirmation is by handle name or derived address only, never by repeating the value.
- **No system-prompt manipulation.** The bundle does not attempt to override agent behavior or inject instructions into the agent's identity files (`SOUL.md`, `MEMORY.md`, `AGENTS.md` are in every skill's `permissions.files.deny_write`).
- **No drain-vector bypass.** When the agent rejects calldata where `recipient`/`onBehalfOf`/`mintRecipient` ≠ `msg.sender`, `aomi-transact` surfaces the block to the user rather than reformulating the prompt. See [`skills/transact/references/drain-vectors.md`](skills/transact/references/drain-vectors.md).

## Migration note

This SECURITY.md is the bundle-level summary. The two skills also ship per-skill SECURITY.md files at `skills/transact/SECURITY.md` and `skills/build/SECURITY.md` once the bundle is fully wired (currently those live alongside the SKILL.mds at the legacy `aomi-transact/` and `aomi-build/` repo roots — kept there for backwards compatibility while consumers migrate).

## Reporting issues

Security issues should be reported privately. See the top-level `SECURITY.md` in `aomi-labs/skills` for the disclosure process, or open a private security advisory on the GitHub repo.
