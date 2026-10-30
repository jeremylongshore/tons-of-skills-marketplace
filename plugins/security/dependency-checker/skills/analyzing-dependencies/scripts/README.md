# Bundled CLI contracts

Python 3.10+ and the standard library run these scripts. Audit and inventory
executables must already be installed. Run commands from the selected project
root; locate scripts through the skill's resource directory.

| Script                         | Purpose                                               | Status                                                                             |
| ------------------------------ | ----------------------------------------------------- | ---------------------------------------------------------------------------------- |
| dependency_check.sh            | Bash shim invoking the Python scanner                 | 0 complete/no known findings; 1 findings/review; 2 incomplete/usage                |
| vulnerability_report_parser.py | Offline format normalization, or scanner with --scan  | Offline 0 valid complete report; 1 incomplete/error or --fail-on-findings; 2 usage |
| license_compliance_checker.py  | Declared metadata inventory                           | 0 complete/no automated flags; 1 review; 2 incomplete/usage                        |
| dependency_runtime.py          | Shared strict JSON, process capture and atomic output | Internal helper, no CLI                                                            |

## Scanner and formatter

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/dependency_check.sh" --tool npm --format json
python3 "${CLAUDE_SKILL_DIR}/scripts/vulnerability_report_parser.py" --input audit.json --format markdown
```

Scanner selectors: `npm`, `pip`, `composer`, `bundler`, `cargo`. Omission selects
supported root manifests. npm/Composer/Bundler/Cargo need an existing lock. Python
needs pinned requirements.txt and uses `--no-deps --disable-pip`; it neither
resolves transitive dependencies nor proves requirements closure.

Formats: text, json, markdown, csv. Shared flags: `--severity` (default low),
`--output`, `--verbose`, `--timeout` (default 30; greater than zero and at most
300 seconds). `--tool` requires scanning. Offline input requires `--input`;
`--fail-on-findings` adds an offline finding gate. The scanner always gates on
unfiltered findings and review flags. Missing severity stays UNKNOWN and visible.

Accepted offline envelopes include npm modern/legacy, pip-audit current/legacy,
legacy Safety arrays, Composer, Bundler, Cargo, generic vulnerabilities arrays and
complete unfiltered normalized-v1 reports. Unsupported/error bodies, invalid
counts, duplicate keys, non-finite numbers and concatenated JSON fail parsing.
Filtered normalized-v1 reports are incomplete inputs because omitted rows cannot
be recovered. The formatter does not contact advisory services.

JSON is one document. Capture process status separately; CSV only represents
finding rows. Retain JSON scope/errors/warnings alongside CSV. The scanner
records native tool exit codes but does not automatically collect tool versions
or database freshness; record those separately for a reproducible audit.

## License inventory

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/license_compliance_checker.py" --format json --python /absolute/path/to/project/.venv/bin/python
```

Flags: `--format text|json`, `--output`, `--python`, `--timeout`, `--strict`,
`--verbose`. npm uses `npm ls --json --all --long`; missing root dependencies,
problems and nonzero enumeration are incomplete. Python invokes selected
`python -m piplicenses --python selected --format=json` from an empty private
working directory to avoid project configuration hiding inventory. It describes
the selected installed environment, not the requirements closure. Standard
pip-licenses system-package exclusions still apply. `--strict` also presents
review warnings as issues; review warnings already return 1 without it.

## Process and output boundaries

Tools run with stdin closed, no shell interpolation, a per-tool deadline and
private temporary stdout/stderr capture. JSON inputs/output capture are bounded
to 32 MiB; stderr capture to 1 MiB, checked while polling and at completion. These
checks do not provide an OS sandbox or hard instantaneous disk quota. Only a
still-running process group created by the invocation is terminated on failure.
Installed tools and their configuration must be trusted. No automatic install,
lock generation, database update or fix is performed; advisory requests remain
tool/configuration dependent.

Native error bodies are not printed. Human-readable fields escape terminal
control bytes; this is not general secret redaction. Reports may still contain
private names and advisory text. Explicit output is an atomic 0600 replacement;
symlink destinations are rejected. A missing parent directory is an output
failure, not automatically created. File inputs are parsed locally and never
executed. The Bash shim needs an available Python interpreter to start.
