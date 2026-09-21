# Anima Skill Pack

> Validated Anima workflows for authorized Figma, website, and prompt-to-code operations (18 skills)

These skills use `@animaapp/anima-sdk` 0.27.0 and its current backend contract.
They cover Figma generation, public website conversion, early-preview prompt
generation, secure deployment, reliability, and governed output review. Current
framework targets are React and HTML; Vue is not advertised by this SDK version.

## Installation

```bash
/plugin install anima-pack@claude-code-plugins-plus
```

## Skills Included

### Standard Skills (S01-S12)

| Skill | What It Does |
|-------|-------------|
| `anima-install-auth` | Install `@animaapp/anima-sdk`, configure Anima + Figma tokens |
| `anima-hello-world` | Generate reviewed React or HTML output from an approved Figma node |
| `anima-local-dev-loop` | Compare supported presets in a bounded local review loop |
| `anima-sdk-patterns` | Build a typed client, output normalizer, and content-addressed cache |
| `anima-core-workflow-a` | Automated Figma-to-React pipeline with component scanning |
| `anima-core-workflow-b` | Convert an authorized website or prompt, then govern customization |
| `anima-common-errors` | Diagnose auth, node, generation, and output quality errors |
| `anima-debug-bundle` | Diagnostic bundle with SDK version and Figma access status |
| `anima-rate-limits` | Honor structured Figma rate-limit callbacks and bounded retry budgets |
| `anima-security-basics` | Token scope restriction, server-side enforcement, secret manager |
| `anima-prod-checklist` | Production readiness validation for design-to-code pipelines |
| `anima-upgrade-migration` | SDK upgrades, manual plugin to automated SDK migration |

### Pro Skills (P13-P18)

| Skill | What It Does |
|-------|-------------|
| `anima-ci-integration` | GitHub Actions scheduled design sync with auto-PR creation |
| `anima-deploy-integration` | Deploy SDK as Express/Vercel/Cloud Run service |
| `anima-webhooks-events` | Figma Webhooks v2 triggering auto-generation on design change |
| `anima-performance-tuning` | File-based cache, incremental generation, output optimization |
| `anima-cost-tuning` | Usage tracking, smart generation policy, cache hit reporting |
| `anima-reference-architecture` | Full design-to-code pipeline architecture with project structure |

## Key Concepts

- **Current SDK** — Examples follow the public 0.27.0 implementation and documentation
- **Server-side only** — SDK runs on backend; never ship tokens to browser
- **Least privilege** — Figma access uses current granular scopes and approved source allowlists
- **Framework support** — React or HTML with `plain_css`, Tailwind, or inline styles
- **Review boundary** — Generated output is quarantined until path, dependency, security, build, and visual checks pass

## License

MIT
