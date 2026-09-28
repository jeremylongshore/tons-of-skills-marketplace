---
name: podium-contact-dedup
description: Deduplicate Podium contacts in production and survive the data-quality failures —
  phone-format inconsistency producing four contacts for one phone, merge-api ordering that
  silently discards the richer record, opt-out flags lost on merge re-enabling marketing on
  an opted-out person, soft-delete confusion, cross-location duplicate blind spots, and
  simultaneous-merge race conditions. Use when you build a Podium dedup pipeline, scan and
  detect duplicate clusters, normalize phones to e164 form across an entire contact corpus,
  preserve opt-out state through merges, or validate cross-location duplicate resolution.
  Trigger with "podium contact dedup", "podium phone normalization", "podium e164",
  "podium duplicate contacts", "podium merge contacts", "podium opt-out preservation",
  "podium cross-location dedup".
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(jq:*), Bash(python3:*), Bash(sqlite3:*), Grep
version: 2.10.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
compatibility: Designed for Claude Code
tags:
  - podium
  - contact-dedup
  - e164-normalization
  - data-quality
  - opt-out-preservation
  - merge-orchestration
---

# Podium Contact Dedup

## Overview

Deduplicate Podium contacts in production and operate the dedup pipeline at scale. This is not a one-shot cleanup script — it is the data-quality layer your integration runs continuously to keep the contact corpus sane while messages, calls, webchats, and reviews keep mutating it. Run it once and Sydney's "0412 345 678" walk-in stops creating a fifth contact next to the four that already exist as `+61 412 345 678`, `(04) 1234-5678`, `+61412345678`, and `0412345678`.

The six production failures this skill prevents:

1. **Phone format inconsistency** — `+61 412 345 678`, `0412 345 678`, `(04) 1234-5678`, `+61412345678` are all the same phone but produce four contacts. Operators paste numbers from a CRM, a phone screen, a written form, and a stored fragment; Podium dedups on exact string match, so all four survive and the next caller appears as a fifth.
2. **Merge API ordering loses fields** — Podium's merge endpoint takes a `primary` and a `duplicate`; whichever you pick as `primary` keeps its own fields, the other's fields are discarded. Pick the wrong record (newer but emptier) as primary and the older, richer record's name, tags, and conversation links vanish silently.
3. **Opt-out flag lost on merge** — duplicate had `marketing_opt_out=true`, primary had `marketing_opt_out=false`; naive merge keeps primary's flag and re-enables marketing on a person who explicitly opted out. This is a compliance incident (TCPA, GDPR Article 21, ACMA Spam Act) and a trust incident — the customer opted out, you marketed at them anyway.
4. **Soft-delete vs hard-delete semantic confusion** — Podium's `DELETE /contacts/{uid}` is reversible; the record is hidden, not destroyed. Treat it as terminal and you ship a "contact reappeared after we deleted them" support ticket every time an admin restores a contact via the UI. Hard-delete (purge) is a separate, irreversible endpoint with different scopes.
5. **Duplicate detection across locations** — same phone calls Sydney AND Burleigh Heads, two contacts created (one per location), per-location dedup misses it entirely. Cross-location dedup needs a separate routine keyed by `phone_natural_key` across the union of contacts in every location_uid, not just within one.
6. **Merge conflicts on simultaneous edits** — two operators (or one operator + one automated job) merge overlapping clusters at the same time; the second merge's `primary` may have already been merged into another record, the API silently merges into a now-stale target, and one operator's intent is dropped without surfacing the conflict.

## Prerequisites

- Python 3.10+ with the `phonenumbers` library (`pip install phonenumbers`)
- A working `podium-auth` integration (this skill calls Podium with an authenticated client)
- Read scope: `contacts.read`. Write scope: `contacts.write`. (`contacts.delete` only if hard-purge is in scope.)
- A local SQLite database for the natural-key index and merge state file (default `./podium-dedup.sqlite`)
- A default region for E.164 parsing (`AU` for Australian deployments, `US` for US — set per-tenant)

## Instructions

Build in this order. Each section neutralizes one production failure mode.

### 1. E.164 normalization with natural-key emission (neutralizes phone-format inconsistency)

Every contact's phone is parsed by the `phonenumbers` library into E.164 form, then hashed into a stable "natural key" suitable for an index lookup. Same human-readable phone → same key, regardless of formatting input.

