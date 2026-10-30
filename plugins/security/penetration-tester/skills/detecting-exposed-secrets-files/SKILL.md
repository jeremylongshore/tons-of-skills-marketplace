---
name: detecting-exposed-secrets-files
description: |
  Probe a target for accidentally-served secret-bearing files in the web root
  — .git/, .env, .DS_Store, backup files, database dumps, key files,
  CI configs, IDE configs.
  Use when: post-deploy verification on a new release, or SOC2 auditor asked
  "what's reachable in the web root that shouldn't be," or a bug-bounty
  report hints at a leaked file.
  Threshold: any of the canonical 40+ paths returns 200 OR returns a body
  matching the expected fingerprint of the file type (e.g., .git/HEAD
  returns content starting with ref: or a 40-char hex SHA).
  Trigger with: "check exposed files", "git directory exposure",
  "env file leak", "backup file scan".
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
  - secrets
  - pentest
---

# Detecting Exposed Secrets Files

## Overview

The single highest-value pentest probe per HTTP request. A `.git/config`
disclosure leaks repo URL + credentials embedded in remote URLs. A `.env`
disclosure leaks every API key the app has. A `backup.sql` disclosure
leaks the entire database. These are not "weak crypto" findings that need
a chained exploit. They are direct, immediate compromise.

The probe set is the canonical 40+ paths web servers commonly expose by
accident: VCS directories (`.git/`, `.svn/`, `.hg/`), dotenv files,
OS metadata (`.DS_Store`), database dumps, archive files, IDE configs,
CI configs, and key files. Each is fingerprinted to distinguish a true
positive (server returns the file's expected content) from a 200 OK
that's actually the application's SPA index page catching the route.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| `.git/HEAD` reachable + valid content | **CRITICAL** | 200 + body matches `ref:` or 40-char SHA | NIST 800-53 SC-28 |
| `.git/config` reachable + repo URL leaked | **CRITICAL** | 200 + body matches `[remote` | NIST 800-53 SC-28 |
| `.env` reachable + dotenv format | **CRITICAL** | 200 + body matches `KEY=VALUE` lines | OWASP A05:2021 |
| `*.sql` / `*.dump` / `backup.*` reachable | **CRITICAL** | 200 + body looks like SQL or binary dump | CWE-538 |
| `.aws/credentials` reachable | **CRITICAL** | 200 + body matches `[default]\naws_access_key_id` | CWE-200 |
| `id_rsa` / `*.pem` / `*.key` reachable | **CRITICAL** | 200 + body matches `BEGIN PRIVATE KEY` or `BEGIN RSA` | CWE-321 |
| `.svn/entries` / `.hg/store/` reachable | **HIGH** | 200 + body matches VCS format | NIST 800-53 SC-28 |
| `.DS_Store` reachable | **MEDIUM** | 200 + binary blob with `Bud1` magic | CWE-538 |
| IDE configs (`.idea/`, `.vscode/`) reachable | **LOW** | 200 + JSON/XML | CWE-200 |
| `composer.json` / `package.json` reachable on prod | **LOW** | 200 + valid JSON in non-API root | CWE-200 |

## Prerequisites

- Python 3.9+ with `requests` library
- Authorization for non-local targets

## Instructions

### Step 1 — Confirm Authorization

```text
"Do you have authorization to perform secret-file discovery on this
 target? I need confirmation before proceeding."
```

### Step 2 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-exposed-secrets-files/scripts/probe_secrets.py \
    https://target.example.com \
    --authorized
```

Options:

```
Usage: probe_secrets.py URL [OPTIONS]

Options:
  --authorized       Attest authorization (required for non-local)
  --output FILE      Write findings to FILE
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --timeout SECS     Per-probe timeout (default: 10)
  --paths-file FILE  Override the canonical probe set with a custom list
  --check-only       Skip body-fingerprint verification (faster, more
                     false positives — useful when target serves SPA
                     index for everything)
```

The scanner sends a GET for each path in the canonical probe set. For
every 200 response, it inspects the body to confirm the response really
is the expected file type (not the app's SPA index catching the route).

### Step 3 — Interpret findings

CRITICAL = direct credential / source code / database exposure.
Ship same-hour fix (configure web server to deny + audit logs for
anyone who already exfiltrated).

### Step 4 — Cross-skill chaining

After this skill, suggest `detecting-debug-endpoints` (#7) — the same
deploy mistake that exposes `.git/` often exposes `/admin/` and
`/server-status/`. And `detecting-directory-listing` (#9) — if any of
the secret-file paths returned a directory listing instead of the file
itself, autoindex is enabled.

## Examples

### Example 1 — Post-deploy verification

User: "We just rolled out v4.2. Make sure we didn't deploy `.env` or
the `.git/` dir by accident."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-exposed-secrets-files/scripts/probe_secrets.py \
    https://app.example.com --authorized --min-severity high
```

### Example 2 — Bug bounty triage

User: "Submission claims our .git/ is exposed."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-exposed-secrets-files/scripts/probe_secrets.py \
    https://app.example.com --authorized --format json --output exposure.json
jq '.[] | select(.title | contains(".git"))' exposure.json
```

The fingerprint check distinguishes real `.git/HEAD` (returns
`ref: refs/heads/main` or a 40-char hex SHA) from false-positive SPA
index pages that 200 on any path.

### Example 3 — CI gate against future deploys

```yaml
- name: Exposed-files gate
  run: |
    python3 plugins/security/penetration-tester/skills/detecting-exposed-secrets-files/scripts/probe_secrets.py \
        "${{ secrets.STAGING_URL }}" \
        --authorized --min-severity critical
```

Exit 1 fails the deploy if any CRITICAL finding lands.

## Output

JSON / JSONL / Markdown. Exit codes: 0 clean, 1 high/critical, 2 error.

## Error Handling

- **Target SPA-catches every URL with 200** → use `--check-only` to skip
  body-fingerprint; expect more false positives but get any real exposure.
- **All probes timeout** → likely DDoS protection blocking the scanner;
  contact the target's security team for an allowlist.
- **Connection error** → exit 2.

## Resources

- `references/THEORY.md` — Why each path matters, fingerprint patterns,
  RFC / OWASP / NIST anchors
- `references/PLAYBOOK.md` — Per-server config snippets to block each
  category of path (nginx, Apache, Caddy, ALB, GCP LB)
- `../analyzing-tls-config/references/AUTHORIZATION.md` — Active-scan
  authorization
