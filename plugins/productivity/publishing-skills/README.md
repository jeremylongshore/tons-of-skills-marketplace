# publishing-skills

Four composable, platform-aware skills for a governed editorial pipeline:

| Skill | Responsibility |
|---|---|
| `blog-topic-research` | Finds current, traceable demand and rejects weak or duplicate topic ideas. |
| `blog-editorial-calendar` | Balances the backlog, reserves work, schedules approved drafts, and reconciles CMS state. |
| `seo-blog-writer` | Researches and drafts one source-grounded article, validates its bundle, and hands it to an approved adapter. |
| `blog-figure-svg` | Produces accessible, static SVG figures and optional reviewed PNG renders from supported article evidence. |

The skills default to read-only research or local draft creation. Scheduling, CMS writes, live publication, destructive replacement, new software installation, and credential use remain explicit owner-approved actions.

## Install

Install the upstream source with the skills CLI:

```bash
npx skills add AutomateLab-tech/publishing-skills
```

Install this marketplace's reviewed projection:

```bash
npx skills add jeremylongshore/tons-of-skills-marketplace --full-depth
```

Or copy an individual `skills/<name>/` directory into the skill directory used by your agent runtime.

## Workflow

1. Run `blog-topic-research` to create an evidence-backed candidate.
2. Add approved candidates to `blog-editorial-calendar`.
3. Let the calendar select and reserve the next item.
4. Run `seo-blog-writer` to produce a local, reviewable article bundle.
5. Use `blog-figure-svg` when the article contains a supported visual relationship.
6. Review claims, links, media, disclosures, metadata, and target state.
7. Invoke the approved publishing adapter and verify the resulting CMS record.

Each skill can also run independently. The backlog, research record, article bundle, SVG source, and mutation receipt provide durable handoff boundaries.

## Requirements

- An agent runtime that provides the tools declared by each `SKILL.md`
- Current web access for source verification
- A writable local draft directory for generated artifacts
- Python 3 only for optional local validators or rasterizers
- For PNG output, an already approved SVG renderer such as ImageMagick, `rsvg-convert`, Inkscape, or CairoSVG
- For CMS mutation, least-privilege credentials supplied through environment variables or a secret store

No skill should install dependencies automatically, copy credentials into content, or infer permission to publish.

## Platform adapters

`seo-blog-writer` defines guarded handoff contracts for static sites, Ghost, and WordPress. The writing workflow remains independent of the delivery system:

- Static output validates that the destination remains inside the approved repository.
- Ghost uses an Admin API key only against the configured Ghost origin.
- WordPress uses an application password or another owner-approved HTTPS authentication method.
- A new adapter must document authentication, sanitization, idempotency, retry, rollback, and post-write verification before use.

## Quality and safety

Every skill contains:

- complete marketplace metadata and clear trigger phrases
- bounded prerequisites and numbered instructions
- least-privilege tool declarations
- approval boundaries and credential handling
- explicit output and failure contracts
- worked examples and verification steps
- links to authoritative platform or standards documentation

Content research does not invent search volume, product facts, prices, versions, quotes, or performance claims. SVG output forbids active content and unsupported data. Publication defaults to draft unless the owner explicitly approves a live or scheduled state.

## Source and license

The original project is [AutomateLab-tech/publishing-skills](https://github.com/AutomateLab-tech/publishing-skills). This marketplace projection preserves the upstream authorship and MIT-0 license while applying its validation and supply-chain gates.
