#!/usr/bin/env python3
"""CoreWeave pack gate: canonical schemas, installed links, deterministic fixtures, secrets.

Does not invoke model providers or platform APIs. A passing offline contract is not
behavioral/production certification. Gitleaks must be installed; absence fails closed.
"""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import tarfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins/saas-packs/coreweave-pack"
HELPERS = {
    "core-workflow-a": "review-inference.py",
    "core-workflow-b": "review-training.py",
    "enterprise-rbac": "review-access.py",
    "ci-integration": "review-workflow.py",
    "incident-runbook": "review-incident.py",
    "workload-health": "check-health.py",
    "cks-provisioning": "review-plan.py",
    "caios-stage-model": "review-transfer.py",
}
FLAGSHIPS = {
    "fabric-diagnostics": "fabric-check.py",
    "gpu-node-forensics": "triage.py",
    "gpu-cost-leak-hunter": "rank-and-report.py",
}


def command(args, **kwargs):
    p = subprocess.run(args, cwd=kwargs.pop("cwd", ROOT), text=True, capture_output=True, timeout=180, **kwargs)
    if p.returncode:
        raise ValueError(f"Command failed ({p.returncode}): {args[0]} {args[1]}\n{p.stderr[:2000]}{p.stdout[:2000]}")
    return p.stdout


def links(root):
    errors = []
    for path in root.rglob("*.md"):
        for target in re.findall(r"\]\(([^)\n]+)\)", path.read_text()):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            value = target.split("#", 1)[0].strip("<>")
            resolved = (path.parent / value).resolve()
            if not resolved.exists() or not resolved.is_relative_to(root.resolve()):
                errors.append(str(path.relative_to(root)) + ": " + target)
    return errors


def unpack_package(archive, destination, source):
    """Accept only byte-identical regular files under package/; never follow links."""
    included = set()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            parts = PurePosixPath(member.name).parts
            if not parts or parts[0] != "package" or ".." in parts or member.name.startswith("/"):
                raise ValueError("Unsafe package path")
            if member.isdir():
                continue
            if not member.isfile() or len(parts) < 2:
                raise ValueError("Package links and special files are forbidden")
            relative = Path(*parts[1:])
            if relative in included:
                raise ValueError("Duplicate package file")
            original = source / relative
            if not original.resolve().is_relative_to(source.resolve()) or any(
                parent.is_symlink() for parent in [original, *original.parents] if parent != source.parent
            ):
                raise ValueError("Package source escapes through a link")
            if not original.is_file() or member.size != original.stat().st_size:
                raise ValueError("Package file is missing or differs from source")
            with bundle.extractfile(member) as stream:
                payload = stream.read()
            if payload != original.read_bytes():
                raise ValueError("Package bytes differ from source")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            included.add(relative)
    required = set()
    for name in ("skills", "agents", "shared", "scripts", "docs", ".claude-plugin"):
        for path in (source / name).rglob("*"):
            relative = path.relative_to(source)
            if (
                path.is_file()
                and not any(part in {"__pycache__", ".terraform", "node_modules", ".git"} for part in relative.parts)
                and path.suffix != ".pyc"
            ):
                required.add(relative)
    required.update(Path(name) for name in ("README.md", "package.json", "QUALITY.md", "offline-results.json"))
    missing = required - included
    if missing:
        raise ValueError("Package omits required files: " + ", ".join(map(str, sorted(missing))))
    return len(included)


