"""Retirement must prevent scaffold recreation and misleading route fallbacks."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_ROUTES = (
    "/plugins/framer-pack",
    "/learn/framer",
    "/skills/framer-ci-integration",
    "/skills/framer-common-errors",
    "/skills/framer-core-feature",
    "/skills/framer-core-workflow-a",
    "/skills/framer-core-workflow-b",
    "/skills/framer-cost-tuning",
    "/skills/framer-debug-bundle",
    "/skills/framer-deploy-integration",
    "/skills/framer-deploy-pipeline",
    "/skills/framer-hello-world",
    "/skills/framer-install-auth",
    "/skills/framer-local-dev-loop",
    "/skills/framer-performance-tuning",
    "/skills/framer-primary-workflow",
    "/skills/framer-prod-checklist",
    "/skills/framer-rate-limits",
    "/skills/framer-reference-architecture",
    "/skills/framer-sdk-patterns",
    "/skills/framer-security-basics",
    "/skills/framer-upgrade-migration",
    "/skills/framer-webhooks-events",
)


class FramerRetirementTests(unittest.TestCase):
    def test_legacy_generator_refuses_before_creating_files(self):
        script = ROOT / "plugins/saas-packs/scripts/generate-skill-db.py"
        for vendor in ("framer", "Framer", " FRAMER "):
            with self.subTest(vendor=vendor), tempfile.TemporaryDirectory() as folder:
                result = subprocess.run(
                    ["python3", str(script), vendor, "Framer", "flagship"],
                    cwd=folder,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("generation is retired", result.stderr)
                self.assertEqual(list(Path(folder).iterdir()), [])

    def test_every_reviewed_route_stays_404_in_the_real_policy(self):
        script = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {decide,loadLiveUniverse} from './marketplace/scripts/build-retired-path-redirects.mjs';
const expected=JSON.parse(process.argv[1]);
const overrides=JSON.parse(readFileSync('marketplace/src/data/retired-path-overrides.json')).overrides;
const actual=Object.keys(overrides).filter(p=>p==='/learn/framer'||p==='/plugins/framer-pack'||p.startsWith('/skills/framer-'));
assert.deepEqual(actual.sort(),expected.sort());
const live=loadLiveUniverse();
assert.equal(decide('/plugins/framer-pack',live,{}).status,301);
for(const path of expected){
  assert.equal(live.routes.has(path+'/'),false,path+' remains live');
  const decision=decide(path,live,overrides);
  assert.equal(decision.status,404,path);
  assert.equal(decision.to,undefined,path);
  assert.equal(decision.rule,'reviewed-keep-404',path);
}
"""
        result = subprocess.run(
            ["node", "--input-type=module", "-e", script, json.dumps(REVIEWED_ROUTES)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
