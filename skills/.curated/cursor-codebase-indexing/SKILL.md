---
name: cursor-codebase-indexing
description: 'Set up and optimize Cursor codebase indexing for semantic code search
  and @Codebase queries.

  Triggers on "cursor index", "codebase indexing", "index codebase", "cursor semantic
  search",

  "@codebase", "cursor embeddings".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- cursor-codebase
compatibility: Designed for Claude Code
---
# Cursor Codebase Indexing

## Overview

Configure codebase indexing so relevant source and documentation are available while sensitive, generated, oversized, and unrelated files remain excluded from AI context.

## Prerequisites

- Repository ownership, expected source/documentation paths, and reviewed `.cursorignore`/indexing exclusions.
- A non-sensitive verification fixture and a change-review path for configuration updates.

## Instructions

1. Define the intended workspace scope and add exclusions before the first indexing pass.
2. Verify required files can be found and excluded paths cannot be attached or discovered.
3. Reindex only after a reviewed configuration/workspace change and capture a redacted result.
4. Monitor index size/performance and narrow scope rather than weakening data controls.

## Output

- A verified index scope with explicit included/excluded paths and an owner for maintenance.

## Examples

Index `src/` and `docs/` for a service while excluding `.env*`, build output, vendor directories, and customer exports. Verify a sanitized source file is available and an excluded placeholder is not before allowing AI work on the repository.

Set up and optimize Cursor's codebase indexing system. Indexing creates embeddings of your code, enabling `@Codebase` semantic search and improving AI context awareness across Chat, Composer, and Agent mode.

## How Indexing Works

```
Your Code Files
      │
      ▼
  Syntax Chunking ─── splits files into meaningful code blocks
      │
      ▼
  Embedding Generation ─── converts chunks to vector representations
      │
      ▼
  Vector Storage (Turbopuffer) ─── cloud-hosted nearest-neighbor search
      │
      ▼
  @Codebase Query ─── your question → embedding → similarity search → relevant chunks
```

### Key Architecture Details

- **Merkle tree** for change detection: only modified files are re-indexed (every 10 minutes)
- **No plaintext storage**: code is not stored server-side; only embeddings and obfuscated metadata
- **Privacy Mode compatible**: with Privacy Mode on, embeddings are computed without retaining source code
- Indexing runs in the background; small projects complete in seconds, large projects (50K+ files) may take hours initially

## Initial Setup

1. Open your project in Cursor
2. Indexing starts automatically on first open
3. Check status: look at the bottom status bar for "Indexing..." indicator
4. View indexed files: `Cursor Settings` > `Features` > `Codebase Indexing` > `View included files`

### Verify Indexing Status

The status bar shows:

- **"Indexing..."** with progress indicator -- initial indexing in progress
- **"Indexed"** -- indexing complete, `@Codebase` queries are available
- No indicator -- indexing may be disabled or not started

## Configuration

### .cursorignore

Exclude files from indexing and AI features. Place in project root. Uses `.gitignore` syntax:

```gitignore
# .cursorignore

# Build artifacts (large, not useful for AI context)
dist/
build/
out/
.next/
target/

# Dependencies
node_modules/
vendor/
venv/
.venv/

# Generated files
*.min.js
*.min.css
*.bundle.js
*.map
*.lock

# Large data files
*.csv
*.sql
*.sqlite
*.parquet
fixtures/
seed-data/

# Secrets (defense in depth -- also use .gitignore)
.env*
**/secrets/
**/credentials/
```

### .cursorindexingignore

Exclude files from indexing only but keep them accessible to AI features when explicitly referenced:

```gitignore
# .cursorindexingignore

# Large test fixtures -- don't index, but allow @Files reference
tests/fixtures/
e2e/recordings/

# Documentation build output
docs/.vitepress/dist/
```

**Difference:** `.cursorignore` hides files from both indexing and AI features. `.cursorindexingignore` only excludes from the index; files can still be referenced via `@Files`.

### Default Exclusions

Cursor automatically excludes everything in `.gitignore`. You only need `.cursorignore` for files tracked by git that you want to exclude from AI.

## Using the Index

### @Codebase Queries

Ask semantic questions about your entire codebase:

```
@Codebase where is user authentication handled?

@Codebase show me all API endpoints that accept file uploads

@Codebase how does the payment processing flow work?

@Codebase find all places where we connect to Redis
```

`@Codebase` performs a nearest-neighbor search using your question's embedding. It returns the most semantically similar code chunks, even if they do not contain the exact keywords you used.

### @Codebase vs @Files vs Text Search

| Method | When to Use | Context Cost |
|--------|------------|--------------|
| `@Codebase` | Discovery -- you don't know which files | High (many chunks) |
| `@Files` | You know exactly which file | Low (one file) |
| `@Folders` | You know the directory | Medium-High |
| `Ctrl+Shift+F` | Exact text/regex match | N/A (editor search) |

Use `@Codebase` for discovery, then switch to `@Files` once you know where the code lives.

## Optimization for Large Projects

### Monorepo Strategy

For monorepos with many packages, open the specific package directory instead of the root:

```bash
# Instead of opening the entire monorepo:
cursor /path/to/monorepo           # Indexes everything -- slow

# Open the specific package:
cursor /path/to/monorepo/packages/api   # Indexes only this package -- fast
```

Or use `.cursorignore` at the root to exclude packages you are not actively working on:

```gitignore
# .cursorignore -- monorepo, focus on api and shared
packages/web/
packages/mobile/
packages/admin/
# packages/api/    ← not listed, so it IS indexed
# packages/shared/ ← not listed, so it IS indexed
```

### Re-Indexing

If search results are stale or indexing appears stuck:

1. `Cmd+Shift+P` > `Cursor: Resync Index`
2. Wait for status bar to show indexing progress
3. If that fails, delete the local cache:
   - macOS: `~/Library/Application Support/Cursor/Cache/`
   - Linux: `~/.config/Cursor/Cache/`
   - Windows: `%APPDATA%\Cursor\Cache\`
4. Restart Cursor and allow full re-index

### File Watcher Limits (Linux)

On Linux, large projects may hit the file watcher limit:

```bash
# Check current limit
cat /proc/sys/fs/inotify/max_user_watches

# Increase (temporary)
sudo sysctl fs.inotify.max_user_watches=524288

# Increase (permanent)
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## Enterprise Considerations

- **Data residency**: Embeddings are stored in Turbopuffer (cloud). Obfuscated filenames and no plaintext code, but metadata exists
- **Privacy Mode**: With Privacy Mode on, embeddings are computed with zero data retention at the provider
- **Air-gapped environments**: Indexing requires network access to Cursor's embedding API. Not available offline
- **Indexing scope**: Only files in the currently open workspace are indexed. Closing a project removes its index from active queries

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| @Codebase returns no results | Index not built | Wait for "Indexed" in status bar |
| Search misses known files | File in .gitignore or .cursorignore | Check ignore files |
| Indexing stuck at N% | Large project or network issue | Resync index via Command Palette |
| Stale results after refactor | Index not yet updated | Wait 10 min or manual resync |
| High CPU during indexing | Initial embedding computation | Normal for first run; subsides |

## Resources

- [Codebase Indexing Docs](https://docs.cursor.com/context/codebase-indexing)
- [Ignore Files](https://docs.cursor.com/context/ignore-files)
- [Secure Codebase Indexing](https://cursor.com/blog/secure-codebase-indexing)
