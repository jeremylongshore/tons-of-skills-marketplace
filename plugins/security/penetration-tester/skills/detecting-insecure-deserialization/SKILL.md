---
name: detecting-insecure-deserialization
description: |
  Scan a source tree for unsafe-by-default deserialization APIs:
  Python pickle.loads / cPickle / shelve / dill, Ruby Marshal.load /
  YAML.load (pre-3.1 default), Java ObjectInputStream.readObject,
  PHP unserialize, .NET BinaryFormatter / NetDataContractSerializer,
  Node.js node-serialize, JavaScript JSON.parse with reviver
  containing eval.
  Use when: pre-commit gate on services that accept binary blobs,
  audit of legacy job-queue code (workers deserializing tasks),
  post-bug-report when "we accept user-uploaded archives."
  Threshold: any call to a known-unsafe deserialization API on
  data that originates from user input, network, file upload,
  or untrusted storage.
  Trigger with: "scan deserialization", "pickle audit", "java
  readObject scan", "yaml.load check".
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
  - deserialization
  - pentest
---

# Detecting Insecure Deserialization

## Overview

Insecure deserialization (CWE-502, OWASP A08:2021) is the highest-
severity injection class in many language stacks because it directly
maps to RCE. Pickle, Java serialization, PHP unserialize, and
BinaryFormatter all execute object-construction code during
deserialization. If that code includes `__reduce__` /
`readObject` / `__wakeup` / `OnDeserialization` callbacks that
the attacker controls, the deserialization step IS code execution.

Most legitimate use cases have safer alternatives (JSON for data,
YAML with safe-load, Protocol Buffers, Avro). The remaining cases
need explicit type allow-lists and HMAC-signed payloads.

## When the skill produces findings

| Finding | Severity | Threshold | Affected control |
|---|---|---|---|
| Python `pickle.loads(...)` | **CRITICAL** | always (untrusted input) | CWE-502 |
| Python `pickle.load(file)` | **CRITICAL** | always | CWE-502 |
| Python `dill.loads` | **CRITICAL** | always | CWE-502 |
| Python `yaml.load(...)` without Loader= | **CRITICAL** | unsafe legacy default | CWE-502 |
| Python `yaml.unsafe_load(...)` | **CRITICAL** | explicit unsafe | CWE-502 |
| Python `shelve.open(...)` | **HIGH** | pickle-backed; user-controllable filename | CWE-502 |
| Java `ObjectInputStream.readObject()` | **CRITICAL** | always | CWE-502 |
| PHP `unserialize($input)` | **CRITICAL** | non-literal input | CWE-502 |
| .NET `BinaryFormatter.Deserialize(...)` | **CRITICAL** | deprecated unsafe API | CWE-502 |
| .NET `NetDataContractSerializer` | **CRITICAL** | also unsafe | CWE-502 |
| .NET `LosFormatter.Deserialize` | **CRITICAL** | ViewState path | CWE-502 |
| Ruby `Marshal.load(...)` | **CRITICAL** | non-literal | CWE-502 |
| Ruby `YAML.load(...)` (pre-3.1 Psych) | **CRITICAL** | safe in Psych 4.0+; needs version check | CWE-502 |
| Node.js `node-serialize.unserialize` | **CRITICAL** | known-vulnerable lib | CWE-502 |
| Node.js `serialize-javascript` reviver | **HIGH** | if used to deserialize untrusted | CWE-502 |

## Prerequisites

- Python 3.9+
- Source tree on local filesystem

## Instructions

### Run

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-insecure-deserialization/scripts/scan_deserialization.py /path/to/repo
```

Options same as previous skills: `--output`, `--format`,
`--min-severity`, `--include-tests`, `--languages`.

### Interpret

CRITICAL across the board because these APIs grant RCE during
deserialization if the input is attacker-controlled. The
verification step is "can the input ever originate from
untrusted source" — if yes, it's an immediate fix.

### Remediation

The fix depends on the data shape:

- **Data is structured (JSON-shaped):** switch to `json.loads`.
- **Data needs polymorphism / arbitrary types:** define a strict
  schema (Pydantic / dataclasses / Protocol Buffers) and validate
  on parse.
- **Data must round-trip exact Python / Java / .NET objects:** use
  HMAC-signed serialization with an explicit type allow-list.

See `references/PLAYBOOK.md` for per-language migrations.

## Examples

### Worker-queue audit

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/detecting-insecure-deserialization/scripts/scan_deserialization.py \
    /path/to/celery-workers --min-severity high
```

Celery defaults to pickle in older configurations; this finds the
remaining unsafe-default callers.

### CI

```yaml
- name: Deserialization scan
  run: |
    python3 plugins/security/penetration-tester/skills/detecting-insecure-deserialization/scripts/scan_deserialization.py \
        . --min-severity high
```

## Output

JSON / JSONL / Markdown. Exit codes: 0 / 1 / 2.

## Error Handling

Pickle / Marshal usage on a private cache file written by the same
application is technically safe (the attacker can't influence the
file contents). The scanner flags it as CRITICAL; verify by reading
where the input file originates.

## Resources

- `references/THEORY.md` — Why deserialization is RCE, gadget chains,
  HMAC-signing pattern, schema-validation alternatives
- `references/PLAYBOOK.md` — Per-language migrations (Python pickle
  → JSON / msgpack, yaml.load → yaml.safe_load, Java ObjectInputStream
  → JSON via Jackson with allow-list, PHP unserialize → JSON
  alternatives, .NET BinaryFormatter → System.Text.Json)
