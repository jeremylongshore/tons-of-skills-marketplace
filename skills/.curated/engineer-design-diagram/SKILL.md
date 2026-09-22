---
name: engineer-design-diagram
description: "Generate production-grade engineering design diagrams (architecture,\
  \ sequence, delta, drift) as\nself-contained dark-themed HTML files with accessible\
  \ inline SVG. Grounds every diagram in real\nrepo topology via DCI \u2014 package\
  \ manifests, docker-compose, k8s, terraform, import graph. Four\nmodes: generate\
  \ from a live repo, diff a PR, trace a stack into a sequence diagram, or watch for\n\
  drift against a fingerprint. Semantic OKLCH palette; Mermaid fallback for large\
  \ graphs.\nUse when visualizing system architecture, reviewing a PR for structural\
  \ change, diagnosing an\nincident from a trace, onboarding to a codebase, or detecting\
  \ architectural drift.\nTrigger with \"/design:generate\", \"/design:diff\", \"\
  /design:trace\", \"/design:watch\", \"draw the\narchitecture\", \"diagram this PR\"\
  , \"engineer design diagram\", or \"architecture diagram\".\n"
allowed-tools: Read,Write,Glob,Grep,Bash(git:*),Bash(ls:*),Bash(cat:*),Bash(jq:*),Bash(docker:*),Bash(kubectl:*),Bash(terraform:*),Bash(python3:*),Bash(xdg-open:*),Bash(open:*),Bash(wslview:*),AskUserQuestion
version: 0.6.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- architecture
- diagram
- visualization
- svg
- html
- pr-review
- drift-detection
- sequence-diagram
- engineering-design
argument-hint: '[generate|diff|trace|watch] [target-path]'
model: inherit
compatibility: Designed for Claude Code
---
# Engineer Design Diagram

