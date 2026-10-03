---
name: sentry-config-audit
description: |
  Diff projects against a written scrub standard. Dirty projects only.
  Does not own the filter matrix or sampler order. Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, checklist]
---

# sentry-config-audit

**Owner:** `sentry-pii-scrub-enforcer` → `config-drift-auditor`

Filters, grouping rules, allowed domains, and scrub settings do not inherit. New projects get Sentry defaults, not the org's standard (SC03).

## Procedure

1. Require a written standard (`references/project-standard.example.json` is an example shape, not the customer's standard). If they did not provide one and did not accept the example keys, stop. Do not infer the standard from the cleanest project.
2. Run `scripts/settings-diff.py --projects <json> --standard <json>`.
3. Report `dirty_projects` only. `clean_projects` are context, not findings.
4. Explain each finding. Do not PUT the fix.
5. Inbound-filter **meaning** (what a health-check glob misses, Ignore vs Discard) is triage `noise-classifier`. If a standard lists those toggles and the script flags them, cite the owner checklist; do not rewrite it.
6. Sample-rate keys: Read `agents/config-drift-auditor/references/sampler-rules/COPIED-FROM.md`. The script sets `sampling_order_restated: false`. Do not add a paragraph that restates `tracesSampler` vs parent vs `tracesSampleRate` (CQ03, CQ06). Say "order is owned by quota `volume-cutter`" and stop.
7. Fan out by project batch only when explaining many dirty rows. Not one agent per key.
8. No token: pasted settings. Do not guess. Live fetch goes through `sentry_readonly.fetch_project_settings` and may still be unimplemented — then stay advisory.

## Fail

Flagging the clean project. Applying settings. Restating sampling order. Echoing the token. Spawning `gdpr-deletion`.
