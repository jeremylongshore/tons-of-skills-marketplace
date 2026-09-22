---
name: techsmith-debug-bundle
description: >-
  Assemble a minimal redacted diagnostic bundle for Snagit COM, Camtasia recorder, deployment, project, or export failures. Use when support or engineering needs reproducible TechSmith evidence. Trigger with "TechSmith debug bundle", "collect Snagit diagnostics", or "Camtasia support evidence".
argument-hint: "[product] [incident-id] [output-directory]"
allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit
version: 1.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- desktop-automation
- techsmith
- diagnostics
model: inherit
effort: medium
compatibility: Designed for Claude Code; TechSmith product execution requires an approved Windows or macOS desktop as documented
---
# TechSmith Redacted Debug Bundle

## Overview

This skill gathers configuration and failure metadata without copying screen captures, videos, project media, user identities, or license keys. The bundle has an explicit schema, redaction pass, size limit, checksum, retention owner, and human review before sharing.

## Prerequisites

- Incident identifier, product/version, affected workstation, and failure timestamp window
- An approved local output directory outside active project storage
- Permission to read product logs and command results at the required classification
- A recipient, retention deadline, and redaction reviewer

## Tool Discipline

Use `Read`, `Glob`, and `Grep` to inspect local scripts, manifests, logs, and tests. Use `WebFetch` only for current primary TechSmith documentation. Use `Write` or `Edit` only after confirming the target repository file and approval boundary.

## Current Contract

- Collect versions, executable paths, COM-registration results, redacted commands, exit codes, and bounded log excerpts.
- For project failures, record paths and hashes rather than copying TSCPROJ, TREC, captures, or media by default.
- Never include a software key, activation request/response, account token, email address, or full environment dump.
- A bundle is not complete until a second redaction scan and manifest/file-count check pass.

## Licensing and Authentication

TechSmith desktop activation is not API authentication. Resolve individual sign-in versus business-key or approved offline activation before execution. Redact all keys, account identifiers, activation artifacts, and sensitive endpoint details.

## Instructions

1. Create an incident-specific directory with restrictive permissions and a maximum bundle size.
2. Record OS, architecture, session type, product version, executable discovery, and safe COM creation result.
3. Capture the exact failing operation, UTC timestamps, exit code, and allowlisted log lines around the failure.
4. Add local-storage status, free space, project-version metadata, media-presence counts, and output validation where relevant.
5. Use pattern and entropy scanning to redact keys, tokens, emails, usernames, and sensitive path components.
6. Write a manifest with hashes, review every file, archive the bundle, and set deletion ownership.

## Approval Boundaries

Do not add screenshots, clipboard data, recordings, project archives, browser state, registry exports, or unrestricted logs without case-specific written approval.

## Output

Return bundle path, manifest hash, file count, byte size, redaction result, omitted sensitive categories, reviewer, recipient, and deletion date.

## Error Handling

| Condition | Response |
|---|---|
| Bundle exceeds size limit | Replace bulk logs with bounded excerpts and hashes. |
| Secret scanner finds a match | Quarantine the bundle and redact or remove the source file. |
| Product version unavailable | Record the failed discovery command rather than guessing. |
| No approved recipient | Keep the bundle local and do not upload it. |

## Examples

The example below shows the minimum redacted evidence expected from a successful invocation of this operator workflow.

```text
incident=TS-204; files=6; bytes=184221; secrets=0; media_included=0; review=pass
```

## Resources

- [Skill-specific official documentation](references/official-docs.md)
- [Camtasia deployment guide](https://assets.techsmith.com/docs/Camtasia_2025_Deployment_Tool_Guide.pdf)
- [Snagit COM samples](https://github.com/TechSmith/Snagit-COM-Samples)
