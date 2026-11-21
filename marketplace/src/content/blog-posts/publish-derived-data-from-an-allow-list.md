---
title: "Allow-List JSON Publishing in Python: Stop Field Leaks"
description: "Rebuild each published JSON object that carries feed data from an allow-list of keys, then plant raw fields in a Python fixture test to check none leak."
date: "2026-11-18"
tags: ["python", "testing", "architecture", "ci-cd", "devops"]
featured: false
canonical: "https://startaitools.com/posts/publish-derived-data-from-an-allow-list/"
---
If you publish numbers computed from a feed you are not cleared to redistribute, the public output can leak the feed without anyone deciding it should. The usual cause is a publisher that copies each record and deletes the fields you already know are bad. A field the upstream adds next month is not on that delete list, so it ships.

This post walks through a publisher that builds its feed-derived objects from named key lists, and a fixture test that plants raw fields so a leak fails the test. At the end you will know how to write both, and where the test stops.

## What broke

The site in question publishes a daily price index for AI model tokens. It is computed from a third-party pricing feed, and the records collected from that feed (raw API responses and the observations normalized from them) are not cleared for redistribution.

A written licensing rule, covered below, says only the computed numbers go public. Three dashboard pages on the old site did not fit that rule: they read raw observations or wrote to a hosted database (Firestore).

The site also had to move. It ran on Firebase hosting, and that hosting went away when the Google Cloud (GCP) account was torn down on 2026-07-09. From then on the deploy jobs could only fail. Moving to a plain static build meant rewriting the publish step anyway, so the publish step got the allow-list.

The three dashboard pages were removed, not ported. The whole change deleted about 11,000 lines, mostly Firebase config, Firestore rules, a functions folder and old JavaScript pages. That is the cost, and the rewrite did not bring those pages back.

## The rule and the risky default

The licensing rule is a written architecture decision record (ADR). It says to keep collected data private and publish only computed indices. Raw API responses and normalized observations stay in folders the publisher never reads.

Its rationale is that the upstream provider's terms of service have not been formally reviewed. The record notes that opening the data later is easy, and un-publishing it is hard.

Picture a hypothetical copy-then-delete publisher, with a made-up field name. It loads a record, removes the keys the author knows are sensitive, and writes what is left. Upstream adds billing_tier to each record. Nobody put it on the delete list, so it goes out with every object. The test checks the keys the author already named, so it stays green.

## The allow-list

The fix inverts the default. Nothing is published unless a list names it. The core is one helper:

```python
def pick(src: dict, keys: list[str]) -> dict:
    return {k: src[k] for k in keys if k in src}
```

Unknown keys are dropped without an error. A new upstream field stays private until someone adds it to a list, which is a code change and a review.

Flat filtering is not enough. The spread summary holds two reference objects, widest and most_endpoints, and each model holds a cheapest object. A raw object nested inside one of those passes through a top-level filter intact. The publisher picks the nested objects too:

```python
for k in ("widest", "most_endpoints"):
    if isinstance(summary.get(k), dict):
        summary[k] = pick(summary[k], REF_KEYS)
```

Each model's cheapest object goes through its own list, CHEAPEST_KEYS. Those three are the only nested picks: widest, most_endpoints and each model's cheapest. The index bodies get one flat pick each.

The coverage has gaps, and the code shows them. The spread's blend object is named in the top-level list but copied whole, with no inner pick. The quantization_mix counts are coerced to integers rather than filtered. The methodology file is written to v1/methodology.json straight from a hand-written YAML rulebook, with no allow-list at all. Some values also pass through whole: the spread's source string, and each index's models_included list of model IDs. None of those carry raw feed fields today, so the licensing rule holds. A future field nested under blend would ship.

## The fixture

A fixture is a small hand-written input file that a test loads. The spread fixture is dated 2026-11-19. It plants two raw fields on purpose:

- The first model carries an endpoints_raw list, which holds per-provider raw prompt prices.
- The second model's cheapest object carries a nested raw_response with the value {"x": 1}.

The test runs the full build against that fixture and asserts three things:

- endpoints_raw and raw_response appear nowhere in dist/v1/spread/latest.json.
- No v1/observations directory exists.
- observation_id and source_url appear in no JSON file under v1.

If someone replaces pick with copy-then-delete, the planted fields leak and the test fails. That is the regression it guards.

It has a limit. The test only finds fields somebody planted. The allow-list handles the fields nobody thought of, and the test exists to keep that allow-list from being quietly removed.

The commit reports 72 pytest tests passing, 7 of them new for the publisher. A build against the 2026-11-19 data renders every page. Playwright screenshots at 1440 and 390 pixels wide found no horizontal scroll, and the browser console logged zero errors. Those checks cover rendering and the planted cases. They do not audit the upstream feed.

## Also shipped

- Listing eligibility is now a rule: aliases, :free, :batch, router and unpriced listings are excluded with a recorded reason. The 2026-11-19 live run kept 344 of 480 listings.
- The new spread collector shows that the same open-weight token sells at a 16x range across 41 providers, and the cheapest one is a different grade (fp4). The same live run covered 57 models with 0 fetch errors.
- The browser CI jobs are pinned to ubuntu-24.04. GitHub's ubuntu-latest had moved to Ubuntu 26.04, where Playwright 1.57.0 refuses to install Chromium, so those jobs failed before any test ran.

## Use this

- Write each public object as pick(record, KEYS) with a named list, call pick again on every nested object you publish, and list the objects you publish unfiltered so the gaps are a decision.
- Plant a raw field at the top level and another inside a nested object in a fixture, then assert both are absent from the published output.
- Read the working publisher at https://github.com/jeremylongshore/stci-standard-inference-token-cost-index/blob/main/scripts/publish_static.py, then copy its structure rather than its key names.

## Related Posts

- [How the token cost index was first built, from collector to daily cron](https://startaitools.com/posts/stci-zero-to-v010-token-cost-index/)
- [Dropping a personal field from telemetry before it leaves the box](https://startaitools.com/posts/claude-code-opentelemetry-drop-user-email-sum-deltas/)
