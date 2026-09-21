---
name: palantir-common-errors
description: >-
  Diagnose Foundry API, Ontology, permission, and transform-build failures from bounded evidence. Use when an operator sees authentication, authorization, throttling, missing-resource, dependency, or build errors. Trigger with "Foundry error" or "Palantir 403".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[error-or-build-id]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, troubleshooting, api]
---
# Palantir Foundry Error Triage

## Overview

Triage the failing surface before changing credentials, permissions, code, or compute. Preserve the server request identifier and Foundry build evidence so similar-looking failures are not collapsed into the same cause.

## Prerequisites

- Capture the exact status code or Foundry error name, request identifier, timestamp, endpoint or build, and affected principal.
- Identify whether the call uses a temporary user token, authorization-code token, or client-credentials service user.
- Read `references/official-docs.md`; use the API reference and in-platform build report as the current contract.
- Reproduce with a read-only request or sandbox branch whenever possible.

## Current Contract

- A `401` points to missing, malformed, expired, or otherwise unusable authentication; it does not justify broader scope.
- A `403` can result from the intersection of token scope, application restrictions, user/service-user permissions, project roles, and mandatory controls.
- Foundry documents global rate and concurrency limits, while individual endpoints may impose stricter limits and return `429` or `503`.
- Transform preview and full build can differ because preview may use a subset of data; repository checks also evaluate dependencies and declared resources.

## Authentication

All Foundry REST API calls use OAuth 2.0 bearer tokens. Never print or persist a token in the triage report. Record the grant type, requested scopes, Developer Console restrictions, and effective user or service-user permissions without recording credential values.

## Instructions

1. Classify the failure as authentication, authorization, limit/concurrency, resource identity, dependency, transform logic, or platform availability.

2. Preserve the smallest complete evidence set: request ID, build ID, branch, commit, principal type, scope names, and affected RIDs or API names.

3. For auth failures, evaluate token validity, scope, application restrictions, project role, and mandatory markings in that order.

4. For `429` or `503`, honor server guidance and apply bounded exponential backoff with jitter; reduce concurrency before retrying.

5. For build failures, inspect the detailed report, compare preview and full inputs, and test the minimal failing transform on a sandbox branch.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Permission grants, application-restriction changes, marking access, token replacement, and production rebuilds require their respective owners. A diagnosis does not authorize any of those mutations.

## Output

A triage record with classification, evidence, ruled-out causes, confirmed cause, minimum remediation, approval owner, validation request, and rollback. Redact tokens, personal data, and sensitive resource names when the audience does not need them.

## Error Handling

| Condition | Response |
|---|---|
| Request ID is missing | Reproduce once with a safe read-only operation and capture response headers; otherwise report the evidence gap. |
| A new token still gets 403 | Stop rotating credentials and evaluate scopes, app restrictions, project roles, and mandatory controls. |
| Retries increase throttling | Cancel the retry loop, reduce concurrency, honor server timing, and contact Palantir Support if disruption persists. |
| Preview passes but build fails | Use the full build report and production input characteristics; do not treat preview as proof of production success. |

## Examples

### Example 1

Triage an Ontology read that changed from `200` to `403` by checking the client-credentials service user, requested scope, Developer Console resource restrictions, project role, and required markings.

### Example 2

Resolve a repeated transform check failure by preserving the build ID, identifying a missing dependency in the repository environment, fixing it on a branch, and rerunning the Foundry check.

## Validation

- The diagnosis cites an exact request or build and an exact principal.
- Authentication and authorization are analyzed as separate layers.
- Backoff is bounded and used only for retryable `429` or `503` responses.
- The proposed remediation is the minimum change that addresses the confirmed cause.
- The post-fix request or build proves recovery without expanding access.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
