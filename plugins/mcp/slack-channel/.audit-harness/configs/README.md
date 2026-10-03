# Shared lint configs — `@intentsolutions/audit-harness`

Canonical lint configuration that the five IEP repos vendor and extend, so a
markdownlint / yamllint / ruff / shellcheck rule lives in **one** place instead
of being re-typed (and silently drifting) in each repo.

| File | Tool | What it tunes |
|---|---|---|
| `markdownlint.yaml` | [markdownlint](https://github.com/DavidAnson/markdownlint) / markdownlint-cli2 | Lab-friendly Markdown: `MD013` (line-length) **off** — specs use long lines in tables and cross-references; inline HTML + non-H1 first line allowed. |
| `yamllint.yaml` | [yamllint](https://yamllint.readthedocs.io) | Workflow/manifest YAML: 2-space indent, `document-start` disabled, line-length relaxed to match the long `uses:`/`run:` lines in GitHub Actions. |
| `ruff.toml` | [ruff](https://docs.astral.sh/ruff/) | Python lint base: `B`+`E`+`F` ruleset, `line-length = 120`, mirroring the audit-harness repo's own `ruff.toml`. |
| `shellcheckrc` | [shellcheck](https://www.shellcheck.net) | Shell lint base: external-source follow + the small set of advisory codes the IEP scripts intentionally allow. |

## How a consuming repo uses these

The installer (`install.sh`) vendors this directory into a consuming repo at
**`.audit-harness/configs/`** alongside the scripts at `.audit-harness/scripts/`.
A consuming repo then **extends** the shared config from its own root config —
it never copies the rules inline.

### markdownlint

`.markdownlint.yaml` (or `.markdownlint-cli2.jsonc` → `"config": { "extends": ... }`)
at the repo root:

```yaml
# .markdownlint.yaml
extends: .audit-harness/configs/markdownlint.yaml
# repo-specific overrides go below — they win over the extended base
MD041: false
```

### yamllint

`.yamllint.yaml` at the repo root:

```yaml
# .yamllint.yaml
extends: .audit-harness/configs/yamllint.yaml
rules:
  # repo-specific overrides win over the extended base
  line-length:
    max: 140
```

### ruff

`ruff.toml` (or `pyproject.toml [tool.ruff]`) at the repo root:

```toml
# ruff.toml
extend = ".audit-harness/configs/ruff.toml"
# repo-specific overrides win over the extended base
line-length = 100
```

### shellcheck

`.shellcheckrc` at the repo root with a `source-path` line so shellcheck can find
the shared rc, then per-file `# shellcheck source=...` or the directives you need.
shellcheck does not have a first-class `extends`, so the consuming repo's
`.shellcheckrc` is the small superset: copy the `disable=`/`enable=`/`external-sources`
lines you want from `.audit-harness/configs/shellcheckrc` and add repo-specific ones.
The shared file is the reference shape; keep the codes in sync via PR review.

## Pinning

These files are hash-pinned in the audit-harness repo's `.harness-hash` via
`.harness-hash-extra-patterns` (`.audit-harness-configs/*`). A silent edit to a
shared lint rule is a policy change and must go through `audit-harness init`
(re-pin) + review — the same discipline that protects the deterministic scripts.

## Why a `configs/` dir vendored under `.audit-harness/`

The source-of-truth dir at the audit-harness repo root is `.audit-harness-configs/`
(so it does not collide with the consumer-side `.audit-harness/` install target).
The installer copies it to `.audit-harness/configs/` in the consumer, giving every
repo the same vendor path to point an `extends` at.
