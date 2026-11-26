---
title: "Classify IMAP Errors Before a Retry Limit Blocks a Poller"
description: "Sort error codes into retryable and permanent before a retry limit counts them. A mail poller hit by a network outage stayed parked until a person could act."
date: "2026-11-25"
tags: ["python", "debugging", "architecture", "automation"]
featured: false
canonical: "https://startaitools.com/posts/retry-limit-should-ask-why-it-failed/"
---
A background poller with a failure limit can park itself during a short network outage, then stay parked after the network recovers. This post covers one mail collector that did exactly that, the change that classifies failures before counting them, and the one-time migration that rescues jobs already stuck. By the end you should be able to split transient failures from permanent ones in your own poller, and re-queue stuck jobs without losing their saved place.

## What broke

The collector reads applicant replies from an agreements mailbox. It keeps a cursor, which is its saved place in that mailbox. The place is recorded as an IMAP UID, the message number the mail server assigns.

On 2026-11-23 the collector failed five times in a row trying to reach the mail server. Its failure limit is five. The cursor moved to a blocked state with the reason `unreachable`, and no further pass was scheduled. The last good pass finished at 18:05 UTC that day. Nothing was read after it.

By the time an operator asked for a restart on 2026-11-25, the mail server answered on port 993 (the encrypted IMAP port) from the host again. The outage was over. The collector was still blocked, and applicant replies from the last day and a half sat uncollected.

A restart was not a shell command. It went through a staff screen behind two-factor login, and no host command existed for it. The model, Claude Fable 5.2, confirmed the port was answering and the cursor was blocked for `unreachable`. It declined to run the restart from a shell. A shell run would skip the two-factor control and write a permanent record under the owner's name. It gave the operator the staff-page steps instead.

## One counter, one branch

Before the change, every failure went through one check. Each failure added one to a consecutive-failure count, which is the number of failures in a row. If the failure code was on a blocking list, or the count reached the limit, the cursor blocked. Past the limit, the code no longer mattered.

The blocking list held `auth_failed`, `tls_refused`, `peer_refused`, `not_configured`, and two takeover codes. Those are failures a retry cannot fix. `unreachable` was not on the list, so it went through the counter like everything else. A single failed login blocks at once. Five unreachable attempts ended in the same blocked state.

That is the bug. A short outage and a wrong password got the same ending, and only one of them needed a person.

## Classify first, then count

After the change, the check reads like this. Here `failures` is the consecutive-failure count including this one, `n` is the current pass number and `code` is the classified error:

```python
at_limit = failures >= settings.CATALYST_MAIL_COLLECT_FAILURE_LIMIT
if code in BLOCKING or (at_limit and code != "unreachable"):
    ...  # block the cursor and open a staff item, as before
else:
    delay = settings.CATALYST_MAIL_POLL_SECONDS
    if at_limit:
        delay = max(delay, 300)
    enqueue_pass(cursor, n + 1, delay)
```

There are three outcomes now:

- Blocking codes still block at once, with no retry chain.
- Other codes block when they hit the limit, as before.
- `unreachable` never blocks. It keeps one successor queued, and once the limit is reached that successor waits at least five minutes.

The job keeps running, and the cursor keeps its consecutive-failure count until a collection succeeds, so the health check still counts it as failing.

The incident also closes itself. When a complete pass finishes on a cursor blocked for `unreachable`, the worker clears the blocked reason. It resolves the open `collector_blocked` staff item for that cursor (a review task asking a person to act), recording the code `mailbox_caught_up` under the actor `system:collect`. Other staff items, such as a failed-login item, are left alone. The restart path for authentication failures is unchanged, and the tests still cover it.

## Rescuing jobs that are already blocked

Changing the code does not unblock a cursor that is already blocked. Migration 0028 handles those.

It selects cursors that are blocked, have `unreachable` as both the blocked reason and the last error, still hold a saved UIDVALIDITY, and point at the configured mailbox and folder. UIDVALIDITY is the mailbox epoch, which says whether the saved UIDs still refer to the same messages. For each match, the migration creates a collect action at the next pass number. Each action carries an idempotency key tied to the cursor and pass number, and the cursor moves to a recovery state, so a rerun of the migration no longer selects it. It keeps the old blocked reason until a complete pass resolves the incident.

The migration keeps the saved UID, the UIDVALIDITY epoch and the completed watermark. Catch-up starts from the saved place, not from a fresh scan.

Cursors without a saved UIDVALIDITY, or on a different mailbox or folder, do not match the filter. They stay blocked for a person. That is the migration's real limit, and it is the first thing to check in your own data.

On each recovery pass until one completes, the worker logs the UIDVALIDITY, the starting and ending UID, the count of eligible UIDs, and a sha256 of the comma-joined UID set. Operations can compare that snapshot with what the inbound store already holds. The log contains no headers, addresses or bodies.

## What it cost, and what is still open

The cost was a day and a half of applicant replies, uncollected, plus a restart that needed a person with a second factor. The code fix merged about two hours after the diagnosis.

Two things remain open:

- The unreachable branch has no cap in the code quoted here. A mailbox that never returns keeps a retry queued every five minutes or longer. Nothing stops on its own, so the health report has to be watched.
- The source record does not show the migration running against the live collector.

The tests cover migration replay, refusal for an authentication block, saved-position catch-up, persistent transient outages, duplicate protection, and the existing restart path for failed authentication.

The change is in pull request 209 on the catalyst onboarding repository: https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/209

## Also shipped

- The same pull request bumped opentelemetry-api from 1.45.1 to 1.45.2 for CVE-2026-126360 and moved the production image to a digest-pinned Wolfi base.

## Use this

- Before any counter runs, sort failure codes into "a retry cannot fix" and "a retry might fix." Block at once on the first kind.
- Give the transient kind a delay floor once the limit is reached (this change uses five minutes), and surface the consecutive-failure count in health until a pass succeeds.
- Before you ship a migration like this, re-queue one real blocked job in a copy of your data at its saved position, and confirm it skips any cursor that has no saved epoch.

**Related posts**

- [A dead socket is not a dead host](https://startaitools.com/posts/a-dead-socket-is-not-a-dead-host/): When two facts share one signal, the signal cannot tell them apart.
- [Crash-durable reply paths](https://startaitools.com/posts/crash-durable-replies-loss-proof/): Making bot reply paths survive a crash.
