---
name: sentry-pii-scrub-enforcer
description: |
  Audits Sentry PII exposure and recommends fixes without applying them: checks
  SDK hook coverage (beforeSend and related hooks) backed by server scrub, prints
  a GDPR erasure plan and stops, and reports which projects drifted from the
  written scrub standard. Never applies server scrub rules and never sends a
  delete. Use when reviewing Sentry PII handling, scrub rules, sendDefaultPii,
  Replay unmask, project scrub drift, or an explicit erasure request.
  Trigger with "sentry PII", "scrub PII", "sentry GDPR", "sendDefaultPii",
  "project scrub drift", "server scrub rules", "replay unmask".
allowed-tools: Read, Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/*")
argument-hint: "[paste: Sentry.init snippet | project settings JSON | event JSON | --org ORG_SLUG --user-id USER_ID]"
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags: [saas, sentry, pii, gdpr, compliance]
---

# Sentry PII Scrub Enforcer

**Recommends. Does not apply.** This skill audits Sentry PII exposure and
scrub coverage; it never deletes data, never writes project scrub settings,
and never echoes `SENTRY_AUTH_TOKEN`.

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

## Authentication

This skill is advisory by default and works entirely on pasted input —
project settings JSON, event JSON, or `Sentry.init` snippets — with no token
required.

If a human later runs the read-only helper scripts against live settings, set
`SENTRY_AUTH_TOKEN` in the environment. Minimum scopes: `project:read`,
`org:read`. Never print or paste the token value; scope detail lives in
`references/token-hygiene.md`.

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
Live read-only API fetch is a planned follow-up; this skill works on pasted
settings JSON today. Do not guess.

### Step 5 — Erasure, only on an explicit ask

If the user did not ask to delete, stop before this step.

Read `agents/gdpr-deletion.md` and `gdpr-delete/CHECKLIST.md`, then:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/print-gdpr-delete-request.py" \
  --org "$SENTRY_ORG" --user-id "$USER_ID"
```

The script prints a plan and refuses the write. Per Sentry's own documentation,
`DELETE /api/0/projects/ORG_SLUG/PROJECT_SLUG/users/USER_ID/` does not exist
and does not erase data. `GET /api/0/projects/ORG_SLUG/PROJECT_SLUG/users/` is
read-only. Deleting an issue deletes every event in it. Spans, logs, profiles,
and feedback are not individually deletable. The script does not delete the
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

Every run returns this fixed report shape:

1. **Contract** — states recommends-only, confirming no write occurred.
2. **Mode** — `live` when a read-only token is set, `advisory` on pasted input.
3. **Hooks** — presence or absence of each `beforeSend*` / `beforeBreadcrumb`
   hook, per init surface (browser, server).
4. **Scrub** — which fields the recommended function removes; confirms the
   event is still returned.
5. **Replay** — `not on`, or findings when Replay is enabled; notes that
   `beforeSend` does not cover Replay unmask.
6. **Drift** — dirty project slugs only, from `settings-diff.py`, or `none`.
7. **Sample order** — always `not restated`; ownership stays with the quota
   skill's sampler rules.
8. **GDPR** — `not asked`, or the printed erasure plan with the write refused.
9. **Token** — confirms `SENTRY_AUTH_TOKEN` was never echoed.
10. **Writes** — always `none`.

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| Hook returns null | Drops every event | Fail the recommendation. Hand to forensics. |
| Token in output | Leak | Redact. Never print `SENTRY_AUTH_TOKEN` or `sntrys_`. |
| Delete during scrub review | Over-help | Do not spawn `gdpr-deletion`. |
| Fake user DELETE | Erasure scripts | Say that path does not erase, per Sentry's own documentation. |
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
