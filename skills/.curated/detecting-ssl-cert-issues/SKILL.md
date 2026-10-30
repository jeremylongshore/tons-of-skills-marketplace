---
name: detecting-ssl-cert-issues
description: |
  Audit a target's TLS certificate beyond protocol/expiry — chain ordering,
  OCSP stapling, revocation status, Certificate Transparency presence,
  key-usage flags, and over-broad wildcards.
  Use when: TLS handshake already passes (skill #1 analyzing-tls-config
  cleared) but you suspect the cert posture is fragile. Auditors flag this
  during SOC2 readiness when a renewal slipped or an intermediate was
  rotated.
  Threshold: missing OCSP stapling on production, fewer than 2 SCTs in
  the cert, intermediate served out of order, key usage missing
  digitalSignature/keyEncipherment, revoked cert presented, or wildcard
  scope of 2-level (e.g., *.com is rejection; *.api.example.com is fine).
  Trigger with: "check cert revocation", "audit ocsp", "ct log check",
  "cert chain audit".
allowed-tools:
  - Read
  - Bash(python3:*)
  - Bash(openssl:*)
disallowed-tools:
  - Bash(rm:*)
  - Edit(/etc/*)
  - Write(/etc/*)
version: 3.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - tls
  - ocsp
  - certificate-transparency
  - pentest
---

# Detecting SSL Certificate Issues

## Overview

This skill is the second-level cert audit, run after `analyzing-tls-config`
clears the protocol+cipher+expiry+hostname basics. It surfaces issues
that don't break the handshake today but make the cert fragile or open
to soft-bypass attacks: missing OCSP stapling forces clients to phone
home to the CA (privacy + latency hit), missing Certificate Transparency
SCTs are rejected by Chrome since 2018, an out-of-order chain confuses
older clients, and over-broad wildcards expand the blast radius of any
future key compromise.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Revoked certificate presented | **CRITICAL** | OCSP responder says "revoked" | RFC 6960 |
| Missing or invalid OCSP staple | **HIGH** | No status_request response on production | RFC 6066, CA/B BR |
| Fewer than 2 SCTs embedded | **HIGH** | CT-policy violation (Chrome enforces) | RFC 6962, CA/B Baseline Reqs |
| Intermediate served out of RFC 5246 order | **MEDIUM** | Server sends root before leaf | RFC 5246 §7.4.2 |
| AIA extension missing | **MEDIUM** | No CA Issuers / OCSP URL in cert | RFC 5280 §4.2.2.1 |
| Over-broad wildcard | **HIGH** | Scope of 2-level or wider (e.g., *.com) | CA/B Baseline Reqs §3.2.2 |
| Wildcard at apex SAN | **LOW** | *.example.com without example.com | RFC 6125 §6.4.3 |
| Key Usage missing digitalSignature | **MEDIUM** | KU bit absent for TLS server cert | RFC 5280 §4.2.1.3 |
| Cert chain longer than 4 | **LOW** | Performance + trust expansion | CA/B Baseline Reqs |

## Prerequisites

- Python 3.9+ with `cryptography` library
- `openssl` CLI 1.1.1+ (for OCSP query + chain enumeration)
- Authorization for non-local targets (see `references/AUTHORIZATION.md`
  in skill #1 `analyzing-tls-config` for the canonical pattern)

## Instructions

### Step 1 — Confirm Authorization

Active scan; ask the user verbatim:

> "Do you have authorization to perform TLS testing on this target?
> I need confirmation before proceeding."

### Step 2 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-ssl-cert-issues/scripts/check_cert_chain.py \
    https://target.example.com \
    --authorized
```

Options:

```
Usage: check_cert_chain.py URL [OPTIONS]

Options:
  --authorized       Attest authorization for non-local targets (required)
  --port PORT        Target port (default: 443)
  --output FILE      Write findings to FILE (default: stdout)
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV critical|high|medium|low|info (default: info)
  --timeout SECS     Per-probe timeout (default: 10)
  --skip-ocsp        Skip OCSP responder query (offline mode)
```

### Step 3 — Interpret findings

CRITICAL/HIGH map to immediate action items; MEDIUM/LOW to backlog
hardening. Cross-reference `references/PLAYBOOK.md` for OCSP stapling
config snippets per server type.

### Step 4 — Cross-skill chaining

- After this skill, suggest `checking-http-security-headers` (#4) to
  verify HSTS preload status — HSTS preload depends on a clean cert
  chain to be effective.
- For CI integration patterns, see `references/PLAYBOOK.md` § CI
  posture-monitoring.

## Examples

### Example 1 — OCSP stapling audit before adopting must-staple

User: "We're considering Must-Staple — what's our OCSP stapling posture
look like across endpoints?"

```bash
for ENDPOINT in https://api.example.com https://app.example.com https://admin.example.com; do
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-ssl-cert-issues/scripts/check_cert_chain.py \
      "$ENDPOINT" --authorized --min-severity medium
done
```

If any endpoint reports "Missing OCSP staple" HIGH, adopting Must-Staple
on that cert breaks it on next renewal until OCSP-stapling config
lands. Pair with `references/PLAYBOOK.md` § OCSP stapling for nginx /
Caddy / Apache config.

### Example 2 — CT-log compliance check before public launch

User: "Pre-launch — does our cert have enough SCTs for Chrome to trust it?"

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-ssl-cert-issues/scripts/check_cert_chain.py \
    https://new-site.example.com --authorized
```

The scanner extracts embedded SCTs from the cert's CT extension. <2
SCTs → HIGH finding; Chrome's CT enforcement policy rejects the
connection silently in HTTPS, leaving users with a generic error.

### Example 3 — Wildcard scope audit

User: "An auditor flagged our wildcard cert as too broad."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-ssl-cert-issues/scripts/check_cert_chain.py \
    https://example.com --authorized --format json | jq '.[] | select(.title | contains("wildcard"))'
```

The JSON output captures the wildcard scope; pair with the auditor's
request to either narrow the SAN list or move to per-service certs.

## Output

JSON / JSONL / Markdown per `lib/report.py`. Exit codes: 0 clean, 1
high/critical, 2 error.

## Error Handling

- **OCSP responder timeout** → emitted as MEDIUM finding (not an error
  exit) with note to investigate responder availability.
- **CT log lookup unavailable** → falls back to embedded-SCT parsing
  only; emits INFO note.
- **Untrusted cert** → out of scope (skill #1 handles); this skill assumes
  the chain validates and looks at deeper posture.

## Resources

- `references/THEORY.md` — OCSP, CT, AIA, chain ordering, wildcard
  scope reasoning with RFC anchors
- `references/PLAYBOOK.md` — OCSP stapling config per server type +
  CT-log compliance + AIA extension correctness
- `../analyzing-tls-config/references/AUTHORIZATION.md` — canonical ROE
  template + 2-step gate (shared across all active-scan skills)
