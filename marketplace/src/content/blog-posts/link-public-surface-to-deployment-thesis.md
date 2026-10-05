---
title: "Connect every public surface to the new canonical"
description: "An evergreen earns the slot when home and About link to it. Search visitors land without knowing the company; the canonical must reach them on the first read."
date: "2026-09-30"
tags: ["web-development", "release-engineering", "estate-anchors", "content-strategy"]
featured: false
canonical: "https://startaitools.com/posts/link-public-surface-to-deployment-thesis/"
---
When a new canonical document lives in your repo, the discipline is to wire every public surface that mentions the estate to that URL. A 45-line evergreen at `/deployment-thesis/` plus a one-sentence update to the home and About pages is the editorial light on Start AI Tools today, mirrored on Tons of Skills within the same hour. This post is the work journal for what got shipped and why the lead is not "I added a page."

## The discipline

A stranger arriving from a Bing search result or a referral does not know your company exists. They land on a post, a tag page, or the home page, and they have to learn in a single read who runs the work, what connects the properties, and which URL explains that picture. If the home page tells them to read the builds, evaluations, failures, and operating lessons behind the work, but the next sentence does not point at `/deployment-thesis/`, the reader fills the gap with guesses.

The rewiring is two sentences on two pages and one evergreen explainer. That is the editorial cost of an estate anchor (a public URL other properties depend on as a contract rather than a reference).

## What `/deployment-thesis/` actually says

The page runs four sections and a seven-row table. Section one is "From AI capability to production work," which names the company and ties the journal back to the wider practice. Section two names the four-step method (Frame, Build, Prove, Operate) in one paragraph. Section three is "One company, connected work," with a table that maps each public property to a role:

- The main site is the customer-facing engineering practice, starting from a defined business outcome.
- Labs and Evals are experiments, results, and limits.
- Demos is working artifacts visitors can inspect alongside sources and evidence boundaries.
- Learn is practice and knowledge transfer.
- Tons of Skills, OMA, and GitHub are inspectable skills and reusable software with project-specific licenses.
- Products are focused software for specific problems.
- This blog is the dated implementation record.

Section four is "The customer must be able to carry it forward," with a practical test: can the designated team use the agreed materials to run a representative workflow, interpret its evaluation, investigate a failure, and make an agreed change. Independence does not mean self-hosted; it means documented rights, support boundaries, and an exit path in the project's actual scope and terms.

The page runs 45 lines of body. It is positioning copy plus a four-step method, not new framework, not new gate. The page is what was missing from the journal.

## The mirror

The same hour, the same tenant. Tons of Skills PR #1593 (`2 files changed, 9 insertions, 2 deletions`) ships the parallel one-sentence rewrites on its home and About. The two PRs share an intent-os PR (`#709`) as the canonical, and a closed Beads record (`spine-7zn1`) tracks the rollout.

This is the rule: every public surface that mentions the estate gets the rewiring in the same hour. Doing it on the next cron tick would not be acceptable, because the canonical is a contract and the home and About pages are its customers. A contract without customers is a doc page.

## Why the lead is not "I added a page"

Three reasons. First, a single-page addition is the trivial half of the work. The cross-property rewiring is the part that earns the post. Second, the cross-property rewiring is the part that proves the canonical works as a contract: if the contracts depend on a sentence that does not yet link, the contract is broken. Third, a work journal that leads with "I added a page" reads like a marketing release. The work journal reports what got built, what broke, and what it cost; the discipline is the finding, and the discipline is the post.

The exception: when a new canonical lives only in the production system with no public surface pointing at it, the post still works as "I shipped an estate anchor." The architectural line between a page and an anchor is whether the rest of the estate treats the URL as a contract.

## What I almost got wrong

The first draft of the new home sentence tried to do too much. It explained Frame, Build, Prove, Operate in the home page, then asked the reader to read `/deployment-thesis/` for the rest. That is the wrong layer. The home page has one job: point at the canonical. If the home page explains the canonical, it competes with the canonical, and the contract is fuzzier.

The final sentence on the home is:

> Read the builds, evaluations, failures, and operating lessons behind the work. [How the work connects](/deployment-thesis/) explains the relationship between engineering, Labs, Evals, Demos, Learn, reusable tools, and products.

Two sentences. One sentence points at the journal; the next sentence points at the canonical. The About page does the same, with two sentences pointing at the canonical from the FAQ block.

## Validation

The PR validated the pinned production flags: Hugo 0.150.0 production-build, `--cleanDestinationDir`, the existing voice linter, and Chromium at 1440px and 390px across all three routes (home, About, `/deployment-thesis/`). One H1 per page, no horizontal overflow on either viewport, voice lint clean, and About FAQ text aligned with the JSON-LD. The existing About placeholders are unchanged. Estate work: Intent OS Beads `spine-7zn1` and the thesis PR on intent-os.

## Also shipped

- intent-eval-platform: j-rig #322 #323 #324 merged; refiner and refiner-core 0.4.0 and jrig-cli 0.3.0 published with sigstore and SLSA provenance.
- claude-code-plugins: dependabot patches (axios, undici, fast-uri, brace-expansion high advisories) plus an a2a-client bundle rebuild.
- claude-code-plugins: CI gate policy on three lapsed `REPORT-ONLY-UNTIL: 2026-09-30` markers decided per-gate on its merits (PR #1594), with one flipped to blocking and two extended with the remaining counts.
- now-lms: post-deploy cleanup PRs #127, #130, #131, with explicit demo quiz deletes, seeded admin cert removal, and `/app` on PYTHONPATH for the cleanup job.
- intent-os: forms-api nodemailer 9.1.1 to 10.0.12 upgrade (PR #706), Documenso receipt docs (#705), and Documenso executed-applicant-NDA archival via the gate general path.

## Use this

- Pick one URL on each public surface that owns the picture of the estate. If the URL does not exist, write it. If the URL exists, point at it. The cost is two sentences and an evergreen explainer.
- Treat every other property that mentions the estate as a customer of that URL. When the canonical moves or the company shape changes, every property gets the same hour of rewiring; doing it on the next cron tick breaks the contract.
- Make the home and About pages do the linking work. If the home page explains the canonical, it competes with it. One sentence for the journal, one sentence for the canonical.

## Related Posts

- [Team-page ordering is a release decision]({{< ref "team-page-ordering-is-a-release-decision.md" >}}) (Tier 2, 2026-09-28): estate-anchor discipline with a CI gate, the same shape as today's rewiring.
- [Use the primitive, not the patch]({{< ref "use-the-primitive-not-the-patch-codeql.md" >}}) (Tier 1, 2026-09-27): the discipline of replacing a patch with the underlying primitive, applied to a security surface.
