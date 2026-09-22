---
name: bamboohr-prod-checklist
description: >-
  Make a go/no-go decision for a BambooHR connector using exact evidence for
  auth, tenant isolation, HR-data handling, reliability, reconciliation,
  monitoring, and rollback. Use when reviewing a production launch or material expansion.
  Trigger with "BambooHR go live", "BambooHR production checklist", or
  "BambooHR launch review".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<release-id> <environment>"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, production, release]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Production Readiness Gate

## Overview

Issue a reproducible go/no-go verdict. A checklist item passes only with current
evidence tied to the release artifact and environment; "configured" or "tested
before" is not a receipt.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

The reviewed BambooHR contract includes tenant-local hosts, OAuth/API-key auth,
caller-owned refreshed-token persistence, typed request IDs/errors, finite SDK
retries, dataset v2, and one-time webhook keys. Legacy dataset/report
deprecations and Python package-registry uncertainty must be explicit.

## Authentication

Require auth mode, identity owner, tenant binding, field/operation permissions,
credential age, rotation/revocation runbook, and OAuth state/token-persistence
tests. Verify references, not secret values.

## Instructions

1. Freeze release commit and artifact digest. Confirm source, generated files,
   dependency lock, vulnerability/secret scans, and required CI are green.
2. Verify each tenant and environment has isolated configuration, identity,
   token/key storage, destination namespace, queues, and checkpoints.
3. Approve the minimum employee fields and workflows; confirm purpose,
   retention, encryption, deletion, backup, log, and support-evidence controls.
4. Prove offline tests for auth, tenant isolation, permission loss, pagination,
   reconciliation, retries, ambiguous writes, schema drift, webhook HMAC/replay,
   and redaction.
5. Prove production topology: timeouts, finite retries, per-tenant concurrency,
   circuit breaker, dead letter, alerts, dashboards, on-call ownership, and
   body-free health checks.
6. If using Python SDK source, record exact commit and approval; do not claim a
   public registry release until reverified. For PHP, record the locked Packagist version.
7. Rehearse rollback without deleting new data or replaying HR mutations. Define
   scheduler/queue ownership and checkpoint compatibility for both versions.
8. Run an approved canary, compare source/destination counts and identities, and
   observe through the agreed window.
9. Mark every gate PASS, FAIL, WAIVED with owner/expiry, or NOT APPLICABLE with
   reason. Any unresolved critical gate yields NO-GO.

## Tool Discipline

Use Read, Glob, and Grep to collect exact release evidence. Use Write/Edit only
for the approved readiness receipt and missing tests/configuration. This skill
does not deploy, rotate secrets, call tenants, or alter production state.

## Approval Boundaries

Launch approval must identify engineering, HR/data owner, security/privacy, and
operations owners as applicable. A waiver needs owner, rationale, compensating
control, and expiry.

## Output

Return release and artifact identity, gate table with evidence links, canary and
reconciliation result, waivers, rollback readiness, approvers, and final GO/NO-GO.

## Error Handling

- Evidence is stale or from another SHA/environment: mark the gate FAIL.
- Rollback depends on an untested mutation replay: NO-GO.
- Required owner absent: NO-GO; do not infer organizational approval.

## Examples

- "Everything passed last week" triggers evidence refresh against this artifact.
- "Ship despite missing token persistence" returns NO-GO for an OAuth connector.

## Resources

Read [official evidence](references/official-docs.md) during the release review.
