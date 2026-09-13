---
name: procore-core-workflow-a
description: >-
  Implement a governed Procore RFI lifecycle from read-only discovery through an approved create or update. Use when integrating RFI intake, assignment, response tracking, attachments, or closure without guessing workflow transitions. Trigger with: "automate Procore RFIs", "create a Procore RFI", "sync RFI status".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[rfi-operation-and-project]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - rfi
  - project-management
compatibility: 'Requires a Procore project with the RFI tool enabled and an OAuth principal holding the endpoint-specific permissions.'
---

# Procore Governed RFI Lifecycle

## Overview

Treat an RFI as a permissioned construction record with project configuration and business transitions, not generic CRUD. Derive fields and allowed actions from the current RFI reference and target project before submitting a mutation.

## Prerequisites

- Target company and project identifiers with the RFI tool enabled
- OAuth principal permitted for the exact read or write operation
- Current RFI endpoint reference, project field configuration, and approval owner

## Instructions

### Step 1: Discover the project contract

List or show a representative RFI to confirm response shape, configurable fields, status values, and project access. Follow Link-header pagination for inventory reads.

### Step 2: Build the intent

Capture subject, question, RFI manager, assignees, due-date policy, attachments, and notification choice. Resolve every referenced user or resource inside the same project.

### Step 3: Validate without side effects

Check required fields against the live endpoint reference and project configuration. Present a sanitized mutation preview and require an identified approver.

### Step 4: Execute once

Send the documented request only after approval. Record the response ID and status immediately; never infer success from a network timeout.

### Step 5: Reconcile lifecycle

Read the RFI after each material transition. Drive responses, distribution, acceptance, or closure only through documented endpoints and fields rather than invented status strings.

### Step 6: Preserve audit evidence

Store identifiers, before-and-after state hashes, actor, timestamp, and outcome without construction narrative or attachment contents.

## Authentication

RFI calls use an OAuth 2.0 Bearer token and the required company routing context. Effective access comes from the user or DMSA permissions, project membership, and whether the RFI tool is enabled.

## Tool Discipline

Use Read and Grep to inspect endpoint contracts, project configuration, and existing adapters. Use Write or Edit only for the approved adapter, test, mutation manifest, or redacted receipt; do not perform an unapproved RFI mutation.

## Output

- Validated RFI intent and permission evidence
- Approved mutation plus read-after-write reconciliation
- Sanitized lifecycle and rollback receipt

Return the project, operation, RFI identifier, observed transition, approval reference, and unresolved dependencies.

## Examples

A field issue becomes an RFI only after the integration resolves the project RFI manager and validates required fields. The service previews the request, records approval, creates once, and reads the returned record before notifying downstream systems.

## Error Handling

| Failure | Response |
| --- | --- |
| Required user is invalid | Resolve membership in the target project; do not substitute another user. |
| 403 or hidden 404 | Check app connection, RFI permissions, project membership, and tool enablement. |
| 422 validation response | Surface the provider error and project field contract; do not strip fields blindly. |
| Mutation outcome is unknown | Reconcile by returned ID or an approved correlation key before retrying. |

## Resources

- [First-party source notes](references/official-docs.md)
- [RFI API reference](https://developers.procore.com/reference/rest/rfis?version=latest)
- [Error code reference](https://developers.procore.com/documentation/error-reference)
- [File attachments and image uploads](https://developers.procore.com/documentation/tutorial-attachments)
