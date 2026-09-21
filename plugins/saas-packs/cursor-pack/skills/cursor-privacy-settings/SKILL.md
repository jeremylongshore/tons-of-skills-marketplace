---
name: cursor-privacy-settings
description: 'Configure Cursor privacy mode, data handling, telemetry, and sensitive
  file exclusion. Triggers on

  "cursor privacy", "cursor data", "cursor security", "privacy mode", "cursor telemetry",

  "cursor data retention".

  '
allowed-tools: Read, Write, Edit, Bash(cmd:*)
version: 1.19.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- cursor
- security
compatibility: Designed for Claude Code
---
# Cursor Privacy Settings

## Overview

Configure Cursor data, privacy, and model-routing settings according to the repository's data classification and organization policy before code is added to AI context.

## Prerequisites

- A current data-classification decision, tenant owner, and approved provider/model policy.
- Authority to inspect or enforce tenant settings and a process for exceptions/incidents.

## Instructions

1. Select the approved privacy/data controls and verify their effective tenant/user state.
2. Configure `.cursorignore` and workspace trust to prevent secrets, customer data, and generated artifacts entering context.
3. Test the boundary with sanitized fixtures and retain redacted verification evidence.
4. Review settings after tenant, provider, policy, or data-classification changes.

## Output

- A verified privacy configuration and context-exclusion boundary for the intended workspace.

## Error Handling

| Condition | Safe response |
|---|---|
| Effective privacy setting is unclear | Do not use sensitive code; escalate to the tenant/security owner. |
| Sensitive path is included | Stop, remove/exclude it, and follow the exposure procedure. |
| Required setting conflicts with policy | Use the restrictive option and obtain a documented exception decision. |

## Examples

Before opening a production repository, verify the approved privacy mode, add known secret/export paths to reviewed ignore configuration, and test with a sanitized path. If the file can still be attached, stop onboarding the repository until the boundary is fixed.

Configure Cursor's privacy controls to protect your code and data. Covers Privacy Mode, data handling policies, file exclusion, telemetry, and enterprise security settings.

## Privacy Mode

### What Privacy Mode Does

| With Privacy Mode ON | With Privacy Mode OFF |
|---------------------|----------------------|
| Zero data retention at model providers | Providers may retain data per their policies |
| Code not used for training (Cursor or providers) | Code may be used to improve AI models |
| Embeddings computed without storing source | Same embedding behavior |
| Telemetry: anonymous usage only | Telemetry may include code snippets |

### Enabling Privacy Mode

**Individual:**
`Cursor Settings` > `General` > `Privacy Mode` > ON

**Team enforcement (Business/Enterprise):**
Admin Dashboard > Privacy > "Enforce Privacy Mode for all members"

When team-enforced:

- Individual users cannot disable Privacy Mode
- Client pings server every 5 minutes to verify enforcement
- New members automatically have Privacy Mode enabled

### Verifying Privacy Mode

