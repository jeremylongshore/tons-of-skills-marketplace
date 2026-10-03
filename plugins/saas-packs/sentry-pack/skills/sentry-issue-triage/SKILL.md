---
name: sentry-issue-triage
description: |
  On-call triage for a Sentry issue that already exists: severity from the
  payload, suspect release, grouping/fingerprint (prospective only), inbound
  noise, a performance-issue span when the issue type is performance, and the
  log line that carries the event id. Use for a Sentry incident, a page, a
  split or merged issue, inbound filters, or a postmortem skeleton. Not a
  generic SRE essay, not "events never arrived" (that is sentry-event-forensics),
  and not a volume cut. Trigger with "sentry incident", "triage this issue",
  "sentry severity", "which release caused this", "sentry fingerprint",
  "inbound filter", "correlate sentry event to logs", "N+1 sentry issue".
allowed-tools: Read, Glob, Grep, Bash(sentry-cli:*), Bash(jq:*), Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, sentry, triage, incident, sre]
---

# Sentry Issue Triage

This page: how bad, which release, which grouping lever, which span, which log
line. The parent is a router. Scripts extract numbers and fingerprints.
Subagents Read `CHECKLIST.md` files; those files are not marketplace skills.

## Overview

Keep seed was `sentry-incident-runbook` (severity and a postmortem). The job
that justified the parent is grouping and noise (OP02–OP08). Those procedures
are separate agents so the postmortem checklist is not also the filter matrix.

| Agent | Checklist | When |
|---|---|---|
| `issue-investigator` | `issue-triage-loop` | Always, for one issue page. Severity and postmortem only. |
| `fingerprint-auditor` | `fingerprint-rules` | Split/merge, message grouping, `{{ default }}`, AI grouping (OP02–OP04). |
| `noise-classifier` | `inbound-filter-matrix` | Noisy project, health-check names, Ignore vs Discard (OP05–OP07). **Owner** of the matrix. |
| `perf-span-auditor` | `span-fingerprint` | Only when the issue type is a performance issue (OP08). |
| `trace-bottleneck` | none here | Raw URL / transaction-name cardinality. Pointer only to quota. |
| `log-correlator` | `event-log-correlation` | Tie `event_id` to a log query. |

Minified frames (OP01) hand off to `sentry-event-forensics` /
`sourcemap-debugger`. This skill does not interpret `data.resolved_with`.

## Prerequisites

- Sentry SaaS. If the user says self-hosted, say the SaaS quota and inbound-filter
  model may not match and stop.
- Optional: `SENTRY_AUTH_TOKEN` with read scopes (`event:read`, `project:read`)
  and `sentry-cli`. Never print the token.
- No token: advisory mode on pasted issue or event JSON. Do not guess an org slug.
- `python3` for `scripts/`. The agent does not re-sum `accepted + filtered + dropped`.
  Filtered is not dropped. Ignore still bills.

## Instructions

### Step 0 — Refuse the wrong job

- Do not spawn `sdk-migrator`, `volume-cutter`, or `gdpr-deletion`. Upgrade, volume
  cut, and delete are other parents and only when the user asked for that job.
- Do not call a Sentry write API (resolve, ignore, merge, discard, rule create).
  Recommend the lever. The operator clicks it.
- Do not send the communication template in `references/communication-template.md`.
- Do not put a rate limit on the `environment` tag. There is no per-environment
  rate limit (Help Center, 2026-07-28). That refusal belongs with quota's
  `key-boundary-mapper`; if the user asks here, say so and stop that branch.
- Fingerprint rules and source maps do not rewrite events already stored.

