---
name: sentry-security-basics
description: 'Configure Sentry security settings and data protection.

  Use when setting up PII scrubbing, managing sensitive data,

  configuring data scrubbing rules, or hardening Sentry for compliance.

  Trigger with phrases like "sentry security", "sentry PII",

  "sentry data scrubbing", "secure sentry", "sentry GDPR".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(grep:*), Bash(curl:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- security
- pii
- data-scrubbing
- gdpr
compatibility: Designed for Claude Code
---
# Sentry Security Basics

## Overview

Configure Sentry's security posture: PII scrubbing with `beforeSend`, built-in data scrubbing, IP anonymization, browser SDK URL filtering, DSN vs auth token handling, CSP reporting, and GDPR data deletion. Covers both client-side (SDK) and server-side (dashboard) controls.

## Prerequisites

- Sentry project created with Owner or Admin role
- `@sentry/node` >= 8.x or `@sentry/browser` >= 8.x installed (or `sentry-sdk` >= 2.x for Python)
- Compliance requirements identified (GDPR, SOC 2, HIPAA, CCPA)
- List of sensitive data patterns for your domain (PII fields, API keys, tokens)

## Instructions

### Step 1 — Understand DSN vs Auth Token Security

The DSN (Data Source Name) is a **client-facing identifier** — it tells the SDK where to send events. It is NOT a secret.

```
https://<public-key>@o<org-id>.ingest.us.sentry.io/<project-id>
```

- The DSN **cannot** read data, delete events, or modify settings
- It is safe to ship in client-side JavaScript bundles
- Restrict abuse via **Allowed Domains** (Project Settings > Client Keys > Configure)

Auth tokens **ARE secrets** — they grant API access to read/write/delete data:

```bash
# NEVER commit auth tokens — store in CI secrets or vault
# GitHub Actions: Settings > Secrets > SENTRY_AUTH_TOKEN
# GitLab CI: Settings > CI/CD > Variables (protected + masked)

# Generate tokens with MINIMAL scopes:
#   CI releases:   project:releases, org:read
#   Issue triage:  project:read, event:read
#   NEVER:         org:admin, member:admin in CI

# Rotate tokens quarterly — revoke unused tokens immediately
# Create separate tokens per pipeline (staging vs production)
```

### Step 2 — Disable Default PII Collection

`sendDefaultPii` defaults to `false` — but always set it explicitly so intent is clear:

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  sendDefaultPii: false, // explicit: no IPs, no cookies, no user-agent
});
```

When `sendDefaultPii: false` (default):

- **No IP addresses** attached to events
- **No cookies** sent in request data
- **No user-agent** strings in request headers
- **No request body** data captured
- User context must be set manually via `Sentry.setUser()`

```python
# Python equivalent
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    send_default_pii=False,  # default, but be explicit
)
```

### Step 3 — Client-Side PII Scrubbing with beforeSend

`beforeSend` runs before every event leaves the client. Use it to strip PII that leaks into error messages, request data, or breadcrumbs:

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  sendDefaultPii: false,

  beforeSend(event, hint) {
    // --- Scrub sensitive headers ---
    if (event.request?.headers) {
      delete event.request.headers['Authorization'];
      delete event.request.headers['Cookie'];
      delete event.request.headers['X-Api-Key'];
      delete event.request.headers['X-Auth-Token'];
    }

    // --- Scrub request body fields ---
    if (event.request?.data) {
      try {
        const data = typeof event.request.data === 'string'
          ? JSON.parse(event.request.data)
          : { ...event.request.data };

        const sensitiveKeys = [
          'password', 'passwd', 'secret', 'token',
          'ssn', 'credit_card', 'card_number', 'cvv',
          'api_key', 'apiKey', 'access_token', 'refresh_token',
        ];
        for (const key of Object.keys(data)) {
          if (sensitiveKeys.some(s => key.toLowerCase().includes(s))) {
            data[key] = '[REDACTED]';
          }
        }
        event.request.data = JSON.stringify(data);
      } catch {
        // non-JSON body — leave as-is
      }
    }

    // --- Scrub PII from exception messages ---
    if (event.exception?.values) {
      for (const exc of event.exception.values) {
        if (exc.value) {
          // Email addresses
          exc.value = exc.value.replace(
            /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
            '[EMAIL_REDACTED]'
          );
          // IPv4 addresses
          exc.value = exc.value.replace(
            /\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/g,
            '[IP_REDACTED]'
          );
          // Credit card numbers (with optional separators)
          exc.value = exc.value.replace(
            /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g,
            '[CC_REDACTED]'
          );
          // Bearer tokens in messages
          exc.value = exc.value.replace(
            /Bearer\s+[A-Za-z0-9\-._~+/]+=*/g,
            'Bearer [TOKEN_REDACTED]'
          );
        }
      }
    }

    // --- Scrub user context ---
    if (event.user) {
      delete event.user.email;
      delete event.user.ip_address;
      // Keep event.user.id for issue grouping (non-PII identifier)
    }

    return event;
  },
});
```

