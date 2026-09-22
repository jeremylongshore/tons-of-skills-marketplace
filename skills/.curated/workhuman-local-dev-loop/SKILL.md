---
name: workhuman-local-dev-loop
description: 'Build a secret-free local development loop for a Workhuman adapter using customer-contract fixtures and an explicitly authorized live lane. Use when developing or testing an integration. Trigger with "build a Workhuman dev loop".'
argument-hint: "[adapter-path] [contract-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, local-development, fixtures, testing]
model: inherit
effort: medium
compatibility: Designed for Claude Code; live tenant tests require explicit customer authorization and synthetic or approved data
---
# Workhuman Contract-First Local Development Loop

## Overview

Develop against sanitized fixtures by default, with the customer contract as authority and live Workhuman access isolated behind a deliberate gate.

## Prerequisites

- Customer-authorized schemas or connector mappings with secrets removed
- Synthetic worker, recognition, award, approval, redemption, and failure fixtures
- Separate local, test, and production configuration with named owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect adapters and fixtures, `WebFetch` to re-check authoritative contracts, and `Write` or `Edit` for local code, tests, fixtures, and redacted evidence.

## Current Contract

Workhuman's public site confirms product and integration capabilities but not universal endpoint schemas. Local mocks must therefore be derived from the customer's current approved artifacts and labeled with provenance, not invented from examples.

## Authentication

The default local lane has no live credential. Load a test credential only through the approved secret provider, deny production hosts, and fail closed when environment or tenant identity is ambiguous.

## Instructions

1. Snapshot the authorized contract with source, date, tenant, environment, and schema fingerprint.
2. Remove names, messages, employment details, balances, addresses, tokens, and correlation identifiers from fixtures.
3. Cover success, valid-empty, unauthorized, forbidden, invalid input, throttling, timeout, duplicate, partial, and schema-drift cases.
4. Put transport behind one adapter that accepts an injected fake and normalizes errors without discarding vendor evidence.
5. Add contract tests for required fields, nullable fields, pagination or checkpoints, idempotency, and unknown-field tolerance.
6. Make the default test command network-denied and deterministic.
7. Gate an optional live test on explicit opt-in, approved non-production tenant, allowlisted host, synthetic record, and cleanup plan.
8. Redact outputs and retain only contract version, test counts, result, and safe correlation evidence.

## Approval Boundaries

Do not capture real workforce payloads, contact production, create awards, or change integration configuration from the local lane without approval.

## Output

Return the contract snapshot, fixture inventory, adapter boundary, deterministic test result, live-lane safeguards, redaction proof, and drift findings.

## Error Handling

| Condition | Response |
|---|---|
| Fixture lacks provenance | Quarantine it and regenerate from an authorized, sanitized contract example. |
| Live host appears in a default test | Fail the test before transport and remove the unsafe configuration. |
| Schema changes | Preserve the old fixture, add the new version, and route migration through change control. |

## Example

A redacted completion receipt might look like this:

```text
contract=customer-2026-09; fixtures=12-synthetic; default-network=denied; live-lane=opt-in-test-only; tests=pass
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)

## Next Steps

Run the fixture suite in CI and review the contract snapshot whenever Workhuman or the customer configuration changes.
