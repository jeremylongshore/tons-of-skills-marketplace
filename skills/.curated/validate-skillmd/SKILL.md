---
name: validate-skillmd
description: |
  Validate and grade SKILL.md files with the marketplace rubric, static production
  checks, and optional J-Rig behavioral evidence. Use when creating a skill,
  checking quality, preparing a marketplace submission, or reviewing evaluation
  results. Trigger with "validate this skill", "grade my skill", "deep eval",
  "check SKILL.md", or "/validate-skillmd".
allowed-tools: "Read,Edit,Write,Bash(python3:*),Bash(pnpm:*),Bash(scripts/run-jrig-eval.sh:*),Glob,Grep,AskUserQuestion"
version: 7.2.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code; requires Python 3, optionally the repository-pinned J-Rig CLI
tags: [validation, skill-quality, marketplace, grading, deep-eval, jrig, behavioral-eval]
user-invocable: true
argument-hint: "[path-to-SKILL.md] [--marketplace|--deep]"
---

# Validate SKILL.md

Read a skill, run the supported validator, and report what its evidence establishes.
The workflow has four tiers: locate the target, grade its content, inspect static
production checks, and optionally assess J-Rig behavioral results.

## Overview

- **Standard**: the validator's default structural checks.
- **Marketplace** (`--marketplace`): the eight required fields (`name`,
  `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`,
  `tags`) and the 100-point rubric. Missing required fields are errors.
- **Deep** (`--deep`): ten deterministic quality dimensions, badges and ranking.
  The validator invokes this engine with `use_llm=False`; it does not execute
  the skill or run J-Rig.
- **Behavioral evaluation**: a separate J-Rig workflow, only when the user
  explicitly requests it. Provider execution may incur API charges. Confirm the
  requested scope, approved provider/model set and available credentials before
  running it; an existing authorization is sufficient.

`--thorough` is not an implemented option in either command documented here.
Do not pass it to the Python validator: that parser currently ignores unknown
arguments, so a successful exit does not prove behavioral evaluation happened.

## Prerequisites

- Locate the marketplace checkout containing `scripts/validate-skills-schema.py`.
  Run the examples below from that repository root; resolve the target skill to
  an absolute path before changing directories.
- Python 3 with the repository's validator dependencies, including `pyyaml`.
- For J-Rig, install the checkout's dependencies with its supported pnpm version
  and use `pnpm exec j-rig`. The binary is `j-rig`, not `jrig`; do not create a
  global symlink or assume a globally installed version matches the checkout.
- Behavioral execution needs a reviewed `eval-spec.yaml` and the repository
  wrapper's approved authentication setup. Its default provider uses a
  SOPS-decrypted DeepSeek API key. Keep credentials in the approved environment
  or secret store; never print them, put them in reports, or commit them.

### Validator authority

Follow repository `CLAUDE.md` and `000-docs/SCHEMA_CHANGELOG.md` for the current
rubric and authority. The prose validator remains authoritative; kernel shadow
validation is advisory until its separate promotion gates are satisfied.
Repository-pinned kernel schemas are reference material, not permission to
override the required-field set or demote marketplace errors.
The field reference is [schema-reminder-frontmatter.md](references/schema-reminder-frontmatter.md).

## Instructions

### Step 1: Locate and read the target

Use Glob to locate `SKILL.md`, Read to inspect the complete file and its linked
resources, and Grep to check referenced commands and tool usage. Resolve ambiguous
targets with AskUserQuestion. Do not execute shell substitutions copied from a
skill simply to inspect it.

```bash
skill_file="/absolute/path/to/SKILL.md"
```

### Step 2: Run supported static validation

```bash
# Standard structural validation
python3 scripts/validate-skills-schema.py "$skill_file"

# Marketplace rubric and machine-readable findings
python3 scripts/validate-skills-schema.py --marketplace --json "$skill_file"

# Deterministic deep assessment of one skill
python3 scripts/validate-skills-schema.py --deep "$skill_file"
```

