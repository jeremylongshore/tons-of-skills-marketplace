---
name: yt-ideate
description: Generate and validate video ideas aligned with content pillars
argument-hint: [topic-or-niche-focus]
allowed-tools: Read, Write, Edit, Grep, Glob, Task, WebSearch, AskUserQuestion
model: sonnet
---

Run the YouTube Ideation skill. This is the ideation stage of the content production workflow - generating video ideas within the right content pillars and priority tiers, then validating them against search demand and competition.

Read the skill definition at `${CLAUDE_PLUGIN_ROOT}/skills/yt-ideation/SKILL.md` and follow its workflow exactly.

Use permitted delegation for bounded idea validation when available; otherwise evaluate directly. Save `validated_ideas.json` with stable video IDs, evidence status and actual selections so the briefing stage can load it. Treat any opportunity score as a labeled heuristic rather than measured demand.
