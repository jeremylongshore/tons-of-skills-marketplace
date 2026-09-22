---
name: langchain-embeddings-search
description: 'Build and query vector stores with LangChain 1.0 without getting burned
  by

  flipped score semantics, embedding-dim mismatches, reranker quirks, and

  chunk-splitter bugs. Use when building a RAG pipeline, choosing between FAISS /

  Pinecone / Chroma / PGVector, filtering by similarity score, or adding a reranker.

  Trigger with "langchain embeddings", "vector store similarity search",

  "langchain RAG retrieval", "FAISS score", "Pinecone score", "reranker score".

  '
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(pip:*), Grep
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- python
- langchain-1.0
- embeddings
- rag
- vector-store
compatibility: Designed for Claude Code
---
# LangChain Embeddings and Vector Search (Python)

## Overview

`FAISS.similarity_search_with_score()` returns L2 distance — **lower is better**.
`Pinecone.similarity_search_with_score()` returns cosine similarity — **higher is
better**. Swap your vector store and your `if score > 0.8` filter now keeps the
garbage and drops the good results, silently. This is pain-catalog entry P12,
and it is the single most common reason a "we migrated from FAISS to Pinecone
for scale" project loses retrieval quality overnight.

The sibling gotchas:

- P13 — `RecursiveCharacterTextSplitter` default separators break inside code
  fences, so RAG over Markdown docs truncates code examples mid-function
- P14 — Embedding-dim mismatch crashes at insert time (after 10 minutes of
  processing), not at `VectorStore.__init__`; the failure blames "dim
  mismatch: 1536 != 3072" and no earlier error
- P15 — Cohere/Jina reranker scores are **within-query relative**, so a 0.34
  top-1 is not worse than a 0.92 top-1 on a different query; filtering by
  threshold is the wrong heuristic

This skill walks through embedding model selection, vector store creation with
the version-safe dim guard, score normalization, hybrid keyword+vector search,
and rerankers with the correct filter-by-rank pattern. Pin: `langchain-core 1.0.x`,
`langchain-community 1.0.x`, `langchain-openai 1.0.x`, `faiss-cpu`, `pinecone-client`.
Pain-catalog anchors: P12, P13, P14, P15, P49, P50.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0` and `langchain-community >= 1.0, < 2.0`
- Embedding provider: `pip install langchain-openai` (text-embedding-3-small/large)
- Vector store: `pip install faiss-cpu` OR `pip install langchain-pinecone`
- Provider API keys: `OPENAI_API_KEY`, `PINECONE_API_KEY`

## Instructions

### Step 1 — Initialize embeddings with an explicit dim

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",  # 1536 dims
    # For text-embedding-3-large, use 3072 dims — must match index
)

# Assert dim at startup (prevents P14)
assert len(embeddings.embed_query("test")) == 1536, "embedding dim drifted"
```

Swapping models (`-small` 1536 → `-large` 3072) is a migration, not a swap.
Plan it — back-fill the index, not just the config.

### Step 2 — Choose a vector store

| Store | Score metric | Latency (1M vectors) | When to use |
|---|---|---|---|
| `FAISS` | L2 distance (lower = better) | ~5ms | Local dev, < 1M vectors, in-process |
| `Chroma` | Cosine similarity (higher = better) | ~10ms | Small multi-user, persistent local |
| `PGVector` | Cosine by default (higher = better) | ~20ms | Existing Postgres, transactional needs |
| `PineconeVectorStore` | Cosine similarity (higher = better) | ~50ms (hosted) | > 1M vectors, multi-tenant, managed |

```python
from langchain_community.vectorstores import FAISS

store = FAISS.from_documents(docs, embedding=embeddings)
results = store.similarity_search_with_score("query", k=5)
# FAISS: [(doc, 0.31), (doc, 0.42), ...] — LOWER IS MORE SIMILAR
```

vs.

```python
from langchain_pinecone import PineconeVectorStore

store = PineconeVectorStore(index_name="prod", embedding=embeddings)
results = store.similarity_search_with_score("query", k=5)
# Pinecone: [(doc, 0.91), (doc, 0.87), ...] — HIGHER IS MORE SIMILAR
```

See [Vector Store Comparison](references/vector-store-comparison.md) for the
feature matrix and the migration gotchas.

### Step 3 — Normalize scores before any threshold filter

Write a normalizer at the retriever boundary, so downstream code never sees
raw store-specific scores:

```python
def normalize(score: float, store_type: str) -> float:
    """Return similarity in [0, 1] where 1 = identical, 0 = unrelated."""
    if store_type == "faiss_l2":
        return 1.0 / (1.0 + score)  # collapse L2 distance into similarity
    if store_type in {"pinecone", "chroma", "pgvector"}:
        return max(0.0, min(1.0, score))  # already similarity, clamp just in case
    raise ValueError(f"Unknown store type: {store_type}")
```

Now `score > 0.7` means the same thing regardless of backend. See
[Score Semantics](references/score-semantics.md) for the per-store derivation.

### Step 4 — Chunk text with language-aware splitters

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

