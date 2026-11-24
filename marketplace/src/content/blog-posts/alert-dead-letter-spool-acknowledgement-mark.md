---
title: "Undelivered Alerts: Gate the Health Check Until Read"
description: "An acknowledgement mark holds the health check on undelivered alerts until a person reads them. Compared as strings, a mark of 9999 could clear them all."
date: "2026-11-23"
tags: ["devops", "automation", "testing", "debugging"]
featured: false
canonical: "https://startaitools.com/posts/alert-dead-letter-spool-acknowledgement-mark/"
---
If you run your own alerting and write undeliverable alerts to a local fallback file (a dead-letter spool), that file can fill up for weeks while every health check stays green. This post shows the check that fails while any alert in that file is unread, and the timestamp bug that almost made it acknowledge everything.

It happened to us. None of our health checks looked at the fallback file, so none of them noticed.

## What broke

We retired the chat relay that used to carry our alerts on 2026-11-12. From then on, alerts that could not be delivered landed in the fallback file. The shared alert script switched its default destination to Discord on 2026-11-20, but several jobs that send alerts had the old destination hardcoded, so theirs kept landing there.

On the production server, 35 high-severity alerts went undelivered between 2026-11-13 and 2026-11-20. The fallback file on the development machine held 1,918 events, about 1,470 of them repeats of the same incidents from a third-party status page.

Nothing measured that file. Our test alert (the canary) was already broken, the email fallback was disabled, and the dead-man check (a heartbeat that alarms when a job goes quiet) shared the same failure. The incident write-up put it in one line: a detector that pages into a dead channel is the same as no detector.

## The check

The liveness sweep (a scheduled job that checks other jobs are still alive) now counts spooled events newer than an acknowledgement mark, and fails while that count is above zero.

The mark is a file beside the spool, named `undelivered.ndjson.acknowledged-through`. It holds one ISO UTC timestamp in the form `YYYY-MM-DDTHH:MM:SSZ`. A failed sweep also fails an external health-check signal that does not depend on the failing channel.

We chose a mark over a time window on purpose. A window lets an unread backlog age out silently, and that is the failure this check exists to close.

The sweep's outcomes are deliberately narrow:

- A missing spool is quiet. It prints `0 -` and passes.
- A corrupt or unreadable spool is reported as unknown, never as healthy.
- Any nonzero count fails the row and tells the operator to read the spool, then write the timestamp of the newest event read into the mark file.

## The string comparison bug

The first version compared timestamps as plain text. That only works when both sides have the same shape. A mark of 9999 sorts above every real timestamp, so it would have acknowledged the whole backlog. The automated review flagged that on the pull request. The fix requires both the mark and each record timestamp to match `YYYY-MM-DDTHH:MM:SSZ`.

```python
TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
if ack and not TS.match(ack):
    print("ERR acknowledgement mark is not a YYYY-MM-DDTHH:MM:SSZ timestamp")
    raise SystemExit
...
if not isinstance(ts, str) or not TS.match(ts):
    bad += 1  # reported as ERR, never compared
    continue
if ack and ts <= ack:
    continue  # the mark names the newest event a person has read
```

The sweep fails the row on the printed `ERR` line, not on the exit code. The string comparison is safe only after the format check. Once both sides match the fixed shape, lexical order equals time order.

The alert writer appends while the sweep reads, so the last line can be half-written. A file that does not end in a newline has its final line ignored. A bad line anywhere else still fails the check.

## Rollout

Merging the change did not change the deployed copies. Each host needed a redeploy and its first acknowledgement mark.

On the dev box, the spool held 1,918 events, with the newest at 05:27:41Z. It was acknowledged after one summary was delivered to Discord. The check then reported nothing undelivered.

That last step is the weak point. The mark is a claim a person makes, and the check cannot tell whether the backlog was read or only skimmed. What the check does is make that claim explicit and dated, and it fails loudly when the claim is missing.

Tests cover a stale mark, three malformed marks, a record with `ts=unknown`, and a torn final line. Verified: blog-rows-test.sh 30 passed, vps-liveness-sweep-test.sh 41 passed.

## How the work went

Claude Fable 5.1 and Claude Fable 5.2 did the work across about seven Claude Code sessions. Most of the 30 errors were permission refusals and exit codes, not wrong hypotheses. The correction that mattered came from automated review, not from those sessions.

## Use this

- Count undelivered events in every alert spool and fail the check while any are newer than a dated acknowledgement mark a person writes after reading them.
- Validate the mark against one fixed timestamp format before comparing it, and test it with a value like 9999 so you know the check refuses it.
- Send the failure through a signal that does not share your alert transport, then redeploy each host and give it its first acknowledgement mark.

## Related Posts

- [GitHub Webhook IP Allowlist: Add the New Hook Ranges](https://startaitools.com/posts/github-webhook-ip-allowlist-new-hook-ranges/): Same incident: a static webhook IP allowlist silently 404ed deliveries from new GitHub hook ranges, and its drift alert never reached a person.
- [Reachability Is Not Freshness](https://startaitools.com/posts/reachability-is-not-freshness/): A status page returned HTTP 200 for two months while serving stale data; checks measured reachability, not freshness.
