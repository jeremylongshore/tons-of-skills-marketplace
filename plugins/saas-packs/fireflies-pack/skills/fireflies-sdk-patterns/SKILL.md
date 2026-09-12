---
name: fireflies-sdk-patterns
description: >-
  Build a typed, bounded Fireflies GraphQL client with operation names, variables, error handling, redaction, and dependency injection. Use when replacing ad hoc requests or a fictional SDK wrapper. Trigger with "Fireflies client pattern", "type Fireflies GraphQL", or "Fireflies API wrapper".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <language>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, fireflies, graphql, architecture]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Fireflies work requires network access"
---
# Fireflies Typed GraphQL Client Patterns

## Overview

Fireflies documents a GraphQL API, not a required first-party language SDK. Keep the transport standards-based and generate or hand-maintain types only from reviewed schema evidence.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The Fireflies principal, team, environment, and data classification for the work.
- Current Fireflies documentation, credentials only when needed, and an accountable approver.

## Current Contract

Every call should carry an operation name, static document, typed variables, an explicit field selection, timeout, and response parser that handles both data and errors. Never interpolate values into GraphQL source or expose bearer keys to clients.

## Authentication

For authenticated operations, inject `FIREFLIES_API_KEY` from an approved secret manager and send it only as `Authorization: Bearer REDACTED_KEY` to `https://api.fireflies.ai/graphql`. Never print, commit, place in a URL, forward to a browser, or include the key in evidence. Webhook signing secrets are separate credentials and must not be reused as API keys.

## Instructions

1. Inventory operations and remove undocumented SDK method assumptions.
2. Choose a maintained GraphQL transport compatible with the repository rather than adding a redundant wrapper stack.
3. Define static documents and typed variables for each approved operation.
4. Centralize endpoint, bearer injection, timeouts, request IDs, redaction, and GraphQL error normalization.
5. Return domain-specific results that preserve nullability and partial-data semantics.
6. Inject the client into callers and provide a fixture transport for tests.
7. Pin dependencies and add schema-drift checks without enabling unrestricted introspection in production.


## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use Write/Edit only for approved implementation or documentation changes. Do not query Fireflies, retrieve meeting content, create an AskFred thread, upload media, change account state, replay an event, or deploy merely because this skill was invoked.

## Approval Boundaries

Require approval before adding a new mutation, exposing a new selected field, enabling tenant-wide access, or replacing the repository's transport dependency.

## Output

Return the exact operation or event surface, environment, authorization class, selected field groups, validation results, content-free metrics, decisions, and a concise pass/fail receipt. Keep secrets and meeting-derived content out of general output.

## Validation

Before reporting success, rerun the smallest relevant deterministic check, compare actual state with the requested outcome and current contract, verify no secret or meeting-derived content entered logs or artifacts, and record unresolved uncertainty explicitly.

## Error Handling

- Unknown field: compare the document with current first-party schema docs.
- Partial data with errors: do not silently treat it as complete.
- Dynamic query construction: replace with static documents and variables.

## Examples

- "Create a transcript client" defines named read operations and redacted error types.
- "Use an undocumented convenience SDK method" is corrected because no such required public SDK contract is assumed.


## Resources

Read [official Fireflies.ai evidence](references/official-docs.md) before relying on a field, filter, event, permission, plan limit, mutation, or processing state.