1. `Cursor Settings` > `General` -- check Privacy Mode toggle
2. [cursor.com/settings](https://cursor.com/settings) -- shows account-level status
3. For teams: Admin Dashboard shows enforcement status per member

## Data Flow: Where Your Code Goes

```
Your Code in Editor
       │
       ├─► Tab Completion ──► Cursor's proprietary model server
       │                      (zero retention with Privacy Mode)
       │
       ├─► Chat/Composer ──► Model provider (OpenAI/Anthropic/Google)
       │                     (zero retention agreements in place)
       │
       ├─► Codebase Index ─► Cursor embedding API ─► Turbopuffer (vector DB)
       │                     (embeddings only, no plaintext code)
       │
       └─► BYOK ───────────► Your API provider directly
                             (your provider's data policy applies)
```

### What IS Stored

| Data | Stored Where | Retention |
|------|-------------|-----------|
| Embeddings (vectors) | Turbopuffer (cloud) | Until project re-indexed |
| Obfuscated file metadata | Cursor servers | Active session only |
| Anonymous telemetry | Cursor analytics | Aggregated, no PII |
| Account info | Cursor auth servers | While account active |

### What Is NOT Stored (Privacy Mode ON)

- Plaintext source code
- Chat prompts and responses
- File contents sent for completion
- Code snippets from Tab suggestions

## Sensitive File Exclusion

### .cursorignore (Best-Effort AI Exclusion)

```gitignore
# .cursorignore -- prevent files from AI features + indexing

# Credentials and secrets
.env
.env.*
.env.local
.env.production
**/secrets/
**/credentials/
**/*.pem
**/*.key
**/*.p12

# Regulated data
**/pii/
**/hipaa/
**/financial-data/

# Internal configuration
.cursor-config-private
infrastructure/terraform.tfvars
```

**Important:** `.cursorignore` is best-effort. Due to LLM unpredictability, it is not a hard security boundary. Do not rely solely on `.cursorignore` to protect truly sensitive data.

### Defense in Depth

```
Layer 1: .gitignore        → Secrets never in repo
Layer 2: .env files        → Config via environment variables
Layer 3: .cursorignore     → Best-effort AI exclusion
Layer 4: Privacy Mode      → Zero data retention at providers
Layer 5: BYOK + Azure      → Route through your own infrastructure
```

## Telemetry Configuration

### What Cursor Collects

With Privacy Mode ON, telemetry is limited to:

- Feature usage counts (how often Chat/Composer/Tab used)
- Error reports (crashes, not code content)
- Performance metrics (response times)
- Extension compatibility data

### Disabling Telemetry

```json
// settings.json
{
  "telemetry.telemetryLevel": "off"
}
```

Or: `Cursor Settings` > search "telemetry" > set to "off"

**Note:** Disabling telemetry may reduce Cursor's ability to diagnose issues affecting your account.

## Network Security

### Required Domains

Allowlist these domains in corporate firewalls/proxies:

```
api.cursor.com           → AI API requests
api2.cursor.com          → AI API requests (fallback)
auth.cursor.com          → Authentication
*.turbopuffer.com        → Codebase indexing (embeddings)
download.cursor.com      → Updates
```

### Proxy Configuration

```json
// settings.json
{
  "http.proxy": "http://proxy.corp.com:8080",
  "http.proxyStrictSSL": true,
  "http.proxyAuthorization": "Basic base64-encoded-credentials"
}
```

### TLS/SSL

All Cursor API communication uses TLS 1.2+. Certificate pinning is not supported, so corporate SSL inspection proxies work (add proxy CA to system trust store).

## Compliance Mapping

### SOC 2

| Control | Cursor Coverage |
|---------|----------------|
| CC6.1 Logical access | SSO, RBAC, MFA via IdP |
| CC6.6 System boundaries | Privacy Mode, .cursorignore |
| CC6.7 Data transmission | TLS 1.2+ for all API calls |
| CC7.2 Monitoring | Admin dashboard usage analytics |

### GDPR

| Requirement | Cursor Coverage |
|-------------|----------------|
| Data minimization | Privacy Mode: zero retention |
| Right to erasure | Account deletion removes all server-side data |
| Data processing agreement | Available on request (Enterprise) |
| Sub-processor list | Published at cursor.com/privacy |

### HIPAA

Cursor does not have a BAA (Business Associate Agreement) as of early 2026. For HIPAA-regulated code:

- Enable Privacy Mode
- Use `.cursorignore` for PHI-containing files
- Consider BYOK through Azure with BAA
- Consult your compliance team before use

## Enterprise Considerations

- **SOC 2 Type II report**: Available on request for Enterprise customers
- **Penetration test results**: Annual pen tests, results shared under NDA
- **Data residency**: Cursor processes requests via US and EU infrastructure. No region pinning available yet
- **Encryption**: AES-256 at rest, TLS 1.2+ in transit
- **Incident response**: Cursor maintains a security incident response plan (details in SOC 2 report)

## Resources

- [Cursor Privacy and Data Use](https://cursor.com/data-use)
- [Cursor Security](https://cursor.com/security)
- [Privacy and Data Governance Docs](https://docs.cursor.com/enterprise/privacy-and-data-governance)
- [Account Privacy Settings](https://docs.cursor.com/account/privacy)
