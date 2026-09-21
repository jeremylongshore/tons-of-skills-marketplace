---
name: firecrawl-multi-env-setup
description: >-
  Separate Firecrawl development, staging, and production identities, targets, budgets, policies, telemetry, and data stores. Use when creating or auditing multiple environments. Trigger with "Firecrawl environments", "Firecrawl staging", or "separate Firecrawl keys".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <environment-set>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, environments, security]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Environment Separation

## Overview

Prevent a test from consuming production credits, crawling production targets, or writing captured content into the wrong store. Environment identity must be explicit and fail closed.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Cloud keys are team-scoped credentials and team limits are shared across keys, so separate keys alone do not guarantee capacity isolation. Key restrictions, spend limits, IP restrictions, distinct teams/accounts where appropriate, and an application policy gateway provide different isolation layers. Self-hosted evaluation has a separate capability and security contract.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Inventory each environment's owner, team/account, key, secret path, egress, allowed domains, endpoints/formats, spend ceiling, queue capacity, retention, store, and alert destination.
2. Create distinct secret-manager entries and workload identities. Validate that configuration names the environment and refuses missing or cross-environment values.
3. Apply environment-specific domain policy, explicit crawl/batch limits, endpoint/format restrictions where available, and non-production credit ceilings.
4. Keep production targets and captured fixtures out of developer machines and pull-request CI. Use synthetic fakes by default and a protected staging tenant for live tests.
5. Route telemetry and audit receipts with an environment label while redacting keys, URLs, custom headers, prompts, and bodies.
6. Test cross-environment secret, target, store, webhook, and queue mistakes; assert they fail before a Firecrawl request or downstream write.
7. Document promotion as configuration and evidence review, not copying a .env file; test independent rotation and rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before creating a team/key, adding a production target to staging, sharing capacity, changing spend controls, or copying data or configuration across environments.

## Output

Return an environment matrix, identities and secret references, target and endpoint policies, budget/capacity isolation, stores, tests, promotion path, and unresolved shared dependencies.

## Error Handling

- A shared team makes capacity isolation impossible: document it and add throttling or choose stronger isolation.
- Environment cannot be identified at startup: fail closed.
- A cross-environment write is detected: halt processing, preserve redacted evidence, and invoke data-incident handling.

## Examples

- "Set up Firecrawl staging" creates its own identity, policy, budget, telemetry, and store.
- "Reuse the production key locally" is rejected even if the key is convenient.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
