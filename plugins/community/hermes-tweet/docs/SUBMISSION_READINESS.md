# Submission readiness

Use this checklist before proposing Hermes Tweet to another project. Submit
only when the target can list or install the existing package without copying,
translating, or repackaging it.

## Confirm the fit

The target must document a native route for at least one of these entries:

- Hermes Agent plugins or Skills
- X/Twitter search, monitoring, or approved publishing tools
- MCP projects that document optional Hermes Agent backends
- plugin catalogs that accept external source repositories
- skill registries, ecosystem directories, or awesome lists with third-party
  entries
- framework integrations backed by a working, tested adapter

Reject a target when any condition below applies:

- Its repository only implements a marketplace, crawler, registry server, or
  hosted submission form.
- It lists only the owner's products, plugins, templates, or source namespace.
- It accepts runtime-specific code instead of a source-linked package entry.
- Its entries are generated, mirrored, vendored, or overwritten from another
  source.
- It requires copying Hermes Tweet into a local plugin or Skill directory.
- It offers only a browser-cookie, TweetClaw, OpenClaw, MCP-server, prompt,
  workflow, connector, app, or framework-adapter route.
- It is archived, closed to outside contributions, or unrelated to Hermes
  Agent and X/Twitter.
- Its stated maturity, usage, payment, or promotion rules exclude Hermes Tweet.
- It already contains the same or an adjacent Xquik entry in that catalog lane.

A filename such as `catalog.json` or `registry.yaml` proves nothing by itself.
Confirm that maintainers accept changes to that exact source file. If a
generator owns the file, edit its documented input instead.

Topic labels such as `agent-skill`, `mcp-server`, or `awesome-list` help with
discovery. They do not prove that a repository accepts third-party entries.

Review the repository license and contribution terms. An explicit incompatible
license or unsigned legal agreement blocks submission. Missing license metadata
is review context, not an automatic rejection. Check common root files such as
`LICENSE`, `LICENSE.md`, `COPYING`, and `NOTICE` before deciding.

## Check the native route

Before preparing a change, verify all of these conditions:

- Contribution docs invite third-party source repositories.
- The pull-request feature is enabled and accepts external fork heads.
- The proposed file is the canonical, PR-editable source.
- The entry can link to `Xquik-dev/hermes-tweet` as shipped.
- The target format supports Hermes Agent or X/Twitter tools.
- The wording and validation match accepted examples.

A disabled pull-request feature, a `404` from its pull-request endpoint, or an
equivalent rejection blocks the route. A successful fork or branch push does
not override that result.

Framework and automation projects need a native implementation before a
listing. Do not invent a tool class, node, action, connector, workflow,
container, package, or example solely to create a catalog entry.

## Prevent duplicates

Search before editing:

- the target README, docs, manifests, examples, indexes, Skills, and catalogs
- open and closed pull requests and issues
- public GitHub code results for `Hermes Tweet`, `hermes-tweet`, `Xquik`, and
  the repository URL
- adjacent names: `TweetClaw`, `OpenClaw`, `SocialClaw`,
  `x-twitter-scraper`, `source-packets`, and `evidence-packets`
- upstream sources for translated, generated, or mirrored lists

Treat a live listing, open proposal, closed submission, duplicate head branch,
or PR creation collision as existing work. Inspect that work instead of
opening another proposal. Refresh it only to fix a merge blocker, broken
validation, stale source pin, or stale target-native wording.

An adjacent Xquik entry saturates a generic catalog lane. Propose Hermes Tweet
only when the target documents a separate Hermes Agent plugin lane. A generic
Claude plugin, agent Skill, or social-tools heading is not enough.

If the target requires an issue first, use its issue process. If maintainers
closed an earlier proposal for maturity or fit, wait for new evidence or a
maintainer request.

## Name the package

The title, summary, slug, and added text must name `Hermes Tweet` or
`hermes-tweet`. Do not title a Hermes Tweet submission only for Xquik,
TweetClaw, OpenClaw, an MCP data entry, or a handoff packet.

Use direct wording that matches the target:

- Hermes Agent Twitter plugin
- Hermes Agent X plugin
- Twitter search and monitoring for Hermes Agent
- read-only by default, with explicit action approval
- compatible with Hermes Desktop, gateways, TUI, CLI, dashboard, and cron
- complementary to browser-cookie and direct OAuth workflows
- copied endpoint URLs resolve only to catalog-listed `/api/v1/...` paths

Do not claim that Hermes Tweet replaces the target, fixes its bugs, bypasses
platform rules, or removes user approval.

## Validate the change

Run every target-required check. When available, also run:

- target tests, linters, manifest checks, and catalog generators
- `git diff --check`
- an exact conflict-marker scan
- an added-line scan for secrets and private implementation details
- live link checks for every changed URL

Reread the rendered title, summary, and diff before requesting review. When
using a shell, prepare Markdown bodies through a reviewed file or another
non-interpolating path.

If a route lacks CI, leave one concise validation comment. Do not repeat
validation comments that already contain current evidence.

## Protect public data

Never publish:

- API keys, cookies, tokens, private account data, screenshots, or raw logs
- nonpublic services, providers, pricing units, capacity, or routing details
- commands that require production access, browser login, payment, or secret
  retrieval

Public examples may name only documented settings: `XQUIK_API_KEY`,
`XQUIK_BASE_URL`, and `HERMES_TWEET_ENABLE_ACTIONS`.
