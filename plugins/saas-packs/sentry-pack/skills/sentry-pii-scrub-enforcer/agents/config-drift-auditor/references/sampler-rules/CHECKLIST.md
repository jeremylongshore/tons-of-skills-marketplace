---

name: sampler-and-filters
description: |
  Labeled copy. Drift field names for sample rates. Not the sampling-order procedure.
  Not a marketplace skill.
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, nested, saas, copy]
---

> **LABELED REFERENCE COPY (mandatory).**
> Copy of quota `sampler-and-filters` for sample-rate **field names** only.
> Owner is `volume-cutter` / `sentry-quota-leak-hunter`.
> Source: `skills/sentry-quota-leak-hunter/agents/volume-cutter/skills/sampler-and-filters/CHECKLIST.md`
> PII `config-drift-auditor` reads this for SC03 sample-rate drift.
> It does **not** rewrite or restate parent-sampling order (CQ03, CQ06, SC03).
> Delete this copy when cross-skill calls work.
> See `COPIED-FROM.md` and `OWNER.md`. If the owner checklist is ahead of this copy, the owner wins. Do not invent order here to fill a stub.

# sampler-rules (copy — fields only)

**Owner:** `sentry-quota-leak-hunter` → `volume-cutter`
**This file is not the owner.** Do not maintain a second decision procedure.

## What drift may compare

`scripts/settings-diff.py` may flag these keys when the written standard contains them:

- `tracesSampleRate`
- `profilesSampleRate`
- `sampleRate` (error sample rate — quota's rule is not "set it to 0")
- `replaysSessionSampleRate`
- presence of `tracesSampler` (a boolean "present", not a ranking of branches)

## What this copy must not contain

The decision order (sampler defined, else parent decision, else `tracesSampleRate`), the rule against overriding `parentSampled === true`, health-check sampler snippets, inbound filters, per-key ceilings, and spike protection. Those stay on the owner checklist. Restating them here is the defect `010` A3 forbids.

Inbound filters are a different copy, owned by triage `noise-classifier`, not by this file.

## Output when a sample key is dirty

"Project `<slug>` `<key>` is `<found>` vs standard `<expected>`. Sampling order was not evaluated. Owner: quota `volume-cutter` `sampler-and-filters`."

`writes: none`.
