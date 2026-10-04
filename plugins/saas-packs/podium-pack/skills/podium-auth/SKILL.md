---
name: podium-auth
description: Authenticate production Podium integrations and survive the auth-side failures —
  OAuth2 access-token expiry storms, refresh-token decay after 90 days of non-use, scope drift
  on re-grant, secret rotation without downtime, multi-tenant token routing, leakage in commits.
  Use when hardening token caching, building a refresh-token decay monitor, rotating Podium
  client credentials, or recovering from 401/403 auth cascades. Trigger with "podium auth",
  "podium oauth", "podium token refresh", "podium scope drift", "podium credential rotation",
  "podium multi-location auth".
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(jq:*), Bash(python3:*), Bash(openssl:*), Grep
version: 2.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
compatibility: Designed for Claude Code
tags:
  - podium
  - oauth2
  - authentication
  - token-management
  - secret-rotation
  - multi-tenant
---

# Podium Auth

## Overview

Authenticate a service to the Podium API and operate the auth layer in production. This is not a setup walkthrough — it is the auth code your integration runs at 3am when a refresh token expires after the long weekend, when a Podium admin removes a scope on re-grant, when an agency credential router sends a request to the wrong location, and when on-call needs to rotate a leaked client secret without dropping in-flight call-transcript webhooks.

The six production failures this skill prevents:

