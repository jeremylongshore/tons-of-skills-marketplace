---
name: hol-guard
description: Protects local AI coding-agent workflows with HOL Guard pre-execution controls, approvals, receipts, and verification. Use when enabling Guard for a supported local harness, reviewing a Guard block, or validating protection before trusted tool execution. Trigger with "hol guard", "protect this workspace", "review guard approvals", or "check guard status".
allowed-tools: "Bash(hol-guard status:*) Bash(hol-guard detect:*) Bash(hol-guard bootstrap:*) Bash(hol-guard install:*) Bash(hol-guard run:*) Bash(hol-guard approvals:*) Bash(hol-guard receipts:*) Bash(pipx install hol-guard==3.0.46)"
version: 0.1.2
author: Hashgraph Online
license: Apache-2.0
compatibility: Supports local harness workflows including Claude Code, Codex, Copilot CLI, Cursor, Gemini CLI, Hermes, OpenClaw, OpenCode, and Antigravity; requires a local Python CLI environment with pipx for optional HOL Guard installation.
tags: [security, ai-agents, approvals, local-first, supply-chain]
---

# HOL Guard

## Overview

HOL Guard is a local security boundary for AI coding-agent tool execution. This skill uses the published `hol-guard` CLI rather than implementing a second policy engine inside the marketplace. It is intended for workspaces where a user wants Guard-owned pre-execution checks, supported harness installation, approval review, receipts, or evidence that protection is active before an agent continues with trusted tool execution.

The normal path stays local. The skill does not require a Hashgraph Online account, API key, hosted service, or remote decision endpoint. It does not send workspace contents, prompts, package names, URLs, Guard findings, or approval data to a hosted HOL service. Harness configuration changes are made only by explicit `hol-guard` commands after the user requests protection.

## Prerequisites

- A local workspace chosen by the user.
- `pipx` when HOL Guard needs to be installed.
- A supported harness such as Claude Code, Codex, Copilot CLI, Cursor, Gemini CLI, Hermes, OpenClaw, OpenCode, or Antigravity.
- User approval before installing software or changing harness protection.

Never read `.env` files, credential stores, private keys, or unrelated secrets. Never bypass a Guard approval. Preserve existing workspace changes and do not edit harness or repository configuration manually to work around Guard.

## Instructions

1. **Inspect current Guard state.** Run `hol-guard status`. If the command is unavailable, do not silently alter the Python environment. Explain that HOL Guard is missing and offer the pinned local installation only when the user asked for setup or explicitly approves it:

   ```bash
   pipx install hol-guard==3.0.46
   ```

2. **Detect the local harness.** After HOL Guard is available, inspect supported harness state with:

   ```bash
   hol-guard detect --json
   ```

   Use the detected harness when it matches the user's intended tool. Common supported names include `claude-code`, `codex`, `copilot`, `cursor`, `gemini`, `hermes`, `openclaw`, `opencode`, and `antigravity`.

3. **Preview protection before applying it.** When the user asked to protect a harness, run the Guard-owned setup and dry-run path rather than editing harness configuration manually:

   ```bash
   hol-guard bootstrap
   hol-guard install <harness>
   hol-guard run <harness> --dry-run
   ```

   Inspect the dry-run output. Do not claim the workspace is protected merely because installation returned without an obvious error.

4. **Apply the protected run only after the preview is understood.** When the user requested execution and the dry-run is acceptable:

   ```bash
   hol-guard run <harness>
   hol-guard status
   ```

   Treat the final `hol-guard status` result as the evidence for whether protection is active.

5. **Handle blocks and approvals through Guard.** When Guard blocks, reviews, or queues an action, inspect the Guard-owned approval surface instead of bypassing it:

   ```bash
   hol-guard approvals
   hol-guard receipts
   ```

   If the user explicitly asks to resolve a specific approval, read the Guard reason and scope first. Use Guard's approval commands only after the requested action and risk are understood.

6. **Return evidence, not a generic safety claim.** Report the harness, the Guard status, any relevant approval or block reason, and the verification command that produced the result. A successful status check proves the observed Guard state; it does not prove that every possible tool, plugin, package, or prompt is safe.

## Output

Return a concise result containing:

- the workspace or harness inspected;
- whether `hol-guard` was already available or installed with user approval;
- the detected harness and protection status;
- the dry-run or final status evidence used to support the conclusion;
- any Guard block, review, approval, or receipt that materially affects the requested action;
- the next Guard-owned action, if one is still required.

Use precise language such as "HOL Guard reports protection active for the selected harness" rather than broad claims such as "the workspace is safe."

## Error Handling

If `hol-guard` is missing, stop before protection commands and offer the pinned `pipx` installation only when installation is within the user's request. If `pipx` is unavailable, recommend an isolated Python CLI installation approach rather than silently modifying the system Python environment.

If detection is ambiguous, report the detected candidates and do not guess a harness. If `hol-guard install`, the dry-run, or the protected run fails, preserve the failure output needed for diagnosis and do not edit harness configuration around Guard to force success. If Guard returns a block, review requirement, unknown decision, or approval request, treat it as a real security decision until the user reviews it through Guard.

If a repository already contains unrelated local changes, preserve them. Do not reset, discard, or overwrite user work in order to make Guard setup cleaner.

## Examples

**Protect a supported harness in the current workspace**

Input: `protect this workspace with hol guard`

Workflow:

```bash
hol-guard status
hol-guard detect --json
hol-guard bootstrap
hol-guard install <harness>
hol-guard run <harness> --dry-run
hol-guard run <harness>
hol-guard status
```

Output: report the final protection state for the selected harness and any Guard-owned changes or warnings shown by the commands.

**Review a Guard block**

Input: `why did hol guard stop that command?`

Workflow:

```bash
hol-guard approvals
hol-guard receipts
```

Output: identify the relevant Guard decision, its reason and scope, and whether an explicit user approval or denial is still pending. Do not override the decision automatically.

**Check protection without changing configuration**

Input: `check guard status`

Workflow:

```bash
hol-guard status
hol-guard detect --json
```

Output: report only the observed local state. Do not install or mutate anything when the user asked for a check.

## Resources

- HOL Guard source: https://github.com/hashgraph-online/hol-guard
- HOL Guard package: https://pypi.org/project/hol-guard/
- Distribution source: https://github.com/hashgraph-online/hol-guard-plugin