Use marketplace mode for marketplace submissions. `--enterprise` remains a
legacy alias. Inspect the single-file score and grade explicitly: `--min-grade`
enforcement belongs to the batch path. For structured results, use the
marketplace `--json` command above. Deep reporting adds diagnostics;
`--deep --report-format json` mixes JSON sections with terminal output.
Markdown/HTML rendering also belongs to the repository batch path.

### Step 2.5: Review the static production checks

The validator already runs five Tier 2 checks. Report their actual error/warning
severity and inspect suspicious findings against the skill body:

1. **Allowed-tools accuracy**: declarations versus tool references; unused tools
   are warnings, not proof of unsafe execution. Inspect substantive usage rather
   than counting the declaration itself as a reference.
2. **Authentication documentation**: warns when configured API indicators appear
   without a recognized authentication-documentation marker.
3. **Dead code**: warns on selected literal-false shell branches.
4. **Tool safety**: errors on unscoped Bash combined with Write/WebFetch without
   a recognized justification marker.
5. **Orchestration bounds**: errors on selected affirmative cross-skill
   orchestration phrases.

Manually review authentication adequacy, contradictory instructions, permission
scope and delegation beyond these heuristics. Static findings do not establish
runtime correctness or production readiness. Surface errors before warnings; fix blocking static
errors before proceeding to behavioral evaluation. Do not weaken the validator
or a repository gate to obtain a passing grade.

### Step 2.7: Optional J-Rig behavioral evidence

Skip this tier unless requested. If prerequisites are missing, report
**INCOMPLETE** with the missing prerequisite; never substitute a verified verdict.
The following commands can inspect tooling without provider calls:

```bash
pnpm exec j-rig --version
pnpm exec j-rig eval --help
pnpm exec j-rig check "$(dirname "$skill_file")" --json
pnpm exec j-rig scaffold-spec "$(dirname "$skill_file")" --stdout
```

`check` reports package integrity, not marketplace rubric compliance. Review a
scaffold before using it: generated cases are a starting point, not evidence of
adequate coverage. The optional `scaffold-spec --draft` path uses a provider and
is outside the deterministic inspection above.

#### Seven quality layers

Use the quality taxonomy in the J-Rig repository README, distinct from its
architectural implementation stages:

| Layer | Quality concern | Evidence to inspect |
|---|---|---|
| 1 | Package integrity | Package check results and errors |
| 2 | Trigger quality | Trigger measurements and their acceptance thresholds |
| 3 | Functional quality | Reviewed criteria and observed criterion verdicts |
| 4 | Regression protection | Prior judgments and the regression comparison |
| 5 | Baseline value | Enabled with-skill versus without-skill comparison |
| 6 | Model variance | Results from distinct actual backend models |
| 7 | Rollout safety | Safety criteria, blockers and promotion reasons |

Cost and latency are additional telemetry, not an eighth layer or a replacement
for package integrity. Ordinary `eval` skips regression and baseline. Supplying
three model names does not enable those comparisons or establish all-layer
coverage.

#### Evaluation through the repository wrapper

Always route authorized behavioral execution through the repository wrapper,
which retains evidence and records a `forge_proofs` row. Set `catalog_plugin` to
the target's catalog name and `behavioral_run_id` to its allocated behavioral
evaluation ID, never a discovery-run ID:

```bash
scripts/run-jrig-eval.sh \
  --skill-dir "$(dirname "$skill_file")" \
  --plugin "$catalog_plugin" \
  --jrig-run-id "$behavioral_run_id" \
  --inventory-db freshie/inventory.sqlite
```

This example uses the wrapper's approved DeepSeek provider/model defaults and
its SOPS authentication path. Inspect `scripts/run-jrig-eval.sh` before changing
providers. It gives J-Rig a scratch DB and retains the primary JSON separately;
only `scripts/record-jrig-proofs.mjs` writes the governed proof row. Never pass
`freshie/inventory.sqlite` to `j-rig eval --db`.

The CLI exposes `--regression-baseline`, `--baseline-check` and `--emit-bundle`,
but this wrapper does not forward them. The workflow above therefore leaves
regression and baseline comparisons incomplete and does not emit a bundle; do
not bypass the wrapper to claim coverage. For existing results, treat
`--no-trigger` or `--no-functional` as skipped evidence. Legacy proof fields
`layers_passed`/`total_layers` count criteria, and `baseline_delta` is not a
measured comparison. Stub results are synthetic; they cannot establish
behavioral success or production readiness.

