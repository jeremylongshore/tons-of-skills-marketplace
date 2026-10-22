---
name: yaml-master
description: 'Execute proactive YAML intelligence: automatically activates when working
  with YAML files.

  Use when appropriate context detected. Trigger with relevant phrases based on skill
  purpose.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(general:*), Bash(util:*)
version: 2.22.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- productivity
- yaml-master
compatibility: Designed for Claude Code
---
# YAML Master

Proactive YAML intelligence: validate syntax, enforce consistent formatting, and keep configuration files schema-correct (Kubernetes, GitHub Actions, Docker Compose, and similar).

## Overview

This skill activates when working with `.yml`/`.yaml` files to detect structural issues early (indentation, anchors, type mismatches), and to produce safe, minimal edits that keep CI/config tooling happy.

## Prerequisites

- The YAML file(s) to inspect and their intended target (e.g., Kubernetes, GitHub Actions, Compose)
- Any relevant schema or constraints (when available)
- Permission to edit the file(s) (or to propose a patch)

## Instructions

1. Parse and validate YAML syntax (identify the first breaking error and its location).
2. Normalize formatting (indentation, quoting) without changing semantics.
3. Validate structure against the target system’s expectations (keys, types, required fields).
4. Identify risky patterns (duplicate keys, ambiguous scalars, anchors used incorrectly).
5. Output a minimal patch plus a short validation checklist (what to run next).

## Output

- Corrected YAML with minimal diffs
- A concise list of issues found (syntax vs schema vs best practice)
- Follow-up validation commands appropriate for the target (e.g., `kubectl apply --dry-run=client`, CI lint)

## Error Handling

- If the schema/target is unknown, ask for the target system and apply syntax-only fixes first.
- If the YAML is valid but tooling still fails, surface the exact downstream error and reconcile expectations.

## Examples

**Example: Fix an indentation/syntax error**

- Input: a workflow with a mis-indented `steps:` block.
- Output: corrected indentation and a note on which job/step was affected.

**Example: Convert JSON to YAML safely**

- Input: a JSON config blob.
- Output: YAML with explicit quoting where necessary to avoid type surprises.

## Resources

- Full detailed guide (kept for reference): [`references/SKILL.full.md`](references/SKILL.full.md)
- YAML spec: https://yaml.org/spec/
- GitHub Actions workflow syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
