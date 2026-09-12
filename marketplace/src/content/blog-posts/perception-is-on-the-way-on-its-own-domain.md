---
title: "Perception Is On the Way, on Its Own Domain"
description: "A customer preview page at perception.intentsolutions.io went live on 2026-09-11 because the full paid-product release surfaced four infrastructure gaps the smaller deployment could close."
date: "2026-09-11"
tags: ["omarchy", "release-engineering", "deployment", "beads", "vite", "fastify", "lets-encrypt", "caddy"]
featured: false
canonical: "https://startaitools.com/posts/perception-is-on-the-way-on-its-own-domain/"
---
The day's pattern is the redirection. One Omarchy entry repo launched Perception's
web/API surface and shipped a customer preview page to `perception.intentsolutions.io`,
but the live deployment was a coming-soon page rather than the full paid product.
The smaller deployment was what the day's infrastructure could close. The same
shift showed up on a second repo, where a 1,262-line master blueprint commit and
17 documents filed into a flat chronological index paired with a 15-child Beads
decomposition that waits on itself by design. Two products, two repos, one shared
shape: ship the version the constraints can actually carry, and name the gap that
forced the smaller scope.

## omarchy-listening-post-entry: Perception's web and API surface, then the customer preview

The repo shipped Perception in two commits on 2026-09-11. The first commit
(`12ba7df feat: establish Perception web and API product`, 00:17 -0600) was
46 files, 5,894 insertions: a new `web/` Vite + React app, a new `api/` Fastify
service with Dockerfile, and a `packages/perception-contract/` shared schema
package that the web app and the API both depend on. The contract carries the
Perception v1 snapshot schema, with `snapshot.id`, `snapshot.staleAfter`,
`snapshot.account`, `snapshot.topics`, and a `snapshot.signals` array typed
to `lane` ∈ `incident | release | pricing | engineering`. The web app imports
the types directly from `@listening-post/perception-contract`; the API and the
contract tests share the same module.

The second commit (`d992ce5 feat: prepare Perception customer preview`,
17:15 -0600) was 102 files, 5,077 insertions and added the rest of the
customer-facing surface: a `PublicExperience.tsx` that owns the public marketing
site, four policy pages (privacy, terms, acceptable-use, support), a passwordless
auth flow with magic links via `consumeMagicLink` and `requestMagicLink`,
account views, customer-journey tests, and a `mailer.ts` plus `customer-messages.ts`
plus `entitlements.ts` plus `billing-webhook.test.ts` that gate access on Lemon
Squeezy subscription state. The schema gained a stricter signals shape (the
array now requires `id, title, url, source, lane, relevance, resolved, quiet,
matchedTopicIds, publishedAt, read` per item with `additionalProperties: false`).
The manifest was updated to point `perceptionEndpoint` at
`https://api.perception.intentsolutions.io` and the web `public/CNAME` file
was written with `perception.intentsolutions.io`. PRODUCT.md, DESIGN.md,
VERIFICATION.md, SECURITY.md, and CHANGELOG.md were authored together.

That is the day's product surface. The live deploy is where the day's
reversal starts.

## Why the live deploy is a coming-soon page

The original direction arrived as a single line near the end of the day's
session: "merge the prs commit push etc deploy the website i meed it online
i meed it online i give u commercial and legal approval." That authorization
covered the full paid-product release: the API at `api.perception.intentsolutions.io`,
the web app, the Lemon Squeezy checkout flow, and the policy pages as binding
production terms.

The agent surfaced four gaps before changing live traffic. GitHub Pages was
not enabled on the repo. The three `PERCEPTION_*` repository variables were
absent. The VPS deploy secrets were absent. The custom domains for both
`perception.intentsolutions.io` and `api.perception.intentsolutions.io` were
failing DNS resolution. PRODUCT.md was explicit that price, billing interval,
refund window, legal operator, governing law, and final checkout URL were
deployment-owned open decisions. The customer copy labelled itself "not yet
production terms."

The redirect that followed read, verbatim: "dude i just want perception.intentsolutions.io
to work as a site people click to know its on the way i posted it in discord."
That is the day's reversal. The full release was deferred, not failed: the
agent was told the goal had shrunk to a single page that says the product is
on its way and links to the GitHub repo.

## GitHub Pages → VPS at intent-solutions

The smaller deployment still needed a live URL. The agent's first attempt was
GitHub Pages: a `gh-pages` branch with the standalone coming-soon HTML and a
Porkbun CNAME at 300s TTL. Pages was configured with Actions as its source,
`PERCEPTION_DEMO_MODE=true` was the only repo variable set, and the
checkout/API variables were deliberately left unset so the preview could not
masquerade as a paid production launch. DNS propagated. Pages started serving
the page over HTTP. The certificate did not arrive.

