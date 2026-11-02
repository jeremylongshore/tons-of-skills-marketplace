---
title: "SSRF Egress Proxy: Deny Your Own Public Production Hosts"
description: "Deny your production hosts by name, resolved address and connected peer, so an SSRF egress proxy refuses them even though they have public addresses."
date: "2026-10-24"
tags: ["security", "python", "architecture", "testing", "ai-agents"]
featured: false
canonical: "https://startaitools.com/posts/ssrf-egress-proxy-deny-your-own-production-hosts/"
---
An SSRF filter (a guard against server-side request forgery, which stops a server fetching URLs an attacker chose) that admits only public addresses still lets your server-side fetcher reach your own production hosts, because those hosts have public addresses. This write-up ends with a deny check for an egress proxy that refuses those hosts by name, by every address they resolve to, and again by the address the socket actually connected to, without letting a DNS hiccup lock all egress shut.

The case is an onboarding app that fetches links applicants submit as evidence. All of that traffic leaves through an egress proxy (the one process allowed to open outbound connections). The proxy already refused private, loopback, link-local and cloud metadata addresses (the endpoint that hands out instance credentials). Anything with an ordinary public address (global unicast, in IP terms) went through.

That rule keeps a fetcher off your internal network. It says nothing about the hosts you run on the public internet. An applicant's link, or a redirect from a harmless-looking page, could aim the fetcher straight at them.

