---
name: generate-social
description: |
  Generates platform-sized, on-brand social templates as SVG from the active
  brand profile, with editable headline, subhead, and call-to-action zones.
  Vector output needs no account, key, or network.
  Use when a user asks for an Instagram post or story, an Open Graph or social
  card, a YouTube thumbnail, or a banner.
  Trigger with "make an Instagram post", "social card", or "/brand-make social".
allowed-tools: Read, Write, Glob, Bash(node:*)
argument-hint: '[platform] [headline] [optional subhead] [optional cta]'
version: "0.5.1"
author: localplugins <localplugins@proton.me>
license: MIT
compatibility: Designed for Claude Code
tags:
- branding
- social-media
- svg
- templates
- marketing
---

# Generate Social

Generates a platform-sized, on-brand social template as SVG from the active brand profile, with editable text zones the user can tweak afterward.

## Overview

The generate-social skill turns a headline (and optional subhead and call-to-action)
into a correctly sized social graphic that uses the brand's palette and fonts. Output
is vector SVG, so it scales cleanly and needs no account, key, or network call. The
generator (`lib/social.mjs`) lays out a brand band, a wrapped headline, an optional
subhead, and an optional accent pill; the skill resolves the active profile, picks the
platform, runs the generator, and saves the file. For a photographic background behind
the template, the raster path lives in the `generate-graphic` skill.

## Prerequisites

- An active brand profile created with `/brand-new` (a `brand/` directory, or `brands/[slug]/`). Read loads its `color-system.json` and `typography.json`.
- Node.js on the PATH — the generator runs as `node lib/social.mjs`.
- Write access to an `output/` directory in the working repository.
- A headline string; subhead and call-to-action are optional parameters.

## Instructions

1. Run `/brand-status` to confirm the active brand; if none exists, tell the user to run `/brand-new` and stop.
2. Use Glob to locate the active brand directory, then Read and validate the profile with `validateProfile`. Stop with the offending field if validation fails.
3. Choose the platform preset — `instagram-square` (default), `instagram-story`, `og-card`, or `youtube-thumb`. Ask the user when unspecified.
4. Generate the template by running the node generator:

   ```js
   import { loadProfile } from '../../lib/brand.mjs';
   import { buildSocial } from '../../lib/social.mjs';
   const profile = loadProfile(activeDir);
   const { svg, platform } = buildSocial(profile, {
     platform: 'instagram-square',
     headline: 'We just raised our Series A',
     subhead: 'Building the future of logistics',
     cta: 'Read the story',
   });
   ```

5. Write the result with the Write tool to `output/[slug]-[platform].svg`.
6. Hand the file to the `visual-guardian` subagent for a palette, contrast, and type pass; apply its fixes or surface its flags.
7. Report the saved path and point out the editable zones so the user can customize or adapt the copy: `id="headline"`, `id="subhead"`, and `id="cta"`.

## Output

One SVG file under `output/`, named for the slug and platform:

```text
output/northwind-instagram-square.svg
```

- Sized to the chosen platform (for example 1080×1080 for `instagram-square`).
- Text sits in editable zones — `id="headline"`, `id="subhead"`, `id="cta"` — that wrap automatically.
- All copy is HTML-escaped before it enters the markup; colors come from the palette only. No raster is produced.

## Error Handling

| Condition | Behavior |
|-----------|----------|
| No active brand profile | Stop and direct the user to `/brand-new`. |
| Profile fails `validateProfile` | Report the offending field and stop. |
| Headline missing | Ask the user for the headline before generating. |
| Unknown platform requested | List the four supported presets and ask the user to pick one. |
| Headline too long for the canvas | The generator wraps text; verify the result and shorten copy if the guardian flags overflow. |

To troubleshoot a clipped layout, verify the copy length against `references/platform-sizes.md`, then re-run and re-check with the guardian.

## Examples

**Example — launch announcement post**

> /brand-make an instagram post announcing our Series A

Builds a 1080×1080 square with the brand band, a wrapped headline, and an accent call-to-action, saved as `output/northwind-instagram-square.svg`.

**Example — link card**

> /brand-make an og card for the blog post

Generates a 1200×630 Open Graph card sized for link previews and hands it to the guardian.

**Example — story cover**

> /brand-make an instagram story

Produces a 1080×1920 story, insetting text clear of the platform's top and bottom safe zones.

## Resources

- `references/platform-sizes.md` — every preset size, safe zones, the layout the generator produces, and how to add a preset.
- Rendered preview — `lib/context/social-instagram-square.png`. Some marketplaces omit binary assets from that directory; if your copy did, view it at [localplugins/plugins](https://github.com/localplugins/plugins/tree/main/brand-forge/lib/context).
- Sibling skills: generate-logo for marks, and generate-graphic for photographic backgrounds — route between them with the `/brand-make` command.
- [Open Graph protocol](https://ogp.me/) — the metadata standard `og-card` targets.
- [Agent Skills documentation](https://code.claude.com/docs/en/skills) — how skills are authored and invoked.
