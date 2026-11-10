# MCP dependency inventory

The MCP dependency inventory audits the root pnpm production lock once. MCP
packages are workspace members; running `npm audit` separately in each directory
without an npm lock does not audit their dependency graph.

Run from the repository root:

```bash
node --test scripts/audit-mcp-workspace.test.mjs
node scripts/audit-mcp-workspace.mjs --output=mcp-workspace-audit.json
```

The JSON records the shared lock hash, each package manifest hash, importer
coverage, and high/critical findings. The workflow retains that report as
`mcp-workspace-dependency-inventory`. Findings cover the **whole workspace
production lock**, including non-MCP consumers. They are not attributed to an
individual MCP package. Packages without Node dependency declarations are marked
explicitly; this does not establish the safety of their Python, shell or other
runtime dependencies.

The command checks declared dependency names against the shared importer and
delegates specifier and security-override validation to pnpm's frozen lock check,
with lifecycle scripts and pnpm hooks disabled. A failed check, changed lock,
missing importer, unsupported peer consumer graph, malformed audit response or
unavailable audit service exits nonzero. This lane does not silently fall back to
a clean result. A future standalone MCP package needs reviewed lock coverage;
the current command reports it as uncovered.

High/critical advisories remain report-only under the existing dated policy.
The changed-standalone-package dependency audit remains a separate blocking gate.
This implementation does not extend a waiver or authorize promotion of an
advisory lane.

## November 10 investigation

At base commit `0500b275e963c027f6b410e8c49c0446945c574e`, the replacement
inventory found 15 MCP package manifests: 10 covered by the shared production
lock and five without Node dependency declarations. The shared production audit
reported two high and four moderate advisories. The high findings were
`GHSA-mrhx-c7xc-m3w5` in `zod@3.25.76` and `GHSA-mrwp-f3q8-3g9p` in
`follow-redirects@1.16.1`. These are time-specific registry observations, not
claims that every MCP package reaches either dependency.

The separate canonical `--agents-only --verbose` scan reported 230 errors across
31 files, including plugin-manifest checks. The strict CLI reported three skill
errors and six command/agent frontmatter errors. These lanes have distinct
denominators; their totals must not be combined into one compliance count.
Mirror findings require upstream fixes under the repository's ownership policy.

[Issue 1814](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1814)
and bead `bd_000-projects-mv1x8` remain open. The three November 7 deadlines remain
expired. Required CI and PR #1852 remain blocked until the findings and waiver
dispositions are resolved through the governed process.

## Proposed disposition, pending approval

The owned authentication command description was shortened in commit
`b7a02bd22`. A repeat strict CLI scan reports three skill errors and five
command/agent frontmatter errors. The remaining strict findings are in the
Hermes Tweet, Skillcrossroads, Hyperflow and Brand Forge mirrors. Every one of
the 31 error-bearing files in the separate canonical agent scan is under a
`.source.json` mirror ancestor. No mirror was edited locally.

The follow-redirects repair already exists in
[PR #1851](https://github.com/jeremylongshore/tons-of-skills-marketplace/pull/1851);
this PR does not duplicate it. The other high production finding is in the
outdated Slack-channel mirror. Its source already contains the Zod migration.

The proposed Slack source-lock update is from
`89e93c97da24d8d0814b3619eacec2c6694168e6` to
`c4abc2c393729020f1c01838284363b46d60b8a6`.
The [immutable upstream comparison](https://github.com/jeremylongshore/claude-code-slack-channel/compare/89e93c97da24d8d0814b3619eacec2c6694168e6...c4abc2c393729020f1c01838284363b46d60b8a6)
includes upstream-only files as well as the selected mirror files.
The sync preview identifies exactly these selected changes:

- Added: `validation-migration.test.ts`.
- Changed: `README.md`, `biome.json`, `journal.ts`, `lib.ts`, `package.json`,
  `policy.ts`, `server.test.ts`, `server.ts`, `tsconfig.json`.
- Removed: none.

Those ten files have 186 added and 26 removed lines. They upgrade Zod to 4.6.6,
adapt record parsing, preserve legacy integer acceptance, add migration tests,
and align the package name while retaining the old CLI alias. A detached checkout
of the exact proposed upstream revision passed `bun test --timeout 15000`
(1,406 tests) and `bun run typecheck`. This is upstream validation; the resulting
marketplace mirror and regenerated pnpm lock still require their own gates.
The sync preview remains quarantined and has changed no mirror or source-lock
bytes. If approved, the implementation must recheck the exact upstream revision
before invoking the canonical sync and reject any newer, unreviewed revision.

Separately, the proposed waiver disposition extends only the three existing
November 7 report-only deadlines to **November 17, 2026 UTC**. The deadline
checker and all existing blocking gates remain active. The reason is to permit
reviewed repair delivery while upstream mirror findings are resolved: PR #1851
holds the redirect fix, the Slack source migration is ready for review, and the
frontmatter scans retain the explicit mirror findings above. The replacement
inventory fails on missing or inconsistent evidence even during that window.
No new error suppression, baseline change, validator promotion, branch-policy
change or direct author notice is proposed. This is a bounded proposal, not an
approved waiver, and it does not establish completion of issue #1814.
