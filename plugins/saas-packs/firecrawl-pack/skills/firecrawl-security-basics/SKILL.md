---
name: firecrawl-security-basics
description: >-
  Secure Firecrawl identities, targets, request options, webhooks, untrusted content, retention, logs, and self-hosted exposure. Use when threat-modeling or hardening an integration. Trigger with "secure Firecrawl", "Firecrawl security review", or "Firecrawl secrets".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<repository-path> <environment>"
version: 1.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, firecrawl, security, privacy]
model: inherit
effort: high
compatibility: "Designed for Claude Code; Firecrawl Cloud work requires network access"
---
# Firecrawl Security Baseline

## Overview

Protect both directions of the integration: credentials and requests sent to Firecrawl, and hostile or sensitive content returned from target sites.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The source authorization, data classification, and environment policy.
- Current Firecrawl documentation, credentials only when needed, and an owner for approvals.

## Current Contract

Cloud uses Bearer API keys; enterprise controls can restrict key endpoints/formats and source IPs and can add threat protection and SIEM evidence. Webhooks use X-Firecrawl-Signature with sha256=hex over the raw body. Cache, ZDR, lockdown, headers/actions, profiles, screenshots, and self-hosting have distinct data and threat boundaries.

## Authentication

For authenticated Cloud operations, inject FIRECRAWL_API_KEY from an approved
secret manager. REST requests use Authorization: Bearer with the key. Never print,
commit, transmit, or place a key in a URL. Keyless access is suitable only where
the current documentation explicitly allows it and the workload accepts its
limits; production workflows should make identity and team ownership explicit.

## Instructions

1. Inventory secrets, teams/roles, key owners, environments, source networks, allowed endpoints/formats, domains, custom headers, retained data, webhooks, stores, and downstream actions.
2. Move every key and webhook secret to an approved secret manager; use workload identity, least privilege, rotation, revocation, and separate environments.
3. Canonicalize and authorize targets before requests. Block private/link-local networks, embedded credentials, disallowed redirects/ports, lookalike hosts, and unauthorized authenticated pages.
4. Minimize formats, actions, headers, profiles, proxies, and retention. Apply key/IP/threat controls where available and keep application policy fail closed.
5. Verify every webhook against raw bytes, require the sha256 prefix, decode equal-length hex, compare timing-safely, deduplicate webhookId, and acknowledge only accepted work.
6. Treat scraped content and extracted JSON as untrusted. Sanitize active content, isolate it from privileged prompts/actions, validate schemas, and scan stored artifacts.
7. For self-hosting, add supported authentication, network controls, TLS, durable stores, patching, backups, monitoring, and provider data-flow review before exposure.

## Tool Discipline

Use Read, Glob, and Grep to inspect code, configuration, tests, and evidence. Use
Write/Edit only for approved implementation or documentation changes. Do not call
Firecrawl, rotate keys, change account settings, scrape a target, or deploy merely
because this skill was invoked.

## Approval Boundaries

Require security/data approval before authenticated scraping, custom headers, browser profiles/actions, sensitive retention, restriction changes, self-host exposure, or adding external providers.

## Output

Return a threat model, identity and secret inventory, target and request controls, webhook verification design, content trust boundary, retention decision, self-host posture, tests, and residual risks.

## Error Handling

- A secret appears in logs or artifacts: revoke/rotate as required and invoke incident handling.
- Webhook raw bytes are unavailable or signature malformed: reject the delivery.
- Target resolution or redirect escapes policy: stop before sending headers or credentials.

## Examples

- "Verify Firecrawl webhooks" validates the exact signed raw body and sha256 format.
- "Pass customer cookies to any URL" is rejected until target, secret, retention, and session controls are approved.

## Resources

Read [official Firecrawl evidence](references/official-docs.md) before relying on
an endpoint, SDK method, plan limit, price, retention option, or self-hosted release.
