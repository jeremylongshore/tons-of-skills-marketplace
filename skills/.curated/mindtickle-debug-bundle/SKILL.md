---
name: mindtickle-debug-bundle
description: 'Assemble a privacy-safe Mindtickle support evidence bundle with configuration fingerprints, timelines, representative failures, and ownership context. Use when preparing a vendor escalation. Trigger with "build Mindtickle debug bundle".'
argument-hint: "[incident-id] [output-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, diagnostics, support, privacy]
model: inherit
effort: medium
compatibility: Designed for Claude Code; evidence collection and disclosure require incident, security, and data-owner authorization
---
# Privacy-Safe Mindtickle Support Bundle

## Overview

Create a deterministic evidence manifest that helps customer and Mindtickle support diagnose a problem without exporting secrets or unnecessary learner data.

## Prerequisites

- A tracked incident, disclosure audience, retention deadline, and support severity
- An approved redaction policy and secure transfer destination
- Read-only access to relevant customer-side configuration, logs, and receipts

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to locate evidence, `WebFetch` to confirm current support requirements, and `Write` or `Edit` only inside the approved bundle path and manifest.

## Current Contract

Mindtickle Support may request business context, logs, files, and appropriate remote access. Official support guidance defines severity and response paths; the customer remains responsible for minimizing and sanitizing what is disclosed.

## Authentication

Do not collect passwords, tokens, cookies, authorization headers, private keys, raw identity-provider assertions, or unrestricted tenant exports. Replace user identifiers with stable incident-local aliases where individual evidence is necessary.

## Instructions

1. Define the incident window, symptom, affected workflow, audience, severity, and questions the bundle must answer.
2. Create an evidence allowlist and explicit denylist before reading files.
3. Collect configuration names and digests, adapter version, contract digest, deployment receipt, timestamps, safe request IDs, and representative sanitized errors.
4. Add expected-versus-actual behavior, one known-good comparison, reproduction limits, recent changes, and attempted mitigations.
5. Scan every artifact for secrets, cookies, personal data, assessment data, content URLs, and internal infrastructure details.
6. Produce a manifest with artifact digests, provenance, redactions, collector, collection time, and expiry.
7. Obtain disclosure approval, transfer through the contracted secure channel, and record the support receipt.

## Approval Boundaries

Do not run new production probes, grant remote access, include raw tenant exports, or send the bundle before security and data-owner approval.

## Output

Return the sanitized bundle path, manifest, digest list, redaction report, reproduction summary, severity rationale, disclosure approval, transfer receipt, and destruction date.

## Error Handling

| Condition | Response |
|---|---|
| Secret scanning finds a credential | Remove it, rotate if exposure occurred, and regenerate the manifest. |
| Evidence exceeds the approved scope | Exclude it and state the unanswered question. |
| Secure transfer is unavailable | Retain the encrypted bundle under policy and do not use consumer sharing links. |

## Example

```text
incident=INC-1042; artifacts=8; pii=aliased; secrets=0; manifest-sha256=...; approval=security-and-data-owner; expiry=30d
```

## Resources

- [Mindtickle Support Services](https://www.mindtickle.com/legal/support-services/)
- [Mindtickle Trust](https://www.mindtickle.com/trust/)

## Next Steps

Track vendor questions and delete the bundle at expiry after retaining only the permitted incident receipt.
