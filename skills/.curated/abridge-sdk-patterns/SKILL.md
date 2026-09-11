---
name: abridge-sdk-patterns
description: "Implement a narrow customer-owned adapter around an approved Abridge tenant interface without claiming a public SDK. Use when coding against vendor-issued integration specifications. Trigger with \"build the Abridge adapter\"."
argument-hint: "[interface-contract] [language]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.5.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- saas
- abridge
- adapter
- private-contract
- reliability
model: inherit
effort: high
compatibility: Designed for Claude Code; live work requires an authorized Abridge tenant, approved test data, and health-system change authority
---
# Abridge Private-Contract Adapter Patterns

## Overview

Keep vendor-specific transport behind a typed port whose schema, authentication, errors, timeouts, and retry rules are pinned to the private contract revision. Make unsupported behavior fail closed and keep clinical review outside the adapter.

## Prerequisites

- The authorized Abridge environment, clinical owner, and health-system policy set
- Current tenant-specific implementation evidence for every private interface in scope
- Synthetic data or the organization's formally approved test-record procedure

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect repository configuration, adapters, tests, policies, and existing evidence. Use `WebFetch` only for current official Abridge, HHS, or named EHR documentation. Use `Write` or `Edit` only after confirming scope, environment, owners, patient-data boundary, and approval state. These tools do not confer access to Abridge, an EHR, or a clinical record; return exact operator steps or an approval-gated handoff for live actions.

## Current Contract

- The cited public Abridge sources describe product workflows, not a general public SDK package or stable REST surface.
- Partner-issued specifications may be implemented only for the authorized tenant and cannot be generalized without evidence.
- Clinical content, credentials, and tenant identifiers must not appear in logs or test fixtures.

## Authentication

Use only the health system's provisioned Abridge application access, SSO, administrative role, or tenant-specific partner authentication documented for the approved environment. Do not infer public API credentials, reuse production secrets in tests, or expose tokens and session material. Verify identity owner, least privilege, environment binding, storage, rotation, and revocation before any authenticated action.

## Instructions

1. Verify the contract owner, revision, environment, authentication protocol, schemas, delivery semantics, and support path.
2. Use `Read`, `Glob`, and `Grep` to inspect existing ports, adapters, configuration, error types, and tests.
3. Define typed request and response envelopes with strict parsing, explicit unknown-field behavior, redacted errors, and bounded timeouts.
4. Implement retries only for contract-authorized idempotent operations; expose manual reconciliation for ambiguous outcomes.
5. Use `Write` or `Edit` to add the adapter, synthetic contract fixtures, version negotiation, and rollback path.
6. Use `WebFetch` only to align user-facing workflow language with official Abridge guidance.

## Approval Boundaries

Do not guess endpoints, credentials, headers, scopes, event names, or response fields. Do not publish private contract material in the repository.

## Output

Return contract revision, implemented operations, auth boundary, parser policy, retry classes, test coverage, logging exclusions, and unsupported operations. Separate verified facts, tenant-specific evidence, assumptions, and actions still awaiting approval.

## Error Handling

| Condition | Response |
|---|---|
| Contract revision is missing | Refuse implementation. |
| Response violates schema | Quarantine the payload metadata and escalate without logging content. |
| Outcome is ambiguous | Do not retry a possible clinical write automatically. |

## Example

The example is a redacted operational receipt, not patient data or proof of vendor certification.

```text
contract=vendor-ICD-r9; operations=3; fixtures=synthetic; unknown-fields=reject; retries=idempotent-only; private-docs-committed=no
```

## Resources

- [Official documentation map](references/official-docs.md) — dated public evidence and the limits of what those sources establish.

Read the source map before changing a workflow. Recheck tenant-specific implementation evidence for every interface or capability that public documentation does not define.

## Next Steps

Revalidate the evidence date and tenant-specific authority before repeating this workflow in another environment, cohort, care setting, or integration mode.
