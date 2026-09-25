<!-- doc-class: canonical -->

# 727 — Master Modernization Blueprint (Platform Master Standard)

**Status:** PROPOSED — becomes AUTHORITATIVE on merge **and** on the `STANDARDS.md § Canonical documents` pointer landing in the same PR (see § 12, gate G4). **The pointer landed in this PR** (§ 11.1 carries the proof); the condition is satisfied as written, not weakened.
**Doc class:** `canonical`
**Date:** 2026-08-13
**Scope:** the whole platform — corpus, catalog, canonical skill contract, harness adapters, provenance and licensing, evaluation and evidence, CI, release and supply chain, documentation governance, cross-repo authority boundaries, the original ten-epic execution plan, and the approved model-neutral Epic 11 extension.
**Authority:** Intent Solutions — **tonsofskills.com** (the live property). The retired legacy domain recorded in frozen document 6767-h is removed by Epic 1 from every actionable first-party and generated surface.
**Repository:** `jeremylongshore/tons-of-skills-marketplace` (canonical). Historical GitHub URLs redirect, and public install slug `jeremylongshore/claude-code-plugins` is a **frozen compatibility contract** — see § 5.6 and decision 803.

---

## 0A. RATIFICATION CORRECTIONS — what changed after conditional ratification

The owner **conditionally ratified** this blueprint on 2026-08-13 and returned nine required corrections. All nine are applied below; this table is the map, so a reader can audit the correction rather than take it on trust. **Nothing was implemented, instantiated, merged, published, or mutated externally to satisfy them** — the corrections are documentation and planning only, and § 20's boundary is unchanged.

| #   | Correction                                          | Where it now lives                                                                               |
| --- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| 1   | The missing root README landing contract            | **§ 6A** (whole section) + § 11 map row + Epic 2 bead 2.13 + `728 § 4 C6` / `729 § 6` cross-refs |
| 2   | Complete the activation mechanism                   | Status line + **§ 11.1** (one-owner-per-fact-class proof) + `STANDARDS.md § Canonical documents` |
| 3   | Correct the disputed compliance figures             | **§ 3.1** (re-measurement, embedded) + scorecard rows 4 and 6 + § 1, § 2, § 13 E8, § 14 row 27   |
| 4   | Repair the benchmark licensing rule                 | `728 § 4` binding preamble + annotations on rows A2, A4, A5, A6, B4, B7, D1                      |
| 5   | Remove the Mission 01 / Epic 1 ambiguity            | **§ 13 EPIC 1** → "Mission 01 is NOT Epic 1" (delivery table + per-bead disposition)             |
| 6   | Preserve progressive epic activation                | **§ 13** + **§ 15.1** historical launch control; amended execution authority recorded in § 13    |
| 7   | Record the npm-token resolution (do NOT perform it) | **§ 18.9** (+ sequencing note in § 18.4)                                                         |
| 8   | Preserve honest independent review                  | **§ 18.5** (rewritten) + Epic 10 independence precondition                                       |
| 9   | Draft contributor wording (do NOT post it)          | `000-docs/709-DR-GUID-reviewing-external-prs.md` § 8 — **drafted, not posted**                   |

The table records the 2026-08-13 ratification corrections. The later owner-authorized 2026-08-26
amendment is additive: it changed repository identity, authorized full Beads graph instantiation,
and added Epic 11 without rewriting the original ratification history.

---

## 0. PRIOR AUTHORITY RECONCILIATION — read this before anything else

**This document SUPERSEDES `000-docs/6767-h-SPEC-DR-STND-claude-code-extensions-master.md`** (v1.0.0, dated 2025-12-28) as the platform master standard.

6767-h self-declares `Status: AUTHORITATIVE - Single Source of Truth`, is scoped to Claude Code only, and names the retired legacy domain as its authority while the live property is `tonsofskills.com`. Eight of its claims are verified stale or false; the four that matter most:

1. Its **Non-Negotiable Invariant #1** — "`allowed-tools` MUST be a CSV string; a YAML array is ❌ wrong" — is **FALSE**. Both forms have been valid since schema 3.3.1 (`scripts/validate-skills-schema.py:487`; `000-docs/SCHEMA_CHANGELOG.md` 3.3.1, 2026-04-28). A reviewer obeying 6767-h **rejects valid frontmatter**. The same false rule is repeated verbatim in `6767-c`, `6767-d`, and `6767-e`, all three of which still self-declare canonical.
2. Its § 5 required-field checklist lists **6** fields. The required set is **8** (`ALWAYS_REQUIRED`, `validate-skills-schema.py:714`); `compatibility` and `tags` are missing from 6767-h.
3. Its § 4.3 "Required Website Gates" invokes `scripts/validate-frontmatter.py`, which **does not exist**, and `corepack pnpm -C marketplace build`, where `marketplace/` uses **npm** (CI-enforced by `check-package-manager`).
4. It is silent on everything built since 2025-12-28: the agent contract, `disallowed-tools`, visibility gating, self-declared config, the kernel SSoT, the three-context CI gate, mirror-by-default external sync, cowork packaging, and submission-docs intake.

