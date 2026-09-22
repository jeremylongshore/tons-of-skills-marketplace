# brightdata-webhooks-events — Official Contract

Checked 2026-09-13 against current Bright Data public documentation.

## Contract Applied

Webhook-style delivery uses the current snapshot delivery endpoint and a managed destination. The receiver streams, authenticates, validates, deduplicates, quarantines, and replays without relying on undocumented IP or retry assumptions.

## Primary Sources

- [Deliver snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/deliver-snapshot)
- [Scraper data delivery](https://docs.brightdata.com/products/scrapers/scrapers-library/data-delivery)
- [Download snapshot](https://docs.brightdata.com/api-reference/scrapers/delivery-apis/download-snapshot)
- [REST API authentication](https://docs.brightdata.com/api-reference/authentication)
