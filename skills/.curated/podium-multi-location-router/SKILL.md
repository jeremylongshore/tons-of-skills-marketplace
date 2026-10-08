---
name: podium-multi-location-router
description: Route Podium API calls across multiple physical locations with strict
  per-location credential isolation, pre-flight location-ID verification, an
  immutable audit trail of every write, idempotent bulk onboarding, and
  per-location rate-limit budgets that cannot starve each other. Use when running
  Podium for more than one physical store (an agency operator managing 50+
  accounts, a multi-store SMB with 2+ locations, or a compliance team that needs
  to prove which location received which write). Trigger with "podium
  multi-location", "podium location router", "podium per-location", "podium
  location audit", "podium bulk onboarding", "podium location_uid verification".
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(jq:*), Bash(python3:*), Bash(sqlite3:*), Grep
version: 2.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
compatibility: Designed for Claude Code
tags:
  - podium
  - multi-location
  - credential-isolation
  - audit-trail
  - agency-ops
  - rate-limit-isolation
---

# Podium Multi-Location Router

## Overview

Route Podium API calls across multiple physical locations and operate the routing layer in production. This is not a tutorial on Podium's location model — it is the per-location dispatch code your integration runs when Sydney and Burleigh Heads share a single OAuth app, when an agency onboards five new stores in one afternoon, and when a compliance auditor walks in and asks "which location's webchat received that contact write at 14:07 UTC last Tuesday."

The six production failures this skill prevents:

1. **Writes to wrong location silently** — Sydney's contact write lands on Burleigh Heads' contact list because the calling code resolved `location_uid` from a stale lookup or hard-coded the wrong UID. The Podium API accepts it, returns 200, and the data sits in the wrong location with no error surface. Naive integrations discover this when a customer reports "I'm getting review requests for a store I've never been to."
2. **Credential cross-contamination** — Sydney's OAuth token gets reused for a write to Burleigh Heads. The Podium API does not reject this because the OAuth app is org-scoped and both locations live under the same org. The write succeeds; the audit trail attributes it to Sydney's credential; post-incident forensics cannot tell whether the write was authorized by Sydney's operator or by a bug.
3. **Audit trail missing location-ID** — log lines say `wrote contact name=Jane Doe` without saying which `location_uid` received the write. When a compliance question lands months later, the integration cannot answer "which location received this customer's data?" The answer determines GDPR data-subject scope and PCI cardholder-data exposure.
4. **Bulk onboarding race condition** — onboarding 5 new locations in one operation spawns 5 OAuth authorization flows. One fails partway (a user closed the consent tab, a redirect URI mismatched), the orchestrator continues with the rest, and the credentials map ends up with 4 valid entries + 1 dangling half-record. Subsequent operations against the half-onboarded location either crash or, worse, fall through to a default credential and write to the wrong place.
5. **Location-ID verification skipped on write** — the application code passes an arbitrary `location_uid` into the Podium call. Podium accepts any well-formed UID and returns 403 only if the current token genuinely has no access. The 403 is swallowed by an upstack handler ("just a stale auth, will retry"), and the integration silently stops working for one location while the rest keep flowing.
6. **Rate-limits not isolated per location** — the integration uses a single shared token bucket. Sydney runs a holiday review-request burst at 2pm and burns the org-wide quota; Burleigh Heads' webchats start returning 429 with no explanation visible to the Burleigh Heads operator who has done nothing wrong.

## Prerequisites

- Python 3.10+
- `podium-auth` skill installed; this skill consumes its `PodiumAuth` and `PodiumOrgRouter` classes
- `podium-rate-limit-survival` skill installed; this skill consumes its per-bucket budget primitive
- Podium OAuth app with `locations.read` scope granted (verifying a `location_uid` requires `GET /v4/locations`)
- A writable directory for the audit log (default `./audit-log/podium-router.jsonl`)
- A persistent location-credential map (file, AWS Secrets Manager, GCP Secret Manager, or SOPS-encrypted YAML)

## Instructions

Build in this order. Each section neutralizes one production failure mode.

### 1. Per-location credential isolation (neutralizes cross-contamination)

The router holds one `PodiumAuth` instance per `location_uid`, never per org. Two locations under the same org get two separate auth instances because the audit trail must attribute every call to a specific location and a specific credential record — even if the underlying OAuth refresh token happens to be shared at the org level.

