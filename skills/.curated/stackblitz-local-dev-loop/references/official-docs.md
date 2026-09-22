# Official local-test references

Checked on 2026-09-10 against current first-party documentation.

- [WebContainers browser support](https://webcontainers.io/guides/browser-support) — Chromium support and beta/constraint notes for other browsers.
- [Browser configuration](https://webcontainers.io/guides/browser-config) — Service Worker, storage, and browser-setting failure modes.
- [Configuring headers](https://webcontainers.io/guides/configuring-headers) — required development and deployment headers.
- [Troubleshooting](https://webcontainers.io/guides/troubleshooting) — HMR duplicate-boot, cached-header, memory, and native-addon evidence.
- [WebContainer API reference](https://webcontainers.io/api) — lifecycle and event contracts to assert in browser tests.

Real runtime behavior needs a supported browser context. DOM simulators remain suitable for pure state and `FileSystemTree` transformations only.
