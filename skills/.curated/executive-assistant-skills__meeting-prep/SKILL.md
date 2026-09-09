---
name: meeting-prep
description: "Prepare briefings for today's meetings \u2014 attendee research, email\
  \ history, past meeting notes, LinkedIn, and company context. Use when running the\
  \ daily meeting prep cron, or when user asks to prepare for meetings, review who\
  \ they're meeting with, or get context on upcoming calls."
version: 1.8.0
license: MIT
author: Martin Gontovnikas <martin@hypergrowthpartners.com>
tags:
- business
- meeting-prep
allowed-tools: Read, Bash(gog:*), Bash(mcporter:*), Bash(python3:*), Bash(openclaw:*),
  Bash(curl:*), Glob, Grep, Write, WebSearch
compatibility: Designed for Claude Code
---
# Daily Meeting Prep

## Config — read before starting

Read `../config/user.json` (resolves to `~/executive-assistant-skills/config/user.json`).
Extract and use throughout:

- `name`, `full_name` — user's name
- `primary_email`, `work_email` — Gmail accounts to check
- `whatsapp` — WhatsApp number for delivery
- `timezone` — IANA timezone (e.g. America/Argentina/Buenos_Aires)
- `slack_username` — Slack DM target
- `workspace` — absolute path to OpenClaw workspace (e.g. ~/.openclaw/workspace)

Do not proceed until you have these values.

## Debug Logging (MANDATORY)

Read `../config/DEBUG_LOGGING.md` for the full convention. Use `python3 {user.workspace}/scripts/skill_log.py meeting-prep <level> "<message>" ['<details>']` at every key step. Log BEFORE and AFTER every external call (gog, mcporter, Granola, web search). On any error, log the full command and stderr before continuing.

## Scope

- Timezone: {user.timezone}
- Calendars: primary of {user.primary_email} AND {user.work_email}
- Today's meetings only

**Timezone note:** Use explicit ART-bounded ISO8601 timestamps for calendar queries, NOT `--date`. Example: `gog calendar list primary --account <email> --from "2026-03-03T00:00:00-03:00" --to "2026-03-04T00:00:00-03:00" --json`. The `--date` flag uses UTC boundaries which misaligns with ART.

- **ALL meetings with attendees** — both external and internal
- Skip personal/solo events with no attendees (e.g. "Personal Trainer", "Golf", all-day reminders)

## Meeting types

### External meetings (attendees outside your email domains)

Full research brief (email context, Granola, LinkedIn, company research) — see below.

### Internal meetings (all attendees from your email domains: hypergrowthpartners.com, growth.li)

Lighter brief — no LinkedIn/company research needed, but still include:

- Attendee list
- Granola context from previous instances of this recurring meeting
- Recent email threads related to the meeting topic/agenda
- Any open action items from last time
- Format: same structure but skip LinkedIn/company sections

### Recurring collaborative meetings (e.g. podcasts, content sessions with external co-hosts)

These are external meetings — give them full briefs. Don't skip recurring meetings just because they're familiar.

## Error handling

- If `gog calendar` fails for one account: continue with the other account, note "⚠️ [account] calendar unavailable" in output.
- If Granola/Grain fails: continue without meeting history, note it per meeting.
- If WhatsApp delivery fails: attempt Slack delivery. If both fail, save to state file and report error.

## For each meeting

### 1. Event basics

Title, local time ({user.timezone}), attendees.

**RSVP status (MANDATORY):** For each attendee, check `responseStatus` from the calendar event:

- `accepted` → no flag needed
- `needsAction` → flag as "⚠️ hasn't responded"
- `declined` → flag as "❌ declined"
- `tentative` → flag as "❓ tentative"

If ANY non-organizer external attendee has NOT accepted (`needsAction`, `tentative`, or `declined`), add a visible line in the brief:
> ⚠️ *RSVP:* <name> hasn't accepted yet

This is informational — it doesn't mean they won't join, but it's useful to know ahead of time, especially for first calls or important meetings.

### 2. Email context (90-day lookback, with historical fallback)

Search Gmail both accounts for exchanges with attendees. For EACH attendee, search using these strategies in order:

1. **Email address** (primary — from calendar invite): `from:<email> OR to:<email>`
2. **Full name**: `"firstname lastname"`
3. **First name + "intro"**: `"intro firstname"` (catches informal intro subjects)
4. **First name + company**: `"firstname companyname"`

The attendee's email from the calendar invite is the most reliable identifier — always start there.

**Intro discovery** (after general email search):
5. Search for intro emails involving the attendee: `subject:intro <email>`, `subject:intro <firstname>`, `subject:introduction <email>`
6. Also check threads where a third party CC'd/introduced the attendee

