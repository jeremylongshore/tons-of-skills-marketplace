---
name: podium-review-request-automation
description: Trigger Podium review requests from Shopify order-shipped events and survive the
  delivery-side failures — cooldown-window violations, ship-event races with refunds, failed-send
  silent rejections, dropped review-response webhooks, multi-platform routing misconfig, and
  opt-out compliance gaps. Use when wiring Shopify orders-fulfilled to Podium review campaigns,
  building a cooldown gate, ingesting review-response webhooks, or auditing opt-out compliance
  across flows. Trigger with "podium review request", "shopify review automation", "podium
  cooldown", "review response webhook", "podium opt-out audit", "review platform routing".
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(jq:*), Bash(python3:*), Bash(redis-cli:*), Grep
version: 2.11.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
compatibility: Designed for Claude Code
tags:
  - podium
  - reviews
  - shopify-integration
  - cooldown-policy
  - opt-out-compliance
  - automation
---

# Podium Review Request Automation

## Overview

Wire Shopify order-shipped events to Podium review requests and operate the delivery layer in production. This is not a campaign-builder walkthrough — it is the integration code your system runs when a merchant ships 300 orders on Black Friday, when a customer initiates a refund 30 minutes after the request fires, when a carrier silently drops the SMS, when a 1-star review-response webhook never arrives, and when an opt-out from a different marketing flow needs to suppress the review-request path.

The six production failures this skill prevents:

1. **Review requests sent during cooldown** — A customer received a review request 5 days ago; a new Shopify shipment triggers another within the cooldown window. The customer is annoyed, replies STOP, and Podium suspends the account for spam-pattern volume. A naive integration has no cooldown gate and rediscovers this rule with every new merchant.
2. **Shopify-ship-event race with refund** — An order ships, the `orders/fulfilled` webhook fires, the review request is sent, and 30 minutes later the customer initiates a refund. The review request is now embarrassing and brand-damaging. Without a delay window between fulfillment and send, every refund-prone product line generates this incident.
3. **Failed-send silent rejection** — Podium accepts the `POST /v4/review-invitations` call and returns 200 with an `invitation_id`. Hours later the actual SMS send is rejected at the carrier (T-Mobile filter, invalid number, opt-out on the destination). The integration thinks it succeeded. The merchant's review velocity quietly drops.
4. **Review-response webhook drops** — A customer leaves a 1-star review. Podium fires the `review.received` webhook. The receiver returns 500 due to a deployment, Podium retries 3 times, then gives up. The team finds out a week later from Google directly. Without webhook persistence + replay + idempotency, low-volume signal evaporates.
5. **Multi-platform routing misconfig** — A campaign is configured to route review requests to Facebook, but the customer doesn't have Facebook. The request quietly fails to land — Podium's response shows "delivered" because the SMS went out, but the destination link 404s on the customer's device. Without per-customer platform validation, the merchant's review pipeline silently caters to the wrong network.
6. **Opt-out compliance gaps** — A customer opted out of marketing SMS 6 months ago, but the opt-out flag sits on the email-marketing flow only. The Podium review-request flow has its own consent path and fires anyway. The merchant catches a TCPA complaint. Opt-out must be a single check across every flow that touches the contact, not per-channel.

## Prerequisites

- Python 3.10+ with `httpx` and `redis` (or `sqlite3` for the SQLite cooldown backend)
- A Podium OAuth app authenticated via the `podium-auth` sibling skill — this skill assumes `auth.get_token()` is available
- A Shopify store with `orders/fulfilled` webhook configured pointing at this integration
- Redis (production) or SQLite (single-node) for cooldown state — keyed by phone number, value is `last_contact_at` epoch seconds
- A persistent inbox for Podium `review.received` webhooks — see the `podium-webhook-reliability` sibling skill for the durable-queue pattern this skill consumes
- An opt-out source-of-truth table that aggregates marketing-SMS, transactional-SMS, and review-flow opt-outs into a single contact-level boolean — see the `podium-contact-dedup` sibling skill for the merge semantics this skill relies on

## Instructions

Build in this order. Each section neutralizes one production failure mode.

### 1. Cooldown gate (neutralizes review-request spam)

Cooldown is a contact-level rate limit, not a campaign-level one. A customer who places two orders in three days must not get two review requests. Key the cooldown by normalized E.164 phone (the canonical contact identifier across Podium and Shopify) and store `last_contact_at` as epoch seconds.

