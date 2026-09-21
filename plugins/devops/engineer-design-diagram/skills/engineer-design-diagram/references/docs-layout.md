# Docs-Layout Rules

Widescreen two-column layout for dense architecture diagrams. Mirrors the pattern used by [Anthropic docs](https://platform.claude.com/docs/en/home), [Linear docs](https://linear.app/docs), and [Vercel architecture pages](https://vercel.com/docs) — sticky context rail on the left, generous diagram + detail column on the right.

## Table of Contents

- [When to use this layout](#when-to-use-this-layout)
- [Philosophy](#philosophy)
- [Page structure](#page-structure)
- [Design tokens](#design-tokens)
- [Typography](#typography)
- [Sidebar anatomy](#sidebar-anatomy)
- [Main column anatomy](#main-column-anatomy)
- [Diagram stage (HTML + SVG hybrid)](#diagram-stage-html--svg-hybrid)
- [Node cards](#node-cards)
- [Plane boundaries](#plane-boundaries)
- [Arrow overlay rules](#arrow-overlay-rules)
- [Detail grid](#detail-grid)
- [Polish](#polish)
- [Verification](#verification)
- [Anti-patterns](#anti-patterns)

## When to use this layout

Use docs-layout when the graph has any of:

- ≥ 8 nodes
- More than one semantic lane / plane / group
- Nodes with 4+ subcomponents each (e.g. a compiler with sub-packages)
- User explicitly asks for a "docs page", "architecture page", or references Anthropic / Linear / Vercel as exemplars

If none of those apply, fall back to `templates/base.html` (single-SVG hero). The docs-layout has higher fixed overhead (sidebar content, detail cards) that looks out of proportion for 4–5 nodes.

## Philosophy

**Dense systems want to render wide.** A two-plane architecture, a microservice mesh, a compiler with multiple passes — these don't compress into a vertical stack without losing relationships. Give the diagram horizontal breathing room and surround it with the context that makes it useful: a navigation rail, the invariants the system is supposed to uphold, a color legend, a sibling grid of detail cards.

**Widescreen-first; no mobile breakpoints.** Architecture documentation is not a landing page. Target `min-width: 1024px` on `<html>`. On narrower viewports the diagram stage scrolls horizontally inside its card while the sidebar stays fixed. Don't fight it with responsive tricks — they always compromise the signal.

**Hybrid HTML + SVG.** Node cards are HTML (flex/grid layout, free hover states, easy content edits, no brittle text-width math); the arrow overlay is a single SVG positioned absolutely over the node stage. HTML handles layout; SVG handles line geometry. This is the same split Linear and Vercel use internally.

## Page structure

```
┌─────────────────────────────────────────────────────────────┐
│  <body>   padding: 40px 48px                                │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  <main class="layout">   max-width: 1400px              ││
│  │  display: grid                                          ││
│  │  grid-template-columns: 260px minmax(0, 1fr)            ││
│  │  gap: 40px                                              ││
│  │                                                         ││
│  │  ┌──────────┐  ┌──────────────────────────────────┐     ││
│  │  │ <aside>  │  │  <section class="main">          │     ││
│  │  │ sticky   │  │  header (h1 + lede)              │     ││
│  │  │ top:40px │  │  diagram-card (hero diagram)     │     ││
│  │  │          │  │  details (2-col detail grid)     │     ││
│  │  │ - badge  │  │  footer                          │     ││
│  │  │ - nav    │  │                                  │     ││
│  │  │ - invar. │  │                                  │     ││
│  │  │ - legend │  │                                  │     ││
│  │  └──────────┘  └──────────────────────────────────┘     ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

Spacing (8px grid):

| Rule | px |
|------|----|
| Body padding | `40px 48px` |
| Column gap | `40px` |
| Section gap (within main) | `48px` |
| Card inner padding | `24px` (detail) / `32px` (diagram) |
| Component gap within cards | `16px` |
| Label-to-value gap | `8px` |
| Tight inline spacing | `4px` |

## Design tokens

GitHub-inspired dark palette (higher contrast than the OKLCH palette used by the single-SVG template; chosen for readability of small UI labels).

```css
:root {
  --bg-page:       #0f1117;
  --bg-surface:    #161b22;
  --bg-raised:     #1c2128;
  --bg-raised-hover: #22272e;
  --border-subtle: #30363d;
  --border-accent: #58a6ff;
  --text-primary:   #e6edf3;
  --text-secondary: #8b949e;
  --text-muted:     #6e7681;
  --accent-blue:    #58a6ff;  /* CLI / entry */
  --accent-green:   #3fb950;  /* service packages */
  --accent-orange:  #f78166;  /* external APIs */
  --accent-purple:  #bc8cff;  /* persistence / shared libs */
  --accent-teal:    #39c5cf;  /* reserved */
}
```

Node-type → accent mapping:

| Role | Accent token | Border on hover |
|------|--------------|-----------------|
| CLI / entry point | `--accent-blue` | 100% opacity |
| Service package | `--accent-green` | 100% opacity |
| Persistence (DB, FS, cache) | `--accent-purple` | 100% opacity |
| External API | `--accent-orange` | 100% opacity |
| Shared library | `--text-muted` (w/ accent-purple left-border strip) | `--text-secondary` |

## Typography

Load Inter (UI) + JetBrains Mono (monospace refs) from Google Fonts.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

Scale:

| Role | Font | Size | Weight | Tracking |
|------|------|------|--------|----------|
| h1 (page title) | Inter | 28px | 600 | -0.015em |
| h2 (section) | Inter | 20px | 600 | normal |
| UI label (CAPS) | Inter | 12px | 500 | 0.08em uppercase |
| Body | Inter | 14px | 400 | normal |
| Lede | Inter | 15px | 400 | normal |
| Node title (mono) | JetBrains Mono | 13px | 600 | -0.01em |
| Node sub | Inter | 11px | 400 | 0.02em |
| Version pill | JetBrains Mono | 12px | 400 | normal |
| Inline `<code>` | JetBrains Mono | 12px | 400 | normal, on tinted bg |

Body defaults: `-webkit-font-smoothing: antialiased`, `-moz-osx-font-smoothing: grayscale`, line-height `1.5`.

## Sidebar anatomy

Four stacked sections with 32px gap between them.

1. **Version badge + tagline**. Monospace pill with a pulsing-dot marker (green `--accent-green` with a soft ring). Tagline below in `--text-muted`, max ~60 chars, one line.
2. **"On this page" nav**. `UI label` header, vertical list of `<a href="#anchor">` links. Each link: 6px padding, 2px transparent left-border; on hover, border becomes `--accent-blue` and text lifts to `--text-primary`. No underline.
3. **Architectural invariants**. `UI label` header, vertical list of 3–5 invariants. Each item has a **3px left border in `--accent-green`** and 12px left padding. This section does load-bearing work — surface the invariants a reader needs to have in mind while reading the diagram (things the code protects). Examples: "Kernel owns durable state", "All ops return Result<T,E>", "Writes are atomic (.tmp + rename)". Lead with the rule, put any qualifier inside.
4. **Legend**. One row per node role; colored 14×10 chip + label. Always include "shared library" even if unused — helps reader calibrate color-coding.

Sidebar is `position: sticky; top: 40px`. It must NOT overflow the viewport vertically at 1024×720 — keep the four sections terse.

## Main column anatomy

Three blocks with 48px gap:

1. **Header** — `<h1>` + lede paragraph (`--text-secondary`, max-width 780px). Lede answers "what is this system, in one paragraph".
2. **Diagram card** — `--bg-surface`, 1px `--border-subtle`, 12px radius, 32px inner padding. Card header has an `<h2>` on the left + a monospace hint on the right (e.g. "grounded in pnpm-workspace.yaml · package deps · src/ topology").
3. **Details grid** — 2-column auto-fit grid of `--bg-surface` cards. Each detail card: 24px padding, 10px radius, `<h3>` with a colored 8px dot marker, bulleted list with em-dash prefix.

## Diagram stage (HTML + SVG hybrid)

Fixed-width inner stage wrapped in a horizontally-scrollable container:

```html
<div class="diagram-scroll">
  <div class="diagram-stage">
    <!-- plane boundaries (divs with dashed borders) -->
    <!-- node cards (position: absolute, pixel coords) -->
    <!-- claude api / external nodes -->
    <!-- types bar / spanning elements -->
    <svg class="arrows-overlay" viewBox="0 0 W H" preserveAspectRatio="none">
      <!-- arrows -->
    </svg>
  </div>
</div>
```

Geometry:

- `.diagram-stage` — `position: relative; width: 1060px; height: 700px; min-width: 1060px` (pick a stage width that fits your graph; 1060 is a good default for two planes)
- `.diagram-scroll` — `overflow-x: auto` so narrow viewports scroll horizontally without breaking layout
- `.arrows-overlay` — `position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; overflow: visible` — the SVG viewBox matches the stage pixel dimensions 1:1 so coordinates are literal

All nodes use `position: absolute; left/top` in pixels. This is deliberate: the moment you have cross-lane arrows that must land on specific node edges, flex/grid reflow becomes a liability. Fixed pixel positions are boring but correct.

## Node cards

```html
<div class="node n-service" style="left: 340px; top: 90px; width: 190px;">
  <div class="node-title">@ico/kernel</div>
  <div class="node-sub">deterministic · Result&lt;T,E&gt;</div>
  <ul class="node-list">
    <li>workspace · state</li>
    <li>tasks (state machine)</li>
  </ul>
  <div class="node-group-label">integrity</div>
  <ul class="node-list">
    <li>SHA-256 chained traces</li>
  </ul>
</div>
```

Rules:

- Every node is `position: absolute; left/top` in pixels. Width explicit; height auto.
- `.node-title` is monospace (package name is code, treat it as code).
- `.node-sub` is 1 line, ≤ 40 chars.
- `.node-list li` uses an em-dash `—` prefix via `::before`, NOT a bullet.
- Inner group labels are small-caps mono, 10px, `--text-muted`.
- Hover: `--bg-raised-hover` + border opacity 100%.

## Plane boundaries

Dashed border + floating label that breaks through the dashed line (anchored by a matching background-color on the label):

```css
.plane {
  position: absolute;
  border: 1px dashed;
  border-radius: 10px;
}
.plane::before {
  content: attr(data-label);
  position: absolute;
  top: -9px; left: 16px;
  padding: 0 8px;
  background: var(--bg-surface); /* matches card bg — punches through the dashed stroke */
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
}
```

Use `--accent-orange` (~0.6 opacity) for one plane and `--accent-green` (~0.6 opacity) for the other. Pick semantics that read: deterministic / probabilistic, data / control, sync / async — whatever the architecture really splits on.

## Arrow overlay rules

Single `<svg class="arrows-overlay">` with `<defs>` for colored markers, then `<line>` / `<path>` elements per arrow. Coords are literal pixels in the stage's coordinate space.

**Arrow catalogue** (copy the pattern, pick colors by relationship semantics):

| Relationship | Color token | Style |
|--------------|-------------|-------|
| Entry invocation | `--accent-blue` | solid |
| Service ↔ persistence | `--text-muted` | solid, bidirectional pair |
| Cross-plane read | `--accent-green` | **dashed** (`stroke-dasharray="5 4"`) |
| Outbound external API | `--accent-orange` | solid |
| Implicit/shared reference (e.g. types) | `--accent-purple` | dotted (`stroke-dasharray="3 4"`), opacity 0.55 |

Marker definitions (one per color) ensure arrowheads match their line color.

**Routing rule — orthogonal only for cross-component arrows.** If two nodes live in different lanes or different rows, draw the arrow as a horizontal or vertical line — never a diagonal. Diagonals cross through whatever happens to be between the endpoints. Choose a y-coordinate that passes through empty space between rows.

**Label placement.** Labels sit 6–8px above the arrow line at its midpoint, same color as the line, JetBrains Mono 9–10px. For very short arrows (< 60px), omit the label.

## Detail grid

2-column auto-fit grid of detail cards. Each card maps to a "story" about a subsystem — roughly one card per plane + one per external surface + one per cross-cutting concern. 4–6 cards is the sweet spot.

Card structure:

```html
<div class="detail-card c-green">
  <h3>Deterministic control plane</h3>
  <ul>
    <li>Short claim about the subsystem.</li>
    <li>Constraint it upholds, or invariant inherited from the diagram.</li>
    <li>One concrete mechanism — ideally with inline <code>code</code>.</li>
    <li>Operational property (performance, security, reliability).</li>
  </ul>
</div>
```

`<h3>` has a colored dot marker (`::before`). Match the dot color to the subsystem's accent. 3–5 bullets per card; each bullet ≤ 2 lines. Don't rewrite the whole node contents here — this is commentary, not a node dump.

## Polish

- **No shadows.** Use borders only. Shadows read as decorative in docs UI.
- **No animations** except the single pulsing version-dot in the sidebar (wrap it in `@media (prefers-reduced-motion: reduce) { animation: none }`).
- **Hover states** on node cards and nav links only. Never on detail cards or the page chrome.
- **`font-feature-settings: 'ss01', 'cv11'`** on body enables Inter's stylistic alternates — subtle but raises quality.
- **Anti-alias** via `-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale`.
- Section labels use uppercase with `letter-spacing: 0.08em` — institutional, not decorative.

## Verification

Pixel positioning means errors won't show up at runtime. Before shipping, run the collision math. The ICO-architecture build established this pattern:

```python
# layout_check.py — minimal collision detector
nodes = {
    "cli":       (170, 400, 135, 110),   # x, y, w, h
    "kernel":    (340, 90, 190, 380),
    "sqlite":    (570, 90, 130, 55),
    # ...
}
arrows = [
    ("cli->kernel",   "cli", "kernel", 305, 425, 338, 425),
    ("cli->compiler", "cli", "compiler", 305, 485, 768, 485),
    # ...
]

def seg_rect(x1,y1,x2,y2, rx,ry,rw,rh):  # Liang-Barsky line-rect intersection
    ...

# For every arrow, assert it doesn't cross any non-endpoint node.
# Assert every endpoint lies on its source/target box edge.
# Assert every node gap >= 40px (where axes overlap).
# Assert every text label fits inside its parent box at the declared font size.
```

Three checks, all of which failed at least once during the ICO build:

1. **Arrow-through-node**: Liang-Barsky test between each arrow and every non-endpoint node rect. Must return 0.
2. **Endpoint attachment**: each arrow start/end must lie on (within 4px of) the corresponding node's edge, not floating in space or buried inside the box.
3. **Text overflow**: for each text label with a declared font-size, check `len(text) * font_size * 0.60 ≤ inner_box_width` (0.60 is the empirical advance width for JetBrains Mono / Inter; good enough for monospace-like sanity checks).

Only after all three pass should you screenshot. Thumbnail views hide 2-px overlaps; math doesn't.

## Anti-patterns

**Do not:**

- Use CSS Grid to position the *node cards themselves*. It works right up until you need an arrow that lands on a specific edge, at which point you're computing grid-cell centers in JavaScript. Just use absolute positioning.
- Let the diagram stage be responsive. At 600px wide, your 1060px diagram isn't "smaller" — it's scrolled. That's the correct behavior.
- Animate the arrow overlay. Flow diagrams aren't slideshows.
- Add tooltips to nodes. The detail grid already exists for that; duplicating breaks the hierarchy.
- Paint shadows on plane boundaries. The whole visual language is flat + bordered. Stay there.
- Pack more than ~8 sub-blocks inside a single node. If a node has 10+ children, promote it to its own plane and split it.
