#!/usr/bin/env python3
"""Unified dependency vulnerability scanner.

Scans project dependencies across multiple ecosystems (npm, pip) and produces
a consolidated vulnerability report. Wraps native audit tools (npm audit,
pip-audit, pip check) and normalizes their output into a unified finding
format suitable for CI pipelines and human review.

Usage:
    python3 dependency_auditor.py /path/to/project [options]

Options:
    --scanners npm,pip     Comma-separated list of scanners to run
    --min-severity low     Minimum severity to report (low|moderate|high|critical)
    --output findings.json Write JSON report to file
    --python PATH          Audit an explicitly selected Python environment
    --verbose              Enable verbose progress output

Exit codes:
    0  No critical or high severity findings
    1  Critical or high severity findings detected
    2  Incomplete audit, unknown advisory severity, invalid input, or report error

Copyright 2026 Claude Code Plugins contributors. Licensed under MIT.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# Severity ranking for sorting and filtering. Lower number means more severe.
SEVERITY_RANK: dict[str, int] = {
    "critical": 0,
    "high": 1,
    "moderate": 2,
    "low": 3,
    "info": 4,
    "unknown": 5,
}

SUPPORTED_SCANNERS: set[str] = {"npm", "pip"}
FUTURE_SCANNERS: dict[str, str] = {
    "cargo": "Cargo.toml",
    "go": "go.mod",
    "bundler": "Gemfile",
}

SUBPROCESS_TIMEOUT: int = 60


class AuditIncomplete(Exception):
    """A selected audit lacks trustworthy, project-bound completion evidence."""


def log(message: str, verbose: bool = True) -> None:
    """Print a progress message to stderr."""
    if verbose:
        print(f"[*] {message}", file=sys.stderr)


def log_warn(message: str) -> None:
    """Print a warning message to stderr (always shown)."""
    print(f"[!] {message}", file=sys.stderr)


def log_error(message: str) -> None:
    """Print an error message to stderr (always shown)."""
    print(f"[-] {message}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Project detection
# ---------------------------------------------------------------------------


def detect_project_type(directory: Path) -> list[str]:
    """Auto-detect project ecosystems by scanning for manifest files.

    Checks for well-known dependency manifest files and returns a list of
    ecosystem identifiers. Supported ecosystems produce actionable scans;
    future-support ecosystems print an informational message.

    Args:
        directory: Root directory of the project to scan.

    Returns:
        List of detected ecosystem strings (e.g. ["npm", "pip"]).
    """
    detected: list[str] = []

    # npm / Node.js
    npm_markers = ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"]
    if any((directory / marker).exists() for marker in npm_markers):
        detected.append("npm")

    # pip / Python
    pip_markers = ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "setup.cfg"]
    if any((directory / marker).exists() for marker in pip_markers):
        detected.append("pip")

    # Future-support ecosystems
    for ecosystem, manifest in FUTURE_SCANNERS.items():
        if (directory / manifest).exists():
            log_warn(
                f"Detected {ecosystem} project ({manifest}), but {ecosystem} scanning is not yet implemented. Skipping."
            )

    return detected


# ---------------------------------------------------------------------------
# npm audit
# ---------------------------------------------------------------------------


def run_npm_audit(directory: Path) -> list[dict[str, Any]]:
    """Run npm audit and parse vulnerability findings.

    Executes ``npm audit --json`` in the target directory and parses the
    structured output. Handles missing npm installations and projects that
    lack a node_modules directory.

    Args:
        directory: Project root containing package.json.

    Returns:
        List of finding dicts with keys matching the unified schema.
    """
    findings: list[dict[str, Any]] = []

    # Check npm is available
    try:
        npm_check = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuditIncomplete("Selected npm executable unavailable: " + type(exc).__name__) from exc
    if npm_check.returncode != 0:
        raise AuditIncomplete("Selected npm executable failed its availability check")

    # Check for package.json
    if not (directory / "package.json").exists():
        raise AuditIncomplete("Selected npm audit requires a project package.json")

    # Warn if node_modules is missing
    if not (directory / "node_modules").is_dir():
        log_warn("Project node_modules is absent; npm audit must still return valid dependency/advisory evidence.")

    try:
        result = subprocess.run(
            ["npm", "audit", "--json"],
            capture_output=True,
            text=True,
            cwd=str(directory),
            timeout=SUBPROCESS_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuditIncomplete("Selected npm audit failed: " + type(exc).__name__) from exc

    # npm audit returns non-zero when vulnerabilities exist, so we parse
    # the output regardless of the return code.
    if not result.stdout.strip():
        raise AuditIncomplete("Selected npm audit produced no structured result")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AuditIncomplete("Selected npm audit returned invalid JSON") from exc

    if (
        result.returncode not in (0, 1)
        or not isinstance(data, dict)
        or "error" in data
        or not (isinstance(data.get("vulnerabilities"), dict) or isinstance(data.get("advisories"), dict))
    ):
        raise AuditIncomplete("Selected npm audit returned an error or unsupported result contract")

    findings.extend(_parse_npm_audit_v2(data))
    if not findings:
        findings.extend(_parse_npm_audit_v1(data))
    if result.returncode == 1 and not findings:
        raise AuditIncomplete("Selected npm audit failed without a completed advisory result")

    return findings


def _parse_npm_audit_v2(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse npm audit JSON output in the v2 format (npm 7+).

    The v2 format uses a top-level ``vulnerabilities`` object keyed by
    package name.
    """
    findings: list[dict[str, Any]] = []
    vulnerabilities = data.get("vulnerabilities", {})
    if not isinstance(vulnerabilities, dict):
        raise AuditIncomplete("npm vulnerabilities must be a mapping")

    for pkg_name, vuln_info in vulnerabilities.items():
        if not isinstance(pkg_name, str) or not pkg_name or not isinstance(vuln_info, dict):
            raise AuditIncomplete("npm vulnerability record is malformed")
        severity = vuln_info.get("severity")
        fix_available = vuln_info.get("fixAvailable")
        fixed_version: Optional[str] = None
        if isinstance(fix_available, dict):
            fixed_version = fix_available.get("version")

        # Each vulnerability entry may reference multiple advisories via "via"
        via_entries = vuln_info.get("via", [])
        if not isinstance(via_entries, list) or any(not isinstance(item, (str, dict)) for item in via_entries):
            raise AuditIncomplete("npm advisory references are malformed")
        if not via_entries:
            findings.append(
                {
                    "scanner": "npm",
                    "package": pkg_name,
                    "severity": _normalize_severity(severity),
                    "title": f"Vulnerability in {pkg_name}",
                    "detail": f"Severity: {severity}. Check npm audit for details.",
                    "cve": None,
                    "installed_version": vuln_info.get("range"),
                    "fixed_version": fixed_version,
                }
            )
            continue

        for via in via_entries:
            if isinstance(via, str):
                # Indirect vulnerability reference (transitive dependency name)
                findings.append(
                    {
                        "scanner": "npm",
                        "package": pkg_name,
                        "severity": _normalize_severity(severity),
                        "title": f"Depends on vulnerable {via}",
                        "detail": f"{pkg_name} is affected through dependency on {via}.",
                        "cve": None,
                        "installed_version": vuln_info.get("range"),
                        "fixed_version": fixed_version,
                    }
                )
            elif isinstance(via, dict):
                cve = _extract_cve(via.get("url", ""))
                findings.append(
                    {
                        "scanner": "npm",
                        "package": pkg_name,
                        "severity": _normalize_severity(via.get("severity", severity)),
                        "title": via.get("title", f"Vulnerability in {pkg_name}"),
                        "detail": via.get("title", "No description available."),
                        "cve": cve,
                        "installed_version": via.get("range") or vuln_info.get("range"),
                        "fixed_version": fixed_version,
                    }
                )

    return findings


