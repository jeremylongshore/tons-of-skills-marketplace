# Owner routing runtime contract

## Registered tools

The MCP server registers lookup_service_owner, lookup_oncall, parse_codeowners,
lookup_recent_assignees, and lookup_recent_committers. Each returns a fixed level, source, base
confidence, and stale=false. Current handlers set team to undefined and do not call a network,
filesystem, GitHub, or service-management provider.

## Library-only helpers

buildRoutingRecommendation() and applyPrecedenceConfidence() exist in mcp/triage-server/lib.ts, but no
MCP tool invokes them. The recommendation helper can apply an override object passed by its caller and
otherwise filters for results with a team or assignee.

## Configuration boundary

config/routing-source-priority.json defines six policy levels and a 30-day staleness threshold. It
does not contain owner mappings. config/surface-repo-mapping.json currently contains empty repo arrays
and is not an ownership fallback map.
