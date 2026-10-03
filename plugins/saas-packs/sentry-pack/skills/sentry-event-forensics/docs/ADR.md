# ADR: sentry-event-forensics

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-10-03
**Status:** Accepted for the v2 draft (`2.0.0-draft`)

## Context

`008` keeps this parent separate from triage and from release-medic. Triage is an issue that exists. Forensics is a layered drop or a planned migration. Release-medic is the pipeline that uploads the bytes that were deployed. `010` keeps `sdk-migrator` and `debug-bundler` off the default fan-out and requires a labeled copy of `ci-sourcemap-upload` on `sourcemap-debugger`.

`resolved_with` is owned here. The grep for `debugId` is owned by release-medic. This skill does not pick a winner URL for `action-release`.

## Decision

1. One cause, one layer, from the drop checklist's order.
2. The parse script is the enum. Agents do not add matchers.
3. `has_debug_meta` does not imply a matching bundle. The script prints null on purpose.
4. No backfill claims.
5. Migration and support bundles are user-initiated phases.
6. `beforeSend` is not a Replay or span scrub.
7. Read-only. Redactor refuses upload.

## Alternatives

| Alternative | Why not |
|---|---|
| Fold this into `sentry-issue-triage` | `009`: those jobs fail differently. Merging them recreates a doc skill. |
| Promote `sdk-migrator` to a sixth parent | Rejected until drop-diagnosis evals are green and a new ADR says otherwise. |
| Restate CI inject steps as canonical here | Owner is `sourcemap-uploader`. The copy is labeled. |
| Teach ProGuard in `sourcemap-debugger` | `008` follow-up 3: JS only. An angle note would come first. |

## Consequences

- A forensics run can tell the user to Read a copy of the release checklist without release-medic being invoked as an agent.
- If the canonical CI checklist changes, this copy must be updated or deleted. `COPIED-FROM.md` says so.
- Native mobile stacks get an explicit "unspecified," which will feel thin. That is the decision.
