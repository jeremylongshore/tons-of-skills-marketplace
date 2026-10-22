---
name: generate-graphic
description: |
  Generates an on-brand marketing graphic — hero image, ad creative,
  background, or texture — with an image model, optionally stamped with the
  brand logo and a caption. Opt-in: needs a provider key and network access.
  Use when a user wants a photographic or illustrative graphic, not a
  text-heavy asset.
  Trigger with "make a hero image", "ad background", or "/brand-make graphic".
allowed-tools: Read, Write, Glob, Bash(node:*)
argument-hint: '[subject to depict, e.g. "a mountain trail at dawn"]'
version: "0.5.1"
author: localplugins <localplugins@proton.me>
license: MIT
compatibility: Designed for Claude Code
tags:
- branding
- image-generation
- marketing
- raster
- opt-in
---

# Generate Graphic

Generates an on-brand marketing graphic through an image model — the one opt-in feature that reaches the network — optionally stamped with the brand logo and a caption.

## Overview

The generate-graphic skill is the opt-in raster engine. Everything else in brand-forge
(logos, social, docs) stays vector and zero-permission; this skill is the only path
that calls an external image provider, so it runs only when a user explicitly wants a
photographic or illustrative graphic. The generator builds a brand-aware prompt with
`lib/raster.mjs`, calls the provider with `lib/genimage.mjs`, and can composite a crisp
vector logo and caption over the result with `lib/composite.mjs`. Text is deliberately
kept out of the image and added as vector on top.

## Prerequisites

- An active brand profile created with `/brand-new`. Read loads its `color-system.json`, `typography.json`, and `visual-identity.md`.
- Two opt-in signals, both required: `BRAND_FORGE_RASTER=1` and a provider key (`GEMINI_API_KEY` by default, or `OPENAI_API_KEY`). The `30-preflight` emitter surfaces this at session start.
- Authentication: the provider api key is read from that environment variable and sent as a request header, never placed in the URL. No credentials are written to disk.
- Node.js on the PATH and Write access to an `output/` directory.

## Instructions

1. Verify both opt-in signals are set. If either is missing, stop, explain how to enable raster, and offer the vector path (`generate-social` or a template) instead, which needs neither.
2. Use Glob to locate the active brand directory, then Read and validate the profile with `validateProfile`.
3. Build the prompt with `lib/raster.mjs` (no network). It encodes the palette in words, the imagery style, and the tone, and turns the brand's don't-rules into an "Avoid:" clause. Warn the user when literal text is requested and route text-heavy work to the vector engine.

   ```js
   import { loadProfile } from '../../lib/brand.mjs';
   import { buildRasterPrompt } from '../../lib/raster.mjs';
   const profile = loadProfile(activeDir);
   const prompt = buildRasterPrompt(profile, { subject: 'a mountain trail at dawn' });
   ```

4. Generate the image (the network call). The provider is swappable and failures retry with backoff, never leaving a half-written file:

   ```js
   import { generateImage } from '../../lib/genimage.mjs';
   await generateImage({ prompt, outPath: 'output/northwind-hero.png', provider: 'gemini' });
   ```

5. Optionally composite the brand logo and a caption over the raster with `lib/composite.mjs`, which writes an SVG overlay referencing the PNG.
6. Hand the result to the `visual-guardian` subagent for a palette and legibility pass. Write the final files and report the saved paths.

## Output

A raster PNG under `output/`, plus an optional vector overlay:

```text
output/northwind-hero.png
output/northwind-hero-overlay.svg
```

- The PNG is the model's image, steered toward the brand palette, style, and tone.
- The optional overlay is a small SVG that references the PNG and adds a crisp logo and caption. Flatten it to a single PNG with `/brand-export`.
- Output is local files only — the skill never auto-posts or uploads.

## Error Handling

| Condition | Behavior |
|-----------|----------|
| `BRAND_FORGE_RASTER` unset | Stop; explain the opt-in and offer the vector alternative. |
| Provider key missing | Stop; name the expected environment variable and do not proceed. |
| User requests literal text in the image | Warn that models render text unreliably; route text to the vector engine. |
| Provider call fails | Retry with backoff; if it still fails, report the error and leave no partial file. |
| Profile fails `validateProfile` | Report the offending field and stop. |

To troubleshoot a failed generation, verify the two opt-in signals with `/brand-status`, then re-run; check `references/brand-raster-prompting.md` to debug an off-brand result.

## Examples

**Example — hero background**

> /brand-make a hero image of a mountain trail at dawn

Builds a brand-aware prompt, generates `output/northwind-hero.png`, and offers to composite the logo over it.

**Example — opt-in not enabled**

> /brand-make a photo background

With `BRAND_FORGE_RASTER` unset, the skill stops, explains how to enable raster, and offers a vector template instead.

**Example — text routed to vector**

> /brand-make a graphic that says "Now hiring"

Warns that baked-in text renders poorly, generates the background here, and composes the words as a vector overlay on top.

## Resources

- `references/brand-raster-prompting.md` — how the prompt is built from the profile, why text stays out of the image, provider notes, and steering tips.
- Rendered preview — `lib/context/graphic-hero.png`. Some marketplaces omit binary assets from that directory; if your copy did, view it at [localplugins/plugins](https://github.com/localplugins/plugins/tree/main/brand-forge/lib/context).
- Sibling skills: generate-social and generate-doc-template for text-heavy, zero-permission assets — route between them with the `/brand-make` command.
- [Gemini image generation docs](https://ai.google.dev/gemini-api/docs/image-generation) — the default provider's API.
- [Agent Skills documentation](https://code.claude.com/docs/en/skills) — how skills are authored and invoked.
