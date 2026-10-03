---
name: blog-figure-svg
description: "Stop using stock photos. Generate accessible, lightweight SVG figures for any blog or CMS - flow diagrams, comparison bar charts, taxonomy/Venn diagrams, annotated terminal mocks, and 1600x840 OG feature cards. Hand-authored SVG (no embedded fonts, no external assets, no AI-image latency) with a consistent palette, screen-reader metadata (title + desc + aria-labelledby), and a figcaption-required handoff to the writer. Rasterizes to compressed PNG ready for Ghost, WordPress, Webflow, or any static-site generator. Built for content marketers, indie hackers, and dev-tool blogs that want unique illustrations on every post without paying a designer or burning Midjourney credits. Trigger when the user says: 'add a figure to the post', 'illustrate this comparison', 'draw a flow diagram for X', 'make a feature/OG image', or any request to produce a chart/diagram for editorial use."
version: 1.1.0
emoji: "🎨"
homepage: https://github.com/AutomateLab-tech/publishing-skills
allowed-tools: WebSearch, WebFetch, Bash(python3:*), Read, Write
author: AutomateLab <hello@automatelab.tech>
license: MIT-0
compatibility: Designed for Claude Code
tags: [seo, content, publishing, figures, svg]
metadata:
  openclaw:
    requires:
      bins:
        - python3
---

# blog-figure-svg

Produces SVG figures intended for blog posts: in-line illustrations (1 per ~500 body words is the rule of thumb) and a templated OG feature card. Output is a clean SVG file (the editable source) rasterized to a compressed PNG (what the post references). Every figure carries `title` + `desc` + `role="img"` so screen readers can read it.

