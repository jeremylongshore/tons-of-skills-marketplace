---
name: navan-reference-architecture
description: >-
  Design a Navan integration architecture with explicit trust, data, identity, and accounting boundaries. Use when building a multi-system travel or expense flow. Trigger with "design Navan architecture", "Navan integration diagram", or "Navan data platform".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surfaces> <destinations> <risk-tier>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Governed Integration Architecture

## Overview

Design a Navan integration architecture with explicit trust, data, identity, and accounting boundaries. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

A durable design separates vendor access, intake, immutable staging, normalization, policy, publication, write-back, reconciliation, and audit. It supports the tenant's actual API, SFTP, SCIM, SSO, or direct-integration contracts without assuming one universal transport.

## Authentication

Place secrets at the ingress boundary, bind each identity to one tenant and purpose, and keep administrative, ingestion, and write-back privileges separate.

## Instructions

1. Inventory Navan surfaces, owners, data classes, consumers, and side effects.
2. Draw trust zones and every network, storage, AI, and human boundary.
3. Define canonical identifiers, money, time, lifecycle, and lineage models.
4. Add queues, checkpoints, deduplication, quarantine, and reconciliation.
5. Specify redaction, retention, encryption, access, deletion, and incident controls.
6. Document scaling, failure, deployment, rollback, and contract-upgrade paths.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

New processors, sensitive destinations, cross-border flows, AI/MCP access, write-back, production identities, and retention changes require architecture and data-owner approval.

## Error Handling

- Do not couple acknowledgement to downstream success without durable receipt.
- Avoid a shared credential across tenants or purposes.
- No diagram is complete without failure and reconciliation paths.

## Output

Return a component map, data-flow and trust boundaries, identity matrix, control owners, failure paths, and decision log. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Separate booking intake from duty-of-care publication.
- Isolate expense reconciliation from privileged ERP posting.

## Validation

Walk success, duplicate, late correction, credential theft, vendor outage, destination outage, data request, and rollback. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
