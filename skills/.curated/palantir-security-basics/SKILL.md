---
name: palantir-security-basics
description: >-
  Establish a Foundry security baseline for users, service applications, data resources, Ontology policies, logs, and exports. Use when onboarding, reviewing architecture, or hardening a release. Trigger with "Palantir security".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[project-application-or-workflow]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, security, least-privilege]
---
# Palantir Foundry Security Baseline

## Overview

Apply least privilege across discretionary roles, mandatory controls, OAuth clients, Ontology policies, logs, and exports. Test both intended access and denial because each control plane covers a different boundary.

## Prerequisites

- Identify owners, users/groups, service users, projects, organizations, markings/CBAC, datasets, Ontology resources, applications, logs, exports, and incident contacts.
- Classify the maximum data sensitivity and writeback impact for the workflow.
- Read `references/official-docs.md` and the target enrollment's policies.
- Begin with a read-only inventory and approved synthetic test personas.

## Current Contract

- Projects and roles govern discretionary access; organizations, markings, and CBAC remain mandatory.
- Developer Console application restrictions and OAuth scopes constrain API clients alongside user/service-user permissions.
- Ontology object/property policies support granular read controls, but mandatory controls are needed where downstream propagation matters.
- Logs and audit exports may contain sensitive values and require explicit access, marking, audience, and retention decisions.

## Authentication

Prefer the grant designed for the architecture, keep secrets in an approved manager, restrict resources and operations, request minimum scopes, and assign rotation/revocation owners. Never use personal tokens for unattended production workloads.

## Instructions

1. Inventory every principal and control plane, then map each permission to a business purpose, resource, owner, and expiry.

2. Move routine access to groups and reduce project roles to the minimum capability.

3. Restrict Developer Console clients to required Ontology entities or Platform operations and verify the acting principal separately.

4. Apply object/property policies and mandatory controls according to read and propagation requirements.

5. Govern logs and exports, run positive/negative tests, scan artifacts for secrets, and schedule access recertification.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

Project, data, security, application, and organization owners approve their respective controls. Credential rotation, permission grants, unmarking, log enablement, and exports are independent live actions.

## Output

A security inventory, threat and data-flow summary, entitlement/control matrix, OAuth restrictions, object/property policy, log/export controls, test evidence, secret-rotation plan, exceptions, and recertification.

## Error Handling

| Condition | Response |
|---|---|
| A token is exposed | Revoke and rotate it, remove it from artifacts/history, assess access, and document the incident. |
| A negative persona can read data | Block release, identify the permitting control plane, and correct the minimum policy. |
| A role appears correct but access fails | Check mandatory controls, dependencies, and application restrictions without broadening everything. |
| A log/export contains unexpected values | Stop access or export, correct logging and markings, and assess exposure. |

## Examples

### Example 1

Harden a backend OSDK service by restricting its service user, OAuth scopes, Developer Console resources, returned properties, log contents, secret storage, and rotation procedure.

### Example 2

Review an Ontology workflow by testing row/property policies for approved personas and applying mandatory controls to derived datasets or exports that require continued protection.

## Validation

- Every principal and permission has a purpose, owner, and review date.
- Positive and negative access tests cover projects, mandatory controls, and application restrictions.
- Secrets are absent from repositories, images, logs, and deliverables.
- Downstream propagation and export controls are explicitly tested.
- Exceptions are time-bounded and monitored.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
