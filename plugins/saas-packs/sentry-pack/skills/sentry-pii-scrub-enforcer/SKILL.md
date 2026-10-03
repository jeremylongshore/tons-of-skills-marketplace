---
name: sentry-pii-scrub-enforcer
description: |
  Recommends (does not apply) Sentry PII controls: stop personal data landing
  (SDK hooks plus server scrub as a backstop), print a GDPR erasure plan and
  stop, and show which projects drifted from the written scrub standard.
  This skill never applies server scrub rules and never sends a delete.
  Use for Sentry PII, scrub rules, sendDefaultPii, Replay unmask, project
  scrub drift, or an explicit erasure request. Trigger with "sentry PII",
  "scrub PII", "sentry GDPR", "sendDefaultPii", "project scrub drift",
  "server scrub rules", "replay unmask".
allowed-tools: Read, Glob, Grep, Bash(sentry-cli:*), Bash(jq:*), Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, sentry, pii, gdpr, compliance]
---

# Sentry PII Scrub Enforcer

**Recommends. Does not apply.** The slug says "enforcer"; the contract is
advisory. A scrub review must not delete data, must not PUT project scrub
settings, and must not echo `SENTRY_AUTH_TOKEN`.

## Overview

Server-side scrubbing runs after the bytes have left the machine (PI01). The
boundary is the SDK. Server rules are the backstop and stay on. Relay is a
parent reference (PI07), not an agent.

| Agent | Checklist | When |
|---|---|---|
| `pii-scrubber` | `before-send-scrub`, `server-scrub-rules` | Scrub review. Still send the event. |
| `replay-privacy` | `replay-privacy` | Only when Replay is on (PI06). `beforeSend` does not see Replay. |
| `config-drift-auditor` | `sentry-config-audit` | Project batches vs the written standard (SC03). |
| `gdpr-deletion` | `gdpr-delete` | Only when the user explicitly asks to delete. Print, then stop. |

Sample-rate drift reads the labeled copy at
`agents/config-drift-auditor/references/sampler-rules/` (owner: quota
`volume-cutter`). This skill does not restate `tracesSampler` order.

## Prerequisites

- Sentry SaaS. Self-hosted: say the SaaS scrub/Relay story may not match and stop.
- Optional read token (`project:read`, `org:read`). Never print it. DSN is public;
  the auth token is not. Scope list: `references/token-hygiene.md`.
- No token: advisory mode on pasted project settings, event JSON, or `Sentry.init`
  snippets.
- A written standard JSON for drift (see `references/project-standard.example.json`).
  Do not invent the org's standard from one clean project.
- `python3`. Scripts call `scripts/lib/sentry_readonly.py`. No MCP. No write tool.

## Instructions

### Step 0 — Refuse writes and the wrong spawn

- Description contract: **Recommends (does not apply).**
- Do not spawn `gdpr-deletion` on a scrub review that did not ask for a delete.
- Do not spawn `sdk-migrator` or `volume-cutter`.
- Do not call PUT/POST/DELETE against Sentry. `print-gdpr-delete-request.py`
  prints a plan and `refuse_write`s. There is no auto-delete.
- Do not treat `beforeSend` as covering Replay unmask, span descriptions, logs,
  or metrics (PI02, PI06).
- A hook that returns `null` is an outage. Hand that to
  `sentry-event-forensics`. Stripping email while still returning the event
  stays here.
- "Does Sentry sign a DPA?" — point at Sentry's DPA. A DPA is not minimization.
  No legal advice. No agent.
- Do not turn this into a repo-wide secret scanner. Report Sentry payload risk
  at `Sentry.init` and route tables the user pointed at.

### Step 1 — Hook coverage (script)

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/scrub-hook-coverage.py" --root "$REPO"
```

The script lists which of `beforeSend`, `beforeSendTransaction`,
`beforeSendSpan`, `beforeSendLog`, `beforeSendMetric`, `beforeBreadcrumb`
appear near `Sentry.init`, plus `sendDefaultPii` and Replay flags. One init:
one `pii-scrubber` pass. Browser init and server init: two passes of the same
agent, not one agent per hook. Node-only: do not spawn `replay-privacy`.

### Step 2 — Scrub, still send

Read `agents/pii-scrubber.md` and both checklists. Recommend one scrub function
called from every `beforeSend*` hook that product surface is enabled. The
function returns the event. It removes `user.email`, card-looking extras,
query secrets, and SQL literals. It keeps `release`, a parameterized
transaction name, and a non-PII request id (PI08). Server scrub stays enabled;
it is not the boundary. Safe Fields do not scope breadcrumb category (PI05).

### Step 3 — Replay, only if on

If `scrub-hook-coverage.py` reports Replay (`replayIntegration`,
`sentryReplayIntegration`, or `maskAllText` / `sentry-unmask`), Read
`agents/replay-privacy.md` and its checklist. Default masking stays. Do not
claim the error `beforeSend` fixed the replay. Quota may read a labeled copy;
this agent remains the owner (`OWNER.md`).

### Step 4 — Drift, dirty projects only

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/settings-diff.py" \
  --projects "$SETTINGS_JSON" \
  --standard "${CLAUDE_SKILL_DIR}/references/project-standard.example.json"
```

