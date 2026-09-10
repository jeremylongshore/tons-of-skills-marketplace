---
title: "Hardening a Marketplace in One Day"
description: "A gate that travels with the contributor workflow closes one leak across 16 plugin trees. A new install integrity schema names what portable installs must carry."
date: "2026-09-08"
tags: ["security", "marketplace", "governance", "typescript", "devops", "release-engineering"]
featured: false
canonical: "https://startaitools.com/posts/hardening-a-marketplace-in-one-day/"
---
The day's spine is one shared seam. An Omarchy plugin tree is the repository itself, shipped as the plugin. AGENTS.md and CLAUDE.md are operator instructions, not runtime assets. Both used to ride along on every install. On 2026-09-08 a single gate closed that leak across the whole estate, a new integrity schema named what a portable install must carry, and a separate security sweep tightened four more surfaces in claude-code-plugins.

The seams are different and the lesson is the same. When many small surfaces share a threat model, harden them all in one pass and ship the gate next to the contributor workflow, not next to the runtime.

## The C44 gate and the leak it closes

The contributing-clanker shipped `c44-omarchy-installable-tree.sh` on 2026-09-08. It is 26 lines:

```bash
HITS=$(gate_tree_files '(^|/)(AGENTS|CLAUDE)\.[mM][dD]$' || true)
if [[ -n "$HITS" ]]; then
  FILES=$(printf '%s\n' "$HITS" | LC_ALL=C sort | paste -sd ', ' -)
  gate_block "agent instruction file in installable plugin tree: $FILES" \
    "keep operator and AI instructions in the containing workspace; do not ship AGENTS.md or CLAUDE.md with an Omarchy plugin"
fi
gate_pass "installable plugin tree excludes agent instruction files"
```

The gate checks `manifest.json` for `entryPoints` to confirm the tree is an Omarchy plugin, walks the installable tree for any file matching `AGENTS.md` or `CLAUDE.md` (case-insensitive), and blocks the submission with a fix message that points at the right workspace.

omarchy-omatrail-entry applied it in the same commit wave. PR #4 added the missing `.gitignore` entries and dropped the existing AGENTS.md and CLAUDE.md from the installable tree, then re-ran the rig proof so the new state sealed cleanly. `.rig-proof.json` flipped its source-package sha256 from `c102f0e0...` to `a992a56d...`, the sourceCommit rolled forward to `37c5c7e8...`, and the runId rotated. The seal cycle costs three commits for the gate plus the rig re-proof, and that is what closing the seam looks like at the repo level.

The interesting part is not the gate. It is the location. C44 lives in `skills/contribute/scripts/gates/`, the same directory as C28 through C43, which means a contributor submitting any Omarchy entry now hits the rule before the plugin ever reaches the marketplace. The gate travels with the contributor workflow, not with the marketplace runtime.

## Sixteen trees got the same contributor workflow on the same day

That is the multiplier. The same day, sixteen omarchy entry repos each merged a `chore: standardize contributor workflow` PR. The count by entry (one commit each except listening-post and omatrail): capture-conveyor, crew-chief, desk-transition, loose-ends, foundry, bazaar, docket, flow-boundary, mlb-booth, wait-state, omatrail, quiet-queue, pit-wall, x-files, workspace-storyboard, widget-template.

Each PR added the same shape: a `.github/ISSUE_TEMPLATE/maintainer_interest.md`, a rewritten `.github/PULL_REQUEST_TEMPLATE.md`, an extended `.github/workflows/test.yml`, a `CONTRIBUTING.md`, and `scripts/ci-change-scope.sh` plus a `c44-omarchy-installable-tree.sh` reference in the gate lane manifest. The harness hash moved on every repo. The gate lane manifest picked up C44 on the entries that ship plugins.

The pattern matters because the alternative is one-off fixes per entry, which is what produced the AGENTS.md leak in the first place. Standardising the contributor workflow means a new gate added today is enforced on every entry tomorrow without a per-repo follow-up PR.

omarchy-listening-post-entry also shipped a real fix that day, separately from the template: a panel anchoring bug in the KeyboardPanel QML component was clearing the pill anchor because `centerOnBar: true` discarded `anchorItem` for top or bottom bars. Clearing the flag and adding a render-proof test fixed it. The fingerprint rolled from `059e179b...` to `ac4b9b3...`.

## The portable install integrity contract

