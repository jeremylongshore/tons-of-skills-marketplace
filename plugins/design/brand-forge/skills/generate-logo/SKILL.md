---
name: generate-logo
description: |
  Generates on-brand, editable SVG logo assets — wordmark, monogram, and
  favicon — from the active brand profile, reusing its exact palette and
  heading font. Vector output needs no account, key, or network.
  Use when a user asks for a logo, wordmark, icon, monogram, or favicon.
  Trigger with "make a logo", "generate a wordmark", or "/brand-make logo".
allowed-tools: Read, Write, Glob, Bash(node:*)
argument-hint: '[logo text — defaults to the brand name]'
version: "0.5.1"
author: localplugins <localplugins@proton.me>
license: MIT
compatibility: Designed for Claude Code
tags:
- branding
- logo
- svg
- vector
- design
---

# Generate Logo

Generates on-brand, editable SVG logo assets — wordmark, monogram, and favicon — from the active brand profile as pure vector output.

## Overview

The generate-logo skill turns a saved brand profile into three ready-to-use logo
variants that reuse the brand's exact palette and heading font. Output is vector SVG,
so every asset scales without loss and needs no account, key, or network call. The
generator (`lib/logo.mjs`) draws each variant deterministically; the skill resolves
the active profile, runs that generator, saves the files, and routes them through
review. Raster copies are produced only on demand through the `/brand-export` command.

## Prerequisites

- An active brand profile created with `/brand-new` (a `brand/` directory, or `brands/[slug]/` with a `brand/.active` pointer). Read loads its `color-system.json` and `typography.json`.
- Node.js on the PATH — the generator runs as `node lib/logo.mjs`.
- Write access to an `output/` directory in the working repository.
- Optional: the `sharp` dependency, only if PNG copies are wanted later.

## Instructions

1. Run `/brand-status` (or `resolveActive` in `lib/brand.mjs`) to confirm which brand is active; if none exists, tell the user to run `/brand-new` and stop.
2. Use Glob to locate the active brand directory, then Read and validate the profile with `validateProfile`. Stop with the offending field if validation fails, for example a non-hex color.
3. Decide the logo text — the optional `text` argument, defaulting to the brand `name`. Ask the user when it is ambiguous.
4. Generate the three variants by running the deterministic node generator:

   ```js
   import { loadProfile } from '../../lib/brand.mjs';
   import { buildLogos } from '../../lib/logo.mjs';
   const profile = loadProfile(activeDir);
   const { wordmark, monogram, favicon } = buildLogos(profile, { text: 'Northwind' });
   ```

5. Write each variant with the Write tool: `output/[slug]-wordmark.svg`, `output/[slug]-monogram.svg`, and `output/[slug]-favicon.svg`.
6. Hand the files to the `visual-guardian` subagent for a palette, contrast, and clear-space pass; apply its fixes or surface its flags.
7. Report the saved paths and describe each variant. To customize sizing or adapt the geometry, edit the SVG directly or consult the reference below.

## Output

Three SVG files under `output/`, one per variant:

```text
output/northwind-wordmark.svg
output/northwind-monogram.svg
output/northwind-favicon.svg
```

- `[slug]-wordmark.svg` — the brand name in the heading font with an accent mark (the everyday logo).
- `[slug]-monogram.svg` — one or two initials in a rounded square, for square or tight placements.
- `[slug]-favicon.svg` — a single initial at 64×64 for browser tabs and app icons.

Each file carries `role="img"` and an `aria-label`, uses palette colors only, and embeds text that is HTML-escaped before it enters the markup. No PNGs are written unless the user runs `/brand-export`.

## Error Handling

| Condition | Behavior |
|-----------|----------|
| No active brand profile | Stop and direct the user to `/brand-new`; do not invent a palette. |
| Profile fails `validateProfile` | Report the offending field (non-hex color, missing font family) and stop. |
| Logo text ambiguous | Ask the user; default to the brand `name` only when unambiguous. |
| Heading font unavailable at render time | The declared fallback in `typography.json` applies — flag the substitution, never mismatch silently. |
| `visual-guardian` flags a contrast miss | Apply the fix or surface it; do not ship an asset below the profile's `minContrast`. |

To troubleshoot a bad render, verify the profile with `/brand-status`, then re-run the generator and re-check with the guardian.

## Examples

**Example — everyday wordmark**

> /brand-make wordmark logo

Resolves the active brand, builds all three variants, and reports `output/northwind-wordmark.svg` plus the monogram and favicon.

**Example — monogram for an app icon**

> /brand-make a square monogram for our app icon

Generates the rounded-square monogram from the brand initials and hands it to the guardian for a clear-space check.

**Example — validation stop**

> /brand-make logo

When `color-system.json` holds an invalid hex, the skill stops at step 2 and reports that field rather than emitting an off-brand asset.

## Resources

- `references/logo-construction.md` — variant geometry, clear-space rules, color roles, and accessibility notes the generator applies.
- Rendered previews — `lib/context/wordmark.png`, `monogram.png`, and `favicon.png`. Some marketplaces omit binary assets from that directory; if your copy did, view them at [localplugins/plugins](https://github.com/localplugins/plugins/tree/main/brand-forge/lib/context).
- Sibling skills: generate-social for platform posts, and generate-doc-template for letterheads and slides — route between them with the `/brand-make` command.
- [SVG on MDN](https://developer.mozilla.org/en-US/docs/Web/SVG) — the vector format every asset is emitted in.
- [Agent Skills documentation](https://code.claude.com/docs/en/skills) — how skills are authored and invoked.
