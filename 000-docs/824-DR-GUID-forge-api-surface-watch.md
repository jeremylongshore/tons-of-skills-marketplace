<!-- doc-class: record -->

# Forge API surface watch

The weekly watch compares tool names captured in a forge research record with the
current official public source catalogue. It opens a review issue when a captured
name disappears or a probe cannot establish an answer. This gives maintainers a
bounded trigger to consider `/skill-creator --reforge` without rewriting a plugin
or treating a failed request as a clean result. Tracking: `claude-e9z6`.

## Scope and evidence limit

The initial adapter covers the Plane plugin's 13 names in
[its original forge research](../plugins/productivity/plane/.forge/research.md).
The reviewed [configuration](../scripts/forge-api-surfaces.json) binds the exact
research SHA-256 and ordered name list. It probes the official
[Plane MCP server](https://github.com/makeplane/plane-mcp-server) public source,
not an authenticated Plane workspace or installed server.

The adapter resolves the current upstream commit, then retrieves its explicit
`RESOURCES` registry and registered resource modules at that one commit. It parses
literal `NAME`, `LEGACY` and `LEGACY_UNMAPPED` declarations with Python's syntax
parser. It does not import or execute upstream Python. Declared legacy aliases
count as present, avoiding a false removal merely because a name is no longer
advertised. Undeclared and explicitly unmappable names require review.

The [first public-source report](825-RA-DATA-forge-api-surface-probe.json) records
source hashes and the exact revision. The finding concerns a documented name
surface. It is not a live outage, installed-version assessment, parameter/schema
compatibility test, behavioral evaluation or authorization to migrate the server.
The upstream [migration notes](https://github.com/makeplane/plane-mcp-server/blob/dc7cfd9f3c305891909e2372f0cc507291353801/README.md#migrating-from-the-nodejs-server)
identify the former Node implementation as deprecated; the actual user's server
version still needs review before changing a plugin.

## Results and failure handling

| Result          | CLI exit | Interpretation                                                                                                                                                                 |
| --------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `NO_NAME_DRIFT` | 0        | Every captured name is present in the parsed catalogue or its declared aliases; no stronger compatibility claim.                                                               |
| `NAME_DRIFT`    | 1        | At least one captured name is absent, including an explicitly unmappable name.                                                                                                 |
| `UNVERIFIED`    | 2        | Missing/unreviewed configuration, changed research binding, unsupported source layout, malformed data, HTTP failure, redirect, size limit or deadline prevents the comparison. |

Every discovered `plugins/*/*/.forge/research.md` without a reviewed probe is an
explicit `UNVERIFIED` row. A new forge capture never disappears into a zero count.
The initial adapter supports only the fixed official Plane repository and registry;
other APIs need a reviewed adapter, not an arbitrary URL in a configuration file.

Requests are unauthenticated HTTPS to two fixed GitHub hosts, with redirects and
proxy inheritance disabled. Each response is limited to 512 KiB, the shared source
budget to 8 MiB, and the registry to 40 resources. The network budget is 120 seconds
with an at-most-eight-second in-flight read allowance; the workflow also has a
five-minute job deadline. Source failures retain an explicit unknown result and
never become an empty successful catalogue. No provider key is needed.

## Run and operate

From the repository root:

```bash
python3 scripts/forge-api-drift.py --output /tmp/forge-api-report.json
```

A nonzero exit is expected for drift or incomplete evidence. Inspect the JSON,
research binding and pinned source before deciding what changed. The report stores
an observation timestamp, upstream commit, source SHA-256 values, missing names and
declared alias targets; it does not store credentials or workspace data.

[Forge API Surface Watch](../.github/workflows/forge-api-drift.yml) runs offline
contract tests on relevant PRs. Live probes run Tuesdays at 07:20 UTC or by a manual
workflow dispatch on `main`. PRs and non-main dispatches never run the live probe
or get an issue-writing job. This maintenance workflow is separate from
`ci-required`; no required context, risk route or existing test is removed.

The probe job has read-only repository permissions, no persisted checkout token,
and no API key. It retains the JSON report for 90 days. A separate reporting job
gets `issues: write`, validates bounded report fields and reconciles one bot-owned
review issue per plugin. It reads the complete bounded open-issue inventory,
ignores user-authored marker spoofs and pull requests, and refuses duplicate
bot-owned matches. Repeated identical evidence sends no comment or update;
changed evidence updates the bot's issue body. It never closes an issue on a later
clean result. The workflow remains red for drift or an unverified probe even
when issue creation succeeds. If publication fails, the failed workflow and report
remain the recovery path; no successful notification is claimed.

Review the report from the same workflow run, the particular installed MCP server,
upstream migration/alias behavior and the plugin's actual instructions. Decide
whether to reforge, make a bounded correction, or record a reviewed non-breaking
disposition. Changes to the research capture require updating its hash and exact
name list in the same reviewed change. The watcher cannot recapture its own baseline,
modify a plugin, push commits, change a provider or run `/skill-creator` itself.

## Verification and rollback

Offline tests exercise missing names versus aliases, unmappable names, unregistered
files, changed captures, unsupported URLs, source failures and inert parsing.
Publisher tests cover invalid reports, injection-shaped fields, pagination, deduplication,
user/PR exclusion and API refusal. Run them with:

```bash
python3 -m unittest discover -s tests -p test_forge_api_drift.py -v
node --test scripts/forge-api-drift-issues.test.mjs
```

To stop future probes, disable this workflow in GitHub or remove its schedule in a
normal reviewed PR. Preserve reports and already-open issues for disposition.
There is no runtime or data migration to reverse. Removing this watcher does not
repair an upstream API change, erase its history or alter existing merge gates.
