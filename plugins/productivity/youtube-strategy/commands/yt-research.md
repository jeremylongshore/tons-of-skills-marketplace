---
name: yt-research
description: Research competitor channels, niches, and trending topics for YouTube content
argument-hint: [channel-urls-or-topic]
allowed-tools: Read, Write, Edit, Grep, Glob, Task, WebSearch, AskUserQuestion
model: sonnet
---

Run the YouTube Research skill. This is Stage 1 of the content production workflow - researching competitor channels, analyzing niches, identifying features and topics worth covering.

Read the skill definition at `${CLAUDE_PLUGIN_ROOT}/skills/yt-research/SKILL.md` and follow its workflow exactly.

**Coordinate the research inputs and outputs.** Use permitted, available delegation for bounded work; otherwise use web research or supplied exports directly. Optional bulk collection needs the existing configured route and approved scope. Save the research coverage and unavailable sources; do not claim a scrape or measured demand when neither was observed.
