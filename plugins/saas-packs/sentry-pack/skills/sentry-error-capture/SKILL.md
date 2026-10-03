---
name: sentry-error-capture
description: |
  DEPRECATED stub. sentry-error-capture moved or was cut in sentry-pack v2.
  Do not use this slug for new work. See the migration map in 000-docs/phase0-kill-list.md §3.
  Trigger retained only so saved workflows get a redirect, not a missing skill.
# version intentionally present so reconstruct-versions sees the stub;
# stub will be deleted in a later tag — not dual maintenance of v1 bodies.
allowed-tools: Read
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [sentry, deprecated, stub, v1-compat]
---

# sentry-error-capture (deprecated stub)

> [!WARNING]
> **Deprecated in sentry-pack@2.0.0.** `sentry-error-capture` is a **Cut stub redirect**.
> It is not a supported implementation. Bodies were not copied from v1.
> Stubs remain until a follow-up tag deletes them (Absorb / pressure-test change 5).


**Disposition: Cut.** Onboarding cookbook. Not rebuilt.

## Compatibility plan

- Deprecation banners ship on stubs in the `2.0.0` tag.
- Do **not** delete stub directories in the same release that removes v1 bodies.
- Delete stubs only in a later tag after operators have migrated bookmarks.
- Canonical map: `000-docs/phase0-kill-list.md` §3 and `000-docs/008-AT-ADEC-sentry-v2-cto-decision.md`.
- Absorb amendment: `000-docs/010-AT-ADEC-sentry-v2-modify-absorb.md`.

## What to do

Do not use this slug for new work. See the migration map in `000-docs/phase0-kill-list.md` §3.

## Overview

Deprecated v1 stub redirect. This slug is not a supported implementation in sentry-pack 2.0.0. The migration map names the disposition (Keep, Merge, or Cut) and the parent skill that owns the job, if any.

## Prerequisites

None. Do not install SDKs or mint tokens for this stub. Read the migration map before continuing saved workflows that still name this slug.

## Instructions

1. Stop. Do not follow any v1 tutorial that used to live in this directory.
2. Open `000-docs/phase0-kill-list.md` section 3 and find this slug.
3. Switch to the parent skill named there, or drop the workflow if the disposition is Cut.

## Output

A redirect only. No Sentry API call, no config diff, and no edited SDK file comes from this stub.

## Error Handling

If the migration map has no row for this slug, say so and stop. Do not invent a replacement. Do not recreate the deleted v1 body.

## Examples

A saved prompt that still says `/sentry-error-capture` should be rewritten to the parent skill in the migration map. Example: a cost question goes to `sentry-quota-leak-hunter`, not a deleted tuning tutorial.

## Resources

- `000-docs/phase0-kill-list.md` section 3 (migration map)
- `000-docs/008-AT-ADEC-sentry-v2-cto-decision.md` (locked cut)
- `000-docs/010-AT-ADEC-sentry-v2-modify-absorb.md` (stub-until-later-tag decision)
- Pack `README.md` migration table

