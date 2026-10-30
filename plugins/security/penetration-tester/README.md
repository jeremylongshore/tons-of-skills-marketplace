# Penetration Tester Plugin

Security testing toolkit for web applications, dependencies, and source code.
The pack contains 25 narrow operators plus an orchestrator, and retains three
legacy CLI routes with separate report contracts. Start with the orchestrator
for authorization, scope and canonical report composition.

## What It Does

| Scanner | Target | What It Checks |
|---------|--------|----------------|
| `security_scanner.py` | Live URLs | Security headers, SSL/TLS, exposed endpoints, HTTP methods, CORS |
| `dependency_auditor.py` | Project dirs | Project-bound npm/pip advisory triage; explicit Python environment or pinned requirements |
| `code_security_scanner.py` | Codebases | Hardcoded secrets, SQL injection, command injection, insecure deserialization |

## Installation

```bash
/plugin install penetration-tester@claude-code-plugins-plus
```

## Setup

Optional setup installs dependencies as a separate, explicitly approved action.
The scanners never invoke this installer automatically:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/setup_pentest_env.sh
```

Or with a virtual environment:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/setup_pentest_env.sh --venv
```

Requires Python 3.9+. The setup script installs `requests`, `bandit`, and
`pip-audit`, then verifies each tool works.

## Quick Start

**Check security headers on a URL:**

```
> Check the security headers on https://example.com
```

**Audit project dependencies:**

```
> Audit the dependencies in this project for vulnerabilities
```

**Scan code for security issues:**

```
> Scan this codebase for hardcoded secrets and security issues
```

**Full security audit:**

```
> Run a full security audit on this project
```

## Scanners

Examples assume the plugin runtime supplies CLAUDE_PLUGIN_ROOT; for standalone
CLI use, supply the actual plugin installation path. Complete the approved ROE
and scope gates first. Legacy CLIs do not prompt for, or validate, an ROE themselves.

### security_scanner.py

HTTP security analysis for live web applications.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/security_scanner.py https://example.com
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/security_scanner.py https://example.com --checks headers,ssl
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/security_scanner.py https://example.com --output report.json
```

**Checks:**

- Security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options,
  Referrer-Policy, Permissions-Policy)
- SSL/TLS certificate validity and expiry
- Exposed endpoints (.git, .env, admin panels, server-status)
- Dangerous HTTP methods (PUT, DELETE, TRACE)
- CORS misconfigurations (wildcard, reflected origin)

### dependency_auditor.py

Unified dependency vulnerability scanner.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/dependency_auditor.py /path/to/project
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/dependency_auditor.py . --min-severity high
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/dependency_auditor.py . --scanners npm,pip --output findings.json
```

**Supports:**

- npm projects (via `npm audit`)
- Python projects (via `pip-audit`)
- Auto-detects project type from manifest files

Python dependency audits use pinned requirements.txt without pip dependency resolution, or
an explicitly designated environment. For example:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/dependency_auditor.py \
  /approved/project --scanners pip --python /approved/project/.venv/bin/python \
  --output legacy-python.json
```

The designated Python uses isolated mode; install the auditor into that approved
environment separately. No missing-tool installation or outdated-package fallback
is used as audit success. An unknown advisory severity remains unknown and requires triage.

### code_security_scanner.py

Static analysis for security vulnerabilities.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/code_security_scanner.py /path/to/code
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/code_security_scanner.py . --tools bandit,regex --severity high
python3 ${CLAUDE_PLUGIN_ROOT}/skills/performing-penetration-testing/scripts/code_security_scanner.py . --exclude "test_*,*_test.py"
```

**Detects:**

- Hardcoded secrets (API keys, AWS keys, passwords, tokens)
- SQL injection (string concatenation in queries)
- Command injection (os.system, subprocess with shell=True)
- Eval/exec usage
- Insecure deserialization (pickle, unsafe YAML loading)
- Weak cryptography (MD5, SHA1)
- Disabled SSL verification

## Output

Legacy scanners provide terminal reports and JSON via --output. Their v2 JSON
shapes differ from canonical v3 Finding streams; keep them separate unless a
validated conversion is explicitly performed. Code-match evidence is redacted.
Web risk scores are null/INCOMPLETE when a selected check fails. A method's
advertisement is informational, not proof of writes, XST or open proxying.

| Exit | Meaning |
| --- | --- |
| 0 | Selected analyses completed; no unfiltered HIGH/CRITICAL finding |
| 1 | A completed analysis produced a HIGH/CRITICAL finding |
| 2 | Missing, invalid, failed or unassessed evidence; no clean verdict |

Display filters cannot change the gate. Dependency reports retain moderate as
the v2 spelling and may show unknown severity; unknown severity is not a clean
assessment. Optional setup, signing, archives and active method experiments
require their separate explicit choices.

## Reference Documentation

The legacy background guides live under
`skills/performing-penetration-testing/references/`:

- **OWASP_TOP_10.md** -- Each OWASP Top 10 risk with scanner mapping and fix templates
- **SECURITY_HEADERS.md** -- HTTP header implementation for Express, Django, Nginx, Apache
- **REMEDIATION_PLAYBOOK.md** -- Copy-paste fix templates for common vulnerabilities

## Authorization and scope

Obtain the owner's approval and pass the structural authorization/scope checks
before scanning. Approve exact local repository and environment paths separately
from network scope. The command/orchestrator instructions supply this routing;
the legacy CLIs do not execute those gates or establish legal authorization.
Missing tools and incomplete evidence stay nonzero. No DoD/STIG, exploit or
certified chain-of-custody claim follows from these reports.

## Commands

- `/pentest` -- Full security testing workflow with authorization checks
- `/scan-headers` -- Quick security header check for a single URL

## Requirements

- Python 3.9+
- `requests` >= 2.31.0
- `bandit` >= 1.7.5 (optional, for code scanning)
- `pip-audit` with --strict/--no-deps/--disable-pip support (optional, for Python auditing)
- `npm` (optional, for JavaScript dependency auditing)

## Contributors

- [@duskfallcrew](https://github.com/duskfallcrew) -- Reported AV false positive from PHP payloads in docs (#300), prompting the v2.0.0 rebuild

## License

MIT License - See LICENSE file for details.
