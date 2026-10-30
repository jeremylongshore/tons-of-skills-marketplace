---
name: validate-consistency
description: |
  Universal document consistency auditor. Runs deterministic drift checks across
  docs, code, tests, and CI, resolves conflicts through a per-fact-class authority
  registry (sot-map.yaml), and produces reports that structurally separate
  deterministic findings from advisory LLM-judged findings. Each local run attempts
  disclosure-approved report and index writes in the caller’s separate Intent OS
  checkout; unavailable or rejected filing is reported as HELD.
  Use when checking documentation accuracy before a release, after major refactors,
  or when onboarding to a new codebase. Also invoked automatically by /release Phase
  1.6.
  Trigger with "/validate-consistency", "check consistency", "validate docs",
  "audit documentation", "doc drift check".
allowed-tools: Read, Glob, Grep, Bash(echo:*), Bash(git:*), Bash(diff:*), Bash(python3:*)
argument-hint: '[optional path to sot-map.yaml — defaults to ~/000-projects/intent-os/sot-map.yaml]'
version: 3.30.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
- documentation
- consistency
- audit
- drift-detection
- quality
---
# Universal Document Consistency Auditor v3.0

## Table of Contents

1. [Overview](#overview)
2. [Truth Invariant](#truth-invariant)
3. [Examples](#examples)
4. [Instructions](#instructions) — Steps 0–6
5. [Severity Assignment Rules](#severity-assignment-rules)
6. [Bootstrap: Drafting Registry Rows](#bootstrap-drafting-registry-rows)
7. [Integration with /release](#integration-with-release)
8. [Output](#output)
9. [Error Handling](#error-handling)
10. [Resources](#resources)

## Overview

Runs deterministic drift checks across all documentation artifacts, resolves conflicts through a per-fact-class authority registry (`sot-map.yaml`), and produces a structured report with actionable findings grouped by category and severity. Deterministic checks and LLM-judged checks are structurally separated: judged findings are advisory-only and never block anything.

## Truth Invariant

The governed brain arbitrates asserted company/doctrine claims and the rules of arbitration — never generated facts. This validator never reads the brain as ground truth for generated facts: authority for a generated fact lives only in a registry row a human has adjudicated. The brain ingests only human-adjudicated findings — raw findings from this skill are candidate evidence, not truth, until a human adjudicates them.

## Examples

**Basic audit:**
> /validate-consistency

Runs the full audit on the current working directory. Loads the authority registry and produces a categorized report.

**Targeted check after refactor:**
> I just renamed a bunch of modules — check consistency

Detects that code changed, runs all 9 checks, surfaces broken cross-references (deterministic) and stale capability claims (advisory).

**Pre-release gate (via /release):**
> /release

Phase 1.6 automatically invokes this skill. Deterministic Critical findings block the release; advisory findings are surfaced for review and never block.

## Prerequisites

- Must be run from inside a git repository (or directory with recognizable project structure)
- Read access to all project files
- An authority registry (`sot-map.yaml`) — optional; without one the skill runs in bootstrap mode (see Step 1)

## Instructions

### Step 0: Announce

```
echo "════════════════════════════════════════════════════════════════"
echo "  DOCUMENT CONSISTENCY AUDIT"
echo "════════════════════════════════════════════════════════════════"
```

### Step 1: Load the Authority Registry

The source of truth is a **per-fact-class authority registry declared as data** — never a global ranking, never auto-detected at runtime.

1. Resolve the registry path: the path supplied by the invoker (argument or explicit instruction) if given; otherwise the default `~/000-projects/intent-os/sot-map.yaml`.
2. Read and parse the registry. Print what was loaded:

```
echo "Authority registry: [path]"
echo "Fact classes registered: [n] — [list of class names]"
```

1. If the registry is missing or unparseable, announce **bootstrap mode**: every fact class is unowned. Conflicts are still detected and reported, but no winner is ever named — each is emitted as `unowned fact-class — human adjudication needed`, and the report includes drafted registry rows for a human to adjudicate (see [Bootstrap](#bootstrap-drafting-registry-rows)).

**Registry row shape:**

```yaml
version: 1
fact_classes:
  version:                              # key = fact_class (snake_case / dotted)
    owner: package-manifest             # required — the ONE producing surface
    mirrors:                            # surfaces expected to restate the fact;
      - readme                          #   each diffed against the owner only
      - changelog                       #   (star topology — never pairwise N×N)
    determinism: deterministic          # deterministic | llm-judged
    depth_tier: T1                      # T1 value-equality | T2 judged/semantic
    staleness_bound: 0                  # days a mirror may lag before lag = drift
    criticality: high                   # critical | high | medium (severity ceiling)
    volatile: false                     # true = mirrors expected to trail (Info-level
                                        #   replication lag inside the bound)
    adjudicated_by: jeremy              # optional provenance — who made the call
    adjudicated_on: YYYY-MM-DD          # optional provenance — when
  license:
    owner: license-file
    mirrors: [readme]
    determinism: deterministic
    depth_tier: T1
    staleness_bound: 0
    criticality: high
    volatile: false
```

**Resolution rule:** when two artifacts disagree on a fact of class F — if the registry has a row for F, the artifact belonging to that row's `owner` class is correct and the finding is filed against the other artifact. If the registry has **no row** for F, emit the finding as `unowned fact-class — human adjudication needed`: list both values and locations, name no winner, never guess.

**Reference:** See `references/sot-registry.md` for the full registry specification, fact-class and artifact-class vocabularies, and the bootstrap appendix.

### Step 2: Inventory Documentation Artifacts

Scan for all documentation artifacts that will be audited:

```bash
# Find all documentation files
echo "Scanning for documentation artifacts..."
```

Use Glob to find:

- `README.md`, `README.*`
- `CLAUDE.md`
- `CHANGELOG.md`, `CHANGES.md`
- `000-docs/**/*.md`
- `docs/**/*.md`
- `planning/**/*.md`
- `VERSION`, `version.txt`
- `.github/workflows/*.yml`, `.github/workflows/*.yaml`
- Package manifests: `package.json`, `Gemfile`, `*.gemspec`, `pyproject.toml`, `Cargo.toml`, `go.mod`

Print a summary of what was found:

```
echo "Documentation artifacts found:"
echo "  - README: [yes/no]"
echo "  - CLAUDE.md: [yes/no]"
echo "  - CHANGELOG: [yes/no]"
echo "  - Canonical docs (000-docs/): [count] files"
echo "  - Other docs (docs/): [count] files"
echo "  - Planning docs: [count] files"
echo "  - CI workflows: [count] files"
echo "  - Package manifests: [list]"
```

### Step 3: Run Drift Checks

Execute ALL applicable checks from the list below. Each check is independent — run every check that has the required files present. Skip checks whose input files don't exist (note the skip, don't error).

Every check carries a **Lane** tag:

- **Deterministic** — existence, string-equality, and exact-comparison checks. Findings may be Critical, Warning, or Info.
- **LLM-judged (advisory)** — checks requiring semantic judgment. Findings are ⚪ Advisory, always — never Critical, never blocking.

**Reference:** See `references/drift-categories.md` for category definitions and severity guide.

#### Check 3.1: Index vs Filesystem (Category 7 — Index/Reference Drift)

**Lane:** Deterministic (referential integrity — no registry row needed; the filesystem is the definitional referent).

If `000-docs/000-INDEX.md` exists:

1. Read the index file
2. Extract all file paths listed in the index
3. For each path, verify the file exists on disk using Glob
4. Scan the `000-docs/` directory for files NOT listed in the index
5. Report: missing files (listed but don't exist), unlisted files (exist but not indexed)

#### Check 3.2: Version String Consistency (Category 1 — Status Drift)

**Lane:** Deterministic. **Fact class:** `version-string`.

Collect version strings from ALL available sources:

- `VERSION` or `version.txt` file
- `package.json` → `version` field
- `*.gemspec` → `version` attribute
- `pyproject.toml` → `[project] version` or `[tool.poetry] version`
- `Cargo.toml` → `[package] version`
- `CHANGELOG.md` → first version header (e.g., `## [1.2.3]` or `## 1.2.3`)
- `README.md` → version badges, install commands with version numbers
- `CLAUDE.md` → any version references

Compare all found version strings. If they disagree, resolve via the `version-string` registry row and flag all deviations from the registered authority. No row → emit `unowned fact-class — human adjudication needed` with every value and location; name no winner.

#### Check 3.3: README Commands vs CI Workflows (Category 4 — CI/Validation Drift)

**Lane:** Deterministic. **Fact class:** `ci-commands`.

If both README and `.github/workflows/` exist:

1. Extract shell commands from README code blocks (look for `bash`, `shell`, `sh` fenced blocks and inline backtick commands in "Getting Started", "Development", "Testing", "Usage" sections)
2. Extract `run:` step commands from all workflow YAML files
3. Compare test commands, build commands, lint commands (exact string comparison)
4. Flag differences, resolving via the `ci-commands` registry row; no row → unowned fact-class callout

#### Check 3.4: CLAUDE.md Doc Table vs Actual Docs (Category 7 — Index/Reference Drift)

**Lane:** Deterministic (referential integrity — no registry row needed).

If `CLAUDE.md` references specific files or directories:

1. Extract all file/directory paths mentioned in CLAUDE.md
2. Verify each path exists
3. Flag references to non-existent files or directories

#### Check 3.5: Stale Phase/Status Language (Category 1 — Status Drift)

**Lane:** LLM-judged (advisory). **Fact class:** `phase-status`.

Search all documentation for phrases that may indicate stale status:

- "no application code" / "no code exists" / "scaffold only" / "placeholder" — flag if `lib/`, `src/`, or `app/` contains actual source files
- "pre-release" / "not yet released" — flag if git tags show version releases
- "planned" / "upcoming" / "future" — flag if the described feature exists in code
- Phase references (e.g., "Phase: Scaffolding") — cross-reference against actual project maturity

Use Grep to search for these phrases, then validate against the filesystem. The grep is deterministic; deciding whether the language is actually stale is semantic judgment, so every finding here is ⚪ Advisory.

#### Check 3.6: Capability Claims vs Code (Category 3 — Capability/Behavior Drift)

**Lane:** LLM-judged (advisory). **Fact class:** `capability-claims`.

If README has a features section (look for `## Features`, `## Capabilities`, `## What it does`, bullet lists under these headers):

1. Extract each claimed feature/capability
2. For each claim, search the codebase for corresponding implementation
3. Flag overclaims (feature listed but no code found)
4. Also: scan for significant code modules/classes that have NO documentation mention (underdocumented features)

Mapping a prose claim to an implementation is semantic judgment — every finding here is ⚪ Advisory.

#### Check 3.7: Cross-Doc Fact Comparison (Category 6 — Cross-Doc Contradiction)

**Lane:** Deterministic for exact-value facts; LLM-judged (advisory) for the description comparison.

Extract and compare key facts across documents:

- **License** (fact class `license`): README license mention vs LICENSE file vs package manifest license field — deterministic
- **Language/runtime version** (fact class `runtime-version`): README vs package manifest vs CI workflow matrix — deterministic
- **Repository URL** (fact class `repository-url`): README badges/links vs package manifest repository field vs git remote — deterministic
- **Description** (fact class `project-description`): README first paragraph vs package manifest description vs CLAUDE.md purpose — semantic equivalence is a judgment call, so report in the advisory lane

Flag any contradictions. Resolve each via its fact-class registry row; no row → unowned fact-class callout.

#### Check 3.8: Broken Cross-References (Category 7 — Index/Reference Drift)

**Lane:** Deterministic (referential integrity — no registry row needed).

Scan all markdown files for internal links and references:

1. Find all `[text](path)` links where path is a relative file path (not URL)
2. Find all explicit file path references in prose (e.g., "see `docs/setup.md`")
3. Verify each referenced file exists
4. Flag broken references with source file, line number, and dead target

#### Check 3.9: Planning-vs-Implementation State (Category 5 — Planning-vs-Implementation Confusion)

**Lane:** LLM-judged (advisory). **Fact class:** `planning-status`.

If `planning/` directory exists:

1. Read planning documents for listed epics, features, milestones
2. Check which planned items have corresponding code implementations
3. Flag: planning says "future" but code exists (stale planning)
4. Flag: docs present planning items as if implemented (overclaim)

Judging whether code "implements" a planned item is semantic — every finding here is ⚪ Advisory.

### Step 4: Compile Report

Produce the report in this exact structure. Deterministic and advisory findings are structurally separated — never mixed in one section.

```markdown
# Document Consistency Audit Report

**Project:** [repo name or directory name]
**Date:** [current date]
**Registry:** [path + fact classes covered | "not found — bootstrap mode, all fact classes unowned"]

## Executive Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical (deterministic only) | [n] |
| 🟡 Warning (deterministic only) | [n] |
| 🔵 Info (deterministic only) | [n] |
| ⚪ Advisory (LLM-judged) | [n] |
| **Total** | **[n]** |

## Part A — Deterministic Findings

### Category 1: Status Drift
[Findings or "No issues found."]
### Category 4: CI/Validation Drift
[Findings or "No issues found."]
### Category 6: Cross-Doc Contradiction
[Findings or "No issues found."]
### Category 7: Index/Reference Drift
[Findings or "No issues found."]

## Part B — Advisory Findings (LLM-judged, never blocking)

### Category 1: Status Drift (phase/status language)
### Category 3: Capability/Behavior Drift
### Category 5: Planning-vs-Implementation Confusion
### Category 6: Cross-Doc Contradiction (description)
[Findings or "No issues found." per section]

## Unowned Fact Classes — Human Adjudication Needed

[One entry per conflict whose fact class has no registry row: fact class, all values, all locations. No winner named.]

## Proposed Registry Rows (bootstrap draft — requires human adjudication)

[Only when unowned fact classes were encountered: a fenced YAML block of drafted rows per the Bootstrap section. The skill never writes sot-map.yaml itself.]

## Priority Actions

[Numbered list of the most impactful fixes, ordered by severity then effort. Deterministic findings first; advisory items listed last and labeled advisory.]
```

**Each finding MUST include:**

- **Severity:** 🔴 Critical / 🟡 Warning / 🔵 Info (deterministic) or ⚪ Advisory (LLM-judged)
- **Fact class:** the registry row cited, or `unowned`
- **What the authority says:** [value from the registered-authority artifact — omit for unowned; list values symmetrically instead]
- **What the drifted artifact says:** [the drifted claim]
- **Location:** `file_path:line_number` for both artifacts
- **Auto-fixable:** Yes / No (could a simple text replacement fix this? reported only — this skill never applies fixes)

### Step 5: Summary

Print a one-line summary after the report:

```
echo ""
echo "Audit complete: [n] critical, [n] warning, [n] info, [n] advisory findings across [n] artifacts."
```

### Step 6: Persist the Local Run

Save each local report into the caller's Intent OS checkout (default
`~/000-projects/intent-os`) using
`${CLAUDE_SKILL_DIR}/scripts/persist-report.py`. Read
[report persistence](references/report-persistence.md) for the input contract,
disclosure policy, filing rules and failure recovery. Use `Bash(python3:*)` only
for this helper as a workflow instruction, not an OS sandbox. Pass the actual
audited directory as `--audited-root`; the writer refuses its report/index
destination inside that tree. Read-only audit behavior is an instruction-level constraint; the Git and Python
grants do not enforce filesystem immutability.

Pass the complete Part A/Part B report and any caller-supplied repair evidence.
Do not invent fixes or treat advisory findings as adjudicated facts. This helper
writes the approved report and an index entry in Intent OS; it never fixes the
audited project, edits the registry, or ingests into the governed brain.

Read the actual result. A missing policy, rejected content, receipt failure or
busy destination is **HELD**, never a saved report. Preserve the conversation
report and name the content-free failure code; do not bypass the filter or copy
the rejected payload into another log. On success, include the returned record
path and SHA-256 in the summary. During `/release`, retain the existing release
audit trail too; only deterministic Critical findings affect its blocking gate.

If there are deterministic critical findings, add:

```
echo "⚠️  Critical issues should be resolved before release."
```

## Severity Assignment Rules

Apply these rules consistently. **Hard rule: LLM-judged findings are ⚪ Advisory, always — never Critical, never Warning, never blocking. No exceptions.**

| Condition | Lane | Severity |
|-----------|------|----------|
| Version mismatch, fact class registered | Deterministic | 🔴 Critical |
| Any conflict on an unowned fact class | Deterministic | 🟡 Warning + unowned callout |
| README test command doesn't match CI | Deterministic | 🟡 Warning |
| Index file missing entries for existing docs | Deterministic | 🟡 Warning |
| Cross-doc disagreement on exact-value fact | Deterministic | 🟡 Warning |
| Broken internal link/reference | Deterministic | 🟡 Warning |
| Extra index entries referencing deleted files | Deterministic | 🔵 Info |
| Feature claimed in README but absent from code | LLM-judged | ⚪ Advisory |
| "scaffold only" language in repo with code | LLM-judged | ⚪ Advisory |
| Planning doc describes implemented feature as future | LLM-judged | ⚪ Advisory |
| Description drift between README/manifest/CLAUDE.md | LLM-judged | ⚪ Advisory |
| Underdocumented feature (exists in code, not in docs) | LLM-judged | ⚪ Advisory |

## Bootstrap: Drafting Registry Rows

Project-type auto-detection survives **only** here — it is a bootstrap heuristic for drafting registry rows, never runtime authority for resolving a conflict.

When the registry is missing or a fact class is unowned, draft proposed rows for the human to adjudicate:

**1. Detect project type** by scanning the working directory for file markers.

**Check for engineering markers:**

- Directories: `lib/`, `src/`, `app/`, `spec/`, `test/`, `tests/`
- Files: `Gemfile`, `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `*.gemspec`, `Makefile`, `CMakeLists.txt`, `pom.xml`, `build.gradle`

**Check for marketing/content markers:**

- Files: `index.html` (at root), `wp-content/`, `themes/`
- Absence of `lib/`, `src/`, `app/`

**Decision:**

- Engineering markers found, no marketing-only markers → **Engineering repo**
- Marketing markers found, no engineering markers → **Marketing/content site**
- Both found → **Hybrid**
- Neither found → **Unknown** — draft conservatively as engineering repo

Detection is additive — check for ANY marker in each category. A single match is sufficient.

**2. Draft rows** mapping each unowned fact class encountered to an authority artifact class, using the legacy hierarchy in `references/sot-registry.md` (appendix) as the drafting heuristic.

**3. Emit the drafted rows** in the report's "Proposed Registry Rows" section as a fenced YAML block, explicitly marked `bootstrap draft — requires human adjudication`. The skill never writes `sot-map.yaml` — a human reviews, edits, and commits the rows.

## Integration with /release

This skill is called by `/release` during Phase 1.6 (Cross-Artifact Consistency Validation). Only Part A deterministic findings feed the release blocking gate: deterministic 🔴 Critical findings block the release. Part B advisory findings and unowned fact-class callouts are surfaced for human review and never block. When invoked from `/release`, the report is incorporated into the release audit trail rather than printed standalone.

## Output

The skill produces a structured markdown report containing:

1. **Executive summary** — finding counts by severity (Critical/Warning/Info/Advisory)
2. **Registry header** — which registry was loaded and which fact classes it covers (or bootstrap mode)
3. **Part A — deterministic findings** by drift category
4. **Part B — advisory (LLM-judged) findings** by drift category, structurally separate
5. **Unowned fact classes** — conflicts needing human adjudication, no winner named
6. **Proposed registry rows** — bootstrap drafts for human review, when applicable
7. **Priority actions** — ordered list of the most impactful fixes

Each individual finding includes: severity icon, lane, fact class, what the authority artifact says (when registered), what the drifted artifact says, file paths with line numbers, and whether the fix is auto-applicable.

The report is printed to the conversation and, after the disclosure gate accepts
it, saved as a dated Intent OS audit record. During `/release`, it is also
incorporated into the existing release audit trail. Report persistence has its
own saved/HELD result; it does not change finding severity or release policy.

## Error Handling

| Condition | Behavior |
|-----------|----------|
| Registry (`sot-map.yaml`) not found | Bootstrap mode: all fact classes unowned; conflicts reported with no winner named; drafted rows emitted |
| Registry unparseable | Treat as not found; report the parse error verbatim in the report header |
| Conflict on a fact class with no registry row | Emit `unowned fact-class — human adjudication needed`; never guess |
| No README or CLAUDE.md found | Skip checks that require those files; note in report |
| No CI workflows found | Skip CI drift checks (3.3); note "No CI workflows found — CI checks skipped" |
| No `000-docs/` directory | Skip index checks (3.1); note in report |
| No planning directory | Skip planning-vs-implementation check (3.9); note in report |
| No package manifest found | Skip version consistency check for that source; use whatever version sources exist |
| Empty repository (no files) | Produce an empty-scope report with both lanes and no invented findings; persist it through Step 6 |
| Binary files in doc paths | Skip binary files; only audit text/markdown files |

Audit checks skip missing inputs and report what could be verified. Persistence
failures remain explicit HELD results; a printed report does not prove a durable
record was saved.

## What This Skill Does NOT Do

- Does not auto-fix anything — it reports. Fixes are a separate step. It never writes `sot-map.yaml` either — drafted rows are for human review.
- Does not guess authority — a conflict on an unowned fact class is reported for human adjudication, never resolved by ranking or inference.
- Does not read the governed brain as ground truth for generated facts (see [Truth Invariant](#truth-invariant)).
- Does not audit email or CRM content — out of scope for v1.
- Does not use WebSearch or WebFetch — filesystem and git only. Does not validate external URLs (no HTTP requests).
- Does not run tests or execute code from the audited project. The bundled
  persistence helper executes only the existing destination disclosure adapter.
- Does not check grammar or writing quality.
- Does not assess documentation completeness (only consistency).

## Resources

- Drift category definitions and severity guide: `references/drift-categories.md`
- Registry specification, fact-class and artifact-class vocabularies, resolution rule, and the legacy-hierarchy bootstrap appendix: `references/sot-registry.md`
- Default registry location: `~/000-projects/intent-os/sot-map.yaml` (path configurable per invocation)
