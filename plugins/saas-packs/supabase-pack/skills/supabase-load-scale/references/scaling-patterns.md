# Scaling Patterns

## Scale Application Workers Separately From the Database

A Kubernetes HPA scales your application, not Supabase compute or database connection
limits. Start with observed CPU/latency/backlog metrics and an explicit maximum.
This CPU-only example assumes the Deployment exists, requests CPU resources, and
has a working metrics server. A queue metric would require your own metrics adapter;
`supabase_queue_depth` is not a built-in Supabase metric.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: supabase-integration-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: supabase-integration
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

## HTTP Clients Are Not SQL Connection Pools

`createClient(projectUrl, publishableKey, options)` constructs the Supabase HTTP
client. Do not put it in a `generic-pool` SQL pool or call a nonexistent generic
`client.close()`. Reuse a browser client within its browser session; create
request-scoped cookie-aware clients for authenticated SSR. Never share a mutable
user session across unrelated server requests. Clean up Realtime channels with
`removeChannel()` when their subscription lifecycle ends.

For direct Postgres drivers, configure a bounded driver pool using the appropriate
Supavisor connection string and budget total connections across all app replicas.
Transaction pooling and prepared-statement compatibility depend on the driver and
workload; see [connection pooling](connection-pooling.md). Application autoscaling
must not silently multiply the database pool past its measured capacity.

[Supabase connection management](https://supabase.com/docs/guides/database/connecting-to-postgres)