**This document does NOT supersede `000-docs/6767-b-SPEC-DR-STND-claude-skills-standard.md`.** 6767-b is the skills frontmatter/rubric standard, actively maintained (v3.6.0, last updated 2026-05-14, currently documenting schema 3.15.2 against the validator's actual `SCHEMA_VERSION = "3.16.1"` — corrected by Epic 2), and it delegates post-3.6.0 rules to `SCHEMA_CHANGELOG.md` via its own currency banner. **6767-h's claim to have superseded 6767-b is formally REVOKED**, because practice never honored it: `STANDARDS.md § Canonical documents` and the global operator instructions both point at 6767-b as the master spec, and 6767-b was maintained for five months _after_ 6767-h froze. 6767-b becomes **subordinate to this blueprint's canonical contract** (§ 5) — it remains the owner of the skill-frontmatter rubric within the boundaries this document sets.

### Section-level disposition of 6767-h

| 6767-h section                                                                        | Disposition                                                                       |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| § 1.1 plugin root anatomy (`.claude-plugin/` contains ONLY `plugin.json`)             | **CARRIED FORWARD** unchanged                                                     |
| § 1.2 skill folder anatomy (`SKILL.md` + `scripts/`/`references/`/`assets/`)          | **CARRIED FORWARD** unchanged                                                     |
| § 3.3 `scripts/` executed · `references/` context-loaded · `assets/` path-addressable | **CARRIED FORWARD** — this is the progressive-disclosure cost model               |
| Invariant #2 — `Bash` must be scoped (`Bash(git:*)`)                                  | **CARRIED FORWARD**, and promoted to a gate (Epic 4)                              |
| Invariant #3 — portable paths, never absolute                                         | **CARRIED FORWARD**, retargeted to `${SKILL_DIR}` in the canonical layer (Epic 3) |
| § 4.1 `marketplace.extended.json` = SoT, `marketplace.json` generated                 | **CARRIED FORWARD AND EXTENDED** — three derived artifacts, not one               |
| **Invariant #1 — `allowed-tools` must be CSV**                                        | **REVERSED.** Both CSV string and YAML list are valid                             |
| § 2.1, § 3.1, § 5 required-field checklists                                           | **REPLACED** by the 8-field `ALWAYS_REQUIRED` set                                 |
| § 3.2 body sections                                                                   | **REPLACED** — body sections credit heading-equivalents (`STANDARDS.md`)          |
| § 4.3 required website gates                                                          | **REPLACED** by the three-context CI gate (§ 11)                                  |
| everything else                                                                       | **SUPERSEDED WITHOUT REPLACEMENT** (obsolete tooling references)                  |

### Freeze, do not delete

`scripts/parse-prose-anchors.py:117` hard-defaults to 6767-h as its parse target, and `scripts/check-prose-anchors.py:24` matches `6767-h § <id>` citations inside JSON-Schema `$comment` fields (fixtures at `tests/fixtures/prose-anchors/`). **Neither script runs in any CI job today** — verified. 6767-h is therefore a live _anchor namespace_ that no gate exercises. Deleting or renumbering it silently breaks a citation contract. It is **frozen with a banner, never removed**, its section anchors are immutable, and Epic 2 puts the anchor checker into CI so the freeze is enforceable rather than aspirational.

`6767-a`, `6767-c`, `6767-d`, `6767-e` are superseded and frozen alongside it. `6767-f` and `6767-g` (scaffold diagrams) survive as **REFERENCE** — their content is structural and remains accurate — and lose their `CANONICAL` self-declaration.

---

## 1. EXECUTIVE POSITION

**Measurement baseline: `origin/main` at `HEAD 478aaf17731714fed9b1779284de6a5b3729ef6e`, 2026-08-14.** Every headline number below was re-measured at that SHA for this document. The documentation branch changes no measurement inputs; its measurement-input equivalence check returns zero. Prior analyses baselined at `436a00f80`, `708692244`, and `49210ecb6`; the tree moved during analysis. Re-baselining before ratification is mandatory, not optional — that is the first thing this document proves about itself.

### Where the platform is

CCPI is a **470-plugin, 3,179-skill, 347-agent** marketplace (471 catalog entries / 467 distinct names; 22,962 tracked files) with genuinely excellent isolated engineering — the cowork packaging subsystem with three hard gates and zero drift, the SQL statement classifier, SOPS `/dev/shm` credential handling, the `sources.lock.json` quarantine, the cosign→Fulcio→production-Rekor evidence chain — surrounded by a governance perimeter that does not close. Four measured facts define the position:

1. **The authoritative gate does not gate.** `--marketplace` appears in exactly **three** workflow locations, all non-blocking: `pr-prescreen.yml:133` (advisory), `promote-curated.yml:90` (`|| true`), `minimax-review.yml:247` (advisory). A pull request adding a `SKILL.md` with **zero of the eight required fields merges clean today.** The 7,687-error baseline is therefore not a legacy pool — it is an **open intake**.
2. **The quality claim is not a claim.** 962 A/B-graded artifacts still fail that gate, including **132 A-graded files carrying 219 errors** (re-measured at this HEAD — § 3.1). The 100-point rubric and the pass/fail gate are independent axes that were never reconciled. The single public verification badge is fed by a **171-byte hand-editable committed file** (`marketplace/src/data/jrig-data.json`) that **no `.astro` page imports**, backed by 3 ledger rows whose own evidence text says the primary artifact "was not retained."
3. **Publication is ungated and identity is borrowed.** `publish-changed-packages.yml` fires on `push: main` with no dependency on any check, under `enforce_admins:false`. The repository contains **63 provenance-marked package mirrors; 58 are live `@intentsolutionsio/*` packages and 5 are outside that npm scope**. PR #1187 now marks all 63 private, but publisher-level provenance exclusion remains E7.2. The current 58-package scoped inventory contains 52 clearly third-party packages excluding Skyvern, one separate AGPL defect, and 5 first-party/ownership-ambiguous packages; 53 are clearly third-party when Skyvern is included. No historical 55 count is treated as current.
4. **Portability is asserted, not built.** 1,454 skills claim Codex/OpenClaw compatibility with zero adapters and zero tests, while the repo's only "adapter" is a **27-file byte-identical fork** that Freshie grades twice.

### Where it must get to

A canonical, harness-free skill contract plus thin **generated** adapters; runtime safety enforced at machine boundaries and labeled where it cannot be; evidence that carries its class and a retrievable hash-matched artifact, or is not evidence; fail-closed validation, promotion, packaging, and release; exactly one writer per fact class across six systems; certification that cannot be self-approved and that expires; and every legacy artifact holding a machine-assigned disposition rather than an unexamined letter grade.

### The single recommended path

The original ratification defined ten epics. The owner-authorized 2026-08-26 amendment added a
model-neutral distribution and identity-migration epic, so the effective programme now has
**eleven epics, one strategy: close the machine boundaries in decision-hierarchy order, pin the
debt, then certify a small honest set.** Not "raise the grade." The sequence is forced by the
hierarchy, not by effort:

> **Quarantine the legal exposure → freeze the false authorities → pin the debt → close the safety boundaries → build the canonical contract → make evidence real → certify a small set and publish the backlog beside it.**

Three commitments make this a strategy rather than a checklist:

- **The correct first output of the certification standard is ZERO certified artifacts.** Criterion E3 (retained, hash-matched primary artifact) is unreachable corpus-wide today: 0 retained primary artifacts, 0 non-null baseline deltas, 0.44% eval-spec adoption. A criteria set that instantly grants A to 1,596 skills would be the same defect being fixed. Publishing "12 certified, 3,668 pending" beats publishing "1,596 A-grade."
- **Nothing is remediated before it is pinned.** 88.9% of the 7,687 errors are mechanically fixable, which is precisely why mass remediation must not start first — it is the most attractive way to spend the whole program producing a number nobody can defend.
- **The kernel authority flip does not happen in this program.** The shadow lane's own `directionBreakdown` reports `existing-PASS / kernel-FAIL: 0` — `authoring/v1` has never once caught something the prose validator missed. Flipping to it would be a pure loss of enforcement. The flip target is `authoring/v2`, the six DR-049 conditions stand unchanged, and pin bumps are explicitly **not** authority movement.

**What this costs in visible terms, stated up front:** the public verification badge goes dark, 1,454 portability claims are withdrawn, ~313 mirrors stop carrying a marketplace grade, and the certified count starts near zero. Every one of those is a truthfulness improvement ranked above the cosmetics it costs.

### Decision hierarchy (binding; lower never overrides higher)

| Rank | Concern                                                                    |
| ---: | -------------------------------------------------------------------------- |
|    1 | User / system safety                                                       |
|    2 | Legal / licensing / attribution / reputational                             |
|    3 | Truthful provenance + public identity                                      |
|    4 | Canonical source-of-truth integrity                                        |
|    5 | Runtime-**ENFORCED** controls (metadata and prose are **NOT** enforcement) |
|    6 | Model / harness portability                                                |
|    7 | Reproducible evidence                                                      |
|    8 | Fail-closed                                                                |
|    9 | Safe compatibility / migration                                             |
|   10 | Maintainability at scale                                                   |
|   11 | Contributor / user UX                                                      |
|   12 | Storage / cosmetics                                                        |

Every ADOPT/REJECT, every conflict resolution, and every escalation in this blueprint cites the rank on which it was decided.

---

## 2. FORMAL A-GRADE CRITERIA

**A-GRADE ⇔ (all of G1–G10) ∧ (all of E1–E6).** Every row terminates in an exit code, a hash comparison, or a filesystem/schema fact. The words _documented_, _reviewed_, _intended_, and _best-practice_ appear in no criterion. The 100-point Freshie score is retained as an **advisory quality hint only** and is explicitly **not** a certification input — 962 A/B artifacts that fail the gate prove why (§ 3.1).

### Gate G — structural prerequisites (any failure ⇒ not A; no partial credit)

| #   | Criterion                                                                                              | Verifier                                         | Why it cannot be satisfied by assertion                                                                                                                                      |
| --- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| G1  | Zero errors at marketplace tier                                                                        | `validate-skills-schema.py --marketplace`        | exit code                                                                                                                                                                    |
| G2  | Zero REFUSE, zero unwaived CHALLENGE                                                                   | `scripts/scan-synced-content.mjs`                | exit code; a waiver requires a **named reviewer, written reason, and expiry** in `scripts/scan-allowlist.txt`, read from the **base** branch (a PR may not allowlist itself) |
| G3  | Unicode hygiene clean                                                                                  | `validate-unicode-hygiene.py --strict`           | exit code                                                                                                                                                                    |
| G4  | `allowed-tools` least-privilege **and** accurate                                                       | tier-2 accuracy check                            | declared-but-unused **and** used-but-undeclared both fail; over-declaring cannot buy a pass                                                                                  |
| G5  | No unscoped `Bash` alongside `Write`/`WebFetch` absent a Safety Justification **naming the operation** | tier-2 tool-safety                               | free text alone does not clear it; the named operation is matched                                                                                                            |
| G6  | Every referenced path resolves inside the skill directory                                              | relative-link check                              | filesystem resolution                                                                                                                                                        |
| G7  | Every declared asset matches its extension                                                             | magic-byte sniff (**not** a NUL sniff)           | 12 artifacts fail this today                                                                                                                                                 |
| G8  | License declared and equal to `.source.json` when mirrored                                             | cross-file compare                               | 9 mirrors contradict upstream today                                                                                                                                          |
| G9  | No vendor-literal model id in the canonical layer                                                      | role-aware model-id classifier, bead-ID-excluded | ~131 true source files fail today                                                                                                                                            |
| G10 | Declared harness requirements satisfiable by ≥2 adapters, **or** explicitly marked single-harness      | adapter matrix                                   | 1,454 skills fail today                                                                                                                                                      |

### Gate E — evidence (class carried in-band; see § 10)

| #   | Criterion                                                                                     | Minimum class |
| --- | --------------------------------------------------------------------------------------------- | ------------- |
| E1  | Deterministic conformance reproducible offline from committed inputs                          | E1            |
| E2  | Committed `eval-spec.yaml`; `j-rig eval` passes under pinned tool + kernel + provider + model | E2            |
| E3  | **Primary `--json` artifact retained and hash-matched to the ledger**                         | E2            |
| E4  | Recorded `baseline_delta`: a deliberately-broken variant of the skill FAILS the same spec     | E3            |
| E5  | Ledger row written by an **independent CI identity**, never the producing agent               | —             |
| E6  | Provenance chain hash-links source → catalog → build → published artifact                     | —             |

**Three binding properties:**

- **Claim ceiling** — rendered strength is the `min` over a plugin's components. One E0 component caps the plugin at E0. Aggregation never raises a class.
- **Retention is a validity condition** — an E2/E3 record whose primary artifact is unretrievable **auto-demotes to E0**.
- **Anything short of the full conjunction is `CERTIFY-PENDING-EVIDENCE` at best, never A.**

**Applied to the corpus today: 0 artifacts qualify.** That is the standard working, not the standard failing.

### Certification tiers (computed, never self-declared)

The gate conjunction above defines the top tier. Because a uniform anatomy across 3,179 skills has exactly two outcomes — set the bar at the floor and certify nothing, or set it high and leave 90% permanently non-compliant — tier is **derived by the validator from what is present and passing**, written to Freshie, and projected onto the site.

| Tier   | Name      | Asserts                                                                           | Expected population               |
| ------ | --------- | --------------------------------------------------------------------------------- | --------------------------------- |
| **T0** | Listed    | parses; frontmatter valid; unicode-clean; not malicious                           | all 3,179                         |
| **T1** | Cataloged | T0 + registry entry + license + provenance resolved + generated artifacts in sync | in-repo + all 63 mirrors          |
| **T2** | Carded    | T1 + `skill-card.yaml` (capabilities, side effects, harness support, limitations) | curated set (~1,881)              |
| **T3** | Evaluated | T2 + `eval-spec.yaml` + a passing evidence bundle referenced by run id            | flagship packs, anything marketed |
| **T4** | Certified | T3 + G1–G10 ∧ E1–E6 + integrity digest + negative fixtures                        | small, deliberate, hand-counted   |

`CERTIFY-PENDING-EVIDENCE` is the honest name for T2-clean artifacts that cannot yet reach T3/T4. Self-declared tiers rot; the existing `verified:` / `curated:` split already teaches that two honest orthogonal flags beat one aspirational one.

---

## 3. BASELINE-TO-TARGET SCORECARD

Measured at `origin/main HEAD 478aaf17731714fed9b1779284de6a5b3729ef6e` unless a source doc is cited. **⚠ = a number prior drafts disputed; resolved here with the deciding measurement.** Rows marked **[RV]** were re-verified for this document today.

| #   | Dimension                                                                          | Measured baseline                                                                                                                                                                                                                                                                                                   | Target                                                                                            |
| --- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| 1   | Tracked files / plugin SKILL.md / agent files **[RV]**                             | 22,962 / 3,179 / 347                                                                                                                                                                                                                                                                                                | unchanged; counted by ONE resolver                                                                |
| 2   | Catalog entries vs distinct names **[RV]**                                         | **471 / 467** (`claudebase`, `geepers-agents` duplicated)                                                                                                                                                                                                                                                           | 467 / 467, uniqueness asserted                                                                    |
| 3   | Tracked stale catalog shadow **[RV]**                                              | 1 (`.claude-plugin/marketplace.extended.json.backup`, 234 entries, 2025-10-28)                                                                                                                                                                                                                                      | 0                                                                                                 |
| 4   | Marketplace-tier errors / compliance **[RM]**                                      | **7,687 errors / 26.3%** over 4,406 files — the **terminal `--marketplace` headline** only. It is NOT the SKILL.md total (7,433 over 3,679 rows) and NOT the agent lane (253 over 353 files). Three cohorts, three numbers; never merged — § 3.1                                                                    | ratchet-pinned, monotone ↓, ≤900 after structural classes clear                                   |
| 5   | Grade distribution **[RV]**                                                        | A 1,596 (43.4%) · B 986 (26.8%) · C 896 (24.3%) · D 193 (5.2%) · F 9 (0.2%); avg 85.1                                                                                                                                                                                                                               | published with cohort + `recall_note`                                                             |
| 6   | A/B artifacts failing the gate **[RM]**                                            | **962** (132 A-graded carrying **219** errors; 830 B-graded carrying 1,936) — § 3.1                                                                                                                                                                                                                                 | 0 among certified; number published                                                               |
| 7   | Structural error classes                                                           | body sections 6,104 · frontmatter fields 728 = **6,832 (88.9%)**                                                                                                                                                                                                                                                    | 0                                                                                                 |
| 8   | Safety error classes                                                               | unscoped `Bash` 222 · tier-2 tool-safety 185 · orchestration 30 · link-escape ~50                                                                                                                                                                                                                                   | 0, each by named human decision                                                                   |
| 9   | Security class (shell substitution in YAML)                                        | **10**                                                                                                                                                                                                                                                                                                              | 0, unwaivable                                                                                     |
| 10  | Agent errors / reported compliance rate                                            | **253** / **224.1%** (791 of 353 — arithmetically impossible)                                                                                                                                                                                                                                                       | 0 by 2026-10-31 / ≤100%, test-pinned                                                              |
| 11  | ⚠ Counterfeit assets (extension ≠ magic bytes)                                     | **12** — 8 under `plugins/`, 4 in `skills/.curated/`, of 46 binary-extension tracked files. _Drafts said 14/18/19/"4 confirmed"; all were looser scans. Deciding method: per-extension magic-byte compare over all `git ls-files`. Boycott-filter icons and servicegraph marks are genuine PNGs — false positives._ | 0                                                                                                 |
| 12  | Binary detection in the promotion path                                             | NUL sniff, 8 KiB (`freshie/scripts/promote-to-curated.py:225`) — misses all 12 while the drift gate prints "in sync (1915 promoted skills)"                                                                                                                                                                         | magic-byte + extension agreement, fail-closed                                                     |
| 13  | ⚠ Malformed `allowed-tools`                                                        | **three measurements of three things**: 3,138 of 3,179 declare it; **10** open with a bare folded scalar `>-` (5 inside the `.codex` fork); **21** carry a token outside any declared universe; **63** was a looser lexical scan                                                                                    | ONE parser, ONE vocabulary; unparseable = ERROR                                                   |
| 14  | ⚠ Distinct free-text `compatibility` values                                        | **40** (drafts said 41/42). Top: 1,409 `…also compatible with Codex and OpenClaw`; 1,385 `Designed for Claude Code`; 45 `…with Codex`. The upstream string is **OpenClaw**, not "OpenCode"                                                                                                                          | 0 free-text; generated projection of `adapters[]`                                                 |
| 15  | Multi-harness claims with zero adapter artifact                                    | **1,454**                                                                                                                                                                                                                                                                                                           | 0                                                                                                 |
| 16  | Adapter files byte-identical to canonical                                          | **27** (`plugins/testing/kobiton-automate/.codex/`)                                                                                                                                                                                                                                                                 | 0, gate-enforced                                                                                  |
| 17  | Functional Claude model-id lines / files                                           | 732 lines / 230 files, of which **97 are the generated curated mirror** → **~131 true source files**; plus 541 provider-prefixed occurrences invisible to a `claude-`-anchored regex                                                                                                                                | 0 in the canonical layer                                                                          |
| 18  | Prose / comparison model references                                                | 189 lines / 59 files                                                                                                                                                                                                                                                                                                | **189 — deliberately preserved**                                                                  |
| 19  | Bead-ID false positives in model-id scans                                          | 10 (`claude-2rb6`, `claude-22cg`, `claude-2o2l`)                                                                                                                                                                                                                                                                    | protected by exclusion list + regression test                                                     |
| 20  | `docs.anthropic.com` occurrences                                                   | 505 across 172 files — **253 (50.1%) in generated artifacts**                                                                                                                                                                                                                                                       | true surface ~252 / ~115 files                                                                    |
| 21  | Retired legacy public domain                                                       | **356 case-insensitive occurrences across 125 tracked files** at `3543d5d167bd4e8d27666c8893080bca3bd72950`: 292 actionable (260 first-party + 32 generated) and 64 retained (4 frozen document/manifest + 60 point-in-time export + 0 provenance mirrors)                                                          | 0 actionable; the 64 retained occurrences remain byte-identical and enumerated                    |
| 22  | Tracked generated artifacts with no drift gate **[RV]**                            | **6** (`skills-index`, `skills-catalog`, `unified-search-index`, `catalog`, `readme-sections`, `jrig-data` — all still tracked under `marketplace/src/data/`)                                                                                                                                                       | 0 — untracked, or regenerate-and-diff                                                             |
| 23  | Worst generated-artifact staleness                                                 | `skills-catalog.json` `generatedAt` 2026-06-02 vs a catalog entry added 2026-07-13 with **0** index entries                                                                                                                                                                                                         | 0 commits of drift                                                                                |
| 24  | Published answers to "how many skills"                                             | **5** (3,179 / 3,678 / 3,051 / 3,008 / 1,915)                                                                                                                                                                                                                                                                       | 1 resolver, 5 **named cohorts**, every number labeled                                             |
| 25  | README metric writers                                                              | **2**, disagreeing (471/3,179/347 gated vs 448/3,008/311 ungated, sourced from a stale index, documenting a workflow file that does not exist)                                                                                                                                                                      | 1                                                                                                 |
| 26  | Public stats past a (nonexistent) freshness bound                                  | 3 of 3 (11 d, 15 d, 15 d) rendered as current                                                                                                                                                                                                                                                                       | 0 rendered as current                                                                             |
| 27  | ⚠ `sources.yaml` vs `sources.lock.json` keys **[RV]**                              | **64 vs 63** — `uizze` has no directory, no catalog entry, no lock entry                                                                                                                                                                                                                                            | equal, asserted                                                                                   |
| 28  | Mirrors shipping license text                                                      | 30 of 63 (33 missing `LICENSE`/`COPYING`)                                                                                                                                                                                                                                                                           | 63 of 63, fail-closed sync                                                                        |
| 29  | Mirror SKILL.md contradicting upstream license                                     | 9 contradict · 23 have none · 1 AGPL-3.0 subtree under a root MIT                                                                                                                                                                                                                                                   | 0 contradictions                                                                                  |
| 30  | ⚠ Provenance-marked mirror packages **[RV]**                                       | **63 repository package mirrors, all `private`; 58 are live IS-scoped npm packages and 5 are non-scoped**. Current classification: 52 third-party excluding Skyvern, 1 AGPL defect, 5 first-party/ambiguous; 53 clearly third-party including Skyvern.                                                              | 0 publishable                                                                                     |
| 31  | Independent boundaries preventing mirror publication                               | **0** (relies on `auto-bump-on-pr.yml:227` declining to bump — defense by side-effect)                                                                                                                                                                                                                              | 2                                                                                                 |
| 32  | Gate dependencies on the publish path                                              | **0** (`on: push`, `enforce_admins:false`)                                                                                                                                                                                                                                                                          | 3 (workflow_run + head-SHA preflight + protected Environment)                                     |
| 33  | Release-path failures swallowed as `⚠`                                             | 3 (tag create, tag push, `gh release create`)                                                                                                                                                                                                                                                                       | 0                                                                                                 |
| 34  | `release.yml` `skip_tests` bypass                                                  | present                                                                                                                                                                                                                                                                                                             | **removed**, not bounded                                                                          |
| 35  | SBOMs                                                                              | **0**                                                                                                                                                                                                                                                                                                               | ≥15 (`plugins/mcp/**` first)                                                                      |
| 36  | Third-party actions on mutable tags in privileged workflows                        | 6 distinct, 13+ uses                                                                                                                                                                                                                                                                                                | 0                                                                                                 |
| 37  | Dependabot config                                                                  | absent                                                                                                                                                                                                                                                                                                              | present, grouped                                                                                  |
| 38  | Kernel / eval-CLI / harness pins                                                   | `core 0.9.0` (published **0.10.0**, ~35 d past a 7-day bound, printing `❌ VIOLATION` and exiting 0 daily) · `jrig-cli 0.1.2` (published 0.2.0) · `audit-harness **^1.3.1**` while implementing a **required** check                                                                                                | `0.10.0` / `0.2.0` / `1.3.1` exact; ordering blocking; staleness alert-routed                     |
| 39  | Kernel shadow report                                                               | generated **2026-06-27** against kernel **0.4.1** (two pins behind); `existing-PASS/kernel-FAIL: **0**`, `existing-FAIL/kernel-PASS: **1948**`                                                                                                                                                                      | regenerated at current pin, **both** v1 and v2 lanes, `existing-PASS/kernel-FAIL` as the headline |
| 40  | `--marketplace` runs that block a merge **[RV]**                                   | **0** (3 occurrences: 2 advisory + 1 `\|\| true`)                                                                                                                                                                                                                                                                   | 1 (ratchet job inside `validate-plugins.yml`)                                                     |
| 41  | `ci-required.needs` — documented vs actual **[RV]**                                | **21 prose-documented / 21 named / 21 actual**; the count is corrected, but row 41 still reports `documented_needs: null` because no machine-readable asserted list exists                                                                                                                                          | equal, machine-asserted                                                                           |
| 42  | Documented schema version **[RV]**                                                 | 3.15.2 (CLAUDE.md, 6767-b) vs `SCHEMA_VERSION = "3.16.1"`                                                                                                                                                                                                                                                           | equal, asserted                                                                                   |
| 43  | Docs self-declaring AUTHORITATIVE/CANONICAL vs linked from `STANDARDS.md` **[RV]** | **8 declared / 1 linked**; 4 of them assert the false CSV rule                                                                                                                                                                                                                                                      | 3 declared, 3 linked, gate-enforced                                                               |
| 44  | `000-INDEX.md` entries vs tracked docs **[RV]**                                    | 166 vs 168                                                                                                                                                                                                                                                                                                          | equal, generated + gated                                                                          |
| 45  | Prose-anchor checker in CI **[RV]**                                                | **0 workflows**, while `parse-prose-anchors.py:117` hard-defaults to `6767-h`                                                                                                                                                                                                                                       | 1, fixture-tested                                                                                 |
| 46  | Tracked files invisible to gitleaks                                                | **14,041 / 22,962 = 61.1%** (every SKILL.md, README, `references/*.md`, `marketplace/dist/**`)                                                                                                                                                                                                                      | 0 blanket file-type allowlists                                                                    |
| 47  | Blocking PR scan for _unverifiable_ secrets                                        | 0 (trufflehog is schedule-only, non-blocking, `--only-verified`)                                                                                                                                                                                                                                                    | 1, diff-scoped, in `ci-required`                                                                  |
| 48  | Supply-chain scan coverage of `push: main`                                         | none (`validate-plugins.yml:1208` is PR-only)                                                                                                                                                                                                                                                                       | full, `--changed-only`                                                                            |
| 49  | MCP plugins with a declared destructive policy / refusal test                      | **0 / 14**                                                                                                                                                                                                                                                                                                          | 14 / 14 declared; every `refuse` claim backed or withdrawn                                        |
| 50  | Unbounded correctness swallows                                                     | ≥4 (`validate-plugins.yml:98`, `:658`, `promote-curated.yml:90-91`)                                                                                                                                                                                                                                                 | 0 unbounded                                                                                       |
| 51  | Safety claims mapped to a named enforcement boundary                               | **0**                                                                                                                                                                                                                                                                                                               | 100%, per-harness                                                                                 |
| 52  | Inventory header vs rows                                                           | **every run disagrees**: 11→3069/3678 (+609) · 10→3069/3678 · 9→3074/3702 · 8→3074/3681 · 7→2987/3713 · **6→3000/19** (would pass today's gate)                                                                                                                                                                     | delta 0, blocking                                                                                 |
| 53  | Tracked export lag                                                                 | exports at run **10**; local DB at run **11**                                                                                                                                                                                                                                                                       | 0 runs, gated                                                                                     |
| 54  | `forge_proofs`                                                                     | **3 rows, 1 plugin** (`databricks-pack`), `baseline_delta` **NULL on 3/3**, identical `verified_at` (batch transcription), `run_id ∈ {2,4,5}` colliding with `discovery_runs.id` max 11, no FK                                                                                                                      | classed, hashed, FK-separated                                                                     |
| 55  | Retained primary eval artifacts                                                    | **0**                                                                                                                                                                                                                                                                                                               | 100% of E2/E3                                                                                     |
| 56  | Public `verified: true` claims with backing **[RV]**                               | 1 claim / 0 backing (`marketplace/src/data/jrig-data.json`, **171 bytes**, no `.astro` page imports it)                                                                                                                                                                                                             | 0 unbacked                                                                                        |
| 57  | `eval-spec.yaml` source adoption **[RV]**                                          | **14 of 3,179 = 0.44%** (26 tracked, incl. 12 curated copies)                                                                                                                                                                                                                                                       | published per run; required at T3                                                                 |
| 58  | Freshie test shape                                                                 | unit only (`tests/test_dolt_sync.py`, 42 functions)                                                                                                                                                                                                                                                                 | ≥1 hermetic end-to-end cycle vs scratch DB                                                        |
| 59  | Single-writer enforcement on Dolt                                                  | prose rule only                                                                                                                                                                                                                                                                                                     | mechanical refusal                                                                                |
| 60  | Artifacts meeting G1–G10 ∧ E1–E6                                                   | **0**                                                                                                                                                                                                                                                                                                               | a named, signed, defensible cohort ≥1                                                             |
| 61  | Open GitHub issues labeled `epic`                                                  | **0 of 11** (171 open beads → outsiders see ~6% of live work)                                                                                                                                                                                                                                                       | every open epic cluster projected, never a gate                                                   |
| 62  | Open launch-blocking legal/provenance items                                        | **3**, none with a recorded disposition                                                                                                                                                                                                                                                                             | 0 open, each owner-signed                                                                         |

### 3.1 Re-measurement of the disputed compliance figures — the correction, with its own proof

Ratification correction 3. Three figures carried into earlier drafts were re-measured from a clean tree at the ratification HEAD; two were wrong. Rows marked **[RM]** above were produced by this run. **The correction is stated with the command that produced it so the reader never has to trust it.**

**HEAD:** `478aaf17731714fed9b1779284de6a5b3729ef6e` (`origin/main`) · **measured:** 2026-08-14. Measurement inputs match `origin/main`; the documentation-only branch adds no corpus, validator, or package changes.

```bash
git rev-parse origin/main                                   # 478aaf17731714fed9b1779284de6a5b3729ef6e
python3 scripts/validate-skills-schema.py --marketplace --skills-only --json | jq -c 'map(select(.path?)) | {skill_files:length, error_files:(map(select((.errors // 0)>0))|length), error_total:(map(.errors // 0)|add), ab_files:(map(select((.grade=="A" or .grade=="B") and ((.errors // 0)>0)))|length), a_failing:(map(select(.grade=="A" and ((.errors // 0)>0)))|length), b_failing:(map(select(.grade=="B" and ((.errors // 0)>0)))|length), a_error_total:(map(select(.grade=="A" and ((.errors // 0)>0))|(.errors // 0))|add), ab_error_total:(map(select((.grade=="A" or .grade=="B") and ((.errors // 0)>0))|(.errors // 0))|add)}'
python3 scripts/validate-skills-schema.py --marketplace      # terminal headline
python3 scripts/validate-skills-schema.py --agents-only      # agent lane
```

`--json` emits one row per SKILL.md (`path, score, grade, errors, warnings`) plus one trailing non-row `kernel_shadow` record, which is excluded from all arithmetic below.

**Cohorts, defined explicitly, then counted.**

| Cohort (explicit definition)                         |     Count |
| ---------------------------------------------------- | --------: |
| Graded artifacts = SKILL.md rows emitted by `--json` | **3,679** |
| A-graded                                             |     1,596 |
| B-graded                                             |       986 |
| A/B total                                            |     2,582 |
| **A/B artifacts with ≥1 ERROR** ("failing the gate") |   **962** |
| — of which A-graded                                  |   **132** |
| — of which B-graded                                  |       830 |
| **Errors carried by the 132 A-graded failures**      |   **219** |
| Errors carried by the 830 B-graded failures          |     1,936 |
| Errors carried by all 962 A/B failures               |     2,155 |

**Verdict on each disputed figure.**

| Figure                             | Status                           | Correct value |
| ---------------------------------- | -------------------------------- | ------------: |
| Prior headline A/B failing         | **REFUTED (not reproducible)**   |       **962** |
| 132 A-graded failing               | **CONFIRMED**                    |           132 |
| Prior headline errors on those 132 | **REFUTED (no measured cohort)** |       **219** |

**The prior error headline has no measured source.** Every near-miss was computed and then _excluded rather than substituted_: warnings on the A-graded failures = 1,101; errors + warnings on them = 1,320; errors on all A/B failures = 2,155; whole-corpus SKILL.md errors = 7,433. A number with no derivable cohort is deleted, not rounded to the nearest plausible neighbor.

**Three totals that count DIFFERENT things. They are named separately and must never be merged into one headline.**

| Measurement                                 | Scope                             |     Value |
| ------------------------------------------- | --------------------------------- | --------: |
| Per-row error sum (`--marketplace --json`)  | 3,679 SKILL.md only               | **7,433** |
| Agent lane (`--agents-only`, standard tier) | 353 agent files                   |   **253** |
| Terminal headline (`--marketplace`)         | SKILL.md + agents + `plugin.json` | **7,687** |

7,433 + 253 = 7,686; the headline is 7,687. **The residual 1 is not attributed here.** `--agents-only` grades at _standard_ tier while the marketplace run grades the same agents at _marketplace_ tier, and 621 `plugin.json` files are also scanned. Writing "7,687 = SKILL errors + agent errors" would be false precision, so three distinct measurements over three distinct cohorts are reported as three numbers.

**One open discrepancy, deliberately not silently rewritten.** This run counts **3,679** graded SKILL.md rows; § 8 and Epic 8 still cite **3,678** from an earlier scan. Both are recorded; neither is edited to match the other. Reconciling them is precisely the job of Epic 1 bead 1.0 (the single measurement harness), and doing it by hand here would re-create the defect this section exists to correct.

---

## 4. TARGET ARCHITECTURE

The authority flow is: **canonical portable skill → validated (GENERATED) harness adapters → generated plugin/package distributions → marketplace + website projections.** Three corrections to that spine are forced by the evidence and are binding (see doc 728 § 3b for the primary-source basis):

1. **Adapters are GENERATED and drift-gated, and they are siblings of distributions, not a stage between canon and distribution.** _Validated_ implies hand-authored-then-checked; every hand-authored adapter layer in the 12-repo benchmark drifted, one of them so far that a published F1 score attaches to a code path most users never take.
2. **A class the flow omits: MIRRORS.** Mirrors are neither canonical nor generated — they are _ingested_. This repo has 63. A mirror may be distributed but may never enter the canonical lane, may never be authored against, and must carry upstream identity through every downstream projection.
3. **The canonical artifact is frontmatter PLUS a closed-schema machine sidecar.** Without that split the canonical artifact accretes operational metadata until the description-injection budget — the one thing that decides whether a skill fires — is crowded out.

```
                          ┌──────────────────────────────────────────────┐
                          │  @intentsolutions/core  (KERNEL)             │
                          │  OWNS: the machine authoring contract        │
                          │    schemas/authoring/v1 (byte-frozen)        │
                          │    schemas/authoring/v2 (strict fork)        │
                          │    + PROPOSED: skill-contract, capability,   │
                          │                eval-spec schemas             │
                          │  NEVER OWNS: the corpus, CI policy, which    │
                          │              tier is required                │
                          └───────────────┬──────────────────────────────┘
                                          │ exact pin, READ-ONLY
                                          │ ADVISORY shadow lane only
                                          ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│  THIS REPO — CCPI / Tons of Skills                                                 │
│  OWNS: the corpus · the catalog SoT · the prose-spec validator (AUTHORITATIVE) ·    │
│        the CI merge gate · the public marketplace · npm publish of first-party      │
│  NEVER OWNS: the authoring schema · eval verdicts · ops/deploy policy · grade       │
│              history                                                               │
│                                                                                    │
│   ┌────────────────── CANONICAL LAYER (harness-free, authored) ────────────────┐   │
│   │  SKILL.md frontmatter  — the IS 8 + already-specified optionals ONLY        │   │
│   │  skill-card.yaml       — the machine contract (T2+): capabilities,          │   │
│   │                          constraints, requires.services, adapters[],        │   │
│   │                          unsupported[], model_class, side_effects,          │   │
│   │                          lifecycle, provenance                              │   │
│   │  BODY: ## Overview/Prerequisites/Instructions/Output/Error Handling/         │   │
│   │        Examples/Resources      references/  scripts/  assets/               │   │
│   │  eval-spec.yaml (T3+)  — already harness-neutral                            │   │
│   │  .source.json          — mirrors ONLY; presence is what determines           │   │
│   │                          attribution (never a heuristic)                     │   │
│   │  RULE: deleting every adapter must leave a complete, gradeable,             │   │
│   │        evaluable skill.                                                     │   │
│   └───────────────┬───────────────┬───────────────┬───────────────┬───────────┘   │
│                   │ GENERATED     │ GENERATED     │ GENERATED     │ GENERATED     │
│      ┌────────────▼───┐ ┌─────────▼─────┐ ┌───────▼──────┐ ┌──────▼────────┐      │
│      │ adapter:       │ │ adapter:      │ │ adapter:     │ │ adapter:      │      │
│      │ claude-code    │ │ codex         │ │ gemini-cli   │ │ …             │      │
│      │ capability_map │ │ capability_map│ │ unsupported[]│ │               │      │
│      │ runtime_binding│ │ unsupported[] │ │  denylist →  │ │               │      │
│      │ invocation     │ │  denylist →   │ │  FAIL-CLOSED │ │               │      │
│      │ execution_pol. │ │  FAIL-CLOSED  │ │              │ │               │      │
│      │ service_wiring │ │               │ │              │ │               │      │
│      └────────────────┘ └───────────────┘ └──────────────┘ └───────────────┘      │
│      THIN ONLY. No body, no references, no eval, no license, no 2nd version.       │
│                                                                                    │
│   INGESTED (never canonical): 63 mirrors — quarantined, provenance-bound,          │
│   never promotable to canonical, never re-badged as Intent Solutions work.          │
└───────┬───────────────────────┬────────────────────────┬──────────────────────────┘
        │ produces gate results │ consumes verdicts      │ cites (read-only)
        ▼                       ▼                        ▼
┌────────────────┐   ┌──────────────────────┐   ┌─────────────────────────┐
│ FRESHIE / DOLT │   │ INTENT EVAL LAB      │   │ INTENT OS               │
│ OWNS: inventory│   │ + @intentsolutions/  │   │ OWNS: host/deploy/ops   │
│  + grade       │   │   jrig-cli           │   │  runbooks, decision log │
│  history       │   │ OWNS: eval execution,│   │ NEVER OWNS: any repo's  │
│  SQLite runtime│   │  provider creds,     │   │  code, catalog, CI, or  │
│  Dolt = SoR    │   │  model-run artifacts,│   │  required-set           │
│  grades.csv =  │   │  the 7-layer method  │   │ PROJECTS — never governs│
│  tracked export│   │ NEVER OWNS: the merge│   │                         │
│ NEVER OWNS: the│   │  gate, the catalog,  │   │ Conflict rule:          │
│  merge gate or │   │  any write to it     │   │  intent-os wins on host │
│  skill content │   │                      │   │  facts; this repo wins  │
│ LOCAL is sole  │   │ j-rig NEVER given    │   │  on catalog/validator   │
│  writer; export│   │  --db inventory.sqlite│  │  facts. Neither edits   │
│  is ONE-WAY    │   │  (it writes run      │   │  the other's SoT.       │
└────────────────┘   │   tables into it)    │   └─────────────────────────┘
                     └──────────┬───────────┘
                                ▼
                    ┌──────────────────────────┐
                    │ BEADS / DOLT             │
                    │ SOLE task authority.     │
                    │ GitHub Issues + Plane    │
                    │ are one-way PROJECTIONS. │
                    │ A projection NEVER gates.│
                    └──────────────────────────┘
```

### Boundary invariants — stated so they cannot erode

1. **The kernel is advisory here until all six DR-049 conditions are met.** `scripts/validate-skills-schema.py` is the authority. **The pin axis and the authority axis are independent** — a bump to `core@0.10.0` is a routine coupling update and is never a flip. The flip target, when it comes, is `authoring/v2`, not `v1`.
2. **Eval evidence is produced by the Lab / j-rig and only _consumed_ here.** This repo may render a verdict; it may never mint one. A badge asserting an eval this repo cannot show a signed bundle for is a false quality claim.
3. **Exactly one writer per fact class, everywhere** — the same shape as beads↔GitHub. Where two systems disagree, the owner in the diagram wins and the other is corrected.
4. **Implementations are never normative.** When a document, a script, and a schema disagree, surface the discrepancy and resolve it _at the authority_; existing implementation behavior is evidence of what is, never of what ought to be. (Adopted verbatim in spirit from `agentskills/agentskills` `AGENTS.md` — the single best governance artifact in the 12-repo benchmark; see doc 728.)
5. **No new authority is created.** The repo's three named historical failures — mirror mis-attribution, one-fact-two-claimants ×2, ~200 silently gitignored docs — are all authority-multiplication failures, not capability gaps. New directories, new schema forks, and second doc roots are refused by default.

---

## 5. CANONICAL MODEL-AGNOSTIC CONTRACT

> **Amendment — 2026-08-26, owner-authorized.** The compatibility constraints in
> §§ 5.6, 6A.3, and 13 remain binding for `plugins/`, `skills/`, package identities,
> and legacy customer entry points, but they no longer prohibit a GitHub repository
> rename. The canonical repository identity is **Tons of Skills Marketplace** at
> `jeremylongshore/tons-of-skills-marketplace`. The historical repository URL and
> `jeremylongshore/claude-code-plugins` install slug remain supported compatibility
> aliases until the migration receipt records their retirement criteria. This
> amendment also authorizes full Beads graph instantiation for this blueprint; Beads
> still enforces dependencies, evidence, and closure gates. Detailed identity,
> harness, and customer-install contracts are recorded in 803–805.

**Denominator reconciliation — 2026-08-30.** The original ratified plan remains a historical
**10-epic / 141-task / 151-record** baseline. The approved Epic 11 extension adds one epic and twelve
original task requirements. Execution then discovered eight legitimate implementation
prerequisites across Epics 5–11, including E11.13. The live canonical programme denominator is
therefore **11 epics / 161 implementation requirements / 172 records**. This is an acceptance
denominator, not a raw `bd children` count: dispositioned duplicate shells do not add work, a bundled
implementation bead may satisfy more than one numbered requirement without shrinking the plan,
and administrative AAR/closure/reconciliation records do not silently create implementation
requirements.

### 5.1 The four homes, and the one rule

**Rule: every fact has exactly one writer.** A field's home is determined by _who writes it and how often it changes_, not by convenience. **The frontmatter is NOT the machine contract and must not be overloaded.**

| Home                                                    | Who writes                    | Cadence              | Read by                                                              | Size discipline                                                                                                                                                                                                                                                                      |
| ------------------------------------------------------- | ----------------------------- | -------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **A · `SKILL.md` frontmatter**                          | skill author                  | per content change   | **the model**, at every catalog load                                 | Hard cap: the IS 8 (`name`, `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`, `tags`) + `disallowed-tools` + the three already-specified optional families (visibility gating 3.5.0, self-declared config 3.6.0). **Nothing new is ever added here.** |
| **B · `skill-card.yaml`** (T2+)                         | skill author / maintainer     | per behavior change  | validators, adapter generators, marketplace filters, security review | closed schema, `additionalProperties: false`                                                                                                                                                                                                                                         |
| **C · registry / catalog entry**                        | catalog maintainer            | per catalog decision | catalog builds, install surfaces, the site                           | closed schema                                                                                                                                                                                                                                                                        |
| **D · evidence store (Dolt: Freshie + `forge_proofs`)** | CI / Intent Eval Lab **only** | per run              | badges, gates, history queries                                       | not a file                                                                                                                                                                                                                                                                           |

The frontmatter budget is the binding constraint and the reason for the split: **any governance field the model does not need in order to decide whether to fire must not be in frontmatter.** The counter-example is measured — a large public catalog that skipped the split ended with 30 ad-hoc `metadata:` sub-keys, `version` on 33% of skills and `allowed-tools` on 24%.

**This split is additive and explicitly does NOT touch `ALWAYS_REQUIRED`.** Reducing the IS 8 to an upstream five- or six-field floor is **REJECTED** — that is the 2026-04-28 realign-to-Anthropic's-floor debacle wearing a new vendor's badge (`SCHEMA_CHANGELOG.md` NON-NEGOTIABLES #1 and #3).

### 5.2 `skill-card.yaml` — the machine contract

`schemas/canonical/v0/skill-contract.schema.json`, `additionalProperties: false` at top level, `Status: DRAFT`, kernel named as the intended eventual owner (Epic 3 bead: propose to `@intentsolutions/core`; this repo must never become its own schema authority).

```yaml
id: plane # stable identity; NEVER renamed (install slugs are API)
version: 0.3.0 # ONE version; display surfaces project from it
intent: > # what it is for. No trigger syntax, no harness verbs.
  Synthesize project-tracker data into observations about team behavior.

inputs:
  - { name: project, type: string, required: true }
outputs:
  - { name: report, type: markdown, schema: ./schemas/report.json }

capabilities: # ABSTRACT. Never a harness tool name.
  - filesystem.read
  - filesystem.write: { paths: ['./out/**'] }
  - shell.exec: { commands: [jq, date] }
  - network.http: { hosts: [api.plane.so] }
  - user.prompt

constraints:
  forbid: [filesystem.write.dotenv, shell.exec.rm, network.exfil]
  bounded: { max_steps: 40 }
  risk_tier: medium # low | medium | high

side_effects: # declared, machine-readable, rendered into the catalog
  writes: [{ path: './out/**', approx_mb_max: 5 }]
  network: [api.plane.so]
  env: [PLANE_API_KEY]

requires:
  services:
    - { kind: mcp, name: plane, env: [PLANE_API_KEY] }

model_class: balanced # reasoning-high | balanced | fast. NEVER a vendor literal.

evaluation: ./eval-spec.yaml # REQUIRED at T3+

not_for: [plane-admin-migration] # sibling that should win; anti-trigger routing

lifecycle: active # active | deprecated | sunset
superseded_by: null
sunset_on: null

provenance:
  author: 'Name <email>'
  license: MIT # SPDX only. "SEE LICENSE IN LICENSE" is invalid.
  spdx: MIT
  source: null # upstream repo URL when mirrored
  source_commit: null # RESOLVED SHA when mirrored — a branch name is not a pin
  upstream_license: null # MUST equal .source.json when mirrored

adapters:
  [claude-code, codex] # enum from the committed adapter registry.
  # Listing a harness with no adapter artifact FAILS CI.
unsupported:
  - capability: user.prompt
    adapter: codex
    reason: 'no interactive-confirmation primitive'
    degradation: fail-closed # fail-closed (DEFAULT) | skip | prompt-in-band

compatibility: <GENERATED> # projection of adapters[]. Never hand-authored.
```

### 5.3 Field disposition — where each of today's fields goes

| Today's field                                                                                 | Home                                                                                                       | Reason                                                                                                                                       |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `name` `description` `version` `author` `license` `tags`                                      | **A · frontmatter** (unchanged)                                                                            | identity / legal / intent — no harness in them; the model needs them at load                                                                 |
| `compatibility` (40 free-text values, 2,905 files)                                            | **frontmatter, but GENERATED** from **B**'s `adapters[]` + `requires.services[]` + `unsupported[]`         | prose is unenforceable; a claim must be machine-checkable to be honest                                                                       |
| **`allowed-tools`** (3,138 files)                                                             | **stays in A** (contract-required) **and is DERIVED-CHECKED against B's `capabilities` + the adapter map** | "may read files" is portable; `Bash(jq:*)` is a Claude Code _expression_ of it. The two must agree or CI fails                               |
| **`disallowed-tools`** (26) / agent `disallowedTools` (318)                                   | **A** keeps the field; **B** carries `constraints.forbid`                                                  | the _intent_ is portable; the spelling is not. Where a harness lacks the primitive → `unsupported` + **fail-closed**                         |
| **`model`** (12 skills / 321 agents: sonnet 268, inherit 36, opus 13, haiku 4)                | **adapter only**; **B** carries `model_class`                                                              | substituting another vendor's literal relocates the lock-in rather than removing it                                                          |
| `effort` `maxTurns` `background` `color` `memory` `permissionMode` `initialPrompt`            | **adapter only**                                                                                           | `maxTurns` maps up to `constraints.bounded`; `permissionMode` maps up to `risk_tier`                                                         |
| `argument-hint` `$ARGUMENTS` `user-invocable` `disable-model-invocation`                      | **adapter only**                                                                                           | slash-command UX is a Claude Code concept                                                                                                    |
| `commands/` (379) · `hooks/` (39) · `.mcp.json` (14) · `agents/` (347)                        | **adapter only**                                                                                           | pure harness wiring                                                                                                                          |
| `${CLAUDE_SKILL_DIR}` / `${CLAUDE_PLUGIN_ROOT}`                                               | **adapter only**; canonical uses `${SKILL_DIR}`                                                            | the validator's instinct (mandate the variable over absolute paths, `validate-skills-schema.py:3355`) is right; the token is harness-branded |
| `## Overview / Prerequisites / Instructions / Output / Error Handling / Examples / Resources` | **canonical body**                                                                                         | genuinely portable; keep the heading-equivalent synonym-fairness rule                                                                        |
| `eval-spec.yaml`                                                                              | **canonical**, required at T3+                                                                             | already harness-neutral: `criteria[].{id, description, method, blocker, judge_prompt}`                                                       |
| side effects, upstream pins, cost, gates, lifecycle                                           | **B · `skill-card.yaml`** — new home                                                                       | these are exactly the fields that would otherwise bloat frontmatter                                                                          |
| grade, eval verdict, evidence class, run id                                                   | **D · Dolt** — never a file                                                                                | a grade copied into a file goes stale the moment the next run lands                                                                          |

### 5.4 Four anti-shallowness rules, binding

1. **Classify by role, never by string.** Functional model id → capability tier. Prose / comparison → **keep** (189 lines; deleting accurate content is a truthfulness loss, not a portability gain). Bead ID → **never touch** (the beads prefix here _is_ `claude`).
2. **Declare harness-specific capability rather than fake portability.** `adapters: [claude-code]` rendering as "Claude Code only" is a _stronger_ honest claim than 1,409 identical untested prose strings.
3. **Migration must be falsifiable.** A CI gate fails on reintroduction of any vendor literal into the canonical layer; otherwise drift returns within one generation cycle.
4. **Fail closed on an unresolvable tier or capability.** An adapter with no matching model **errors**. Silent substitution is exactly how "model-agnostic" becomes a claim exceeding its evidence.

### 5.5 Ecosystem conformance projection

The IS canonical frontmatter is a **strict superset** of the open Agent Skills spec and is therefore non-conformant to that spec's reference validator, which errors on unknown top-level keys. Measured: ~490 of 500 sampled IS SKILL.md carry top-level `version:` while only 45 carry any `metadata:` block — i.e. roughly 3,100 IS skills currently fail the ecosystem's own reference validator.

**Resolution: dual-write, not surrender.** A generated _conformance projection_ additionally writes `version`, `author`, and `tags` into the spec-legal `metadata:` string map, so shipped artifacts are spec-legal without touching `ALWAYS_REQUIRED`. Rank 6 (portability) is served without spending rank 4 (SoT integrity).

### 5.6 Frozen compatibility contracts

- **Public install slug `jeremylongshore/claude-code-plugins`** is hardcoded in the CLI, the Hero snippet, and hundreds of READMEs. GitHub's 301 to the canonical repo name is load-bearing. **Any rename is a breaking API change.** It is declared in the registry as `compat.install_slug` with a comment naming it a frozen API, so a future "normalization" PR cannot break it by accident. **This constraint applies to every layout proposal in this blueprint** — no epic renames `plugins/`, `skills/`, or the slug.
- **`plugins/<category>/<plugin>/skills/<name>/`** stays. A flat `skills/<name>/` root is **REJECTED**: the name is already taken by the numbered curriculum dirs plus `.curated` (which skills.sh crawls as an external contract), and flattening 3,179 skills would break the slug, `pluginRoot`, ~470 plugin `package.json`, cowork zip paths, `sources.yaml` mirror targets, and every route in the Astro site.
- **`marketplace/public/downloads/`** stays gitignored, wiped and rebuilt per build, drift-gated. A tracked `distributions/` directory is **REJECTED** — it would re-create the two-claimant failure the repo already paid for.
- **An in-repo `schemas/` tree is permitted only as an interim**, under `schemas/canonical/v0/` with a mandatory `UPSTREAM-PENDING: <kernel-issue>` header and a bead to land it in the kernel. New governance schemas are authored in the kernel and consumed here.

---

## 6. HARNESS ADAPTER STANDARD

**The repo already has an adapter and it is the anti-pattern.** `plugins/testing/kobiton-automate/.codex/` is 27 files byte-identical to `skills/` (three `SKILL.md` pairs verified IDENTICAL). Freshie grades both copies — 10 compliance rows for a 5-skill plugin — and the same 5 malformed `allowed-tools` values are counted twice. **A fork is not an adapter.**

**An adapter is GENERATED. Hand-authored adapter content is prohibited.**

**An adapter MAY contain, and nothing else:**

| Section            | Contents                                                                                                      |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| `capability_map`   | canonical capability → this harness's tokens (`shell.exec{jq} → Bash(jq:*)`; `user.prompt → AskUserQuestion`) |
| `runtime_bindings` | path/arg variables (`${SKILL_DIR} → ${CLAUDE_SKILL_DIR}`)                                                     |
| `invocation`       | how the harness surfaces it (slash command + `argument-hint`, auto-invoke, subagent)                          |
| `execution_policy` | `model`, `effort`, `maxTurns`, `background`, `permissionMode`, `color`                                        |
| `service_wiring`   | `.mcp.json` / hooks in that harness's schema                                                                  |
| `unsupported[]`    | capabilities this harness cannot honor, with reason + degradation                                             |

**An adapter MUST NEVER contain:** skill body or instructions · `references/` · `scripts/` · the evaluation contract · license or attribution · a second version number · any behavioral divergence.

**Gate — `scripts/check-adapter-thinness.mjs`, a job inside `validate-plugins.yml`, listed in `ci-required.needs` — fails when:** any adapter file is byte-identical to a canonical file · an adapter contains `SKILL.md`, `references/`, `scripts/`, `eval-spec.yaml`, a license, or a version · an adapter declares a capability absent from the canonical `capabilities`.

**Symlink farms are REJECTED at plural scale** (at most one directory-level symlink). Symlinks break on checkouts without symlink support, and at least one harness silently drops them during install.

### Harness differences that actually matter

|              | Claude Code                                       | Codex CLI                                | Gemini CLI                                      | Other                |
| ------------ | ------------------------------------------------- | ---------------------------------------- | ----------------------------------------------- | -------------------- |
| Discovery    | SKILL.md frontmatter                              | `.codex/skills/`                         | `GEMINI.md` + extensions                        | plugin-support model |
| Tool grant   | `allowed-tools` allowlist + `Bash(cmd:*)` scoping | different namespace, no `Bash()` scoping | per-tool confirmation, no frontmatter allowlist | plugin-mediated      |
| **Denylist** | `disallowed-tools` / `disallowedTools`            | **none** → `unsupported`                 | **none** → `unsupported`                        | n/a                  |
| Subagents    | `agents/*.md`, `model`, `background`, `maxTurns`  | none equivalent                          | none equivalent                                 | n/a                  |
| MCP naming   | `mcp__server__tool` (72 files depend)             | differs                                  | differs                                         | differs              |
| Runtime var  | `${CLAUDE_SKILL_DIR}`                             | differs                                  | differs                                         | differs              |

**The denylist row is load-bearing.** On a harness with no denylist primitive, a skill whose safety posture _depends_ on that denylist must **fail closed**, not run unprotected. Rank 5 (enforce at machine boundaries) beats rank 6 (portability): **portability is never purchased with a silently dropped safety control.**

---

## 6A. ROOT README AND REPOSITORY LANDING CONTRACT

Ratification correction 1. `728 § 4 C6` and `729 § 6` both **REJECT "README as catalog surface"** and neither names what replaces it. A rejection with no replacement is not a decision — it is a hole, and at 470 plugins the hole is the first thing every visitor, contributor, and partner walks into. **This section is the replacement, and it owns the fact class "root README / repository landing experience" in § 11.**

**The reframe, stated once:** the README stops being a _catalog_ (an enumeration that drifts the moment the corpus moves) and becomes a **governed landing contract** — a small, generated, gate-checked surface whose job is to route a reader to the right place in under a minute, and whose every number carries the cohort and command that produced it. The catalog itself lives where a catalog belongs: `marketplace.extended.json` (source of truth), the website (browse/search), `skills-index.json` (machine), `skills.sh.json` + `llms.txt` (external discovery). **The README points at those. It never becomes one.**

### 6A.1 What the landing surface must say, and what it must never do

**Must say:**

1. **Tons of Skills is a model-agnostic agent-skills platform.** Not "a Claude Code plugin repo." The canonical layer is harness-free by construction (§ 5); Claude Code is the **first and best-supported** harness, not the definition of the product. The one-line identity is a platform statement with a harness list beneath it, never a vendor statement with an asterisk.
2. **Scale is the strength, and it is stated in the open.** ~470 plugins · ~3,179 skills · ~347 agents is the largest curated agent-skills corpus in the ecosystem, and hiding or shrinking it to look tidy would trade the single most defensible fact about the platform for cosmetics. **The answer to scale is navigation and honest labeling, never reduction.** Every published count appears with its cohort name and the command that produces it (§ 3.1; Epic 1 beads 1.5/1.6) — an unlabeled count is what produced five contradictory answers to "how many skills."
3. **Five orthogonal ways in, because there are five real questions.** By **harness/model** ("I'm on Codex — what works for me?"), by **application/job** ("I need to review a PR"), by **skill category**, by **plugin**, and by **certification tier** (§ 2's computed tiers — T0…T4 / CERTIFIED / PENDING). Each is a link into a generated surface, not an inline list.
4. **Four artifact classes, distinguished on sight and never blurred.** This is a rank-3 (truthful provenance) requirement, not a UX nicety:

   | Class                   | What it is                                           | How the reader can tell                                                                             |
   | ----------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
   | **Canonical skill**     | First-party, harness-free, the source of truth       | No `.source.json`; carries `skill-card.yaml`; certification tier rendered                           |
   | **Generated adapter**   | A thin, machine-produced harness projection (§ 6)    | Lives under a generated path, carries a "generated — do not edit" header, has no body or references |
   | **First-party package** | An IS-authored distribution (npm, cowork zip)        | `@intentsolutions*` scope, IS-authored, license is ours                                             |
   | **Upstream mirror**     | Somebody else's work we host under mirror-by-default | `.source.json` present; upstream author + license + resolved SHA rendered inline (`728 § 4 B3`)     |

5. **Harness support is stated by adapter, not by adjective.** Claude Code, Codex, Gemini CLI, and any future harness appear only where a **declared, generated adapter** exists, with its `unsupported[]` degradations visible. **A copied skill tree is not an adapter and must never be presented as one** — the repo's only "adapter" today is a 27-file byte-identical fork (§ 6), and the README is exactly where that misrepresentation would go public. `1,454` prose portability claims with zero adapter artifacts are withdrawn, not restated.
6. **tonsofskills.com is the live property.** The retired legacy domain is replaced on this surface (Epic 1 bead 1.13) — **and nowhere inside the frozen `6767-*` set, a registered point-in-time export, or any mirror-owned file**, where the historical record must stay byte-identical.

**Must never do:** per-skill rows (the drift engine every benchmarked repo fell into — `728 § 4 C6`) · a hand-maintained count · a second metrics writer · a claim with no cohort · a harness name with no adapter · a badge with no retained, hash-matched artifact (§ 2 criterion E3) · a rename of anything in § 6A.3.

### 6A.2 Proposed information architecture

Ordered by what a first-time reader needs, with a hard budget per block. Everything marked _(generated)_ is written by a generator and drift-gated; everything else is short, hand-authored prose that does not contain numbers.

```
1  Identity            model-agnostic agent-skills platform · one sentence · harness row (adapter-backed only)
2  Install             the frozen public slug, verbatim, first screen — see 6A.3
3  Scale, labeled      (generated) counts + cohort names + the command that produced each
4  Five ways in        (generated links) by harness/model · by application · by category · by plugin · by tier
5  What the classes    canonical · generated adapter · first-party package · upstream mirror (the 6A.1 table)
   mean
6  Certification       what a tier means, what it does NOT mean (the recall_note discipline, 728 § 4 D8),
                       and the live certified/pending split — published even when certified is near zero
7  Contribute          intake standard (700) + external-PR review standard (709) + AI-disclosure
8  Governance          STANDARDS.md · this blueprint · SECURITY.md · LICENSE + NOTICE
9  Provenance          mirror-by-default in one paragraph, linking 694, with upstream credit stated
```

**AUTO-TOC's scope is capped, not extended:** counts and category links only. `generate-readme-toc.mjs` gains a byte budget and a "no per-skill rows" assertion (`728 § 4 C6`).

### 6A.3 Frozen on this surface — a rename here is a breaking API change

- **The public install slug `jeremylongshore/claude-code-plugins` is reproduced verbatim** and is a **frozen compatibility contract** (§ 5.6). It is hardcoded in the CLI, the Hero snippet, and hundreds of READMEs; GitHub's 301 to the canonical repo name is load-bearing. **No README redesign may "normalize" it to the canonical repo name.**
- **`plugins/` and `skills/` keep their meaning and their paths.** `plugins/<category>/<plugin>/skills/<name>/` is the documented layout; root `skills/` remains the curriculum + `.curated` mirror that skills.sh crawls as an external contract. The landing surface **describes** both; it never proposes flattening either.
- **The canonical repo name and the marketplace catalog id are unchanged**: `jeremylongshore/claude-code-plugins-plus-skills` and `claude-code-plugins-plus`.

### 6A.4 Acceptance criteria — measurable, or it did not land

| #   | Criterion                                                                                                                            | Verifier                                                                                            |
| --- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| R1  | Zero per-skill rows in `README.md`                                                                                                   | A gate asserting the AUTO-TOC block emits category/count rows only; planted row ⇒ red run           |
| R2  | Byte budget held (README ≤ 25 KB; AUTO-TOC block ≤ 8 KB)                                                                             | Byte assertion in the same gate; the benchmark's failure mode is a 50,315-byte README               |
| R3  | Exactly **one** metrics writer feeds the README                                                                                      | `resolveCorpus()` is the only producer (Epic 1 beads 1.5/1.9); a second writer fails CI             |
| R4  | Every published number carries a cohort label and a reproducing command                                                              | Regenerate-and-diff, plus a grep asserting no bare integer outside a labeled generated block        |
| R5  | Every harness named on the surface has a declared adapter                                                                            | Cross-check README harness list against the generated `adapters[]` registry; extra name ⇒ red       |
| R6  | The install slug string appears verbatim and unmodified                                                                              | String assertion pinned in a test, with the "frozen API" comment naming why                         |
| R7  | Zero retired-legacy-domain occurrences in `README.md`; frozen `6767-*`, registered point-in-time exports, and mirror files unchanged | Domain lint (Epic 1 bead 1.13) + zero-diff assertions for every retained class                      |
| R8  | Each of the four artifact classes is defined on the surface and machine-derivable                                                    | Class definition maps 1:1 to a computable predicate (`.source.json` presence, scope, tier)          |
| R9  | The five navigation entry points resolve to live generated surfaces (no 404, no hand-maintained list)                                | Link check in CI; every target is a generated artifact with a drift gate                            |
| R10 | The certified/pending split is rendered from the certification report, including when certified is 0                                 | Reads `certification-report.json` (Epic 10); absent file ⇒ renders "not yet certified", never blank |

### 6A.5 The proposed bead that implements and verifies this — **PROPOSED ONLY**

> **Epic 2, bead 2.13 — "Rebuild the root README as a governed landing contract with a per-class navigation map and a byte-budget gate."**
> Type `feature` · P1 · parent: the Epic 2 epic bead.
> **Acceptance:** R1–R10 above, each with the command that proves it and a linked red run for every new assertion; the install-slug string test pinned; zero frozen-file diffs.
> **Rollback:** `git revert` the README + gate commit; the observable is the restored byte count and a green `check-generated-artifacts` run.
> **Prohibited:** renaming the slug, `plugins/`, or `skills/` · editing any file under a `.source.json` ancestor · adding per-skill rows · hand-writing any count · naming a harness that has no generated adapter.
> **Depends on:** Epic 1 beads 1.5/1.6 (the corpus resolver and cohort labels — otherwise R3/R4 cannot be satisfied) and Epic 2 bead 2.3 (the authority-pointer gate). **Consumed by:** Epic 10's launch gate.

**No bead is instantiated by this document.** `2.13` is a document-local handle for the dependency graph, never a bead ID or a bead title (§ 13).

---

## 7. PROVENANCE AND LICENSING POLICY

**P1 — Identity is never borrowed.** No artifact bearing the Intent Solutions name, npm scope, package identity, or maintainer record may contain work Intent Solutions did not author, absent written, recorded, per-source consent. Preserving an `author` field is attribution; it is not permission to publish under our name. _(ranks 2, 3)_

**P2 — License text travels with the bytes, always.** Every mirrored source's `include[]` must carry `LICENSE`/`COPYING`. Any artifact we distribute — git tree, npm tarball, cowork zip, curated index, built site — carries the license text of everything inside it. A copyleft source with no license text in the mirror is a **hard sync failure**, not a warning. _(rank 2, enforced at rank 5)_

**P3 — Copyleft is quarantined by default.** AGPL/GPL/LGPL admitted only under an explicit recorded per-source decision naming the distribution channels, isolating the subtree with its own `LICENSE`, marking it `private: true` for npm, and stating the reciprocity obligation in the catalog entry. Default for a new copyleft source is **REFUSE**. _(ranks 2, 8)_

**P4 — One provenance record, machine-checked.** `.source.json` is the single source of truth for a mirror's upstream, author, and license, and it **must carry a resolved `source_commit` SHA** — today it records a _branch_, which cannot answer "what exactly did we mirror" after the branch moves. `sources.yaml`, the catalog, `plugin.json`, `package.json`, and SKILL.md frontmatter are **projections** and must equal it — asserted inside `ci-required`. Disagreement is a build failure, not a docs task. _(ranks 3, 4)_

**P5 — Provenance is fail-closed.** Unknown, contradictory, or unverifiable provenance ⇒ **QUARANTINE** (frozen mirror, excluded from every publish and index surface) until a human resolves it. Never publish-and-annotate. _(rank 8)_

**P6 — Publication requires consent, per channel.** Consent is per-source, per-channel (git mirror ≠ npm ≠ curated index ≠ cowork zip), recorded as a linked upstream issue/PR in `sources.yaml`, and revocable, with a documented, tested takedown path per channel. **Absence of objection is not consent.** _(ranks 2, 3, 10)_

**P7 — Own work declares its own license.** Every first-party plugin declares `license` in its catalog entry, not only in SKILL.md frontmatter (397 of 471 entries carry none today). The MIT-root vs "Intent Solutions Proprietary" contradiction is resolved once, in writing, and CI enforces the answer. _(ranks 3, 4)_

**P8 — Enforcement claims name their boundary.** Every advertised safety property is labeled with where it is enforced — harness runtime / CI job / MCP server / **prose only** — and against which harnesses. A property enforced only by Claude Code is declared Claude-Code-specific. Unenforced properties may be documented as guidance, **never presented as guarantees**. Declared-and-unverified side effects render as _declared_, never as a badge implying enforcement. _(ranks 3, 5, 6)_

**P9 — Attribution survives every transform.** Any pipeline that copies, indexes, mirrors, zips, or repackages must carry author + license + upstream through — and must self-test that it did. Attribution additionally lives **inside the `description` and a `## Source` body section** for all 63 mirrors, so it survives catalog extraction even when the detection layer fails. The `.curated` republication bug is the canonical failure mode; every new derived surface ships with an equivalent exclusion test. _(ranks 2, 3, 7)_

**P10 — Contributions disclose AI assistance.** A marketplace that is openly AI-authored and runs an external intake funnel states its AI-assistance expectation in `CONTRIBUTING.md` and the PR template. The reviewer's problem — how much scrutiny to apply — is real at 470 plugins, and this costs nothing while foreclosing a predictable reputational attack. _(ranks 2, 3, 11)_

**P11 — Policy is read from the base branch.** Waivers, allowlists, and contributor exceptions resolve against `origin/main`, never the PR head. **A pull request may not allowlist itself.** Waivers carry owner + reason + **expiry**. _(ranks 1, 8)_

---

## 8. LEGACY DISPOSITION DECISION TREE

**Ordered, first-match-wins.** Security and legal gates fire before any quality consideration, so nothing can be certified _around_ an unresolved provenance problem.

```
G0  SECURITY          → QUARANTINE
    [security] shell substitution in a YAML field, or a REFUSE from
    scan-synced-content. NEVER waivable. NEVER certifiable.

G1  LEGAL/PROVENANCE  → QUARANTINE
    Upstream license absent · copyleft without a reviewed redistribution
    position · frontmatter license ≠ .source.json · contradictory authorship.

G2  TRUTHFULNESS      → QUARANTINE
    The artifact misrepresents itself: a declared deliverable absent or
    counterfeit (extension ≠ magic bytes) · body cites files that do not
    exist · description claims a capability allowed-tools cannot perform.

G3  OWNERSHIP         → CERTIFY-UPSTREAM | QUARANTINE
    Any ancestor holds .source.json. We do NOT edit these.
      clean (0 errors, grade ≥ B) → CERTIFY-UPSTREAM (attested as mirrored,
                                    grade disclosed as upstream's, never
                                    re-badged as Intent Solutions)
      otherwise                    → QUARANTINE pending upstream PR or delist
    NEVER → REMEDIATE.

G4  UNSAFE-BY-DESIGN  → DEEP-REMEDIATE
    Unscoped Bash with Write/WebFetch · tier-2 tool-safety · orchestration
    bounds. Human judgment required. Scripts MUST NOT touch these.

G5  STRUCTURAL-ONLY   → AUTO-MIGRATE
    Remaining errors are body-section / frontmatter-field / relative-link.
    Deterministic transform + re-validation. Sections added must be
    substantive; a header-only stub FAILS the stub assertion.

G6  CLEAN + PROVEN    → CERTIFY
    0 errors ∧ G1–G10 ∧ E1–E6 (§ 2, § 10).

G7  CLEAN, NO EVIDENCE→ CERTIFY-PENDING-EVIDENCE
    0 errors, but no reproducible eval. May be listed. May NOT carry a badge.

G8  ARCHIVE
    Superseded but historically load-bearing (decision records, prior
    authorities, retired baselines). Retained read-only, frozen banner,
    forward pointer. NEVER deleted — 6767-h is a live anchor namespace.

G9  DELETE-CANDIDATE
    Proven-disposable AND recoverable. Requires all three:
      (1) a named regenerating command OR git history retains the content,
      (2) a named restore path recorded in the deleting PR,
      (3) zero inbound references.
    Junk is never preserved to inflate the catalog; useful content is
    NEVER deleted to improve a percentage.
```

### Applied — projected buckets over 3,679 graded artifacts

Every count is **re-derived at execution time from the joined ledger, never carried forward** from this table.

| Bucket                   | Count |     % | Note                                                                                                  |
| ------------------------ | ----: | ----: | ----------------------------------------------------------------------------------------------------- |
| CERTIFY (gate-clean + A) | 1,300 | 35.3% | **most land in CERTIFY-PENDING-EVIDENCE on day one** — evidence, not grade, is the binding constraint |
| AUTO-MIGRATE             | 1,110 | 30.2% | A/B with structural-only errors                                                                       |
| AUTO-MIGRATE (bulk-born) |   826 | 22.5% | C-grade, never individually reviewed                                                                  |
| QUARANTINE               |   318 |  8.6% | 312 mirror-with-errors + 6 counterfeit-asset skills                                                   |
| CERTIFY-UPSTREAM         |    65 |  1.8% | clean mirrors, attributed to upstream                                                                 |
| DEEP-REMEDIATE           |    59 |  1.6% | first-party D/F + safety classes                                                                      |

**~88% is mechanically recoverable. The genuinely expensive work is 59 skills + 37 agent files + 318 quarantine decisions ≈ 414 items.** The staleness signal that matters is not calendar age — three bulk commits touched 2,720 / 1,782 / 443 files — it is that **2,331 of 3,179 plugin skills (73%) were born in a bulk generation event and never individually revisited.**

**Deprecation is a first-class disposition, and nobody in the public benchmark has one.** Twelve of twelve reference repositories ship renames as plain commits and consolidations as silent deletes. This platform carries a constraint none of them do — a legacy install slug hardcoded in hundreds of READMEs — so a silent delete is a breaking API change here in a way it is not for them. `lifecycle` / `superseded_by` / `sunset_on` / `migration_note` live in the skill card, and a sunset artifact gets a tombstone route rather than a 404.

---

## 9. EVALUATION AND EVIDENCE STANDARD

**S1 — Four evidence classes. A claim may never cite a class weaker than it asserts.**

| Class                          | Definition                                                                                                                     | Supports               |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------- |
| **E0 Assertion**               | an author states it                                                                                                            | **nothing**            |
| **E1 Deterministic**           | validator / `j-rig check` / harness exit code, reproducible offline from committed inputs                                      | structural conformance |
| **E2 Behavioral-reproducible** | `j-rig eval` with committed `eval-spec.yaml`, pinned CLI + kernel + provider + model, **primary `--json` retained and hashed** | capability claims      |
| **E3 Adversarial**             | E2 + red-team cases + a `baseline_delta` proving the eval discriminates                                                        | safety claims          |

**S2 — Class is carried in-band.** `verified: {class, spec_sha256, artifact_sha256, artifact_uri, tool, kernel, provider, model, recorded_by_identity, at}`. **No class → no badge.** Render surfaces read the class, never a boolean.

**S3 — Retention is a validity condition, not hygiene.** An E2/E3 record whose primary artifact is unretrievable **auto-demotes to E0**. _Applied today, all three `forge_proofs` rows demote and the badge goes dark. That is the correct outcome — the evidence for the badge does not exist._

**S4 — A baseline delta is mandatory for E3.** `passed 11/11` against a spec authored alongside the skill demonstrates the spec is _satisfiable_, not that the skill is good. `baseline_delta` is NULL on 3 of 3 rows, so **no current record can reach E3.**

**S5 — Determinism envelope.** Exact (non-`^`) pins for `jrig-cli` and `core`; committed spec; pinned provider + model + temperature; recorded seed; adapter id. A non-deterministic provider is permitted only for E2 with **n≥3 runs and a recorded variance bound**; a single sample is **E1**.

**S6 — Storage split by role.** Dolt/Freshie holds the **ledger** (verdict, class, hashes, pins, timestamps — small, diffable, append-only, publicly auditable). A separate artifact store holds the **payload** (raw `--json`), addressed by the ledger hash, and never enters the CMDB or the public DoltHub push — that is exactly the leak `gate_export_allowlist()` blocks. _A ledger without retrievable payloads is worthless; a payload store without the ledger's pins is worthless. Neither alone is evidence._

**S7 — No self-approval.** The producing agent may not record its own verdict as final. Ledger writes originate from an **independent CI identity** against a re-executed eval, never a local transcription.

**S8 — Claim ceiling.** Rendered strength = **min** over a plugin's components. One E0 component caps the plugin at E0. Aggregation never raises a class.

**S9 — Namespace separation.** `forge_proofs.run_id` (values 2, 4, 5 — j-rig's counter) is renamed `jrig_run_id`; a separate `discovery_run_id` carries a real FK. Historical rows migrate with `discovery_run_id` NULL — honest: they were never joinable.

**S10 — Discoverability is scored two-sided.** Every `eval-spec.yaml` carries **negative cases**: the skill must fire when relevant _and stay silent when not_. Negatives are near-miss sibling-skill prompts, not unrelated noise. At 3,179 skills, mis-routing is the dominant runtime failure, so sibling-negatives are mandatory at T3.

**S11 — PASS is a per-dimension gate, not an uplift number.** A skill passes when every configured dimension passes for at least one supported harness. Measured improvement is diagnostic evidence and never by itself overrides the gate — otherwise a skill that makes the agent _worse on safety_ passes on a correctness gain.

**S12 — Deterministic graders first; the model only for semantic assertions.** This is already the shape of `j-rig check` (free, offline) vs `j-rig eval` (~$2–5/skill); it becomes explicit policy. **A full behavioral sweep of the corpus is 3,179 × ~$2 ≈ $6.3k** — that number is written down here so nobody proposes "eval everything" without pricing it. Cohorts are stratified samples, approved per cohort.

**S13 — Every emitted score carries a `recall_note`: what this score does NOT prove.** A Freshie **A** means "8 fields present + body sections graded" — **not** "this skill works." The site currently projects the letter without the caveat. `recall_note` is a required field on every grade/eval artifact and renders next to every badge.

**S14 — Publish negative results.** Self-audits that score poorly, negative deltas on flagship examples, and known false-positive classes are published rather than suppressed. This is the cheapest credibility instrument available and the hardest for a competitor to fake.

---

## 10. CI AND RELEASE STANDARD

### 10.1 The four structural rules (do not regress)

1. `validate-plugins.yml` runs on **every** `pull_request` — **never** add a `paths:` filter to it.
2. **Never add a path-filtered workflow's context to the required set.** New blocking checks are _jobs inside_ `validate-plugins.yml` listed in `ci-required.needs`. (The old 10-context set caused the #778/#964 stuck-PR class.)
3. A job in the aggregate's `needs:` may only skip via a _designed_ `if:` — `skipped` counts as PASS, so an undesigned skip silently greens the gate.
4. The five split lint workflows stay retired; `tests/ci/test_path_routing.py` pins this.

**Required contexts remain exactly three:** `ci-required` (20 → 21 jobs) + `gitleaks` + `skill-conform`. **No epic in this program adds a fourth required context.**

**Two universal killers, both already visible in the public benchmark at n=198 and both with direct analogues here:** (a) _a gate that cannot fail_ (`set +e … exit 0`; `continue-on-error` rationalized as "the next cron self-heals") and (b) _a validator that cannot see the whole tree_ (a depth-1 directory read made 5.6% of a corpus structurally invisible — exactly where its three frontmatter-less files were hiding). The defenses are the bounded-swallow rule (§ 10.3) and the corpus-census invariant: **validator-discovered SKILL.md count must equal on-disk count minus _declared_ exclusions.**

### 10.2 The legacy-debt ratchet — `scripts/.marketplace-compliance-baseline.json`

```jsonc
{
  "$comment": "Shrink-only. Entries may ONLY be REMOVED. Regenerate ONLY through the owner-dispatched capture whose immutable artifact is verified by required CI.",
  "schema_version": "3.16.1", // gate FAILS on validator SCHEMA_VERSION drift → forces a conscious re-baseline
  "generated_from": { "sha": "…", "run_id": "…", "captured_at": "…" }, // emitted IN CI, never locally
  "corpus_definition": "resolveCorpus('graded')", // REQUIRED; never defaults silently
  "corpus": { "skill_files": 0, "plugin_dirs": 0, "agent_files": 0 },
  "totals": { "errors": 0, "grade_A_plus_B": 0, "grade_A_plus_B_pct": 0.0 },
  "rule_inventory": ["E-MISSING-REQUIRED-FIELD", "…"], // unknown rule id ⇒ FAIL
  "entries": ["plugins/x/y/skills/z/SKILL.md :: E-MISSING-REQUIRED-FIELD :: tags"],
}
```

**Key is the `(artifact_path, rule_id, field)` triple** — never a bare count, never a bare rule id.

| Assertion | Rule                                                                  | Blocks                                      |
| --------- | --------------------------------------------------------------------- | ------------------------------------------- |
| **R1**    | no `(path, rule, field)` outside `entries`                            | new debt (closes the open intake)           |
| **R2**    | `totals.errors` monotone non-increasing                               | fixing one file while breaking two          |
| **R3**    | `corpus.skill_files` may not fall >2% without a matching catalog diff | deleting the corpus as "compliance"         |
| **R4**    | `grade_A_plus_B_pct` may not fall                                     | dilution by adding barely-passing artifacts |

**Six anti-gaming vectors, each with its defeat:** reproduce a baselined error at a new path → triple-keying · rename or split a rule id → `rule_inventory` · re-emit the baseline inside the offending PR → **every permissive policy-envelope mutation requires a one-file PR whose bytes match an immutable artifact from an owner-dispatched capture on the protected default branch, and a capture branch is single-use** · weaken a rule and re-baseline → `schema_version` pin · mass-delete plugins → R3 · ratchet the number down as aspiration → **the baseline is written by a bot on merge, after the gate passed; humans never hand-lower it.**

**E6.6 governance amendment (2026-09-02).** The repository intentionally does not require human review for ordinary changes. CODEOWNERS remains an ownership-routing aid, not the E6.6 enforcement boundary. Every permissive baseline policy-envelope mutation requires the existing `ci-required` ratchet job to verify an exact one-file PR against a byte-identical Actions artifact from a first-attempt repository-owner dispatch on the protected default branch. This includes adding accepted entries, increasing `totals.errors`, decreasing `grade_A_plus_B_pct`, or changing schema, rule inventory, corpus contract/denominators, provenance, comments, or unknown envelope fields. Strict entry removal and monotone metric improvement do not broaden the envelope. The run id, workflow path, owner actor and triggering actor, successful capture job, source SHA, single capture commit, same-repository PR, and single-use branch are all fail-closed inputs. The initial E6.2 CODEOWNERS-reviewed capture remains valid historical evidence; this amendment governs later envelope exceptions. The pinned artifact's legacy `$comment` is replaced only by the next authorized capture, never by a hand edit.

**Landing:** Phase 1 = R1 only (the existing 7,687 pinned, merges keep flowing). Phase 2 (+2 weeks) = R2. Phase 3 = R3 + R4. Phase 4 = the same machinery on `--agents-only` (baseline 253), at or before its `REPORT-ONLY-UNTIL: 2026-10-31`. Runtime budget: full `--marketplace` measured at ~79 s; the job must stay ≤120 s or state the trade. **A CI cost budget is stated in seconds and anything exceeding it gets a named home**, so `ci-required` does not slide into a 40-minute PR.

**Scoring discipline:** any change to scoring must **damp by finding cardinality and cluster by root cause**. A flat per-finding deduction with no damping produces distributions nobody can act on — the 7,687-error mass is exactly that disease. Scan scope defaults to skill-standard directories with `--include-all` as an explicit opt-in, because fixtures and references legitimately _describe_ anti-patterns.

**Reproducibility:** every blocking gate ships a documented **one-command local invocation**. If a contributor cannot run the exact scan that blocks them, they will optimize against the wrong signal — and in at least one documented public case, actively destroyed quality doing so.

### 10.3 Bounded-swallow rule

Any `|| true`, `continue-on-error`, or bypass `if:` on a correctness-bearing step carries:

```
# REPORT-ONLY-UNTIL: YYYY-MM-DD (reason: <why>; tracking: "<bead title>")
# Enforced by scripts/check-ci-deadlines.py. A lapsed date FAILS the build.
```

The deadline scanner is **extended beyond `.github/workflows/`** to `scripts/`, baseline JSONs, and `scan-allowlist.txt`. Unbounded swallows to close: `validate-plugins.yml:98`, `:658`, `promote-curated.yml:90-91`, and `release.yml`'s `skip_tests` (**deleted, not bounded** — a release that cannot pass validation is not a release).

**Every advisory lane carries a written promotion condition, an owner, and an expiry — and a red scheduled run must page a human.** A gate that prints `❌ VIOLATION` and exits 0 for 35 consecutive days is the definition of silent degradation, and it happened here.

### 10.4 Release standard

**V1 — One bump semantic, four surfaces, one checker.** `package.json` is the npm surface; the other three are display. `reconstruct-versions.mjs --check` becomes a **blocking step of `validate`**. The 99.3% npm/display divergence is **declared, not eliminated**.

**V2 — Publication is unreachable without a green gate. Three independent locks, each sufficient alone:**

1. `workflow_run` on the validate workflow with `conclusion == 'success'` (replaces raw `push`);
2. a **preflight job** re-querying the check-runs for the head SHA — this survives an admin merge, which lock 1 does not;
3. `NPM_TOKEN` moved into a protected GitHub **Environment** (`npm-production`) — **the only lock a PR cannot edit away.** Locks 1–2 are workflow logic.

The registry 200-check is retained but is _not_ the safety net: it prevents _duplicate_ publish, never _unintended_ publish.

**V3 — A release is a five-tuple or it is not a release:** `{npm tarball, sigstore provenance attestation, annotated git tag, GitHub Release, signed evidence bundle row}`. The three `|| { echo "⚠ …" }` swallows are removed. `--generate-notes` is not evidence; a signed bundle is.

**V4 — SBOM per published package** (CycloneDX, `plugins/mcp/**` first), digest referenced from the evidence bundle.

**V5 — Pins move in lockstep and staleness is visible.** `core → 0.10.0` **and** `jrig-cli → 0.2.0` in one PR (jrig-cli@0.1.2 depends on `core@0.9.0` exactly; bumping one alone yields two un-hoisted kernel copies), with the shadow re-baselined in the same PR. `audit-harness` pinned exactly. The `kernel-vendor-hash` **ordering** assertion becomes blocking; staleness stays advisory but routes to Slack.

**V6 — The six authority-flip conditions stand unchanged:** ≥99.5% corpus agreement (deterministic folds 100%) · ≥30-day advisory soak · zero open P0s · tested Rekor superseding-event rollback · CTO+CISO+VP-DevRel sign-off · ≥14-day public deprecation notice. **Not met.** Flipping early would weaken a live security gate (rank 1 over rank 6).

**V7 — Integrity before signing.** Content integrity is checked **separately from** signature validity: an artifact can carry a perfectly genuine signature while its content has drifted. Adopt build-time **content digests** recorded into Freshie/Dolt (cheap, automatic, no PKI, no human in the loop). **Defer cryptographic per-skill signing** — in the public benchmark, coupling "publishable" to "centrally re-signed" froze ~24% of a 336-skill catalog behind manual cross-org action; at 3,179 that is thousands of stale skills. **If signing exists at all it must be automatic on content change**, and it must land in a public transparency log. Dolt already gives this platform the append-only public record that every benchmarked repo lacks.

**V8 — Versioning policy with named axes.** Three axes (skill / upstream / pack-format) and the rule most policies forget: **tightening a previously-loose constraint is BREAKING**. Consumers reject unsupported majors and refuse to over-claim. The kernel `authoring/v1` (byte-frozen) → `v2` (strict fork) transition _is_ a constraint-tightening event and is named as breaking.

---

## 11. DOCUMENTATION AUTHORITY MAP

**Structural rule, machine-enforced (gate G4 of the doc-governance job):** _a document may declare `Status: AUTHORITATIVE` (or `CANONICAL`) only if `STANDARDS.md § Canonical documents` links it._ At the ratification baseline **8 declared, 1 was linked**. That single rule is what `6767-a/c/d/e/h` violated for eight months.

**Activation status: the pointer landed in this PR.** `STANDARDS.md § Canonical documents` now links 727 (platform master standard), 728 (evidence base), and 729 (decision) — so this document's Status condition is satisfied _by the same PR that files it_, exactly as written, and **not** by weakening the condition. § 11.1 is the proof that the resulting graph has one owner per fact class.

| Fact class                                                       | **Single owner**                                                                       | Executable form / delegate                             | Loser being retired                                                          |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------- |
| Skill frontmatter required set, tier model, error-vs-warning     | `000-docs/SCHEMA_CHANGELOG.md` § NON-NEGOTIABLES                                       | `ALWAYS_REQUIRED` (`validate-skills-schema.py:714`)    | 6767-h § 5 (says 6 fields); 6767-c/d/e (CSV-only)                            |
| Full skills standard + 100-point rubric                          | `000-docs/6767-b-SPEC-DR-STND-claude-skills-standard.md`                               | SCHEMA_CHANGELOG post-3.6.0                            | 6767-h's claim to supersede it — **withdrawn in writing (§ 0)**              |
| Agent-definition contract                                        | `AGENT_ALWAYS_REQUIRED` (`validate-skills-schema.py:608`) + SCHEMA_CHANGELOG 3.10/3.11 | —                                                      | `CLAUDE.md`'s "all 317 agents are A-grade" (measured: 347 files, 253 errors) |
| Machine authoring schema                                         | `@intentsolutions/core` `authoring/v1` CHANGELOG (external)                            | **cited, never duplicated**                            | —                                                                            |
| Which validator is authoritative                                 | **this blueprint (727)**                                                               | —                                                      | `CLAUDE.md` + `STANDARDS.md` restatements → links                            |
| Platform master standard (plugins, CI, release, docs governance) | **this blueprint (727)**                                                               | —                                                      | `000-docs/6767-h-SPEC-DR-STND-claude-code-extensions-master.md`              |
| CI gate architecture / required contexts                         | **this blueprint (727)**                                                               | `.github/workflows/validate-plugins.yml`               | `CLAUDE.md` (19 vs actual 20) → pointer                                      |
| Canonical model-agnostic contract + adapter standard             | **this blueprint (727) § 5–6**                                                         | `schemas/canonical/v0/` (interim, `UPSTREAM-PENDING`)  | free-text `compatibility`                                                    |
| Root README / repository landing experience                      | **this blueprint (727) § 6A**                                                          | `generate-readme-toc.mjs` + the § 6A.4 gates           | `728 § 4 C6` / `729 § 6` rejected the old pattern without naming a successor |
| Release / versioning / publish                                   | `RELEASING.md`                                                                         | publish workflows                                      | —                                                                            |
| Doc filing contract                                              | `000-docs/000-DR-STND-document-filing-system.md` (v4.4)                                | —                                                      | —                                                                            |
| Ignore / ledger model                                            | `000-docs/.gitignore` header                                                           | `scripts/check-docs-ignore-policy.mjs` (21 assertions) | —                                                                            |
| External-sync model                                              | `000-docs/694-AT-DECR-external-sync-mirror-by-default-model.md`                        | `sources.yaml` + `sources.lock.json`                   | —                                                                            |
| Submission intake standard                                       | `000-docs/700-DR-GUID-skill-submission-standard.md`                                    | `scripts/check-submission-docs.mjs`                    | —                                                                            |
| External-PR review standard                                      | `000-docs/709-DR-GUID-reviewing-external-prs.md`                                       | —                                                      | —                                                                            |
| Public spec posture / upstream floor                             | `STANDARDS.md`                                                                         | agentskills.io + code.claude.com snapshots             | —                                                                            |
| Maintainer ladder                                                | `GOVERNANCE.md` + `MAINTAINERS.md`                                                     | `CODEOWNERS`                                           | —                                                                            |
| Evidence classes + retention                                     | **the evidence standard filed by Epic 5** (this blueprint § 9 until then)              | ledger schema                                          | —                                                                            |
| Reference architecture + benchmark                               | `000-docs/728-RA-DATA-reference-architecture-benchmark.md`                             | —                                                      | —                                                                            |
| Reference-architecture decision                                  | `000-docs/729-AT-ADEC-reference-architecture-synthesis.md`                             | —                                                      | —                                                                            |
| Task authority                                                   | **beads / Dolt**                                                                       | GitHub Issues + Plane are projections                  | —                                                                            |
| Session protocol                                                 | `AGENTS.md` (agent-facing pointer)                                                     | —                                                      | overlap with `CLAUDE.md`                                                     |
| Host / deploy / ops facts                                        | `~/000-projects/intent-os/ops/` (external)                                             | —                                                      | restatements in this repo → pointers                                         |

### Three document classes, machine-labeled `<!-- doc-class: … -->` on line 1

- **`canonical`** — editable via PR; may declare AUTHORITATIVE only if `STANDARDS.md` links it.
- **`generated`** — editable by nothing; the header names the producing command; rebuild-and-diff in CI. Applies to `000-INDEX.md`, `721-*.json`, `716-*.json`, `717-*.json`, `719-*.json`, `725-*.json`, `freshie/grades.csv`, `freshie/grade-histogram.json`, and the future `certification-report.json` / `launch-readiness.json`.
- **`frozen`** — byte-identical to `origin/main` unless the same PR edits the superseding doc. Applies to `6767-a`, `6767-c`, `6767-d`, `6767-e`, `6767-h`.

**Supersession is a record, not a status edit.** One PR must carry: the frozen banner on the old doc · a per-section disposition table in the new doc · the `STANDARDS.md` pointer update · the `doc-class: frozen` marker. **Never delete or renumber a `6767-*` file.**

### 11.1 Activation proof — exactly one owner per fact class

Ratification correction 2. The activation condition in this document's Status line ("authoritative on merge **and** on the `STANDARDS.md` pointer landing in the same PR") is **kept unchanged and satisfied**, not softened. What follows is the proof obligation that condition creates: after the pointer lands, does the authority graph have exactly one owner per fact class, with no fact owned twice and no fact orphaned?

**Test applied to every row of the § 11 map:** (a) exactly one document/artifact is named as owner; (b) every other document that used to state the same fact now points at the owner rather than restating it; (c) the owner is reachable from `STANDARDS.md § Canonical documents` in ≤ 1 hop, either directly or through a document that table links.

| Fact class                                                        | Sole owner                                                  | Reachable from `STANDARDS.md`  | Competing claimant, and its new state                                                            |
| ----------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------------ |
| Platform master standard (plugins, CI, release, docs governance)  | **727** (this doc)                                          | direct link (added in this PR) | `6767-h` — frozen, superseded, section-level disposition recorded in § 0                         |
| Skill frontmatter required set / tier model / error-vs-warning    | `SCHEMA_CHANGELOG.md` § NON-NEGOTIABLES                     | direct link                    | `6767-h` § 5 (6 fields), `6767-c/d/e` (CSV-only) — frozen with banners naming the falsehood      |
| Full skills standard + 100-point rubric                           | `6767-b`                                                    | direct link                    | `6767-h`'s supersession claim — withdrawn in writing (§ 0)                                       |
| Canonical model-agnostic contract + adapter standard              | **727 § 5–6**                                               | via 727                        | free-text `compatibility` strings — become a generated projection (Epic 3)                       |
| **Root README / repository landing experience**                   | **727 § 6A** _(new — correction 1)_                         | via 727                        | `728 § 4 C6` and `729 § 6` rejected the old pattern and named no replacement; both now cite § 6A |
| Reference-architecture evidence base                              | **728**                                                     | direct link (added in this PR) | — (previously unlinked)                                                                          |
| Reference-architecture decision (adopt/modify/reject + licensing) | **729**                                                     | direct link (added in this PR) | — (previously unlinked)                                                                          |
| External-sync model                                               | `694` + `sources.yaml`/`sources.lock.json`                  | direct link                    | —                                                                                                |
| Submission intake standard                                        | `700`                                                       | direct link (added in this PR) | —                                                                                                |
| External-PR review standard                                       | `709`                                                       | direct link (added in this PR) | —                                                                                                |
| Public spec posture / upstream floor                              | `STANDARDS.md`                                              | is the table                   | `CLAUDE.md` restatements → links                                                                 |
| Machine authoring schema                                          | `@intentsolutions/core` `authoring/v1` CHANGELOG (external) | via `STANDARDS.md` § kernel    | cited, never duplicated                                                                          |
| Task authority                                                    | beads / Dolt                                                | via 727 § 13                   | GitHub Issues + Plane are projections, never authority (§ 13, correction 6)                      |

**Result: no double ownership, no orphan.** Two properties are load-bearing and must not erode:

1. **A fact class gains an owner only by a `STANDARDS.md` row, never by a header edit.** Adding a `Status: AUTHORITATIVE` line to a document that this table does not link is a red run under Epic 2 bead 2.3, not an authority grant.
2. **727 owning several fact classes is not multi-ownership.** Multi-ownership is _one fact with two claimants_. Each row above names exactly one owner; where that owner is 727, the competing claimant is frozen, withdrawn, or converted to a pointer in the same PR that made the claim.

---

## 12. TEMPLATES

Kept deliberately short. Each is a shape, not a form to fill in mechanically.

**Bead**

```
Title:  <Complete imperative sentence. No code prefix. No bead ID.>
Type:   task | bug | feature | epic     Priority: 0-3
Parent: <epic bead title>               Labels: <1-3 plain-English topic words>
Acceptance: <measurable. Names the command that proves it and the before/after number.>
Rollback:   <exact revert command + the observable that confirms it worked.>
Prohibited: <what an executing agent must NOT touch in this bead.>
```

**Annotation (in-code / in-workflow, for any bounded exception)**

```
# REPORT-ONLY-UNTIL: 2026-10-31 (reason: corpus unbaselined; tracking: "<bead title>")
# Enforced by scripts/check-ci-deadlines.py. A lapsed date FAILS the build.
```

**Independent review**

```
Reviewer: <name/identity — NOT the implementer, NOT chosen by the implementer>
Method:   I re-ran every command myself from a clean checkout. I did not accept
          any number from a PR body or an AAR.
 1. Re-measured baselines match the claim ....................... PASS/FAIL + output
 2. Each new gate BITES (red run opened by me, not linked to me) . PASS/FAIL + URL
 3. Zero files changed under any .source.json ancestor ........... PASS/FAIL + diff
 4. ALWAYS_REQUIRED / tier model / error-vs-warning unchanged .... PASS/FAIL + diff
 5. No baseline hand-lowered; every change bot-authored post-merge PASS/FAIL
 6. No `|| true` / continue-on-error added to a correctness step . PASS/FAIL
 7. Kernel pins & branch protection unchanged .................... PASS/FAIL
 8. Outsider Test passes on every PR ............................. PASS/FAIL
Verdict: <EXIT / RETURN TO OPEN>
```

**Handoff**

```
Epic: <title>            State: <n of m beads closed>
Landed:      <bead titles + merge SHAs>
In flight:   <bead title + branch + PR# + what is blocking>
Not started: <bead titles + why (dependency / owner decision / budget)>
Escalations open: <item + who owns the answer + since when>
Numbers as of <SHA>: <the 3-5 scorecard rows this epic moves>
Next action: <one sentence, imperative>
Read first:  <ordered file list>
```

**bd memory**

```
bd remember "<key-in-kebab-case>: <one durable fact, plain English, with the number
that makes it checkable and the file:line that proves it. State what a future session
would otherwise re-derive expensively or get wrong.>"
```

**ADR**

```
# NNN-AT-DECR-<slug>
Status: ACCEPTED | SUPERSEDED by NNN   Date: YYYY-MM-DD   doc-class: canonical
Decision:     <one sentence, imperative>
Context:      <the measured facts that forced it — with commands>
Alternatives: <each, and the decision-hierarchy rank on which it lost>
Consequences: <what becomes true; what becomes harder; what we now owe>
Rollback:     <how to undo, and what makes it irreversible if it is>
Enforced by:  <file:line of the gate, or the literal words "prose only">
```

**GitHub Issue (projection — never an authority, never a gate)**

```
<Plain-English epic title, identical to the epic bead>

**Beads:** <bead titles, one per line — NEVER the 3-char handles>

**What changes about the platform:** <2-3 sentences>
**Measured baseline → target:** <the 3-5 scorecard rows>
**What moved where** (only when freezing/superseding): <old → new authority table>

Beads/Dolt is the authority for this work. This issue is a projection: it never
gates a merge and is never a required status check. If this issue and the bead
disagree, the bead is right.

- Jeremy Longshore
intentsolutions.io
```

---

## 13. THE ORIGINAL TEN EPICS AND THE APPROVED EPIC 11 EXTENSION

**How to read this section.** Each epic carries: objective · measurable outcome · dependencies and entry criteria · **proposed** PR-sized beads · bead dependency graph · risks and mitigations · allowed and PROHIBITED scope · a Claude Code execution prompt · acceptance criteria · tests and evals · evidence contract · rollback · independent-review gate · exit scorecard · AAR + bd-memory requirement · GitHub Issue projection.

**Ratification boundary.** The ten full epic bodies below are the original ratified plan. At that
time their beads were proposals documented here only. The 2026-08-26 amendment subsequently
authorized full Beads graph instantiation and added Epic 11, whose effective inventory is appended
after Epic 10. The `N.M` handles remain specification references, not authority over live issue IDs;
Beads/Dolt owns current task state and dependency truth.

### Activation authority — amended after ratification correction 6

The original progressive-activation rule is preserved here as ratification history; it governed the
initial containment mission before the owner-authorized 2026-08-26 amendment. It no longer
prohibits full graph instantiation. The durable parts remain: Beads authority, dependency order,
evidence-backed closure, independent review, and explicit escalation for external mutations.

**Current execution authority:**

1. **Beads/Dolt is the task authority.** GitHub Issues and Plane are projections. Drift is reconciled
   toward Beads, never away from it.
2. The full approved graph may exist. A task becomes executable only when its live dependencies,
   scope, WIP boundary, and acceptance evidence permit it; instantiation alone never proves readiness.
3. Parallel work is allowed only where the dependency graph and file ownership make it safe. No
   actor may bypass a blocker, manufacture a duplicate implementation, or close from inherited intent.
4. Every governed unit still closes with its required tests, evidence, independent review, AAR or
   closure record, rollback, and read-back. External registry, credential, organization, and Tailnet
   mutations remain owner/external actions unless separately authorized.

**Historical launch rules — superseded as activation authority on 2026-08-26. Live authority is the
current execution authority in § 13 above.** The six original launch rules are retained below in
historical form so the initial decision is not rewritten after the fact:

1. **Beads/Dolt is the task authority.** GitHub Issues and Plane are **projections**. A projection is never the record; drift is reconciled toward beads, never away from it.
2. At ratification, the ~151 proposed records were not to be instantiated in one uncontrolled batch.
3. Before the amendment, only the owner-authorized execution slice was instantiated.
4. Before the amendment, one governed slice ran at a time and exited through review, AAR, evidence,
   and the owner review gate.
5. **A P0 containment bead from a later-numbered epic may run first ONLY when § 1's binding decision hierarchy proves it outranks normal sequence** — and the proof is written down, naming the rank and the exposure it closes.
6. **Any such exception is recorded as an explicit PRE-PROGRAM CONTAINMENT MISSION**, with its own name, its own AAR, and its own boundary. It is **never** silent cross-epic scope drift, and it never entitles the rest of that epic to start early.

**The dependency graphs in this section and in § 15 are DEPENDENCY graphs, not activation
schedules.** An arrow means "this cannot be correct before that," not "start both now." Section 15.1
records the original launch sequence; the amended current activation authority is the live Beads graph
plus the four rules above.

**Rules that apply to every epic without restating them ten times:**

- **PROHIBITED everywhere:** editing any file under a `.source.json` ancestor (mirror-by-default; upstream owns it) · changing `ALWAYS_REQUIRED`, the tier model, or error-vs-warning semantics without the `SCHEMA_CHANGELOG.md` approval gate · adding a fourth required status context · adding a `paths:` filter to `validate-plugins.yml` · adding `|| true` / `continue-on-error` to a correctness-bearing step without a `REPORT-ONLY-UNTIL:` marker · hand-lowering a ratchet baseline · flipping kernel authority · renaming the install slug, `plugins/`, or `skills/` · mutating any external registry (npm, DoltHub, GitHub org settings) — those are owner actions.
- **Evidence contract everywhere:** every bead closes with the command that proves it, its output, and the before/after number. A gate is not accepted until a **red run** exists that the implementer did not author. `bd-sync close` (never raw `bd close`) so the GitHub/Plane projections settle.
- **Rollback everywhere:** every bead names the exact revert and the observable that confirms the revert worked. Where `git revert` is insufficient (registry state, GitHub Environments, rotated credentials), the bead says so explicitly and the step is escalated rather than executed.

---

### EPIC 1 — Repository cleanup and measurement baseline

**Objective.** Make every published number reproducible from one command, remove the artifacts that give one fact two claimants, and close the counterfeit-asset class — so that every later epic argues about outcomes instead of arithmetic.

#### Mission 01 is NOT Epic 1 — read this before claiming anything here is already done

Ratification correction 5. The **completed** repository-cleanup **Mission 01** (2026-08-11 → 2026-08-12, PRs **#1174–#1184**, AAR: `000-docs/726-AA-AACR-mission-01-baseline-aar.md`) and **proposed Epic 1** are two different objects that share a subject. **Mission 01 was PRE-PROGRAM FOUNDATION work**: it ran before this blueprint existed, it produced the baseline this document re-measured, and it is closed. Epic 1 is a proposed slice of _this_ program. They are not the same mission, not the same beads, and the completion of one does not close the other. Every disposition below was checked against `origin/main` HEAD `478aaf17731714fed9b1779284de6a5b3729ef6e`, which **already contains all of Mission 01** — so nothing here is "pending merge."

**What Mission 01 actually delivered, and where it lands.**

| Mission 01 delivered                                                                                                                    | Evidence                                                               | Lands on                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Baseline docs **716–726** + the mandatory `000-INDEX.md` (absent since doc-filing v4.4 adoption)                                        | doc 726 "What shipped"; PR #1174                                       | Epic 1 bead 1.0 (partially) · Epic 2 bead 2.4 (the index this epic must now _generate_) |
| Untracked the freshie sqlite archives — **48,848,896 B (31,494,144 + 17,354,752)** — and closed the `.gitignore` gap that admitted them | `git show --stat 84b663672`                                            | No Epic 1 bead. Pre-program cleanup; no proposed work is retired by it                  |
| Moved `000-docs` ignore ownership to a **per-directory policy + public filing ledger**, with CI gates                                   | PR #1175; `scripts/check-docs-ignore-policy.mjs` (21 assertions)       | Epic 2 (the governance substrate Epic 2 builds on). No Epic 1 bead                      |
| Rescued the Learning Lab from a `workspace/` ignore rule                                                                                | PR #1177                                                               | No Epic 1 bead                                                                          |
| Fixed the provenance defect that republished **6 external plugins under Intent Solutions' name** in the curated index                   | PR #1182, commit `47627a690`                                           | Epic 7 § P1 / Epic 8 mirror disposition — **not** Epic 1                                |
| Removed the **28.5 MB byte-identical `public/data` projection** and gated its return                                                    | PR #1183; `scripts/check-generated-artifacts.mjs` (tracking-only gate) | Epic 1 beads **1.7 and 1.8** — scope reduced, see below                                 |
| Repaired the RTM's dead ADR citations                                                                                                   | PR #1184; `scripts/check-doc-citations.mjs`                            | Epic 2 (citation integrity). No Epic 1 bead                                             |

**Disposition of every proposed Epic 1 bead against that delivery.**

| Bead | Disposition                             | Basis (measured at `origin/main` HEAD `478aaf1773`)                                                                                                                                                                                               |
| ---- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.0  | **PARTIALLY SATISFIED**                 | Mission 01 produced the numbers as **12 one-off read-only diagnostics** across docs 716–725, not as one re-runnable command. § 3.1's 3,679-vs-3,678 discrepancy is the direct cost. The harness is still required                                 |
| 1.1  | **STILL REQUIRED**                      | Scorecard row 3 **[RV]**: `marketplace.extended.json.backup` still tracked                                                                                                                                                                        |
| 1.2  | **STILL REQUIRED**                      | Row 2 **[RV]**: 471 entries / 467 distinct names                                                                                                                                                                                                  |
| 1.3  | **STILL REQUIRED**                      | `freshie/scripts/promote-to-curated.py:225` `_is_binary()` is **still the 8 KiB NUL sniff**, verified in-tree. PR #1182 excluded binaries from the mirror; it did not replace the sniff                                                           |
| 1.4  | **STILL REQUIRED**                      | Row 11 **[RV]**: 12 counterfeit assets remain (8 under `plugins/`, 4 in `skills/.curated/`)                                                                                                                                                       |
| 1.5  | **STILL REQUIRED**                      | Row 24 **[RV]**: five published answers to "how many skills"                                                                                                                                                                                      |
| 1.6  | **STILL REQUIRED**                      | Depends on 1.5                                                                                                                                                                                                                                    |
| 1.7  | **PARTIALLY SATISFIED — scope reduced** | The `marketplace/public/data/*.json` class is **done** (#1183). Row 22 **[RV]** shows the **six `marketplace/src/data/` artifacts still tracked and ungated**. The bead survives against those six only                                           |
| 1.8  | **PARTIALLY SATISFIED — scope reduced** | `check-generated-artifacts.mjs` exists and is wired into `validate-plugins.yml`, but by its own header it "checks TRACKING, not content." The **regenerate-and-diff** gate this bead specifies is still absent. Reuse the file, do not rewrite it |
| 1.9  | **STILL REQUIRED**                      | Row 25 **[RV]**: two disagreeing README metric writers                                                                                                                                                                                            |
| 1.10 | **STILL REQUIRED**                      | Row 26: 3 of 3 stats artifacts rendered past a bound that does not exist                                                                                                                                                                          |
| 1.11 | **STILL REQUIRED**                      | Row 13: the three malformed-`allowed-tools` measurements are unchanged                                                                                                                                                                            |
| 1.12 | **STILL REQUIRED**                      | Row 27 **[RV]**: `sources.yaml` 64 keys vs `sources.lock.json` 63 (`uizze` orphaned)                                                                                                                                                              |
| 1.13 | **STILL REQUIRED**                      | Row 21 correction: 356 case-insensitive occurrences across 125 files at `3543d5d167bd4e8d27666c8893080bca3bd72950`; 292 actionable and 64 retained by machine-readable class                                                                      |
| 1.14 | **STILL REQUIRED**                      | § 18.7 unchanged; owner-gated                                                                                                                                                                                                                     |

**E1.2 implementation measurement (2026-08-17).** At exact base
`48894e82d31f8bc160d3157d299e675c538ca0a7`,
`jq '{rows:(.plugins|length), names:([.plugins[].name]|unique|length), duplicates:([.plugins[].name]|group_by(.)|map(select(length>1)|{name:.[0],count:length}))}' .claude-plugin/marketplace.extended.json`
reported 471 rows, 467 names, `claudebase` ×4, and `geepers-agents` ×2. E1.2 retains
one on-disk-source-matching row for each name, merges the non-conflicting Geepers upstream links
into its richer record, regenerates the two source-owned public catalog surfaces, and adds
duplicate-name refusal to `scripts/validate-catalog-invariants.py`. The same command then reports
467 rows, 467 names, and no duplicates. This correction belongs to E1.2; E1.8 consumes the clean
source but does not claim or duplicate this work.

**Measurements that must be re-run before Epic 1 is claimed complete** (all of them by bead 1.0, none by hand): rows 1, 2, 3, 4, 11, 12, 22, 24, 25, 26, 27 — plus the graded-artifact cohort itself (3,679 vs 3,678, § 3.1). Any Epic 1 exit claim that cites a Mission 01 number rather than a harness number is rejected: Mission 01's numbers were correct **for its HEAD**, and the tree has moved twice since.

**Does the proposed bead count change? No — Epic 1 stays at 15.** Two beads (1.7, 1.8) have **narrower scope**, and one (1.0) is partially informed, but **zero are fully satisfied and zero are superseded**, so there is nothing to remove. This is stated explicitly because the opposite error — inventing filler work to preserve a headline count — is the failure mode this correction exists to prevent. The count that _does_ move is Epic 2's, which gains the README landing-contract bead from § 6A (12 → 13); § 17 carries the new totals.

**Measurable outcome.** Catalog entries 471 → 467 with a uniqueness assertion · tracked stale catalog shadow 1 → 0 · counterfeit assets 12 → 0 with a magic-byte gate · deterministic tracked marketplace projections without a drift gate 4 → 0 · README metric writers 2 → 1 resolver with 5 named cohorts · `sources.yaml`/lock keys 64/63 → equal · retired-domain occurrences 292 actionable → 0, with 64 classified frozen or historical occurrences retained byte-identically.

**E1.8 population correction (2026-08-17).** The ratification-time six-file headline and the later
writer-discovery count of eight described different cohorts. At exact base
`66603ebe4704884f8cf886328b4fbe6c0b2fb99c`, `pnpm run measure:e1 --row=22 --stdout` found eight
tracked `marketplace/src/data` JSON files with executable writers. Registry-backed authority
classification separates them into four deterministic local projections (`catalog.json`,
`skills-catalog.json`, `skills-index.json`, and `unified-search-index.json`), three point-in-time
network snapshots (`github-stats.json`, `npm-stats.json`, and `skills-stats.json`, owned by E1.10),
and one canonical editorial file (`spotlights.json`). Those populations are not interchangeable.
The first bounded E1.8 slice gates `skills-index.json`. The second slice, measured from exact base
`e39ed6dcae0e6eead8a018d5b796eae6caba324c`, runs
`node marketplace/scripts/discover-skills.mjs --level=full` and compares stable `filePath`
identities against `git show HEAD:marketplace/src/data/skills-catalog.json`: the stale L1 baseline
moves 3,008→3,068 through 96 additions, 36 removals, and 2,943 changed records among 2,972 shared
paths. Of those additions and removals, 73 and 7 respectively are beneath a `.source.json`
ancestor; the slice changes only the generated projection and edits zero mirrored `SKILL.md`
files. The second slice gates that updated full catalog through
`node marketplace/scripts/discover-skills.mjs --level=full --check`. `catalog.json` and
`unified-search-index.json` remain E1.8 work, so two of four deterministic projections are gated and
this bead remains open. The third slice, measured from exact base
`98f652ff5ba00181b76d1aae9e6698741b69c132`, replaces `sync-catalog.mjs`'s output-as-input merge and
runtime timestamps with one strict renderer whose only inputs are the 467-row canonical extended
catalog and the 3,068-row full skill projection. `node marketplace/scripts/sync-catalog.mjs`
moves the stale tracked output from 450 plugins / 3,022 skills / 81 commands to 467 plugins / 3,068
distinct skill paths / 80 commands. Skills join to normalized `parentPlugin.path` and canonical
plugin `source`; the two intentional source-alias pairs receive equal per-plugin counts while the
global total counts each `filePath` once (3,068, not the alias-summed 3,074). Canonical plugin order
is preserved, the legacy default author remains on the two canonical rows without one, the governed
retired-domain normalizer applies to the complete rendered value, timestamps and output-owned flags
are omitted, malformed or contradictory inputs fail closed, and
`node marketplace/scripts/sync-catalog.mjs --check` compares rendered bytes with the stage-0 Git
index without mutating the worktree. `unified-search-index.json` remains the final
E1.8 slice, so three of four deterministic projections are gated at the end of that third slice.
The fourth slice, measured from exact base
`8558c10dd5c29f62d74b4463a69fa922dd56cfc0`, replaces the search producer's wall-clock
`meta.generated` field and output overwrite disguised as `--check` with one source-derived renderer
and non-mutating stage-0 Git-index comparison. The committed baseline moves from 448 plugins / 3,008
skills / 0 documents / 3,456 total items / 311 agents / 19 hooks to 467 plugins / 3,068 skills / 24
documents / 3,559 total items / 347 agents / 28 hooks. Plugin, skill, and documentation order and
load-bearing consumer fields remain compatible; the renderer supports the repository's scalar,
block-list, and inline-list documentation frontmatter, rejects malformed identities and symlinked or
unreadable surfaces, and applies governed retired-domain normalization to the complete output. The
existing unconditional generated-content job invokes the same renderer with `--check`, so all four
deterministic local projections now have executable content-drift gates without a new required
context or path filter.

**E1.8 determinism completion (2026-09-25).** At exact base
`96d59a6ff0c9d3fb33a10425ec28508568babe0f`, two projections still were not byte-stable: the first two
E1.8 slices kept a wall-clock `generatedAt` in `skills-index.json` and `skills-catalog.json` and made
`--check` pass by copying the committed value. Two regenerations from identical inputs produced
different bytes, and over the preceding 30 days (708 commits on `main`) that line changed in 112 of
the 113 commits touching each file, so any two pull requests that regenerated them conflicted. The
producer now writes neither field, matching the third and fourth slices' removal of wall-clock
fields from `catalog.json` and `unified-search-index.json`. The public `/data/skills-catalog.json`
keeps the schema 3.4.0 `generatedAt` field, now stamped at build time by `copy-public-data.mjs`
(honoring `SOURCE_DATE_EPOCH`). No consumer read the tracked value: the sitemap emits no
`lastmod`, `skills-index.json` is not publicly served, and row 23 is `not_reproducible` because a
timestamp cannot establish staleness. In the same change the committed scorecard stops persisting
the whole-tree `tracked_files` value of rows 1 and 46; § 1 row 1's definition is unchanged and
`pnpm run measure:e1 --row=1 --stdout` still reports all three values. The count is a pure function
of the commit that contains it, and it changed in 132 of the 146 commits touching the scorecard (38
of them changed nothing else). Each affected committed row names the omitted value under
`unpersisted_values`, and `persistedReport` fails closed if a measured row stops producing it.
Real collisions remain conflicts by design: `.harness-hash` tamper evidence, Freshie run and Dolt
identities, and content-derived counts.

**E1.13 measurement correction (2026-08-16).** The earlier 341/121 headline used a case-sensitive grep and treated all non-6767 files as one population. At exact base `3543d5d167bd4e8d27666c8893080bca3bd72950`, `git grep -I -i -o "$(printf '%s%s' claudecode plugins.io)" <SHA> -- | wc -l` reports 356 occurrences and the corresponding `-l` command reports 125 files. Running `node scripts/check-dead-domain.mjs --json --root <clean-checkout-of-SHA>` separates 292 actionable occurrences (260 editable first-party + 32 registered generated projections) from 64 retained occurrences (3 in frozen 6767-h + 1 in its byte-pinned anchor manifest + 60 in the registered Freshie run-1 snapshot + 0 provenance mirrors). The 292/64 correction supersedes the earlier 293/63 partition, which incorrectly treated the frozen anchor manifest as editable. These populations are not interchangeable. The gate targets zero actionable occurrences and requires every retained class to remain byte-identical.

**E1.6 first-slice progress (2026-08-17).** At exact base
`109179f92cf7f01b95ad2f88fd15956713631fc2`,
`node scripts/corpus-resolver.mjs --cohort marketplace-visible --cohort graded --cohort first-party --cohort curated-mirror --cohort curriculum --json | jq '.cohorts | map_values(.count)'`
reports 3,068 / 3,679 / 2,802 / 1,915 / 500 respectively. This bounded slice changes none of
those values. It labels five live global website totals as `marketplace-visible`, renders the
cohort definition and exact resolver command next to each, and adds
`pnpm run validate:published-count-cohorts` to the existing `validate` job. The fixture-driven gate
recursively discovers count-bearing public Astro pages and components from literals, catalog
counts, collection lengths, post-noun numeric forms, and identifier-independent rendered
expressions—including multiline expressions split from the `skills` noun by adjacent markup—rather
than one identifier. URL path segments, prose durations, stars, other-population units, narrative
heading shapes, collection renderers, and unrelated attributes are excluded by fixtures rather than
silently treated as skill totals; plain/canonical/hyphenated count-label headings still bind adjacent
counts, and nested object syntax stays owned by its enclosing expression. The first
inventory finds 51 Astro sources: five global pages are enforced, 46 discovered non-global or
point-in-time sources are grouped by exact path as owned deferrals, and
the generated social image is a forty-seventh path-level deferral. Three local/query expressions
on otherwise enforced pages are separately registered, producing 50 owned deferral claims in
total. Discovery binds every detected expression to an exact enforced or deferred registration;
simple brace/interpolation wrappers normalize, but compound wrappers do not inherit an inner
registration. A second count or unregistered member/call extension added to an already registered
page therefore fails closed. Unknown cohorts, unsafe
or unreadable paths, symlinks, comment-only labels, missing provenance, and unregistered new count
sources or expressions fail closed. Astro frontmatter and script/style bodies cannot satisfy the
rendered count/label contract, markup attributes cannot impersonate it, and provenance must be a
top-level component tag parsed outside quoted attributes and Astro expression strings. Paired raw
text elements are parsed with quote- and brace-aware opening tags, so a quoted `/>` cannot disguise
a script body as self-closing; malformed raw-text elements are refused. Cowork packages, entity-local cards, vendor packs, stale live copy, and research snapshots
are not forced into the marketplace cohort. Entity-local cards are now separately labeled and bound
to exact deferred claims in `scripts/published-count-cohorts.json`; their local contracts are not
interchangeable with the marketplace cohort. Cowork package and bundle surfaces are likewise bound
to exact `Cowork-package-local` claims; their generated archive population is separate from the
marketplace cohort. README work is deferred because its generated count
contract overlaps active PRs; the authoritative local check is
`node scripts/generate-readme-toc.mjs --check` (there is no `pnpm run readme:check`). E1.6 remains
open until every published count surface is either enforced with its true cohort or governed as an
explicit non-live/historical exception.

**E1.6 vendor-pack continuation (2026-08-18).** Thirty generated `/learn/<vendor>/` pages now
label their pack and category counts as `vendor-pack-local`; unscoped metadata totals were removed.
The registry carries 60 exact claims (two per page), and the live checker reports
`ALLOW cohorts=5 enforced=6 deferred=88 discovered=20`. Numeric values remain unchanged. The
learning-hub aggregate, stale live copy, research snapshots, README, and mirrored content remain
separate deferred populations.

**E1.6 learning-hub continuation (2026-08-18).** The learning-hub landing page now separates
two aggregate vendor-pack totals from two per-pack card/tier counts. Four exact claims are
registered, and the checker reports `ALLOW cohorts=5 enforced=6 deferred=91 discovered=20`.
The values remain unchanged; research, stale/live-copy, README, and mirrored populations remain
deferred.

**E1.6 research-snapshot continuation (2026-08-18).** The research landing page and six published
research analyses now display a shared 2026-03-04 snapshot boundary tied to repository commit
`256db0b3eabc0669ffe75bc16f19053820c3e91c`. Their historical values remain deferred and are not
presented as current marketplace totals.

**E1.6 live-copy/quality-rule continuation (2026-08-18).** The documentation CTA now identifies
its retained 418-plugin and 2,834-skill wording as `historical-copy` and explicitly says it is not
a live total. The grading page now identifies its numeric bands as `quality-rule` policy rather
than a corpus count. Both paths remain path-level deferred in the checker because neither is a
current canonical cohort.

**E1.6 closure candidate (2026-08-18).** The completed count-contract slices now classify every
discovered numeric surface as one of the five canonical cohorts or an explicit local/historical
deferred class. Closure evidence is filed in AAR 769; Beads/Dolt remains the authority for the
final bead state.

**E2.6 documentation-number correction (2026-08-18).** Epic 1 closed the same day (AAR 774), so
several rows of this blueprint that assert a defect as _current_ now describe a state that no
longer exists. This correction dispositions them; the original rows remain as the ratified
baseline record and must be read together with this block. (1) **Schema version**: the
validator's `SCHEMA_VERSION` is now `4.0.0` (SCHEMA_CHANGELOG entry 2026-08-16); CLAUDE.md and
6767-b's banner both already state 4.0.0, so rows 42/53 and the § 0 premise ("6767-b documents
3.15.2 against 3.16.1") are at their target state — bead 2.8's assertion keeps them there. The
`3.16.1` literals at §§ 0, 3, 8 and the example `schema_version` in § 6 are spent baselines.
(2) **Catalog identity**: 471/467 with `claudebase`×4 + `geepers-agents`×2 is resolved by E1.2 —
the measured state is 468 entries / 468 unique names / zero duplicates (scorecard row 2).
(3) **Source parity**: 64-vs-63 with `uizze` orphaned is resolved by the owner's acceptance of
the UIZZE mirror (PR #1242) plus E1.12 — 64 == 64 with a bidirectional CI parity gate
(scorecard row 27); the blueprint's "remove uizze" disposition was reshaped by owner decision,
recorded in AAR 772. (4) **Docs index**: 166-vs-168 is resolved by E2.4 — the index is generated
and drift-gated; its count lives in exactly one generated line (214 at this correction).
(5) **`ci-required`**: the aggregate now needs 21 jobs and the three required contexts are
`ci-required` + `gitleaks` + `skill-conform`; CLAUDE.md enumerates them and bead 2.7's assertion
keeps the prose equal to the workflow. (6) **The "all 317 agents A-grade" claim** no longer
exists in CLAUDE.md — retired for the measured 347-file/253-error framing this blueprint
demanded. (7) **Skill-count cohorts**: the `3,179 SKILL.md` figure used across §§ 0–11 and docs
728/729 is a point-in-time file count; the live cohorts are tracked `plugins/**/SKILL.md` files
(3,181 at this correction) vs marketplace-visible distinct skills (3,069) vs curated mirror
(1,915), each regenerable via the E1.0 harness — bare re-quotes of 3,179 as a present-tense fact
are incorrect. (8) **Plugin totals**: "~470"/"470-plugin" reads resolve to the catalog-entry
cohort, 468 at this correction. Bead 2.6's own target text (§ 13 row 2.6) predates these
landings; its operative targets are the assertions in beads 2.7/2.8 plus the cohort-label
discipline of E1.6. (9) **Epic 2's exit criterion "8→3 self-declarations, all linked"**
(§ 13, and exit-scorecard row 43's "8/1 → 3/3") is reconciled against the live graph: the
effective authority-claimant count is **2** (this blueprint and 6767-b), both linked — the
freeze retired more claimants than the criterion anticipated, so the target is EXCEEDED, not
missed. The pinned assertion is `check-doc-authority.test.mjs` (two claimants, twelve
canonical-table links); "2 ≤ 3, all linked" is the satisfied reading, recorded here so no
audit needs to re-derive it.

**E3 closure corrections (2026-08-19).** Two cells of this section are superseded by delivered
reality, disclosed at closure (AAR 789): (1) **row 3.6** prescribed converting the Kobiton Codex
fork "into a real thin adapter"; the delivered disposition is **deletion** — § 6's own rule that
adapters are generated and hand-authored adapter content is prohibited makes a hand conversion
dishonest, and the registry holds only `claude-code`. Root cause of the fork (an unanchored
`skills/**` include auto-matching at any depth) was fixed at the source and the reappearance
class converted to lock drift (AAR 783 + addendum). (2) The **measurable-outcome line's
"1,454"** multi-harness-claim count was the pre-regeneration figure; the measured surface at
execution was **2,700 first-party files** across exactly four claim strings, all withdrawn, with
the ratchet blocking recurrence (AAR 786). The acceptance-criteria cells "adapters[] present on
every skill" and "zero free-text compatibility" are dispositioned literal-vs-delivered in AAR
789: intent met via the truthful-claim + ratchet + registry state; letter completes with organic
skill-card adoption, policed by gates already live.

**E3.13 kernel-boundary record (2026-08-19).** The canonical contract was proposed to the
kernel as `intent-eval-core#90` (schemas `skill-contract`, `capability`, `eval-spec`), citing
`schemas/canonical/v0/` as the draft. The ownership boundary stands as designed: this repository
is never its own schema authority — the v0 directory is `DRAFT · UPSTREAM-PENDING`, every
consumer names that status, and on kernel adoption the local draft becomes a cited vendored copy
of the kernel contract with the kernel changelog as the canonical record of semantics. Until
adoption, the draft evolves only through reviewed PRs here with #90 linked.

**Dependencies / entry criteria.** None for the measurement harness, the catalog work, and the asset sniff. The dead-domain sweep **must wait for Epic 2's freeze** — the frozen set is an input, not an afterthought.

**Proposed beads (15).**

| #    | Bead title (imperative, plain English)                                                                                  | Type · P                | Acceptance (abbreviated)                                                                                                                                                                                                                                                                                                                                                                                                                |
| ---- | ----------------------------------------------------------------------------------------------------------------------- | ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.0  | Build the single measurement harness that emits every number in this blueprint from one command.                        | feature · P1            | One committed script, one output artifact, one command line per scorecard row, re-runnable from a clean checkout.                                                                                                                                                                                                                                                                                                                       |
| 1.1  | Delete the tracked stale copy of the plugin catalog and forbid a second catalog-shaped file.                            | task · P1               | `marketplace.extended.json.backup` untracked; `validate-catalog-invariants.py` fails on any second catalog-shaped tracked file; blob SHA recorded in the PR for recoverability.                                                                                                                                                                                                                                                         |
| 1.2  | Collapse the four duplicate catalog entries and make catalog-name uniqueness a build failure.                           | bug · P1                | `len(plugins) == len({p.name}) == 467`; keep the entry whose `source` matches the on-disk directory; **never rename a plugin**; uniqueness assertion added.                                                                                                                                                                                                                                                                             |
| 1.3  | Replace the curated-mirror NUL-byte binary test with a magic-byte content-type check that fails on extension mismatch.  | bug · P0                | `promote-to-curated.py:225` `_is_binary()` replaced by a content-type sniff; extension/bytes mismatch **fails non-zero**; unit tests cover the real cases plus a genuine PNG.                                                                                                                                                                                                                                                           |
| 1.4  | Remove the counterfeit placeholder assets from the source plugins and regenerate the curated mirror.                    | task · P1               | Every binary-extension file whose content is text deleted or renamed with the referencing body updated; mirror regenerated; grade changes recorded. **Must land after 1.3 or a revert republishes counterfeits.**                                                                                                                                                                                                                       |
| 1.5  | Extract one corpus resolver and route every counting surface through it.                                                | feature · P1            | `resolveCorpus(cohort)` returns the file set for `marketplace-visible`, `graded`, `first-party`, `curated-mirror`, `curriculum`; four call sites converted; counts asserted against a fixture tree, not the live corpus.                                                                                                                                                                                                                |
| 1.6  | Label every published count with the cohort it counts.                                                                  | task · P1               | No number published without a cohort. Values do not change in this bead — only their labels.                                                                                                                                                                                                                                                                                                                                            |
| 1.7  | Stop tracking the build-derived marketplace data artifacts that no non-build consumer reads.                            | task · P0               | Scope is the **six under `marketplace/src/data/`** (the `public/data` class was closed pre-program by PR #1183). For each, the PR records whether anything outside the build reads the committed bytes; every "no" is gitignored and added to `check-generated-artifacts.mjs`'s `PROJECTIONS`, matching the `cowork-manifest.json` precedent.                                                                                           |
| 1.8  | Add regenerate-and-diff drift gates for every generated artifact that must stay tracked.                                | feature · P0            | **Extends `scripts/check-generated-artifacts.mjs` — never replaces it.** That gate checks _tracking_ by design; this bead adds the _content_ check: an exact byte comparison using `git diff --no-index --quiet` against a temporary render per surviving artifact, without mutating the worktree, as a **job inside `validate-plugins.yml`** listed in `ci-required.needs`; a deliberately-mutated artifact produces a linked red run. |
| 1.9  | Delete the orphaned README metrics writer.                                                                              | task · P2               | `scripts/update-metrics.mjs` removed with its `package.json` entry; PR states the alternative considered (rewrite onto `resolveCorpus`) and why deletion won.                                                                                                                                                                                                                                                                           |
| 1.10 | Give the external stats artifacts an explicit freshness bound that fails loudly.                                        | feature · P2            | Each stats artifact declares `max_age_hours`; a breach fails or routes to Slack; the site never renders an out-of-bound number as current.                                                                                                                                                                                                                                                                                              |
| 1.11 | Repair the malformed tool allowlists and make an unparseable allowlist an error.                                        | bug · P0                | Every **first-party** unparseable `allowed-tools` corrected (both CSV and YAML-list forms remain valid); **mirror-owned instances are not edited**, only recorded; validator emits ERROR; post-fix first-party count 0, so the rule adds zero baseline debt.                                                                                                                                                                            |
| 1.12 | Remove the registered external source that has no directory, catalog entry, or lock entry, and assert key-set equality. | task · P3               | `uizze` removed; CI asserts `sources.yaml` and `sources.lock.json` key sets are equal; `sync-external.mjs` is not run.                                                                                                                                                                                                                                                                                                                  |
| 1.13 | Replace the dead public domain in first-party surfaces and block its reintroduction.                                    | task · P2               | 292 actionable occurrences replaced across **non-frozen first-party sources and their registered generated projections**; 64 frozen or point-in-time occurrences and every mirror occurrence left byte-identical and enumerated; a case-insensitive, fail-closed lint rule blocks reintroduction.                                                                                                                                       |
| 1.14 | Move the local MCP server credential out of plaintext.                                                                  | task · P1 (owner-gated) | The working-tree `/.mcp.json` no longer holds a live-shaped key in plaintext `env`; value sourced from SOPS. **Rotation is asked once, never assumed** (see § 18.7).                                                                                                                                                                                                                                                                    |

**Bead dependency graph.**

```
1.0 ──▶ 1.5 ──▶ 1.6
1.3 ──▶ 1.4                    (sniff before removal; reverting 1.4 alone republishes counterfeits)
1.7 ──▶ 1.8                    (decide what stays tracked, then gate what stays)
1.1, 1.2, 1.9, 1.11, 1.12, 1.14   independent
E2 freeze ──▶ 1.13             (cross-epic: the frozen set is an input)
1.10 independent; consumed by Epic 10's launch gate
```

**Risks and mitigations.** _Deleting a tracked artifact that a consumer secretly reads_ → 1.7 requires a written grep answer per artifact before any untracking. _The magic-byte sniff producing false positives on genuine binaries_ → unit tests include genuine PNG/ZIP fixtures; the boycott-filter icons and servicegraph marks are confirmed genuine and must keep passing. _A mass domain edit touching frozen documents_ → 1.13 is gated behind Epic 2 and enumerates every skipped occurrence.

**Allowed scope.** `.claude-plugin/`, `freshie/scripts/`, `scripts/`, `marketplace/src/data/` tracking status, `sources.yaml`, `.gitignore`, first-party non-frozen surfaces.
**PROHIBITED scope.** Any `.source.json` subtree · any `6767-*` document · the validator's required-field set · plugin renames · deleting a plugin directory to improve a count.

**Claude Code execution prompt.**

> Work one bead at a time on a branch off `origin/main`. Before changing anything, run the measurement harness (bead 1.0) and paste its output into the bead note — that is the before number. For every bead that adds a gate, land the gate and the corpus fix in the **same PR**, then prove the gate bites by pushing a deliberately-broken commit to a scratch branch and linking the red run. Never edit a file whose directory tree contains `.source.json`. If a bead's fix would change a published count, state the cohort. Close with `bd-sync close` and the command output, never a summary.

**Acceptance criteria.** All 15 beads closed with evidence; scorecard rows 2, 3, 11, 12, 22, 24, 25, 26, 27 at target; `node scripts/check-generated-artifacts.mjs` and the new drift gates green; the measurement harness reproduces every § 3 row from a clean checkout.

**Tests and evals.** Unit tests for the magic-byte sniff (3 real counterfeits + 1 genuine binary), the corpus resolver (per-cohort counts against a fixture tree), catalog uniqueness, and `sources.yaml`↔lock key equality. Regenerate-and-diff proof runs for each drift gate. No behavioral eval required — this epic is entirely E1.

**Evidence contract.** E1. Every number cited in a bead note comes from the harness, with the command line recorded. The counterfeit removal records the pre-removal file list and each file's magic-byte verdict.

**Rollback.** Per bead, `git revert`. Two coupled pairs are called out in their PRs: 1.3+1.4 (reverting 1.4 alone republishes counterfeits) and 1.7+1.8 (reverting 1.7 alone leaves gates pointing at untracked files).

**Independent-review gate.** A reviewer who is not the implementer re-runs the harness from a clean checkout and confirms every claimed before/after pair, and independently opens one red run per new gate.

**Exit scorecard.** Rows 2 (471/467→467/467), 3 (1→0), 11 (12→0), 12 (NUL→magic-byte), 22 (6→0), 24 (5→1+cohorts), 25 (2→1), 26 (3→0), 27 (64/63→equal).

**AAR + bd memory.** File an `AA-AACR` AAR recording which measurements changed between `436a00f80`, `708692244`, `49210ecb6`, and the current `origin/main` HEAD `478aaf177` and why. `bd remember "corpus-cohorts: five named cohorts resolved by resolveCorpus(); the five historical skill counts map 1:1 onto them — <file:line>"`.

**GitHub Issue projection.** One `epic`-labeled issue titled with the epic's plain-English name, carrying a `**Beads:**` list. Never a required check.

---

### EPIC 2 — Documentation authority and source-of-truth consolidation

**Objective.** End the eight-month condition in which eight documents declare themselves authoritative, one is linked, and four instruct reviewers to reject valid frontmatter — and make the condition mechanically unrepeatable.

**Measurable outcome.** Docs self-declaring AUTHORITATIVE 8 → 3, all 3 linked from `STANDARDS.md`, gate-enforced · `000-INDEX.md` 166 entries vs 168 tracked → equal and generated · documented schema version 3.15.2 → asserted equal to `SCHEMA_VERSION` · prose-documented `ci-required` count 21 = actual 21, but machine assertion 0 → 1 · prose-anchor checker in 0 CI jobs → 1 · every `6767-*` document carries a frozen banner naming its verified falsehoods.

**Dependencies / entry criteria.** None. **Blocks:** Epic 1 bead 1.13 (dead-domain sweep) and any later epic that edits a `6767-*` file.

**Proposed beads (13).** _(12 as originally drafted, +1 from ratification correction 1 — the root README landing contract, § 6A.5.)_

| #    | Bead title                                                                                                        | Type · P     | Acceptance (abbreviated)                                                                                                                                                                                                                                                                                                    |
| ---- | ----------------------------------------------------------------------------------------------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2.1  | Freeze the five superseded standards documents with a banner that names their known-false rules.                  | task · P0    | `6767-a/c/d/e/h` each gain a top-of-file SUPERSEDED–FROZEN banner citing file:line for each falsehood; **no content below the banner altered, no section anchor changed**; `6767-f`/`6767-g` marked REFERENCE and lose their CANONICAL self-declaration; `6767-b` untouched.                                                |
| 2.2  | File the platform master blueprint and record its section-level disposition of the superseded master spec.        | task · P0    | Doc 727 filed per doc-filing v4.4, ledgered and indexed, containing § 0's disposition table and the explicit withdrawal of 6767-h's claim over 6767-b.                                                                                                                                                                      |
| 2.3  | Add a gate that fails any document declaring itself authoritative unless `STANDARDS.md` links it.                 | feature · P0 | New check inside the existing `doc-governance` job; a planted violation produces a linked red run. **This is the machine boundary that makes the drift unrepeatable.**                                                                                                                                                      |
| 2.4  | Generate `000-INDEX.md` from the tracked file list and gate it for drift.                                         | feature · P1 | `scripts/generate-docs-index.mjs` implements the algorithm the index header already specifies; file marked `generated`; `doc-governance` regenerates and diffs; 166/168 → equal.                                                                                                                                            |
| 2.5  | Label every document with a machine-readable class and enforce the frozen and generated classes.                  | feature · P1 | `<!-- doc-class: canonical\|generated\|frozen\|record -->` on line 1 of every `000-docs/*.md`; `frozen` ⇒ byte-identical to `origin/main` unless the same PR edits the superseding doc; `generated` ⇒ rebuild-and-diff.                                                                                                     |
| 2.6  | Correct every documented number that disagrees with the code.                                                     | bug · P1     | Four verified drifts corrected **to measured truth, never the reverse**: schema 3.15.2→3.16.1; `ci-required` 19→21 enumerated (**already corrected by E1.8; remeasure, do not duplicate**); "all 317 agents A-grade"→347 files/253 errors/report-only; external-source count after 1.12. Each correction cites its command. |
| 2.7  | Assert that the documented required-check list equals the actual `ci-required` needs list.                        | feature · P1 | A check parses `needs:` from the workflow and the fenced machine-parseable block in this blueprint and fails on difference; planted mismatch → linked red run.                                                                                                                                                              |
| 2.8  | Assert that the documented schema version equals the validator's `SCHEMA_VERSION`.                                | feature · P2 | Compares `SCHEMA_VERSION` against every documented occurrence; frozen docs exempt **by class**, never by filename allowlist.                                                                                                                                                                                                |
| 2.9  | Run the prose-anchor checker in CI so freezing the master spec cannot silently break citations.                   | feature · P1 | `check-prose-anchors.py` + `parse-prose-anchors.py` run inside `doc-governance` against `tests/fixtures/prose-anchors/`; a deleted/renamed anchor in 6767-h produces a linked red run.                                                                                                                                      |
| 2.10 | Publish the one-owner-per-fact-class authority map and make every competing document point to it.                 | task · P1    | § 11's map is the single owner list; `CLAUDE.md`, `AGENTS.md`, `STANDARDS.md` replace restatements with links.                                                                                                                                                                                                              |
| 2.11 | Record the authority boundary between this repo, the kernel, the eval CLI, the eval lab, Intent OS, and the CMDB. | task · P2    | § 4's boundary invariants stated per system, including the pin-axis/authority-axis separation and the ban on `j-rig eval --db freshie/inventory.sqlite`.                                                                                                                                                                    |
| 2.12 | Make supersession a required record shape with a template and a checklist.                                        | task · P2    | A template requiring, in **one PR**: frozen banner + per-section disposition + `STANDARDS.md` pointer + `doc-class: frozen`. The 6767 reconciliation is the worked example.                                                                                                                                                 |
| 2.13 | Rebuild the root README as a governed landing contract with a per-class navigation map and a byte-budget gate.    | feature · P1 | Criteria **R1–R10 of § 6A.4**, each with the command that proves it and a linked red run per new assertion; install-slug string test pinned; zero frozen-file diffs; `plugins/`, `skills/`, and the slug unrenamed. **Depends on 1.5/1.6 + 2.3.**                                                                           |

**Bead dependency graph.**

```
2.2 ──▶ 2.1 ──▶ 2.3            STRICTLY SERIAL: the pointer gate red-fails everything
                               until the seven self-declarations are removed
2.1 ──▶ 2.9                    the anchor checker must exist before the freeze is claimed enforceable
2.4 ──▶ 2.5                    index generated before class enforcement
2.6 ──▶ 2.7, 2.8               correct the numbers, then assert them
2.10, 2.11, 2.12 independent
2.1 ──▶ (Epic 1) 1.13
(Epic 1) 1.5, 1.6 ──▶ 2.13 ; 2.3 ──▶ 2.13    cohorts + the pointer gate before the landing contract
```

**Risks and mitigations.** _Landing the pointer gate before the banners_ → strict serialization 2.2→2.1→2.3, stated in the beads. _A banner edit that shifts a section anchor_ → banners are additive prepends only; 2.9's checker proves anchors survived. _Correcting a number in the wrong direction_ → 2.6 requires the command output in the PR body for each correction.

**Allowed scope.** `000-docs/`, `STANDARDS.md`, `CLAUDE.md`, `AGENTS.md`, `README.md` (bead 2.13 only), the `doc-governance` job, `scripts/generate-docs-index.mjs`, `scripts/generate-readme-toc.mjs`.
**PROHIBITED scope.** Any content edit below a frozen banner · renumbering or deleting any `6767-*` file · editing `6767-b`'s rubric · changing the validator · renaming the public install slug, `plugins/`, or `skills/` (§ 6A.3) · adding per-skill rows or any hand-written count to `README.md`.

**Claude Code execution prompt.**

> Land 2.2, then 2.1, then 2.3 — in that order, one PR each. The banners are **prepends only**: verify with `git diff --stat` that every frozen file shows additions and zero deletions, and verify with `check-prose-anchors.py` that every section anchor still resolves. When correcting a documented number, paste the command and its output into the PR body; if the code is wrong rather than the doc, stop and file a bead instead of editing the doc to match a bug. Never touch `6767-b`.

**Acceptance criteria.** All 13 beads closed; `node scripts/check-docs-ignore-policy.mjs`, `node scripts/check-doc-citations.mjs`, and the new authority-pointer, doc-class, index-drift, schema-version, ci-count, prose-anchor, and README landing-contract (§ 6A.4 R1–R10) checks all green; 8→3 self-declarations, all linked.

**Tests and evals.** Fixture-based tests for the authority-pointer gate (a planted `Status: AUTHORITATIVE` doc), the doc-class enforcer (a hand-edited generated doc; an edited frozen doc), the index generator, and the prose-anchor checker. E1 only.

**Evidence contract.** E1. Each gate ships with a linked red run authored by someone other than the implementer.

**Rollback.** Banners and markers are additive prepends — `git revert` restores byte-identical originals. Gates are removed by deleting one invocation from `doc-governance`, with no document change.

**Independent-review gate.** The reviewer confirms `git diff` shows zero deletions in every frozen file, independently opens the four planted-violation red runs, and confirms `6767-b` is byte-identical.

**Exit scorecard.** Rows 41 (19/17/20 → equal), 42 (3.15.2 → equal), 43 (8/1 → 3/3), 44 (166/168 → equal), 45 (0 → 1).

**AAR + bd memory.** AAR records the supersession chain as it was found (6767-h claiming to supersede the document every live pointer treated as master) and the rule that now prevents it. `bd remember "doc-authority-gate: a 000-docs file may declare AUTHORITATIVE only if STANDARDS.md links it; enforced in the doc-governance job"`.

**GitHub Issue projection.** One `epic` issue plus one cluster issue for the freeze, each with a `**Beads:**` list and the old→new authority table.

---

### EPIC 3 — Canonical model-agnostic plugin and skill contract

**Objective.** Replace 40 free-text compatibility strings and ~131 vendor-literal source files with a machine-checkable canonical contract, a capability vocabulary, and declared adapters — so a portability claim is a fact rather than a sentence.

**Measurable outcome.** Multi-harness claims with zero adapter artifact 1,454 → 0 · adapter files byte-identical to canonical 27 → 0, gate-enforced · functional model ids in the canonical layer ~131 files → 0, with the 189 prose lines deliberately preserved and the 10 bead-ID lines protected by a regression test · distinct free-text `compatibility` values 40 → 0 (generated projection) · a committed capability vocabulary covering every token across 3,138 allowlist-bearing files.

**Dependencies / entry criteria.** Requires Epic 1's regeneration and corpus resolver (bead 3.1 re-measures the true migration surface **after** regeneration, because 50.1% of `docs.anthropic.com` occurrences are in generated artifacts). Owns the tool-token vocabulary that Epic 4's gate consumes.

**Proposed beads (13).**

| #    | Bead title                                                                                                                | Type · P     | Acceptance (abbreviated)                                                                                                                                                                                                              |
| ---- | ------------------------------------------------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 3.1  | Regenerate every derived artifact, then publish the true model-agnostic migration surface as a committed baseline.        | task · P0    | A tracked `RA-DATA` baseline records, post-regeneration and per classification: functional vs prose vs bead-ID model-id counts, `docs.anthropic.com` occurrences, `${CLAUDE_*}` occurrences — the real surface, not the inflated one. |
| 3.2  | Write the canonical harness-free skill contract and ship it as a versioned JSON Schema draft.                             | feature · P0 | `schemas/canonical/v0/skill-contract.schema.json` + a prose companion; `additionalProperties: false`; `UPSTREAM-PENDING` header naming the kernel issue.                                                                              |
| 3.3  | Publish a capability vocabulary that maps every tool token in the corpus to an abstract capability, under one parser.     | feature · P0 | `schemas/canonical/v0/capability-map.json` covers every token across the 3,138 allowlist-bearing files; the 21 unknown-token files are enumerated and dispositioned; **one parser, one vocabulary**.                                  |
| 3.4  | Replace free-text compatibility with declared adapters, service requirements, and unsupported capabilities in the schema. | feature · P0 | Schema adds `adapters[]` (registry enum), `requires.services[]`, `unsupported[]{capability,reason,degradation}` with `degradation` defaulting to **fail-closed**; a generator emits `compatibility` from them.                        |
| 3.5  | Add a thin-adapter conformance gate that fails when an adapter file duplicates a canonical file.                          | feature · P0 | `scripts/check-adapter-thinness.mjs` in `ci-required.needs`; fails on byte-identical files, on body/`references/`/`scripts/`/eval/license/version inside an adapter, and on an adapter capability absent from canonical.              |
| 3.6  | Convert the Codex fork in the Kobiton plugin into a real thin adapter and delete the duplicated canonical files.          | task · P1    | 27 duplicated files removed; the adapter contains only the six permitted sections; Freshie stops double-grading the plugin; the dated waiver from 3.5 is deleted in the same PR.                                                      |
| 3.7  | Classify every Claude model identifier by syntactic role and protect bead IDs from any migration tooling.                 | task · P0    | `scripts/classify-model-ids.mjs` emits three disjoint sets (functional / prose / bead-ID) plus a committed exclusion list; a unit test asserts the three known bead IDs are never rewritten.                                          |
| 3.8  | Replace functional model identifiers in the canonical layer with capability tiers that fail closed when unresolvable.     | feature · P1 | Canonical carries `model_class ∈ {reasoning-high, balanced, fast}`; adapters resolve it; **an adapter with no matching model errors** — silent substitution is a schema violation with a test proving it.                             |
| 3.9  | Introduce a portable skill-directory variable and generate the Claude-branded form in the adapter.                        | feature · P1 | Canonical bodies use `${SKILL_DIR}`; the Claude Code adapter emits `${CLAUDE_SKILL_DIR}`; the validator's existing anti-absolute-path rule is retargeted for canonical files.                                                         |
| 3.10 | Add a canonical-layer vendor-literal gate that fails when a Claude-specific token reappears in the harness-free core.     | feature · P0 | A job in `ci-required.needs` fails on a concrete model id, `${CLAUDE_*}`, `mcp__`-prefixed names, `Bash(...)` scoping, or `disallowedTools` **in a canonical-layer file**; adapters exempt by path.                                   |
| 3.11 | Backfill adapter declarations across the corpus and withdraw every untested portability claim.                            | task · P0    | Every skill declares `adapters[]`; a skill with no adapter artifact for a harness **may not list it**; the 1,409 + 45 claiming Codex/OpenClaw resolve to `adapters: [claude-code]`; a ratchet blocks new unbacked claims.             |
| 3.12 | Render the declared adapter matrix on the marketplace and retire free-text compatibility from the UI.                     | task · P2    | Detail pages render `adapters[]` + `unsupported[]` with reason text; no page reads the free-text string; route count stays within the 2,800–4,000 budget.                                                                             |
| 3.13 | Propose the canonical contract to the kernel and record the ownership boundary.                                           | task · P1    | An issue on `@intentsolutions/core` proposing `skill-contract`, `capability`, and `eval-spec` schemas, citing `schemas/canonical/v0/` as the draft; the boundary statement lands in this blueprint.                                   |

**Bead dependency graph.**

```
3.1 ──▶ 3.2 ──▶ 3.4 ──▶ 3.11 ──▶ 3.12
3.2 ──▶ 3.3 ──▶ (Epic 4) 4.2
3.5 ──▶ 3.6                    (gate first, with a dated waiver; then remove the fork)
3.7 ──▶ 3.8 ──▶ 3.10
3.9 ──▶ 3.10
3.13 after 3.2/3.3/3.4 exist as drafts
```

**Risks and mitigations.** _Withdrawing 1,454 portability claims looks like a regression_ → the PR states the honest framing: an untested claim was withdrawn, not a capability removed; the site shows `adapters:[claude-code]` as a stronger claim than an unverifiable sentence. _A model-id sweep destroying bead IDs or accurate prose_ → 3.7's three-way classifier and its regression test land before any rewrite. _The repo becoming its own schema authority_ → 3.2's `UPSTREAM-PENDING` header and 3.13's kernel issue are acceptance conditions, not follow-ups.

**Allowed scope.** `schemas/canonical/v0/`, `scripts/` (classifier, thinness gate, vocabulary), canonical-layer SKILL.md frontmatter/body in **first-party** plugins, the Kobiton `.codex/` adapter, marketplace rendering.
**PROHIBITED scope.** Any `.source.json` subtree · changing `ALWAYS_REQUIRED` · deleting the 189 prose model references · touching bead IDs · renaming the install slug.

**Claude Code execution prompt.**

> Do 3.1 first and treat its output as the only true surface — the pre-regeneration numbers are inflated by generated artifacts. Before any bulk rewrite, land 3.7's classifier and its bead-ID regression test, and show the three disjoint sets in the bead note. When you add the thinness gate (3.5), ship it with a **dated** waiver for the known Kobiton fork and delete that waiver in 3.6's PR. Never rewrite a prose or comparison model reference. Every adapter you produce must be generated by a script in `scripts/adapters/`, never hand-authored.

**Acceptance criteria.** All 13 beads closed; the vendor-literal gate and the thinness gate both in `ci-required.needs` with linked red runs; `adapters[]` present on every skill; zero free-text `compatibility` authored anywhere.

**Tests and evals.** Unit tests: the model-id classifier (functional/prose/bead-ID), fail-closed model resolution, capability-map coverage over the corpus, thinness-gate positives and negatives. E1 throughout; no behavioral eval is required to prove a contract.

**Evidence contract.** E1, plus a committed `RA-DATA` baseline (3.1) that any reviewer can regenerate.

**Rollback.** Schema and gates revert cleanly. The corpus edits in 3.8/3.9/3.11 are batched per plugin so a single revert restores a bounded set; each PR names the batch.

**Independent-review gate.** The reviewer re-runs 3.1's harness, confirms the 189 prose lines and 10 bead IDs are untouched by `git diff`, and opens their own red run against both new gates.

**Exit scorecard.** Rows 13, 14, 15, 16, 17, 18, 19, 20 at target.

**AAR + bd memory.** AAR records why "model-agnostic" was previously a string rather than a contract. `bd remember "model-id-classes: functional ids migrate, prose ids stay (189 lines), bead IDs are never touched — the beads prefix here is literally 'claude'"`.

**GitHub Issue projection.** One `epic` issue; one cluster issue for the adapter standard.

---

### EPIC 4 — Runtime safety, permissions, and MCP boundary enforcement

**Objective.** Move every safety claim onto a named enforcement boundary, or label it as prose — and close the four scanning gaps through which an unverified credential, an unscanned push, or an unproven refusal guarantee reaches production.

**Measurable outcome.** Safety claims mapped to a named boundary 0 → 100% · tracked files invisible to gitleaks 61.1% → 0 blanket file-type allowlists · blocking PR scan for unverifiable secrets 0 → 1 in `ci-required` · supply-chain scan coverage of `push: main` none → full · MCP plugins with a declared destructive policy 0/14 → 14/14, every `refuse` claim backed or withdrawn · unscoped-`Bash` and tier-2 tool-safety findings frozen by a shrink-only ratchet · the 10 shell-substitution security errors blocking on changed files.

**Dependencies / entry criteria.** Requires Epic 3's tool-token vocabulary (bead 3.3) for the allowlist gate, and Epic 6's ratchet machinery for the safety ratchets. Bead 4.5 must precede 4.6 or the new scan drowns in the same false positives and gets neutered.

**Proposed beads (14).**

| #    | Bead title                                                                                                        | Type · P                | Acceptance (abbreviated)                                                                                                                                                                                                         |
| ---- | ----------------------------------------------------------------------------------------------------------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 4.1  | Publish a register of every safety property the platform claims and the boundary that enforces it.                | task · P0               | A tracked `DR-STND` register: each claim's exact public wording and location, the enforcing artifact (harness runtime / CI job file:line / MCP server code / **prose only**), and which harnesses it holds for.                  |
| 4.2  | Add a tool-token vocabulary gate that fails on any `allowed-tools` token outside the declared universe.           | feature · P0            | A job in `ci-required.needs`; the 21 verified offending files are fixed or dispositioned first so the gate adds zero new baseline debt.                                                                                          |
| 4.3  | Freeze unscoped `Bash` declarations with a shrink-only ratchet so no new skill can add one.                       | feature · P0            | Triple-keyed ratchet pins the current bare-`Bash` skills and tier-2 tool-safety findings; totals monotone non-increasing; baseline bot-written on merge.                                                                         |
| 4.4  | Make the shell-substitution security rule blocking on changed files.                                              | feature · P0            | `[security] YAML field contains shell substitution` blocks on PR-changed files; the 10 existing occurrences are pinned and **never waivable**; a new one fails the build.                                                        |
| 4.5  | Replace the gitleaks file-type blanket allowlist with path-anchored, reason-carrying exceptions.                  | feature · P0            | `.gitleaks.toml` no longer allowlists `SKILL.md`/`README.md`/`CHANGELOG.md`/`references/*.md` by type; each surviving exception is a specific path with a written reason and expiry.                                             |
| 4.6  | Add a blocking, diff-scoped scan for unverifiable secrets on every pull request.                                  | feature · P0            | A trufflehog job **without** `--only-verified`, scoped to changed files, on `pull_request`, in `ci-required.needs`. Closes the union gap: a rotated key or internal token in a SKILL.md is currently invisible to both scanners. |
| 4.7  | Run the supply-chain content scan on pushes to main, not only on pull requests.                                   | bug · P0                | `scan-synced-content.mjs --changed-only` also runs on `push: main`; REFUSE stays exit 2 and unwaivable; the PR states the residual (`enforce_admins:false`).                                                                     |
| 4.8  | Give the MCP config validator a deadline and make it fail closed on the classes it already detects.               | bug · P1                | `validate-plugins.yml:98`'s `\|\| true` gains a `REPORT-ONLY-UNTIL:` marker **and** the unambiguous classes (invalid JSON, missing transport-required fields) become blocking.                                                   |
| 4.9  | Prove or withdraw the Dolt MCP server's destructive-verb refusal guarantee.                                       | feature · P0            | Either a conformance test drives the plugin's **actual MCP entrypoint** with destructive verbs and asserts refusal, or the README claim is withdrawn. No third option.                                                           |
| 4.10 | Require every MCP plugin to declare its destructive-operation policy and back it with an executable refusal test. | feature · P0            | All 14 declare `destructive_policy ∈ {refuse, recommend-only, permit-with-confirmation, permit}` plus the enforcing artifact path; a gate fails a `refuse`/`recommend-only` declaration with no passing refusal test.            |
| 4.11 | Ratchet agent frontmatter errors so the report-only window cannot expand.                                         | task · P1               | The 253-error `--agents-only` baseline pinned with the same triple-keyed ratchet; the schema 3.11.0 body-vs-allowlist check confirmed inside the ratchet.                                                                        |
| 4.12 | Fix the agents-only compliance arithmetic so its denominator is trustworthy.                                      | bug · P2                | No more `224.1%`; a unit test asserts `0 ≤ rate ≤ 100` and `compliant ≤ total`; the 253 figure confirmed unaffected. _(Owner: Epic 6 bead 6.9 — this row is the consumer.)_                                                      |
| 4.13 | Define fail-closed degradation for safety controls a harness cannot enforce, and gate on it.                      | feature · P0            | A skill whose posture depends on a denylist must declare, per adapter, either an enforcement mechanism or `unsupported[].degradation: fail-closed`; a gate fails silent-drop.                                                    |
| 4.14 | Rotate the plaintext MCP credential on this box and refuse to start on a plaintext key in an MCP config.          | task · P0 (owner-gated) | The live-shaped key is rotated **by the owner** and moved to SOPS; a pre-flight check refuses to proceed on a plaintext `env` key. See § 18.7.                                                                                   |

**Bead dependency graph.**

```
(Epic 3) 3.3 ──▶ 4.2
(Epic 6) ratchet ──▶ 4.3, 4.11
4.5 ──▶ 4.6                    STRICTLY SERIAL — de-blanket before adding the unverified scan
4.2 ──▶ 4.3 ──▶ 4.4            vocabulary, then scope, then security class
4.9 ──▶ 4.10                   prove one, then require all fourteen
4.1, 4.7, 4.8, 4.12, 4.13 independent
4.14 owner-gated, parallel from day 0
```

**Risks and mitigations.** _The unverified-secret scan flooding PRs_ → 4.5 lands first and the scan is diff-scoped; the first week runs with a `REPORT-ONLY-UNTIL` marker and a measured false-positive rate before it blocks. _Withdrawing a refusal guarantee looks bad_ → withdrawing an unproven guarantee is a rank-3 improvement; the alternative is a live false safety claim. _Ratchet flap_ → 4.3/4.11 inherit Epic 6's two-week R1 observation window.

**Allowed scope.** `.gitleaks.toml`, `.github/workflows/`, `scripts/`, MCP plugin manifests and their tests, the enforcement register document.
**PROHIBITED scope.** Changing branch protection or `enforce_admins` (owner-only, § 18.5) · rotating any credential without an explicit yes · editing mirror content · adding a fourth required context.

**Claude Code execution prompt.**

> Land 4.1 first: you cannot close a boundary you have not named. For every claim in the register, the enforcing artifact is a file:line or the literal words "prose only" — no third answer. Land 4.5 before 4.6 and record the measured false-positive count from the first week. For 4.9, drive the **actual MCP entrypoint**, not a unit-tested helper; if you cannot make it refuse, withdraw the claim in the same PR. Never rotate a credential — prepare the change, state it, and stop.

**Acceptance criteria.** All 14 beads closed; three new blocking jobs inside `ci-required` with linked red runs; the enforcement register published with zero unmapped claims; 14/14 MCP policies declared.

**Tests and evals.** Refusal conformance tests per MCP plugin (destructive verb in → refusal out). Negative tests for the vocabulary gate, the denylist fail-closed gate, and the shell-substitution rule. E1 for structure; **E3 is required for any surviving safety claim** — a refusal test is precisely a baseline delta.

**Evidence contract.** E1 for gates; E3 for refusal guarantees (an adversarial case must fail the un-fixed variant). The register cites file:line for every enforced claim.

**Rollback.** Each gate is one job removal. `.gitleaks.toml` reverts cleanly. The credential rotation is **not** revertible by git and is owner-executed.

**Independent-review gate.** The reviewer independently drives each MCP refusal test, confirms the gitleaks config no longer contains file-type blankets, and opens their own red run for each new blocking job.

**Exit scorecard.** Rows 8, 9, 46, 47, 48, 49, 50, 51 at target.

**AAR + bd memory.** AAR records the union gap between `--only-verified` and the file-type blanket. `bd remember "secret-scan-union-gap: gitleaks blanket-allowlisted every SKILL.md/README/references md (61.1% of tracked files) while trufflehog ran --only-verified on a schedule — an unverifiable real credential was invisible to both"`.

---

### EPIC 5 — Dolt, Freshie, provenance, and real integration testing

**Objective.** Make the inventory and evidence pipeline refuse to publish anything it cannot substantiate — no phantom runs, no lagging exports, no unretained proofs, no counterfeit assets promoted into the public mirror.

**Measurable outcome.** Inventory header-vs-rows delta (currently +609 on run 11, and run 6 at 3,000/19 would pass today's gate) → 0, blocking · tracked export lag 1 run → 0, gated · retained primary eval artifacts 0 → 100% of E2/E3 · `forge_proofs` rows carrying an evidence class 0/3 → 3/3 (all demoting to E0, correctly) · Freshie tests unit-only → ≥1 hermetic end-to-end cycle against scratch databases · `promote-curated.yml`'s two `|| true` swallows → 0.

**Dependencies / entry criteria.** Requires Epic 1's magic-byte sniff (1.3) for the promotion path. Owns the evidence-class standard (5.11) that Epic 9 implements and Epic 10 consumes.

**Proposed beads (13).**

| #    | Bead title                                                                                                | Type · P     | Acceptance (abbreviated)                                                                                                                                                                                                                                                                                                                                                          |
| ---- | --------------------------------------------------------------------------------------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 5.1  | Make the inventory exporter refuse any run whose header count disagrees with its own row count.           | bug · P0     | `gate_run_completeness()` additionally asserts `discovery_runs.total_skills == COUNT(*) …` and raises `SyncError` naming both numbers; the existing `IS NULL` check is retained (different failure); unit tests reconstruct run 6's exact shape; a dry run against the current DB **fails**, captured verbatim. The producer fix is a separate bead filed before this one closes. |
| 5.2  | Rename the behavioral-eval run column so it can never be joined against the discovery run counter.        | bug · P1     | `forge_proofs.run_id` → `jrig_run_id` across schema, recorder, enricher, and export column lists.                                                                                                                                                                                                                                                                                 |
| 5.3  | Detect files whose extension claims a binary type while their bytes are text, and refuse to promote them. | bug · P0     | The promotion path fails closed on extension/magic-byte disagreement; the drift gate can no longer print "in sync" while republishing counterfeits.                                                                                                                                                                                                                               |
| 5.4  | Gate the tracked grade exports so they can never lag the latest exported inventory run.                   | feature · P1 | A check asserts `grade-histogram.json.run_id == MAX(discovery_runs.id)` and that `grades.csv` row count matches; today this fails (exports at run 10, DB at run 11).                                                                                                                                                                                                              |
| 5.5  | Quarantine the counterfeit asset files and record a disposition for each.                                 | task · P1    | Each of the 12 gets a recorded disposition (replace / rename / withdraw the claim); none remains in the curated mirror.                                                                                                                                                                                                                                                           |
| 5.6  | Make the curated-mirror promotion workflow fail closed instead of swallowing grading and sync failures.   | bug · P0     | `promote-curated.yml:90-91`'s two `\|\| true` swallows are removed or bounded with `REPORT-ONLY-UNTIL:`; a forced failure produces a red run.                                                                                                                                                                                                                                     |
| 5.7  | Build a hermetic end-to-end fixture that runs the whole inventory cycle against scratch databases.        | test · P0    | `rebuild-inventory` → `--populate-db` → `dolt-sync` → `promote-to-curated` against temp SQLite, temp Dolt, and a fake remote; **refuses to run** if a `dolt sql-server` holds port 3308.                                                                                                                                                                                          |
| 5.8  | Add a negative test proving a leaked eval runtime table aborts the public export.                         | test · P0    | A planted j-rig run table causes `gate_export_allowlist()` to hard-fail before any push.                                                                                                                                                                                                                                                                                          |
| 5.9  | Make the exporter refuse to run while a Dolt sql-server holds the repository.                             | feature · P1 | Mechanical refusal replaces the prose single-writer rule.                                                                                                                                                                                                                                                                                                                         |
| 5.10 | Prove the tracked grade exports are byte-reproducible from a clean checkout.                              | test · P1    | A test regenerates `grades.csv` + `grade-histogram.json` and diffs.                                                                                                                                                                                                                                                                                                               |
| 5.11 | File the evidence standard that assigns every quality claim an evidence class and a retention rule.       | task · P0    | § 9 filed as a canonical `000-docs` record: E0–E3, in-band class carriage, retention as a validity condition, claim ceiling, no self-approval, storage split. **This epic owns it; Epics 9 and 10 consume it.**                                                                                                                                                                   |
| 5.12 | Demote every unretained behavioral proof to an assertion and take the verified badge dark.                | bug · P0     | All 3 `forge_proofs` rows demote to E0 (their own text says the primary artifact was not retained); the public badge goes dark; the demotion is published rather than hidden.                                                                                                                                                                                                     |
| 5.13 | Make the exporter recover a stranded run tag exactly once after a failed push.                            | bug · P2     | A failed DoltHub push leaves a recoverable state; recovery is idempotent and tested.                                                                                                                                                                                                                                                                                              |

**Bead dependency graph.**

```
5.11 ──▶ 5.12                  class the evidence, then demote what fails the class
5.1 ──▶ 5.4                    run coherence before export coherence
(Epic 1) 1.3 ──▶ 5.3 ──▶ 5.5
5.6 independent · 5.9 ──▶ 5.7 ──▶ 5.8, 5.10
5.2 ──▶ (Epic 9) 9.3
5.13 independent
```

**Risks and mitigations.** _A blocking coherence gate stops all exports on day one_ → that is the intended behavior; 5.1's acceptance explicitly requires the dry run to fail and the message to be captured, and the producer fix is filed as its own bead before 5.1 closes. _The hermetic test touching the live DB_ → 5.7 refuses to run when port 3308 is held and uses only temp paths; a reviewer verifies with `lsof`.

**Allowed scope.** `freshie/`, `scripts/record-jrig-proofs.mjs`, `scripts/run-jrig-eval.sh`, `promote-curated.yml`, the evidence-standard document.
**PROHIBITED scope.** Any write to the public DoltHub record from CI · running `j-rig eval --db freshie/inventory.sqlite` · rewriting Dolt history · deleting `/backup` or `~/backups`.

**Claude Code execution prompt.**

> Land 5.11 before 5.12 — you cannot demote a claim before the class exists that demotes it. For 5.1, the acceptance is that the dry run **fails**; capture the message verbatim and file the producer bead before closing. Never point `j-rig` at the tracked inventory database; use the wrapper and a `/dev/shm` scratch DB. Before running anything that writes Dolt, confirm no `dolt sql-server` is listening on 3308 and stop if one is.

**Acceptance criteria.** All 13 beads closed; the coherence, export-lag, and allowlist gates blocking with linked red runs; one hermetic cycle test in CI; the evidence standard filed and linked from `STANDARDS.md`.

**Tests and evals.** Unit: run-coherence (run 6's shape), export lag, magic-byte promotion, allowlist leak. Integration: the hermetic cycle. Reproducibility: byte-identical export regeneration. E1 throughout, with 5.12 producing the first honest E0 classification.

**Evidence contract.** E1 for gates. 5.12's demotion is itself the evidence contract working: a claim whose artifact cannot be retrieved is not evidence.

**Rollback.** All gates revert as single commits; no data is written and no Dolt history is rewritten by any bead in this epic.

**Independent-review gate.** The reviewer runs the hermetic test on a clean checkout, confirms it refuses when 3308 is held, and confirms the three demoted rows render no badge anywhere on the built site.

**Exit scorecard.** Rows 12, 52, 53, 54, 55, 56, 58, 59 at target.

**AAR + bd memory.** AAR records that every inventory run's header disagreed with its rows, and that run 6 (3,000 header / 19 rows) would have passed the old gate. `bd remember "freshie-run-coherence: gate_run_completeness tested only IS NULL; every run 6-11 header disagrees with its row count (run 11: 3069 vs 3678)"`.

---

### EPIC 6 — Marketplace validation and the legacy-debt ratchet

**Objective.** Close the open intake. Today a `SKILL.md` with zero of the eight required fields merges clean; after this epic, the existing 7,687 errors are pinned and no new `(path, rule, field)` triple can enter.

**Measurable outcome.** `--marketplace` runs that block a merge 0 → 1 · new marketplace errors admissible per PR: unbounded → 0 · `totals.errors` monotone non-increasing · `grade_A_plus_B_pct` non-decreasing · corpus deletion as compliance blocked · agent baseline 253 pinned before its `REPORT-ONLY-UNTIL: 2026-10-31` · unbounded correctness swallows ≥4 → 0.

**Dependencies / entry criteria.** Requires Epic 1's corpus resolver (the baseline must name its `corpus_definition`) and a quiet tree (the baseline is emitted **in CI**, never locally). **Blocks:** Epic 4's safety ratchets and all of Epic 8's remediation.

**Proposed beads (14).**

| #    | Bead title                                                                                           | Type · P     | Acceptance (abbreviated)                                                                                                                                                                                                                                  |
| ---- | ---------------------------------------------------------------------------------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 6.1  | Add a mode that emits a triple-keyed compliance baseline from a full marketplace validator run.      | feature · P0 | `--emit-baseline` produces the § 10.2 JSON keyed `(path, rule_id, field)`, with `schema_version`, `corpus_definition`, `rule_inventory`, and `generated_from`.                                                                                            |
| 6.2  | Emit and commit the pinned compliance baseline in a pull request that changes nothing else.          | task · P0    | Baseline emitted **in CI** from a quiet tree; the PR touches exactly one file; CODEOWNERS-approved.                                                                                                                                                       |
| 6.3  | Block any marketplace error that is not already in the pinned baseline.                              | feature · P0 | R1 live; a planted new error fails; existing 7,687 keep merging.                                                                                                                                                                                          |
| 6.4  | Add the compliance ratchet as a blocking job inside the plugin validation workflow.                  | feature · P0 | Job inside `validate-plugins.yml`, listed in `ci-required.needs`; runtime ≤120 s or the trade is stated.                                                                                                                                                  |
| 6.5  | Reject a baseline whose rule inventory or schema version no longer matches the validator.            | feature · P0 | An unknown rule id or a `SCHEMA_VERSION` drift fails, forcing a conscious re-baseline.                                                                                                                                                                    |
| 6.6  | Refuse permissive baseline policy-envelope changes outside an owner-authorized baseline-only change. | feature · P0 | Strict-subset/monotone diff vs `origin/main`; any permissive entry, metric, schema, inventory, corpus, denominator, or provenance change requires a one-file PR that byte-matches the immutable artifact from an owner-dispatched default-branch capture. |
| 6.7  | Make the total error count and the A-plus-B share monotone non-increasing.                           | feature · P0 | R2 + R4 live after the two-week R1 observation window.                                                                                                                                                                                                    |
| 6.8  | Refuse a corpus shrink that is not matched by a catalog change.                                      | feature · P0 | R3 live: `corpus.skill_files` may not fall >2% without a matching catalog diff.                                                                                                                                                                           |
| 6.9  | Fix the agent compliance-rate arithmetic that reports two hundred twenty-four percent.               | bug · P1     | **Owner of this fix.** `0 ≤ rate ≤ 100`, `compliant ≤ total`, unit-pinned; the 253 error figure unchanged.                                                                                                                                                |
| 6.10 | Pin the agent-frontmatter baseline and make new agent violations blocking.                           | feature · P1 | Same machinery on `--agents-only`, landed at or before 2026-10-31.                                                                                                                                                                                        |
| 6.11 | Give every remaining correctness swallow an expiry date and a tracking bead.                         | task · P1    | **Owner of the bounded-swallow rule.** `validate-plugins.yml:98`, `:658` and every peer carry a `REPORT-ONLY-UNTIL:` marker.                                                                                                                              |
| 6.12 | Extend the deadline enforcer to scan scripts, baselines, and the scan allowlist.                     | feature · P2 | `check-ci-deadlines.py` scans beyond `.github/workflows/`.                                                                                                                                                                                                |
| 6.13 | Assert that the documented required-check set matches the actual one.                                | feature · P2 | Consumes Epic 2 bead 2.7; no second implementation.                                                                                                                                                                                                       |
| 6.14 | Shrink the baseline once by fixing a single mechanical error class end to end.                       | task · P1    | One rule id cleared corpus-wide; the baseline shrinks by exactly that count, bot-written on merge — proving the ratchet's only legal direction.                                                                                                           |

**Bead dependency graph.**

```
6.1 ──▶ 6.2 ──▶ 6.3 ──▶ 6.4        STRICTLY SERIAL
6.4 ──(≥2 weeks flap observation)──▶ 6.7 ──▶ 6.8
6.5, 6.6 land with 6.3 (anti-gaming is not a follow-up)
6.9 ──▶ 6.10
6.11 ──▶ 6.12
6.14 last — it is the proof, not the goal
```

**Risks and mitigations.** _An unstable gate indistinguishable from a regression_ → the mandatory two-week R1 window before R2/R3/R4. _Someone re-baselines inside a fix PR_ → 6.6's subset-only diff plus owner-run/artifact provenance. _The baseline becoming an aspiration_ → the baseline is bot-written on merge after the gate passed; humans lower it only by fixing artifacts (6.14 is the worked example).

**Allowed scope.** `scripts/validate-skills-schema.py` (new `--emit-baseline` mode only), `scripts/.marketplace-compliance-baseline.json`, `validate-plugins.yml`, `capture-marketplace-compliance-baseline.yml`, `scripts/check-ci-deadlines.py`.
**PROHIBITED scope.** Changing `ALWAYS_REQUIRED`, the tier model, or error-vs-warning semantics · hand-editing the baseline · adding a fourth required context · lowering a threshold to make a PR pass.

**Claude Code execution prompt.**

> Emit the baseline **in CI**, from a quiet default-branch tree, in a PR that changes exactly one file. Any permissive policy-envelope exception must byte-match the immutable artifact from a repository-owner dispatch; a branch name or human-authored baseline is never authority. This covers entries, monotone totals, schema/rule inventory, corpus/denominators, and provenance—not only new triples. Land R1 alone and leave it alone for two weeks — record the flap rate in the bead note before you tighten anything. If a PR of yours fails the ratchet, fix the artifact; never touch the baseline. The baseline's only legal edit is a bot-authored shrink on merge. Do not add a fourth required status context: the ratchet is a job inside `validate-plugins.yml`.

**Acceptance criteria.** All 14 beads closed; R1–R4 live; the six anti-gaming defeats each demonstrated by a linked red run; runtime within budget; agent baseline pinned.

**Tests and evals.** Six anti-gaming tests (new path, renamed rule, in-PR re-emit, weakened rule, mass delete, hand-lowered total), plus a runtime assertion. E1.

**Evidence contract.** E1. Every rule's red run is linked from the epic's AAR, each opened by someone other than the implementer.

**Rollback.** Remove the ratchet job from `ci-required.needs` — one line, no corpus change. The baseline file may stay; it is inert without the job.

**Independent-review gate.** The reviewer opens all six anti-gaming red runs themselves and confirms the baseline's git history contains only bot-authored commits after 6.2.

**Exit scorecard.** Rows 4, 10, 40, 50 at target; row 7's structural mass pinned pending Epic 8.

**AAR + bd memory.** AAR states plainly that before this epic a zero-field `SKILL.md` merged clean. `bd remember "marketplace-ratchet: baseline is keyed (path, rule_id, field), emitted in CI only, shrink-only, bot-written on merge; --marketplace blocks via a job inside validate-plugins.yml, never a new required context"`.

---

### EPIC 7 — Versioning, packaging, release, and supply-chain hardening

**Objective.** Make publication unreachable without a green gate, stop publishing other people's work under the Intent Solutions identity, and turn a release into a five-tuple that cannot half-succeed.

**Measurable outcome.** Provenance-marked repository mirrors 63 (58 scoped, 5 non-scoped) → 0 publishable · independent boundaries preventing mirror publication 0 → 2 · gate dependencies on the publish path 0 → 3 · release-path swallows 3 → 0 · `skip_tests` present → removed · SBOMs 0 → ≥15 · third-party actions on mutable tags in privileged workflows 6 → 0 · Dependabot absent → present · mirrors shipping license text 30/63 → 63/63, fail-closed.

**Dependencies / entry criteria.** Bead 7.1 has **zero prerequisites and is the recommended first bead of the entire program** (§ 15). Locks 1–2 of bead 7.3 are delegable; lock 3 (the protected Environment) is owner-only (§ 18.4).

**Proposed beads (16).**

| #    | Bead title                                                                                     | Type · P   | Acceptance (abbreviated)                                                                                                                                                                                                                                               |
| ---- | ---------------------------------------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 7.1  | Mark every externally mirrored package private so it can never be published.                   | task · P0  | All 63 repository `package.json` files under a directory containing `.source.json` carry `"private": true` (58 scoped npm packages plus 5 non-scoped mirrors); a tree-wide invariant test fails if a future mirror lands without it.                                   |
| 7.2  | Refuse to publish any plugin directory that carries an upstream source record.                 | task · P0  | Both publish workflows skip candidates where `.source.json` exists, logging each skip by name; a dry run lists 0 mirror packages; covered by a fixture test.                                                                                                           |
| 7.3  | Make npm publication unreachable without the three required checks passing.                    | task · P0  | `workflow_run` + `conclusion == 'success'`; a preflight job re-queries check-runs for the head SHA (survives an admin merge); `NPM_TOKEN` moved to a protected `npm-production` Environment (**owner action**); a deliberately-red branch proves publish does not run. |
| 7.4  | Fail the release run when a tag, release, or evidence row is missing.                          | task · P1  | The three `⚠`-swallows removed; a release asserted as the five-tuple; a fault-injection run produces a red run and no orphan npm publish.                                                                                                                              |
| 7.5  | Run the version-surface checker as a blocking step of the validate job.                        | task · P1  | `reconstruct-versions.mjs --check` blocks.                                                                                                                                                                                                                             |
| 7.6  | Declare the npm-version and display-version split wherever a version is shown.                 | task · P2  | The 99.3% divergence is declared, not eliminated.                                                                                                                                                                                                                      |
| 7.7  | Bump the kernel and eval CLI pins together and re-baseline the shadow soak.                    | chore · P1 | _Citation only — Epic 9 bead 9.10 owns this._                                                                                                                                                                                                                          |
| 7.8  | Block ordering violations in the vendor-hash gate and route staleness to a human.              | chore · P1 | _Citation only — Epic 9 beads 9.10/9.12 own this._                                                                                                                                                                                                                     |
| 7.9  | Pin every third-party action in the privileged workflows to a commit SHA.                      | task · P1  | 6 distinct actions / 13+ uses SHA-pinned in every privileged or signing workflow.                                                                                                                                                                                      |
| 7.10 | Add dependency update automation for actions and npm.                                          | task · P1  | Grouped Dependabot config; the 22 open advisories gain a remediation path.                                                                                                                                                                                             |
| 7.11 | Pin the harness that implements a required check to an exact version.                          | chore · P1 | **Owner of this fix.** `@intentsolutions/audit-harness` `^1.3.1` → exact `1.3.1`, with the rationale in the commit: it implements the required `skill-conform` context.                                                                                                |
| 7.12 | Retire the release workflow's test-skipping input.                                             | task · P1  | `skip_tests` **deleted**, not bounded — a release that cannot pass validation is not a release.                                                                                                                                                                        |
| 7.13 | Stage the license-defect remediation packet for owner decision, without mutating the registry. | task · P0  | A document-only packet covering the AGPL artifact and the current 53 clearly third-party / 5 ambiguous cohort; **no registry mutation**. Longest lead time in the program — start day 0. See § 18.1/17.2.                                                              |
| 7.14 | Require license text in every mirror's file include list and fail the sync without it.         | task · P0  | 63/63 mirrors ship `LICENSE`/`COPYING`; a missing one is a hard sync failure.                                                                                                                                                                                          |
| 7.15 | Emit an SBOM for every published package and reference it from the evidence bundle.            | task · P2  | CycloneDX, `plugins/mcp/**` first; digest referenced from the bundle.                                                                                                                                                                                                  |
| 7.16 | Extend the signed-evidence workflow past its two gates to the required set and each publish.   | task · P1  | Signed evidence covers the required gates and every publish, not 2 of ~20.                                                                                                                                                                                             |

**Bead dependency graph.**

```
7.1 ──▶ 7.2 ──▶ 7.3 ──▶ 7.4        STRICTLY SERIAL: quarantine → gate → evidence
7.13 parallel from day 0 (owner-input-gated, longest lead time)
7.9 ──▶ 7.10 · 7.5 ──▶ 7.6 · 7.14 independent · 7.12 independent
7.15, 7.16 after 7.4
7.7/7.8 are citations of Epic 9; 7.11 is owned here and consumed by Epic 9
```

**Risks and mitigations.** _Marking 63 provenance-marked packages private breaks a consumer_ → none has a documented consumer; the change is additive and `git revert`-able; the PR enumerates every package. _Lock 3 blocking the epic_ → locks 1 and 2 land independently and each is sufficient alone; lock 3 is escalated, not blocked on. _The AGPL packet forcing a rushed public action_ → 7.13 is document-only by construction; quarantine (7.1) removes the time pressure from the fix.

**Allowed scope.** `plugins/**/package.json` (the `private` flag only), publish and release workflows, `.github/dependabot.yml`, action pins, `sources.yaml` include lists, the remediation packet document.
**PROHIBITED scope.** **Any npm registry mutation** (publish, deprecate, unpublish) · creating or modifying GitHub Environments · contacting any upstream contributor · changing branch protection · editing mirror content.

**Claude Code execution prompt.**

> Start with 7.1 and finish it in one sitting: one `"private": true` per mirrored package plus a tree-wide invariant test. It touches no corpus file, no catalog, no workflow logic, and reverts exactly. Then 7.2, then 7.3's locks 1 and 2 — stop at lock 3 and escalate. Prepare 7.13 as a document only: no npm command, no upstream contact, no issue opened on anyone else's repo. Any contributor-facing wording is drafted for sign-off, never posted.

**Acceptance criteria.** All 16 beads closed or escalated with a recorded owner decision; 0 mirror packages publishable; a red-branch proof that publish does not run; the five-tuple asserted; SBOMs emitted for `plugins/mcp/**`.

**Tests and evals.** Invariant test over the tree (`.source.json` ⇒ `private: true`); publish-filter fixture test; fault-injection release run; SHA-pin assertion over privileged workflows. E1.

**Evidence contract.** E1, plus signed evidence bundles (7.16) for the required gates and each publish. The red-branch publish proof is linked from the epic AAR.

**Rollback.** 7.1/7.2/7.4/7.9/7.12 revert cleanly. **7.3 lock 3 does not** — moving `NPM_TOKEN` back out of the Environment is a documented, owner-executed two-step, stated in the PR.

**Independent-review gate.** The reviewer independently pushes a red branch and confirms no publish job runs, and confirms `git ls-files '*.source.json'` maps 1:1 onto packages carrying `private: true`.

**Exit scorecard.** Rows 28, 29, 30, 31, 32, 33, 34, 35, 36, 37 at target.

**AAR + bd memory.** AAR records that mirror non-publication previously depended on an unrelated script declining to bump a version — defense by side-effect. `bd remember "mirror-publish-boundary: 63 provenance-marked repository package mirrors (58 scoped, 5 non-scoped) were publishable via push:main with zero gate; the boundary is now private:true + a .source.json publish filter + three publish locks"`.

---

### EPIC 8 — Legacy certification, remediation, quarantine, and archival

**Objective.** Assign every graded artifact a machine-derived disposition, then execute the mechanical migrations in reviewed batches — so the corpus stops being an undifferentiated 7,687-error mass and becomes a ledger with named buckets.

**Measurable outcome.** Graded artifacts with a machine-assigned disposition 0 → 3,679 · A/B artifacts failing the gate 962 → 0 among certified, with the number published · counterfeit assets 12 → 0 · shell-substitution errors 10 → 0 by hand · mirrors carrying a marketplace grade they did not earn ~313 → 0 (quarantined or CERTIFY-UPSTREAM) · structural error classes 6,832 → 0 in reviewed batches.

**Dependencies / entry criteria.** **Cannot start before Epic 6's ratchet is live** (otherwise remediation and intake are indistinguishable), Epic 1's resolver exists, and Epic 5's evidence standard is filed. Longest-running epic; its batches run in the background of everything after E6.

**Proposed beads (15).**

| #    | Bead title                                                                                     | Type · P     | Acceptance (abbreviated)                                                                                                                                 |
| ---- | ---------------------------------------------------------------------------------------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 8.1  | Publish the disposition ledger that assigns every graded artifact a bucket.                    | feature · P0 | Every one of the 3,679 graded artifacts carries a first-match-wins § 8 disposition, derived by machine, republishable from one command.                  |
| 8.2  | Reject any file whose bytes contradict its declared extension.                                 | feature · P0 | Corpus-wide gate (Epic 1 owns the promotion-path half; this is the CI half).                                                                             |
| 8.3  | Replace or withdraw every counterfeit asset and the claims that reference them.                | task · P0    | 12 → 0; each referencing body updated; grade impact recorded.                                                                                            |
| 8.4  | Remove the shell substitution from skill frontmatter by hand.                                  | bug · P0     | 10 → 0; hand-reviewed, never scripted; each fix explained.                                                                                               |
| 8.5  | Quarantine every external mirror that fails the gate so it stops carrying a marketplace grade. | task · P0    | ~312 mirrors dispositioned QUARANTINE or CERTIFY-UPSTREAM; **no mirror file is edited**.                                                                 |
| 8.6  | Remove the duplicate catalog entries and delete the stale catalog shadow.                      | task · P1    | Consumes Epic 1 beads 1.1/1.2; no second implementation.                                                                                                 |
| 8.7  | Fix the impossible compliance arithmetic in agent-only validator mode.                         | bug · P1     | Consumes Epic 6 bead 6.9.                                                                                                                                |
| 8.8  | Migrate the missing-frontmatter-field class in reviewed batches.                               | task · P1    | 728 errors cleared in bounded batches with re-validation per batch; the ratchet shrinks by exactly the cleared count.                                    |
| 8.9  | Migrate the missing-body-section class in bounded batches with re-validation.                  | task · P1    | 6,104 errors cleared; **sections must be substantive** — a header-only stub fails the stub assertion.                                                    |
| 8.10 | Scope every unscoped tool grant and justify the ones that must stay broad.                     | task · P0    | Each of the 222 either scoped or carrying a Safety Justification that **names the operation**; human judgment required, scripts prohibited.              |
| 8.11 | Take the unbacked verification badge dark until an evidence class supports it.                 | bug · P0     | Consumes Epic 9 bead 9.2.                                                                                                                                |
| 8.12 | Make the inventory run stamp self-consistent and gate the export against its own header.       | bug · P0     | Consumes Epic 5 bead 5.1.                                                                                                                                |
| 8.13 | Build the end-to-end inventory integration test against a scratch database.                    | test · P0    | Consumes Epic 5 bead 5.7.                                                                                                                                |
| 8.14 | Archive the dead-domain and superseded references outside the authority documents.             | task · P2    | Consumes Epic 1 bead 1.13 after Epic 2's freeze.                                                                                                         |
| 8.15 | Certify the first cohort with real behavioral evidence and publish grades with their class.    | feature · P1 | A capped cohort (10–15 skills, § 18.6) reaches E2/E3 with retained hash-matched artifacts; grades publish with their evidence class and a `recall_note`. |

**E8.8 ownership correction (2026-08-30).** The original 728-record row remains the
ratified historical baseline, but its literal remediation reading conflicts with this epic's
own `.source.json` stop-rule. A clean run at base `478aaf177` reproduces 728 missing-required-
frontmatter records across 294 skills: **one editable first-party record** (Hyperfocus,
`allowed-tools`) and **727 upstream-owned mirror records**. Commit `7ed360083` clears the sole
first-party record by declaring the minimal `Read` capability. Mirror bytes are not credited as
remediation: commit `1243dac98` removed 137 failing mirror records, and `2aba004d4` removed or
rewrote 12 `llm-box` records while introducing two `x-twitter-scraper` records. The governed
current state is 580 records across 265 mirror skills, all ledgered `QUARANTINE`, and zero
first-party records. Therefore the operative acceptance is: editable first-party debt reaches
and remains at zero; every raw mirror finding stays unedited and quarantined; the structural
ratchet fails any first-party growth or equal-count swap. The correction changes neither the
historical count nor the prohibition on editing upstream-owned files.

**Bead dependency graph.**

```
(Epic 6 ratchet) ──▶ 8.8, 8.9, 8.10        remediation is meaningless before the intake closes
8.1 ──▶ 8.5, 8.8, 8.9, 8.10                the ledger assigns the buckets the batches execute
8.2 ──▶ 8.3
8.4 standalone, hand-only
8.6/8.7/8.11/8.12/8.13/8.14 are consumers of Epics 1/5/6/9 — no second implementation
8.15 last, and only after § 18.6 is approved
```

**Risks and mitigations.** _Bulk remediation producing header-only stubs_ → 8.9's stub assertion fails a section that adds a heading without substance; batches are capped and re-validated. _Editing a mirror while "remediating"_ → 8.5 is quarantine-or-attribute only, and CI fails any diff under a `.source.json` ancestor. _Cost overrun on 8.15_ → the cohort is capped and approved per cohort, never per run.

**Allowed scope.** First-party corpus files, the disposition ledger, the curated mirror regeneration.
**PROHIBITED scope.** **Any edit under a `.source.json` ancestor** · scripting a fix for a G4 safety class · deleting a plugin to improve a percentage · publishing a certification without a retained artifact.

**Claude Code execution prompt.**

> Do not start any batch until the ratchet is live — otherwise you cannot tell remediation from intake. Run 8.1 first and let the machine assign every disposition; do not hand-pick. Batches are bounded (≤50 files), each re-validated, each shrinking the baseline by exactly the count you cleared. For the safety classes (8.4, 8.10), work by hand and explain each decision in the bead note; a script is a rejection. If a file's tree contains `.source.json`, stop — that is upstream's file.

**Acceptance criteria.** All 15 beads closed; every graded artifact carries a disposition; structural classes cleared; the certified cohort published with its class and its backlog beside it.

**Tests and evals.** Stub assertion for added sections; disposition-ledger reproducibility test; per-batch re-validation. **8.15 requires E2/E3**: committed `eval-spec.yaml`, pinned tool/kernel/provider/model, retained hash-matched `--json`, and a `baseline_delta` from a deliberately-broken variant.

**Evidence contract.** E1 for migrations; E2/E3 for the certified cohort, with retention as a validity condition.

**Rollback.** Each batch is one revert. The disposition ledger is regenerable. 8.15's certifications are revoked by demoting the ledger rows, which is an ordinary write, not a deletion.

**Independent-review gate.** The reviewer re-derives the disposition ledger from a clean checkout and confirms the bucket counts, samples 10 migrated files for substantive sections, and independently verifies one certified skill's artifact hash.

**Exit scorecard.** Rows 6, 7, 8, 9, 11, 60 at target.

**AAR + bd memory.** AAR records that 2,331 of 3,179 plugin skills were born in a bulk generation event and never individually revisited — the real staleness signal, not calendar age. `bd remember "legacy-buckets: disposition is first-match-wins security→legal→truthfulness→ownership→unsafe→structural→clean; ~88% mechanically recoverable, ~414 items need judgment"`.

---

### EPIC 9 — Bind Intent Eval Lab and Intent OS across machine-checked boundaries

**Objective.** Make the cross-repo authority contract mechanical: evidence produced by the Lab and only consumed here, host facts owned by Intent OS and only cited here, kernel pins moved in lockstep, and no identity able to certify its own output.

**Measurable outcome.** Evidence records carrying a class, pins, and artifact hash 0 → 100% · unbacked public `verified:true` claims 1 → 0 · retained primary eval artifacts 0 → 100% of E2/E3 · ledger writes by the producing identity → refused mechanically · kernel pin 35 days stale → current, ordering blocking, staleness Slack-routed · shadow lane measuring `authoring/v1` → both lanes, `existing-PASS/kernel-FAIL` headlined · duplicated Intent OS host facts unmeasured → measured then eliminated.

**Dependencies / entry criteria.** Requires Epic 5's evidence standard (5.11) and its column rename (5.2). Owns the kernel/jrig-cli lockstep bump that Epic 7 cites.

**Proposed beads (14).**

| #    | Bead title                                                                                         | Type · P     | Acceptance (abbreviated)                                                                                                                                                                                                                       |
| ---- | -------------------------------------------------------------------------------------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 9.1  | Publish the cross-repo authority contract that names one writer per fact class.                    | task · P0    | A `000-docs` record with exactly one owner per row across this repo, the kernel, jrig-cli, the Lab, Intent OS, Freshie/Dolt, and beads.                                                                                                        |
| 9.2  | Take the verification badge claim dark until it can be re-earned from retained evidence.           | bug · P0     | `jrig-data.json` (171 bytes, no `.astro` importer) and its build step removed, **or** every entry set `verified:false` with a reason; the false badge claim in `CLAUDE.md` corrected.                                                          |
| 9.3  | Add an evidence class, pins, and artifact hash to the eval ledger schema.                          | feature · P0 | `forge_proofs` gains `evidence_class`, `artifact_sha256`, `artifact_uri`, `spec_sha256`, `tool_version`, `kernel_version`, `provider`, `model`, `recorded_by_identity`; `run_id` split into `jrig_run_id` + `discovery_run_id` with a real FK. |
| 9.4  | Demote every eval record whose primary artifact cannot be retrieved.                               | feature · P0 | Recorder and export gate set `E0` when `artifact_uri` is absent or the bytes do not hash to `artifact_sha256`; applied today this demotes 3 of 3.                                                                                              |
| 9.5  | Retain the primary eval JSON and record its hash at eval time.                                     | feature · P0 | `run-jrig-eval.sh` writes the `--json` result to a durable path **outside** `/dev/shm` (which stays reserved for the SOPS key and scratch DB) and records its hash.                                                                            |
| 9.6  | Refuse a ledger write whose signer is the identity that produced the result.                       | feature · P0 | `record-jrig-proofs.mjs` requires `recorded_by_identity` and refuses an E2/E3 write when it equals the producing identity, or when a local identity targets the real inventory.                                                                |
| 9.7  | Make an internally inconsistent inventory run fail the export instead of publishing.               | bug · P0     | Consumes Epic 5 bead 5.1.                                                                                                                                                                                                                      |
| 9.8  | Gate the tracked grade exports against lagging the local inventory run.                            | feature · P1 | Consumes Epic 5 bead 5.4.                                                                                                                                                                                                                      |
| 9.9  | Add the end-to-end Freshie cycle test against a scratch Dolt repository.                           | test · P0    | Consumes Epic 5 bead 5.7.                                                                                                                                                                                                                      |
| 9.10 | Bump the kernel and eval CLI pins in lockstep and re-baseline the shadow soak.                     | chore · P0   | **Owner of this change.** `core 0.9.0 → 0.10.0` **and** `jrig-cli 0.1.2 → 0.2.0` in one PR, both exact; shadow re-baselined in the same PR; lockfile shows one hoisted kernel copy.                                                            |
| 9.11 | Pin the harness that implements a required check to an exact version.                              | chore · P1   | Consumes Epic 7 bead 7.11.                                                                                                                                                                                                                     |
| 9.12 | Route the advisory kernel staleness violation to a lane a human reads.                             | task · P1    | `kernel-vendor-hash.yml` stays advisory and out of the required set, but a `VIOLATION` posts to Slack; verified by forcing a violation on a scratch branch.                                                                                    |
| 9.13 | Point the shadow lane at the strict authoring schema and report the only decision-relevant number. | feature · P1 | Both `authoring/v1` and `v2` lanes run; the summary leads with `existing-PASS / kernel-FAIL`.                                                                                                                                                  |
| 9.14 | Measure and then eliminate duplicated Intent OS host facts in this repo's docs.                    | task · P2    | Step 1 produces a **measured** count (today unmeasured — stated as an evidence gap, never estimated); step 2 replaces each duplication with a pointer.                                                                                         |

**Bead dependency graph.**

```
(Epic 5) 5.11 ──▶ 5.12 ──▶ 9.3 ──▶ 9.5 ──▶ 9.6      class → demote → schema → retain → no-self-approval
9.2 independent and early (a live false public claim)
9.10 ──▶ 9.13 ──▶ 9.12
9.7/9.8/9.9/9.11 are consumers — no second implementation
9.1 first (the contract the rest enforces) · 9.14 last
```

**Risks and mitigations.** _A lockstep bump splitting the kernel into two copies_ → 9.10's acceptance includes reading the lockfile and asserting one hoisted copy. _Re-baselining the shadow being read as an authority change_ → the PR states the pin/authority separation explicitly and cites the six unmet DR-049 conditions. _Retained artifacts leaking into the public DoltHub record_ → the payload store is separate from the ledger by construction (§ 9 S6) and the export allowlist has a negative test (Epic 5 bead 5.8).

**Allowed scope.** `scripts/record-jrig-proofs.mjs`, `scripts/run-jrig-eval.sh`, the ledger schema, kernel/jrig-cli/audit-harness pins, `kernel-shadow-validation.mjs`, `kernel-vendor-hash.yml`, the cross-repo contract document.
**PROHIBITED scope.** **Flipping kernel authority** · writing to Intent OS · writing to the Lab's stores · publishing any badge without a class · pointing `j-rig` at the tracked inventory DB.

**Claude Code execution prompt.**

> 9.2 first — a false public verification claim is live. Then 9.1, then the chain 9.3→9.5→9.6 in order; reordering produces a ledger that records unverifiable claims. When you bump the pins (9.10), bump both in one PR and paste the lockfile evidence showing a single hoisted kernel copy. State in that PR body, in one sentence, that this is a coupling update and not an authority flip, and cite the six unmet conditions. Never point `j-rig eval --db` at `freshie/inventory.sqlite`.

**Acceptance criteria.** All 14 beads closed; the badge dark; every ledger row classed; a refused self-approval demonstrated in a test; pins current and lockstep; both shadow lanes reporting.

**Tests and evals.** Self-approval refusal test; artifact-hash mismatch demotion test; lockfile single-copy assertion; shadow-lane regeneration diff. E1 for mechanics; the ledger itself is the E2/E3 substrate.

**Evidence contract.** E1 for the mechanics, and this epic **builds** the machinery by which E2/E3 becomes possible at all. Nothing here mints a verdict.

**Rollback.** Schema additions are additive; the demotion rule is one revert. The pin bump reverts as a pair — never one of the two.

**Independent-review gate.** The reviewer confirms no `.astro` page reads a boolean `verified`, forces a self-approval attempt and observes the refusal, and re-runs the shadow lane themselves.

**Exit scorecard.** Rows 38, 39, 54, 55, 56 at target; rows 52, 53, 58, 59 confirmed via Epic 5.

**AAR + bd memory.** AAR records the `existing-PASS/kernel-FAIL: 0` finding and why it makes `authoring/v1` the wrong flip target. `bd remember "kernel-flip-target: authoring/v1 shadow reports existing-PASS/kernel-FAIL = 0 — flipping to v1 would be a pure loss of enforcement; the flip target is v2 and all six DR-049 conditions remain unmet"`.

---

### EPIC 10 — Independent certification, launch readiness, and continuous governance

**Objective.** Define "certified" once, evaluate it from machine facts alone, make it un-self-approvable, give it an expiry, and publish the certified set beside its backlog.

**Measurable outcome.** Artifacts meeting G1–G10 ∧ E1–E6: 0 → a named, signed, defensible cohort ≥1 · certification evaluator: none → one command producing `certification-report.json`, fail-closed on any missing input · self-approved certifications: possible → mechanically refused · certification TTL: none → fixed clock with a scheduled sweep · launch decision: unasserted → a signed, condition-by-condition GO · open `epic`-labeled issues 0/11 → every open epic cluster projected.

**Dependencies / entry criteria.** Terminal epic. Requires Epics 1–9. Strictly serial internally.

**Proposed beads (14).**

| #     | Bead title                                                                        | Type · P     | Acceptance (abbreviated)                                                                                                                                                                                                                                                       |
| ----- | --------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 10.1  | Publish the certification standard as the repo's only definition of certified.    | task · P0    | A canonical `000-docs` record, linked from `STANDARDS.md`, containing § 2's G1–G10 and E1–E6 verbatim, with the tier mapping.                                                                                                                                                  |
| 10.2  | Record who may certify, who may waive, and what may never be waived.              | task · P0    | Roles tied to `GOVERNANCE.md`/`MAINTAINERS.md`/`CODEOWNERS`; three unambiguous statements: the producing identity may never certify; the never-waivable set (a REFUSE, a security-class error, an unresolved provenance contradiction); waivers carry owner + reason + expiry. |
| 10.3  | Build the certification evaluator that decides from machine facts alone.          | feature · P0 | One script produces `certification-report.json` with a per-artifact verdict, evidence class, and machine reason codes; inputs are validator JSON, scanner output, the ledger, and the disposition ledger — nothing else.                                                       |
| 10.4  | Make the certification evaluator fail closed on any input it cannot obtain.       | feature · P0 | Missing/unreadable/stale input ⇒ `NOT-CERTIFIED` with `E-EVIDENCE-UNAVAILABLE`; a test removes each input in turn.                                                                                                                                                             |
| 10.5  | Emit and verify a signed evidence bundle for every certification verdict.         | feature · P0 | The verdict lands as a kernel `gate-result/v1` row inside an `EvidenceBundle`, cosign keyless-signed via Fulcio to **production Rekor**, then verified.                                                                                                                        |
| 10.6  | Refuse any certification whose signer is the identity that produced the artifact. | feature · P0 | A machine check compares the bundle's signing identity against the PR author and the producing identity; combined with CODEOWNERS, no single identity can author, evaluate, and certify.                                                                                       |
| 10.7  | Correct the documented CI gate count and assert it against the workflow.          | bug · P1     | Consumes Epic 2 bead 2.7.                                                                                                                                                                                                                                                      |
| 10.8  | Fix the agent compliance denominator before any agent gate depends on it.         | bug · P1     | Consumes Epic 6 bead 6.9.                                                                                                                                                                                                                                                      |
| 10.9  | Bound the freshness of every public number the site renders.                      | feature · P1 | Consumes Epic 1 bead 1.10; the site renders a dated statement or nothing, never a stale number as current.                                                                                                                                                                     |
| 10.10 | Retire the second README metrics writer that reports a different corpus.          | bug · P1     | Consumes Epic 1 bead 1.9.                                                                                                                                                                                                                                                      |
| 10.11 | Publish the machine-evaluated launch-readiness gate.                              | feature · P0 | `launch-readiness.json`: a boolean plus a per-condition breakdown, evaluated **strictly in decision-hierarchy order** so no quality result can offset a legal one.                                                                                                             |
| 10.12 | Expire certifications on a fixed clock and re-certify on a schedule.              | feature · P1 | Every certification carries an issue date and TTL; a scheduled sweep demotes expired ones automatically and reports the delta. Advisory for merges; **authoritative for rendering**.                                                                                           |
| 10.13 | Publish the certified set and the uncertified backlog on the same page.           | feature · P2 | An uncertified artifact renders **no badge** — never a dimmed or "pending" badge that reads as a weaker certification; the backlog count is stated.                                                                                                                            |
| 10.14 | Project this epic as labeled GitHub epic issues without making them an authority. | chore · P2   | One `epic`-labeled issue plus at most two cluster issues, each with a `**Beads:**` list; every linked bead's notes carry the `GitHub:` line; never a required check.                                                                                                           |

**Bead dependency graph.**

```
10.1 ──▶ 10.3 ──▶ 10.4 ──▶ 10.5 ──▶ 10.6 ──▶ 10.11    STRICTLY SERIAL, TERMINAL
        definition → evaluator → fail-closed → signed → un-self-approvable → launch gate
10.2 lands with 10.1
10.12 ──▶ 10.13 after 10.6
10.7/10.8/10.9/10.10 are consumers of Epics 1/2/6
10.14 anytime
```

**Risks and mitigations.** _Certifying zero artifacts reading as failure_ → § 1 commits to that outcome in advance and § 10.13 publishes the backlog beside the certified set. _An evaluator that silently skips a missing input_ → 10.4's per-input removal test. _A launch GO that nobody signed_ → 10.11 produces the computation; § 18.8 escalates the attestation to the owner, so the strongest artifact in the program is not left unproduced.

**Allowed scope.** The certification standard, the evaluator, `emit-evidence.yml`, the launch-readiness artifact, marketplace rendering of class and backlog, GitHub issue projections.
**PROHIBITED scope.** Asserting a launch GO without the owner's signature · certifying any artifact with an unretained primary artifact · rendering a badge for an uncertified artifact in any form · making a GitHub issue a required check.

**Claude Code execution prompt.**

> Follow the serial chain exactly: 10.1 → 10.3 → 10.4 → 10.5 → 10.6 → 10.11. Build the evaluator to read only machine facts; if it cannot obtain an input, the verdict is NOT-CERTIFIED with `E-EVIDENCE-UNAVAILABLE` — never a pass, never a skip. Expect and report zero certified artifacts on the first run; that is the standard working. Compute `launch-readiness.json`, publish it, and **stop** — the GO decision is the owner's signature, not yours.

**Acceptance criteria.** All 14 beads closed; the evaluator green with a per-input fail-closed test suite; at least one signed, verified bundle in production Rekor; the site rendering class + backlog; `launch-readiness.json` published with every condition evaluated.

**Tests and evals.** Fail-closed per-input tests; self-approval refusal test; bundle signature verification; TTL sweep test with a clock fixture. E1 for the machinery; the certified cohort itself must satisfy E2/E3.

**Evidence contract.** Every certification verdict is a signed bundle row referencing retained, hash-matched artifacts. A verdict without a bundle is not a verdict.

**Rollback.** The evaluator and gates revert cleanly. Certifications are revoked by ledger demotion plus a superseding signed bundle — **never** by deleting a Rekor entry, which is impossible by design and is why 17.8's rollback protocol matters.

**Independent-review gate.** A reviewer who is neither the implementer nor the certifier re-runs the evaluator from a clean checkout, verifies one bundle's signature independently, and confirms the site renders no badge for any uncertified artifact.

**Independence precondition — binding (ratification correction 8; owner amendment 2026-09-02).** **This epic may NOT claim independent certification until the machine-enforced no-self-approval condition is real.** That evidence boundary is independent of the ordinary PR approval count (§ 18.5): the reviewer must be an independent second identity or a qualified human reviewer, and **an alternate identity controlled by the implementer does not count**. Until the certification topology is enforced, the certification artifact says "self-approved" rather than omitting the fact. A certification claim that outruns the boundary enforcing it is the exact defect this program was convened to end.

**Exit scorecard.** Rows 5, 6, 26, 60, 61, 62 at target.

**AAR + bd memory.** AAR records the first certified cohort, its cost, and every artifact that failed and why. `bd remember "certification: A-grade = G1-G10 ∧ E1-E6; the 100-point Freshie score is advisory only and is not a certification input — 962 A/B artifacts fail the gate"`.

---

### EPIC 11 — Model-neutral distribution and identity migration (approved extension)

**Objective.** Make Tons of Skills a model-neutral marketplace with one portable Agent Skills
source, registry-backed native installation paths, truthful support claims, and a
compatibility-preserving public repository identity.

**Authority.** Owner-authorized amendment dated 2026-08-26; decision and implementation
contracts 803–805; Beads parent `claude-rblh`. This extension does not reopen the original ten
epics' technical philosophy. Omarchy Quattro/QML plugins are native extensions, not Agent Skills
adapters, and no harness is publicly supported without registry-backed evidence.

**Effective implementation requirements (13).** The first twelve are the approved extension.
E11.13 is a real prerequisite discovered during rename preflight. Bead `claude-rblh.17` performs
the required blueprint/graph reconciliation, but—like the Epic 5 and Epic 9 closure beads—it is an
administrative closure-support record and does not increase the implementation denominator.

| #     | Task requirement                                                           | Acceptance boundary                                                                                  |
| ----- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 11.1  | Authorize the model-neutral contract and repository identity migration     | Decision 803 names the canonical identity, compatibility aliases, public-claim rule, and exclusions. |
| 11.2  | Define and validate the harness registry schema                            | Only registry-backed `verified-native` entries may support a public harness claim.                   |
| 11.3  | Verify official harness skill support and installation paths               | Primary-source evidence is retained; unknown or unsupported paths remain unclaimed.                  |
| 11.4  | Implement one portable Agent Skills source contract                        | One source tree; no copied per-harness skill trees.                                                  |
| 11.5  | Add registry-backed universal installer commands                           | Installer resolves only declared portable targets and fails closed on unsupported/native classes.    |
| 11.6  | Validate native-path installation behavior                                 | Disposable-path tests prove the declared user/project destinations without touching personal state.  |
| 11.7  | Align public site and README language with verified support                | Model-neutral positioning is truthful; support wording is generated or checked against the registry. |
| 11.8  | Complete repository-rename preflight and external identity audit           | Every external identity is verified or assigned a blocking remediation with an owner and receipt.    |
| 11.9  | Execute and receipt the canonical GitHub repository rename                 | Canonical URL, legacy redirect, origin, and rollback receipt are retained.                           |
| 11.10 | Verify legacy URL, install slug, CLI command, and package identity         | Compatibility paths work without claiming a package or install-slug rename.                          |
| 11.11 | Establish the Omarchy native-extension lane                                | QML/shell extensions are never represented as portable Agent Skills.                                 |
| 11.12 | Monitor the migration and file the post-migration AAR                      | AAR records receipts, rollback, unresolved dependencies, and registry status.                        |
| 11.13 | Update and verify the Tailscale OIDC trust subject after repository rename | Canonical subject succeeds; former repository subject is refused; redacted Tailnet receipt retained. |

**Dependency boundary.** E11.1 and E11.2 are independent roots in the live graph. E11.1 is the
governing decision record, but it is not represented as a Beads blocking edge. The enforced
portable-distribution chain is `11.2 → 11.3 → 11.4 → 11.5 → 11.6 → 11.7`. The identity chain is
`11.8 → 11.9`, followed by parallel E11.10 compatibility verification and E11.13 external trust
remediation; both feed E11.12. E11.11 depends on E11.2 and also feeds E11.12. E11.13 is post-rename
work, not a prerequisite for performing the preflight that discovered it. The live Beads graph must
preserve that direction.

**Administrative-record disposition.** Physical child records `claude-rblh.13`, `.14`, and `.15` are
administrative duplicate shells for canonical E11.10, E11.11, and E11.12. They add zero task
requirements and carry no dependency or implementation authority over canonical `.10`, `.11`, and
`.12`. Bead `.17` is closure/reconciliation support and also adds zero implementation requirements.
The physical 17-child count is therefore **13 implementation requirements + 1 closure-support
record + 3 duplicate shells** and must never be presented as the Epic 11 acceptance denominator.

**Allowed scope.** Registry, installer, model-neutral public copy, repository-identity migration,
compatibility verification, and the separate Omarchy native-extension lane.

**PROHIBITED scope.** Copying skill trees per harness; claiming support without a verified registry
record; renaming legacy install/package identities without separate evidence; treating native QML or
shell extensions as portable skills; bypassing an unresolved external trust boundary.

**Acceptance criteria.** All 13 effective implementation requirements close with registry-backed or retained
migration evidence; compatibility paths remain verified; public claims match the registry; native
extensions remain separately typed; the post-migration AAR includes the Tailscale trust receipt.

**AAR + rollback.** The AAR records canonical and legacy URL behavior, installer and support
receipts, the external trust migration, duplicate disposition, and rollback observables. Repository
rollback never implies deleting redirects, rewriting npm identity, or weakening evidence gates.

---

## 14. AUDIT FINDINGS MAPPED TO PROPOSED BEADS

Severity: **P0** = safety / legal / false public claim · **P1** = source-of-truth integrity or fail-open gate · **P2** = drift / maintenance · **P3** = cosmetic.

| #   | Finding                                                                                                                                                                    | Epic      | Bead                                                                                 | Sev |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------ | --- |
| 1   | AGPL-3.0 content on live public npm with no license text in the tarball                                                                                                    | 7         | 7.13 (packet) → **§ 18.1 escalation**                                                | P0  |
| 2   | 53 clearly third-party plugins published under the IS npm scope, no consent record                                                                                         | 7         | 7.1, 7.2 (quarantine) → **§ 18.2**                                                   | P0  |
| 3   | `walkie-talkie` three-way authorship contradiction                                                                                                                         | 8         | 8.1 (G1 QUARANTINE) → **§ 18.3**                                                     | P0  |
| 4   | 33 of 63 mirrors ship no LICENSE file; 36 include-lists omit it                                                                                                            | 7         | 7.14                                                                                 | P0  |
| 5   | Publish fires on `push: main` with no gate dependency; `enforce_admins:false`                                                                                              | 7         | 7.3                                                                                  | P0  |
| 6   | `NPM_TOKEN` in an unprotected job                                                                                                                                          | 7         | 7.3 (Environment) → **§ 18.4**                                                       | P0  |
| 7   | Publisher has no `.source.json` exclusion                                                                                                                                  | 7         | 7.2                                                                                  | P0  |
| 8   | `--marketplace` never blocks a merge; a zero-field SKILL.md merges clean                                                                                                   | 6         | 6.1–6.4 (R1)                                                                         | P0  |
| 9   | 10 `[security]` shell-substitution errors, unenforced on changed files                                                                                                     | 4 / 8     | 4.4 / 8.4                                                                            | P0  |
| 10  | gitleaks blind to 61.1% of tracked files                                                                                                                                   | 4         | 4.5                                                                                  | P0  |
| 11  | No blocking scan for _unverifiable_ secrets                                                                                                                                | 4         | 4.6                                                                                  | P0  |
| 12  | Supply-chain content scan is PR-only; `push: main` reaches prod ungraded                                                                                                   | 4         | 4.7                                                                                  | P0  |
| 13  | `jrig-data.json`: a 171-byte hand-editable file is the CI source of a `verified:true` claim                                                                                | 9         | 9.2 (**DELETE — resolved**)                                                          | P0  |
| 14  | 3 `forge_proofs` rows transcribed; primary artifact not retained; `baseline_delta` NULL 3/3                                                                                | 9         | 9.4, 9.5                                                                             | P0  |
| 15  | No independent-identity requirement on ledger writes                                                                                                                       | 9         | 9.6                                                                                  | P0  |
| 16  | 12 counterfeit assets (extension ≠ magic bytes); 4 republished publicly                                                                                                    | 1 / 5 / 8 | 1.3+1.4 / 5.3+5.5 / 8.2+8.3                                                          | P0  |
| 17  | The NUL-byte sniff cannot detect them; the drift gate reports "in sync"                                                                                                    | 5         | 5.3                                                                                  | P0  |
| 18  | `gate_run_completeness` tests `IS NULL` only; run 6 (19 rows / 3,000 header) would export                                                                                  | 5 / 9     | 5.1 / 9.7                                                                            | P0  |
| 19  | Every inventory run's header disagrees with its rows (+609 current)                                                                                                        | 5         | 5.1                                                                                  | P0  |
| 20  | `promote-curated.yml` promotes behind two `\|\| true`                                                                                                                      | 5         | 5.6                                                                                  | P0  |
| 21  | MCP destructive-refusal guarantee asserted with no proof in-tree                                                                                                           | 4         | 4.9, 4.10                                                                            | P0  |
| 22  | Plaintext live-shaped provider key in the working-tree `.mcp.json`                                                                                                         | 1 / 4     | 1.14 / 4.14 → **§ 18.7**                                                             | P0  |
| 23  | 8 docs declare AUTHORITATIVE; 1 linked; 4 assert a rule the validator contradicts                                                                                          | 2         | 2.1, 2.3                                                                             | P0  |
| 24  | 6767-h claims to supersede 6767-b, which every live pointer treats as master                                                                                               | 2         | 2.1, 2.2                                                                             | P0  |
| 25  | 1,454 skills claim untested harness compatibility with zero adapters                                                                                                       | 3         | 3.11                                                                                 | P0  |
| 26  | The only "adapter" is 27 byte-identical files; Freshie grades both copies                                                                                                  | 3         | 3.5, 3.6                                                                             | P1  |
| 27  | 962 A/B artifacts fail the gate (132 A-graded carrying 219 errors)                                                                                                         | 8 / 10    | 8.1, 8.8–8.10 / 10.1                                                                 | P0  |
| 28  | Four deterministic tracked marketplace projections need drift gates; eight writer-backed JSON files split into 4 deterministic / 3 external snapshot / 1 editorial cohorts | 1         | 1.7, 1.8 / 1.10                                                                      | P1  |
| 29  | Two README metric writers disagreeing (471/3,179/347 vs 448/3,008/311)                                                                                                     | 1 / 10    | 1.9 / 10.10                                                                          | P1  |
| 30  | Four incompatible corpus definitions → 5 published skill counts                                                                                                            | 1         | 1.5, 1.6                                                                             | P1  |
| 31  | 471 catalog entries / 467 distinct names; propagates to `marketplace.json`                                                                                                 | 1 / 8     | 1.2 / 8.6                                                                            | P1  |
| 32  | Tracked stale catalog shadow (`.backup`, 234 entries, 2025-10-28)                                                                                                          | 1 / 8     | 1.1 / 8.6                                                                            | P1  |
| 33  | `sources.yaml` 64 keys vs lock 63 (`uizze` orphan)                                                                                                                         | 1         | 1.12                                                                                 | P2  |
| 34  | `grades.csv` published with no regeneration gate                                                                                                                           | 5         | 5.4                                                                                  | P1  |
| 35  | Tracked exports lag the local DB by a full run                                                                                                                             | 5 / 9     | 5.4 / 9.8                                                                            | P1  |
| 36  | `forge_proofs.run_id` collides with `discovery_runs.id`, no FK                                                                                                             | 5 / 9     | 5.2 / 9.3                                                                            | P1  |
| 37  | The single-writer Dolt rule is prose only                                                                                                                                  | 5         | 5.9                                                                                  | P1  |
| 38  | No end-to-end Freshie cycle test; unit-only                                                                                                                                | 5 / 9     | 5.7, 5.8, 5.10, 5.13 / 9.9                                                           | P1  |
| 39  | `--agents-only` reports 224.1% compliance (791 of 353)                                                                                                                     | 6         | **6.9 (owner)**; 4.12 / 8.7 / 10.8 consume                                           | P1  |
| 40  | 253 agent errors behind `\|\| true`                                                                                                                                        | 4 / 6     | 4.11 / 6.10                                                                          | P1  |
| 41  | Three release-path failures swallowed as `⚠`                                                                                                                               | 7         | 7.4                                                                                  | P1  |
| 42  | `release.yml skip_tests` disables the only release validation                                                                                                              | 7         | 7.12                                                                                 | P1  |
| 43  | `reconstruct-versions.mjs --check` exists, wired to nothing                                                                                                                | 7         | 7.5                                                                                  | P1  |
| 44  | 99.3% npm/display version divergence, undeclared                                                                                                                           | 7         | 7.6                                                                                  | P2  |
| 45  | Zero SBOMs across ~470 published packages                                                                                                                                  | 7         | 7.15                                                                                 | P2  |
| 46  | 6 third-party actions on mutable tags in privileged/signing workflows                                                                                                      | 7         | 7.9                                                                                  | P1  |
| 47  | No Dependabot config; 22 open advisories with no remediation path                                                                                                          | 7         | 7.10                                                                                 | P1  |
| 48  | `audit-harness` on `^1.3.1` while implementing a _required_ check                                                                                                          | 7 / 9     | **7.11 (owner)**; 9.11 consumes                                                      | P1  |
| 49  | Kernel pin 35 days stale; the gate prints `❌ VIOLATION` and exits 0 daily                                                                                                 | 7 / 9     | **9.10 (owner)**; 7.7/7.8 are citations; 9.12 routes                                 | P1  |
| 50  | Shadow report from 2026-06-27 at kernel 0.4.1; `existing-PASS/kernel-FAIL` unpublished                                                                                     | 9         | 9.10, 9.13                                                                           | P1  |
| 51  | Shadow measures `authoring/v1`, which has never caught anything (**wrong flip target**)                                                                                    | 9         | 9.13                                                                                 | P1  |
| 52  | Prose-documented `ci-required` = actual 21, but no machine-readable asserted list exists                                                                                   | 2 / 10    | **2.7 (owner)**; 10.7 consumes                                                       | P2  |
| 53  | Documented schema 3.15.2 vs `SCHEMA_VERSION 3.16.1`                                                                                                                        | 2         | 2.6, 2.8                                                                             | P2  |
| 54  | "All 317 agents are A-grade" vs 347 files / 253 errors                                                                                                                     | 2         | 2.6                                                                                  | P1  |
| 55  | `000-INDEX.md` 166 entries vs 168 tracked; hand-maintained                                                                                                                 | 2         | 2.4                                                                                  | P2  |
| 56  | Prose-anchor checker runs in no CI job while 6767-h is a live namespace                                                                                                    | 2         | 2.9                                                                                  | P1  |
| 57  | 356 case-insensitive retired-domain occurrences: 292 actionable, 64 retained                                                                                               | 1 / 8     | 1.13 / 8.14                                                                          | P2  |
| 58  | Public stats 11–15 days stale, rendered as current                                                                                                                         | 1 / 10    | **1.10 (owner)**; 10.9 consumes                                                      | P1  |
| 59  | 10 folded-scalar / 21 unknown-token / 63 lexical `allowed-tools` — three measures, one parser needed                                                                       | 3 / 4     | 3.3 (vocabulary) + 4.2 (gate)                                                        | P1  |
| 60  | ~131 source files carry functional Claude model ids in the canonical layer                                                                                                 | 3         | 3.7, 3.8                                                                             | P1  |
| 61  | `${CLAUDE_SKILL_DIR}` mandated by the validator over a portable form                                                                                                       | 3         | 3.9                                                                                  | P2  |
| 62  | 505 `docs.anthropic.com` occurrences, 50.1% in generated artifacts                                                                                                         | 3         | 3.1 (re-measure), 3.11                                                               | P2  |
| 63  | Unbounded advisory swallows at `validate-plugins.yml:98` and `:658`                                                                                                        | 4 / 6     | **6.11 (owner)**; 4.8 is the MCP-specific case                                       | P1  |
| 64  | `check-ci-deadlines.py` scans only `.github/workflows/`                                                                                                                    | 6         | 6.12                                                                                 | P2  |
| 65  | Denylist-dependent skills silently unprotected on denylist-less harnesses                                                                                                  | 4         | 4.13                                                                                 | P0  |
| 66  | Signed evidence covers 2 of ~20 gates                                                                                                                                      | 7 / 10    | 7.16 / 10.5                                                                          | P1  |
| 67  | 0 of 11 open issues labeled `epic`; 171 open beads invisible to outsiders                                                                                                  | 10        | 10.14                                                                                | P3  |
| 68  | 397 of 471 catalog entries carry no `license`; root MIT vs "Proprietary" doctrine conflict                                                                                 | 7 / 8     | 7.14 / 8.1 (G1)                                                                      | P1  |
| 69  | Ambiguous catalog identities reading as Anthropic-affiliated                                                                                                               | 8         | 8.1 (G2)                                                                             | P1  |
| 70  | No certification TTL; a claim stays "true" forever once made                                                                                                               | 10        | 10.12                                                                                | P1  |
| 71  | Ungated self-approving `verified:true` in `jrig-data.json` + a false badge claim in `CLAUDE.md`                                                                            | 9         | 9.2                                                                                  | P0  |
| 72  | Historical branch protection was unsatisfiable; owner amended ordinary merge policy to zero reviews on 2026-09-02                                                          | 10        | Ordinary merge gap resolved; certification independence remains at 10.2 → **§ 18.5** | P1  |
| 73  | 13 aging external contributor PRs, 4 with ZERO CI (fork PRs stall in `action_required`)                                                                                    | 2 / 7     | intake triage under 7.13's review discipline; `709-DR-GUID` governs                  | P1  |
| 74  | Nested `000-docs/` negations still dead in one plugin                                                                                                                      | 1         | 1.7-adjacent gitignore audit                                                         | P2  |
| 75  | Flaky `JournalWriter` test inside the required gate                                                                                                                        | 6         | 6.11 (bounded marker) + a de-flake bead                                              | P1  |
| 76  | Stale mirror still tracking ~23.6 MB                                                                                                                                       | 8         | 8.5 (QUARANTINE disposition)                                                         | P2  |
| 77  | Duplicate doc numbers 001 / 010 / 678 in `000-docs`                                                                                                                        | 2         | 2.4 (generated index surfaces them)                                                  | P3  |

**Findings 72–77 are the carry-in items** from the current open-defect sweep. They are folded into the epics above rather than tracked separately, so no defect lives outside the plan. Two carry an explicit note: finding 72 is an **escalation, not a bead** (§ 18.5) — the compensating controls close its consequences without changing the setting; finding 73's remediation is bounded by `000-docs/709-DR-GUID-reviewing-external-prs.md` and by the rule that **any contributor-facing wording is drafted for owner sign-off, never posted**.

---

## 15. CRITICAL PATH AND SEQUENCING

### The true chain

**Read this diagram as a DEPENDENCY graph, not a schedule.** An arrow means "cannot be correct
before"; it does **not** authorize starting anything. Section 15.1 records the original launch
sequence that governed the pre-amendment containment mission. Current execution authority is § 13's
amended rule plus the live Beads dependency graph.

```
                    ┌─────────────────────────────────────────────┐
  SLICE 1           │ E7.1  mirror private:true      [rank 2]     │  ← FIRST BEAD
  (pre-program      │ E7.13 AGPL/consent packet (document only)   │
   containment)     │ ─────────────────────────────────────────── │
                    │ E4.14 plaintext credential — NOT in slice 1 │
                    │       (owner-gated escalation § 18.7)       │
                    └───────────────┬─────────────────────────────┘
                                    │
        ┌───────────────────────────┼──────────────────────────┐
        ▼                           ▼                          ▼
  E2 AUTHORITY FREEZE        E7.2/7.9 publish filter    E1 MEASUREMENT
  (2.2→2.1→2.3/2.9)          + SHA-pin privileged wf    HARNESS + resolver
  ── STRICTLY SERIAL ──      ── independent ──          (1.0 → 1.5/1.6/1.7/1.8)
  blocks: E1.13, E6, E8                                 blocks: E3, E6, E8
        │                           │                          │
        └─────────────┬─────────────┴──────────────┬───────────┘
                      ▼                            ▼
              E6 RATCHET (6.1→6.2→6.3→6.4→6.7→6.8)   E5 EVIDENCE STANDARD
              ── STRICTLY SERIAL, R1 first ──         (5.11 → 5.12) + Freshie
              blocks: E4 ratchets, E8 remediation      gates (5.1→5.6→5.3→5.4)
                      │                            │
        ┌─────────────┴────────────┐               │
        ▼                          ▼               ▼
  E4 SAFETY BOUNDARIES       E3 CANONICAL      E9 CROSS-REPO BOUNDARIES
  (4.5→4.6 serial;           CONTRACT          (9.1→9.3→9.5→9.6 serial)
   4.2→4.3→4.4 serial;       (3.1→3.2→3.4      needs E5's standard
   4.1/4.7 parallel)          →3.11→3.12)       + E1's regeneration
        │                          │                     │
        └──────────┬───────────────┴─────────────────────┘
                   ▼
            E8 LEGACY DISPOSITION + REMEDIATION
            (8.1 ledger → 8.8/8.9/8.10 batches → 8.15 cohort)
            LONGEST-RUNNING. Needs E6 ratchet + E1 resolver + E5 standard.
                   │
                   ▼
            E10 CERTIFICATION + LAUNCH GATE
            (10.1→10.3→10.4→10.5→10.6→10.11→10.13)
            ── STRICTLY SERIAL. Terminal. ──
```

### Strictly serial — cannot be parallelized without producing a wrong result

| Chain                                            | Why                                                                                                                          |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `E2.2 → E2.1 → E2.3`                             | the pointer gate red-fails everything until the seven self-declarations are removed                                          |
| `E6.1 → E6.2 → E6.3 → E6.4`                      | the baseline must be emitted from a quiet tree, in CI, before R1 can block                                                   |
| `E6 R1 → E6 R2/R3/R4` (≥2 weeks)                 | you must know R1's flap rate first, or an unstable gate is indistinguishable from a regression                               |
| `E4.5 → E4.6`                                    | de-blanket gitleaks _before_ adding the unverified scan, or the new job drowns in the same false positives and gets neutered |
| `E7.1 → E7.2 → E7.3 → E7.4`                      | quarantine before gating before evidencing; each is the precondition of the next being meaningful                            |
| `E5.11 → E5.12 → E9.3 → E9.5 → E9.6`             | class → demote → schema → retain → no-self-approval. Reordering produces a ledger that records unverifiable claims           |
| `E1.3 → E1.4` and `E5.3 → E5.5`                  | the sniff must land before the counterfeits are removed, or a revert republishes them                                        |
| `E10.1 → E10.3 → E10.4 → E10.5 → E10.6 → E10.11` | definition → evaluator → fail-closed → signed → un-self-approvable → launch gate                                             |
| `E2.1 → E1.13`                                   | the frozen set must exist before any mass dead-domain edit                                                                   |

### Genuinely parallelizable

**"Parallelizable" means "will not corrupt each other if authorized together" — it is a safety
property, not an authorization.** Under the amendment, Beads dependencies, WIP, file ownership, and
the evidence boundary determine whether parallel work is actually ready.

- **E2 (authority) ∥ E7 (supply chain) ∥ E1 (measurement)** — disjoint file sets, no shared gate.
- **E4.1 / 4.7 / 4.8 / 4.12 ∥ everything** — the register, the push-leg scan, the MCP deadline, and Slack routing touch nothing else.
- **E3 ∥ E4** after E1's regeneration — they share only the tool-token vocabulary (owner: E3.3; E4.2 consumes).
- **E5's Freshie integrity chain ∥ E6's ratchet** — different subsystems entirely.
- **E8's batch migrations ∥ E9** — once the ratchet is live, batches run continuously in the background of everything else.

### The original recommended first implementation bead (historical launch decision)

> **Epic 7, bead 7.1 — "Mark every externally mirrored package private so it can never be published."**

**Why this and not the ratchet or the authority freeze:**

1. **It is the highest-ranked live exposure a single commit can close.** Rank 2 (legal / licensing / attribution / reputational) outranks rank 4 (SoT integrity, which the ratchet serves) and rank 3. 63 provenance-marked repository package mirrors (including 58 scoped npm packages) are publishable _right now_ through a `push: main` path with no publisher-level provenance gate, and mirror non-publication currently depends on an unrelated script declining to bump a version — **defense by side-effect, not a boundary.**
2. **It has zero prerequisites.** Unlike E7.3 (needs the CI invariant), E6.2 (needs a quiet tree and a corpus resolver), or E2.3 (needs the freeze), 7.1 depends on nothing.
3. **It is additive, mechanical, and trivially revertible.** One `"private": true` line per package plus a tree-wide invariant test. No corpus file, no catalog, no workflow logic, no external mutation.
4. **It quarantines silently.** It stops future exposure without any public announcement, preserving the owner's freedom to decide the _existing_-artifact remediation (§ 18.1, § 18.2) on his own timeline rather than under pressure created by our own fix.
5. **It is small enough to finish and prove in one sitting**, which matters: the first bead of the 151-record ratified programme should demonstrate the whole discipline — measure, fix the root cause, add the gate in the same PR, prove the gate bites, close with evidence.

### 15.1 The original authorized launch sequence (historical; ratification correction 6)

At ratification, this subsection **superseded every other ordering statement in the document** and
governed the first containment mission. The 2026-08-26 owner amendment superseded it as current
activation authority when it authorized full Beads graph instantiation. It remains here to preserve
the launch decision and its evidence; it must not be used to deactivate or delete the live graph.

**Slice 1 — PRE-PROGRAM CONTAINMENT MISSION (the only thing authorized to start at ratification).**

| In slice 1                                                                     | Rank / justification                                                                                  |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| **E7.1** — mark every externally mirrored package `private`                    | **rank 2**, live exposure, zero prerequisites, mechanical, revertible in one commit                   |
| **E7.13** — the AGPL / consent packet, **document only, no external mutation** | **rank 2**, owner-input-gated, longest lead time in the program; produces a document, mutates nothing |

**Why this is an exception and how it is recorded.** E7.1 and E7.13 belong to **Epic 7**, and running them before Epics 1–6 is exactly the "later-numbered P0 containment bead runs first" case that § 13 rule 5 governs. The proof is on the record: rank 2 (legal / licensing / attribution / reputational) outranks rank 4 (SoT integrity, which the ratchet serves) and rank 3, and 63 provenance-marked repository package mirrors (58 scoped npm packages and 5 non-scoped mirrors) are publishable **right now** through a `push: main` path with no publisher-level provenance gate. Per § 13 rule 6 this is therefore filed as a named **PRE-PROGRAM CONTAINMENT MISSION** with its own AAR — **not** as "starting Epic 7." Closing E7.1 and E7.13 does **not** activate E7.2, E7.3, or any other Epic 7 bead.

**These two beads ran as one slice, not as "parallel epics."** Parallelism _inside_ that authorized
slice was permitted; the original rule forbade instantiating multiple epics at once. This paragraph
describes the historical launch boundary, not the post-amendment live graph.

**Explicitly NOT in slice 1:** **E4.14 / E1.14** (the plaintext MCP credential). It is an owner-gated escalation (§ 18.7) — the pre-flight check is delegable, the rotation is not, and no rotation is performed or assumed. The earlier draft's Day-0 diagram listed it beside E7.1; that was a dependency observation, and it is corrected here.

**Historical slice exit conditions — all four were required before the next activation decision.**
(a) both beads closed with the command output that proves them; (b) independent review by someone
who is not the implementer, per § 18.5's honest-review rule; (c) the containment-mission AAR filed;
(d) **the owner review gate passed.**

**Original slice-2 rule, now superseded as an activation constraint.** The dependency graph named the
Epic 2 authority freeze, Epic 1 measurement harness, and Epic 7 publish filter as natural next
candidates, while leaving the choice to the owner after slice 1. The amendment later made that choice
for graph instantiation: the approved full graph exists, while Beads dependencies and closure gates
still decide what can execute and what can close.

---

## 16. CONTINUOUS GOVERNANCE AFTER CERTIFICATION

What runs forever, and what each thing would catch if it stopped.

| Cadence                    | Control                                                                                                            | Catches                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| **Every PR (blocking)**    | `ci-required` (21 jobs) + `gitleaks` + `skill-conform`                                                             | the merge contract itself                                                                                    |
| Every PR (blocking)        | **compliance ratchet R1–R4**                                                                                       | any new debt; any total increase; any A+B dilution; any corpus deletion dressed as compliance                |
| Every PR (blocking)        | thin-adapter gate · canonical vendor-literal gate · tool-token vocabulary gate                                     | the canonical/adapter line eroding back into forks and vendor lock                                           |
| Every PR (blocking)        | asset content-type sniff · license-consistency check · `sources.yaml`↔lock key equality                            | counterfeits, mislabeled licenses, orphan sources                                                            |
| Every PR (blocking)        | authority-pointer gate · doc-class enforcement · schema-version assertion · required-set self-description          | a document claiming authority it was not granted; a frozen doc edited; documented numbers drifting from code |
| Every PR (blocking)        | diff-scoped **unverified**-secret scan; regenerate-and-diff on every generated artifact                            | credentials no verified-only scanner sees; stale published facts                                             |
| Every PR (blocking)        | `reconstruct-versions.mjs --check`                                                                                 | display-surface version drift                                                                                |
| **Every push to main**     | supply-chain content scan `--changed-only`                                                                         | the admin-merge / direct-push path                                                                           |
| **Every publish**          | 3 publish locks + the release five-tuple + SBOM + signed bundle                                                    | unintended publication; incomplete releases; unattributed dependencies                                       |
| **Daily**                  | `kernel-vendor-hash` (ordering **blocking**, staleness → Slack) · stats freshness bound                            | pin ordering violations; a number rendered past its bound; **an advisory gate nobody reads**                 |
| **Weekly**                 | `promote-curated` refresh · external sync auto-PR (≤1 open) · `bd-sync status` drift sweep (advisory) · Dependabot | mirror drift; upstream drift; bead↔issue divergence; dependency advisories                                   |
| **Per inventory run**      | header==rows gate · export-coherence gate · export allowlist · hermetic cycle test                                 | a phantom run publishing; exports lagging; a payload leaking into the public record                          |
| **Per certification**      | evaluator (fail-closed) + signed bundle + no-self-approval check                                                   | a claim exceeding its evidence; a self-approved verdict                                                      |
| **On a TTL clock**         | certification expiry sweep (advisory for merges; **authoritative for rendering**)                                  | a true claim quietly becoming a historical one                                                               |
| **Quarterly**              | kernel shadow re-baseline at the current pin, both v1 and v2 lanes, `existing-PASS/kernel-FAIL` headlined          | the only number that answers "would flipping weaken the gate?"                                               |
| **Per release + per epic** | independent-review gate; the implementer may never self-certify                                                    | the failure mode this entire program exists to end                                                           |

**The five properties that must hold forever, restated so they cannot erode:**

1. **A number is published only with its cohort and its command.** Five answers to "how many skills" is what unlabeled numbers produce.
2. **A gate that reports and exits 0 must route its failure somewhere a human reads.** 35 consecutive silent `❌ VIOLATION`s is the general case, not a one-off.
3. **A gate observed only green is unverified.** The red negative-test run is the artifact.
4. **The baseline is written by a bot after the gate passed.** Humans lower it by fixing artifacts.
5. **The producing identity never certifies.** Enforced at a machine boundary; prompt-only enforcement is advisory.

---

## 17. RATIFIED AND EFFECTIVE PROGRAMME DENOMINATORS

### Original ratified plan (historical baseline)

| Epic | Title                                                                | Task beads |
| ---- | -------------------------------------------------------------------- | ---------: |
| 1    | Repository cleanup and measurement baseline                          |     **15** |
| 2    | Documentation authority and source-of-truth consolidation            |     **13** |
| 3    | Canonical model-agnostic plugin and skill contract                   |         13 |
| 4    | Runtime safety, permissions, and MCP boundary enforcement            |         14 |
| 5    | Dolt, Freshie, provenance, and real integration testing              |         13 |
| 6    | Marketplace validation and the legacy-debt ratchet                   |         14 |
| 7    | Versioning, packaging, release, and supply-chain hardening           |         16 |
| 8    | Legacy certification, remediation, quarantine, and archival          |         15 |
| 9    | Bind Intent Eval Lab and Intent OS across machine-checked boundaries |         14 |
| 10   | Independent certification, launch readiness, continuous governance   |         14 |
|      | **Task beads**                                                       |    **141** |
|      | **Epic beads** (`--type=epic`, one per epic)                         |     **10** |
|      | **TOTAL**                                                            |    **151** |

**Count changes from ratification (2026-08-13), stated so the delta is auditable:**

| Change                                                                                                                       | Epic |                                    Δ |
| ---------------------------------------------------------------------------------------------------------------------------- | ---- | -----------------------------------: |
| Correction 1 — root README landing contract (bead 2.13, § 6A.5)                                                              | 2    |                               **+1** |
| Correction 5 — Mission 01 reconciliation: 0 beads satisfied, 0 superseded; 1.7/1.8 narrowed in scope, 1.0 partially informed | 1    |                                **0** |
|                                                                                                                              |      | **140 → 141 task · 150 → 151 total** |

**Epic 1's count deliberately did not drop.** Two beads were narrowed and one was partially informed by the completed Mission 01, but none was retired, and no filler bead was invented to protect a headline number in either direction (§ 13 EPIC 1, "Mission 01 is NOT Epic 1"). **A count is a consequence of the work, never a target.**

At ratification these 151 records were proposals, not a batch to create; § 15.1 limited the first
activation to two containment beads. That statement remains the historical baseline, but its
instantiation constraint was superseded by the 2026-08-26 amendment.

### Approved extension and current effective denominator

| Component                                             | Implementation requirements | Epic records | Total records |
| ----------------------------------------------------- | --------------------------: | -----------: | ------------: |
| Original ratified plan                                |                         141 |           10 |           151 |
| Epic 11 original approved extension                   |                          12 |            1 |            13 |
| Discovered prerequisites across Epics 5–11            |                           8 |            0 |             8 |
| **Current effective canonical programme denominator** |                     **161** |       **11** |       **172** |

The eight discovered implementation prerequisites close real implementation/evidence gaps found
during execution; they are not duplicate shells or administrative closure records:

| Bead             | Discovered prerequisite                                                  |
| ---------------- | ------------------------------------------------------------------------ |
| `claude-h05s.15` | Run the Freshie export allowlist before Dolt identity setup              |
| `claude-nfzl.18` | Restore pinned Ruff format compliance in CI scripts                      |
| `claude-jqvw.17` | Make version-surface agreement work in shallow CI clones                 |
| `claude-5e0c.31` | Reconcile llm-box AGPL metadata and publication projections              |
| `claude-5e0c.32` | Repair first-party duplicate headings that blocked Markdown validation   |
| `claude-5e0c.33` | Regenerate the gated disposition ledger and Epic 1 scorecard             |
| `claude-snmr.15` | Classify certification standard 808 in the canonical document-class gate |
| `claude-rblh.16` | E11.13: update and verify the post-rename Tailscale OIDC trust subject   |

These are canonical acceptance requirements, not raw database-row counts. The live Epic 11 parent
has 17 physical children: 13 effective implementation requirements, closure/reconciliation bead
`claude-rblh.17`, and three dispositioned duplicates (`.13`, `.14`, `.15`) of canonical E11.10,
E11.11, and E11.12. The closure record and duplicate shells add **zero** to the implementation
denominator. Conversely, one physical implementation bead may deliberately satisfy several
numbered requirements. Count from this table and the task maps, never from raw child length.

The amendment authorizes the full approved Beads graph. It does not waive dependencies, evidence,
review, rollback, external-action boundaries, or closure read-back. The post-modernization discovery
programme (`claude-qyxc`) depends on Epic 11 and remains outside this 172-record modernization
denominator.

**Ownership conflicts resolved.** Each duplicate collapses to one owner; the other epic _consumes_. A second implementation is an automatic bead rejection.

| Duplicated work                                        | Owner                                                            | Consumers                                                                     |
| ------------------------------------------------------ | ---------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| The compliance ratchet machinery                       | **Epic 6**                                                       | Epic 4 (safety ratchets), Epic 8 (remediation), Epic 10 (certification input) |
| The evidence class standard (E0–E3)                    | **Epic 5** (5.11)                                                | Epic 9 (mechanics), Epic 10 (certification)                                   |
| `--agents-only` compliance arithmetic                  | **Epic 6** (6.9)                                                 | Epics 4, 8, 10                                                                |
| Kernel/jrig-cli lockstep pin bump + shadow re-baseline | **Epic 9** (9.10)                                                | Epic 7 (7.7/7.8 become citations)                                             |
| `audit-harness` exact pin                              | **Epic 7** (7.11)                                                | Epic 9 (9.11)                                                                 |
| Stats freshness bound                                  | **Epic 1** (1.10)                                                | Epic 10 (launch condition)                                                    |
| Bounded-swallow markers                                | **Epic 6** (6.11/6.12)                                           | Epic 4 (4.8 is the MCP-specific case)                                         |
| `ci-required` count assertion                          | **Epic 2** (2.7)                                                 | Epics 6 (6.13), 10 (10.7)                                                     |
| `promote-curated.yml` `\|\| true`                      | **Epic 5** (5.6)                                                 | —                                                                             |
| `release.yml skip_tests`                               | **Epic 7** (7.12)                                                | —                                                                             |
| Tool-token vocabulary                                  | **Epic 3** (3.3)                                                 | Epic 4 (4.2 is the gate)                                                      |
| Counterfeit-asset detection                            | **Epic 5** (5.3, promotion path) + **Epic 1** (1.3/1.8, CI gate) | Epic 8 (8.2/8.3 disposition)                                                  |

**The one bead this blueprint adds beyond the epic drafts — Epic 1, bead 1.0: "Build the single measurement harness that emits every number in this blueprint from one command."** Every disputed count in § 3 exists because five different scans measured five different things. One committed script, one output artifact, one command line per number, re-runnable from a clean checkout — otherwise every AAR in this program will argue about arithmetic instead of outcomes.

---

## 18. ESCALATIONS — ITEMS EXCEEDING DELEGATED AUTHORITY

Nine items genuinely meet the threshold. Everything else in this blueprint is delegable. **None of them is performed by this document** — each is stated with a recommendation, the consequences of acting and of delaying, and the reason it exceeds delegated authority.

**18.1 — AGPL-3.0 content on a live public npm artifact under the Intent Solutions scope. TIME-SENSITIVE.**
`@intentsolutionsio/skyvern@0.1.5`, published 2026-06-18, ships a 10,889-byte README reproducing an AGPL-3.0 upstream's skill content verbatim, with **zero occurrences of "GNU AFFERO" or "GNU GENERAL PUBLIC"** anywhere in the tarball. AGPL-3.0 § 4 conditions verbatim conveyance on giving every recipient a copy of the License. The counterparty is an actively-maintained commercial AGPL vendor.
**Recommendation:** publish a corrected version carrying the full AGPL text and an upstream attribution notice; deprecate the defective version; check unpublish eligibility. Adding `LICENSE` to that source's `include[]` is delegable (bead 7.14).
**Consequence of acting:** a public correction visible to the counterparty — and the strongest possible evidence of good faith. Small reputational cost, compliance restored.
**Consequence of delaying:** every additional day is additional distribution of a non-compliant artifact under your scope, and AGPL is on the list most enterprise procurement scanners flag automatically.
**Why it exceeds authority:** legal exposure not technically eliminable; requires npm registry mutation on a live public artifact; likely warrants counsel.

**18.2 — Current third-party plugins published under the Intent Solutions npm scope with no consent record.**
Live since 2026-04-21 across ≥20 distinct authors and organizations. The current cohort is 53 clearly third-party packages including Skyvern (52 ordinary-license packages plus one AGPL defect); 5 additional scoped packages remain first-party/ownership-ambiguous. MIT/Apache-2.0 permit only the acts granted by those licenses, so this is not a copyright conclusion — `author` is preserved in every package. The exposure is different: the package **identity** (`@intentsolutionsio/<their-name>`) and the **maintainer of record** present third-party work as Intent Solutions' published output on a registry consumers read as an ownership signal. No consent artifact exists in `sources.yaml` or in decision records 694/700/709; absence is unresolved, not proof of absence.
**Recommendation:** quarantine first (beads 7.1 + 7.2 — delegable, and already the first bead), _then_ reach out, _then_ decide per package. In that order.
**Consequence of acting:** contributor conversations you may not want yet; possible requests to unpublish.
**Consequence of delaying:** quarantine stops the _flow_ but the existing 58 scoped artifacts stay live; for a business seeking enterprise certification, "publishes other people's work under its own scope" is exactly the finding a partner diligence review surfaces.
**Why it exceeds authority:** first publication under the owner's identity already occurred; remediation is a business/legal choice; **any contributor-facing wording requires sign-off before posting.**

**18.3 — The `walkie-talkie` authorship contradiction.**
One mirrored directory makes three incompatible claims: `SKILL.md` names Jeremy Longshore as author; `plugin.json` and the catalog say "Walkie-Talkie Maintainers"; `LICENSE` says "Copyright (c) 2026 walkie-talkie contributors". The upstream org is real. It is published today under the IS scope.
**Recommendation:** state whether that org is yours. If it is, the catalog and LICENSE misattribute your own work and are corrected. If it is not, a `SKILL.md` asserting your name over a third party's work is live and must be corrected upstream-side.
**Consequence of acting:** one sentence resolves it.
**Consequence of delaying:** the record cannot be truthful in all three places, so the honest state is QUARANTINE — indefinitely.
**Why it exceeds authority:** only the owner knows the answer. No repository evidence settles it.

**18.4 — Moving `NPM_TOKEN` into a protected GitHub Environment.**
This is the only publish lock a pull request cannot edit away. Locks 1 and 2 are workflow logic and can be removed in a PR; the Environment cannot, without an admin action.
**Recommendation:** create the `npm-production` Environment with protection rules and move the secret. Bead 7.3's code half is delegable; this half is not. **Sequence it with § 18.9** — the secret that moves into the Environment should be the _replacement_ token, so revocation, minimum-scope re-issue, and the Environment move happen once rather than twice.
**Consequence of acting:** a small one-time UI action; publish thereafter requires satisfying the environment's rules.
**Consequence of delaying:** the publish path stays defended only by logic a future PR can delete — the pattern that produced defense-by-side-effect in the first place.
**Why it exceeds authority:** GitHub org/repo admin action; also not revertible by `git revert`.

**18.5 — Review-free ordinary merges and independent evidence are different controls (owner amendment, 2026-09-02).**
Branch protection is `enforce_admins: false` with 0 required approving reviews and no required code-owner review. The repository owner deliberately chose this policy so ordinary changes do not stall on a human review ritual. Three rules now bind:

1. **The three protected status contexts remain the ordinary merge gate.** `ci-required`, `gitleaks`, and `skill-conform` must report green. This amendment does not authorize an admin bypass or a fourth required context.
2. **CODEOWNERS routes responsibility; it does not authorize a permissive baseline policy-envelope mutation.** E6.6 replaces the old review-dependent exception with a narrower machine-verifiable boundary: any edit that adds accepted entries, worsens monotone metrics, or changes the schema/rule/corpus/denominator/provenance contract requires an exact one-file PR that byte-matches an immutable artifact produced by a first-attempt, repository-owner-dispatched capture on the protected default branch. The required ratchet job verifies the trusted workflow path, owner actor and triggering actor, run/job success, source SHA, single capture commit, same-repository PR, and single-use branch.
3. **Independent review remains an evidence property wherever this blueprint requires it.** A producing identity may not certify its own artifact. An alternate identity controlled by the implementer is not independent. Epic 10 therefore remains blocked from claiming independent certification until its machine-enforced no-self-approval condition exists; this is separate from GitHub's ordinary PR approval count.

**No branch-protection change is proposed or performed by E6.6.** This amendment records the owner's already-live policy and gives every exceptional permissive policy-envelope path a fail-closed authorization mechanism without imposing human review on unrelated changes.
**Consequence of acting:** ordinary work remains review-free, while any baseline relaxation or contract redefinition becomes attributable, replay-resistant, and artifact-proven.
**Consequence of delaying:** current authority would contradict the live repository policy, and a branch-name-only exception would remain spoofable.
**Why this amendment is in scope:** branch settings remain owner-only; the owner already made that decision. E6.6 reconciles repository authority and enforces its own narrower exception without mutating settings.

**18.6 — Behavioral-eval spend for the first certified cohort.**
Real `j-rig eval` runs cost roughly **$2–5 per skill** via the default provider, and E2 requires **n≥3 runs** for a non-deterministic provider plus a broken-variant baseline run per skill. A 12-skill cohort is therefore on the order of **$100–250**, not $30. A full corpus sweep would be ~$6.3k (§ 9 S12).
**Recommendation:** authorize a capped first cohort (10–15 skills, budget ≤$300) chosen for demonstrative value rather than volume. Approve **per cohort**, not per run.
**Consequence of acting:** the first genuinely evidenced certification in the platform's history; the badge can come back true.
**Consequence of delaying:** certification stays at zero indefinitely and the E3 tier remains theoretical — the A-grade definition published but never exercised.
**Why it exceeds authority:** spending money.

**18.7 — Rotating the plaintext provider credential in the working-tree `.mcp.json`.**
A live-shaped API key sits in plaintext `env` in the working-tree `/.mcp.json`. **Verified: git-ignored at `.gitignore:118` and never in git history** — it has not been published. The pre-flight check that prevents recurrence is delegable (beads 1.14 / 4.14); the rotation is not.
**Recommendation:** rotate and move the value into SOPS. **Asked once, not assumed** — no rotation performed without an explicit yes.
**Consequence of acting:** brief interruption to a local MCP integration.
**Consequence of delaying:** a live credential sits unencrypted on a box where multiple agent sessions run with filesystem access.
**Why it exceeds authority:** credential rotation only the owner controls. _(Per standing instruction, no rotation is proposed for the Tailscale/GitHub PAT, the DeepSeek key, or the HuggingFace token — those are settled.)_

**18.8 — Personal attestation for the launch decision and for any future kernel-authority flip.**
`launch-readiness.json` produces a boolean and a per-condition breakdown; it cannot _stop_ a human. The six DR-049 flip conditions include a CTO + CISO + VP-DevRel sign-off triple that, in this organization, resolves to one person.
**Recommendation:** treat both as signed decisions of record — the launch GO recorded as an ADR whose verdict is included in a signed evidence bundle (beads 10.5 / 10.11), and the flip left unattempted for the duration of this program.
**Consequence of acting:** the launch claim carries your name and is auditable.
**Consequence of delaying:** launch readiness is computed but never asserted, leaving the strongest artifact in the program — a signed, condition-by-condition GO — unproduced.
**Why it exceeds authority:** a certification claim requiring personal attestation; an irreversible public commitment.

**18.9 — The npm publish token: treat as potentially LIVE, replace, and move into the protected Environment. OWNER-AUTHORIZED EXTERNAL ACTION — NOT PERFORMED HERE.**
Ratification correction 7. **The plan must not depend on anyone remembering whether the old token was revoked.** A credential whose disposition is carried in memory is, for planning purposes, live. This item exists so the question is answered by a record rather than by recollection.
**Recommendation, in this order:** (1) **treat the old npm token as potentially live** and assume it still grants publish on the `@intentsolutions*` scopes; (2) **revoke it**; (3) **create a replacement with the minimum scope the publish workflow actually needs** — publish on the specific scopes, nothing broader, and no read of unrelated org state; (4) **move the replacement into the protected `npm-production` GitHub Environment** (§ 18.4 — the only publish lock a pull request cannot edit away); (5) **record verification without exposing the secret**: `gh secret list` / the Environment's name + `updated_at`, plus one successful gated publish run — **never** the value, never a prefix, never a truncation, in any log, PR body, receipt, or prompt.
**Consequence of acting:** one short window where publish is unavailable while the secret moves; thereafter every publish must satisfy the Environment's protection rules.
**Consequence of delaying:** an unrevoked token with unknown scope remains a standing publish path around every lock this program adds — and the 58 existing scoped mirror artifacts (§ 18.2) are exactly what such a path could reach.
**Why it exceeds authority:** npm registry credential lifecycle plus a GitHub org/repo admin action; not revertible by `git revert`. **No revocation, rotation, creation, or Environment change was performed during the ratification-correction mission**, and none may be performed by an executing agent without an explicit owner instruction. _(Unrelated and already settled per standing instruction: the Tailscale/GitHub PAT, the DeepSeek key, and the HuggingFace token — no rotation is proposed for those.)_

**Explicitly NOT escalated,** so the list stays credible: the 61.1% gitleaks blind spot and the open CodeQL alerts are serious engineering risks with **no evidence of an actual leak** — `gitleaks` is green on the required gate, `gate_export_allowlist()` hard-fails before any public DoltHub push, and `run-jrig-eval.sh` handles the provider key correctly. Those are hardening work (beads 4.5, 4.6), not disclosure events. Deleting `marketplace.extended.json.backup` is likewise not an escalation — git history retains it and the three-condition delete rule is satisfied.

---

## 19. CONFLICT RESOLUTIONS OF RECORD

Where the source analyses disagreed, the call and the ranking basis. Recorded so the disagreement is not re-litigated silently.

| Conflict                                                                          | Resolution                                                                                                                                                                                                                                                       | Basis                                                 |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Counterfeit assets: 4 / 14 / 18 / 19                                              | **12** (8 source + 4 curated), by per-extension magic-byte compare over all tracked files. The boycott-filter icons and servicegraph marks are genuine PNGs                                                                                                      | rank 7 — one method, published with its command       |
| Malformed `allowed-tools`: 63 / 21 / 10                                           | **All three are real, of three different things.** The deliverable is a parser + vocabulary (E3.3) and a gate (E4.2), not a number                                                                                                                               | rank 4                                                |
| Kernel flip target: v1 or v2                                                      | **v2, and the flip stays frozen.** v1's `existing-PASS/kernel-FAIL: 0` means flipping to it is a pure loss of enforcement                                                                                                                                        | rank 1 over rank 6                                    |
| `jrig-data.json`: delete or class-carry                                           | **Delete** the file + build step; correct the badge claim in `CLAUDE.md`. Verified 171 bytes, no `.astro` importer                                                                                                                                               | rank 2/3 over rank 9                                  |
| Mirror packages: repository 63 / live scoped npm 58                               | **63 repository mirrors are private; 58 scoped artifacts remain live; 53 are clearly third-party including Skyvern and 5 are ambiguous**                                                                                                                         | rank 5 — machine rules do not take judgment inputs    |
| External sources: 63 or 64                                                        | **64 in yaml, 63 in lock**; `uizze` orphaned. Delete + assert key-set equality                                                                                                                                                                                   | rank 4                                                |
| Canonical artifact: one `skill.yaml` vs frontmatter + sidecar                     | **Frontmatter + `skill-card.yaml` sidecar** (§ 5.1). Overloading frontmatter spends the description-injection budget that decides whether a skill fires, and the benchmark shows exactly what "one big frontmatter" produces at scale                            | rank 10 + rank 4                                      |
| Canonical root: flat `skills/` vs today's `plugins/<cat>/<plugin>/skills/<name>/` | **No rename.** The name is taken, the install slug is a frozen API, and a flat namespace at 3,179 is a collision hazard                                                                                                                                          | rank 9 over rank 12                                   |
| Uniform anatomy vs tiers                                                          | **Tiers T0–T4, computed not declared.** Uniform anatomy at this scale either sets the bar at the floor or leaves 90% permanently non-compliant                                                                                                                   | rank 10 + rank 11                                     |
| Who owns the evidence standard                                                    | **Epic 5 files it**; Epic 9 implements mechanics; Epic 10 consumes                                                                                                                                                                                               | rank 4 — one writer per fact class                    |
| Who owns the ratchet                                                              | **Epic 6.** Epics 4, 8, 10 consume. A second implementation is an automatic bead rejection                                                                                                                                                                       | rank 11                                               |
| Epic 1's dead-domain sweep vs Epic 2's freeze                                     | **Epic 2 freezes first**; the frozen set is an input to the sweep                                                                                                                                                                                                | rank 10                                               |
| Baseline commit                                                                   | Analyses baselined at `436a00f80`, then `708692244`, then `49210ecb6`; **this document re-measured at `origin/main` HEAD `478aaf17731714fed9b1779284de6a5b3729ef6e`.** The ratchet baseline must be emitted from a quiet tree in CI                              | rank 7                                                |
| A/B artifacts failing the gate; A-graded error load                               | **962 and 219**, from the full `origin/main` re-measurement recorded with its commands in § 3.1. 132 A-graded failing is confirmed. Earlier unqualified headlines are not reproducible and are not used                                                          | rank 7 — one method, published with its command       |
| One error headline or three                                                       | **Three, never merged.** SKILL.md per-row 7,433 (3,679 rows) · agent lane 253 (353 files) · terminal `--marketplace` headline 7,687. The residual 1 is left unattributed rather than explained away                                                              | rank 3 over rank 12 — false precision is a lie        |
| README as catalog surface: rejected, with what in its place?                      | **Rejected as a catalog; replaced by a governed landing contract (§ 6A)** — model-agnostic identity, scale stated with cohorts, five navigation axes, four artifact classes, adapter-backed harness claims, frozen slug                                          | rank 3 + rank 11                                      |
| Mission 01 vs Epic 1                                                              | **Different objects.** Mission 01 is closed PRE-PROGRAM FOUNDATION work; Epic 1 is proposed. 0 beads satisfied, 0 superseded, 2 narrowed, 1 partially informed; count stays 15                                                                                   | rank 4 — one owner per fact, including "what is done" |
| Human review for ordinary merges vs independent certification                     | **Ordinary merges require the three protected CI contexts, not a human approval.** Independent certification remains separately un-self-approvable; every permissive E6.6 baseline-envelope mutation uses owner-dispatch plus immutable-artifact proof (§ 18.5). | owner amendment + rank 3                              |

---

## 20. WHAT THIS DOCUMENT DOES NOT DO

Stated so the boundary is explicit and no reader infers more authority than was exercised.

- At original ratification on 2026-08-13, it **instantiated nothing**. The later 2026-08-26 owner
  amendment authorized the full graph, which was instantiated externally in Beads. This document
  still performs no Beads, GitHub Issue, Plane, branch-protection, registry, credential, or Tailnet
  mutation; § 13 specifies requirements while Beads/Dolt owns their live state.
- It **changes no production behavior**: no schema, validator, workflow, adapter, marketplace file, README, or catalog entry is modified by this document.
- It **does not flip kernel authority** and does not move any pin.
- It **does not resolve the nine escalations** in § 18; it states them, with recommendations, consequences of acting and of delaying, and the reason each exceeds delegated authority. In particular it performs **no** credential revocation, rotation, or GitHub Environment change (§ 18.9), and **no** branch-protection change (§ 18.5).
- Its **numbers are a snapshot at `origin/main` HEAD `478aaf17731714fed9b1779284de6a5b3729ef6e`**. Epic 1 bead 1.0 will replace this snapshot with the committed measurement harness; until then, every number remains cohort-labeled and command-backed.

**Companion documents:** `000-docs/728-RA-DATA-reference-architecture-benchmark.md` (the primary-source evidence base for § 4–§ 6 and § 10) and `000-docs/729-AT-ADEC-reference-architecture-synthesis.md` (the decision record: what was adopted, modified, rejected, and the licensing constraints on each).
