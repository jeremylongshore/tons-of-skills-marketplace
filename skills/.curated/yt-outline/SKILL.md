---
name: yt-outline
description: Create a filmable YouTube outline and demo prep checklist from approved
  brief and packaging artifacts. Use when planning screen actions, section timing
  and rehearsals. Trigger with "outline this video" or "demo prep checklist".
allowed-tools: WebSearch, Read, Write
version: 1.11.0
author: Claude Code Plugins <jeremy@intentsolutions.io>
license: MIT
tags:
  - productivity
  - yt-outline
compatibility: Designed for Claude Code
---

# YouTube Outline

## Overview

Turn an approved brief and selected packaging into a filmable outline and demo
prep checklist. Specify what the presenter says, what appears on screen and what
the team needs to prepare, with honest rehearsal and timing status.

## Prerequisites

- The approved `video-brief-{slug}.md` and `packaging-{slug}.md`, or explicitly
  supplied paths for those artifacts.
- Their shared video ID, selected title/thumbnail direction and target duration.
- Demo constraints, available accounts/sample data and any rehearsal results.

Read both selected artifacts. Resolve different IDs or conflicting approved
versions before writing. Reuse the brief's recorded outline/checklist output
paths; legacy filenames work when explicitly selected. Do not load
`video-brief-yt-outline.md` merely because this skill is named yt-outline.

## Instructions

1. Confirm the approved viewer outcome and selected packaging. Keep the opening
   aligned with that promise; return a material scope change to the user rather
   than silently expanding the brief.
2. Use WebSearch for technical steps that need current primary documentation.
   Cite the relevant sources and observation date. Separate documented behavior,
   actual rehearsal results and steps still to verify. Writing an outline does
   not authorize running demos, changing accounts or installing software.
3. Choose a structure appropriate to the video. A feature tutorial can show the
   outcome, establish prerequisites, demonstrate the workflow and close with the
   CTA. A comparison needs comparable inputs and observable differences. An update
   video needs the actual change, walkthrough and its consequences for the viewer.
   Use the approved length rather than forcing a fixed tutorial duration.
4. For each section, write its purpose, talking points, on-screen content, demo
   actions, expected observable result and transition. Include a fallback for
   fragile live steps. Do not invent success, benchmark numbers or completed tests.
5. Assign estimated section durations and add them to a running total. If the
   total exceeds the approved slot, propose cuts or a revised duration instead
   of labeling an overlong outline as within budget. Distinguish estimates from
   a timed rehearsal.
6. Build a separate demo prep checklist by sequence: accounts/access needed,
   sanitized sample data, ready assets, initial state, rehearsal checks and backup
   recording/screenshots. Keep secrets out of the documents. List the CTA asset
   and any promises that still need production work.
7. Present the outline and checklist for review. Use Write to save
   `video-outline-{slug}.md` and `demo-prep-checklist-{slug}.md`, preserving selected
   existing paths. Record video ID, source brief/packaging paths, estimated total
   duration, open checks and review status. Mark approval only when given; the
   writing stage does not start filming or execute the prep checklist.

## Output

Two linked production documents with the same video ID:

- `video-outline-{slug}.md`: selected title, audience/outcome, source inputs,
  section plan, estimated timings, transitions and CTA.
- `demo-prep-checklist-{slug}.md`: preparation by demo, rehearsal checks, asset
  needs, open issues and fallback options.

For each outline section, a compact table can make the handoff clear:

| Section      | Talking point             | On screen / action       | Expected result                                | Estimate / running total |
| ------------ | ------------------------- | ------------------------ | ---------------------------------------------- | ------------------------ |
| First report | Show the promised outcome | Open the prepared report | Viewer sees the fields the tutorial will build | 1 min / 1 min            |

The row is a planning example, not proof that a demo was executed. If a standard
output path belongs to another video, choose a different ID before saving.

## Error Handling

| Situation                                | Recovery                                                                                |
| ---------------------------------------- | --------------------------------------------------------------------------------------- |
| Brief or packaging is missing/unapproved | Request the selected approved inputs before finalizing the outline.                     |
| Selected title conflicts with the brief  | Resolve the promise with the user; do not plan an unsupported demonstration.            |
| Feature behavior cannot be confirmed     | Label the open rehearsal check and provide a fallback rather than fabricating a result. |
| Estimated sections exceed the target     | Cut optional depth or propose a longer slot; retain the actual arithmetic.              |
| Output belongs to another video          | Preserve it and choose the correct video ID or explicit revision path.                  |

## Examples

**Standard handoff:** “Outline the MCP reporting video.” Read
`video-brief-mcp-reporting.md` and `packaging-mcp-reporting.md`, check their IDs and
approval states, then write `video-outline-mcp-reporting.md` and
`demo-prep-checklist-mcp-reporting.md`. Record the exact input paths in both.

**Unrehearsed feature:** “The demo needs a preview feature we have not tested.”
Describe the documented steps, flag the access/rehearsal dependency and plan a
recorded fallback. Do not call the demo verified or execute it as part of writing.

## Resources

Use the approved brief, selected packaging, recorded primary documentation and
actual rehearsal notes. This stage produces planning documents; access to demo
services is a preparation requirement for the filming team, not an API dependency
of the outline skill.
