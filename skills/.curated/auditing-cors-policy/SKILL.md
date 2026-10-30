---
name: auditing-cors-policy
description: |
  Audit a target's CORS posture — Access-Control-Allow-Origin handling,
  reflected-origin bypass, credentials+wildcard mismatch, preflight
  OPTIONS behavior, Vary header correctness.
  Use when: a third-party integration is failing CORS preflight and
  someone proposes "just set Allow-Origin to *" as the fix, OR your
  bug-bounty inbox has a credential-reuse exploit chain.
  Threshold: any reflection of arbitrary Origin into Allow-Origin,
  Allow-Credentials:true with wildcard origin (browser-rejected combo
  but server config wrong), missing Vary:Origin on per-origin responses,
  preflight cached over 86400s, OR Allow-Origin trust of attacker-
  controlled subdomain pattern.
  Trigger with: "audit cors", "check cors policy", "cors bypass",
  "preflight check".
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
  - cors
  - web
  - pentest
---

# Auditing CORS Policy

## Overview

CORS misconfiguration is one of the most common middle-severity findings
in web bug bounties. The browser-enforced rules are subtle, the failure
modes are silent (the wrong cors response just works until an attacker
weaponizes it), and the "fix" engineers reach for —
`Access-Control-Allow-Origin: *` — opens the very class of attacks CORS
was meant to prevent when paired with credentials.

This skill probes each common CORS misconfiguration with synthetic
Origin headers and grades the response.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Origin reflected without validation | **HIGH** | Synthetic Origin `https://attacker.example` echoed in Allow-Origin | OWASP A05:2021 |
| Allow-Credentials:true with wildcard Allow-Origin | **CRITICAL** | Browser rejects but server is asserting the worst combo | OWASP A05:2021 |
| Allow-Credentials:true with reflected Origin | **CRITICAL** | Attacker site can read authenticated responses cross-origin | OWASP A05:2021, CWE-942 |
| Subdomain wildcard pattern bypass | **HIGH** | `Allow-Origin: *.example.com` matches `attacker.example.com.evil.com` | CWE-942 |
| Missing Vary:Origin on per-origin response | **MEDIUM** | CDN caches one origin's response for all origins | RFC 7234 |
| Preflight cache > 86400s | **LOW** | Access-Control-Max-Age over 24h limits revocation agility | MDN best practice |
| Null Origin trusted | **HIGH** | `Allow-Origin: null` accepted (sandboxed iframes, data: URLs) | CWE-942 |
| All HTTP methods permitted | **MEDIUM** | `Allow-Methods: *` enables CSRF-via-CORS for state-change | OWASP A05:2021 |

## Prerequisites

- Python 3.9+ (`requests` library)
- Authorization for non-local targets (`../analyzing-tls-config/references/AUTHORIZATION.md`)

## Instructions

### Step 1 — Confirm Authorization

```text
"Do you have authorization to perform CORS testing on this target?
 I need confirmation before proceeding."
```

### Step 2 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/auditing-cors-policy/scripts/audit_cors.py \
    https://api.example.com/endpoint \
    --authorized
```

Options:

```
Usage: audit_cors.py URL [OPTIONS]

Options:
  --authorized       Attest authorization for non-local targets (required)
  --output FILE      Write findings to FILE
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --timeout SECS     Per-probe timeout (default: 10)
  --method METHOD    HTTP method for the main probe (default: GET)
```

The scanner sends multiple probes per target:

1. Baseline request with no Origin header
2. Probe with safe Origin (https://allowed-origin.example.com)
3. Probe with attacker Origin (https://attacker.example)
4. Probe with subdomain-bypass Origin
5. Probe with Origin:null
6. OPTIONS preflight with Access-Control-Request-Headers / Method

For each, it records the response's CORS headers and grades against
the threshold table above.

### Step 3 — Interpret findings

CRITICAL = credential-stealing chain available; ship same-day fix.
HIGH = arbitrary cross-origin read of public-but-sensitive content;
ship within sprint.
MEDIUM/LOW = posture hardening; backlog.

### Step 4 — Cross-skill chaining

If CORS findings land alongside auth findings (skill #20 `confirming-
pentest-authorization` would have caught the auth side at engagement
scope), suggest `authentication-validator` plugin for full session-
handling audit.

## Examples

### Example 1 — Reflected-origin bug bounty triage

User: "Bug bounty submission claims CORS bypass on /api/profile."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/auditing-cors-policy/scripts/audit_cors.py \
    https://api.example.com/profile \
    --authorized \
    --format json | jq '.[] | select(.severity == "critical" or .severity == "high")'
```

If the reflected-origin probe + Allow-Credentials:true both fire, the
submission is valid; pay the bounty and ship the fix from `PLAYBOOK.md`.

### Example 2 — Pre-launch CORS sweep on a new API gateway

User: "We're rolling out a new gateway — audit every endpoint's CORS posture."

```bash
for ENDPOINT in $(cat endpoints.txt); do
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/auditing-cors-policy/scripts/audit_cors.py \
      "$ENDPOINT" --authorized --min-severity high --format jsonl >> cors-audit.jsonl
done
jq -s 'group_by(.severity) | map({sev: .[0].severity, count: length})' cors-audit.jsonl
```

### Example 3 — CI guard against CORS regression

Drop into deploy gate:

```yaml
- name: CORS posture gate
  run: |
    python3 plugins/security/penetration-tester/skills/auditing-cors-policy/scripts/audit_cors.py \
        https://staging-api.example.com/auth \
        --authorized \
        --min-severity high
```

Exit 1 fails the deploy if any new high/critical lands.

## Output

JSON / JSONL / Markdown per `lib/report.py`. Exit 0 clean, 1 high/
critical, 2 error.

## Error Handling

- **Target returns no CORS headers at all** → INFO finding "CORS not
  configured" with note that this is fine for non-cross-origin endpoints.
- **Preflight fails with 405** → MEDIUM finding suggesting OPTIONS
  handler missing.
- **Connection error** → exit 2 with underlying error.

## Resources

- `references/THEORY.md` — How CORS works, why each finding matters
- `references/PLAYBOOK.md` — Allow-list config templates per server
  type / framework (nginx, Express, Spring, FastAPI, Rails)
- `../analyzing-tls-config/references/AUTHORIZATION.md` — Active-scan
  authorization pattern