Read `agents/config-drift-auditor.md` and `sentry-config-audit/CHECKLIST.md`.
Explain rows the script marks dirty. Do not list clean projects as failures.
Fan out by project batch, not one agent per toggle. Inbound-filter semantics
stay with triage `noise-classifier`; this audit only diffs the toggles against
the written standard.

For sample-rate keys, Read
`agents/config-drift-auditor/references/sampler-rules/COPIED-FROM.md`.
Compare the numeric fields the script lists. Do not rewrite parent-sampling
order (CQ03, CQ06, SC03).

Live settings, when a token exists, go through `SentryReadOnlyClient.fetch_project_settings`.
If the client is still a TODO, use the paste. Do not guess.

### Step 5 — Erasure, only on an explicit ask

If the user did not ask to delete, stop before this step.

Read `agents/gdpr-deletion.md` and `gdpr-delete/CHECKLIST.md`, then:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/print-gdpr-delete-request.py" \
  --org "$SENTRY_ORG" --user-id "$USER_ID"
```

The script prints a plan and refuses the write. Help Center (2026-08-03):
`DELETE /api/0/projects/{org}/{project}/users/{id}/` does not exist and does
not erase data. `GET /api/0/projects/{org}/{project}/users/` is read-only.
Deleting an issue deletes every event in it. Spans, logs, profiles, and
feedback are not individually deletable. The script does not delete the
project. No GDPR auto-delete.

### Step 6 — Relay (PI07)

When policy needs a scrub change without a redeploy, Read
`references/relay-boundary.md`. No Relay agent. No `sentry-relay-ops` skill.
SDK hooks stay even if Relay is recommended, so a DSN pointed straight at
Sentry is still scrubbed.

## Output

```
Skill: sentry-pii-scrub-enforcer
Contract: recommends, does not apply
Mode: live | advisory
Hooks: <present / missing per surface>
Scrub: <fields removed; event still returned>
Replay: <not on | findings; beforeSend does not cover unmask>
Drift: <dirty project slugs only, or none>
Sample order: not restated (quota sampler owner)
GDPR: not asked | printed request, write refused, no auto-delete
Token: not echoed
Writes: none
```

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| Hook returns null | Drops every event | Fail the recommendation. Hand to forensics. |
| Token in output | Leak | Redact. Never print `SENTRY_AUTH_TOKEN` or `sntrys_`. |
| Delete during scrub review | Over-help | Do not spawn `gdpr-deletion`. |
| Fake user DELETE | Erasure scripts | Say that path does not erase (Help Center 2026-08-03). |
| Over-broad denylist | `*user*` / `*session*` | Keep release, transaction, request id (PI08). |
| Self-hosted | Out of scope | Stop. |

## Examples

### Example 1: Email and a card-looking extra

Event has `user.email=a@b.co` and `extra.card=4111111111111111`. Recommend
deleting those keys inside `beforeSend` and **returning the event**. A hook
that returns null fails. Server denylist is additional, not a substitute.
No delete call.

### Example 2: Two inits

`web` has `sendDefaultPii: true`, `api` has `sendDefaultPii: false`.
`settings-diff.py` flags `web` only. Do not rewrite `api`.

## Resources

- `${CLAUDE_SKILL_DIR}/references/relay-boundary.md` — PI07, not an agent
- `${CLAUDE_SKILL_DIR}/references/sql-breadcrumbs.md` — PI05
- `${CLAUDE_SKILL_DIR}/references/token-hygiene.md`
- `${CLAUDE_SKILL_DIR}/references/project-standard.example.json`
- `${CLAUDE_SKILL_DIR}/references/pain-coverage.md` — PI01–PI08
- `${CLAUDE_SKILL_DIR}/docs/PRD.md`, `ADR.md`, `ONE-PAGER.md`
- Pack ADR `008` and absorb `010`
