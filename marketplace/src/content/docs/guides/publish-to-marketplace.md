---
title: 'Publish a Plugin to the Marketplace'
description: 'Complete guide to publishing a Claude Code plugin to the Tons of Skills marketplace. Covers requirements, marketplace.extended.json, sync-marketplace, enterprise validation, submission process, and versioning.'
section: 'guides'
order: 6
keywords:
  - 'publish'
  - 'marketplace'
  - 'submit plugin'
  - 'marketplace.extended.json'
  - 'sync-marketplace'
  - 'enterprise validation'
  - 'Tons of Skills'
  - 'plugin submission'
  - 'versioning'
officialLinks:
  - title: 'Tons of Skills Marketplace'
    url: 'https://tonsofskills.com'
  - title: 'Anthropic Claude Code Documentation'
    url: 'https://code.claude.com/docs/en/'
relatedDocs:
  - 'guides/build-a-plugin'
  - 'reference/plugin-json-schema'
  - 'ecosystem/marketplace-overview'
---

## Start with ownership and the current contract

This marketplace publishes native plugins and portable instruction surfaces with different runtime and provenance requirements. Review the [current contribution guide](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/.github/CONTRIBUTING.md) and [STANDARDS.md](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/STANDARDS.md) before authoring a submission.

An entry in the catalog is not automatic approval, provider endorsement, featured placement, or behavioral certification. Use the current [published catalog](/explore) rather than undated plugin, skill, or user totals.

## Prepare the actual artifact

A repository-owned instruction plugin needs a coherent manifest, README, license, and the components it claims. Runtime plugins also need their launch artifacts and dependencies. A complete marketplace skill has eight required frontmatter fields and substantive body sections; a header-only placeholder is not implementation.

Use [Build a plugin](/docs/guides/build-a-plugin), [Write a skill](/docs/guides/write-a-skill), and the [manifest reference](/docs/reference/plugin-json-schema) for examples. Keep native format minimums separate from the marketplace overlay. Plugin `author` is an object; the marketplace envelope includes a valid homepage and `commands`, even when that array is empty.

Pure external mirrors remain upstream-owned. Register them through the reviewed `sources.yaml` / lock workflow, preserve attribution and license, and submit improvements upstream. Do not locally rewrite mirrored files or waive capability findings to make a submission pass.

## Validate before submission

From the repository root, substitute the actual author-owned path:

```bash
set -euo pipefail
python3 scripts/validate-skills-schema.py --standard --verbose plugins/category/my-plugin/
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/category/my-plugin/
claude plugin validate ./plugins/category/my-plugin
```

`--standard` requests the open format floor; marketplace mode requires the repository's eight fields, including `compatibility` and `tags`. Agent validation has a separate strict envelope. Include substantive Overview, Prerequisites, Instructions, Output, Error Handling, Examples, and Resources, or accepted equivalent headings, as appropriate to the actual contract.

The current static rubric has five pillars: progressive disclosure30, ease of use25, utility20, spec compliance15, and writing style10, plus documented modifiers. Letter bands are A90–100, B80–89, C70–79, D60–69, and F below60. These are grading facts, not a new fixed acceptance threshold or proof the plugin works in production.

Exercise meaningful success and failure paths for executable code. Check credentials, data handling, output bounds, failure propagation, child cleanup, and installed entry paths where relevant. A companion `ccpi validate` result is not a complete native manifest, secret-scanning, or retained behavioral-evaluation receipt.

## Add the catalog entry through its owner

`.claude-plugin/marketplace.extended.json` is the editable listing source. This fragment illustrates a local source and category; it is not a complete submission or a plugin manifest:

```json
{
  "name": "example-review",
  "source": "./plugins/devops/example-review",
  "description": "Review selected configuration and return evidence-linked observations.",
  "version": "1.0.0",
  "category": "devops"
}
```

Follow the current entry shape and source ownership rules. Use a current category from the catalog, not a retired17-value table. `repository` alone does not declare the local plugin source or authorize an external mirror.

Regenerate derived surfaces with their canonical producers:

```bash
pnpm run sync-marketplace
```

Do not hand-edit `marketplace.json`, generated plugin packages, the README catalog block, or site/search projections. Skill-content changes require the canonical verification and affected projection workflow; sync alone does not cover every output. Freshie's inventory, history, and promotion pipeline are governed evidence operations, not an optional arbitrary database write each contributor should run. See [Freshie's documentation](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/freshie/README.md).

## Submit a reviewable change

1. Create an ordinary branch and preserve unrelated files and contributor history.
2. Stage only the authored and legitimately regenerated paths.
3. Use the registered commit/PR scope from `.github/.commit-rules.json`.
4. Explain the concrete behavior change, ownership, affected outputs, and meaningful checks.
5. Report failures and untested boundaries honestly; do not turn absent evidence into a pass.
6. Let required exact-head CI and repository review rules govern the merge.

The required contexts remain `ci-required`, `gitleaks`, and `skill-conform`; their actual jobs and routing live in the canonical CI documents. Static grades and advisory reviews are different evidence classes. This guide does not change approval, waiver, policy, or baseline authority.

## Versions and updates

The repository's approved routine formula uses MINOR changes for display surfaces and PATCH changes for npm. These namespaces can legitimately differ. Follow [blueprint727 V1](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/000-docs/727-AT-ARCH-master-modernization-blueprint.md) and current auto-bump automation rather than manually forcing npm and display versions to match.

Describe actual behavior changes and validation in the PR and changelog where required. Do not add dynamic shell preprocessing for score points or run an unbounded whole-corpus batch fixer from a tutorial. If a scoped remediation tool is appropriate, preview a specifically authorized cohort, inspect the exact diff, and use its documented scope and failure semantics.

## Publication checklist

- Authorship, source ownership, and license are explicit.
- Manifest and components satisfy their actual native and marketplace contracts.
- Instruction examples are complete or clearly labeled fragments; no unsafe unfinished runtime stub is advertised as working.
- The exact artifact's success, failure, and cleanup behavior is tested where applicable.
- Generated projections come from canonical producers and match the reviewed source.
- Credentials and personal data are absent from shared evidence.
- Version namespaces and current catalog identity agree with governed automation.
- Required CI and review evidence are for the actual final head.

After merge, check the published identity and installation bytes. A cached third-party page or a successful listing render is not proof that all runtime or portability requirements have been met.
