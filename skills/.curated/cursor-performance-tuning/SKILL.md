---
name: cursor-performance-tuning
description: 'Optimize Cursor IDE performance: reduce memory usage, speed up indexing,
  tune AI features, and manage

  extensions for large codebases. Triggers on "cursor performance", "cursor slow",
  "cursor optimization",

  "cursor memory", "speed up cursor", "cursor lag".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- performance
compatibility: Designed for Claude Code
---
# Cursor Performance Tuning

## Overview

Improve Cursor responsiveness by measuring indexing scope, resource use, extension load, and network conditions while preserving required workspace and data controls.

## Prerequisites

- A reproducible performance symptom, baseline measurement, and approved local settings backup.
- A reviewed `.cursorignore` strategy; do not expose excluded files to gain speed.

## Instructions

1. Measure startup, indexing, memory, and request latency for the affected workspace.
2. Reduce unnecessary roots, extensions, and generated-file indexing before clearing caches.
3. Make one reversible change, compare against baseline, and retain the setting only when it improves the agreed metric.
4. Back up settings before cache maintenance and test the restored workspace afterward.

## Output

- A measured, reversible performance change with before/after evidence.

## Error Handling

| Condition | Safe response |
|---|---|
| Cache clear does not help | Restore settings and investigate extension/indexing scope rather than repeating deletion. |
| Performance requires policy exception | Keep policy intact and escalate for a documented decision. |
| Network latency is the cause | Use approved network troubleshooting; do not route code through an unapproved service. |

## Examples

For a slow monorepo, measure indexing time, add generated artifacts to the existing reviewed ignore rules, close inactive workspace roots, and measure again. Keep the change only if it improves the baseline without hiding required source or documentation.

Diagnose and fix Cursor IDE performance issues. Covers editor optimization, indexing tuning, extension auditing, AI feature configuration, and strategies for large codebases.

## Performance Diagnostic Workflow

```
Step 1: Identify bottleneck
         ├── Editor lag? → Step 2 (Editor settings)
         ├── High CPU?   → Step 3 (Extension audit)
         ├── Slow AI?    → Step 4 (AI tuning)
         └── Memory?     → Step 5 (Memory management)

Step 2: Editor settings
         ├── Disable minimap, breadcrumbs
         ├── Reduce file watcher scope
         └── Increase memory limits

Step 3: Extension audit
         ├── Profile running extensions
         ├── Disable heavy extensions
         └── Use workspace-scoped disabling

Step 4: AI feature tuning
         ├── Optimize .cursorignore
         ├── Use faster models
         └── Manage chat history

Step 5: Memory management
         ├── Close unused workspace folders
         ├── Limit open editor tabs
         └── Clear caches
```

## Editor Optimization

### settings.json Performance Settings

```json
{
  // Disable visual features for speed
  "editor.minimap.enabled": false,
  "editor.renderWhitespace": "none",
  "editor.guides.bracketPairs": false,
  "breadcrumbs.enabled": false,
  "editor.occurrencesHighlight": "off",
  "editor.matchBrackets": "never",
  "editor.folding": false,
  "editor.glyphMargin": false,

  // Reduce file watching scope
  "files.watcherExclude": {
    "**/node_modules/**": true,
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/dist/**": true,
    "**/build/**": true,
    "**/coverage/**": true,
    "**/.next/**": true,
    "**/target/**": true
  },

  // Exclude from search and explorer
  "files.exclude": {
    "**/node_modules": true,
    "**/.git": true,
    "**/dist": true,
    "**/build": true
  },

  // Memory limits
  "files.maxMemoryForLargeFilesMB": 4096,

  // Reduce auto-save overhead
  "files.autoSave": "onFocusChange",

  // Limit search results
  "search.maxResults": 5000
}
```

### Disable Animations

```json
{
  "workbench.list.smoothScrolling": false,
  "editor.smoothScrolling": false,
  "editor.cursorSmoothCaretAnimation": "off",
  "terminal.integrated.smoothScrolling": false
}
```

## Extension Audit

### Profile Running Extensions

`Cmd+Shift+P` > `Developer: Show Running Extensions`

This shows:

- Extension name
- Activation time (ms)
- Profile CPU time

Sort by activation time. Extensions taking > 500ms are worth investigating.

### Process Explorer

`Cmd+Shift+P` > `Developer: Open Process Explorer`

Shows per-process CPU and memory usage:

- Main window
- Extension host (all extensions combined)
- Individual extension processes
- Terminal processes

### Common High-Impact Extensions

