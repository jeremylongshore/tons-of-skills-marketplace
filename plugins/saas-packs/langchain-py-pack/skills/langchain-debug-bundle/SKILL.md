---
name: langchain-debug-bundle
description: "Produce a reproducible, sanitized diagnostic bundle for a LangChain\
  \ / LangGraph\nincident \u2014 environment snapshot, version manifest, filtered\
  \ astream_events(v2)\ntranscript, propagating callback stack, LangSmith trace URL\
  \ \u2014 so a debug\ncolleague can reproduce the failure without a live terminal.\
  \ Use when triaging\na production incident, filing a Discord or GitHub bug report,\
  \ asking for help\non the LangChain forum, or archiving a post-mortem artifact.\n\
  Trigger with \"langchain debug bundle\", \"langgraph debug dump\",\n\"langchain\
  \ diagnostic export\", \"langsmith trace export\", \"astream_events dump\",\n\"\
  langchain incident bundle\".\n"
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
- debugging
- observability
- incident-response
compatibility: Designed for Claude Code
---
# LangChain Debug Bundle (Python)

## Overview

An on-call engineer pages you at 2am: the production agent loops, `ToolMessage`
outputs are empty strings, the user sees "I could not find the answer." Someone
asks the right question — *what state was the graph in when it gave up?* — and
there is no answer, because the terminal that caught the failure is already
gone, the Kubernetes pod has restarted, and the LangSmith URL was never
recorded.

This skill produces one artifact: a single `bundle-<incident_id>.tar.gz` (typically
1-10 MB) containing everything a second engineer needs to reproduce the failure
without a live terminal — environment and version manifest, filtered
`astream_events(version="v2")` JSONL, a propagating callback stack, the
LangSmith trace URL, and a post-write sanitization pass.

Four pitfalls make naive bundles useless:

- **P01** — `ChatAnthropic.stream()` reports `token_usage` only on stream close; token math read from `on_llm_end` lags by stream duration, so cost context in the bundle is wrong.
- **P28** — `BaseCallbackHandler.with_config(callbacks=[...])` does NOT propagate into subgraphs or inner `create_react_agent` loops. A debug callback bound that way silently captures zero events from the place the incident actually happened.
- **P47** — `astream_events(version="v2")` emits 2,000+ events per invocation. A raw dump is 50 MB and unreadable; an SSE viewer crashes on it.
- **P67** — `astream_log()` is soft-deprecated in 1.0. Diagnostic tooling built on it breaks on the next minor version.

The skill's answer: assemble the manifest, capture v2 events with a whitelist
(drop lifecycle noise, keep `on_chat_model_stream` / `on_tool_*` / any `*_error`
event), attach `DebugCallbackHandler` via `config["callbacks"]` at invoke time,
pull the LangSmith URL from the active `RunTree`, run the sanitization pass,
tar it up. Pinned: `langchain-core 1.0.x`, `langgraph 1.0.x`, `langsmith 0.1.x`.
Pain-catalog anchors: P01, P28, P47, P67.

## Prerequisites

- Python 3.10+
- `langchain-core >= 1.0, < 2.0`, `langgraph >= 1.0, < 2.0`
- `langsmith >= 0.1.40` for `RunTree` access
- Active LangSmith project (`LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY=...`,
  `LANGSMITH_PROJECT=...`) — canonical 1.0 env-var names, not the legacy
  `LANGCHAIN_TRACING_V2` (see P26).
- Write access to a staging directory outside the repo tree.

## Instructions

### Step 1 — Assemble the environment manifest

Record the runtime snapshot that lets a colleague reproduce on a different
host. See [env-manifest-template.md](references/env-manifest-template.md) for
the exact YAML shape.

```python
import platform, sys, os, subprocess, datetime

RELEVANT = [
    "langchain-core", "langchain", "langgraph",
    "langchain-anthropic", "langchain-openai",
    "langsmith", "anthropic", "openai", "pydantic",
]

def pip_show(name: str) -> str | None:
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "pip", "show", name],
            stderr=subprocess.DEVNULL, text=True,
        )
        for line in out.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
    except subprocess.CalledProcessError:
        return None

def build_manifest(incident_id: str, invoke_meta: dict) -> dict:
    return {
        "bundle_spec_version": "1.0",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "incident_id": incident_id,
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
        },
        "packages": [
            {"name": n, "version": pip_show(n)}
            for n in RELEVANT if pip_show(n) is not None
        ],
        # NAMES only — never values. Sanitized by design (P27 posture).
        "env_var_names_present": sorted(
            k for k in os.environ
            if k.startswith(("LANGSMITH_", "LANGCHAIN_", "ANTHROPIC_", "OPENAI_", "GOOGLE_"))
        ),
        "invocation": invoke_meta,
    }
```

