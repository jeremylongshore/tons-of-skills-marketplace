# Provider Tier Matrix

**Snapshot date: 2026-04-21.** Provider tiers change quarterly — **re-verify against the official console before shipping.** Treat this table as a starting point, never a source of truth.

Official sources:

- Anthropic: https://platform.claude.com/docs/en/api/rate-limits
- OpenAI: https://platform.openai.com/docs/guides/rate-limits
- Google Gemini: https://ai.google.dev/gemini-api/docs/rate-limits

## What the numbers mean

| Term | Meaning |
|---|---|
| **RPM** | Requests per minute — counts every API call, cached or not |
| **ITPM** | Input tokens per minute — prompt tokens (including cached reads on Anthropic) |
| **OTPM** | Output tokens per minute — completion tokens only |
| **TPM** | Tokens per minute — combined input + output (OpenAI's older naming) |
| **Concurrent** | Max in-flight requests at any moment (where reported) |
| **Cached separation** | Whether cache reads/writes have their own budget |

On Anthropic, **RPM counts all requests uniformly** — cached reads consume the same 1 RPM as uncached calls (P31). A cache-heavy workload at 50 RPM can 429 while the ITPM budget shows plenty of headroom. Budget RPM at the client level (semaphore + Redis limiter), not by token count.

## Anthropic

| Tier | RPM | ITPM | OTPM | Eligibility |
|---|---|---|---|---|
| Free / Evaluation | 5 | 20K | 4K | Signup default |
| Build Tier 1 | 50 | 40K | 8K | $5 credit purchase |
| Build Tier 2 | 1000 | 80K | 16K | $40 spent, 7d wait |
| Build Tier 3 | 2000 | 160K | 32K | $200 spent, 7d wait |
| Build Tier 4 | 4000 | 400K | 80K | $400 spent, 14d wait |
| Scale (enterprise) | Custom | Custom | Custom | Sales contract |

Notes:

- Limits are **per workspace per model**. `claude-sonnet-4-6` and `claude-haiku-4-5` have separate counters — a fanout to both doubles your effective RPM.
- **Prompt caching**: cache reads count toward RPM but use the **cache-read ITPM** budget (a separate line item on the dashboard). Cache writes count toward RPM and uncached ITPM.
- `anthropic-beta: prompt-caching-2024-07-31` is GA in 2026; no opt-in needed but dashboard keeps legacy cached-read numbers in a separate metric.
- Rate-limit headers: `anthropic-ratelimit-requests-remaining`, `anthropic-ratelimit-tokens-remaining`, `anthropic-ratelimit-reset`. Read these in a callback to predict 429 before it happens.

## OpenAI

| Tier | RPM (GPT-4o) | TPM (GPT-4o) | RPD | Eligibility |
|---|---|---|---|---|
| Free | 3 | 40K | 200 | Signup default (no credits) |
| Tier 1 | 500 | 30K | 10K | $5 paid |
| Tier 2 | 5000 | 450K | — | $50 paid + 7d |
| Tier 3 | 5000 | 800K | — | $100 paid + 7d |
| Tier 4 | 10000 | 2M | — | $250 paid + 14d |
| Tier 5 | 10000 | 30M | — | $1K paid + 30d |

Notes:

- Model-specific. `gpt-4o-mini` has higher RPM than `gpt-4o` at the same tier.
- **Rate-limit headers**: `x-ratelimit-remaining-requests`, `x-ratelimit-remaining-tokens`, `x-ratelimit-reset-requests`, `x-ratelimit-reset-tokens`. OpenAI returns these on **every** response, not just 429s — cheap to read.
- OpenAI's TPM counts **input + output** combined, unlike Anthropic's split ITPM/OTPM.
- Free tier's 3 RPM is unusable for real work; assume Tier 1 as the floor in docs.

## Google Gemini

| Tier | RPM (2.5 Pro) | TPM (2.5 Pro) | RPD | Eligibility |
|---|---|---|---|---|
| Free | 15 | 1M | 1500 | Signup default (AI Studio) |
| Paid Tier 1 | 2000 | 4M | — | Billing enabled |
| Paid Tier 2 | 10000 | 10M | — | $250 spent |
| Paid Tier 3 | 30000 | 20M | — | $1K spent |

Notes:

- Free tier TPM is high (1M) but RPM is brutal (15). Chatbots fit; bulk ETL does not.
- Gemini 2.5 Flash has ~3x the RPM of Pro at each tier.
- **Rate-limit headers**: Google uses `x-goog-quota-units-remaining` and `retry-after`. Less uniform than OpenAI/Anthropic.
- Safety-block (`finish_reason=SAFETY`) is **not** a rate-limit error — it's deterministic for the same input. See pain-catalog P65.

## Recommended `requests_per_second` for `InMemoryRateLimiter`

**Single-process dev only** — for multi-worker prod, use [Redis Limiter Pattern](redis-limiter-pattern.md).

Target: 70% of your tier's RPM to leave headroom for interactive traffic and spikes.

| Tier | Target RPM | `requests_per_second` |
|---|---|---|
| Anthropic Free (5 RPM) | 3 | 0.05 |
| Anthropic Build 1 (50 RPM) | 35 | 0.58 |
| Anthropic Build 2 (1000 RPM) | 700 | 11.6 |
| OpenAI Tier 1 (500 RPM) | 350 | 5.8 |
| OpenAI Tier 3 (5000 RPM) | 3500 | 58.3 |
| Gemini Free (15 RPM) | 10 | 0.17 |
| Gemini Paid 1 (2000 RPM) | 1400 | 23.3 |

## Which limit binds first?

For any given workload, exactly one limit binds. Do the math:

```
avg_input_tokens_per_call * requests_per_minute  →  effective ITPM usage
avg_output_tokens_per_call * requests_per_minute →  effective OTPM usage
requests_per_minute                              →  effective RPM usage
```

Examples:

- **Short chat replies** (~500 input / ~200 output): RPM binds first
- **Long document Q&A** (~20K input / ~500 output): ITPM binds first on Anthropic Build 1 (40K ITPM / 20K = only 2 requests/min possible)
- **Long completions** (~500 input / ~8K output): OTPM binds first on Anthropic Build 1 (8K OTPM / 8K = 1 request/min)

Pick the limiter configured for the binding constraint, not the nominal RPM.

## Separate monitors: cached vs uncached

On Anthropic, cache-heavy workloads trip 429 differently:

```python
# Callback that separates metrics
class CacheAwareUsageHandler(BaseCallbackHandler):
    def on_llm_end(self, response, **kwargs):
        usage = response.llm_output.get("usage", {})
        cache_read = usage.get("cache_read_input_tokens", 0)
        cache_write = usage.get("cache_creation_input_tokens", 0)
        uncached = usage.get("input_tokens", 0) - cache_read - cache_write
        metrics.incr("anthropic.cached_read_tokens", cache_read)
        metrics.incr("anthropic.cached_write_tokens", cache_write)
        metrics.incr("anthropic.uncached_input_tokens", uncached)
```

Alert on each independently. A 90% cache hit rate will still 429 at your RPM ceiling.

## Verification checklist before shipping

- [ ] Confirmed current tier in provider console (tier changes with spend)
- [ ] Measured actual p50/p95 input/output tokens on representative traffic
- [ ] Computed which limit binds first for your workload
- [ ] Configured `requests_per_second` at 70% of binding limit
- [ ] Confirmed rate limiter is Redis-backed (not `InMemoryRateLimiter`) if workers > 1
- [ ] Added callback that logs per-call RPM-remaining header
- [ ] Verified retry-after header is honored (LangChain does this by default)
- [ ] Set `max_retries=2` (not the 6 default — see pain-catalog P30)
- [ ] Narrow `with_fallbacks(exceptions_to_handle=...)` tuple documented (see pain-catalog P07)