```python
import phonenumbers
from phonenumbers import NumberParseException

def normalize_phone(raw: str, default_region: str = "AU") -> dict:
    """Return {e164, national, country, natural_key, valid} for any input format."""
    try:
        parsed = phonenumbers.parse(raw, default_region)
    except NumberParseException as e:
        return {"valid": False, "reason": f"parse_failed: {e}"}
    if not phonenumbers.is_valid_number(parsed):
        return {"valid": False, "reason": "not_a_valid_number"}
    e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
    return {
        "valid": True,
        "e164": e164,                         # +61412345678
        "national": national,                 # 0412 345 678
        "country": phonenumbers.region_code_for_number(parsed),
        "natural_key": e164,                  # the E.164 IS the natural key — no further hashing needed
    }
```

The natural key is the E.164 string itself. Hashing it adds nothing — E.164 is already canonical and bounded in length. Use the E.164 directly as the SQLite primary key on the natural-key index.

### 2. SQLite-backed natural-key index (neutralizes O(N²) duplicate scans)

A naive dedup scans every pair of contacts — O(N²) on a 50k-contact corpus is hours. Instead, build a `(natural_key → [contact_uid, ...])` index in SQLite once, then duplicate detection is O(N) over the index.

```sql
CREATE TABLE IF NOT EXISTS contact_index (
    contact_uid    TEXT PRIMARY KEY,
    location_uid   TEXT NOT NULL,
    natural_key    TEXT NOT NULL,   -- E.164
    raw_phone      TEXT,
    name           TEXT,
    field_count    INTEGER NOT NULL DEFAULT 0,
    marketing_opt_out  INTEGER NOT NULL DEFAULT 0,
    sms_opt_out        INTEGER NOT NULL DEFAULT 0,
    email_opt_out      INTEGER NOT NULL DEFAULT 0,
    deleted_at_podium  TEXT,        -- ISO8601, NULL if live
    updated_at_podium  TEXT NOT NULL,
    indexed_at         TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_natural_key ON contact_index(natural_key);
CREATE INDEX IF NOT EXISTS idx_natural_key_per_location ON contact_index(natural_key, location_uid);
```

The `field_count` column is precomputed at index time so the merge orchestrator picks the richer record as `primary` without re-fetching every record.

### 3. Duplicate detection with confidence scoring (neutralizes blind merges)

A cluster is a set of contacts sharing the same `natural_key`. Within a cluster, each pair gets a confidence score in `[0.0, 1.0]`:

| Factor | Weight |
|---|---|
| Same E.164 (always true within a cluster) | 0.60 — required floor |
| Same name (case-insensitive, normalized) | +0.20 |
| Same email | +0.15 |
| Overlapping tags | +0.05 |

Only clusters with all pairwise scores `>= 0.80` auto-merge by default. Lower-scored clusters surface for human review.

```python
def cluster_confidence(a: dict, b: dict) -> float:
    score = 0.60   # same natural_key by construction
    if a.get("name") and a["name"].strip().lower() == (b.get("name") or "").strip().lower():
        score += 0.20
    if a.get("email") and a["email"].strip().lower() == (b.get("email") or "").strip().lower():
        score += 0.15
    a_tags, b_tags = set(a.get("tags") or []), set(b.get("tags") or [])
    if a_tags & b_tags:
        score += 0.05
    return round(min(score, 1.0), 4)
```

### 4. Merge orchestrator with primary selection (neutralizes lost richer record)

For each auto-mergeable cluster, pick the `primary` by this deterministic rule, in order:

1. **Most fields populated** (highest `field_count`) — the richer record wins.
2. **Most recently updated** (`updated_at_podium`) — break ties toward fresher state.
3. **Lowest contact_uid** (lexical) — final, deterministic, reproducible tiebreak.

Every other contact in the cluster is a `duplicate` to be merged INTO the primary. Never trust caller-supplied ordering — always compute primary inside the orchestrator.

```python
def select_primary(cluster: list[dict]) -> dict:
    return max(
        cluster,
        key=lambda c: (c["field_count"], c["updated_at_podium"], -ord_key(c["contact_uid"]))
    )

def ord_key(uid: str) -> int:
    # Stable, deterministic tiebreak — lower uid sorts first
    return sum(ord(c) for c in uid)
```

### 5. Opt-out preservation by union (neutralizes compliance re-enable)

The strongest setting wins, always. If any record in the cluster has `marketing_opt_out=true`, the merged record has `marketing_opt_out=true`. Same for `sms_opt_out` and `email_opt_out`. This rule is non-negotiable and is the reason every cluster's opt-out state is computed BEFORE the merge API call, then forced via `PATCH /contacts/{primary_uid}` immediately after the merge completes.

```python
def union_opt_outs(cluster: list[dict]) -> dict:
    return {
        "marketing_opt_out": any(c.get("marketing_opt_out") for c in cluster),
        "sms_opt_out":       any(c.get("sms_opt_out") for c in cluster),
        "email_opt_out":     any(c.get("email_opt_out") for c in cluster),
    }
```