**Recent email context** (after intro discovery):
7. Pull the most recent email threads with this attendee (by email address) to surface any recent updates, asks, or context leading into today's call

**Historical fallback** (if no results from 90-day search):
8. Run a broader search with NO date filter: `from:<email> OR to:<email>` — this catches long-standing relationships where the last email was months/years ago. If older threads exist, this is NOT a first call — note the relationship history.

- First call vs follow-up? Base this on ALL email history found (including historical), not just 90-day window
- **If first call: MUST include "who introduced + when" (date) if found in email; if not found, explicitly say "No intro trail found in email"**
- If follow-up: extract updates since last call
- **If email contains a concrete commercial trigger** (pricing, deliverables, scope, budget, urgency, timeline, decision-maker request), include it explicitly in the brief

### 3. Granola context

**Search by ATTENDEE, not by meeting title.** The same recurring meeting may have different titles week to week. Always search by the attendee's name or email to find all past meetings with them.

```bash
# Primary: search by attendee name
mcporter call granola.query_granola_meetings query="meetings with [attendee full name]"

# Fallback: search by company if attendee name yields no results
mcporter call granola.query_granola_meetings query="meetings with [company name]"
```

**Cross-check with `list_meetings`:** If the query results seem stale (oldest match is weeks old but you expect more recent), also run `list_meetings` for `last_week` or `this_week` and scan the participant lists for the attendee's email or name. This catches meetings where the title doesn't mention the attendee or company.

- **Recent (< 3 weeks):** Provide a richer summary (not one-liner): decisions made, key tensions, explicit action items, owners, and unresolved questions
- **Older (3+ weeks):** Broader context — relationship history, past decisions, recurring themes
- **No attendee match but company match exists:** Use company-level context and label it clearly as company-level
- **No results / first meeting:** Note that, provide email context instead
- Preserve citation links `[[N]](url)`
- Include a short explicit line: **"Why this meeting now"** based on prior action items or current email trigger
- **Exact name matching**: When attributing Granola results to an attendee, verify BOTH first AND last name match exactly. Different people can share a first name — never assume a match based on first name alone.
- **Auth failure:** If Granola returns an auth error, run `mcporter auth granola --reset` and retry once. If still failing, note "⚠️ Granola unavailable" and continue without it.
- **Empty summary:** If Granola returns a meeting record but with no/empty summary, note "Previous meeting found but no summary available" — don't silently skip it.

### 4. LinkedIn research

- Search: `"[attendee name] [company] LinkedIn"`
- Extract: current role, background, recent posts/activity

### 5. Company research

- Search: `"[company] recent news"`
- Search: `"[company] funding crunchbase"` (if startup/VC relevant)
- Extract: company stage, announcements, what they do

## Research rules

Read `{user.workspace}/style/MEETING_PREP_RULES.md` for additional research steps.

## Output format

Send via WhatsApp ({user.whatsapp}) AND Slack (DM to {user.slack_username}). **One message per meeting, chronological order, is mandatory.**

**Also send to Chief of Staff:** After sending all meeting briefs, upload the markdown brief file (`{user.workspace}/state/meeting-prep-YYYY-MM-DD.md`) to {user.chief_of_staff.name}'s Slack DM. Use the Slack API `files.upload` (or `files.uploadV2`):

```bash
curl -s -F file=@{user.workspace}/state/meeting-prep-YYYY-MM-DD.md \
  -F channels={user.chief_of_staff.slack_dm_channel} \
  -F title="Meeting Prep — <date>" \
  -F initial_comment="📋 *Meeting Prep — <day>*" \
  -H "Authorization: Bearer <bot_token>" \
  https://slack.com/api/files.upload
```

**Never collapse into a single summary block.** The user expects one standalone message per meeting. Send each meeting brief as a separate message to BOTH WhatsApp and Slack. If one channel fails, still deliver to the other.

Start with a short intro: "📋 *MEETING PREP — <day>* — <N> meetings (<X> external, <Y> internal)"

Then one message per meeting in this format — use bold subsections and blank lines between each section for readability:

```
*<number>. <Name/Company> — <local time>*

*Who:* <Role>, <Company> (<location>). <What the company does, 1 sentence>. <Funding/stage if relevant>.

*Context:* <First call vs follow-up>. <If first call: who intro'd + when (date); if unavailable: "No intro trail found in email">.

*Email history:* <Key email context — include important commercial/decision triggers when present (pricing, scope, deliverables, urgency, budget, decision-maker request)>.

*Granola:* <Richer recap: key decisions, action items, owners, unresolved questions, and why a follow-up was needed. If no attendee notes, use company-level notes and label it. Or "No previous meetings found in Granola">.

*Why this meeting now:* <One sentence grounded in prior action items and/or current email trigger>.

*Focus areas:* <ONLY items derived from prior action items and current email trigger — not generic strategy prompts>.

*Links:* <LinkedIn, company site, Crunchbase>
```

