---
name: bamboohr-security-basics
description: >-
  Threat-model and harden a BambooHR integration that handles employee PII,
  OAuth tokens, API keys, files, and webhooks. Use when reviewing access,
  storage, logging, or incident controls. Trigger with "secure BambooHR",
  "BambooHR PII", "BambooHR threat model", or "BambooHR secrets".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<integration-path> [auth|data|webhooks|full]"
version: 1.5.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, hr, bamboohr, security, privacy]
model: inherit
effort: high
compatibility: Designed for Claude Code
---
# BambooHR Integration Security

## Overview

Treat the connector as a high-sensitivity HR data system. Security is not only
secret storage: it includes tenant isolation, field-level authorization, data
minimization, webhook authenticity, auditability, and deletion.

## Prerequisites

- The target repository or integration path and the requested operator outcome.
- The tenant, identity, and data scope only when approved live work is in scope.
- The current evidence register plus customer-specific permissions and agreements.

## Current Contract

BambooHR permissions affect which employee fields and operations an identity
can access. The official SDK supports secure logging and request-ID extraction,
but application logs, queues, databases, exports, and support artifacts remain
the operator's responsibility. Webhook creation returns a one-time private key.

## Authentication

Use OAuth for partner integrations with validated `state`, exact HTTPS redirect
URIs, encrypted per-subject token storage, and persisted token rotation. For API
keys, use a dedicated least-privilege user, named owner, expiry review, and
tested revocation. Never share one identity across tenants.

## Instructions

1. Map trust boundaries: user/browser, callback, token store, connector,
   BambooHR tenant, queue, destination, logs, backups, support, and analytics.
2. Inventory every requested field and classify sensitivity. Remove fields not
   tied to an approved purpose; isolate government IDs, compensation, medical,
   dependent, benefit, and file data.
3. Enforce tenant from trusted credential metadata, not from a request body.
   Validate identifiers at every queue and storage boundary.
4. Redact authorization, keys, cookies, query strings, webhook secrets, and HR
   values. Allow request IDs, operation names, status, latency, and safe counts.
5. For webhooks, store the creation-only key atomically, verify HMAC-SHA256 over
   raw bytes using the currently documented carrier, compare in constant time,
   and reject before parsing or side effects.
6. Encrypt in transit and at rest, set retention and deletion jobs, restrict
   backup access, and test subject/customer deletion obligations.
7. Exercise cross-tenant access, denied fields, revoked credentials, replay,
   log injection, oversized payload, SSRF-like tenant input, and support-bundle
   exfiltration in tests.

## Tool Discipline

Use Read, Glob, and Grep for code and configuration inspection. Use Write/Edit
only for explicitly approved hardening and regression tests. Never write sample
secrets or real employee records.

## Approval Boundaries

Require security/data-owner approval before broadening fields, OAuth scopes,
API-key permissions, retention, destinations, webhook events, or support access.
Do not rotate or revoke live credentials as part of an audit without approval.

## Output

Return assets, trust boundaries, field inventory, identities and permissions,
findings by severity, exact remediation, test evidence, retention/deletion
controls, owners, and unresolved risk acceptances.

## Error Handling

- Suspected secret or HR-data exposure: stop collection, preserve minimal audit
  metadata, and invoke the organization's incident process.
- Cross-tenant ambiguity: fail closed before a BambooHR or destination request.
- Missing webhook verification contract: disable processing, not verification.

## Examples

- "Review our BambooHR logs" searches for sensitive categories without printing values.
- "Give the connector admin access" is replaced by an operation/field permission map.

## Resources

Read [official evidence](references/official-docs.md) and the executed customer
agreements before finalizing controls.
