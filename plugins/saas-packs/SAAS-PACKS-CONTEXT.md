# 49-Vendor SaaS Skill Packs - Post-Compaction Recovery

> **READ THIS FIRST** after any context loss, compaction, or new session.

## Quick Recovery Commands

```bash
# 1. Check current beads state
bd sync                              # Pull latest
bd list --status in_progress         # What was I working on?
bd ready                             # What's available to work on?

# 2. Check CSV progress
cat plugins/saas-packs/TRACKER.csv | head -20

# 3. Check dependency graph
bd blocked | head -20
```

## What Is This Project?

**888 skills across 49 SaaS vendors** organized as individual installable packs.

| Tier | Vendors | Skills Each | Total |
|------|---------|-------------|-------|
| Flagship+ | 4 | 30 | 120 |
| Flagship | 8 | 24 | 192 |
| Pro | 22 | 18 | 396 |
| Standard | 15 | 12 | 180 |
| **TOTAL** | **49** | - | **888** |

## Key Locations

| What | Where |
|------|-------|
| Full Plan | ` |
| TRACKER.csv | `plugins/saas-packs/TRACKER.csv` |
| Beads Epic | `ccpi-saas` (master), `ccpi-saas-infra` (infrastructure) |
| Templates | `plugins/saas-packs/_templates/` |
| Generated Packs | `plugins/saas-packs/[vendor]-pack/` |
| Website Pages | `marketplace/src/pages/learn/` |

## Current Phase Detection

Run these commands to determine where we are:

```bash
# Count completed skills
grep -c "skills_created" plugins/saas-packs/TRACKER.csv 2>/dev/null || echo "CSV not yet created"

# Check if infrastructure is done
bd show ccpi-saas-infra 2>/dev/null || echo "Infrastructure epic not created"

# Check which vendor we're on
bd list --status in_progress | grep -E "ccpi-[a-z]+" | head -1
```

## Workflow Phases

### Phase 0: Infrastructure (Do First)

- [ ] Create TRACKER.csv
- [ ] Create beads epics + tasks
- [ ] Create _templates/slots/
- [ ] Update pnpm-workspace.yaml

### Phase 1+: Vendor Packs (One at a Time)

For each vendor (starting with Supabase):

1. Research vendor docs (Explore agent)
2. Create all skills (worker agents)
3. Test each skill (validation scripts)
4. Create website pages (frontend agent)
5. Create PR for pack
6. Gemini review → fix → merge
7. Update CSV → close tasks

## Agent Architecture

```
MAIN AGENT (You)
├── BEADS-MANAGER (manages tasks, CSV, deps)
├── WORKER AGENTS (generate skills, tests, pages)
└── CODE-REVIEWER (fixes validation failures)
```

**Beads Manager responsibilities:**

- Mark tasks in_progress/completed
- Update TRACKER.csv after completions
- Run `bd sync` after batches
- Verify dependencies before assigning work

## Critical Rules

1. **One skill at a time** - No batch generation
2. **CSV update on every close** - `bd close <id> --reason "... CSV: column=value"`
3. **Dependency graph enforced** - Only work on `bd ready` tasks
4. **1 PR per pack** - Not per skill (49 PRs total, not 888)
5. **Gemini reviews PRs** - Auto-fix, auto-merge when approved

## First Steps After Fresh Context

1. Read this file (you're doing that now)
2. Run `bd sync && bd list --status in_progress`
3. Check TRACKER.csv for progress
4. Continue from where you left off

## If Starting Fresh (No Beads Tasks)

```bash
# 1. Create master epic
bd create "EPIC: 49-Vendor SaaS Skill Packs" -t epic -p 0

# 2. Create infrastructure epic
bd create "EPIC: Infrastructure" -t epic -p 0 --parent ccpi-saas

# 3. Run task generator (creates 2,186 tasks)
python3 scripts/generate-saas-beads.py | bash

# 4. Run dependency generator
python3 scripts/generate-saas-beads.py --deps-only | bash

# 5. Verify
bd ready  # Should show only infra tasks
```

## Company List (49 total)

**Flagship+ (30 skills):** Supabase, Vercel, Sentry, LangChain

**Flagship (24 skills):** Clerk, PostHog, ClickHouse, Together AI, Mistral AI, Alchemy, Apify, Bright Data

**Pro (18 skills):** Cursor, OpenRouter, Groq, Linear, Fly.io, StackBlitz, Framer, Hex, Fathom, ElevenLabs, Deepgram, AssemblyAI, Retell AI, Runway, Ideogram, FireCrawl, Exa, Customer.io, Attio, Apollo, Windsurf

**Standard (12 skills):** Clay, CodeRabbit, Fireflies.ai, Gamma, Granola, Instantly, Kling AI, Lindy, SerpApi, Vast.ai, Juicebox, Fondo, Finta, Wispr, Anima

## Slot System Quick Reference

| Slots | Name | All Vendors? |
|-------|------|--------------|
| S01-S12 | Standard (install, hello world, etc.) | Yes (49) |
| P13-P18 | Pro (CI, deploy, webhooks, perf, cost, arch) | 35 vendors |
| F19-F24 | Flagship (multi-env, observability, incident, data, RBAC, migration) | 13 vendors |
| X25-X30 | Flagship+ (advanced debug, scale, reliability, policy, arch variants, pitfalls) | 5 vendors |

---

*Last updated: 2025-12-29*
*Full plan:
