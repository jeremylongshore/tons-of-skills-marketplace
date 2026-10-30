---
name: checking-http-security-headers
description: |
  Audit a target's HTTP security headers — CSP, HSTS, X-Frame-Options,
  X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and the
  Cross-Origin trio (COOP, COEP, CORP).
  Use when: SOC2 / PCI auditor flagged "missing security headers" or a
  Mozilla Observatory grade is below B, OR you need HSTS preload
  eligibility for chrome://net-internals.
  Threshold: any missing required header on production HTML response,
  HSTS max-age below 31536000s (preload requirement), CSP with
  'unsafe-inline' or 'unsafe-eval', X-Frame-Options absent AND CSP
  frame-ancestors absent (clickjacking), Cache-Control allowing public
  cache on authenticated endpoint.
  Trigger with: "audit security headers", "check csp", "hsts check",
  "header posture".
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
  - http-headers
  - csp
  - hsts
  - pentest
---

# Checking HTTP Security Headers

## Overview

HTTP response headers are the cheapest defense-in-depth layer most web
apps ship. Each header closes one specific attack class — HSTS forces
HTTPS, CSP blocks script injection, X-Frame-Options blocks clickjacking,
etc. Missing headers don't break the app; they just leave the attack
class open. This skill probes for the presence + value correctness of
the canonical security-relevant headers.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| HSTS header missing | **HIGH** | No Strict-Transport-Security on HTTPS response | OWASP A05:2021 |
| HSTS max-age below preload threshold | **MEDIUM** | max-age under 31536000s (1y) | hstspreload.org |
| HSTS includeSubDomains missing for preload | **LOW** | preload directive without includeSubDomains | hstspreload.org |
| CSP header missing | **HIGH** | No Content-Security-Policy header | OWASP A03:2021 |
| CSP allows unsafe-inline | **MEDIUM** | script-src or style-src includes 'unsafe-inline' | OWASP A03:2021 |
| CSP allows unsafe-eval | **MEDIUM** | script-src includes 'unsafe-eval' | OWASP A03:2021 |
| CSP frame-ancestors AND X-Frame-Options both missing | **HIGH** | Clickjacking open | CWE-1021 |
| X-Content-Type-Options:nosniff missing | **MEDIUM** | MIME-sniff attack open | OWASP A05:2021 |
| Referrer-Policy missing or unsafe-url | **MEDIUM** | Cross-origin URL leakage | OWASP A05:2021 |
| Permissions-Policy missing | **LOW** | Camera/mic/geo permissions unrestricted | Permissions Policy spec |
| Server: header discloses version | **LOW** | nginx/1.18.0 → fingerprintable | CWE-200 |
| Cache-Control public on authenticated response | **HIGH** | Shared cache may serve user A's response to user B | CWE-525 |

## Prerequisites

- Python 3.9+
- Authorization for non-local targets

## Instructions

### Step 1 — Confirm authorization

```text
"Do you have authorization to perform header testing on this target?
 I need confirmation before proceeding."
```

### Step 2 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/checking-http-security-headers/scripts/check_headers.py \
    https://example.com \
    --authorized
```

Options:

```
Usage: check_headers.py URL [OPTIONS]

Options:
  --authorized       Attest authorization (required for non-local)
  --output FILE
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --timeout SECS     Per-probe timeout (default: 10)
  --authenticated    Treat as authenticated endpoint (stricter Cache-Control gate)
```

### Step 3 — Interpret findings

HIGH = open exploitable class (no HSTS = MITM downgrade open; no CSP =
XSS class wide open; no clickjacking guard = UI-redress attacks).
MEDIUM/LOW = posture hardening.

### Step 4 — Cross-skill chaining

- After this skill, suggest `auditing-cors-policy` (#3) — CSP and CORS
  interact; certain CSP directives need matching CORS headers.
- For HSTS preload submission, see `references/PLAYBOOK.md` § HSTS
  preload checklist.

## Examples

### Example 1 — Mozilla Observatory grade improvement

User: "Observatory gives us a D. What's missing?"

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/checking-http-security-headers/scripts/check_headers.py \
    https://example.com \
    --authorized \
    --format markdown
```

The Markdown report groups by severity; map each finding to the
`PLAYBOOK.md` snippet for the target server type. Observatory grade
typically moves D → B after addressing all HIGH findings.

### Example 2 — HSTS preload eligibility pre-submission

User: "We want to submit to hstspreload.org. Is our HSTS config ready?"

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/checking-http-security-headers/scripts/check_headers.py \
    https://example.com \
    --authorized --min-severity low
```

Look for "HSTS max-age below preload threshold" and "includeSubDomains
missing" — both must clear before submission, OR hstspreload.org will
reject.

### Example 3 — Authenticated-endpoint Cache-Control sweep

User: "We had a Cache-Control bug last quarter where authenticated
responses got cached publicly. Audit /api/* to make sure it's fixed."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/checking-http-security-headers/scripts/check_headers.py \
    https://api.example.com/me \
    --authorized --authenticated
```

The `--authenticated` flag bumps Cache-Control posture from MEDIUM to
HIGH and adds a check for `Cache-Control: public` (forbidden on
authenticated content).

## Output

JSON / JSONL / Markdown. Exit codes 0 / 1 / 2 per `lib/report.py`.

## Error Handling

- **No HTML response** → INFO finding noting headers may not apply
  (JSON APIs use a subset of headers).
- **Redirect to login** → follows once, audits the destination page.
- **Connection error** → exit 2.

## Resources

- `references/THEORY.md` — Per-header reasoning, attack-class mapping
- `references/PLAYBOOK.md` — Config snippets per server type for each
  required header
- `../analyzing-tls-config/references/AUTHORIZATION.md` — Active-scan
  authorization