After the certificate stall, the agent switched to the VPS path that was
already under control. Caddy was healthy on the VPS, passwordless sudo was
available, and the same static page was served from there. The first Caddy
reload failed closed because the new access-log file did not yet exist with
Caddy ownership. The reload was isolated and retried after creating only
that log file with the service's established permissions. The second reload
succeeded. Porkbun was then asked to move the `perception` CNAME from GitHub
Pages to the VPS A record, with an automatic rollback path armed during the
cutover. Caddy issued the Let's Encrypt certificate on retry. The local DNS
resolver on the workstation had a stale negative cache for the new A record,
which the agent bypassed to confirm the public origin.

`perception.intentsolutions.io` now serves the coming-soon page over HTTPS
from the VPS. The full paid product remains local and un-pushed; the open
beads for price, billing interval, refund window, legal operator, governing
law, and final checkout URL still own those decisions.

## intent-blue-gold: 17 Stage 0 documents plus an Epic 0 Beads decomposition

The second repo's day was a documentation discipline pass plus a Beads
decomposition. The first commit (`d9cd691 docs: replace product summary with
canonical MVP execution blueprint`) added 1,262 insertions across a single
file, the master blueprint that owns the BLUE → GOLD → BLUE → WELCOME
sequence. The second commit (`a23517b docs: file Stage 0 repository records`)
filed 17 source documents (`PRODUCT.md`, `V1-SCOPE.md`, `RISK-REGISTER.md`,
`THREAT-MODEL.md`, `MIGRATION-CONTRACT.md`, `COMPATIBILITY.md`, `RESEARCH.md`,
`AI-STRATEGY.md`, `DECISIONS.md`, `MASTER-BLUEPRINT.md`, the `docs/` subfolder
documents) into a flat chronological `000-docs/` tree using a global sequence
plus an `AGENTS.md` at root, a `CODEX-HANDOFF.md` update, and a
`000-docs/000-INDEX.md` that names the order.

The Beads side was harder. The first Beads init auto-adopted the unrelated
Intent Eval Dolt database (1,499 imported issues inherited from a remote the
agent had not selected). The first reset attempt succeeded technically but the
inherited graph was still present in the local Dolt history. The second reset
moved the `.beads/` directory to `/tmp/intent-blue-gold-beads-XQ7n2p/imported-beads`
and `/tmp/intent-blue-gold-beads-reset-xXV59D/imported-beads` and started
with `dolt.local-only: true` and `backup.enabled: false` so no remote could be
adopted. The third init came up clean (zero issues, no Dolt remote, no
Intent Eval reference).

On the clean workspace the master blueprint was decomposed into five epics,
and Epic 0 (engineering foundation, CI/CD, repository quality gates) was
decomposed into 15 bounded Beads children using three Luna-high subagents.
The decomposition surfaced a cross-slice overlap (the CI orchestration bead
and the bootstrap bead both claimed the local command), which was narrowed so
CI consumes the bootstrap-owned gate rather than reimplementing it. The
final DAG has nine dependency waves with maximum parallelism of three, a
single onboarding/exit gate at the apex, and selective Epic 1 integration:
research and safety-analysis work remains runnable, schema/fixture hardening
waits for Epic 0 validators, experiment operationalization waits for workflow
+ destructive-test-isolation controls, and the controlled BLUE → GOLD → BLUE
proof waits for the final Epic 0 exit gate.

The Beads config (`dolt.local-only: true`, `backup.enabled: false`, no remote)
was committed, the issue graph was validated with `bd lint` and `bd dep cycles`
(zero cycles, zero lint warnings), and the worktree was committed, pushed,
and merged to `main` as PR #1 with `delete_branch_on_merge` flipped from
`false` to `true` first via the GitHub repository API.

## Also shipped

The comehomealabama journal (a separate Astro surface, not startaitools)
published `ac9b179 post(journal): Orange Beach is three different decisions.
Know which one you're making.`, automated by `scripts/journal/mandy-land.sh`
after the voice and fair-housing lints both passed. That post lives on the
Mandy machine and does not enter the startaitools archive.

## What it cost

Two redirects, one certificate stall, one Caddy fail-closed reload, two
failed Beads resets, and a 1,262-insertion master blueprint rewrite that
became the canonical reference. The Perception web/API surface and the
Beads Epic 0 graph both landed in their final form on the first attempt
inside their own repositories. The deploy paths and the Beads remote selection
each needed a second try. The customer-facing launch is now bounded by what
HTTPS, Porkbun, and a Caddy file permission can carry, not by what the
product itself can carry.

## Related Posts

- [The Same Mission on Two Surfaces in One Day](https://startaitools.com/posts/the-same-mission-on-two-surfaces-in-one-day/), 2026-09-10's pair of initial scaffolds and the marketplace claim ledger pattern that precedes the Perception customer preview
- [A 953-Line Skill Entry Fits the Budget Again](https://startaitools.com/posts/a-953-line-skill-entry-fits-the-budget-again/), 2026-09-09's split-and-pull-only refactor and the same-day 17-repo audit-harness refresh
- [Hardening a Marketplace in One Day](https://startaitools.com/posts/hardening-a-marketplace-in-one-day/), 2026-09-08's C44 installable-tree gate and the portable install integrity contract that ship next to the contributor workflow
