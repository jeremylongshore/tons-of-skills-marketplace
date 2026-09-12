---
name: fireflies-enterprise-rbac
description: >-
  Govern Fireflies team roles, channels, privacy, sharing, and privileged mutations with current permission and rate-limit checks. Use when performing enterprise administration or access review. Trigger with "Fireflies RBAC", "Fireflies admin", or "change meeting access".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <workflow-scope>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, rbac, enterprise]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Team Access and Privileged Mutations

## Overview

Govern Fireflies team roles, channels, privacy, sharing, and privileged mutations with current permission and rate-limit checks.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

setUserRole accepts admin or user and requires admin authority while preserving at least one admin. Private channels are visible only to members. Privacy values include link, owner, participants, teammatesandparticipants, and teammates. Meeting owners or same-team admins control supported privacy, sharing, and channel mutations.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Inventory the acting principal, target users or meetings, current roles, channels, privacy, and shares.
2. Separate read-only access review from mutation planning.
3. Validate least privilege, ownership, same-team constraints, and the remaining-admin invariant.
4. Preview exact role, privacy, share, revoke, or channel changes with affected identities through a restricted channel.
5. Obtain accountable approval and execute one bounded mutation batch.
6. For updateMeetingChannel, enforce 1–5 transcript IDs and its all-or-nothing behavior.
7. Re-query safe state, record a redacted receipt, and define rollback where the API supports it.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before every role, channel, privacy, sharing, or revocation mutation; public-link privacy requires explicit data-owner approval.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- require_elevated_privilege: stop instead of switching to a broader key.
- admin_must_exist: preserve at least one administrator.
- Batch channel update fails: treat the whole 1–5 item batch as unchanged and reconcile.

## Examples

- "Review fireflies team access and privileged mutations" produces a bounded plan and redacted receipt.
- A request that widens access or mutates production is paused at the approval boundary.

## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
