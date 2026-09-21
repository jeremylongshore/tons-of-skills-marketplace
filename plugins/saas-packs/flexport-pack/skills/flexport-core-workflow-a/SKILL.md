---
name: flexport-core-workflow-a
description: >-
  Run Flexport MCP rate discovery through a human-approved booking decision. Use when searching lanes, evaluating full price, requesting a quote, or booking freight with an auditable approval boundary. Trigger with: "search Flexport rates", "book Flexport freight", "approve Flexport quote".
allowed-tools: Read, Grep, Write, Edit
version: 2.0.0
argument-hint: '[lane-cargo-and-approval-policy]'
model: inherit
effort: high
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
  - saas
  - flexport
  - booking
  - mcp
compatibility: 'Requires an authenticated Flexport MCP connection, account permission for selected tools, and an authorized freight approver.'
---

# Approval-Gated Flexport Rate to Booking

## Overview

Separate discovery from commitment. MCP rate tools can search, evaluate, request, and book; a booking must never be inferred from a search result or performed before a named approver accepts the final normalized terms.

## Prerequisites

- Validated origin, destination, cargo, dates, mode, and incoterm
- Authenticated connection to `https://mcp.flexport.com/mcp`
- Named approver, spend boundary, and duplicate-prevention store

## Instructions

### Step 1: Normalize the lane

Resolve addresses, company entities, ports, addresses, and commodity inputs with read-only network tools. Preserve opaque Flexport identifiers.

### Step 2: Search without commitment

Call `rates_search_instant_price` with approved inputs and store the search/result identifiers plus a redacted input digest.

### Step 3: Evaluate the candidate

Use `rates_evaluate_total_price_from_instant_price_search` for the selected result. Present currency, charge breakdown, timing, assumptions, and expiry exactly as returned.

### Step 4: Choose the branch

If instant booking is unavailable, use `rates_request_rate` and reconcile the quote request. Do not substitute `rates_book_without_rate` unless that supplier flow was explicitly approved.

### Step 5: Require human approval

Bind the approver, exact evaluated result, cargo digest, and approval expiry. Re-evaluate when any material input or provider term changes.

### Step 6: Book once and reconcile

Persist an operation key before `rates_instant_book`; store the returned booking reference and reconcile ambiguous outcomes before any retry.

## Authentication

REST calls authenticate with a cached OAuth 2.0 client-credentials Bearer token using audience `https://api.flexport.com`, or an explicitly accepted broad API key. Use distinct credentials per workload and never log credentials or tokens. MCP calls use the authenticated connection to `https://mcp.flexport.com/mcp` and remain subject to each tool's documented account permissions.

## Tool Discipline

Use Read and Grep for discovery and evidence. Use Write or Edit only for the approved artifact, code, configuration, test, or receipt described by this workflow; do not make an unapproved Flexport-side change.

## Output

- Scoped decision or implementation artifact
- Redacted operation and validation receipt
- Failure, rollback, and follow-up ownership record

Return a machine-reviewable receipt in this shape; adapt the operation values, but never place credentials or provider payloads in it:

```yaml
surface: rest-v3
operation: shipment-read
decision: approved
outcome: verified
evidence:
  release_sha: recorded-out-of-band
  provider_reference: redacted
rollback_owner: logistics-platform
```

## Examples

An operator searches an ocean lane, evaluates one returned rate, and receives a review card. Only after the logistics owner approves that exact result does the service make one booking call and record the returned reference.

## Error Handling

| Failure | Response |
| --- | --- |
| No instant rate | Create a quote request or stop; never fabricate a price. |
| Permission denied | Route to an authorized role instead of escalating credentials. |
| Terms changed after approval | Invalidate approval and present a fresh evaluation. |
| Booking outcome ambiguous | Reconcile by known references before considering another mutation. |

## Resources

- [First-party source notes](references/official-docs.md)
- [Flexport MCP tools](https://apidocs.flexport.com/v3/tag/MCP-Tools/)
- [Booking tutorial](https://developers.flexport.com/tutorials/booking/)
- [Flexport API reference](https://apidocs.flexport.com/v3/)
