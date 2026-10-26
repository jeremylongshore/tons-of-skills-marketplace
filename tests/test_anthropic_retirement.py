"""Retirement must prevent scaffold recreation and misleading route fallbacks."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_ROUTES = (
    "/learn/anthropic",
    "/plugins/anthropic-pack",
    "/skills/anth-advanced-troubleshooting",
    "/skills/anth-architecture-variants",
    "/skills/anth-ci-integration",
    "/skills/anth-common-errors",
    "/skills/anth-core-workflow-a",
    "/skills/anth-core-workflow-b",
    "/skills/anth-cost-tuning",
    "/skills/anth-data-handling",
    "/skills/anth-debug-bundle",
    "/skills/anth-deploy-integration",
    "/skills/anth-enterprise-rbac",
    "/skills/anth-hello-world",
    "/skills/anth-incident-runbook",
    "/skills/anth-install-auth",
    "/skills/anth-known-pitfalls",
    "/skills/anth-load-scale",
    "/skills/anth-local-dev-loop",
    "/skills/anth-migration-deep-dive",
    "/skills/anth-multi-env-setup",
    "/skills/anth-observability",
    "/skills/anth-performance-tuning",
    "/skills/anth-policy-guardrails",
    "/skills/anth-prod-checklist",
    "/skills/anth-rate-limits",
    "/skills/anth-reference-architecture",
    "/skills/anth-reliability-patterns",
    "/skills/anth-sdk-patterns",
    "/skills/anth-security-basics",
    "/skills/anth-upgrade-migration",
    "/skills/anth-webhooks-events",
    "/skills/anthropic-advanced-troubleshooting",
    "/skills/anthropic-architecture-variants",
    "/skills/anthropic-ci-integration",
    "/skills/anthropic-common-errors",
    "/skills/anthropic-core-feature",
    "/skills/anthropic-cost-tuning",
    "/skills/anthropic-data-handling",
    "/skills/anthropic-debug-bundle",
    "/skills/anthropic-deploy-pipeline",
    "/skills/anthropic-enterprise-rbac",
    "/skills/anthropic-hello-world",
    "/skills/anthropic-incident-runbook",
    "/skills/anthropic-install-auth",
    "/skills/anthropic-known-pitfalls",
    "/skills/anthropic-load-scale",
    "/skills/anthropic-local-dev-loop",
    "/skills/anthropic-migration-deep-dive",
    "/skills/anthropic-multi-env-setup",
    "/skills/anthropic-observability",
    "/skills/anthropic-performance-tuning",
    "/skills/anthropic-policy-guardrails",
    "/skills/anthropic-primary-workflow",
    "/skills/anthropic-prod-checklist",
    "/skills/anthropic-rate-limits",
    "/skills/anthropic-reference-architecture",
    "/skills/anthropic-reliability-patterns",
    "/skills/anthropic-sdk-patterns",
    "/skills/anthropic-security-basics",
    "/skills/anthropic-upgrade-migration",
    "/skills/anthropic-webhooks-events",
)


class AnthropicRetirementTests(unittest.TestCase):
    def test_legacy_generator_refuses_before_creating_files(self):
        script = ROOT / "plugins/saas-packs/scripts/generate-skill-db.py"
        for vendor in ("anthropic", "Anthropic", " ANTHROPIC "):
            with self.subTest(vendor=vendor), tempfile.TemporaryDirectory() as folder:
                result = subprocess.run(
                    ["python3", str(script), vendor, "Anthropic", "flagship"],
                    cwd=folder,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("generation is retired", result.stderr)
                self.assertEqual(list(Path(folder).iterdir()), [])

    def test_cowork_cards_reference_published_downloads(self):
        editorial = json.loads((ROOT / "marketplace/src/data/cowork-packs.json").read_text())
        published = {
            row["name"] for row in json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())["plugins"]
        }
        self.assertEqual(editorial["meta"]["totalPacks"], len(editorial["packs"]))
        for card in editorial["packs"]:
            if card.get("isSaasPack"):
                self.assertIn(card["packName"], published, card["id"])

    def test_every_reviewed_route_stays_404_in_the_real_policy(self):
        script = """
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {decide,loadLiveUniverse} from './marketplace/scripts/build-retired-path-redirects.mjs';
const expected=JSON.parse(process.argv[1]);
const overrides=JSON.parse(readFileSync('marketplace/src/data/retired-path-overrides.json')).overrides;
const actual=Object.keys(overrides).filter(p=>p==='/learn/anthropic'||p==='/plugins/anthropic-pack'||p.startsWith('/skills/anthropic-')||p.startsWith('/skills/anth-'));
assert.deepEqual(actual.sort(),expected.sort());
const live=loadLiveUniverse();
assert.equal(decide('/plugins/anthropic-pack',live,{}).status,301);
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
