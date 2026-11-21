# SpecStream Operator Skill Pack

Operator workflows and offline payload checks for [SpecStream](https://specstream.ai): Search API, drop-in search routes, Extract API, Deep Search structured tables, recurring schedules, and remote Streamable HTTP MCP setup.

## Installation

```bash
/plugin install specstream-pack@claude-code-plugins-plus
```

Or via `ccpi`:

```bash
ccpi install specstream-pack
```

## Authentication and Keyless Behavior

`specstream-pack` works offline without `SPECSTREAM_API_KEY` set:

- All validation helpers and unit tests run locally with zero network calls.
- Unauthenticated SpecStream discovery endpoints (`GET https://api.specstream.ai/v1/search-dialects`, `GET https://api.specstream.ai/v1/search-engines`, `GET https://api.specstream.ai/v1/agent/lists`, and `GET https://api.specstream.ai/.well-known/agent-card.json`) require no key and cost nothing.
- Live pay-per-request calls can use MPP or x402 without an account, or use a scoped `SPECSTREAM_API_KEY` (`Authorization: Bearer <key>`) created in the SpecStream workspace (`https://specstream.ai/workspace`) or via agent signup (`POST /v1/agent/signup`).

## Skills Included

| Skill | What It Covers |
| --- | --- |
| `specstream-search-and-dropins` | `GET /v1/web-search` ($5/1,000 default, $1/1,000 `speed=fast`), `POST /v1/web-search`, `passages=true`, `images=true`, and drop-in base URLs for Tavily, Exa, Brave, Serper, SearXNG, Google CSE, Bing v7, and Firecrawl v2. |
| `specstream-extract` | `POST /v1/extract` ($0.80/1,000 pages; empty pages uncharged), 1-20 URLs or `pages` HTML per call, `format`/`include` options, `Idempotency-Key`, and per-URL statuses. |
| `specstream-tables` | Deep Search multi-row structured tables (`POST /v1/agent/lists`, `POST /v1/parse`, MCP `compile` -> `quote_capacity_work` -> `authorize_capacity_work` -> `get_find_decisions`), `confirm_max_cents` approval, and per-row `source_url`/`seen_at` provenance. |
| `specstream-schedules` | Saved Deep Search schedules, hourly-to-yearly refresh runs inside `spend_cap_cents` limits, half-rate changed/new rows vs 1c unchanged rows, Slack/email/sheet/CRM/webhook delivery, and signals. |
| `specstream-mcp-setup` | Remote Streamable HTTP MCP server (`https://api.specstream.ai/mcp`) via OAuth or Bearer token, key scopes (`finds:spend`, `zero_retention`, `eu_egress_only`), agent signup, and A2A (`/a2a`). |

## Offline Verification

Validate any JSON request or MCP config locally without API keys:

```bash
python3 plugins/saas-packs/specstream-pack/scripts/validate_specstream_payload.py --kind search --stdin <<'EOF'
{"q": "\"specstream\" search api", "speed": "fast", "num": 10}
EOF
```

Run the pack's schema validation and contract tests:

```bash
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/saas-packs/specstream-pack/
python3 -m unittest tests/test_specstream_pack_contract.py -v
```

## Documentation

- [PRD](docs/PRD.md)
- [Architecture Decision Record](docs/ADR.md)
- [One-Pager](docs/ONE-PAGER.md)
- [SpecStream Agent Reference](https://specstream.ai/agents.md)
