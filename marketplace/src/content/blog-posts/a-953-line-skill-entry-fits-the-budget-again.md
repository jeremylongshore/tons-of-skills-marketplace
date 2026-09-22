---
title: "A 953-line skill entry fits the budget again"
description: "A 953-line skill entry collapses to 267 lines plus four pull-only references, and the same day seventeen Omarchy repos pin the audit-harness and review Action to the same SHA."
date: "2026-09-09"
tags: ["claude-code", "skills", "release-engineering", "security", "dependency-management", "omarchy"]
featured: false
canonical: "https://startaitools.com/posts/a-953-line-skill-entry-fits-the-budget-again/"
---
The day reads as two coordinated hygiene passes. The first is internal to the
contributing-clanker skill entry, and the second is a single dep-refresh PR
applied to seventeen Omarchy entry repos. They share the same shape: a long
running surface (a single SKILL.md; a long-running audit-harness pin) gets
trimmed or locked, and the receipt is a number plus a hash.

## The SKILL.md that nobody could load in full

contributing-clanker PR #77 (commit `63df1ee`, 2026-09-09 00:40 UTC) cut
`skills/contribute/SKILL.md` from 953 lines to 267 lines, a 72% reduction. The
content moved into four reference files, three of them new:

- `references/operations.md` (69 lines, new): dashboard, live reconciliation,
  override audit, runtime drift, dry-run email policy.
- `references/repo-intake.md` (91 lines, new): GitHub URL or `owner/repo` slug
  parsing, owned-repo scope guard, new versus known-repo briefing.
- `references/submission-policy.md` (143 lines, new): required fit fields,
  collaboration surface, counterparty design intent, candidate updates after
  submission.
- `references/workflow-guide.md` (153 to 112 lines): trimmed end-to-end flow.

The SKILL.md itself now reads as a thin index. Step 1 (Detect invocation mode)
points at `[repo intake](references/repo-intake.md)` and `[operations](references/operations.md)`.
Step 3 (Require a current dossier and first-touch fit) points at
`[submission policy](references/submission-policy.md)`. The Resources section
at the end lists all seven reference files in plain markdown links. A
contributor who needs only the daily status flow pulls only `operations.md`;
a contributor onboarding a new repo pulls only `repo-intake.md`.

The diff is 558 insertions and 893 deletions across the five files. The skill
fits a tighter first-load budget, and the references stay readable as their
own documents because each one was written with its own scope.

A small but telling diff: the front matter changed the `allowed-tools` entry
from `- Task` to `- Agent`. The skill entry now declares the modern subagent
tool rather than the deprecated one, which would have produced a stale warning
on every invocation. The wording of the description block also tightened: from
a multi-line justified narrative to a one-paragraph capability statement.

## Seventeen repos pin to one SHA

The second batch is a coordinated dep refresh that landed across all
seventeen Omarchy entry repos on the same day. Each repo merged a single
`chore(deps): refresh ecosystem dependencies (#N)` PR with an identical
commit body: "Updates the audit harness and review Action, removes the
vulnerable qs override, hard-pins remaining Actions, fixes the maintainer
intake link, and refreshes the reviewed anti-tamper seal. Local and remote
gates passed."

The substantive changes per repo are the same five:

1. `@intentsolutions/audit-harness` bumped from `^1.3.1` to `^1.4.0`.
2. The review Action `jeremylongshore/minimax-code-review` bumped from
   `d1314b96c1b261d5bf026d0a669823a7e5ce6b46` to
   `bcaa65182e52183f14746663aa2049641c0dbca5 # v0.5.0`. Every reference in
   `.github/workflows/minimax-review.yml` now uses the same SHA with a
   `# v0.5.0` comment, so a reader can audit the pin by eye.
3. A vulnerable `qs` override is removed from `package.json` (the dep
   update replaces the override with a fixed upstream version).
4. The remaining Actions in `gates.yml` and `minimax-review.yml` are
   hard-pinned to full SHAs where they were previously referenced by tag.
5. The maintainer-intake link in `README.md` is fixed from a relative
   `../../issues/new?template=...` to an absolute
   `https://github.com/jeremylongshore/<repo>/issues/new?template=...`,
   which works whether the README is read on GitHub or from a clone.

The `.harness-hash` file rolls on every repo. Reading the
capture-conveyor-entry diff shows the new hash entries for
`.github/workflows/minimax-review.yml` and `package.json` (the two files
whose contents changed); the other entries stay byte-for-byte identical.
That is the audit surface verifying the seal: every file listed in
`.harness-hash` was reviewed and approved as part of the new state.

The seventeen repos touched: bazaar, capture-conveyor, crew-chief,
desk-transition, docket, flow-boundary, foundry, listening-post,
loose-ends, mlb-booth, omatrail, pit-wall, quiet-queue, wait-state,
widget-template, workspace-storyboard, x-files. (mlb-booth got the
refresh plus its own separate feature commit, covered below.)

## omarchy-mlb-booth-entry: persist club and clock settings

The mlb-booth entry repo shipped an additional commit on the same day that
was not part of the dep-refresh wave: `6366a3a feat: persist club and
clock settings (#5)`, by David Reed. A new `SettingsForm.qml` (358 lines)
adds keyboard-accessible settings for all 30 clubs and 12 or 24-hour
first-pitch times, persists the selected club across shell restarts and
failed or stale schedule responses, and adds a deterministic live-feed
loading path.

The commit also updates `Model.js` (55 new lines), `Panel.qml` (210 lines
with churn), `e2e/rig-after-open.sh` (27 lines), and rolls the
`.harness-hash` and `.rig-proof.json` fingerprints. The render-proof
test was the gating surface: the new `.rig-proof.json` records the
panel's post-settings render, and the maintainer approval used the same
seal pathway as the other entries.

This was a real user-facing change on top of the hygiene wave, not part
of the wave itself.

## What the two batches share

Both reads are routine on a single surface and structural on the estate.
The SKILL.md refactor only touches one file's line count in the diff
stat, but it changes what gets loaded when a contributor invokes
`/contribute` and what stays hidden behind a reference link. The
seventeen-repo dep refresh only changes a SHA and a `^` in each repo,
but it locks the audit-harness to one published version across the
whole Omarchy entry estate, removes a vulnerable override from each
clone, and reseals the harness hash for every entry.

The shape is the same. A long-running surface is reduced to a smaller
loadable form, and a long-running pin is hardened against silent drift.
The cost is the diff size; the receipt is the harness hash on each
entry and the references index on the skill entry.

## Related Posts

- [Hardening a Marketplace in One Day](https://startaitools.com/posts/hardening-a-marketplace-in-one-day/) (2026-09-08, the previous day's sweep across the same estate)
- [One Corrected Check, Fifteen Repos](https://startaitools.com/posts/one-corrected-check-fifteen-repos/) (2026-08-30, the multi-repo propagation pattern this day repeated)
- [Enforcement Travels With the Code: Shipping @intentsolutions/audit-harness v0.1.0](https://startaitools.com/posts/audit-harness-v010-enforcement-travels-with-code/) (2026-04-21, the audit-harness origin)
