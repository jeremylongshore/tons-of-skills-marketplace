# Dependency Checker

Audit selected project dependencies with installed tools, normalize existing
reports and inventory declared license metadata. Failed or partial observations
stay incomplete rather than becoming an empty clean report.

## Installation and use

```text
/plugin install dependency-checker@claude-code-plugins-plus
/check-deps
```

The command shortcut is `/depc`. Select a project root and authorize any live
audit requests first. Package names and versions can be sent to configured
advisory services. The plugin does not install tools, generate lock files, apply
upgrades or run `audit fix`.

## Supported audit routes

| Selector | Required project inputs                                   | Installed executable            |
| -------- | --------------------------------------------------------- | ------------------------------- |
| npm      | package.json and package-lock.json or npm-shrinkwrap.json | npm                             |
| pip      | Explicit pinned requirements.txt                          | pip-audit                       |
| composer | composer.json and composer.lock                           | composer                        |
| bundler  | Gemfile and Gemfile.lock                                  | bundle-audit or bundler-audit   |
| cargo    | Cargo.toml and Cargo.lock                                 | cargo with the audit subcommand |

These are root-level routes, not a recursive workspace or dependency-closure
proof. Yarn/pnpm locks, Go modules, Poetry/Pipfile resolution, outdated-package
research and abandoned-project research are not implemented by the bundled
scanner. Exporting Python requirements is a separate operator action. Python
scanning disables dependency resolution and pip use; incomplete or skipped
packages do not count as verified absence of vulnerabilities.

## Reports

The scanner returns 0 for complete/no known findings in selected scope, 1 for
findings or review flags, and 2 for incomplete scanning or invalid usage. It emits
one JSON document with scope, completion, findings, errors, warnings and tool exit
codes when `--format json` is selected. `--severity` filters display only;
unknown severity remains visible and hidden findings still fail the gate.

The offline report formatter supports text, JSON, Markdown and CSV. Its default
exit 0 means a valid complete report, even with findings; use
`--fail-on-findings` for a finding gate. CSV exports finding rows and must be kept
with the JSON coverage record and process status. A filtered normalized report
cannot be reused to prove completeness because it omits findings.

The license checker inventories npm's installed tree and an explicitly selected
Python environment. Unknown/compound declarations and non-permissive categories
require review. Its result does not establish legal compatibility. It returns 2
for incomplete enumeration and 1 for review flags, including without `--strict`.
Python needs an existing absolute interpreter path and `piplicenses` available
there; project-level package-selection defaults are not applied.

Reports can contain private package names. Explicit output files are replaced
atomically with private permissions; terminal control bytes in human-readable
fields are escaped. This is not general secret redaction or a sandbox.

See the [skill workflow](skills/analyzing-dependencies/SKILL.md),
[CLI contracts](skills/analyzing-dependencies/scripts/README.md),
[upstream references](skills/analyzing-dependencies/references/README.md) and
[coverage-aware report template](skills/analyzing-dependencies/assets/report_template.md).

## Verification

Repository regression fixtures invoke the actual bundled CLIs with fake local
audit executables, covering all five routes, findings, native failures, missing
tools, timeouts, malformed output and contradictory counters. They do not
establish live advisory-service availability or a security certification.

```bash
python3 -m pytest -q tests/test_standalone_dependency_checker.py
```

## License

MIT. See [LICENSE](LICENSE).
