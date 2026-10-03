---
name: blog-editorial-calendar
description: "Run your blog like a queue, not a guessing game. This skill is the orchestration layer on top of blog-topic-research and seo-blog-writer: it keeps an evidence-backed backlog, picks the next topic so your corpus drifts toward the cluster + format mix you defined, schedules posts into a rolling daily cadence, and marks them done — autonomously, two posts a day if you want. It scores every pick by how far each topic cluster is from its target weight (so you never end up with 40 troubleshooting posts and no comparisons), reconciles the backlog against what's actually live on your CMS, and auto-refills by calling blog-topic-research when the queue runs dry. Platform-agnostic: it drives whatever publish adapter seo-blog-writer is configured for (Ghost, WordPress, static site). Built for founders, indie hackers, and content teams who want a hands-off long-tail SEO pipeline that publishes on a schedule and stays balanced. Trigger when the user says: 'what should I write next', 'pick the next topic', 'schedule the next N posts', 'editorial calendar status', 'add this to the backlog', 'mark this post done', or any variant of running a recurring publish cadence."
version: 1.0.0
emoji: "🗓️"
homepage: https://github.com/AutomateLab-tech/publishing-skills
allowed-tools: WebSearch, WebFetch, Read, Write, Bash
author: AutomateLab <hello@automatelab.tech>
license: MIT-0
compatibility: Designed for Claude Code
tags: [seo, content, publishing, editorial, blogging]
metadata:
  openclaw:
    requires:
      bins: []
---

# blog-editorial-calendar

The scheduler and topic-picker that sits on top of the other two skills. `blog-topic-research` fills a backlog with evidence-backed topics; `seo-blog-writer` turns one topic into a published post. This skill decides **which** topic to write **next** and **when** to publish it, so the corpus drifts toward the content mix you defined instead of whatever you felt like writing that day.

```
/blog-editorial-calendar next [N]                          # pick + write + auto-schedule into the next slots
/blog-editorial-calendar next [N] --draft                  # pick + write, leave as a draft (no schedule)
/blog-editorial-calendar next [N] <slot>[, <slot> ...]     # pick + write + schedule each explicit slot
/blog-editorial-calendar status
/blog-editorial-calendar add "<topic>" --cluster <c> --format <f> [--priority N] [--notes "..."]
/blog-editorial-calendar mark-done <id-or-slug>
/blog-editorial-calendar sync                              # reconcile the backlog against what's live on your CMS
```

`next` always writes. With no flags it schedules each post into the next free slot of the rolling cadence; with `--draft` it writes but leaves the post as a draft; with explicit slot args it uses the named windows. The author and target platform come from `config.json` (see below) — this skill never overrides them.

---

## Configuration — `config.json`

Everything site-specific lives in `skills/blog-editorial-calendar/config.json`, **not** in this file. Edit it once for your blog; the reference code below reads it. Example:

```json
{
  "target_platform": "ghost",
  "author": "Editorial",
  "cadence": {
    "posts_per_day": 2,
    "slots_utc": [[6, 0, 11, 59], [18, 0, 22, 59]]
  },
  "cluster_targets": {
    "core-product": 0.30,
    "integrations": 0.25,
    "use-cases":    0.25,
    "ecosystem":    0.20
  },
  "format_targets": {
    "how-to-fix": 0.35, "x-vs-y": 0.15, "how-to-connect": 0.10,
    "how-to-automate": 0.10, "use-case": 0.10, "listicle": 0.07,
    "migration": 0.05, "release-recap": 0.05, "what-is": 0.03
  },
  "cluster_tag_map": {
    "core-product": ["Product"],
    "integrations": ["Integrations"],
    "use-cases":    ["Use Cases"],
    "ecosystem":    ["Ecosystem"]
  }
}
```

- **`cluster_targets`** — your topic buckets and the share of the corpus each should hold. The names are yours; the example above is a placeholder. They must sum to ~1.0. This is the primary balancing axis.
- **`format_targets`** — post-shape mix (universal; the defaults above are sensible for a how-to blog). Secondary axis.
- **`cluster_tag_map`** — maps each cluster to the CMS tag(s) `sync` uses to classify live posts.
- **`cadence`** — how many posts/day and the UTC windows they fall into.
- **`target_platform` / `author`** — passed straight through to `seo-blog-writer`.

