# ADR: sentry-pii-scrub-enforcer

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-10-03
**Status:** Accepted for the local v2 draft (not pushed)

## Context

`008` names this parent for "stop PII landing, delete only when asked, show which
projects drifted." `009` flagged the slug: "enforcer" reads as a write, and
Decision 4 forbids writes. `010` A4 locks the description's first line:
**Recommends (does not apply).** `010` A2 adds `replay-privacy` and keeps Relay
as a parent reference. `010` A3 puts a labeled copy of quota's sampler under
`config-drift-auditor` so sample drift is visible without restating order.

Help Center (2026-08-03) removed the erasure shortcut most scripts still print.
`DELETE /api/0/projects/{org}/{project}/users/{id}/` is not an endpoint.

## Decision

1. The skill recommends SDK hooks, server rules, Replay masking, and drift fixes. It does not PUT them.
2. `gdpr-deletion` runs only on an explicit delete ask. The script prints the user id and a plan, then `refuse_write`. No auto-delete. No project delete.
3. The printed plan records that the project-users DELETE does not erase data, and that `GET /api/0/projects/{org}/{project}/users/` is read-only.
4. Issue `DELETE` URLs may be printed only for issue ids the operator supplied, with `sent: false`. Deleting an issue deletes every event in it. Spans, logs, profiles, and feedback are not individually deletable.
5. `beforeSend` returning null is an outage for forensics, not a scrub.
6. `config-drift-auditor` explains `settings-diff.py` rows. It Reads `references/sampler-rules/COPIED-FROM.md` and does not rewrite sampling order.
7. Inbound-filter semantics stay with triage `noise-classifier`. This parent may diff a toggle the standard lists; it does not own the matrix.
8. One shared read-only client. No MCP. No token in output.

## Alternatives

| Alternative | Why not |
|---|---|
| Apply server scrub when the user says "enforce" | `010` A4. The eval blocker is `recommends-not-applies`. |
| Auto-delete on any PII mention | A scrub review must not helpfully delete (`008` Decision 4). |
| Treat `DELETE .../users/{id}/` as erasure | False as of Help Center 2026-08-03. Shipping it would be a fake compliance action. |
| Restate `tracesSampler` order in the drift checklist | Two owners. Copy is read-only (`010` A3). |
| Replay agent on every review | PI06 spawns only when Replay is on. Node-only does not. |
| Relay subagent | PI07 is a reference. |

## Consequences

- Operators who wanted a one-click erasure get a plan and a refusal. That is the point of read-only v2.
- The quota sampler copy under this skill can lag the owner until batch A fills `sampler-and-filters`. This copy does not invent the order to fill the gap.
- "Enforcer" stays the slug so `007` / `008` / `009` do not fork a third name.

## Confirmation

`eval-spec.yaml` blockers include `recommends-not-applies`, `no-gdpr-auto-delete`, `beforesend-not-replay`, `no-spawn-gdpr-on-scrub-only`, and `no-sentry-writes`. Description line 1 matches A4.
