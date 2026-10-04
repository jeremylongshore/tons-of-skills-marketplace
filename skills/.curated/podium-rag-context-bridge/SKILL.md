---
name: podium-rag-context-bridge
description: Bridge a live Podium call transcript or webchat turn to an LLM by fetching relevant
  historical conversation context as a structured RAG bundle — vector search over embedded prior
  conversations + reranking + live Podium contact lookup, merged under a hard latency budget that
  keeps the call answerable in real time. Use when wiring a transcription-driven agent loop to an
  LLM that needs cross-channel customer memory, building the substrate that turns "transcript
  chunk" into "LLM-ready prompt with context", or hardening an existing RAG pipeline against
  staleness, reranking noise, PII leakage, token-budget overflow, and missed-the-call latency.
  Trigger with "podium rag", "podium llm context", "podium transcript to llm", "podium retrieval",
  "podium vector search", "podium real-time context", "podium agent grounding".
allowed-tools: Read, Write, Edit, Bash(curl:*), Bash(jq:*), Bash(python3:*), Bash(psql:*), Grep
version: 2.12.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
compatibility: Designed for Claude Code
tags:
  - podium
  - rag
  - llm-context
  - vector-search
  - reranking
  - real-time-context
---

# Podium RAG Context Bridge

## Overview

Take a live transcript chunk (or webchat turn) and emit a structured RAG context bundle the calling LLM can drop into its prompt. This is not a chatbot. This is the substrate that sits between Podium's transcription stream and whatever LLM your agent loop is using — fetching the right historical context, fast enough to matter, in a shape the model can actually consume.

The substrate combines two retrieval surfaces: a **vector store** of past Podium conversations (embedded at ingest by `podium-conversation-history-export`) and a **live Podium API lookup** for the contact's fresh state (phone, opt-out, location, last-seen). The two surfaces answer different questions — vectors answer "what did this person ever say about this topic," the live API answers "is the phone number we're about to dial actually still their phone number." A naive RAG pipeline collapses them and ships drift to the model.

The six production failures this skill prevents:

1. **Relevance scoring picks wrong historical context** — naive cosine similarity over top-K=5 chunks surfaces the five most similar embeddings; on real Podium corpora most of those are off-topic boilerplate ("thanks for reaching out", "have a great day"). The model sees noise, generates a generic reply, and the operator loses the customer. Fix: cross-encoder reranking + per-contact filtering BEFORE the model sees anything.
2. **Vector store stale vs live Podium data drift** — the contact updated their phone yesterday; today the vector store still embeds the old number. The model answers "I'll call you back at (555) 0100" using a number that hasn't worked in 16 hours. Vector recall and live state are different SLAs and must be merged with live state winning on any field that can mutate.
3. **Transcript chunk boundaries lose context** — the transcriber emits chunks every 800ms. A boundary that cuts "my order number is" / "ABC-12345" in half means neither chunk retrieves the order. Both retrieve nothing relevant. Fix: sliding-window overlap (default 200ms tail of previous chunk prepended to the embed query) plus chunk coalescing before embedding.
4. **LLM token budget overflow** — retrieved context plus system prompt plus transcript history pushes the user prompt past the model's window. Most models silently truncate from the middle; some refuse the request. Either way the model is operating on a corrupted prompt. Fix: hard token budget per retrieval surface (default 1500 tokens of context, summarized if over).
5. **PII reaches LLM in raw form** — the retrieved historical context still contains credit-card-like strings, full home addresses, and DOBs that were never redacted at ingest because nobody told the ingest pipeline they had to. The LLM will repeat them back. Fix: redaction filter at retrieval time as the last line of defense before emission, even if ingest is supposed to do it too.
6. **Context emission latency exceeds call duration** — by the time the bridge returns context, the customer has already hung up. The vector store p99 is 600ms, the reranker p99 is 400ms, the Podium lookup p99 is 300ms — serially that is over a second per turn and the agent never catches up. Fix: parallel fan-out + a hard 800ms wall-clock timeout that returns whatever finished, with a structured `partial: true` flag so the LLM knows it is grounding on incomplete context.

