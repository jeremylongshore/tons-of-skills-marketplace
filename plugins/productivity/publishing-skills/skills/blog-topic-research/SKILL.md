---
name: blog-topic-research
description: 'Build a deduplicated editorial backlog from current, traceable demand and authoritative product evidence. Use when deciding which long-tail topics are worth writing before drafting begins. Trigger with "research blog topics" or "find evidence-backed content ideas".'
argument-hint: "[count] [cluster-or-product] [--append-to path]"
allowed-tools: Read, WebSearch, WebFetch, Write, Edit
version: 1.2.0
author: AutomateLab <hello@automatelab.tech>
license: MIT-0
tags: [seo, topic-research, search-intent, content-strategy, evidence]
model: inherit
effort: high
compatibility: Designed for Claude Code; search evidence changes over time, and backlog writes require editorial approval plus revalidation of source currency
---
# Evidence-Backed Blog Topic Research

## Overview

Find specific editorial opportunities supported by real user questions and current primary sources. Each accepted topic includes an evidence trail, search intent, version context, known-answer status, and duplicate-risk decision.

This workflow does not invent search volume or treat autocomplete as proof of commercial value. It separates observed demand from editorial judgment.

## Prerequisites

- Target audience, product or subject boundary, business goal, locale, and preferred language
- Existing titles, canonical URLs, slugs, and planned backlog for cannibalization checks
- Approved topic clusters and formats, if the publication uses a taxonomy
- Current access to public search results, official documentation, changelogs, issue trackers, and relevant community sources
- A requested count between 1 and 100; default to 25 when omitted

## Tool Discipline

Use `Read` for the supplied inventory and taxonomy. Use `WebSearch` to discover candidate questions and `WebFetch` to verify the actual source page, date, title, and context. Use `Write` or `Edit` only after the user approves backlog changes; do not store private community data, credentials, or unnecessary personal information.

## Instructions

1. Confirm scope, audience, locale, time horizon, count, excluded subjects, and the publication's definition of a useful conversion or reader outcome.
2. Read the existing coverage inventory. Normalize case, punctuation, product names, versions, error codes, and canonical URLs while preserving the original titles.
3. Search across at least three suitable signal classes: official docs or changelogs, public issue trackers, vendor forums, Stack Overflow, Reddit, or visible search suggestions. Respect access controls and site terms.
4. Fetch each candidate source. Capture its title, URL, publication or update date when available, exact short evidence excerpt, source type, and whether it is primary or community evidence.
5. Pair demand evidence with at least one current authoritative source whenever the topic makes product, API, version, legal, medical, financial, performance, or pricing claims.
6. Classify search intent and format: `how-to-fix`, `how-to-connect`, `how-to-automate`, `x-vs-y`, `what-is`, `use-case`, `listicle`, `migration`, or `release-recap`.
7. Score evidence explicitly. Use `1` for a single relevant public mention, `2` for repeated or engaged discussion, and `3` for strong repeated demand across independent sources. Label this an editorial signal score, never search volume.
8. Run duplicate checks against published and planned coverage. Reject a matching canonical intent; flag near matches that differ only by phrasing; preserve distinct version, error, integration-pair, or audience qualifiers when justified.
9. Extract only supported problem summaries, fix kernels, version constraints, and question variants. Mark unresolved or conflicting answers instead of resolving them from model memory.
10. Rank accepted topics by evidence, business relevance, authority availability, coverage gap, and freshness. Explain the factors and report any shortfall rather than padding the list.
11. Present the candidate set for approval. Append only accepted records to the requested path, preserving stable IDs and source timestamps.

## Evidence Contract

Each accepted record should contain:

```json
{
  "topic": "How to diagnose webhook signature failures after key rotation",
  "cluster": "integrations",
  "format": "how-to-fix",
  "intent": "troubleshooting",
  "signal_score": 3,
  "demand_signals": [
    {
      "type": "github_issue",
      "url": "https://example.com/public-issue",
      "evidence": "Short exact title or question",
      "observed_at": "2026-09-11"
    }
  ],
  "primary_sources": ["https://example.com/current-official-doc"],
  "version_context": "verify at drafting time",
  "duplicate_decision": "accept",
  "duplicate_matches": []
}
```

Keep excerpts short and attributable. A URL that no longer contains the claimed evidence does not satisfy the contract.

## Approval Boundaries

Do not bypass robots controls, authentication, rate limits, paywalls, or community privacy expectations. Do not write to the editorial backlog, contact source authors, or turn sensitive anecdotes into content without explicit approval. Treat health, legal, financial, and security topics as requiring qualified review.

## Output

Return:

- scope and research timestamp
- ranked accepted candidates with factor-level rationale
- evidence and primary-source URLs per topic
- rejected candidates with duplicate, weak-evidence, stale-source, or out-of-scope reasons
- coverage gaps, conflicts, and the number of requested topics not found
- append preview and final write receipt when approved

## Error Handling

| Condition | Response |
|---|---|
| Search result cannot be fetched | Do not use its snippet as verified evidence; find an accessible primary page or reject it. |
| Source dates or versions conflict | Preserve both, lower confidence, and require revalidation during drafting. |
| Existing coverage inventory is absent | Run title-level checks on supplied context, mark cannibalization incomplete, and do not claim uniqueness. |
| Evidence contains personal or sensitive data | Minimize or omit it and retain only the public question needed for editorial evaluation. |
| Fewer qualified topics than requested | Return the valid subset and a source-by-source shortfall report. |
| Append target changed during review | Re-read, rerun duplicate checks, and preview the merged result before writing. |

## Examples

Research a focused backlog:

```text
request: 10 topics for the integrations cluster
accepted: 7
rejected: 2 duplicate intents, 1 stale unsupported version claim
top candidate: webhook signature failures after key rotation
evidence: public issue + current vendor verification guide
append: awaiting approval
```

Reject a plausible but unsupported idea:

```text
candidate: "Best automation platform for every startup"
result: reject
reason: vague intent, no measurable comparison contract, and no qualifying demand evidence
```

## Verification

- Re-fetch every selected URL and confirm it supports the stored title or excerpt.
- Confirm every factual or version-sensitive topic has a primary source.
- Confirm accepted titles pass the same duplicate checks against published and planned coverage.
- Confirm no score is described as monthly search volume unless it comes from a named, current data provider.
- Confirm appended record count and IDs match the approved preview.

## Resources

- [Google Search Central: Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)
- [Google Trends help](https://support.google.com/trends/)
- [GitHub documentation for searching issues and pull requests](https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests)
- [Stack Exchange API documentation](https://api.stackexchange.com/docs)

## Next Steps

Pass approved records to `blog-editorial-calendar`. Re-fetch the decisive sources when drafting because questions, documentation, and product behavior can change.
