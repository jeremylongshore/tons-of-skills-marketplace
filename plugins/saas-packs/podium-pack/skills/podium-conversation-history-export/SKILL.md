---
name: podium-conversation-history-export
description: Bulk-export Podium conversation, review, and contact history into a vector-store-ready
  corpus with cursor-paginated full crawls, CDC via updated_at watermarks, attachment URL refresh
  on expiry, windowed semantic chunking, and PII redaction before embedding. Use when standing up
  a RAG pipeline on a Podium org, building nightly incremental syncs, or hardening export jobs
  against attachment expiry. Trigger with "podium history export", "podium rag corpus", "podium
  cdc sync", "podium incremental export", "podium chunk for embedding".
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(jq:*), Bash(python3:*), Bash(sqlite3:*), Bash(gzip:*), Grep
version: 2.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
compatibility: Designed for Claude Code
tags:
  - podium
  - data-export
  - cdc
  - rag-pipeline
  - chunking
  - pii-redaction
---

# Podium Conversation History Export

## Overview

Bulk-export a Podium organization's historical conversations, reviews, and contacts into a corpus suitable for embedding into a vector store. This is the skill you run when the customer says "we have two years of knowledge in there" and the AI team wants every thread, every review, every contact note searchable by similarity. It is not a one-shot script — it is the full-export-plus-incremental-CDC pipeline that ingests the historical backlog once and then keeps the corpus current via nightly `updated_at` watermark passes.

The six production failures this skill prevents:

1. **Cursor pagination drift** — Podium's `next_cursor` is server-side state derived from a sort key plus a position. If a conversation is created, updated, or deleted mid-export, naive cursor walks duplicate records (an updated row reappears at the new position) or skip records (a row deleted between pages shifts the cursor's anchor). A correct walk pins the sort to a stable monotonic field and dedups on `id`.
2. **Incremental CDC gaps via the updated_at watermark** — naive `updated_at > $watermark` queries miss writes that happen at exactly the watermark second. Two writes within the same second on opposite sides of the boundary produce a permanent hole. Correct CDC uses `>=` with explicit overlap margin and dedups in the loader on `(id, updated_at)`.
3. **Attachment URL expiry mid-download** — Podium attachment URLs are pre-signed S3-style URLs that expire on the order of 15 minutes. A bulk exporter that takes an hour will get `403 SignatureDoesNotMatch` on every attachment whose URL was issued in the first quarter of the run. Correct downloaders detect the 403, fetch a fresh signed URL by `attachment_id`, and resume.
4. **Oversized thread chunking failures** — a 4000-message conversation thread (a long-running concierge thread for a high-touch RV dealer customer) blows the typical 8K-token embedding budget if naively concatenated. Chunking must be windowed with semantic boundaries (turn boundaries, day boundaries, idle gaps) and emit overlapping chunks for cross-window retrieval.
5. **PII not redacted before embedding** — vector stores are effectively eternal; once a customer's SSN, credit-card number, or address is embedded it cannot be unembedded without recomputing the index. Redact at chunk-emit time with the same PII pattern set used by `podium-call-transcript-pipeline`, before any vector is computed.
6. **Export OOM on long threads** — naively loading all messages of a 4000-message thread into memory before chunking blows the heap on the host running the export. Correct exports stream message-by-message into JSONL, then a separate pass streams JSONL into chunks. Memory cost stays O(window-size), not O(thread-size).

## Prerequisites

- Python 3.10+
- `podium-auth` (this skill assumes a `PodiumAuth` instance is available; do not re-implement OAuth here)
- `podium-rate-limit-survival` (this skill assumes the calling layer obeys per-endpoint quotas — bulk export is the most rate-limit-aggressive workload in the pack)
- A persistent CDC watermark store — SQLite is the default; `cdc_watermark.py` ships with it
- Local disk for streaming JSONL output, gzip-compressed (typical 2-year org: ~1–10 GB raw, 200 MB–2 GB gzipped)
- An attachment-download target directory (S3 bucket, GCS bucket, or local path)
- The PII redaction pattern set from `podium-call-transcript-pipeline` (reused; do not fork)

## Authentication

This skill does NOT implement OAuth. All HTTP calls flow through a `podium_get()` injected dependency that holds a `PodiumAuth` instance from the `podium-auth` skill — that layer handles token caching, 80%-TTL refresh, single-flight locks, and scope validation. Bootstrap by `Read`-ing your refresh-token file, instantiate `PodiumAuth(client_id, client_secret, refresh_token)`, then pass the instance to every export script via `--refresh-token-file` and the env-var credential flags. The five scripts in this skill never construct credentials in-process; they delegate.

If you need to harden the auth path itself (rotation, decay monitoring, multi-tenant routing), `Read` `podium-auth/SKILL.md` and stack that skill on top — this skill is the bulk-data layer, not the auth layer.

## Instructions

Step 1 → Step 6 below. Build in this order. Each step neutralizes one of the six production failure modes from the Overview, in the same order.

### Step 1. Cursor-paginated full crawl (neutralizes cursor drift)

Pin the sort to a stable monotonic field (`created_at` ascending) and dedup on `id` in the loader. Persist the cursor after every successful page so a crash mid-walk resumes at the last successful page boundary, not at the start.

```python
import asyncio, json, time
from pathlib import Path
from typing import AsyncIterator

CURSOR_PATH = Path("./.cursor.conversations.json")
PAGE_SIZE = 100   # Podium documents 100 as the max; do not exceed

async def crawl_conversations(podium_get, location_uid: str) -> AsyncIterator[dict]:
    """Yield conversations in created_at-ascending order. Resumable across crashes."""
    state = json.loads(CURSOR_PATH.read_text()) if CURSOR_PATH.exists() else {}
    cursor = state.get("cursor")
    seen_ids = set(state.get("seen_ids", []))   # bounded; trim periodically

    while True:
        params = {
            "location_uid": location_uid,
            "sort": "created_at:asc",
            "limit": PAGE_SIZE,
        }
        if cursor:
            params["cursor"] = cursor

        resp = await podium_get("/v4/conversations", params=params)
        body = resp.json()

        page = body.get("data", [])
        for row in page:
            if row["id"] in seen_ids:
                continue                 # dedup against mid-walk updates
            seen_ids.add(row["id"])
            yield row

        cursor = body.get("next_cursor")
        # Persist after EVERY page — crash resume must land on the last good cursor
        CURSOR_PATH.write_text(json.dumps({
            "cursor": cursor,
            "seen_ids": list(seen_ids)[-50_000:],   # keep last 50k ids only
            "updated_at": time.time(),
        }))

        if not cursor:
            return
```

The `seen_ids` set is bounded at 50k to prevent unbounded memory growth on a multi-million-row export. Tune the cap to roughly 5× `PAGE_SIZE × pages_in_one_hour` — large enough to dedup any reasonable update churn within the page-write window, small enough to fit in memory.

### Step 2. Incremental CDC via overlap-margin watermark (neutralizes boundary gaps)

A naive `updated_at > $watermark` query misses any row whose `updated_at` is exactly the watermark second. Use `>=` and dedup in the loader; advance the watermark only after the page is fully persisted.

```python
import sqlite3, time, json

WATERMARK_DB = "./watermarks.sqlite"

def get_watermark(resource: str) -> float:
    con = sqlite3.connect(WATERMARK_DB)
    cur = con.execute("SELECT watermark FROM cdc WHERE resource = ?", (resource,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else 0.0

def advance_watermark(resource: str, new_watermark: float) -> None:
    con = sqlite3.connect(WATERMARK_DB)
    con.execute("""
        INSERT INTO cdc(resource, watermark, updated_at) VALUES(?, ?, ?)
        ON CONFLICT(resource) DO UPDATE SET watermark = excluded.watermark, updated_at = excluded.updated_at
    """, (resource, new_watermark, time.time()))
    con.commit()
    con.close()

async def incremental_pull(podium_get, resource: str, overlap_margin_s: int = 60):
    """Pull rows with updated_at >= (watermark - overlap_margin) and dedup."""
    watermark = get_watermark(resource)
    since = max(0, watermark - overlap_margin_s)        # explicit overlap

    cursor = None
    max_seen = watermark
    seen_keys = set()

    while True:
        params = {"updated_since": since, "sort": "updated_at:asc", "limit": 100}
        if cursor:
            params["cursor"] = cursor
        body = (await podium_get(f"/v4/{resource}", params=params)).json()

        for row in body.get("data", []):
            key = (row["id"], row["updated_at"])
            if key in seen_keys:
                continue
            seen_keys.add(key)
            yield row
            max_seen = max(max_seen, row["updated_at"])

        cursor = body.get("next_cursor")
        if not cursor:
            break

    # Advance watermark only after the full pass succeeds, not per-page —
    # a partial pass must re-pull from the previous watermark on retry.
    advance_watermark(resource, max_seen)
```

The `overlap_margin_s = 60` is intentional. Podium's `updated_at` granularity is one second; a 60s overlap absorbs clock-skew and same-second writes without producing useful duplicate volume.

### Step 3. Attachment download with refresh-on-403 (neutralizes pre-signed URL expiry)

Podium attachment URLs are pre-signed and expire ~15 minutes after they appear in the conversation payload. A multi-hour bulk export must re-fetch the signed URL by attachment ID when a download returns 403.