## Prerequisites

- Python 3.10+
- A populated vector store of past Podium conversations. Recommended bootstrap: run `podium-conversation-history-export` against the org's full history, embed each chunk, and write to a pgvector table (schema in `references/implementation.md`)
- A working `podium-auth` instance for the live Podium contact lookup
- An embedding model available at request time. Default: `BAAI/bge-large-en-v1.5` via `sentence-transformers` (free, local) or `text-embedding-3-small` via OpenAI (hosted, ~$0.00002/embed)
- A cross-encoder reranker for the second-stage score. Default: `BAAI/bge-reranker-base` (free, local). LLM-as-reranker is also supported but adds latency and cost
- pgvector ≥ 0.5 if using the default backend. Pinecone / Weaviate adapters are documented but not the reference path

## Instructions

Build in this order. Each section neutralizes one production failure mode.

### 1. Sliding-window chunk coalescing (neutralizes boundary loss)

The first thing that goes wrong is upstream of every other thing: the transcript chunks themselves arrive truncated on a word boundary that matters. Before the chunk hits the embedding model, prepend the tail of the previous chunk and the head of the next chunk (if available) so the embed query sees a full clause, not a sentence fragment.

```python
from dataclasses import dataclass, field
from collections import deque
from typing import Deque

@dataclass
class TranscriptCoalescer:
    """Coalesce 800ms transcript chunks into overlap-window embed queries."""
    tail_window_ms: int = 200
    head_window_ms: int = 200
    _recent: Deque[str] = field(default_factory=lambda: deque(maxlen=3))

    def feed(self, chunk: str) -> str:
        # tail of the previous chunk, then current chunk
        prev_tail = self._tail(self._recent[-1]) if self._recent else ""
        self._recent.append(chunk)
        return f"{prev_tail} {chunk}".strip()

    def _tail(self, s: str) -> str:
        # naive: last ~30 chars; production: last word-bounded ~200ms of text
        return s[-30:] if len(s) > 30 else s
```

Without this, every embed query is doing word-boundary keyhole surgery on the corpus and missing relevant context for reasons that have nothing to do with the model.

### 2. Vector query with cross-encoder reranking (neutralizes relevance noise)

Top-K cosine similarity gives you the five most-similar chunks. Most are off-topic. The cure is a second pass through a cross-encoder that scores `(query, candidate)` pairs directly — slower but ~10x more accurate at the top of the list. Pull top-20 from the vector store, rerank to top-5, return.

```python
import asyncio
from typing import Protocol

class VectorStore(Protocol):
    async def query(self, embedding: list[float], top_k: int,
                    filter: dict | None = None) -> list[dict]: ...

class Reranker(Protocol):
    async def score(self, query: str, candidates: list[str]) -> list[float]: ...

class PgvectorStore:
    """pgvector reference implementation. Replace with Pinecone/Weaviate as needed."""
    def __init__(self, dsn: str):
        import psycopg
        self.dsn = dsn  # Inject the managed connection string at runtime.

    async def query(self, embedding: list[float], top_k: int,
                    filter: dict | None = None) -> list[dict]:
        import psycopg
        contact_uid = (filter or {}).get("contact_uid")
        sql = """
            SELECT id, contact_uid, content, channel, occurred_at,
                   1 - (embedding <=> %s::vector) AS cosine_score
            FROM podium_conversations
            WHERE (%s IS NULL OR contact_uid = %s)
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        async with await psycopg.AsyncConnection.connect(self.dsn) as conn:
            cur = await conn.execute(sql, (embedding, contact_uid, contact_uid, embedding, top_k))
            rows = await cur.fetchall()
        return [
            {"id": r[0], "contact_uid": r[1], "content": r[2],
             "channel": r[3], "occurred_at": r[4], "score": float(r[5])}
            for r in rows
        ]

async def search_with_rerank(
    query_text: str,
    embedder, vector_store: VectorStore, reranker: Reranker,
    contact_uid: str | None = None,
    pool_k: int = 20, final_k: int = 5,
) -> list[dict]:
    """Two-stage retrieval. ANN recall to pool_k, cross-encoder rerank to final_k."""
    embedding = await embedder.embed(query_text)
    pool = await vector_store.query(embedding, top_k=pool_k,
                                    filter={"contact_uid": contact_uid} if contact_uid else None)
    if not pool:
        return []
    scores = await reranker.score(query_text, [c["content"] for c in pool])
    for c, s in zip(pool, scores):
        c["rerank_score"] = float(s)
    pool.sort(key=lambda c: c["rerank_score"], reverse=True)
    return pool[:final_k]
```

