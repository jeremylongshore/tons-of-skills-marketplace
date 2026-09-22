# Official troubleshooting references

Checked on 2026-09-10 against current first-party documentation.

- [WebContainers troubleshooting](https://webcontainers.io/guides/troubleshooting) — duplicate boot, cached header, memory, install, embed, and native-addon failure modes.
- [Browser configuration](https://webcontainers.io/guides/browser-config) — Service Worker, third-party storage, Brave, Chrome, and Edge configuration constraints.
- [WebContainers browser support](https://webcontainers.io/guides/browser-support) — supported and beta browser behavior.
- [Configuring headers](https://webcontainers.io/guides/configuring-headers) — valid isolation-header configurations.
- [WebContainer API reference](https://webcontainers.io/api) — error, port, server-ready, process exit, and lifecycle evidence.

Diagnose from the final served response and runtime events. Do not fix an isolation problem by broadly weakening security controls or blindly retrying dependency installation.
