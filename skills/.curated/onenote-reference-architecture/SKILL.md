---
name: onenote-reference-architecture
description: >-
  Define a production OneNote architecture for delegated access, multiple content locations, bounded workers, reconciliation, and evidence. Use when standardizing several OneNote workloads. Trigger with "design OneNote architecture", "standardize OneNote services", or "review OneNote topology".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workloads> <locations> <recovery-objectives>"
version: 1.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, onenote, architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live OneNote actions require network access, delegated authentication, and explicit approval"
---
# OneNote Integration Reference Architecture

## Overview

Define a production OneNote architecture for delegated access, multiple content locations, bounded workers, reconciliation, and evidence.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Microsoft Graph OneNote documentation and the selected integration's tested contract.
- Named identity, content, workload, security, and operations owners appropriate to the requested scope.
- Synthetic or approved non-production fixtures with secrets and real notebook content removed.

## Current Contract

The architecture must distinguish user, Microsoft 365 group, and SharePoint-site roots; delegated user sessions; metadata versus page bodies; reads versus controlled HTML writes; queues; and reconciliation. OneNote does not provide documented change notifications or delta for these resources. Recheck the dated evidence map before relying on mutable permissions, limits, SDK behavior, supported resources, or cloud availability.

## Authentication

Bind each authorization grant to app, tenant, user, environment, scopes, and approved roots. Encrypt token caches and separate deployment authority from content authority.

## Instructions

1. State workloads, sources of truth, locations, consistency, recovery, and data-classification objectives.
2. Map clients, auth broker, encrypted token store, OneNote gateway, per-user queues, workers, checkpoints, evidence, and destinations.
3. Define v1.0 request, hierarchy, paging, HTML, error, and throttling contracts at the gateway.
4. Design scheduled section-scoped polling and full reconciliation without undocumented delta or webhook endpoints.
5. Threat-model token theft, cross-user access, content leakage, replay, queue starvation, and unsupported cloud deployment.
6. Choose rollout stages, capacity envelope, observability, incident controls, and tested rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, delegated credentials, tenant or notebook content, consent, file transfer, deployment, writes, spend, sharing changes, or deletion.

## Approval Boundaries

Require architecture, identity, security, content, and operations owners before production. New roots, scopes, destinations, or writes each require explicit approval.

## Error Handling

- Reject app-only or tenant-unbound designs.
- Reject event-driven claims without a supported OneNote signal.
- Reject an architecture without pagination, reconciliation, and revoked-session handling.

## Output

Return the decision record, topology, trust boundaries, identity model, data flows, failure modes, capacity model, rollout, and rollback. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Model two users and a group notebook without cross-user queue leakage.
- Recover a polling checkpoint after revocation and reauthentication.

## Validation

Exercise and record these paths with expected and observed results:

- user root
- group root
- site root
- revocation
- queue isolation
- reconciliation

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal OneNote guarantee.
