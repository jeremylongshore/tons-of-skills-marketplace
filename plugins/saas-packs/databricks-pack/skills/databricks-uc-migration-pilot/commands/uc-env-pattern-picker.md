---
name: uc-env-pattern-picker
description: Recommend a dev/test/prod UC isolation pattern and emit a DAB target stub
aliases: [uc-env-picker, env-isolation]
---

# /uc-env-pattern-picker

Recommends one of four Unity Catalog environment-isolation patterns for the
**one-metastore-per-region-per-account** constraint, then emits a ready-to-paste
Databricks Asset Bundle (DAB) `target` stub for the choice.

## Usage

```
/uc-env-pattern-picker
```

## What it does

Asks three questions and maps the answers to a pattern (full detail, cost models,
and tradeoffs in `references/uc-environment-isolation-patterns.md`):

1. **Compliance** — must environments be *physically* isolated (separate billing /
   SSO / audit boundary), or is logical separation acceptable?
2. **Cost** — is cross-region data-egress cost acceptable for isolation?
3. **Lineage / BI** — does the team need a clean per-env lineage graph, or is a
   shared lineage graph tolerable?

Recommendation map:

| If… | Pattern | Friction / Isolation / Cost |
|---|---|---|
| Logical separation OK, cost-sensitive, shared lineage tolerable | **single-metastore-catalog-per-env** (`bronze_dev`/`bronze_prod`) | low / low / low |
| Need true metastore isolation, egress cost acceptable | **multi-region** | medium / high / high (egress) |
| Hard isolation required (billing/SSO/audit) | **multi-account** | high / highest / high |
| Want isolation with low friction and can ask the account team | **soft-quota-bump** (request the per-region limit be lifted) | low if granted / high / low |

## Output

- The recommended pattern with its one-line rationale and the tradeoff it accepts.
- A matching **DAB `target` stub** — for the default (catalog-per-env) pattern, an
  env-parameterized `databricks.yml` `targets:` block using `var.env` so
  `bronze_${var.env}` resolves per target. Copy it into your bundle.
