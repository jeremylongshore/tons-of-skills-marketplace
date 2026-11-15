---
title: "45-Minute Pipeline Timeout: Count Passes, Not Payload Size"
description: "A trimmed canary with one fewer reviewer and no tool rounds cut tokens from 104M to 30M and still hit the 45-minute ceiling. Count passes, not payload size."
date: "2026-11-14"
tags: ["ai-agents", "automation", "ci-cd", "claude-code"]
featured: false
canonical: "https://startaitools.com/posts/timeout-is-a-sequence-problem-not-a-context-problem/"
---
A scheduled multi-agent writing pipeline runs against a 45-minute wall-clock ceiling, and this post hands you the three numbers worth measuring, the reason shrinking each request did not help, and the evidence that the simple pipeline is the weaker writer. Three runs in one day's telemetry hit that ceiling and timed out, so the obvious lever was to make every model request smaller.

We trimmed the context and ran one reviewer fewer. Token volume fell about 70 percent, and the run still timed out.

That mismatch is the finding. The payload did not order the outcomes. The sequence was how many agent passes ran and how slow each one was.

## What the pipeline costs

Here is one week of seven posts, measured in the run's own request logs by Claude Opus 5.5, the model that ran the session, working inside intent-os (the company's internal operations and documentation repo):

| Component | Tokens | What it is |
|---|---|---|
| Cache re-reads | 196.5M | the same context sent again, billed at about a tenth of the normal input price |
| Cache writes | 7.8M | the first time that context is stored |
| Output | 0.9M | what the models actually wrote |
| 7 posts | ~205M | about $105, about $15 each |

A cache re-read is the same context sent to the model again on a later request. A cache write is the first time that context is stored. The API bills a re-read at roughly a tenth of the normal input price, which is why a pipeline that resends the same context over and over is dominated by them.

About $15 per post at Claude API prices for that week, and one post a day at that rate is roughly $450 a month. That week is not the same set of runs as the table below, and the two sets of numbers do not line up: the table's four rows carry roughly 220M to 245M tokens between them, against about 205M for the whole week. Two caveats on that number. The $105 includes a couple of failed attempts, and my own chat ran on Opus in the same windows, so the telemetry cannot separate it out. $15 is the upper end, not the floor.

The shape of the bill matters more than the total. 196.5M of those tokens are cache re-reads, and each post re-reads a huge context about 100 to 170 times. Only 0.9M of those 205M tokens were output. The pipeline is re-reading the same context over and over.

## What the trim changed

Before and after, from the same day's telemetry:

| Run | Setup | Avg context per request | Total tokens | Result |
|---|---|---|---|---|
| 02:00 | old, MiniMax | 179k | 104M | timed out |
| 04:00 slot, started 04:18 | old, MiniMax | 142k | 76M | timed out |
| canary | trimmed, MiniMax | 140k | 30M (writer + 2 reviewers) | timed out at 45 min, nearly finished |
| Opus runs | old, Claude Opus 5.5 | 155-214k | 11-35M | landed |

Read the third row and the fourth row together. The trimmed canary carried the smallest context per request of the four and still died at the ceiling. The Opus runs that landed, on the old and fatter setup, carried the fattest requests of any run that landed, up to 214k against the canary's 140k. Context size did not order the outcomes. Those two rows differ in three ways at once, model, trimming and agent count, so read the pair as a correlation and not as a controlled comparison. The landed runs spent 11M to 35M tokens, and the canary that missed the ceiling spent 30M, inside that same band. Token volume does not predict the timeout cleanly. A 30M run missed while a 35M run landed, and the two largest runs, 76M and 104M, both missed.

What the trim removed was the repo's ambient CLAUDE.md instruction files and its MCP servers, the external tools an agent can call. The writer's own brief stayed, and so did the skill. The writer runs fine without them. The skill loaded, the reviewer agents ran, the post and its sign-offs were written, and the session log has it reaching the site build before the ceiling killed it. So the context the writer was carrying was not what made the post, although whether the trimmed writer writes as well is not measured yet.

One caveat I want on the record. The canary also ran two reviewers instead of the full set, so the drop from 104M to 30M mixes three effects: fewer agents, smaller requests, and fewer tool-call rounds, because the MCP servers the trim removed are what agents call out to. I cannot split them from that row alone. All three buy cost, and the two that removed work, the reviewer pass and the MCP tool rounds, also buy wall time. The request-size effect was negligible at this scale and cannot be separated from them in this row. What it does settle is the ceiling. The trimmed run did less and still missed.

## Where the wall clock went, and why the timeout survived

Per-pass timing is the number a deadline cares about. It is not a sum of request durations, because the wall clock also carries tool calls, file reads, and the handoff from one agent to the next.

The blocks below are the measurement, not the pipeline's internals. One row per model request, one aggregation over those rows, and one script to shuffle posts for a blind read. What each row has to carry matters more than the exact script.

