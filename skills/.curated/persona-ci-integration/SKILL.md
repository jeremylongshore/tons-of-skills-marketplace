---
name: persona-ci-integration
description: >-
  Build Persona CI around offline contract fixtures and bounded sandbox smoke tests without production identity data. Use when adding integration gates. Trigger with: "test Persona in CI", "Persona contract tests", "Persona GitHub Actions".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[repository-and-test-command]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - persona
  - ci
  - contract-testing
  - sandbox
compatibility: 'Requires an authorized Persona environment, current first-party documentation, a reviewed dated API version, and privacy-safe operational evidence.'
---

# Contract-Safe Persona CI

## Overview

Keep the required CI gate deterministic and secret-minimal. Offline fixtures validate JSON:API, version, idempotency, webhook HMAC, replay, and unknown additions; an optional protected sandbox job proves connectivity without making production a test dependency.

## Prerequisites

- Repository test conventions and required status names
- Redacted signed fixtures for REST and webhook contracts
- Protected sandbox secret scope and synthetic test identities

## Instructions

### Step 1: Define the offline denominator

List parsers, commands, event transitions, security checks, error envelopes, pagination, and compatible-addition cases that must run on every change.

### Step 2: Pin contract provenance

Record source URLs, retrieval date, split fingerprints, API version, template context, and redaction method for every fixture.

### Step 3: Test mutations safely

Assert operation IDs, idempotency-key reuse only with identical parameters, timeout reconciliation, and no automatic duplicate inquiry.

### Step 4: Test webhook adversaries

Cover modified raw body, stale timestamp, multiple `v1` candidates, constant-time comparison, duplicates, reordering, and unknown event types.

### Step 5: Isolate the sandbox smoke lane

Run only for trusted branches, use a sandbox key, create a unique synthetic inquiry, cap calls, and retain redacted evidence.

### Step 6: Fail closed on leaks and drift

Scan fixtures and logs for key, token, signature, PII, and wrong-host patterns; make unexplained contract drift fail the gate.

## Authentication

Required offline tests use no live credential. The optional protected job uses only a sandbox bearer key and sandbox webhook secret supplied by the CI secret store.

## Tool Discipline

Use Read and Grep to inspect application configuration, provider documentation, fixtures, schemas, tests, and redacted operational evidence before proposing a change. Use Write or Edit only for an approved implementation, configuration, test, runbook, or redacted receipt. Do not create, resume, approve, decline, redact, rotate, revoke, deploy, or otherwise mutate production Persona resources without explicit operator approval.

## Output

- Required offline contract-test suite
- Protected optional sandbox-smoke workflow
- Fixture provenance, drift, and redaction receipts

Return the environment, resource and event identifiers, API version, template context, source-contract fingerprint, evidence, unresolved risk, rollback state, and final decision without exposing bearer keys, webhook secrets, inquiry session tokens, raw identity documents, or unnecessary PII.

## Examples

A pull request adds an unknown verification type fixture and proves the mapper routes it to review. The trusted-branch job then creates one synthetic sandbox inquiry and stores only its ID and response metadata.

## Error Handling

| Failure | Response |
| --- | --- |
| Fork job requests secrets | Skip the live lane and run the complete offline denominator. |
| Fixture contains PII or token | Block the build, quarantine the artifact, and rotate an exposed credential. |
| Sandbox flakes | Keep it outside the deterministic denominator, preserve evidence, and reconcile any created inquiry. |

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
