---
name: fingerprint-rules
description: |
  Fingerprint matchers, {{ default }}, AI-grouping opt-out, prospective only.
  Does not restack existing issues. Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, checklist]
---

# fingerprint-rules

**Owner:** `sentry-issue-triage` → `fingerprint-auditor`
**Script:** `scripts/fingerprint-from-event.py`

## First line

Rules fix **new** events only. They do not rewrite events already stored and they do not merge the issues already created (OP04). Source maps do not either; that handoff is separate.

## Procedure

1. Run the script. Quote `fingerprint`, `grouping_hint`, `has_stack`, `message_has_id_like_token`, `fully_custom_fingerprint`.
2. Grouping order to cite, not to invent: fingerprint, then stack trace, then exception type+value, then message. Exception grouping is weak when the text interpolates ids.
3. If `has_stack` is false and `message_has_id_like_token` is true (OP02): recommend an SDK fingerprint that is `{{ default }}` plus one stable tag, **or** a project fingerprint rule with matchers. Say which.
4. If `fully_custom_fingerprint` is true (OP03): say AI grouping is skipped for those events. Prefer keeping `{{ default }}` when the intent is to add a dimension, not replace identity. Unmerge is manual and per fingerprint; do not click it.
5. Custom rules beat built-in fingerprints on events that arrive after the rule. Confirm on a **new** event's grouping information. Do not tell the user the existing stream is clean.
6. Stack-trace rules (`max-frames`, in-app) are error issues only. Do not offer them for a performance issue (that is `span-fingerprint`).
7. Recommend the rule text. Do not PUT it. Multi-project: the rule does not inherit (SC03). Drift is `sentry-pii-scrub-enforcer` / `config-drift-auditor`, not a second copy of this checklist.
8. Algorithm version changes apply to new events only. Do not promise a grouping upgrade restacks history.

## AI merge vs custom fingerprint

- AI grouping embeds message plus in-app frames (or all frames if none are in-app) and only merges into an existing issue. It never splits a fingerprint group.
- `{{ default }}` in the fingerprint keeps AI on that portion.
- A fully custom fingerprint opts out.

## Output

First line is "prospective only". Then the script facts. Then one recommended rule or "no rule; message is already stable". `backfill: false`. `writes: none`.

## Fail

"This will regroup yesterday's issues." Omitting the opt-out when the fingerprint has no `{{ default }}`. Applying the rule via API.
