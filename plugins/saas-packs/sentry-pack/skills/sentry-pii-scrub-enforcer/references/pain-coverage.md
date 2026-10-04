# Pain coverage — PII

| ID | Owner | Not |
|---|---|---|
| PI01 server scrub is after transit | `pii-scrubber` / `server-scrub-rules` plus SDK hooks | "The UI is enough" |
| PI02 `beforeSend` misses spans, logs, metrics | `before-send-scrub` | One hook marked done |
| PI03 `sendDefaultPii` and IP storage | same scrubber; drift script | A separate agent |
| PI04 URLs and breadcrumbs | `before-send-scrub` section "URLs are not keys" | A repo-wide DLP scan |
| PI05 SQL / log breadcrumbs | `references/sql-breadcrumbs.md` | Safe Fields as a category scope |
| PI06 Replay unmask | `replay-privacy` when Replay is on | `beforeSend` |
| PI07 Relay | `references/relay-boundary.md` | An agent or a Relay skill |
| PI08 over-scrub | scrubber done-check keeps release, transaction, request id | Deleting `event.extra` wholesale |
| SC03 project drift | `config-drift-auditor` / `settings-diff.py` | Owning the inbound-filter matrix |
| SC03 sample rates | Read `references/sampler-rules/` copy | Restating `tracesSampler` order |

Parent reference, no agent: DPA pointer (not minimization, not legal advice); token hygiene.
