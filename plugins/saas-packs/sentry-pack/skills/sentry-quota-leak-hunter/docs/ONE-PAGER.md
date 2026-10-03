# ONE-PAGER: sentry-quota-leak-hunter

**Version:** 2.0.0-draft
**Date:** 2026-10-03

## Who

Whoever is asking why Sentry volume moved: finance, on-call, platform.

## What

A ranked reading of org stats by category and one lever that is not "buy more": sampler, named `beforeSend`, inbound filter, or per-key minute ceiling. Org / project / key / environment / team / alert rule, when that is the question.

## When

A bill, a 429, a spike-protection mail, `tracesSampleRate: 1`, or "rate limit staging." Not during an unrelated SDK upgrade.

## Where

Sentry SaaS usage API or a pasted stats JSON. Not self-hosted.

## Why

The expensive mistakes are mismatched boundaries: sampling treated as a ceiling, environment treated as a quota silo, filtered added to dropped, Ignore treated as free.

## Stack

- Router: `SKILL.md`
- Script: `scripts/parse-usage-stats.py` → `pack/scripts/lib/sentry_readonly.py`
- Agents: `usage-auditor`, `volume-cutter`, `cardinality-hunter`, `key-boundary-mapper`
- Checklists under those agents (`CHECKLIST.md`, not nested `SKILL.md`)
- Labeled copies: inbound-filter matrix, replay-privacy, config-drift

## Do not

Sum outcomes. Invent dollars. Set `sampleRate: 0`. Put a rate limit on `environment`. Spawn a category agent. Write to the Sentry API.
