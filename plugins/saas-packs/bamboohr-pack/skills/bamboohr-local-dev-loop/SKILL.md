---
name: bamboohr-local-dev-loop
description: >-
  Create a fast BambooHR development loop with synthetic fixtures, a recording-
  free fake transport, contract tests, and opt-in test-tenant reads. Use when
  developing safely without copying employee data onto laptops. Trigger with
  "BambooHR local dev", "mock BambooHR", or "BambooHR test fixtures".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <runtime>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, local-development, testing]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Local Development Loop

## Overview

Make local iteration independent of production HR data and network availability.
Use a fake transport whose fixtures are designed from the official schema, not
recorded from real employees.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

The official OpenAPI and SDK docs define operations, status codes, auth modes,
pagination, and typed errors. They are suitable inputs for contract fixtures;
they do not authorize copying actual BambooHR payloads into a repository.

## Authentication

Default local configuration uses obvious non-secret placeholders and a fake
transport. A live test-tenant profile is separate, ignored by version control,
loaded from an approved secret store, and never activated by ordinary test or
watch commands.

## Instructions

1. Inspect runtime, package manager, test framework, local configuration, and
   current BambooHR adapter.
2. Put a transport interface behind the adapter. Implement an in-memory fake
   with explicit scripted responses and request assertions.
3. Create synthetic employees and HR objects with impossible domains and values.
   Cover active/inactive/future states, missing permitted fields, pagination,
   empty results, and schema drift without realistic government IDs or records.
4. Add scenarios for `401`, `403`, `409`, `412`, `413`, `422`, `429`, `503`,
   `504`, `598`, timeout, redaction, request IDs, and ambiguous mutation outcome.
5. Add a watch command that runs offline unit/contract tests only. Keep any
   integration test behind an explicit profile and approval gate.
6. For webhook development, generate payloads locally, verify raw-byte HMAC
   behavior with a synthetic key, and test replay/idempotency. Do not capture a
   real delivery as a fixture.
7. Document reset, seeded scenarios, schema-pin update, and the exact command
   that proves the default loop performs no network calls.

## Tool Discipline

Use Read, Glob, and Grep to inspect code and ignored paths. Use Write/Edit for
approved fake transport, fixtures, tests, and developer docs. Do not install
packages or access BambooHR under this skill.

## Approval Boundaries

Require approval before adding a dependency, storing any live credential,
calling a tenant, capturing traffic, or adding a fixture derived from customer
data. Redaction does not automatically make a production payload reusable.

## Output

Return transport boundary, scenario inventory, fixture provenance, commands,
no-network proof, coverage for auth/retry/pagination/webhooks, test results, and
any optional live profile that remains disabled.

## Error Handling

- Test attempts network access: fail the suite and identify the unmocked operation.
- Fixture resembles real HR data: remove it and replace with synthetic values.
- Fake diverges from pinned OpenAPI: update through a reviewed contract diff.

## Examples

- "Record production responses for tests" is rejected in favor of synthetic fixtures.
- "Make BambooHR tests fast" yields an offline fake plus targeted contract tests.

## Resources

Read [official evidence](references/official-docs.md) when designing scenarios.