---

## Status model — the dedup gate

The backlog is the single source of truth for what topics are taken. Every topic flows through three statuses:

| Status | Meaning | Set by |
|---|---|---|
| `queued` | Researched and ready to write | `add`, or `blog-topic-research --append` |
| `in-progress` | Writer has started; publish not yet complete | `seo-blog-writer` at start (auto-creates the row if missing) |
| `done` | Uploaded to the CMS in any state — draft, scheduled, or published | `seo-blog-writer` the moment the publish call returns 2xx |

Plus `killed` for topics intentionally dropped (kept so research doesn't re-add them).

**This vocabulary is the entire dedup mechanism.** The picker filters on `status == "queued"` only — it never needs a title-similarity match at pick time. As long as the writer locks at start and flips at publish, the picker cannot pick a topic that's already in flight or already shipped. If the writer crashes mid-flow, revert the orphan row to `queued` (with a `last_error` note) so the topic re-enters the pool.

---

## Data files

`backlog.json` lives at `skills/blog-editorial-calendar/backlog.json`. Schema for a **queued** entry:

```json
{
  "topics": [
    {
      "id": "self-host-on-a-vps",
      "topic": "Self-hosting <product> on a $5 VPS: complete 2026 setup walkthrough",
      "cluster": "core-product",
      "format": "how-to-automate",
      "priority": 1,
      "status": "queued",
      "tags": ["Tutorial", "Product"],
      "notes": "anchor post - long, link-worthy",
      "added_at": "2026-01-04",
      "published_slug": null,
      "published_at": null,
      "research_proof": {
        "demand_signals": [
          {"type": "github_issue", "url": "https://...", "evidence": "verbatim issue title"},
          {"type": "keyword_data", "url": "dataforseo:labs/keyword_overview", "evidence": "\"self host <product> vps\" search_volume=210/mo, keyword_difficulty=12"}
        ],
        "primary_sources": ["https://docs..."],
        "keywords": ["primary keyword", "lsi 1", "lsi 2"],
        "problem_summary": "1-2 factual sentences in writer-voice. Empty string if not derivable.",
        "confirmed_fixes": [{"kernel": "short fix phrase", "source": "https://..."}],
        "version_context": "v1.65+ or null",
        "question_variants": ["paraphrase 1", "paraphrase 2"]
      }
    }
  ]
}
```

The `research_proof` blob is written by `blog-topic-research --append` and carries the writer a vetted scaffold so its research step telescopes. **It is stripped on done-flip** (see `mark-done`) so the file stays small across hundreds of posts.

Field domains:

| Field | Allowed values |
|---|---|
| `cluster` | any key in `config.json` → `cluster_targets` |
| `format` | `how-to-fix`, `how-to-connect`, `how-to-automate`, `x-vs-y`, `what-is`, `use-case`, `listicle`, `migration`, `release-recap` |
| `status` | `queued`, `in-progress`, `done`, `killed` |
| `priority` | integer; lower = pick sooner; default 100 (tiebreaker only) |

---

## Preflight: auto-sync (every invocation)

Before running the requested command, refresh the local index of what's live on your CMS, then reconcile the backlog against it. The writer's platform adapter already knows how to list posts — reuse that. Write the result to `state/published-index.json` (gitignored): one row per post with `slug`, `title`, `status`, `published_at`, `tags`. All three CMS states — `published`, `scheduled`, `draft` — count as "this topic is taken".

```bash
# Platform-neutral: ask seo-blog-writer's configured adapter to list posts.
# (Ghost example — substitute your platform's list endpoint.)
# GET /ghost/api/admin/posts/?limit=all&fields=id,slug,title,status,published_at&include=tags
```

After the index refreshes, run the [sync](#command-sync) reconciliation. If the list call fails (credentials missing, network error), print `sync skipped: <reason>` and continue against the stale index — `status` is fine on stale data, and the writer's start-of-run lock catches any race the index would have.

**Write-through:** when the writer flips a backlog row to `done` at publish time, it should also upsert the new post into `state/published-index.json` so the index stays consistent without waiting for the next preflight.

---

## Command: `next` — dispatch

Three modes, detected in this order:

1. Scan args for `morning` / `afternoon` / `evening` (incl. plurals) → **slot mode**.
2. Else if `--draft` is present → **draft mode** (write, leave as a draft).
3. Otherwise → **auto-schedule mode** (the default).

| Input | Result |
|---|---|
| `next` | 1 post, scheduled in the next free slot |
| `next 4` | 4 posts across the next slots |
| `next 1 --draft` | 1 post, left as a draft |
| `next today evening` | 1 post in tonight's evening window |
| `next 3 mornings` | 3 posts in the next 3 morning slots |

Never silently fall back from slot mode to auto-schedule. If a slot keyword is present and date parsing fails, abort with a clear error.

### Auto-schedule mode (default)

Walks the cadence forward from the latest scheduled (or, if none, published) post. With `posts_per_day: 2` and the two default windows, slots alternate morning → evening → morning → evening, every day. For each of N picks:

1. Compute the next slot timestamp (parser below).
2. Run [scoring](#scoring) to pick one topic. If the queue is empty, trigger [backlog refill](#backlog-refill).
3. Mark it `in-progress` and save (belt-and-suspenders; the writer also locks at its start).
4. Invoke `/seo-blog-writer "<topic>" --target <platform> --publish-at <iso> --author "<author>"`.
5. The writer flips the row to `done`, sets `published_slug` + `published_at` when the publish call returns 2xx. No `mark-done` needed in the happy path.
6. On failure the writer reverts the row to `queued` with `last_error` and the loop **stops** — don't grind through the backlog while one topic is broken.

### Cadence reference parser

Prints N ISO-8601 UTC timestamps, chronological, one per line.

```bash
python3 - "<N>" <<'PY'
import datetime, json, pathlib, random, sys

N = int(sys.argv[1])
base = pathlib.Path("skills/blog-editorial-calendar")
cfg  = json.loads((base / "config.json").read_text())
SLOTS = [tuple(s) for s in cfg["cadence"]["slots_utc"]]   # [(sh,sm,eh,em), ...]
now = datetime.datetime.now(datetime.timezone.utc)

data = json.loads((base / "backlog.json").read_text())
done_pub = [t for t in data["topics"]
            if t.get("status") == "done" and t.get("published_at")]

def window(day, idx):
    sh, sm, eh, em = SLOTS[idx]
    start = datetime.datetime(day.year, day.month, day.day, sh, sm, tzinfo=datetime.timezone.utc)
    end   = datetime.datetime(day.year, day.month, day.day, eh, em, tzinfo=datetime.timezone.utc)
    return start, end

if done_pub:
    latest = max(t["published_at"] for t in done_pub)
    last_dt = datetime.datetime.fromisoformat(latest.replace("Z", "+00:00"))
    # find which slot the last post fell in, then advance one
    idx = max((i for i, (sh, *_ ) in enumerate(SLOTS) if last_dt.hour >= sh), default=0)
    if idx + 1 < len(SLOTS):
        cur_day, slot_idx = last_dt.date(), idx + 1
    else:
        cur_day, slot_idx = last_dt.date() + datetime.timedelta(days=1), 0
else:
    cur_day, slot_idx = now.date(), 0

stamps, guard = [], 0
while len(stamps) < N and guard < 365 * len(SLOTS) + len(SLOTS):
    guard += 1
    start, end = window(cur_day, slot_idx)
    if end > now:
        floor = max(start, now + datetime.timedelta(minutes=2))
        span = max(0, int((end - floor).total_seconds()))
        stamps.append(floor + datetime.timedelta(seconds=random.randint(0, span)))
    slot_idx += 1
    if slot_idx >= len(SLOTS):
        slot_idx = 0
        cur_day += datetime.timedelta(days=1)

if len(stamps) < N:
    sys.exit(f"could not fit {N} slots within a year")
for t in stamps:
    print(t.isoformat().replace("+00:00", "Z"))
PY
```

### Draft mode

Same loop, but invoke `/seo-blog-writer "<topic>" --draft` instead of `--publish-at`. No slot timestamp is reserved.

### Slot mode

Parse explicit windows (`today evening`, `7 May morning`, `mornings`, etc.), sort timestamps ascending, then run the same pick → write loop per slot. If a *singular* slot ends in the past at run time, abort before writing anything; plural slots auto-skip past windows.

---

## Scoring

Two-stage: cluster first (primary balancing axis), then format inside the chosen cluster (secondary axis). Both targets come from `config.json`.

```bash
python3 - "<N>" <<'PY'
import json, pathlib, sys
N = int(sys.argv[1])
base = pathlib.Path("skills/blog-editorial-calendar")
cfg  = json.loads((base / "config.json").read_text())
CLUSTER_TARGET = cfg["cluster_targets"]
FORMAT_TARGET  = cfg["format_targets"]

data   = json.loads((base / "backlog.json").read_text())
topics = data["topics"]
done   = [t for t in topics if t["status"] == "done"]
queued = [t for t in topics if t["status"] == "queued"]

c_counts = {c: 0 for c in CLUSTER_TARGET}
f_counts = {f: 0 for f in FORMAT_TARGET}
for t in done:
    c_counts[t["cluster"]] = c_counts.get(t["cluster"], 0) + 1
    f_counts[t["format"]]  = f_counts.get(t["format"], 0)  + 1
total = sum(c_counts.values())

c_deficit = {c: CLUSTER_TARGET[c] - (c_counts[c] / max(total, 1)) for c in CLUSTER_TARGET}
f_deficit = {f: FORMAT_TARGET[f]  - (f_counts.get(f, 0) / max(total, 1)) for f in FORMAT_TARGET}

recent = sorted([t for t in done if t.get("published_at")],
                key=lambda t: t["published_at"], reverse=True)
last_cluster = recent[0]["cluster"] if recent else None
last_format  = recent[0]["format"]  if recent else None

picks = []
for _ in range(N):
    c_score = {c: c_deficit[c] - (0.10 if c == last_cluster else 0) for c in CLUSTER_TARGET}
    avail = {c: [t for t in queued if t["cluster"] == c and t not in picks] for c in CLUSTER_TARGET}
    chosen = None
    for c in sorted(CLUSTER_TARGET, key=lambda c: c_score[c], reverse=True):
        if not avail[c]:
            continue
        def key(t):
            fmt = t["format"]
            return (-(f_deficit.get(fmt, 0) - (0.05 if fmt == last_format else 0)), t.get("priority", 100))
        chosen = sorted(avail[c], key=key)[0]
        break
    if not chosen:
        break
    picks.append(chosen)
    last_cluster, last_format = chosen["cluster"], chosen["format"]

print(f"Current mix ({total} done):")
for c in CLUSTER_TARGET:
    pct = (c_counts[c] / max(total, 1)) * 100
    print(f"  {c:16s} {c_counts[c]:3d}  ({pct:4.1f}% / target {CLUSTER_TARGET[c]*100:.0f}%)  deficit {c_deficit[c]*100:+5.1f}pp")
print(f"\nNext {len(picks)} pick(s):")
for i, pk in enumerate(picks, 1):
    print(f"  {i}. [{pk['cluster']:14s}/{pk['format']:14s}] {pk['topic']}  (id={pk['id']})")
PY
```

The `-0.10` (cluster) and `-0.05` (format) penalties stop the picker from stacking the same cluster/format two posts in a row. `priority` is only a tiebreaker.

---

## Backlog refill

If scoring returns no pick — `queued` is empty across every cluster — pause and invoke `/blog-topic-research 10 --append`, which validates candidates and prompts for confirmation before writing them as `queued` rows. Then re-run scoring and continue. Refill fires **at most once** per `next N` invocation; if the queue empties again in the same call, halt with a shortfall message rather than re-prompting. This is a fallback, not a routine pre-fetch — keep the queue ahead with proactive research runs.

---

## Command: `status`

Print queued / in-progress / done counts per cluster and format, current-vs-target mix, age of the oldest queued item, and count of stale (>30-day) queued items. Reuses the counting code from scoring.

## Command: `add`

Validate `cluster` is a key in `config.json`, `format` is in the format set, and `id` is unique (kebab-case from the topic, stop-words stripped, ≤60 chars). Append and save. Refuse if any existing row already has that `id`.

```python
import re
STOP = {"the","a","an","for","with","in","to","of","on","and","or","is","are"}
slug = "-".join(t for t in re.findall(r"[a-z0-9]+", topic.lower()) if t not in STOP)[:60].rstrip("-")
```

## Command: `mark-done`

In the happy path the writer flips the row automatically. This is the manual fallback (post made directly in the CMS, or a writer that crashed after publish but before the flip). Find by `id` or `published_slug`, set `status = "done"`, and **strip the heavy fields** so the backlog stays lean.

**Done-row schema** (only these kept): `id`, `topic`, `cluster`, `format`, `tags`, `status`, `published_slug`, `published_at`. Removed on flip: `priority`, `notes`, `added_at`, `research_proof`, `last_error`.

```bash
python3 - "<id-or-slug>" "<actual-slug>" <<'PY'
import json, pathlib, datetime, sys
key, slug = sys.argv[1], sys.argv[2]
p = pathlib.Path("skills/blog-editorial-calendar/backlog.json")
data = json.loads(p.read_text())
KEEP = {"id","topic","cluster","format","tags","status","published_slug","published_at"}
hit = next((t for t in data["topics"] if t["id"] == key or t.get("published_slug") == key), None)
if not hit:
    sys.exit(f"not found: {key}")
hit["status"] = "done"
hit["published_slug"] = slug
hit["published_at"] = hit.get("published_at") or datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")
for k in list(hit):
    if k not in KEEP:
        del hit[k]
p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
print(f"marked done: {hit['id']} -> {slug}")
PY
```

## Command: `sync`

Reconcile the backlog against `state/published-index.json` (refreshed in preflight). Auto-runs before every command.

1. For each live post, match a backlog row by `published_slug`, else by Jaccard token overlap ≥0.7 against the title (slug match is authoritative).
2. **Matched + stale** (not `done`, or slug differs) → set `done`, fill `published_slug` + `published_at`, strip heavy fields.
3. **Matched + `killed`** → surface, don't auto-revive.
4. **Unmatched live post** → auto-import as a `done` row, deriving `cluster` from the primary tag (via `cluster_tag_map`), `format` heuristically from the title (` vs ` → `x-vs-y`; `what is` → `what-is`; `fix`/`error` → `how-to-fix`; `connect`/`integrate` → `how-to-connect`; default → `how-to-automate`). If no tag matches a cluster, set `cluster: "?"` and surface for manual fix.
5. **Backlog `done` rows whose slug is in none of the live sets** → surface as missing (probably deleted in the CMS).

Diff-only output: `~` updated, `+` auto-imported, `?` ambiguous, `-` missing. Empty diff → `sync: backlog matches CMS`.

---

## What this skill does NOT do

- **Does not draft posts.** It delegates the whole writing pipeline to `seo-blog-writer`. It's a scheduler around that, not a replacement.
- **Does not pick the platform or author.** Both come from `config.json` and pass through to the writer untouched.
- **Does not weight format above cluster.** Cluster mix is primary; format is secondary, applied within the chosen cluster.
- **Does not run more than one loop at a time.** The `in-progress` status is the lock; a second `next` while one is in flight should detect it and refuse.
- **Does not touch git.** Treat each `add` / `mark-done` / `next` like a normal source edit; you commit.
- **Does not refill silently.** When the queue empties, refill calls `blog-topic-research`, which shows candidates and asks before writing them. Fires at most once per `next N`.

---

## One-command summary

```
/blog-editorial-calendar next [N]                      # pick -> write -> schedule into the next cadence slots
/blog-editorial-calendar next [N] --draft              # pick -> write -> leave as a draft
/blog-editorial-calendar next [N] <slot>[, <slot>...]  # pick -> write -> schedule each explicit slot
```

1. Load `backlog.json` + `config.json`. Bucket queued/done by cluster and format.
2. Compute deficit vs your target weights.
3. Penalize the most-recently-done cluster (−0.10) and format (−0.05) to avoid stacking.
4. Pick the highest-scoring cluster with queued items, then the topic whose format has the largest deficit; `priority` breaks ties. If the queue is empty, refill once via `blog-topic-research`.
5. Compute the next slot timestamp (auto-schedule), use the explicit slot (slot mode), or skip timestamping (draft mode).
6. Lock to `in-progress`, invoke `seo-blog-writer`; it flips the row to `done` on a 2xx publish. On failure it reverts to `queued` and the loop halts.
7. For N>1, repeat with the just-picked cluster/format treated as "most recent" and advance the cadence.
```