Each section on its own paragraph (blank line before each bold label). Keep it concise but well-structured — readability over density.

If a meeting already happened, prefix with ✅ and keep brief.
If there's a schedule conflict, flag with ⚠️.

## Save full brief

Save the full detailed brief to `{user.workspace}/state/meeting-prep-YYYY-MM-DD.md` and also send it as a file attachment via WhatsApp.

## ⚠️ CRON CREATION (CRITICAL — DO NOT SKIP)

This section is NON-OPTIONAL. Cron creation MUST happen for every run with meetings. If you run out of context or time before completing this section, the entire run is a FAILURE.

**Execution order:** Create ALL crons IMMEDIATELY after saving the brief file — BEFORE the assertions step. Do not defer cron creation to "after everything else."

Log: `python3 {user.workspace}/scripts/skill_log.py meeting-prep INFO "Starting cron creation for N meetings"`

## Pre-meeting reminders

After generating all briefs, create a one-shot cron job for EACH meeting that fires 5 minutes before start time. The cron job should:

1. Read `{user.workspace}/state/meeting-prep-YYYY-MM-DD.md`
2. Find the section for that specific meeting
3. Resend the FULL formatted brief for that meeting (same format as the original WhatsApp message — bold subsection labels, blank lines, links, etc.)
4. Prefix with "⏰ *5 min reminder*\n\n" then the full brief

**Hard formatting contract (no exceptions):**

- The reminder body must be copied verbatim from `{user.workspace}/state/meeting-prep-YYYY-MM-DD.md` for that meeting block.
- Do NOT rewrite, summarize, translate, normalize, or reformat any part of that block.
- Keep language exactly as generated in the source brief.
- Only allowed change is adding the `⏰ *5 min reminder*` prefix.

Use `openclaw cron add` with `--at` set to 5 min before meeting time, `--delete-after-run`, `--no-deliver`, `--channel whatsapp`, and `--to {user.whatsapp}`. The `--no-deliver` flag prevents the announce mechanism from sending a separate message — the task sends WhatsApp directly.

**Hard requirement:** after creating jobs, run `openclaw cron list` and verify the expected number of `pre-meeting-` jobs for today. If count is lower than expected, immediately retry creation and report failure explicitly.

Log each created cron: `python3 {user.workspace}/scripts/skill_log.py meeting-prep INFO "Created pre-meeting cron" '{"meeting": "<name>", "fires_at": "<time>"}'`

## Post-meeting action items + drafts

After generating all briefs, create a one-shot cron job for EACH meeting that fires 10 minutes after the meeting END time. The cron task should reference the action-items-todoist skill:

Task: "Read and follow ~/executive-assistant-skills/action-items-todoist/SKILL.md. Process ONLY the meeting titled '<meeting title>' that ended around <end time>. Send results to WhatsApp ({user.whatsapp})."

Use `openclaw cron add` with `--at` set to 10 min after meeting end time, `--delete-after-run`, `--session isolated`, `--timeout-seconds 1200`, `--no-deliver`, `--channel whatsapp`, and `--to {user.whatsapp}`. Name them `post-meeting-<short-name>`.

**Hard requirement:** after creating jobs, run `openclaw cron list` and verify the expected number of `post-meeting-` jobs for today. If count is lower than expected, immediately retry creation and report failure explicitly.

Log each created cron: `python3 {user.workspace}/scripts/skill_log.py meeting-prep INFO "Created post-meeting cron" '{"meeting": "<name>", "fires_at": "<time>"}'`

Log final count: `python3 {user.workspace}/scripts/skill_log.py meeting-prep INFO "Cron creation complete" '{"pre_meeting": N, "post_meeting": M, "expected": E}'`

**If cron count doesn't match expected:** Log ERROR and send WhatsApp alert: "⚠️ Meeting prep: only created X/Y pre-meeting and A/B post-meeting crons. Some reminders/action-items may be missing."

### Deduplication (MANDATORY)

After processing, the cron MUST append the meeting title to `{user.workspace}/state/processed-meetings-YYYY-MM-DD.json` (array of meeting titles already processed). This lets the end-of-day catch-all skip them.

**Before creating ANY Todoist task**, the cron MUST:

1. Read `{user.workspace}/state/processed-meetings-YYYY-MM-DD.json` — if this meeting is already listed, SKIP entirely (another cron already handled it)
2. Fetch all open Todoist tasks and check for duplicates by matching task content against the new task intent (same person + same action = duplicate)
3. If a matching task already exists, do NOT create a duplicate — skip it silently

This prevents the scenario where a post-meeting cron and the daily end-of-day cron both process the same meeting and create duplicate tasks.

## Sanity checks

