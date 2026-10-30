<!-- doc-class: record -->

<!-- prettier-ignore-start -->

---
filing_code: DR-GUID-EXTERNAL-SOURCE-VETTING-PLAYBOOK-2026-07-06
date: 2026-07-06
status: active
scope: Human procedures for listing, reviewing, and suspending external plugin sources — sources.yaml, sync drift review, scan sign-off, surface tiers
related:
  - 000-docs/698-TQ-SECU-external-sync-threat-model.md (the threat model this playbook operates)
  - 000-docs/694-AT-DECR-external-sync-mirror-by-default-model.md (mirror-by-default policy + contributor protocol)
  - SECURITY.md (repo security policy)
  - "GitHub issue #966 — Harden the external plugin sync against supply-chain injection"
sibling_prs:
  - feat/sync-lockfile-pinning (Track A — content pinning + drift quarantine)
  - feat/sync-security-scan (Track B — deterministic REFUSE/CHALLENGE/FLAG scan)
  - docs/sync-threat-model (Track C — this document + the threat model)
---

<!-- prettier-ignore-end -->

# External-Source Vetting Playbook (Contributors + Maintainers)

## Purpose

The [sync threat model](698-TQ-SECU-external-sync-threat-model.md) is blunt about the limits
of the machine layers: pinning proves content unchanged, not benign; the scanner recognizes
shapes of badness, not badness. **The human decisions are the actual security boundary.**
This playbook is the operating procedure for those decisions: what the flags gate, what a
maintainer checks before listing a source, how drift review works, how a scan CHALLENGE is
signed off, and how the surface tiers scale the scrutiny.

Machine enforcement lands via the sibling branches `feat/sync-lockfile-pinning` and
`feat/sync-security-scan` (umbrella: issue #966). Where this playbook and those
implementations differ on mechanics, the merged code is authoritative — update this doc.

## The two flags — what `verified` and `curated` actually gate

Orthogonal by design (full rationale: the mirror-by-default decision record):

| Flag             | What it means                                                                                                          | What it mechanically does                                                                                                                                                                                                             |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `verified: true` | A maintainer completed the listing checklist below and vouches for the source's trust and quality **at listing time**. | It is a **trust record, not a control** — the sync engine does not branch on it. It feeds catalog trust-level display (SECURITY.md § Plugin Trust Levels) and is the precondition for listing at the `scripted` or `hooks-mcp` tiers. |
| `curated: true`  | We locally hardened the plugin past its upstream.                                                                      | **Freezes the mirror entirely** — no clone, no write, no orphan-prune, even under `--force`. Only the catalog entry stays current. The standing off-ramp is upstreaming the improvement, then dropping the flag.                      |

Honest corollaries:

- `verified: true` decays. It is one person's judgment at one moment; every later upstream
  change is covered by the drift-quarantine review, not by the original vet.
- `curated: true` is a curation tool that doubles as the strongest security control we have —
  it severs the upstream write path. It is legitimate to apply it defensively to a
  `hooks-mcp`-tier source whose upstream you want to advance only by deliberate re-baseline.

## Surface-tier policy

Every source is classified by the **highest-risk surface its include globs admit** — the tier
follows the file list, never the author's description. A source with no explicit tier is
classified from the surface actually present in its mirror, defaulting to the highest surface
found (classification fails closed; the sync itself keeps working).

| Tier            | Admits                                                                                          | Handling                                                                                                                                                                                                                                                                                                                                                  |
| --------------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `markdown-only` | `SKILL.md`, `README.md`, `references/**`, other prose/docs                                      | Routine path: drift quarantine + scan + standard review. The residual vector is prompt injection (threat model V4) — the drift reviewer **reads the changed instructions as instructions**, not as prose.                                                                                                                                                 |
| `scripted`      | markdown-only + shell / Python / JS the skill invokes (mirrored with executable bits preserved) | Drift review reads **every changed script line**. Scan REFUSE patterns bind hardest here. Any new network endpoint, env access, or file write outside the plugin's own tree must be justified in the review before merge.                                                                                                                                 |
| `hooks-mcp`     | scripted + `hooks/**`, `.mcp.json`, `mcp-server/**`                                             | Highest blast radius — these execute **automatically** in users' agents. Every drift requires explicit human re-approval (the quarantine PR may not be merged on green checks alone); each MCP `command`/`url` and each hook command is justified per entry, per change. Consider `curated: true` freeze-handling for sources here whose upstream churns. |

Tier changes are one-way-hard: moving a source **up** a tier (its globs start admitting
scripts or hooks) is a new listing decision — run the full checklist below again. Moving down
(narrowing globs) needs only a normal PR review.

## Before adding a source to `sources.yaml` — the listing checklist

The PR that adds a source is the vet. Every item below is evidence in that PR's description
or review thread; `verified: true` asserts all of them were done.

1. **Author identity and track record.** Real account with organic history: account age,
   other repositories, external corroboration (site, npm, community presence). A fresh
   account shipping a polished plugin is a flag, not a disqualifier — it raises the bar on
   every following step.
2. **Typosquat check.** The plugin name is not confusable with an existing catalog entry or
   a well-known plugin elsewhere (threat model V5, catalog-level). Check
   `.claude-plugin/marketplace.extended.json` for near-collisions before anything else.
3. **License.** Explicit, present upstream, compatible with redistribution in this
   marketplace, and recorded in the source entry.
4. **Read everything the globs admit.** At the commit you are vetting, read every file that
   will match the `include` patterns — not just SKILL.md. Scripts line-by-line; hook and MCP
   configs command-by-command; every network endpoint accounted for and documented in the
   review. If it is too much to read, the include list is too wide (next item).
5. **Least-privilege globs.** Include only what the plugin needs to function. Never blanket
   `**`. Exclude tests, CI, dotfiles, lockfiles. If the plugin works markdown-only, do not
   sync its scripts — the tier follows the globs, and narrower globs are a smaller attack
   surface forever after.
6. **Assign the tier honestly** per the table above, from what the globs admit.
7. **Dry-run the sync.** `node scripts/sync-external.mjs --dry-run --source=<name>` —
   confirm the file list matches what you read in step 4, and that no "unsupported glob"
   warnings fire (a dead glob is a silent no-op rule).
8. **Run the security scan** over the mirrored tree. REFUSE findings end the listing until
   fixed upstream — no exceptions, no allowlist. CHALLENGE findings are signed off per the
   procedure below, in the same PR. FLAG findings are acknowledged in the review thread.
9. **Set `verified: true` last**, after 1–8, in the same PR, so the flag and its evidence
   land together. The lockfile entries for the source bootstrap from exactly this vetted
   content — the vet commit is the baseline every future drift is measured against.

Contributor-facing conduct throughout (friendly-issue-first, credit preserved, Jeremy's
wording sign-off on any contributor-facing post) is governed by the mirror-by-default
decision record § Respectful-contributor protocol.

## Lockfile drift review — the quarantine PR

With pinning in place (branch `feat/sync-lockfile-pinning`), the weekly sync compares every
mirrored file's hash against `sources.lock.json`:

- **Match** → the source flows into the routine sync PR, as today.
- **Drift** → the source is held out into its **own quarantine PR**: that source's diff only,
  plus the corresponding lock update. Small, single-origin, readable.

**Reviewing a quarantine PR:**

1. Read the diff as if it were a brand-new submission of the changed files — the original
   vet does not transfer to new content.
2. Scale scrutiny by tier: prose changes → read as instructions (V4); script changes → every
   line; hook/MCP changes → per-entry justification and explicit re-approval, never merged
   on green checks alone.
3. Sanity-check the upstream story: does the change correspond to organic upstream activity
   (commits, release notes, an issue it fixes)? A large unexplained rewrite, a force-push, or
   a brand-new committer on a stable repo warrants slowing down, not just reading harder.
4. Watch the classic escalations: new network endpoints, env/credential access, encoded or
   minified blobs, `allowed-tools` widening, new executable files, glob-boundary creep.
5. **Merging the quarantine PR is the re-vet.** The lock update inside it is the durable
   approval record — who approved, when, which hashes. Never hand-edit the lockfile to
   silence drift without reading the diff; that converts the approval record into a lie.

If the drift is unwanted (upstream went a direction we don't ship): close the quarantine PR
and either drop the source, narrow its globs, or freeze it `curated: true` pending an
upstream conversation.

## Signing off a scan CHALLENGE

The scanner (branch `feat/sync-security-scan`) grades findings so the gate stays credible —
an ungraded gate produces a false-positive storm and gets disabled:

| Verdict       | Meaning                                                                                                                           | Override path                                                                  |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **REFUSE**    | Known-hostile shape (pipe-to-shell, encoded exec, credential exfil).                                                              | **None.** Fix upstream or don't ship the content. REFUSE is not allowlistable. |
| **CHALLENGE** | Legitimate-capable but dangerous-capable (network calls in scripts, env harvesting, hook/MCP changes, `allowed-tools` expansion). | Blocked until a human adds a **scoped allowlist entry**.                       |
| **FLAG**      | Suspicious-but-explainable (obfuscation smells, minified blobs).                                                                  | Non-blocking; acknowledged in the PR review thread.                            |

The bot advisory mode accepted in PR #969 is a scanner execution mode, not a
CHALLENGE approval. It applies only to a same-repository sync PR whose PR number
and exact current head are bound to a receipt from the approved Sync External
Plugins workflow. Human PRs, forks, prefix lookalikes, and missing or mismatched
provenance retain full grading. REFUSE always blocks and is never waivable.
Advisory scan success does not satisfy the scoped human CHALLENGE approval and
reviewed allowlist requirements above.

**Allowlist discipline** (the exact file location and entry format live with the scanner —
see the `feat/sync-security-scan` PR):

1. An entry is scoped as narrowly as the scanner allows — this source, this file, this
   pattern. Never a blanket pattern-wide or source-wide waiver.
2. Every entry carries a justification ("posts release notes to the author's own API,
   documented in their README"), the reviewer's handle, and the date.
3. The allowlist is code: it changes only by reviewed PR, and the sign-off entry should land
   in the same PR as the content it excuses, so approval and evidence stay attached.
4. **Prune it.** An allowlist that only grows becomes a rubber stamp (threat model, residual
   risk #3). When a source is removed or its globs narrow, its entries go too; stale entries
   found during any review are deleted on sight.

## Suspending or removing a source

When an upstream is compromised, goes hostile, or simply dies:

1. **Stop the bleeding.** If a poisoned sync PR is open, close it. If it merged, revert the
   merge commit first, ask questions after.
2. **Cut the source.** Remove its entry from `sources.yaml` (or, for a temporary hold,
   freeze it `curated: true` — note that freezing keeps the current mirror published, so it
   is only appropriate when the _current_ content is trusted and it's the _future_ you're
   blocking).
3. **Remove the mirror.** Delete the plugin directory and its catalog entry in
   `.claude-plugin/marketplace.extended.json`; run the lint-ignore generator so the managed
   exclusion block stays in sync.
4. **Clean the records.** Drop the source's lockfile entries and any scan-allowlist entries.
5. **Disclose.** If users may have installed poisoned content, this is a vulnerability:
   private advisory per SECURITY.md, then a public advisory naming affected plugin versions
   once users can act on it. No public issue before the advisory.

## Review discipline — the anti-fatigue rules

The whole defense degrades to theater if review becomes ritual. Standing rules:

- **Small units or no merge.** The quarantine model exists so no one reviews a 100-file
  multi-source diff again. If a quarantine PR is still too big to actually read, that is a
  reason to freeze or drop the source, not to skim.
- **Green checks are the floor, not the decision** — especially at `hooks-mcp` tier, where
  explicit human re-approval is the gate by policy.
- **Say "no" cheaply.** Closing a quarantine PR costs nothing; the next sync regenerates the
  proposal. The default answer to an unreadable or unexplained drift is no.
- **The audit trail is load-bearing.** Vet evidence in listing PRs, lock updates as approval
  records, justified allowlist entries — these are what let the _next_ maintainer trust the
  state of the mirror without re-deriving it from diffs.

## References

- Threat model: `000-docs/698-TQ-SECU-external-sync-threat-model.md`
- Mirror-by-default decision record: `000-docs/694-AT-DECR-external-sync-mirror-by-default-model.md`
- Repo security policy: `SECURITY.md`
- Umbrella issue: jeremylongshore/claude-code-plugins-plus-skills#966
- Sibling implementation PRs: branches `feat/sync-lockfile-pinning`, `feat/sync-security-scan`
