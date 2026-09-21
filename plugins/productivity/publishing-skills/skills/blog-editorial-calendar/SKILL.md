---
name: blog-editorial-calendar
description: 'Operate an evidence-backed editorial queue, balance topic and format coverage, schedule approved drafts, and reconcile backlog state with the publishing system. Use when choosing or scheduling the next blog work. Trigger with "show the editorial calendar" or "pick the next topic".'
argument-hint: "[status|next|add|mark-done|sync] [options]"
allowed-tools: Read, WebSearch, WebFetch, Write, Edit
version: 1.1.0
author: AutomateLab <hello@automatelab.tech>
license: MIT-0
tags: [seo, editorial-calendar, content-operations, scheduling, backlog]
model: inherit
effort: high
compatibility: Designed for Claude Code; scheduling, publication, CMS reconciliation, and backlog mutation require the content owner's approval and current platform access
---
# Editorial Calendar Operations

## Overview

Maintain a durable editorial backlog and select the next work from evidence rather than intuition. This skill balances configured topic clusters and post formats, reserves publishing slots, and reconciles local state with the real CMS before changing the queue.

It coordinates `blog-topic-research` and `seo-blog-writer`; it does not replace their research, drafting, review, or publishing controls.

## Prerequisites

- An approved `config.json` defining `target_platform`, author, UTC cadence, cluster targets, format targets, and CMS tag mappings
- A writable `backlog.json` with stable IDs, titles, clusters, formats, evidence URLs, priorities, statuses, and scheduled timestamps
- Read-only CMS listing access for `sync`; separate approved write access only when the user requests scheduling or publication
- `blog-topic-research` for backlog replenishment and `seo-blog-writer` for draft production
- Topic and format target weights that each total approximately `1.0`

## Tool Discipline

Use `Read` to inspect configuration and backlog state. Use `WebSearch` and `WebFetch` only to confirm public evidence or read the authorized CMS inventory. Use `Write` or `Edit` for reviewed, secretless state updates; never write credentials, raw access tokens, or unpublished sensitive content into receipts.

## Instructions

1. Parse the requested action: `status`, `next`, `add`, `mark-done`, or `sync`. Reject unknown actions and mutually incompatible scheduling flags.
2. Read and validate `config.json` and `backlog.json`. Confirm unique IDs, valid statuses, parseable UTC timestamps, nonnegative priorities, and target weights near `1.0`.
3. Run a read-only reconciliation before selection. Match CMS records by stable CMS ID first, canonical URL second, and normalized slug only as a last resort. Report ambiguous matches instead of guessing.
4. For `next`, score only eligible `ready` items. Rank cluster deficit first, then format deficit, evidence strength, explicit priority, and oldest creation time. Record the score factors so the choice is reproducible.
5. Reserve the selected item with a stable run ID. For `--draft`, invoke the writer without a publish time. Otherwise choose the next free configured UTC slot or validate each explicit slot.
6. Require review before any live publish or schedule mutation. Pass the topic scaffold and approved target to `seo-blog-writer`; do not copy CMS credentials into the handoff.
7. Commit the state transition only after the downstream operation returns a durable draft ID, CMS ID, or explicit failure. Move `ready -> reserved -> drafted -> scheduled -> published`; never skip directly to `published` without CMS evidence.
8. For `add`, normalize the title and compare it with existing titles, slugs, canonical URLs, and distinctive error/version tokens. Add only evidence-backed, nonduplicate topics.
9. For `mark-done`, require a matching live URL or an owner-approved manual receipt. For `sync`, preserve local notes while updating only fields supported by CMS evidence.
10. Return the chosen work, schedule, state changes, conflicts, and next eligible slot. Leave failed or ambiguous items recoverable.

## Selection Contract

Each backlog record should include:

```json
{
  "id": "topic-0042",
  "title": "How to diagnose webhook signature failures",
  "cluster": "integrations",
  "format": "how-to-fix",
  "status": "ready",
  "priority": 2,
  "evidence_urls": ["https://example.com/verified-source"],
  "scheduled_at": null,
  "cms_id": null,
  "canonical_url": null
}
```

Selection must be deterministic for the same configuration, backlog, and CMS snapshot. Never fabricate traffic, demand, availability, or publication evidence.

## Approval Boundaries

Ask for owner approval before scheduling, publishing, rescheduling, deleting, bulk-mutating, or overwriting reconciled backlog state. A read-only `status` or dry-run selection does not require CMS write access. Default to draft when publication intent is absent.

## Output

Return a compact operational receipt containing:

- action, run ID, timestamp, and configuration checksum
- selected IDs and score factors
- old and new statuses
- draft, schedule, CMS ID, and canonical URL when available
- conflicts, skipped duplicates, shortfalls, and required approvals
- next eligible slot and recommended follow-up

## Error Handling

| Condition | Response |
|---|---|
| Missing or invalid configuration | Stop before mutation and list the exact invalid keys or totals. |
| CMS inventory is unavailable | Mark reconciliation unverified; allow local dry-run status but do not claim a slot is free or a post is live. |
| Two records match one CMS post | Preserve both records, report the collision, and require an owner decision. |
| Downstream drafting fails | Release the reservation or mark it `blocked` with the failure receipt; do not consume the slot. |
| Queue has no eligible topics | Report the shortfall and invoke `blog-topic-research` only with the approved cluster and count. |
| Concurrent update changes the backlog | Re-read, recompute, and require confirmation if the selected item or slot changes. |

## Examples

Dry-run the next two selections without publishing:

```text
request: next 2 --draft --dry-run
result: topic-0042 (integrations deficit 0.08), topic-0017 (use-cases deficit 0.05)
mutation: none
next_slot_utc: 2026-09-12T06:00:00Z
```

Reconcile an already published item:

```text
request: sync
matched: topic-0042 -> cms_id=post_918 by canonical_url
transition: scheduled -> published
conflicts: 0
```

## Verification

- Re-run `status` and confirm the recorded counts equal the backlog totals.
- Confirm no two active records share a CMS ID or canonical URL.
- Confirm every scheduled timestamp fits a configured slot and no slot is double-booked.
- Confirm every `published` record has a CMS-derived ID or owner-approved receipt.
- Confirm a second dry-run against unchanged inputs returns the same ranking.

## Resources

- [Google Search Central: Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Ghost Admin API overview](https://docs.ghost.org/admin-api/)
- [WordPress REST API handbook](https://developer.wordpress.org/rest-api/)
- [RFC 3339 date and time profile](https://www.rfc-editor.org/rfc/rfc3339.html)

## Next Steps

Review target weights monthly against actual business priorities and search performance. Revalidate platform APIs before changing the reconciliation adapter.
