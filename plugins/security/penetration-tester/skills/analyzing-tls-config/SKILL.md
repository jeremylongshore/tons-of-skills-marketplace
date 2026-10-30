---
name: analyzing-tls-config
description: |
  Analyze a target's TLS configuration — negotiated protocol version, cipher
  suite, certificate chain, expiry, and downgrade vectors.
  Use when: SOC2 auditor flagged your endpoint for "weak TLS" but you don't
  know which control failed (TSC CC6.7 transmission integrity vs CC6.6
  encryption) or which cipher is the problem.
  Threshold: any negotiated TLSv1.0 or TLSv1.1, OR a cipher with RC4 / 3DES /
  null / EXPORT, OR a cert with under 30 days to expiry, OR a chain that fails
  hostname verification.
  Trigger with: "audit tls", "check ssl config", "weak tls", "analyze tls".
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
  - ssl
  - pentest
  - transport-layer
---

# Analyzing TLS Configuration

## Overview

This skill audits a target's TLS posture against current best practice
(NIST SP 800-52r2, Mozilla TLS Configuration Guidelines, PCI DSS v4.0 Req
4.2.1.1). It reports specific findings — not "your TLS is weak" but
"your server negotiated TLSv1.0 with RC4-SHA — see remediation".

## When the skill produces findings

Specific failure thresholds, in order of severity:

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| TLSv1.0 or TLSv1.1 negotiated | **HIGH** | Any handshake completes at v1.0/v1.1 | NIST 800-52r2 §3.1, PCI DSS Req 4.2.1.1 |
| Null / EXPORT / anonymous cipher | **CRITICAL** | Any null / EXPORT / aNULL in negotiated suite | NIST 800-52r2 §3.3.1 |
| RC4 / 3DES cipher | **HIGH** | Sweet32, RC4 biases | NIST 800-52r2 §3.3.1, PCI DSS Req 4.2.1.1 |
| Cert expires in <7 days | **CRITICAL** | notAfter - now ≤ 7d | NIST 800-52r2 §4.1 |
| Cert expires in <30 days | **HIGH** | notAfter - now ≤ 30d | NIST 800-52r2 §4.1 |
| Cert hostname mismatch | **HIGH** | SAN/CN doesn't match target host | RFC 6125 |
| Self-signed or untrusted CA | **MEDIUM** | Chain doesn't validate to system CA | Mozilla TLS Guidelines |
| Weak key (RSA < 2048, ECDSA < 256) | **HIGH** | Public key bits below threshold | NIST 800-52r2 §3.4 |
| Forward secrecy absent | **MEDIUM** | No ECDHE / DHE in negotiated suite | NIST 800-52r2 §3.3.1 |

## Prerequisites