The merge-then-patch sequence:

1. Compute `opt_outs = union_opt_outs(cluster)` BEFORE any API call.
2. Call Podium merge API: `POST /contacts/{primary_uid}/merge` with `{"duplicate_uids": [...]}`.
3. Immediately `PATCH /contacts/{primary_uid}` with `opt_outs` to overwrite whatever Podium's merge left there.

Do not rely on Podium's merge to preserve opt-outs. The PATCH is the canonical source of truth for the final state.

### 6. Soft-delete vs hard-delete handling (neutralizes "contact reappeared")

Podium's `DELETE /contacts/{uid}` is **soft delete** — the record sets `deleted_at` and disappears from default list endpoints but remains restorable via the Podium UI. Treat it as a state change, not a destruction.

The dedup pipeline never hard-deletes. It always:

1. Calls `POST /contacts/{primary_uid}/merge` — Podium soft-deletes the duplicates and links their conversation history to the primary.
2. Records the operation in the local audit log with `operation=merge, soft_delete=true, restorable=true`.
3. If a human admin restores a soft-deleted duplicate via the Podium UI, the next dedup run sees it again and re-merges it. This is by design — the audit log surfaces the loop so a human can decide whether the restore was intentional.

Hard-delete (`/contacts/{uid}?hard=true` — separate scope, separate endpoint) is reserved for compliance erasure requests (GDPR right-to-be-forgotten, CCPA delete request) and runs through a different skill, not this one.

### 7. Cross-location dedup (neutralizes the Sydney + Burleigh Heads case)

Per-location dedup misses the case where the same phone exists as two separate contacts in two different locations. The cross-location scan runs after per-location dedup completes:

```python
def cross_location_clusters(db) -> list[list[dict]]:
    """Return clusters of contacts sharing a natural_key across DIFFERENT location_uids."""
    rows = db.execute("""
        SELECT natural_key, contact_uid, location_uid, field_count, updated_at_podium
        FROM contact_index
        WHERE deleted_at_podium IS NULL
        GROUP BY natural_key
        HAVING COUNT(DISTINCT location_uid) > 1
    """).fetchall()
    # ... assemble per-key cluster
```

Cross-location merges have a different policy: by default they DO NOT auto-merge, because a person may legitimately be a customer of two separate franchises. They surface for human review with both location names attached. The auto-merge threshold can be raised per-deployment when the operator confirms locations represent the same business entity (e.g., two co-located retail floors).

### 8. Idempotent merge with state file (neutralizes mid-run crash)

Every cluster operation is recorded in `merge_state` BEFORE the API call and confirmed AFTER. A crash mid-merge leaves a `pending` row; the next run sees it, queries Podium for the current state of the primary, and either confirms `done` or retries.

```sql
CREATE TABLE IF NOT EXISTS merge_state (
    cluster_id        TEXT PRIMARY KEY,    -- hash of sorted contact_uids
    natural_key       TEXT NOT NULL,
    primary_uid       TEXT NOT NULL,
    duplicate_uids    TEXT NOT NULL,       -- JSON array
    status            TEXT NOT NULL,       -- pending | merging | merged | patched | failed
    attempts          INTEGER NOT NULL DEFAULT 0,
    last_error        TEXT,
    started_at        TEXT NOT NULL,
    completed_at      TEXT
);
```

State transitions: `pending → merging → merged → patched`. Only `patched` is terminal-success. A run resumes from any non-terminal state by re-checking the primary in Podium.

### 9. Conflict detection on simultaneous edits (neutralizes the race)

Before each merge API call, the orchestrator re-fetches each duplicate and verifies `updated_at_podium` matches the indexed value. If a duplicate has been updated since the index was built (another operator merged it into a different record, an admin edited it, an inbound message arrived), the orchestrator:

1. Aborts the merge for this cluster.
2. Logs `conflict_detected` to the audit log with the stale `indexed_updated_at` vs the current `live_updated_at`.
3. Marks the cluster `re_index_required` — the next run rebuilds the index for this `natural_key` and re-evaluates.

This is fail-stop, not fail-silent. A simultaneous-merge race surfaces in the audit log, not in the customer's marketing inbox.

## Error Handling

Troubleshoot failures using the table below — each row maps a wire-level symptom to the root cause and the action. For deeper debug, the `audit-log.jsonl` records every cluster's pre- and post-merge state, and the `merge_state` SQLite table is the resumable source of truth for any in-flight operation.

