# Brain Save runtime contract

This reference records the mode-specific write contract implemented by the
`governed-second-brain` plugin. The skill body owns the workflow; this file owns exact tool
availability and response semantics.

## Contents

- [Tool matrix](#tool-matrix)
- [Capture inputs](#capture-inputs)
- [Authentication and authorization](#authentication-and-authorization)
- [Safe result interpretation](#safe-result-interpretation)

## Tool matrix

| Tool                 | Local mode                           | Team mode                                |
| -------------------- | ------------------------------------ | ---------------------------------------- |
| `brain_search`       | Governed search                      | Governed team search                     |
| `brain_capture`      | Append a proposal to the local spool | Submit or durably queue a team proposal  |
| `brain_govern`       | Drain and govern the local spool     | Not exposed; governance runs server-side |
| `brain_transition`   | Owner lifecycle transition           | Exposed to admins; members receive 403   |
| `brain_status`       | Lifecycle and category counts        | Connection and server health             |
| `brain_audit_verify` | Verify local chain and anchors       | Not exposed to the client                |

## Capture inputs

Both modes accept required `title` and `content`, plus optional `category` and `filePaths`. Categories
are `decision`, `pattern`, `convention`, `architecture`, `troubleshooting`, `onboarding`, or
`reference`.

Team mode additionally accepts optional `sessionId` and `learningIndex`. Session-end capture must pass
both, with `learningIndex` from 0 through 4, so each learning has a stable idempotency slot. Manual
one-off capture omits both.

`brain_transition` requires `memoryId`, `to`, and a non-empty `reason`; `actor` is optional.
Transitioning to `superseded` also requires the replacement UUID in `supersededBy`. Governed search
citations use `qmd://COLLECTION/MEMORY_UUID.md`, which supplies the transition ID without a separate
list operation.

## Authentication and authorization

Local mode is a single-owner trust domain and does not use an API credential. Team mode requires
`TEAMKB_API_URL`, a per-user `TEAMKB_API_TOKEN`, and `TEAMKB_TENANT_ID`, either in the environment or
the protected `~/.teamkb/team.json` configuration. Never echo tokens or capture credentials as memory.

Team members may search, check health, and propose captures. Team lifecycle transitions and inbox
review actions require an admin token. A 401 or 403 is a hard authorization result, not a transient
delivery failure.

## Safe result interpretation

- Local `brain_capture` means only that the proposal reached the spool. Promotion is known only after
  `brain_govern` returns its disposition.
- Team `intake: created` means the proposal reached the inbox; it does not mean promotion.
- Team `intake: already_exists` means an idempotent proposal already exists; do not create another.
- Team `queued: true` means the exact proposal was saved to the durable client outbox after a network
  or server failure. Report it as queued, not promoted. A later successful capture drains the outbox.
- A team 4xx response is surfaced without queuing because retrying invalid authentication, disclosure,
  or validation input would loop.
- `brain_audit_verify` proves whether the local hash chain and anchors are internally consistent. It
  does not prove the captured content is true.