Record env-var *names*, not values. Values go through the sanitization pass in
Step 5, but the safest design is never to capture them.

### Step 2 — Capture `astream_events(version="v2")` with a filter

Raw v2 events flood 2,000+ per invocation (P47). A server-side filter drops
lifecycle noise (`on_chain_start`/`on_chain_end`) and keeps model, tool, and
error events — yielding 50-200 events per invocation and a ~500 KB JSONL.

```python
import json, itertools
from pathlib import Path

KEEP = {
    "on_chat_model_start", "on_chat_model_end",
    "on_tool_start", "on_tool_end", "on_tool_error",
    "on_retriever_start", "on_retriever_end",
    "on_custom_event",
}
# Additionally: any event whose name ends in "_error"
# Additionally: 1-in-10 sampled on_chat_model_stream (for response reconstruction)

async def capture_events(graph, inputs, config, out_path: Path) -> int:
    sample = itertools.count()
    written = 0
    with out_path.open("w") as f:
        async for evt in graph.astream_events(inputs, config=config, version="v2"):
            name = evt["event"]
            if name == "on_chat_model_stream" and next(sample) % 10 != 0:
                continue
            if name not in KEEP and not name.endswith("_error"):
                continue
            f.write(json.dumps({
                "event": name,
                "name": evt.get("name"),
                "run_id": str(evt.get("run_id")),
                "tags": evt.get("tags"),
                "metadata": evt.get("metadata"),
                "data": _json_safe(evt.get("data", {})),
            }, default=str) + "\n")
            written += 1
    return written
```

Never use `astream_log()` (P67). The full event taxonomy and `_json_safe`
helper live in [astream-events-capture.md](references/astream-events-capture.md).

### Step 3 — Attach callbacks that propagate into subgraphs (P28)

Callbacks bound via `Runnable.with_config(callbacks=[...])` fire on the outer
chain only. They go silent the moment the graph crosses into a subgraph or an
inner `create_react_agent` loop — exactly where incidents happen. Pass them via
`config["callbacks"]` at invoke time instead.

```python
from langchain_core.callbacks import BaseCallbackHandler

class DebugCallbackHandler(BaseCallbackHandler):
    def __init__(self): self.records: list[dict] = []
    def on_tool_start(self, serialized, input_str, *, run_id, parent_run_id=None, **kw):
        self.records.append({
            "kind": "tool_start", "run_id": str(run_id),
            "parent_run_id": str(parent_run_id) if parent_run_id else None,
            "tool": serialized.get("name"), "input": input_str[:500],
        })
    def on_tool_error(self, error, *, run_id, **kw):
        self.records.append({
            "kind": "tool_error", "run_id": str(run_id),
            "error_type": type(error).__name__, "error_message": str(error)[:1000],
        })

debug = DebugCallbackHandler()

result = await agent.ainvoke(
    {"messages": [("user", reproducer_prompt)]},
    config={
        "configurable": {"thread_id": thread_id},
        "callbacks": [debug],                      # propagates into subgraphs
        "tags": ["debug-bundle", incident_id],
        "metadata": {"incident_id": incident_id},
    },
)
```

The full handler (LLM + retriever + tool lifecycle) and a propagation smoke
test live in [callback-propagation.md](references/callback-propagation.md).

### Step 4 — Record the LangSmith trace URL

A trace URL is cheaper than any local artifact — one click and the colleague
sees the full run with latency, token counts, and input/output per node. Pull
it from the active `RunTree` if you have a live handle; otherwise construct it
from the invoke's `run_id`:

```python
from langsmith.run_helpers import get_current_run_tree

def capture_langsmith_url() -> str | None:
    rt = get_current_run_tree()
    if rt is None:
        return None  # tracing not enabled or run already closed
    return rt.get_url()  # https://smith.langchain.com/o/.../r/<run_id>

# Write to langsmith.url in the bundle:
url = capture_langsmith_url()
(staging / "langsmith.url").write_text(url or "(no trace URL available)")
```

The URL requires the colleague to have access to the LangSmith project. For
public sharing, use `RunTree.share()` to generate a public snapshot URL. Never
paste a non-shared URL into a public Discord thread — the page redirects to a
login and leaks the project name.

### Step 5 — Sanitize before packaging

Every file in the staging dir passes through the redaction pass **before** the
tar.gz is written. This is the last-mile guard; upstream redaction middleware
should already have caught credential material, but the bundle cannot assume
that.

