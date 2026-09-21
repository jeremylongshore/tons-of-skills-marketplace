---
title: "The Pipeline Landed Its Own Output Today"
description: "Four commits at 04:19 -0600: the BitLocker post, its social card, the tonsofskills dual-publish, and the v1.17.35 tag. No new code; the 4-gate loop ran clean."
date: "2026-09-14"
tags: ["release-engineering", "automation", "blog-pipeline"]
featured: false
canonical: "https://startaitools.com/posts/the-pipeline-landed-its-own-output-today/"
---
Today's engineering was zero. Today's bookkeeping was one minute.

The 04:19 -0600 window on startaitools master holds four commits:

```
6a904081 post(2026-09-13): Three Gates on Standard-User BitLocker State Observation (Tier 2)
98b766db assets(2026-09-13): social image and cards for three-gates-on-standard-user-bitlocker-state-observation
dd6fd923 chore: release v1.17.35 [skip ci]
68d74f6a docs: update changelog for v1.17.35 [skip ci]
```

Each one is a gate, and each gate is a separate commit by design.

## The post commit (6a904081)

This is `blog-land.sh`. Yesterday's `/blog-backfill` run wrote the post body and a `.blog-staging/DATE.intent.json` sentinel. Today's job was the deterministic lander: verify the sentinel says `ready:true`, confirm a classifier record exists in `decisions.jsonl`, confirm the step-8 audit addendum landed, then `hugo --buildFuture --gc --minify --cleanDestinationDir` to confirm 2199 pages still render, then `git add` the post file and push to master.

No LLM is in this path. The producer wrote yesterday, the lander commits today. The reason for that split is exactly what it looks like: a blocked gate cannot brick the next morning's run because it is quarantined, not published.

## The assets commit (98b766db)

Still inside `blog-land.sh`, still after publish, the post-image generator runs. `make-post-image.py` derives a prompt from the landed post's title, slug-seeds a vendor model pick from `MiniMaxProvider.models` (deliberately a vetted subset, not the full vendor catalogue), and either gets a 1200x630 social card plus a 1080x1080 square back or falls through to the deterministic `make-social-card.py` PIL baseline.

The fallback is recorded rather than hidden. The brand frame and the no-lettering rule still apply either way. A bad minute at the image vendor cannot turn a good publish into a quarantine, because image generation is deliberately outside the publish path.

## The tonsofskills dual-publish (1965ee289 on claude-code-plugins)

Same minute, same markdown file, copy across to `intent-solutions-io/claude-code-plugins` (the tonsofskills repo) on `main`. This is `publish_file_to_repo` from `scripts/blog/lib-cron-common.sh`: git plumbing only, working tree untouched, retry-on-race. The publishing path stays out of the working tree entirely, so nothing later has to clean up a merge state.

The dual-publish exists so a draft on one surface is never a draft on the other. tonsofskills reads the same markdown verbatim, no rewrite layer between them.

## The release pair (dd6fd923, 68d74f6a)

`release.yml` runs on push to master and inspects the front matter for semver signals. The post commit bumped `version.txt` to 1.17.35 (from 1.17.34, which carried the previous post), so the workflow emitted two commits:

- `chore: release v1.17.35 [skip ci]`: the version bump plus the git tag
- `docs: update changelog for v1.17.35 [skip ci]`: the CHANGELOG.md entry

The `[skip ci]` on both keeps a second workflow run from re-firing the bump-and-release loop recursively. Without it, the bump would commit, push, trigger the workflow again, bump again, and so on. That mistake gets made once per project.

## What was not today's work

A few things in the working tree are real but are not today's substance. The `layouts/partials/schema.html` edit (changing the JSON-LD standdown check from `application/ld+json` to `"BlogPosting"`) is load-bearing: smarter check, no more false positives on FAQPage schema. It is sitting uncommitted because the test I want to write alongside it is not done.

The orphan post `content/posts/the-day-the-green-checks-were-lying.md` is a 46-day backlog item with a `ready:true` sentinel, not today's problem. The five `drafts/` directories and `investigations/` are WIP, none of them landed today.

## The day in one sentence

The pipeline is supposed to run like this: the producer decides, the lander commits, the publisher pushes, the releaser tags. Today it did. Tomorrow's run starts fresh because nothing today left state behind.

**Related posts:**

- [Three Gates on Standard-User BitLocker State Observation](https://startaitools.com/posts/three-gates-on-standard-user-bitlocker-state-observation/) (the Tier 2 case study this morning's run landed)
- [Sealing a 168-Bead Planning Graph Took Three Reviews and a Seven-Seat Council](https://startaitools.com/posts/sealing-a-168-bead-planning-graph-took-three-reviews-and-a-seven-seat-council/) (the prior Tier 2 in the same window)