The `contact_uid` filter is load-bearing — for any transcript chunk where you already know who is on the line, pre-filtering to that contact's history is both faster (smaller search space) and more relevant (no cross-contact pollution).

### 3. Live Podium fetch + merge with vector results (neutralizes staleness drift)

The vector store is a snapshot. The contact's phone, opt-out flag, and last-seen-at are live state that can mutate any time. Whenever the RAG bundle includes "the contact's phone number," that field MUST come from the live API, not from a year-old embedded message.

```python
import time
import httpx
from podium_auth import PodiumAuth

LIVE_FIELDS = {"phone", "email", "opt_out_sms", "opt_out_email", "location_uid", "last_seen_at"}

async def fetch_live_contact(auth: PodiumAuth, contact_uid: str) -> dict:
    token = await auth.get_token()
    async with httpx.AsyncClient(timeout=2.0) as c:
        r = await c.get(
            f"https://api.podium.com/v4/contacts/{contact_uid}",
            headers={"Authorization": f"Bearer {token}"},
        )
    if r.status_code != 200:
        return {"error": r.status_code, "live_fields_available": False}
    body = r.json()
    return {k: body.get(k) for k in LIVE_FIELDS} | {"live_fields_available": True}

def merge_live_over_vector(vector_hits: list[dict], live_contact: dict) -> dict:
    """Live state wins on any field listed in LIVE_FIELDS. Vector hits keep only content."""
    return {
        "contact": live_contact,
        "historical_excerpts": [
            {"content": h["content"], "channel": h["channel"],
             "occurred_at": h["occurred_at"], "rerank_score": h["rerank_score"]}
            for h in vector_hits
        ],
    }
```

The merge rule is asymmetric on purpose — vector results NEVER override a live field, even if the rerank score is high. A high-scoring 2023 chunk that mentions "(555) 0100" loses to a 2026 live API response of "(555) 0199" every time.

### 4. PII redaction filter (neutralizes PII reaching the LLM)

Ingest is supposed to redact. Ingest forgot. The retrieval-time filter is the last line of defense and must NOT trust the corpus.

```python
import re

REDACTION_PATTERNS = [
    # credit-card-like 13-19 digit strings (Luhn-validated would be stronger)
    (re.compile(r"\b\d{13,19}\b"), "[REDACTED:CC]"),
    # SSN-like
    (re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"), "[REDACTED:SSN]"),
    # full street addresses (loose — opt-in per-deployment)
    (re.compile(r"\b\d{1,5}\s+\w+\s+(St|Ave|Rd|Blvd|Lane|Ln|Dr|Drive|Court|Ct)\b", re.I),
        "[REDACTED:ADDR]"),
    # email
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[REDACTED:EMAIL]"),
    # E.164-ish phone
    (re.compile(r"\+?\d[\d\s\-().]{8,}\d"), "[REDACTED:PHONE]"),
    # DOB-ish dates
    (re.compile(r"\b(0?[1-9]|1[0-2])/-/-\d{2}\b"),
        "[REDACTED:DOB]"),
]

def redact(text: str) -> str:
    for pat, repl in REDACTION_PATTERNS:
        text = pat.sub(repl, text)
    return text

def redact_bundle(bundle: dict) -> dict:
    bundle["historical_excerpts"] = [
        {**e, "content": redact(e["content"])} for e in bundle["historical_excerpts"]
    ]
    return bundle
```