1. **Access-token expiry storms** — OAuth2 access tokens expire on the order of an hour. Every concurrent request notices expiry simultaneously, races to refresh, the token endpoint rate-limits, and the integration cascades to red. Reactive refresh on `401` is wrong.
2. **Refresh-token decay (90-day non-use clock)** — Podium refresh tokens expire after 90 days without use. Integrations with seasonal usage patterns (a campervan retailer's off-season) silently lose access on day 91 and require a full user reconnection.
3. **Scope drift on re-grant** — When a Podium organization admin re-grants the OAuth app, the new token's scope set may differ from the old one. Cached tokens start returning `403` on previously-working endpoints. Retrying does not help.
4. **Secret leakage in commits** — Podium client secrets are wide-scope and not auto-expiring. A single leaked commit exposes the entire integration. Standard `.env` hygiene is non-optional.
5. **Multi-tenant credential routing** — Agencies managing 50+ Podium organizations cannot use a single env var. Requests sent to the wrong organization silently operate on the wrong location's contacts and webchats with no error.
6. **Rotation without downtime** — Rotating a leaked client secret naively drops every in-flight webhook handler. Production rotation needs dual-credential overlap, drained refresh, and a verified health check before the old secret is revoked.

## Prerequisites

- Python 3.10+ (examples) or Node.js 18+
- Podium account with an OAuth app: Settings → Developer → Apps → Create app
- `client_id`, `client_secret`, `redirect_uri` from the app's OAuth tab
- A user-completed authorization flow producing the initial `refresh_token`
- A secret store the runtime can read at startup and on rotation signal (env var for dev, AWS Secrets Manager / GCP Secret Manager / SOPS for prod)

## Instructions

Build in this order. Each section neutralizes one production failure mode.

### 1. Token-cache pattern (neutralizes expiry storms)

Cache the access token in-process keyed by organization, and refresh **proactively** at 80% of TTL behind a single-flight lock so concurrent callers serialize on one refresh.

```python
import asyncio
import time
from dataclasses import dataclass
from typing import Optional
import httpx

@dataclass
class CachedToken:
    value: str
    expires_at: float  # unix seconds

class PodiumAuth:
    TOKEN_URL = "https://accounts.podium.com/oauth/token"

    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self._cached: Optional[CachedToken] = None
        self._lock = asyncio.Lock()

    async def get_token(self) -> str:
        # Refresh at 80% of TTL — token endpoint can throttle if every call refreshes
        if self._cached and time.time() < self._cached.expires_at - 600:
            return self._cached.value

        async with self._lock:
            # Re-check inside the lock — another coroutine may have refreshed
            if self._cached and time.time() < self._cached.expires_at - 600:
                return self._cached.value
            await self._refresh()
            return self._cached.value

    async def _refresh(self) -> None:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
        if r.status_code != 200:
            raise PodiumAuthError(r.status_code, r.text)
        body = r.json()
        self._cached = CachedToken(
            value=body["access_token"],
            expires_at=time.time() + body["expires_in"],
        )
        # Podium rotates the refresh token on every refresh — persist the new one
        if "refresh_token" in body:
            self.refresh_token = body["refresh_token"]
            await self._persist_refresh_token(body["refresh_token"])

class PodiumAuthError(Exception):
    def __init__(self, status: int, body: str):
        super().__init__(f"Podium auth failed {status}: {body}")
        self.status = status
        self.body = body
```

The single-flight lock is non-negotiable. Under burst load (a Shopify webhook fans out 200 review requests at midnight when the access token has just expired), every request races to the token endpoint, Podium throttles, and the burst fails atomically.

### 2. Refresh-token rotation persistence (neutralizes silent rotation drift)

Podium **rotates the refresh token on every successful refresh.** The old refresh token is invalidated immediately. If your process refreshes successfully but crashes before persisting the new refresh token, the next process startup has a dead credential.

Persist the new refresh token to your secret store inside the refresh call, before returning the new access token to the caller:

```python
async def _persist_refresh_token(self, new_refresh: str) -> None:
    # Replace with your secret store: AWS Secrets Manager, GCP Secret Manager, SOPS, etc.
    # Atomic write — temp file + rename, never a partial write.
    import os, tempfile, json
    path = os.environ["PODIUM_REFRESH_TOKEN_FILE"]
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".podium_refresh.")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump({"refresh_token": new_refresh, "rotated_at": time.time()}, f)
        os.replace(tmp, path)
    except Exception:
        os.unlink(tmp)
        raise
```

### 3. 90-day decay monitor (neutralizes refresh-token expiry)

Podium refresh tokens die after 90 days of non-use. Track `last_used_at` alongside the token; warn at day 60, page at day 75, hard-fail at day 85 with instructions for re-authorization.

```python
DECAY_WARN_DAYS = 60
DECAY_PAGE_DAYS = 75
DECAY_HARD_FAIL_DAYS = 85

def check_decay(last_used_at: float) -> None:
    age_days = (time.time() - last_used_at) / 86400
    if age_days >= DECAY_HARD_FAIL_DAYS:
        raise PodiumAuthError(
            0,
            f"Refresh token unused for {age_days:.0f}d (>{DECAY_HARD_FAIL_DAYS}d) — "
            "user must re-authorize the Podium OAuth app before requests resume.",
        )
    if age_days >= DECAY_PAGE_DAYS:
        page_oncall(
            f"Podium refresh token nearing expiry: {age_days:.0f}d / 90d",
            severity="high",
        )
    elif age_days >= DECAY_WARN_DAYS:
        log_warn(f"Podium refresh token age: {age_days:.0f}d / 90d")
```

This protects the seasonal-business case explicitly: a campervan retailer's off-season is exactly the failure mode where naive integrations break silently and ship operators discover it when they reopen for summer.

### 4. Scope validation on every refresh (neutralizes scope drift)

When a Podium admin re-grants your app, the new access token's scope set is whatever the admin selected — which may be a subset of what you previously had. Validate scopes immediately after each refresh; fail loudly rather than discover the drift on a 403 in production:

```python
REQUIRED_SCOPES = {
    "conversations.read",
    "conversations.write",
    "contacts.read",
    "contacts.write",
    "reviews.read",
    "reviews.write",
}

def validate_scopes(token_body: dict) -> None:
    granted = set(token_body.get("scope", "").split(" "))
    missing = REQUIRED_SCOPES - granted
    if missing:
        raise PodiumAuthError(
            0,
            f"Scope drift detected — missing: {sorted(missing)}. "
            "A Podium org admin must re-grant these scopes in the OAuth app settings.",
        )
```

Wire `validate_scopes(body)` into `_refresh()` immediately after the JSON parse, before assigning to `self._cached`.

### 5. Secret leakage prevention (neutralizes commit leakage)

Podium client secrets are long-lived and grant access to every endpoint the OAuth app is scoped for. **Never put them in source code, log output, or git history.**

```bash
# .gitignore — verify these are present
.env
.env.local
.env.*.local
podium-credentials.json
podium-refresh-token.json

# Audit the repo for accidentally-committed credentials before this becomes prod
git log --all --full-history --oneline -- .env
grep -rnE "podium.*(client_secret|refresh_token)\s*=\s*['\"]" --include="*.py" --include="*.ts" --include="*.json" .
```

For prod, encrypt credentials at rest with SOPS + age (Intent Solutions standard) and decrypt in-process — never write the plaintext to disk.

### 6. Dual-credential rotation runbook (neutralizes downtime on rotation)

When rotating a leaked or aging client secret:

1. **Create the new credential first** — in the Podium developer console, generate a new client_secret for the same OAuth app. Both old and new are valid simultaneously for a short window.
2. **Deploy the new secret to your secret store** under a versioned key (`podium/client_secret_v2`).
3. **Signal the running process to reload** (SIGHUP, env var change trigger, or rolling restart). The token cache picks up the new secret on the next refresh.
4. **Verify with a health-check call** — fetch the OAuth token info endpoint and confirm the response carries the expected `client_id`.
5. **Revoke the old secret** in the Podium console only after the health check passes and queue depth has drained.

```python
async def verify_credential(token: str) -> bool:
    async with httpx.AsyncClient(timeout=5) as c:
        r = await c.get(
            "https://api.podium.com/v4/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    return r.status_code in (200, 204)
```

## Error Handling

| HTTP Status | Podium Error | Root Cause | Action |
|---|---|---|---|
| `401 Unauthorized` | `invalid_token` | Access token expired or malformed | Refresh; if refresh also 401, re-authorize |
| `401 Unauthorized` | `invalid_grant` | Refresh token expired (90d) or revoked | User must re-authorize the OAuth app |
| `403 Forbidden` | `insufficient_scope` | Scope removed on re-grant | Admin re-grants required scopes |
| `400 Bad Request` | `invalid_client` | Wrong client_id/secret combination | Verify against Podium dev console |
| `429 Too Many Requests` | `rate_limited` | Token endpoint throttled (auth burst) | Back off with `Retry-After` header |
| `500/502/503` | `server_error` | Podium-side transient | Exponential backoff with jitter, max 4 attempts |

## Examples

### Minimal access-token request

```bash
curl -s -X POST https://accounts.podium.com/oauth/token \
  -d grant_type=refresh_token \
  -d refresh_token="{your-refresh-token}" \
  -d client_id="{your-client-id}" \
  -d client_secret="{your-client-secret}" | jq '{access_token, expires_in, scope}'
```

### Wire the cache into an HTTP client

```python
auth = PodiumAuth(
    client_id=os.environ["PODIUM_CLIENT_ID"],
    client_secret=os.environ["PODIUM_CLIENT_SECRET"],
    refresh_token=load_refresh_token(),
)

async def podium_get(path: str) -> httpx.Response:
    token = await auth.get_token()
    async with httpx.AsyncClient() as c:
        return await c.get(
            f"https://api.podium.com{path}",
            headers={"Authorization": f"Bearer {token}"},
        )
```

### Multi-tenant router (agency case)

```python
class PodiumOrgRouter:
    def __init__(self, credentials: dict[str, dict]):
        # credentials = {"acme-rv": {client_id, client_secret, refresh_token}, ...}
        self._auths: dict[str, PodiumAuth] = {
            org: PodiumAuth(**creds) for org, creds in credentials.items()
        }

    async def get_token(self, org_slug: str) -> str:
        auth = self._auths.get(org_slug)
        if not auth:
            raise KeyError(f"No Podium credentials for org: {org_slug}")
        return await auth.get_token()
```

## Output

- Token-cache module with single-flight refresh at 80% TTL
- Refresh-token rotation persistence (atomic write to secret store)
- 90-day decay monitor with warn / page / hard-fail thresholds
- Scope validation invoked on every refresh
- `.gitignore` audited for credential leakage patterns
- Dual-credential rotation runbook documented in the repo

## Resources

- [Podium API docs — Authentication](https://docs.podium.com/reference/authentication)
- [OAuth 2.0 Authorization Code Flow](https://docs.podium.com/reference/oauth-2-0)
- [Podium Developer Console](https://www.podium.com/developer)
- [config/settings.yaml](config/settings.yaml) — TTL thresholds, decay alert routing, scope list
- [references/errors.md](references/errors.md) — ERR_AUTH_* codes with cause + solution
- [references/examples.md](references/examples.md) — 10 worked examples (single-tenant, multi-tenant, rotation, decay)
- [references/implementation.md](references/implementation.md) — Node.js equivalents, AWS/GCP secret-store wiring, SOPS+age integration
- [scripts/token_refresh.py](scripts/token_refresh.py) — CLI: manual token refresh with persistence
- [scripts/rotate_secret.py](scripts/rotate_secret.py) — CLI: dual-credential rotation orchestrator
- [scripts/verify_creds.py](scripts/verify_creds.py) — CLI: health-check a credential pair
- [scripts/scope_audit.py](scripts/scope_audit.py) — CLI: compare required vs granted scopes
