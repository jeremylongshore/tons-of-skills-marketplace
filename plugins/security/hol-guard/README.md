# HOL Guard for tons-of-skills-marketplace

This directory is the review-scoped HOL Guard payload for `jeremylongshore/tons-of-skills-marketplace`. It is intentionally a non-executable manifest, skills, documentation, and license payload so the marketplace mirrors a small, auditable install surface while the actual security CLIs remain independently published packages.

## Admitted files

The payload contains only:

- `.claude-plugin/plugin.json`
- `skills/hol-guard/SKILL.md`
- `skills/plugin-scanner/SKILL.md`
- `README.md`
- `LICENSE`

It contains no hooks, MCP manifests, executable helper scripts, package lifecycle scripts, background daemons, telemetry setup, OAuth flow, or hosted-service dependency.

## Runtime boundary

HOL Guard itself is installed separately from the user's configured Python package index. The review-scoped Guard skill pins the local runtime to:

```bash
pipx install hol-guard==3.0.46
```

The pre-install scanning skill uses the separately published `plugin-scanner` CLI pinned to the exact package version reviewed for this payload:

```bash
pipx install plugin-scanner==3.0.123
```

Installation is offered only after the user asks for the relevant workflow or explicitly approves installation. The skills keep enforcement and scanning in the published local CLIs rather than reimplementing security policy in marketplace content.

The default workflow is local-first. It does not require a Hashgraph Online account, API key, hosted service, or remote policy endpoint. Workspace contents, prompts, package names, URLs, Guard findings, scanner findings, and approval data are not sent to a hosted HOL service by this payload.

## What the skills do

The included `hol-guard` skill guides supported local agent harnesses such as Claude Code, Codex, Copilot CLI, Cursor, Gemini CLI, Hermes, OpenClaw, OpenCode, and Antigravity through Guard status inspection, harness detection, protection setup, dry-run validation, approval review, receipts, and post-install verification. It does not duplicate Guard enforcement logic. A user-facing security decision remains the output of the installed HOL Guard runtime.

The included `plugin-scanner` skill provides the promised pre-install scanning workflow for AI agent skills, plugins, MCP servers, packages, and repositories. It delegates scanning to the local `plugin-scanner` CLI and does not execute the target being inspected.

## Source

- Runtime source: https://github.com/hashgraph-online/hol-guard
- HOL Guard package: https://pypi.org/project/hol-guard/
- Plugin Scanner package: https://pypi.org/project/plugin-scanner/
- Distribution source: https://github.com/hashgraph-online/hol-guard-plugin