| HTTP Status | Podium Error | Root Cause | Action |
|---|---|---|---|
| `400 Bad Request` | `invalid_duplicate_uid` | A duplicate_uid does not exist or already soft-deleted | Re-fetch and re-evaluate cluster — duplicate may have been merged elsewhere |
| `404 Not Found` | `contact_not_found` | Primary uid no longer exists (hard-deleted between index and merge) | Skip cluster; the data is gone, no recovery needed |
| `409 Conflict` | `merge_in_progress` | Another merge is already operating on one of these contacts | Wait with exponential backoff; another orchestrator instance is mid-merge |
| `422 Unprocessable` | `cross_location_merge_blocked` | Primary and duplicate are in different location_uids and tenant policy forbids | Surface to human review queue; do not retry |
| `429 Too Many Requests` | `rate_limited` | Burst merge load tripped Podium's per-tenant limit | Honor `Retry-After`; downstream skill is `podium-rate-limit-survival` |
| `500/502/503` | `server_error` | Podium-side transient | Exponential backoff with jitter, max 4 attempts; keep cluster `pending` |

## Examples

### Normalize a single phone number from CLI

```bash
python3 scripts/phone_normalize.py --phone "0412 345 678" --region AU --output json
```

Output:

```json
{
  "valid": true,
  "e164": "+61412345678",
  "national": "0412 345 678",
  "country": "AU",
  "natural_key": "+61412345678"
}
```

### Build the natural-key index and find duplicate clusters

```bash
# 1. Pull all contacts from a location and populate the SQLite index
python3 scripts/find_duplicates.py \
  --location-uid loc_abc123 \
  --db ./podium-dedup.sqlite \
  --token-env PODIUM_ACCESS_TOKEN \
  --output json

# Output: clusters of length >= 2, each with confidence score and suggested primary
```

### Dry-run a merge of one cluster

```bash
python3 scripts/merge_contacts.py \
  --cluster-id cl_7f3a... \
  --db ./podium-dedup.sqlite \
  --token-env PODIUM_ACCESS_TOKEN \
  --dry-run
```

Dry-run prints the planned operation — `primary_uid`, `duplicate_uids`, `opt_out_union`, and the exact API calls that would fire — without contacting Podium.

### Execute the merge for real

```bash
python3 scripts/merge_contacts.py \
  --cluster-id cl_7f3a... \
  --db ./podium-dedup.sqlite \
  --token-env PODIUM_ACCESS_TOKEN
```

### Scan for cross-location duplicates after per-location runs complete

```bash
python3 scripts/cross_location_dedup.py \
  --db ./podium-dedup.sqlite \
  --output review-queue.json
```

The output is a human-review queue, not an auto-merge plan — cross-location merges require operator confirmation by default.

## Output

- E.164 normalization function with natural-key emission, validated by the `phonenumbers` library
- SQLite-backed natural-key index keyed on `natural_key` and `(natural_key, location_uid)`
- Duplicate detection emitting clusters with confidence scores (0.60 floor, 0.80 auto-merge threshold)
- Merge orchestrator with deterministic primary selection (field_count > updated_at > uid)
- Opt-out preservation via union-then-PATCH after every merge
- Cross-location duplicate scanner producing a human-review queue
- Idempotent merge state file (resumable after crash)
- Conflict detection via `updated_at_podium` re-check before each merge

## Resources

- [Podium API docs — Contacts](https://docs.podium.com/reference/contacts)
- [Podium API docs — Contact merge](https://docs.podium.com/reference/contact-merge)
- [phonenumbers library (Google libphonenumber port)](https://github.com/daviddrysdale/python-phonenumbers)
- [E.164 spec (ITU-T Recommendation E.164)](https://www.itu.int/rec/T-REC-E.164)
- [config/settings.yaml](config/settings.yaml) — region defaults, confidence thresholds, opt-out policy
- [references/errors.md](references/errors.md) — ERR_DEDUP_* codes with cause + solution
- [references/examples.md](references/examples.md) — 10 worked examples (single phone, cluster, cross-location, resume)
- [references/implementation.md](references/implementation.md) — Node port, libphonenumber wiring, audit log schema
- [scripts/phone_normalize.py](scripts/phone_normalize.py) — CLI: normalize a phone to E.164 + natural-key
- [scripts/find_duplicates.py](scripts/find_duplicates.py) — CLI: scan and emit cluster proposals with scores
- [scripts/merge_contacts.py](scripts/merge_contacts.py) — CLI: merge a cluster (primary + dupes) with `--dry-run`
- [scripts/cross_location_dedup.py](scripts/cross_location_dedup.py) — CLI: cross-location scan for human review