```python
import time
import redis
from typing import Optional

class CooldownGate:
    DEFAULT_COOLDOWN_DAYS = 30

    def __init__(self, redis_url: str, cooldown_days: int = DEFAULT_COOLDOWN_DAYS):
        self.r = redis.from_url(redis_url, decode_responses=True)
        self.cooldown_seconds = cooldown_days * 86400

    def _key(self, phone_e164: str) -> str:
        return f"podium:cooldown:{phone_e164}"

    def can_send(self, phone_e164: str) -> tuple[bool, Optional[float]]:
        """Returns (allowed, seconds_remaining_if_blocked)."""
        last = self.r.get(self._key(phone_e164))
        if last is None:
            return True, None
        elapsed = time.time() - float(last)
        if elapsed >= self.cooldown_seconds:
            return True, None
        return False, self.cooldown_seconds - elapsed

    def mark_sent(self, phone_e164: str) -> None:
        # SETEX with the cooldown window — Redis auto-expires the key, so old contacts roll off.
        self.r.setex(self._key(phone_e164), self.cooldown_seconds, time.time())
```

The cooldown window default is 30 days — adjust per-merchant in `config/settings.yaml`. Critically, `mark_sent` runs **after** Podium accepts the API call, but the cooldown is the gate for the decision — never let two concurrent webhook handlers both pass the check and both send.

### 2. Refund-race buffer (neutralizes premature sends)

Shopify's `orders/fulfilled` fires the moment the merchant marks a shipment as packed and labeled. Customer receipt of the package — and the window for refund decisions before review-worthiness exists — happens hours to days later. Buffer the send by a configurable delay (default 5 days from `fulfilled_at`), and re-check the order's refund status at send time:

```python
async def schedule_review_request(order: dict, send_after: float) -> None:
    """Schedule, do not send-now. The actual send is gated at fire time on refund status."""
    await delayed_queue.enqueue(
        topic="podium.review.send",
        payload={"order_id": order["id"], "phone": order["customer"]["phone"]},
        not_before=send_after,
    )

async def fire_scheduled_send(payload: dict) -> None:
    order = await shopify.get_order(payload["order_id"])
    # Refund check at send time — order may have been refunded in the buffer window
    if order.get("financial_status") in {"refunded", "partially_refunded", "voided"}:
        log_event("review_send_skipped_refund", order_id=order["id"])
        return
    if order.get("cancelled_at") is not None:
        log_event("review_send_skipped_cancelled", order_id=order["id"])
        return
    await send_review_request(order)
```

The delayed queue must survive process restart — Redis streams, SQS with DLQ, or Postgres-backed `pgmq` all work. An in-memory `asyncio.sleep` does not.

### 3. Failed-send detection (neutralizes silent rejection)

The Podium API's `POST /v4/review-invitations` response only confirms the invitation record was created — it does not confirm the SMS was delivered to the carrier. Subscribe to `review_invitation.failed` and `review_invitation.delivered` webhooks separately, persist them keyed by `invitation_id`, and reconcile delivery state against the original request after a 24-hour SLA window:

```python
class InvitationOutbox:
    """Tracks every send → carrier-confirmed-delivered transition. Anything unresolved after 24h is escalated."""

    def record_sent(self, invitation_id: str, phone: str, order_id: str) -> None:
        self.r.hset(f"podium:inv:{invitation_id}", mapping={
            "status": "sent",
            "phone": phone,
            "order_id": order_id,
            "sent_at": time.time(),
        })
        self.r.expire(f"podium:inv:{invitation_id}", 86400 * 7)

    def record_delivered(self, invitation_id: str) -> None:
        self.r.hset(f"podium:inv:{invitation_id}", "status", "delivered")
        self.r.hset(f"podium:inv:{invitation_id}", "delivered_at", time.time())

    def record_failed(self, invitation_id: str, reason: str) -> None:
        self.r.hset(f"podium:inv:{invitation_id}", "status", "failed")
        self.r.hset(f"podium:inv:{invitation_id}", "failure_reason", reason)
        # Critical: roll back the cooldown — the customer never received the message,
        # so blocking them from a future request is wrong.
        phone = self.r.hget(f"podium:inv:{invitation_id}", "phone")
        if phone:
            self.r.delete(f"podium:cooldown:{phone}")
```

The cooldown-rollback step on `failed` is non-obvious and important. Treating a failed send as a "did contact" decision punishes a customer for a carrier filter they did not ask for.

### 4. Review-response webhook handler (neutralizes dropped responses)

