---
name: langchain-data-handling
description: "Load and chunk documents for LangChain 1.0 RAG pipelines correctly \u2014\
  \nlanguage-aware splitters, table-safe PDF loaders, Cloudflare-compatible web\n\
  loaders, chunk-boundary strategies that survive real-world structure. Use when\n\
  building a RAG pipeline, diagnosing why retrieval misquotes a table, or\ndebugging\
  \ a crawler returning blank content. Trigger with \"langchain document\nloader\"\
  , \"text splitter\", \"chunking strategy\", \"pdf loader\",\n\"markdown splitter\"\
  , \"webbaseloader\".\n"
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(pip:*)
version: 2.7.0
license: MIT
author: Jeremy Longshore <jeremy@intentsolutions.io>
tags:
- saas
- langchain
- langgraph
- python
- langchain-1.0
- document-loaders
- text-splitters
- rag
compatibility: Designed for Claude Code
---
# LangChain Data Handling — Loaders and Splitters (Python)

## Overview

You have a RAG system over a Python docs site. A user asks "what does
`trim_messages` do?" and the retriever returns this chunk:

```
### `trim_messages(strategy="last", include_system=True)`

Trim a message history to fit a token budget. The newest messages are kept;
older messages are dropped. Pass `include_system=True` to preserve the system
```

...and that's it. The chunk ends there. The code example showing the function
body — the actual thing the user wanted — is in a **different** chunk, retrieved
with a lower similarity score and dropped before the LLM sees it. The model
then hallucinates the function's behavior from the signature alone.

This is pain-catalog entry **P13**. `RecursiveCharacterTextSplitter`'s default
separators are `["\n\n", "\n", " ", ""]`. It splits on any blank line — including
**inside** triple-backtick code fences in Markdown. The fix is a one-line swap
to `RecursiveCharacterTextSplitter.from_language(Language.MARKDOWN)`, which
treats the fence as an atomic unit, but you have to know the bug exists.

The sibling failures this skill prevents:

- **P49** — `PyPDFLoader` splits by page. A 5-row financial table that spans
  a page break gets torn in half; rows 1-3 go in one chunk, rows 4-5 in another
  with no header. A RAG answer sourced from the second chunk misquotes the
  numbers because the column meanings are in the first chunk. Fix: use
  `PyMuPDFLoader` or `UnstructuredPDFLoader`, which detect tables and emit
  them as distinct structured elements.
- **P50** — `WebBaseLoader`'s default User-Agent is `python-requests/2.x`.
  Cloudflare-protected sites flag this as a bot and return a **403 interstitial
  HTML page** ("Checking your browser...") instead of real content. The crawler
  indexes the challenge page. You notice weeks later when every retrieval from
  that source returns the same Cloudflare text. Fix: set a realistic
  `header_template={"User-Agent": "Mozilla/5.0 ..."}`, respect `robots.txt`,
  and rate-limit per-host to 1 req/sec.

Pinned versions: `langchain-core 1.0.x`, `langchain-community 1.0.x`,
`langchain-text-splitters 1.0.x`, `pymupdf`, `unstructured`.
Pain-catalog anchors: P13, P49, P50, P15.

This skill is the **upstream half** of the RAG pipeline — load and chunk.
For the downstream half (embedding, scoring, reranking) see the pair skill
`langchain-embeddings-search`, which covers score semantics (P12), dim guards
(P14), and reranker filtering (P15). Do not re-implement chunking there.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0` and `langchain-community >= 1.0, < 2.0`
- `langchain-text-splitters >= 1.0, < 2.0`
- PDF support: `pip install pymupdf unstructured[pdf]`
- Web loading: `pip install beautifulsoup4 requests`
- For corpus dedup (optional): `pip install datasketch`

## Instructions

### Step 1 — Choose a loader by source format

Loader selection is the first decision — get it wrong and no amount of
splitter tuning will recover. Use the decision table:

| Source | Use | NOT | Why |
|---|---|---|---|
| PDF with tables | `PyMuPDFLoader` or `UnstructuredPDFLoader` | `PyPDFLoader` | Tables torn by page splits (P49) |
| PDF text-only | `PyPDFLoader` | — | Simple, fast, OK when no tables |
| Web page | `WebBaseLoader(header_template=...)` | Default UA | Cloudflare 403 (P50) |
| Markdown docs | `UnstructuredMarkdownLoader` | Plain text read | Preserves heading structure |
| HTML long-form | `WebBaseLoader` + `HTMLHeaderTextSplitter` | Plain text | Keeps `<h1>`/`<h2>` context |
| Code repo | `GenericLoader` with language parser | `DirectoryLoader` as text | Language-aware chunking |
| Corpus (1000+ docs) | `DirectoryLoader` + `glob` filter | One-by-one | Parallel load, progress |

```python
from langchain_community.document_loaders import (
    PyMuPDFLoader,            # table-aware PDF
    WebBaseLoader,            # web pages (set custom UA)
    UnstructuredMarkdownLoader,
    DirectoryLoader,
)

