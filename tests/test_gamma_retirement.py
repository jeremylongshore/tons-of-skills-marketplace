"""Keep the retired Gamma tutorials out of active installation surfaces."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETIRED = (
    "advanced-troubleshooting",
    "ci-integration",
    "common-errors",
    "core-feature",
    "core-workflow-a",
    "core-workflow-b",
    "cost-tuning",
    "data-handling",
    "debug-bundle",
    "deploy-integration",
    "deploy-pipeline",
    "enterprise-rbac",
    "hello-world",
    "incident-runbook",
    "install-auth",
    "known-pitfalls",
    "load-scale",
    "local-dev-loop",
    "migration-deep-dive",
    "multi-env-setup",
    "observability",
    "performance-tuning",
    "primary-workflow",
    "prod-checklist",
    "rate-limits",
    "reference-architecture",
    "reliability-patterns",
    "sdk-patterns",
    "security-basics",
    "upgrade-migration",
    "webhooks-events",
)


class GammaRetirementTests(unittest.TestCase):
    def test_source_scaffolds_and_curated_copies_cannot_be_installed(self):
        for relative in (
            "plugins/saas-packs/gamma-pack",
            "plugins/saas-packs/skill-databases/gamma",
            "marketplace/src/pages/learn/gamma",
        ):
            path = ROOT / relative
            populated = path.is_file() or path.is_symlink()
            if path.is_dir():
                for entry in path.rglob("*"):
                    if not (entry.is_file() or entry.is_symlink()):
                        continue
                    parts = entry.relative_to(path).parts
                    # Private historical sidecars may survive a checkout. They
                    # are not installable content and must not be deleted to
                    # satisfy this guard. Tracked documents never qualify:
                    # check-ignore deliberately ignores tracked index entries.
                    historical = (
                        relative == "plugins/saas-packs/gamma-pack"
                        and len(parts) > 1
                        and parts[0] == "000-docs"
                        and not entry.is_symlink()
                    )
                    if historical:
                        ignored = subprocess.run(
                            ["git", "check-ignore", "--quiet", "--", entry.relative_to(ROOT).as_posix()],
                            cwd=ROOT,
                            capture_output=True,
                        )
                        if ignored.returncode == 0:
                            continue
                    populated = True
                    break
            self.assertFalse(populated, relative)
        self.assertEqual(list((ROOT / "skills/.curated").glob("gamma-*")), [])
        catalog = json.loads((ROOT / ".claude-plugin/marketplace.extended.json").read_text())
        self.assertNotIn("gamma-pack", {p["name"] for p in catalog["plugins"]})
        vendors = json.loads((ROOT / "marketplace/src/data/vendor-packs.json").read_text())
        self.assertNotIn("gamma", {v["id"] for v in vendors["vendors"]})
        self.assertNotIn("plugins/saas-packs/gamma-pack:", (ROOT / "pnpm-lock.yaml").read_text())

    def test_active_generated_projections_do_not_advertise_retired_installation(self):
        for relative, token in (
            (".claude-plugin/marketplace.json", '"name": "gamma-pack"'),
            ("marketplace/src/data/catalog.json", '"slug": "gamma-pack"'),
            ("marketplace/src/data/skills-index.json", '"parentPlugin": "gamma-pack"'),
            ("marketplace/src/data/skills-catalog.json", '"name": "gamma-pack"'),
            ("marketplace/src/data/unified-search-index.json", '"name": "gamma-pack"'),
            ("marketplace/src/data/npm-stats.json", "@intentsolutionsio/gamma-pack"),
            ("marketplace/src/data/npm-stats.json", "@intentsolutionsio/gamma-skill-md-pack"),
            ("skills/.curated/MANIFEST.json", "plugins/saas-packs/gamma-pack/"),
            ("freshie/grades.csv", "plugins/saas-packs/gamma-pack/"),
            ("freshie/disposition-ledger.json", "plugins/saas-packs/gamma-pack/"),
        ):
            with self.subTest(path=relative):
                self.assertNotIn(token, (ROOT / relative).read_text())

    def test_legacy_generator_refuses_retirement_before_writing_anything(self):
        generator = ROOT / "plugins/saas-packs/scripts/generate-skill-db.py"
        for name in ("gamma", "Gamma", " GLEAN "):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                result = subprocess.run(
                    ["python3", str(generator), name, "Gamma", "pro"],
                    cwd=folder,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("generation is retired", result.stderr)
                self.assertEqual(list(Path(folder).iterdir()), [])

    def test_retired_urls_remain_explicit_404_decisions(self):
        # Exercise the real policy against the current live universe. Explicit
        # retirement must not fall back to another vendor or a section index.
        script = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {decide,loadLiveUniverse} from './marketplace/scripts/build-retired-path-redirects.mjs';
const overrides=JSON.parse(readFileSync('marketplace/src/data/retired-path-overrides.json')).overrides;
const paths=JSON.parse(process.argv[1]);
const live=loadLiveUniverse();
assert.equal(decide('/plugins/gamma-pack',live,{}).status,301);
for(const path of paths){
  assert.equal(live.routes.has(path+'/'),false,path+' is still live');
  const decision=decide(path,live,overrides);
  assert.equal(decision.status,404,path);
  assert.equal(decision.to,undefined,path);
  assert.equal(decision.rule,'reviewed-keep-404',path);
}
"""
        paths = ["/learn/gamma", "/plugins/gamma-pack", *["/skills/gamma-" + name for name in RETIRED]]
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script, json.dumps(paths)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
