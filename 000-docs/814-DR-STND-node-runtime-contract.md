<!-- doc-class: record -->

# Repository Node.js Runtime Contract

Status: active

## Full-repository contract

Repository-level development and verification commands require Node.js
`>=22.12.0`. This floor is required by the Astro dependency used by the
`marketplace/` build. `.node-version` is the single source for the tested minimum, and
`scripts/check-node-version.mjs` is the dependency-free preflight used before
repository-level build, test, lint, typecheck, verification, development, and
quick-test paths.

The full-repository entry points are:

- `pnpm build` (includes the Astro marketplace build through the workspace)
- `pnpm test`, `pnpm typecheck`, `pnpm lint`, and `pnpm run verify`
- `./scripts/quick-test.sh`
- CI jobs that install the root workspace or build/generated-content surfaces
- `cd marketplace && npm run build`

These paths should use the `.node-version` runtime or an equivalent Node.js
22.12+ setup.

CI jobs that run repository-wide commands or build or install the marketplace
use the maintained Node 22 line. Using the moving LTS line in CI keeps security
patches current while the engine and preflight preserve the explicit `22.12.0`
compatibility floor.

Focused CI lanes may remain on Node 20 when they install only a filtered
package/tooling slice and do not build or install the marketplace:
`validate-plugins`'s validation-scripts, package-manager, CLI smoke, codeblock
syntax, CODEOWNERS, and document-governance checks; the CLI compatibility
matrix; and package-publish lanes. This is deliberate scope preservation, not
a second full-repository contract.

## Narrower compatibility matrices

The repository contains independently consumable packages and focused CI
jobs with lower runtime declarations. Those declarations remain intentional:

| Surface                                                             | Supported Node line | Boundary                                 |
| ------------------------------------------------------------------- | ------------------- | ---------------------------------------- |
| `packages/cli`                                                      | `>=18.0.0`          | Package-local CLI runtime/build contract |
| `packages/plugin-validator`                                         | `>=14.0.0`          | Package-local validator contract         |
| `plugins/mcp/a2a-client` and `plugins/mcp/databricks-workspace-mcp` | `>=20.0.0`          | Package-local MCP runtime contracts      |

Lowering the root engine or changing these package-local floors would be a
different compatibility decision. A package-local command can continue to
use its own declared floor when it does not enter the repository build or
verification path.

## Failure behavior

The preflight exits nonzero before any guarded repository command when the
active Node version is below `22.12.0`. Its message names both the actual
version and the required minimum, and points to `.node-version` for recovery.

Plain filtered dependency installation is intentionally not a guarded
repository command: the CLI compatibility matrix installs only the CLI slice
under its lower declared runtime. The root engine warning still exposes the
mismatch, and every command that can enter the marketplace build fails closed.