```python
import asyncio, time
from dataclasses import dataclass, field
from typing import Optional
from podium_auth import PodiumAuth, PodiumOrgRouter, PodiumAuthError

@dataclass
class LocationCredential:
    location_uid: str
    org_slug: str
    client_id: str
    client_secret: str
    refresh_token_file: str
    verified_at: float = 0.0   # unix seconds; 0 = never verified

class LocationRouter:
    def __init__(self, credentials: list[LocationCredential], audit_log_path: str):
        self._creds: dict[str, LocationCredential] = {c.location_uid: c for c in credentials}
        self._auths: dict[str, PodiumAuth] = {}
        self._audit_log_path = audit_log_path
        self._verify_lock = asyncio.Lock()

    def get_client(self, location_uid: str) -> "PodiumLocationClient":
        cred = self._creds.get(location_uid)
        if not cred:
            raise UnknownLocationError(location_uid)
        if location_uid not in self._auths:
            self._auths[location_uid] = PodiumAuth(
                client_id=cred.client_id,
                client_secret=cred.client_secret,
                refresh_token=load_refresh_token(cred.refresh_token_file),
            )
        return PodiumLocationClient(
            location_uid=location_uid,
            auth=self._auths[location_uid],
            router=self,
        )
```

The map key is `location_uid`, never `org_slug`. Two locations under the same org get two map entries with the same `client_id`/`client_secret` but distinct `refresh_token_file` paths. This is the line that prevents Sydney's token from being reused for a Burleigh Heads write — the router has no syntactic path from a `location_uid` to a different location's auth.

### 2. Pre-flight location-ID verification (neutralizes silent wrong-location writes)

Before any write, the router confirms the `location_uid` exists in the set returned by `GET /v4/locations` for the current credential. Cache the verification with a short TTL — typically 1 hour — so a re-org of locations on the Podium side eventually propagates without re-verifying every call.

```python
VERIFY_TTL_SECONDS = 3600

async def ensure_location_verified(self, location_uid: str) -> None:
    cred = self._creds[location_uid]
    if time.time() - cred.verified_at < VERIFY_TTL_SECONDS:
        return
    async with self._verify_lock:
        if time.time() - cred.verified_at < VERIFY_TTL_SECONDS:
            return
        auth = self._auths[location_uid]
        token = await auth.get_token()
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(
                "https://api.podium.com/v4/locations",
                headers={"Authorization": f"Bearer {token}"},
            )
        if r.status_code != 200:
            raise LocationVerificationError(location_uid, r.status_code, r.text)
        ids = {loc["uid"] for loc in r.json().get("locations", [])}
        if location_uid not in ids:
            raise LocationNotInScopeError(location_uid, sorted(ids))
        cred.verified_at = time.time()
```

`LocationNotInScopeError` is the loud version of "Podium returned 403 silently." It fires before the call is made, so the caller cannot accidentally write to a location their token does not own. The 1-hour TTL keeps the verification cost negligible while bounding the staleness window.

### 3. Structured audit log on every call (neutralizes audit-trail gaps)

Every API call routed through this skill emits one JSON line to the audit log. The fields are fixed: `{ts, location_uid, org_slug, endpoint, method, status, request_id, latency_ms}`. No tokens, no request bodies, no PII — just the routing fingerprint.

```python
import json, os, time, uuid

def emit_audit(self, *, location_uid: str, endpoint: str, method: str,
               status: int, latency_ms: float, request_id: str) -> None:
    cred = self._creds[location_uid]
    record = {
        "ts": time.time(),
        "location_uid": location_uid,
        "org_slug": cred.org_slug,
        "endpoint": endpoint,
        "method": method,
        "status": status,
        "request_id": request_id,
        "latency_ms": round(latency_ms, 2),
    }
    # Append-only; one line per call. Operators rotate with logrotate, not in-process.
    os.makedirs(os.path.dirname(self._audit_log_path), exist_ok=True)
    with open(self._audit_log_path, "a") as f:
        f.write(json.dumps(record) + "\n")
```

The `request_id` is generated by the client wrapper (`uuid.uuid4().hex`) and also returned in any error so the operator can correlate a customer complaint to a single audit-log line. Six months later, when compliance asks "which location received this write?", `audit_log_query.py` answers in one second.

