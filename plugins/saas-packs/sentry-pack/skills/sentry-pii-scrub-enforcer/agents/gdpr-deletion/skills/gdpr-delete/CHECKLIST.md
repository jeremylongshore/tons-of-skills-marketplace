---
name: gdpr-delete
description: |
  Print an end-user erasure plan and stop. No auto-delete. No fake user DELETE.
  Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, checklist]
---

# gdpr-delete

**Owner:** `sentry-pii-scrub-enforcer` → `gdpr-deletion`
**Run only when** the user explicitly asked to delete or erase a person's data. A scrub review does not qualify.

## Script

```bash
python3 scripts/print-gdpr-delete-request.py --org "$ORG" --user-id "$USER_ID"
```

Add `--project` when they named one. Add `--issue-id` only for ids they supplied. Do not invent issue ids. Do not pass `--send`.

## What the output must say

- `auto_delete: false` and `applied: false`.
- The user id they named.
- `false_endpoint.erases_data: false` for `DELETE /api/0/projects/{org}/{project}/users/{id}/` (Help Center, 2026-08-03). `GET` on that collection is read-only and is not an erasure.
- Search hint `user.id` / `user.email` so a human can find issues. Deleting an issue deletes every event in it. You cannot delete one error event.
- Replays and attachments are per-object deletes the operator does in the product. Do not loop-delete them from here.
- Spans, logs, profiles, and feedback are not individually deletable. Do not recommend deleting the project unless they already said the whole project must go. The script sets `project_delete` to not printed.
- `refused_write` from `sentry_readonly.refuse_write`.
- Authorization header is `Bearer <REDACTED>`. The live token must not appear.

You are not Sentry's privacy team. Their form is for a data subject asking Sentry about Sentry's own processing, not for events a customer sent. Do not file that form on the customer's behalf from this skill.

Retention (30–90 days by plan and type) is not a substitute for an erasure they still have to perform. Do not invent a backup-expiry date.

## Fail

Sending the DELETE. Claiming the user endpoint erased data. Running this checklist without an explicit delete ask. Echoing `SENTRY_AUTH_TOKEN`.
