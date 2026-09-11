---
name: seo-blog-writer
description: 'Research, draft, validate, and hand off one source-grounded long-tail article through an approved CMS or static-site adapter. Use when turning a confirmed topic into publish-ready editorial content. Trigger with "write an SEO blog post" or "draft an article about this topic".'
argument-hint: "[topic] [--target static|ghost|wordpress] [--draft|--publish|--publish-at ISO-8601]"
allowed-tools: Read, WebSearch, WebFetch, Write, Edit, Bash(python3:*)
version: 2.3.0
author: AutomateLab <hello@automatelab.tech>
license: MIT-0
tags: [seo, content-writing, source-verification, structured-data, publishing]
model: inherit
effort: high
compatibility: Designed for Claude Code; claims require current sources, and CMS writes, schedules, publication, destructive edits, and credential use require content-owner approval
---
# Source-Grounded SEO Blog Writer

## Overview

Turn one approved long-tail topic into a reviewable article bundle: research notes, clean draft, metadata, structured-data recommendations, link inventory, and an adapter handoff. The default is local draft output; live publication is never inferred.

Optimize for reader usefulness and accurate extraction, not keyword stuffing or synthetic authority. Structured data must describe visible page content and does not guarantee rankings or AI citations.

## Prerequisites

- A specific topic, intended reader, search intent, locale, brand voice, and review owner
- Current first-party sources plus independent sources where comparison or risk claims need them
- Existing site inventory for internal links and cannibalization checks
- A writable local draft directory
- For CMS delivery, an approved target and credentials supplied through environment variables or the platform's secret store
- For optional local validation scripts, Python 3 and dependencies already approved by the owner

## Tool Discipline

Use `Read` to inspect the editorial brief, brand guidance, and existing coverage. Use `WebSearch` for discovery and `WebFetch` to verify current sources. Use `Write` or `Edit` for local draft artifacts. The scoped `Bash(python3:*)` authority is only for reviewed local validation and approved adapter scripts with quoted paths and environment-provided credentials; never echo secrets or place them in prompts, URLs, drafts, fixtures, logs, or receipts.

## Instructions

1. Parse the topic and flags. Reject an empty or overly broad topic. Default to `--target static --draft`; treat `--publish` and `--publish-at` as explicit, mutually exclusive owner instructions.
2. Check existing titles, slugs, canonical URLs, and intent. Stop or narrow the angle when the proposed post would cannibalize existing coverage.
3. Research the topic with current sources. For each material claim, record URL, publisher, date, retrieval date, supported statement, and confidence. Prefer official documentation for product behavior and primary data for numbers.
4. Define the reader's problem, desired outcome, exclusions, format, and claim boundary before drafting. Do not invent metrics, quotes, prices, versions, customer stories, or observed results.
5. Build an outline that answers the primary question early, then supports it with logically ordered sections. Headings should describe reader tasks or decisions, not mechanically repeat keywords.
6. Draft in the approved voice. Distinguish fact from inference, date volatile claims, use code only when tested or clearly labeled illustrative, and include limitations where a reasonable reader could be misled.
7. Add internal links only when they improve the reader's path. Verify external links, use descriptive anchor text, and record sponsorship or affiliate disclosures required by policy.
8. Add FAQ, breadcrumb, article, or how-to structured data only when the visible page and site implementation satisfy the applicable Google schema requirements. Never mark up hidden, invented, or unsupported content.
9. Produce a safe slug, title, description, canonical suggestion, social image brief, accessible alt text, taxonomy, and publication timestamp. Keep the canonical host and author identity configurable.
10. Run the pre-publish checks: source coverage, link validity, HTML structure, code safety, accessibility, disclosure, spelling, duplicate intent, and metadata consistency. Sanitize generated HTML according to the target platform.
11. Write the local bundle and present a review summary. Require approval for the final title, claims, media, links, disclosures, and target state.
12. If approved, invoke the selected adapter with least-privilege credentials. Create a draft first when the platform supports it; publish or schedule only when the explicit approved state matches the request.
13. Re-fetch the CMS record after mutation. Record its ID, state, canonical URL, scheduled time, and content checksum without storing credentials.

## Bundle Contract

The default static handoff contains:

