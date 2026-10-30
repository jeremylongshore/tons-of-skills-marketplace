---
name: yt-ideation
description: Generate filmable YouTube video ideas, explain their evidence and priority,
  and save user selections for briefing. Use when planning content from research or
  a topic. Trigger with "video ideas", "what should I make next" or "brainstorm videos".
allowed-tools: WebSearch, Read, Write, Task
version: 1.11.0
author: Claude Code Plugins <jeremy@intentsolutions.io>
license: MIT
tags:
  - productivity
  - yt-ideation
  - youtube
  - content-strategy
compatibility: Designed for Claude Code
---

# YouTube Ideation

## Overview

Develop useful, filmable video ideas from the creator's audience, research and
production constraints. Distinguish supported opportunities from creative
hypotheses and save the selected ideas for the briefing stage.

## Prerequisites

- A topic or niche, intended viewer and desired viewer outcome.
- Optional `niche-analysis.json` and `niche-report.md`, or explicit research paths.
- Constraints such as target length, deadline, available demos and channel goals.

Reuse supplied context and Read the selected research before generating ideas.
Without research, proceed with explicitly labeled hypotheses; do not imply that
search demand or competition has been measured. No ORM, API account or CLI
installation is required to develop ideas.

## Instructions

1. Establish the creator's content pillars, audience, practical outcomes and
   production limits. Use their existing content types and tiers if supplied;
   otherwise describe the format directly instead of inventing a growth taxonomy
   or requiring a fixed percentage mix.
2. Generate the requested number of ideas, or a manageable shortlist when no
   quantity is specified. Draw from observed coverage gaps, audience questions,
   verified updates, comparisons and practical workflows. Keep the angle specific
   enough that a teammate can explain what the viewer will learn or build.
3. Use WebSearch when current features, competing videos or an audience question
   need checking. Save URLs and observation dates. Treat anecdotes, visible views
   and search snippets as different evidence types; none alone measures demand
   for a new video. Mark unsupported trend/demand claims as hypotheses.
4. Evaluate ideas against audience fit, evidence, differentiation, filmability,
   demo access and useful scope within the deadline. Reject or defer infeasible
   ideas with a reason. Use Task for bounded idea validation only if delegation is
   available and permitted; direct evaluation is a valid route. A delegated
   score is a heuristic, not measured demand or a growth forecast.
5. Present a prioritized shortlist with each working title, angle, format,
   supporting evidence, open questions and feasibility tradeoffs. Explain the
   ordering qualitatively. Use numeric scores only if the user asks for a defined
   rubric, and label the criteria/assumptions rather than presenting them as
   predictions of views or CTR.
6. Ask which ideas to develop into briefs, unless the user already selected them
   or explicitly delegated that selection. Give every idea a unique, filename-safe
   lowercase video ID such as `mcp-reporting`; preserve IDs on revisions. Record
   whether selection was made by the user or delegated to the assistant.
7. Use Write to save `validated_ideas.json` in the working directory. Include all
   shortlisted ideas, their evidence status and actual selection state. Before
   overwriting a prior project, Read it and preserve unrelated ideas or use a
   separate project directory. Report the saved path and selected IDs for the
   brief stage, which writes `video-brief-{slug}.md` using the same ID.

## Output

`validated_ideas.json` is the handoff to briefing. The name is retained for the
existing workflow; each record must distinguish checked evidence from an
unvalidated hypothesis. Include:

- Focus, audience and exact research input paths (or an explicit research gap).
- Each idea's id, working_title, angle, content_type and any user-defined tier.
- evidence_status, source URLs, feasibility, priority rationale and open questions.
- selected and selection_basis, reflecting an actual choice rather than merely
  the assistant's recommendation.

This illustrative record is a hypothesis, not a validated market result:

```json
{
  "focus": "reporting workflows",
  "research_inputs": [],
  "ideas": [
    {
      "id": "mcp-reporting",
      "working_title": "Build a Weekly Report From One CSV",
      "angle": "Show one report outcome for a solo operator",
      "content_type": "practical tutorial",
      "evidence_status": "hypothesis",
      "source_urls": [],
      "feasibility": "demo rehearsal still required",
      "priority_rationale": "fits the proposed audience; demand remains unmeasured",
      "selected": false,
      "selection_basis": "awaiting selection"
    }
  ]
}
```

A recommendation does not set selected to true. If selection is explicitly
delegated, record that basis; if no selection exists, save the shortlist and stop
before drafting briefs for unchosen ideas.

## Error Handling

| Situation                                      | Recovery                                                             |
| ---------------------------------------------- | -------------------------------------------------------------------- |
| Research missing                               | Label hypotheses and identify the most useful verification question. |
| Idea promises an unavailable feature or result | Narrow it to a supported outcome or defer it.                        |
| Demo cannot be filmed within constraints       | Offer a smaller demonstration or explain the dependency.             |
| Several ideas share an ID                      | Assign distinct IDs before saving so later artifacts cannot collide. |
| User has not selected an idea                  | Save the shortlist with selected false and ask for the choice.       |
| Existing file belongs to another project       | Preserve it and choose the intended project directory.               |

## Examples

**Research-backed shortlist:** “Use the niche report and suggest five beginner
video ideas we can film this week.” Read the selected research, propose filmable
angles with source links and explain the priority. Save the shortlist and actual
selections to `validated_ideas.json`.

**Direct idea:** “Develop an idea about weekly reporting without doing research.”
Use the supplied audience and goal, label demand and competition unmeasured, and
avoid manufactured opportunity scores. Carry the selected ID into briefing.

## Resources

Use the creator's content pillars, selected research files and observed primary
sources. The briefing skill reads `validated_ideas.json`; approved production
briefs then feed packaging and outlining. This stage creates a documented
creative shortlist rather than changing an application configuration.
