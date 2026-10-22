---
name: janitor-security
description: "Heuristic security scan of installed skills — prompt-injection phrases, hidden unicode instructions, credential-store access, network-pipe-to-shell and payload-smuggling patterns. Use when the user asks 'are my skills safe', wants to scan skills for prompt injection or malware patterns, or before trusting a newly installed skill. Trigger with '/janitor-security'."
allowed-tools: Read, Bash(bash:*)
argument-hint: "[--path <dir>] [--json]"
version: 1.6.0
author: Krzysztof Hendzel <krzysztoff.hendzel@gmail.com>
license: MIT
compatibility: Designed for Claude Code. Requires bash 3.2+ (macOS default works). Reads local skill files only; no network access.
tags:
  - skills
  - security
  - prompt-injection
  - audit
  - maintenance
---

# Security Scan

Heuristic scan of skill content for prompt-injection and malicious patterns.

## Overview

A skill is text your agent trusts: its SKILL.md is read as instructions and its scripts run on your machine. Public research (Snyk's ToxicSkills, 2026) found prompt injection in roughly a third of tested community skills. This scan flags the known bad shapes across every installed skill, in every scope (user, project, codex, plugin):

- **Injection phrases** — "ignore all previous instructions", "do not tell the user"
- **Hidden instructions** — imperative text in HTML comments (invisible when rendered), zero-width/bidi unicode between plain characters
- **Payload smuggling** — large decodable base64 blobs in markdown
- **Dangerous scripts** — network piped into a shell (`curl … | bash`), decode-and-execute, credential-store access (`~/.ssh`, `~/.aws`, keychain), URL shorteners, plain-HTTP calls, uploads of variable data

Findings are heuristics, not proof: a RISK verdict means "read this before trusting it". Legit tools trip these rules too (e.g. an installer that pipes curl into bash) — the point is that YOU see it and decide.

## Prerequisites

- Claude Code with the skills-janitor plugin installed (provides `scripts/security.sh`)
- bash 3.2+ (the stock macOS bash works; no external dependencies, no network access)

## Instructions

### Step 1: Run the scan

```bash
bash ~/.claude/skills/skills-janitor/scripts/security.sh           # all installed skills
bash ~/.claude/skills/skills-janitor/scripts/security.sh --json    # machine-readable
bash ~/.claude/skills/skills-janitor/scripts/security.sh --path ~/some/skill-dir   # one directory
```

### Step 2: Present verdicts honestly

Per-skill verdict: **RISK** (any HIGH finding), **REVIEW** (any MEDIUM), **PASS**. For each flagged skill show the finding titles, the file, and the evidence snippet. Do NOT call a finding "malware" — describe what the pattern does and let the user judge intent (e.g. "media-use pipes a HeyGen installer from the network into bash — a common install pattern, but verify the URL before trusting it").

### Step 3: Recommend next steps

- RISK on a skill the user doesn't recognize or need → `/janitor-swipe` or delete it outright
- RISK on a known/trusted tool → read the flagged file once, then move on
- Before installing something new → `/janitor-discover <url>` runs this same scan pre-install

## Output

Summary line (`Scanned: N | RISK: x | REVIEW: y | PASS: z`) followed by flagged skills, each with severity-tagged findings, the file, and an evidence snippet. `--json` emits the full structured report.

## Error Handling

1. **Error**: `security.sh: No such file or directory`
   **Solution**: The plugin is installed under a different root — locate it with `ls ~/.claude/skills` or check the plugin cache.

2. **Error**: Everything shows PASS but the user expected a finding
   **Solution**: The scan covers markdown and script files up to 1MB, 200 files per skill; binaries and huge files are skipped. Check the specific file manually.

3. **Error**: A trusted skill shows RISK
   **Solution**: Expected for tools that legitimately use flagged patterns (installers, credential helpers). Read the evidence line — if it matches the tool's documented purpose, note it and move on. Verdicts are advisory; nothing is deleted.

## Examples

### Example 1: Full audit

**Input**: "Are my skills safe? Check for prompt injection."

**Output**: Run the scan, lead with the summary ("178 scanned, 2 RISK, 0 REVIEW"), then explain each flagged skill in plain language with its evidence, and close with a recommendation per skill.

### Example 2: One suspicious folder

**Input**: "Scan ~/Downloads/cool-skill before I install it."

**Output**: Run with `--path ~/Downloads/cool-skill` and present the verdict; suggest `/janitor-discover` for the overlap check too.

## Resources

- Scan engine (plugin-relative): `{baseDir}/../../scripts/security.sh`
- `/janitor-discover <url>` — pre-install check (overlap + this security scan on the fetched SKILL.md)
- `/janitor-report` — general health check (errors, duplicates, broken skills)
- `/janitor-swipe` — delete what you don't trust
