---
name: brain-save
description: |
  Create and manage governed memories by capturing one fact, decision, pattern, or
  convention, or by retiring an outdated memory. This is side-effecting and never
  auto-fires. Use when preserving a durable fact without a full recompile or changing
  a memory's lifecycle. Trigger with "/brain-save".
allowed-tools: "mcp__governed-brain__brain_search, mcp__governed-brain__brain_capture, mcp__governed-brain__brain_govern, mcp__governed-brain__brain_transition, mcp__governed-brain__brain_status, mcp__governed-brain__brain_audit_verify"
version: 1.0.1
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: Apache-2.0
compatibility: "Designed for Claude Code; ships with the governed-second-brain plugin. Local mode governs in-process and requires qmd 2.x on PATH for search refresh. Team mode proxies to an authenticated team brain when TEAMKB_API_URL, TEAMKB_API_TOKEN, and TEAMKB_TENANT_ID are configured."
tags: [brain, governance, save, capture, local-first, team]
argument-hint: "[save <fact> | retire <memory-id>]"
disable-model-invocation: true
model: inherit
effort: medium
---

# Brain Save — write a fact into your brain (governed)

`/brain` reads; `/brain-save` writes governed memory. Use it to remember one durable fact without
recompiling a corpus or to retire a memory that is no longer true.

## Overview

The brain learns in two ways: a bulk **compile** ingests a whole corpus at once, and `/brain-save`
adds (or retires) a **single** item on demand. Either way, **governance stays in code**: this skill
_captures_ a candidate, then runs the deterministic **govern** step (dedupe → policy → promotion) that
decides what actually gets stored — and writes a SHA-256 hash-chained audit event for the decision. You
are proposing an item for the brain to keep; the deterministic curator owns whether and how it lands.

## Why this never auto-fires

`disable-model-invocation: true` means Claude will not trigger this from conversation — it runs only
when you explicitly type it. Writing to **your durable brain** is a deliberate act, not a chat side
effect. In **local mode** you own the brain outright — no server, token, or role; the only gate is
that you asked. In **team mode** the same deliberate-act rule holds, and the server _additionally_
enforces your role (a member proposes; an admin governs and retires).

## Prerequisites

- The `governed-second-brain` plugin is installed (it auto-wires the local `governed-brain` MCP server
  with the capture + govern tools).
- In **local mode**, `qmd` 2.x is on `PATH` so the govern step can refresh the search index after a
  promotion. If qmd is absent, capture + govern + the audit receipt still complete; only fresh-search
  visibility waits. Team clients do not require a local qmd installation.
- **Works in both modes.** In **local mode** (default, no `TEAMKB_API_URL`) all the tools below run
  in-process. In **team mode** (`TEAMKB_API_URL` set) the brain is governed centrally on the server:
  you **propose** with `brain_capture` and the server **disposes** (govern runs server-side, so there
  is no client `brain_govern`); `brain_transition` is exposed but **admin-only** (a member gets a clear
  403); `brain_status` is a connection-health probe; `brain_audit_verify` is not exposed to the team
  client.
- See [the runtime contract](references/runtime-contract.md) for exact tool availability,
  authentication, result semantics, and safe retry behavior.

## Instructions

### Save a new fact

