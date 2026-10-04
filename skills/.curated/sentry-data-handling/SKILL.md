---
name: sentry-data-handling
description: 'Configure GDPR-compliant data handling, PII scrubbing, and data

  retention policies in Sentry. Use when implementing beforeSend

  filters, server-side data scrubbing rules, IP anonymization,

  data subject deletion requests, or SOC 2 audit controls.

  Trigger with phrases like "sentry pii scrubbing", "sentry gdpr",

  "sentry data privacy", "scrub sensitive data sentry",

  "sentry data retention", "sentry compliance".

  '
allowed-tools: Read, Write, Edit, Grep, Bash(curl:*), Bash(node:*)
version: 1.51.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- sentry
- security
- compliance
- gdpr
- pii
- data-privacy
compatibility: Designed for Claude Code
---
# Sentry Data Handling

Configure PII scrubbing, GDPR compliance, data retention, and audit controls for Sentry. This skill covers client-side filtering with `beforeSend`, server-side scrubbing rules, data subject erasure via API, and SOC 2 compliance patterns.

## Overview

Sentry captures error context that often contains personally identifiable information (PII) — emails in stack traces, credit card numbers in request bodies, IP addresses in headers. Production deployments must scrub this data at two layers: client-side via `beforeSend` hooks (before data leaves the application) and server-side via Sentry's built-in Data Scrubber (defense in depth). GDPR requires additional controls: consent-based initialization, data subject deletion endpoints, and a signed Data Processing Agreement. This skill implements all three layers with TypeScript and Python examples, plus verification tests to prove scrubbing works end-to-end.

## Prerequisites

- Sentry SDK v8 installed and initialized (`@sentry/node` or `sentry-sdk`)
- Sentry project with **Admin** or **Owner** role (required for Security & Privacy settings)
- Compliance requirements documented (GDPR, HIPAA, PCI-DSS, or SOC 2)
- Auth token with `project:write` and `org:admin` scopes for API operations
- Data Processing Agreement signed at https://sentry.io/legal/dpa/ (GDPR requirement)

## Instructions

### Step 1 — Client-Side PII Scrubbing with beforeSend

The first defense layer prevents PII from leaving your application. Configure `beforeSend`, `beforeSendTransaction`, and `beforeBreadcrumb` hooks during SDK initialization:

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // CRITICAL: disable automatic PII collection
  // When false, Sentry will NOT capture IP addresses, cookies, or user-agent
  sendDefaultPii: false,

  beforeSend(event) {
    return scrubEvent(event);
  },

  beforeSendTransaction(event) {
    return scrubEvent(event);
  },

  beforeBreadcrumb(breadcrumb) {
    if (breadcrumb.data) {
      const sensitiveKeys = ['password', 'token', 'secret', 'api_key', 'authorization'];
      for (const key of sensitiveKeys) {
        if (breadcrumb.data[key]) {
          breadcrumb.data[key] = '[REDACTED]';
        }
      }
    }
    return breadcrumb;
  },
});
```

Implement the `scrubEvent` function to strip PII from headers, request bodies, error messages, and user context:

```typescript
function scrubEvent(event: Sentry.Event): Sentry.Event | null {
  // Strip sensitive headers
  if (event.request?.headers) {
    const redactHeaders = ['Authorization', 'Cookie', 'X-Api-Key', 'X-Auth-Token'];
    for (const header of redactHeaders) {
      delete event.request.headers[header];
    }
  }

  // Scrub request body fields
  if (event.request?.data) {
    const data = typeof event.request.data === 'string'
      ? safeJsonParse(event.request.data)
      : event.request.data;

    if (data && typeof data === 'object') {
      scrubObject(data as Record<string, unknown>);
      event.request.data = JSON.stringify(data);
    }
  }

  // Scrub PII patterns from error messages
  if (event.exception?.values) {
    for (const exc of event.exception.values) {
      if (exc.value) {
        exc.value = scrubPiiPatterns(exc.value);
      }
    }
  }

  // Reduce user context to anonymous ID only
  if (event.user) {
    event.user = { id: event.user.id };
  }

  return event;
}

