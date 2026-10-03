---
name: before-send-scrub
description: |
  SDK scrub hooks that strip PII and still return the event.
  beforeSend does not cover Replay. Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, checklist]
---

# before-send-scrub

**Owner:** `sentry-pii-scrub-enforcer` → `pii-scrubber`
**Script:** `scripts/scrub-hook-coverage.py`
**Contract:** recommend the hook. Do not apply a patch unless the user asked for a diff in their repo — and even then do not claim it was deployed. Do not call Sentry.

## Hook table (PI02)

| Hook | Sees | Does not see |
|---|---|---|
| `beforeSend` | errors and messages | spans, logs, metrics, Replay DOM |
| `beforeSendTransaction` | transactions (not every SDK; quotas guide) | Replay |
| `beforeSendSpan` | spans | Replay |
| `beforeSendLog` | logs | Replay |
| `beforeSendMetric` | metrics | Replay |
| `beforeBreadcrumb` | breadcrumbs, including URL and SQL | Replay network bodies |

One shared function, called from every hook whose surface is enabled. Tests should feed one fixture per type. Returning `null` drops the event (outage → forensics). Forgetting to return the event drops everything.

## Denylist that still sends

For an event fixture, remove and still return the event:

- `user.email`, `user.ip_address` when IP storage is not allowed
- extras that match a card (13–19 digits, Luhn not required for the recommendation — a 16-digit PAN-shaped string is enough to flag)
- `request` query keys `token`, `email`, `password`, and any `?email=`
- breadcrumb URLs: drop query and fragment in `beforeBreadcrumb`

Keep: `release`, a parameterized `transaction`, a non-PII request id (PI08). Do not `delete event.extra` wholesale. Do not denylist `*user*` or `*session*` on the server side as the primary fix.

## sendDefaultPii (PI03)

`sendDefaultPii: true` is a finding even if a password denylist exists. Leave it false. Set user to an internal id via `setUser` only after that id is allowed. Do not put email in tags (tags are searchable).

## URLs are not keys (PI04)

A path segment `/users/1234` has no key for the denylist. Parameterize transaction names. `dataCollection.urlQueryParams` and `dataCollection.httpHeaders` exist on current JS docs; the built-in denylist (`auth`, `token`, `password`, `secret`) does not cover `q`, `id`, or `user`. Recommend an explicit deny or `urlQueryParams: false` when that option exists on the SDK version in the repo. Do not invent the option for an SDK the docs you have do not list.

## Replay

If the coverage script sets `replay_on`, this checklist's last line is: spawn `replay-privacy`. `beforeSend` does not cover unmask.

## Fail

Returning null. Claiming the UI scrub makes SDK hooks unnecessary. Claiming `beforeSend` fixed Replay. Echoing a token. Writing project settings.