**First, search the brain (search-before-save).** Call **`brain_search`** with
`{ query: "TITLE_AND_KEY_TERMS", scope: "all" }` and summarize what the brain already knows
from the `qmd://` hits. If the fact is **already covered, stop and say so** — don't duplicate it (the
inbox does _not_ dedupe at intake; only promotion dedupes, so this pre-save search is what keeps the
inbox from piling up). An empty `results` list (e.g. `qmd` isn't on `PATH`, or the brain is empty)
means _no known coverage_ — proceed to capture; it is **not** a block. Then capture only the
genuinely-new delta:

1. Confirm it's worth keeping — _"Would I benefit from finding this in 30 days?"_ Skip ephemeral
   debugging steps, throwaway preferences, secrets, or anything already in a CLAUDE.md/README.
2. Pick a category: `decision`, `pattern`, `convention`, `architecture`, `troubleshooting`,
   `onboarding`, or `reference`.
3. Call **`brain_capture`** with `{ title, content, category, filePaths? }`. In **team mode**,
   SessionEnd/autocapture must also pass `sessionId` + `learningIndex` (0..4) so each learning has its
   own idempotency slot; manual captures omit both. The team inbox deduplicates at intake, but the
   pre-save search still reduces noise.
4. In **local mode only**, call **`brain_govern`** to drain the spool through deterministic dedupe,
   policy, secret detection, and promotion. Report the returned promoted, quarantined, rejected,
   duplicate, flagged, and skipped counts.
5. In **team mode**, do **not** call `brain_govern`; it is intentionally absent. Report whether
   `brain_capture` created a proposal, found an existing proposal, or queued the proposal in the
   durable client outbox. Promotion is a separate server-side governance decision.

### Retire an outdated memory

1. Find the memory with `/brain`, then extract its UUID from the returned citation filename
   (`qmd://COLLECTION/UUID.md`). Do not invent or infer an ID when the citation is not UUID-shaped.
2. Call **`brain_transition`** with `{ memoryId, to, reason, actor, supersededBy? }`. Supply the
   replacement memory UUID as `supersededBy` when `to` is `superseded`. Valid moves:
   `active → {deprecated, superseded, archived}`, `deprecated → {active, archived}`,
   `superseded → archived`. Every transition writes a hash-chained audit event.

> **Team mode:** `brain_transition` is **admin-only** — a member token gets a clear 403 and nothing is
> applied. (In local mode you are always the owner, so it always works.)

### Check brain health

Call **`brain_status`** before or after a batch. Local mode returns counts by lifecycle and category;
team mode returns connection health (`mode`, API URL, token presence, health, and server version).

### Verify the receipts

In **local mode**, call **`brain_audit_verify`** to check the audit trail's SHA-256 hash chain and
external anchor log. It reports tamper signatures, documented migration exceptions, benign ordering
forks, and anchor breaks. Team clients do not expose this tool; request server-side audit evidence from
an authorized operator instead of claiming verification.

## Output

- After a local save: report what `brain_govern` returned and whether the search index refreshed.
- After a team save: report the capture result exactly — created, already present, durably queued, or
  failed. A team capture is a proposal, not proof of promotion.
- After a retire: report the new lifecycle state and confirm an audit event was written.
- After a status check: summarize local lifecycle/category counts or team connection health, matching
  the mode-specific response.

## Examples

**Save a decision:**

```
/brain-save I'm going Apache-2.0 across the stack so the public can self-host.

→ brain_capture({ title: "License: Apache-2.0 across the stack",
                  content: "...", category: "decision" })
→ brain_govern()
→ Promoted 1 (qmd://kb-decisions/9c2e42f1-7b60-4ed2-a9dd-648d6c786d43.md); 0 rejected, 0 duplicate.
  Audit event written.
```

**Retire a superseded memory:**

```
/brain-save retire memory 9c2e42f1-7b60-4ed2-a9dd-648d6c786d43 — superseded by the new deploy runbook.

→ brain_transition({ memoryId: "9c2e42f1-7b60-4ed2-a9dd-648d6c786d43",
                     to: "superseded",
                     supersededBy: "3b7cc2ec-7c61-433b-85b7-f20928350d55",
                     reason: "Superseded by the new deploy runbook", actor: "owner" })
→ Memory 9c2e42f1-7b60-4ed2-a9dd-648d6c786d43 → superseded; audit event written.
```

## Error Handling

| Situation                                  | Response                                                                                                                                                          |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Local `brain_govern` rejects the candidate | Policy declined it (e.g. duplicate, too short, possible secret). Report the reason — the governance pipeline is working as designed.                              |
| Local `qmd` is not on `PATH`               | Govern + audit still complete; the post-promote index refresh is skipped, so the new memory will not show in search until qmd is installed and govern runs again. |
| Team capture is queued                     | Report that the proposal is in the durable outbox, not promoted. A later successful capture drains queued proposals.                                              |
| Team API returns 401 or 403                | Check the per-user token and role. Do not retry an authorization failure as if it were transient.                                                                 |
| `brain_transition` rejects the move        | The lifecycle state machine forbids it; pick a valid target state.                                                                                                |
| Content may contain a secret               | Stop and strip it. Do not rely on the pipeline's secret-detection as the only check.                                                                              |

## Guardrails

- **Origin tokens prove WHERE a capture came from — not that it is true.** Captures carry an HMAC
  origin token bound to (candidate id, tenant, capture time) under the installation secret, and govern
  rejects a forged claim before promotion (`origin_token_invalid`, receipted). But an AUTHENTICATED
  insider — anyone holding a valid team token and/or the origin secret — can still save poisoned
  content with a perfectly valid origin. The mitigations for content poisoning are the deterministic
  govern policy, human review of the inbox/quarantine queues, and supersession — not the token.
- Never save content containing secrets, tokens, or credentials.
- `reason` on a retire must be a real, human-readable justification — it lands in the permanent audit
  trail.
- A govern rejection is the system working as designed, not a bug to work around.

## Resources

- [bobs-big-brain-plugin](https://github.com/jeremylongshore/bobs-big-brain-plugin) — this plugin and its runtime.
- The read counterpart: the `/brain` skill (cited queries).
