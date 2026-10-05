# Brain runtime contract

This reference records the public `brain_search` contract implemented by the
`governed-second-brain` plugin. The skill body owns the answer workflow; this file owns exact runtime
details.

## Contents

- [Tool input](#tool-input)
- [Successful result](#successful-result)
- [Mode and authentication](#mode-and-authentication)
- [Failure semantics](#failure-semantics)

## Tool input

`brain_search` accepts:

- `query`: required non-empty string.
- `scope`: optional `curated`, `all`, `inbox`, or `archived`; default `curated`.
- `limit`: optional integer from 1 through 50; default 10.

Start with 1–4 distinctive keywords. Keep the same keywords when broadening from `curated` to `all`
so the scope change is the only variable.

## Successful result

Both modes return a JSON object containing the query, scope, result count, and `results`. Each result
can contain `citation`, `snippet`, `score`, and `collection`. Cite only `citation` values actually
returned by the tool. Never synthesize a `qmd://` URI.

Local results identify the source as `local-qmd`. Team results come from the configured team service.
Treat snippets as evidence for only the claims they state; provenance does not independently prove a
claim true.

## Mode and authentication

Local mode is selected when no real `TEAMKB_API_URL` is configured. It runs in-process against the
local brain and requires no API credential. A compatible qmd 2.x executable must be on `PATH` for
indexed retrieval.

Team mode is selected when `TEAMKB_API_URL` is set directly or loaded from `~/.teamkb/team.json`.
`TEAMKB_API_TOKEN` supplies the per-user bearer credential and `TEAMKB_TENANT_ID` selects the tenant.
The runtime refuses to start team mode without a token. Never print the token or configuration file
contents.

## Failure semantics

- A successful empty result is not permission to answer from general knowledge. Complete the
  curated-to-all ladder, then state that no governed evidence was found.
- A local result with a note about a missing index means qmd or its index is unavailable; report the
  operational issue.
- A team response with `ok: false`, an authorization error, or an unreachable-service error is a tool
  failure, not an empty knowledge result. Report it distinctly and do not fabricate an answer.
