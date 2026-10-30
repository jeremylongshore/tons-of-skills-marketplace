---
name: fingerprinting-server-software
description: |
  Identify the server software, framework, and component versions a
  target is running from its HTTP response signatures — Server header,
  X-Powered-By, Via, X-AspNet-Version, X-Runtime, X-Drupal-Cache,
  X-Generator, Set-Cookie name patterns, error-page artwork,
  HTTP method behavior signatures.
  Use when: penetration test reconnaissance phase, post-deploy audit
  of fingerprintable exposure, or before reporting "no obvious version
  disclosure" to an auditor.
  Threshold: any version string in a response header (e.g.,
  Server header with nginx/1.18.0, X-Powered-By with PHP/7.4.21,
  X-Generator with Drupal 9), or any framework-default Set-Cookie
  name (PHPSESSID, JSESSIONID, connect.sid, _csrf_token).
  Trigger with: "fingerprint server", "version disclosure",
  "tech-stack identification", "what's this site running".
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
  - fingerprinting
  - reconnaissance
  - pentest
---

# Fingerprinting Server Software

## Overview

Version disclosure is the cheapest recon an attacker buys. A single
GET request returns the `Server:` header, the `X-Powered-By:` header,
and any framework-default cookies. From those three signals the
attacker derives: web server family + exact version, app-framework +
version, language runtime + version. That maps directly to a CVE
catalog query: every published CVE affecting any of those components,
filtered to ones an unauthenticated attacker can trigger.

The fix is operationally trivial (one line in nginx, one line in
Apache, one line in IIS) but the discipline isn't universal. This
skill enumerates the signals + reports each disclosure with the
severity matching how much it enables follow-on attack.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Server header discloses version | **MEDIUM** | `Server: nginx/1.18.0` or similar with explicit version | CWE-200 |
| Server header discloses minor version | **LOW** | `Server: nginx` (no version) | CWE-200 |
| X-Powered-By discloses framework version | **MEDIUM** | `X-Powered-By: PHP/7.4.21`, `Express`, `ASP.NET` | CWE-200 |
| X-AspNet-Version present | **HIGH** | Specific dotnet runtime version | CWE-200 |
| X-Runtime / X-Rails / X-Django headers present | **LOW** | Framework identification, no version | CWE-200 |
| X-Generator: drupal/wordpress + version | **MEDIUM** | CMS family + version disclosure | CWE-200 |
| Via header discloses proxy chain | **LOW** | Reveals upstream architecture (Varnish, Squid, CloudFront) | CWE-200 |
| Framework-default Set-Cookie pattern | **LOW** | `PHPSESSID`, `JSESSIONID`, `connect.sid`, etc. | CWE-200 |
| Error page reveals stack trace | **HIGH** | 5xx response body contains source file paths or framework banner | CWE-209 |
| HTTP/2 server-push fingerprint | **LOW** | HTTP/2 `:server` pseudo-header with version | CWE-200 |
| ETag format identifies cluster member | **LOW** | Apache-style hex ETags reveal node | CWE-200 |

## Prerequisites

- Python 3.9+ with `requests`
- Authorization for non-local targets

## Instructions

### Step 1 — Confirm Authorization

```text
"Do you have authorization to perform server-fingerprinting probes on
 this target? I need confirmation before proceeding."
```

### Step 2 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fingerprinting-server-software/scripts/fingerprint_server.py \
    https://target.example.com \
    --authorized
```

Options:

```
Usage: fingerprint_server.py URL [OPTIONS]

Options:
  --authorized       Attest authorization (required for non-local)
  --output FILE      Write findings to FILE
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --timeout SECS     Per-probe timeout (default: 10)
  --trigger-error    Send a malformed request to surface error-page disclosure
                     (off by default — some WAFs block on this)
```

The scanner sends a baseline GET + an OPTIONS + (optionally) a
malformed request to surface error-page disclosure. For each
response, it parses the standard fingerprinting headers and
classifies each match against the threshold table above.

### Step 3 — Interpret findings

The vast majority of findings will be MEDIUM or LOW. CWE-200 is by
itself rarely a critical vulnerability — it's a recon enabler.

The exception: error-page stack-trace disclosure (CWE-209) is HIGH
because production error pages should never leak server-internal
paths or framework banners. If the error page reveals
`/home/app/src/handlers/auth.py`, the attacker now knows the source
layout AND that the language is Python.

### Step 4 — Cross-skill chaining

After this skill, suggest:

- `detecting-debug-endpoints` (#7) — fingerprinted framework points
  to which debug endpoints to probe (e.g., Server: nginx → check
  /nginx_status; X-Powered-By: Spring → check /actuator/*).
- `detecting-exposed-secrets-files` (#6) — framework fingerprint
  informs which CI / IDE / build-tool configs to probe for.

## Examples

### Example 1 — Post-deploy version-disclosure audit

User: "Make sure we're not leaking nginx version on prod."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fingerprinting-server-software/scripts/fingerprint_server.py \
    https://app.example.com --authorized --min-severity medium
```

Expected on a properly-configured host: zero findings of medium+.

### Example 2 — Tech-stack identification on an unknown target

User: "Bug bounty submission. We don't know what stack this runs.
What's the surface?"

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fingerprinting-server-software/scripts/fingerprint_server.py \
    https://target.example.com --authorized --format markdown
```

Use the output to inform which subsequent skills to chain (debug-
endpoint probe, secrets-file probe).

### Example 3 — Error-page exposure check

User: "Audit production error pages for stack-trace disclosure."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/fingerprinting-server-software/scripts/fingerprint_server.py \
    https://app.example.com --authorized --trigger-error --min-severity high
```

The `--trigger-error` flag sends a malformed request to provoke a
500. Some WAFs block on this; check with the target's ops team if
the result comes back empty.

## Output

JSON / JSONL / Markdown. Exit codes: 0 clean, 1 high/critical, 2 error.

## Error Handling

- **WAF blocks fingerprinting requests** → expected on
  Cloudflare/Imperva targets. The CDN itself is what gets
  fingerprinted, not the origin.
- **Connection error** → exit 2.

## Resources

- `references/THEORY.md` — Per-header reasoning: what each disclosure
  enables, threat-modeling guidance, CVE-lookup workflow
- `references/PLAYBOOK.md` — Per-server-type remediation snippets
  (nginx server_tokens, Apache ServerTokens, IIS removeHeader,
  Express helmet hidePoweredBy, framework-default cookie renaming)
- `../analyzing-tls-config/references/AUTHORIZATION.md` — Active-scan
  authorization pattern