The other substantial commit of the day is `feat(cli): define portable install integrity contract` (#1454), which lives in `packages/cli/src/lib/portable-integrity.ts`. 727 lines of TypeScript, plus a 156-line JSON schema at `packages/cli/schemas/portable-install-receipt-v1.schema.json`, plus a 502-line test file, plus a CLI publish workflow step that runs the contract and unit tests before build.

The contract names four constants: `PORTABLE_INSTALL_RECEIPT_SCHEMA_VERSION = 'portable-install-receipt/v1'`, `PORTABLE_TREE_FORMAT = 'portable-skill-tree/v1'`, `PORTABLE_TREE_ALGORITHM = 'sha256-tree-v1'`, and `PORTABLE_INSTALL_RECEIPT_FILE = '.ccpi-portable-install.json'`.

The contract also names the bounded inputs. Five size caps: `MAX_RECEIPT_BYTES` at 1 MiB, `MAX_TREE_ENTRIES` at 10,000, `MAX_EVIDENCE_ENTRIES` at 64, plus `MAX_GIT_OUTPUT_BYTES` and `MAX_TREE_BYTES` at 64 MiB each. The minimum harness registry version is 2. The canonical source pattern is `plugins/<vendor>/<plugin>/skills/<skill>`. Windows reserved names (`con`, `prn`, `aux`, `nul`, `com[1-9]`, `lpt[1-9]`) are rejected up front.

What this buys: when a CLI command ships a portable install (a `portable-skill-tree/v1` directory plus a `.ccpi-portable-install.json` receipt), the recipient can verify the receipt against the schema, the tree against the algorithm, and the canonical source against the path pattern, in that order, with bounded inputs and a known registry version. The integrity story is the same whether the install came from a marketplace download, a CI artifact, or a developer machine.

The review trail on this commit is also worth keeping. It went in as 8 commits on one PR: the feature, an auto-bump (npm patch plus display minor), three test rounds (`pin canonical source parity`, `stabilize Git integration timing`, `address final integrity review findings`), a `version portable contract boundary explicitly` fix, and a governance scorecard refresh. The auto-bump commit carries the literal sign-off `jeremy made me do it / -claude`, which is the only honest commit footer on the estate.

## The security sweep in claude-code-plugins

The other 13 commits on 2026-09-08 in claude-code-plugins are hardenings on existing surfaces, each on its own PR, each on its own threat model.

**Gitleaks policy hardening (#1468).** 622 insertions, 88 deletions across the gitleaks config and the validator. The interesting bit is in `.github/workflows/validate-plugins.yml`: the checkout action now sets `fetch-depth: 0` (full history plus tags) so the secret-fingerprint verifier can prove every ignored finding is ancestral to an exact, pinned annotated release tag rather than trusting a PR-created ref. The workflow also adds `permissions: contents: read` so the read-only token cannot be escalated.

**CodeQL parser and URL boundaries (#1464).** 564 insertions across `check-jrig-db-boundary.mjs` (parser hardening) and `check-official-links.mjs` (URL boundary). The CodeQL workflow itself was re-scoped from PR-only-first-party to include repository automation after current-main high findings in `scripts/` proved that excluding automation leaves security fixes unverifiable until after merge.

**Four high-severity CodeQL findings (#1455).** 472 insertions. Added `internal-link-utils.mjs` plus tests, split `validate-internal-links.mjs` and `sitemap-xml.test.mjs`, hardened `check-identity-compatibility.mjs`. The validate-plugins workflow now runs the four marketplace regression tests (skill-redirects, install-skill-redirects, internal-link-utils, sitemap-xml) in one step.

**Windows path contracts (#1461).** A new workflow file plus hardenings across 30 scripts. The workflow is `windows-path-contract.yml`, runs on PRs and `workflow_dispatch`, and the same contract tests run in required Linux jobs. This one is marked advisory real-Windows evidence rather than required CI because hosted-runner availability is provider-dependent.

**Identity compatibility (#1474).** The smallest patch of the day and the most surgical:

```javascript
function directCallsIn(node, receiver, method) {
  const calls = [];
  const visit = (current) => {
    // Calls inside any nested function are not part of buildProgram's executed
    // registration flow. This includes a function-like node passed as the root
    // (for example, a variable initializer containing a decoy function).
    if (ts.isFunctionLike(current)) return;
```

A 4-line change. Before, the visitor skipped only nested functions not equal to the root, which let a decoy nested function in a variable initializer satisfy the program identity contract by name without ever executing. Now any function-like node stops the descent. The new test exercises a `decoyName()` inside `buildProgram()` and a `decoyCommand()` assigned to `const skills = function ...` and confirms the contract still flags both as a violation.

The sweep shape matters. Five separate PRs, each on its own threat model, each on its own review surface. None of them were a debugging journey; all of them were hardenings of an existing rule that had a known gap. The cost is the total of the diffs, and the receipts are the 5 PRs plus the harness-hash delta in the repo.

## Also shipped

contributing-clanker also rewrote `skills/contribute/SKILL.md` from 953 lines down to a fraction of that, splitting the content into four references (`operations.md`, `repo-intake.md`, `submission-policy.md`, `workflow-guide.md`). The skill went from a single long document to a short entry plus four pull-only references, which keeps the skill on first-load under a tighter budget and lets a contributor pull only the reference they need. That commit actually landed on 2026-09-09 at 03:09 UTC but was prepared on 2026-09-08 and is the natural pair to the C44 gate.

claude-code-plugins also dual-published yesterday's `the-cost-of-one-feature-in-a-sealed-repo` to tonsofskills.com/blog via `marketplace/src/content/blog-posts/`. The Astro copy carries the canonical pointer back to startaitools.com, which is the right direction.

## Why a single-day sweep

The seam the day closes is the same on every surface. AGENTS.md and CLAUDE.md were leaking into Omarchy plugin trees because they lived in the same repo as the plugin. The gitleaks allowlist had to trust PR-created refs because the checkout depth was 2. The CodeQL parser trusted a function-name match without checking call-site reachability. The portable CLI had no documented contract for what an install actually carries.

Closing one leak on one repo fixes one repo. Closing one leak on a gate that travels with the contributor workflow fixes every repo the gate will ever see, which on 2026-09-08 was sixteen of them, and on every day after that is every entry repo that adopts the template. The integrity schema does the same for portable installs. Both are cheap to write, expensive to skip.

## Related Posts

- [Verified Plugins Program: Building a Quality Signal for the Marketplace](https://startaitools.com/posts/verified-plugins-program-quality-signal-for-the-marketplace/)
- [A green result only covers what it ran](https://startaitools.com/posts/a-green-result-only-covers-what-it-ran/)
- [The Cost of One Feature in a Sealed Repo](https://startaitools.com/posts/the-cost-of-one-feature-in-a-sealed-repo/)
