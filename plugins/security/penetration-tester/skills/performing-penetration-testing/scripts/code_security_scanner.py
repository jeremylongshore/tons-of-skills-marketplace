"""
Static analysis security scanner combining Bandit and custom regex pattern detection.

Scans source code for common security vulnerabilities including hardcoded secrets,
SQL injection, command injection, insecure deserialization, and weak cryptography.

Usage:
    python3 code_security_scanner.py /path/to/code [options]

Options:
    --tools bandit,regex    Comma-separated list of scan engines (default: both)
    --output findings.json  Write JSON report to file
    --severity low          Minimum severity threshold (critical, high, medium, low)
    --exclude "test_*"      Comma-separated glob patterns to exclude
    --verbose               Print detailed progress information

Exit codes:
    0 - No critical or high severity findings
    1 - Critical or high severity findings detected
    2 - Scanner error (missing tools, invalid arguments, etc.)
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEVERITY_ORDER: dict[str, int] = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

SCANNABLE_EXTENSIONS: set[str] = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".rb",
    ".go",
    ".php",
    ".sh",
}

SKIP_DIRS: set[str] = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
}

BANDIT_TIMEOUT_SECONDS: int = 120

# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# Each entry: (compiled_pattern, category, severity, confidence, title, remediation, cwe)

_HARDCODED_SECRET_PATTERNS: list[tuple[re.Pattern[str], str, str, str, str, str, str | None]] = [
    (
        re.compile(r"""api[_\-]?key\s*[=:]\s*["'][A-Za-z0-9]{20,}""", re.IGNORECASE),
        "hardcoded-secret",
        "high",
        "medium",
        "Hardcoded API key detected",
        "Move API keys to environment variables or a secrets manager.",
        "CWE-798",
    ),
    (
        re.compile(r"""AKIA[0-9A-Z]{16}"""),
        "hardcoded-secret",
        "critical",
        "high",
        "AWS Access Key ID detected",
        "Rotate the exposed key immediately and use IAM roles or environment variables.",
        "CWE-798",
    ),
    (
        re.compile(r"""password\s*[=:]\s*["'](?!["']$)(?!\s*$)(?!<%=)(?!\$\{)(?!\{\{)[^"']+["']""", re.IGNORECASE),
        "hardcoded-secret",
        "high",
        "medium",
        "Hardcoded password detected",
        "Use environment variables or a secrets manager instead of hardcoded passwords.",
        "CWE-798",
    ),
    (
        re.compile(r"""-----BEGIN\s+(?:RSA\s+|EC\s+|DSA\s+)?PRIVATE\s+KEY-----"""),
        "hardcoded-secret",
        "critical",
        "high",
        "Private key embedded in source code",
        "Remove the private key from source and store it in a secure vault.",
        "CWE-321",
    ),
    (
        re.compile(
            r"""(?:secret|token|bearer)\s*[=:]\s*["'][A-Za-z0-9+/=]{20,}""",
            re.IGNORECASE,
        ),
        "hardcoded-secret",
        "high",
        "medium",
        "Hardcoded secret or token detected",
        "Store secrets in environment variables or a dedicated secrets manager.",
        "CWE-798",
    ),
]

_SQL_INJECTION_PATTERNS: list[tuple[re.Pattern[str], str, str, str, str, str, str | None]] = [
    (
        re.compile(
            r"""(?:execute|cursor|query)\s*\(\s*f["'].*(?:%s|%d|\{)""",
            re.IGNORECASE,
        ),
        "sql-injection",
        "high",
        "high",
        "Potential SQL injection via string formatting",
        "Use parameterized queries or prepared statements instead of string formatting.",
        "CWE-89",
    ),
    (
        re.compile(r"""["']SELECT\s+.*["']\s*\+\s*""", re.IGNORECASE),
        "sql-injection",
        "high",
        "medium",
        "SQL query built with string concatenation (SELECT)",
        "Use parameterized queries instead of string concatenation.",
        "CWE-89",
    ),
    (
        re.compile(r"""["']INSERT\s+.*["']\s*\+\s*""", re.IGNORECASE),
        "sql-injection",
        "high",
        "medium",
        "SQL query built with string concatenation (INSERT)",
        "Use parameterized queries instead of string concatenation.",
        "CWE-89",
    ),
]