Podium fires `review.received` when a customer leaves a review on any routed platform. The webhook must be idempotent (Podium retries on any non-2xx for up to 3 attempts) and must classify sentiment so negative reviews escalate while positive reviews land in a thank-you flow:

```python
import hmac, hashlib

def verify_signature(body: bytes, signature_header: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)

async def handle_review_received(req) -> tuple[int, str]:
    body = await req.body()
    sig = req.headers.get("X-Podium-Signature", "")
    if not verify_signature(body, sig, os.environ["PODIUM_WEBHOOK_SECRET"]):
        return 401, "bad signature"

    event = json.loads(body)
    event_id = event["id"]

    # Idempotency — Podium retries, our handler must not double-process.
    if not await idempotency.claim(event_id, ttl_seconds=86400):
        return 200, "duplicate"

    review = event["data"]
    rating = review["rating"]            # 1..5
    platform = review["platform"]        # "google" | "facebook" | "podium"

    if rating <= 2:
        await escalate_negative_review(review)
    elif rating >= 4:
        await thank_positive_reviewer(review)
    # 3-star = neutral, log only

    return 200, "ok"
```

Persistence under load is covered by the `podium-webhook-reliability` sibling skill. The classification step is the application-level contract — wire `escalate_negative_review` to a Slack/email channel with response SLA, and `thank_positive_reviewer` to a follow-up campaign.

### 5. Multi-platform routing validation (neutralizes silent route-failure)

A merchant configures a Podium campaign to route requests to Facebook. The SMS goes out, but the link inside it lands on `facebook.com/{merchant-page}/reviews` — which only works if the customer is logged into Facebook on the receiving device. Many customers don't have Facebook at all. Without per-customer platform inference, the merchant's review pipeline silently fails.

