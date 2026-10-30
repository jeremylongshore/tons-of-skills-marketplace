# Plane API Surface

Reviewed 2026-10-23. This plugin does not install or pin a server implementation.
The May capture names match the versioned legacy Node comparison below; that
match does not identify a user's installed version. Inspect the connected server
identity and schemas before any call. The MCP prefix is chosen by the host and
may differ from `mcp__plane`.

## Versioned primary references

- Legacy comparison: [`@makeplane/plane-mcp-server@0.1.5`](https://registry.npmjs.org/@makeplane/plane-mcp-server/0.1.5), whose `gitHead` is [`537d9760efb72c1fca4b5c3259aa0710bf60fefd`](https://github.com/makeplane/plane-mcp-server/tree/537d9760efb72c1fca4b5c3259aa0710bf60fefd/src/tools). Its tool registrations contain all 13 captured names and `get_projects`. This is a comparison version, not an installed-version claim.
- Python comparison: [`plane-mcp-server` 0.3.5 at `dc7cfd9f3c305891909e2372f0cc507291353801`](https://github.com/makeplane/plane-mcp-server/blob/dc7cfd9f3c305891909e2372f0cc507291353801/pyproject.toml). Its [resource definitions](https://github.com/makeplane/plane-mcp-server/tree/dc7cfd9f3c305891909e2372f0cc507291353801/plane_mcp/tools) declare consolidated tools/actions. The [README](https://github.com/makeplane/plane-mcp-server/blob/dc7cfd9f3c305891909e2372f0cc507291353801/README.md) describes the Node server as deprecated and unmaintained.

Neither source inspection nor an alias establishes deployed availability, matching
response schemas, or successful authentication. No workspace was queried for this review.

## Capability mapping

The Python column lists resource tool + `action`, not a legacy function to call.
Inspect the actual schema, supply its required arguments, and use only permitted
reads. Pass `project_id` explicitly on project-scoped queries even when optional.

| Legacy tool | Python tool / action | Arguments for intended scope |
|---|---|---|
| `get_projects` | `project` / `list` | Workspace configured in server |
| `list_project_issues` | `workitem` / `list` | `project_id` |
| `get_issue_using_readable_identifier` | `workitem` / `retrieve_by_identifier` | `workitem_identifier` (e.g. `DEMO-12`) |
| `get_issue_comments` | `workitem_comment` / `list` | `project_id`, `workitem_id` |
| `get_issue_worklogs` | `work_log` / `list` | `project_id`, `workitem_id` |
| `get_total_worklogs` | `project` / `worklog_summary` | `project_id` |
| `list_cycle_issues` | `cycle` / `list_workitems` | `project_id`, `cycle_id` |
| `get_cycle` | `cycle` / `retrieve` | `project_id`, `cycle_id` |
| `list_module_issues` | `module` / `list_workitems` | `project_id`, `module_id` |
| `get_workspace_members` | `member` / `list_workspace` | Workspace configured in server |
| `list_cycles` | `cycle` / `list` | `project_id` |
| `list_modules` | `module` / `list` | `project_id` |
| `list_states` | `state` / `list` | `project_id` |
| `transfer_cycle_issues` | `cycle` / `transfer_workitems` | **MUTATION: excluded from all observation recipes** |

The last four read rows are declared Python legacy aliases. The other nine
captured names are absent from that Python registry; the table gives reviewed
replacement capabilities, not interchangeable parameter/response contracts.
The legacy [transfer implementation](https://github.com/makeplane/plane-mcp-server/blob/537d9760efb72c1fca4b5c3259aa0710bf60fefd/src/tools/cycles.ts)
POSTs a transfer. Python marks `transfer_workitems` as non-read. Never invoke it
to infer replanning. `update_issue` and all other writes are also excluded.
These exclusions are prose instructions; this plugin has no enforcing MCP proxy.

## Authentication

Delegate authentication to the user's configured server; never collect credentials.
The legacy [request helper](https://github.com/makeplane/plane-mcp-server/blob/537d9760efb72c1fca4b5c3259aa0710bf60fefd/src/common/request-helper.ts)
uses `PLANE_API_KEY` and optional `PLANE_API_HOST_URL` (default public API);
legacy tools use `PLANE_WORKSPACE_SLUG`. Python stdio configuration instead uses
`PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, and optional `PLANE_BASE_URL` as documented
in its pinned README. Hosted OAuth has a different setup. Do not substitute one
family's configuration for another. Report sanitized 401/403 status without raw
headers, tokens, host URLs, or response bodies.

## Response and pagination checks

Read the actual schema and returned envelope. Do not assume every tool returns
`results`/`next_cursor`, that points are numeric, or that cycle membership is an
issue field. Normalize UUIDs, state groups, timestamps, units and membership only
from observed fields. Missing data stays unknown. A cycle's current members or
end date do not prove its original plan or actual close time.

Use actual cursor/offset arguments with a finite request/time budget; stop on a
repeated cursor, malformed page, denied scope, or exhausted budget. State pages
read, truncation and observation time. Label first-page output sampled and never
report workspace-wide totals from incomplete visibility. Honor server retry
instructions on 429 within that budget; no universal rate limit is assumed.

## Drift disposition

The scheduled source watcher in `scripts/forge-api-surfaces.json` compares the
immutable May capture with latest official Python definitions. Its source-name
finding is expected during this documented legacy-to-Python transition; it is
not an installed-server outage. Keep the historical capture and watcher baseline
unchanged. Review future findings against pinned source and the connected schema;
do not recapture names automatically to turn an alert green.
