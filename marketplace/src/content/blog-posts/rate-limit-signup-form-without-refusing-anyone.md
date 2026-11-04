---
title: "Rate Limit a Django Signup Form Without Refusing Anyone"
description: "Rate-limit a Django signup form by deferring verification emails instead of refusing applicants. Submissions are stored; the mail waits for an open hour."
date: "2026-10-31"
tags: ["python", "architecture", "authentication", "web-development"]
featured: false
canonical: "https://startaitools.com/posts/rate-limit-signup-form-without-refusing-anyone/"
---
A rate limit on a public form answers a burst with an error, and the real person who arrived during the spike leaves with it. If you run a public signup or request-access form and need abuse controls without a CAPTCHA, this post shows a cap that refuses nobody: the submission is stored, the person gets the normal confirmation page, and only the verification email waits in the job queue until the first hour with room.

The form here is a request-access form: people apply to join a program, so each submission is an application. It also gets two bot checks, and neither one throws away a slow person's answers.

## Defer the send, not the applicant

Two global caps cover new applications: 30 per UTC clock hour and 100 per UTC day. These global caps are the part that refuses nobody. The form keeps its separate per-client and per-address limits, and those still answer an over-limit sender with a 429 page. Over a global cap, the application is still accepted and stored. Its verification email job is queued with a due time set to the start of the first window that still has room.

The job queue is an ordinary database table of pending jobs (`PendingAction` in this Django code), and each row already had a `due_at` column saying when it may run. The deferral reuses that column, which avoided a schema migration at a moment when other in-flight work also touched the same models. The background worker already picks up only jobs whose due time has passed, so nothing new has to run the delayed send.

Counting follows release time (when its verification send is allowed to run), not arrival time. Each new application counts in the window it is released into, recorded as `deferred_until` on its `submission_received` event. A backlog therefore drains at the capped rate and never faster. Revisions, repeats and reissues do not count and are never deferred.

The window search is a short loop:

```python
candidate = now
for _ in range(CAP_LOOKAHEAD):
    if by_day.get(_day(candidate), 0) >= daily:
        candidate = _day(candidate) + DAY
    elif by_hour.get(_hour(candidate), 0) >= hourly:
        candidate = _hour(candidate) + HOUR
    else:
        break
return None if candidate == now else candidate
```

It checks the day first, then the hour, and moves forward until it finds room. As a worked example of the arithmetic: at 30 an hour, three full hours hold 90 applications, so the day's last 10 places land in the fourth hour, and anything after that waits for the next UTC day.

The loop is bounded. `CAP_LOOKAHEAD` is 24 times 400 hours, and the code comment says that past it the cap settings are absurd, so the last candidate is used. If you copy the loop, keep a bound like this one rather than an open `while`.

## One lock for the count and the event insert

The intake transaction first inserts the application row. Then it takes `pg_advisory_xact_lock`, a transaction-scoped lock, counts the window, and inserts the `submission_received` event that the next count will read. The key is a fixed pair, so every transaction that creates a new application takes the same lock. Taking it after the application row, never before, leaves the existing handling of two simultaneous first posts for the same email exactly as it was. The lock is held until commit, so the next count sees this application's event. Two simultaneous new applications cannot both take the last place in a window.

Here is the caveat. The lock runs only on PostgreSQL. The code checks `connection.vendor == "postgresql"` and skips the lock on anything else. On another engine the count and the event insert are not serialized, and a test run there never exercises the lock.

## Bot checks that hand back the form

The honeypot is a hidden field named `website`, kept off screen and out of the accessibility tree. A person never fills it, so a value there marks a script. A filled honeypot gets the same accepted response as a real submission, the redirect to the received page, and nothing is recorded or sent. The bot sees success. The data is gone.

The render-time check protects slow people. The page carries `form_token`, the render time signed with the site secret under its own salt. A submission whose token is missing, forged, older than `CATALYST_INTAKE_FORM_MAX_AGE_SECONDS` (two hours), or younger than `CATALYST_INTAKE_FORM_MIN_AGE_SECONDS` (three seconds) gets the form back with its values, status 400, and nothing recorded.

The three-second floor exists because a script posts faster than a person reads the page.

Why hand back the form instead of showing a received page? A person whose page sat open past two hours would otherwise lose the submission without knowing it. Returning the form keeps their answers in front of them.

The token is stateless, and that is its weak spot. It proves a page was rendered recently. It does not prove first use, so a captured token can be replayed inside its window. The per-client and per-address limits, CSRF and the duplicate rules bound what a replay can do. A single-use nonce would close that gap, but it needs server state for every render, and this design avoids that trade.

## What broke on the first run

The first full run across twelve test modules ended with 3 failed and 332 passed. Two failures were new tests with wrong expectations. The third was a guard test that still expected a code path the change had removed. All three were fixed. A rerun of four modules covering the public intake (`test_public_intake`, `test_guards`, `test_acceptance`, `test_invitation`) passed 102 tests. A second commit in the same change (public host aliases) was verified over a different set of eleven modules: 261 passed.

These are test counts, not traffic. Nothing here measures how the caps behave under a real burst of public submissions.

## What it costs

The cost is delay. The verification mail, the applicant's email-confirmation step and everything after them wait behind the backlog. The applicant sees the received page now and the verification later.

The challenge's lifetime starts at release, not at submission, so a late verification still gets its full window. The deferral is only queue time for the send. Anything that assumes the verification mail arrives at submission time will be wrong during a backlog, and that is the first thing to check when you adopt this.

The change is in [PR #151](https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/151).

## Use this

- Put the cap on the send, not the submission. Store the row, return the normal confirmation, and set the verification job's due time to the first window with room.
- Take the count lock after the row insert and before the event insert, in the same transaction, and check that your production engine really runs it. The code skips it on anything but PostgreSQL.
- Sign the render time with its own salt. Then test that a missing, forged or too-fast token returns the form with status 400 and writes no row.

**Related posts**

- [Why SMTP 250 is not delivery, and what proves it](https://startaitools.com/posts/smtp-250-not-delivery-three-receipts/)
- [The first slice of the same v2 service, split into one PR per layer](https://startaitools.com/posts/first-slice-eight-pr-one-day/)