```python
import asyncio, httpx
from pathlib import Path

async def download_attachment(podium_get, attachment_id: str, signed_url: str, dest: Path) -> None:
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.get(signed_url)
        if r.status_code == 403:
            # URL expired — fetch a fresh one
            fresh = (await podium_get(f"/v4/attachments/{attachment_id}")).json()
            signed_url = fresh["url"]
            r = await c.get(signed_url)
        r.raise_for_status()
        dest.write_bytes(r.content)

async def parallel_download(podium_get, attachments: list[dict], out_dir: Path, concurrency: int = 8) -> None:
    sem = asyncio.Semaphore(concurrency)
    async def _one(att):
        async with sem:
            dest = out_dir / f"{att['id']}{att.get('ext', '')}"
            await download_attachment(podium_get, att["id"], att["url"], dest)
    await asyncio.gather(*[_one(a) for a in attachments])
```

`concurrency=8` is the safe default — Podium documents per-org rate limits, and the attachments are served from a CDN that tolerates moderate parallelism. Raise only after observing the integration's headroom against the rate-limit-survival skill's metrics.

### Step 4. Windowed thread chunking with semantic boundaries (neutralizes oversized threads)

A long thread must chunk on natural boundaries — turn boundaries inside a conversation, idle gaps > 24h, and a hard cap on tokens per chunk. The chunker streams the JSONL export, never holding more than `window_size` messages in memory.

```python
def chunk_thread(messages: list[dict], target_tokens: int = 1500, overlap_tokens: int = 200):
    """Yield chunks of ~target_tokens with overlap, breaking on idle gaps > 24h."""
    chunks = []
    current: list[dict] = []
    current_tokens = 0

    for i, msg in enumerate(messages):
        msg_tokens = approx_tokens(msg["body"])
        idle_gap = 0
        if i > 0:
            idle_gap = msg["created_at"] - messages[i-1]["created_at"]

        # Force-break on >24h idle OR token cap
        if current_tokens + msg_tokens > target_tokens or idle_gap > 86400:
            if current:
                chunks.append(_emit_chunk(current))
                # Overlap: carry last ~overlap_tokens of messages into next chunk
                carry = []
                carry_tokens = 0
                for m in reversed(current):
                    t = approx_tokens(m["body"])
                    if carry_tokens + t > overlap_tokens:
                        break
                    carry.insert(0, m)
                    carry_tokens += t
                current = carry
                current_tokens = carry_tokens
        current.append(msg)
        current_tokens += msg_tokens

    if current:
        chunks.append(_emit_chunk(current))
    return chunks

def approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)   # OpenAI rule of thumb; replace with tiktoken in prod
```

The 24-hour idle-gap break is critical for support-style threads where a single thread spans months — without it, the semantic context of a chunk is incoherent (a Q1 issue and a Q4 follow-up share an embedding).

### Step 5. PII redaction before embedding (neutralizes eternal-PII compliance failure)

Run the same redaction pattern set as `podium-call-transcript-pipeline` at chunk-emit time, before any text leaves the export process toward the embedding API. Redactions are non-recoverable — that is the point.

```python
import re

PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    (re.compile(r"\b(?:\d[ -]*?){13,16}\b"), "[REDACTED_CARD]"),
    (re.compile(r"\b[A-Z]{1,2}\d{6,9}\b"), "[REDACTED_LICENSE]"),
    (re.compile(r"\b\d{1,5} [\w ]{1,40}(?:Street|St|Ave|Avenue|Rd|Road|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct)\b", re.I), "[REDACTED_ADDR]"),
    (re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"), "[REDACTED_EMAIL]"),
    (re.compile(r"\+?\d{1,3}[ -.]?\(?\d{3}\)?[ -.]?\d{3}[ -.]?\d{4}"), "[REDACTED_PHONE]"),
]

def redact(text: str) -> str:
    for pat, repl in PII_PATTERNS:
        text = pat.sub(repl, text)
    return text
```

Run redaction on the chunk body, the customer-facing display name in any quoted message, and the attachment filename if it is reproduced in the chunk. **Do not** redact the message `id` or `created_at` — those are non-PII and necessary for retrieval traceability.

### Step 6. Streaming JSONL output (neutralizes export OOM)

Stream one record per line, gzip-compressed, with no in-memory aggregation. The chunker reads JSONL line-by-line and emits chunks; the embedder reads chunks line-by-line and emits vectors. Memory cost is O(one record) at every stage.

```python
import gzip, json
from pathlib import Path

async def stream_export(rows_iter, out_path: Path) -> int:
    """Write rows to a gzip-compressed JSONL file, one record per line."""
    count = 0
    with gzip.open(out_path, "wt", encoding="utf-8") as f:
        async for row in rows_iter:
            f.write(json.dumps(row, separators=(",", ":")))
            f.write("\n")
            count += 1
            if count % 1000 == 0:
                f.flush()   # bound data loss on crash
    return count
```

