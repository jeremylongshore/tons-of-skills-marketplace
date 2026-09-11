---
name: salesforce-policy-guardrails
description: 'Gate Salesforce code and configuration for SOQL injection, secret exposure, unsafe API versions, missing access checks, destructive writes, and unreviewed org changes. Use when running CI or review. Trigger with "add Salesforce guardrails".'
argument-hint: "[repository] [policy-profile]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.8.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [saas, salesforce, policy, secure-coding, ci]
model: inherit
effort: high
compatibility: Designed for Claude Code; blocking policy and exceptions require code, security, Salesforce platform, and business-owner governance
---
# Salesforce Integration Policy Guardrails

## Overview

Turn recurring integration hazards into deterministic checks with fail-closed severity, exact evidence, owned exceptions, and no secret-dependent fork execution.

## Prerequisites

- Repository, Salesforce DX or adapter layout, languages, CI trust model, protected branches, and code owners
- Current API EOL, OAuth, security, object and field access, sharing, limits, and deployment contracts
- Policy authority, severity model, baseline findings, exception format, expiry, and remediation owners

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect approved repository and evidence files, `WebFetch` to re-check current first-party Salesforce documentation, and `Write` or `Edit` only for secretless plans, fixtures, configuration, and redacted receipts.

## Current Contract

Salesforce requires parameter-safe query construction and layered authorization, while supported API versions and client-app guidance evolve. Static rules cannot prove runtime CRUD, field access, sharing, limits, or org identity and must be paired with protected tests.

## Authentication

Static and fixture gates must run without Salesforce credentials. Protected runtime checks use a minimum non-production principal only after exact-head trust and must never expose secrets to fork code.

## Instructions

1. Inventory query construction, credentials, app and OAuth settings, API versions, objects and fields, mutations, events, retries, logs, and deployment paths.
2. Define checks for string-built SOQL, secrets, unsafe logs, retired or fixed versions, broad scopes, wrong-org defaults, and unrestricted queries.
3. Add rules for missing CRUD and field-access evidence, destructive operations, blind retries, unbounded concurrency, checkpoint resets, and reconciliation gaps.
4. Create positive and negative fixtures for every rule and pin scanners, actions, runtimes, dependencies, and rule hashes.
5. Run secretless checks on every change and protected org contract checks only in trusted environments.
6. Ratchet against a reviewed baseline; require exact finding, owner, reason, scope, expiry, and compensating control for exceptions.
7. Measure escapes and false positives, close expired waivers, and update policies from incidents and Salesforce contract changes.

## Approval Boundaries

Do not suppress blockers, broaden globs, add permanent waivers, expose CI secrets, or auto-fix Salesforce org state without policy-owner approval.

## Output

Return the policy catalog, authority and hashes, fixture results, findings, baseline delta, exceptions with expiry, protected-test receipt, and owners.

## Error Handling

| Condition | Response |
|---|---|
| Rule flags generated or vendored content | Narrow the rule with an evidence-backed path boundary rather than disabling the category. |
| Runtime permission cannot be proven statically | Require a protected non-production test and label static evidence as incomplete. |
| Exception has no owner or expiry | Fail the gate until governance metadata is complete. |

## Example

A redacted completion receipt might look like this:

```text
profile=enterprise; rules=12; fixtures=24-pass; blockers=0; waivers=2-expiring; fork-secrets=0; runtime=protected-pass
```

## Resources

- [Salesforce SOQL injection guidance](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/pages_security_tips_soql_injection.htm)
- [REST API end-of-life policy](https://developer.salesforce.com/docs/platform/api-rest/guide/api-rest-eol.html)

## Next Steps

Run the workflow first in the lowest-risk authorized org and preserve its redacted receipt. Schedule a review against the next Salesforce seasonal release and the customer change calendar.
