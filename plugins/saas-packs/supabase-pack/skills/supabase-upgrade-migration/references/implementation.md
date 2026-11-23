# Upgrade implementation review

Read the manifest, lockfile and actual installed versions before proposing a change.
Choose exact target versions using each package's release notes and runtime metadata;
JavaScript SDK, CLI, SSR helper and Python SDK have independent release histories.
Do not infer a fixed API version or compatible runtime from a major version alone.

- [JavaScript SDK releases](https://github.com/supabase/supabase-js/releases)
- [CLI releases](https://github.com/supabase/cli/releases)
- [Python SDK releases](https://github.com/supabase-community/supabase-py/releases)

Apply only the relevant ecosystem's upgrade with its existing package manager.
Preserve the prior source and lockfile for reviewed rollback. Review installation
scripts and do not apply remote database changes as a side effect of an SDK upgrade.

For generated types, follow the [guarded local-generation example](../SKILL.md#generate-types-without-truncating-the-previous-file).
Its temporary file and same-directory rename preserve the old artifact if the CLI
fails or emits nothing. This is not TypeScript validation: inspect the diff and run
the application's typecheck and scoped regression tests after generation.
