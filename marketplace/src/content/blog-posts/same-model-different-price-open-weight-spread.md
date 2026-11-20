---
title: "OpenRouter Price Spread: One Open-Weight Model Spans 16.08x"
description: "Pricing for one open-weight model spans 16.08x across OpenRouter providers. The cheapest endpoint serves fp4. How to measure the provider price spread."
date: "2026-11-19"
tags: ["llm-pricing", "open-weight-models", "openrouter", "quantization", "stci"]
featured: false
canonical: "https://startaitools.com/posts/same-model-different-price-open-weight-spread/"
---
If you quote, benchmark or budget an open-weight model by one price per model, one number is standing in for a spread of sellers and serving precisions. This post shows how wide that hidden spread was on one day, how to measure it with an open daily price index, and what to print beside any price so a reader can judge it.

A model name is not a price. OpenRouter, a marketplace that resells many providers' model APIs, lists the same open weights from many providers. Each provider runs one or more endpoints (a separately priced deployment of the model) and sets its own rate. A per-model price, whether an average or a pick, collapses those rates into one number.

The measurement comes from the Standardized Token Cost Index (STCI), an open daily price index for model tokens. Its first run under STCI methodology 2.0.0 (the methodology, from here on), on 2026-11-19, found the most-listed model to be `deepseek/deepseek-v4.1-flash-1017`: 50 endpoints from 41 providers. Its blended price (input and output rates combined into one per-token rate, weighting output 3:1) runs from $0.12 to $1.95 per 1M tokens. That is a 16.08x spread.

The cheapest of those endpoints, from a provider called Ambient, serves the model at fp4. fp4 is 4-bit floating-point weights, a more heavily quantized serving format than fp8 (8-bit). The JSON calls this field `quantization`; mxfp4 is another 4-bit variant. So the cheapest token may be a different grade of the same model than the median one.

The widest model in the run is a different one. `deepseek/deepseek-v4.1-flash` has 39 endpoints and a 34.82x max/min ratio. Both figures matter, because the widest spread and the most listings are different questions. The 16.08x case answers the second.

## Why do open-weight model prices differ between providers?

Each provider sets its own rate for the same model weights, and providers do not all serve those weights at the same precision. For the most-listed model, the cheapest of 50 endpoints served fp4 while most endpoints that reported a precision served fp8. For this model, the lowest price and a lower precision coincide. The data does not show that precision explains the whole spread.

## What the per-model spread record contains

The collector fetches each open-weight model's per-provider endpoint list. For every model with positive prices, it records the endpoint and provider counts, the min, p25, median, p75 and max blended prices, the max/min and p75/p25 ratios, the serving-precision mix, and the cheapest endpoint with its precision. Models with fewer than four priced endpoints are not reported.

The record for the most-listed model:

```json
{
  "model_id": "deepseek/deepseek-v4.1-flash-1017",
  "endpoints": 50,
  "providers": 41,
  "min_blended": 0.1212,
  "p25_blended": 0.3904,
  "median_blended": 0.55,
  "p75_blended": 0.8912,
  "max_blended": 1.95,
  "max_min_ratio": 16.08,
  "p75_p25_ratio": 2.28,
  "quantization_mix": {
    "fp4": 6,
    "fp8": 23,
    "mxfp4": 2,
    "unknown": 19
  },
  "cheapest": {
    "provider": "Ambient",
    "quantization": "fp4",
    "blended": 0.1212
  }
}
```

Three things in that record change how the price should be quoted.

First, 19 of 50 endpoints (38%) report no precision. The precision mix is incomplete before any analysis begins.

Second, 23 of the 31 endpoints that report a precision are fp8. For this model, fp8 is the most common known precision.

Third, the cheapest endpoint is one of six fp4 endpoints. Its blended price of 0.1212 is under a quarter of the 0.55 median. For this model, quoting the cheapest figure means quoting an fp4 price without saying so.