### 4. Idempotent bulk onboarding orchestrator (neutralizes partial-failure races)

Onboarding multiple locations in one operation must be resumable. The orchestrator processes one location at a time, writes each location's credential record to the map atomically, and is safe to re-run after partial failure — already-onboarded locations are detected and skipped.

```python
@dataclass
class OnboardingResult:
    location_uid: str
    status: str          # "onboarded" | "skipped_existing" | "failed"
    error: Optional[str] = None

async def onboard_locations(self, new: list[LocationCredential]) -> list[OnboardingResult]:
    results: list[OnboardingResult] = []
    for cred in new:
        if cred.location_uid in self._creds:
            results.append(OnboardingResult(cred.location_uid, "skipped_existing"))
            continue
        try:
            # 1. Persist credential record atomically BEFORE adding to in-memory map
            self._persist_credential(cred)
            # 2. Build auth + verify location_uid is reachable
            self._auths[cred.location_uid] = PodiumAuth(
                client_id=cred.client_id,
                client_secret=cred.client_secret,
                refresh_token=load_refresh_token(cred.refresh_token_file),
            )
            self._creds[cred.location_uid] = cred
            await self.ensure_location_verified(cred.location_uid)
            results.append(OnboardingResult(cred.location_uid, "onboarded"))
        except Exception as e:
            # Roll back the half-written entry so a re-run doesn't see a phantom location
            self._creds.pop(cred.location_uid, None)
            self._auths.pop(cred.location_uid, None)
            results.append(OnboardingResult(cred.location_uid, "failed", str(e)))
    return results
```

The critical invariant: a location is either fully onboarded (credential persisted + auth instantiated + verification passed) or fully absent. There is no third state. A re-run after partial failure picks up exactly where the previous run left off.

### 5. Per-location rate-limit budgets (neutralizes shared-quota starvation)

This skill stacks on top of `podium-rate-limit-survival`. Each location gets its own token bucket; one location's burst cannot starve another. The default budget per location is conservative — read it from `config/settings.yaml` and tune per-deployment.

```python
from podium_rate_limit import TokenBucket   # from podium-rate-limit-survival

class PodiumLocationClient:
    def __init__(self, location_uid: str, auth: PodiumAuth, router: LocationRouter):
        self._location_uid = location_uid
        self._auth = auth
        self._router = router
        # One bucket per location — sized to the per-location plan, NOT the org-wide quota.
        self._bucket = router.bucket_for(location_uid)

    async def call(self, method: str, path: str, **kwargs) -> httpx.Response:
        await self._router.ensure_location_verified(self._location_uid)
        await self._bucket.acquire()
        request_id = uuid.uuid4().hex
        token = await self._auth.get_token()
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.request(
                method,
                f"https://api.podium.com{path}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Request-ID": request_id,
                },
                **kwargs,
            )
        self._router.emit_audit(
            location_uid=self._location_uid,
            endpoint=path,
            method=method,
            status=r.status_code,
            latency_ms=(time.monotonic() - start) * 1000,
            request_id=request_id,
        )
        return r
```

A burst from Sydney drains Sydney's bucket and only Sydney's bucket. Burleigh Heads has its own bucket with its own refill timer and remains operational regardless.

### 6. Unknown-location refusal (neutralizes silent fall-through)

Asking for a client for an unknown `location_uid` raises immediately. There is no default credential, no "best guess" routing, no fallback to the first registered location. This is the single line that prevents "5 fails, the 6th call falls through to wherever" from being a viable failure mode.

```python
class UnknownLocationError(KeyError):
    def __init__(self, location_uid: str):
        super().__init__(
            f"No credentials for location_uid={location_uid}. "
            f"Run onboard_location.py to register, then reload the router."
        )

class LocationNotInScopeError(PodiumAuthError):
    def __init__(self, location_uid: str, scope: list[str]):
        super().__init__(
            403,
            f"location_uid={location_uid} not in /v4/locations scope. "
            f"Token sees {len(scope)} locations; this UID is not one of them. "
            f"Verify with verify_location.py."
        )
```

## Error Handling