Python equivalent using `before_send`:

```python
import re

def before_send(event, hint):
    # Scrub emails from exception messages
    if 'exception' in event:
        for exc in event['exception'].get('values', []):
            if exc.get('value'):
                exc['value'] = re.sub(
                    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                    '[EMAIL_REDACTED]',
                    exc['value']
                )
                exc['value'] = re.sub(
                    r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
                    '[IP_REDACTED]',
                    exc['value']
                )

    # Strip user PII
    if 'user' in event:
        event['user'].pop('email', None)
        event['user'].pop('ip_address', None)

    # Scrub request headers
    request = event.get('request', {})
    headers = request.get('headers', {})
    for key in ['Authorization', 'Cookie', 'X-Api-Key']:
        headers.pop(key, None)

    return event

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    send_default_pii=False,
    before_send=before_send,
)
```

### Step 4 — Server-Side Data Scrubbing Rules

Configure in **Project Settings > Security & Privacy**:

| Setting | What it does |
|---------|-------------|
| **Data Scrubber** | Auto-scrubs fields matching common PII patterns (enabled by default) |
| **Sensitive Fields** | Custom field names to always scrub: `password`, `ssn`, `credit_card_number`, `api_key`, `secret`, `token`, `authorization` |
| **Safe Fields** | Fields excluded from scrubbing (e.g., `transaction_id`, `correlation_id`) |
| **Scrub IP Addresses** | Removes or zeroes IP addresses on all events |
| **Scrub Credit Cards** | Detects and removes card number patterns |

Organization-wide defaults: **Organization Settings > Security & Privacy** applies to all projects unless overridden at project level.

Advanced scrubbing rules (regex-based) can target specific event paths:

```
# Example server-side rules (configure in UI):
# Pattern: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
# Target:  $message, $error.value, $extra.**
# Action:  Replace with [Filtered]

# Pattern: \b\d{3}-\d{2}-\d{4}\b
# Target:  $extra.**, $contexts.**
# Action:  Replace with [Filtered] (SSN pattern)
```

### Step 5 — Browser SDK URL Filtering

Use `denyUrls` and `allowUrls` to control which scripts generate captured errors:

```typescript
Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // Ignore errors from third-party scripts
  denyUrls: [
    /extensions\//i,           // Browser extensions
    /^chrome:\/\//i,           // Chrome internal
    /^chrome-extension:\/\//i, // Chrome extensions
    /^moz-extension:\/\//i,    // Firefox extensions
    /graph\.facebook\.com/i,   // Facebook SDK
    /connect\.facebook\.net/i, // Facebook SDK
    /cdn\.jsdelivr\.net/i,     // CDN-hosted third-party
  ],

  // Only capture errors from your own code
  allowUrls: [
    /https?:\/\/(www\.)?example\.com/i,
    /https?:\/\/staging\.example\.com/i,
  ],
});
```

Also configure **Allowed Domains** in **Project Settings > Client Keys (DSN) > Configure** to prevent unauthorized origins from sending events to your DSN:

```
example.com
*.example.com
staging.example.com
```

### Step 6 — CSP Reporting via Sentry

Sentry can ingest Content-Security-Policy violation reports. Use the **Security Headers** endpoint (not the main DSN):

```
# Find the report URI in Project Settings > Security Headers
# Format: https://o<org-id>.ingest.us.sentry.io/api/<project-id>/security/?sentry_key=<public-key>
```

Add to your CSP header:

```
Content-Security-Policy: default-src 'self'; script-src 'self'; report-uri https://o123456.ingest.us.sentry.io/api/789/security/?sentry_key=abc123
```

Or use the newer `report-to` directive:

```
Report-To: {"group":"sentry","max_age":86400,"endpoints":[{"url":"https://o123456.ingest.us.sentry.io/api/789/security/?sentry_key=abc123"}]}
Content-Security-Policy: default-src 'self'; report-to sentry
```

### Step 7 — GDPR Data Deletion

Sentry supports right-to-erasure requests via API:

```bash
# Delete a specific issue and all its events
curl -X DELETE \
  -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/issues/$ISSUE_ID/"

# Delete events by tag (find issues for a specific user first)
curl -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/issues/?query=user.id:$USER_ID" \
  | jq '.[].id' \
  | xargs -I{} curl -X DELETE \
    -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
    "https://sentry.io/api/0/projects/$SENTRY_ORG/$SENTRY_PROJECT/issues/{}/"
```

For bulk deletion, use **Organization Settings > Data Privacy > Data Removal Requests** (Business/Enterprise plans).

Data retention settings: **Organization Settings > Subscription > Event Retention** — configure 30/60/90-day retention windows to auto-purge old data.

### Step 8 — Auth Token Hygiene Checklist

