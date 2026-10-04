# resolved_with enum

From the Help Center article "How were my source maps resolved"
(https://www.sentry.help/en/articles/13964309-how-were-my-source-maps-resolved):

- `debug-id` — recommended matcher
- `url`
- `index`
- `release`
- `release-old`
- `scraping` — Sentry fetched the file from the web
- `unknown`

`scripts/parse-resolved-with.py` accepts this set and only this set.
Different frames in one event can differ. `has debug_meta` is not `has a matching bundle`.

No reprocessing: https://www.sentry.help/en/articles/13965232-javascript-how-do-i-verify-debug-ids-for-source-maps
