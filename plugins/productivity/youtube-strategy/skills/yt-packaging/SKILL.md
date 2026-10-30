---
name: yt-packaging
description: Develop title and thumbnail concept pairs from an approved YouTube brief
  and record the user selection. Use when preparing packaging before outlining. Trigger
  with "package this video", "title ideas" or "thumbnail concepts".
allowed-tools: WebSearch, Read, Write
version: 1.11.0
author: Claude Code Plugins <jeremy@intentsolutions.io>
license: MIT
tags:
  - productivity
  - yt-packaging
compatibility: Designed for Claude Code
---

# YouTube Packaging

## Overview

Create title options and thumbnail concepts that communicate the approved
video's value together. Recommendations are creative hypotheses; they do not
establish a click-through rate or guarantee distribution.

## Prerequisites

- An approved brief supplied by path or complete brief details from the user.
- The same video ID and working directory used for `video-brief-{slug}.md`.
- Timing context, brand constraints and any supplied channel analytics.

Read the exact brief named by the user or its recorded handoff path. For the
standard flow, Read `video-brief-{slug}.md`; do not substitute a filename derived
from the skill name. If the user supplies brief details directly, confirm those
are the approved scope and retain them in the packaging document.

## Instructions

1. Extract the viewer, outcome, angle, demo boundaries and CTA from the approved
   brief. If approval or the chosen brief is unclear, resolve that before
   packaging. Reuse its video ID and output path, including explicit legacy paths.
2. Use WebSearch to inspect relevant existing video titles when competitive
   context is needed. Record URLs and the observation date. Distinguish observed
   titles/views from a hypothesis about why viewers clicked; do not invent
   analytics or present view counts as measured demand for a new video.
3. Draft a manageable set of title options across useful approaches: direct
   benefit, a specific question, a demonstrated comparison or a timely update.
   Each promise must fit the actual brief. Avoid unsupported exclusivity,
   “everything,” or earnings/results claims the video cannot substantiate.
4. Develop thumbnail concepts that complement the strongest titles. Specify the
   focal subject, composition, short text overlay, contrast, assets needed and
   small-size readability. These are design directions, not generated images.
   Identify which title each concept supports and why they form one message.
5. Recommend a combination with a rationale and alternatives. Suggest a testable
   variant when useful, labeling it as a proposal rather than an experiment
   already run. Ask the user to select or revise the title and thumbnail direction.
6. Use Write to save `packaging-{slug}.md`. Record status (`draft` or `approved`),
   the video ID, source brief path, selected title and selected thumbnail concept.
   Keep options separate from selections; mark approval only after the user has
   made that choice. Report the saved path for the outline stage.

## Output

A packaging document containing:

- Video ID, approval status and the exact source brief path.
- Title options with the promise, intended viewer and tradeoffs for each.
- Thumbnail concepts with layout, text and asset needs.
- Recommended pair, the user's actual selection, and any unresolved decisions.
- Research links and any proposed test, with assumptions clearly labeled.

Use the recorded output path for an existing selected artifact. If the standard
filename belongs to another video, choose a different ID; do not overwrite it.
Do not describe a draft concept as a finished thumbnail or publish the video.

## Error Handling

| Situation                                    | Recovery                                                                                          |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Brief missing or not approved                | Request the correct brief or approved details before selecting packaging.                         |
| Competitive research unavailable             | Develop options from the brief and disclose the research gap.                                     |
| A title promises more than the demo delivers | Narrow the title or send the scope change back for brief approval.                                |
| User mixes options                           | Record the chosen title and thumbnail together; do not infer a selection from the recommendation. |
| Video IDs or source paths disagree           | Resolve which brief the packaging belongs to before saving or handing off.                        |

## Examples

**From a brief:** “Package `video-brief-mcp-reporting.md`.” Read that file and use
its `mcp-reporting` ID. Propose title/thumbnail pairs, ask for a selection, and save
`packaging-mcp-reporting.md` with the brief path and actual approval state.

**Targeted revision:** “Keep title 2, but show the report rather than a logo in the
thumbnail.” Preserve title 2, revise the selected concept and update the same
packaging artifact. Do not claim the revision improved CTR without real test data.

## Resources

The approved brief and user-supplied brand references are the primary inputs.
Use observed competitor pages and supplied channel analytics as evidence when
available. The approved packaging and its source brief feed the outline stage;
no separate optimization API or installation is required.
