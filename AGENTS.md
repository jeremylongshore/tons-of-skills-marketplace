# Repository Guidelines

## Project Structure

This is the Tons of Skills Claude Code plugin marketplace. Author plugins under `plugins/<category>/<plugin-name>/`; a plugin commonly contains `skills/`, `commands/`, `.claude-plugin/plugin.json`, and a README. The editable catalog is `.claude-plugin/marketplace.extended.json`; its `marketplace.json`, generated plugin `package.json` files, and the README table of contents are derived. Shared tooling lives in `scripts/`, workspace packages in `packages/`, Python regression tests in `tests/`, and the Astro site in `marketplace/`.

## Build, Test, and Development

Use Node 22.12+ and pnpm 9.15.9+ for repository-level commands; `.node-version` records the tested Node floor. `marketplace/` deliberately uses npm. Independently consumable packages and focused CI jobs may retain their own lower Node floors when they do not enter the full-repository or marketplace build path; see `000-docs/814-DR-STND-node-runtime-contract.md`.

```bash
pnpm install
./scripts/quick-test.sh                 # fast repository sanity check
pnpm test && pnpm typecheck && pnpm lint
pnpm run verify                         # CI-equivalent verification pipeline
pnpm run sync-marketplace               # regenerate catalog-derived files
cd marketplace && npm run dev           # local Astro site, port 4321
cd marketplace && npx playwright test   # website end-to-end tests
```

Do not hand-edit generated catalog artifacts. Run `pnpm run sync-marketplace` before committing catalog or plugin changes. Validate skill metadata with `python3 scripts/validate-skills-schema.py --marketplace --verbose`; use `python3 scripts/validate-unicode-hygiene.py` for changed skill content.

## Style and Naming

Follow the existing file’s style; use Prettier for JavaScript, TypeScript, JSON, YAML, and Markdown (`pnpm run format:check`) and ESLint (`pnpm lint`) for code. Use two-space indentation in JS/TS and JSON. Name plugin folders lowercase kebab-case (for example, `plugins/mcp/example-plugin`) and skills as `skills/<skill-name>/SKILL.md`. Keep frontmatter compliant with the schema validator rather than inventing local variants.

## Tests

Add or update focused tests beside the affected package or in `tests/`; Python tests use `test_*.py` and TypeScript tests commonly use `*.test.ts`. Run the narrowest relevant test first, then the commands above. Changes to validators, schemas, or catalog generation require their targeted regression suite plus the marketplace schema validation.

## Commits and Pull Requests

Use Conventional Commit-style subjects visible in history, such as `fix(ci): harden validation` or `docs(contributing): clarify workflow`. Keep each commit scoped. PRs should explain the user-facing change, link the beads issue, include screenshots for visual site changes, and include regenerated derived files when applicable. Use `bd` for task tracking: run `bd ready`, claim the issue, and close it when complete. Before finishing, commit, pull/rebase, run `bd sync`, push, and confirm `git status` is up to date.

## Merge gates (do not weaken)

Required branch-protection contexts on `main`: **`ci-required`**, **`gitleaks`**, **`skill-conform`**.

- `skill-conform` is a **separate** always-report workflow (`audit-harness conform --strict`). Never add it (or any path-scoped / provider-dependent job) to `ci-required`'s `needs:`.
- Behavioral skill eval (`skill-eval-advisory.yml`) is **advisory only** until explicitly graduated.
- Full gate architecture, validator SSoT rules, and non-negotiables: see `CLAUDE.md`.
- Which document owns which fact class: blueprint `000-docs/727` § 11 (the authority map),
  indexed publicly by `STANDARDS.md § Canonical documents`. Point at owners; don't restate.
