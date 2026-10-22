#!/usr/bin/env python3
"""Observe canonical agent discovery/verdicts without changing validator output.

The validator's batch --json returns before its agent loop. This adapter calls
the same discovery/validation functions instead; it does not implement rules.
It never executes main(), populates a database, or modifies an agent file.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def observe(root: Path) -> dict:
    validator_path = root / "scripts" / "validate-skills-schema.py"
    spec = importlib.util.spec_from_file_location("agent_shadow_validator", validator_path)
    validator = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = validator
    spec.loader.exec_module(validator)
    agents = sorted(validator.find_agent_files(root))
    rows = []
    for path in agents:
        row = {"path": path.relative_to(root).as_posix(), "available": False}
        try:
            # Refuse external symlink targets rather than publishing their data.
            path.resolve().relative_to(root)
            before = path.read_bytes()
            result = validator.validate_agent(path)
            if path.read_bytes() != before:
                raise RuntimeError("agent changed during observation")
            match = validator.RE_FRONTMATTER.match(before.decode("utf-8"))
            row.update(
                available=True,
                content_sha256=hashlib.sha256(before).hexdigest(),
                frontmatter=match.group(1) if match else None,
                fatal=result.get("fatal"),
                errors=[] if "fatal" in result else result["errors"],
                warnings=[] if "fatal" in result else result["warnings"],
            )
        except Exception as exc:
            row["reason"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)
    return {
        "schema_version": "agent-python-observation/v1",
        "status": "complete" if rows and all(row["available"] for row in rows) else "partial",
        "validator_schema_version": validator.SCHEMA_VERSION,
        "validator_sha256": hashlib.sha256(validator_path.read_bytes()).hexdigest(),
        "discovered": len(agents),
        "rows": rows,
    }


if __name__ == "__main__":
    print(json.dumps(observe(Path(__file__).resolve().parents[1]), sort_keys=True))
