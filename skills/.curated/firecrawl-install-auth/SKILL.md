---
name: firecrawl-install-auth
description: >-
  Install the current Firecrawl Node or Python SDK, configure Cloud authentication, and verify package provenance and secret injection. Use when bootstrapping or repairing client setup. Trigger with "install Firecrawl", "configure FIRECRAWL_API_KEY", or "Firecrawl authentication".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> [node|python|rest]"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, installation, authentication]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl SDK Installation and Authentication

## Overview

Make the client dependency, v2 surface, identity owner, and secret path explicit. Do not preserve the legacy method surface merely because an old package still resolves.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Current first-party docs install the Node package as firecrawl and construct the named Firecrawl client; the underlying published SDK is maintained in firecrawl/firecrawl. Python installs firecrawl-py and imports Firecrawl. Top-level clients default to v2, while feature-frozen v1 compatibility is separate. REST Cloud requests use Bearer keys.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Inspect the repository language, runtime, lockfile, package manager, current Firecrawl dependency/imports, endpoint family, and secret conventions.
2. Confirm the official package from Firecrawl's docs and source, then add it through the existing package manager with a reviewed version range and lockfile change.
3. Replace legacy FirecrawlApp/scrapeUrl-style usage only as part of an explicit v2 migration; do not mix old and new methods under one untyped wrapper.
4. Create one client per process boundary using FIRECRAWL_API_KEY from the approved secret manager. Permit a custom API URL only for an explicitly selected self-hosted environment.
5. Validate configuration at startup using presence and shape checks without logging the key. Associate the secret with an owning team, workload, environment, and rotation record.
6. Run offline construction/type tests, then one approved minimal scrape if network validation is authorized. Assert provenance and metadata.statusCode without logging content.
7. Record the resolved package version, source, lockfile diff, auth mode, test evidence, and rollback.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require approval before adding the dependency, changing its major version, creating or rotating a key, enabling keyless production traffic, or pointing at a nonstandard API URL.

## Output

Return runtime and package-manager findings, package/source/version, import and v2 method surface, secret-manager reference, identity owner, verification results, and rollback steps.

## Error Handling

- Package identity is ambiguous: stop and verify against official docs and repository metadata.
- Key is missing: fail startup for authenticated operations; never substitute a stand-in value or another environment's key.
- Legacy calls remain: inventory and migrate them deliberately rather than hiding them behind any casts.

## Examples

- "Install Firecrawl for TypeScript" uses the current Node package and named client from official docs.
- "Paste the key into config.ts" is rejected in favor of secret-managed FIRECRAWL_API_KEY.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
