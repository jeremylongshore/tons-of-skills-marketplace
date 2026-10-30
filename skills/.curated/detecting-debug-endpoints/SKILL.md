---
name: detecting-debug-endpoints
description: |
  Probe a target for accidentally-public admin / debug / introspection
  endpoints — Spring Boot Actuator, Apache server-status, Prometheus
  metrics, GraphQL playground, Swagger UI, phpMyAdmin, JMX-over-HTTP
  (Jolokia), Elasticsearch _cat, Kibana / Grafana / Eureka / Consul
  panels.
  Use when: post-deploy verification, security audit before SOC2,
  inheriting a system you didn't build, or a bug bounty hints at an
  exposed introspection panel.
  Threshold: any of the canonical 40+ admin/debug paths returns 200,
  302 to a login, or framework-specific JSON shape (e.g., Actuator
  returning a _links object, server-status HTML body containing
  the Apache Server Status title).
  Trigger with: "check debug endpoints", "actuator exposure", "admin
  panel scan", "graphql playground check".
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
  - admin-panels
  - actuator
  - pentest
---

# Detecting Debug Endpoints

## Overview

Modern web stacks ship rich introspection by default. Spring Boot
Actuator exposes `/actuator/env` (every environment variable),
`/actuator/heapdump` (a live heap snapshot that contains credentials),
`/actuator/jolokia` (JMX bean invocation = pre-auth RCE in some
configurations). Apache `mod_status` exposes `/server-status` with
internal IPs, request counts, and the URL of every active request.
Prometheus `/metrics` exposes operational telemetry that often
includes connection-string-bearing labels by accident. phpMyAdmin
exposes the entire database if unauthenticated.

These are not bugs in the frameworks. They're features that ship
enabled-by-default for development convenience and stay enabled in
production because nobody disabled them at install time. The probe
set covers the canonical 40+ paths and grades each by the response
fingerprint specific to that framework.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Spring Boot Actuator `/env` exposed | **CRITICAL** | 200 + body has `"propertySources"` | OWASP A05:2021 |
| Spring Boot Actuator `/heapdump` exposed | **CRITICAL** | 200 + `Content-Type: application/octet-stream` + multi-MB body | CWE-200 |
| Spring Boot Actuator `/jolokia` exposed | **CRITICAL** | 200 + body has `"agent":"jolokia"` | CWE-749 |
| phpMyAdmin reachable | **CRITICAL** | 200 + HTML body contains "phpMyAdmin" + login form | OWASP A07:2021 |
| Prometheus `/metrics` exposed | **HIGH** | 200 + body has `# HELP` or `# TYPE` lines | CWE-200 |
| Apache `mod_status` exposed | **HIGH** | 200 + body contains "Apache Server Status" | CWE-200 |
| Spring Boot Actuator `/actuator` index | **HIGH** | 200 + body has `"_links"` JSON | OWASP A05:2021 |
| Generic `/admin` returning 200 (not 401/403) | **HIGH** | 200 + HTML body with admin-shaped UI | CWE-285 |
| Elasticsearch `_cat` exposed | **HIGH** | 200 + body matches `health\s+status\s+index` | CWE-200 |
| GraphQL Playground on prod | **MEDIUM** | 200 + body contains `"GraphQLPlayground"` | CWE-200 |
| Swagger UI on prod | **MEDIUM** | 200 + body contains `"swagger-ui"` | CWE-200 |
| Spring Boot Actuator `/health` exposed | **MEDIUM** | 200 + body has `"status":"UP"` | CWE-200 |
| `phpinfo` page on prod | **MEDIUM** | 200 + body has `PHP Version` heading | CWE-200 |
| `/robots.txt` discloses admin paths | **LOW** | 200 + `Disallow:` lines mentioning `/admin` | CWE-200 |

## Prerequisites

- Python 3.9+ with `requests`
- Authorization for non-local targets

## Instructions

### Step 1 — Confirm Authorization

```text
"Do you have authorization to perform admin / debug endpoint
 discovery on this target? I need confirmation before proceeding."
```

