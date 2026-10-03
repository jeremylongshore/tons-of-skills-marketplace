# ADR: sentry-release-medic

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-10-03
**Status:** Accepted for the v2 draft (`2.0.0-draft`)

## Context

`008` Decision 5: when Help Center and the Sentry blog disagree about `action-release` inject, trust a `debugId` grep and cite both. Decision 1 puts CI upload and release health under this parent, not under triage. `010` requires the forensics `sourcemap-resolution` checklist to be copied here with `OWNER.md` / `COPIED-FROM.md` until a cross-skill call spike succeeds. RL08 (10k cap, duration stopped 2023-01-12) is an eval negative, not a footnote.

## Decision

1. Grep the artifact that will run. `.map` `debug_id` does not count.
2. One release string. Do not invent a second name. `--release` on upload does not create the release.
3. Order is build, inject, upload, deploy those bytes. `fetch-depth: 0` when commits matter.
4. Health is the session-stats script. No API read, no "fine."
5. JS only.
6. Read-only. Wrong-project uploads (SC05) are named here.
7. `resolved_with` is not re-derived in this skill's voice. The copy points at the owner.

## Alternatives

| Alternative | Why not |
|---|---|
| Pick the Help Center and delete the blog | A future action that really injects still passes the grep. A doc-only edit would not. `008` forbids picking a winner URL. |
| Put symbolication interpretation only here | Event JSON parsing is forensics. Two interpreters will drift. |
| Mark 90-day crash-free fine if the chart looks smooth | That is the false pass RL08 describes. |
| Upload from the skill | Read-only v2. A bad upload is worse than a recommendation. |

## Consequences

- CI authors get a recommendation they still have to run, with the exact release id and the grep command.
- The doc conflict stays visible in `references/action-release-conflict.md` so a later editor cannot tidy it away.
- Release health will often come back "not fine" on the first paste, because people paste the 90-day query. That is the skill working.
