# PRD: sentry-pii-scrub-enforcer

**Author:** Jeremy Longshore (Intent Solutions)
**Date:** 2026-10-03
**Status:** Draft (`2.0.0-draft`) — local, not pushed

> Description contract (absorb `010` A4): **Recommends (does not apply).**
> No GDPR auto-delete. Filled from ADR `008`/`010`, kill-list §4, research `004`.

## Problem

Personal data leaves the process before a security review notices. Server-side
scrubbing is on by default and still runs after the bytes have left the machine.
One `beforeSend` does not see spans, logs, metrics, or Session Replay. `sendDefaultPii`
is a separate switch from the denylist. URLs and SQL breadcrumbs carry identifiers
that are not keys named `password`. Replay is private until someone unmasks it.
Projects do not inherit scrub or filter standards. And an erasure script that
`DELETE`s `/api/0/projects/{org}/{project}/users/{id}/` confirms nothing: that
endpoint does not exist (Help Center, 2026-08-03).

The slug says enforcer. v2 must not apply scrub rules or delete events.

## Target users

| User | Context | Primary need |
|---|---|---|
| Security reviewer | "Does Sentry scrub?" | A hook-coverage gap list and a scrub that still returns the event |
| Platform owner | Many projects, one intended standard | Dirty projects only, from a written standard |
| Operator with an erasure request | Explicit delete ask | A printed plan, the user id, and a refused write — not an auto-delete |

## Success criteria

Tied to `eval-spec.yaml` blockers.

1. Email and a card-looking extra are removed and the event is still sent; `beforeSend` returning null fails — `scrub-keeps-event`.
2. First-line contract and the answer recommend rather than apply — `recommends-not-applies`.
3. `beforeSend` is not treated as Replay coverage; `replay-privacy` spawns only when Replay is on — `beforesend-not-replay`.
4. Drift flags only the dirty project and does not restate sampler order — `drift-flags-dirty-only`, `drift-reads-quota-sampler`.
5. GDPR path prints the plan and the user id, states the fake user DELETE does not erase, and does not send — `gdpr-prints-and-stops`, `no-gdpr-auto-delete`.
6. Scrub-only reviews do not spawn `gdpr-deletion` — `no-spawn-gdpr-on-scrub-only`.
7. No Sentry write, no token echo — `no-sentry-writes`, `never-echo-token`.

## Functional requirements

- **FR-1:** `scripts/scrub-hook-coverage.py` lists hooks and Replay markers. It does not patch.
- **FR-2:** `pii-scrubber` Reads `before-send-scrub` and `server-scrub-rules`. Server scrub stays a backstop.
- **FR-3:** `replay-privacy` is the PI06 owner. Quota copies are labeled, not a second owner.
- **FR-4:** `scripts/settings-diff.py` diffs against a written standard. Sample-rate rows point at the quota sampler copy and set `sampling_order_restated: false`.
- **FR-5:** `scripts/print-gdpr-delete-request.py` prints `auto_delete: false`, redacts auth, and `refuse_write`s. It does not delete a project.
- **FR-6:** PI07 Relay is `references/relay-boundary.md`, not an agent.
- **FR-7:** Reads use `scripts/lib/sentry_readonly.py`. `--apply` exits refused.

## Out of scope

- Applying Advanced Data Scrubbing, turning on prevent-IP, or deleting issues.
- Legal advice. A DPA is not minimization.
- Repo-wide secret scanning beyond Sentry call sites the user pointed at.
- SSO/SCIM click-paths (cut with `sentry-enterprise-rbac`).
- Self-hosted Sentry and Relay SRE as a product.
- Restating `tracesSampler` / parent-sampling order (quota owns it).