- Python 3.9+
- `openssl` CLI (used for cipher enumeration the Python `ssl` module can't introspect directly)
- Authorization to test the target (active scan — see `references/AUTHORIZATION.md`)

## Instructions

### Step 1 — Confirm Authorization

Active scan. Before invoking the scanner, ask the user verbatim:

> "Do you have authorization to perform TLS testing on this target?
> I need confirmation before proceeding."

If the user says yes, proceed. If unsure, ask them to obtain written
authorization. See `references/AUTHORIZATION.md` for the attestation
pattern. **Never run the scanner against a target the user does not own
or have written permission to test.**

### Step 2 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/analyzing-tls-config/scripts/analyze_tls.py \
    https://target.example.com \
    --authorized
```

The `--authorized` flag is required for any non-loopback / non-RFC1918
target (gate enforced in `lib/authz_check.py`).

Options:

```
Usage: analyze_tls.py URL [OPTIONS]

Options:
  --authorized          Attest authorization for non-local targets (required)
  --port PORT           Target port (default: 443)
  --output FILE         Write findings to FILE (default: stdout)
  --format FMT          json | jsonl | markdown (default: markdown)
  --min-severity SEV    Floor: critical|high|medium|low|info (default: info)
  --timeout SECS        Per-probe timeout (default: 10)
```

### Step 3 — Interpret findings

The scanner emits one `Finding` per detected issue. For each:

1. Read the **severity** band — CRITICAL and HIGH require immediate action.
2. Read the **affected control** — map to the framework the user is audited against.
3. Read the **remediation** — copy-paste-ready config snippets for nginx /
   Caddy / Apache / HAProxy / AWS ALB / GCP LB.
4. Cross-reference `references/PLAYBOOK.md` for the full template if the
   inline remediation is just a one-liner.

### Step 4 — Report to user

Group findings by severity. For each, lead with the specific symptom
("TLSv1.0 negotiated") rather than the category ("transport security
problem"). Pair every finding with one remediation step the user can
take in the next 30 minutes.

### Step 5 — Cross-skill chaining (optional)

If the user is doing a broader audit:

- After this skill runs, suggest **`detecting-ssl-cert-issues`** (skill #2)
  for deeper cert-chain analysis (revocation, CT log presence,
  intermediate-cert order).
- For HTTP-layer security headers that complement TLS findings, suggest
  **`checking-http-security-headers`** (skill #4) to audit HSTS preload
  status, which is meaningless without proper TLS.

## Examples

### Example 1 — SOC2 audit prep on a production endpoint

User says: "Auditor flagged our checkout endpoint for weak TLS. Help me figure out what's wrong."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/analyzing-tls-config/scripts/analyze_tls.py \
    https://checkout.example.com \
    --authorized \
    --min-severity high
```

Expected output: a Markdown report with each HIGH/CRITICAL finding, the
specific NIST/PCI control it violates, and a copy-paste remediation
snippet for the target server type. Pair with `references/PLAYBOOK.md`
for full templates.

### Example 2 — CI integration on a staging gate

Pin the scan into the deploy pipeline before promotion:

```yaml
- name: TLS posture check (staging)
  run: |
    python3 plugins/security/penetration-tester/skills/analyzing-tls-config/scripts/analyze_tls.py \
        https://staging.example.com \
        --authorized \
        --min-severity high \
        --format json \
        --output tls-report.json
```

Exit code 1 fails the deploy if any HIGH/CRITICAL finding lands. The
JSON report uploads as a build artifact for the security team to
triage.

### Example 3 — Quick local check during dev

For local services (carve-out applies — no `--authorized` needed):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/analyzing-tls-config/scripts/analyze_tls.py \
    https://localhost:8443
```

Useful when prototyping TLS-terminating proxies (Caddy, Traefik) before
shipping to staging.

## Output

Each finding includes:

- `skill_id`: `analyzing-tls-config`
- `title`: imperative — e.g. "Server negotiates obsolete TLSv1.0"
- `severity`: critical / high / medium / low / info
- `target`: the URL scanned
- `detail`: technical explanation of WHY this finding triggered
- `remediation`: specific fix
- `cvss_score` / `cwe_id`: when applicable
- `affected_control`: framework + control ID (e.g. `NIST 800-52r2 §3.1`)
- `references`: source URLs

JSON output is pipeable to `jq` for CI integration. Markdown output is
human-readable for direct sharing with the engineering team.

Exit codes: `0` clean (no high/critical), `1` findings (high or critical),
`2` error (auth missing, target unreachable, unparseable input).

## Error Handling

**`--authorized` missing for non-local target** → exit 2 with attestation
message pointing to `references/AUTHORIZATION.md`. Re-run with the flag
after confirming authorization.

**Target unreachable** → exit 2 with the underlying socket error. Common
causes: firewall blocks port 443, DNS resolution failure, server not
listening on the configured port (try `--port`).

**Certificate chain incomplete** → finding emitted at MEDIUM severity (the
scanner does not bail; it captures what was sent and reports the gap).

## Resources

- `references/THEORY.md` — How TLS negotiation works, why each finding
  matters, primary RFC references
- `references/PLAYBOOK.md` — Copy-paste remediation templates per finding
  for nginx, Caddy, Apache, HAProxy, AWS ALB, GCP LB
- `references/AUTHORIZATION.md` — Authorization attestation pattern + ROE
  example for active scans
