# Audit and metadata references

Contract review: 2026-10-25. These upstream references explain native commands
and report formats, not live-service verification or permission to run them.

## pip-audit

JSON includes dependency vulns and skipped-package records. Requirements auditing uses --no-deps and --disable-pip to avoid implicit resolution/pip activity; keep skip coverage incomplete.

[Reviewed upstream source](https://github.com/pypa/pip-audit/tree/828e77a4d4aa6bee8d315681db6928771d951a7c)

## Bundler Audit

JSON has version, created_at and typed results. The wrapper uses check --format json --no-update, retaining insecure-source review outcomes.

[Reviewed upstream source](https://github.com/rubysec/bundler-audit/tree/831cdc92a029af6df828654133e407c81f90330b)

## Cargo Audit

Native vulnerability found/count/list must agree. The wrapper disables fetching with --no-fetch; database availability/freshness remains an audit prerequisite.

[Reviewed upstream source](https://github.com/rustsec/rustsec/tree/010f12aea2d7c663704ddd4c22d351ea5629e402)

## Composer Audit

Audit --locked reads the existing lock. Advisory findings, abandoned/filter/cooldown/ignored policy and unreachable sources are distinct outcomes. Current and historical native exit conventions differ.

[Reviewed upstream source](https://github.com/composer/composer/tree/fac7d53f689dee6254f110f3b0104dfa39e607a9)

## pip-licenses

Inventories installed environment metadata. --python selects an environment; pyproject.toml can supply package-selection/output defaults. The bundled invocation uses a private empty cwd and an explicit interpreter. System-package exclusions remain upstream defaults.

[Reviewed upstream source](https://github.com/raimon49/pip-licenses/tree/2a8cfbc292a7f9b8d3170995ea77aa12e2a37db4)

## npm Audit

[npm audit command](https://docs.npmjs.com/cli/commands/npm-audit/)
requires an existing lock and can send dependency metadata to configured registry
services. The wrapper requests all severities and does not invoke audit fix.
Native audit thresholds must not hide the report's unfiltered finding gate.

## License expressions

[SPDX expression syntax](https://spdx.github.io/spdx-spec/v2.3.1/SPDX-license-expressions/)
distinguishes identifiers, LicenseRef values, AND/OR/WITH operators and grouping.
The bundled inventory is not a full SPDX parser: only known exact IDs/names are
categorized. Preserve the original expression and flag unresolved declarations
for review rather than accepting a matching substring. Category labels and
legacy combination hints do not determine rights or legal compatibility.