# PDF with tables — P49 fix
pdf_docs = PyMuPDFLoader("10-Q-filing.pdf").load()

# Web page — P50 fix
web_docs = WebBaseLoader(
    "https://example.com/article",
    header_template={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    },
).load()

# Markdown docs site
md_docs = UnstructuredMarkdownLoader("docs/guide.md").load()

# Corpus
corpus = DirectoryLoader(
    "./docs", glob="**/*.md",
    loader_cls=UnstructuredMarkdownLoader,
    show_progress=True,
).load()
```

Hard limit: keep single-PDF ingestion under **5 MB** per call. Larger files
should be pre-split with `pdftk` / `qpdf` to avoid OOM on `PyMuPDFLoader`'s
full-document parse.

See [Loader Selection Matrix](references/loader-selection-matrix.md) for the
full per-format table with cost and accuracy notes.

### Step 2 — Pick a splitter by content type

| Content | Splitter | chunk_size | chunk_overlap | Why |
|---|---|---|---|---|
| Prose (docs, articles) | `RecursiveCharacterTextSplitter.from_language(Language.MARKDOWN)` | 1000 | 100 | Preserves code fences (P13) |
| Python source | `RecursiveCharacterTextSplitter.from_language(Language.PYTHON)` | 1500 | 150 | Splits at `def`/`class` |
| FAQ / Q&A | `RecursiveCharacterTextSplitter` with `separators=["\n\n"]` | 500 | 50 | One chunk per Q-A pair |
| HTML long-form | `HTMLHeaderTextSplitter` | — | — | Headers become metadata |
| Generic text | `RecursiveCharacterTextSplitter` | 1000 | 100 | Safe default |

```python
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    Language,
    HTMLHeaderTextSplitter,
)

# GOOD — P13 fix for Markdown
md_splitter = RecursiveCharacterTextSplitter.from_language(
    Language.MARKDOWN, chunk_size=1000, chunk_overlap=100,
)

# GOOD — Python code
py_splitter = RecursiveCharacterTextSplitter.from_language(
    Language.PYTHON, chunk_size=1500, chunk_overlap=150,
)

# GOOD — HTML long-form with heading-as-metadata
html_splitter = HTMLHeaderTextSplitter(
    headers_to_split_on=[("h1", "Header 1"), ("h2", "Header 2")],
)

# BAD — breaks inside code fences (P13)
bad = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
```

See [Language-Aware Splitters](references/language-aware-splitters.md) for the
full list of `Language.*` enum values, custom separator patterns, and the
code-fence-detection regex for when you need a custom splitter.

### Step 3 — Tune chunk_size and overlap

Defaults from the table work for most corpora. Tune when:

- **Retrieval misses context**: increase `chunk_size` (1000 → 1500) or
  `chunk_overlap` (100 → 200). Overlap is what bridges a concept that crosses
  chunk boundaries.
- **Retrieval too broad, answers wander**: decrease `chunk_size` (1000 → 500).
  Smaller chunks = more precise retrieval but more chunks to index.
- **Tables / structured data**: do NOT tune — index them separately (step 4).

A 1% overlap-to-size ratio is too low (200/20000); 20% is the sweet spot for
most prose. Code needs less overlap (10%) because function boundaries are
natural splits.

### Step 4 — Detect and index tables as structured records

Tables are **not** text. If your corpus has financial filings, product specs,
or any tabular data, index tables as separate records with column metadata:

```python
import fitz  # pymupdf directly for table detection

