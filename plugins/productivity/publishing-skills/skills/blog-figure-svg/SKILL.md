---
name: blog-figure-svg
description: 'Design accessible, source-backed SVG editorial figures and optionally rasterize reviewed assets for a blog or CMS. Use when a post needs a flow, comparison, taxonomy, terminal mock, or feature card. Trigger with "add a figure to this post" or "make an SVG diagram".'
argument-hint: "[flow|compare|taxonomy|terminal|feature] [title] [options]"
allowed-tools: Read, Write, Edit, Bash(command:*), Bash(magick:*), Bash(identify:*), Bash(rsvg-convert:*), Bash(inkscape:*), Bash(python3:*)
version: 1.2.0
author: AutomateLab <hello@automatelab.tech>
license: MIT-0
tags: [svg, accessibility, editorial-design, diagrams, image-optimization]
model: inherit
effort: high
compatibility: Designed for Claude Code; file creation is local by default, while brand changes, data claims, uploads, overwrites, and publication require owner approval
---
# Accessible Editorial SVG Figures

## Overview

Create lightweight editorial artwork whose visual claims are traceable to the approved article or source data. Supported shapes are process flows, comparison bars, taxonomies, terminal mocks, and `1600x840` feature cards.

The editable SVG is the source of truth. PNG rasterization is optional, and CMS upload remains a separate approved action.

## Prerequisites

- Final or near-final article copy with the intended anchor paragraph
- Approved title, caption, data points, source URLs, brand palette, and output directory
- A writable local draft directory such as `tmp/blog-drafts/`
- For PNG output, one installed rasterizer: ImageMagick, `rsvg-convert`, Inkscape, or CairoSVG
- Optional `pngquant` or `oxipng` for lossless or reviewed lossy compression

## Tool Discipline

Use `Read` to inspect the approved article and brand tokens. Use `Write` or `Edit` for local SVG, caption, and receipt files. The scoped `Bash` commands may only detect or invoke the named local renderers and Python validator; never interpolate untrusted titles, SVG fragments, filenames, or shell arguments.

## Instructions

1. Identify the single information structure to communicate. Choose `flow` for ordered steps, `compare` for sourced numeric values, `taxonomy` for categories, `terminal` for verified command output, or `feature` for a title card.
2. Extract the exact facts from the approved source. Record a URL or article anchor for every number, quote, product claim, and terminal line. Omit unsupported content.
3. Create a safe kebab-case filename, refuse parent traversal or absolute output paths, and avoid overwriting an existing asset unless the owner approves.
4. Lay out the figure on a responsive SVG `viewBox`. Use text elements rather than embedded fonts, preserve readable contrast, and keep labels legible at the target display width.
5. Add a unique `<title>` and `<desc>`, then connect them with `role="img"` and `aria-labelledby`. Decorative shapes should not add noise to the accessibility tree.
6. Keep the SVG self-contained: no scripts, event handlers, remote images, external stylesheets, `foreignObject`, or unreviewed embedded data.
7. Validate the XML and scan for forbidden active content. Review clipping, reading order, contrast, label accuracy, and source correspondence.
8. If PNG output is requested, choose an installed rasterizer, pass fully quoted local paths, render at the required dimensions, and verify the output type and dimensions.
9. Compress only after preserving the SVG source. Compare before/after dimensions and file size, and retain quality acceptable for text and fine lines.
10. Return paths, dimensions, alt text, caption, evidence mapping, validation results, and any upload action still awaiting approval.

## SVG Contract

Every figure starts with this security and accessibility shape:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900"
     role="img" aria-labelledby="figure-title figure-desc">
  <title id="figure-title">Approved figure title</title>
  <desc id="figure-desc">Concise explanation of the relationships shown.</desc>
  <rect width="1600" height="900" fill="#ffffff"/>
  <!-- Reviewed, static vector elements only. -->
</svg>
```

For comparison charts, label values directly and start quantitative axes at zero unless an explicit analytical reason is disclosed in the caption. For terminal mocks, reproduce only sanitized output; never include secrets, tokens, home paths, customer data, or misleading commands.

## Rasterization

Detect tools without installing anything:

```bash
command -v magick
command -v rsvg-convert
command -v inkscape
python3 -c 'import cairosvg; print(cairosvg.__version__)'
```

Example with trusted local paths:

```bash
magick -density 192 -background white figure.svg -resize 1600x figure.png
identify figure.png
```

Do not run package installers automatically. If no renderer exists, deliver the validated SVG and provide installation options for the owner to choose.

## Authentication

Local SVG creation, validation, and rasterization require no authentication and must not make network requests. CMS authentication is deliberately out of scope for this skill; pass the reviewed asset to the publishing workflow, which owns the target-specific secret and upload controls.

## Approval Boundaries

Require approval before inventing or altering brand tokens, changing sourced values, overwriting assets, installing software, uploading to a CMS, or publishing. A figure must not imply causation, scale, performance, price, or endorsement beyond its cited evidence.

## Output

Produce:

- editable `.svg` path and SHA-256 digest
- optional `.png` path, dimensions, MIME type, and byte size
- article anchor, figure title, descriptive alt text, and visible caption
- evidence mapping for factual labels and values
- XML, active-content, accessibility, and render checks
- unresolved decisions and upload/publication status

## Error Handling

| Condition | Response |
|---|---|
| Source data conflicts | Stop the chart, list the conflicting values and dates, and request an authoritative source. |
| SVG parser rejects the file | Do not rasterize or upload; repair the XML and rerun validation. |
| Active content is detected | Remove scripts, handlers, remote resources, and `foreignObject`; regenerate from safe primitives. |
| Labels clip or contrast fails | Adjust layout or palette, then inspect again at target width. |
| Rasterizer is unavailable | Return the validated SVG and an explicit unexecuted renderer recommendation. |
| Output path already exists | Use a new versioned filename or obtain overwrite approval. |

## Examples

Create a source-backed process figure:

```text
request: flow "Webhook delivery lifecycle"
steps: receive -> authenticate -> enqueue -> process -> acknowledge
source: approved article section "Delivery lifecycle"
outputs: webhook-delivery-lifecycle.svg, webhook-delivery-lifecycle.png
validation: XML clean; active content absent; 1600x900; alt text present
```

Refuse an unsupported comparison:

```text
request: compare three vendors by reliability
result: blocked
reason: the article provides no comparable reliability measurement or source
next: supply an authoritative dataset or use a nonquantitative taxonomy
```

## Verification

- Parse the SVG as XML and confirm one unique title/description pair.
- Search for `script`, event attributes, `javascript:`, remote references, and `foreignObject`; expect none.
- Inspect the rendered asset at desktop and narrow content widths.
- Verify every number and terminal line against the recorded source.
- Verify PNG dimensions and MIME type independently of the extension.

## Resources

- [WAI Images Tutorial](https://www.w3.org/WAI/tutorials/images/)
- [WAI guidance for complex images](https://www.w3.org/WAI/tutorials/images/complex/)
- [MDN SVG element reference](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/svg)
- [OWASP Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

## Next Steps

Attach the figure receipt to the article review, then let the publishing workflow perform the separately approved upload and rendered-page verification.
