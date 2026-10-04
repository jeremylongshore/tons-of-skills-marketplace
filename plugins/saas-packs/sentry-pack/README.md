# Sentry Skill Pack

**v2.0.0**: five operational skills for running Sentry in production. Version 1 was a 30-skill
tutorial curriculum organized around SDK features; version 2 is organized around the jobs
operators actually bring to Sentry.

All five skills are **advisory**: they work on configuration, stats and event JSON you paste in
(or `sentry-cli` output), and they recommend changes. They do not change your Sentry
organization. Live read-only API fetch is a planned follow-up.

## Installation

```bash
/plugin install sentry-pack@claude-code-plugins-plus
```

## The five skills

| Skill | Use it to |
|-------|-----------|
| `sentry-quota-leak-hunter` | Find which meter moved and which lever fixes it (sampling, filters, cardinality) before buying more quota |
| `sentry-event-forensics` | Explain why an event, sourcemap or trace did not show up, layer by layer |
| `sentry-release-medic` | Repair a release: CI sourcemap upload, finalize, deploy markers and release health |
| `sentry-issue-triage` | Triage a page: severity, suspect release, slow span and the correlated log line |
| `sentry-pii-scrub-enforcer` | Check PII scrubbing and project-standard drift; recommends changes, never applies them |

Each skill ships bundled helper scripts (shared code in `scripts/lib/sentry_readonly.py`). They read
input and print to stdout. They make no network calls, write no files, and refuse `--apply` and
`--send`. Each skill's `allowed-tools` is limited to its own scripts and read-only tooling.

## Migrating from v1

Every v1 skill name still resolves to a short redirect that tells you where its job went, so saved
prompts keep working. The redirects are removed in a later release.

| v1 skill(s) | v2 skill |
|-------------|----------|
| `sentry-cost-tuning` (Keep) · `sentry-load-scale` · `sentry-performance-tuning` · `sentry-rate-limits` | `sentry-quota-leak-hunter` |
| `sentry-advanced-troubleshooting` (Keep) · `sentry-debug-bundle` · `sentry-migration-deep-dive` · `sentry-upgrade-migration` | `sentry-event-forensics` |
| `sentry-release-management` (Keep) · `sentry-ci-integration` · `sentry-deploy-integration` | `sentry-release-medic` |
| `sentry-incident-runbook` (Keep) · `sentry-observability` | `sentry-issue-triage` |
| `sentry-data-handling` (Keep) · `sentry-policy-guardrails` · `sentry-security-basics` | `sentry-pii-scrub-enforcer` |
| `sentry-architecture-variants` · `sentry-common-errors` · `sentry-enterprise-rbac` · `sentry-error-capture` · `sentry-hello-world` · `sentry-install-auth` · `sentry-known-pitfalls` · `sentry-local-dev-loop` · `sentry-multi-env-setup` · `sentry-performance-tracing` · `sentry-prod-checklist` · `sentry-reference-architecture` · `sentry-reliability-patterns` · `sentry-sdk-patterns` | Cut: no direct replacement (the redirect explains why) |

Full map with reasons: [`000-docs/phase0-kill-list.md`](000-docs/phase0-kill-list.md).

## How the pack is organized

- Each skill keeps its agents under `skills/<skill>/agents/`. Agent procedures are
  `CHECKLIST.md` files (not `SKILL.md`), so they are not listed as separate marketplace skills.
- Where two skills need the same reference, it is a labeled copy (`OWNER.md` names the owning
  skill, `COPIED-FROM.md` names the source) rather than a silent duplicate.
- The pack ships no hooks and no MCP server.

## Design records

- [`000-docs/000-INDEX.md`](000-docs/000-INDEX.md)
- [`000-docs/001-AT-ADEC-sentry-v2-rebuild-decisions.md`](000-docs/001-AT-ADEC-sentry-v2-rebuild-decisions.md)

## License

MIT
