<!-- doc-class: canonical -->

# Schema Changelog — Claude Code Skills Spec (Intent Solutions)

This file tracks every change to the validator's required-fields set, field
migrations (deprecations, removals, renames), validator script versions, and
master-spec-doc revisions. It is **separate** from the main repo `CHANGELOG.md`
and is versioned independently.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Schema version follows [Semantic Versioning](https://semver.org/) where:

- **MAJOR** — breaking changes to required-fields set, validator API surface,
  or rejected/accepted-fields semantics.
- **MINOR** — additive changes (new optional fields, new tier, additional
  marketplace polish recommendation).
- **PATCH** — clarifications, doc updates, internal refactors with no
  observable change to validator output.

Cross-references:

- Master spec doc: `000-docs/6767-b-SPEC-DR-STND-claude-skills-standard.md`
- Validator: `scripts/validate-skills-schema.py`
- Bulk-fix tool: `scripts/batch-remediate.py`
- Repo-level releases: `CHANGELOG.md`

---

## NON-NEGOTIABLES — read before touching this file

Established 2026-04-28 after a one-day schema debacle (see "How we got here"
below). These rules are NOT to be relaxed without explicit written approval
from Jeremy Longshore in the issue/PR thread BEFORE the change lands.

1. **`ALWAYS_REQUIRED` is the IS enterprise 8-field set:**

   ```
   {name, description, allowed-tools, version, author, license, compatibility, tags}
   ```

   This is intentionally stricter than Anthropic's published spec. Do not
   reduce it. Do not reframe it as "marketplace polish" or "tracking
   recommendations." It's the canonical IS rubric.

2. **Marketplace tier produces ERRORS for missing required fields, not
   warnings.** Demoting required-field errors to warnings breaks the
   marketplace gate.

3. **The IS rubric SITS ON TOP of Anthropic's spec.** It does not replace
   Anthropic's spec, and it does not need to match Anthropic's spec floor.
   Anthropic's spec is intentionally permissive (every field is optional);
   the IS marketplace is intentionally strict.

4. **Spec source priority for technical correctness:**
   1. [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) — primary, complete frontmatter reference
   2. [agentskills.io/specification](https://agentskills.io/specification) — open standard Claude Code follows
   3. [platform.claude.com/docs/en/agents-and-tools/agent-skills/overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — API surface
   4. The IS enterprise rubric layered on top — additive, never subtractive

5. **Tracking metadata (version, author, license) is REQUIRED at marketplace
   tier, not optional polish.** Anthropic doesn't track these in their own
   reference repo; that's their stylistic choice. The IS marketplace requires
   them for trust signals, downstream pinning, and legal clarity.

6. **Bug fixes that bring the validator into spec compliance are always OK
   to apply autonomously.** Examples: accepting YAML lists for `allowed-tools`,
   fixing conditional-field rules to match documented defaults, adding
   missing documented fields like `arguments` / `paths` / `shell`. These
   are technical-correctness fixes — not "spec realignment."

7. **Architectural changes (required-fields set, tier model, error vs
   warning semantics) need explicit approval BEFORE the change lands.**

---

## Kernel changelog citation — authoring/v1 semantics are canonical upstream

Standing rule (2026-06-12, changelog-observance gate per intent-eval-lab doc
045 § 6): the contract semantics of the `authoring/v1` family — required-field
sets, folds, field types for skill-frontmatter and the other authoring
contracts — are **CANONICAL in the Spec Authority Kernel's changelog**:

[`@intentsolutions/core` → `schemas/authoring/v1/CHANGELOG.md`](https://github.com/jeremylongshore/intent-eval-core/blob/main/schemas/authoring/v1/CHANGELOG.md)

When an entry below concerns a kernel-tracked field, it **cites the matching
kernel changelog entry instead of duplicating its rationale**. CCPI entries stay
scoped to what changed HERE (validator behavior, tier wiring, prose-spec text);
the "why" for contract semantics lives in the kernel entry being cited.

This section is additive: it does not modify, weaken, or reinterpret the
NON-NEGOTIABLES above. The IS 8-field rubric and the errors-not-warnings tier
semantics are unchanged — the kernel encodes that same rubric as its
`is-overlay` schemas, and its overlay-required floor evolves under the same
approval discipline.

---

## How we got here — the 2026-04-28 schema debacle

This section exists so the same mistake doesn't get re-made. The full
back-and-forth is preserved below in the version-by-version changelog.

**The mistake**: starting from a valid observation ("the IS validator requires
8 fields where Anthropic's published spec only requires 2"), I drove four
schema-version churns trying to "realign" the IS rubric to Anthropic's
permissive floor. Each time, the user pushed back; each time, I added a
correction layer instead of stopping. End state: same enterprise standard
we started with, plus a few genuine technical fixes (compatibility migration,
allowed-tools YAML-list parsing, conditional-field rules), at the cost of
a day of churn and four schema versions.

**Why it was wrong**: the IS enterprise rubric is intentionally stricter than
Anthropic's spec. That's the value-add. Reducing it to match the spec floor
deletes the value. Anthropic's spec being permissive is not a bug we need
to fix in our rubric; it's a feature of the _open_ spec that the _enterprise_
layer sits on top of.

**Process failure**: I worked off summaries of the Anthropic spec instead of
reading [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)
line-by-line first. When the user pushed back the first time, I did a deeper
read but kept the "spec realignment" framing instead of recognizing it as
the wrong direction. Each subsequent correction was a half-fix that the user
had to reject again.

**What stuck (the kept changes from the experiments)**:

- `compatible-with` (closed CSV platform list) → `compatibility` (free-text per AgentSkills.io spec). The deprecated alias still parses; `batch-remediate.py --migrate-compatible-with` migrates files in bulk.
- `when_to_use` correctly reclassified as documented Anthropic optional (was wrongly flagged as deprecated in earlier IS rubrics).
- `arguments`, `paths`, `shell` added to schema registry with type validation — all documented Anthropic optional fields that were missing from the registry.
- `effort: xhigh` added to valid values per Anthropic doc (`low/medium/high/xhigh/max`).
- `allowed-tools` now accepts both YAML list and space-separated string per Anthropic spec (was previously rejecting YAML lists and only splitting on commas).
- `agent` field no longer triggers "missing required" warning when absent with `context: fork` (Anthropic doc: "If omitted, uses general-purpose").
- `argument-hint` conditional fixed (no longer falsely suppressed by `disable-model-invocation: true` since the user can still invoke via `/`).
- `${CLAUDE_EFFORT}` added to YAML substitution allow-list.
- New tooling: `scripts/batch-remediate.py` for bulk migrations.
- New doc: this `SCHEMA_CHANGELOG.md` (was no schema-level changelog before).

**What got reverted (the structural changes that should have never happened)**:

- Reducing `ALWAYS_REQUIRED` from 8 fields to {name, description}. Reverted.
- Reframing tier model so marketplace was warnings-only. Reverted to errors-only.
- Reclassifying `version`/`author`/`tags` as `source: 'tracking'` / `'marketplace polish'`. Reverted to `source: 'enterprise'`.
- Rewriting `templates/skill-template.md` as a "supreme canonical form" with placeholders for every documented field. Reverted to enterprise template (8 required fields filled in, optional fields commented).
- Rewriting `frontmatter-spec.md` section 3 as "Tracking & Marketplace Polish Fields." Reverted to "Intent Solutions Enterprise Required Fields."

**The dance not to repeat**: don't try to "realign IS to Anthropic spec." The two
operate at different layers. IS = strict enterprise rubric. Anthropic = permissive
open spec. The validator already knows about both. Bug fixes that improve spec
compliance are welcome; structural changes to the IS rubric are not.

---

## [4.1.0] — 2026-09-09 compatibility amendment

### Added

- Recognize the optional subagent `experimental` map documented by Anthropic in
  Claude Code v2.1.248. Validate its current `cacheTtl` setting as `5m` or `1h`
  and warn when a key would be ignored by Claude Code.

### Changed

- Accept `manual` as the documented alias for `permissionMode: default`.
- Accept full Claude model IDs such as `claude-opus-5` in addition to the
  `sonnet`, `opus`, `haiku`, `fable`, and `inherit` aliases.
- Reconcile the `ccpi validate` compatibility path with the same contract. It
  no longer requires retired `capabilities` metadata and now validates the
  current model, effort, permission, MCP, and experimental forms.
- Recognize the current skill `background` field and `fable`/full-model forms
  documented in Claude Code's live skills frontmatter reference.

This is a spec-compliance update under NON-NEGOTIABLE #6. It changes no required
field set, tier boundary, or error-versus-warning policy. Primary source:
[`code.claude.com/docs/en/sub-agents`](https://code.claude.com/docs/en/sub-agents),
fetched 2026-09-09.

## [4.1.0] — 2026-08-19

**Added** (blueprint 727 E4.3/E4.4): `--safety-metrics` mode — emits the
safety-ratchet metric sets as JSON (first-party `bare_bash` skills, the
`tier2_tool_safety` finding set, every YAML `shell_substitution` occurrence as
`file::field`; `.source.json` mirror subtrees excluded as upstream-owned) and
exits. Consumed by `scripts/check-safety-ratchet.mjs`, the triple-keyed
monotone ratchet in the `validate` job. No grading semantics changed; the mode
reuses `parse_allowed_tools` / `tier2_check_tool_safety` /
`check_yaml_shell_substitution` verbatim so the gate owns no classification
logic of its own.

## [4.0.2] — 2026-08-19

### Fixed

- **Compliance-rate denominator** (blueprint 727 Epic 4 bead 4.12): the summary rate divided
  compliant files (which include the plugin-manifest validation lane) by skills+commands+agents
  only, producing impossible rates (observed 224.1%). The denominator now includes validated
  plugin manifests and the summary prints their count. Per-file verdicts, error classes, and the
  agents-only 253-error baseline are unaffected. A unit test asserts 0 ≤ rate ≤ 100 and
  compliant ≤ total.

## [4.0.1] — 2026-08-18

### Added

- **Portable runtime variables accepted** (blueprint 727 Epic 3 bead E3.9): `${SKILL_DIR}` and
  `${PLUGIN_ROOT}` join `YAML_VALUE_ALLOWED_VARS` as the harness-free spellings of
  `${CLAUDE_SKILL_DIR}` / `${CLAUDE_PLUGIN_ROOT}`. Canonical-layer artifacts write the portable
  form; the claude-code adapter (`scripts/adapters/claude-code-adapter.mjs`) emits the branded
  form. The anti-absolute-path posture is unchanged — same variables, harness-free spelling.
  No required field, tier semantics, or error class changed.

## [4.0.0] — 2026-08-16 — Malformed `allowed-tools` entries fail closed

**Breaking error-vs-warning correction — NON-NEGOTIABLE #7. APPROVED by the
ratified modernization blueprint 727 E1.11 and Jeremy Longshore's written
execution directive.** The major version follows this changelog's rule for a
change to rejected/accepted validator semantics.

### Changed

- Structurally malformed `allowed-tools` entries now produce an **ERROR** at
  standard, marketplace, and enterprise tiers. This covers unbalanced
  parentheses, empty scopes, missing tool names, and illegal base identifiers.
- Well-formed but unknown tool names remain **WARNING**-level advisories; E1.11
  does not introduce or change the tool-token vocabulary.
- CSV, space-separated string, YAML-list, and folded-scalar forms remain
  accepted when their parsed entries are structurally valid.
- The schema 3.0.0 migration note's planned removal of the deprecated
  `compatible-with` alias in 4.0.0 is **superseded and deferred**. This focused
  release does not remove that compatibility surface; removal requires its own
  measured, owner-approved migration slice.

### Corpus and authority evidence

- All 2,802 first-party tracked skills were remeasured: 2,801 declare
  `allowed-tools`, with zero malformed declarations, so the new error adds no
  first-party baseline debt.
- The 377 mirror-owned skills were recorded but not edited. The ten Kobiton
  folded-scalar files (five canonical / `.codex` byte-identical pairs) remain
  parseable and valid.
- The kernel v1 shape check does not encode this entry grammar. That advisory
  semantic delta remains outside E1.11; the repository validator retains
  authority under `CLAUDE.md` until the separately governed kernel cutover.

---

## [3.16.1] — 2026-07-23 — Security lane: load-time shell + disallowed-tools entry validation (advisory)

**Additive advisory-only surface — no change to `ALWAYS_REQUIRED`, tiers, or
error-vs-warning semantics for required fields.** Residual of closed PR #1113
(VALID_TOOLS portion already shipped as 3.16.0 via #1115).

### Added

- **Load-time shell substitution findings** on SKILL.md bodies: `` !`cmd` `` and
  ` ```! ` blocks reported as `[security]` warnings (not errors). Ordinary
  fenced documentation of the syntax is excluded. Kill switch named:
  `disableSkillShellExecution`.
- **`disallowed-tools` entry validation** mirroring `allowed-tools` — misspelled
  or legacy names in a deny list no longer pass silently (a deny that matches
  nothing is worse than a missing deny).

### Why advisory

This is widely used, documented Claude Code preprocessing. Making the first
detection of it a merge-blocking error would burn trust. The goal is reviewable
surface, not a sudden corpus red wall.

---

## [3.16.0] — 2026-07-23 — Canonical 43-tool `VALID_TOOLS` + `Task`→`Agent` legacy alias (spec-compliance)

**Additive spec-compliance bug fix — no change to `ALWAYS_REQUIRED`, the tier
model, or error-vs-warning semantics.** Autonomous-OK class per NON-NEGOTIABLE
#6 (aligns the allowlist with the published tools reference).

### Changed

- **`VALID_TOOLS`** expanded from **13** names to the full **43** built-ins from
  [code.claude.com/docs/en/tools-reference](https://code.claude.com/docs/en/tools-reference)
  (captured 2026-07-23). The previous set omitted `Agent` (and dozens of other
  current tools) while listing the retired name `Task`.
- **`Task`** moved to **`LEGACY_TOOL_ALIASES` → `Agent`**. Still accepted, but
  emits a warning preferring `Agent` (rename since Claude Code v2.1.63; the
  SDK still emits `Task` in some `system:init` tool lists).
- Body-vs-allowlist tool-name regex updated to recognise the same set (plus the
  legacy `Task` alias so body mentions still count as references).

### Why this is not architectural

Unknown-tool feedback was already **advisory** (WARNING), not a marketplace
ERROR. Expanding the known set only removes false "unknown tool" warnings for
correct modern names and adds an explicit legacy-alias warning for `Task`.
`ALWAYS_REQUIRED`, tiers, and error-vs-warning semantics are untouched.

### Evidence

Pre-fix: declaring `Agent` in `allowed-tools` produced _Unknown tool 'Agent'_.
Post-fix: clean. Declaring `Task` produces the legacy-alias warning instead of
passing silently as a first-class tool.

### Source

IEP plan `golden-imagining-planet` Phase A; resumes Claude sessions
`fix-spec-currency-loop` + `run-tools-current-spec`.

---

## [3.15.2] — 2026-07-12 — `disallowed-tools` cross-field enforcement made real (spec-compliance, additive; closes claude-41c2.2)

**Additive spec-compliance implementation — no change to `ALWAYS_REQUIRED`, the
tier model, or error-vs-warning semantics.** Autonomous-OK class per
NON-NEGOTIABLE #6 (implements already-documented behavior; not architectural).
`disallowed-tools` has been _recognized_ since 3.7.0, but its two documented
rules (repo CLAUDE.md § Optional frontmatter 3.7.0, `000-docs/681`) were never
actually checked — the field parsed clean regardless of content.

### Added

- **Shape guard:** `disallowed-tools` must be a string or a YAML list (same
  shapes as `allowed-tools`). A non-string/non-list value (e.g. an int) is now
  an ERROR: _"'disallowed-tools' must be a list of strings or a space/comma-
  separated string"_.
- **Cross-field overlap rule:** a tool pattern MUST NOT appear in both
  `allowed-tools` and `disallowed-tools` — declaring a tool simultaneously
  permitted and denied is contradictory and almost always a mis-scoped list.
  Now an ERROR at **every tier**: _"contradictory tool declaration: […] appears
  in both allowed-tools and disallowed-tools"_. This mirrors the existing 3.5.0
  `requires_*` / `fallback_for_*` visibility-overlap rule; both lists normalize
  through the shared `parse_allowed_tools()` so `Bash(rm:*)` matches whether it
  was written CSV, space-separated, or as a YAML list.

### Why this is not architectural

The `disallowed-tools` field itself stays **optional** (ALWAYS_REQUIRED is
untouched); the new errors only fire when the field is present and either
malformed or self-contradictory. Error-vs-warning semantics for the required
set are unchanged. This is the "make an already-recognized optional field's
documented constraints real" class, parallel to how 3.8.0 made `allowed-tools`
entry validation real.

### Corpus safety

All 26 in-corpus SKILL.md files that declare `disallowed-tools` (the
penetration-tester pack, defense-in-depth denials of tools NOT in their
`allowed-tools`) were re-validated: **zero** newly fail on the overlap or shape
checks.

### Tests

Six regression tests added to `tests/test_validate_skills_schema_frontmatter.py`:
overlap-is-error (standard + marketplace tiers), disjoint-is-clean, shared-
normalization overlap (space form vs list form), disallowed-without-allowed is
clean (guarded), and bad-shape is error.

---

## [3.15.1] — 2026-07-02 — Body-vs-allowlist regex recognizes kebab/snake MCP server names (spec-compliance bug fix, issue #843)

**Bug fix — no change to `ALWAYS_REQUIRED`, the tier model, or error-vs-warning
semantics.** Autonomous-OK class per NON-NEGOTIABLE #6 (spec-compliance
technical-correctness fix); PR gated for review per the Backlog Zero campaign
governance rule (validator changes wait for Jeremy).

### Fixed

- **`_RE_MCP_FQ` (the #843 body-vs-allowlist scanner) now matches MCP server
  names containing hyphens or underscores.** The old pattern
  `mcp__[a-zA-Z0-9]+__[a-zA-Z0-9_]+` only accepted a bare-alnum server segment,
  so real-world fully-qualified refs like `mcp__semantic-scholar__paper_search`
  (kebab) and `mcp__plugin_automate_kobiton__getApp` (snake) never matched at
  all. A declared-and-used tool with such a server name was therefore invisible
  to the body scan and falsely warned as _"declares MCP tool … but the body never
  references it — over-declared privilege"_. New pattern:
  `mcp__[a-zA-Z0-9]+(?:[-_][a-zA-Z0-9]+)*__[a-zA-Z0-9_]+`.
- **Separator-ambiguity choice (deliberate):** the server segment is alnum runs
  joined by a SINGLE `-`/`_`, and each joiner must be followed by an alnum char —
  so the segment can never swallow the `__` separator (whose second char is `_`,
  not alnum). `mcp__a_b__c` parses as server `a_b` + tool `c`, deterministically.
  The charset mirrors the existing `RE_MCP_TOOL_REF` (allowed-tools permission
  form, which already accepted `mcp__database-explorer__query_database`) minus
  its `^…$` anchors — `_RE_MCP_FQ` was the lone outlier. The tool segment is
  unchanged (`[a-zA-Z0-9_]+`, underscores already allowed).

### Tests

Five regression tests added to the #843 section of
`tests/test_validate_skills_schema_frontmatter.py`: kebab declared+used clean,
snake declared+used clean, undeclared kebab body ref still a CHECK 1 error,
over-declared kebab tool still warns, and the `mcp__a_b__c` separator guard.

### Backward compatibility

Non-breaking for correct agents: anything that passed at 3.15.0 with a truthful
allowlist still passes at 3.15.1 with same or fewer warnings. Repo-wide
marketplace run at landing (old vs new validator, same tree):

- **−4 false over-declared warnings** — `mcp__dolt-mcp-vcs__{query,list_databases}`,
  declared AND genuinely used in agent bodies, previously invisible to the scan.
- **+2 previously-invisible TRUE-positive CHECK 3 errors** —
  `plugins/community/sprint/agents/{nextjs-diagnostics-agent,ui-test-agent}.md`
  reference `mcp__next-devtools__*` / `mcp__claude-in-chrome__*` in their bodies
  while declaring zero `mcp__*` tools. These are genuine #843 defects (every
  call runtime-blocked) that the old regex could not see — the check working
  as designed, not a regression. Both files are pre-existing on `main` and
  outside this PR's diff; no blocking CI lane runs a full-tree marketplace
  pass, so no gate flips. Fix tracked as ordinary agent-file remediation.

---

## [3.15.0] — 2026-07-01 — Enterprise body-section checks credit equivalent heading names (iel-62j fairness, additive)

**Additive MINOR — no change to `ALWAYS_REQUIRED`, the tier model, or
error-vs-warning semantics.** The enterprise (marketplace) body-section checks
now credit equivalent, well-understood heading names, so an external contributor
is **not** failed for standard-but-non-IS section wording (`iel-62j`):

- Synonyms credited: `## Usage` ≈ `## Instructions`; `## Summary` /
  `## Capabilities` ≈ `## Overview`; `## Returns` ≈ `## Output`;
  `## Troubleshooting` ≈ `## Error Handling`; `## References` ≈ `## Resources`.
  Resolution runs through `SECTION_SYNONYMS` / `resolve_present_heading()`, so
  the presence, non-empty-content, and step-by-step checks all honor the
  synonyms uniformly.
- `RECOMMENDED_SECTIONS` was never a published standard (see the note there);
  requiring the EXACT IS wording was off-spec. This corrects that.
- **Not a semantics change.** An error still fires when NEITHER the canonical
  section NOR any synonym is present. Tiers, `ALWAYS_REQUIRED`, and the
  frontmatter `capabilities` **BAN** (NON-NEGOTIABLE) are all unchanged — only
  `## Capabilities` **as a heading** is credited as an `Overview` synonym, which
  is distinct from the still-banned frontmatter `capabilities` field.

**Version-number provenance (kills the label collision).** `3.15.0` here is the
validator's `SCHEMA_VERSION` constant (`scripts/validate-skills-schema.py`) — the
skills-spec schema line this changelog tracks, bumped by the `iel-62j` fairness
change. It shipped in the same PR window as the mirror-by-default external-sync
work (`000-docs/694-AT-DECR`, PR #932), but that sync/manifest machinery versions
on a **separate** axis; the `3.15.0` label refers **only** to the validator
schema, not to any sync-manifest or plugin version.

---

## [3.14.0] — 2026-06-28 — L2 consumer-cutover: plugin.json drift-gated against the kernel (additive, advisory)

**Additive MINOR — no change to any required-field set, tier model, or
error-vs-warning semantics.** Closes the second half of the auto-currency loop
(692-AA-AACR § 0.5): `PLUGIN_JSON_FIELDS` was hand-maintained with **no** comparison
to the kernel, so when upstream gained GA fields the validator silently went stale
and needed a hand-patch (the 3.12.0 event).

- New `load_kernel_plugin_fields()` reads the kernel's **current** plugin-manifest
  field surface from `@intentsolutions/core` `authoring/**v2**`
  (`upstream-base ∪ is-overlay`). v2, not v1 — the v1 plugin-manifest fold is an
  early ~10-field capture; v2 carries the full GA surface. Needs core `>=0.9.0`.
- `kernel_shadow_report()` gains a `plugin_manifest` block comparing
  `PLUGIN_JSON_FIELDS` against that surface; `print_kernel_shadow()` warns when CCPI
  is **stale** (a kernel field we lack). The existing `kernel-shadow-validation.yml`
  CI lane now surfaces plugin-manifest drift automatically — no more hand-patch.
- The shadow immediately caught one drift: the kernel sanctions a `metadata`
  plugin.json field (authoring/v2 is-overlay) that CCPI lacked — **adopted** into
  `PLUGIN_JSON_FIELDS` (now `fields_match: true`).

**Advisory** (`PLUGIN_JSON_FIELDS` stays authoritative until the DR-049 flip), so no
NON-NEGOTIABLE is touched — same posture as the existing skill-frontmatter + agent
kernel shadows.

---

## [3.13.0] — 2026-06-28 — plugin.json unrecognized-field handling: error → warning, + `--strict` (NON-NEGOTIABLE #7, **approved**)

**Error-vs-warning semantics change — NON-NEGOTIABLE #7. APPROVED by Jeremy
Longshore 2026-06-28** (sign-off recorded in the PR thread before landing).

`validate_plugin_json()` previously appended every unrecognized top-level
plugin.json field as an **ERROR** (`Unknown field … not in Anthropic spec`).
That hard-rejected valid current Anthropic plugins and diverged from the platform
in two ways:

1. **Anthropic's own `claude plugin validate` reports unrecognized fields as
   warnings, not errors** — "a plugin with only unrecognized-field warnings still
   passes validation and loads at runtime" (plugins-reference § "Unrecognized
   fields", verified live 2026-06-28). Only `--strict` promotes them to errors;
   wrong-_type_ fields still fail.
2. **This validator already warns (never errors) on unknown SKILL.md fields
   (`validate_frontmatter`, "UNKNOWN FIELDS") and unknown agent fields
   (`validate_agent`).** The plugin.json path erroring was the lone outlier.

Changes:

- Unrecognized plugin.json field → **WARNING** by default (was ERROR).
- New **`--strict`** CLI flag promotes those warnings back to errors (mirrors
  `claude plugin validate --strict`); thread through `validate_plugin` /
  `validate_plugin_json`. CI may opt in to catch typos before publishing.
- Wrong-**type** field and missing required **`name`** stay hard errors at every
  level — Anthropic fails those too.
- Adds a `difflib` near-miss "did you mean '<field>'?" hint, matching Anthropic's
  typo suggestion.

**Unchanged:** every required-fields set (SKILL `ALWAYS_REQUIRED`, agent floor),
tier model, and the missing-required-field-is-an-ERROR rule (NON-NEGOTIABLES
#1, #2). This change is strictly about _unrecognized_ fields, not _required_ ones.

---

## [3.12.0] — 2026-06-28 — plugin.json manifest brought up to current Anthropic GA spec (additive)

**Additive MINOR — no change to any required-field set, tier model, or
error-vs-warning semantics.** `PLUGIN_JSON_FIELDS` (the `.claude-plugin/plugin.json`
manifest allowlist) had only the pre-GA 15 fields. The Anthropic plugin manifest
has since gained several **GA** fields; the validator was therefore hard-rejecting
valid, current Anthropic plugins with `Unknown field: '<x>' — not in Anthropic
spec` (an ERROR), which is no longer true for these fields.

Added to `PLUGIN_JSON_FIELDS` (all optional; `name` remains the only required
field, unchanged):

| Field            | Type    | Status                     | Note                                                  |
| ---------------- | ------- | -------------------------- | ----------------------------------------------------- |
| `displayName`    | string  | GA (Claude Code v2.1.143+) | human-readable name in the `/plugin` picker           |
| `defaultEnabled` | boolean | GA (v2.1.154+)             | enabled by default absent a user preference           |
| `dependencies`   | array   | GA                         | required plugins w/ optional semver constraints       |
| `userConfig`     | object  | GA                         | user-configurable values prompted at enable time      |
| `channels`       | array   | GA                         | message-channel declarations bound to MCP servers     |
| `$schema`        | string  | GA (metadata only)         | JSON Schema URL; ignored at load time                 |
| `experimental`   | object  | experimental               | holds `experimental.themes` / `experimental.monitors` |

`TYPE_MAP` in `validate_plugin_json()` gained `boolean` (for `defaultEnabled`).

**Source of truth verified against** [code.claude.com/docs/en/plugins-reference](https://code.claude.com/docs/en/plugins-reference)
§ "Plugin manifest schema". Spec-compliance fix under **NON-NEGOTIABLE #6**
("adding missing documented fields" — explicitly autonomous-OK).

**Explicitly NOT changed here (NON-NEGOTIABLE #7 — needs sign-off):** the
unknown-field handling for _genuinely_ unknown fields remains an ERROR. Anthropic's
own `claude plugin validate` treats unrecognized fields as **warnings** (errors
only under `--strict`); aligning the IS validator to that warn-not-error policy is
an error-vs-warning-semantics change and is **deferred pending explicit approval**.
Adding the GA fields above already removes the false rejection of valid current
plugins (those fields are no longer "unknown"); the remaining decision only
affects typos / other-ecosystem metadata.

---

## [3.11.0] — 2026-06-18 — Agent body-vs-allowlist consistency check (additive, issue #843)

**Additive MINOR — no change to any required-field set, tier model, or
error-vs-warning semantics for those fields.** `validate_agent()` now inspects
the agent BODY (previously it read only frontmatter) and cross-checks it against
the `tools` allowlist, which is a runtime gate (tools not listed are blocked at
runtime). Closes the defect class where an agent's body invokes an MCP tool it
never declares and silently runtime-blocks every call (surfaced on
`kobiton/automate#67` by the customer, not our validator).

New checks in `check_agent_body_vs_allowlist()`:

- **CHECK 1 (ERROR):** body contains a fully-qualified `mcp__<server>__<tool>`
  that is not in the declared allowlist (partial-coverage case).
- **CHECK 3 (ERROR):** the allowlist declares zero `mcp__*` tools but the body
  references fully-qualified MCP tools — highest-confidence form; every call
  would block.
- **CHECK 2 (WARN):** body backtick-mentions a verbCamelCase short name
  (`listDevices`, `getSession`, …) with no matching declared `mcp__*__<name>`.
  Heuristic; gated to MCP-oriented agents only (declares an mcp tool or has a
  FQ ref) to avoid flagging plain code prose like `getStaticProps`.
- **WARN (over-declared):** a declared `mcp__*__<tool>` whose suffix never
  appears in the body — privilege drift.

Fenced code blocks are stripped before matching so documented examples don't
trip the FQ checks. Errors are agent-level (agents are not tier-gated).

**Corpus impact:** run against all 317 in-repo agents — caught one genuine
pre-existing defect (`plugins/analytics/web-analytics/agents/data-collector.md`
invoked six `mcp__umami__*` tools with only `Read` declared), fixed in the same
change by declaring the six tools. Zero false-positive errors elsewhere.

Tests: `tests/test_validate_skills_schema_frontmatter.py` (9 `843` cases —
CHECK 1/2/3, over-declared, fenced-code exemption, non-MCP suppression, and an
end-to-end `validate_agent` fixture). `validate-agent` skill SKILL.md updated to
reference the validator-side check (the shell heuristic becomes a fallback).

---

## [3.10.0] — 2026-06-17 — AGENT gate flipped to kernel-strict + enterprise-fleshed (required-field-set change, **approved**)

**This is an architectural change to the AGENT required-field set** (NON-NEGOTIABLE
#7 — architectural changes need explicit approval BEFORE landing — governs it). It
ships under Jeremy's explicit 2026-06-17 sign-off: "strictness =
kernel-strict always" + "flesh out the entire spec enterprise — empties and all."
It does **NOT** touch the SKILL `ALWAYS_REQUIRED` set, the skill tier model, or skill
error-vs-warning semantics — only the agent contract. (The parallel skill treatment
is a separate, deliberate change — the skill required set is the debacle-sensitive
zone and moves only on its own explicit sign-off.)

**The required set is now two layers, both ERRORS at every tier (agents are NOT
tier-gated like skills):**

- **(a) Kernel floor (8):** `name, description, tools, model, color, version,
author, tags` — the kernel `agent-definition` effective-required set.
- **(b) Enterprise live set on top of the floor** — "flesh out the entire spec,
  empties and all," so every authored agent carries the full supported surface and
  the upgrade levers are always visible:
  - `+ disallowedTools, skills, background` for **all** agents → **11 required on a
    plugin agent** (the common case; `disallowedTools: []`, `skills: []`,
    `background: false` are the no-op empties).
  - `+ hooks, mcpServers, permissionMode` for **standalone** agents only → **14
    required** (those three are configured at the plugin level and runtime-ignored
    on a plugin agent, so requiring them there would be noise + a warning).
  - The five fields with **no valid empty value** — `effort, maxTurns, memory,
isolation, initialPrompt` — are carried as a commented **"upgrade levers"** block
    in the agent body template (visible standing menu, not parser-required).

Rationale: `/validate-agent` and the marketplace validator had drifted ~6 months and
were lenient on agents (only `name` + `description` required; the IS-invented
`capabilities` / `expertise_level` / `activation_priority` were warnings). 311 agents
shipping publicly in `plugins/*/agents/` were below bar (0/311 carried `tags`; 23
carried banned fields). A gate that does not enforce the standard cannot hold the
fleet to it — so the gate is fixed first.

Authority for the agent required set is the **Spec Authority Kernel**
(`@intentsolutions/core` `schemas/authoring/v1/agent-definition.schema.json`): the
union of the upstream-base floor `[name, description]`
(code.claude.com/docs/en/sub-agents § "Supported frontmatter fields") and the
is-overlay required delta `[tools, model, color, version, author, tags]`. Kernel
CHANGELOG is canonical for that schema.

- **Agents are NOT tier-gated like skills.** The required set (kernel floor ∪
  enterprise live set — 11 on a plugin agent, 14 standalone) is now an **ERROR at
  every tier** when any member is missing (was: only `name` + `description`). The
  `AGENT_ENTERPRISE_LIVE_COMMON` / `AGENT_STANDALONE_ONLY_REQUIRED` /
  `AGENT_UPGRADE_LEVERS` constants carry the layering; `is_plugin_agent` selects the
  11-vs-14 set.
- New `load_kernel_agent_required()`: existence-guarded read of the kernel
  `agent-definition` base + overlay layers; returns the union `required` set, or
  `None` (degrade to the inline `AGENT_ALWAYS_REQUIRED` mirror) when the kernel is
  not vendored. Never raises. This is the "consume the kernel schema" path; the
  inline mirror is the fallback, tagged with a TODO to the DR-049 consumer-cutover
  bead.
- `fable` added to the agent `model` enum →
  `[sonnet, haiku, opus, fable, inherit]` (matches the kernel enum +
  code.claude.com/docs/en/sub-agents § "Choose a model").
- Banned agent fields promoted **WARN → ERROR**: `capabilities`, `expertise_level`,
  `activation_priority`, `activation_triggers`, `type`, `category` (IS-invented, in
  no canonical spec) plus `compatible-with` / `when_to_use` (kernel
  `deprecationRegistry` universal fold). `DEPRECATED_AGENT_FIELDS` is now empty.
- `tools` accepts `string|array` (tolerant): the kernel narrows the wire form to a
  YAML array, but the documented Anthropic form is a comma-separated string and the
  public corpus uses both. Required-presence is enforced without forcing a
  mechanical re-typing of every agent. `tags` entries are validated as strings.
- Agent `description` over-length **warning** realigned `200 → 1536` (the kernel
  `disclosureMarkers` cap) so a trigger-rich A-grade description ("Use when…/Trigger
  with…") no longer warns. The `< 20` minimum stays an error.

Migration: the 311 in-repo product agents are remediated to green in the **same
branch/PR** as this change — flipping the gate strict turns CI red until they carry
the 8 fields, so the gate and the fleet land together.

## [3.9.0] — 2026-06-12 — Kernel-loaded shadow comparison (advisory, additive)

Consumer-cutover cleanup for the Spec Authority Kernel (DR-049 shadow soak;
the advisory→authoritative flip is explicitly OUT of this change). **No change
to `ALWAYS_REQUIRED`, the tier model, or error-vs-warning semantics** — the
hand-authored 8-field set stays authoritative and is now annotated as the
D4-preserved audit trail.

- New `load_kernel_required()` helper: existence-guarded read of
  `node_modules/@intentsolutions/core/schemas/authoring/v1/skill-frontmatter`
  (upstream-base + is-overlay layers); derives the kernel effective required
  set (base ∪ overlay) and combined property surface. Kernel absent → degrades
  gracefully, never raises.
- New `--kernel-shadow` flag: prints the comparison at startup (stderr).
  Identical sets → NOTE; delta → WARNING listing the difference. Advisory
  only — never affects verdicts or exit codes.
- `--json` output now always carries a trailing `{"kernel_shadow": {...}}`
  advisory element (both batch and single-file modes) with the required-set
  comparison plus the `disallowed-tools` presence comparison. In-repo
  consumers (`run-verification-pipeline.mjs`, `pr-prescreen/coordinator.py`,
  `kernel-shadow-validation.mjs`) skip entries carrying the `kernel_shadow`
  key.
- `ALWAYS_REQUIRED` and the `disallowed-tools` registry entry are commented
  as D4 hand-authored entries preserved as audit trail; the kernel shadow
  compares at runtime.

## [3.8.0] — 2026-06-11 — Real `allowed-tools` entry validation + standard-tier missing-`name` diagnostic (additive)

Code-review fixes (findings f-ccp-validator-1..4). **No change to `ALWAYS_REQUIRED`,
the tier model, or error-vs-warning semantics** — all new diagnostics are
WARNING-level (NON-NEGOTIABLE #7 reserves error/warning semantic changes for
explicitly approved architectural work).

### Fixed — `validate_tool_permission` actually validates (f-ccp-validator-1)

The function previously returned `True` for every entry and its diagnostic
messages were silently dropped by the caller, so misspelled tool names
(`Reads`), truncated wildcards (`Bash(git add *` without the closing paren),
and stray fragments (`wc:*)`) all passed without a word. Now:

- **Malformed entries** (unbalanced parentheses, scope not closing at end of
  entry, empty scope `Bash()`, illegal characters in the tool name, empty
  entry) → WARNING at every tier.
- **Well-formed but unknown base tool names** (e.g. `Reads`) → WARNING with a
  did-you-mean suggestion when a close match exists.
- **MCP tool references** (`mcp__server__tool`) are recognized as valid.
- The old `cmd:*`-format advisory is dropped: Anthropic's canonical example is
  the space form `Bash(git add *)` (code.claude.com/docs/en/skills), so a
  no-colon scope is spec-compliant, not suspect.

Severity note: these are WARNINGS (not marketplace ERRORS) because the
NON-NEGOTIABLES do not define tool-entry severity and #7 makes any
error-vs-warning escalation an approval-gated architectural change. If a
malformed-entry ERROR at marketplace tier is wanted, that needs explicit
sign-off first.

### Fixed — standard tier emits a missing-`name` diagnostic (f-ccp-validator-2)

`STANDARD_REQUIRED = {name, description}`, but a SKILL.md with no `name` field
produced zero frontmatter-presence diagnostics at standard tier. Now emits a
WARNING (`Missing required field: 'name'`), parallel to the existing
missing-`description` warning at that tier.

### Fixed — stale "marketplace = warnings-only" docs (f-ccp-validator-3)

The module docstring and the comment blocks around `MARKETPLACE_TRACKING_FIELDS`
still described marketplace tier as "WARNINGS for missing polish fields … No
additional ERRORS beyond Standard" — pre-3.3.0 wording that contradicts
NON-NEGOTIABLES #1–#2 and the actual code (missing `ALWAYS_REQUIRED` fields
error at marketplace tier since 3.3.0). Docstrings now state the 8-field
ERROR behavior. The stale `Schema: 3.0.0` header line is also corrected.

### Fixed — dead expression in `validate_frontmatter` (f-ccp-validator-4)

Removed a discarded `fm.get("metadata", …)` expression statement (dropped
assignment left over from a refactor; value was never used).

### Migration

None required. Existing skills keep validating; some now surface WARNINGS for
malformed/unknown `allowed-tools` entries or a missing `name`. Warnings do not
fail validation (unless `--fail-on-warn`) and do not affect rubric grades.

---

## [3.7.0] — 2026-05-28 — Recognize `disallowed-tools` (Claude Code v2.1.152, additive)

Adds the `disallowed-tools` field to the schema registry. Source: Claude Code v2.1.152 changelog (released 2026-05-27) — _"Skills and slash commands can now set `disallowed-tools` in frontmatter to remove tools from the model while the skill is active."_ **No validator rule changes** — `ALWAYS_REQUIRED` 8-field set is untouched; `disallowed-tools` is recognized as an Anthropic-spec optional field with the same string|array shape as `allowed-tools`.

### Added — `disallowed-tools` (top-level, string or array)

```yaml
# String form (space-separated, matches allowed-tools convention):
disallowed-tools: Bash WebFetch

# Array form (YAML list):
disallowed-tools:
  - Bash
  - WebFetch
```

Shape: identical to `allowed-tools` (`string|array` with the same parser). Source classified as `anthropic`; tier `standard`. Validates type only; semantics (which tools to disallow) are skill-author concern.

### Tier placement (per SAK plan 031 § 14.10 binding)

`disallowed-tools` is recognized but NOT added to `MARKETPLACE_TRACKING_FIELDS`. Rationale: it is optional security polish (lets a skill self-disable risky tools), not a marketplace-required tracking field. Skills are free to omit it; including it is encouraged for security-sensitive skills. The `ALWAYS_REQUIRED` 8-field IS marketplace set (`name, description, allowed-tools, version, author, license, compatibility, tags`) is untouched.

Per SAK plan 031 § 14.10 (NON-NEGOTIABLES item 3: _"The IS rubric SITS ON TOP of Anthropic's spec"_): this addition lands at the IS marketplace tier in the canonical validator. Future kernel `intent-eval-core/schemas/authoring/v1/skill-frontmatter.schema.json` will mirror this placement under `$defs.openStandardCompliant` (since 2.1.152 is a Claude Code extension, not agentskills.io spec) AND `$defs.isMarketplace` (so IS-tier consumers recognize it).

### Snapshot anchor

The Claude Code 2.1.152 changelog entry was captured 2026-05-27 in:

- `intent-eval-platform/intent-eval-lab/research/claude-docs-spec-tree-2026-05-27.md` (full 22-URL spec snapshot)
- `000-docs/anthropic-skills-spec-snapshot.md` (local-canonical refresh due as part of this PR)

### Migration

None required. Existing skills that do not use `disallowed-tools` continue to validate. Skills that already shipped `disallowed-tools` (prior to validator recognition) will stop producing unknown-field warnings.

### Out of scope (intentional non-goals)

- Cross-field check that `disallowed-tools` ∩ `allowed-tools` is empty. (Possible follow-up; not in this patch — keeps wedge minimal per § 14.8 directive 1.)
- Promotion to `MARKETPLACE_TRACKING_FIELDS`. (Optional security polish, not required tracking metadata.)
- Validator-side enforcement of which tools are "safe" to disallow vs. require allowed-tools symmetry.

### Plan / bead refs

- Plan: `intent-eval-platform/intent-eval-lab/000-docs/031-PP-PLAN-skill-refiner-sak-amendment-v6-2026-05-28.md` § 14.8 directive 1
- Bead: `bd_000-projects-umij` (ccp-d4-followup)
- Parent SAK epic: `bd_000-projects-3kye`

---

## [3.6.0] — 2026-05-14 — Self-declared config surface (additive, no architectural changes)

Adds two optional frontmatter blocks so skills self-describe the secrets and config keys they consume. The installer / runtime helper can then prompt the user on first run instead of letting them hit a runtime error mid-task. **No validator rule changes** — `ALWAYS_REQUIRED` 8-field set is untouched.

### Added — `required_environment_variables` (top-level, list of objects)

```yaml
required_environment_variables:
  - name: GITHUB_TOKEN
    prompt: 'Personal access token (repo + write:packages scopes)'
    help: 'Create at https://github.com/settings/tokens'
    required_for: 'PR comment + release operations'
```

Shape: each entry must be a mapping with at least `name` + `prompt`. Missing either is an ERROR. `help` and `required_for` are optional.

### Added — `metadata.intent-solutions.config` (nested under existing `metadata`, list of objects)

```yaml
metadata:
  intent-solutions:
    config:
      - key: default_branch
        description: 'Branch to target for new PRs'
        default: main
        prompt: 'What branch should PRs target?'
```

Shape: each entry must be a mapping with at least `key` + `description` + `default`. Missing any is an ERROR. `prompt` is optional (helper falls back to "Set `<key>`?").

### Added — cross-field consistency with `requires_env` (schema 3.5.0)

If a skill declares `requires_env: [X]` for visibility gating but doesn't have a matching `required_environment_variables` entry with `name: X`, the validator emits a WARNING. Reason: the user installing the skill needs to know _what_ X should contain, not just that it must be set. Non-blocking — declaration alone is still useful for visibility, not every skill needs installer copy.

### Storage convention

Resolved values from the installer land in `~/.claude/skill-config/<skill-name>.yaml` (mode 600, plain YAML). The marketplace does NOT enforce a specific loader — Python / bash / Node skills each read this file with whatever YAML library suits them. The contract is the file path and the YAML shape, not the language.

### Documentation

New: `000-docs/264-DR-GUID-skill-config-pattern.md` — full reference with examples, validation rules, migration notes, and explicit non-goals.

### Rationale

At 2783 skills, the first-run UX is wildly inconsistent — some prompt cleanly, most throw `KeyError` partway into a task when they discover an env var isn't set. Self-declaration lets the installer prompt uniformly across the catalog without forcing every skill author to ship custom onboarding code. The pattern is the open-standard convention (agentskills.io) for skill installers.

### Migration

None required. Existing skills that hardcode env reads continue to work. To opt in, add one or both blocks to the skill's frontmatter. For skills already using `requires_env` (3.5.0), adding the matching `required_environment_variables` entries silences the cross-field warning.

### Out of scope (intentional non-goals — see `264-DR-GUID-skill-config-pattern.md`)

- Grep-the-body heuristic for undeclared env-var reads (too noisy at scale, false-positive prone)
- Automatic secret-value format validation (skill-specific concern)
- Runtime config-file watcher

Cross-refs: bead `claude-la6s`, GH issue `claude-code-plugins-plus-skills#713`, Plane CCPI-23. Completes the self-improving-skills series: #714 (3.4.0 progressive disclosure) → #715 (3.5.0 conditional visibility) → this (3.6.0 self-declared config).

---

## [3.5.0] — 2026-05-14 — Conditional skill visibility (additive, no architectural changes)

Adds four optional frontmatter fields so skills can self-declare their environment / tooling dependencies. Consumers (the marketplace UI, the Claude Code skill loader) can then hide skills whose deps are absent, and surface fallback alternatives when a primary tool isn't available. **No validator rule changes** — the `ALWAYS_REQUIRED` 8-field set is untouched.

### Added — four optional list-of-strings fields

```yaml
# Hidden unless every listed env var is set.
requires_env: [GITHUB_TOKEN, OPENAI_API_KEY]

# Hidden unless every listed tool is available on PATH.
requires_tools: [docker, kubectl]

# Shown ONLY when these env vars are NOT set (the skill is the fallback).
fallback_for_env: [FIRECRAWL_API_KEY]

# Shown ONLY when these tools are NOT available (fallback pattern).
fallback_for_tools: [rg]
```

All four accept three input forms (the parser normalizes):

| Form         | Example                                                       |
| ------------ | ------------------------------------------------------------- |
| Block list   | `requires_env:`<br>`  - GITHUB_TOKEN`<br>`  - OPENAI_API_KEY` |
| Inline array | `requires_env: [GITHUB_TOKEN, OPENAI_API_KEY]`                |
| CSV string   | `requires_env: GITHUB_TOKEN, OPENAI_API_KEY`                  |

### Concrete examples from our catalog (illustrative — not auto-populated)

- `/gemini-pr-review` would set `requires_env: [GCP_PROJECT]` so it hides on accounts without GCP auth.
- `/whop-deployment-specialist` would set `requires_env: [WHOP_API_KEY]`.
- A generic web-search skill would set `fallback_for_env: [FIRECRAWL_API_KEY]` so it surfaces only on accounts without Firecrawl configured.

### Added — cross-field visibility-rule validation

`validate-skills-schema.py` now rejects skills where the same identifier appears in both `requires_{scope}` and `fallback_for_{scope}` (per scope: env vs tools). A skill cannot simultaneously _require_ X to be set AND be the _fallback_ for X being absent — that's a contradiction. Validated as an ERROR (not warning) since it produces undefined visibility behavior.

### Added — generalized YAML block-list parsing

`marketplace/scripts/discover-skills.mjs` previously only honored block-list `- item` syntax for the hardcoded `allowed-tools` key. Generalized so any key (including the new visibility fields and existing `tags`) can use block-list form.

### Added — visibility fields in L0 index

`skills-index.json` (L0, schema 3.4.0) now includes `requires_env`, `requires_tools`, `fallback_for_env`, `fallback_for_tools` per skill — empty arrays for skills that don't declare them. Client-side filtering can run against the index without fetching the heavy L1 catalog.

### Rationale

At 2783 skills, the catalog surfaces many skills the user can never run — they require API keys, cloud auth, or local tools that aren't present. The conditional-visibility pattern is the open-standard convention (per `agentskills.io`) for letting skills describe their own preconditions. Pure additive: skills that don't declare these fields keep the current always-visible behavior.

### Migration

None required. Existing skills continue to validate cleanly. To opt a skill in, add one or more of the four fields to its frontmatter.

Cross-refs: bead `claude-22cg`, GH issue `claude-code-plugins-plus-skills#712`, Plane CCPI-22. Part of the self-improving-skills series — schema 3.4.0 progressive disclosure preceded this (PR #714); 3.6.0 self-declared env vars (#713) follows.

---

## [3.4.0] — 2026-05-14 — Progressive disclosure: 3-tier skill catalog (additive, no architectural changes)

Adds a load-tier contract for the skills catalog. The validator and required-fields set are **unchanged** — this is a build-pipeline / consumer-protocol additive change, not a schema rule change.

### Added

- **L0 metadata index** at `marketplace/src/data/skills-index.json`. Schema:

  ```json
  {
    "schemaVersion": "3.4.0",
    "level": "metadata",
    "skills": [{ "slug", "name", "description", "version", "category", "parentPlugin" }],
    "count": <n>,
    "generatedAt": "<ISO>",
    "categories": [...]
  }
  ```

  Always emitted by `discover-skills.mjs`. ~150 bytes per skill — for the current 2770-skill catalog, the artifact is 817 KB raw / **97 KB gzipped**, vs the existing L1 catalog at 23 MB raw / 5.5 MB gzipped. 56× reduction for trigger-match / browse-list use cases.

- **`--level=metadata|full|file`** CLI flag on `marketplace/scripts/discover-skills.mjs`:
  - `--level=full` (default) — emits both L0 index and L1 catalog. Backward compat with current marketplace UI build.
  - `--level=metadata` — emits L0 only. Skips `mdToHtml(body)` per-skill; 3× build speedup (~0.5s vs ~1.6s on the current catalog).
  - `--level=file` — runtime-only concept (client-side single-reference-file read). Build step errors with guidance.

- **`schemaVersion` + `level` fields** in both L0 (`skills-index.json`) and L1 (`skills-catalog.json`) outputs so consumers can pin behavior.

### Rationale

At 2770 skills (and growing toward 4000+ per the route-count budget) the existing single-tier load forced every consumer of the catalog to pull 5.5 MB of gzipped body HTML even when they only needed name+description for trigger matching. The progressive-disclosure pattern is the open-standard convention (per `agentskills.io`) and is purely additive: existing consumers that read `skills-catalog.json` get the same artifact with two new top-level metadata fields; new consumers that only need browse/match data fetch the dramatically smaller `skills-index.json`.

### Migration

None required. Existing build invocations (`node marketplace/scripts/discover-skills.mjs` with no args) continue to produce `skills-catalog.json` exactly as before, plus the new `skills-index.json` alongside.

Cross-refs: bead `claude-nwdy`, GH issue `claude-code-plugins-plus-skills#711`, Plane CCPI-21. Followed by the conditional-visibility (#712) and self-declared-env (#713) issues in the same schema 3.4.0 series.

---

## [3.3.2] — 2026-05-12 — Agent field spec-compliance bug fixes (no architectural changes)

Discovered while triaging two external-contributor PRs (#679 from `CeciliaZ030` for `aomi-labs/skills`, #680 from `ali5ter` for four external plugins): the IS agent validator was flagging two fields that ARE documented Anthropic spec fields, leading to wrong review feedback on legitimate agent submissions.

### Fixed

- **`color` (agent frontmatter) is a documented Anthropic field, not deprecated.** Per [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents): _"Display color for the subagent in the task list and transcript. Accepts `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, or `cyan`."_ Old validator placed `color` in `DEPRECATED_AGENT_FIELDS` and emitted _"Non-standard field. Not in Anthropic spec. Will be removed in future validation."_ That message was wrong. Moved to `AGENT_FIELDS` with valid-color enum; agents using any of the eight allowed values now validate cleanly.
- **`initialPrompt` (agent frontmatter) is a documented Anthropic field, not unknown.** Per the same source: _"Auto-submitted as the first user turn when this agent runs as the main session agent (via `--agent` or the `agent` setting)."_ Old validator treated it as an unknown field and emitted _"Unknown field: 'initialPrompt'"_. Added to `AGENT_FIELDS` with `'string'` type. Agents using it now validate cleanly.
- **`permissionMode: 'auto'` added to valid values.** Anthropic's documented set now includes `auto` (was previously missing). Validator's `valid` enum now: `['default', 'acceptEdits', 'auto', 'dontAsk', 'bypassPermissions', 'plan']`.

### Authorization

Per `SCHEMA_CHANGELOG.md` NON-NEGOTIABLE #6: _"Bug fixes that bring the validator into spec compliance are always OK to apply autonomously. Examples: accepting YAML lists for `allowed-tools`, fixing conditional-field rules to match documented defaults, adding missing documented fields like `arguments` / `paths` / `shell`. These are technical-correctness fixes — not 'spec realignment.'"_ This release adds two more such fields to the registry and adds one more permissionMode value. No architectural changes; the IS 8-field enterprise required set remains unchanged.

### Backward compatibility

Non-breaking. Agents that previously passed at 3.3.1 still pass at 3.3.2 (same or fewer warnings). Agents that were previously WARN'd for `color`/`initialPrompt` now validate cleanly.

### Cross-source verification (newest-spec wins)

The fix was verified against five authoritative sources, all current as of 2026-05-12:

1. **[code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)** — Claude Code subagent frontmatter table lists both `color` and `initialPrompt` as documented optional fields.
2. **[platform.claude.com/docs/en/agents-and-tools/agent-skills/overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)** — Platform-side skill spec (skills, not agents) — required fields remain `name` + `description`; max 1024 chars on description; no XML tags; no "anthropic"/"claude" reserved words in name.
3. **[agentskills.io/specification](https://agentskills.io/specification)** — Open standard. Required: `name`, `description`. Optional: `license`, `compatibility`, `metadata`, `allowed-tools`.
4. **[anthropics/skills/template/SKILL.md](https://github.com/anthropics/skills/blob/main/template/SKILL.md)** — Anthropic's canonical template uses only `name` + `description`.
5. **[anthropics/skills/skills/{pdf,docx,mcp-builder,canvas-design,internal-comms,algorithmic-art}/SKILL.md](https://github.com/anthropics/skills/tree/main/skills)** — Anthropic's own six canonical skills use only `name`, `description`, `license`. They do not use `tags`/`version`/`author`/`compatibility` — those remain IS extensions intentionally additive on top of the Anthropic spec.

All checks the validator currently enforces (name max 64 chars, lowercase-numbers-hyphens only, no XML tags in name/description, no reserved words "anthropic"/"claude" in name via `FORBIDDEN_WORDS`, description max 1024 chars) are confirmed against the newest source documentation and remain correct.

### Validator landing

Released via PR #705 (`fix/p2-agent-validator-spec-current`) which merged to `main` as commit `5debf572f` on 2026-05-12. That PR also added two related blog posts (`agents-md-cross-tool-plugin-brief.md`, `coherence-day-drift-detection-strategic-spine.md`) but did not bump `SCHEMA_VERSION` or update this changelog. This entry retroactively closes that gap.

---

## [3.3.1] — 2026-04-28 — Spec-compliance bug fixes (no architectural changes)

After the 3.3.0 restoration, a careful re-read of [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) found three concrete bugs where the validator diverged from Anthropic's documented behavior. All three are pure spec-compliance fixes — no IS architectural changes.

### Fixed

- **`allowed-tools` YAML list form accepted.** Anthropic doc: _"Accepts a space-separated string or a YAML list."_ Validator was rejecting YAML lists with the message _"must be a comma-separated string (CSV), not a YAML array"_. Now accepts both forms; YAML list, space-separated string, comma-separated string, and mixed forms all parse correctly.
- **`allowed-tools` space-separated parsing.** Anthropic's canonical example uses space-separated form: `Bash(git add *) Bash(git commit *) Bash(git status *)`. Old parser only split on commas, which would treat the whole string as one tool. New parser is paren-depth-aware so multi-word tools like `Bash(git add *)` stay as one token in space-separated form.
- **`agent` field no longer warns "missing" when defaulting to general-purpose.** Anthropic doc: _"If omitted, uses general-purpose."_ Old `CONDITIONAL_FIELDS` rule warned that `agent` was missing whenever `context: fork` was set. Removed.
- **`argument-hint` conditional rule.** Was: `user-invocable=true AND disable-model-invocation=false`. Anthropic doc: `disable-model-invocation: true` only blocks Claude's auto-invocation; the user can still invoke via `/`. So argument-hint is still relevant when `disable-model-invocation: true`. Fixed to: `user-invocable=true` only.

### Added

- **`${CLAUDE_EFFORT}`** added to `YAML_VALUE_ALLOWED_VARS` allow-list. Documented Anthropic substitution variable for the current effort level.

### Backward compatibility

Non-breaking. All existing skills that passed at 3.3.0 still pass at 3.3.1 with same or fewer warnings. Skills that were previously rejected for using YAML-list `allowed-tools` form now pass.

---

## [3.3.0] — 2026-04-28 — Restored 8-field enterprise standard

The 3.0.0–3.2.0 experiments tried to relax the IS enterprise rubric toward an "Anthropic spec floor" of `{name, description}` only. That direction made the standard worse, not better — the marketplace needs full tracking + governance metadata on every shipped skill, not just the two minimal Anthropic-required fields. This release reverts that direction.

### What's restored

- **`ALWAYS_REQUIRED` is back to 8 fields**: `{name, description, allowed-tools, version, author, license, compatibility, tags}`. Missing any of these = ERROR at marketplace tier. Same as the original IS rubric, with the only change being `compatible-with` → `compatibility` (the kept fix from 3.0.0).
- **Marketplace tier presence-check logic** restored to strict-enforcement form. Removed the per-field "tracking-reason" warning text (the warnings became errors again, no commentary needed).
- **`version`/`author`/`tags` `source` label** back to `'enterprise'` from `'tracking'`. They're enterprise-required fields, not optional metadata.
- **Templates and docs** restored to enterprise framing — required = full 8-field set, optional = the documented Anthropic fields you customize on top.

### What's kept from the experiments (genuine improvements only)

- **`compatible-with` → `compatibility` migration** (from 3.0.0). This is the only architectural change retained. Free-text per AgentSkills.io spec, max 500 chars. `compatible-with` remains parsed as a deprecated alias with migration suggestion.
- **`when_to_use` correctly classified as documented Anthropic optional** (from 3.1.0). Earlier IS rubrics treated it as deprecated; that was wrong per `code.claude.com/docs/en/skills`.
- **`arguments`, `paths`, `shell` added to `SKILL_FIELDS`** (from 3.1.0) as documented Anthropic optional fields with type validation.
- **`effort: xhigh`** added to valid values (from 3.1.0) per Anthropic's documented `low/medium/high/xhigh/max`.
- **1,536-char combined cap** validation for `description` + `when_to_use` per Anthropic's documented limit.
- **`scripts/batch-remediate.py --migrate-compatible-with`** tool (from 3.0.0) for bulk migrations.
- **`Skill()` permission rule documentation** in skill-creator references (Skill(name) exact / Skill(name \*) prefix).

### What's reverted

- Required-fields reduction to {name, description} → reverted to 8-field enterprise standard
- "Standard tier vs marketplace tier" framing where marketplace was just warnings → reverted to strict-error marketplace tier
- `version/author/tags` reclassification as "tracking metadata" with source='tracking' → reverted to source='enterprise'
- `MARKETPLACE_TRACKING_FIELDS` rename → kept the rename internally but logic uses `ALWAYS_REQUIRED`
- "Supreme canonical template" with placeholders for every documented field → reverted to enterprise template (8 required fields filled, optional fields commented)
- `frontmatter-spec.md` section 3 reframe → restored to "Intent Solutions Enterprise Required Fields"
- `CLAUDE.md` frontmatter section reframe → restored to enterprise required-field listing

### Net result

The validator now enforces the original IS enterprise standard exactly, with these technical corrections layered in:

| Field                         | Status in 3.3.0                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------ |
| `name`                        | Required (unchanged)                                                                 |
| `description`                 | Required (unchanged)                                                                 |
| `allowed-tools`               | Required (unchanged)                                                                 |
| `version`                     | Required (unchanged)                                                                 |
| `author`                      | Required (unchanged)                                                                 |
| `license`                     | Required (unchanged)                                                                 |
| `tags`                        | Required (unchanged)                                                                 |
| `compatibility`               | Required (replaces `compatible-with`)                                                |
| `compatible-with`             | **Deprecated alias** — still parsed, warns + suggests migration                      |
| `when_to_use`                 | Documented Anthropic optional (was wrongly flagged deprecated in earlier IS rubrics) |
| `arguments`, `paths`, `shell` | Documented Anthropic optional (newly added to schema registry)                       |
| `effort` valid values         | `low / medium / high / xhigh / max` (added xhigh)                                    |

---

## [3.2.0] — 2026-04-28 — Maximum-capability default + supreme canonical template (REVERTED IN 3.3.0)

### Why this release

Two related framing problems in 3.1.0:

1. **Tier model was apologetic.** `version`, `author`, `tags` were classified as `source: 'intent-solutions'` and described as "marketplace polish" — as if tracking metadata were a quirky IS extension instead of how every package manager (npm, PyPI, Cargo, Homebrew) operates. Anthropic's own reference repo _chooses_ not to use them, but they're tolerated by the spec and they're how serious skill marketplaces function.
2. **Templates and docs led with the minimal form.** Following Anthropic's reference-repo style of `name + description + license`, the IS template encouraged minimalism. That contradicts what a marketplace operator actually needs — full tracking metadata for every shipped skill.

### Changed

- **Validator design principle now stated explicitly**: "maximum capability by default; users customize down." Every documented Anthropic field is first-class, every AgentSkills.io optional is first-class, every tracking field is first-class. Validator only enforces (a) required-field presence (b) type/value validity (c) security constraints.
- **`version`, `author`, `tags` reclassified** from `source: 'intent-solutions'` → `source: 'tracking'`. Description updated in `SKILL_FIELDS` schema registry to reflect that top-level tracking metadata is the dominant convention across language-ecosystem package managers and that Anthropic doesn't reject it.
- **`MARKETPLACE_RECOMMENDED` renamed to `MARKETPLACE_TRACKING_FIELDS`** (old name kept as alias). The new name reflects what the fields actually are: tracking + governance metadata, not aesthetic "polish."
- **Per-field warning messages** at marketplace tier now surface the _reason_ each field matters: `author` → maintainership/contact, `version` → downstream pinning, `license` → legal clarity, `allowed-tools` → security, `tags` → discovery, `compatibility` → runtime requirements. Engineers see the actual cost of omitting each field.
- **`templates/skill-template.md` rewritten as the supreme canonical form** — every documented field present and configured with placeholders. The minimal form (name + description only) is documented as a fallback, not the default.
- **`frontmatter-spec.md` section 5 ("Recommended Field Order") rebuilt as the supreme form** with explicit "customize down, never up" guidance.

### Added

- "Minimal form (only when you genuinely have nothing to add)" subsection clarifying that the Anthropic reference-repo style is _valid_ but not the IS standard.

### Backward compatibility

Non-breaking. Skills that pass at 3.1.0 still pass at 3.2.0 with identical errors/warnings. The reframe is purely educational — same fields, same validation rules, clearer naming and richer warning messages.

### What this enables

A user shipping a skill to the IS marketplace gets a frontmatter that:

- Tracks who maintains it (`author`)
- Tracks what version they're on (`version`)
- Documents what license applies (`license`)
- Pre-approves the right tools (`allowed-tools`, scoped)
- Surfaces in marketplace discovery (`tags`)
- States runtime requirements (`compatibility`)
- Documents triggers explicitly (`when_to_use` + `description`)
- Constrains auto-activation when needed (`disable-model-invocation`, `user-invocable`)
- Restricts file-context activation (`paths`)

That's the full first-class set. Customize down by deleting what doesn't apply.

---

## [3.1.0] — 2026-04-28 — Correction: deeper read of Claude Code skills doc

### Why this release

Schema 3.0.0 (earlier the same day) was published before fully reading the Claude Code skills frontmatter reference at [`code.claude.com/docs/en/skills#frontmatter-reference`](https://code.claude.com/docs/en/skills#frontmatter-reference). Several documented optional fields were missing or misclassified:

| Issue                 | Pre-3.1.0                  | Anthropic doc says                                                                                                                                                                                                          | Fix                                                                                  |
| --------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `when_to_use`         | Marked DEPRECATED          | Documented optional: _"Additional context for when Claude should invoke the skill, such as trigger phrases or example requests. Appended to `description` in the skill listing and counts toward the 1,536-character cap."_ | Restored to `SKILL_FIELDS` as documented optional. Removed from `DEPRECATED_FIELDS`. |
| `arguments`           | Missing                    | Documented: _"Named positional arguments for `$name` substitution in the skill content. Accepts a space-separated string or a YAML list."_                                                                                  | Added to `SKILL_FIELDS`. Validated as `string\|array`.                               |
| `paths`               | Missing                    | Documented: _"Glob patterns that limit when this skill is activated. Accepts a comma-separated string or a YAML list."_                                                                                                     | Added to `SKILL_FIELDS`. Validated as `string\|array`.                               |
| `shell`               | Missing                    | Documented: _"Shell to use for `` !`command` `` and ` ```! ` blocks. Accepts `bash` (default) or `powershell`."_                                                                                                            | Added to `SKILL_FIELDS` with valid values `[bash, powershell]`.                      |
| `effort` valid values | `[low, medium, high, max]` | `low`, `medium`, `high`, **`xhigh`**, `max`                                                                                                                                                                                 | Added `xhigh` to valid values.                                                       |

### Added

- **`when_to_use` reclassified as documented optional** per `code.claude.com/docs/en/skills#frontmatter-reference`. Validator no longer warns about it being deprecated. Validator now warns when combined `description` + `when_to_use` length exceeds Anthropic's documented 1,536-character cap on the skill listing entry.
- **`arguments` field** added to schema registry. Type: `string|array`. Accepts space-separated string (e.g. `arguments: issue branch`) or YAML list. Names map to `$name` substitution positions.
- **`paths` field** added to schema registry. Type: `string|array`. Glob patterns limiting auto-activation per file context.
- **`shell` field** added to schema registry. Valid values: `bash` (default), `powershell`. PowerShell on Windows requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`.
- **`effort: xhigh`** added to valid values for the `effort` field. Higher than `high`, distinct from `max`.
- **Cross-surface alignment note**: `code.claude.com/docs/en/skills` documents _"All fields are optional. Only `description` is recommended."_ — this is more permissive than `platform.claude.com` (API surface) which requires `name` and `description`. The IS validator follows the API + AgentSkills.io stance (name + description required) for marketplace consistency, with `name` accepting the directory-name fallback per Claude Code semantics.

### Changed

- `DEPRECATED_FIELDS` no longer contains `when_to_use`. Earlier IS rubrics treated `when_to_use` as deprecated; that was wrong.
- `SCHEMA_VERSION` constant: `'3.0.0'` → `'3.1.0'`.
- Documentation across `frontmatter-spec.md`, `validation-rules.md`, master spec, and `CLAUDE.md` updated to reflect the corrected field reference.

### Backward compatibility

This release is non-breaking. Files that previously triggered a `when_to_use` deprecation warning now validate cleanly. The four newly-documented optional fields (`arguments`, `paths`, `shell`, plus the corrected `when_to_use`) are accepted when present and silent otherwise.

---

## [3.0.0] — 2026-04-28 — Realigned to Anthropic published sources

### Why this release

Pre-v3 schema required eight fields at the (then-named) "enterprise" tier:
`name`, `description`, `allowed-tools`, `version`, `author`, `license`,
`compatible-with`, `tags`. Six of those eight are not actually required by any
published Anthropic source. As a Claude Enterprise partner positioning Intent
Solutions as a leader in the plugin/skill ecosystem, every public claim about
the SKILL.md spec must be defensible against Anthropic's published spec — which
this schema previously was not.

### Verified across seven authoritative sources (2026-04-28)

| Source                           | URL                                                                               | Required fields                                                                                        |
| -------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Anthropic platform overview      | `platform.claude.com/docs/en/agents-and-tools/agent-skills/overview`              | `name`, `description` only                                                                             |
| Anthropic best practices         | `platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`        | `name`, `description` only                                                                             |
| Claude Code skills doc           | `code.claude.com/docs/en/skills`                                                  | None required (`description` recommended)                                                              |
| Anthropic plugins reference      | `code.claude.com/docs/en/plugins-reference`                                       | No SKILL.md fields beyond skills doc                                                                   |
| Anthropic engineering blog       | `anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills` | `name`, `description` only                                                                             |
| AgentSkills.io open standard     | `agentskills.io/specification`                                                    | `name`, `description` only; `license`, `compatibility`, `metadata`, `allowed-tools` listed as optional |
| anthropics/skills reference impl | `github.com/anthropics/skills`                                                    | `name`, `description` only                                                                             |

### Changed

- **`ALWAYS_REQUIRED` reduced** from `{name, description, allowed-tools, version, author, license, compatible-with, tags}` → `{name, description}`. Sources: all seven above.
- **Tier renamed**: "Enterprise" → "Marketplace". The `--enterprise` CLI flag and `TIER_ENTERPRISE` constant remain as backward-compat aliases for one minor version. Renaming was needed because the previous label conflated this tier with Anthropic's actual Enterprise plan tier — they are unrelated. The new name reflects the tier's actual purpose: marketplace polish recommendations layered on top of Anthropic's spec.
- **Marketplace polish fields downgraded from ERROR → WARNING**: `allowed-tools`, `version`, `author`, `license`, `tags`, `compatibility` are all optional per Anthropic / AgentSkills.io spec. Validator now warns when any are missing at marketplace tier; no errors. Higher rubric scores still reward inclusion.

### Added

- **`compatibility` accepted as a documented optional field** per `agentskills.io/specification`. Free-text string, max 500 chars. Replaces the deprecated `compatible-with` CSV platform list. Pre-v3 schema rejected this field as INVALID — that was wrong. Examples per the AgentSkills.io spec:

  ```yaml
  compatibility: "Designed for Claude Code"
  compatibility: "Requires Python 3.10+ with uv installed"
  compatibility: "Requires git, docker, and jq on PATH"
  compatibility: "Designed for Claude Code, also compatible with Codex and OpenClaw"
  compatibility: "Node.js >= 18, npm >= 9"
  ```

- **`metadata` accepted as a documented optional field** per `agentskills.io/specification`. Arbitrary key-value mapping. Engineers may nest `version`, `author`, `tags`, etc. under `metadata.*` per the open standard, or keep them top-level (Intent Solutions extension).
- **`compatible-with` reclassified from REQUIRED → DEPRECATED**. Validator continues to parse this field for backward compatibility (3,385 existing public-repo SKILL.md files keep passing immediately) and emits a deprecation warning with a per-file migration suggestion that quotes the user's actual value. Migration tooling: `scripts/batch-remediate.py --migrate-compatible-with`.
- **`scripts/batch-remediate.py`** — new bulk-fix script. The `--migrate-compatible-with` flag implements the translation table:

  | Input                                           | Output                                                                             |
  | ----------------------------------------------- | ---------------------------------------------------------------------------------- |
  | `compatible-with: claude-code`                  | `compatibility: Designed for Claude Code`                                          |
  | `compatible-with: claude-code, codex, openclaw` | `compatibility: Designed for Claude Code, also compatible with Codex and OpenClaw` |
  | `compatible-with: ["claude-code"]`              | `compatibility: Designed for Claude Code`                                          |
  | (empty `compatible-with`)                       | field removed                                                                      |

  Idempotent: running twice on the same file is safe.

- **`SCHEMA_VERSION` constant** in `validate-skills-schema.py`, set to `'3.0.0'`. Validator banner now reads `validator v7.0 / schema 3.0.0`.

### Removed

- **`compatibility` and `metadata` from `INVALID_SKILL_FIELDS`**. Pre-v3 schema rejected both as not-Anthropic. Both are documented optional fields in `agentskills.io/specification`. Removing them as INVALID restores spec alignment. The pre-v3 rejection effectively forced engineers to choose between Intent Solutions' rubric and the open standard — that is no longer the case.
- **`VALID_PLATFORMS` allow-list semantics for `compatible-with`**. The pre-v3 validator restricted `compatible-with` values to a closed set: `{claude-code, codex, openclaw, aider, continue, cursor, windsurf}`. That allow-list was an Intent Solutions invention not present in any published spec. The deprecated alias still parses any value the engineer writes; the warning suggests a `compatibility:` migration target derived from the actual value.

### Migration impact

| Surface                                               | Impact                                                                                                                                                                                                                   |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **3,385 public-repo SKILL.md files** under `plugins/` | Zero errors (warnings about `compatible-with` deprecation are expected and OK). Bulk migration tracked in a separate follow-up issue. Not done in this release.                                                          |
| **45 personal skills under `~/.claude/skills/`**      | Migrated 2026-04-28 alongside this release. ~20 had `compatible-with`; rest unaffected.                                                                                                                                  |
| **CI configs that pass `--enterprise`**               | Continue to work. Validator emits a deprecation warning suggesting the rename to `--marketplace`. Removal targeted for the next minor version.                                                                           |
| **Skills authored after this release**                | Should use `compatibility` (free-text per AgentSkills.io). Removal of the deprecated `compatible-with` alias was originally targeted for schema v4.0.0; that target is superseded and deferred by the 4.0.0 entry above. |

### Backward compatibility guarantee

This release is **non-breaking** for existing SKILL.md files. Every file that
passed at the previous "enterprise" tier continues to pass at the new
"marketplace" tier. The strict-mode CI gate on `validate-plugins.yml` does not
need changes. Deprecation warnings are emitted but do not fail CI by default
(set `--fail-on-warn` if stricter behavior is desired).

### Master spec doc updates (`000-docs/6767-b-SPEC-DR-STND-claude-skills-standard.md`)

- Bumped doc version `2.0.0 → 3.0.0`
- Required Fields section: `name` + `description` only
- New "Marketplace Polish Recommendations" section
- Sources block: all seven verified URLs
- `compatible-with` references replaced with `compatibility` examples
- Inline `compatibility` usage examples added per AgentSkills.io spec

### Tier model

| Tier                              | Hard requirements                           | Warnings                                                                                         | Audience                                                  |
| --------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------- |
| **Standard** (default)            | `name`, `description`                       | none                                                                                             | All skills, all authors. Mirrors Anthropic spec verbatim. |
| **Marketplace** (`--marketplace`) | `name`, `description`                       | Missing polish fields (`allowed-tools`, `version`, `author`, `license`, `tags`, `compatibility`) | IS marketplace submissions. Adds 100-point rubric.        |
| **Deep** (`--deep`)               | (delegates to standard or marketplace tier) | (deep-eval engine specific)                                                                      | Quality analysis, Elo ranking, optional LLM judge.        |

### Authors

Jeremy Longshore <jeremy@intentsolutions.io>
