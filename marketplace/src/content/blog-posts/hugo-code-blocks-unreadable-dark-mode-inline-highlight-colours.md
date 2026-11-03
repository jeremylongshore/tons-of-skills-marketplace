---
title: "Hugo Dark Mode Code Blocks Unreadable: Fix noClasses"
description: "Hugo's Chroma highlighter writes inline colours that override dark mode code boxes. Set noClasses = false, generate per-theme stylesheets, test 4.5:1 contrast."
date: "2026-11-02"
tags: ["web-development", "debugging", "testing", "claude-code"]
featured: false
canonical: "https://startaitools.com/posts/hugo-code-blocks-unreadable-dark-mode-inline-highlight-colours/"
---
Plain code text on this site turned near-white on a light grey box whenever dark mode was on. Light mode looked fine. The cause was Hugo's syntax highlighter, which wrote its own light colours into every code block. This post covers the cause, the fix, and a check you can run on your own site tomorrow.

## What broke

The site is built with Hugo, a static site generator. It has defaulted to dark styling since the May redesign, and phones in dark mode get that default too. A dark-mode bug here reaches readers by default.

Code blocks are highlighted by Chroma, the highlighting library Hugo ships with. Chroma's default output writes colours directly onto each element as inline styles. The style this site used put a light background, #f0f0f0, on every code block.

The theme, meanwhile, set code text to its own foreground colour, which is near-white in dark mode. The inline light background beat the theme's dark code box, so near-white text sat on light grey.

Measured in headless Chrome, which is Chrome running without a window so a script can read the colours it paints, the contrast on the live article from October 31 was 1.05:1. Contrast runs from 1:1 (no difference) to 21:1 (black on white). The Web Content Accessibility Guidelines (WCAG) ask for at least 4.5:1 for normal text.

Highlighted keywords such as `for` and `return` stayed readable, because the highlighter had coloured them dark green. Tokens it left uncoloured, such as variable names and plain text, inherited the theme's near-white foreground.

The diagnosis ran in a Claude Opus 5.5 session. The model fetched the live page and its CSS, pulled out the foreground and background values, and rendered the first code block in both themes. It named the cause before touching any code, then waited for owner approval before fixing.

## The fix

The fix has three parts.

First, stop the highlighter from writing colours inline. In the Hugo config:

```toml
[markup.highlight]
    noClasses = false
```

Hugo now emits class names on the tokens. The colours live in a stylesheet, where each theme can scope its own.

Second, generate one stylesheet per theme. A small generator script runs `hugo gen chromastyles` twice, once for the github style (light) and once for github-dark (dark). It prefixes every rule with its theme selector, so dark colours apply only in dark mode. It drops Chroma's background rules, so the site's own code box shows through. The output is committed as a file and loaded after the site's main stylesheet.

The palette moved off the friendly style. Friendly's constants and string interpolation fell to 2.4:1 on the light code box. Every visible token in the new palettes is at least 4.5:1.

Third, test every token. The test computes WCAG relative luminance for each token colour against its code box, in both themes, and fails on any pair under 4.5:1. It also fails when the committed stylesheet no longer matches what the generator would write, and when a rule is not scoped to a theme or carries a Chroma background.

The first version of that test failed on its own output. It read the generated file's header comment as a CSS selector and reported an "unscoped selector." That was fixed before merge.

## What the numbers say

Verification ran on a local build across six posts and 29 code blocks, at 390px and 1280px, in dark and light. The weakest token measured 6.66:1 in dark and 5.21:1 in light.

The same change also reworked code boxes on phones (600px wide or less), a separate problem from contrast. They now run the full screen width at 0.8rem. Lines scroll sideways and never wrap, because wrapping would break indentation. On the first block at 390px, horizontal overflow fell from 169px to 25px, with no page scroll.

Three limits. These numbers come from a local build, not the live site. The test checks code tokens against their code box, not every element on the page. And six posts is a sample.

The change itself is in [pull request 180](https://github.com/jeremylongshore/startaitools.com/pull/180), merged November 2, 2026.

## Use this

- Open a dark-mode page with a code block, inspect the text colour against its background, and work out the ratio. Anything under 4.5:1 fails WCAG for normal text.
- Set `noClasses = false` under `[markup.highlight]`, then generate one stylesheet per theme with `hugo gen chromastyles --style=<name>`. Scope each rule to its theme selector and drop Chroma's background rule so your own code box shows.
- Add a test that checks every token colour against its code box in each theme and fails below 4.5:1. Make it fail too when the generated stylesheet goes stale.

## Related Posts

- [Design tokens and validator parity on the marketplace site](https://startaitools.com/posts/design-tokens-and-validator-parity-marketplace-foundations/)
- [Migrating hardcoded colours to CSS variables in a page redesign](https://startaitools.com/posts/implementing-brand-consistency-with-css-variables-a-sponsor-page-redesign/)