### Step 1 — Parse the payload (script, not eyeballing)

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/issue-context.py" --pasted "$ISSUE_JSON"
python3 "${CLAUDE_SKILL_DIR}/scripts/fingerprint-from-event.py" --pasted "$EVENT_JSON"
```

Live read, only when a token exists, goes through `scripts/lib/sentry_readonly.py`
(`fetch_event_json`). The shared client refuses writes. If it raises
"TODO: live … not implemented", fall back to pasted JSON and say advisory.
Do not invent a second HTTP client.

`issue-context.py` is the severity rubric and the only timestamps the postmortem
may use (`firstSeen`, `lastSeen`). If release is null, the suspect release is
unknown. Do not invent one.

### Step 2 — Severity and postmortem

Read `agents/issue-investigator.md`, then
`agents/issue-investigator/skills/issue-triage-loop/CHECKLIST.md`.
Fill the skeleton from the script JSON. Five-whys stay blank unless the payload
or the repo states a cause. `issue-triage-loop` does **not** own inbound filters.

### Step 3 — Grouping (when the stream is lying)

Spawn `fingerprint-auditor` when the question is split issues, merged issues,
a changing message, or a fingerprint rule — or when
`fingerprint-from-event.py` reports `message_has_id_like_token: true` or
`has_stack: false`. Read `fingerprint-rules/CHECKLIST.md`.

First line of that branch: rules fix **new** events only (OP04). Merging is the
only lever on issues that already exist, and it is the least precise. Custom
fingerprints that omit `{{ default }}` opt out of AI grouping (OP03).

### Step 4 — Noise (when the project is noisy, not on every event)

Spawn `noise-classifier` for "this project is noisy", health-check names, or
Ignore vs Discard. Read `inbound-filter-matrix/CHECKLIST.md`. This file is the
canonical matrix. Quota's `volume-cutter` keeps a labeled copy
(`COPIED-FROM.md`); do not paste a second matrix into this parent's other
checklists.

One obvious `ignoreErrors` match on one event: answer from the checklist; do
not fan out. Do not spawn one agent per issue in a long list. Rank by `count`
from the script and run agents on the top few.

### Step 5 — Performance issue vs cardinality (different jobs)

- Issue type is a performance issue (N+1, span evidence): spawn
  `perf-span-auditor` and Read `span-fingerprint/CHECKLIST.md`. Thresholds are
  rote. Do not invent them. Stack-trace rules do not apply.
- Transaction name is a raw URL (cardinality / spend): spawn `trace-bottleneck`.
  It Reads the OWNER pointer at
  `agents/trace-bottleneck/skills/transaction-cardinality/OWNER.md`
  and, if needed, the single checklist under
  `sentry-quota-leak-hunter` / `cardinality-hunter`. It does not fork that
  file and it does not call quota's agent. Cardinality does not cover OP08.

### Step 6 — Log line

Spawn `log-correlator`. Read `event-log-correlation/CHECKLIST.md`. Run
`scripts/find-event-id-log.py` against the repo the user pointed at. Return a
query that includes the event id, or say the codebase never writes it. Do not
recommend installing Datadog.

### Step 7 — Minified frames

If frames are minified or the user asks why grouping split after a build, name
OP01 and hand off to `sentry-event-forensics` agent `sourcemap-debugger`.
Do not restate `resolved_with` matchers. See
`references/symbolication-handoff.md`.

## Output

```
Skill: sentry-issue-triage
Mode: live | advisory
Severity: SEV-1..SEV-4 (from issue-context.py only)
Suspect release: <payload release or unknown>
Next check: <one action>
Agents used: <names actually spawned>
Prospective: fingerprint/stack rules and maps do not restack stored events
Postmortem: timeline timestamps copied from the payload; no invented times
Log: <query containing event id> | codebase never writes event_id
Handoff: <forensics symbolication | quota cardinality path | none>
Writes: none
```

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| No token and no paste | Nothing to classify | Ask for issue or event JSON. Do not guess counts or a release. |
| Live fetch TODO | Shared client scaffold | Advisory mode on the paste. Do not hand-roll REST. |
| Fictional postmortem times | Hallucinated timeline | Only `firstSeen` / `lastSeen` / event `timestamp` from the script. |
| Second sampler pasted | Forked cardinality | Stop. Point at quota `transaction-cardinality`. |
| Filter matrix inside the postmortem | Merged jobs | Move filter work to `noise-classifier`. |
| `beforeSend: () => null` | Outage, not triage | Hand to `sentry-event-forensics`. |
| Self-hosted | Out of scope | Say the SaaS model may not match and stop. |

## Examples

### Example 1: Issue payload → severity and that release

Input issue: `level=error`, `userCount=120`, `count=4000`, `status=unresolved`,
`release=backend@1.4.2`, `firstSeen=2026-10-03T14:02:11Z`. Script returns SEV-1
and that release. Postmortem timeline cites `2026-10-03T14:02:11Z` only. No
second timestamp is invented. No discard is clicked.

### Example 2: Event id with no logger field

`find-event-id-log.py` scans the repo and finds no `event_id` / `event.event_id`
write. Output: "codebase never writes it" plus the event id that was searched.
No Datadog install step.

## Resources

- `${CLAUDE_SKILL_DIR}/references/severity-rubric.md`
- `${CLAUDE_SKILL_DIR}/references/pain-coverage.md` — OP01–OP08 owners
- `${CLAUDE_SKILL_DIR}/references/grouping-fields.md` — field names only
- `${CLAUDE_SKILL_DIR}/references/communication-template.md` — do not send
- `${CLAUDE_SKILL_DIR}/references/symbolication-handoff.md`
- `${CLAUDE_SKILL_DIR}/docs/PRD.md`, `ADR.md`, `ONE-PAGER.md`
- Pack: `000-docs/008-AT-ADEC-sentry-v2-cto-decision.md` and `010` (010 wins on checklists, copies, eval negatives)
- Shared client: `scripts/lib/sentry_readonly.py`
