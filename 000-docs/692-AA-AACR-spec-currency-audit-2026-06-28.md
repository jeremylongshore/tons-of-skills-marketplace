<!-- doc-class: record -->

# Spec-Currency Audit — Claude Code authoring artifacts vs IS validators (2026-06-28)

**Code:** 692-AA-AACR · **Author:** Jeremy Longshore · **Date:** 2026-06-28

**Historical record:** §§ 0–10 retain the June audit. For the later persistence
replacement and remaining currency gaps, read the [2026-10-12 reconciliation](#11-reconciliation-2026-10-12).

**Scope:** Are the Intent Solutions validators (`scripts/validate-skills-schema.py`,
the `/validate-*` skills, the catalog scripts, the vendored kernel schemas) current
against the live Anthropic Claude Code authoring specs as of mid-2026?
**Method:** Six authoring surfaces fetched + cited from `code.claude.com/docs`
(plugins-reference, skills, sub-agents, hooks, mcp, plugin-marketplaces; docs map
auto-generated 2026-06-26), then each repo/skill validator cross-checked against the
verified spec. Four read-only audit passes + the live-doc fetches back every claim.

## 0. Verdict at a glance

| Surface                  | Enforcer                                                 | Spec-currency verdict                                                              |
| ------------------------ | -------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **plugin.json manifest** | `validate-skills-schema.py` `PLUGIN_JSON_FIELDS`         | **FIXED** — was the one blocking gap (schema 3.12.0 + 3.13.0, merged)              |
| **SKILL.md frontmatter** | `validate-skills-schema.py` `SKILL_FIELDS`               | **CURRENT** — all live fields recognized; unknowns warn, not error                 |
| **Agent definition**     | `validate-skills-schema.py` `AGENT_FIELDS`               | **CURRENT** — one intentional IS narrowing (preserved) + one dead constant (fixed) |
| **hooks**                | `/validate-hook` skill (global)                          | **CURRENT** — one cosmetic table-row omission (fixed in the global skill)          |
| **.mcp.json**            | `/validate-mcp` skill (global) + kernel schema           | skill: **2 doc gaps (fixed)**; kernel schema: **FLAGGED (architectural)**          |
| **marketplace.json**     | catalog scripts + `/validate-marketplace` skill + kernel | **FLAGGED** — blocked behind the kernel `authoring/v1 → v2` cutover (soak-gated)   |

**Headline:** the one _blocking_ in-repo currency bug was plugin.json (already fixed
and merged — schema 3.12.0 added 7 GA fields + `experimental`; 3.13.0 flipped
unrecognized-field handling error → warning + `--strict`). Everything else this repo
_enforces_ is current. The remaining items are (a) intentional IS-overlay choices we
keep on purpose, (b) cosmetic/doc fixes applied here, or (c) **architectural kernel /
gated cutover work that must not be changed autonomously** — flagged below for a
decision.

## 0.5 ROOT CAUSE — why a hand-patch was needed at all (the auto-currency loop is broken in two places)

The point of the spec-drift-watch (`intent-eval-lab/.github/workflows/spec-drift-watch.yml`,
daily 09:00 UTC, 16 upstream surfaces, FF#2 field-diff → kernel SSoT) is that I should
**never** have to hand-patch a field set. That it was needed is the real finding. Diagnosis:

1. **The watcher IS alive — but it cannot persist anything it produces.** The latest run
   logs show it fetching all 16 surfaces, the heartbeat advancing (`last run 24.3h ago`),
   and `recorded run; all 16 surfaces under the streak threshold` — in the GH Actions
   **cache**. But **every commit-back push fails**: `main` requires 9 status checks
   (`enforce_admins:false`), and the `github-actions` bot is not an admin, so a direct push
   of a fresh (un-checked) commit is rejected. Confirmed in every run log
   (`archive commit-back push failed (branch protection?) — delta preserved as a workflow
artifact`) and in git history (no bot commit-back has **ever** landed on `main`).
   **Consequence:** the kernel SSoT snapshots, the liveness `.state.json`, the lineage log,
   and the currency evidence are all frozen at the last **manual** deep-capture PR
   (#132–#137). The committed `specs/snapshots/.state.json` is `last_run_utc: null` forever
   → `watcher-liveness.py` prints `"heartbeat bootstrap — no prior run recorded yet (OK)"`
   → the dead-man heartbeat is inert and the dashboard reads **DEGRADED / no successful live
   run recorded**. The watcher built to "never fail silent-green" _is_ silent-green, because
   it can't write its own liveness proof back.

2. **Even with a current SSoT, CCP doesn't consume it.** The kernel's vendored
   plugin-manifest snapshot (`intent-eval-lab/specs/_vendor/upstream/plugin-manifest/`)
   **already contains** `displayName`, `defaultEnabled`, `channels`, `dependencies`,
   `userConfig`, `experimental` — captured by a manual run in June. So the drift-watch had
   the current manifest; CCP's `PLUGIN_JSON_FIELDS` was stale only because it is
   **hand-maintained and not generated from / validated against the kernel SSoT**. The
   kernel→CCP consumer-cutover (the SAK Phase-2/Phase-4 work, soak-gated per
   `project_ccpi_cicd_posture_soak_gate`) is unbuilt, so a current kernel does **not** make
   CCP current.

**So the cure is not more hand-patches — it is closing two loops:**

- **(L1) Persistence:** make the watcher's commit-back succeed. Options (Jeremy's call —
  security posture): give the push an **admin/bypass token** (a fine-grained PAT or GitHub
  App in a bypass allowlist; since `enforce_admins:false`, an admin-authenticated push
  bypasses the status-check gate), **or** have the watcher open an **auto-mergeable PR** for
  its captures (keeps `main` gated), **and** set the external dead-man (`SPEC_DRIFT_HEARTBEAT_URL`,
  currently unset) so absence of the daily ping alerts without any commit. Until L1 lands,
  the SSoT only advances on manual capture PRs and liveness can't be proven from the repo.
- **(L2) Consumption:** the gated kernel→CCP consumer-cutover — `PLUGIN_JSON_FIELDS` (and the
  other hand-maintained validator sets) should be **derived from / drift-gated against** the
  kernel `authoring/v*` schemas, so a kernel update propagates without a hand-patch.

The individual fixes in §§ 1–8 are correct and worth keeping, but they are **symptom
treatment**. L1 + L2 are the cure.

## 1. plugin.json — FIXED (reference)

`PLUGIN_JSON_FIELDS` carried only the pre-GA 15 fields and **errored** on every
unrecognized field. Anthropic had added 7 GA fields + an `experimental` object, and
its own `claude plugin validate` _warns_ (never errors) on unknowns.

- **Schema 3.12.0** — added `displayName`, `defaultEnabled`, `dependencies`,
  `userConfig`, `channels`, `$schema`, `experimental`; `TYPE_MAP` gained `boolean`.
- **Schema 3.13.0** — unrecognized plugin.json field → **WARNING** (was ERROR);
  new `--strict` promotes to error; wrong-type + missing `name` stay errors; difflib
  "did you mean" hint. NON-NEGOTIABLE #7, approved 2026-06-28.

Source: `code.claude.com/docs/en/plugins-reference` § "Plugin manifest schema" +
§ "Unrecognized fields". Both fixes merged; `/validate-plugin` reference
(`plugin-schema.md`) synced to 22 fields.

## 2. SKILL.md frontmatter — CURRENT (no change)

`SKILL_FIELDS` recognizes the full live set, verified against
`code.claude.com/docs/en/skills` § "Frontmatter reference": `name`, `description`,
`when_to_use` (underscore — the lone non-kebab key, confirmed against the doc),
`license`, `compatibility`, `metadata`, `allowed-tools`, `disallowed-tools`,
`disable-model-invocation`, `user-invocable`, `model`, `effort`, `context`, `agent`,
`argument-hint`, `arguments`, `hooks`, `paths`, `shell`. Unknown skill fields →
**warning** ("Will be ignored by the runtime"), matching Anthropic.

> Correction to an earlier in-session claim: a grep-escaping bug (`\|` under
> `grep -E`) made `agent`/`argument-hint`/`user-invocable`/`when_to_use` look absent.
> They are all present. There was no SKILL.md gap.

## 3. Agent definition — CURRENT (one fix, one intentional narrowing preserved)

`AGENT_FIELDS` recognizes all 15 optional + 2 required live fields; the
`permissionMode`, `memory`, and `color` enums match the spec exactly; the
plugin-restricted set (`hooks`, `mcpServers`, `permissionMode` silently ignored on
plugin agents) and the banned-field list are correct.

- **FIXED here (dead code):** module-level `VALID_EFFORT_LEVELS` (line 1588) was a
  stale, unused `["low","medium","high","max"]` — missing `xhigh`. The _live_ check
  uses `AGENT_FIELDS["effort"]` (correct, includes `xhigh`); the dead constant is
  aligned to avoid a future-use landmine.
- **PRESERVED (intentional IS narrowing — per the "leave my extras" instruction):**
  the agent `model` enum (`sonnet|haiku|opus|fable|inherit`) **rejects full
  `claude-*` model IDs**, which Anthropic permits and which the _skill_ path accepts.
  The code comment states this is a deliberate IS-contract narrowing. Left as-is. If
  you want the agent path to accept full IDs (matching the skill path + spec), that's
  a one-line change — say the word.

## 4. hooks — CURRENT (cosmetic fix, global skill)

This repo's `validate-skills-schema.py` does **not** validate hook-event structure
(it only checks the `hooks` field is a dict / the `hooks.json` parses) — it delegates
to the `/validate-hook` skill. That skill + its `anthropic-hooks-reference.md` live in
`~/.claude/skills/` (**not** in this repo's git) and already carry the full current
event surface (incl. `SessionEnd`, `StopFailure`, `PostToolUseFailure`, `Elicitation`)
and all 5 handler types with correct required fields.

- **FIXED in the global skill:** the reference's Hook Events _table_ omitted a
  `SessionEnd` row even though the rest of the file uses it — internal inconsistency,
  now corrected. (Global file; not part of this repo's PR.)

## 5. .mcp.json — skill doc gaps FIXED; kernel schema FLAGGED

Two surfaces, with conflicting transport models:

- **`/validate-mcp` skill (global `~/.claude/skills/`) — FIXED (doc-level):** its
  transport allowlist was `stdio|http|sse|ws`, missing the **`websocket`** and
  **`streamable-http`** aliases the spec defines, and it did not mark **`sse`
  deprecated** (the bundled reference and the kernel `$comment` both do). Aliases
  added + `sse` deprecation note added.
- **Kernel schema (`@intentsolutions/core` `authoring/v1/.../mcp-config.v1.json`) —
  🚩 FLAGGED (architectural, do NOT autonomously change):** the vendored/installed
  kernel models a non-existent `transport` field (real configs use **`type`**), has
  **no `url` property**, and makes `command`/`args`/`env` unconditionally required —
  so it cannot represent any http/sse/ws server and fails even real stdio configs
  (which carry no `transport` key). This is a kernel SSoT defect, ISEDC-gated, and
  lives in `@intentsolutions/core`, not here. **Needs a kernel change + ISEDC review.**

## 6. marketplace.json — FLAGGED (blocked on the kernel v1→v2 cutover)

The catalog scripts that are field-agnostic by design (`validate-catalog-invariants.py`,
`check-catalog-format.py`) are **current**. The gap is that `sync-marketplace.cjs`
(line ~63) reads the kernel `authoring/**v1**` fold, whose per-entry shape is only
`name` + `source` (relative-path source). The **current `authoring/v2`** fold (shipped
in `@intentsolutions/core@0.9.0`) models all the modern per-entry fields
(`displayName`, `defaultEnabled`, `strict`, `tags`, `category`, …) + all five source
forms (github / url / git-subdir / npm / relative).

🚩 **FLAGGED (do NOT autonomously change):** pointing the consumer at `authoring/v2` is
the **kernel-consumer-cutover** that is **soak-gated** per the CCPI CI/CD posture
(`project_ccpi_cicd_posture_soak_gate`). The modern fields currently survive in the
CLI catalog only because they pass through the un-stripped path — not because the
kernel sanctions them. The `/validate-marketplace` skill (global) likewise vendors the
stale v1 schema and its SKILL.md prose/Step-5 matcher omit the `git-subdir`/`npm`
object source forms. **All of this should land together with the v2 cutover**, not
piecemeal (editing prose while the trusted schema stays v1 creates a prose-vs-schema
mismatch).

- **`relevance` (v2.1.152+):** documented by Anthropic but absent **everywhere**,
  including kernel `authoring/v2`. This is an **upstream kernel gap** — file against
  `@intentsolutions/core` to add it to `marketplace-catalog.v2.json` per-entry.

## 7. Kernel version drift — FLAGGED (verify before acting)

`package.json` pins `@intentsolutions/core@0.9.0`, but the audit agents reported the
installed `node_modules` tree resolving to an older generation (0.4.1 was reported;
the lockfile shows multiple transitive versions; the package's `exports` block blocks
a direct version read). Because §5 and §6 both target the kernel, **the authoritative
mcp-config / marketplace contract is currently ambiguous.** Reconcile first
(`pnpm install` to relink, confirm `authoring/v2` is present) before any kernel-facing
change. This is environment/coordination work, not a committed-code fix.

## 8. What was changed by this audit

| Change                                                          | Where                                                        | Class                 |
| --------------------------------------------------------------- | ------------------------------------------------------------ | --------------------- |
| Dead `VALID_EFFORT_LEVELS` aligned to include `xhigh`           | `scripts/validate-skills-schema.py` (this repo)              | hygiene / correctness |
| `SessionEnd` events-table row added                             | `~/.claude/skills/.../anthropic-hooks-reference.md` (global) | doc currency          |
| `websocket` + `streamable-http` aliases; `sse` deprecation note | `~/.claude/skills/validate-mcp/SKILL.md` (global)            | doc currency          |
| This audit doc                                                  | `000-docs/692-AT-AUDT-…` (this repo)                         | record                |

## 9. Open decisions for you (not auto-changed)

**The cure (close the auto-currency loop — see § 0.5):**

0a. **L1 — drift-watch persistence.** Pick the commit-back mechanism so the watcher can
write back: admin/bypass push token, or auto-mergeable capture PRs; plus set
`SPEC_DRIFT_HEARTBEAT_URL` for durable external liveness. Until this lands, the SSoT
only advances on manual capture PRs and liveness can't be proven from the repo.

0b. **L2 — kernel→CCP consumer-cutover.** Derive/drift-gate `PLUGIN_JSON_FIELDS` (and the
other hand-maintained validator sets) against the kernel `authoring/v*` schemas, so a
kernel update propagates without a hand-patch. Soak-gated (SAK Phase-2/4).

**Smaller items:**

1. **Agent `model` full-IDs** — accept `claude-*` on the agent path (match skill path
   - spec), or keep the intentional IS narrowing? (Left narrowed for now.)
2. **Kernel mcp-config schema** (§5) — architectural fix in `@intentsolutions/core`,
   ISEDC-gated.
3. **Marketplace `authoring/v1 → v2` cutover** (§6) — soak-gated; lands the modern
   per-entry fields + source forms in `sync-marketplace.cjs` + the global skill
   together.
4. **`relevance`** (§6) — upstream kernel addition.
5. **Version-drift reconcile** (§7) — `pnpm install` + confirm v2, before 2–4.

## 10. Sources

All verified live 2026-06-28 against `code.claude.com/docs/en/`:
`plugins-reference`, `skills`, `sub-agents`, `hooks`, `mcp`, `plugin-marketplaces`
(docs map auto-generated 2026-06-26). Field-level currency for plugin.json is also
recorded in `SCHEMA_CHANGELOG.md` 3.12.0 + 3.13.0.

## 11. Reconciliation (2026-10-12)

This addendum reconciles bead `bd_000-projects-n2k2`; it does not certify the whole
currency loop. Repository observations are pinned to marketplace
`0ae01c7779c2837361584f300ee04c6b9f35d1df`, lab
`ba25e998de26a6d14be3041d2d836976c48c85a0`, and core
`dcd5f0064e9964b1b9b13d5fca7dcf8dd5ceb3fa`.

### Root cause and shipped repairs

The June investigation recorded three boundary failures: protected `main` rejected watcher
persistence; the consumer's installed kernel lagged its declared version; and
the hand-maintained plugin-field registry had no kernel comparison. A successful
fetch did not prove durable capture, and a current lab capture did not prove a
published kernel or an updated consumer.

Lab [PR #207](https://github.com/jeremylongshore/intent-eval-lab/pull/207) merged
June 29 UTC with bypass-token persistence. That was an intermediate repair.
[PR #234](https://github.com/jeremylongshore/intent-eval-lab/pull/234) replaced it
on July 23 with default-`GITHUB_TOKEN` writes to `spec-drift/auto-promotion` and
reviewed PR promotion. [PR #235](https://github.com/jeremylongshore/intent-eval-lab/pull/235)
retries creation of a missing promotion PR on scheduled/manual runs while the
promotion branch is ahead, including runs with no new commits;
[PR #238](https://github.com/jeremylongshore/intent-eval-lab/pull/238)
stops restoring the human-vendored baseline from the bot branch.
[PR #391](https://github.com/jeremylongshore/intent-eval-lab/pull/391) makes merged
promotions reset baseline-staleness accounting and consolidates drift issues.
The June bypass-token recommendation is therefore superseded; this audit does
not establish whether the obsolete secret was deleted.

The consumer's [schema 3.14.0 implementation][currency-validator] added
`load_kernel_plugin_fields()` and the advisory `plugin_manifest` comparison.
This checkout now declares and resolves `@intentsolutions/core@0.10.0`.
Directly calling `kernel_shadow_report()` reports eight matching required skill
fields and 23 matching plugin fields, but `disallowed_tools.match` is false.
Those results establish local agreement or disagreement with the installed
kernel, not agreement with every current upstream field.

### What the current evidence does and does not prove

At lab promotion [PR #381](https://github.com/jeremylongshore/intent-eval-lab/pull/381)
head `2dc8eef06d9ed0074bc7befdae71fb116d782a43`, the
[persisted state][currency-state] records `last_run_utc: 2026-10-12T09:37:56Z`
for 16 surfaces. The [scheduled run][currency-run] failed its final gate on
baseline-stale streaks while reporting `heartbeat_stale=false`. A live heartbeat
does not mean current baselines. Before promotion merges, inspect its branch
as well as `main`; the older `main` heartbeat alone cannot diagnose a dead watcher.

The [CI adapter][currency-adapter] explicitly skips the Python JSON's trailing
`kernel_shadow` element. Therefore the plugin-field comparison's existence does
not establish that the kernel-shadow CI report retains or alerts on it.
`kernel_shadow_report()` compares skill requiredness, one skill property
(`disallowed-tools`), and plugin field names; it is not full `SKILL_FIELDS` or
`AGENT_FIELDS` parity. The separate v1/v2 skill-corpus shadow must not be described
as complete field-registry coverage.

The `metadata` provenance question now has an upstream answer: Anthropic documents
an optional object for custom data, ignored by the runtime, requiring Claude Code
v2.1.222 or later. [Official manifest reference](https://code.claude.com/docs/en/plugins-reference#metadata).
The lab's [October 1 re-vendor][currency-vendor] adopted it from the September 23
capture. Core's [v2 overlay][currency-overlay] still calls it kernel-only and
contains the explicit convergence trigger to move it into the upstream base when
documented. Provenance is confirmed; kernel convergence and consumer delivery
remain outstanding. Matching consumer/kernel field sets can preserve stale
provenance together.

### Disposition of the original five follow-ups

Beads remains the task authority; these are dated dispositions, not closure claims.

| Follow-up                           | Disposition and evidence needed                                                                                                                                                                                                                                                                                     |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| a. Lab → kernel release cadence     | Open: `bd_000-projects-51f0f`; related capture work `bd_000-projects-218d`. The inspected lab/core release workflows are tag-triggered. The consumer's daily `kernel-vendor-hash` job checks published-package coupling; it does not publish lab changes. Prove governed promotion, release, and consumer adoption. |
| b. Narrow the bypass token          | Superseded by PR #234's default-token PR path. Do not restore the bypass architecture; secret retirement is not verified here.                                                                                                                                                                                      |
| c. Confirm `metadata` provenance    | Confirmed upstream as above; retain the schema-convergence obligation in `bd_000-projects-n2k2` until governed source, release, and consumer receipts exist.                                                                                                                                                        |
| d. Watch the watchers               | Open: current cross-reference execution and delivered stale-alert evidence were not obtained. A configured schedule is insufficient; verify promotion-branch heartbeat, baseline staleness, published package, installed consumer, and actual notification.                                                         |
| e. Cover other hand-maintained sets | Open under `bd_000-projects-n2k2` / SAK `bd_000-projects-9k5h`. Child `bd_000-projects-n2k2.1` owns retaining the plugin comparison in CI evidence with a planted-mismatch proof. Broader registry parity remains open; inspect existing `bd_000-projects-3kye.15` before duplicating its shadow scope.             |

The authority/cutover rules remain owned by [CLAUDE.md](../CLAUDE.md#validation--the-kernel-ssot--cicd-posture)
and [SCHEMA_CHANGELOG.md](SCHEMA_CHANGELOG.md). This documentation change neither
changes validator authority nor completes the five follow-ups. Keep `n2k2` open.

For follow-up a, compare the pinned [lab release workflow][currency-lab-release],
[core release workflow][currency-core-release], and
[consumer coupling workflow][currency-coupling]; they establish different parts
of the delivery path.

[currency-validator]: https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/0ae01c7779c2837361584f300ee04c6b9f35d1df/scripts/validate-skills-schema.py#L895-L993
[currency-adapter]: https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/0ae01c7779c2837361584f300ee04c6b9f35d1df/scripts/kernel-shadow-validation.mjs#L205-L242
[currency-state]: https://github.com/jeremylongshore/intent-eval-lab/blob/2dc8eef06d9ed0074bc7befdae71fb116d782a43/specs/snapshots/.state.json
[currency-run]: https://github.com/jeremylongshore/intent-eval-lab/actions/runs/38231081454
[currency-vendor]: https://github.com/jeremylongshore/intent-eval-lab/blob/ba25e998de26a6d14be3041d2d836976c48c85a0/specs/_vendor/upstream/plugin-manifest/vendor-meta.json
[currency-overlay]: https://github.com/jeremylongshore/intent-eval-core/blob/dcd5f0064e9964b1b9b13d5fca7dcf8dd5ceb3fa/schemas/authoring/v2/is-overlay/plugin-manifest.v2.json#L50-L54
[currency-lab-release]: https://github.com/jeremylongshore/intent-eval-lab/blob/ba25e998de26a6d14be3041d2d836976c48c85a0/.github/workflows/release.yml
[currency-core-release]: https://github.com/jeremylongshore/intent-eval-core/blob/dcd5f0064e9964b1b9b13d5fca7dcf8dd5ceb3fa/.github/workflows/release.yml
[currency-coupling]: https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/0ae01c7779c2837361584f300ee04c6b9f35d1df/.github/workflows/kernel-vendor-hash.yml
