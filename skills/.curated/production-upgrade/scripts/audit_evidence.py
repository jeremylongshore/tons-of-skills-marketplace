#!/usr/bin/env python3
"""Validate an upgrade evidence manifest without executing recorded commands."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


REVISION = re.compile(r"^[0-9a-f]{40,64}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SECRET_KEYS = {
    "api_key",
    "authorization_header",
    "cookie",
    "password",
    "presigned_url",
    "private_key",
    "secret",
    "token",
}


class ManifestError(ValueError):
    """Safe validation failure that never includes a rejected secret value."""


def no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"duplicate key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ManifestError(f"non-standard JSON constant: {value}")


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=no_duplicate_object,
            parse_constant=reject_constant,
        )
    except UnicodeDecodeError as error:
        raise ManifestError("manifest must be UTF-8") from error
    except json.JSONDecodeError as error:
        raise ManifestError(f"invalid JSON at line {error.lineno}, column {error.colno}") from error
    if not isinstance(data, dict):
        raise ManifestError("manifest root must be an object")
    return data


def require_keys(data: dict[str, Any], required: set[str], context: str) -> None:
    missing = sorted(required - set(data))
    unknown = sorted(set(data) - required)
    if missing:
        raise ManifestError(f"{context} missing key(s): {', '.join(missing)}")
    if unknown:
        raise ManifestError(f"{context} unknown key(s): {', '.join(unknown)}")


def reject_secret_keys(value: Any, path: str = "manifest") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in SECRET_KEYS:
                raise ManifestError(f"secret-bearing field is prohibited: {path}.{key}")
            reject_secret_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_secret_keys(child, f"{path}[{index}]")


def require_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{context} must be a non-empty string")
    return value


def require_date(value: Any, context: str) -> str:
    text = require_string(value, context)
    try:
        date.fromisoformat(text)
    except ValueError as error:
        raise ManifestError(f"{context} must be an ISO date") from error
    return text


def contained_file(root: Path, relative_value: Any, context: str) -> Path:
    relative = Path(require_string(relative_value, context))
    if relative.is_absolute() or ".." in relative.parts:
        raise ManifestError(f"{context} must be a contained relative path")
    candidate = root / relative
    current = candidate
    while current != root:
        if current.is_symlink():
            raise ManifestError(f"{context} may not traverse a symlink")
        current = current.parent
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise ManifestError(f"{context} does not resolve to a retained file") from error
    if root not in resolved.parents or not resolved.is_file():
        raise ManifestError(f"{context} must resolve to a regular file inside the root")
    return resolved


def verify_hash(path: Path, expected: Any, context: str) -> None:
    digest = require_string(expected, context)
    if not SHA256.fullmatch(digest):
        raise ManifestError(f"{context} must be a lowercase SHA-256")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest:
        raise ManifestError(f"{context} does not match retained artifact")


def validate_command(root: Path, item: Any, context: str, *, expect_success: bool) -> None:
    if not isinstance(item, dict):
        raise ManifestError(f"{context} must be an object")
    require_keys(item, {"command", "exit_code", "artifact", "artifact_sha256"}, context)
    require_string(item["command"], f"{context}.command")
    exit_code = item["exit_code"]
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        raise ManifestError(f"{context}.exit_code must be an integer")
    if expect_success and exit_code != 0:
        raise ManifestError(f"{context}.exit_code must be zero")
    if not expect_success and exit_code == 0:
        raise ManifestError(f"{context}.exit_code must prove the broken variant failed")
    artifact = contained_file(root, item["artifact"], f"{context}.artifact")
    verify_hash(artifact, item["artifact_sha256"], f"{context}.artifact_sha256")


def audit(data: dict[str, Any], root: Path) -> dict[str, Any]:
    require_keys(
        data,
        {"schema_version", "subject", "source_revision", "research", "decisions", "validation", "review", "release"},
        "manifest",
    )
    reject_secret_keys(data)
    if data["schema_version"] != 1:
        raise ManifestError("schema_version must equal 1")

    subject = data["subject"]
    if not isinstance(subject, dict):
        raise ManifestError("subject must be an object")
    require_keys(subject, {"id", "version"}, "subject")
    require_string(subject["id"], "subject.id")
    require_string(subject["version"], "subject.version")

    revision = require_string(data["source_revision"], "source_revision")
    if not REVISION.fullmatch(revision):
        raise ManifestError("source_revision must be a lowercase 40-64 character hexadecimal revision")

    research = data["research"]
    if not isinstance(research, dict):
        raise ManifestError("research must be an object")
    require_keys(research, {"official_sources", "pain_catalog", "gaps"}, "research")
    sources = research["official_sources"]
    if not isinstance(sources, list) or not sources:
        raise ManifestError("research.official_sources must be a non-empty array")
    for index, source in enumerate(sources):
        context = f"research.official_sources[{index}]"
        if not isinstance(source, dict):
            raise ManifestError(f"{context} must be an object")
        require_keys(source, {"url", "verified_at"}, context)
        url = require_string(source["url"], f"{context}.url")
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ManifestError(f"{context}.url must be a credential-free HTTPS URL")
        require_date(source["verified_at"], f"{context}.verified_at")
    contained_file(root, research["pain_catalog"], "research.pain_catalog")
    if not isinstance(research["gaps"], list) or not all(isinstance(item, str) for item in research["gaps"]):
        raise ManifestError("research.gaps must be an array of strings")

    decisions = data["decisions"]
    if not isinstance(decisions, dict):
        raise ManifestError("decisions must be an object")
    require_keys(decisions, {"architecture", "threat_model", "migration"}, "decisions")
    for key in ("architecture", "threat_model", "migration"):
        contained_file(root, decisions[key], f"decisions.{key}")

    validation = data["validation"]
    if not isinstance(validation, dict):
        raise ManifestError("validation must be an object")
    require_keys(validation, {"commands", "baseline_delta", "adversarial_cases"}, "validation")
    commands = validation["commands"]
    if not isinstance(commands, list) or not commands:
        raise ManifestError("validation.commands must be a non-empty array")
    for index, item in enumerate(commands):
        validate_command(root, item, f"validation.commands[{index}]", expect_success=True)
    validate_command(root, validation["baseline_delta"], "validation.baseline_delta", expect_success=False)
    adversarial_cases = validation["adversarial_cases"]
    if not isinstance(adversarial_cases, int) or isinstance(adversarial_cases, bool) or adversarial_cases < 1:
        raise ManifestError("validation.adversarial_cases must be a positive integer")

    review = data["review"]
    if not isinstance(review, dict):
        raise ManifestError("review must be an object")
    require_keys(review, {"independent", "reviewer", "review_revision", "findings"}, "review")
    if not isinstance(review["independent"], bool):
        raise ManifestError("review.independent must be a boolean")
    if not isinstance(review["findings"], list) or not all(isinstance(item, str) for item in review["findings"]):
        raise ManifestError("review.findings must be an array of strings")
    if review["independent"]:
        require_string(review["reviewer"], "review.reviewer")
        review_revision = require_string(review["review_revision"], "review.review_revision")
        if review_revision != revision:
            raise ManifestError("review.review_revision must equal source_revision")
    elif review["reviewer"] is not None or review["review_revision"] is not None:
        raise ManifestError("self-review must use null reviewer and review_revision")

    release = data["release"]
    if not isinstance(release, dict):
        raise ManifestError("release must be an object")
    require_keys(release, {"authorized", "published"}, "release")
    if not isinstance(release["authorized"], bool) or not isinstance(release["published"], bool):
        raise ManifestError("release fields must be booleans")
    if release["published"] and not release["authorized"]:
        raise ManifestError("published evidence cannot exist without release authorization")
    if release["authorized"] and not review["independent"]:
        raise ManifestError("release authorization requires independent review")

    if release["authorized"]:
        status = "RELEASE-READY"
    elif review["independent"]:
        status = "REVIEWED"
    else:
        status = "CANDIDATE"
    return {"schema_version": 1, "status": status, "source_revision": revision}


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name in ("pain.md", "architecture.md", "threat.md", "migration.md", "pass.txt", "fail.txt"):
            (root / name).write_text(f"{name}\n", encoding="utf-8")

        def digest(name: str) -> str:
            return hashlib.sha256((root / name).read_bytes()).hexdigest()

        manifest = {
            "schema_version": 1,
            "subject": {"id": "fixture", "version": "1.0.0"},
            "source_revision": "a" * 40,
            "research": {
                "official_sources": [{"url": "https://example.com/spec", "verified_at": "2026-09-05"}],
                "pain_catalog": "pain.md",
                "gaps": [],
            },
            "decisions": {
                "architecture": "architecture.md",
                "threat_model": "threat.md",
                "migration": "migration.md",
            },
            "validation": {
                "commands": [
                    {
                        "command": "fixture-pass",
                        "exit_code": 0,
                        "artifact": "pass.txt",
                        "artifact_sha256": digest("pass.txt"),
                    }
                ],
                "baseline_delta": {
                    "command": "fixture-fail",
                    "exit_code": 1,
                    "artifact": "fail.txt",
                    "artifact_sha256": digest("fail.txt"),
                },
                "adversarial_cases": 1,
            },
            "review": {"independent": False, "reviewer": None, "review_revision": None, "findings": []},
            "release": {"authorized": False, "published": False},
        }
        assert audit(manifest, root)["status"] == "CANDIDATE"
        manifest["token"] = "never-print-this"
        try:
            audit(manifest, root)
        except ManifestError as error:
            assert "never-print-this" not in str(error)
        else:
            raise AssertionError("secret-bearing field was accepted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print(json.dumps({"status": "PASS", "self_test": True}, sort_keys=True))
        return 0
    if args.manifest is None:
        parser.error("manifest is required unless --self-test is used")
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ManifestError("root must be a directory")
        result = audit(load_manifest(args.manifest), root)
    except (OSError, ManifestError) as error:
        print(json.dumps({"status": "BLOCKED", "error": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
