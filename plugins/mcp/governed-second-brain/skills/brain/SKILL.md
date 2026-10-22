---
name: brain
description: |
  Search and analyze governed notes, decisions, runbooks, and conventions, returning
  a qmd:// citation for every supported claim. Use when checking what the brain has
  captured about architecture, infrastructure, decisions, or operating practices.
  Trigger with "/brain", "ask the brain", or "check my knowledge base".
allowed-tools: "mcp__governed-brain__brain_search"
version: 1.2.1
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: Apache-2.0
compatibility: "Designed for Claude Code; ships with the bobs-big-brain (governed-brain) plugin, which auto-wires the governed-brain MCP server. Works in both modes: local (in-process, needs qmd on PATH) and team (proxies to your team brain when TEAMKB_API_URL is set). Same brain_search either way."
tags: [brain, knowledge, search, citations, governance, local-first, team]
argument-hint: "[question]"
model: inherit
effort: low
---

# Brain — cited answers from your governed knowledge base

Ask your knowledge **brain** a question and get an answer grounded in your governed
corpus, where **every claim carries a qmd:// citation**. The brain does not paraphrase
from memory — it retrieves governed memories and cites them, so any answer is
verifiable after the fact.

## Overview

This is the read surface of Bob's Big Brain: your files are **compiled** into
governed memories, **governed** by deterministic code, and **retrieved** with citations
by **Tobi's qmd** (OSS). The `brain_search` MCP tool fronts that retrieval. Your product
surround is INTKB govern + ICO compile + this plugin — not a fork of qmd.

The job here is to turn a natural-language question into a cited answer — and to refuse
to answer beyond what the citations support.

## Prerequisites

- The **bobs-big-brain** / governed-brain plugin is installed (MCP `governed-brain`).
- **Mode is automatic.** In **local mode** (default) search runs **in-process**
  against your local `~/.teamkb` index — no network, no API key; a compatible **qmd**
  binary must be available (prefer monorepo pin `@tobilu/qmd` via the Registrar / installer).
  Operators can use `scripts/bbb-qmd` from bobs-big-brain-registrar so XDG points at the team
  index, not personal `~/.cache/qmd`. In **team mode** (`TEAMKB_API_URL` set) search
  proxies to the team brain. Every hit is a `qmd://` citation.
- See [the runtime contract](references/runtime-contract.md) for exact inputs, result shapes,
  authentication, and mode-specific failures.

## Instructions

### Step 1: Search the governed corpus

Retrieval is **Tobi's qmd** (BM25 keyword via the MCP). Prefer **short keyword queries**
over full sentences.

1. Derive **1–4 distinctive nouns/verbs** from the user question (drop what/why/how, articles,
   auxiliaries, prepositions).
2. Call **`brain_search`** with those keywords and `scope: "curated"` (default promoted knowledge).

```
brain_search({ query: "SOPS age secrets", scope: "curated" })
```

The tool returns `{ source, results: [{ citation, snippet, score, collection }] }`.
Each `citation` is a `qmd://COLLECTION/FILENAME` URI — the receipt for that hit.

**Empty-result ladder (do not stop after one miss):**

1. **Keyword retry (curated):** only if the first call was still a long natural-language sentence
   (you skipped deriving 1–4 keywords). Re-run with 1–4 keywords only. **Skip this step** when the
   first query was already keyword-style — do not re-call with the same tokens.
2. **Scope retry (`all`):** if curated is still empty, re-run the **same keywords** with
   `scope: "all"`. Do **not** use `inbox`/`archived` unless the user asks.
3. Only after curated+keywords and all+keywords are empty → Step 3 (honest refuse).

```
brain_search({ query: "shipped week", scope: "curated" })
// if empty (keywords already used):
brain_search({ query: "shipped week", scope: "all" })
```

### Step 2: Answer ONLY from the cited results

- Synthesize a direct answer from the returned snippets.
- **Attach the qmd:// citation to every claim**, inline — for example:
  `The proxy reverse-proxies the API (qmd://kb-curated/system-map.md).`
- If two hits conflict, surface both with their citations rather than silently
  picking one — the governance layer tracks contradictions; do not paper over them.
- **Do not add knowledge the citations do not support.** Any reasoning beyond the
  corpus must be labeled clearly as inference, not the brain's answer.

### Step 3: Handle an empty result honestly

If `results` is **still** empty after the empty-result ladder in Step 1, say so plainly: the brain
has nothing governed on that topic. Do **not** fall back to general knowledge and present it as the
brain's answer. Optionally note that the topic may need to be captured (run `/brain-save`).

## Output

1. A short, direct answer.
2. Each load-bearing claim followed by its qmd:// citation.
3. A closing **Sources** list of the distinct qmd:// URIs used.

## Examples

**Cited answer:**

```
/brain what does my system map say about the proxy?

→ The proxy is the single ingress; it reverse-proxies each domain to its service
  and must be reloaded, not restarted, after edits (qmd://kb-curated/system-map.md).

Sources:
- qmd://kb-curated/system-map.md
```

**Empty result (honest refusal):**

```
/brain what is my refund policy?

→ The brain has nothing governed on a refund policy. I won't guess from general
  knowledge. If this should be in your brain, capture it with /brain-save.
```

## Error Handling

| Situation                              | Response                                                                                                                         |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `brain_search` returns empty `results` | Run the empty-result ladder (keywords → scope all); only then refuse. Do not fabricate.                                          |
| `qmd` missing / index empty            | Retrieval degrades to empty. Tell operator: install `@tobilu/qmd`, run INTKB `pnpm search-canary -- --heal` or `bbb-qmd status`. |
| MCP tool unavailable                   | Plugin not enabled; install/enable bobs-big-brain / governed-brain.                                                              |
| User asks to write/capture             | Out of scope here — direct them to `/brain-save`.                                                                                |

## Guardrails

- Read-only. This skill never writes to the corpus — capture and governance live in
  `/brain-save`.
- Never invent a qmd:// URI. Cite only URIs returned by `brain_search`.
- Prefer fewer, well-cited claims over a broad answer that cannot be anchored.
- Do not conflate this product with IRSB / Moat / Scout (separate stack).
- **Provenance ≠ truth.** Promotion receipts record each memory's capture channel (or `unattested`)
  and an origin-token hash — that proves WHERE a capture came from, not that its content is true. An
  authenticated insider can still have saved poisoned content with a valid origin; weigh cited answers
  accordingly and rely on govern policy, human review, and supersession as the content-quality gates.

## Resources

- [Bob's Big Brain umbrella](https://github.com/intent-solutions-io/bobs-big-brain-umbrella) — stack map.
- [bobs-big-brain-plugin](https://github.com/jeremylongshore/bobs-big-brain-plugin) — this plugin.
- [bobs-big-brain-registrar](https://github.com/jeremylongshore/bobs-big-brain-registrar) — govern layer (Bob's Big Brain Registrar) + `bbb-qmd`.
- [tobi/qmd](https://github.com/tobi/qmd) (npm `@tobilu/qmd`) — retrieve engine (OSS; the stack pins it rather than forking it).
- [bobs-big-brain-compiler](https://github.com/jeremylongshore/bobs-big-brain-compiler) — compile layer (Bob's Big Brain Compiler).
- The write counterpart: the `/brain-save` skill (governed capture).