# BAD — breaks inside Markdown code fences (P13)
bad = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

# GOOD — respects Markdown structure
md_splitter = RecursiveCharacterTextSplitter.from_language(
    Language.MARKDOWN, chunk_size=1000, chunk_overlap=100,
)

# For Python source files
py_splitter = RecursiveCharacterTextSplitter.from_language(
    Language.PYTHON, chunk_size=1500, chunk_overlap=150,
)
```

PDF pipelines have their own pain: `PyPDFLoader` splits by page, tearing tables
in half (P49). Use `PyMuPDFLoader` or `UnstructuredPDFLoader` for documents
with tables.

### Step 5 — Hybrid search (keyword + vector)

Pure vector search misses exact-match keywords (product SKUs, error codes,
function names). Combine BM25 + vector:

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

bm25 = BM25Retriever.from_documents(docs); bm25.k = 5
vector = store.as_retriever(search_kwargs={"k": 5})

ensemble = EnsembleRetriever(
    retrievers=[bm25, vector],
    weights=[0.4, 0.6],  # tune on your eval set
)
```

See [Hybrid Search](references/hybrid-search.md) for the eval harness and the
weight-tuning procedure.

### Step 6 — Rerank by rank, not by score

```python
from langchain_cohere import CohereRerank

reranker = CohereRerank(top_n=3, model="rerank-v3.5")
reranked = reranker.compress_documents(
    documents=candidates, query=query,
)
# reranked[0].metadata["relevance_score"] is query-relative — 0.34 may be the best
# WRONG: [d for d in reranked if d.metadata["relevance_score"] > 0.5]
# RIGHT: reranked[:top_n]  — trust the rank order
```

Filter by *rank* (keep top-k) not threshold. Calibration per-query is possible
but rarely worth the engineering cost.

## Output

- Embeddings initialized with dim assertion at startup
- Vector store chosen from the comparison matrix with score-semantics awareness
- Score normalizer applied at retriever boundary (no raw scores downstream)
- Language-aware text splitter that respects code fences and PDF structure
- Hybrid retriever combining BM25 and vector with tuned weights
- Reranker filtering by rank, not threshold

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `PineconeApiException: dim mismatch: 1536 != 3072` | Changed embedding model without reindexing (P14) | Create a new index with the new dim; migrate in a background job |
| Retrieval quality drops after FAISS→Pinecone swap | Score semantics flipped (P12) | Apply `normalize()` at boundary; retune threshold on eval set |
| RAG answers misquote tables | `PyPDFLoader` tore table across pages (P49) | Switch to `PyMuPDFLoader` or `UnstructuredPDFLoader` |
| RAG retrieval drops code examples mid-function | `RecursiveCharacterTextSplitter` broke code fence (P13) | Use `from_language(Language.MARKDOWN/PYTHON)` |
| Cohere reranker top-1 score < 0.5 | Scores are per-query relative (P15) | Filter by rank (`reranked[:k]`), not threshold |
| `WebBaseLoader` returns 403 / Cloudflare interstitial (P50) | Default User-Agent flagged as bot | Pass `header_template={"User-Agent": "Mozilla/5.0 ..."}`; respect robots.txt |
| `ValueError: expected str instance, NoneType found` on embed | Empty document content | Filter `docs = [d for d in docs if d.page_content.strip()]` before embedding |

## Examples

### Building a RAG retriever with hybrid search

End-to-end: load Markdown docs with language-aware chunking, embed with OpenAI
`text-embedding-3-small`, index in FAISS for local dev, wrap in an
`EnsembleRetriever` with BM25 at 0.4 weight and vector at 0.6.

See [Hybrid Search](references/hybrid-search.md) for the full builder and the
weight-tuning procedure on a golden set.

### Migrating from FAISS to Pinecone without quality regression

The three gotchas: (a) score semantics flip (P12), (b) the migration needs a
re-embed unless the source embedding is stable, (c) threshold filters must be
retuned on the new score scale.

See [Vector Store Comparison](references/vector-store-comparison.md) for the
migration checklist.

### Per-tenant vector stores without leakage

Use Pinecone namespaces or PGVector row-level security. Construct the retriever
per-request with the tenant ID — never bind a retriever at import time (P33).

See the pack's `langchain-enterprise-rbac` skill for the tenant-isolation pattern.

## Resources

- [LangChain Python: Vector stores](https://python.langchain.com/docs/integrations/vectorstores/)
- [LangChain Python: Retrievers](https://python.langchain.com/docs/concepts/retrievers/)
- [LangChain: Text splitters](https://python.langchain.com/docs/concepts/text_splitters/)
- [FAISS docs](https://github.com/facebookresearch/faiss/wiki) (score is L2 distance)
- [Pinecone metrics](https://docs.pinecone.io/guides/indexes/understanding-indexes#metrics) (cosine default)
- [Cohere Rerank](https://docs.cohere.com/docs/rerank-overview) (score per-query relative)
- Pack pain catalog: `docs/pain-catalog.md` (entries P12, P13, P14, P15, P49, P50)
