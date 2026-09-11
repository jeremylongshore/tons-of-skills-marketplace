---
name: mindtickle-hello-world
description: 'Discover a Mindtickle tenant''s licensed capabilities and produce a safe first integration proof without assuming public API details. Use when starting a Mindtickle exercise or tenant handoff. Trigger with "start with Mindtickle".'
argument-hint: "[tenant] [business-outcome]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, mindtickle, onboarding, discovery, proof-of-concept]
model: inherit
effort: medium
compatibility: Designed for Claude Code; tenant discovery requires authorized customer access and any external proof requires owner approval
---
# Mindtickle Capability Discovery and First Proof

## Overview

Turn a business outcome into an entitlement-aware, read-only proof that establishes the real tenant contract before implementation begins.

## Prerequisites

- A named tenant site owner and one measurable business outcome
- The purchased package or order summary and an approved non-production audience
- Access to current tenant documentation without copying confidential content into the repository

## Tool Discipline

Use `Read`, `Glob`, and `Grep` for existing assumptions and fixtures, `WebFetch` for current official sources, and `Write` or `Edit` for a redacted capability matrix and proof plan.

## Current Contract

Package contents differ. Public descriptions identify learning modules, assessments, certifications, coaching, Readiness Index, Asset Hub, Digital Sales Rooms, analytics, and Call AI in different combinations. Availability in one tenant is evidence, not a universal product contract.

## Authentication

Use the onboarding decision from `mindtickle-install-auth`. Discovery must use a named least-privilege principal; never use shared administrator credentials or scrape authenticated UI pages as an API substitute.

## Instructions

1. Define the outcome, audience, data sensitivity, success metric, and maximum proof scope.
2. Compare the purchased package, visible tenant modules, managed integration catalogue, and tenant API documentation.
3. Mark each needed capability confirmed, absent, restricted, or vendor clarification required.
4. Choose the smallest reversible proof: a local fixture exercise, a tenant read, or a site-owner-led UI walkthrough.
5. Define acceptance before execution, including expected fields, freshness, authorization, and zero unintended mutations.
6. Obtain approval for any tenant access, then run the proof once and capture redacted evidence.
7. Convert confirmed observations into a contract fixture; label every tenant-specific inference and expiry date.

## Approval Boundaries

Do not create courses, users, assignments, rooms, exports, or connectors during discovery unless the proof explicitly authorizes that mutation and rollback.

## Output

Return the outcome statement, capability matrix, authoritative sources, proof method, redacted receipt, gaps, and a go/no-go recommendation.

## Error Handling

| Condition | Response |
|---|---|
| Marketing page and tenant differ | Treat the tenant entitlement and signed order as controlling; record the discrepancy. |
| Proof would expose learner data | Replace it with synthetic fixtures or aggregate evidence. |
| No reversible first action exists | Stop with a vendor-question packet instead of forcing a live test. |

## Example

```text
outcome=confirm reporting fit; capabilities=reporting-confirmed,webhooks-unverified; proof=authorized-aggregate-read; decision=proceed-with-tenant-contract
```

## Resources

- [Subscription services](https://www.mindtickle.com/legal/description-of-subscription-services/)
- [Mindtickle integrations](https://www.mindtickle.com/platform/integrations/)

## Next Steps

Route confirmed API work to `mindtickle-sdk-patterns` and a program rollout to `mindtickle-core-workflow-a`.
