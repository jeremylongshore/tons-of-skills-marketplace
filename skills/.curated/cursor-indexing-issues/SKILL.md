---
name: cursor-indexing-issues
description: 'Troubleshoot Cursor codebase indexing: stuck indexing, empty search,
  @codebase failures, and

  performance issues. Triggers on "cursor indexing", "cursor index", "@codebase not
  working",

  "cursor search broken", "indexing stuck".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-indexing
compatibility: Designed for Claude Code
---
# Cursor Indexing Issues

## Overview

Diagnose missing, stale, slow, or over-broad codebase indexing while keeping sensitive and generated files excluded from AI context.

## Prerequisites

- The affected workspace, expected file/path, current ignore configuration, and a non-sensitive reproduction.
- Authority to inspect repository indexing settings without weakening data-exclusion rules.

## Instructions

1. Confirm the file is inside an approved workspace root and not intentionally excluded by ignore configuration.
2. Check index status, refresh only the affected workspace, and compare the result against a known expected file.
3. Change ignore/rule configuration through normal review, then verify both inclusion of required files and exclusion of sensitive paths.

## Output

- A scoped indexing diagnosis with a verified inclusion/exclusion result.

## Error Handling

| Condition | Safe response |
|---|---|
| Sensitive file is indexed | Stop sharing context, add/repair the exclusion, and follow exposure policy. |
| Index remains stale | Capture redacted diagnostics and escalate; do not remove all ignore controls. |
| Large repository is slow | Narrow workspace roots and generated-file scope before resyncing. |

## Examples

When `src/service.ts` is absent, verify its root and ignore rules, resync indexing, then ask a minimal chat to reference only that file. If a `.env` file becomes visible during testing, stop and correct the exclusion before continuing.

Diagnose and fix codebase indexing problems. Covers stuck indexing, empty search results, stale results, and performance optimization for large codebases.

## Quick Diagnosis

| Symptom | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| Status bar stuck on "Indexing..." | Large codebase or network issue | Add `.cursorignore`, resync |
| @Codebase returns nothing | Index not built or file excluded | Wait for index, check ignore files |
| @Codebase finds wrong code | Stale index | Resync index |
| Indexing crashes / restarts | Memory or file watcher limits | Increase limits, reduce scope |
| "Unable to index" error | Network blocked or auth expired | Check proxy/firewall, re-auth |

## Fix: Stuck Indexing

### Step 1: Reduce Scope

Create or update `.cursorignore` in project root:

```gitignore
# .cursorignore -- exclude non-essential directories

# Build output
dist/
build/
.next/
out/
target/

# Dependencies (always exclude)
node_modules/
vendor/
.venv/
venv/

# Generated / large files
*.min.js
*.min.css
*.bundle.js
*.map
*.lock
package-lock.json
yarn.lock
pnpm-lock.yaml

# Data files
*.csv
*.sql
*.sqlite
*.parquet
*.json.gz
fixtures/

# Media
*.png
*.jpg
*.gif
*.svg
*.mp4
*.woff2
```

### Step 2: Resync Index

`Cmd+Shift+P` > `Cursor: Resync Index`

### Step 3: Clear Cache (if resync fails)

```bash
# macOS
rm -rf ~/Library/Application\ Support/Cursor/Cache/
rm -rf ~/Library/Application\ Support/Cursor/CachedData/

# Linux
rm -rf ~/.config/Cursor/Cache/
rm -rf ~/.config/Cursor/CachedData/

# Windows (PowerShell)
Remove-Item -Recurse "$env:APPDATA\Cursor\Cache"
Remove-Item -Recurse "$env:APPDATA\Cursor\CachedData"
```

Restart Cursor after clearing cache. Full re-index begins automatically.

## Fix: @Codebase Returns No Results

### Check 1: Is Indexing Complete?

Look at the bottom status bar. If it says "Indexing...", wait for it to finish. For projects with 10K+ files, initial indexing can take 10-30 minutes.

