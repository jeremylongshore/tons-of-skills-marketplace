# SpecStream Search API and Drop-In Reference

## Native Endpoints

- `GET https://api.specstream.ai/v1/web-search?q=<query>`
- `POST https://api.specstream.ai/v1/web-search` with JSON body `{"q": "...", "speed": "fast"}`
- `POST https://api.specstream.ai/v1/web-search/batch`
- `GET https://api.specstream.ai/v1/web-search/answers` and `/answers/{id}` (history, zero cost, `finds:read`)
- `GET https://api.specstream.ai/v1/search-dialects` (unauthenticated, zero cost)
- `GET https://api.specstream.ai/v1/search-engines` (unauthenticated, zero cost)

## Pricing

- Default search (`speed=default` or omitted): $0.005 up to 10 results ($5 per 1,000), +$0.006 per started block of 10 additional results.
- Fast tier (`speed=fast`, default on drop-in routes): $0.001 up to 10 results ($1 per 1,000), +$0.0012 per started block of 10 additional results.
- Empty result sets (`200` with empty `sources` and `rows`) cost nothing.

## Drop-In Routes

| Provider | SpecStream Base / Route | Key Placement |
| --- | --- | --- |
| Tavily | `https://api.specstream.ai/tavily` (`POST /tavily/search`, `/tavily/extract`) | Bearer token or `api_key` |
| Exa | `https://api.specstream.ai/exa` (`POST /exa/search`, `/exa/contents`) | `x-api-key` or Bearer token |
| Brave Search | `https://api.specstream.ai` (`GET /res/v1/web/search`) | `X-Subscription-Token` |
| Serper | `https://api.specstream.ai/serper` (`POST /serper/search`) | `X-API-KEY` |
| SearXNG | `https://api.specstream.ai/searxng/<key>` (`GET /searxng/search`) | Path, `key=`, `X-API-Key`, Bearer, or Basic |
| Google CSE | `https://api.specstream.ai` (`GET /customsearch/v1`) | `key=`, `X-Goog-Api-Key`, or Bearer |
| Bing v7 | `https://api.specstream.ai/v7.0/search` | `Ocp-Apim-Subscription-Key` |
| Firecrawl v2 | `https://api.specstream.ai/firecrawl` (`POST /firecrawl/v2/search`, `/scrape`) | Bearer token |
