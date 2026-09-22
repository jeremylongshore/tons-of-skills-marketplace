# Support

How to get help with this repository, what response time to expect, and what is
fully supported versus best-effort.

## Where to ask

| I want to…                        | Go to                                                                                                                                    |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Ask a usage question              | [GitHub Discussions — Q&A](https://github.com/jeremylongshore/tons-of-skills-marketplace/discussions/categories/q-a)                     |
| Propose or discuss an idea        | [GitHub Discussions — Ideas](https://github.com/jeremylongshore/tons-of-skills-marketplace/discussions/categories/ideas)                 |
| Show off something you built      | [GitHub Discussions — Show and tell](https://github.com/jeremylongshore/tons-of-skills-marketplace/discussions/categories/show-and-tell) |
| Request a new plugin pack         | [Plugin Pack Request discussion template](DISCUSSION_TEMPLATE/plugin-pack-request.yml)                                                   |
| Report a bug or request a feature | [Open an issue](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/new/choose)                                         |
| Submit a plugin                   | The plugin-submission issue template, then follow [CONTRIBUTING.md](CONTRIBUTING.md)                                                     |
| Report a security vulnerability   | [SECURITY.md](SECURITY.md) — **never a public issue**                                                                                    |

Issue templates exist for bug reports, feature requests, documentation problems,
questions, plugin submissions, and killer-skill nominations — the
[issue chooser](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/new/choose)
routes you to the right one.

## Triage SLA

**First response within 72 hours** on new Issues and Discussions. That first
response is triage — an acknowledgment, a label, a question back, or a routing
decision — not necessarily a fix. Complex fixes land on their own schedule and are
tracked in the issue thread.

## Security reports

Follow [SECURITY.md](SECURITY.md): report privately via
[GitHub Security Advisories](https://github.com/jeremylongshore/tons-of-skills-marketplace/security/advisories/new)
or email `jeremy@intentsolutions.io`. Security reports get acknowledged within
24 hours with a remediation timeline within 72 hours — faster than the general
triage SLA above.

## What's supported vs best-effort

This repo follows the mirror-by-default model for externally-synced plugins (see
[STANDARDS.md](../STANDARDS.md) and the
[decision record](../000-docs/694-AT-DECR-external-sync-mirror-by-default-model.md)),
which determines where a fix can actually land:

- **Intent Solutions–authored plugins and skills** (the large in-repo majority),
  the catalog tooling, the `ccpi` CLI, and the marketplace site are **fully
  supported here** — bugs in them are ours to fix, under the SLA above.
- **Mirrored external plugins** (registered in `sources.yaml`) are **best-effort**.
  Their upstream repo is the source of truth and we deliberately do not carry local
  patches, so a bug in a mirrored plugin's own code belongs in the upstream
  maintainer's tracker. Open an issue here anyway if you're not sure — triage will
  identify the upstream repo and point you (or the report) at it. Problems with
  _how we mirror or catalog_ an external plugin are ours and fully supported.

## Before you post

- Check [README.md](../README.md) and [CONTRIBUTING.md](CONTRIBUTING.md) — most
  install, catalog, and submission questions are answered there.
- Search existing issues and discussions; duplicates get closed with a pointer.
- Interactions in every support channel are governed by the
  [Code of Conduct](../CODE_OF_CONDUCT.md).
