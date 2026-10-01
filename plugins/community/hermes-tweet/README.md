# Hermes Tweet for Twitter Search & X Actions

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/13725/badge)](https://www.bestpractices.dev/projects/13725)
[![CI](https://github.com/Xquik-dev/hermes-tweet/actions/workflows/ci.yml/badge.svg)](https://github.com/Xquik-dev/hermes-tweet/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/hermes-tweet.svg)](https://pypi.org/project/hermes-tweet/)

Add Twitter API search, monitoring, and approved X actions to
[Hermes Agent](https://github.com/NousResearch/hermes-agent).

Explore 102 OpenAPI-generated endpoints, including 33 prepaid reads and 7 direct MPP routes.
Reads and actions use separate tools. Actions stay disabled by default.
The plugin bundles a Hermes Skill and 2 slash commands.

## When to use Hermes Tweet

Use this plugin for X/Twitter search, reads, or monitoring in Hermes.
Choose an SDK for application code.

## Install

Install and enable the plugin:

```bash
hermes plugins install Xquik-dev/hermes-tweet --enable
```

Hermes scans plugins during install and update. Review any warning before
continuing. A dangerous verdict blocks installation or disables an update.

Or install the PyPI package into Hermes:

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-tweet
hermes plugins enable hermes-tweet
```

Install a local checkout:

```bash
hermes plugins install file:///absolute/path/to/hermes-tweet --force --enable
```

## Configure

Create an API key in Xquik. Then set:

```bash
export XQUIK_API_KEY="xq_..."
```

Optional settings:

```bash
export XQUIK_BASE_URL="https://xquik.com"
export HERMES_TWEET_ENABLE_ACTIONS="false"
```

Restart Hermes after changing environment variables.

## Tools

| Tool | Purpose |
| --- | --- |
| `tweet_explore` | Search the bundled catalog. Makes no API call. |
| `tweet_read` | Call catalog-listed read endpoints. |
| `tweet_action` | Call private or mutating endpoints. Disabled by default. |

Use `tweet_explore` first. Then pass a listed `/api/v1/...` path to the matching tool.

Copied Xquik URLs work when their paths match the catalog.

## Common Twitter API tasks

Start with `tweet_explore`. Invoke only the path returned by the catalog.

| Task | Catalog query | Tool |
| --- | --- | --- |
| Search X posts | `search tweets by query` | `tweet_read` |
| Read profile timelines | `list recent tweets posted by a user` | `tweet_read` |
| Export followers | `run extraction` | `tweet_action` |
| Export following accounts | `run extraction` | `tweet_action` |
| Monitor an account | `create monitor` | `tweet_action` |
| Post or reply | `create tweet` | `tweet_action` |

Set `include_actions` for extraction, monitoring, and writing searches.
`tweet_action` always follows the approval rules below.

## Safety

- Tools never accept credentials as arguments.
- The plugin injects `XQUIK_API_KEY` at request time.
- Admin, billing, credit, support, guest-wallet, and API-key routes stay hidden.
- Account re-authentication routes stay hidden.
- Binary downloads stay outside the agent catalog. Use REST for those files.
- Private reads and mutations use `tweet_action`.
- `tweet_action` requires `HERMES_TWEET_ENABLE_ACTIONS=true`.

Without an API key, Hermes exposes only `tweet_explore`.

## Slash commands

| Command | Purpose |
| --- | --- |
| `/xstatus` | Show Xquik account and usage status. |
| `/xtrends` | Show current X trends. |

## Development

Regenerate the catalog from the canonical OpenAPI schema:

```bash
python scripts/build_catalog.py ../xquik/openapi.yaml
```

Run all checks:

```bash
uv run --python 3.12 --group dev ruff format --check .
uv run --python 3.12 --group dev ruff check .
uv run --python 3.12 --group dev basedpyright
uv run --python 3.12 --group dev pytest --cov=hermes_tweet --cov=tests --cov-report=term-missing --cov-fail-under=100
uv run --python 3.12 --group dev bandit -c pyproject.toml -r hermes_tweet scripts fuzz
uv run --python 3.12 --group dev pip-audit
uv run --python 3.12 --group dev bash scripts/check_reproducible.sh
uv run --python 3.12 --group dev python -m build
uv run --python 3.12 --group dev twine check dist/*
```

## Links

- [Xquik API reference](https://docs.xquik.com/api-reference/overview)
- [Xquik authentication](https://xquik.com/auth.md)
- [Context7 guide](https://context7.com/xquik-dev/hermes-tweet)
- [Integration patterns](docs/INTEGRATION_PATTERNS.md)
- [Hermes runtime hosts](docs/HERMES_SURFACES.md)
- [Organization support policy](https://github.com/Xquik-dev/.github/blob/main/SUPPORT.md)
- [Security policy](SECURITY.md)
- [Contribution guide](https://github.com/Xquik-dev/.github/blob/main/CONTRIBUTING.md)

## License

[MIT](LICENSE)

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