Validate platform routing **at request-time** against a customer profile if one exists, and fall back to a known-good default (Podium's own webchat review) when the configured target is uncertain:

```python
def select_review_platform(customer: dict, campaign: dict) -> str:
    """Choose the highest-confidence platform for this customer.

    Priority: explicit customer preference > campaign default > podium-webchat fallback.
    """
    if customer.get("preferred_review_platform"):
        return customer["preferred_review_platform"]

    target = campaign.get("default_platform", "google")
    # Light heuristic: prefer google over facebook for unknown-platform customers.
    # Facebook reviews require a logged-in account; google reviews work for anyone.
    if target == "facebook" and not customer.get("facebook_uid"):
        return "google"
    return target
```

Track the chosen platform on the invitation record so post-hoc analysis can identify route-misconfig patterns. The fallback to Google is conservative on purpose — Google reviews always render publicly and don't require a customer account.

### 6. Unified opt-out check (neutralizes compliance gaps)

A customer opting out of any flow — marketing SMS, transactional SMS, review requests, account emails — should suppress every flow that touches them. Implementing per-flow opt-out separately is how merchants accumulate TCPA exposure.

The unified check sits in front of `mark_sent`:

```python
async def is_opted_out(phone_e164: str) -> bool:
    """Returns True if the contact has opted out of ANY flow that suppresses this one."""
    # Source of truth: the merged contact record from podium-contact-dedup.
    contact = await contacts.get_by_phone(phone_e164)
    if contact is None:
        return False
    return any([
        contact.get("marketing_sms_opt_out", False),
        contact.get("review_request_opt_out", False),
        contact.get("global_unsubscribe", False),
        # STOP reply on any prior message — Podium tracks this at the contact level.
        contact.get("podium_keyword_optout", False),
    ])

async def gate_review_request(order: dict) -> bool:
    phone = normalize_e164(order["customer"]["phone"])
    if await is_opted_out(phone):
        log_event("review_send_skipped_optout", order_id=order["id"])
        return False
    allowed, _ = cooldown.can_send(phone)
    if not allowed:
        log_event("review_send_skipped_cooldown", order_id=order["id"])
        return False
    return True
```

Run this exact predicate at both schedule-time and fire-time. A contact who opts out during the 5-day refund buffer must not receive the scheduled send.

## Error Handling

| HTTP / Event | Podium Error | Root Cause | Action |
|---|---|---|---|
| `400 Bad Request` | `invalid_phone` | Phone number is not E.164 or unreachable | Skip — log and continue. Do not retry. |
| `409 Conflict` | `cooldown_violation` | Podium-side cooldown rejected the send | Trust Podium — log and skip. Do not bypass. |
| `429 Too Many Requests` | `rate_limited` | Campaign rate limit hit | Honor `Retry-After`. See `podium-rate-limit-survival`. |
| `review_invitation.failed` (webhook) | `carrier_filtered` | Carrier (T-Mobile/Verizon) rejected the SMS | Roll back cooldown; flag the phone for manual review. |
| `review_invitation.failed` (webhook) | `recipient_optout` | Customer replied STOP to a prior message | Mark `podium_keyword_optout=true` on the contact, propagate to opt-out source-of-truth. |
| `review.received` (webhook) | N/A | Customer left a review | Verify signature → classify sentiment → route. |
| Signature mismatch | N/A | Webhook signature verification failed | Return 401; do not process. Page on persistent mismatches (possible secret rotation drift). |

## Examples

### Schedule a review request from a Shopify `orders/fulfilled` webhook

```python
async def shopify_fulfilled_handler(req) -> tuple[int, str]:
    body = await req.body()
    if not verify_shopify_hmac(body, req.headers.get("X-Shopify-Hmac-Sha256", "")):
        return 401, "bad hmac"

    order = json.loads(body)
    phone = normalize_e164(order["customer"]["phone"])
    if not await gate_review_request(order):
        return 200, "skipped"

    send_after = time.time() + REFUND_BUFFER_DAYS * 86400
    await schedule_review_request(order, send_after)
    return 200, "scheduled"
```

### Cooldown lookup from the CLI

```bash
python3 scripts/cooldown_check.py --phone "+61412345678" --redis-url "$REDIS_URL"
```

Output:

```json
{
  "phone": "+61412345678",
  "last_contact_at": 1714752000.0,
  "cooldown_days_remaining": 23.4,
  "can_send": false
}
```

### Run the opt-out compliance audit for a contact

```bash
python3 scripts/optout_compliance_audit.py --phone "+61412345678"
```

Output:

```json
{
  "phone": "+61412345678",
  "marketing_sms_opt_out": true,
  "review_request_opt_out": false,
  "global_unsubscribe": false,
  "podium_keyword_optout": false,
  "suppressed": true,
  "drift_detected": true,
  "drift_reason": "review_request_opt_out=false despite marketing_sms_opt_out=true — propagate via podium-contact-dedup"
}
```

### Run the Shopify → Podium bridge locally for end-to-end testing

```bash
python3 scripts/shopify_to_podium_bridge.py \
  --port 8787 \
  --shopify-webhook-secret-env SHOPIFY_WEBHOOK_SECRET \
  --podium-campaign-id "{your-podium-campaign-id}" \
  --redis-url "$REDIS_URL" \
  --cooldown-days 30 \
  --refund-buffer-days 5
```

The bridge listens on `:8787/shopify/orders-fulfilled` and `:8787/podium/review-received`. Both endpoints verify their respective signatures before processing.

## Output

- Cooldown gate (Redis-backed) with phone-keyed `last_contact_at` and SETEX-driven expiry
- Refund-race buffer with delayed-queue send + at-fire refund-status re-check
- Failed-send outbox tracking `sent → delivered | failed` with cooldown rollback on failure
- Idempotent `review.received` webhook handler with sentiment classification
- Multi-platform routing selector with Google-fallback for unknown-platform customers
- Unified opt-out predicate consulted at both schedule-time and fire-time

## Resources

- [Podium API docs — Review Invitations](https://docs.podium.com/reference/review-invitations)
- [Podium webhooks — review.received, review_invitation.*](https://docs.podium.com/reference/webhooks)
- [Shopify webhooks — orders/fulfilled](https://shopify.dev/docs/api/admin-rest/2024-04/resources/webhook)
- [config/settings.yaml](config/settings.yaml) — cooldown window, refund-buffer days, platform-preference rules
- [references/errors.md](references/errors.md) — ERR_REVIEW_* codes with cause + solution
- [references/examples.md](references/examples.md) — 10 worked examples (single-merchant, multi-platform, opt-out propagation)
- [references/implementation.md](references/implementation.md) — SQLite cooldown backend, durable-queue options, sentiment classifier, Node.js port
- [scripts/shopify_to_podium_bridge.py](scripts/shopify_to_podium_bridge.py) — webhook listener with cooldown + opt-out gates
- [scripts/cooldown_check.py](scripts/cooldown_check.py) — CLI: query a phone's cooldown state
- [scripts/review_response_handler.py](scripts/review_response_handler.py) — CLI: replay-process a stored `review.received` event
- [scripts/optout_compliance_audit.py](scripts/optout_compliance_audit.py) — CLI: cross-flow opt-out drift detection
