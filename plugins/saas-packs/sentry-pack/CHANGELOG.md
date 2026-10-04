# Changelog — sentry-pack

All notable changes to this pack. Format follows [Keep a Changelog](https://keepachangelog.com/);
versioning is SemVer on the `sentry-pack` marketplace slug.

## [2.0.0]

### Changed

- Rebuilt the pack around five operational jobs instead of 30 SDK tutorials:
  `sentry-quota-leak-hunter`, `sentry-event-forensics`, `sentry-release-medic`,
  `sentry-issue-triage` and `sentry-pii-scrub-enforcer`.
- All five skills are advisory: they work on pasted configuration, stats and event JSON (or
  `sentry-cli` output) and recommend changes. Live read-only API fetch is a planned follow-up.

### Added

- Per-skill agents whose procedures are `CHECKLIST.md` files, so they are not listed as separate
  marketplace skills.
- Bundled helper scripts with a shared module, `scripts/lib/sentry_readonly.py`. Scripts print to
  stdout, make no network calls, write no files, and refuse `--apply` / `--send`.
- `000-docs/`: the v1 → v2 migration map (`phase0-kill-list.md`) and the rebuild decision record.

### Deprecated

- All 30 v1 skill names now resolve to short redirects that name the replacement skill or explain
  the cut (Keep 5 · Merge 11 · Cut 14). The redirects are removed in a later release.

### Security

- Each skill's `allowed-tools` is limited to its own bundled scripts and read-only tooling, so the
  advisory-only design is enforced by the permission boundary, not only by instructions.
