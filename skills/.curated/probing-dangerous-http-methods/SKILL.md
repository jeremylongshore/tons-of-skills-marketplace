---
name: probing-dangerous-http-methods
description: |
  Discover advertised HTTP methods with bounded OPTIONS requests, then
  verify separately selected methods only under explicit scoped ROE permission.
  Use when auditing post-deploy method policy or approved WebDAV/proxy experiments.
  Requires disposable fixtures, conditional cleanup and private evidence for
  writes; reports missing or ambiguous evidence as inconclusive.
  Trigger with "audit http methods", "trace check", or "webdav probe".
allowed-tools:
  - Read
  - Bash(python3:*)
argument-hint: "<url> [--active-method METHOD --roe FILE --ledger FILE]"
disallowed-tools:
  - Bash(rm:*)
  - Edit(/etc/*)
version: 3.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - http-methods
  - xst
  - webdav
  - pentest
---

# Probing Dangerous HTTP Methods

## Overview

Compare anonymous HTTP method capabilities with the owner's explicit policy.
The default sends only OPTIONS to the exact supplied URL, follows no redirect,
and does not read its response body. Allow is advertisement, not proof of a
write, an open proxy or exploitation. An API path name does not establish policy.

Active experiments require separate method selection, a structurally valid ROE,
an exclusive private ledger and bounded postcondition evidence. The checker does
not verify signing identity or establish legal authorization. Obtain the owner's
approval independently before executing an experiment.

## Prerequisites

- Use the plugin's Python environment and installed dependencies.
- Supply a literal HTTP(S) URL without credentials, query, fragment or ambiguous paths.
- For active probes, obtain an unexpired ROE using the authorization skill's
  required authorizer, time-window, signature and scope fields.
- Prepare an existing owner-private directory (0700) for a new ledger (0600).
  Never reuse or overwrite a prior ledger.

## Instructions

### Step 1 — Discover without mutation

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/probing-dangerous-http-methods/scripts/probe_methods.py \
  https://fixture.example.test/app --authorized --format json
```

The anonymous direct session ignores ambient credentials, cookies and proxies.
Missing, malformed, redirected, auth-gated or failed discovery returns exit 2.
A valid bounded advertisement is INFO; it does not certify application security.

### Step 2 — Review explicit active permission

Use Read to inspect the approved ROE and route policy before selecting methods.

Add this block to a complete owner-approved ROE; it is not a complete ROE itself:

```yaml
http_method_probe:
  target: https://fixture.example.test/app
  allowed_methods: [PUT, DELETE, COPY, MOVE]
  unexpected_methods: [PUT, COPY, MOVE]
  disposable_base: https://fixture.example.test/probe-fixtures/
  exclusive_disposable_namespace: true
  cleanup_authorized: true
```

The exact target and the entire dedicated same-origin disposable directory must
be in scope, with no overlapping exclusion. Every selected method needs explicit
permission. PUT/DELETE/COPY/MOVE require helper PUT and DELETE permission even
when only one is selected. MKCOL requires MKCOL, DELETE, PROPFIND and LOCK;
LOCK is an internal cleanup helper, not a selectable general-purpose probe.
Never approve an existing user-data directory as the disposable namespace.

TRACE and PROPFIND need no disposable directory. DEBUG additionally requires
`debug_response_sha256`, an owner-approved fixture digest. CONNECT requires an
explicit HTTP proxy root, a scoped HTTPS `proxy_destination`,
`controlled_proxy_destination: true` and `proxy_response_sha256`. It tests only
that controlled destination with TLS verification; never use metadata services,
internal discovery targets or arbitrary destinations as proof fixtures.

### Step 3 — Select each active method explicitly

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/probing-dangerous-http-methods/scripts/probe_methods.py \
  https://fixture.example.test/app --authorized --roe approved-roe.yaml \
  --active-method COPY --ledger private-evidence/new-copy-run.jsonl --format json
```

Repeat `--active-method` only for separately approved methods. All active probes
require `--authorized`, including local targets. `--is-api` is a legacy
discovery-only hint and cannot override the attested active policy.

### Step 4 — Preserve evidence and interpret the gate

| Gate | Meaning |
| --- | --- |
| 0 | Bounded selected experiments verified or explicitly rejected; no demonstrated owner-policy violation |
| 1 | A verified capability is listed in the owner's unexpected_methods policy |
| 2 | Missing, malformed, ambiguous or failed evidence; stop and reconcile |

The gate is computed before `--min-severity` filtering. HIGH means a verified
owner-policy violation, not automatic exploitation. 401/403/405/501 on supported
read-like experiments are recorded as rejection, not proof the method is absent
for every principal. Redirects and generic success pages are inconclusive.

## Method evidence

| Method | Positive evidence and limits |
| --- | --- |
| TRACE | Fresh synthetic nonce and matching TRACE request-line echo; no browser cookie-theft claim |
| DEBUG | Exact approved response digest, not HTTP 200 alone |
| PROPFIND | Depth 0, exact-resource DAV multistatus and successful requested property |
| PUT / DELETE | Unique absent generated file, conditional creation, exact payload/strong ETag readback, conditional deletion and verified absence |
| COPY / MOVE | Owned synthetic source, absent generated destination, Overwrite F, exact destination readback, MOVE source absence, complete conditional cleanup |
| MKCOL | Unique conditional creation; empty collection evidence; bounded exclusive depth-infinity write lock; empty reinspection; token/ETag-conditional delete and absence |
| CONNECT | Verified TLS response digest from the one approved HTTPS destination through the approved HTTP proxy |

## Output

Use `--format json`, `jsonl` or `markdown`, and optional `--output FILE`.
The report contains bounded summaries and hashes. The private append-only ledger
records request intent before transport, response hashes and ownership/cleanup
receipts. It contains fixture URLs and must remain private; it is not a signed
chain-of-custody or compliance certificate.

## Error Handling

Stop after the first ambiguous active experiment. No automatic mutation retry,
blind finally-cleanup or ledger-based write resume is performed. A lost response
can leave a created fixture or short lock pending. Preserve the ledger and ask
the owner to reconcile the generated resources; do not delete a changed resource.

Bounds are 64 requests, 64 KiB per response, 512-byte synthetic request payloads,
and a 180-second deadline checked between operations and during body streaming.
`--timeout` must be finite and at most 30 seconds. Requests socket-idle timeouts
are not a hard total wall-clock bound while waiting for headers. Collection
cleanup relies on RFC-compliant lock enforcement; unsupported locking or unknown
server behavior is inconclusive. Do not weaken conditions to obtain a pass.

## Examples

A post-deploy OPTIONS run may show PUT in Allow. Report the advertisement and
compare with the route owner's policy; do not issue PUT automatically.

A selected COPY run may create two synthetic file URLs, verify copied bytes,
then conditionally delete both. Report verified only after cleanup succeeds.
If either ETag changes, retain the private receipt and return inconclusive.

## Resources

- [Theory and primary standards](references/THEORY.md)
- [Policy remediation and reconciliation](references/PLAYBOOK.md)
- The plugin's `analyzing-tls-config/references/AUTHORIZATION.md` covers general active-scan authorization.
