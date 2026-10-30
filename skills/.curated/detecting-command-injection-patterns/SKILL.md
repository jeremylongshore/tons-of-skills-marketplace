---
name: detecting-command-injection-patterns
description: |
  Scan a source tree for command-injection vulnerable patterns:
  shell=True calls in Python subprocess, os.system / os.popen with
  interpolated strings, Node child_process.exec with template
  literals, Ruby backticks / Kernel#system / Kernel#exec with
  interpolation, Go exec.Command with shell wrapping, PHP system /
  passthru / shell_exec / backticks with $-interpolation, Java
  Runtime.exec with concatenated args.
  Use when: pre-commit gate on code that calls out to shell utilities,
  audit of file-processing / archive-handling / image-conversion
  code, post-bug-report investigation for "we shell out to a tool."
  Threshold: any shell-invocation API called with a string that
  contains a variable interpolation, OR shell=True with anything
  other than a fixed literal.
  Trigger with: "scan command injection", "shell=True audit",
  "find exec calls", "check os.system".
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
  - command-injection
  - pentest
---

# Detecting Command Injection Patterns

## Overview

Command injection (CWE-78, OWASP A03:2021) shows up wherever an
application shells out to a binary. Image conversion (`convert`),
archive extraction (`tar`, `unzip`), video processing (`ffmpeg`),
DNS lookup (`dig`), and "we just need to call this CLI tool once"
are the common origins.

The vulnerability shape is universal: a string is built including
user input, then handed to a shell interpreter. The shell parses
the string with normal shell semantics — including `;`, `|`, `&`,
`$()`, backticks. Any of those in the user-controlled portion
becomes shell-executable.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Python `subprocess.run(..., shell=True)` with interpolation | **CRITICAL** | f-string / concat / format argument with `shell=True` | CWE-78 |
| Python `os.system(...)` with interpolation | **CRITICAL** | non-literal argument | CWE-78 |
| Python `os.popen(...)` with interpolation | **CRITICAL** | non-literal argument | CWE-78 |
| Node `child_process.exec(...)` with template literal | **CRITICAL** | `${...}` in the command string | CWE-78 |
| Node `child_process.execSync(...)` with template | **CRITICAL** | same | CWE-78 |
| Ruby backticks with interpolation | **CRITICAL** | `` `cmd #{var}` `` | CWE-78 |
| Ruby `Kernel#system(string)` with interpolation | **CRITICAL** | `system("cmd #{var}")` | CWE-78 |
| Go `exec.Command("sh", "-c", ...)` with interpolation | **HIGH** | shell wrapper with var | CWE-78 |
| PHP `system / exec / passthru / shell_exec` with $-interp | **CRITICAL** | `system("cmd $var")` | CWE-78 |
| Java `Runtime.exec(String)` with concat | **HIGH** | single-string form (vs array) with var | CWE-78 |

## Prerequisites

- Python 3.9+
- Target source tree on local filesystem

## Instructions

### Step 1 — Run the scanner

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-command-injection-patterns/scripts/scan_cmdi.py /path/to/repo
```

Options:

```
Usage: scan_cmdi.py PATH [OPTIONS]

Options:
  --output FILE      Write findings to FILE
  --format FMT       json | jsonl | markdown (default: markdown)
  --min-severity SEV (default: info)
  --include-tests    Include test directories (default: excluded)
  --languages LIST   Comma-separated subset to scan
```

### Step 2 — Interpret findings

CRITICAL = direct user-input → shell construction. Fix immediately.

HIGH = pattern where the shell layer exists but user-input reachability
needs verification.

### Step 3 — Remediation

The universal fix: pass arguments as a list (array), not a single
string. Most APIs have a list form that bypasses shell entirely.

See `references/PLAYBOOK.md` for per-language patterns.

## Examples

### Example 1 — Pre-commit on a media-processing service

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-command-injection-patterns/scripts/scan_cmdi.py \
    --min-severity high $(git diff --name-only main...HEAD | tr '\n' ' ')
```

### Example 2 — CI gate

```yaml
- name: Command-injection scan
  run: |
    python3 plugins/security/penetration-tester/skills/detecting-command-injection-patterns/scripts/scan_cmdi.py \
        . --min-severity high
```

## Output

JSON / JSONL / Markdown. Exit codes: 0 clean, 1 high/critical, 2 error.

## Error Handling

False positives common in build scripts that interpolate fixed
build constants. Verify each finding by reading whether the
interpolated value is user-reachable.

## Resources

- `references/THEORY.md` — Why shell=True is the default footgun,
  per-language shell-out idioms, argument-vector vs command-string
  semantics
- `references/PLAYBOOK.md` — Per-language safe-shellout patterns
  (Python subprocess list-args, Node spawn, Ruby Open3.capture3,
  Go exec.Command list-args, Java ProcessBuilder, PHP escapeshellarg)
