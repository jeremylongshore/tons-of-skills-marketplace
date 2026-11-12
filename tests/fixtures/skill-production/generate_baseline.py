"""Maintainer-only oracle capture from immutable original Git blobs, never new helpers."""

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
BASE = "ed4778951a4007d1ca56781a468233212e371502"
EXPECTED_VALIDATOR = "fb202d6362f8e33c55654ff8b278dbe5bccd122b297bccb3ca15a6aac3358595"
EXPECTED_AGENT = "646c4bd196086c3102b1c9604c884787481db39494d0c1c286e97b9f992bfaf6"


def main():
    inputs = Path(__file__).with_name("inputs.json").read_bytes()
    blobs = {}
    for name, expected in [("validate-skills-schema.py", EXPECTED_VALIDATOR), ("agent_body_tools.py", EXPECTED_AGENT)]:
        data = subprocess.check_output(["git", "--no-replace-objects", "show", f"{BASE}:scripts/{name}"], cwd=ROOT)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"original source identity mismatch: {name}")
        blobs[name] = data
    with tempfile.TemporaryDirectory(prefix="skill-production-original-") as temp:
        root = Path(temp)
        for name, data in blobs.items():
            (root / name).write_bytes(data)
        spec = importlib.util.spec_from_file_location(
            "pinned_original_skill_validator", root / "validate-skills-schema.py"
        )
        original = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(original)
        cases = []
        for case in json.loads(inputs):
            errors, warnings, infos = original.validate_tier2_production_gate(
                Path("unused"), case["body"], case["frontmatter"]
            )
            cases.append({"id": case["id"], "errors": errors, "warnings": warnings, "infos": infos})
    original_tree = ast.parse(blobs["validate-skills-schema.py"])
    names = {"parse_allowed_tools", "_tier2_extract_declared_base_tools", "validate_tier2_production_gate"}
    functions = {
        n.name: hashlib.sha256(
            ast.get_source_segment(blobs["validate-skills-schema.py"].decode(), n).encode()
        ).hexdigest()
        for n in original_tree.body
        if isinstance(n, ast.FunctionDef) and (n.name in names or n.name.startswith("tier2_check_"))
    }
    license_bytes = subprocess.check_output(["git", "--no-replace-objects", "show", f"{BASE}:LICENSE"], cwd=ROOT)
    if hashlib.sha256(license_bytes).hexdigest() != "32ef688a3e3c3b0c811cb5909788e1e4af711f2a672ee3a9941702e6603aa33b":
        raise ValueError("original MIT license identity mismatch")
    receipt = {
        "original_function_sha256": functions,
        "license_sha256": hashlib.sha256(license_bytes).hexdigest(),
        "source_commit": BASE,
        "source_hashes": {name: hashlib.sha256(data).hexdigest() for name, data in blobs.items()},
        "inputs_sha256": hashlib.sha256(inputs).hexdigest(),
        "scope": "Exact original five-check results; no runtime-safety or whole-schema equivalence claim",
        "cases": cases,
    }
    Path(__file__).with_name("expected.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
