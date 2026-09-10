---
name: posthog-data-handling
description: |
  Implement consent-aware PostHog collection, PII minimization, masking, retention, and deletion workflows. Use when analytics must satisfy a documented privacy or data-governance requirement. Trigger with "PostHog privacy", "PostHog PII", or "PostHog GDPR".
argument-hint: "[project-path] [privacy-requirement]"
allowed-tools: Read, Write, Edit
version: 1.13.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- posthog
- compliance
compatibility: Designed for Claude Code
---
# PostHog Data Handling

## Overview

Privacy-safe analytics with PostHog. Covers property sanitization to strip PII before events leave the browser, consent-based tracking (opt-in/opt-out), GDPR data subject access requests and deletion, and PostHog's built-in privacy controls (IP masking, session recording masking).

## Prerequisites

- PostHog project with current privacy, retention, and deletion capabilities verified for its deployment model
- `posthog-js` and/or `posthog-node` installed
- Privacy policy covering analytics data collection
- Cookie consent mechanism (e.g., CookieConsent banner)

## Authentication

- Browser capture uses the public project token; do not treat it as a secret or grant it private API access.
- Subject-access, export, and deletion operations use a least-privilege personal API key or OAuth token against the private regional API host.
- Load private credentials from a server-side secret manager, redact them from logs, and never expose them through client bundles or analytics properties.
- Confirm the target project ID and US or EU region before any destructive privacy operation.

## Instructions

### Tool discipline

Use `Read` to inspect the relevant configuration and implementation before proposing changes. Use `Write` only for a new, explicitly requested artifact inside the target project. Use `Edit` for minimal changes to existing project files after the evidence pass.

### Step 1: Privacy-Safe Initialization

```typescript
import posthog from 'posthog-js';

posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
  api_host: 'https://us.i.posthog.com',

  // Disable autocapture to control exactly what's captured
  autocapture: false,

  // Respect browser Do Not Track setting
  respect_dnt: true,

  // Don't capture until user consents
  opt_out_capturing_by_default: false, // Set true for opt-in model

  // Sanitize ALL properties before they leave the browser
  sanitize_properties: (properties, eventName) => {
    // Remove IP address
    delete properties['$ip'];

    // Remove potentially identifying properties
    delete properties['$device_id'];

    // Redact URLs containing tokens or auth info
    if (properties['$current_url']) {
      properties['$current_url'] = properties['$current_url']
        .replace(/token=[^&]+/g, 'token=[REDACTED]')
        .replace(/key=[^&]+/g, 'key=[REDACTED]')
        .replace(/session=[^&]+/g, 'session=[REDACTED]');
    }

    // Redact referrer tokens
    if (properties['$referrer']) {
      properties['$referrer'] = properties['$referrer']
        .replace(/token=[^&]+/g, 'token=[REDACTED]');
    }

    return properties;
  },

  // Session recording privacy
  session_recording: {
    maskAllInputs: true,           // Mask all input fields
    maskTextSelector: '.pii-data', // Mask specific elements
  },
});
```

### Step 2: Consent-Based Tracking

```typescript
// Cookie consent integration
interface ConsentState {
  analytics: boolean;
  functional: boolean;
  marketing: boolean;
}

export function handleConsentChange(consent: ConsentState) {
  if (consent.analytics) {
    // User opted in — start capturing
    posthog.opt_in_capturing();
  } else {
    // User opted out — stop capturing and clear local data
    posthog.opt_out_capturing();
    posthog.reset(); // Clears distinct_id, device_id, session data
  }
}

// Check consent before identifying (PII)
export function identifyWithConsent(
  userId: string,
  properties: Record<string, any>,
  hasAnalyticsConsent: boolean
) {
  if (!hasAnalyticsConsent) return;

  // Only send non-PII properties by default
  const safeProperties: Record<string, any> = {
    plan: properties.plan,
    signup_date: properties.signupDate,
    account_type: properties.accountType,
    // Do NOT include: email, name, phone, address
  };

  posthog.identify(userId, safeProperties);
}

// On page load: restore consent state
export function restoreConsent() {
  const consent = getCookieConsent(); // Your consent mechanism
  if (consent?.analytics === false) {
    posthog.opt_out_capturing();
  }
}
```

### Step 3: GDPR Data Subject Access Request (SAR)