_COMMAND_INJECTION_PATTERNS: list[tuple[re.Pattern[str], str, str, str, str, str, str | None]] = [
    (
        re.compile(r"""os\.system\("""),
        "command-injection",
        "high",
        "high",
        "Use of os.system() allows shell command injection",
        "Use subprocess.run() with a list of arguments and shell=False.",
        "CWE-78",
    ),
    (
        re.compile(r"""subprocess\.(?:call|run|Popen)\(.*shell\s*=\s*True"""),
        "command-injection",
        "high",
        "high",
        "Subprocess call with shell=True enables command injection",
        "Pass commands as a list with shell=False instead of shell=True.",
        "CWE-78",
    ),
    (
        re.compile(r"""\beval\("""),
        "command-injection",
        "medium",
        "medium",
        "Use of eval() can execute arbitrary code",
        "Avoid eval(). Use ast.literal_eval() for data parsing or refactor logic.",
        "CWE-95",
    ),
    (
        re.compile(r"""\bexec\("""),
        "command-injection",
        "medium",
        "medium",
        "Use of exec() can execute arbitrary code",
        "Avoid exec(). Refactor to use safer alternatives.",
        "CWE-95",
    ),
]

_DESERIALIZATION_PATTERNS: list[tuple[re.Pattern[str], str, str, str, str, str, str | None]] = [
    (
        re.compile(r"""pickle\.loads?\("""),
        "insecure-deserialization",
        "high",
        "high",
        "Insecure deserialization with pickle",
        "Avoid pickle for untrusted data. Use JSON or a safe serialization format.",
        "CWE-502",
    ),
    (
        re.compile(r"""yaml\.load\((?!.*Loader\s*=\s*(?:Safe|Base)Loader)"""),
        "insecure-deserialization",
        "high",
        "high",
        "Unsafe YAML loading without SafeLoader",
        "Use yaml.safe_load() or pass Loader=SafeLoader to yaml.load().",
        "CWE-502",
    ),
    (
        re.compile(r"""marshal\.loads?\("""),
        "insecure-deserialization",
        "high",
        "medium",
        "Insecure deserialization with marshal",
        "Avoid marshal for untrusted data. Use JSON or a safe serialization format.",
        "CWE-502",
    ),
]

_CRYPTO_NETWORK_PATTERNS: list[tuple[re.Pattern[str], str, str, str, str, str, str | None]] = [
    (
        re.compile(r"""verify\s*=\s*False"""),
        "insecure-transport",
        "medium",
        "high",
        "SSL/TLS certificate verification disabled",
        "Enable certificate verification. Set verify=True or provide a CA bundle.",
        "CWE-295",
    ),
    (
        re.compile(r"""\bMD5\b|\.md5\(""", re.IGNORECASE),
        "weak-crypto",
        "medium",
        "medium",
        "Use of weak MD5 hashing algorithm",
        "Use SHA-256 or stronger hashing. For passwords, use bcrypt or Argon2.",
        "CWE-328",
    ),
    (
        re.compile(r"""\bSHA1\b|\.sha1\(""", re.IGNORECASE),
        "weak-crypto",
        "medium",
        "medium",
        "Use of weak SHA-1 hashing algorithm",
        "Use SHA-256 or stronger hashing. For passwords, use bcrypt or Argon2.",
        "CWE-328",
    ),
    (
        re.compile(r"""http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])"""),
        "insecure-transport",
        "medium",
        "low",
        "Insecure HTTP URL (not HTTPS)",
        "Use HTTPS for all external communications.",
        "CWE-319",
    ),
]

ALL_REGEX_PATTERNS = (
    _HARDCODED_SECRET_PATTERNS
    + _SQL_INJECTION_PATTERNS
    + _COMMAND_INJECTION_PATTERNS
    + _DESERIALIZATION_PATTERNS
    + _CRYPTO_NETWORK_PATTERNS
)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _log(message: str, verbose: bool = True) -> None:
    """Print a progress message to stderr."""
    if verbose:
        print(f"[scanner] {message}", file=sys.stderr)


def _is_binary_file(filepath: Path) -> bool:
    """Return True if file appears to be binary (contains null bytes in first 1KB)."""
    try:
        with open(filepath, "rb") as fh:
            chunk = fh.read(1024)
            return b"\x00" in chunk
    except OSError as exc:
        raise ScanIncomplete("Selected source file could not be inspected: " + type(exc).__name__) from exc


def _should_exclude(filepath: Path, exclude_patterns: list[str] | None) -> bool:
    """Check if a file matches any exclusion glob pattern."""
    if not exclude_patterns:
        return False
    name = filepath.name
    rel = str(filepath)
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel, pattern):
            return True
    return False