| HTTP Status | Error | Root Cause | Action |
|---|---|---|---|
| `403 Forbidden` | `LocationNotInScopeError` | `location_uid` not in token's `/v4/locations` set | Run `verify_location.py`; confirm the credential is for the right org |
| `404 Not Found` | `LocationDeletedError` | Location was deleted on the Podium side | Remove from credentials map; alert the operator |
| N/A | `UnknownLocationError` | Caller asked for a `location_uid` not in the map | Re-run `onboard_location.py` for the missing UID |
| N/A | `OnboardingPartialFailure` | Bulk onboarding completed N-1 of N locations | Re-run; idempotent — already-onboarded are skipped |
| `429 Too Many Requests` | `LocationRateLimitExceeded` | Per-location bucket exhausted | Bucket auto-refills; respect `Retry-After`; tune bucket in `config/settings.yaml` |
| `401 Unauthorized` | underlying `PodiumAuthError` | Token refresh failed for this specific location | Surface to ops; auth-side recovery is `podium-auth`'s domain |

## Examples

### Pre-flight verify a location_uid before a write

```bash
python3 scripts/verify_location.py \
  --location-uid {your-location-uid} \
  --credentials-file ./config/locations.json
```

Exit code 0 = the UID is in scope; exit code 1 = not in scope (silent 403 prevented); exit code 2 = config or network error.

### Onboard a new location idempotently

```bash
python3 scripts/onboard_location.py \
  --location-uid {your-new-location-uid} \
  --org-slug acme-rv-sydney \
  --client-id-env PODIUM_CLIENT_ID \
  --client-secret-env PODIUM_CLIENT_SECRET \
  --refresh-token-file ./secrets/sydney-refresh.json \
  --credentials-file ./config/locations.json
```

Re-running with the same `--location-uid` is safe — already-onboarded locations are detected and the script exits 0 with status `skipped_existing`.

### Query the audit log for a specific location and date range

```bash
python3 scripts/audit_log_query.py \
  --audit-log ./audit-log/podium-router.jsonl \
  --location-uid {your-location-uid} \
  --since 2026-05-01 \
  --until 2026-05-12 \
  --output json
```

Output: one JSON record per matching call, including `request_id` for cross-correlation with downstream systems.

### Programmatic use — write a contact to a specific location

```python
router = LocationRouter.from_credentials_file("./config/locations.json",
                                              audit_log_path="./audit-log/podium-router.jsonl")
client = router.get_client(location_uid="{your-location-uid}")
r = await client.call("POST", "/v4/contacts", json={
    "first_name": "Jane",
    "last_name": "Doe",
    "phone": "+15555550100",
    "location_uid": "{your-location-uid}",
})
r.raise_for_status()
```

Every call produces exactly one audit-log line. The `location_uid` argument is verified against `/v4/locations` before the request is sent.

## Output

- `LocationRouter` library with one `PodiumAuth` instance per `location_uid` (never per org)
- Pre-flight `ensure_location_verified()` against `GET /v4/locations` with a 1-hour TTL
- Append-only JSONL audit log: one line per call with `{ts, location_uid, org_slug, endpoint, method, status, request_id, latency_ms}`
- Idempotent `onboard_locations()` orchestrator — safe to re-run after partial failure
- Per-location token bucket sized independently of org-wide quota
- `UnknownLocationError` and `LocationNotInScopeError` to make silent wrong-location writes impossible

## Resources

- [Podium API docs — Locations](https://docs.podium.com/reference/locations)
- [Podium API docs — Contacts](https://docs.podium.com/reference/contacts)
- [config/settings.yaml](config/settings.yaml) — verification TTL, audit-log path, per-location bucket defaults, onboarding concurrency
- [references/errors.md](references/errors.md) — ERR_LOC_* codes with cause + solution
- [references/examples.md](references/examples.md) — 10 worked examples (single-location, agency, onboarding, audit query)
- [references/implementation.md](references/implementation.md) — Node.js port, audit-log retention, SQLite query layer
- [scripts/location_router.py](scripts/location_router.py) — library: `LocationRouter.get_client(location_uid)`
- [scripts/verify_location.py](scripts/verify_location.py) — CLI: confirm a `location_uid` is reachable
- [scripts/onboard_location.py](scripts/onboard_location.py) — CLI: idempotently onboard a new location
- [scripts/audit_log_query.py](scripts/audit_log_query.py) — CLI: query the audit log by location_uid + date range
