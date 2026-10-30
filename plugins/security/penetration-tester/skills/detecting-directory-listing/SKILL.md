---
name: detecting-directory-listing
description: |
  Probe a target for directories that return auto-generated index
  listings instead of denying or serving a specific file — exposes
  the full file tree under any reachable directory, including files
  the application never linked to.
  Use when: post-deploy verification on a static-asset host, security
  audit before SOC2, or following up on a finding from skill #6
  (exposed-files) where a backup-file path returned 200 with HTML
  body instead of the expected file content (suggests autoindex
  serving a directory listing).
  Threshold: any directory-shaped path returns 200 with HTML body
  matching the framework-specific autoindex fingerprint (nginx
  fancyindex, Apache mod_autoindex Index of/, Caddy browse, Lighttpd
  mod_dirlisting, etc.).
  Trigger with: "directory listing check", "autoindex detection",
  "open directory scan".
allowed-tools:
  - Read
  - Bash(python3:*)
  - Bash(curl:*)
disallowed-tools:
  - Bash(rm:*)
  - Edit(/etc/*)
version: 3.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - information-disclosure
  - autoindex
  - pentest
---

# Detecting Directory Listing

## Overview

Web servers can be configured to auto-generate an HTML index page
when a request hits a directory without a matching default file
(no `index.html` / `index.php` / etc.). The auto-generated page
lists every file in the directory. This is by design for static-
file servers and FTP-style file-sharing setups; it's a misconfiguration
on application servers where the file tree was never meant to be
public.

The risk compounds in two ways:

1. **File enumeration without prior knowledge.** Attackers find files
   you didn't link to (backup files, log files, old uploads).
2. **Chaining with exposed-files (#6).** A `/.git/` request that
   returns an autoindex listing reveals every object file under
   `.git/objects/` and confirms the entire repo is reachable for
   GitDumper-style reconstruction.

This skill probes commonly-vulnerable directory paths and grades
each based on the framework-specific autoindex fingerprint.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Application-root directory listing | **HIGH** | `/` returns autoindex page | OWASP A05:2021 |
| Backup / upload / log directory listing | **HIGH** | `/backup/`, `/uploads/`, `/logs/`, `/dump/` autoindex | CWE-548 |
| Asset directory listing (`/assets/`, `/static/`) | **MEDIUM** | autoindex on asset dirs (enables file enumeration) | CWE-548 |
| Config directory listing | **CRITICAL** | `/config/`, `/conf/`, `/.config/` autoindex | NIST 800-53 SC-28 |
| VCS subdir listing (chains with skill #6) | **CRITICAL** | `/.git/`, `/.svn/`, `/.hg/` autoindex | NIST 800-53 SC-28 |
| Generic root reachable via autoindex | **MEDIUM** | `/` or arbitrary path autoindex on app server | OWASP A05:2021 |

## Prerequisites

- Python 3.9+ with `requests`
- Authorization for non-local targets

## Instructions

### Step 1 — Confirm Authorization

```text
"Do you have authorization to perform directory-listing discovery on
 this target? I need confirmation before proceeding."
```

### Step 2 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-directory-listing/scripts/probe_directory_listing.py \
    https://target.example.com \
    --authorized
```

Options:

```
Usage: probe_directory_listing.py URL [OPTIONS]

Options:
  --authorized       Attest authorization (required for non-local)
  --output FILE      Write findings to FILE
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --timeout SECS     Per-probe timeout (default: 10)
  --paths-file FILE  Custom probe set (one path per line)
```

For each candidate directory path, the scanner appends a trailing
slash and sends a GET. If the response is 200 and the HTML body
matches one of the canonical autoindex fingerprints (Apache,
nginx, Caddy, Lighttpd, IIS, Python http.server, Node serve, etc.),
it's a finding.

### Step 3 — Interpret findings

CRITICAL = config or VCS directory listing → direct credential or
source-code exposure when combined with skill #6's secret-file
probe. Ship same-hour fix.

HIGH = backup / upload / log / app-root listing → significant file
enumeration. Often reveals backup files (`.bak`, `.swp`, `.orig`),
log files with embedded credentials in URLs, and orphaned uploads
from old releases. Ship within sprint.

MEDIUM = asset directory listing → file enumeration but bounded
risk if asset content is genuinely public. Still better to disable
than to leave on.

### Step 4 — Cross-skill chaining

After this skill, suggest:

- `detecting-exposed-secrets-files` (#6) — if any of the secret-
  file paths (`.git/`, `.env`) return an autoindex page instead of
  the expected file, that's the autoindex feature confirming repo
  exposure.
- `detecting-debug-endpoints` (#7) — directory listings under
  framework paths (`/static/`, `/public/`) sometimes expose
  framework-debug artifacts.

## Examples

### Example 1 — Static-asset host audit

User: "We just spun up a new S3 + CloudFront. Verify autoindex isn't
on by accident."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-directory-listing/scripts/probe_directory_listing.py \
    https://cdn.example.com --authorized --min-severity medium
```

S3 buckets configured with `ListBucket` permissions return XML
directory listings; the scanner detects those too.

### Example 2 — Following up on .git exposure

User: "Skill #6 found .git/HEAD exposed. Check if the full directory
is browseable."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-directory-listing/scripts/probe_directory_listing.py \
    https://app.example.com --authorized --paths-file <(echo .git/)
```

If the `.git/` probe returns an autoindex listing instead of the
404 it should, the whole repository is reachable for reconstruction
via GitDumper-style tools.

### Example 3 — CI gate against autoindex regression

```yaml
- name: Directory-listing gate
  run: |
    python3 plugins/security/penetration-tester/skills/detecting-directory-listing/scripts/probe_directory_listing.py \
        "${{ secrets.STAGING_URL }}" \
        --authorized --min-severity high
```

Exit 1 fails the deploy if any HIGH or CRITICAL autoindex finding
lands. Catches the regression where a new vhost gets deployed
without the deny-autoindex directive.

## Output

JSON / JSONL / Markdown. Exit codes: 0 clean, 1 high/critical, 2 error.

## Error Handling

- **Target returns SPA index for every URL** → the scanner's
  fingerprint check distinguishes a real autoindex from an SPA
  catch-all. SPAs don't generate autoindex-shaped HTML.
- **WAF blocks the scanner** → expected behavior on
  Cloudflare-fronted hosts. The fingerprint will be of the CDN's
  block page, not the origin.
- **Connection error** → exit 2.

## Resources

- `references/THEORY.md` — Per-server autoindex behavior, fingerprint
  patterns, S3 / GCS / Azure Blob considerations
- `references/PLAYBOOK.md` — Per-server config to disable
  autoindex (nginx `autoindex off`, Apache `Options -Indexes`,
  Caddy disabling browse, etc.) + cloud-storage equivalents
- `../analyzing-tls-config/references/AUTHORIZATION.md` — Active-scan
  authorization pattern