```text
tmp/blog-drafts/<slug>.research.md
tmp/blog-drafts/<slug>.draft.html
tmp/blog-drafts/<slug>.metadata.json
tmp/blog-drafts/<slug>.receipt.json
```

The metadata should include title, slug, description, canonical suggestion, author, tags, source URLs, review state, target adapter, desired publication state, and checksums. Keep secrets outside the bundle.

## Adapter Safety

- **Static site:** validate the destination is inside the approved repository and refuse path traversal or silent overwrite.
- **Ghost:** use the configured Admin API origin and an environment-provided Admin key; verify the response belongs to the same origin.
- **WordPress:** use HTTPS, an environment-provided application password, and the minimum account role required for the requested state.
- **Other CMS:** document endpoint, authentication, retry, idempotency, sanitization, and rollback behavior before first use.

Never install packages, create accounts, change permissions, delete posts, rotate credentials, or publish through a new adapter without owner approval.

## Authentication

Ghost uses an Admin API key provided through the operator's secret store or environment and sent only to the configured Ghost origin. WordPress uses an application password or another owner-approved WordPress authentication method over HTTPS. Static output uses no network credential. Adapter scripts must read credentials at runtime, redact request diagnostics, refuse unexpected origins, and never serialize authentication material into the bundle.

## Approval Boundaries

Require explicit approval before live publication, scheduling, updating an existing post, uploading assets, destructive replacement, using affiliate claims, or making regulated advice. Human review is mandatory for legal, medical, financial, safety, security, and reputationally sensitive content.

## Output

Return:

- local bundle paths and checksums
- concise article and audience summary
- source-to-claim coverage and unresolved claims
- metadata, structured-data types, internal/external link counts, and disclosures
- validation results and review decisions
- adapter target, CMS ID, resulting state, canonical URL, or explicit reason no mutation occurred
- rollback or correction instructions for any live change

## Error Handling

| Condition | Response |
|---|---|
| Required claim lacks a current source | Remove or qualify the claim; do not fill the gap from memory. |
| Sources materially disagree | Describe the disagreement, date each position, and require editorial judgment. |
| Draft duplicates existing search intent | Stop publication and propose consolidation, redirect, or a narrower angle. |
| Validation or sanitization fails | Keep the local draft, report exact failures, and do not invoke the CMS adapter. |
| CMS request times out or returns an unknown result | Query by idempotency key or draft slug before retrying to avoid duplicates. |
| Publish succeeds but verification fails | Preserve the CMS ID, stop further mutation, and offer owner-approved rollback or correction. |
| Credential appears in output | Stop, redact the artifact, rotate the exposed credential, and audit logs before continuing. |

## Examples

Create a local draft from a verified brief:

```text
request: "How to diagnose webhook signature failures" --target static --draft
sources: 4 verified, 2 primary
bundle: tmp/blog-drafts/diagnose-webhook-signature-failures.*
claims needing review: 1 performance statement removed
mutation: none
```

Schedule through an approved CMS adapter:

```text
request: same approved bundle --target ghost --publish-at 2026-09-15T14:00:00Z
review: approved by content owner
result: cms_id=post_918; state=scheduled; canonical=https://blog.example.com/example/
verification: state and timestamp re-fetched; credentials absent from receipt
```

## Verification

- Re-fetch decisive sources and confirm each material claim is supported and current.
- Parse the HTML and confirm one title, logical headings, descriptive links, valid language, and alt text for meaningful images.
- Confirm structured data matches visible content and validates for the selected type.
- Confirm the target, desired state, canonical host, author, slug, and scheduled time match the approved metadata.
- After CMS mutation, independently retrieve the record and compare its state and checksum with the approved bundle.
- For a live post, verify the canonical page, rendered metadata, links, images, and structured data without assuming immediate sitemap or search indexing.

## Resources

- [Google Search Essentials](https://developers.google.com/search/docs/essentials)
- [Google guidance for helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
- [Ghost Admin API overview](https://docs.ghost.org/admin-api/)
- [WordPress REST API handbook](https://developer.wordpress.org/rest-api/)
- [OWASP Cross Site Scripting Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

## Next Steps

Route the bundle through editorial review, then publish through the approved adapter. Schedule a source-freshness review for volatile claims and update or retire the article when its evidence changes.
