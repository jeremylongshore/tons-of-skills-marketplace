---
title: "Rank Current Truth with the Rerank, Not the Clock"
description: "Reindexing by updatedAt alone can let a chronological hit beat a current decision. The fix: lifecycle and history demotion in finalScore, with a paired test."
date: "2026-10-04"
tags: ["ai-agents", "search", "architecture", "debugging"]
featured: false
canonical: "https://startaitools.com/posts/rank-current-truth-with-the-rerank-not-the-clock/"
---
A search for "GCP exodus" in the team brain (the indexed knowledge base we search every day) kept returning a how-to from March instead of the AAR (after-action report) from July. The how-to was well cited (it had many other places linking to it). The AAR was correct. The how-to won.

The brain reindexes on `updatedAt` (the timestamp each record was last edited). The AAR was newer than the how-to, so on a raw search the AAR should have ranked first. It did not, because the AAR is a decision record and the lifecycle step (the part of the system that marks each record as active, superseded, or deprecated) had marked it as `superseded` to a follow-on entry in the same topic. That lifecycle downgrade did not get re-evaluated during ranking. The older how-to, untouched and uncorrected, kept the top slot.

This is the kind of bug a search system can hide for months if the corpus is small enough that "the top hit usually points near the truth."

## Where the score came from

The registrar's rerank (the second-pass scoring function that re-orders hits after a first-pass search) took a `query` and the hit list, and that was it. `rerankCitedHits(query, hits)` produced a score, the score sorted the list, the top hit got displayed. Lifecycle and history were real attributes on the record, but they only entered the score as the raw index itself, not as a ranker input. So once the indexer (the first-pass search that builds the initial hit list) demoted a record on lifecycle, the demotion was permanent in the score layer.

The new signature is four args:

```ts
export declare function rerankCitedHits(
  query: string,
  title: string,
  lifecycle: LifecycleState,
  history: HistoryMarker
): finalScore
```

`finalScore` is now the only number that orders the list. Search rank, lifecycle, and history demotion all fold into the same number. Ties at the sort layer break on recency so the more recent of two equally-demoted records still surfaces first.

The demotion lives in one place:

```ts
const demotion = lifecyclePenalty(lifecycle) + historyPenalty(history);
return searchScore(query, title) - demotion;
```

`lifecyclePenalty` returns 0 for `active`, a positive weight for `superseded`, a higher one for `deprecated`. `historyPenalty` reads the marker, returns 0 for a first-class record, a small weight for an amendment, and a larger one for an editorial-only pass-through. The exact weights live in the search practice doc and get re-tuned against the last 90 days of merges.

## Proof that the fix was the fix

The plugin wires the same change into the local MCP server, so the local `brain_search` path picks it up. The paired test in `test/rerank-wiring.test.ts` is what made the merge possible. The test runs the same query against both the old and new rerank on the same fixture, and asserts the old wiring placed the AAR below the how-to, and the new wiring flips it.

That is the load-bearing assertion: the test fails on the old code and passes on the new code. Without it, the change was untested and the day looked like routine cleanup.

## Also shipped

The umbrella session dispatched 206 tool calls across models Claude Sonnet 5.5 and Claude Fable 5.1, with most of the day spent on the ranker fix and the plugin wiring. Two related PRs landed the same day:

- `bobs-big-brain-registrar` PR #359: the rerank change itself.
- `bobs-big-brain-plugin` PR #72: the local MCP server wiring, on branch `fix/local-search-rerank-policy`.

A separate PR in the curator/policy-engine/api path added a bounded human-escalation hold for ambiguous audience and secret decisions, and the plugin picked up a surface for that hold in the same window. Those are not the focus of this post.

## Use this

- If your ranker takes only the query and the hits, lifecycle and history are not in the score. Move them into the same `finalScore` so a demotion at the index layer also demotes at the ranker layer.
- Write a test that runs the same query against the old and new rerank on a fixture where the wrong answer is known. A green build that only exercises the new path proves the new code works. A paired assertion proves the old code was wrong.
- The fix lives in `bobs-big-brain-registrar` PR #359. The pattern moves to any reranker over a structured corpus where newer authoritative content can be demoted on its own.

## Related Posts

- [Reachability Is Not Freshness](/reachability-is-not-freshness/): a 200 status code is not a proof of currency, same as a 200 hit on a search is not a proof of current truth.
- [The Primary Record Settles What a Derived One Assumed](/the-primary-record-settles-what-a-derived-one-assumed/): derived signals vs primary records; the rerank is a derived signal that should not silently override a primary lifecycle fact.
