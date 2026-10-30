---
title: 'SaaS Skill Packs: Platform Integrations'
description: 'Learn how SaaS skill packs provide platform-specific Claude Code integrations. Covers available packs, anatomy, usage, and how to create custom SaaS packs for any platform API.'
section: 'guides'
order: 4
keywords:
  - 'SaaS pack'
  - 'skill pack'
  - 'platform integration'
  - 'API skills'
  - 'Stripe'
  - 'GitHub'
  - 'Slack'
  - 'Vercel'
  - 'SaaS integration'
  - 'Claude Code integrations'
officialLinks:
  - title: 'Anthropic Claude Code Documentation'
    url: 'https://code.claude.com/docs/en/'
  - title: 'Tons of Skills Marketplace'
    url: 'https://tonsofskills.com/explore'
relatedDocs:
  - 'concepts/plugins'
  - 'concepts/skills'
  - 'ecosystem/marketplace-overview'
---

## What a SaaS pack contains

A SaaS pack groups instructions for one provider's real operator workflows: authentication, common operations, errors, deployment, security, and recovery. It is still an instruction artifact unless it separately ships a runtime integration. Describing an API is not the same as executing it or certifying a deployment.

Repository packs live under `plugins/saas-packs/`; matching `*-pack` directories are included by the repository workspace configuration. Their Node package metadata may be generated or explicitly custom-owned. Do not overwrite custom metadata or assume every pack is a private npm package.

## Find current packs

Use [Explore](/explore) and the current catalog's `saas-packs` entries. Do not copy an old table of hypothetical integrations into an availability claim.

For example, `apollo-pack` describes Apollo sales engagement and prospecting, not Apollo GraphQL. `claude-pack` describes the Claude API and Anthropic SDK, not a promise to cover all Claude Code plugin authoring. Provider names can refer to different products; read the actual entry and source.

Examples such as `stripe-pack`, `github-pack`, `netlify-pack`, and `square-pack` in older versions of this page were not registered identities at the reviewed snapshot. A hypothetical tutorial name must not be presented as an installable pack.

## Install a registered pack

After reviewing the actual pack, use native marketplace installation. For a registered example:

```bash
claude plugin marketplace add jeremylongshore/tons-of-skills-marketplace
claude plugin install claude-pack@claude-code-plugins-plus --scope project
```

Adding the marketplace does not install every pack. Native scope, enablement, and reload behavior still apply. Use namespaced commands or skills from the actual installed artifact; an imagined `/stripe-setup` command is not evidence of a real installed component.

See [installation](/docs/getting-started/installation) for companion-versus-native differences and [the current native guide](https://code.claude.com/docs/en/discover-plugins) for supported management commands.

## Design a coherent pack

Start with real, evidence-backed outcomes rather than a target number of skills. A provider with three distinct workflows and one with thirty need different structures; there is no universal3–8 skill acceptance rule here.

A useful inventory records each identity's purpose, current primary sources, credential scope, input/output contract, destructive or costly actions, failure handling, and test evidence. Treat mutable provider facts such as quotas, API versions, SDK floors, and prices as versioned facts to verify, not generic boilerplate.

```text
plugins/saas-packs/example-provider-pack/
  .claude-plugin/plugin.json
  README.md
  LICENSE
  skills/provider-read-only-review/
    SKILL.md
    references/api-contract.md
    references/reviewed-cases.md
```

This is an illustrative layout, not an existing provider integration or an executable scaffold.

## Use the current authoring contract

The plugin manifest uses an author object and the marketplace envelope described in [the manifest reference](/docs/reference/plugin-json-schema). Skills require the unchanged eight marketplace fields, including `compatibility` and `tags`; `compatible-with` is deprecated.

Use [the complete skill example](/docs/guides/write-a-skill) as an authoring starting point, then replace the generic review behavior with the provider's actual supported workflow. Do not label an incomplete payment snippet “PCI-compliant” or assume an old SDK lower bound accepts a later pinned API version. Pin and test the selected SDK/API combination against its primary documentation.

## Provider reference fragment

The following is an intentionally partial API-reference format, not a live request or complete Stripe integration. The endpoint and chosen parameters must be verified against the selected API version before use:

````markdown
# Reviewed Checkout Contract

Record the provider API version, SDK version, required credentials, and the
approved operation before implementing a request.

```json
{
  "example_response_id": "synthetic-only",
  "scope": "illustrative response shape, not a provider receipt"
}
```

Document success, validation errors, authorization failures, retries, and
partial-operation recovery using the actual provider contract.
````

Keep secret credentials server-side. User/session authorization, provider API authentication, webhook verification, data minimization, and legal/compliance review are separate boundaries. A client library or payment widget alone does not certify the whole application.

## Write useful supporting material

Each retained instruction should link to actual local references. Include dated primary sources where facts can change, exact supported request/response examples, approved credential handling, and meaningful failure cases. Do not defer core runtime behavior to mutable upstream-main instructions without a reviewed provenance boundary.

Separate read-only diagnostics from changes that create accounts, alter billing, delete data, send messages, deploy code, or invoke paid APIs. A tool grant or installed CLI does not itself authorize those actions.

## Validate without inventing a quality policy

From the repository root, replacing the illustrative path:

```bash
python3 scripts/validate-skills-schema.py --standard --verbose plugins/saas-packs/example-provider-pack/
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/saas-packs/example-provider-pack/
```

The current rubric's B band starts at80, but a rubric band is not an automatic acceptance decision. There is no universal500-word minimum or requirement to manufacture one-pagers. Preserve actual operator value, current sources, valid metadata, meaningful examples, and honest evidence; do not pad content to satisfy a retired tutorial rule.

Do not run an unbounded `batch-remediate.py --all --execute` to “upgrade” a pack. Any fixer requires an authorized finite scope, selected supported fixes, a reviewed preview, and preservation of upstream mirror ownership. It does not supply missing product behavior or certify provider correctness.

Once authored changes are approved, follow the canonical verification, catalog, search, curated, and measurement producers that actually apply. Do not hand-edit generated packages or mirrors, and do not treat a successful sync as proof of every projection.

## Next steps

- [Build the enclosing plugin](/docs/guides/build-a-plugin)
- [Review skills and their frontmatter](/docs/reference/skill-frontmatter)
- [Publish through the current review process](/docs/guides/publish-to-marketplace)
