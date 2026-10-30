---
name: detecting-eval-exec-usage
description: |
  Scan a source tree for dynamic-code-execution APIs that an attacker
  can hijack: Python eval / exec / compile, JavaScript eval /
  Function() / setTimeout(string), Ruby eval / instance_eval /
  class_eval, Java ScriptEngine, PHP eval / assert($str), .NET
  Activator.CreateInstance / Reflection.Emit with dynamic input.
  Use when: pre-commit gate on any application that parses
  user-uploaded code (rule engines, formula evaluators,
  plugin systems), or post-bug-report when "we run user-supplied
  expressions."
  Threshold: any call to eval / exec / Function / similar where the
  argument is not a string literal.
  Trigger with: "scan eval", "find dynamic exec", "audit eval calls",
  "code injection patterns".
allowed-tools:
  - Read
  - Bash(python3:*)
  - Glob
  - Grep
disallowed-tools:
  - Bash(rm:*)
  - Bash(curl:*)
version: 3.33.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Designed for Claude Code
tags:
  - security
  - static-analysis
  - code-injection
  - pentest
---

# Detecting eval / exec Usage

## Overview

Dynamic-code-execution APIs (CWE-95 Eval Injection) let an
application interpret a string as code at runtime. If the string
contains anything user-controllable, the application has handed
the attacker arbitrary code execution.

The defensive posture: don't use these APIs. The exceptions are
narrow: rule engines, formula evaluators (spreadsheet `=` formulas),
plugin systems with explicit sandboxing. For everything else,
there's almost always a safer alternative.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Python `eval(...)` with non-literal | **CRITICAL** | argument contains var ref | CWE-95 |
| Python `exec(...)` with non-literal | **CRITICAL** | argument contains var ref | CWE-95 |
| Python `compile(...)` with non-literal | **HIGH** | source string contains var | CWE-95 |
| Python `__import__(var)` | **HIGH** | dynamic module loading | CWE-95 |
| JS `eval(...)` | **CRITICAL** | any | CWE-95 |
| JS `new Function(str)` | **CRITICAL** | any non-literal | CWE-95 |
| JS `setTimeout/setInterval(string)` | **HIGH** | string instead of function | CWE-95 |
| Ruby `eval(...)`/`instance_eval(...)`/`class_eval(...)` | **CRITICAL** | non-literal | CWE-95 |
| PHP `eval(...)` | **CRITICAL** | always | CWE-95 |
| PHP `assert($str)` | **CRITICAL** | (legacy code-eval form) | CWE-95 |
| PHP `create_function` | **CRITICAL** | deprecated, eval-equivalent | CWE-95 |
| Java `ScriptEngineManager` + eval | **HIGH** | dynamic script execution | CWE-95 |
| C# `Activator.CreateInstance(Type.GetType(str))` | **HIGH** | type loading from string | CWE-95 |

## Prerequisites

- Python 3.9+
- Source tree on local filesystem

## Instructions

### Run

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-eval-exec-usage/scripts/scan_eval.py /path/to/repo
```

Options: `--output FILE`, `--format json|jsonl|markdown`,
`--min-severity`, `--include-tests`, `--languages LIST`.

### Interpret

CRITICAL = direct RCE vector. Replace the dynamic execution with
explicit logic (lookup table, switch statement) or a sandboxed
expression library (Python `simpleeval`, JavaScript `expr-eval`,
Ruby `Dentaku`).

### Remediation

See `references/PLAYBOOK.md`.

## Examples

### Pre-commit

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-eval-exec-usage/scripts/scan_eval.py \
    --min-severity high $(git diff --name-only main...HEAD | tr '\n' ' ')
```

### CI

```yaml
- run: |
    python3 plugins/security/penetration-tester/skills/detecting-eval-exec-usage/scripts/scan_eval.py \
        . --min-severity high
```

## Output

JSON / JSONL / Markdown. Exit codes: 0 / 1 / 2.

## Error Handling

False positive on `eval("'literal'")` — the value is a constant
string. Verify the regex match by reading the source line.

## Resources

- `references/THEORY.md` — Why dynamic-code execution is the
  highest-impact injection class, sandbox limits, the
  formula-evaluator design pattern
- `references/PLAYBOOK.md` — Per-language safe alternatives
  (Python simpleeval / ast.literal_eval, JS expression-eval
  libraries, Ruby Dentaku, Java scripting sandboxes)