```python
import re

PATTERNS = [
    ("openai_key",    r"sk-proj-[A-Za-z0-9_-]{16,}|sk-[A-Za-z0-9_-]{32,}"),
    ("anthropic_key", r"sk-ant-[A-Za-z0-9_-]{16,}"),
    ("google_key",    r"AIza[A-Za-z0-9_-]{35}"),
    ("langsmith_key", r"lsv2_(?:pt|sk)_[A-Za-z0-9]{32,}"),
    ("bearer",        r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{20,}"),
    ("db_uri",        r"[a-z]+://[^:/\s]+:[^@\s]+@[^/\s]+"),
    ("private_key",   r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"),
]

def sanitize_file(path, patterns=PATTERNS) -> dict[str, int]:
    text, counts = path.read_text(), {}
    for name, pat in patterns:
        new, n = re.subn(pat, f"[REDACTED:{name}]", text)
        if n: counts[name] = n; text = new
    path.write_text(text)
    return counts
```

The full pattern catalog (credentials, session tokens, PII, internal URLs) and
the pre-upload `tar -xzf ... && grep` scan live in
[sanitization-checklist.md](references/sanitization-checklist.md). For the
production-grade upstream redaction middleware, use the forthcoming
`langchain-security-basics` skill.

### Step 6 — Bundle with an index

Write a top-level `MANIFEST.yaml` that describes every file and records the
sanitization summary. Then tar.gz the staging dir.

```python
import tarfile, yaml
from pathlib import Path

def write_bundle(staging: Path, manifest: dict, sanitize_report: dict,
                 out: Path, events_count: int, callback_count: int) -> Path:
    index = {
        "bundle_spec_version": "1.0",
        "incident_id": manifest["incident_id"],
        "generated_at": manifest["generated_at"],
        "files": [
            {"name": "manifest.yaml",  "purpose": "env + version snapshot"},
            {"name": "events.jsonl",   "purpose": f"filtered astream_events(v2), {events_count} events"},
            {"name": "callbacks.txt",  "purpose": f"DebugCallbackHandler records, {callback_count} entries"},
            {"name": "langsmith.url",  "purpose": "trace URL (shared) or (none)"},
            {"name": "notes.txt",      "purpose": "free-form engineer notes, sanitized"},
        ],
        "sanitization": sanitize_report,
    }
    (staging / "MANIFEST.yaml").write_text(yaml.safe_dump(index, sort_keys=False))
    with tarfile.open(out, "w:gz") as tar:
        tar.add(staging, arcname=out.stem)
    return out

bundle = write_bundle(
    staging=Path("/tmp/bundle-INC-2026-0421-A"),
    manifest=m, sanitize_report=report,
    out=Path("/tmp/bundle-INC-2026-0421-A.tar.gz"),
    events_count=n_events, callback_count=len(debug.records),
)
```

## Output

| File in bundle | Purpose | Source | Sanitization step |
|---|---|---|---|
| `MANIFEST.yaml`   | Index + file descriptions + redaction counts | Step 6 | N/A (authored) |
| `manifest.yaml`   | Python/OS/package/env-var-name snapshot      | Step 1 | Run pass; env-var *names* only by design |
| `events.jsonl`    | Filtered `astream_events(v2)` — model, tool, error events | Step 2 | Per-line regex redaction |
| `callbacks.txt`   | `DebugCallbackHandler` records (JSONL)       | Step 3 | Per-line regex redaction |
| `langsmith.url`   | `RunTree.get_url()` (shared if public)       | Step 4 | Verify no embedded API key param |
| `notes.txt`       | Engineer's free-form observations            | Manual | Per-line regex redaction |

Typical size: **1-10 MB** compressed. Typical event count after filter: **50-200**
per invocation (down from 2,000+ raw). Bundle is self-contained — no external
dependencies beyond `tar -xzf` and a text editor.

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `events.jsonl` has no subgraph events | Callbacks bound via `Runnable.with_config(callbacks=[...])` instead of `config["callbacks"]` (P28) | Move callbacks to invoke-time config; see [callback-propagation.md](references/callback-propagation.md) |
| `events.jsonl` is 50 MB+ | Filter not applied or `on_chain_*` events not excluded (P47) | Enforce `KEEP` whitelist and 1:10 streaming sample; Step 2 |
| `DeprecationWarning: astream_log is deprecated` | Captured via `astream_log()` instead of `astream_events(v2)` (P67) | Migrate to `graph.astream_events(..., version="v2")` |
| `response_metadata["token_usage"]` empty in `on_chat_model_end` records | Read before stream closed (P01) | Aggregate from `on_chat_model_stream` chunks with `usage_metadata`; see model-inference skill |
| `langsmith.url` is empty | Tracing not enabled or `get_current_run_tree()` returned `None` | Set `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY=...`, `LANGSMITH_PROJECT=...` (P26) |
| `TypeError: Object of type X is not JSON serializable` in events capture | Tool returned a custom class with no `.model_dump()` | Extend `_json_safe` in [astream-events-capture.md](references/astream-events-capture.md) |
| Pre-upload scan finds `sk-...` pattern | Upstream middleware missed a key, or regex too lax | Add specific pattern to `PATTERNS`, re-run Step 5, re-archive |

