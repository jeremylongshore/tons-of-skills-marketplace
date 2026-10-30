#!/usr/bin/env python3
"""Inventory declared license metadata and flag review; not a legal certificate.

0: completed with no automated review flags; 1: review/strict flags;
2: incomplete enumeration or usage. No package installation is performed.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Dict, Set, Tuple

from dependency_runtime import (
    CheckError,
    array_value,
    load_json,
    object_value,
    parse_json,
    run_tool,
    string_value,
    visible,
    write_report,
)


@dataclass
class License:
    name: str
    spdx_id: str
    category: str
    description: str

    def is_permissive(self):
        return self.category == "permissive"

    def is_copyleft(self):
        return self.category == "copyleft"

    def is_proprietary(self):
        return self.category == "proprietary"


# Known licenses database
KNOWN_LICENSES: Dict[str, License] = {
    "MIT": License("MIT", "MIT", "permissive", "Very permissive license"),
    "Apache-2.0": License("Apache License 2.0", "Apache-2.0", "permissive", "Permissive with patent grant"),
    "BSD-2-Clause": License("BSD 2-Clause", "BSD-2-Clause", "permissive", "Simple BSD-style license"),
    "BSD-3-Clause": License("BSD 3-Clause", "BSD-3-Clause", "permissive", "Standard BSD license"),
    "ISC": License("ISC", "ISC", "permissive", "ISC/OpenBSD style license"),
    "GPL-2.0": License("GNU GPL v2", "GPL-2.0", "copyleft", "Strong copyleft (requires source)"),
    "GPL-3.0": License("GNU GPL v3", "GPL-3.0", "copyleft", "Strong copyleft (requires source)"),
    "LGPL-2.1": License("GNU LGPL v2.1", "LGPL-2.1", "copyleft", "Weak copyleft (library only)"),
    "LGPL-3.0": License("GNU LGPL v3", "LGPL-3.0", "copyleft", "Weak copyleft (library only)"),
    "AGPL-3.0": License(
        "GNU AGPL v3",
        "AGPL-3.0",
        "copyleft",
        "Strong copyleft (includes network use)",
    ),
    "MPL-2.0": License("Mozilla Public License 2.0", "MPL-2.0", "copyleft", "File-level copyleft"),
    "EPL-1.0": License("Eclipse Public License 1.0", "EPL-1.0", "copyleft", "Weak copyleft"),
    "Unlicense": License("Unlicense", "Unlicense", "permissive", "Public domain-like"),
    "CC0-1.0": License("CC0 1.0", "CC0-1.0", "permissive", "Public domain waiver"),
}

# Legacy review hints only; combinations do not establish legal incompatibility.
INCOMPATIBLE_COMBINATIONS: Set[Tuple[str, str]] = {
    ("GPL-2.0", "Apache-2.0"),
    ("GPL-2.0", "GPL-3.0"),
    ("AGPL-3.0", "MIT"),
    ("GPL-3.0", "CDDL-1.0"),
}


@dataclass
class Dependency:
    name: str
    version: str
    license: str
    license_obj: License | None = None

    def is_compatible_with_permissive(self):
        """Category convenience only, never a compatibility/legal determination."""
        return self.license_obj is not None and self.license_obj.is_permissive()


class LicenseCompliance:
    def __init__(self, strict_mode=False, verbose=False, python_executable=None, timeout=30):
        self.strict_mode = strict_mode
        self.verbose = verbose
        self.python_executable = python_executable
        self.timeout = timeout
        self.dependencies = []
        self.issues = []
        self.warnings = []
        self.errors = []
        self.enumerations = []

    @property
    def complete(self):
        return bool(self.enumerations) and not self.errors

    def warning(self, message):
        self.warnings.append(message)

    def error(self, message):
        self.errors.append(message)

    def resolve_license(self, declaration):
        if not isinstance(declaration, str):
            raise CheckError("license declaration must be text")
        declaration = declaration.strip()
        # Exact IDs/names only. A compound expression is not its first term.
        # Unsupported expressions, LicenseRef values and unknown IDs need review.
        for identifier, item in KNOWN_LICENSES.items():
            if declaration.casefold() in {identifier.casefold(), item.name.casefold()}:
                return item
        return None

    def _dependency(self, name, version, declaration):
        name = string_value(name, "dependency name")
        if version is None:
            version = "unknown"
        if not isinstance(version, str):
            raise CheckError("invalid dependency version")
        if isinstance(declaration, dict):
            # npm's historical single-license object. Lists/expressions are not
            # silently flattened into an approved license.
            declaration = declaration.get("type")
        if declaration is None:
            declaration = "Unknown"
        if not isinstance(declaration, str):
            raise CheckError("invalid license declaration")
        self.dependencies.append(Dependency(name, version, declaration, self.resolve_license(declaration)))

    def _process_npm_dependencies(self, dependencies, parent=""):
        pending = [object_value(dependencies, "npm dependency tree")]
        while pending:
            for name, row in pending.pop().items():
                row = object_value(row, "npm dependency")
                if row.get("missing") or row.get("invalid"):
                    self.error("npm reported a missing/invalid installed dependency")
                self._dependency(name, row.get("version"), row.get("license"))
                nested = object_value(row.get("dependencies", {}), "nested npm dependencies")
                pending.append(nested)

    def check_npm_licenses(self):
        record = {"tool": "npm", "scope": "installed tree at the selected project root", "complete": False}
        self.enumerations.append(record)
        try:
            manifest = object_value(load_json("package.json"), "package manifest")
            declared = set()
            for field in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
                declared.update(object_value(manifest.get(field, {}), field))
            code, raw = run_tool(["npm", "ls", "--json", "--all", "--long"], timeout=self.timeout)
            record["exit_code"] = code
            if code not in (0, 1):
                raise CheckError(f"npm license enumeration failed with exit code {code}")
            data = object_value(parse_json(raw), "npm installed tree")
            if data.get("error") or data.get("problems") or code:
                self.error("npm reported incomplete or inconsistent installed-tree coverage")
            dependencies = object_value(data.get("dependencies", {}), "npm dependencies")
            if declared - dependencies.keys():
                self.error("declared root dependencies are absent from the installed inventory")
            self._process_npm_dependencies(dependencies)
            record["complete"] = not self.errors
        except CheckError as error:
            self.error(str(error))
        return record["complete"]

    def _process_python_dependencies(self, dependencies):
        for row in array_value(dependencies, "Python license inventory"):
            row = object_value(row, "Python license record")
            self._dependency(row.get("Name"), row.get("Version"), row.get("License"))

    def check_python_licenses(self):
        record = {
            "tool": "pip-licenses",
            "scope": "explicitly selected installed Python environment; not requirements closure",
            "complete": False,
        }
        self.enumerations.append(record)
        try:
            selected = self.python_executable
            if (
                not selected
                or not Path(selected).is_absolute()
                or not Path(selected).is_file()
                or not os.access(selected, os.X_OK)
            ):
                raise CheckError("Python license inventory requires an explicit executable --python path")
            # pip-licenses reads selection/output defaults from cwd/pyproject.toml.
            # An empty private cwd prevents project configuration from silently
            # filtering the explicitly selected installed environment.
            command = [selected, "-m", "piplicenses", "--python", selected, "--format=json"]
            with tempfile.TemporaryDirectory(prefix="dependency-license-") as directory:
                code, raw = run_tool(command, timeout=self.timeout, cwd=directory)
            record["exit_code"] = code
            if code:
                raise CheckError(f"Python license enumeration failed with exit code {code}")
            self._process_python_dependencies(parse_json(raw))
            record["complete"] = True
        except CheckError as error:
            self.error(str(error))
        return record["complete"]

    def check_compatibility(self):
        """Retain conservative review hints; package names alone prove no rights."""
        for dependency in self.dependencies:
            license_obj = dependency.license_obj
            if license_obj is None:
                self.warning(
                    f"Unresolved license metadata/expression: {visible(dependency.name)} ({visible(dependency.license)})"
                )
            elif not license_obj.is_permissive():
                self.warning(
                    f"License obligations require context review: {visible(dependency.name)} ({visible(dependency.license)})"
                )
        identifiers = {dep.license_obj.spdx_id for dep in self.dependencies if dep.license_obj}
        for first, second in sorted(INCOMPATIBLE_COMBINATIONS):
            if first in identifiers and second in identifiers:
                self.warning(
                    f"Legacy policy review hint: {first} with {second}; no incompatibility determination is made"
                )
        if self.strict_mode:
            self.issues.extend(self.warnings)

    def check(self):
        if Path("package.json").is_file():
            self.check_npm_licenses()
        if any(Path(name).is_file() for name in ("requirements.txt", "pyproject.toml", "Pipfile", "Pipfile.lock")):
            self.check_python_licenses()
        if not self.enumerations:
            self.error("no supported root license inventory was selected")
        self.check_compatibility()
        return self.complete and not self.issues and not self.warnings

    def to_json(self):
        status = (
            "incomplete"
            if not self.complete
            else "review-required"
            if self.issues or self.warnings
            else "no-automated-review-flags"
        )
        return json.dumps(
            {
                "summary": {
                    "complete": self.complete,
                    "status": status,
                    "total_dependencies": len(self.dependencies),
                    "has_issues": bool(self.issues),
                    "has_warnings": bool(self.warnings),
                    "legal_compatibility_verified": False,
                },
                "enumerations": self.enumerations,
                "dependencies": [
                    {
                        "name": dep.name,
                        "version": dep.version,
                        "license": dep.license,
                        "category": dep.license_obj.category if dep.license_obj else "unknown",
                    }
                    for dep in self.dependencies
                ],
                "issues": self.issues,
                "warnings": self.warnings,
                "errors": self.errors,
            },
            indent=2,
            allow_nan=False,
        )

    def to_text(self):
        result = json.loads(self.to_json())
        lines = [
            "License Metadata Review Inventory",
            f"Status: {result['summary']['status']}",
            f"Total recorded dependencies: {len(self.dependencies)}",
            "Declared metadata only; legal compatibility is not verified.",
        ]
        lines.extend(f"{visible(dep.name)}@{visible(dep.version)}: {visible(dep.license)}" for dep in self.dependencies)
        lines.extend(f"INCOMPLETE: {visible(item)}" for item in self.errors)
        lines.extend(f"REVIEW: {visible(item)}" for item in self.warnings)
        return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text")
    parser.add_argument("--output", "-o")
    parser.add_argument("--strict", action="store_true", help="also classify review warnings as issues")
    parser.add_argument("--python", help="absolute Python executable for an installed-environment inventory")
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)
    if not 0 < args.timeout <= 300:
        parser.error("timeout must be greater than zero and at most 300 seconds")
    checker = LicenseCompliance(args.strict, args.verbose, args.python, args.timeout)
    checker.check()
    try:
        write_report(checker.to_json() if args.format == "json" else checker.to_text(), args.output)
    except CheckError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 2 if not checker.complete else 1 if checker.issues or checker.warnings else 0


if __name__ == "__main__":
    sys.exit(main())
