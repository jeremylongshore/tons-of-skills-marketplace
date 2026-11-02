---
title: "Discord Webhook 204 No Content: Confirm with ?wait=true"
description: "Add ?wait=true to a Discord webhook POST to get the created message ID back. Mark an RSS item seen only when every copy is confirmed."
date: "2026-10-28"
tags: ["discord", "webhooks", "rss", "reliability", "python"]
featured: false
canonical: "https://startaitools.com/posts/discord-webhook-wait-true-confirm-delivery/"
---
A feed relay (a job that forwards new RSS items into chat) that marks an item as seen on any 2xx response can record a post as delivered that never reached the intended channel, and log no error. A plain Discord webhook POST (a request to a channel's webhook URL) returns HTTP 204 and an empty body. The relay learns the request was accepted, but not which message it created, so it has nothing to check.

The fix is a delivery loop that counts a post as delivered only when Discord returns the message ID for the expected webhook and channel. It retries only the copy that did not confirm, and it holds anything with an unknown outcome for a person to settle.

## What a 204 cannot prove

The fix starts with one query parameter. Add `?wait=true` to the POST, and Discord returns the created message, including its `id`, `channel_id` and `webhook_id`. A bare 2xx tells you the request was accepted. The returned receipt (the created message object, with its ID) tells you what was created.

Check those fields against what you expected. A simplified version of the check:

```python
ok = (
    status in (200, 201)
    and SNOWFLAKE.fullmatch(str(data.get("id", "")))
    and data.get("channel_id") == dest["channel_id"]
    and data.get("webhook_id") == hook_id
)
```

`SNOWFLAKE` is a regex for Discord's 64-bit IDs. The channel and webhook checks matter because an ID alone does not prove the message landed where your route says it should. A 204 from a webhook that now points at the wrong channel still looks like success, and the item is marked seen while the intended channel never gets it.

Before the first POST to each destination in a run, the relay does a read-only GET of the webhook metadata. It checks the ID, the webhook type and the channel. A misconfigured destination fails there, before any message goes out to that destination.

Mentions are disabled, and the at-sign is neutralized, so a feed title cannot ping the channel.

## Record the attempt before the request

Write the attempt to disk before the HTTP call. Discord can accept a request even when the relay never sees the response, and a timeout is exactly that case.

A simplified version of that ordering:

```python
part.update(state="in_flight", attempts=part.get("attempts", 0) + 1)
save(db, key, parts)  # durable before the request that may be accepted
resp = post(url, body)
```

After the response, each copy lands in one of three states:

- **confirmed**: a 200 or 201 with a matching receipt.
- **rejected**: a definitive client error (400, 401, 403, 404, 405, 413, 415 or 422). The request will not succeed as sent.
- **uncertain**: any other status except 429 (rate limits, below), a 2xx whose receipt does not match, a timeout, or a transport error. The relay cannot prove whether Discord posted.

## Retry only the missing copy

A route can name one to three destinations. Each copy has its own receipt key. An item enters the seen list only after every copy is confirmed. If one copy is held by a rate limit, the item stays unseen, and the next hourly run retries only that copy. A copy held as uncertain or rejected waits for the operator (below). A partial success does not justify resending the whole item.

A 429 is a definite refusal, so it is safe to retry. A wait of up to 60 seconds is waited out inside the run. A longer wait holds the copy until the next run.

## Hold uncertain outcomes for a person

Uncertain copies never resend automatically. A timeout does not tell you whether Discord posted, so an automatic retry risks a duplicate. I would not put a timeout behind an automatic retry, even if duplicates look rare in your traffic.

The operator checks the channel and settles the copy by hand. `confirm` records a message you found in Discord. For a definitive 4xx, fix the cause first, then `retry-rejected` releases that copy for another attempt.

When any item is held, the job exits 1. The job's liveness file stops advancing, and the sweep (a scheduled job that checks other jobs are still alive) reports the stall. The failure is loud.

## What broke on the way in

Before cutover, while the delivery change was being split out, five feeds turned up behind 301 and 308 redirects. The engine refuses redirects on purpose, as an SSRF guard (server-side request forgery protection). Each of those feeds had logged zero entries every hour and delivered nothing, a collection problem rather than a delivery one. The fix points the feeds at their final URLs. Following redirects at runtime was the alternative. Fixed URLs were chosen because the no-redirect rule protects the fetcher.

The first real install was refused at an ownership check, before any write. The directory belonged to a different user ID than the code assumed. The check now resolves the account by name, because a number breaks on a rebuilt host.

The first timer-triggered run after that delivered 42 confirmed messages. One funding headline showed a raw HTML entity for a curly quote. Some feeds double-encode entities. The parser removes one layer, and the relay had unescaped bodies but not titles. Titles now get the same `html.unescape` pass. Event identity is the source ID plus the entry ID, so the change could not resend anything already delivered.

## Also shipped

- Review bots found two bugs in the ownership fix before merge: a test that exercised the wrong tuple, and a group comparison that used the wrong group ID.

## Use this

- Add `?wait=true` to every webhook POST (Discord's [execute webhook reference](https://docs.discord.com/developers/resources/webhook) documents it), then check the returned `id`, `channel_id` and `webhook_id` before you count the copy as delivered.
- Write each attempt to disk as `in_flight` before the HTTP call. Never resend a copy whose outcome is unknown until someone has checked the channel.
- Give each destination copy its own receipt key, and mark an item seen only after every copy is confirmed. The next run then retries only the missing copy, and a partial success never resends the copies that already landed.

## Related Posts

- [SMTP 250 is not delivery](https://startaitools.com/posts/smtp-250-not-delivery-three-receipts/)
- [A database restore does not undo emails already sent](https://startaitools.com/posts/database-restore-does-not-undo-outward-effects/)
- [An SSRF egress proxy that denies your own production hosts](https://startaitools.com/posts/ssrf-egress-proxy-deny-your-own-production-hosts/)