function scrubObject(obj: Record<string, unknown>): void {
  const sensitiveKeys = [
    'password', 'passwd', 'secret', 'token', 'api_key', 'apiKey',
    'ssn', 'social_security', 'credit_card', 'cc_number', 'cvv',
    'email', 'phone', 'address', 'dob', 'date_of_birth',
  ];

  for (const key of Object.keys(obj)) {
    if (sensitiveKeys.some(sk => key.toLowerCase().includes(sk))) {
      obj[key] = '[REDACTED]';
    } else if (typeof obj[key] === 'string') {
      obj[key] = scrubPiiPatterns(obj[key] as string);
    } else if (typeof obj[key] === 'object' && obj[key] !== null) {
      scrubObject(obj[key] as Record<string, unknown>);
    }
  }
}

function scrubPiiPatterns(str: string): string {
  return str
    .replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[EMAIL]')
    .replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{1,7}\b/g, '[CC_NUMBER]')
    .replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[SSN]')
    .replace(/\b(\+1)?[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}\b/g, '[PHONE]');
}

function safeJsonParse(str: string): unknown {
  try { return JSON.parse(str); } catch { return null; }
}
```

**Python equivalent** — use the same `before_send` pattern:

```python
import sentry_sdk
import re

def scrub_event(event, hint):
    """Remove PII from Sentry events before transmission."""
    # Strip sensitive headers
    request = event.get("request", {})
    headers = request.get("headers", {})
    for key in ["Authorization", "Cookie", "X-Api-Key"]:
        headers.pop(key, None)

    # Scrub user context to anonymous ID
    user = event.get("user")
    if user:
        event["user"] = {"id": user.get("id")}

    # Scrub PII patterns from exception messages
    for exc in event.get("exception", {}).get("values", []):
        if exc.get("value"):
            exc["value"] = re.sub(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "[EMAIL]", exc["value"]
            )

    return event

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    send_default_pii=False,
    before_send=scrub_event,
    traces_sample_rate=0.1,
)
```

### Step 2 — Server-Side Data Scrubbing and IP Anonymization

Server-side scrubbing acts as defense in depth. Configure in **Project Settings > Security & Privacy**:

1. **Enable Data Scrubber** — automatically redacts values matching common PII field names (password, token, secret)
2. **Custom Sensitive Fields** — add project-specific fields:
   - `password`, `secret`, `token`, `api_key`, `ssn`, `credit_card`, `cvv`, `authorization`
3. **Safe Fields** — fields that must never be scrubbed:
   - `transaction_id`, `order_id`, `request_id`, `trace_id`
4. **Scrub IP Addresses** — enable to remove client IPs from all events
5. **Scrub Credit Cards** — detect and remove card number patterns

For advanced regex-based rules, navigate to **Project Settings > Security & Privacy > Advanced Data Scrubbing**:

```
# Remove credit card patterns from all string fields
[Remove] [Regex: \d{4}-\d{4}-\d{4}-\d{4}] from [$string]

# Remove email addresses everywhere
[Remove] [Regex: \b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b] from [$string]

# Remove SSN patterns
[Remove] [Regex: \b\d{3}-\d{2}-\d{4}\b] from [$string]

# Mask passwords in request bodies
[Mask] [Password] from [extra.request_body]

