---
name: schliff
description: >
  Deterministic linter and scorer for instruction files — SKILL.md, AGENTS.md,
  CLAUDE.md. No model in the loop: the same bytes score the same everywhere.
  Use for linting, scoring, auditing or CI-gating an instruction file, and for
  checking whether the commands a file promises actually resolve in the repo.
  Trigger phrases: "lint my skill", "score my skill", "audit skill",
  "review my skill", "harden skill", "make this skill better",
  "optimize my skill", "improve [metric] from X to Y", "benchmark skill",
  "check my AGENTS.md", "is my AGENTS.md lying", or paste a SKILL.md for
  auto-analysis. Also use when a user shares an instruction file without
  explicit instructions. Do NOT use for authoring a file from scratch — use a
  skill-creator first, then schliff. Do NOT use for application-code linting,
  SQL tuning, or runtime behaviour testing.
license: MIT
compatibility: Requires uv, which provides uvx.
allowed-tools: Bash(uvx schliff *), Bash(uvx schliff@8.12.0 *)
---

# schliff — deterministic instruction-file linter

## Overview

Scores one instruction file per dimension and turns that score into a CI gate.

## Prerequisites

`uv` on PATH (it provides `uvx`). No API key. Expects an instruction-file path
for most commands; see each command's `--help`.

## Commands

These run anywhere `uv` is available: no plugin, no checkout. All except `badge`
and `demo` accept `--json` for machine-readable output.

- `uvx schliff score <file>` — score one instruction file, per-dimension breakdown
- `uvx schliff doctor --skill-dirs <dir>` — grade every skill in a directory
- `uvx schliff verify <file> --min-score 75` — CI gate; exits 1 below the threshold
- `uvx schliff check-commands <file> --repo <dir>` — do the file's commands resolve?
- `uvx schliff suggest <file>` — ranked fixes with estimated score impact
- `uvx schliff badge <file>` — markdown score badge
- `uvx schliff compare <a> <b>` — two files side by side
- `uvx schliff demo` — score a built-in bad skill to see the output shape

Pin the version in CI: `uvx schliff@8.12.0 verify <file> --min-score 75`.

## Examples

Example 1 — score a skill:

```
$ uvx schliff score SKILL.md
  structure      95/100    triggers   95/100    quality  90/100
  Structural Score  87.4/100  [A]        Tokens: 1,044 / 2,000 (ok)
```

Grades run S · A · B · C · D · E · F. `4/7 dims` in the readout means no eval
suite was found beside the file, so only the deterministic dimensions could be
measured and the score is capped — a coverage statement, not a quality verdict.
`verify` scales its threshold by that same coverage, so a missing eval suite
never fails CI on its own.

Example 2 — is the file telling the truth?

```
$ uvx schliff check-commands AGENTS.md --repo .
  resolved   'make test'      make target 'test' defined in Makefile
  dangling   'npm run lint'   package.json has no script 'lint'
```

`dangling` is claimed only when absence is provable; anything unresolvable is
reported `unknown`, never as a defect.

## Workflow

1. `uvx schliff doctor --skill-dirs <dir>` — find the worst file.
2. `uvx schliff suggest <file>` — see the ranked fixes and their impact.
3. Apply them, then `uvx schliff score <file>` to confirm the delta.
4. Gate it: `uvx schliff verify <file> --min-score 75` in CI.

## If the schliff plugin is installed

Only with the full plugin from schliff's own marketplace (`/plugin marketplace add
Zandereins/schliff`, then `/plugin install schliff@schliff`). A skill-only mirror
and the `uvx` path above do not ship these commands, which also need `python3` >= 3.10:
`/schliff:analyze` · `/schliff:doctor` · `/schliff:init` · `/schliff:bench` ·
`/schliff:eval` · `/schliff:report` · `/schliff:mesh` · `/schliff:triage` ·
`/schliff:auto`

## Output

Produces per-dimension scores, a composite grade, and a gate-usable exit code.

## Error Handling

A gate result exits 1 with the finding on stdout: `verify` below the threshold or
with `--regression`, and `check-commands` finding a dangling command. Other
failures exit 1 or 2, depending on the command, and print the cause on stdout or
stderr.

## Scope

Use when measuring or gating the quality or honesty of an instruction file.
Do not use for authoring from scratch, application-code linting, or runtime
behaviour testing. schliff measures — it does not write.

## Handoffs

- No file to score yet → instead use a skill-creator skill to author one, then
  come back to schliff to measure it.
- Score plateaus after the suggested fixes → then use a skill-authoring or
  writing skill; the remaining gap is content, not structure.
- `check-commands` reports `dangling` → fix the file or the repo, re-run it.
- Any non-zero exit → report stdout and stderr verbatim; one of them names the
  cause.

## Resources

- [Scoring methodology](https://github.com/Zandereins/schliff/blob/main/docs/SCORING.md)
- [Source and issues](https://github.com/Zandereins/schliff)
- [PyPI package](https://pypi.org/project/schliff/)