def extract_tables_as_records(pdf_path: str) -> list[dict]:
    """Extract tables as one record per row."""
    doc = fitz.open(pdf_path)
    records = []
    for page_num, page in enumerate(doc):
        tables = page.find_tables()
        for table in tables:
            rows = table.extract()
            if not rows:
                continue
            headers = rows[0]
            for row_idx, row in enumerate(rows[1:], start=1):
                record = {
                    "page": page_num,
                    "table_idx": tables.tables.index(table),
                    "row_idx": row_idx,
                    "content": " | ".join(f"{h}: {v}" for h, v in zip(headers, row)),
                    "metadata": dict(zip(headers, row)),
                }
                records.append(record)
    return records
```

Now a question like "what was Q3 revenue?" retrieves a **single row** with its
column headers attached, not half a table missing the column meanings. See
[Table Preservation](references/table-preservation.md) for the full pattern
including hybrid retrieval (prose + table records).

### Step 5 — Preserve metadata through the pipeline

The loader attaches metadata (source, page, heading); the splitter propagates
it. Front-matter in Markdown, PDF page numbers, and web URLs should all end
up in `doc.metadata` so retrieval results are citable:

```python
for doc in md_docs:
    # Markdown front-matter (if loader extracted it)
    print(doc.metadata.get("title"), doc.metadata.get("date"))

# Splitter-preserved metadata
chunks = md_splitter.split_documents(md_docs)
assert chunks[0].metadata == md_docs[0].metadata  # preserved
```

Custom metadata (tenant_id, version, confidence) should be added **before**
splitting so every chunk inherits it.

### Step 6 — Deduplicate noisy corpora

Web crawls and scraped docs often contain near-duplicate pages (nav chrome,
footer boilerplate, syndicated posts). MinHash-based dedup at the chunk level
keeps the index clean:

```python
from datasketch import MinHash, MinHashLSH

lsh = MinHashLSH(threshold=0.9, num_perm=128)
kept = []
for i, chunk in enumerate(all_chunks):
    mh = MinHash(num_perm=128)
    for tok in chunk.page_content.lower().split():
        mh.update(tok.encode())
    if not list(lsh.query(mh)):
        lsh.insert(str(i), mh)
        kept.append(chunk)
```

A threshold of 0.9 catches near-duplicates (minor wording differences) without
eating legitimate paraphrases.

### Step 7 — Compose the pipeline

```python
# Multi-stage: load → split → dedup → index
def build_rag_index(source_dir: str, store):
    # 1. Load
    docs = DirectoryLoader(
        source_dir, glob="**/*.md",
        loader_cls=UnstructuredMarkdownLoader,
    ).load()

    # 2. Clean (empty-content filter)
    docs = [d for d in docs if d.page_content.strip()]

    # 3. Split (language-aware)
    splitter = RecursiveCharacterTextSplitter.from_language(
        Language.MARKDOWN, chunk_size=1000, chunk_overlap=100,
    )
    chunks = splitter.split_documents(docs)

    # 4. Dedup (optional for noisy corpora)
    # chunks = dedup_minhash(chunks, threshold=0.9)

    # 5. Index — handoff to langchain-embeddings-search
    store.add_documents(chunks)
    return store