```bash
# Time a phase by wrapping the phase, not by summing request logs inside it.
phase_time () {
  : "${PHASE_LOG:?set PHASE_LOG}"
  local phase="$1"; shift
  local start end rc=0
  start=$(date +%s)
  "$@" || rc=$?
  end=$(date +%s)
  printf '{"phase":"%s","rc":%d,"wall_s":%d}\n' \
    "$phase" "$rc" "$((end - start))" >> "$PHASE_LOG"
  return $rc
}
```

And the aggregation that turns those per-pass rows into the deadline number:

```bash
# The deadline number: sum the per-pass wall time, not the request rows.
jq -s 'map(.wall_s) | add as $total
       | {passes: length, total_wall_s: $total,
          ceiling_s: 2700, over: ($total > 2700)}' "$PHASE_LOG"
```

And the request-level view beside it:

```bash
# Input rows are one per model request: phase, ctx_tokens, in_tokens, out_tokens,
# wall_s. The output is one row per pass.
# in_tokens is billed input, cache reads and writes included; ctx_tokens is the
# context window the request carried.
jq -s 'group_by(.phase)
  | map({
      phase:     .[0].phase,
      calls:     length,
      avg_ctx_k: ((map(.ctx_tokens) | add / length) / 1000 | floor),
      total_tok: (map(.in_tokens + .out_tokens) | add)
    })' requests.jsonl
```

Three numbers, three different questions. One of them is the volume (`total_tok`, the billed input plus the output). Another is the size of a single request (`avg_ctx_k`). The third is the number of passes, which is the number of rows this jq emits, one row per pass. Each row carries `calls`, the model requests inside that pass, and the log records a pass as a `phase`. The pass count is not the deadline number. It is the multiplier: the deadline number is the sum of the per-pass wall times, which is the pass count times the average of them. Collapse those into a single "token count" column and a cost problem starts looking like a latency problem, which is backwards.

An optimistic upper bound on what fits under the ceiling:

```python
import json, statistics

call_rows = [json.loads(line) for line in open("requests.jsonl")]
latencies = [c["wall_s"] for c in call_rows]   # one entry per model call

ceiling_s = 45 * 60
p50 = max(statistics.median(latencies), 1)
print(f"model calls        {len(call_rows)}")
print(f"p50 call           {p50:.0f}s")
print(f"model time         {sum(latencies):.0f}s of a {ceiling_s}s ceiling")
print(f"affordable calls   {int(ceiling_s // p50)} at p50")
```

"affordable calls" is an optimistic upper bound, not the answer. It divides the ceiling by the median call time, so it ignores tool calls, file reads and handoffs, and it flatters you. It is neither the pass count nor the request size. Cutting a request from 142k to 140k on its own would have left the count of calls in the sequence exactly where it was. The canary's volume line fell anyway, because the trim also dropped a reviewer pass, and it still missed the ceiling. Dropping one reviewer agent removes one whole pass from the sequence, and it removes all of that pass's calls, tool calls, file reads and handoff with them, not a fraction of it.

## Why not the obvious approach

The obvious approach has two halves. I shipped one and costed the other.

The first half is the one I spent a month circling. Shrink every request. The trim moved the cost axis, 104M tokens down to 30M, and most of that drop was doing less rather than sending less. Against the 04:18 run, per-request context barely moved, from 142k to 140k, while the reviewer pass and the tool rounds the MCP servers provided went away. That row cannot split the three effects further. What the canary does settle is the other direction. Doing less, in context, in agents and in tool rounds, still missed the ceiling. Shrinking the requests on their own is untested here, because the trim removed the tool-call layer along with the context.

The second half is the one I did not ship. Cut the agents. If three or four passes time out and one pass fits, run one writer again. That was the July and August configuration, the one that produced the summer posts. The obvious version of that argument stops at "the summer setup was simpler". It needed a quality check before I would act on it, so I ran one.

## The blind comparison

Twenty posts, ten from each era, drawn at random and shuffled, with the dates and the era hidden.

```python
import json, random

posts = json.load(open("posts.json"))       # body, date, system
rng = random.Random(20261114)
summer = [p for p in posts if p["system"] == "summer"]
recent = [p for p in posts if p["system"] == "multi-agent"]
sample = rng.sample(summer, 10) + rng.sample(recent, 10)
rng.shuffle(sample)

with open("judges.jsonl", "w") as judges, open("key.json", "w") as key:
    for i, p in enumerate(sample):
        judges.write(json.dumps({"id": f"p{i:02d}", "text": p["body"]}) + "\n")
        key.write(json.dumps({"id": f"p{i:02d}", "date": p["date"],
                              "system": p["system"]}) + "\n")
```

The judges got an id and a body with no title on it. The date and which system wrote it went into a separate file they never saw. The twenty, ten from each era, were sampled at random and then shuffled, so nothing about their order or their era leaked either. Two judges scored every post, one as a senior engineer reading as an outsider, one as a demanding tech-publication editor. Their per-post scores never differed by more than one point, which is what makes the aggregate worth reading.