### Step 3: Report observed coverage and outcomes

For each actual model, report package counts, criterion pass/fail/unsure counts,
rollout decision, promotion decision/reasons, regression/baseline enabled status
and results, and available usage/cost telemetry. Preserve errors and missing
fields instead of coercing them into passes.

The primary JSON is keyed by requested model. Inspect `pkgReport`, `scoreCard`,
`decision`, `report`, `promotion` and `cost`; special failure or skipped-functional
results can omit those fields. Criterion counts are not seven-layer pass counts.
A `ship` decision alone is insufficient when promotion remains advisory.

When reviewing a separately retained bundle, it is an array of statements. Coverage lives at
`[].predicate.coverage.dimensions_evaluated` and `dimensions_skipped`, separately
from primary JSON. These fields describe execution coverage, not layer verdicts.
The pinned CLI does not serialize trigger precision/recall in its primary JSON
or bundle; mark that evidence unavailable unless separately retained. Requested
model labels also need not identify distinct backend models: inspect provider,
judge and actual usage metadata before claiming model-variance coverage.

Do not automatically label a skill **JRig-Verified**, publish a badge, or infer
production readiness from a zero exit code, a model matrix, static grade, or
criterion counter. Apply the repository's promotion policy to retained evidence.

| Assessment | Report |
|---|---|
| Static errors or behavioral blockers | FAIL; list the blocking findings first |
| Requested evidence unavailable, skipped or synthetic | INCOMPLETE; name the gap |
| Static checks pass; behavioral evaluation not requested | Static PASS; behavioral SKIPPED |
| Requested checks have reviewed real evidence | Report observed outcomes and promotion status |

### Step 4: Apply authorized fixes and recheck

Prioritize errors, then substantive quality gaps, then presentation warnings.
Use Edit or Write for requested repairs, preserving the skill's purpose and
platform-specific metadata. Re-run the same validator command and compare its
actual before/after scores and findings; do not invent point gains. Keep large
reference tables in linked files and leave required sections readable.

## Output

- Target path, tool versions and exact commands run.
- Marketplace grade and reported rubric breakdown, when requested.
- Static errors and warnings, including the five Tier 2 checks.
- Behavioral scope, actual providers/models, retained artifact paths, observed
  outcomes, skipped dimensions and missing evidence, when requested.
- Prioritized repairs and before/after validation for changes made.
- A separate statement of promotion status; no automatic certification claim.

## Error Handling

| Error | Recovery |
|---|---|
| Target missing | Locate it with Glob; resolve ambiguity before grading |
| Python or validator unavailable | Report automated validation unavailable; label any manual review separately |
| YAML parse error | Report the parser location and repair the syntax |
| User requests `--thorough` | Explain the unsupported flag and use the separate authorized J-Rig workflow |
| J-Rig, eval spec or provider credentials unavailable | Mark requested behavioral evaluation INCOMPLETE |
| Provider or evaluator fails | Preserve the infrastructure error; do not count it as a skill pass |
| Required layer lacks evidence | Report the gap; do not claim all-layer verification |

## Examples

**Marketplace submission:**

```text
/validate-skillmd --marketplace path/to/SKILL.md
```

**Deterministic deep assessment:**

```text
/validate-skillmd --deep path/to/SKILL.md
```

**Explicit behavioral request:**

```text
Evaluate this skill with the approved provider and model set, retain the evidence,
and report skipped comparisons separately. Do not infer a verified badge.
```

## Resources

- [Frontmatter reference](references/schema-reminder-frontmatter.md)
- Marketplace checkout: `scripts/validate-skills-schema.py`, `scripts/deep_eval/`,
  `000-docs/SCHEMA_CHANGELOG.md` and `CLAUDE.md`.
- Repository-pinned J-Rig: `pnpm exec j-rig eval --help`; J-Rig README quality layers.
- Proof retention: `scripts/run-jrig-eval.sh` and `scripts/record-jrig-proofs.mjs`.
