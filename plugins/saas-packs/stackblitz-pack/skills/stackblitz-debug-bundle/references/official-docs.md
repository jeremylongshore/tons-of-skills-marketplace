# Official diagnostics references

Checked on 2026-09-10 against current first-party documentation.

- [WebContainer API reference](https://webcontainers.io/api) — observable lifecycle, event, process, filesystem, and preview contracts.
- [WebContainers troubleshooting](https://webcontainers.io/guides/troubleshooting) — actionable failure signatures and environment evidence.
- [Browser configuration](https://webcontainers.io/guides/browser-config) — browser-policy evidence worth recording coarsely.
- [Configuring headers](https://webcontainers.io/guides/configuring-headers) — isolation headers to normalize without collecting unrelated response headers.
- [API versioning and support](https://webcontainers.io/guides/api-support) — record both client version and hosted-runtime distinction.

These sources do not require collecting source files, secret values, cookies, or full terminal histories. Bundle schemas should minimize and explicitly label diagnostic data.
