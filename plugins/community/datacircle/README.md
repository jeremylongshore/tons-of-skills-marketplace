# Datacircle for Claude Code

Find the best GTM APIs. We benchmark all the GTM APIs and we put the results on our website: https://datacircle.dev

This plugin gives Claude Code one skill, `datacircle`, that calls our open API at https://api.datacircle.dev/v1. It is free, with no key and no account (spec: https://api.datacircle.dev/v1/openapi.json).

## Install

In Claude Code:

```
/plugin marketplace add waynehamadi/claude-code-datacircle
/plugin install datacircle@datacircle
```

Or from a shell:

```bash
claude plugin marketplace add waynehamadi/claude-code-datacircle
claude plugin install datacircle@datacircle
```

## Use

Ask about a GTM API and the skill loads when it applies:

- "Which email finder API is best?"
- "What's the cheapest LinkedIn profile API per 1,000 results?"
- "Where does Bright Data rank?"

Or call it by name: `/datacircle:datacircle best phone validation API`.

Each answer gives the provider, the plan, its score out of 100 and its price per 1,000 results, with a link to the page on datacircle.dev it came from.

## The calls it makes

- `GET /apis`: every API on our sheet
- `GET /apis/{slug}/best`: who is best for one
- `GET /plans`: every plan, by API, provider or price
- `GET /providers/{slug}`: one provider's ranks

## Requirements

`curl`, and `jq` to pick keys (or `python3`). At most 60 calls a minute from one address. Every plan is also one file at https://datacircle.dev/datacircle.json.

## License

MIT. The data is CC BY 4.0, from https://datacircle.dev.