def _parse_npm_audit_v1(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse npm audit JSON output in the v1 format (npm 6).

    The v1 format uses a top-level ``advisories`` object keyed by advisory ID.
    """
    findings: list[dict[str, Any]] = []
    advisories = data.get("advisories", {})

    for _adv_id, advisory in advisories.items():
        if not isinstance(advisory, dict):
            raise AuditIncomplete("npm advisory record is malformed")
        cve_list = advisory.get("cves", [])
        cve = cve_list[0] if cve_list else None
        findings.append(
            {
                "scanner": "npm",
                "package": advisory.get("module_name", "unknown"),
                "severity": _normalize_severity(advisory.get("severity")),
                "title": advisory.get("title", "Unknown vulnerability"),
                "detail": advisory.get("overview", "No description available."),
                "cve": cve,
                "installed_version": advisory.get("findings", [{}])[0].get("version"),
                "fixed_version": advisory.get("patched_versions"),
            }
        )

    return findings


# ---------------------------------------------------------------------------
# pip-audit
# ---------------------------------------------------------------------------


def run_pip_audit(directory: Path, python_executable: Optional[Path] = None) -> list[dict[str, Any]]:
    """Audit explicit requirements or an explicitly designated environment.

    Never install a scanner, resolve/install a project, or fall back to the
    wrapper's ambient interpreter. Requirements mode uses fully pinned input
    with pip disabled; environment mode runs the already-installed auditor in
    the designated interpreter. Preserve a venv interpreter's lexical path.
    """
    if python_executable is not None:
        if not python_executable.is_file():
            raise AuditIncomplete("The explicitly designated Python interpreter is unavailable")
        cmd = [str(python_executable), "-I", "-m", "pip_audit", "--format=json", "--strict"]
    else:
        req_args = _pip_audit_requirement_args(directory)
        if not req_args:
            raise AuditIncomplete("Python auditing requires pinned requirements.txt or explicit --python environment")
        cmd = ["pip-audit", "--format=json", "--strict", *req_args, "--no-deps", "--disable-pip"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(directory), timeout=SUBPROCESS_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuditIncomplete("Selected pip-audit unavailable or failed: " + type(exc).__name__) from exc
    if result.returncode not in (0, 1):
        raise AuditIncomplete("Selected pip-audit returned a failure status")
    findings = _parse_pip_audit_output(result.stdout)
    if result.returncode == 1 and not findings:
        raise AuditIncomplete("Selected pip-audit failed without a completed advisory result")
    return findings


def _pip_audit_requirement_args(directory: Path) -> list[str]:
    """Build pip-audit CLI args pointing to requirement files if present."""
    args: list[str] = []
    req_file = directory / "requirements.txt"
    if req_file.exists():
        args.extend(["--requirement", str(req_file)])
    return args


def _parse_pip_audit_output(raw_output: str) -> list[dict[str, Any]]:
    """Parse JSON output from pip-audit into unified findings."""
    findings: list[dict[str, Any]] = []
    if not raw_output.strip():
        raise AuditIncomplete("Selected pip-audit produced no structured result")

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise AuditIncomplete("Selected pip-audit returned invalid JSON") from exc

    # pip-audit can return either a top-level list or a dict with
    # "dependencies" key depending on version.
    vulns: list[dict[str, Any]] = []
    if isinstance(data, list):
        vulns = data
    elif isinstance(data, dict):
        if "error" in data:
            raise AuditIncomplete("Selected pip-audit returned an error result")
        vulns = data.get("dependencies", data.get("vulnerabilities"))
    else:
        raise AuditIncomplete("Selected pip-audit returned an unsupported result")
    if not isinstance(vulns, list):
        raise AuditIncomplete("Selected pip-audit omitted its dependency list")

    for entry in vulns:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("name"), str)
            or not entry["name"]
            or entry.get("skip_reason")
        ):
            raise AuditIncomplete("Selected pip-audit contained an invalid or skipped dependency")
        pkg_name = entry.get("name", "unknown")
        installed = entry.get("version", entry.get("installed_version"))
        vuln_list = entry.get("vulns", [entry] if "id" in entry else [])
        if not isinstance(vuln_list, list) or not ("vulns" in entry or "id" in entry):
            raise AuditIncomplete("Selected pip-audit contained an invalid advisory list")

        for vuln in vuln_list:
            if not isinstance(vuln, dict) or not isinstance(vuln.get("id"), str) or not vuln["id"]:
                raise AuditIncomplete("Selected pip-audit contained an invalid advisory")
            vuln_id = vuln.get("id", "")
            cve = vuln_id if vuln_id.startswith("CVE-") else _extract_cve(vuln_id)
            description = vuln.get("description", vuln.get("detail", ""))
            if description is not None and not isinstance(description, str):
                raise AuditIncomplete("pip advisory description is malformed")
            fix = vuln.get("fix_versions", vuln.get("fixed_version"))
            if isinstance(fix, list):
                fix = fix[0] if fix else None

            findings.append(
                {
                    "scanner": "pip-audit",
                    "package": pkg_name,
                    "severity": _normalize_severity(vuln.get("severity")),
                    "title": f"{vuln_id}: {pkg_name}" if vuln_id else f"Vulnerability in {pkg_name}",
                    "detail": description or "No description provided by pip-audit.",
                    "cve": cve,
                    "installed_version": installed,
                    "fixed_version": fix,
                }
            )

    return findings


def run_pip_check(directory: Path, python_executable: Optional[Path] = None) -> list[dict[str, Any]]:
    """Run pip check to detect broken dependencies and version conflicts.

    Parses the text output of ``pip check`` into structured findings. Broken
    dependencies are reported as moderate severity because they may indicate
    supply-chain manipulation or installation tampering.

    Args:
        directory: Project root (used as working directory).

    Returns:
        List of finding dicts with keys matching the unified schema.
    """
    findings: list[dict[str, Any]] = []

    if python_executable is None or not python_executable.is_file():
        raise AuditIncomplete("pip check requires an explicitly designated --python environment")
    try:
        result = subprocess.run(
            [str(python_executable), "-I", "-m", "pip", "check"],
            capture_output=True,
            text=True,
            cwd=str(directory),
            timeout=SUBPROCESS_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuditIncomplete("Selected pip check failed: " + type(exc).__name__) from exc

    if result.returncode == 0:
        return findings
    if result.returncode != 1 or not result.stdout.strip():
        raise AuditIncomplete("Selected pip check did not produce a completed conflict result")

    # pip check output lines look like:
    #   packageA 1.0 requires packageB, which is not installed.
    #   packageA 1.0 has requirement packageB>=2.0, but you have packageB 1.5.
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if " requires " not in line and " has requirement " not in line:
            raise AuditIncomplete("Selected pip check returned an unsupported diagnostic")

        # Extract package name (first token)
        parts = line.split()
        pkg_name = parts[0] if parts else "unknown"
        installed_version = parts[1] if len(parts) > 1 else None

        findings.append(
            {
                "scanner": "pip-check",
                "package": pkg_name,
                "severity": "moderate",
                "title": f"Dependency conflict: {pkg_name}",
                "detail": line,
                "cve": None,
                "installed_version": installed_version,
                "fixed_version": None,
            }
        )

    return findings


# ---------------------------------------------------------------------------
# Unification and deduplication
# ---------------------------------------------------------------------------


def unify_results(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize, deduplicate, and sort findings by severity.

    Deduplication key is (package, cve) for findings with a CVE, or
    (package, scanner, title) for findings without one. Results are sorted
    with critical findings first.

    Args:
        findings: Raw list of finding dicts from all scanners.

    Returns:
        Deduplicated and sorted list of unified finding dicts.
    """
    seen: dict[tuple[str, ...], dict] = {}

    for f in findings:
        # Normalize severity
        f = dict(f)
        f["severity"] = _normalize_severity(f.get("severity"))

        # Build dedup key
        if f.get("cve"):
            key = (f["package"], f["cve"])
        else:
            key = (f["package"], f["scanner"], f["title"])

        if key not in seen or SEVERITY_RANK[f["severity"]] < SEVERITY_RANK[seen[key]["severity"]]:
            seen[key] = f

    # Sort by severity rank, then package name
    unified = sorted(seen.values(), key=lambda f: (SEVERITY_RANK[f["severity"]], f["package"]))
    return unified


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def generate_report(
    directory: Path,
    findings: list[dict[str, Any]],
    output_path: Optional[Path],
    *,
    errors: Optional[list[str]] = None,
    gate: Optional[int] = None,
    unfiltered_count: Optional[int] = None,
    inputs: Optional[dict] = None,
) -> None:
    """Generate a markdown report to stdout and optionally write JSON to file.

    The report includes a summary table of findings by severity and detailed
    listings grouped by severity level.

    Args:
        directory: Scanned project directory (shown in report header).
        findings: Unified and sorted list of finding dicts.
        output_path: Optional path for JSON file output.
    """
    errors = errors or []
    # Summary counts
    counts: dict[str, int] = {"critical": 0, "high": 0, "moderate": 0, "low": 0, "info": 0}
    for f in findings:
        sev = f.get("severity", "moderate")
        counts[sev] = counts.get(sev, 0) + 1

    total = len(findings)

    print()
    print("=" * 60)
    print("  Dependency Vulnerability Audit Report")
    print("=" * 60)
    print(f"  Project: {directory}")
    print(f"  Total findings: {total}")
    if errors:
        print("  INCOMPLETE: selected audit evidence is unavailable or invalid.")
        for error in errors:
            print("  " + error)
    print()

    if total == 0:
        print("  No findings at the selected display threshold.")
        print()
        print("=" * 60)
    else:
        # Summary table
        print("  Severity Breakdown:")
        print("  -------------------")
        for sev in ("critical", "high", "moderate", "low", "info", "unknown"):
            count = counts.get(sev, 0)
            if count > 0:
                label = sev.upper().ljust(10)
                print(f"    {label} {count}")
        print()

        # Detailed findings grouped by severity
        for sev in ("critical", "high", "moderate", "low", "info", "unknown"):
            sev_findings = [f for f in findings if f["severity"] == sev]
            if not sev_findings:
                continue

            print(f"  [{sev.upper()}]")
            print(f"  {'-' * 40}")
            for f in sev_findings:
                print(f"    Package:   {f['package']}")
                print(f"    Scanner:   {f['scanner']}")
                print(f"    Title:     {f['title']}")
                if f.get("cve"):
                    print(f"    CVE:       {f['cve']}")
                if f.get("installed_version"):
                    print(f"    Installed: {f['installed_version']}")
                if f.get("fixed_version"):
                    print(f"    Fix:       {f['fixed_version']}")
                if f.get("detail") and f["detail"] != f["title"]:
                    detail_lines = f["detail"].splitlines()
                    print(f"    Detail:    {detail_lines[0]}")
                    for dl in detail_lines[1:]:
                        print(f"               {dl}")
                print()

        print("=" * 60)

    # JSON output
    if output_path is not None:
        report_data = {
            "project": str(directory),
            "total": total,
            "counts": counts,
            "findings": findings,
            "errors": errors,
            "status": "incomplete" if errors else "complete",
            "exit_code": gate,
            "total_unfiltered_findings": total if unfiltered_count is None else unfiltered_count,
            "audit_inputs": inputs or {},
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
        log(f"JSON report written to {output_path}", verbose=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize_severity(severity: object) -> str:
    """Normalize a severity string to one of the canonical levels."""
    s = severity.strip().lower() if isinstance(severity, str) else "unknown"
    mapping: dict[str, str] = {
        "critical": "critical",
        "high": "high",
        "moderate": "moderate",
        "medium": "moderate",
        "low": "low",
        "info": "info",
        "informational": "info",
        "none": "info",
    }
    return mapping.get(s, "unknown")


def _extract_cve(text: str) -> Optional[str]:
    """Extract a CVE identifier from a string, if present."""
    import re

    match = re.search(r"CVE-\d{4}-\d{4,}", text)
    return match.group(0) if match else None


def _severity_from_vuln_id(vuln_id: str) -> str:
    """An advisory identifier alone does not establish its severity."""
    # CVE/GHSA/PYSEC identifiers do not encode a severity assessment.
    return "unknown"


def _filter_by_severity(
    findings: list[dict[str, Any]],
    min_severity: str,
) -> list[dict[str, Any]]:
    """Filter findings to only include those at or above the minimum severity."""
    threshold = SEVERITY_RANK.get(min_severity, 3)
    return [f for f in findings if f["severity"] == "unknown" or SEVERITY_RANK.get(f["severity"], 99) <= threshold]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for the dependency auditor CLI."""
    parser = argparse.ArgumentParser(
        description="Unified dependency vulnerability scanner.",
        epilog="Example: python3 dependency_auditor.py ./my-project --min-severity moderate",
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Path to the project directory to scan.",
    )
    parser.add_argument(
        "--scanners",
        type=str,
        default=None,
        help="Comma-separated list of scanners to run (e.g. npm,pip). Default: auto-detect.",
    )
    parser.add_argument(
        "--min-severity",
        type=str,
        default="low",
        choices=["critical", "high", "moderate", "low", "info"],
        help="Minimum severity to include in the report (default: low).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to write JSON report file.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose progress output on stderr.",
    )
    parser.add_argument(
        "--python", type=Path, help="Explicit project environment interpreter; never installed or auto-selected"
    )

    args = parser.parse_args()
    directory: Path = args.directory.resolve()
    verbose: bool = args.verbose
    python_executable = args.python.absolute() if args.python is not None else None
    if python_executable is not None and not python_executable.is_file():
        parser.error("--python must identify an existing explicitly approved project interpreter")

    if not directory.is_dir():
        log_error(f"Directory does not exist: {directory}")
        sys.exit(2)

    # Determine which scanners to run
    if args.scanners:
        requested = [s.strip().lower() for s in args.scanners.split(",")]
        unknown = [s for s in requested if s not in SUPPORTED_SCANNERS]
        if unknown or len(requested) != len(set(requested)):
            parser.error("Select distinct supported scanners: npm,pip")
        ecosystems = [s for s in requested if s in SUPPORTED_SCANNERS]
    else:
        log(f"Auto-detecting project types in {directory}...", verbose)
        ecosystems = detect_project_type(directory)

    if not ecosystems:
        log_warn(
            f"No supported project types detected in {directory}. Supported: {', '.join(sorted(SUPPORTED_SCANNERS))}"
        )
        sys.exit(2)

    log(f"Scanners to run: {', '.join(ecosystems)}", verbose)
    if python_executable is not None and "pip" not in ecosystems:
        parser.error("--python applies only to a selected Python audit")

    # Collect findings from all scanners
    all_findings: list[dict[str, Any]] = []
    errors: list[str] = []

    if "npm" in ecosystems:
        log("Running npm audit...", verbose)
        try:
            all_findings.extend(run_npm_audit(directory))
        except Exception as exc:
            errors.append(str(exc) if isinstance(exc, AuditIncomplete) else "npm audit failed: " + type(exc).__name__)
        log(f"npm audit: {len(all_findings)} raw findings so far.", verbose)

    if "pip" in ecosystems:
        pip_start = len(all_findings)

        log("Running pip-audit...", verbose)
        try:
            all_findings.extend(run_pip_audit(directory, python_executable))
        except Exception as exc:
            errors.append(str(exc) if isinstance(exc, AuditIncomplete) else "pip audit failed: " + type(exc).__name__)

        if python_executable is not None:
            log("Running pip check in the explicitly designated environment...", verbose)
            try:
                all_findings.extend(run_pip_check(directory, python_executable))
            except Exception as exc:
                errors.append(
                    str(exc) if isinstance(exc, AuditIncomplete) else "pip check failed: " + type(exc).__name__
                )

        pip_count = len(all_findings) - pip_start
        log(f"pip scanners: {pip_count} raw findings.", verbose)

    # Unify and filter
    unified = unify_results(all_findings)
    if any(f["severity"] == "unknown" for f in unified):
        errors.append("One or more advisory severities were not supplied; severity assessment remains incomplete")
    filtered = _filter_by_severity(unified, args.min_severity)

    log(
        f"Unified: {len(unified)} total, {len(filtered)} at or above {args.min_severity} severity.",
        verbose,
    )

    # Evidence/finding gates are computed from unfiltered evidence.
    has_critical_or_high = any(f["severity"] in ("critical", "high") for f in unified)
    gate = 2 if errors else 1 if has_critical_or_high else 0
    inputs = {"project_directory": str(directory), "selected_scanners": ecosystems}
    if "pip" in ecosystems:
        inputs["python"] = (
            {"mode": "designated-environment", "interpreter": str(python_executable), "isolated": True}
            if python_executable is not None
            else {
                "mode": "pinned-requirements",
                "requirements": str(directory / "requirements.txt"),
                "dependency_resolution": "disabled",
            }
        )
    try:
        generate_report(
            directory, filtered, args.output, errors=errors, gate=gate, unfiltered_count=len(unified), inputs=inputs
        )
    except OSError as exc:
        log_error("Requested report could not be persisted: " + type(exc).__name__)
        gate = 2
    sys.exit(gate)


if __name__ == "__main__":
    main()
