# PostWire hosted MCP — security note

Written for the marketplace's hosted-MCP audit. It describes what the server does today, including
the parts that are not implemented; anything listed as missing is missing.

## What the plugin talks to

- **Hosted MCP:** `https://postwire.io/api/mcp` — Streamable HTTP, stateless (a fresh server and
  transport per request, so no session state is retained between calls).
- **Local alternative:** `npx -y postwire-mcp` over stdio, same five tools.

Both are thin adapters. Every tool proxies to PostWire's REST API with the caller's key, so
authentication, plan limits, rate limiting and validation are enforced in one place rather than
duplicated in the MCP layer.

## Authentication: storage and transport

- **Transport is HTTPS.** Plain HTTP is answered with a 308 redirect to the HTTPS URL; the API is
  not served over an unencrypted connection.
- **The key is supplied by the caller per request**, as `Authorization: Bearer pw_live_...`. The
  server holds no credential of its own for the caller, and stores nothing between requests.
- **Keys are stored hashed.** The database keeps a SHA-256 hash (`key_hash`) plus a short
  non-secret prefix for display. The raw key is shown once at creation and cannot be recovered — a
  database read does not yield a usable credential.
- **Keys can be revoked** (`revoked` flag, checked on every lookup) and may carry an expiry.
- **Scoped keys:** a key created before the account's email is verified has `scope: "preview"` and
  cannot publish; it is promoted to `full` only when the address is confirmed.
- The endpoint also accepts the key as a `?api_key=` query parameter, because several MCP clients
  cannot set headers. **This is less safe** — query strings appear in proxy and server logs — and
  the header form should be preferred wherever the client supports it.
- **The social network tokens never leave the server.** The caller's API key is not a social token;
  OAuth credentials are held server-side and are never returned by any tool.

## Tool annotations

Declared on every tool, in both the hosted and stdio servers, so a client can decide what needs
confirmation:

| Tool | readOnly | destructive | idempotent | openWorld |
|---|---|---|---|---|
| `generate_posts` | yes | no | no | yes |
| `post_to_social` | **no** | **yes** | **no** | yes |
| `get_post_status` | yes | no | yes | yes |
| `list_platforms` | yes | no | yes | yes |
| `my_account` | yes | no | yes | yes |

`post_to_social` is the only public write. It is marked destructive because once a network accepts a
post it is visible to a real audience, and PostWire cannot reliably retract it — deletion support
varies by platform and is not exposed as a tool.

## Server-side enforcement

None of this depends on the client behaving well; it is enforced in the API:

- **Ownership** — every call resolves to an account through the key; a caller can only touch its own
  connections and posts.
- **Plan limits** — the monthly post count is checked *before* publishing, and only successful posts
  are billed.
- **Rate limits** — per-account buckets (for example 60 posts/minute, 60 media uploads/hour).
- **Pre-flight validation** — before anything is sent: the account must have connected each
  requested network, the text must be within that platform's character limit, and video networks
  must have a video. A request naming a network the account has not connected is refused **whole**,
  rather than publishing to the others and leaving a partial result.
- **Media** — uploads are restricted by content type and size, and stored under a per-account path.

## Replay and duplicate posts

**There is no idempotency key today, and this is the weakest point of the design.** A repeated
`post_to_social` call with the same arguments will publish again. Two consequences worth stating
plainly:

- An agent that retries on a network timeout can double-post. The publish call is not safe to
  retry blindly.
- `idempotentHint: false` on `post_to_social` reflects this honestly rather than claiming a
  guarantee the server does not provide.

What exists instead is partial mitigation: a per-account rate limit, and a scheduler that treats a
partially successful run as done specifically so a retry cannot repost the items that already
worked. An explicit client-supplied idempotency key is the correct fix and is not implemented.

## Confirm before publishing

The skill instructs the agent to show the drafts and get explicit confirmation before calling
`post_to_social`. **That instruction is a prompt, not an enforcement mechanism** — a model can
ignore it.

What is enforced in code is narrower and should not be mistaken for the same thing: the destructive
annotation above (so clients that gate destructive tools will prompt), plan and rate limits, and
refusal of an entire request when any platform would fail. The server does not, and cannot, verify
that a human saw the draft.

Operators who need a hard gate should run the tool in a client that requires approval for
non-read-only tools.

## Reporting

Security reports: **privacy@postwire.io**, or the support form at https://postwire.io/support.html
(both are monitored by the maintainer).
