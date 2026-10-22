---
name: generate-doc-template
description: |
  Generates on-brand document and deck templates — letterhead, slide, and
  one-pager — as SVG from the active brand profile, with editable title,
  subtitle, and body zones. Vector output needs no account, key, or network.
  Use when a user asks for a letterhead, a slide or deck master, or a branded
  one-pager.
  Trigger with "make a letterhead", "branded slide", or "/brand-make letterhead".
allowed-tools: Read, Write, Glob, Bash(node:*)
argument-hint: '[kind] [title] [optional subtitle] [optional body]'
version: "0.5.1"
author: localplugins <localplugins@proton.me>
license: MIT
compatibility: Designed for Claude Code
tags:
- branding
- documents
- svg
- templates
- design
---

# Generate Doc Template

Generates a branded, print- or screen-ready document template as SVG from the active brand profile, with editable content zones.

## Overview

The generate-doc-template skill turns a title (and optional subtitle and body) into a
branded document or deck master. Output is vector SVG, so it scales cleanly, prints
crisply, and needs no account, key, or network call. The generator (`lib/doctpl.mjs`)
draws a shared margin grid, brand mark, and accent rules, then fills the requested
kind; the skill resolves the active profile, picks the kind, runs the generator, and
saves the file. Convert to PDF or PNG downstream with `/brand-export`.

## Prerequisites

- An active brand profile created with `/brand-new` (a `brand/` directory, or `brands/[slug]/`). Read loads its `color-system.json` and `typography.json`.
- Node.js on the PATH — the generator runs as `node lib/doctpl.mjs`.
- Write access to an `output/` directory in the working repository.
- A title string; subtitle and body are optional parameters.

## Instructions

1. Run `/brand-status` to confirm the active brand; if none exists, tell the user to run `/brand-new` and stop.
2. Use Glob to locate the active brand directory, then Read and validate the profile with `validateProfile`. Stop with the offending field if validation fails.
3. Choose the kind — `letterhead` (default), `slide`, or `one-pager`. Ask the user when it is unclear.
4. Generate the template by running the node generator:

   ```js
   import { loadProfile } from '../../lib/brand.mjs';
   import { buildDoc } from '../../lib/doctpl.mjs';
   const profile = loadProfile(activeDir);
   const { svg, kind } = buildDoc(profile, {
     kind: 'letterhead',
     title: 'Offer of Employment',
     body: 'Dear candidate, we are delighted to extend an offer.',
   });
   ```

5. Write the result with the Write tool to `output/[slug]-[kind].svg`.
6. Hand the file to the `visual-guardian` subagent for a palette, contrast, and type pass; apply its fixes or surface its flags.
7. Report the saved path and point out the editable zones so the user can customize or adapt the copy: `id="title"`, `id="subtitle"`, and `id="body"`.

## Output

One SVG file under `output/`, named for the slug and kind:

```text
output/northwind-letterhead.svg
```

- Sized to the chosen kind — `letterhead` and `one-pager` at 816×1056 (US Letter @96dpi), `slide` at 1280×720 (16:9).
- Content sits in editable zones — `id="title"`, `id="subtitle"`, `id="body"` — that wrap automatically. A letterhead with no body ships with sample content rules the user replaces.
- All copy is HTML-escaped before it enters the markup; colors come from the palette only.

## Error Handling

| Condition | Behavior |
|-----------|----------|
| No active brand profile | Stop and direct the user to `/brand-new`. |
| Profile fails `validateProfile` | Report the offending field and stop. |
| Title missing | Ask the user for a title before generating. |
| Unknown kind requested | List the three supported kinds and ask the user to pick one. |
| Body font unavailable at render time | The declared fallback in `typography.json` applies — flag the substitution, never mismatch silently. |

To troubleshoot a crowded page, verify the copy against the margins in `references/layout-grids.md`, then re-run and re-check with the guardian.

## Examples

**Example — formal letterhead**

> /brand-make a letterhead for an offer letter

Builds an 816×1056 letterhead with the brand mark, an accent rule, the title, and the body, saved as `output/northwind-letterhead.svg`.

**Example — deck title slide**

> /brand-make a title slide for our pitch deck

Generates a 1280×720 slide with a left accent bar, the brand mark, and a large title zone.

**Example — executive one-pager**

> /brand-make a one-pager summarizing Q3 results

Produces an 816×1056 one-pager with a primary header band, then title and body zones ready to edit.

## Resources

- `references/layout-grids.md` — every kind's size, the shared grid, per-kind layout, editable zones, and how to add a kind.
- Rendered previews — `lib/context/letterhead.png` and `slide.png`. Some marketplaces omit binary assets from that directory; if your copy did, view them at [localplugins/plugins](https://github.com/localplugins/plugins/tree/main/brand-forge/lib/context).
- Sibling skills: generate-logo for marks, and generate-social for platform posts — route between them with the `/brand-make` command.
- [Paper sizes reference (ISO 216)](https://en.wikipedia.org/wiki/ISO_216) — background on the print dimensions used.
- [Agent Skills documentation](https://code.claude.com/docs/en/skills) — how skills are authored and invoked.
