# Changelog — sentry-pack

All notable changes to this pack. Format loosely follows [Keep a Changelog](https://keepachangelog.com/);
versioning is SemVer on the `sentry-pack` marketplace slug.

## [Unreleased] — 2.0.0

### Added

- Draft scaffold for the v2 rebuild: five top-level skills
  (`sentry-quota-leak-hunter`, `sentry-event-forensics`, `sentry-release-medic`,
  `sentry-issue-triage`, `sentry-pii-scrub-enforcer`) with agent trees, nested
  child skills under agents, eval-spec stubs, and docs stubs.
- Pack-level `000-docs/` (research + CTO ADR copy) and migration map pointer
  (kill list §3).
- Empty/minimal `hooks/hooks.json` — hooks are not default (ADR Decision 4).

### Changed

- Ground-up rebuild vs v1's 30 documentation skills (Cut 14 / Merge 11 / Keep 5).
  See README **Migration: v1 → v2** and `phase0-kill-list.md` §3.

### Notes

- Status: landed on `feat/plugins-saas-packs-sentry-v2` as **2.0.0** (strict semver; `2.0.0-draft` fails catalog version agreement). Not tagged. npm package stays `private` until a follow-up publish decision.
- Locked decisions: `000-docs/008-AT-ADEC-sentry-v2-cto-decision.md`.

## 2.0.0-draft (Absorb / MODIFY) — 2026-10-03

- Nested agent checklists renamed `SKILL.md` → `CHECKLIST.md` (marketplace corpus safety).
- Amended tree: fingerprint-auditor, noise-classifier, perf-span-auditor, replay-privacy; SC04 on org-key-boundaries; quota category fan-out = script + usage-auditor.
- Mandatory labeled reference copies (`OWNER.md` / `COPIED-FROM.md`) until cross-skill calls proven.
- Eval negatives from pressure test 009; PII description recommends / does not apply.
- Thin v1 stub redirects for Keep/Merge/Cut slugs; plugin.json v2 framing.
- Shared `scripts/lib/sentry_readonly.py` (no MCP).
- Absorb ADR: `000-docs/010-AT-ADEC-sentry-v2-modify-absorb.md`.
