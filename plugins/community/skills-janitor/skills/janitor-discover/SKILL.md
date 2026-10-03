---
name: janitor-discover
description: "Find new skills on GitHub or check a specific skill before installing. Use when the user wants to search for skills, evaluate a skill URL, check overlap and security risk before installing, or compare a local skill against alternatives. Trigger with '/janitor-discover'."
allowed-tools: Read, Bash(bash:*)
argument-hint: "<query-or-url> [--limit N] [--compare <skill>] [--json]"
version: 1.6.0
author: Krzysztof Hendzel <krzysztoff.hendzel@gmail.com>
license: MIT
compatibility: Designed for Claude Code. Requires bash 3.2+, curl, and network access to the GitHub API (anonymous works; GITHUB_TOKEN raises rate limits).
tags:
  - skills
  - discovery
  - github-search
  - pre-install
  - duplicates
  - security
---

# Skill Discovery & Pre-Install Check

Combined entry point for finding skills on GitHub and for evaluating a specific skill (URL or local path) before installing it.

## Overview

Replaces the v1.2 split between `/janitor-search` and `/janitor-precheck`. The dispatcher picks the right mode from the argument shape. Search results are relevance-gated (a repo must carry a skill signal in its name/description/topics) and ranked by relevance before stars, so generic mega-repos don't crowd out actual skills.

| Argument | Mode | What runs |
|---|---|---|
| Keyword(s) like `seo` or `n8n workflows` | Discovery | `search.sh` — find matching skills on GitHub |
| `--compare <skill-name>` | Comparison | `search.sh --compare` — find alternatives to a local skill |
| Full URL: `https://github.com/user/skill` | Pre-install check | `precheck.sh` — analyze before installing |
| Short repo: `user/skill` | Pre-install check | `precheck.sh` (auto-expanded to URL) |
| Local path: `~/path/to/skill` | Pre-install check | `precheck.sh` (local folder) |

Pre-install mode runs **two** checks, not one: overlap against what's already installed, and
(since v1.6) a security scan of the candidate via `security.sh` — the same heuristics
`/janitor-security` uses on installed skills.

## Prerequisites

- Claude Code with the skills-janitor plugin installed (provides `scripts/discover.sh`, `search.sh`, `precheck.sh`, `compare.sh`)
- bash 3.2+ and `curl`
- Network access to `api.github.com` (anonymous OK; set `GITHUB_TOKEN` for higher rate limits and code search)

## Instructions

### Step 1: Dispatch on argument shape

```bash
bash ~/.claude/skills/skills-janitor/scripts/discover.sh <query-or-url> [options]
```

Examples:

- `discover.sh seo` — search for SEO-related skills
- `discover.sh n8n --limit 20` — top 20 n8n skills
- `discover.sh --compare marketing-seo-audit` — alternatives to a local skill
- `discover.sh https://github.com/user/my-skill` — check before installing
- `discover.sh user/my-skill` — same, short form

### Step 2: Present results per mode

**Discovery mode** — ranked list of GitHub repos with skill name, description, stars, last updated, and a one-line verdict.

**Pre-install mode** — two sections. First, overlap analysis: which of the user's existing skills (including plugin skills) overlap with the candidate by description, and a recommendation to install / skip / replace. Second, a `--- Security (<scope>) ---` block.

**Always report the security scope back to the user**, because it differs by source:

| Source | Scanned |
|---|---|
| Local path | Full directory — SKILL.md **and** bundled scripts |
| URL / `user/repo` | Fetched SKILL.md **only** — scripts are never downloaded, so re-check after cloning |

A `PASS` on a remote URL therefore means "nothing suspicious in the text we could see", not "this repo is safe". Say so when the candidate ships scripts.

## Output

Discovery: a numbered table (repository, stars, updated, INSTALLED/AVAILABLE status).

Pre-install: overlap buckets (HIGH ≥60%, MODERATE 30–59%, LOW <30%) with shared keywords and a final verdict line (`HIGH_OVERLAP` / `MODERATE_OVERLAP` / `SAFE`), plus a security block that prints either `No suspicious patterns found.` (PASS), `Security scan unavailable.` (UNKNOWN), or `VERDICT: REVIEW|RISK` followed by one severity + title + evidence line per finding. With `--json`, the same data lands under a `security` key (`verdict`, `scope`, `findings`).

## Error Handling

1. **Error**: `GitHub API rate limit exceeded`
   **Solution**: Set the `GITHUB_TOKEN` environment variable (any classic token, no scopes needed) and re-run; anonymous search allows only a few requests per minute.

2. **Error**: `Could not fetch SKILL.md from <url>`
   **Solution**: The repo keeps its SKILL.md at a non-standard path — pass a direct URL to the SKILL.md file, or a local clone path instead.

3. **Error**: No results for a valid topic
   **Solution**: The relevance gate drops repos without any skill signal. Broaden the keyword (e.g. `n8n skill` → `n8n`) or check the cached results note — results are cached for 24h in `data/search-cache.json`.

4. **Error**: `Security scan unavailable.` (verdict `UNKNOWN`)
   **Solution**: `security.sh` failed or returned no parseable JSON — the overlap result is still valid, but do not present the candidate as security-checked. Re-run, or scan after cloning with `/janitor-security`.

## Examples

### Example 1: Find skills by topic

**Input**: "Find me an n8n skill."

**Output**: Run `discover.sh n8n`, present the ranked table, and flag any result already installed.

### Example 2: Check before installing

**Input**: "Is github.com/user/seo-helper worth installing?"

**Output**: Run `discover.sh https://github.com/user/seo-helper`, then summarize: overlap with existing skills, the verdict (e.g. "MODERATE_OVERLAP — 45% with marketing-skills:seo-audit"), the security verdict, and a recommendation. Note that only the fetched SKILL.md was scanned.

### Example 3: Candidate trips the security scan

**Input**: "Check user/handy-helper before I install it."

**Output**: Run `discover.sh user/handy-helper`. If the security block reports `VERDICT: RISK`, lead with that rather than the overlap number — quote the finding's severity, title and evidence, explain that RISK means "read this before trusting it" (not "malware"), and remind the user that bundled scripts were not fetched.

## Resources

- Dispatcher (plugin-relative): `{baseDir}/../../scripts/discover.sh`
- Search cache: `data/search-cache.json` (24h TTL)
- `/janitor-security` — same scan, run across everything already installed
- `/janitor-report` — health check of currently installed skills
- `/janitor-value` — are existing skills earning their context cost
- `/janitor-fix` — fix issues with installed skills
