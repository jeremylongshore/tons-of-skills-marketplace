---
title: "Move Deterministic Math Out of the LLM Prompt"
description: "Move date windows, site lists, and per-site totals out of the LLM prompt and into a Python file the wrapper reads before the prompt is built."
date: "2026-09-23"
tags: ["automation", "ci-cd", "devops", "umami", "reporting"]
featured: false
canonical: "https://startaitools.com/posts/move-wrapper-math-out-of-the-llm-prompt/"
---
The Monday 8 a.m. rollup (a per-week HTML email stitched together by a bash wrapper around an LLM) used to ask the model to fetch and total Umami metrics for four sites. Its site list lived inside the prompt. The total lived wherever the model put it. Nothing checked the email contained every site. If a model quietly dropped a row, the email still went out, green check or not, and nobody saw the gap until someone noticed the dashboard felt short.

That changed in one PR, in four commits, on `scripts/blog/blog-team-rollup.sh`, the wrapper for that rollup. Three pieces moved out of the prompt and into files the wrapper reads or runs.

1. The site list now comes from `~/.claude/skills/web-analytics/scripts/estate_registry.py` (the registry is the same installed JSON file the daily report uses, so the two reports cannot drift). No silent fallback if the registry is missing or invalid. The wrapper exits with `ERROR: analytics registry is unavailable or invalid`.
2. A new `weekly_metrics.py` materializes the exact 7-day window (epoch-millisecond, no date math in the prompt), totals the metrics the wrapper already pulled from Umami, and writes an HTML dashboard before the prompt is built. The prompt only writes the interpretation.
3. After the agent finishes the final HTML, the wrapper runs `--check-report` against the registry. Any domain in `SITES` missing from the rendered HTML, the wrapper refuses to send. The send never happens.

Here is the part that matters.

```bash
# weekly_metrics.py materializes the period and the per-site totals
# before the prompt is built
SITES = ("startaitools.com", "tonsofskills.com",
         "jeremylongshore.com", "intentsolutions.io")
WINDOW_MS = 7 * 24 * 60 * 60 * 1000
```

```bash
# blog-team-rollup.sh, after the agent finishes the HTML
python3 weekly_metrics.py --out /tmp/weekly.html --check-report \
  || { echo "weekly report missing one or more sites"; exit 1; }
```

The prompt describes the week. The Python file decides what the week is. The wrapper owns the gate; the LLM does not.

Two other commits in the same PR are small and worth knowing together. The wrapper passes `--strict-mcp-config --mcp-config '{"mcpServers":{}}'` to the agent invocation, so a REST rollup cannot pull MCP servers (and their side effects) into the cron. And `web-analytics-daily.sh` now reads the MiniMax key from `~/.config/intentsolutions/api-providers.sops.json` (jq-extracted JSON), not the older dotenv SOPS file the eval lab uses. One-line change in spirit, brings the daily report into line with how the rest of the stack reads the same key.

The transferable rule is short. A wrapper's deterministic gate is not its prompt. It is three pieces working together: the files it reads for state (the registry, the key, the config), the math it materializes before the prompt is built (date windows, totals, counts), and the check it runs on its own output before sending (every required row present, every required field present). If any one of those three lives inside the prompt, the wrapper is asking the model to be its own QA, and the model is not QA.

Same shape as a kitchen line check. The receipt (the machine-written record proving a step ran, like a printed chit on a POS station) is the pass or fail. The cook's word is not the gate. A deploy that depends on the model telling you it deployed is the same mistake. If the smoke test cannot prove the thing boots clean, it does not ship.

## Use this

- Pick the list that owns a piece of state in your wrapper (sites, users, repos, configs). Move it into a file the rest of your system already reads, so two reports cannot drift.
- Materialize any arithmetic the wrapper needs (date windows, totals, counts) into a Python or shell file before the prompt is built. The prompt describes; the file decides.
- Add a `--check-report` step that refuses to send or write output missing anything the parent produced. The wrapper owns its gate; the LLM does not.

## Also shipped

- Rewrote the About page for AI search, with answer-style headings and a cleaner FAQPage block.
- An offline regression test that writes a fake `weekly_metrics.py` and asserts the wrapper rejects a dropped site under `OMIT_SITE=1`. The test is the only thing that would have caught the original bug if anyone had run it.
- The empty-MCP config on REST rollups: a REST rollup is a REST rollup. It does not get to pull MCP servers into a cron at 8 a.m.

## Related Posts

- [Deterministic-First LLM Advisory CI](https://startaitools.com/posts/deterministic-first-llm-advisory-ci/)
- [Git Plumbing for Unattended Cron in a Shared Checkout](https://startaitools.com/posts/git-plumbing-unattended-cron-shared-checkout/)
