---
name: bamboohr-reference-architecture
description: >-
  Design a multi-tenant BambooHR connector with explicit auth, ingestion,
  webhook, queue, storage, destination, reconciliation, and audit boundaries.
  Use when creating or reviewing production HR integration architecture.
  Trigger with "BambooHR architecture", "BambooHR system design", or
  "multi-tenant BambooHR connector".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<integration-scope> <single-tenant|multi-tenant>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, architecture, multi-tenant]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Reference Architecture

## Overview

Produce an architecture that keeps control-plane actions, HR data-plane reads,
mutations, webhook reception, and downstream delivery independently governable.
The connector is not the authority for HR policy; BambooHR and the approved
destination each retain explicit ownership.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

Use tenant-local BambooHR hosts and current official OpenAPI operations. Prefer
dataset v2 for new bulk reads. Support OAuth token refresh with external
persistence, typed request IDs/errors, bounded retries, and webhook one-time key
custody. Treat deprecated report/dataset v1 paths as migration boundaries.

## Authentication

The control plane stores encrypted, tenant-scoped credential metadata and exact
redirect/permission configuration. Workers receive short-lived access to one
tenant credential; they cannot choose arbitrary hosts or read another tenant's
tokens. API-key mode uses a dedicated BambooHR identity and explicit rotation.

## Instructions

1. Define actors, tenants, business outcomes, systems of record, fields,
   workflows, freshness, scale, residency, retention, and recovery objectives.
2. Draw trust boundaries among consent/callback, token store, scheduler, sync
   worker, webhook ingress, queue, schema validator, destination adapter,
   checkpoint store, audit log, monitoring, and support tooling.
3. Separate read and mutation workers and permissions. Route jobs with an
   immutable tenant ID resolved to trusted credential and destination metadata.
4. For scheduled sync, use minimized dataset v2 reads, deterministic pagination,
   transactional checkpoints, idempotent destination upsert, and periodic full
   reconciliation.
5. For webhooks, terminate TLS, retain raw bytes only in memory for verified
   HMAC, reject replay, enqueue idempotently, acknowledge promptly, and use the
   event only as a trigger for an authorized source read when appropriate.
6. Enforce field allowlists and schema versions before queues/storage. Encrypt
   approved HR data and keep bodies out of general logs, traces, and dead letters.
7. Add per-tenant concurrency, finite retries, circuit breaker, dead-letter
   review, request-ID correlation, and backpressure.
8. Design credential revocation, tenant offboarding, data deletion, webhook
   replacement, schema migration, regional failure, and rollback before launch.

## Tool Discipline

Use Read, Glob, and Grep to ground the design in the existing system. Use
Write/Edit only for approved architecture records, diagrams-as-code, and
interface contracts. This skill does not provision or mutate infrastructure.

## Approval Boundaries

Require approval for field and workflow scope, auth model, tenant routing,
regions, retention, destination authority, webhook events, mutation path, and
recovery objectives. Record unresolved decisions rather than guessing.

## Output

Return context/container/component views, data flows and trust boundaries,
identity/permission matrix, field contract, queue/checkpoint/idempotency model,
failure paths, SLOs, retention/deletion, decisions, risks, and validation plan.

## Error Handling

- Unknown system of record: stop write-path design until ownership is resolved.
- Shared tenant credential/destination namespace: classify as a blocking isolation risk.
- No reconciliation or rollback model: architecture is not production-ready.

## Examples

- "Design employee sync" yields both scheduled reconciliation and webhook trigger paths.
- "Use one admin key for all customers" is rejected at the tenant trust boundary.

## Resources

Read [official evidence](references/official-docs.md) before finalizing interfaces.
