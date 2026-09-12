---
name: adobe-reference-architecture
description: >-
  Define a production Adobe architecture spanning identity, service adapters, async workers, asset custody, I/O Events, App Builder, evidence, and recovery. Use when this Adobe operator workflow is needed. Trigger with "design Adobe architecture", "Adobe reference architecture", or "standardize Adobe services".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<workloads> <services> <recovery-objectives>"
version: 1.8.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, adobe, architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Adobe actions require network access, appropriate entitlement and authentication, and explicit approval"
---
# Adobe Integration Reference Architecture

## Overview

Define a production Adobe architecture spanning identity, service adapters, async workers, asset custody, I/O Events, App Builder, evidence, and recovery.. This workflow produces a reviewable artifact and evidence before any live side effect.

## Prerequisites

- Current first-party Adobe documentation for every selected service, API version, auth flow, limit, and lifecycle.
- Named product, identity, security, data, budget, release, and operations owners appropriate to the scope.
- Synthetic or approved non-production fixtures with secret and content canaries.

## Current Contract

The architecture separates control plane from data plane: identity/entitlement/configuration/deploy/approvals are control; prompts/documents/images/events/jobs are data. Each Adobe product has its own version, storage, error, limit, and lifecycle adapter. Recheck the dated evidence map before relying on mutable product behavior.

## Authentication

Bind credential broker output to organization, project/workspace, service, scopes, product profiles, environment, and owner. User-owned data uses explicit user auth rather than silent S2S substitution.

## Instructions

1. State business workflows, sources of truth, services, data classifications, consistency, budget, RTO, and RPO.
2. Map clients, auth broker, service adapters, queues, workers, asset storage, event ingress, evidence store, and destinations.
3. Define request, async-status, idempotency, retry, cancellation, signed-URL, output-verification, and cleanup contracts per service.
4. Define I/O Events authenticity/deduplication and App Builder workspace/deploy/log boundaries.
5. Threat-model credential theft, cross-environment access, forged events, URL leakage, replay, duplicate spend, and retired API use.
6. Choose canary stages, capacity envelope, observability, incident controls, reconciliation, and tested rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect current documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Skill invocation alone does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, or deletion.

## Approval Boundaries

Architecture, security, data, budget, product, and operations owners approve production. New services, scopes, storage destinations, event providers, writes, or destructive actions require explicit approval.

## Error Handling

- Reject shared unbound credentials and generic one-client-for-everything designs.
- Reject synchronous waiting without cancellation/reconciliation.
- Reject architectures containing JWT, Photoshop v1, or retired Lightroom Firefly Services.

## Output

Return decision record, topology, trust boundaries, identity matrix, service contracts, data flows, failure modes, rollout, and rollback. Mark assumptions, observed environment behavior, owners, evidence dates, and unresolved gaps explicitly.

## Examples

- Trace one Firefly job from approval to verified artifact deletion.
- Trace one forged event to rejection before enqueue.

## Validation

Exercise and record expected and observed results for:

- auth boundary
- async job
- asset custody
- duplicate event
- vendor outage
- rollback

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated Adobe sources before execution.
- Treat observed tenant or product behavior as environment-specific evidence, never a universal Adobe guarantee.
