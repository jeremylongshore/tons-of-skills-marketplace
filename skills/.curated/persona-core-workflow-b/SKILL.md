---
name: persona-core-workflow-b
description: >-
  Interpret Persona verification resources without collapsing provider evidence into an automatic business decision. Use when mapping checks to review outcomes. Trigger with: "evaluate Persona verification", "map KYC result", "handle Persona checks".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[inquiry-id-and-policy]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - verifications
  - decisioning
  - kyc
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Persona Verification Evidence and Decision Boundary

## Overview

Separate Persona verification lifecycle evidence from the application’s approve, reject, or review decision. Government ID, phone, selfie, document, and database verification types can evolve; the integration must tolerate unfamiliar types and values.

## Prerequisites

- Inquiry ID with authorized access
- Versioned business decision policy and manual-review owner
- PII-minimized mapping for needed verification attributes

## Instructions

### Step 1: Read authoritative resources

Fetch the inquiry and related verification resources under the pinned API version. Record IDs, types, statuses, checks, and timestamps without copying unnecessary PII.

### Step 2: Validate completeness

Determine which verification types the template and policy require. Missing evidence is unknown or incomplete, not a silent pass.

### Step 3: Normalize conservatively

Map known provider states to internal evidence states and preserve unknown types or values for review. Never fabricate check enums.

### Step 4: Apply the policy boundary

Evaluate provider evidence through the versioned internal policy. Record the policy version and reasons independently of Persona’s status.

### Step 5: Handle later changes

Accept verified webhook updates and reconcile the resource before changing the decision. Guard terminal decisions against stale or out-of-order events.

### Step 6: Produce an auditable receipt

Retain resource IDs, redacted evidence facts, event IDs, policy version, decision, reviewer, and appeal or retry route.

## Authentication

Use a service bearer key limited to the correct Persona environment. Authorization to retrieve a verification does not authorize broad storage or display of its PII.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Normalized verification-evidence set
- Versioned business decision with explicit unknowns
- Manual-review and audit receipt

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

A government-ID verification is passed but a required selfie resource is absent. The evidence mapper records one pass and one missing requirement; the policy sends the case to review instead of approving it.

## Error Handling

| Failure | Response |
| --- | --- |
| Unknown verification type | Preserve its resource ID and type, mark the mapping unsupported, and route to review. |
| Conflicting evidence | Re-read the inquiry and verifications, compare creation times, and apply the reviewed policy. |
| PII appears in telemetry | Stop export, restrict access, redact the field, and follow the incident process. |

## Validation

Verify the result against the linked first-party evidence, the pinned API version, redacted contract fixtures, an expected failure path, and the documented rollback or manual-disposition path. A successful request is not proof of a successful identity decision.

## Resources

- [First-party source notes](references/official-docs.md)
- [API introduction](https://docs.withpersona.com/api-introduction)
- [API quickstart](https://docs.withpersona.com/api-quickstart-tutorial)
- [API keys](https://docs.withpersona.com/api-keys)
- [Rate limits](https://docs.withpersona.com/rate-limiting)
- [Webhook best practices](https://docs.withpersona.com/webhooks-best-practices)
- [Request idempotence](https://docs.withpersona.com/idempotence)
