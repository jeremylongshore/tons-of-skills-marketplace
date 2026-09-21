---
name: procore-enterprise-rbac
description: >-
  Govern Procore DMSA and user access through endpoint-to-tool permission mapping, permitted projects, installation review, and negative tests. Use when designing least privilege, investigating 403 or hidden 404 responses, or upgrading an app manifest. Trigger with: "audit Procore permissions", "scope a Procore DMSA", "review Procore project access".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[principal-and-endpoint-inventory]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - procore
  - permissions
  - least-privilege
compatibility: 'Requires Procore company administrator access, the application manifest, and an approved endpoint inventory.'
---

# Procore Permission and Project-Scope Governance

## Overview

Procore access is the intersection of OAuth principal, tool permission, enabled project tool, project membership, permitted projects, and company routing. Manage these dimensions explicitly rather than treating a broad role label as the API contract.

## Prerequisites

- User or DMSA identity and installed app version
- Complete endpoint, method, company, project, and data-classification inventory
- Current permission builder output and administrator for the target company

## Instructions

### Step 1: Map operations to tools

For each endpoint, record the company- or project-level Procore tool and minimum documented permission. Remove permissions that lack a current call-site owner.

### Step 2: Review the DMSA manifest

Compare declared permissions with the inventory before releasing a new app version. Treat newly requested permissions as a reviewed contract change.

### Step 3: Review permitted projects

List the projects selected during installation and compare them with the approved tenant scope. Remember that administrators may need to reconfigure permitted projects after app update or reinstall.

### Step 4: Avoid manual drift

Use App Management and the intended manifest workflow. Investigate directory-level manual adjustments because they can diverge from app permissions and complicate upgrades.

### Step 5: Test both sides

Run approved reads for required tools and expected-denial tests for an unpermitted project and an unnecessary operation. Treat excess access as a release blocker.

### Step 6: Record approval

Capture app version, permission diff, project-scope diff, administrator decision, test results, and rollback procedure without exposing tenant data.

## Authentication

API calls use OAuth 2.0 Bearer tokens. Authorization Code assumes the current user's permissions; DMSA Client Credentials assumes the DMSA permissions and permitted-project configuration established through installation.

## Tool Discipline

Use Read and Grep to inspect manifests, endpoint requirements, and permission evidence. Use Write or Edit only for the approved map, manifest change, test, or receipt; do not grant or revoke Procore access without administrator approval.

## Output

- Endpoint-to-tool permission matrix
- DMSA manifest and permitted-project diff
- Positive and negative authorization test evidence

Return unexplained permissions, missing access, excess access, approver, and safe rollback.

## Examples

An RFI reader requests only the RFI tool's documented read permission and access to selected pilot projects. The release test proves the pilot is readable and a non-permitted project remains inaccessible before the manifest is promoted.

## Error Handling

| Failure | Response |
| --- | --- |
| 403 on required endpoint | Verify app connection, tool permission, project membership, permitted project, and tool enablement. |
| Existing resource returns 404 | Treat concealed read access as a permission hypothesis, not proof of absence. |
| Manifest adds broad admin access | Reject unless each capability is documented and independently approved. |
| Update loses project scope | Reconfigure permitted projects and rerun positive and negative tests. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Developer Managed Service Accounts](https://developers.procore.com/documentation/developer-managed-service-accounts)
- [Working with user permissions](https://developers.procore.com/documentation/tutorial-user-permissions)
- [Troubleshooting permissions](https://developers.procore.com/documentation/troubleshooting)
