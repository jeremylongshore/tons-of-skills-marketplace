---
name: procore-core-workflow-b
description: >-
  Implement a Procore submittal workflow with version-aware discovery, required-field validation, workflow-state reconciliation, and controlled notifications. Use when listing, creating, routing, or reading submittals and their workflow data. Trigger with: "automate Procore submittals", "create a Procore submittal", "inspect submittal workflow".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[submittal-operation-and-project]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - submittals
  - approvals
compatibility: 'Requires a Procore project with Submittals enabled and an OAuth principal authorized for the chosen endpoint and workflow action.'
---

# Procore Version-Aware Submittal Workflow

## Overview

Submittal endpoints coexist across versions and may expose beta surfaces. Select the documented version per operation, preserve company routing and notification controls, and reconcile workflow state instead of assuming a generic approve-or-reject contract.

## Prerequisites

- Target company and project with Submittals enabled
- Current endpoint version and changelog reviewed for every intended operation
- Required managers, approvers, specification context, and notification policy resolved

## Instructions

### Step 1: Select the endpoint version

Open the current Submittals API reference and choose the supported route for the required operation. Record whether a surface is beta and obtain explicit risk acceptance before using it.

### Step 2: Discover project data

List a bounded page of submittals and retrieve workflow data for a representative record. Capture required headers, fields, allowed filters, and pagination metadata.

### Step 3: Validate the proposal

Resolve project users and specification references, obtain any next-number value through the documented endpoint, and make email behavior explicit. Never invent a workflow status.

### Step 4: Approve the mutation

Render a sanitized request preview with target project, selected API version, recipients, and expected outcome. Require approval before creating or changing a submittal.

### Step 5: Execute and reconcile

Send the mutation once, then fetch the submittal and its workflow data. Confirm the observed workflow state rather than trusting a local projection.

### Step 6: Record compatibility

Keep endpoint-version selection in an adapter and test both current response fields and failure shapes so future migrations remain bounded.

## Authentication

Submittal calls authenticate with an OAuth 2.0 Bearer token. Provide `Procore-Company-Id` wherever the endpoint reference requires it, and rely on the principal's project and Submittals permissions.

## Tool Discipline

Use Read and Grep to inspect endpoint versions, workflow fields, and project configuration. Use Write or Edit only for the approved adapter, test, proposal, or receipt; do not perform an unapproved submittal mutation.

## Output

- Endpoint-version and permission decision
- Validated submittal proposal and approval record
- Read-after-write workflow-state receipt

Return the selected route version, project, submittal identifier, notification choice, observed workflow state, and rollback owner.

## Examples

Before creating a submittal, an adapter reads the current reference, requests the project's next available number, resolves the manager and approvers, and previews whether emails will be sent. It then reconciles the returned workflow data after approval.

## Error Handling

| Failure | Response |
| --- | --- |
| Only beta endpoint fits | Document the gap and obtain risk acceptance; do not label beta as stable. |
| Required actor or spec is missing | Stop and resolve the project dependency before mutation. |
| 403 or 422 response | Preserve the provider detail and verify permissions, fields, and workflow constraints. |
| Read-after-write disagrees | Treat Procore as authoritative and halt downstream publication until reconciled. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Submittals API reference](https://developers.procore.com/reference/rest/submittals?version=latest)
- [API lifecycle](https://developers.procore.com/documentation/rest-api-lifecycle)
- [Error code reference](https://developers.procore.com/documentation/error-reference)
