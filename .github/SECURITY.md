# Security Policy

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

Use [GitHub Private Security Advisories](https://github.com/jeremylongshore/tons-of-skills-marketplace/security/advisories/new) to report vulnerabilities privately. Alternatively, email **jeremy@intentsolutions.io**.

We will acknowledge receipt within 24 hours and provide a remediation timeline within 72 hours.

## Scope

This policy covers:

- All plugins and skills in the `plugins/` directory (hundreds of plugins, thousands of skills — current counts are auto-generated in the [README](../README.md))
- The `ccpi` CLI tool (`@intentsolutionsio/ccpi` on npm)
- Cowork zip distribution packages
- CI/CD pipelines and GitHub Actions workflows
- The marketplace web application

## How We Protect Users

### Automated Validation

Every plugin submission runs through CI checks before merge:

- **Structure validation** — required files, valid JSON/YAML, script permissions
- **Secret scanning** — detects hardcoded API keys, tokens, credentials
- **Malicious pattern detection** — flags dangerous commands, suspicious URLs, obfuscated code, path traversal attempts
- **Dependency audit** — `npm audit` for MCP server plugins

### Code Review

All changes to `main` require:

- Pull request with passing CI checks
- Branch protection enforced — no direct pushes
- Maintainer review of all plugin code, commands, agents, and scripts

### Distribution Security

Plugin zip packages (cowork downloads) are built with:

- Path traversal rejection — archives cannot reference parent directories or absolute paths
- Sensitive file exclusion — `.env`, credentials, `.git/`, and similar files are stripped at build time
- Symlink prevention — archives do not follow or include symbolic links
- SHA-256 integrity checksums published alongside every package
- CI validation gate — packages are not published unless all checks pass

### Monitoring

- **GitHub vulnerability alerts and security updates** — routine version-update PRs are
  disabled; vulnerable npm dependencies receive grouped remediation PRs, while vulnerable
  GitHub Actions dependencies receive individual remediation PRs
- **CodeQL** — static analysis on push, PR, and weekly schedule
- **Secret scanning with push protection** — blocks commits containing detected secrets
- **Weekly full-history secret scan** — trufflehog runs on a Sunday schedule against the entire git history (`.github/workflows/secret-scan.yml`)

## Plugin Trust Levels

| Level         | Requirements                                                                                                                                                                                                                       | Recommendation                |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| **Community** | Automated CI passed                                                                                                                                                                                                                | Inspect before production use |
| **Verified**  | A maintainer completed the listing checklist in the [vetting playbook](../000-docs/699-DR-GUID-external-source-vetting-playbook.md) and vouches for the source's trust and quality at listing time — a trust record, not a control | Lower risk; still inspect     |
| **Featured**  | Editorial pick: A-grade at marketplace tier + the pack/flagship doc set                                                                                                                                                            | Recommended                   |

## External Plugin Sync — Supply-Chain Security

Some plugins are mirrored weekly from external repositories listed in `sources.yaml`
(via `scripts/sync-external.mjs` and the `sync-external.yml` workflow). Because those
upstreams are outside our control, the sync is defended in layers: content pinning with
drift quarantine (`sources.lock.json`), a deterministic REFUSE/CHALLENGE/FLAG security
scan, surface tiers by blast radius (`markdown-only` / `scripted` / `hooks-mcp`), the
curated freeze, and a mandatory human review gate on every sync PR.

- **Threat model** (assets, trust boundary, attack vectors, mitigations, residual risk):
  [000-docs/698-TQ-SECU-external-sync-threat-model.md](../000-docs/698-TQ-SECU-external-sync-threat-model.md)
- **Vetting playbook** (listing checklist, drift review, scan sign-off, tier policy):
  [000-docs/699-DR-GUID-external-source-vetting-playbook.md](../000-docs/699-DR-GUID-external-source-vetting-playbook.md)

Suspected compromise of a synced upstream is a vulnerability — report it privately per
"Reporting a Vulnerability" above.

## For Plugin Developers

- Never hardcode secrets — use environment variables
- Pin exact dependency versions in `package.json`
- Document all network calls and permissions in your README
- Run `python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/<category>/<your-plugin>/` before submitting (plus `./scripts/quick-test.sh` for a fast build/lint sanity check)
- See [CONTRIBUTING.md](CONTRIBUTING.md) for the full submission checklist

## Supported Versions

| Version           | Supported                    |
| ----------------- | ---------------------------- |
| Latest (`main`)   | Yes                          |
| Previous releases | Best-effort security patches |

---

**Last Updated:** September 2026