Generates production-grade engineering design diagrams as single-file HTML with inline SVG, grounded in real repository topology. Credit: design palette + arrow-masking pattern inspired by [Cocoon AI's architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) (MIT). See [THIRD_PARTY_LICENSES.md](references/THIRD_PARTY_LICENSES.md).

## Overview

Most diagramming tools produce pretty pictures disconnected from reality. This skill does the opposite: it reads the actual repo (package manifests, docker-compose, k8s, terraform, import graph) and emits a diagram that reflects the real system. It also knows how the system *changed* — PR-diff mode highlights structural deltas, trace mode turns a stack/log into a sequence diagram, and drift mode detects when the architecture has wandered from a stored fingerprint.

Four modes share a common pipeline (DCI grounding → node/edge graph → template fill → fingerprint write). Output is a single self-contained HTML file that opens in any browser, plus a Mermaid text block for copy-paste into docs. Dark theme with semantic OKLCH color coding by component role. Accessible by default (ARIA, `<title>`/`<desc>`, reduced-motion, keyboard navigation).

## Layout Philosophy — pick the shape before you draw

Dense technical systems want to render **wide**. This is how Anthropic docs, Linear docs, and Vercel architecture pages present multi-component systems: a sticky left rail for context (nav, invariants, legend) and a generous main column for the diagram itself. Mimic that pattern when your content is dense, and use the simpler single-SVG hero when it isn't.

Two supported output shapes, one decision up front:

| Shape | Use when | Template |
|-------|----------|----------|
| **Single-SVG hero** (classic) | ≤8 nodes, one-screen takeaway, no sub-grouping, no accompanying explanation needed | `templates/base.html` |
| **Docs-layout page** (widescreen) | ≥8 nodes, multiple planes/groupings/sub-blocks, want invariants + detail cards + legend alongside the diagram | `templates/docs-layout.html` |

**Widescreen-first for docs-layout.** Target `min-width: 1024px`; do *not* add mobile breakpoints for docs-layout output — it's architecture documentation, not a landing page. The diagram needs horizontal breathing room. On narrow viewports the diagram stage scrolls horizontally inside its card while the sidebar stays visible.

**Hybrid rendering** in docs-layout mode: HTML/CSS for all node cards (easier to maintain, free hover states, content edits don't trigger collision math), SVG overlay positioned absolutely *over* the node grid for arrows only. Arrows are the one place SVG still wins — fixed pixel coords, clean arrowheads, no brittle CSS-line math. Pure-SVG stays the default for the single-hero shape because the payoff of HTML flex doesn't materialize at small node counts.

**Layout-decision signal:** if during Step 2 the graph has any of — (a) more than one semantic lane/plane, (b) subcomponent lists of 4+ items per node, (c) the user asks for "docs page" / "architecture page" / references Anthropic/Linear/Vercel docs as exemplars — pick **docs-layout**. Otherwise stay with single-SVG.

See [docs-layout.md](references/docs-layout.md) for the full widescreen spec (grid geometry, design tokens, sidebar anatomy, arrow overlay placement, hover states).

## Prerequisites

- Git repository (for generate/diff/watch modes)
- At least one of: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `docker-compose.yml`, `k8s/*.yaml`, `terraform/*.tf`
- Python 3.9+ (for `scripts/fingerprint.py`)
- A browser to view output
- Optional: `kubectl` (cluster introspection), `terraform` (state parsing), `jq` (manifest parsing)

## Environment Detection (DCI)

!`git rev-parse --show-toplevel 2>/dev/null || echo "not a git repo"`
!`git rev-parse --short HEAD 2>/dev/null || echo "no-head"; git branch --show-current 2>/dev/null || echo "no-branch"`
!`ls package.json pyproject.toml Cargo.toml go.mod requirements.txt docker-compose.yml Dockerfile 2>/dev/null | head -10 || echo "no manifests"`
!`command -v jq >/dev/null 2>&1 && jq -r '.name,(.dependencies // {} | keys[]?)' package.json 2>/dev/null | head -20 || echo "no package.json / no jq"`
!`docker compose config --services 2>/dev/null | head -30 || echo "no docker-compose"`
!`find . -maxdepth 3 -type d \( -name k8s -o -name kubernetes -o -name manifests \) 2>/dev/null | head -5 || echo "no k8s dir"`
!`find . -maxdepth 3 -name '*.tf' 2>/dev/null | head -10 || echo "no terraform"`

## Instructions

### Step 1: Mode Detection

Parse the first token of `$ARGUMENTS`:

| Invocation | Mode | Playbook |
|------------|------|----------|
| `/design:generate` or empty | generate | [mode-playbooks.md#generate](references/mode-playbooks.md#generate) |
| `/design:diff` | diff | [mode-playbooks.md#diff](references/mode-playbooks.md#diff) |
| `/design:trace <path>` | trace | [mode-playbooks.md#trace](references/mode-playbooks.md#trace) |
| `/design:watch` | watch | [mode-playbooks.md#watch](references/mode-playbooks.md#watch) |

All modes share Steps 2-5. Mode-specific variations documented in the per-mode playbook.

### Step 2: Build the Node/Edge Graph

Use the DCI block output + targeted reads to populate a working graph:

- **Nodes** from: docker-compose service names, k8s `kind: Deployment/Service/StatefulSet`, terraform resource blocks, package manifest names (for standalone apps), detected binaries in `bin/` or `cmd/`.
- **Edges** from: docker-compose `depends_on` + exposed ports, k8s Service selectors + NetworkPolicy, terraform resource references, import-graph via Grep (`import.*from`, `require(`, `use crate::`), exposed HTTP/gRPC routes.
- **Role classification** per node using [drawing-rules.md § Role inference](references/drawing-rules.md#role-inference). Defaults to `slate` (external/unknown) when heuristics don't match.
- **Groups** from: k8s namespaces, terraform modules, docker-compose networks, directory boundaries for monorepos.

For graphs with >50 nodes, fall back to Mermaid (see Step 3 template selection).

### Step 3: Choose Template and Render

Apply the layout-selection rule from **Layout Philosophy** first, then pick the template for the chosen mode:

| Mode | Layout shape | Template | Output |
|------|--------------|----------|--------|
| generate / diff | single-SVG hero (simple graphs) | [templates/base.html](templates/base.html) | Centered SVG on dark canvas, cards row below |
| generate / diff | docs-layout page (dense graphs) | [templates/docs-layout.html](templates/docs-layout.html) | Two-column widescreen page: sticky sidebar + main column with diagram card + detail grid |
| diff (any shape) | — | selected template + delta classes | `delta-added` / `delta-removed` / `delta-changed` CSS markers on changed nodes/edges |
| trace | sequence | [templates/sequence.html](templates/sequence.html) | Sequence diagram with lifelines and message arrows |
| watch | — | none — markdown drift report | Markdown only; no HTML render |

**For single-SVG hero**: fill placeholders per [drawing-rules.md](references/drawing-rules.md) — color palette, SVG arrow-masking, z-order, 40px spacing, dashed boundaries, legend placement. Keep the grid `<pattern>`, `#020617` canvas, pulsing header dot (with reduced-motion guard).

**For docs-layout page**: fill placeholders per [docs-layout.md](references/docs-layout.md) — GitHub-inspired palette (`#0f1117` / `#161b22` / `#1c2128`), Inter + JetBrains Mono, 260px sticky sidebar, fixed-pixel node stage with SVG arrow overlay, hover states on node cards. No mobile breakpoints. Populate the sidebar with: (a) version badge, (b) "On this page" nav, (c) "Architectural invariants" list (surface up to 5 load-bearing constraints you inferred from the code/config — e.g. "Kernel owns durable state", "All ops return Result<T,E>"), (d) node-type legend.

If node count >50 OR the model signals layout failure (overlapping boxes, arrows crossing through nodes), switch to `templates/mermaid-fallback.html` regardless of layout shape.

### Step 4: Update Fingerprint State

For generate/diff/watch modes, write structural state to `${CLAUDE_PLUGIN_DATA}/arch-state.json` (or `~/.claude-state/arch-state.json` fallback if the env var is unset):

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/fingerprint.py write --input /tmp/graph.json
```

Schema documented in [fingerprint-spec.md](references/fingerprint-spec.md). Fingerprint persists across sessions so `watch` mode can detect drift.

### Step 5: Validate and Open

Run the HTML validator before presenting output:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/validate_html.py $CWD/.arch/<mode>-<timestamp>.html
```

Validator confirms: ARIA labels present, reduced-motion rule exists, no unexpected external script sources beyond Google Fonts. If validation fails, iterate on the template fill — don't ship an inaccessible diagram.

Open the result via `${CLAUDE_SKILL_DIR}/scripts/open_in_browser.sh` (OS-aware: `xdg-open` on Linux, `open` on macOS, `wslview` on WSL). Echo the Mermaid equivalent to the chat as a copy-pasteable text block.

### Feedback Loop

1. Run `validate_html.py` after Step 5.
2. If ARIA or contrast checks fail → fix template fill → re-validate.
3. If >50 nodes rendered as overlapping boxes → restart Step 3 with Mermaid fallback.
4. **(docs-layout only)** If arrows cross non-endpoint nodes OR text overflows a node box → re-run layout math (see [docs-layout.md § verification](references/docs-layout.md#verification)) before re-screenshotting. Don't eyeball it; collision math is cheap and catches what a thumbnail hides.
5. Maximum 3 iterations before falling back to Mermaid and flagging for manual review.

## Output

- **generate / diff / trace modes**: one HTML file at `$CWD/.arch/<mode>-<timestamp>.html` (self-contained, offline-capable, Google Fonts as the sole external dep) + one Mermaid text block echoed to chat.
- **watch mode**: markdown drift report with sections `Added`, `Removed`, `Changed`, each line citing the source file that justified the delta.
- **All modes**: updated fingerprint at `${CLAUDE_PLUGIN_DATA}/arch-state.json`.

Detailed output contracts in [mode-playbooks.md](references/mode-playbooks.md).

## Examples

### Example 1 — Generate architecture view from a monorepo

**Input:**

```
/design:generate
```

**Behavior:** DCI auto-loads `docker-compose.yml` services (`web`, `api`, `db`, `cache`), classifies roles (frontend/backend/db/db), reads `web/src/lib/api-client.ts` for the HTTP edge to `api`, reads `docker-compose.yml` `depends_on` for api→db and api→cache edges. Fills `templates/base.html`, writes `~/.arch/generate-2026-04-19T12-00.html`, writes fingerprint with 4 nodes + 3 edges.

**Output excerpt (Mermaid block):**

```
flowchart TB
  web["Web Frontend"]:::frontend --> api["API Service"]:::backend
  api --> db["Postgres"]:::db
  api --> cache["Redis"]:::db
```

### Example 2 — PR delta on a branch that adds Redis

**Input:**

```
/design:diff
```

**Behavior:** Loads prior fingerprint, re-runs DCI on working tree, computes set-diff. Renders architecture view with `class="delta-added"` on the `cache` node and the `api→cache` edge. Summary line: `Added 1 node (cache), 1 edge (api→cache)`.

### Example 3 — Sequence diagram from a Sentry event

**Input:**

```
/design:trace ./incidents/sentry-2026-04-18-payment-timeout.json
```

**Behavior:** Parses Sentry JSON (exception frames + transaction spans), infers 4 lifelines (`checkout-api`, `payment-service`, `stripe-webhook-listener`, `fraud-check`), renders sequence diagram with the timeout marked on the final arrow. No fingerprint write in trace mode.

### Example 4 — Drift watch after a quiet sprint

**Input:**

```
/design:watch
```

**Behavior:** Loads prior fingerprint, re-runs DCI, diffs. Output:

```
## Drift report — 2026-04-19 vs 2026-04-12

### Added
- Node `recommendations-service` (backend) — source: docker-compose.yml:services.recommendations
- Edge `api` → `recommendations-service` — source: api/src/handlers/product.ts:44

### Removed
- Edge `api` → `legacy-search` — source: api/src/handlers/search.ts removed in f8a2c91
```

## Edge Cases

- **No package manifests**: DCI returns empty. Ask the user to describe the system in prose, fall back to prompt-only generation without DCI grounding.
- **>150 components**: Hard cap at 150 rendered nodes. Overflow bucket labeled `… +N more`; full list preserved in fingerprint.
- **Stack trace format unknown**: Three parsers (Sentry JSON, OTel span, raw text). Unknown formats emit Mermaid-only sequence rather than failing.
- **No `main` branch for diff**: Probe `origin/HEAD` → `main` → `master` → `trunk`. If none found, fall back to `HEAD~1`.
- **Docker compose binary naming**: Probe both `docker compose` (modern) and `docker-compose` (legacy).
- **${CLAUDE_PLUGIN_DATA} unset**: Fallback chain `${CLAUDE_PLUGIN_DATA}` → `${XDG_STATE_HOME}/claude/arch` → `~/.claude-state/arch`.
- **iOS Safari large-diagram rendering**: Avoid SVG paths with >10k points per element; fall back to Mermaid for graphs that approach this limit.
- **k8s manifests with CRDs**: Role defaults to `slate` (external/unknown) when no heuristic matches; document in the legend.

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `not a git repo` | Running outside git | Init a repo or cd to one; DCI handles the empty case but diff/watch require git |
| `no manifests` | No package files found | Use prose-only mode; skill will ask user to describe the system |
| `fingerprint schema mismatch` | State file from older schema version | `fingerprint.py` refuses cross-version diff and emits baseline-restart guidance |
| `ARIA validation failed` | Template fill omitted `<title>`/`<desc>` | Re-fill with role-appropriate labels from [accessibility.md](references/accessibility.md) |
| `overlapping boxes detected` | Too many nodes for SVG layout | Auto-switch to Mermaid fallback (node count >50 trigger) |
| `no diff base` | `main`/`master`/`trunk` all missing | Use `HEAD~1` as base, warn user in output |
| `kubectl not installed` | Live cluster introspection unavailable | Skip cluster overlay; diagram still renders from static manifests |
| `trace parser unknown format` | Input file matches no known schema | Emit Mermaid-only sequence with best-effort parsing, flag for user review |

## Resources

- [drawing-rules.md](references/drawing-rules.md) — color palette, z-order, arrow-masking, spacing, legend placement (single-SVG hero — Cocoon-AI-inspired patterns)
- [docs-layout.md](references/docs-layout.md) — widescreen two-column layout spec (grid geometry, design tokens, sidebar anatomy, HTML+SVG hybrid arrow overlay, verification math) — mirrors Anthropic / Linear / Vercel docs patterns
- [mode-playbooks.md](references/mode-playbooks.md) — per-mode workflows with inputs, steps, outputs
- [fingerprint-spec.md](references/fingerprint-spec.md) — JSON schema for structural state + diff algorithm
- [accessibility.md](references/accessibility.md) — ARIA patterns, reduced-motion, keyboard nav
- [dci-block.md](references/dci-block.md) — DCI command catalog with output-size budgets
- [troubleshooting.md](references/troubleshooting.md) — iOS Safari, large graphs, schema drift
- [templates/base.html](templates/base.html) — single-SVG hero shell (≤8 nodes, simple graphs)
- [templates/docs-layout.html](templates/docs-layout.html) — widescreen docs-page shell (≥8 nodes, planes, sub-groupings, detail cards)
- [templates/sequence.html](templates/sequence.html) — sequence diagram variant (trace mode)
- [templates/mermaid-fallback.html](templates/mermaid-fallback.html) — Mermaid-only render for >50 nodes
- [scripts/fingerprint.py](scripts/fingerprint.py) — write / read / diff structural state
- [scripts/validate_html.py](scripts/validate_html.py) — ARIA + no-external-deps checker
- [scripts/collect_dci.sh](scripts/collect_dci.sh) — bounded DCI harvester for large repos
- [scripts/open_in_browser.sh](scripts/open_in_browser.sh) — OS-aware opener
- [THIRD_PARTY_LICENSES.md](references/THIRD_PARTY_LICENSES.md) — Cocoon-AI attribution + MIT notice
- [examples/](examples/) — Cocoon-AI sample diagrams (web-app, aws-serverless, microservices) kept as visual reference
- External: [Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) (inspiration source, MIT)
- External: [Mermaid diagram syntax](https://mermaid.js.org/intro/)