- **Calendar is source of truth for meeting count**: Cross-reference email threads with the actual calendar events. If an invite was moved/rescheduled, it's still ONE meeting — don't count it as multiple. Check the calendar event ID, not email threads, to determine unique meetings.
- **First call vs follow-up**: Verify by checking if there is an ACTUAL past Granola meeting with this specific person (exact name match). Rescheduled invites or multiple scheduling emails do NOT make it a follow-up. Only a previously held meeting does.
- **Message count check (MANDATORY):** Number of sent meeting-brief messages must equal number of meetings with attendees (external + internal). If not equal, send missing meeting messages immediately.
- **Cron count check (MANDATORY):** Number of `pre-meeting-` jobs and `post-meeting-` jobs created for today must each equal number of meetings with attendees (external + internal).

### Automated assertions (MANDATORY)

After sending all meeting messages and creating all one-shot jobs, run:

```bash
python3 {user.workspace}/scripts/meeting_prep_assertions.py \
  --date YYYY-MM-DD \
  --brief-file {user.workspace}/state/meeting-prep-YYYY-MM-DD.md
```

- If exit code is 0: proceed normally.
- If exit code is non-zero: create missing cron jobs and/or send missing meeting messages, then re-run up to 2 times. If still failing after 2 retries, report the assertion output in your completion note and proceed.
- Include the assertion result summary in your final internal completion note.

## Meeting type-specific enrichment

### Deal flow calls (new companies, potential clients/advisory)

- Extract MORE detail from email threads: what the company does, product description, funding status, round size, investors, ARR if mentioned
- Search Crunchbase/web for latest funding info if not in emails
- Include company stage, team size, and key metrics when available

### Investor/VC calls

- Include link to the fund's profile page (website, Crunchbase, or AngelList)
- Note their investment thesis, typical check size, and stage focus if findable
- Helps identify fit before the call

## Scheduling difficulty flag

- If a meeting took a long time to schedule (intro was weeks/months before the actual meeting), flag it: "⏳ *Scheduling note:* Intro came in <date>, took <N weeks/months> to get on the books."
- If the meeting was rescheduled multiple times, note how many times
- This provides useful context on the relationship dynamic and signals the meeting may be higher-stakes

## Rules

- Executive style, concise
- No meetings with attendees today → NO_REPLY
- Missing data → state briefly ("No email history found"), don't invent
- Never silently omit a data source — if something returned nothing, say so
- **No cross-contamination**: Each meeting brief must only include information verified for THAT specific attendee. Do not mix up intro sources, email threads, or Granola notes between different meetings. Double-check that every fact in a brief belongs to the correct person.
- **No generic focus areas**: Focus must be anchored in (a) explicit prior action items from Granola and/or (b) explicit email trigger for this meeting. If neither exists, say so and use a discovery focus.

## Overview

Prepares executive briefings for each of today's meetings, including attendee research, email history, past meeting notes from Granola/Grain, LinkedIn profiles, company research, and RSVP status, delivered as individual meeting briefs via WhatsApp and Slack.

## Prerequisites

- `gog` CLI configured with both Gmail/Calendar accounts
- `mcporter` with Granola and Grain MCP connections authenticated
- Web search access for LinkedIn and company research
- `openclaw cron` CLI for pre-meeting reminder and post-meeting action item cron jobs
- Slack bot token for Chief of Staff file upload
- WhatsApp delivery endpoint configured in `user.json`
- `meeting_prep_assertions.py` script in workspace for post-run validation

## Instructions

See the Steps section above (For each meeting: Steps 1 through 5) and the Cron Creation section for the full workflow.

## Output

- One WhatsApp message per meeting with structured brief (Who, Context, Email history, Granola, Focus areas, Links)
- Full brief saved to `{user.workspace}/state/meeting-prep-YYYY-MM-DD.md`
- Slack DM with brief file to Chief of Staff
- Pre-meeting reminder crons (5 min before each meeting)
- Post-meeting action item crons (10 min after each meeting)

## Examples

```bash
# The skill queries both calendars, researches each attendee, and delivers briefs.
# Example WhatsApp brief:
# "1. Sarah Chen (Acme Corp) - 10:00 ART
#  Who: VP Engineering, Acme Corp (Series B, SF). AI infrastructure platform.
#  Context: Follow-up. Intro'd by David Park on Feb 15.
#  Granola: Discussed POC scope, agreed on 2-week trial. Action: send proposal.
#  Focus areas: Review POC progress, discuss pricing."
```

## Resources

- [Google Calendar API](https://developers.google.com/calendar/api)
- [Gmail API](https://developers.google.com/gmail/api)
- [Granola API](https://granola.ai/docs)
- Grain API
- [LinkedIn](https://www.linkedin.com)
- [Crunchbase](https://www.crunchbase.com)
