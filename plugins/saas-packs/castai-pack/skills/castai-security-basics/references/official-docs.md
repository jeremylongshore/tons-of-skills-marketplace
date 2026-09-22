# CAST AI Security Review: Official Sources

Consulted: 2026-09-13

- [Kubernetes permissions](https://docs.cast.ai/docs/kubernetes-permissions) — service-account permissions and feature-gated additions.
- [Cloud permissions](https://docs.cast.ai/docs/cloud-permissions) — provider access by integration purpose.
- [Hosted components](https://docs.cast.ai/docs/hosted-components) — components enabled by umbrella-chart mode.
- [API access](https://docs.cast.ai/docs/api-access) — organization-scoped keys, headers, regions, and lifecycle.
- [Kvisor](https://docs.cast.ai/docs/kvisor) — current warning that Kubernetes Security features are changing.
- [Configuring Kvisor features](https://docs.cast.ai/docs/sec-configuring-kvisor) — optional telemetry and associated cloud access.

## Boundary

Rendered installation and current enabled features are the audit subject. Documentation lists possible permissions but does not prove they are necessary in a specific cluster.
