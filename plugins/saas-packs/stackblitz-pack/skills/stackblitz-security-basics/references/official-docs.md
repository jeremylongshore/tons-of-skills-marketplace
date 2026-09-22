# Official security-boundary references

Checked on 2026-09-10 against current first-party documentation.

- [WebContainers introduction](https://webcontainers.io/guides/introduction) — browser-local execution and StackBlitz's stated containment model.
- [WebContainer API reference](https://webcontainers.io/api) — auth, process, filesystem, export, preview, and lifecycle capabilities that cross trust boundaries.
- [Commercial usage](https://webcontainers.io/enterprise) — licensing and enterprise/private-package context.
- [Configuring headers](https://webcontainers.io/guides/configuring-headers) — cross-origin isolation requirements.
- [WebContainers troubleshooting](https://webcontainers.io/guides/troubleshooting) — embed requirements, network-adjacent browser constraints, native addons, and resource failures.
- [StackBlitz SDK](https://developer.stackblitz.com/platform/api/javascript-sdk) — public project sources and browser-memory persistence semantics.

Browser containment is not authorization to mount secrets, trust dependencies, accept arbitrary paths, trust preview messages, or publish exported user data. Derive controls from the actual host/runtime data flow.
