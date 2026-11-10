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
