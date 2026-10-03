---
name: replay-privacy
description: |
  Session Replay masking and unmask rules (PI06). Spawn only when Replay is on.
  Owner is replay-privacy. Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, checklist]
---

# replay-privacy

**Canonical owner:** `sentry-pii-scrub-enforcer` → `replay-privacy`
**Spawn only if** `scrub-hook-coverage.py` reports `replay_on`, or the user pasted a Replay init. Do not run this on a Node-only SDK.

Quota may keep a labeled copy. That copy is not a second owner. See `OWNER.md`.

## Defaults

Sentry documents Replay as private by default: text and images redacted in the browser before send; playback is asterisks and gray boxes. A server-side scan of replay metadata (console, network URLs) for cards, SSNs, and tokens is not "we masked the DOM."

## Findings

- `maskAllText: false` is a finding. Recommend the default (masked).
- `sentry-unmask` is for static content. It is a finding on any node that can contain user-generated text (billing form, email, profile). Recommend removing the class from those nodes.
- Network detail / response body capture is a finding. Recommend leaving bodies off.
- Console logs inside the replay are the breadcrumb problem again. Do not log tokens.
- `beforeSend` / `beforeSendSpan` do not see the replay payload. Never say the error scrub covered unmask.

## Output

List each unmask or body-capture site. State `beforeSend_covers_replay: false`. Recommend the default mask. Do not toggle the project. `writes: none`.

## Fail

Spawning on a scrub review that has no Replay. Applying `maskAllText`. Claiming the issue is solved because server scrub is on.