## Examples

### Triage decision tree — "which file in the bundle do I read first?"

Give a colleague this table with the bundle so they know where to start:

| Symptom in the ticket | Start with | Then |
|---|---|---|
| "Agent looped forever" / `GraphRecursionError` | `events.jsonl` (filter `on_tool_start`) | `callbacks.txt` for tool→tool timing |
| "Tool returned empty" / "Could not find the answer" (P09) | `events.jsonl` (grep `on_tool_error`) | `callbacks.txt` for the parent `run_id` |
| "Wrong answer, correct tool called" | `events.jsonl` (grep `on_chat_model_start` + last `on_tool_end`) | LangSmith trace URL for full context |
| "Token count wrong in dashboard" (P01, P25) | `events.jsonl` `on_chat_model_stream` chunks | `manifest.yaml` for retry middleware presence |
| "Works locally, fails in prod" | `manifest.yaml` diff against local | `events.jsonl` for env-specific branches |
| "Memory resets between turns" (P16) | `manifest.yaml` → `langgraph.thread_id` present? | `events.jsonl` → checkpointer restore events |

### Incident-driven capture — reproducing and bundling in one script

See [callback-propagation.md](references/callback-propagation.md) for the full
invoke-time config pattern. The skeleton:

```python
async def reproduce_and_bundle(agent, reproducer, incident_id: str) -> Path:
    debug = DebugCallbackHandler()
    staging = Path(f"/tmp/bundle-{incident_id}"); staging.mkdir(exist_ok=True)

    try:
        result = await agent.ainvoke(
            reproducer,
            config={"configurable": {"thread_id": f"debug-{incident_id}"},
                    "callbacks": [debug], "tags": ["debug-bundle", incident_id]},
        )
        invoke_meta = {"status": "success"}
    except Exception as e:
        invoke_meta = {"status": "error",
                       "error_class": type(e).__name__, "error_message": str(e)[:500]}

    # Step 2 — capture events (separate invocation with same inputs OR replay
    # from RunTree if already in LangSmith)
    n_events = await capture_events(agent, reproducer, {...}, staging / "events.jsonl")

    # Step 1 — manifest, Step 3 — callbacks, Step 4 — LangSmith URL, Step 5 — sanitize
    # Step 6 — bundle
    return write_bundle(staging, build_manifest(incident_id, invoke_meta), ..., ...)
```

### Discord / forum bug report checklist

Before posting to the LangChain Discord or GitHub Issues:

1. Run the pre-upload `tar -xzf && grep` scan ([sanitization-checklist.md](references/sanitization-checklist.md))
2. Confirm `langsmith.url` is a *shared* URL (public), not a project-internal one
3. Strip the `incident_id` if it maps to internal ticket numbers you cannot disclose
4. Include in the post: bundle attachment, a 3-sentence symptom description, the
   exact reproducer prompt, the first line of `MANIFEST.yaml` (spec version
   and versions of `langchain-core` + `langgraph`)

## Resources

- [LangChain callbacks concept](https://python.langchain.com/docs/concepts/callbacks/)
- [`astream_events` v2](https://python.langchain.com/docs/how_to/streaming/#using-stream-events)
- [LangSmith observability](https://docs.smith.langchain.com/observability)
- [LangSmith `RunTree` API](https://docs.smith.langchain.com/reference/python/run_helpers)
- [LangGraph streaming modes](https://langchain-ai.github.io/langgraph/how-tos/streaming/)
- [LangChain 1.0 release notes](https://blog.langchain.com/langchain-langgraph-1dot0/)
- Pack pain catalog: `docs/pain-catalog.md` (entries P01, P26, P28, P47, P67)
- Companion skills: `langchain-observability`, `langchain-security-basics` (upstream redaction middleware), `langchain-model-inference` (token accounting)