def installed_package(scratch):
    archive_dir = scratch / "archive"
    archive_dir.mkdir()
    command(["npm", "pack", str(PACK), "--ignore-scripts", "--json", "--pack-destination", str(archive_dir)])
    archives = list(archive_dir.glob("*.tgz"))
    if len(archives) != 1 or archives[0].is_symlink():
        raise ValueError("Expected one regular npm package archive")
    installed = scratch / "installed"
    count = unpack_package(archives[0], installed, PACK)
    failures = links(installed)
    for skill in (installed / "skills").iterdir():
        failures.extend(links(skill))
    if failures:
        raise ValueError("Installed references failed: " + "; ".join(failures))
    return installed, {
        "mode": "npm pack --ignore-scripts; byte-checked extraction; installed fixture replay",
        "files": count,
        "archive_sha256": hashlib.sha256(archives[0].read_bytes()).hexdigest(),
        "references": "PASS: plugin and standalone skill boundaries",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="Write a local result receipt; not a certification")
    parser.add_argument("--gitleaks", default="gitleaks", help="Installed gitleaks executable")
    args = parser.parse_args()
    errors = []
    receipt = {
        "schema": "coreweave-pack-validation/v1",
        "skills": [],
        "agents": [],
        "eval_specs": [],
        "behavioral_evaluation": "NOT RUN",
        "live_account_validation": "NOT RUN",
    }
    spec = importlib.util.spec_from_file_location("cw_canonical_validator", ROOT / "scripts/validate-skills-schema.py")
    canonical = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = canonical
    spec.loader.exec_module(canonical)
    skills = sorted((PACK / "skills").glob("*/SKILL.md"))
    if len(skills) != 26:
        errors.append("Expected exactly 26 maintained skills; review inventory before changing this contract.")
    for skill in skills:
        result = canonical.validate_skill(skill, tier=canonical.TIER_MARKETPLACE)
        fm, body = canonical.parse_frontmatter(skill.read_text())
        grade = canonical.grade_skill(skill, body, fm)
        receipt["skills"].append(
            {
                "path": str(skill.relative_to(ROOT)),
                "errors": result.get("errors", []),
                "warnings": result.get("warnings", []),
                "grade": grade.get("grade"),
                "score": grade.get("score"),
            }
        )
        errors.extend([str(skill) + ": " + e for e in result.get("errors", [])])
        if result.get("fatal"):
            errors.append(str(skill) + ": " + result["fatal"])
        text = skill.read_text().lower()
        if "community-contributed" not in text or "not affiliated" not in text:
            errors.append(str(skill) + ": missing disclaimer")
        if not (skill.parent / "docs/BLUEPRINT.md").is_file():
            errors.append(str(skill) + ": missing blueprint")
        if skill.parent.name.removeprefix("coreweave-") in HELPERS:
            if (skill.parent / "scripts/review_common.py").read_bytes() != (
                PACK / "shared/review_common.py"
            ).read_bytes():
                errors.append(str(skill) + ": shared evidence helper drift")
    errors.extend(links(PACK))
    # Curated installations contain one skill, without the surrounding plugin tree.
    for skill in skills:
        errors.extend(links(skill.parent))
    for agent in sorted((PACK / "agents").glob("*.md")):
        result = canonical.validate_agent(agent)
        receipt["agents"].append({"path": str(agent.relative_to(ROOT)), **result})
        errors.extend([str(agent) + ": " + e for e in result.get("errors", [])])
        if result.get("fatal"):
            errors.append(str(agent) + ": " + result["fatal"])
        fm = yaml.safe_load(agent.read_text().split("---", 2)[1])
        for name in fm.get("skills", []):
            local = name.removeprefix("coreweave-pack:")
            if not (PACK / "skills" / local / "SKILL.md").is_file():
                errors.append(str(agent) + ": unresolved skill " + name)
        if any(fm.get(k) for k in ("hooks", "mcpServers", "permissionMode")):
            errors.append(str(agent) + ": runtime-ignored plugin-agent security fields")
    manifest_result = canonical.validate_plugin_json(PACK / ".claude-plugin/plugin.json")
    errors.extend(manifest_result.get("errors", []))
    # No live connector or execution hook is needed for this offline product.
    # Fail rather than silently calling a newly introduced unreviewed component absent.
    present = list(PACK.rglob("hooks.json")) + list(PACK.rglob(".mcp.json"))
    manifest = json.loads((PACK / ".claude-plugin/plugin.json").read_text())
    if present or manifest.get("hooks") or manifest.get("mcpServers"):
        errors.append(
            "New hook/MCP surface requires explicit component validation before this offline-only gate can accept it."
        )
    for skill in skills:
        fm = yaml.safe_load(skill.read_text().split("---", 2)[1])
        if fm.get("hooks") or fm.get("mcpServers"):
            errors.append(str(skill) + ": inline execution surface not reviewed")
    receipt["hooks"] = "ABSENT: offline helpers need no automatic command interception"
    receipt["mcp"] = "ABSENT: account access is not required; official MCP is documented, not auto-connected"
    try:
        command([sys.executable, str(PACK / "scripts/sync-cost-gates.py"), "--check"])
        specs = sorted((PACK / "skills").glob("*/eval-spec.yaml"))
        if len(specs) != len(HELPERS) + len(FLAGSHIPS):
            raise ValueError("Eval inventory does not match offline adapters")
        with tempfile.TemporaryDirectory(prefix="cw-offline-") as directory:
            scratch = Path(directory)
            installed, receipt["distribution"] = installed_package(scratch)
            (scratch / "sitecustomize.py").write_text(
                'import sys\ndef guard(event,args):\n if event in ("socket.connect","socket.getaddrinfo","subprocess.Popen","os.system"):\n  raise RuntimeError("offline boundary")\nsys.addaudithook(guard)\n'
            )
            env = {"PATH": os.defpath, "PYTHONPATH": str(scratch), "PYTHONDONTWRITEBYTECODE": "1"}
            for source_spec in specs:
                path = installed / source_spec.relative_to(PACK)
                data = yaml.safe_load(path.read_text())
                name = path.parent.name
                slug = name.removeprefix("coreweave-")
                criteria = {c["id"] for c in data["criteria"]}
                cases = data["test_cases"]
                if (
                    data["skill_name"] != name
                    or len(criteria) != len(data["criteria"])
                    or len({c["id"] for c in cases}) != len(cases)
                ):
                    raise ValueError(name + ": invalid or duplicate eval identities")
                if any(not set(c["criteria_ids"]) <= criteria for c in cases):
                    raise ValueError(name + ": unknown criterion reference")
                package = json.loads(command(["pnpm", "exec", "j-rig", "check", str(path.parent), "--json"]))
                if package.get("summary", {}).get("errors", 1):
                    raise ValueError(name + ": package integrity failed")
                passed = 0
                if slug in HELPERS:
                    fixtures = json.loads((path.parent / "tests/fixtures/cases.json").read_text())
                    for fixture in fixtures:
                        if fixture["id"] not in {c["id"] for c in cases}:
                            raise ValueError(name + ": orphan fixture")
                        source = scratch / "input.json"
                        source.write_text(json.dumps(fixture["input"]))
                        p = subprocess.run(
                            [
                                sys.executable,
                                str(path.parent / "scripts" / HELPERS[slug]),
                                "--input",
                                str(source),
                                "--as-of",
                                "2026-11-05T12:01:00Z",
                            ],
                            env=env,
                            cwd=scratch,
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        actual = json.loads(p.stdout)
                        expected = fixture["expected_status"]
                        if (
                            actual["status"] != expected
                            or p.returncode != {"reviewed": 0, "blocked": 2, "incomplete": 3}[expected]
                            or p.stderr
                        ):
                            raise ValueError(name + ": fixture failed " + fixture["id"])
                        if not set(fixture["expected_codes"]) <= {f["code"] for f in actual["findings"]}:
                            raise ValueError(name + ": missing expected refusal " + fixture["id"])
                        for key, expected_value in fixture.get("expected_observations", {}).items():
                            if actual["observations"].get(key) != expected_value:
                                raise ValueError(name + ": incorrect observation " + fixture["id"] + ": " + key)
                        if "SECRET_CANARY" in p.stdout:
                            raise ValueError(name + ": injected instruction escaped evidence boundary")
                        passed += 1
                else:
                    # Existing raw-log/arithmetic tools retain their original self-test adapters.
                    command(
                        [sys.executable, str(path.parent / "scripts" / FLAGSHIPS[slug]), "--self-test"],
                        env=env,
                        cwd=scratch,
                    )
                    passed = 1
                receipt["eval_specs"].append(
                    {
                        "skill": name,
                        "spec_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "package_integrity": "PASS",
                        "offline_contract_cases": passed,
                        "model_judged_criteria": "NOT RUN",
                        "coverage": "deterministic helper contract only; trigger/model judgments not established",
                    }
                )
            executable = shutil.which(args.gitleaks)
            if not executable:
                raise ValueError("gitleaks executable missing; secret scan cannot be skipped")
            command([executable, "dir", str(PACK), "--redact", "--no-banner"])
            receipt["gitleaks"] = "PASS"
    except (ValueError, KeyError, OSError, tarfile.TarError, subprocess.TimeoutExpired) as exc:
        errors.append(str(exc))
    receipt["errors"] = errors
    receipt["status"] = "FAIL" if errors else "PASS (static and offline contracts only)"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(receipt, indent=2, default=str) + "\n")
    print(
        json.dumps(
            {
                "status": receipt["status"],
                "skills": len(skills),
                "eval_specs_checked": len(receipt["eval_specs"]),
                "errors": errors,
            },
            indent=2,
        )
    )
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
