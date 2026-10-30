"""Retirement guard and real npm archive integrity for the Langfuse operator pack."""

import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins/saas-packs/langfuse-pack"
GENERATOR = ROOT / "plugins/saas-packs/scripts/generate-skill-db.py"
OPERATORS = {
    "langfuse-trace-ingestion-medic",
    "langfuse-experiment-guardian",
    "langfuse-cost-forensics",
    "langfuse-prompt-release-guardian",
    "langfuse-data-boundary-auditor",
}


class LangfusePackIntegrityTests(unittest.TestCase):
    def test_legacy_scaffolding_cannot_be_regenerated_even_with_case_variants(self):
        for vendor in ("langfuse", "Langfuse", " LANGFUSE "):
            with tempfile.TemporaryDirectory() as folder:
                result = subprocess.run(
                    ["python3", str(GENERATOR), vendor, "Langfuse", "flagship+"],
                    cwd=folder,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("generation is retired", result.stderr)
                self.assertEqual(list(Path(folder).iterdir()), [])
        self.assertFalse((ROOT / "plugins/saas-packs/skill-databases/langfuse").exists())

    def test_real_archive_contains_exact_operator_set_without_local_caches(self):
        # Build from indexed source in scratch, then introduce a cache that npm
        # must exclude. No source tree, provider or published package is mutated.
        paths = subprocess.check_output(
            ["git", "ls-files", "--", str(PACK.relative_to(ROOT))], cwd=ROOT, text=True
        ).splitlines()
        with tempfile.TemporaryDirectory() as folder:
            scratch = Path(folder) / "source"
            scratch.mkdir()
            for relative in paths:
                source = ROOT / relative
                target = scratch / source.relative_to(PACK)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            cache = scratch / "skills/langfuse-cost-forensics/scripts/__pycache__/synthetic.pyc"
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(b"synthetic cache must not ship")
            result = subprocess.run(
                ["npm", "pack", "--ignore-scripts", "--json", "--pack-destination", folder],
                cwd=scratch,
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(len(payload), 1)
            info = payload[0] if isinstance(payload, list) else next(iter(payload.values()))
            self.assertEqual(info["name"], "@intentsolutionsio/langfuse-pack")
            self.assertEqual(info["version"], "2.0.0")
            with tarfile.open(Path(folder) / info["filename"], "r:gz") as archive:
                files = [member for member in archive.getmembers() if member.isfile()]
                names = [member.name for member in files]
                self.assertEqual(len(names), len(set(names)))
                actual = {
                    name.split("/")[2]
                    for name in names
                    if name.startswith("package/skills/") and name.endswith("/SKILL.md")
                }
                self.assertEqual(actual, OPERATORS)
                self.assertFalse(any("__pycache__" in name or name.endswith((".pyc", ".pyo")) for name in names))
                for member in files:
                    relative = member.name.removeprefix("package/")
                    self.assertNotEqual(relative, member.name)
                    self.assertNotIn("..", Path(relative).parts)
                    source = scratch / relative
                    self.assertTrue(source.is_file(), relative)
                    self.assertEqual(archive.extractfile(member).read(), source.read_bytes(), relative)
                manifest = json.load(archive.extractfile("package/.claude-plugin/plugin.json"))
                self.assertEqual(manifest["name"], "langfuse-pack")
                self.assertEqual(manifest["version"], "2.0.0")


if __name__ == "__main__":
    unittest.main()
