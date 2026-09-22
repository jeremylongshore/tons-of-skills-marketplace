# Official integration references

Checked on 2026-09-10 against current first-party documentation and npm registry metadata.

- [WebContainer API reference](https://webcontainers.io/api) — `configureAPIKey` and `auth.init` must run before `boot`; auth status and boot options are defined here.
- [Commercial usage](https://webcontainers.io/enterprise) — production commercial use requires a license; prototypes and proofs of concept are treated separately.
- [Configuring headers](https://webcontainers.io/guides/configuring-headers) — supported COOP/COEP combinations and matching `coep` option.
- [WebContainers quickstart](https://webcontainers.io/guides/quickstart) — installation, single boot, secure deployment, mount, spawn, and preview sequence.
- [StackBlitz JavaScript SDK](https://developer.stackblitz.com/platform/api/javascript-sdk) — embed/open methods are separate from a custom WebContainer host.

Registry snapshot: `@webcontainer/api` latest `1.6.4`; `@stackblitz/sdk` latest `1.11.1`. Repository lockfiles and installed types remain implementation authority.