### Step 2 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-debug-endpoints/scripts/probe_debug.py \
    https://target.example.com \
    --authorized
```

Options:

```
Usage: probe_debug.py URL [OPTIONS]

Options:
  --authorized       Attest authorization (required for non-local)
  --output FILE      Write findings to FILE
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --timeout SECS     Per-probe timeout (default: 10)
  --paths-file FILE  Override the default probe set with a custom list
  --include-redirects  Treat 302/303 to /login as findings (debug panel
                       exists but auth gates it — still worth noting)
```

The scanner sends a GET for each path. For 200 responses, it inspects
the body for the framework-specific fingerprint to confirm a true
positive (not the app's SPA index page). For 302 responses to common
login paths, the panel exists but auth is in front — flagged only
with `--include-redirects`.

### Step 3 — Interpret findings

CRITICAL = direct compromise vector (env vars / heapdump / Jolokia /
phpMyAdmin). Ship same-hour fix: take the endpoint behind authn or
disable it. Audit for prior exploitation.

HIGH = information disclosure substantial enough to drive subsequent
attacks (server-status reveals request URLs including session tokens
in query strings; /metrics labels often contain connection strings;
/admin reachable means brute-force can start).

MEDIUM = posture hardening (health checks, swagger).

### Step 4 — Cross-skill chaining

After this skill, suggest:

- `detecting-exposed-secrets-files` (#6) — same deploy mistake. If
  `/server-status` is reachable, `.git/` often is too.
- `auditing-cors-policy` (#3) — if a GraphQL or admin endpoint is
  reachable AND has open CORS, the attack chain compounds.

## Examples

### Example 1 — Inheriting a system audit

User: "We just acquired example.io. Quick audit of admin surface."

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-debug-endpoints/scripts/probe_debug.py \
    https://example.io --authorized --min-severity medium
```

Commonly surfaces forgotten `/server-status` on Apache hosts,
`/actuator/*` left enabled from Spring Boot defaults, leftover
`/phpmyadmin` from initial install.

### Example 2 — Spring Boot Actuator paranoia sweep

User: "We use Spring Boot heavily. Show me everywhere Actuator is
reachable."

```bash
for ENDPOINT in $(cat spring-services.txt); do
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-debug-endpoints/scripts/probe_debug.py \
      "$ENDPOINT" --authorized --format jsonl
done | jq 'select(.title | contains("Actuator"))'
```

### Example 3 — CI gate against accidental re-enablement

```yaml
- name: Debug-endpoint guard
  run: |
    python3 plugins/security/penetration-tester/skills/detecting-debug-endpoints/scripts/probe_debug.py \
        "${{ secrets.STAGING_URL }}" \
        --authorized --min-severity high
```

Exit 1 fails the deploy if any HIGH or CRITICAL endpoint exposure
appears. Catches the regression where a debug profile gets enabled
in a `application-prod.yml` by accident.

## Output

JSON / JSONL / Markdown per `lib/report.py`. Exit codes: 0 clean, 1
high/critical, 2 error.

## Error Handling

- **SPA catches every URL with 200** → use `--check-only` semantics
  (default: fingerprint check filters out SPA matches).
- **WAF / CDN blocks the scanner** → expected for some targets.
  Coordinate with the target's security team for an allowlist; or
  run the scanner from inside the target's network if you have
  authorized internal access.
- **Connection error** → exit 2 with underlying error.

## Resources

- `references/THEORY.md` — Per-framework reasoning: why Actuator,
  mod_status, Prometheus, GraphQL Playground, Swagger, phpMyAdmin
  each matter; canonical fingerprints
- `references/PLAYBOOK.md` — Per-framework remediation: Spring Boot
  Actuator authn, Apache mod_status `<Location>` deny, Prometheus
  Bearer-token, GraphQL introspection toggle, Swagger profile gate
- `../analyzing-tls-config/references/AUTHORIZATION.md` — Active-scan
  authorization pattern
