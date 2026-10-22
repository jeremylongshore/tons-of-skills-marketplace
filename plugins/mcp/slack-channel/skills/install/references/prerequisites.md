# Prerequisites — detailed checks

Reference for the `install` mode's Step 0. Each check has a
deterministic detection command and a copy-pasteable recovery.

## 1. Bun ≥ 1.0

**Detect:**

```bash
bun --version
```

Expected: `1.x.x` or higher. If the command is not found, Bun is not
installed.

**Install:**

```bash
curl -fsSL https://bun.sh/install | bash
```

After install, restart your shell (or `source ~/.bashrc` / `source ~/.zshrc`)
and re-run `bun --version` to confirm.

### Node.js fallback

If the user prefers Node.js (or Bun install fails on their platform):

```bash
node --version    # need ≥ 20.x
```

Then edit `.mcp.json` in the repo root to change the runner:

```diff
- "command": "bun",
- "args": ["server.ts"]
+ "command": "npx",
+ "args": ["tsx", "server.ts"]
```

Run `npm install` (instead of `bun install`) on the next install step.
Performance is ~2× slower than Bun but functionally identical.

### Docker fallback

If neither Bun nor a recent Node is available:

```bash
docker --version  # need ≥ 24.x
docker build -t claude-slack-channel .
```

Edit `.mcp.json`:

```diff
- "command": "bun",
- "args": ["server.ts"]
+ "command": "docker",
+ "args": ["run", "--rm", "-i", "-v", "~/.claude/channels/slack:/state", "claude-slack-channel"]
```

## 2. Claude Code with Channels support

**Detect:**

```bash
claude --version
```

Use a current Claude Code build and confirm that `claude --help` exposes the
`--channels` option. Version `2.1.80` was the original research-preview floor,
not a permanent statement of the current support boundary.

**Upgrade:**

Follow the official install / upgrade path at https://code.claude.com/docs/en/setup.
On most systems:

```bash
# macOS / Linux
curl -fsSL https://claude.ai/install.sh | bash

# Or if installed via npm
npm install -g @anthropic-ai/claude-code@latest
```

Re-check with `claude --version` after upgrading.

## 3. Supported Anthropic authentication and organization policy

**Detect:**

```bash
claude auth status
```

(If the installed build exposes a different auth-status command, trust its
current `--help` output.)

The current Channels contract accepts either a `claude.ai` account or an
Anthropic Console API key. It does not support authentication through Amazon
Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry.

For a `claude.ai` login:

```bash
claude login
```

Complete the browser flow, then confirm the authenticated session. Console API
key users should confirm that Claude Code is using their Console credential.

### Why this matters

On claude.ai Team and Enterprise plans, an Owner must enable Channels under
**Admin settings → Claude Code → Channels**, or deploy
`channelsEnabled: true` in managed settings. Console organizations permit
Channels by default unless managed settings disable them. A policy block can
look like a plugin-registration failure, so check it before rotating Slack
tokens.

## Optional: `jq` (only needed for `doctor` / `repair` modes)

The `doctor` and `repair` modes use `jq` for JSON parsing of Slack API
responses and `access.json` validation. The `install` mode itself does
not need it — skip this if you're only doing a fresh install.

```bash
command -v jq    # confirm whether jq is installed
```

If missing:

```bash
# macOS
brew install jq

# Debian / Ubuntu
sudo apt install jq

# Fedora / RHEL
sudo dnf install jq

# Other: https://jqlang.org/download/
```

## All required checks green? Proceed to Step 1

When the runtime, Channels option, authentication, and organization policy all
report acceptable values, continue to the Slack app creation step.

Authoritative source: [Claude Code Channels](https://code.claude.com/docs/en/channels).
