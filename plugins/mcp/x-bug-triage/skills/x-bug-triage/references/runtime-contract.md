# X bug triage runtime contract

## Live network surface

resolve_username, fetch_mentions, search_recent, search_archive, fetch_conversation, and
fetch_quote_tweets call X API v2 with X_BEARER_TOKEN. Successful responses may be cached locally.
Mentions default to 8 pages with a documented 800-post cap; recent search defaults to 3 pages; archive
search defaults to 2; conversation fetch uses at most 5 pages.

## Local library surface

Parser, classifier, redactor, scorer, dedupe, clustering, database, override, audit, retention,
freshness, and source-status helpers exist under lib/. No MCP tool exposes the normalization or
clustering pipeline and no checked-in command orchestrates all stages. New clusters start at low
severity; config-defined escalation rules are not executed automatically.

## Stub surface

- All four repo-analysis handlers generate synthetic evidence from input strings.
- All five routing handlers return fixed metadata with no team or assignee.
- create_draft_issue creates local text from supplied JSON.
- check_existing_issues compares only titles supplied by the caller.
- confirm_and_file performs no GitHub request and returns an /issues/NEW placeholder.
- parse_review_command checks syntax only.

## Absent surface

The plugin exposes no Slack tool, no terminal-state store, no real GitHub scan/file client, no
severity engine, and no end-to-end MCP command. The database schema can store overrides, issue links,
and audit rows, but the review-command MCP parser does not write them.
