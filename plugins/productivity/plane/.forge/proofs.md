# Forge Proofs — Plane Plugin

> 2026-10-23 qualification: the record below is historical static evidence. Its
> production-ready language and old behavioral command examples do not establish
> live compatibility or authorize provider execution. The current versioned mapping
> is in `skills/plane/references/api-surface.md`. No authenticated workspace or
> behavioral evaluation was run for this source review; consult the current
> validate-skillmd workflow before any separately authorized evaluation.

**Forge run**: 2026-05-07
**Plugin slug**: `plane`
**Forge version**: /skill-creator v8.1.0

## Tier 1 — IS Marketplace Validator

**Command**:
```bash
python3 scripts/validate-skills-schema.py --marketplace plugins/productivity/plane/skills/plane/SKILL.md
```

**Result**: Grade **A (97/100)**

| Pillar | Score | Notes |
|---|---|---|
| Progressive Disclosure | 30/30 | Excellent token economy (≤150 lines), 3 reference files, well-structured |
| Ease of Use | 24/25 | Complete metadata, 'Use when' + trigger phrases present, 8 sections |
| Utility | 18/20 | Has overview, prerequisites, output spec, error handling, validation, 3 examples |
| Spec Compliance | 15/15 | Valid frontmatter, proper naming, good description, optional fields ok |
| Writing Style | 8/10 | Good voice, concise, minor: some second-person phrasing |
| Modifiers | +2 | grep-friendly + supporting_files (3 substantial reference files) |

**Errors**: 0
**Warnings**: 0 (after iteration — initial run had backtick-in-description warning fixed)

## Tier 2 — Static Production Gate

**Command** (runs inline as part of validate-skills-schema.py at marketplace tier):

| Check | Verdict |
|---|---|
| tier2:allowed-tools-accuracy | ✅ PASS — all declared tools (Read, Bash(jq:*), Bash(date:*), AskUserQuestion) referenced in body |
| tier2:auth-documented | ✅ PASS — auth section present (env vars documented) |
| tier2:dead-code | ✅ PASS — no literal-false branches |
| tier2:tool-safety | ✅ PASS — no unscoped Bash + dangerous companion |
| tier2:orchestration-bounds | ✅ PASS — agents are nested within this skill (subagent synthesis), not cross-skill orchestration |

**Tier 2 verdict**: **GREEN**

## Tier 3A — JRig Package Integrity

**Command**:
```bash
j-rig check plugins/productivity/plane/skills/plane
```

**Result**: **12 passed, 0 warnings, 0 errors**

Checks executed (per JRig v0.14.0 deterministic registry):

- `pkg:skill-md-exists` — pass
- `pkg:skill-md-parses` — pass
- `pkg:name-present` — pass
- `pkg:description-present` — pass
- `heuristic:description-length` — pass
- `heuristic:description-words` — pass
- `pkg:body-size` — pass
- `pkg:no-xml-tags-name` — pass
- `pkg:no-xml-tags-description` — pass
- `pkg:references-resolve` — pass (all 3 reference files exist)
- `anthropic:no-time-sensitive` — pass
- `pkg:body-min-lines` — pass

**Tier 3A verdict**: **GREEN**

## Tier 3B — JRig 7-Layer Behavioral Eval

**Status**: **NOT RUN** in this forge cycle.

Reason: behavioral eval across the model matrix (Haiku / Sonnet / Opus) takes ~10–30 minutes per skill and costs ~$2–$5 in API spend per the documented `--thorough` policy in `/validate-skillmd` SKILL.md. No current UI renders a JRig-Verified badge. A maintainer may record governed evidence only through the repository wrapper:

```bash
scripts/run-jrig-eval.sh \
  --skill-dir plugins/productivity/plane/skills/plane \
  --plugin plane \
  --models haiku,sonnet,opus \
  --inventory-db freshie/inventory.sqlite
```

The wrapper gives JRig a scratch database under `/dev/shm`, then the repository-owned recorder posts
the `tier3-jrig` row to `forge_proofs`. `marketplace/scripts/enrich-jrig-data.mjs` can derive an
untracked inspection projection from that row, but no live marketplace page consumes it after PR
#1046 removed the badge UI.

**Forge Gate 7 verdict**: **PASS** — all required gates (Tier 1 Grade A + Tier 2 GREEN + Tier 3A GREEN) cleared. Tier 3B is opt-in per documented policy and does not block the forge run.

## Final verdict

**Plugin is production-ready.** Validation evidence above is reproducible via:

```bash
python3 scripts/validate-skills-schema.py --marketplace plugins/productivity/plane/skills/plane/SKILL.md
j-rig check plugins/productivity/plane/skills/plane
```

Both commands run in seconds and cost nothing.

## Forge run summary

| Phase | Outcome | Time |
|---|---|---|
| Gate 1 NOI | Accepted: "Plane is a team behavior observatory" | ~5 min |
| Gate 2 Ecosystem | 5 competing tools cataloged; gap (behavioral synthesis) confirmed uncovered | ~10 min |
| Gate 3 API surface | 14 endpoints documented in api-surface.md (subset of full Plane API) | ~10 min |
| Gate 4 Archetype | Project / Workflow tracker; default compound set (velocity/stale/bottleneck) adopted + extended | ~5 min |
| Gate 5 Compound commands | 5 commands designed in compound-commands.md, each with synthesis logic + scoring | ~20 min |
| Gate 6 Generation | SKILL.md, 2 agents, 3 references, plugin.json, README.md written | ~30 min |
| Gate 7 Validation | Tier 1 Grade A, Tier 2 GREEN, Tier 3A GREEN | ~5 min |
| Gate 8 PR + catalog | (pending — will land via the feat/forge-plane-plugin branch) | ~10 min |

**Total: ~95 minutes** for a full hand-executed forge run. The /skill-creator skill's documented expectation is "~30 minutes from API name to PR-ready plugin" once tooling is mature; this 95-minute run is hand-executed with manual content authoring for the depth-of-thought sections (NOI justification, ecosystem analysis, compound-command rationale). A more automated future run could compress significantly.
