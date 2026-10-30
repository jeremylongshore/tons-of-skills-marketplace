"""Retirement must prevent scaffold recreation and misleading route fallbacks."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_ROUTES = (
    "/plugins/apple-notes-pack",
    "/learn/apple-notes",
    "/skills/apple-notes-advanced-troubleshooting",
    "/skills/apple-notes-ci-integration",
    "/skills/apple-notes-common-errors",
    "/skills/apple-notes-core-feature",
    "/skills/apple-notes-core-workflow-a",
    "/skills/apple-notes-core-workflow-b",
    "/skills/apple-notes-cost-tuning",
    "/skills/apple-notes-data-handling",
    "/skills/apple-notes-debug-bundle",
    "/skills/apple-notes-deploy-integration",
    "/skills/apple-notes-deploy-pipeline",
    "/skills/apple-notes-enterprise-rbac",
    "/skills/apple-notes-hello-world",
    "/skills/apple-notes-incident-runbook",
    "/skills/apple-notes-install-auth",
    "/skills/apple-notes-known-pitfalls",
    "/skills/apple-notes-load-scale",
    "/skills/apple-notes-local-dev-loop",
    "/skills/apple-notes-migration-deep-dive",
    "/skills/apple-notes-multi-env-setup",
    "/skills/apple-notes-observability",
    "/skills/apple-notes-performance-tuning",
    "/skills/apple-notes-primary-workflow",
    "/skills/apple-notes-prod-checklist",
    "/skills/apple-notes-rate-limits",
    "/skills/apple-notes-reference-architecture",
    "/skills/apple-notes-reliability-patterns",
    "/skills/apple-notes-sdk-patterns",
    "/skills/apple-notes-security-basics",
    "/skills/apple-notes-upgrade-migration",
    "/skills/apple-notes-webhooks-events",
)


class AppleNotesRetirementTests(unittest.TestCase):
    def test_legacy_generator_refuses_before_creating_files(self):
        script = ROOT / "plugins/saas-packs/scripts/generate-skill-db.py"
        for vendor in ("apple-notes", "Apple-Notes", " APPLE-NOTES "):
            with self.subTest(vendor=vendor), tempfile.TemporaryDirectory() as folder:
                result = subprocess.run(
                    ["python3", str(script), vendor, "Apple Notes", "flagship"],
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
const actual=Object.keys(overrides).filter(p=>p==='/learn/apple-notes'||p==='/plugins/apple-notes-pack'||p.startsWith('/skills/apple-notes-'));
assert.deepEqual(actual.sort(),expected.sort());
const live=loadLiveUniverse();
assert.equal(decide('/plugins/apple-notes-pack',live,{}).status,301);
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