# Replace credit card data everywhere with placeholder
[Replace] [Credit card] with [REDACTED] from [**]
```

**Data forwarding** — if forwarding events to external systems (Splunk, BigQuery), apply the same scrubbing rules at the destination. Configure forwarding in **Project Settings > Data Forwarding**.

**Data retention** — configure in **Organization Settings > Subscription > Data Retention**:

| Plan | Default retention | Maximum retention |
|------|-------------------|-------------------|
| Developer | 30 days | 30 days |
| Team | 90 days | 90 days |
| Business | 90 days | 365 days |
| Enterprise | 90 days | Custom |

### Step 3 — GDPR Compliance and Data Subject Requests

**Right to be Informed** — document Sentry usage in your privacy policy. Disclose what data is collected (stack traces, device info, anonymized user IDs) and the legal basis (legitimate interest in application reliability).

**Consent-based initialization** — for strict GDPR compliance, gate Sentry on user consent:

```typescript
function initSentryWithConsent(hasConsent: boolean): void {
  if (!hasConsent) {
    // Do not initialize Sentry — no data sent
    return;
  }

  Sentry.init({
    dsn: process.env.SENTRY_DSN,
    sendDefaultPii: false,
    beforeSend: scrubEvent,
  });
}
```

**Right to Erasure (Article 17)** — delete user data via the Sentry API:

```bash
# Delete all events for a specific issue
curl -X DELETE \
  -H "Authorization: Bearer ${SENTRY_AUTH_TOKEN}" \
  "https://sentry.io/api/0/projects/${SENTRY_ORG}/${SENTRY_PROJECT}/issues/${ISSUE_ID}/" \
  || { echo "ERROR: Deletion failed — verify auth token has project:admin scope"; exit 1; }
```

```typescript
// Programmatic deletion for data subject requests
async function handleDeletionRequest(userId: string): Promise<void> {
  const org = process.env.SENTRY_ORG;
  const project = process.env.SENTRY_PROJECT;
  const token = process.env.SENTRY_AUTH_TOKEN;

  // Search for issues containing user data
  const searchRes = await fetch(
    `https://sentry.io/api/0/projects/${org}/${project}/issues/?query=user.id:${userId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (!searchRes.ok) {
    throw new Error(`Search failed: ${searchRes.status} ${searchRes.statusText}`);
  }

  const issues = await searchRes.json();

  // Delete each matching issue
  for (const issue of issues) {
    const deleteRes = await fetch(
      `https://sentry.io/api/0/projects/${org}/${project}/issues/${issue.id}/`,
      { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } }
    );

    if (!deleteRes.ok) {
      throw new Error(`Deletion failed for issue ${issue.id}: ${deleteRes.status}`);
    }
  }

  console.log(`Deleted ${issues.length} issues for user ${userId}`);
}
```

**Audit log access** — Business and Enterprise plans provide audit logs at **Organization Settings > Audit Log**. Export via API for SOC 2 evidence:

```bash
# Retrieve audit log entries (requires org:admin scope)
curl -H "Authorization: Bearer ${SENTRY_AUTH_TOKEN}" \
  "https://sentry.io/api/0/organizations/${SENTRY_ORG}/audit-logs/" \
  || echo "ERROR: Audit logs require Business or Enterprise plan"
```

**SOC 2 compliance checklist:**

1. Enable audit logging (Business/Enterprise plan required)
2. Configure SSO/SAML for authentication
3. Enable IP allowlisting for API access
4. Set up regular access reviews via role-based access control
5. Sign the DPA at https://sentry.io/legal/dpa/
6. Document data flow in your security documentation

## Output

After completing all three steps, your Sentry deployment will have:

- Client-side PII scrubbing via `beforeSend` removing sensitive headers, request bodies, and PII patterns (emails, SSNs, credit cards, phone numbers)
- Server-side Data Scrubber enabled with custom sensitive fields and advanced regex rules
- IP anonymization active across all events
- GDPR-compliant consent gating and data subject deletion endpoint
- Data retention configured per organizational requirements
- Audit log access for SOC 2 compliance evidence

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| PII still visible in events | `beforeSend` not matching patterns | Run verification test below; check regex coverage against your data |
| Over-scrubbing useful data | Safe fields not configured | Add field names to the Safe Fields list in Project Settings |
| `401 Unauthorized` on deletion API | Token missing `project:admin` scope | Regenerate auth token with correct scopes at Settings > Auth Tokens |
| Audit logs unavailable | Developer or Team plan | Upgrade to Business or Enterprise for audit log access |
| `sendDefaultPii: true` in production | Environment-unaware configuration | Gate PII collection: `sendDefaultPii: process.env.NODE_ENV !== 'production'` |
| Data retention not applying | Plan limitation | Verify retention settings match plan tier in Organization Settings |
| GDPR erasure request timeout | Large volume of matching issues | Batch deletions with rate limiting; use `?cursor=` pagination |

## Examples

**Example 1: GDPR-Compliant Node.js Setup (TypeScript)**

Request: "Configure Sentry for GDPR compliance in a Node.js Express app"

```typescript
import * as Sentry from '@sentry/node';
import express from 'express';

