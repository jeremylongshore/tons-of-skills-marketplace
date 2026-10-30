---
name: yt-brief
description: Create a YouTube production brief with viewer outcome, angle, demo scope
  and CTA. Use when developing a selected video idea before packaging. Trigger with
  "write a video brief" or "brief this idea".
allowed-tools: WebSearch, Read, Write
version: 1.11.0
author: Claude Code Plugins <jeremy@intentsolutions.io>
license: MIT
tags:
  - productivity
  - yt-brief
compatibility: Designed for Claude Code
---

# YouTube Brief

## Overview

Turn a selected video idea into a production brief that the packaging and
filming team can use. Define one viewer outcome, the angle that earns a click,
and what the demonstration must actually deliver.

## Prerequisites

- A selected idea, supplied directly or identified in `validated_ideas.json`.
- The intended audience, target length, deadline and any required feature or CTA.
- A working directory and video ID, such as `mcp-reporting`. Reuse the ID for all
  stages: `video-brief-{slug}.md`, `packaging-{slug}.md`,
  `video-outline-{slug}.md`, and `demo-prep-checklist-{slug}.md`.

If the user supplies an existing artifact, Read that exact file first. Reuse its
video ID and recorded paths; legacy filenames are valid when explicitly selected.
If an output path belongs to another video, select a different ID rather than
replacing it. Updating the user's selected brief is a revision of that artifact.

## Instructions

1. Read the selected idea and relevant research. Ask only for missing decisions
   that change the brief: audience, intended outcome, scope or production limits.
   Carry forward the user's chosen content type and tier; do not invent a tier
   taxonomy when none is supplied.
2. Use WebSearch when technical capabilities, release timing or competitive
   claims need verification. Prefer primary documentation and record source URLs
   and the date checked. Keep unknown behavior as an open demo check; searching
   documentation does not prove the demo has been rehearsed.
3. Write a focused brief with the fields below. Choose enough key points to
   deliver the outcome within the target length. Separate a proposed giveaway
   from an asset that already exists; do not promise an unavailable download.
4. Present the draft and ask the user to approve or revise the angle, scope and
   CTA before advancing to packaging. A previous idea selection does not approve
   a new brief. Preserve approval already given for the actual brief.
5. Use Write to save `video-brief-{slug}.md` in the working directory. Record its
   video ID, status (`draft` or `approved`), intended output paths and research
   links. Mark it approved only after the user's approval; report the saved path
   and the next stage rather than starting packaging automatically.

### Brief content

- Working title, content type and any user-defined tier.
- Target viewer, starting knowledge and the problem they want solved.
- Angle: why this demonstration is useful compared with existing coverage.
- Viewer outcome and the key points that support it.
- Demo sequence, accounts/sample data needed and unverified demo steps.
- CTA asset, its readiness and where it will be delivered.
- Target duration, deadline and any time-sensitive claims with sources.
- Exclusions and open decisions that could prevent filming.

## Output

A production brief saved as `video-brief-{slug}.md`, with a clear approval status
and enough detail for a teammate to prepare packaging and demos. Include these
handoff fields before the substantive brief:

```text
Video ID: mcp-reporting
Status: draft
Packaging output: packaging-mcp-reporting.md
Outline output: video-outline-mcp-reporting.md
Demo checklist output: demo-prep-checklist-mcp-reporting.md
```

The ID is an example, not a fixed filename for every video. Keep draft status
visible if approval is still pending.

## Error Handling

| Situation                                    | Recovery                                                                 |
| -------------------------------------------- | ------------------------------------------------------------------------ |
| Several ideas could be selected              | Ask which idea to develop; do not merge unrelated ideas into one brief.  |
| Research or claimed capability is missing    | State the gap and list a demo check; do not invent a successful result.  |
| The requested scope exceeds the filming slot | Propose a smaller outcome or a series and let the user choose.           |
| Output belongs to another video              | Use a distinct video ID or the user's explicitly selected revision path. |
| Brief is not approved                        | Save a draft and stop before packaging.                                  |

## Examples

**Direct idea:** “Brief a video showing a solo operator how to build a weekly
report with MCP; keep it under 15 minutes.” Establish the viewer's starting setup,
identify the single report outcome and propose the concrete demonstration. Save
`video-brief-mcp-reporting.md` as a draft for review.

**Revision:** “Use the existing brief, but remove the paid service from the demo.”
Read the named brief, preserve its ID and revise the prerequisites, sequence and
CTA consistently. Do not treat the old approval as approval of a changed scope.

## Resources

Use the user's selected idea, `validated_ideas.json` when available, and the
recorded research sources. The approved brief is the input to this plugin's
packaging stage. No API account or command-line installation is required to write
a brief; any demo setup belongs in the production document.
