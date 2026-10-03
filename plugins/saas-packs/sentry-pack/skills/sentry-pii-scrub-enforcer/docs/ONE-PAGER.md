# Sentry PII Scrub Enforcer

**Recommends (does not apply) the scrub, Replay mask, and project-drift fixes that keep personal data out of Sentry — and prints an erasure plan without sending it.**

## Problem

Server scrubbing is a backstop that runs after data has left the machine. A single `beforeSend` misses spans, logs, metrics, and Replay. Projects drift from the standard because filters and scrub rules do not inherit. Erasure scripts still call a user DELETE Sentry does not implement.

## Solution

A router. `scrub-hook-coverage.py` lists hooks. `pii-scrubber` recommends a scrub that returns the event. `replay-privacy` runs only when Replay is on. `settings-diff.py` flags dirty projects. `print-gdpr-delete-request.py` prints the user id and refuses the write. Sampler order stays with quota.

## W5

| | |
|---|---|
| **Who** | Security reviewers, platform owners, operators with an explicit erasure ask |
| **What** | Hook gaps, a still-send scrub, dirty projects, a print-only erasure plan |
| **When** | A PII review, Replay unmask, project drift, or a GDPR delete request |
| **Where** | Claude Code, Sentry SaaS or pasted inits and settings |
| **Why** | The slug says enforcer; the client refuses writes, including auto-delete |

## Stack

| Layer | Choice |
|---|---|
| Skill runtime | Claude Code parent `SKILL.md` |
| Nested procedures | `CHECKLIST.md` under agents |
| Data plane | `scripts/lib/sentry_readonly.py` or pasted JSON / source |
| Arithmetic | `settings-diff.py`, `scrub-hook-coverage.py`, `print-gdpr-delete-request.py` |
| Knowledge | Relay reference, SQL breadcrumbs, token hygiene, labeled sampler copy |

## Differentiators

1. **Recommends, does not apply.** `--apply` is `refuse_write`.
2. **No GDPR auto-delete.** The fake project-users DELETE is labeled `erases_data: false`.
3. **`beforeSend` is not Replay.** Unmask is `replay-privacy`. Sampling order is not restated.
