---
name: palantir-debug-bundle
description: >-
  Collect a minimal, redacted Foundry diagnostic bundle for API, OSDK, transform, or Compute Module incidents. Use when support or engineering needs reproducible evidence without credentials or protected data. Trigger with "Palantir debug bundle".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[request-build-or-module-id]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, debugging, incident-response]
---
# Palantir Redacted Diagnostic Bundle

## Overview

Collect identifiers and platform evidence that allow another operator to reproduce the failure while excluding bearer tokens, secrets, object values, dataset rows, and unnecessary logs. The bundle is an inventory and evidence manifest, not an indiscriminate archive.

## Prerequisites

- Identify the failure surface, time window, owner, support case, audience, and maximum allowed data classification.
- Obtain request IDs, build IDs, repository branch/commit, module version, SDK package versions, and non-secret environment metadata.
- Read `references/official-docs.md` and confirm whether log access is enabled and appropriately marked.
- Create the bundle in an access-controlled temporary location with an expiration owner.

## Current Contract

- Foundry build reports, debugger sessions, and metrics are distinct evidence surfaces.
- Service and trace logs can contain values from prompts, objects, or upstream systems; viewing them can require Edit permission, log access, and markings.
- A caller can record OAuth grant type and scope names without recording a bearer token or client secret.
- Python transform debugging is an interactive investigation tool; debugger values are not proof of committed output.

## Instructions

1. Write a manifest naming the incident, audience, time window, collection authority, and prohibited data.

2. Collect exact IDs, versions, branch/commit, timestamps, status or error names, sanitized request metadata, and relevant platform links.

3. Export only the smallest log excerpts authorized for the audience and replace tokens, secrets, personal data, and protected values with typed redaction markers.

4. Reproduce the issue with a safe request, preview, or sandbox build and record the result.

5. Review the bundle against the prohibition list, compute file hashes, set an expiration, and transfer through the approved channel.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

The resource owner authorizes evidence collection; the security or data owner authorizes any logs; the support owner authorizes transfer. Never attach `.env`, credential files, raw headers, datasets, object payloads, or complete log exports.

## Output

A manifest plus minimal redacted evidence: identifiers, versions, topology, timestamps, status/error names, selected platform links, reproduction result, file hashes, redaction record, audience, and expiration.

## Error Handling

| Condition | Response |
|---|---|
| The only reproduction requires production writeback | Stop and design a non-production or validation-only reproduction. |
| Log access is unavailable | Record the missing evidence and ask the authorized owner; do not broaden your own access. |
| A secret appears during review | Quarantine the bundle, rotate the exposed credential, regenerate sanitized evidence, and document the incident. |
| The bundle is too large to review | Reduce it to the failing request/build/module and the smallest relevant time window. |

## Examples

### Example 1

Prepare an API support bundle containing request ID, endpoint template, response status, grant type, scope names, SDK version, timestamps, and a redacted reproduction—without headers or object data.

### Example 2

Prepare a transform-build bundle containing build and job IDs, branch commit, declared inputs/outputs, failing stack frames, selected metrics, and a one-page reproduction manifest.

## Validation

- A second operator can identify and reproduce the failure from the manifest.
- Every file has an owner, classification, hash, and expiration.
- Secret and sensitive-value scans find no unapproved data.
- Log evidence is limited to the authorized source executor and time window.
- The transfer receipt confirms the intended audience only.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
