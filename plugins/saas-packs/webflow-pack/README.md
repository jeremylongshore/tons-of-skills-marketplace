# Webflow Skill Pack

> 24 verified Claude Code workflows for Webflow Data API v2, Webflow Cloud, CLI, CMS, webhooks, security, migration, and production operations.

The pack is read-first and approval-gated. It verifies the target repository, installed SDK or CLI version, token type, scopes, environment, and resource IDs before proposing changes. Live content publication, destructive operations, token revocation, webhook registration, and production deployments remain separate approval boundaries.

## Installation

```bash
/plugin install webflow-pack@claude-code-plugins-plus
```

## Operator Workflows

| Area | Skills |
|---|---|
| Bootstrap | `webflow-install-auth`, `webflow-hello-world`, `webflow-local-dev-loop`, `webflow-sdk-patterns` |
| Content and APIs | `webflow-core-workflow-a`, `webflow-core-workflow-b`, `webflow-webhooks-events` |
| Reliability | `webflow-common-errors`, `webflow-debug-bundle`, `webflow-rate-limits`, `webflow-observability`, `webflow-incident-runbook` |
| Delivery | `webflow-ci-integration`, `webflow-deploy-integration`, `webflow-prod-checklist`, `webflow-multi-env-setup` |
| Governance | `webflow-security-basics`, `webflow-data-handling`, `webflow-enterprise-rbac`, `webflow-cost-tuning` |
| Architecture and change | `webflow-reference-architecture`, `webflow-performance-tuning`, `webflow-upgrade-migration`, `webflow-migration-deep-dive` |

## Current Contracts

- Data API v2 is the default API surface.
- Use a site token for controlled single-site work, a workspace token only for supported workspace/read use cases, and OAuth for user-authorized applications.
- CMS staged and live content are distinct. Saving, publishing, unpublishing, archiving, deleting, and site-wide publishing are different operations.
- Content Delivery serves documented cached live-item reads. Cache misses and bypasses reach origin and count against the active plan limit.
- API-created webhooks can be signature-verified; dashboard-created webhooks do not include the required signature headers.
- Webflow CLI 2.x requires Node.js 22.13.0 or newer. The current `apps` management surface uses the CLI `next` channel, so CI must pin an exact version.

Every skill includes a dated `references/official-docs.md` file. At execution time, the live official endpoint page and the target project's installed types remain authoritative.

## Quality Contract

All 24 skills must pass the repository's marketplace validator at Grade A with no Tier-2 production findings. The pack contract also rejects the stale shortcuts removed by this remediation: automatic production publication, universal bulk-size claims, floating CLI versions in CI, fabricated webhook secrets, and fixed pricing claims.

## Official References

- [Webflow developer documentation](https://developers.webflow.com/)
- [Data API v2 index](https://developers.webflow.com/data/v2.0.0/llms.txt)
- [Webflow CLI](https://developers.webflow.com/cli/llms.txt)
- [Webflow MCP and AI tooling](https://developers.webflow.com/mcp/llms.txt)

## License

MIT