def _severity_at_or_above(severity: str, threshold: str) -> bool:
    """Return True if severity meets or exceeds the threshold."""
    return SEVERITY_ORDER.get(severity, 99) <= SEVERITY_ORDER.get(threshold, 99)


def _normalize_bandit_severity(raw: str) -> str:
    """Map Bandit severity strings to our canonical levels."""
    mapping = {
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low",
        "UNDEFINED": "low",
    }
    return mapping.get(raw.upper(), "low")


def _normalize_bandit_confidence(raw: str) -> str:
    """Map Bandit confidence strings to canonical levels."""
    return raw.lower() if raw.lower() in ("high", "medium", "low") else "low"


# ---------------------------------------------------------------------------
# Bandit scanning
# ---------------------------------------------------------------------------


class ScanIncomplete(Exception):
    """A selected analysis did not produce trustworthy complete evidence."""


def _safe_context(line: str) -> str:
    # Suppress the whole source line: a second finding on that same line must
    # not accidentally reveal the credential redacted in the first finding.
    if any(category == "hardcoded-secret" and pattern.search(line) for pattern, category, *_ in ALL_REGEX_PATTERNS):
        return "[REDACTED: credential-like source line]"
    return line.strip()[:200]


def _redacted_finding(finding: dict) -> dict:
    result = dict(finding)
    result["detail"] = _safe_context(str(result.get("detail", "")))
    if (
        result.get("category") in {"hardcoded-secret", "B105", "B106", "B107"}
        or result.get("cwe") in {"CWE-259", "CWE-798"}
        or "hardcoded" in str(result.get("title", "")).lower()
    ):
        result["detail"] = "[REDACTED: credential-like evidence]"
    return result


