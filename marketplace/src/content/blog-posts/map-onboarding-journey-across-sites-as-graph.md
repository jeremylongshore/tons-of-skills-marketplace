---
title: "Onboarding Flow Audit: Crawl Multi-Site Steps as One Graph"
description: "Crawl a multi-site onboarding flow and its email steps as one graph to compare it with the path a newcomer expects. Missing links become the fix list."
date: "2026-11-07"
tags: ["ux", "onboarding", "ai-agents", "claude-code", "web-development"]
featured: false
canonical: "https://startaitools.com/posts/map-onboarding-journey-across-sites-as-graph/"
---
Each page in this flow reads fine on its own, and the flow still breaks between them. You can find those breaks by crawling the whole flow read-only (visiting and logging every step without changing anything) as one graph, then listing the links a newcomer expects and cannot find.

A newcomer can start on the main site, land on a separate learning site, hit a page that asks for something the marketing page never mentioned, and hear nothing at all if the answer is no.

The person who runs these sites called the experience "very discombobulated" and wanted a page they could point people to for understanding. Reading the pages one at a time would not show where the path contradicts itself. This post covers the method that did show it, what broke along the way, and what got fixed.

## Crawl the flow as a graph

The flow touched three surfaces: the main marketing site, the learning site with its sign-in and start page, and the offline steps. Offline steps are automated emails and e-signature requests, meaning documents sent for electronic signing. They never appear as a web page.

I had AI coding agents do the crawling (Claude Opus 5.5 and Claude Fable 5.1, in Claude Code), but any crawler that logs links would work. They ran three read-only crawls in parallel, one per surface. On a website a crawl follows links and logs each page; for the offline steps it read the email templates and the process log instead. Each crawl wrote a summary plus one node-and-edge file. A node is a page, email or signature step. An edge is a link or handoff between two nodes.

The website crawls read raw HTML and probed likely URLs. They did not open the token routes, meaning the email confirmation link and the setup link. No crawl changed or submitted anything. The offline crawl masked invite codes, because they work as access tokens.

The counts, by surface:

- Learning site: 36 nodes and 69 edges.
- Main site: 66 nodes and 558 edges, including 14 external stubs and 3 shared header and footer elements counted as nodes.
- Offline steps: 62 nodes and 75 edges.

The agent session then merged the three files into one private HTML map of the flow as it stands. Solid arrows mark links and automated steps. Red dashed arrows mark links a reader would expect that do not exist, and red boxes mark dead ends.

Those expected-but-absent edges are the useful part. A missing edge is easier to argue about than a vague sentence.

## What was out of date first

Two of the three crawls found their local checkouts out of date. A checkout is the local copy of a repository. The main-site checkout was behind origin/main, the shared main branch on the remote server, so that crawl read live behavior wherever the two disagreed. The offline crawl's checkout was 68 commits behind origin/main, so it read the newer templates straight from the remote branch.

The main-site crawl's instructions also assumed 36 pages, a separate figure from the learning site's 36 nodes. The live sitemap, the public list of a site's pages, had 38 URLs. The crawl followed the live list.

## What the map found

These are the top findings, in ranked order. The full list had 14.

- The only path from the main site toward joining was one quiet home-page link. It landed on the learning site's root, not on the request form.
- No page explained the process before the form. The home page said "selective" and "invitation-only," while the form said "free to join."
- Three dead ends. The start page asked for a company email and had no way back to the request form. The signing return page said "Back to Learn" without naming what was signed or what came next. The firm chapter of the atlas, the public overview pages, had no call to action. Separately, a declined or held applicant received nothing at all.
- Firms had no path at all.
- Public copy stated who holds the customer contract three different ways.

Further down the list, routes left over from the learning site's retired course software still answered for anyone who typed them in. That covered the login page, the member area, a privacy page, an empty blog, and a duplicate home page. The terms page showed placeholder tokens where the liability cap and governing law belonged. A next-steps email still sent members to the old sign-in.

The waits are written into the templates. A confirmation email arrives within minutes. A clarification reminder fires after 5 business days, a closing note 10 business days later, and a signing reminder after 5 business days. The NDA (nondisclosure agreement) and User Agreement carry no deadline. Before the fix, no page a newcomer saw before applying described the process at all.

The map also listed 12 missing cross-links to add, and three sentences to settle once and reuse everywhere.

## What got fixed

Fourteen findings became 28 tracked items: 6 epics (parent items that group related tasks), 20 tasks and 2 owner decisions. Every task has a parent. Four agents worked the streams in parallel.

Three fixes merged the same day. The main-site change is at https://github.com/jeremylongshore/intent-solutions-landing/pull/102. It adds two entry links on the home page, one for engineers and one for firms, a how-it-works page with the five joining steps and their timing, and an alliance page. The alliance page opens with "Proposed: the Alliance Agreement is in legal review," so its draft status is stated rather than implied. It also replaces three conflicting customer-contract statements with one. Every page now renders that statement from a single source, because the old copy drifted each time a page stated it separately.

On the learning site, the start page now links to the request form and to the how-it-works page. It also says the member pays the exam fee at registration, through the official exam pages, and that the company does not sell exam access.

Caddy, the web server that routes traffic for these sites, sent the retired privacy page and the password-reset route to 410, a status code meaning gone for good. The duplicate home page and the empty blog got 302, a temporary redirect to the root. The login and member-area routes got a noindex header (X-Robots-Tag, asking search engines not to list them) instead of 410. That keeps the owner's admin access while the decision to decommission stays open.

The config validated, the server reloaded, and the route checks came back as expected: the privacy page and password reset returned 410, the duplicate home page and blog returned 302, the login page returned 200 with the noindex header, and the start, request-access and root pages returned 200.

The rest are still open.

## Use this

- Crawl each surface read-only into a node-and-edge file, including email and signature steps, before you edit any copy.
- For every node, ask what a newcomer expects next, then check whether that edge exists. Each missing edge goes on the fix list.
- Check the crawl's page count against the live sitemap, and confirm each checkout matches origin before you trust its output.

## Related Posts

- [Coordinating a product launch across multiple repos](https://startaitools.com/posts/coordinating-a-product-launch-across-multiple-repos/)
- [Database restore does not undo outward effects](https://startaitools.com/posts/database-restore-does-not-undo-outward-effects/)
- [SMTP 250 is not delivery: three receipts](https://startaitools.com/posts/smtp-250-not-delivery-three-receipts/)
