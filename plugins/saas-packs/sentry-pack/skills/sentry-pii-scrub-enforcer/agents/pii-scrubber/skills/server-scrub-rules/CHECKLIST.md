---
name: server-scrub-rules
description: |
  Server-side scrubbing as a backstop. Recommend rules; do not apply them.
  Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, checklist]
---

# server-scrub-rules

**Owner:** `sentry-pii-scrub-enforcer` → `pii-scrubber`

## Facts

- Server scrubbing runs after the event has left the SDK (PI01). It is on by default and should stay on.
- It scrubs a documented subset unless Advanced Data Scrubbing rules are added. It does not make SDK hooks optional.
- It applies to new events only. It does not scrub fields on events already stored. You cannot edit an event in place.
- Prevent IP storage is a separate server setting from `sendDefaultPii` and from the password denylist.
- Safe Fields do not apply to breadcrumb category. See `references/sql-breadcrumbs.md`.
- Advanced rules are key- and pattern-based. A pattern `*user*` or `*session*` will destroy diagnostic fields (PI08). Prefer exact field names from the fixture (`credit_card`, `email`, `password`, `token`).

## Recommend, do not apply

Print the rule the operator would add (field name, method mask or remove). Do not PUT `/api/0/projects/{org}/{project}/` scrub settings. `settings-diff.py --apply` is refused on purpose.

Label nothing here as Business/Enterprise unless you are pointing at a different lever (release filter, error-message filter, Delete & Discard). Those are not server scrub. Spike-protection plan placement stays blank.

## Fail

"I enabled Advanced Data Scrubbing." "Server scrub covers Replay." "Safe Fields will skip SQL breadcrumbs."