| Extension | Impact | Mitigation |
|-----------|--------|------------|
| **GitLens** | CPU: high on large repos | Disable for repos > 50K commits or use lightweight mode |
| **Prettier** | CPU: triggers on every save | Set `"editor.formatOnSave": false`, format manually |
| **TypeScript** | Memory: large projects | Increase `"typescript.tsserver.maxTsServerMemory": 4096` |
| **ESLint** | CPU: validates on type | Set `"eslint.run": "onSave"` instead of "onType" |
| **Spell Checker** | CPU: large files | Add exclusion patterns for generated files |
| **Import Cost** | CPU: recalculates on change | Disable for projects with many imports |

### Disable Per Workspace

Right-click extension > `Disable (Workspace)`. This keeps the extension available for other projects while removing it from the current slow one.

## AI Feature Tuning

### Indexing Optimization

The biggest performance lever for AI features:

```gitignore
# .cursorignore -- aggressive exclusion for large projects
node_modules/
dist/
build/
.next/
out/
target/
coverage/
.turbo/
.cache/
__pycache__/
*.pyc
venv/
.venv/

# Generated code
*.min.js
*.min.css
*.bundle.js
*.d.ts.map
*.tsbuildinfo

# Data files
*.csv
*.json.gz
*.parquet
*.sqlite
*.sql

# Lock files
package-lock.json
yarn.lock
pnpm-lock.yaml
Cargo.lock

# Media
*.png
*.jpg
*.gif
*.svg
*.mp4
*.woff2

# Documentation build output
docs/dist/
docs/.vitepress/dist/
```

### Tab Completion Speed

Tab completion is fast by design (~100ms), but can feel slow if:

- The file is very large (> 10K lines): split the file
- Many extensions are running: audit extensions
- Network is slow: Tab requires network for model inference

### Chat/Composer Response Time

| Factor | Impact | Fix |
|--------|--------|-----|
| Model choice | Opus/o1 are slower than Sonnet/GPT-4o | Use faster models for simple tasks |
| Context size | More @-mentions = slower | Use @Files not @Codebase when possible |
| Conversation length | Long chats slow down | Start new chat frequently |
| Server load | Peak hours are slower | Use off-peak or BYOK |

### Managing Chat History

Long chat sessions consume memory and slow down responses:

```
Signs of chat-related slowdown:
- Typing lag in the chat input
- Editor becomes sluggish after extended chat session
- AI responses take progressively longer

Fix:
1. Start a new chat (Cmd+N in chat panel)
2. Close old chat tabs
3. One topic per chat session
```

## Large Codebase Strategies

### For Projects > 50K Files

```
1. Open specific packages, not the whole monorepo
   cursor packages/api/    # Not: cursor .

2. Aggressive .cursorignore (see above)

3. Multi-root workspace with only active packages
   File > Add Folder to Workspace (selectively)

4. Disable codebase indexing if not needed
   Cursor Settings > Features > Codebase Indexing > off
   (You lose @Codebase but gain performance)

5. Increase system resources
   Close other Electron apps (Slack, Teams, Discord)
   Increase swap space on Linux
```

### Linux File Watcher Limits

```bash
# Check current limit
cat /proc/sys/fs/inotify/max_user_watches

# Increase (required for large projects)
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Memory Monitoring

```bash
# macOS: Monitor Cursor memory usage
top -pid $(pgrep -f "Cursor")

# Linux: Monitor Cursor processes
ps aux | grep -i cursor | sort -rn -k4

# If memory exceeds 4GB consistently:
# 1. Close unused workspace folders
# 2. Limit open editor tabs to ~20
# 3. Restart Cursor daily during heavy use
```

## Cache Management

### Clear Caches

```bash
# macOS
rm -rf ~/Library/Application\ Support/Cursor/Cache/
rm -rf ~/Library/Application\ Support/Cursor/CachedData/
rm -rf ~/Library/Application\ Support/Cursor/Code\ Cache/

# Linux
rm -rf ~/.config/Cursor/Cache/
rm -rf ~/.config/Cursor/CachedData/
rm -rf ~/.config/Cursor/Code\ Cache/
```

Restart Cursor after clearing. Caches rebuild automatically.

### Database Maintenance

Cursor stores extension data in SQLite databases. If the storage directory grows large:

```bash
# Check size (macOS)
du -sh ~/Library/Application\ Support/Cursor/

# If > 2GB, clearing Cache/ and CachedData/ usually reclaims most space
```

## Enterprise Considerations

- **Baseline performance**: Establish performance baselines for standard project sizes on team hardware
- **Hardware recommendations**: 16GB RAM minimum for large projects, 32GB for monorepos
- **Network performance**: AI features require low-latency internet. VPN routing can add 200-500ms per request
- **Standardized settings**: Distribute performance-optimized `settings.json` to all team members

## Resources

- [VS Code Performance Tips](https://code.visualstudio.com/docs/editor/editingevolved#_performance)
- Cursor Forum - Performance
- [Codebase Indexing](https://docs.cursor.com/context/codebase-indexing)