```typescript
// Find a person by email and export their data
async function handleSubjectAccessRequest(email: string) {
  const personalKey = process.env.POSTHOG_PERSONAL_API_KEY!;
  const projectId = process.env.POSTHOG_PROJECT_ID!;

  // 1. Find the person by email property
  const searchResponse = await fetch(
    `https://us.posthog.com/api/projects/${projectId}/persons/?properties=[{"key":"email","value":"${encodeURIComponent(email)}","type":"person"}]`,
    { headers: { Authorization: `Bearer ${personalKey}` } }
  );
  const searchData = await searchResponse.json();

  if (!searchData.results?.length) {
    return { found: false, message: 'No person found with that email' };
  }

  const person = searchData.results[0];
  const distinctId = person.distinct_ids[0];

  // 2. Export their events (strip PII from export)
  const eventsResponse = await fetch(
    `https://us.posthog.com/api/projects/${projectId}/query/`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${personalKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: {
          kind: 'HogQLQuery',
          query: `SELECT event, timestamp, properties FROM events WHERE distinct_id = '${distinctId}' ORDER BY timestamp DESC LIMIT 1000`,
        },
      }),
    }
  );
  const eventsData = await eventsResponse.json();

  return {
    found: true,
    person: {
      distinct_ids: person.distinct_ids,
      properties: person.properties,
      created_at: person.created_at,
    },
    events_count: eventsData.results?.length || 0,
    events: eventsData.results,
  };
}
```

### Step 4: GDPR Right to Erasure (Data Deletion)

```typescript
// Delete a person and all their events
async function handleDeletionRequest(email: string) {
  const personalKey = process.env.POSTHOG_PERSONAL_API_KEY!;
  const projectId = process.env.POSTHOG_PROJECT_ID!;

  // 1. Find the person
  const searchResponse = await fetch(
    `https://us.posthog.com/api/projects/${projectId}/persons/?properties=[{"key":"email","value":"${encodeURIComponent(email)}","type":"person"}]`,
    { headers: { Authorization: `Bearer ${personalKey}` } }
  );
  const searchData = await searchResponse.json();

  if (!searchData.results?.length) {
    return { deleted: false, reason: 'Person not found' };
  }

  const personId = searchData.results[0].id;

  // 2. Delete the person (PostHog also deletes associated events)
  const deleteResponse = await fetch(
    `https://us.posthog.com/api/projects/${projectId}/persons/${personId}/`,
    {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${personalKey}` },
    }
  );

  if (!deleteResponse.ok) {
    throw new Error(`Deletion failed: ${deleteResponse.status}`);
  }

  return {
    deleted: true,
    personId,
    timestamp: new Date().toISOString(),
  };
}
```

### Step 5: Property Filtering for Data Exports

```typescript
// Strip PII from HogQL query results before exporting
const BLOCKED_PROPERTIES = ['$ip', 'email', 'phone', 'name', 'address', 'ssn'];

async function safeExport(hogql: string) {
  const response = await fetch(
    `https://us.posthog.com/api/projects/${process.env.POSTHOG_PROJECT_ID}/query/`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.POSTHOG_PERSONAL_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: { kind: 'HogQLQuery', query: hogql } }),
    }
  );
  const data = await response.json();

  // Remove blocked columns from results
  if (data.columns && data.results) {
    const blockedIndexes = new Set(
      data.columns.map((col: string, i: number) =>
        BLOCKED_PROPERTIES.some(b => col.toLowerCase().includes(b)) ? i : -1
      ).filter((i: number) => i >= 0)
    );

    data.columns = data.columns.filter((_: string, i: number) => !blockedIndexes.has(i));
    data.results = data.results.map((row: any[]) =>
      row.filter((_: any, i: number) => !blockedIndexes.has(i))
    );
  }

  return data;
}
```

## Error Handling

| Issue | Cause | Solution |
|-------|-------|----------|
| PII in autocapture events | Form data captured automatically | Disable autocapture, use manual capture |
| IP address in events | Not stripped by sanitize_properties | Add `delete properties['$ip']` |
| Consent not persisted | opt_out state lost on reload | Store consent in cookie, call opt_out on load |
| Deletion API returns 404 | Wrong person ID or already deleted | Search by email first, check response |
| Session recordings show PII | Text not masked | Add `maskAllInputs: true` and `maskTextSelector` |

## GDPR Compliance Checklist

- [ ] `sanitize_properties` strips PII before events leave browser
- [ ] Consent mechanism with `opt_in_capturing` / `opt_out_capturing`
- [ ] `respect_dnt: true` in PostHog init
- [ ] Session recording masks all inputs
- [ ] Subject Access Request handler implemented
- [ ] Data Deletion handler implemented
- [ ] Privacy policy updated to mention PostHog analytics

## Output

- Privacy-safe PostHog initialization with property sanitization
- Consent-based tracking with opt-in/opt-out
- GDPR Subject Access Request handler
- GDPR Data Deletion handler
- PII-safe data export function

## Examples

For a consent-gated web app, start opted out, enable capture only after the consent signal, mask sensitive elements, reject prohibited properties before send, and test both consent states. Produce a data map and identify any deletion step that requires private-API authorization.

## Resources

See [official PostHog references](references/official-docs.md) for current authority and verification boundaries.

- [PostHog Privacy Controls](https://posthog.com/docs/privacy)
- [PostHog GDPR Compliance](https://posthog.com/docs/privacy/gdpr-compliance)
- [PostHog Persons API](https://posthog.com/docs/api/persons)
- [PostHog Data Collection Controls](https://posthog.com/docs/privacy/data-collection)