Real evidence fetching is still switched off in production. This check had to land before it could be switched on. How the fetcher role is split out of the web container is covered in [Docker Container Security Hardening: What Unit Tests Miss](https://startaitools.com/posts/docker-hardening-your-test-suite-cannot-see/).

The naive fixes are worse than the gap. Remember every address a production name ever resolved to, and the set grows until the guard refuses everything. Refuse whenever a lookup fails, and one flaky nameserver stops all fetching. The first version of this change did both, and a review agent caught it before merge.

## Can a public-address SSRF filter still reach your own production hosts?

Yes. An SSRF filter that admits only public addresses still lets your fetcher reach your own production hosts, because those hosts have public addresses. A public-address classifier cannot say "public, but ours", so the fix is a second list of host names. The proxy checks that list by name, by every resolved address and by the connected peer.

## Why the public-address rule cannot express "mine"

A global unicast classifier answers one question: is this address on the public internet? Your production hosts answer yes. The classifier has no way to say "public, but ours", so a second list is needed.

That list has to name your hosts specifically, and it has to hold up when DNS moves underneath it. The same mismatch, a check that validated a hostname while the fetch routed by address, came up earlier in the custom-feed field of an RSS bar plugin for Omarchy (an opinionated Arch Linux desktop setup by DHH). See [Every Verdict Carries the Scope It Actually Ran](https://startaitools.com/posts/a-green-result-only-covers-what-it-ran/).

## What the deny list file must contain

The deny list is a secret-free file of logical host names, pointed to by an environment variable. Format rules:

- ASCII only, at most 64 KiB and 256 names.
- One dotted DNS name per line, with `#` comments.
- Each entry denies itself and every name under it.
- An IP address, a single label, or a label written as a `0x` hex number (such as `0x7f`) makes the file malformed.

## What three checks does the egress proxy run on each request?

The proxy checks every request three times against that list:

1. **By name, before any lookup.** The requested host is compared with the deny names. A match is refused with `host_denied`.
2. **By resolved address.** Every address the target resolves to is compared with every address the deny names resolve to. A match is refused with `address_denied`. This catches a different name pointing at the same machine.
3. **By connected peer.** After the socket connects, the peer address is classified again and compared with a fresh resolution of the deny names. A match is refused with `peer_denied`. This catches a deny name whose DNS answer moves onto the target's address between the check and the connection. The target itself is not resolved again: the proxy connects to the addresses it already checked.

Here is the request path from `assessments/egress.py` (the name check happens inside `policy.target()`), cut off once the tunnel is accepted:

```python
def handle(client, policy: Policy) -> str:
    upstream = None
    try:
        host, port, addresses, extra = policy.target(read_head(client))
        if not addresses or not all(classify(ip, extra) for ip in addresses):
            raise Refusal(403, "address_not_allowed")
        denied = policy.denied_addresses()
        if any(canonical(ip) in denied for ip in addresses):
            raise Refusal(403, "address_denied")
        for address in addresses:  # every answer already passed classify; try each until one connects
            try:
                upstream = socket.create_connection((address, port), timeout=CONNECT_SECONDS)
                break
            except OSError:
                continue
        if upstream is None:
            raise Refusal(502, "connect_failed")
        peer = upstream.getpeername()[0]
        if not classify(peer, extra):
            raise Refusal(403, "peer_not_allowed")
        if canonical(peer) in policy.denied_addresses():  # resolved afresh: a DNS change since the check is caught here
            raise Refusal(403, "peer_denied")
        reply(client, 200, "ok", peer)
        # ... tunnel splice, except and finally omitted
```

Two details matter. The address and peer checks run after the public-address check, so they only ever narrow what was already allowed. And `denied_addresses()` runs twice per connection, one lookup pass of the deny names each time. Each pass runs in one thread and is bounded on its own by the existing 10-second deadline.

## One spelling per address

Address comparison by string fails quietly. `::ffff:203.0.113.10` (an IPv4-mapped IPv6 address, defined in [RFC 4291 section 2.5.5.2](https://www.rfc-editor.org/rfc/rfc4291#section-2.5.5.2)), `::ffff:cb00:710a` and `203.0.113.10` name one IPv4 host. A link-local IPv6 address can also carry a zone suffix such as `%eth0`. If the deny set holds one spelling and the target arrives in another, the set membership test misses.

```python
def canonical(ip: str) -> str:
    """One spelling per address: the zone dropped and an IPv4-mapped IPv6 address unwrapped, so `::ffff:a.b.c.d`, its
    hex form and `a.b.c.d` compare equal. Anything that is not an address is ""."""
    try:
        addr = ipaddress.ip_address(str(ip).split("%", 1)[0])
    except ValueError:
        return ""
    if addr.version == 6 and addr.ipv4_mapped is not None:
        addr = addr.ipv4_mapped
    return str(addr)
```

Both sides of every comparison go through this function. The tests cover a production address arriving as IPv4, IPv6, `::ffff:a.b.c.d` and `::ffff:hhhh:hhhh`.

## Why not list the production addresses instead?

A file of IP addresses looks simpler. It breaks the first time a host moves, and it silently stops protecting the new address. Logical names survive a move, and the file stays free of anything sensitive.

Resolving at check time handles DNS changes in both directions. A name that moves to a new address is caught by the fresh answer. An address the name pointed at recently stays denied from memory until newer addresses push it out of a capped history. A change between the check and the connect is caught at the peer.

The other obvious choice was to exit at startup when the file is broken. That was rejected too. Exiting leaves the fetcher with nothing to act on. A live proxy answering `503 deny_list_unavailable` tells the fetcher to retry the item instead of closing it, and the failing healthcheck marks the container unhealthy where an operator can see it.

## The first version could shut all egress

The implementation ran from a Claude Opus 5.5 session coordinating specialist agents. Its first version kept every address a denied name had ever resolved to. The commit message called it a never-shrinking union, chosen deliberately to cover DNS rebinding in both directions.

```python
def denied_addresses(self) -> frozenset:
        answers = resolve_names(self.deny)
        if any(addresses is None for addresses in answers.values()):
            raise Refusal(502, "deny_list_unresolved")
        fresh = {canonical(ip) for addresses in answers.values() for ip in addresses} - {""}
        with self.lock:
            if len(self.denied_seen | fresh) > DENY_SEEN_LIMIT:
                raise Refusal(502, "deny_list_unresolved")
            self.denied_seen |= fresh
            return frozenset(self.denied_seen)
```

Read it as an operator would. Two lines can stop all egress. The lookup-failure one recovers only once DNS answers again; the size limit never recovers without a restart.

A read-only security and privacy review agent, dispatched on the open pull request, returned these as its first three findings, each rated medium:

1. **The latch.** Once the remembered set would pass `DENY_SEEN_LIMIT` (4096), every request returns 502 until a restart. A deny name served from a rotating or geo-DNS pool keeps growing the set. The result stops all fetching, well beyond the one host it meant to block. The review also noted each CONNECT started one thread per name, twice, so an operator error in the list could cause thread storms.
2. **One flaky name blocks everything.** Any SERVFAIL, timeout or `EAI_AGAIN` on any deny name made every fetch return 502. A decommissioned name whose nameserver stopped answering, or a resolver outage, becomes a lasting denial of service. The review noted it could never become a silent allow, which is the correct direction; the price was all fetching.
3. **A non-resolving name denies nothing, silently.** NXDOMAIN and NODATA become an empty answer. A typo in the list, or a split-horizon name the egress container cannot resolve, gives zero protection and raises nothing.

Fail-closed and stay-available pull in opposite directions. The first draft chose closed at every fork, including the forks where closed meant closing everything. Each review finding got its own fix-up commit before merge, and each code finding its own test. The third is only partly closed, as the next section says.

## The bounded version: per-name memory with last-good answers

```python
def denied_addresses(self) -> frozenset:
        answers = resolve_names(self.deny)
        with self.lock:
            failed = [name for name, addresses in answers.items() if addresses is None]
            if any(name not in self.remembered for name in failed):
                raise Refusal(502, "deny_list_unresolved")
            for name, addresses in answers.items():
                if addresses is not None:
                    self.remember(name, addresses)
            if failed:
                logger.info("egress deny_lookup_stale")
            denied = frozenset(ip for kept in self.remembered.values() for ip in kept)
        if not denied:  # a list in which no name resolves denies nothing at all: refuse rather than pretend
            raise Refusal(503, "deny_list_resolves_nothing")
        return denied
```

What changed, finding by finding:

- **Memory is bounded per name, with no global limit.** `remember()` keeps a name's fresh answer in full, plus earlier addresses up to 64 in all (a fresh answer larger than 64 is kept whole). The oldest address missing from the fresh answer is evicted first. The file is capped at 256 names on load. No global limit remains that could latch the proxy shut.
- **A failed lookup keeps that name's last good answer.** The fallback is logged as one outcome code, `deny_lookup_stale`, never the name. Resolution now runs as one lookup pass in a single thread.
- **Refusal is reserved for unknowns.** A name whose lookup has never succeeded (SERVFAIL or a timeout, not a clean "no such name") still refuses with `502 deny_list_unresolved`, which the fetcher retries. If that name's lookups keep failing, every request keeps refusing until one succeeds; the refusal is retryable, and the startup count shows the gap. If no name in the list resolves at all, every request gets `503 deny_list_resolves_nothing`.
- **Startup reports the gap.** A pass at start seeds each name's last good answer and logs `deny_names_unresolved=N`, a count without names.

One name that does not exist, inside a list where others do resolve, still denies nothing. The startup count is the only signal for that case, so it is worth alerting on.

## When the deny file is missing or malformed

A missing, unreadable, oversized, empty or malformed file sends every request a `503 deny_list_unavailable`. The fetcher treats that as transient and retries. The code is logged once at start, and the healthcheck (`python -m assessments.egress --check`) fails while the list does not load.

Staging bind-mounts its deny file instead of baking it into the image. Production is meant to mount the operator's file the same way, so staging exercises that path. The real production list is still a pending host-preparation item.

A separate test asserts that egress refusal codes never reach the model request the clarification path starts from, any mail, or a non-staff template.

## Limits that remain

- **Peer refusal comes after the handshake.** A `peer_denied` connection completes its TCP handshake with the denied host before it is closed. Zero bytes are sent.
- **The resolver is trusted.** A resolver that answered the deny names falsely would hide their addresses. Network isolation, the host allow-list and TLS hostname verification remain the controls for that.
- **Changes need a restart.** The file is read at start. A replaced bind-mounted file keeps a stale inode, so mount the directory or restart.
- **Hex labels cost a real name.** A host such as `0xab.example.org` cannot be listed. Listing it makes the whole file malformed, so every request gets `503 deny_list_unavailable`.

## Verification

The change added 25 tests in `tests/test_egress.py`. They cover a name and a name under it refused before lookup, the four address spellings, a DNS change between requests and between check and connect, per-name bounds without a latch, the last good answer, the never-resolved name, one thread per pass, the all-unresolved list with its startup count, and missing, empty, comment-only, malformed, non-ASCII and oversized files.

The full suite on the final head passed 1744 tests in 50 min 21 s. The run before the review, which already held the first version's tests, passed 1733.

The staging check runs against the compose stack on the dev box. A public stand-in plays the production host. It was refused by name, a name under it was refused, and `1.1.1.1.nip.io` and `1.0.0.1.nip.io` (names that resolve to the address written in them) were refused by resolved address. A control request to an ordinary public name, which the staging stack allows, tunnelled through.

Staging also caught one more wobble. The first run after the review scored 132 PASS, 0 FAIL, 1 NOT RUN: a by-address case missed a single transient lookup. The probe now retries before reporting; it already printed NOT RUN rather than FAIL when the proxy cannot reach public DNS. The final run on a clean tree scored 133 PASS, 0 FAIL, 0 NOT RUN, with the egress healthcheck passing `compose up --wait`.

The merged change, one commit per review finding, is at https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/101.

## Frequently asked questions

### How does an SSRF deny list avoid blocking all egress when DNS fails?

A failed lookup keeps the last good answer for that name, and the proxy logs only the outcome code `deny_lookup_stale`, never the name. A name whose lookup has never succeeded (SERVFAIL or a timeout, not a clean "no such name") refuses with `502 deny_list_unresolved`, which the fetcher retries. If no name in the list resolves at all, every request gets `503 deny_list_resolves_nothing`. A name that does not exist, inside a list where others resolve, still denies nothing, so the startup count is the signal to alert on.

### Why does a deny list miss an IPv4-mapped IPv6 address?

One host can carry several spellings: `::ffff:203.0.113.10`, `::ffff:cb00:710a` and `203.0.113.10` all name the same IPv4 host. A string comparison against a single spelling misses the others. The proxy unwraps IPv4-mapped IPv6 and drops any zone suffix such as `%eth0` on both sides of every comparison, and the tests cover the IPv4, IPv6, `::ffff:a.b.c.d` and `::ffff:hhhh:hhhh` forms.

### Can a DNS change between the check and the connection get past an SSRF deny list?

Not the target's own DNS: the proxy connects to the target addresses it already checked, so the target name is not resolved again. If a deny name's DNS answer moves onto that address in the meantime, the peer check catches it as long as that fresh lookup succeeds (a failed lookup falls back to the last good answer): it compares the peer with a fresh resolution of the deny names and refuses with `peer_denied` before any bytes are sent. The TCP handshake with the denied host still completes first.

<script type="application/ld+json">
{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "How does an SSRF deny list avoid blocking all egress when DNS fails?", "acceptedAnswer": {"@type": "Answer", "text": "A failed lookup keeps the last good answer for that name, and the proxy logs only the outcome code deny_lookup_stale, never the name. A name whose lookup has never succeeded (SERVFAIL or a timeout, not a clean \"no such name\") refuses with 502 deny_list_unresolved, which the fetcher retries. If no name in the list resolves at all, every request gets 503 deny_list_resolves_nothing. A name that does not exist, inside a list where others resolve, still denies nothing, so the startup count is the signal to alert on."}}, {"@type": "Question", "name": "Why does a deny list miss an IPv4-mapped IPv6 address?", "acceptedAnswer": {"@type": "Answer", "text": "One host can carry several spellings: ::ffff:203.0.113.10, ::ffff:cb00:710a and 203.0.113.10 all name the same IPv4 host. A string comparison against a single spelling misses the others. The proxy unwraps IPv4-mapped IPv6 and drops any zone suffix such as %eth0 on both sides of every comparison, and the tests cover the IPv4, IPv6, ::ffff:a.b.c.d and ::ffff:hhhh:hhhh forms."}}, {"@type": "Question", "name": "Can a DNS change between the check and the connection get past an SSRF deny list?", "acceptedAnswer": {"@type": "Answer", "text": "Not the target's own DNS: the proxy connects to the target addresses it already checked, so the target name is not resolved again. If a deny name's DNS answer moves onto that address in the meantime, the peer check catches it as long as that fresh lookup succeeds (a failed lookup falls back to the last good answer): it compares the peer with a fresh resolution of the deny names and refuses with peer_denied before any bytes are sent. The TCP handshake with the denied host still completes first."}}]}
</script>

## Also shipped

- Same app: an authorized erasure path with an audited tombstone exception and a durable record kept outside the backup.
- bobs-big-brain-plugin: installer cleanup confined to validated targets, with recoverable data preserved.
- claude-code-plugins: five unsupported SaaS tutorial packs retired, and the security plugin's HTTP method probes constrained to owned fixtures.
- diagnostic-pro: homepage contrast and keyboard access fixed.
- intent-whop-products: new repo scaffolded with CI and releases on a self-hosted runner.

## Use this

- **List your production hosts by name, and compare addresses in one form.** Resolve the names at check time, unwrap IPv4-mapped IPv6 and drop the zone on both sides, and refuse subdomains of each entry too.
- **Check the connected peer, after the resolved answer.** Run `getpeername()` through the same classifier and a fresh deny resolution, so a deny name that moves onto the target's address between check and connect is refused before a byte is sent.
- **Bound what you remember, per name.** Keep the fresh answer plus a capped history, fall back to the last good answer on a failed lookup, and refuse only for names whose lookup never succeeded, a list that resolves to nothing, or a file that does not load, each with a retryable code.

## Related posts

- [Docker Container Security Hardening: What Unit Tests Miss](https://startaitools.com/posts/docker-hardening-your-test-suite-cannot-see/): the same app's staging deploy, five hardening controls that passed their own tests, and the review question behind each.
- [Every Verdict Carries the Scope It Actually Ran](https://startaitools.com/posts/a-green-result-only-covers-what-it-ran/): every verdict covers only what it ran, including a request-forgery class closed by deleting the feature.
- [Rate Limit a Django Signup Form Without Refusing Anyone](https://startaitools.com/posts/rate-limit-signup-form-without-refusing-anyone/): the same app again, deferring mail instead of refusing applicants, a fail-safe that does not punish users.
