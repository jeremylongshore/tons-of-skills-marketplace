# Usage access, units and completeness

CoreWeave documents managed Grafana access for admin/metrics/write groups, but an empty query can also indicate filters, missing instrumentation or a wrong datasource. Record the actual error, metric metadata, units and scope before choosing a remedy.

Mission Control MCP exposes `coreweave_billing_get_focus_usage`. It returns usage quantities, not dollars. Use explicit timestamps (at most the documented 90-day range), follow every page token with the same scope, and retain `data_as_of`. Consumed and pricing quantities have distinct meanings; do not join differently grouped exports and double-count them.

For telemetry, `billing:instance:total` is an instance count. Establish samples/step and GPUs per observed instance before deriving GPU-hours. Missing samples do not count as zero. No `billing_gpu` metric or reservation-label key is assumed. A partial month is not automatically a full 30-day input.

Sources: [usage guidance](https://docs.coreweave.com/observability/usage-monitoring), [MCP tool contract](https://docs.coreweave.com/observability/mission-control-mcp/reference/tools).
