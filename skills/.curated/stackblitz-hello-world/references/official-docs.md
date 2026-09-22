# Official smoke-test references

Checked on 2026-09-10 against current first-party documentation.

- [WebContainers quickstart](https://webcontainers.io/guides/quickstart) — supported minimal order: boot once, mount, spawn/install, observe exit, start, then consume `server-ready`.
- [WebContainer API reference](https://webcontainers.io/api) — current signatures for `boot`, `mount`, `spawn`, `on`, processes, and `teardown`.
- [Running processes](https://webcontainers.io/guides/running-processes) — process streams and runtime events.
- [Working with the filesystem](https://webcontainers.io/guides/working-with-the-file-system.html) — `FileSystemTree` and initial bulk mount model.
- [Configuring headers](https://webcontainers.io/guides/configuring-headers) — cross-origin isolation requirements.

Use installed `@webcontainer/api` types for the pinned dependency. Never construct the dynamic preview URL or assume that a successful boot implies a successful process.
