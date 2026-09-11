---
name: workhuman-ci-integration
description: 'Build fork-safe CI gates for a Workhuman adapter using pinned customer contracts, synthetic fixtures, and an optional protected tenant smoke test. Use when automating integration verification. Trigger with "add Workhuman CI".'
argument-hint: "[repository] [adapter-path]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.4.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, workhuman, ci, testing, contracts]
model: inherit
effort: high
compatibility: Designed for Claude Code; CI must keep customer contracts and credentials out of untrusted or fork-triggered jobs
---
# Workhuman Contract and Fixture CI

## Overview

Turn customer-authorized Workhuman behavior into deterministic, secret-free merge gates and isolate any live tenant probe behind trusted approval.

## Prerequisites

- A pinned contract or mapping digest, typed adapter, and sanitized synthetic fixtures
- CI threat model covering forks, artifacts, logs, caches, and secret exposure
- Named owners for tenant access, contract updates, failures, and live-test approval

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect workflows and test assets, `WebFetch` to re-check authoritative context, and `Write` or `Edit` for CI, tests, fixtures, and redacted receipts.

## Current Contract

Workhuman publicly confirms open-API and managed-integration capabilities without publishing universal routes or schemas. CI must pin the customer's authorized artifacts and fail on drift rather than embedding assumptions from the former pack.

## Authentication

Default pull-request jobs receive no Workhuman secrets. A live check may use only an approved non-production principal in a protected environment with host allowlisting and no untrusted code execution.

## Instructions

1. Pin contract, mapping, fixture, and adapter digests and document their owners and review dates.
2. Add secretless gates for schema validity, generated-code drift, type checks, unit tests, contract tests, Unicode, and secret scanning.
3. Cover read, valid-empty, invalid, duplicate, timeout, throttling, partial, drift, and ambiguous-write behavior with synthetic fixtures.
4. Assert that tests deny network by default and that fixtures contain no workforce, recognition, reward, financial, or credential data.
5. Separate required deterministic checks from an optional trusted live lane.
6. Gate the live lane on explicit approval, non-production tenant, synthetic identity, allowlisted host, bounded read-only operation, and cleanup.
7. Redact logs and artifacts; retain only version, digest, safe status, timing, counts, and correlation evidence.
8. Make contract or fixture drift fail with an owner and regeneration instruction.

## Approval Boundaries

Do not expose secrets to forks, run customer writes, upload private contracts as public artifacts, or make provider-dependent live tests required without a governed exception.

## Output

Return the gate graph, pinned digests, fixture safety proof, required test result, live-lane controls, redaction evidence, failure ownership, and CI receipt.

## Error Handling

| Condition | Response |
|---|---|
| Fork job requests a secret | Deny it and keep the required lane fixture-only. |
| Contract digest changes | Fail closed until reviewed artifacts and fixtures regenerate together. |
| Live smoke is unavailable | Report it separately; do not weaken deterministic required gates. |

## Example

A redacted completion receipt might look like this:

```text
contract=sha256:...; required=12-pass; network=denied; secrets=0; live=protected-read-only; artifacts=redacted
```

## Resources

- [Workhuman integrations](https://www.workhuman.com/capabilities/integrations/)
- [Workhuman security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)

## Next Steps

Require these gates before deployment and review the protected live lane after any CI trust-boundary change.