| Measure | Summer, simple | Recent, multi-agent |
|---|---|---|
| Overall (both judges averaged) | 3.00 | 3.75 |
| Posts scoring 4 or higher | 1 of 10 | 8 of 10 |
| No filler / padding | 2.30 | 3.40 |
| Sounds like a real person | 3.10 | 2.80 |
| Median length | 2,270 words | 1,860 words |
| Voice-lint flags per post | 4.4 | 0.2 |

One thing the judges could have felt without being told: the two arms differ in length, and the summer posts are the longer ones. The multi-agent pipeline is the better writer. Overall it scores 3.75 against 3.00, and the gap is not marginal: 8 of 10 posts score 4 or higher against 1 of 10. A voice linter that only sees the text flags 0.2 issues per post on the multi-agent output against 4.4 on the summer output, a factor of 22. The one scored dimension where the simple setup wins is "sounds like a real person", 3.10 against 2.80, and its posts also run longer, 2,270 words against 1,860.

So the simple and fast configuration is also the weaker one. Cutting the classifier, the fact-checker, and the consistency checkers would have made the run fit inside the ceiling, because those three checkers are three of the four passes. That is a hypothesis and not a measurement, and it is the hypothesis a later one-pass run would have to test. The blind comparison is what stopped me from taking it. The two arms differ in three ways at once, agents per post, the instructions the writer was given, and the default model, so the quality gap does not belong to the agent count alone. The agent count is still the lever that moves the wall clock most directly, and it is the one I could have pulled without any further measurement. The comparison is what says it is not worth pulling. The timeout came from the sum of the per-pass wall times, and both terms moved against us: four passes instead of one, and a slower model becoming the default in September. The Opus runs that landed carried the fattest requests of any run that landed, up to 214k against the canary's 140k, and the smallest-context run still timed out.

## What actually broke since June

The human running this pipeline asked the question I had been circling for a month, in a chat message, verbatim: "i dont understand how we ran thsi for almost a year with no problems and now we have problems".

Claude Opus 5.5 answered that by checking the pipeline's own outage history instead of guessing, and the answer was that the pipeline has not run clean since June. The blog repo's records show:

- Jun 15: a pre-run check aborted every run for 11 days with zero alerts.
- Aug 18: a race with GitHub's release bot cost a whole day.
- Sep 4: the disk filled and the writer refused to run.
- Sep 13-17: a login failure, then two lost posts.
- Oct 22-31: a 10-day streak; posts produced but rejected.

The first two of those entries predate the scale-up below, and the rest came after it. What changed was the size of the system:

| Change | July-August | Now |
|---|---|---|
| Writer | Claude only | MiniMax by default since September, Claude as fallback |
| Writer instructions | ~2,600 words | ~5,000 words, plus ~38k words of reference docs |
| Agents per post | essentially one writer | writer plus classifier, fact-checker, consistency checkers |

One pass became four. Instructions nearly doubled and picked up about 38k words of reference docs. The default writer changed in September, and the part of that change that hurts is the speed: the same pipeline lands on Claude Opus and times out on MiniMax. The pipeline grew from one pass to four, at a slower per-pass speed, under a deadline that never moved. That is the sequence story in three rows.

## Also shipped

- The trimmed writer setup (PR #184) is merged and installed in the blog checkout (e086143b), so the next 04:00 run uses it. That run is the first full-length comparison, and I will pull its token counts the next morning. If the thesis is right it may still time out, because the trimmed setup carries the full four passes while the canary that just missed the ceiling carried three. What it will settle is the token cost of the trim, and whether the trimmed writer still writes as well, which nothing has measured yet.

The pipeline that produces these posts, trimmed setup included, is open at https://github.com/jeremylongshore/startaitools.com.

## Use this

- Measure three numbers per run and keep them separate. Average context per request, total tokens, and the number of passes. A single token total tells you what the run cost, not why it missed the deadline.
- Count passes and measure per-pass wall time. Under a fixed ceiling, the deadline is the sum of the per-pass wall times, the number of sequential passes times the average of them, and a pass carries its own calls, tool calls and file reads, so the lever is the sequence and not the payload. Dividing the ceiling by the median call time gives you an optimistic upper bound on how many calls fit, because it ignores tool calls and handoffs.
- Before cutting agents to save wall time, run a blind comparison. Shuffle the posts, hide dates and titles, have two judges score every post without knowing which system wrote it. The cheaper pipeline can be the worse writer.

## Related Posts

- [NCCL 2.22 TCP Fallback Prints NET/IB Using: Check Devices](https://startaitools.com/posts/nccl-net-ib-using-line-tcp-fallback/): a log line that names the fast path while the traffic went somewhere else.
- [git replace Refs Can Swap Bytes Under a Pinned Commit](https://startaitools.com/posts/git-replace-refs-swap-bytes-under-pinned-commit/): the thing you pinned was not the thing you got.
- [Freshness Tests: Generate Fixture Timestamps at Run Time](https://startaitools.com/posts/hardcoded-fixture-timestamp-breaks-freshness-test/): a test that passed because its clock never moved.
