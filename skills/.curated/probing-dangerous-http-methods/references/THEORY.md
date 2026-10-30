# HTTP method evidence and limits

## Discovery and policy

OPTIONS and Allow describe advertised capabilities. They do not demonstrate
handler execution, authentication bypass or mutation. PUT, DELETE and WebDAV
have legitimate uses; a route name or method name alone is not a vulnerability.
The operator supplies the unexpected-method policy in approved ROE metadata.

## TRACE and browser boundaries

TRACE can echo a request. This probe sends a fresh synthetic nonce and requires
both its echo and the matching request line. It sends no cookies or credentials.
The Fetch standard forbids CONNECT, TRACE and TRACK as script-selected methods;
therefore a successful native TRACE request does not prove the old TRACE-via-XHR
HttpOnly-cookie theft chain. Assess browser behavior and any separate exploit
path independently. Do not translate nonce echo into session-theft evidence.

## Controlled CONNECT

CONNECT establishes a proxy tunnel to a destination. A status-only response
cannot establish arbitrary forwarding or access to internal services. This
adapter requests one owner-controlled HTTPS fixture through the exact approved
HTTP proxy, retains TLS verification and checks the approved response digest.
It proves only that bounded experiment. It does not enumerate destinations,
probe cloud metadata or infer a provider-specific credential exposure.

## DEBUG and PROPFIND

DEBUG is application-specific. Verify only an owner-approved response fixture;
do not infer diagnostic access from a generic HTTP 200 page. PROPFIND uses Depth
0 and asks only for resourcetype. Positive evidence needs a DAV multistatus for
the exact target and a successful property response. It does not establish a
recursive directory listing. Responses are bounded UTF-8 XML; DTD/entity
constructs and other declarations are rejected rather than resolved.

## Conditional file experiments

Generated URLs use random nonces beneath the attested exclusive directory.
HEAD 404 is followed by conditional PUT with If-None-Match *, then exact
synthetic readback and a strong ETag. COPY/MOVE require a fresh absent
destination and Overwrite F. Conditional cleanup rechecks bytes and ETag,
uses If-Match, and verifies absence. A changed resource, lost acknowledgement or
partial operation is inconclusive; idempotent method semantics do not justify
blindly retrying a mutation. These experiments never upload executable payloads.

## Collections and concurrency

WebDAV collection DELETE has recursive semantics. A collection ETag need not
represent its children's state. MKCOL cleanup consequently requires explicit
LOCK and PROPFIND helper permission: verify a new empty collection, request an
exclusive depth-infinity write lock with a maximum 60-second lease, validate its
nonce owner/token/root/type/depth, reinspect emptiness, and conditionally delete
using both the strong ETag and lock token. The locally observed lease must still
be valid. No delete occurs if children or ambiguous lock metadata appear.
This relies on the server enforcing standard lock/precondition semantics and
cannot protect against an administrative override or a noncompliant server.
On failure retain evidence; short locks expire without an unverified cleanup.

## Primary sources

- [RFC 9110 §9: HTTP methods](https://www.rfc-editor.org/rfc/rfc9110.html#section-9)
- [Fetch: forbidden methods](https://fetch.spec.whatwg.org/#forbidden-method)
- [RFC 4918: WebDAV, particularly §§7, 9.1, 9.6, 9.10 and 10.4](https://www.rfc-editor.org/rfc/rfc4918.html)
- [Requests: proxy and TLS behavior](https://requests.readthedocs.io/en/latest/user/advanced/#proxies)
