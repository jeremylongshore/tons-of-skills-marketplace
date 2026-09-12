---
name: notion-advanced-troubleshooting
description: >-
  Diagnose difficult Notion integration failures from redacted evidence without trial-and-error writes. Use when ordinary error handling has not isolated the fault. Trigger with "trace Notion failure", "analyze Notion request ID", or "debug Notion permissions".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<environment> <symptom> <request-id-or-window>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, troubleshooting]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Evidence-First Advanced Troubleshooting

## Overview

Diagnose difficult Notion integration failures from redacted evidence without trial-and-error writes.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Treat the HTTP status, Notion error code, request identifier, selected API version, object type, and connection access graph as separate evidence. A page, database, and data source ID are not interchangeable. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Use a redacted credential fingerprint only. Confirm connection type, token owner, capabilities, shared content, and environment; never copy a bearer token into a bundle.

## Instructions

1. Freeze retries and preserve one representative response with its request identifier.
2. Reconstruct the request method, object type, selected version, payload shape, and target environment.
3. Trace effective access from token owner through capabilities and explicitly shared content.
4. Classify the fault as transport, authentication, authorization, object identity, version shape, limit, conflict, or service failure.
5. Reproduce with a read-only metadata request or fixture before proposing any write.
6. Return the smallest corrective change, rollback, and escalation evidence.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require the content owner before reading a new page, expanding capabilities, changing sharing, replaying a write, or sending evidence to support.

## Error Handling

- Do not convert a 403 into a broader token request until content sharing and capabilities are independently checked.
- Do not retry validation or conflict errors blindly.
- If evidence contains secrets or workspace content, stop and redact before continuing.

## Output

Return a timeline, request fingerprint, evidence table, fault classification, ruled-out causes, minimal fix, rollback, and escalation package. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Separate an inaccessible data source from a malformed filter.
- Use a request identifier and redacted response to escalate a persistent service fault.

## Validation

Exercise and record these paths with expected and observed results:

- secret-free evidence
- correct object identity
- version-aware payload
- read-only reproduction
- minimal fix
- rollback tested

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
