# pr-to-spec

**The flight envelope for agentic coding.**

CodeRabbit reviews for humans. `pr-to-spec` converts for agents.

Turn any code change — a GitHub PR, a local branch, staged edits — into a structured, agent-consumable spec with intent drift detection. CLI *and* MCP server — use it from the terminal or as a plugin in Claude Code, Cursor, and Windsurf.

[![CI](https://github.com/jeremylongshore/pr-to-prompt/actions/workflows/ci.yml/badge.svg)](https://github.com/jeremylongshore/pr-to-prompt/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Gist: One-Pager & Audit](https://img.shields.io/badge/gist-one--pager%20%26%20audit-blue)](https://gist.github.com/jeremylongshore/5b2de7ba9baca1eaaa0a757b5b0c48db)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jeremylongshore.github.io/pr-to-prompt/)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U5S225PTME)

---

## What It Does

```
declare intent → make changes → pr-to-spec check → agent sees clean/drift/high-risk
```

1. **Declare intent**: Tell `pr-to-spec` what you're building, what scope is allowed, and your risk ceiling
2. **Make changes**: Work normally in your branch
3. **Check drift**: `pr-to-spec check --json` produces a structured spec + drift signals
4. **Agent consumes**: Any agent reads the envelope and acts accordingly

---

## Quick Start

### Local Diff (no GitHub needed)

```bash
# Analyze your current branch vs main
pr-to-spec scan --branch main --json

# Analyze staged changes only
pr-to-spec scan --staged --json

# Analyze last 3 commits
pr-to-spec scan --diff 3 --json
```

### Intent + Drift Detection

```bash
# 1. Declare what this change is supposed to do
pr-to-spec intent set \
  --goal "Add rate limiting to API" \
  --scope "src/middleware/**" \
  --forbid "src/db/**" \
  --max-risk medium \
  --type feature

# 2. After making changes, check for drift
pr-to-spec check --json
# exit 0 = clean, exit 2 = high-risk, exit 3 = drift detected

# Show current intent
pr-to-spec intent show
```

### GitHub PR Analysis

```bash
# Analyze a GitHub PR
pr-to-spec --repo owner/repo --pr 42 --json | your-agent review

# Extract just the risk flags
pr-to-spec --repo owner/repo --pr 42 --json | jq '.spec.risk_flags'

# Feed to Claude for review
pr-to-spec --repo owner/repo --pr 42 --json \
  | claude --print "Review this spec and decide: approve, request changes, or needs info"
```

---

## MCP Server

pr-to-spec ships an MCP server for IDE integration. When installed as a Claude Code plugin, these tools are available automatically.

### Tools

| Tool | Description |
|------|-------------|
| `analyze_pr` | Analyze a GitHub PR and generate a structured spec |
| `scan_local` | Scan local git changes (branch, staged, commits) |
| `check_drift` | Check changes against declared intent for drift |
| `set_intent` | Declare what a code change should accomplish |
| `show_intent` | Show the current intent declaration |
| `analyze_assumptions` | Surface implicit decisions with 2x2 matrix |

### Plugin Installation

Install the skill with the official skills CLI:

```bash
npx skills add jeremylongshore/pr-to-prompt --skill pr-to-spec
```

To load both the skill and bundled MCP server from a checkout, run Claude Code
with `--plugin-dir /path/to/pr-to-prompt`. Or add the bundled server to your
project's `.mcp.json` and expose `GITHUB_TOKEN` in the server environment:

```json
{
  "mcpServers": {
    "pr-spec-analyzer": {
      "command": "node",
      "args": ["/path/to/pr-to-prompt/dist/mcp-bundle/index.js"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

---

## Agent Protocol

All `--json` output is wrapped in the agent protocol envelope:

```json
{
  "version": 1,
  "command": "check",
  "status": "drift_detected",
  "exit_code": 3,
  "signals": [
    {
      "type": "forbidden_touch",
      "description": "1 forbidden file(s) modified",
      "severity": "high",
      "details": ["src/db/schema.ts"]
    }
  ],
  "spec": { ... },
  "intent": { ... }
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Clean — no issues |
| `1` | Error |
| `2` | High-risk changes detected |
| `3` | Drift from declared intent |
| `4` | Gate policy failed |

### Drift Signals

| Signal | Trigger |
|--------|---------|
| `scope_creep` | Files changed outside `expected_scope` |
| `forbidden_touch` | Files matching `forbidden_scope` were modified |
| `risk_escalation` | Detected risk level exceeds `max_risk` |
| `size_overrun` | Total LOC changed exceeds `size_budget` |
| `type_mismatch` | Inferred change type doesn't match `expected_type` |

---

## CLI Reference

### `pr-to-spec` (analyze a GitHub PR)

```
Options:
  --repo <owner/name>      GitHub repository (required)
  --pr <number>            Pull request number (required)
  --out <directory>        Output directory (default: ./output)
  --token <token>          GitHub token (or set GITHUB_TOKEN env var)
  --format <format>        Output: yaml, markdown, json, both (default: both)
  --stdout                 Print to stdout instead of files
  --quiet                  Suppress logging
  --field <path>           Extract a single field (dot notation)
  --json                   Shorthand for --format json --stdout --quiet
  --comment                Post spec summary as a PR comment
  --ai-enhance             Enhance spec with AI-generated insights
  --debug                  Log API requests, git commands, and timing
  -V, --version            Show version
  -h, --help               Show help
```

### `pr-to-spec scan` (analyze local changes)

```
Options:
  --branch <ref>           Base branch to diff against (default: main)
  --diff <n>               Diff last N commits
  --staged                 Analyze staged changes only
  --out <directory>        Output directory (default: ./output)
  --format <format>        Output: yaml, markdown, json, both
  --stdout                 Print to stdout
  --quiet                  Suppress logging
  --json                   Shorthand for --format json --stdout --quiet
  --field <path>           Extract a single field
```

### `pr-to-spec intent` (manage intent declaration)

```
Subcommands:
  set                      Set the intent for this project
  show                     Show the current intent
  analyze                  Analyze assumptions and surface decisions
  approve                  Approve the current intent (draft → approved)
  lock                     Lock the current intent (approved → locked)
  gate                     Evaluate intent gate policy

intent set Options:
  --goal <text>            What this change is trying to achieve (required)
  --scope <glob...>        Expected file globs (repeatable)
  --forbid <glob...>       Forbidden file globs (repeatable)
  --max-risk <level>       Maximum acceptable risk: low, medium, high
  --type <type>            Expected change type: feature, bugfix, refactor, etc.
  --size-budget <n>        Max total lines changed
  --json                   Output as JSON
```

### `pr-to-spec check` (drift detection)

```
Options:
  --branch <ref>           Base branch to diff against
  --diff <n>               Diff last N commits
  --staged                 Analyze staged changes only
  --quiet                  Suppress logging
  --json                   Output as JSON agent protocol envelope
```

### `pr-to-spec contract` (verification contracts)

```
Subcommands:
  add                      Add a new contract
  list                     List all contracts
  remove                   Remove a contract by ID

contract add Options:
  --type <type>            Contract type (required)
  --description <text>     Contract description
  --params <json>          Contract parameters as JSON
  --severity <level>       blocking or warning (default: blocking)
  --json                   Output as JSON

Contract types: no_new_dependencies, no_file_outside_scope,
  max_files_changed, no_pattern_in_diff, require_pattern_in_diff,
  no_new_exports
```

### `pr-to-spec graph` (intent DAG)

```
Subcommands:
  query                    Query ancestors or descendants of a node
  impact                   Show nodes impacted by changes
  stats                    Show graph statistics

graph query Options:
  --node <id>              Node ID to query (required)
  --direction <dir>        up (ancestors) or down (descendants)
  --json                   Output as JSON
```

### `pr-to-spec feedback` (review/CI feedback)

```
Subcommands:
  review                   Ingest a code review result
  ci                       Ingest CI pipeline results
  status                   Show current feedback and graph status

feedback review Options:
  --reviewer <name>        Reviewer name (required)
  --status <status>        approved, changes_requested, commented (required)
  --comment <text...>      Review comments (repeatable)
  --target <id...>         Target node IDs (required)
  --json                   Output as JSON
```

---

## GitHub Action

```yaml
# .github/workflows/pr-to-spec.yml
name: PR to Spec
on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  generate-spec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate spec
        id: spec
        uses: jeremylongshore/pr-to-prompt@main
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          INPUT_COMMENT: "true"
          INPUT_FORMAT: "both"

      - uses: actions/upload-artifact@v4
        with:
          name: prompt-spec-pr-${{ github.event.pull_request.number }}
          path: .pr-to-spec/specs/
```

---

## Risk Classification

Built-in heuristic rules flag changes to:

| Category | Severity | Triggers |
|----------|----------|----------|
| `authentication` | **high** | Auth, login, session, OAuth, JWT files |
| `secrets` | **high** | .env, .key, .pem, credentials files |
| `database` | **high** | Migrations, .sql, schema files |
| `permissions` | **high** | RBAC, ACL, policy files |
| `payment` | **high** | Stripe, billing, subscription files |
| `dependencies` | medium | Lockfiles, package managers |
| `infrastructure` | medium | Docker, Terraform, k8s, deploy configs |
| `destructive-operations` | medium | DROP TABLE, DELETE FROM in patches |
| `security-config` | medium | CORS, CSP, security headers |
| `large-change` | low | 300+ line changes in a single file |

---

## Architecture

```
src/
  servers/        MCP server (6 tools via stdio transport)
  cli/            CLI entrypoints (analyze, scan, intent, check)
  action/         GitHub Action entrypoint
  core/
    schema/       Zod schema for the canonical prompt-spec format
    github/       Octokit-based PR data fetching
    sources/      DiffSource abstraction (GitHub PR, local branch, staged, commits)
    parsing/      Deterministic spec generation from diff metadata
    risk/         Rule-based risk classification heuristics
    intent/       Intent schema and YAML storage (.pr-to-spec/intent.yaml)
    drift/         Drift detection against declared intent
    protocol/     Agent protocol envelope (version, status, exit_code)
    rendering/    YAML, Markdown, JSON, and PR comment renderers
    ai/           Optional AI enhancement (Anthropic, OpenAI)
    diff/         Spec version diffing
```

### Design Principles

- **Deterministic first**: Core spec uses heuristics, not LLMs. Reproducible and auditable.
- **No execution**: Never runs code — metadata and diffs only.
- **Agent-native**: JSON envelope output, clean exit codes, field extraction. Built for piping.
- **Local-first**: Works on local branches and staged changes without GitHub.
- **Minimal trust surface**: Read-only by default. Zod-validated output.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | For GitHub PRs | GitHub token with PR read access |
| `ANTHROPIC_API_KEY` | No | For AI-enhanced summaries |
| `OPENAI_API_KEY` | No | Alternative AI provider |
| `PR_TO_SPEC_DIR` | No | Config directory (default: `.pr-to-spec`) |

---

## Troubleshooting

**"GitHub token is invalid or expired"**
Your `GITHUB_TOKEN` has expired or is malformed. Generate a new one with `repo` scope (or fine-grained: pull requests read access).

**"PR #N not found in owner/repo"**
The PR doesn't exist, or your token doesn't have access to this repo. Check the repo name (`owner/name`) and PR number.

**"GitHub API rate limit exceeded"**
You've hit the GitHub API rate limit. Wait for the reset time shown in the error, or use a token with higher limits.

**"Not a git repository"**
Run `pr-to-spec scan` or `pr-to-spec check` from inside a git repository. For GitHub PRs, use `--repo` and `--pr` instead.

**"Branch or ref 'X' not found"**
The branch you specified with `--branch` doesn't exist locally. Check with `git branch -a`.

**"PR has 300+ files; results may be incomplete"**
GitHub's API returns at most 300 files per page. Very large PRs may have truncated file lists.

---

## Development

```bash
pnpm install       # Install dependencies
pnpm build         # Compile TypeScript
pnpm test          # Run tests
pnpm lint          # Lint with Biome
pnpm typecheck     # TypeScript strict check
pnpm check         # All of the above
pnpm dev           # Watch mode
```

## License

MIT — see [LICENSE](./LICENSE).