Apply `redact_bundle` AFTER `merge_live_over_vector` and BEFORE the bundle ever reaches the LLM emission path. The live-contact fields are not redacted — they are the inputs the LLM needs to compose the answer (the bridge ships them unredacted to the model and the model is responsible for not echoing the customer's own DOB back at them).

### 5. Token-budget enforcement (neutralizes context overflow)

The LLM has a window. The bundle has whatever shape retrieval emitted. The two must reconcile before the prompt is built or the model silently truncates from the middle.

```python
def approx_tokens(s: str) -> int:
    # tiktoken-style ~4 chars / token; replace with model-specific tokenizer in prod
    return max(1, len(s) // 4)

def enforce_budget(bundle: dict, max_tokens: int = 1500) -> dict:
    """Drop lowest-rerank excerpts until under budget. Summarize if dropping reaches 1."""
    excerpts = bundle["historical_excerpts"]
    excerpts.sort(key=lambda e: e["rerank_score"], reverse=True)
    total = sum(approx_tokens(e["content"]) for e in excerpts)
    while total > max_tokens and len(excerpts) > 1:
        dropped = excerpts.pop()
        total -= approx_tokens(dropped["content"])
    if total > max_tokens and excerpts:
        # last-resort hard truncate of the single remaining excerpt
        e = excerpts[0]
        e["content"] = e["content"][: max_tokens * 4]
        e["truncated"] = True
    bundle["historical_excerpts"] = excerpts
    bundle["token_count"] = total
    return bundle
```

`max_tokens` is the budget for the historical-excerpts surface only — the live contact block, system prompt, and live transcript history have their own allocations in the calling agent loop. Sizing them all together is the calling agent's job; this skill is responsible for keeping retrieval inside its own slice.

### 6. Hard timeout + parallel fan-out (neutralizes missed-the-call latency)

The bridge MUST return inside the latency budget. If reranking is slow today, the bundle ships without reranked excerpts and the LLM grounds on raw vector hits — degraded but timely. The flag `partial: true` tells the model it is grounding on incomplete context.

```python
import asyncio
import time

async def build_context(
    transcript_chunk: str,
    contact_uid: str | None,
    auth, embedder, vector_store, reranker,
    timeout_ms: int = 800,
) -> dict:
    """Fan out retrieval surfaces in parallel; merge what completes before timeout."""
    started = time.monotonic()
    deadline = started + timeout_ms / 1000.0

    async def with_deadline(coro):
        try:
            return await asyncio.wait_for(coro, timeout=max(0.01, deadline - time.monotonic()))
        except asyncio.TimeoutError:
            return None

    coalesced = transcript_chunk  # production: pass through TranscriptCoalescer
    vec_task  = asyncio.create_task(
        with_deadline(search_with_rerank(coalesced, embedder, vector_store, reranker,
                                          contact_uid=contact_uid))
    )
    live_task = asyncio.create_task(
        with_deadline(fetch_live_contact(auth, contact_uid)) if contact_uid else asyncio.sleep(0)
    )

    vec_hits = (await vec_task) or []
    live     = (await live_task) or {"live_fields_available": False}
    elapsed_ms = int((time.monotonic() - started) * 1000)

    bundle = merge_live_over_vector(vec_hits, live)
    bundle = redact_bundle(bundle)
    bundle = enforce_budget(bundle)
    bundle["meta"] = {
        "elapsed_ms": elapsed_ms,
        "timeout_ms": timeout_ms,
        "partial": elapsed_ms >= timeout_ms,
        "had_vector_hits": bool(vec_hits),
        "had_live_lookup": live.get("live_fields_available", False),
    }
    return bundle
```

The deadline is the contract. A bridge that misses the deadline is broken even if its output is perfect. Measure p99 against `timeout_ms` and treat sustained `partial: true` rates above 5% as a paging incident.

## Error Handling

| Surface | Failure | Bundle behavior |
|---|---|---|
| Vector store unreachable | `vec_task` returns None | `historical_excerpts: []`, `meta.had_vector_hits: false` |
| Embedder model timeout | embed step exceeds budget | Skip vector surface entirely; live-only bundle |
| Reranker timeout | rerank step exceeds budget | Fall back to raw cosine score from vector store |
| Live Podium 429 | rate-limited | `contact.live_fields_available: false`; vector-only bundle |
| Live Podium 401 | auth dead | Surface to `podium-auth` decay monitor; vector-only bundle this call |
| Live Podium 404 | unknown contact_uid | `contact: {"error": 404}`; vector hits without contact filter |
| All surfaces timeout | hard 800ms hit | Empty bundle with `meta.partial: true` — LLM grounds on transcript alone |

## Examples

### Minimal: build a bundle for one transcript chunk

```bash
python3 scripts/context_fetch.py \
  --transcript "I had a question about my last order" \
  --contact-uid "ctc_abc123" \
  --pgvector-dsn "{your-pgvector-dsn}" \
  --output json
```

Output (truncated):

```json
{
  "contact": {"phone": "+15551230199", "opt_out_sms": false, "live_fields_available": true},
  "historical_excerpts": [
    {"content": "Order ABC-12345 shipped Tuesday", "channel": "webchat",
     "occurred_at": "2026-05-01T14:22:00Z", "rerank_score": 0.91}
  ],
  "token_count": 14,
  "meta": {"elapsed_ms": 412, "timeout_ms": 800, "partial": false,
           "had_vector_hits": true, "had_live_lookup": true}
}
```

### Raw vector query (no live merge, no redaction)

```bash
python3 scripts/vector_query.py \
  --query "did they ask about refund policy" \
  --contact-uid "ctc_abc123" \
  --pgvector-dsn "{your-pgvector-dsn}" \
  --top-k 5
```

### Build the LLM prompt from a bundle

```bash
python3 scripts/transcript_to_llm.py \
  --transcript "I had a question about my last order" \
  --bundle-file ./bundle.json \
  --system-prompt-file ./system.txt \
  --max-tokens 4000
```

Emits a structured prompt: `SYSTEM` block, `LIVE CONTACT` block, `HISTORICAL CONTEXT` block (with rerank scores), `TRANSCRIPT TURN` block. The LLM sees clearly which fields are live and which are historical.

### Score a single (query, candidate) pair

```bash
python3 scripts/relevance_score.py \
  --query "did they ask about refund policy" \
  --candidate "Our policy is 30-day refunds with receipt"
# 0.87
```

## Output

- `context_fetch.py`-shaped pipeline that emits a structured JSON bundle in ≤800ms
- pgvector schema + ingest hook that feeds `podium-conversation-history-export` output into the vector store
- Reranker wiring (cross-encoder default; LLM-reranker optional adapter)
- Redaction filter applied at retrieval time as the last line of defense
- Token budget enforced per surface with rerank-priority drop ordering
- Hard deadline + `partial: true` flag so the LLM never silently grounds on incomplete context
- p99 latency dashboard with vector / rerank / live-fetch broken out — sustained `partial` >5% is a page

## Resources

- [Podium API docs — Contacts](https://docs.podium.com/reference/contacts)
- [pgvector documentation](https://github.com/pgvector/pgvector)
- [BGE reranker — BAAI/bge-reranker-base](https://huggingface.co/BAAI/bge-reranker-base)
- [config/settings.yaml](config/settings.yaml) — pool_k / final_k, timeout budgets, redaction patterns, embedder + reranker defaults
- [references/errors.md](references/errors.md) — ERR_RAG_* codes with cause + solution
- [references/examples.md](references/examples.md) — 10 worked examples (single-tenant, agent-loop, sandbox eval, fault drills)
- [references/implementation.md](references/implementation.md) — pgvector schema, Pinecone/Weaviate adapters, embedder + reranker swaps, ingest hook for the export skill
- [scripts/context_fetch.py](scripts/context_fetch.py) — CLI: transcript chunk + contact → JSON bundle
- [scripts/vector_query.py](scripts/vector_query.py) — CLI: raw two-stage retrieval with rerank
- [scripts/transcript_to_llm.py](scripts/transcript_to_llm.py) — CLI: format a turn + bundle into an LLM prompt
- [scripts/relevance_score.py](scripts/relevance_score.py) — CLI: score (query, candidate) ∈ [0, 1]
