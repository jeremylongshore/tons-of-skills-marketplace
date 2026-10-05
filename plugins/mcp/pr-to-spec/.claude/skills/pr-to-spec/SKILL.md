---
name: pr-to-spec
description: Analyze code changes and detect intent drift with the pr-to-spec CLI, converting a branch, staged edits, recent commits, or a GitHub pull request into an agent-consumable spec. Use when declaring intent before a change, checking completed work for drift, or producing review evidence. Trigger with "/pr-to-spec", "scan this diff", "check intent drift", or "declare change intent".
version: 0.8.1
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires Node.js 20+, the pr-to-spec CLI on PATH, and a Git repository; remote pull-request analysis also requires GitHub read access.
tags: [git, pr, spec, intent-drift, code-review, agent-protocol]
argument-hint: "[scan | check | intent set | intent show]"
allowed-tools: ["Bash(pr-to-spec:*)", "Bash(git:*)"]
model: inherit
effort: high
---

# pr-to-spec

## Overview

Turn observed code changes into a versioned JSON spec and compare them with a
declared intent. Lead with the outcome and supporting signals, risks, contracts,
and policy evidence; never treat a nonzero gate exit as an ordinary CLI failure.

## Prerequisites

- Run inside the Git repository being analyzed with Node.js 20+ and
  `pr-to-spec` on `PATH`.
- Fetch the intended base ref before branch comparison if the local ref may be
  stale.
- For remote PR analysis, provide `GITHUB_TOKEN` through the environment. Prefer
  a fine-grained token with pull-request read access; do not pass tokens on the
  command line or print them.
- Treat `.pr-to-spec/intent.yaml`, `contracts.yaml`, and `policy.yaml` as project
  governance state. Review changes before committing them.

## Instructions

### Step 1: Declare intent before editing

Quote globs so the shell does not expand them:

```bash
pr-to-spec intent set \
  --goal "Add rate limiting to the API" \
  --scope "src/middleware/**" \
  --forbid "src/db/**" \
  --max-risk medium \
  --json
pr-to-spec intent show --json
```

Add `--type` or `--size-budget` when they express a real acceptance boundary.
Do not broaden intent after a drift result merely to make the gate pass.

### Step 2: Select one local comparison

Use one comparison mode and request JSON for deterministic agent parsing:

```bash
pr-to-spec scan --branch main --json
pr-to-spec scan --staged --json
pr-to-spec scan --diff 3 --json
```

`--staged` takes precedence, then `--diff`; otherwise the CLI compares the
current branch with `--branch` or `main`. A scan can exit `2` when high-risk
changes are found even though it produced a valid spec.

For a GitHub pull request, use the root command:

```bash
pr-to-spec --repo OWNER/REPO --pr 42 --json
```

Set the token in the calling environment without echoing it.

### Step 3: Check completed work

Run the same comparison boundary used for the scan:

```bash
pr-to-spec check --branch main --json
```

Expected result: a versioned envelope whose exit code distinguishes clean,
high-risk, drift, policy failure, and runtime error states.

If no intent exists, `check` falls back to scan behavior and returns `0` or `2`.
With intent, it evaluates drift, verification contracts, and any policy gate.
Read the JSON `status`, `signals`, `gate_result`, and `contracts` fields before
deciding whether work may continue.

### Step 4: Respond to the gate

- `0`: clean for the evaluated boundary.
- `2`: valid result with high-risk changes; review risk flags.
- `3`: drift or a blocking contract violation; fix the change or deliberately
  revise intent with an explicit explanation.
- `4`: policy gate failed; satisfy its blocking checks.
- `1`: invocation, Git, configuration, or runtime error; repair and rerun.

Never collapse codes `2`–`4` into a generic failure because each requires a
different response.

## Output

JSON output uses the versioned agent-protocol envelope:

```json
{
  "version": 1,
  "command": "check",
  "status": "drift_detected",
  "exit_code": 3,
  "signals": [],
  "spec": {},
  "intent": {}
}
```

Report the comparison boundary, exit code and meaning, changed-file summary,
highest risk, each drift signal, contract and gate results, and the next safe
action. Preserve the JSON with review evidence when it gates a release.

## Error Handling

- Missing base ref: fetch or choose an existing ref; verify with `git branch -a`.
- No changes: confirm the selected branch, staged set, or commit count.
- No intent: declare one for drift checking, or state that check used scan-only
  behavior.
- Exit `2`, `3`, or `4`: parse the emitted envelope before remediation.
- Remote authentication failure: validate repository access and token scope
  without logging the token.
- Malformed governance YAML: repair the named `.pr-to-spec` file and rerun.

## Examples

```bash
pr-to-spec intent set --goal "Refactor cache keys" \
  --scope "src/cache/**" --forbid "src/auth/**" --max-risk low --json
pr-to-spec check --branch main --json
```

```bash
pr-to-spec scan --staged --field intent.change_type --stdout
```

Expected result: only the inferred change type for the staged diff.

## Resources

- [CLI contract, state, and security boundaries](references/cli-contract.md)
- [Repository README](https://github.com/jeremylongshore/pr-to-prompt/blob/main/README.md)
- [Documentation site](https://jeremylongshore.github.io/pr-to-prompt/)
- [Examples](https://github.com/jeremylongshore/pr-to-prompt/tree/main/examples)