```

For the embedding + indexing + retrieval steps, see `langchain-embeddings-search`.

## Output

- Loader chosen from the selection matrix matching source format and table needs
- Splitter chosen from the decision tree matching content type
- Chunk size + overlap tuned from the defaults (1000/100 prose, 1500/150 code, 500/50 FAQ)
- Tables extracted as structured records with column metadata (not text chunks)
- Web loaders configured with realistic User-Agent and `robots.txt` respect
- Metadata preserved through loader → splitter → index
- Optional MinHash dedup (threshold 0.9) for noisy corpora

## Error Handling

| Error / symptom | Cause | Fix |
|-------|-------|-----|
| RAG retrieves function signature without body | `RecursiveCharacterTextSplitter` broke inside code fence (P13) | Use `from_language(Language.MARKDOWN)` or add `"```"` as first separator |
| Table rows misquoted in RAG answer | `PyPDFLoader` tore table by page (P49) | Switch to `PyMuPDFLoader`; index tables as structured records |
| `WebBaseLoader` returns 403 / blank content | Default UA flagged by Cloudflare (P50) | Set `header_template={"User-Agent": "Mozilla/5.0 ..."}`; respect robots.txt |
| `ValueError: expected str, NoneType found` during split | Empty `page_content` | Filter `[d for d in docs if d.page_content.strip()]` before splitting |
| `MemoryError` loading PDF | PDF > 5 MB ingested in one call | Pre-split with `pdftk` / `qpdf`; process chunks separately |
| Chunks missing metadata after split | Custom metadata added after loading but before splitting was lost | Add metadata **before** `split_documents()`; verify `chunks[0].metadata` preserved |
| Retrieval quality low on FAQ corpus | Chunks too large, one chunk holds multiple Q-A pairs | Drop to `chunk_size=500, chunk_overlap=50` with `separators=["\n\n"]` |
| Web crawl indexes Cloudflare challenge page | No check for HTTP status / response length | Assert `len(doc.page_content) > 500` and reject pages containing `"Checking your browser"` |
| Duplicate chunks eat retrieval slots | Syndicated content, nav chrome not stripped | MinHash dedup at threshold 0.9 before indexing |
| Reranker scores inconsistent across chunks | Chunks of wildly different size change score distribution (P15) | Normalize chunk size within a corpus; target ±20% of `chunk_size` |

## Examples

### Ingesting a Markdown docs site with code examples

Markdown docs with Python code fences require `Language.MARKDOWN` to keep
fence boundaries intact. Chunk size 1000 with 100 overlap preserves one
function-sized example per chunk. Front-matter fields (title, date, author)
are attached as metadata for citation. See
[Language-Aware Splitters](references/language-aware-splitters.md).

### Ingesting a PDF filing with financial tables

10-Q filings have dozens of multi-row tables. Use `PyMuPDFLoader` for the prose
and a direct `fitz.find_tables()` pass to extract tables as structured records.
Index prose with `chunk_size=1000` and tables as one-row-per-record with the
header row concatenated. Questions like "what was Q3 revenue?" hit a single row
with column meanings attached. See
[Table Preservation](references/table-preservation.md).

### Crawling a documentation site behind Cloudflare

Set a realistic User-Agent, fetch `robots.txt` first and respect `Disallow`
rules, rate-limit to 1 req/sec per host, and prefer the site's sitemap or RSS
feed when available. Assert response length > 500 chars and reject known
interstitial patterns. See [Crawler Hygiene](references/crawler-hygiene.md).

### Ingesting a Python code repo for code RAG

`GenericLoader` with `LanguageParser(language=Language.PYTHON)` preserves
function and class boundaries. Chunk size 1500 with 150 overlap gives enough
context for typical function-level queries. Imports and module docstrings
end up in their own chunks — tag them with metadata for higher precision
retrieval on "where is X imported from" queries.

## Resources

- [LangChain Python: Text splitters](https://python.langchain.com/docs/concepts/text_splitters/)
- [LangChain Python: Document loaders](https://python.langchain.com/docs/concepts/document_loaders/)
- [LangChain Python: Retrievers](https://python.langchain.com/docs/concepts/retrievers/)
- [PyMuPDF (fitz) docs](https://pymupdf.readthedocs.io/) — table detection via `page.find_tables()`
- [Unstructured.io](https://unstructured.io/) — table-aware PDF parsing
- [Cloudflare bot management](https://developers.cloudflare.com/bots/concepts/bot/) — why default UAs fail
- [robots.txt spec](https://www.rfc-editor.org/rfc/rfc9309.html) — crawler obligations
- Pair skill: `langchain-embeddings-search` (embed/score/rerank — downstream of this skill)
- Pack pain catalog: `docs/pain-catalog.md` (entries P13, P49, P50, P15)