// Initialize with full compliance configuration
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV || 'development',
  sendDefaultPii: false,

  beforeSend(event) {
    // Strip all user PII except anonymous ID
    if (event.user) {
      event.user = { id: event.user.id };
    }
    // Remove auth headers
    if (event.request?.headers) {
      delete event.request.headers['Authorization'];
      delete event.request.headers['Cookie'];
    }
    return event;
  },
});

const app = express();

// GDPR deletion endpoint
app.delete('/api/gdpr/erasure/:userId', async (req, res) => {
  const { userId } = req.params;
  try {
    await handleDeletionRequest(userId);
    res.json({ status: 'deleted', userId });
  } catch (error) {
    Sentry.captureException(error);
    res.status(500).json({ error: 'Deletion failed' });
  }
});
```

Result: PII scrubbing active, IP anonymization enabled server-side, consent-based init, deletion endpoint at `/api/gdpr/erasure/:userId`.

**Example 2: HIPAA-Strict Python Configuration**

Request: "Lock down Sentry for a healthcare application — no PHI can be transmitted"

```python
import sentry_sdk
import os

def hipaa_scrub(event, hint):
    """Remove ALL user-identifiable information for HIPAA compliance."""
    # Remove entire user context
    event.pop("user", None)

    # Remove all request headers (may contain PHI in auth tokens)
    request = event.get("request", {})
    request.pop("headers", None)
    request.pop("cookies", None)
    request.pop("data", None)  # Request body may contain PHI

    # Keep only technical error data
    return event

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    send_default_pii=False,
    before_send=hipaa_scrub,
    traces_sample_rate=0.05,  # Minimal tracing to reduce data exposure
)
```

Result: Zero user PII transmitted — only stack traces, file paths, and technical metadata reach Sentry.

**Example 3: Verify Scrubbing Works**

Request: "Test that our PII scrubbing actually removes sensitive data"

```typescript
// Verification test — send an event with known PII and confirm it's scrubbed
Sentry.withScope((scope) => {
  scope.setUser({
    id: 'verify-test-001',
    email: 'should-be-scrubbed@example.com',
    ip_address: '192.168.1.100',
  });

  scope.setContext('test_data', {
    password: 'should-be-scrubbed',
    credit_card: '4111-1111-1111-1111',
    api_key: 'sk_live_should_be_scrubbed',
    safe_field: 'this-should-remain-visible',
  });

  Sentry.captureMessage('Data scrubbing verification test');
});

// Check the event in Sentry dashboard:
// - email: missing (stripped by beforeSend)
// - ip_address: missing (sendDefaultPii: false)
// - password: [REDACTED]
// - credit_card: [REDACTED]
// - api_key: [REDACTED]
// - safe_field: "this-should-remain-visible" (preserved)
```

## Resources

- [Data Scrubbing Rules](references/pii-scrubbing.md) — client-side scrubbing patterns and regex reference
- [Server-Side Scrubbing](references/server-side-data-scrubbing.md) — dashboard configuration and advanced rules
- [GDPR Compliance](references/gdpr-compliance.md) — consent handling, user deletion, and pseudonymization
- [Error Handling Reference](references/errors.md) — common failure modes and solutions
- Sentry Data Privacy Docs
- [Advanced Data Scrubbing](https://docs.sentry.io/product/data-management-settings/scrubbing/)
- Sentry GDPR Overview
- [Data Processing Agreement](https://sentry.io/legal/dpa/)
- [Sentry Security](https://sentry.io/security/)

## Next Steps

- Configure **release health** to correlate errors with deployments — use the `sentry-release-management` skill
- Set up **rate limits** to control event volume and costs — use the `sentry-rate-limits` skill
- Implement **role-based access control** for team permissions — use the `sentry-enterprise-rbac` skill
- Add **performance monitoring** with privacy-safe tracing — use the `sentry-performance-tracing` skill