Hypothetical, not a record from the run: a team benchmarks against the cheapest endpoint, then budgets against the median. The benchmark and the budget may now describe different grades of the same token.

## Spread across 57 OpenRouter open-weight models

[STCI](https://startaitools.com/posts/stci-zero-to-v010-token-cost-index/) also publishes headline indexes from the same listings. In this run, 480 listings became 344 eligible ones. The other 136 were excluded by rule, not by a list of model IDs: 92 batch variants (their rates attach to the base model), 19 aliases, 17 free variants and 8 routers.

The spread covers 57 models (those with at least four priced endpoints), with zero fetch errors. The run summary:

```json
{
  "models_measured": 57,
  "fetch_errors": 0,
  "median_max_min_ratio": 2.53,
  "median_p75_p25_ratio": 1.31,
  "widest": {
    "model_id": "deepseek/deepseek-v4.1-flash",
    "max_min_ratio": 34.82,
    "endpoints": 39
  },
  "most_endpoints": {
    "model_id": "deepseek/deepseek-v4.1-flash-1017",
    "endpoints": 50,
    "providers": 41,
    "max_min_ratio": 16.08
  }
}
```

Across those 57 models, the median max/min ratio is 2.53x and the median p75/p25 ratio is 1.31x. The typical model's endpoints run about two and a half times from cheapest to dearest, and the middle half of them sit within about 1.3x. Max/min is sensitive to a single outlier endpoint, and the quartile ratio is not. For the most-listed model, the max of $1.95 sits well above the p75 of $0.89, while its p75/p25 ratio is 2.28x. Quote the quartile ratio beside the max/min.

The headline indexes compress the same listings into single numbers. STCI-ALL is $6.00 per 1M blended across all 344 eligible listings. STCI-FRONTIER is $12.04 across 9 models, STCI-EFFICIENT is $1.05 across 9, and STCI-OPEN is $2.05 across 23. Each is one number for a group of models, and none shows how far apart the prices inside one model are.

## Why not quote the cheapest price or one index

Two approaches look reasonable. Each fails in a specific way.

Publishing the cheapest listed price per model is the first. It is what a budget spreadsheet wants. It also selects one endpoint out of 50, and for the most-listed model that endpoint is the fp4 one. The spread record keeps the cheapest endpoint with its precision. That min is a range bound, labeled with its grade, not the model's price.

A headline index is the second. It answers a trend question, and it cannot answer a question about one model, because it is one number over a group of models (344 for STCI-ALL).

## What the spread does not measure

The methodology states its limits. They matter for any quote built on it.

- It measures listed prices, not prices paid. Subsidized or negotiated rates are invisible to it. A reported-price panel is the planned remedy, not something that has shipped.
- It has one source. OpenRouter supplies both the prices and the endpoint list.
- Endpoints are weighted equally. Usage weighting needs reported volumes the methodology does not yet have.
- The 3:1 output-to-input blend is an assumption. It is stated, not measured.

The spread also has a cost. It adds about 60 requests per day to one public endpoint.

## Verification, and what the hash does not prove

The test suite passes: 77 tests, 12 of them new in `tests/test_methodology_v2.py`. The run's verification hash, `3b422aefd8c603c8`, reproduced on a second dry run. A matching hash shows the output is repeatable from the same inputs. It does not show that the listed prices were correct when they were fetched.

## How to run it for a date

Run the three commands in the order the methodology lists them, with the same date each time. They fetch live listings, so running them today will not reproduce the 2026-11-19 figures; the raw observations are not published.

```sh
python -m services.collector.pipeline --date 2026-11-19
python -m services.collector.spread --date 2026-11-19
python -m services.indexer.pipeline --date 2026-11-19
```

The spread lands at `data/spread/2026-11-19.json`. The public JSON built from this file goes through an allow-list, covered [the day before](https://startaitools.com/posts/publish-derived-data-from-an-allow-list/).

Publish the spread beside the price, not instead of it. A price line should carry the min, median and max, the endpoint and provider counts, the precision mix and the precision of the cheapest endpoint. A max/min ratio above the run's 2.53x median is the signal to put that range up front. Models with fewer than four priced endpoints are not reported, so a missing model says nothing about how tight its spread is.

The methodology, the code and the first run's spread file are in the repository, which keeps its older name: https://github.com/jeremylongshore/stci-standard-inference-token-cost-index

## Also shipped

- CI (merged with the methodology change): Playwright 1.57.0 refused to install Chromium on `ubuntu-latest`, which now resolves to 26.04. The browser jobs are pinned to `ubuntu-24.04`.

## Frequently asked questions

### How do you measure the price spread for an open-weight model?

The collector fetches each open-weight model's per-provider endpoint list and records the min, p25, median, p75 and max blended prices, the max/min and p75/p25 ratios, and the serving-precision mix. Models with fewer than four priced endpoints are not reported. The spread for a given day is written to a dated JSON file under data/spread/.

### Should you quote the cheapest endpoint price for an open-weight model?

In the first run, quoting the cheapest figure for the most-listed model meant quoting an fp4 price without saying so, and if your quality bar is fp8, it is the wrong number to budget with. The cheapest endpoint for deepseek/deepseek-v4.1-flash-1017 was Ambient at fp4, with a blended price of 0.1212 against a 0.55 median. Publish the min, median and max together, with the endpoint and provider counts, the precision mix and the cheapest endpoint's precision.

### What does the spread not measure?

It measures listed prices, not prices paid, so subsidized or negotiated rates are invisible to it. It has one source, OpenRouter, which supplies both the prices and the endpoint list. Endpoints are weighted equally, and usage weighting needs reported volumes the methodology does not yet have. The 3:1 output-to-input blend is an assumption, stated but not measured.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How do you measure the price spread for an open-weight model?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The collector fetches each open-weight model's per-provider endpoint list and records the min, p25, median, p75 and max blended prices, the max/min and p75/p25 ratios, and the serving-precision mix. Models with fewer than four priced endpoints are not reported. The spread for a given day is written to a dated JSON file under data/spread/."
      }
    },
    {
      "@type": "Question",
      "name": "Should you quote the cheapest endpoint price for an open-weight model?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "In the first run, quoting the cheapest figure for the most-listed model meant quoting an fp4 price without saying so, and if your quality bar is fp8, it is the wrong number to budget with. The cheapest endpoint for deepseek/deepseek-v4.1-flash-1017 was Ambient at fp4, with a blended price of 0.1212 against a 0.55 median. Publish the min, median and max together, with the endpoint and provider counts, the precision mix and the cheapest endpoint's precision."
      }
    },
    {
      "@type": "Question",
      "name": "What does the spread not measure?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "It measures listed prices, not prices paid, so subsidized or negotiated rates are invisible to it. It has one source, OpenRouter, which supplies both the prices and the endpoint list. Endpoints are weighted equally, and usage weighting needs reported volumes the methodology does not yet have. The 3:1 output-to-input blend is an assumption, stated but not measured."
      }
    }
  ]
}
</script>

## Use this

- Run the three commands above for one date and read `data/spread/<date>.json` for any model you plan to quote.
- Quote each price with its min, median and max, its endpoint and provider counts, and its precision mix. If a model's max/min ratio is above the run's 2.53x median, lead with the range.
- If your quality bar is fp8, check the cheapest endpoint's precision before budgeting with it; for the most-listed model it was fp4. The spread record does not give an fp8 price, so pull the per-provider endpoint list and filter it by precision before you quote.

## Related Posts

- Previous day: the STCI site publishes derived JSON from an allow-list so raw licensed fields cannot leak. [Read it](https://startaitools.com/posts/publish-derived-data-from-an-allow-list/)
- January 2026: STCI v0.1.0, the first token cost index build. [Read it](https://startaitools.com/posts/stci-zero-to-v010-token-cost-index/)
