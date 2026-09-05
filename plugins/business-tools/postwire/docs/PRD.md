# PRD: postwire

**Author:** Renzo Madueño (PostWire)
**Date:** 2026-09-02
**Status:** Active

## Problem

Publishing one idea to several social networks is not one job, it is five, and the failure is
silent. Each network wants a different shape — YouTube needs a title, description and tags; TikTok
caps at 2,200 characters and rewards a hook in the first line; LinkedIn suppresses reach on posts
with a link in the body; X cuts at 280. An agent that sends identical text everywhere produces a
post that underperforms on four of the five, and nobody tells it.

The second half of the problem is worse: partial failure. Ask for four networks, get two. From
PostWire's own logs, one user made **30 publish attempts and got 3 successes** over six hours,
because the API accepted requests naming networks that account had never connected and published to
whichever ones happened to work. Of eight accounts that connected a network and never published,
**four had connected only YouTube and TikTok** — both refuse a post without a video, and nothing
said so until after the post was written.

Connecting the accounts is its own wall. TikTok's App Review asks for a demo video of the working
integration you cannot build until you are approved.

## Target users

| User                     | Context                                                         | Primary need                                              |
| ------------------------ | --------------------------------------------------------------- | --------------------------------------------------------- |
| Developer with an agent  | Wants the agent to publish, not to hand back a draft to paste    | One tool call that actually posts, and fails loudly        |
| Solo founder / creator   | Announcing releases across networks without writing five posts   | A native version per network from one idea                 |
| Small agency             | Several client brands, each with its own set of accounts         | Per-brand separation, flat pricing, no per-network fee     |
| Automation builder (n8n) | A workflow that should post a video from Drive or a blog RSS     | HTTP endpoints that validate before publishing             |

## Success criteria

1. **No partial publishes.** A request naming an unconnected network, a caption over that platform's
   limit, or a video network with no video is refused whole, before anything goes out.
2. **A different post per network.** `generate_posts` returns a distinct draft per platform —
   correct length, hashtag convention, and YouTube title plus tags — never the same string repeated.
3. **Every failure names its fix.** An error states the platform, the actual number where a limit
   applies, and the action to take. "youtube requires a video_url" is a fact; "youtube needs a video
   — upload one in the composer or pass video_url" is an instruction.
4. **A first post is reachable without a media file.** A user whose only connected networks require
   video is offered a network that accepts text, rather than a dead end.

## Functional requirements

- **FR-1:** `post_to_social` publishes to one or more networks in a single call, and validates
  connection, character limit and media requirements for every named platform **before** sending
  any of them.
- **FR-2:** `generate_posts` turns one prompt into a per-platform draft, applying that platform's
  limit, format and hashtag conventions.
- **FR-3:** `list_platforms` answers **without an API key**, so an agent can show what is supported
  before its user has signed up.
- **FR-4:** `my_account` reports plan, monthly usage and connected accounts, so an agent can explain
  a quota refusal instead of retrying into it.
- **FR-5:** Tool annotations mark `post_to_social` as non-read-only and destructive, so a client can
  require confirmation before a public write.

## Out of scope

- **Analytics and engagement metrics.** This publishes; it does not report on how a post performed.
- **Deleting or editing published posts.** Retraction support varies by platform and is deliberately
  not exposed as a tool — see `SECURITY.md`.
- **Replying, commenting or DMs.** Publishing only.
- **Hosting a media library.** Uploads are a short-lived staging step to give a network a URL it can
  read, not durable storage.
- **Guaranteed idempotency.** There is no idempotency key today; a repeated publish call posts
  again. Stated plainly in `SECURITY.md` rather than implied away.
