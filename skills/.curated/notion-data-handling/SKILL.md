---
name: notion-data-handling
description: >-
  Define data classification, minimization, retention, and deletion controls for a Notion integration. Use when workspace content or user data crosses a system boundary. Trigger with "govern Notion data", "review Notion PII", or "design Notion retention".
allowed-tools: Read,Glob,Grep,Write,Edit
argument-hint: "<data-flow> <jurisdiction> <retention-objective>"
version: 1.40.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags: [saas, notion, privacy]
model: inherit
effort: high
compatibility: "Designed for Claude Code; live Notion actions require network access and explicit approval"
---
# Notion Data Handling and Privacy Control

## Overview

Define data classification, minimization, retention, and deletion controls for a Notion integration.. This workflow produces an auditable decision or artifact before any live action.

## Prerequisites

- Current first-party Notion documentation and the selected integration's tested API-version contract.
- A named workspace owner, content or data owner, and operation owner.
- Synthetic or approved non-production fixtures with secrets and workspace content removed.

## Current Contract

Notion page content, properties, comments, user objects, files, logs, and webhook metadata have different sensitivity and lifecycle characteristics. Connection capabilities and content sharing bound access but do not replace application governance. Recheck the dated evidence map before relying on mutable fields, endpoints, versions, limits, or delivery behavior.

## Authentication

Minimize content and user capabilities, separate tenants, and prohibit credentials or raw sensitive content in logs and fixtures.

## Instructions

1. Map collection, purpose, lawful basis, classification, owner, processor, destination, and retention for every field class.
2. Minimize requested capabilities, selected properties, page bodies, user fields, and webhook subscriptions.
3. Define encryption, tenant isolation, logging, backup, export, correction, deletion, and legal-hold behavior.
4. Represent Notion trash, application deletion, destination deletion, and retained audit evidence as separate states.
5. Exercise subject and owner workflows on synthetic records before production.
6. Record residual risk, exceptions, expiry dates, and review owners.

## Tool Discipline

Use Read, Glob, and Grep to inspect documentation, configuration, code, fixtures, and evidence. Use Write and Edit only for approved repository artifacts. Invocation alone does not authorize network access, credentials, workspace content, user data, file transfer, deployment, capability or sharing changes, writes, spend, or deletion.

## Approval Boundaries

Require privacy, security, and data-owner approval before sensitive reads, external processing, historical export, retention change, or irreversible deletion.

## Error Handling

- Do not infer deletion from a missing search result.
- Do not log page bodies to prove a privacy control.
- Freeze deletion when legal hold or object identity is unresolved.

## Output

Return the data-flow map, field-class register, control matrix, retention schedule, deletion state machine, test evidence, and exceptions. Identify assumptions, owners, expirations, and evidence gaps explicitly.

## Examples

- Export only approved properties for a subject request.
- Prove destination deletion while retaining a content-free audit receipt.

## Validation

Exercise and record these paths with expected and observed results:

- least privilege
- tenant isolation
- redacted logs
- retention expiry
- legal hold
- deletion reconciliation

## Resources

- [Current first-party evidence map](references/official-docs.md) — recheck dated sources before relying on mutable behavior.
- Treat observed tenant behavior as environment-specific evidence, never a universal Notion guarantee.