```bash
# Scan codebase for leaked auth tokens
grep -rn "sntrys_" --include="*.ts" --include="*.js" --include="*.py" \
  --include="*.env*" --include="*.yaml" --include="*.yml" \
  --exclude-dir=node_modules --exclude-dir=.git .

# Sentry auth tokens start with "sntrys_" — any match is a leak
# If found: revoke immediately at sentry.io/settings/auth-tokens/
```

Token best practices:

- **Separate tokens per environment** — never share between dev/staging/production
- **Minimal scopes** — `project:releases` + `org:read` for CI source map uploads
- **Set expiration dates** — 90 days max for CI tokens
- **Rotate quarterly** — calendar reminder, automate if possible
- **Audit via API** — `GET /api/0/api-tokens/` to list all active tokens

## Output

After completing these steps you will have:

- `sendDefaultPii: false` set explicitly in SDK init
- `beforeSend` callback stripping emails, IPs, credit cards, auth headers, and tokens from events
- Server-side data scrubber enabled with custom sensitive field list
- `denyUrls` / `allowUrls` filtering out third-party noise in browser projects
- Allowed Domains restricting which origins can send events
- CSP `report-uri` configured for security header violation reporting
- GDPR deletion workflow documented and tested
- Auth tokens stored in CI secrets with minimal scopes and expiration dates

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| PII appears in captured events | `sendDefaultPii: true` or PII embedded in error messages | Set `sendDefaultPii: false`; add `beforeSend` scrubbing for error message patterns |
| Auth token leaked in repo | Token committed to version control | Revoke at sentry.io/settings/auth-tokens/ immediately; rotate; add `sntrys_` pattern to `.gitignore` and pre-commit hooks |
| Events from unknown domains | DSN used by unauthorized origins | Configure Allowed Domains in Project Settings > Client Keys > Configure |
| CSP reports not appearing | Wrong report URI or missing `sentry_key` param | Use the Security Headers endpoint from Project Settings, not the main DSN |
| `beforeSend` drops all events | Callback returns `null` instead of `event` | Ensure every code path returns the `event` object; return `null` only to intentionally drop |
| Server scrubber too aggressive | Safe fields being redacted | Add field names to the Safe Fields list in Security & Privacy settings |
| GDPR delete returns 403 | Auth token missing `project:admin` scope | Generate a new token with `project:admin` scope for deletion operations |

## Examples

### TypeScript — Full Production Init

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  sendDefaultPii: false,

  beforeSend(event, hint) {
    // Strip PII from exception values
    event.exception?.values?.forEach(exc => {
      if (exc.value) {
        exc.value = exc.value
          .replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[EMAIL]')
          .replace(/\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/g, '[IP]')
          .replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '[CC]');
      }
    });

    // Strip auth headers
    if (event.request?.headers) {
      delete event.request.headers['Authorization'];
      delete event.request.headers['Cookie'];
    }

    // Scrub user PII, keep ID for grouping
    if (event.user) {
      event.user = { id: event.user.id };
    }

    return event;
  },

  beforeSendTransaction(event) {
    // Scrub PII from transaction names (e.g., /users/john@example.com/profile)
    if (event.transaction) {
      event.transaction = event.transaction.replace(
        /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
        '[EMAIL]'
      );
    }
    return event;
  },
});
```

### Python — Django with PII Scrubbing

```python
import os
import re
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
IP_RE = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

def before_send(event, hint):
    # Scrub exception messages
    for exc in event.get('exception', {}).get('values', []):
        if exc.get('value'):
            exc['value'] = EMAIL_RE.sub('[EMAIL]', exc['value'])
            exc['value'] = IP_RE.sub('[IP]', exc['value'])

    # Strip sensitive headers
    headers = event.get('request', {}).get('headers', {})
    for h in ['Authorization', 'Cookie', 'X-Api-Key']:
        headers.pop(h, None)

    # Scrub user PII
    user = event.get('user', {})
    user.pop('email', None)
    user.pop('ip_address', None)

    return event

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[DjangoIntegration()],
    send_default_pii=False,
    before_send=before_send,
    traces_sample_rate=0.1,
)
```

## Resources

- [Scrubbing Sensitive Data](https://docs.sentry.io/platforms/javascript/data-management/sensitive-data/)
- [Advanced Data Scrubbing](https://docs.sentry.io/security-legal-pii/scrubbing/advanced-datascrubbing/)
- [Security & Privacy Settings](https://docs.sentry.io/security-legal-pii/scrubbing/server-side-scrubbing/)
- [Auth Tokens](https://docs.sentry.io/api/guides/create-auth-token/)
- [GDPR & Data Privacy](https://docs.sentry.io/security-legal-pii/security/)
- Security Headers (CSP)

## Next Steps

- **sentry-alerts-config** — set up alert rules for security-related events
- **sentry-performance-monitoring** — configure tracing with PII-safe transaction names
- **sentry-release-tracking** — source map uploads with scoped auth tokens
