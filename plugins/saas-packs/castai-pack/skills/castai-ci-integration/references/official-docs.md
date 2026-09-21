# CAST AI CI Integration: Official Sources

Consulted: 2026-09-13

- [API access](https://docs.cast.ai/docs/api-access) — regional endpoints, `X-API-Key`, organization scoping, and key handling.
- [Connect with castctl](https://docs.cast.ai/docs/connect-with-castctl) — supported dry-run and non-interactive connection paths.
- [Autoscaler settings](https://docs.cast.ai/docs/autoscaler-settings) — policy endpoint and current CPU-limit semantics.
- [Workload Autoscaler configuration](https://docs.cast.ai/docs/workload-autoscaling-configuration) — policy, annotation, and automation controls.
- [Horizontal Pod Autoscaling](https://docs.cast.ai/docs/horizontal-pod-autoscaling) — native HPA ownership and configuration behavior.

## Boundary

These sources establish control semantics. The workflow must still derive exact commands, provider versions, and resource addresses from the pinned repository configuration instead of guessing them.