def run_bandit_scan(
    directory: Path,
    exclude_patterns: list[str] | None = None,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """
    Run Bandit static analysis on a directory and return structured findings.

    Missing, failed or malformed selected-tool evidence is incomplete. No
    scanner is installed automatically and raw tool output is never logged.
    """
    cmd: list[str] = ["bandit", "-r", str(directory), "-f", "json", "-q"]

    if exclude_patterns:
        # Bandit's -x flag accepts comma-separated paths/globs
        cmd.extend(["-x", ",".join(exclude_patterns)])

    _log(f"Running bandit on {directory} ...", verbose)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=BANDIT_TIMEOUT_SECONDS,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        raise ScanIncomplete("Selected Bandit analysis unavailable or failed: " + type(exc).__name__) from exc

    # Bandit returns exit code 1 when it finds issues, which is expected.
    if result.returncode not in (0, 1):
        raise ScanIncomplete("Selected Bandit analysis returned an unsupported exit status")
    stdout = result.stdout.strip()
    if not stdout:
        raise ScanIncomplete("Selected Bandit analysis produced no structured result")

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ScanIncomplete("Selected Bandit result was not valid JSON") from exc

    if not isinstance(data, dict) or not isinstance(data.get("results"), list) or data.get("errors"):
        raise ScanIncomplete("Selected Bandit result was incomplete or lacked its results list")

    findings: list[dict[str, Any]] = []
    for issue in data.get("results", []):
        if (
            not isinstance(issue, dict)
            or issue.get("issue_severity") not in ("LOW", "MEDIUM", "HIGH")
            or not isinstance(issue.get("filename"), str)
            or not issue["filename"]
            or type(issue.get("line_number")) is not int
            or issue["line_number"] < 1
            or not isinstance(issue.get("issue_text"), str)
            or not isinstance(issue.get("issue_cwe", {}), dict)
        ):
            raise ScanIncomplete("Selected Bandit result contained a malformed issue")
        credential = (
            issue.get("test_id") in {"B105", "B106", "B107"} or "hardcoded" in str(issue.get("test_name", "")).lower()
        )
        findings.append(
            {
                "tool": "bandit",
                "file": str(Path(issue.get("filename", "unknown")).resolve()),
                "line": issue.get("line_number", 0),
                "severity": _normalize_bandit_severity(issue.get("issue_severity", "LOW")),
                "confidence": _normalize_bandit_confidence(issue.get("issue_confidence", "LOW")),
                "category": issue.get("test_id", "unknown"),
                "title": issue.get("test_name", "Unknown issue"),
                "detail": "[REDACTED: credential-like evidence]" if credential else _safe_context(issue["issue_text"]),
                "remediation": "",
                "cwe": (f"CWE-{issue['issue_cwe']['id']}" if issue.get("issue_cwe", {}).get("id") else None),
            }
        )

    _log(f"Bandit found {len(findings)} issue(s).", verbose)
    return findings


# ---------------------------------------------------------------------------
# Regex-based scanning
# ---------------------------------------------------------------------------


def run_regex_scan(
    directory: Path,
    exclude_patterns: list[str] | None = None,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """
    Walk the directory tree and scan source files against compiled regex
    patterns for common security vulnerabilities.

    Skips binary files, hidden/vendored directories, and files matching
    exclusion patterns.
    """
    findings: list[dict[str, Any]] = []
    files_scanned = 0

    _log(f"Running regex scan on {directory} ...", verbose)

    def walk_error(exc):
        raise ScanIncomplete("Selected source directory could not be inspected: " + type(exc).__name__)

    for root, dirs, files in os.walk(directory, onerror=walk_error):
        # Prune directories we never want to enter (modifying dirs in-place)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

        for filename in files:
            filepath = Path(root) / filename

            # Extension filter
            if filepath.suffix.lower() not in SCANNABLE_EXTENSIONS:
                continue

            # Exclusion filter
            rel_path = filepath.relative_to(directory)
            if _should_exclude(rel_path, exclude_patterns):
                continue

            if filepath.is_symlink():
                raise ScanIncomplete("Selected source includes a symbolic link; no external content was read")

            # Skip binary files
            if _is_binary_file(filepath):
                continue

            try:
                lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError as exc:
                raise ScanIncomplete("Selected source could not be read: " + type(exc).__name__) from exc

            files_scanned += 1
            is_test_file = _is_test_path(str(rel_path))

            for line_num, line in enumerate(lines, start=1):
                stripped = line.strip()
                # Skip comments (basic heuristic across languages)
                if stripped.startswith("#") or stripped.startswith("//"):
                    continue

                for pattern, category, severity, confidence, title, remediation, cwe in ALL_REGEX_PATTERNS:
                    # Skip insecure HTTP check in test files
                    if category == "insecure-transport" and "http://" in title.lower() and is_test_file:
                        continue

                    if pattern.search(line):
                        # Extra validation for password pattern: skip placeholders
                        if "password" in title.lower() and _is_password_placeholder(line):
                            continue

                        truncated_line = _safe_context(line)
                        findings.append(
                            {
                                "tool": "regex",
                                "file": str(filepath.resolve()),
                                "line": line_num,
                                "severity": severity,
                                "confidence": confidence,
                                "category": category,
                                "title": title,
                                "detail": truncated_line,
                                "remediation": remediation,
                                "cwe": cwe,
                            }
                        )

    _log(f"Regex scan complete: {files_scanned} file(s) scanned, {len(findings)} issue(s) found.", verbose)
    return findings


def _is_test_path(rel_path: str) -> bool:
    """Heuristic to detect test files and directories."""
    parts = rel_path.lower().replace("\\", "/")
    return (
        "/test/" in parts
        or "/tests/" in parts
        or parts.startswith("test/")
        or parts.startswith("tests/")
        or parts.endswith("_test.py")
        or parts.endswith("_test.js")
        or parts.endswith("_test.ts")
        or "test_" in Path(rel_path).name.lower()
        or ".test." in Path(rel_path).name.lower()
        or ".spec." in Path(rel_path).name.lower()
    )


def _is_password_placeholder(line: str) -> bool:
    """
    Return True if a password assignment looks like a placeholder, empty
    string, environment variable reference, or template variable rather
    than a real hardcoded credential.
    """
    lower = line.lower()
    placeholders = [
        'password = ""',
        "password = ''",
        'password: ""',
        "password: ''",
        "password = os.environ",
        "password = os.getenv",
        "password = env(",
        "password = config",
        "password = settings",
        "password = none",
        "password = null",
        "password_hash",
        "password_field",
        "password_input",
        "password_reset",
        "${",
        "<%=",
        "{{",
        "placeholder",
        "changeme",
        "xxx",
        "example",
        "your_password",
        "your-password",
        "password_here",
        "<password>",
    ]
    for p in placeholders:
        if p in lower:
            return True
    return False


# ---------------------------------------------------------------------------
# Merge and deduplicate findings
# ---------------------------------------------------------------------------


def merge_findings(
    bandit_results: list[dict[str, Any]],
    regex_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Merge findings from bandit and regex scanners into a unified list.

    Keep distinct issue categories/titles at a shared location. For the same
    issue identity, retain highest severity before comparing safe detail length.

    Results are sorted by severity (critical > high > medium > low),
    then by file path, then by line number.
    """
    # Build index for deduplication: (resolved_file, line) -> finding
    seen: dict[tuple, dict[str, Any]] = {}

    for finding in bandit_results + regex_results:
        finding = _redacted_finding(finding)
        key = (finding["file"], finding["line"], finding.get("category"), finding.get("title"))
        if key in seen:
            existing = seen[key]
            new_rank = SEVERITY_ORDER.get(finding["severity"], 99)
            old_rank = SEVERITY_ORDER.get(existing["severity"], 99)
            if new_rank < old_rank or new_rank == old_rank and len(finding["detail"]) > len(existing.get("detail", "")):
                seen[key] = finding
        else:
            seen[key] = finding

    merged = list(seen.values())
    merged.sort(
        key=lambda f: (
            SEVERITY_ORDER.get(f["severity"], 99),
            f["file"],
            f["line"],
        )
    )
    return merged


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def generate_report(
    directory: Path,
    findings: list[dict[str, Any]],
    output_path: Path | None = None,
    *,
    errors: list[str] | None = None,
    gate: int | None = None,
    unfiltered_count: int | None = None,
) -> None:
    """
    Print a Markdown-formatted security report to stdout and optionally
    write a JSON report to the specified output path.
    """
    findings = [_redacted_finding(row) for row in findings]
    errors = errors or []
    if errors:
        print("INCOMPLETE security scan: selected analyses did not finish reliably.")
        for error in errors:
            print("  " + error)
    if not findings:
        print("\n=== Security Scan Report ===\n")
        print(f"Target: {directory.resolve()}\n")
        print("No findings at the selected display threshold.\n")
        if output_path:
            _write_json_report(
                directory, findings, output_path, errors=errors, gate=gate, unfiltered_count=unfiltered_count
            )
        return

    # -- Summary statistics --
    by_severity: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_file: dict[str, int] = {}

    for f in findings:
        sev = f["severity"]
        cat = f["category"]
        fil = f["file"]
        by_severity[sev] = by_severity.get(sev, 0) + 1
        by_category[cat] = by_category.get(cat, 0) + 1
        by_file[fil] = by_file.get(fil, 0) + 1

    print("\n=== Security Scan Report ===\n")
    print(f"Target: {directory.resolve()}")
    print(f"Total findings: {len(findings)}\n")

    # Severity summary
    print("## Findings by Severity\n")
    for sev in ("critical", "high", "medium", "low"):
        count = by_severity.get(sev, 0)
        if count > 0:
            label = sev.upper()
            print(f"  {label}: {count}")
    print()

    # Category summary
    print("## Findings by Category\n")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    print()

    # Top 5 most affected files
    top_files = sorted(by_file.items(), key=lambda x: -x[1])[:5]
    if top_files:
        print("## Top Affected Files\n")
        for filepath, count in top_files:
            # Show relative path if possible
            try:
                rel = Path(filepath).relative_to(directory.resolve())
            except ValueError:
                rel = filepath
            print(f"  {rel} ({count} finding(s))")
        print()

    # Detailed findings grouped by severity
    print("## Detailed Findings\n")
    current_severity = None
    for finding in findings:
        sev = finding["severity"]
        if sev != current_severity:
            current_severity = sev
            print(f"### {sev.upper()}\n")

        try:
            rel = Path(finding["file"]).relative_to(directory.resolve())
        except ValueError:
            rel = finding["file"]

        print(f"- **{finding['title']}**")
        print(f"  File: {rel}:{finding['line']}")
        print(f"  Tool: {finding['tool']} | Confidence: {finding['confidence']}")
        if finding.get("cwe"):
            print(f"  CWE: {finding['cwe']}")
        if finding.get("detail"):
            detail_display = finding["detail"][:200]
            print(f"  Detail: {detail_display}")
        if finding.get("remediation"):
            print(f"  Remediation: {finding['remediation']}")
        print()

    # JSON output
    if output_path:
        _write_json_report(
            directory, findings, output_path, errors=errors, gate=gate, unfiltered_count=unfiltered_count
        )


def _write_json_report(
    directory: Path,
    findings: list[dict[str, Any]],
    output_path: Path,
    *,
    errors: list[str] | None = None,
    gate: int | None = None,
    unfiltered_count: int | None = None,
) -> None:
    """Write the findings to a JSON file."""
    findings = [_redacted_finding(row) for row in findings]
    report = {
        "scanner": "code_security_scanner",
        "target": str(directory.resolve()),
        "total_findings": len(findings),
        "summary": {
            "by_severity": {},
            "by_category": {},
        },
        "findings": findings,
        "errors": errors or [],
        "status": "incomplete" if errors else "complete",
        "exit_code": gate,
        "total_unfiltered_findings": len(findings) if unfiltered_count is None else unfiltered_count,
    }

    for f in findings:
        sev = f["severity"]
        cat = f["category"]
        report["summary"]["by_severity"][sev] = report["summary"]["by_severity"].get(sev, 0) + 1
        report["summary"]["by_category"][cat] = report["summary"]["by_category"].get(cat, 0) + 1

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, default=str)
        print(f"\nJSON report written to: {output_path}", file=sys.stderr)
    except OSError as exc:
        raise ScanIncomplete("Requested JSON report could not be persisted: " + type(exc).__name__) from exc


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse arguments and run the security scanner."""
    parser = argparse.ArgumentParser(
        prog="code_security_scanner",
        description="Static analysis security scanner combining Bandit and custom regex patterns.",
        epilog="Exit code 0 if no critical/high findings, 1 otherwise, 2 on scanner error.",
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Path to the source code directory to scan.",
    )
    parser.add_argument(
        "--tools",
        type=str,
        default="bandit,regex",
        help="Comma-separated list of scan engines to use (default: bandit,regex).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to write JSON report (optional).",
    )
    parser.add_argument(
        "--severity",
        type=str,
        default="low",
        choices=["critical", "high", "medium", "low"],
        help="Minimum severity threshold to report (default: low).",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        default=None,
        help='Comma-separated glob patterns to exclude (e.g. "test_*,*_test.py").',
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress information to stderr.",
    )

    args = parser.parse_args()

    # Validate directory
    if not args.directory.is_dir():
        print(f"[scanner] Error: '{args.directory}' is not a valid directory.", file=sys.stderr)
        sys.exit(2)

    directory = args.directory.resolve()
    tools = [t.strip().lower() for t in args.tools.split(",")]
    exclude_patterns = [p.strip() for p in args.exclude.split(",")] if args.exclude else None
    severity_threshold = args.severity.lower()
    verbose = args.verbose

    valid_tools = {"bandit", "regex"}
    if not tools or any(tool not in valid_tools for tool in tools) or len(tools) != len(set(tools)):
        parser.error("Select distinct supported tools: bandit,regex")

    _log(f"Scanning: {directory}", verbose)
    _log(f"Tools: {', '.join(tools)}", verbose)
    _log(f"Severity threshold: {severity_threshold}", verbose)
    if exclude_patterns:
        _log(f"Exclude patterns: {', '.join(exclude_patterns)}", verbose)

    # Run selected scan engines
    bandit_results: list[dict[str, Any]] = []
    regex_results: list[dict[str, Any]] = []
    errors: list[str] = []

    if "bandit" in tools:
        try:
            bandit_results = run_bandit_scan(directory, exclude_patterns, verbose)
        except Exception as exc:
            errors.append(
                str(exc) if isinstance(exc, ScanIncomplete) else "Bandit analysis failed: " + type(exc).__name__
            )

    if "regex" in tools:
        try:
            regex_results = run_regex_scan(directory, exclude_patterns, verbose)
        except Exception as exc:
            errors.append(
                str(exc) if isinstance(exc, ScanIncomplete) else "Regex analysis failed: " + type(exc).__name__
            )

    # Merge and deduplicate
    all_findings = merge_findings(bandit_results, regex_results)

    # Apply severity filter
    filtered_findings = [f for f in all_findings if _severity_at_or_above(f["severity"], severity_threshold)]

    _log(
        f"Total: {len(all_findings)} finding(s), {len(filtered_findings)} at or above '{severity_threshold}' severity.",
        verbose,
    )

    # Evidence and finding gates are independent of presentation filtering.
    has_critical_or_high = any(f["severity"] in ("critical", "high") for f in all_findings)
    gate = 2 if errors else 1 if has_critical_or_high else 0
    try:
        generate_report(
            directory, filtered_findings, args.output, errors=errors, gate=gate, unfiltered_count=len(all_findings)
        )
    except ScanIncomplete as exc:
        print("[scanner] " + str(exc), file=sys.stderr)
        gate = 2
    sys.exit(gate)


if __name__ == "__main__":
    main()