### Check 2: Is the File Excluded?

A file might be excluded by:

1. `.gitignore` (Cursor respects this by default)
2. `.cursorignore` (explicit exclusion)
3. `.cursorindexingignore` (excluded from index but not from AI features)

Verify: `Cursor Settings` > `Features` > `Codebase Indexing` > `View included files`

This opens a text file listing all indexed paths. Search for the file you expect to find.

### Check 3: Network Connectivity

Indexing requires network access to Cursor's embedding API. Test:

- Can you access `api.cursor.com`?
- Is a corporate proxy blocking outbound HTTPS?
- Is a VPN interfering?

### Check 4: Semantic vs Keyword Search

`@Codebase` uses semantic search (embeddings), not keyword matching. The query "authentication middleware" will find files about auth even if they never use the word "middleware." But it may miss files if the semantic meaning is very different from the query.

For exact keyword matching, use `Cmd+Shift+F` (workspace search) instead.

## Fix: Stale / Outdated Results

Cursor re-checks for file changes every 10 minutes using a Merkle tree. If you need fresher results:

1. Save all open files
2. `Cmd+Shift+P` > `Cursor: Resync Index`
3. Wait for "Indexed" status to reappear
4. Retry your `@Codebase` query

## Performance Optimization for Large Projects

### Indexing Time Benchmarks

| Project Size | Files Indexed | Initial Index Time |
|-------------|--------------|-------------------|
| Small (< 1K files) | ~500 | < 30 seconds |
| Medium (1K-10K files) | ~5,000 | 1-5 minutes |
| Large (10K-50K files) | ~20,000 | 5-30 minutes |
| Very large (50K+) | ~50,000+ | 30 min - 2 hours |

### Monorepo Strategy

Do not open the entire monorepo root. Instead:

```bash
# Open just the package you're working on:
cursor packages/api/

# Or use .cursorignore to exclude other packages:
# .cursorignore
packages/web/
packages/mobile/
packages/admin/
packages/deprecated-*
```

### Linux File Watcher Limits

If indexing crashes on Linux with large projects:

```bash
# Check current limit
cat /proc/sys/fs/inotify/max_user_watches

# Increase to 524288 (persists across reboots)
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Memory Pressure

If Cursor runs out of memory during indexing:

```json
// settings.json
{
  "files.maxMemoryForLargeFilesMB": 4096,
  "files.watcherExclude": {
    "**/node_modules/**": true,
    "**/.git/**": true,
    "**/dist/**": true,
    "**/build/**": true
  }
}
```

## .cursorignore vs .cursorindexingignore

| File | Indexed? | Available to AI? | Use Case |
|------|----------|-----------------|----------|
| Listed in `.cursorignore` | No | No (best effort) | Secrets, large binaries, build output |
| Listed in `.cursorindexingignore` | No | Yes (via @Files) | Test fixtures, docs, large but useful files |
| Not in any ignore file | Yes | Yes | Your source code |

Use `.cursorindexingignore` for files you want to reference explicitly but not have polluting search results:

```gitignore
# .cursorindexingignore
tests/fixtures/large-sample.json
docs/api-spec.yaml
e2e/recordings/
```

## Enterprise Considerations

- **Data residency**: Embeddings stored in Turbopuffer cloud. No plaintext code stored, but metadata (obfuscated filenames) exists server-side
- **Air-gapped environments**: Indexing requires outbound HTTPS. Not available in fully air-gapped setups
- **Index freshness SLA**: 10-minute polling interval is not configurable. Manual resync is the only way to force immediate re-index
- **Audit**: No logging of which files are indexed. Use `.cursorignore` proactively for regulated data

## Resources

- [Codebase Indexing Docs](https://docs.cursor.com/context/codebase-indexing)
- [Ignore Files](https://docs.cursor.com/context/ignore-files)
- [Secure Codebase Indexing](https://cursor.com/blog/secure-codebase-indexing)
