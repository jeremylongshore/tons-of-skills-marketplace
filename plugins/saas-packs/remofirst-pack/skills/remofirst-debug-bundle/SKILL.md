---
name: remofirst-debug-bundle
description: >-
  Assemble a privacy-safe RemoFirst support escalation bundle with a redacted
  timeline, record keys, screenshots index, and reproduction boundary. Use when
  support needs evidence for a platform or connector incident. Trigger with
  "RemoFirst debug bundle", "escalate RemoFirst", or "RemoFirst support ticket".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<incident-type> <redacted-record-key>"
version: 2.0.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, remofirst, incident-response, support, privacy]
model: inherit
effort: high
compatibility: Designed for Claude Code; live RemoFirst access requires an approved client account and explicit operator action
---
# RemoFirst Privacy-Safe Support Bundle

## Overview

Produce the smallest support packet that lets RemoFirst investigate without
copying credentials, worker documents, bank details, full payrolls, or unrelated
personal data. The bundle describes observed behavior and approved record keys;
it does not reverse-engineer a private API or scrape a browser session.

## Prerequisites

- Incident owner, affected workflow, first/last observed time, and severity.
- A redaction standard and approved support channel.
- Consent to include each screenshot or exported field.

## Current Contract

RemoFirst accepts support by email, in-platform chat/live agent, and Help Center
ticket. The Workday guide asks for company name, affected team member, relevant
Workday record or event, and a clear issue description. Payment investigations
may require provider-issued trace evidence; sensitive values should travel only
through the approved support path.

## Instructions

1. Assign a bundle ID, owner, severity, workflow, environment, tenant/company,
   affected period, first seen, last seen, and business impact.
2. Write expected and observed behavior in neutral terms. Separate facts from
   hypotheses and label every timestamp with timezone.
3. Include only redacted provider-visible identifiers needed to locate the case.
   Use placeholders for worker, bank, payment, and authentication values.
4. List reproduction steps that stop before any irreversible approval, payment,
   connector reset, offboarding, or personal-data exposure.
5. Create an evidence manifest with filename, source, capture time, owner,
   redaction reviewer, sensitivity, and retention deadline.
6. Scan the bundle for passwords, codes, cookies, tokens, bank details, identity
   documents, health data, and unrelated workers. Remove or quarantine findings.
7. Draft the support message with bundle ID, urgency, requested decision, and next
   contact time. A human reviews and sends it through the approved channel.

## Tool Discipline

Use Read, Glob, and Grep to inventory and scan approved local evidence. Use Write
or Edit for the redacted manifest and draft. Do not capture new live data, send a
message, upload an attachment, reset a connector, or alter a record.

## Approval Boundaries

Require approval before including any personal/payment evidence, uploading the
bundle, naming a worker, initiating a trace, or reproducing against production.
Never include authenticator, recovery, session, or bank-secret material.

## Output

Return bundle ID, severity, redacted timeline, expected/observed behavior,
reproduction boundary, evidence manifest, redaction result, requested provider
action, owner, next-update time, retention deadline, and send approval state.

## Error Handling

- Evidence cannot be redacted safely: omit it and describe what support may request.
- Multiple workers implicated: split the bundle or aggregate without identifiers.
- Unknown timezone or sequence: mark UNKNOWN; do not manufacture chronology.
- Urgent payroll impact: escalate severity while preserving approval boundaries.

## Examples

- A Workday time-off sync issue includes the mapped absence type and event key,
  but not the employee address or OAuth secret.
- A payment delay references the invoice/PRID through redacted suffixes only.
- "Attach the browser cookie" is rejected as credential disclosure.

## Validation

- Facts, hypotheses, reproduction, and requested action are distinct.
- Every evidence item has owner, sensitivity, redaction, and retention metadata.
- Secret and personal-data scan is clean before human send review.

## Resources

See [references/official-docs.md](references/official-docs.md) for the reviewed
support, connector, payment, access, and data-protection sources.
