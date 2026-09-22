---
name: windsurf-performance-tuning
description: 'Optimize Devin Desktop (formerly Windsurf) IDE performance: indexing speed, Cascade responsiveness,
  and memory usage.

  Use when Windsurf is slow, indexing takes too long, Cascade times out,

  or the IDE uses too much memory.

  Trigger with phrases like "windsurf slow", "windsurf performance",

  "optimize windsurf", "windsurf memory", "cascade slow", "indexing slow".

  '
allowed-tools: Read, Write, Edit, Grep
argument-hint: "[scope or requirements]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- windsurf
- performance
- indexing
- optimization
compatibility: Designed for Claude Code
---
# Windsurf Performance Tuning

## Overview

Optimize Windsurf's indexing engine, Cascade context building, Supercomplete latency, and overall IDE responsiveness. Most performance issues stem from indexing too many files or missing exclusion patterns.

## Prerequisites

- Windsurf IDE installed
- Understanding of workspace indexing
- Access to Windsurf settings

Capture a repeatable latency or indexing symptom before changing exclusions, extensions, workspace scope, or editor settings.

## Tool Use

- Use `Read` to inspect only the repository files and configuration needed for the request.
- Use `Grep` to locate relevant settings, rules, logs, or code without broad collection.
- Use `Write` only for a new artifact the user requested; never write credentials or unreviewed production configuration.
- Use `Edit` for bounded, reviewable changes and preserve unrelated user work.

## Instructions

### Step 1: Optimize Workspace Indexing

The indexing engine is the #1 performance factor. Exclude everything that isn't source code:

```gitignore
# .codeiumignore — aggressive exclusion for large codebases
# Build artifacts
node_modules/
dist/
build/
.next/
.nuxt/
.output/
.svelte-kit/
coverage/
.cache/

# Package manager
pnpm-lock.yaml
package-lock.json
yarn.lock

# Generated code
*.min.js
*.min.css
*.bundle.js
*.chunk.js
**/*.map
generated/
__generated__/

# Binary and media files
*.png
*.jpg
*.gif
*.svg
*.ico
*.mp4
*.woff
*.woff2
*.ttf
*.eot

# Data files
*.sqlite
*.db
*.sql.gz
*.csv

# Python
__pycache__/
*.pyc
.venv/
venv/
.tox/
*.egg-info/

# Go
vendor/

# Rust
target/
```

### Step 2: Open Focused Workspaces

```
# DON'T: Open entire monorepo root
windsurf ~/monorepo/          # Indexes ALL packages = slow

# DO: Open specific service directories
windsurf ~/monorepo/apps/web/        # Only indexes web app
windsurf ~/monorepo/packages/api/    # Only indexes API

# Each Windsurf window gets its own focused AI context
# Cascade performs better with fewer, relevant files
```

### Step 3: Tune IDE Settings

```json
// settings.json — performance-focused configuration
{
  // Indexing limits
  "codeium.indexing.maxFileSize": 524288,

  // Reduce extension overhead
  "extensions.autoUpdate": false,
  "extensions.autoCheckUpdates": false,

  // Editor performance
  "editor.minimap.enabled": false,
  "editor.renderWhitespace": "none",
  "editor.bracketPairColorization.enabled": false,

  // File watcher optimization
  "files.watcherExclude": {
    "**/node_modules/**": true,
    "**/dist/**": true,
    "**/.git/objects/**": true,
    "**/build/**": true
  },

  // Search exclusions
  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/coverage": true,
    "**/*.min.js": true
  }
}
```

### Step 4: Optimize Cascade Usage

```markdown
## Cascade Performance Tips

1. Start fresh sessions for new tasks
   - Long conversations accumulate context, slowing responses
   - Click + in Cascade panel to start new conversation

2. Use @ mentions instead of describing files
   - BAD: "Look at the auth service file"
   - GOOD: "@src/services/auth.ts fix the token refresh logic"

3. Scope prompts narrowly
   - BAD: "Refactor the authentication system"
   - GOOD: "Extract JWT validation from src/middleware/auth.ts into src/services/jwt.ts"

4. Use Chat mode for questions, Code mode for edits
   - Chat mode is lighter — doesn't build full edit context
   - Switch modes based on intent

5. Choose the right model for the task
   - A currently available SWE-family model: routine work at lower or no quota cost when labeled free
   - SWE-1: standard coding tasks
   - SWE-1.5 / Claude: complex multi-file tasks (worth the wait)
```

### Step 5: Memory Management

```markdown
## Reduce Memory Usage

1. Close unused editor tabs
   - Each open file adds to memory footprint
   - Cmd/Ctrl+K Cmd/Ctrl+U: close unused tabs

2. Limit extensions
   - Each extension consumes memory
   - Disable extensions you don't actively use
   - Check: Extensions > "@enabled" to review

3. Disable unused Supercomplete languages
   - Settings > codeium.autocomplete.languages
   - Disable for languages you don't write

4. Monitor process memory
   - Help > Open Process Explorer
   - Look for extensions consuming >200MB
```

### Step 6: Benchmark Your Setup

```bash
#!/bin/bash
set -euo pipefail
echo "=== Windsurf Performance Check ==="

# Workspace size
FILE_COUNT=$(find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' | wc -l)
echo "Indexed files: ~$FILE_COUNT"

# Config status
echo "Has .codeiumignore: $([ -f .codeiumignore ] && echo 'YES' || echo 'NO (SLOW!)')"
IGNORE_LINES=$(wc -l < .codeiumignore 2>/dev/null || echo 0)
echo "Ignore patterns: $IGNORE_LINES"

# Recommendations
if [ "$FILE_COUNT" -gt 5000 ]; then
  echo "WARNING: >5000 files. Add more patterns to .codeiumignore"
fi
if [ "$IGNORE_LINES" -lt 5 ]; then
  echo "WARNING: Few ignore patterns. Add build artifacts, binaries, lock files"
fi
```

## Output

Return a before-and-after performance record with workspace size, indexing boundaries, memory and CPU observations, configuration changes, measured improvement, and rollback instructions. Label conclusions as measured, inferred, or still unverified.

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| Indexing never completes | Too many files | Add `.codeiumignore`, open subdirectory |
| Cascade timeout | Complex prompt + large context | Narrow scope, start fresh session |
| High memory usage | Too many extensions/tabs | Close tabs, disable unused extensions |
| Supercomplete lag | Large file open | Split large files, add to maxFileSize limit |
| IDE freezes | Extension conflict | Safe Mode: `windsurf --disable-extensions` |

## Examples

### Quick Performance Fix

```bash
# Create minimal .codeiumignore if missing
[ -f .codeiumignore ] || cat > .codeiumignore << 'EOF'
node_modules/
dist/
build/
.next/
coverage/
*.min.js
*.map
EOF
```

### Reset Indexing

```
Command Palette (Cmd/Ctrl+Shift+P):
Use the current indexing reset control in Devin Desktop Settings after downloading diagnostics.
```

## Resources

- [Focused first-party references](references/official-docs.md)
- [Windsurf Context Awareness](https://docs.devin.ai/desktop/context-awareness/overview)
- [Windsurf Ignore](https://docs.devin.ai/desktop/context-awareness/windsurf-ignore)
- [Autocomplete Tips](https://docs.devin.ai/desktop/autocomplete/tips)

## Related Skill

Continue with `windsurf-cost-tuning` to connect performance findings with seat allocation, quota consumption, and approved extra-usage budgets.
