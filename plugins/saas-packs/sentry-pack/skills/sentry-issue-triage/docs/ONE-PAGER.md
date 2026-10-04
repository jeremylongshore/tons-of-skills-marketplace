# Sentry Issue Triage

**Turns one Sentry issue page into a severity, a suspect release, a grouping or noise lever, and a log query — from the payload, without clicking Ignore or inventing a timeline.**

## Problem

The issue stream lies in a few repeatable ways: unstable minified frames, messages used as identity, fingerprint rules that do not restack history, noise filters that were never turned on, Ignore that still bills, and performance issues that do not obey error fingerprint rules. The postmortem then invents times the payload never had.

## Solution

A router skill. `issue-context.py` and `fingerprint-from-event.py` read pasted or read-only event JSON. Subagents Read checklists: postmortem, fingerprint rules, inbound-filter matrix, span fingerprint, log correlation. Cardinality stays owned by quota. Symbolication stays owned by forensics. Nothing is written to Sentry.

## W5

| | |
|---|---|
| **Who** | On-call and the person writing the postmortem from a real issue |
| **What** | Severity, suspect release, prospective grouping/noise recommendation, log query or an explicit miss |
| **When** | A page, a split/merge question, a noisy project, an N+1 issue |
| **Where** | Claude Code, Sentry SaaS or a pasted issue JSON |
| **Why** | Scripts own counts and timestamps; agents cannot restack history or click Discard by accident |

## Stack

| Layer | Choice |
|---|---|
| Skill runtime | Claude Code `SKILL.md` (parent only) |
| Nested procedures | `CHECKLIST.md` under agents, `skills: []` |
| Data plane | `scripts/lib/sentry_readonly.py` or pasted JSON |
| Arithmetic | `issue-context.py`, `fingerprint-from-event.py`, `find-event-id-log.py` |
| Knowledge | `references/` severity rubric, matrix owner, symbolication handoff |

## Differentiators

1. **Postmortem is not the filter matrix.** `noise-classifier` owns Ignore vs Discard.
2. **Prospective only.** Fingerprint rules and source maps do not rewrite stored events. The first line says so.
3. **N+1 is not cardinality.** `perf-span-auditor` loads span thresholds; `trace-bottleneck` only points at quota's checklist.