This skill is **platform-agnostic** — the SVG and PNG it produces work in any CMS (Ghost, WordPress, Webflow, Sanity) or static-site generator (Hugo, Astro, Eleventy, Jekyll, Next-MDX). It complements `seo-blog-writer` (handles the publish step for whatever platform you're on) and `blog-topic-research` (validates the topic). Use it during the **illustration step** of writing a post — after the prose is stable so the anchor sentences are final.

```
/blog-figure-svg flow      "<title>"   --steps "Trigger -> Filter -> HTTP -> Slack"
/blog-figure-svg compare   "<title>"   --bars "Zapier:0.03,Make:0.015,n8n:0.008" --unit "$ per task"
/blog-figure-svg taxonomy  "<title>"   --groups "Workflows,Agents,RPA" --notes "see references/style-examples.md"
/blog-figure-svg terminal  "<title>"   --lines "$ npm install\nadded 42 packages"
/blog-figure-svg feature   "<headline>"   --accent "#4F46E5" --pill "How To"
```

All variants write to `tmp/blog-drafts/<slug>-<N>-<short-name>.svg` (editable source, gitignored), then rasterize to `<slug>-<N>-<short-name>.png` (uploaded to the blog CDN).

---

## Before you start

The skill expects a working directory it can write into. Default: `tmp/blog-drafts/`. The PNG rasterizer requires one of:

- **ImageMagick** (`magick` command) — preferred. `magick -density 192 -background white in.svg -resize 1600x out.png`.
- **rsvg-convert** — `rsvg-convert -w 1600 -b white in.svg -o out.png`.
- **inkscape** (CLI) — `inkscape --export-type=png --export-width=1600 in.svg`.
- **cairosvg** (Python) — `pip install cairosvg`; `cairosvg in.svg -W 1600 -o out.png`.

Plus **pngquant** (or `oxipng`) for compression — typical 60-80% size reduction with no visible quality loss. Core Web Vitals and ad-network reviews (Mediavine, Raptive) care about image weight.

```bash
command -v magick || command -v rsvg-convert || command -v inkscape || python3 -c "import cairosvg" 2>/dev/null \
  || echo "no SVG rasterizer found - install one of magick, rsvg-convert, inkscape, cairosvg"
command -v pngquant || command -v oxipng || echo "no PNG compressor - install pngquant or oxipng"
```

---

## The three illustration shapes

Match each figure to a paragraph the reader has just finished, and to **one concrete information structure**:

| Shape | Use when the post... | Variant |
|---|---|---|
| **Comparison** | ...cites two or more numbers (prices, latencies, accuracy, counts) | `compare` (bar chart) |
| **Taxonomy** | ...introduces named categories (e.g. workflow / agent / RPA, or trigger / action / filter) | `taxonomy` (Venn, hierarchy, or labelled groups) |
| **Process / flow** | ...describes a "how to" sequence, integration topology, or decision tree | `flow` (horizontal flow with named steps) |
| **CLI / API mock** | ...shows command output, an error message, or a config blob | `terminal` (annotated terminal mock) |
| **Title card** | ...needs an OG feature image | `feature` (1600x840 templated card) |

**Never plot data the post doesn't already cite.** If you can't identify even one information structure to illustrate, skip — note in the report "no figures: post is too short / too definitional."

**Hard rule for editorial pipelines:** any post >=800 words needs at least 1 figure; figure count = `max(1, body_words // 500)`. Sub-800-word definitional explainers are the only legitimate zero-figure case.

---

## Palette and typography

Pick from these hex values. **No new hues** — consistency across figures is the brand:

| Hex | Role |
|---|---|
| `#3b82f6` | accent blue — primary data series |
| `#fb923c` | orange — secondary series |
| `#10b981` | green — tertiary / positive |
| `#0b0b11` | text — titles, primary callouts |
| `#475569` / `#6b7280` / `#9ca3af` | greys — secondary labels, axis ticks |
| `#cbd5e1` / `#94a3b8` | light greys — gridlines, weak series |
| `#fafafa` | background fill |

**Typography:** `font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif"` only. **No embedded web fonts** — they fail to load in feed readers, dark-mode previews, and AMP renders. Sizes: title 20px bold, section labels 14-16px, axis labels 11-13px.

**ViewBox:** `viewBox="0 0 800 <height>"` for inline figures (a sane width for most CMS content columns, including Ghost's Casper, the WordPress block editor, and Hugo / Astro defaults); `viewBox="0 0 1600 840"` for OG cards. **Do not set root `width`/`height` attributes** — let the host theme scale.

---

## SVG skeleton (every figure)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 360"
     font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif"
     role="img" aria-labelledby="t1 d1">
  <title id="t1">Short, informative title - what the figure shows</title>
  <desc id="d1">Long-form description for screen readers - what the bars/circles/lines depict, including all numbers shown on screen</desc>
  <rect width="800" height="360" fill="#fafafa"/>
  <!-- bars / circles / paths / labels -->
</svg>
```

**Accessibility checklist:**
- `role="img"` on the root `<svg>`.
- `<title>` + `<desc>` referenced via `aria-labelledby` (NOT `aria-describedby` — the former covers both).
- Suffix IDs with the figure number (`t1`/`d1`, `t2`/`d2`, ...) so multiple figures on one page don't collide.
- `<desc>` includes every number visible in the figure (screen readers can't OCR the chart).

**Honesty:** never round towards a more dramatic gap, never anchor an axis to inflate differences. If the data is "practitioner observation, not a measured study," say so in `<desc>` and in a small grey caption inside the figure.

---

## Variant: `flow` — horizontal process flow

For: "how to" sequences, integration topology, decision trees.

```python
# Args: title, steps (--steps "Trigger -> Filter -> HTTP -> Slack")
import sys, html, pathlib

title, steps_arg, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
steps = [s.strip() for s in steps_arg.split('->') if s.strip()]
n = len(steps)
assert 2 <= n <= 7, f"flow needs 2-7 steps, got {n}"

W, H = 800, 240
margin_x = 60
gap = (W - 2*margin_x) / (n - 1) if n > 1 else 0
box_w, box_h = 130, 64
cy = H // 2 + 10

nodes = []
arrows = []
for i, s in enumerate(steps):
    cx = margin_x + i * gap
    x = cx - box_w / 2
    y = cy - box_h / 2
    nodes.append(
        f'<rect x="{x:.0f}" y="{y:.0f}" width="{box_w}" height="{box_h}" '
        f'rx="8" fill="#fff" stroke="#3b82f6" stroke-width="2"/>'
        f'<text x="{cx:.0f}" y="{cy + 5:.0f}" text-anchor="middle" '
        f'font-size="14" font-weight="600" fill="#0b0b11">{html.escape(s)}</text>'
    )
    if i < n - 1:
        x1 = cx + box_w / 2
        x2 = margin_x + (i + 1) * gap - box_w / 2
        arrows.append(
            f'<line x1="{x1:.0f}" y1="{cy}" x2="{x2 - 8:.0f}" y2="{cy}" '
            f'stroke="#6b7280" stroke-width="2" marker-end="url(#arrow)"/>'
        )

desc = f"Flow diagram showing steps: {' to '.join(steps)}."

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif"
     role="img" aria-labelledby="t1 d1">
  <title id="t1">{html.escape(title)}</title>
  <desc id="d1">{html.escape(desc)}</desc>
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#6b7280"/>
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="#fafafa"/>
  <text x="{W//2}" y="40" text-anchor="middle" font-size="20" font-weight="700" fill="#0b0b11">{html.escape(title)}</text>
  {"".join(arrows)}
  {"".join(nodes)}
</svg>'''
pathlib.Path(out_path).write_text(svg, encoding='utf-8')
print(f"wrote {out_path} ({n} steps)")
```

---

## Variant: `compare` — bar chart

For: numeric comparisons (prices, latencies, accuracy, counts). 2-7 bars.

```python
# Args: title, bars (--bars "Zapier:0.03,Make:0.015,n8n:0.008"), unit
import sys, html, pathlib

title, bars_arg, unit, out_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
pairs = []
for chunk in bars_arg.split(','):
    label, val = chunk.split(':')
    pairs.append((label.strip(), float(val.strip())))
n = len(pairs)
assert 2 <= n <= 7, f"compare needs 2-7 bars, got {n}"

W, H = 800, 360
margin_x, margin_top, margin_bottom = 80, 70, 70
plot_w = W - 2 * margin_x
plot_h = H - margin_top - margin_bottom
max_v = max(v for _, v in pairs)
bar_w = plot_w / (n * 1.5)
gap = bar_w * 0.5
colors = ['#3b82f6', '#fb923c', '#10b981', '#94a3b8', '#6b7280', '#cbd5e1', '#475569']

bars = []
labels = []
for i, (label, val) in enumerate(pairs):
    h = (val / max_v) * plot_h if max_v else 0
    x = margin_x + i * (bar_w + gap)
    y = margin_top + (plot_h - h)
    bars.append(
        f'<rect x="{x:.0f}" y="{y:.0f}" width="{bar_w:.0f}" height="{h:.0f}" fill="{colors[i % len(colors)]}"/>'
        f'<text x="{x + bar_w/2:.0f}" y="{y - 8:.0f}" text-anchor="middle" font-size="13" font-weight="600" fill="#0b0b11">{val:g}</text>'
    )
    labels.append(
        f'<text x="{x + bar_w/2:.0f}" y="{H - margin_bottom + 24:.0f}" text-anchor="middle" font-size="13" fill="#475569">{html.escape(label)}</text>'
    )

desc = f"Bar chart comparing {unit}: " + ", ".join(f"{label} {val:g}" for label, val in pairs) + "."

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif"
     role="img" aria-labelledby="t1 d1">
  <title id="t1">{html.escape(title)}</title>
  <desc id="d1">{html.escape(desc)}</desc>
  <rect width="{W}" height="{H}" fill="#fafafa"/>
  <text x="{W//2}" y="36" text-anchor="middle" font-size="20" font-weight="700" fill="#0b0b11">{html.escape(title)}</text>
  <text x="{W//2}" y="56" text-anchor="middle" font-size="12" fill="#6b7280">{html.escape(unit)}</text>
  <line x1="{margin_x}" y1="{H - margin_bottom}" x2="{W - margin_x}" y2="{H - margin_bottom}" stroke="#cbd5e1" stroke-width="1"/>
  {"".join(bars)}
  {"".join(labels)}
</svg>'''
pathlib.Path(out_path).write_text(svg, encoding='utf-8')
print(f"wrote {out_path} ({n} bars)")
```

---

## Variant: `taxonomy` — labelled groups (Venn-lite)

For: introducing named categories. 2-4 groups.

```python
# Args: title, groups (--groups "Workflows,Agents,RPA"), notes
import sys, html, pathlib, math

title, groups_arg, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
groups = [g.strip() for g in groups_arg.split(',') if g.strip()]
n = len(groups)
assert 2 <= n <= 4, f"taxonomy needs 2-4 groups, got {n}"

W, H = 800, 400
cx, cy = W // 2, H // 2 + 20
r = 110
colors = ['#3b82f6', '#fb923c', '#10b981', '#94a3b8']
opacity = 0.4

circles = []
labels = []
if n == 2:
    positions = [(cx - 60, cy), (cx + 60, cy)]
elif n == 3:
    positions = [(cx, cy - 50), (cx - 70, cy + 40), (cx + 70, cy + 40)]
else:  # 4
    positions = [(cx - 70, cy - 50), (cx + 70, cy - 50), (cx - 70, cy + 50), (cx + 70, cy + 50)]

for i, ((x, y), label) in enumerate(zip(positions, groups)):
    circles.append(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{colors[i]}" fill-opacity="{opacity}" stroke="{colors[i]}" stroke-width="2"/>'
    )
    # Label outside the circle, away from center
    dx, dy = x - cx, y - cy
    mag = math.sqrt(dx*dx + dy*dy) or 1
    lx = x + (dx / mag) * (r + 30)
    ly = y + (dy / mag) * (r + 30)
    labels.append(
        f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle" font-size="15" font-weight="600" fill="#0b0b11">{html.escape(label)}</text>'
    )

desc = f"Taxonomy diagram showing groups: {', '.join(groups)}, with overlapping regions indicating shared concepts."

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif"
     role="img" aria-labelledby="t1 d1">
  <title id="t1">{html.escape(title)}</title>
  <desc id="d1">{html.escape(desc)}</desc>
  <rect width="{W}" height="{H}" fill="#fafafa"/>
  <text x="{W//2}" y="40" text-anchor="middle" font-size="20" font-weight="700" fill="#0b0b11">{html.escape(title)}</text>
  {"".join(circles)}
  {"".join(labels)}
</svg>'''
pathlib.Path(out_path).write_text(svg, encoding='utf-8')
print(f"wrote {out_path} ({n} groups)")
```

---

## Variant: `terminal` — annotated terminal mock

For: command output, error messages, config blobs.

```python
# Args: title, lines (newline-separated), out_path
import sys, html, pathlib

title, lines_arg, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
lines = lines_arg.split('\n')
assert 1 <= len(lines) <= 16, f"terminal needs 1-16 lines, got {len(lines)}"

W = 800
line_h = 22
H = 80 + line_h * len(lines) + 30
chrome_h = 36

rows = []
for i, ln in enumerate(lines):
    y = 80 + chrome_h + i * line_h
    # Highlight error lines red, prompt lines green
    color = '#fb923c' if 'error' in ln.lower() or 'fail' in ln.lower() else '#10b981' if ln.startswith('$') else '#cbd5e1'
    rows.append(
        f'<text x="32" y="{y}" font-family="ui-monospace, Menlo, Consolas, monospace" '
        f'font-size="14" fill="{color}" xml:space="preserve">{html.escape(ln)}</text>'
    )

desc = "Terminal mock showing: " + " | ".join(ln for ln in lines if ln.strip())[:200]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif"
     role="img" aria-labelledby="t1 d1">
  <title id="t1">{html.escape(title)}</title>
  <desc id="d1">{html.escape(desc)}</desc>
  <rect width="{W}" height="{H}" fill="#fafafa"/>
  <text x="{W//2}" y="36" text-anchor="middle" font-size="18" font-weight="700" fill="#0b0b11">{html.escape(title)}</text>
  <rect x="20" y="60" width="{W - 40}" height="{H - 80}" rx="8" fill="#0b0b11"/>
  <circle cx="40" cy="78" r="6" fill="#fb923c"/>
  <circle cx="58" cy="78" r="6" fill="#10b981"/>
  <circle cx="76" cy="78" r="6" fill="#94a3b8"/>
  {"".join(rows)}
</svg>'''
pathlib.Path(out_path).write_text(svg, encoding='utf-8')
print(f"wrote {out_path} ({len(lines)} lines)")
```

---

## Variant: `feature` — OG / feature card (1600x840)

For: the post's hero image (Ghost `feature_image`, WordPress `featured_media`, the static-site front-matter `feature_image` field, OG previews, social cards). One per post.

The card uses a tinted gradient background, a 24px grid pattern at 7% opacity, a soft radial highlight, and either a giant accent number (when the headline contains a 1-3 digit number) or a placeholder icon slot. Brand text (your wordmark, pill label) is configurable.

```python
# Args: headline, accent (hex), pill (short tag like "How To"), brand_wordmark, out_path
import sys, html, textwrap, re, pathlib

headline, accent, pill, brand, out_path = sys.argv[1:6]

# Auto-fit headline: 3-line cap on common tiers (longest tier may use 4).
n = len(headline)
if   n <= 32:  size, wrap, max_lines = 120, 14, 2
elif n <= 60:  size, wrap, max_lines = 92,  20, 3
elif n <= 90:  size, wrap, max_lines = 76,  26, 3
else:          size, wrap, max_lines = 60,  32, 4

lines = textwrap.wrap(headline, wrap)[:max_lines]
line_h = int(size * 1.15)
total_h = line_h * (len(lines) - 1) + size
y0 = 420 - total_h // 2 + size       # vertical center inside 1600x840

tspans = "".join(
    f'<tspan x="120" dy="{0 if i==0 else line_h}">{html.escape(line)}</tspan>'
    for i, line in enumerate(lines)
)

# Hero element: number-as-hero when the headline has a 1-3 digit number,
# otherwise a clean geometric placeholder. Skips 4-digit matches (years).
m = re.search(r'\b(\d{1,3})\b', headline)
if m:
    hero = (
        f'<text x="1500" y="640" text-anchor="end" font-family="ui-sans-serif, system-ui, sans-serif" '
        f'font-weight="800" font-size="500" fill="{accent}" '
        f'opacity="0.20" letter-spacing="-20">{m.group(1)}</text>'
    )
else:
    # Default placeholder icon: stacked geometric shapes
    hero = (
        f'<g transform="translate(1190,260) scale(1.0)" fill="none" stroke="{accent}" stroke-width="7" stroke-linecap="round">'
        f'<circle cx="140" cy="140" r="100" opacity="0.4"/>'
        f'<circle cx="140" cy="140" r="60" opacity="0.6"/>'
        f'<circle cx="140" cy="140" r="20" fill="{accent}" opacity="1"/>'
        f'</g>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 840" role="img" aria-labelledby="t1 d1">
  <title id="t1">{html.escape(headline)}</title>
  <desc id="d1">Feature card for blog post: {html.escape(headline)}. Pill label: {html.escape(pill)}.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#F8FAFC"/>
      <stop offset="100%" stop-color="#E2E8F0"/>
    </linearGradient>
    <radialGradient id="hi" cx="0.15" cy="0.1" r="0.7">
      <stop offset="0%" stop-color="{accent}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="{accent}" stroke-width="1" opacity="0.07"/>
    </pattern>
  </defs>
  <rect width="1600" height="840" fill="url(#bg)"/>
  <rect width="1600" height="840" fill="url(#grid)"/>
  <rect width="1600" height="840" fill="url(#hi)"/>
  <rect x="0" y="0" width="14" height="840" fill="{accent}"/>
  {hero}
  <text x="120" y="{y0}" font-family="ui-sans-serif, system-ui, sans-serif" font-size="{size}" font-weight="800" fill="#0F172A" letter-spacing="-2">{tspans}</text>
  <text x="120" y="760" font-family="ui-sans-serif, system-ui, sans-serif" font-size="28" font-weight="700" fill="{accent}" letter-spacing="2">{html.escape(brand.upper())}</text>
  <text x="1480" y="760" text-anchor="end" font-family="ui-sans-serif, system-ui, sans-serif" font-size="24" font-weight="600" fill="#475569" letter-spacing="1">{html.escape(pill)}</text>
</svg>'''
pathlib.Path(out_path).write_text(svg, encoding='utf-8')
print(f"wrote {out_path} ({len(lines)} lines, hero={'number' if m else 'icon'})")
```

**Customising the hero icon:** replace the placeholder `<g>` block with cluster-specific iconography from your project. Keep stroke width 5-9, viewBox-relative coordinates (drawn for a 280x280 box), and stroke-only fills so the icon reads at thumbnail size in social previews. Examples (n8n nodes, code brackets, agent graph, RPA grid) are easy to author — see the `feature` script's structure.

---

## Rasterize SVG to PNG

The SVG is the editable source. The blog references PNG only — most CMSes deliver PNG more reliably through their CDN than SVG.

```bash
# Preferred: ImageMagick at 192 DPI (renders text at 2x for sharpness)
for svg in tmp/blog-drafts/<slug>-*.svg; do
  png="${svg%.svg}.png"
  magick -density 192 -background white "$svg" -resize 1600x "$png"
done

# Or one of the fallbacks:
rsvg-convert -w 1600 -b white in.svg -o out.png
inkscape --export-type=png --export-width=1600 in.svg
python3 -c "import cairosvg; cairosvg.svg2png(url='in.svg', write_to='out.png', output_width=1600)"
```

`-density 192` renders text at 2x before resize (sharpness). `-background white` prevents black halos around antialiased edges. `-resize 1600x` is the practical ceiling for a CMS content column.

### Compress before upload

ImageMagick output is 200-400 KB per figure; `pngquant` typically cuts that 60-80% with no visible quality loss.

```bash
for png in tmp/blog-drafts/<slug>-*.png; do
  pngquant --skip-if-larger --strip --output "$png" --force 256 "$png" || true
done
ls -lh tmp/blog-drafts/<slug>-*.png
```

If `pngquant` isn't installed, `oxipng -o 4 tmp/blog-drafts/<slug>-*.png` is a slower fallback. If neither is available, surface to the user and proceed — don't block the post on compression.

### Verify the PNG

```bash
# Confirm dimensions and bit depth
magick identify tmp/blog-drafts/<slug>-*.png 2>/dev/null \
  || python3 -c "from PIL import Image; import sys; [print(p, Image.open(p).size) for p in sys.argv[1:]]" tmp/blog-drafts/<slug>-*.png
```

Open each PNG locally and confirm: text is sharp at 100% zoom, no missing glyphs, no black halos.

---

## Embed in the post

For each figure, identify the **anchor sentence** in the draft — the closing `</p>` of the paragraph the figure should appear after. Pick a phrase distinctive enough that `str.replace` finds exactly one match.

Insert with a generic `<figure>` block (renders cleanly in every major CMS theme and every static-site generator's default Markdown→HTML pipeline):

```html
<figure>
  <img src="<uploaded-png-url-or-relative-path>" alt="<full description with all numbers and labels>" loading="lazy">
  <figcaption>One sentence restating the takeaway in plain English (15-30 words).</figcaption>
</figure>
```

**Caption rules:**
- **Required on every figure.** No bare `<img>` and no `<figure>` without a `<figcaption>`. The `seo-blog-writer` skill's bundle validation refuses figures without captions.
- One sentence, 15-30 words, restating the takeaway in plain English (not "Figure showing X" — say what the reader should conclude).
- Allowed tags inside `<figcaption>`: `<a>` (with `rel="nofollow noopener"` for external), `<em>`. Nothing else.
- No "Figure 1." numbering.

**Alt text rules:**
- Restate every label and number visible in the figure. Screen readers read alt, not the figure.
- 50-200 chars. Longer than the caption.

Verify each PNG URL appears exactly once in the draft:

```bash
python3 -c "
import pathlib, re, sys
html = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
for m in re.finditer(r'src=\"([^\"]+\.png)\"', html):
    print(m.group(1))
" tmp/blog-drafts/<slug>.draft.html | sort | uniq -c
```

Each URL should print `1`. Zero = anchor missed; >1 = anchor matched multiple paragraphs (extend the anchor).

---

## Upload to your CMS

This skill doesn't ship a CMS uploader — the `seo-blog-writer` skill handles auth and the upload endpoint for each platform it targets. After generating PNGs:

- **For Ghost:** `seo-blog-writer`'s Ghost adapter exposes an image-upload snippet (POST to `/ghost/api/admin/images/upload/` with the Admin API JWT).
- **For WordPress:** `seo-blog-writer`'s WordPress adapter posts to `/wp-json/wp/v2/media` with application-password auth.
- **For static-site generators (Hugo, Astro, Eleventy, Jekyll, Next-MDX):** drop the PNGs into the project's static / public / assets directory and reference relative paths in the figure tag.
- **For other CMSes (Webflow, Sanity, Strapi, Contentful):** write a 20-line adapter that POSTs the PNG to the platform's media endpoint, then splice the returned URL.

---

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `magick: no decode delegate` on `.svg` | ImageMagick built without rsvg | Fallback: `rsvg-convert`, `inkscape`, or `cairosvg` |
| Text rendered as boxes / missing glyphs in PNG | Embedded font referenced but not installed | Use only generic `ui-sans-serif, system-ui` font families; no `@font-face` |
| Black halos around shapes in PNG | Antialiased SVG rendered against a transparent background | Pass `-background white` to ImageMagick |
| PNG looks blurry | Rasterized at 96 DPI | Use `-density 192` (or `-w 1600` with rsvg/cairosvg) |
| `aria-labelledby` ignored by screen readers | Missing `role="img"` on the root `<svg>` | Add `role="img"` — without it, the SVG is treated as a graphic group |
| Feature card text overflows the 1600x840 canvas | Headline longer than ~120 chars | Truncate headline or use the longest tier (60pt, 4 lines, 32 chars/line) |
| Figcaption missing on a `<figure>` | Manually pasted `<img>` not wrapped in `<figure>` | Wrap in `<figure>...<figcaption>...</figcaption></figure>` — every figure needs a caption |

---

## Companion skills

- **`blog-topic-research`** — validates that a long-tail topic has real demand signals before drafting.
- **`seo-blog-writer`** — drafts, scrubs, AI-SEO-audits, and publishes the post to your CMS (Ghost, WordPress, or static-site) via the platform adapter.

Together, the three form a complete long-tail SEO publishing pipeline: research the topic, write the post, illustrate it, publish.
