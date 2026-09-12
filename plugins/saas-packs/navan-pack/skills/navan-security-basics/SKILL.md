---
name: navan-security-basics
description: >-
  Threat-model a Navan integration across identity, travel, expense, payment, file, and downstream systems. Use when performing design or security review. Trigger with "secure Navan integration", "Navan threat model", or "review Navan data flow".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<surface> <data-class> <destination>"
version: 1.9.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, navan, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live or external Navan actions require network access and explicit approval"
---
# Navan Integration Security Boundary

## Overview

Threat-model a Navan integration across identity, travel, expense, payment, file, and downstream systems. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Access to the selected tenant's current Navan Help Center and contracted integration documentation.
- A named business owner and data owner for the travel or expense workflow.
- A non-production evidence set with secrets and traveler data removed.

## Current Contract

Navan states that its APIs undergo security testing and that data in transit and sensitive data at rest are encrypted. Those vendor controls do not replace customer-side least privilege, downstream encryption, retention, monitoring, or third-party AI governance.

## Authentication

Use dedicated integration identities, scoped access, approved secret storage, host binding, rotation, and revocation. Keep interactive admin and automation credentials separate.

## Instructions

1. Draw trust boundaries from Navan through every processor and destination.
2. Classify credentials and traveler, itinerary, payment, receipt, profile, and location data.
3. Minimize fields, purposes, destinations, retention, and human access.
4. Model credential theft, tenant mix-up, injection, replay, exfiltration, and confused-deputy paths.
5. Add deny-by-default network, logging, artifact, and AI-tool policies.
6. Test detection, containment, revocation, reconciliation, and notification paths.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, schemas, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, traveler or expense data, bookings, payments, policy or identity changes, file transfers, deployments, or deletion.

## Approval Boundaries

Any new processor, third-party AI or MCP connection, broader scope, production secret, cross-border transfer, or sensitive-data export requires security and data-owner approval.

## Error Handling

- Do not put traveler or receipt content in prompts or logs by default.
- Certification badges are not authorization for a new use.
- Fail closed on tenant, host, identity, or destination ambiguity.

## Output

Return a data-flow diagram, threat register, control owners, residual risks, approval boundaries, and verification plan. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Review a Booking API feed into a duty-of-care vendor.
- Constrain an MCP assistant to a minimal approved itinerary view.

## Validation

Exercise tenant isolation, revoked credentials, malicious fields, log redaction, unauthorized destination, and incident containment. Record expected and observed results, including fail-closed behavior.

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources and the selected tenant's in-account contract before relying on mutable endpoints, fields, entitlements, limits, or delivery behavior.
- Record tenant observations as environment-specific evidence, never universal Navan guarantees.