`separators=(",", ":")` saves ~5% on disk; `f.flush()` every 1000 rows bounds the data-loss window on a crash to one flush interval.

## Error Handling

| HTTP Status | Podium Error | Root Cause | Action |
|---|---|---|---|
| `403 Forbidden` | `SignatureDoesNotMatch` (attachment) | Pre-signed URL expired | Re-fetch via `GET /v4/attachments/:attachment_id`, retry once |
| `404 Not Found` | `conversation_not_found` | Conversation deleted mid-export | Skip; log the id; do not retry |
| `409 Conflict` | `cursor_invalid` | Cursor from a previous export run is no longer valid | Drop cursor; restart from current watermark |
| `429 Too Many Requests` | `rate_limited` | Page rate exceeded org quota | Honor `Retry-After`; delegate to `podium-rate-limit-survival` |
| `500/502/503` | `server_error` | Podium-side transient | Exponential backoff with jitter, max 4 attempts |
| `(local)` | `watermark_drift` | CDC watermark advanced past max_seen on a partial run | Reset to last good watermark via `cdc_watermark.py --reset` |

## Examples

### Full historical export (one-shot)

```bash
python3 scripts/export_conversations.py \
  --location-uid "{your-location-uid}" \
  --mode full \
  --out ./exports/conversations.jsonl.gz \
  --attachments-dir ./exports/attachments
```

### Incremental nightly sync

```bash
# Run nightly via cron. Watermark advances after success; partial runs re-pull.
python3 scripts/export_conversations.py \
  --location-uid "{your-location-uid}" \
  --mode incremental \
  --watermark-db ./watermarks.sqlite \
  --overlap-margin-seconds 60 \
  --out ./exports/conversations.$(date +%F).jsonl.gz
```

### Inspect / reset / advance the CDC watermark

```bash
# Inspect
python3 scripts/cdc_watermark.py --resource conversations --db ./watermarks.sqlite

# Reset (re-pull everything from epoch)
python3 scripts/cdc_watermark.py --resource conversations --db ./watermarks.sqlite --reset

# Advance manually (e.g., after a manual backfill via another tool)
python3 scripts/cdc_watermark.py --resource conversations --db ./watermarks.sqlite --advance 1715212800
```

### Chunk an export for embedding

```bash
python3 scripts/chunk_for_embedding.py \
  --input ./exports/conversations.jsonl.gz \
  --output ./exports/chunks.jsonl.gz \
  --target-tokens 1500 \
  --overlap-tokens 200 \
  --redact-pii
```

Output is JSONL where each line is a chunk: `{chunk_id, source_id, source_type, created_at_window, body, token_estimate, pii_redacted: true}`. Pipe directly into your vector-store loader.

### Parallel attachment download with refresh-on-403

```bash
python3 scripts/attachment_downloader.py \
  --input ./exports/conversations.jsonl.gz \
  --out-dir ./exports/attachments \
  --concurrency 8 \
  --refresh-on-403
```

## Output

- Streaming gzip-compressed JSONL export of conversations, reviews, contacts
- CDC watermark SQLite store with `cdc_watermark.py` inspector
- Attachment directory with all attachments downloaded, retried-on-403
- Chunked JSONL with PII redacted, ready for vector-store ingestion
- Cursor checkpoint files (resumable across crashes)

## Resources

- [Podium API docs — Conversations](https://docs.podium.com/reference/list-conversations)
- [Podium API docs — Reviews](https://docs.podium.com/reference/list-reviews)
- [Podium API docs — Contacts](https://docs.podium.com/reference/list-contacts)
- [Podium API docs — Attachments](https://docs.podium.com/reference/get-attachment)
- [config/settings.yaml](config/settings.yaml) — page size, overlap margin, concurrency, chunking thresholds
- [references/errors.md](references/errors.md) — ERR_EXPORT_* codes with cause + solution
- [references/examples.md](references/examples.md) — 10 worked examples (full crawl, incremental, chunk, redact, route to pgvector/Qdrant/Weaviate)
- [references/implementation.md](references/implementation.md) — Node.js equivalents, vector-store-specific loaders, chunk sizing math
- [scripts/export_conversations.py](scripts/export_conversations.py) — CLI: full or incremental conversation export
- [scripts/export_reviews.py](scripts/export_reviews.py) — CLI: full or incremental review export
- [scripts/cdc_watermark.py](scripts/cdc_watermark.py) — CLI: inspect / reset / advance the CDC watermark
- [scripts/attachment_downloader.py](scripts/attachment_downloader.py) — CLI: parallel download with refresh-on-403
- [scripts/chunk_for_embedding.py](scripts/chunk_for_embedding.py) — CLI: chunk JSONL with PII redaction
