# penetration-tester test suite

Pytest-based unit tests for the v3.0.0 pack. Covers the shared `lib/` modules, all ten cluster 4–6 scripts, and representative paths in all fifteen cluster 1–3 scripts. This is script coverage, not an exhaustive branch or language-pattern coverage claim. Wired into the repo-level `python-tests` matrix job in `.github/workflows/validate-plugins.yml`; `test_*.py` files are auto-discovered without any per-pack workflow.

## Layout

```
tests/
├── conftest.py                              # shared fixtures
├── test_early_cluster_parsers.py             # offline HTTP/TLS fingerprints + source checks
├── test_lib_finding.py                      # Finding + Severity contract
├── test_lib_report.py                       # report.emit / exit_code
├── test_cluster4_dependency_analysis.py     # npm-audit + pip-audit + license + transitive
├── test_cluster5_engagement_governance.py   # authz + scope + record
├── test_cluster6_reporting.py               # compose + owasp + exec-summary
└── README.md                                # this file
```

## Running locally

From the pack root:

```bash
cd plugins/security/penetration-tester
python3 -m pytest tests/ -v
```

With coverage:

```bash
python3 -m pytest tests/ --cov=skills --cov=lib --cov-report=term-missing
```

From the repo root:

```bash
python3 -m pytest plugins/security/penetration-tester/tests/ -v
```

## What's covered

- **`lib/finding.py`** — every Severity classmethod (`from_cvss`, `from_npm_audit`, `from_bandit`), Finding fingerprint stability, to_dict/from_json round-trip, JSONL emit/load.
- **`lib/report.py`** — JSON/JSONL/Markdown emission, stdout fallback, exit-code thresholds.
- **Early clusters** — HSTS transport/policy boundaries, obsolete versus modern TLS, directory/debug/secret-response fingerprints and inspection bounds, plus SQL/command injection, deserialization and eval source checks with location, safe alternatives, language filtering and missing files. The new parser module refuses socket connections and subprocesses. Additional cases cover ordered/partial certificate blocks and OCSP text, CORS reflection and credential combinations, server/version disclosure, secret entropy and redaction, and the explicit path-limited MD5 exception. Existing method-probe and fail-closed suites exercise additional authorization and HTTP safety paths.
- **Cluster 4 (4 scripts)** — npm audit v1/v2 parsers, pip-audit record parser, license family classification, dep-graph trace_paths algorithm, project-type detection.
- **Cluster 5 (3 scripts)** — ROE field validation, time-window expiry, signer allowlist, target-in-scope checks (host / CIDR / wildcard), scope target classification, CIDR overlap, manifest SHA-256 + hash-mismatch detection, symlink + empty-file flagging.
- **Cluster 6 (3 scripts)** — finding normalization + required-field policy, OWASP classification (skill / CWE / keyword / override), risk-score composition + band interpretation, priority selection + effort/impact heuristics, stable summary rendering.

## What's NOT covered

- **Integration tests against live external tools.** The scripts wrap `npm audit`, `pip-audit`, `pipdeptree`, `npm ls`, `gpg`. Those external tools aren't invoked in unit tests; instead the parsers are tested with realistic fixture JSON.
- **Exhaustive cluster 1–3 behavior.** Early-cluster fixtures cover each script, including the existing method-probe suite, but do not establish live-server behavior, full certificate validation, or exhaustive language-pattern coverage.
- **End-to-end engagement workflow.** Each script tested standalone; the cluster 5 → cluster 1-4 → cluster 6 flow is covered indirectly via fixtures.

## Test data

- `sample_findings` fixture — 3 representative findings across critical/high/medium.
- `sample_roe_dict` / `sample_roe_path` — a complete valid ROE.
- `engagement_dir` — a full fake engagement directory with ROE + findings.
- `npm_audit_v1_output` / `npm_audit_v2_output` — realistic-shaped npm audit JSON.

All fixtures live in `conftest.py` and are auto-discovered by pytest.

## Bugs caught by writing this suite

Adding these tests immediately surfaced two real script bugs:

1. **`audit_npm.py` `_parse_v2`** — assumed `via[].source` was always iterable; npm v2 can emit a scalar (int or string). Fixed by normalizing to a list before iteration.
2. **`record_engagement.py` `DEFAULT_EXCLUDES`** — used `**/` glob syntax that `fnmatch` doesn't understand; the manifest file was being included in its own manifest. Fixed by using fnmatch-compatible patterns.

Both fixes shipped in this PR alongside the test suite.

## Convention

- One test class per script (`TestAuditNpm`, `TestCheckLicenses`, etc.).
- Each class imports the script via `_load_script` to keep module imports localized.
- Parametrize where input variation matters (severity bands, license classifications, target types).
- Fixtures live in `conftest.py`; never duplicate fixture data inside test files.
- Keep each test under ~20 lines; complex tests indicate the script itself needs refactoring.
