# brightdata-core-workflow-b — Official Contract

Checked 2026-09-13 against current Bright Data public documentation.

## Contract Applied

The current async lifecycle is trigger, progress, then snapshot download under `/datasets/v3`. The workflow binds each transition to one approved manifest and treats output as quarantined until validation.

## Primary Sources

- [Web Scraper API asynchronous requests](https://docs.brightdata.com/api-reference/rest-api/scraper/asynchronous-requests)
- [Download snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/download-snapshot)
- [Scraper async requests guide](https://docs.brightdata.com/products/scrapers/scrapers-library/async-requests)
- [Authentication and API keys](https://docs.brightdata.com/api-reference/authentication)
