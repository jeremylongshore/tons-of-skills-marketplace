"""Offline production-contract tests for agent-systems-toolkit."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "skill-enhancers" / "agent-systems-toolkit"
EXPECTED_SKILLS = {"artifact-creator", "artifact-validator", "production-upgrade"}
EXPECTED_AGENTS = {
    "upgrade-architect",
    "upgrade-implementation-engineer",
    "upgrade-researcher",
    "upgrade-security-adversary",
    "upgrade-verification-engineer",
}
REQUIRED_SKILL_FIELDS = {
    "name",
    "description",
    "allowed-tools",
    "version",
    "author",
    "license",
    "compatibility",
    "tags",
}
REQUIRED_PLUGIN_AGENT_FIELDS = {
    "name",
    "description",
    "tools",
    "model",
    "color",
    "version",
    "author",
    "tags",
    "disallowedTools",
    "skills",
    "background",
}
BANNED_AGENT_FIELDS = {
    "capabilities",
    "expertise_level",
    "activation_priority",
    "activation_triggers",
    "type",
    "category",
    "compatible-with",
    "when_to_use",
}


def frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"missing frontmatter: {path}")
    _, raw, _body = text.split("---", 2)
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise AssertionError(f"frontmatter is not an object: {path}")
    return data


class ToolkitShapeTests(unittest.TestCase):
    def test_plugin_and_package_versions_match(self) -> None:
        manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        package = json.loads((PACK / "package.json").read_text(encoding="utf-8"))
        catalog = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text(encoding="utf-8"))
        entry = next(plugin for plugin in catalog["plugins"] if plugin["name"] == manifest["name"])
        self.assertEqual(manifest["name"], "agent-systems-toolkit")
        self.assertEqual(manifest["version"], package["version"])
        self.assertEqual(package["name"], "@intentsolutionsio/agent-systems-toolkit")
        self.assertEqual(manifest["description"], entry["description"])
        self.assertEqual(manifest["keywords"], entry["keywords"])

    def test_exact_skill_set_and_required_frontmatter(self) -> None:
        skill_paths = sorted((PACK / "skills").glob("*/SKILL.md"))
        self.assertEqual({path.parent.name for path in skill_paths}, EXPECTED_SKILLS)
        for path in skill_paths:
            data = frontmatter(path)
            self.assertEqual(data["name"], path.parent.name)
            self.assertFalse(REQUIRED_SKILL_FIELDS - set(data), path)
            self.assertNotIn("model", data, path)
            self.assertNotIn("Claude", str(data["compatibility"]), path)

    def test_portable_skill_tree_has_no_claude_runtime_tokens(self) -> None:
        for path in (PACK / "skills").rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("${CLAUDE_", text, path)
                self.assertNotIn("claude-opus-", text, path)
                self.assertNotIn("claude-sonnet-", text, path)

    def test_portable_skills_do_not_pre_authorize_network_or_shell(self) -> None:
        expected = {
            "artifact-creator": {"Read", "Write", "Edit"},
            "artifact-validator": {"Read"},
            "production-upgrade": {"Read", "Write", "Edit"},
        }
        for skill, tools in expected.items():
            data = frontmatter(PACK / "skills" / skill / "SKILL.md")
            declared = {item.strip() for item in str(data["allowed-tools"]).split(",")}
            self.assertEqual(declared, tools, skill)

    def test_skill_relative_links_resolve_inside_each_skill(self) -> None:
        pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for skill in sorted((PACK / "skills").iterdir()):
            if not skill.is_dir():
                continue
            root = skill.resolve()
            for path in skill.rglob("*.md"):
                for target in pattern.findall(path.read_text(encoding="utf-8")):
                    if "://" in target or target.startswith("#"):
                        continue
                    resolved = (path.parent / target.split("#", 1)[0]).resolve()
                    self.assertTrue(resolved == root or root in resolved.parents, (path, target))
                    self.assertTrue(resolved.exists(), (path, target))

    def test_capability_map_preserves_legacy_entrypoints_without_claiming_authority(self) -> None:
        data = json.loads((PACK / "capability-map.json").read_text(encoding="utf-8"))
        capabilities = data["capabilities"]
        self.assertEqual(len({item["id"] for item in capabilities}), len(capabilities))
        legacy = {name for item in capabilities for name in item["legacyEntrypoints"]}
        self.assertLessEqual(
            {"skill-creator", "agent-creator", "plugin-creator", "validate-plugin"},
            legacy,
        )
        self.assertIn("does not replace", data["authorityPolicy"])

    def test_eval_specs_cover_adversarial_and_non_trigger_cases(self) -> None:
        for path in sorted((PACK / "skills").glob("*/eval-spec.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            cases = data["test_cases"]
            self.assertIn("adversarial", {case["tier"] for case in cases}, path)
            self.assertIn("should_not_trigger", {case["trigger_expectation"] for case in cases}, path)


class ToolkitAgentTests(unittest.TestCase):
    def test_exact_agent_set_and_enterprise_fields(self) -> None:
        agent_paths = sorted((PACK / "agents").glob("*.md"))
        self.assertEqual({path.stem for path in agent_paths}, EXPECTED_AGENTS)
        for path in agent_paths:
            data = frontmatter(path)
            self.assertEqual(data["name"], path.stem)
            self.assertFalse(REQUIRED_PLUGIN_AGENT_FIELDS - set(data), path)
            self.assertFalse(BANNED_AGENT_FIELDS & set(data), path)
            self.assertEqual(data["model"], "inherit")
            self.assertEqual(data["skills"], ["production-upgrade"])
            self.assertFalse(data["background"])

    def test_only_implementation_agent_can_write(self) -> None:
        for path in sorted((PACK / "agents").glob("*.md")):
            data = frontmatter(path)
            tools = set(data["tools"])
            denied = set(data["disallowedTools"])
            if path.stem == "upgrade-implementation-engineer":
                self.assertLessEqual({"Write", "Edit"}, tools)
            else:
                self.assertFalse({"Write", "Edit"} & tools)
                self.assertLessEqual({"Write", "Edit"}, denied)

    def test_verifier_has_no_broad_or_mutating_shell_prefix(self) -> None:
        data = frontmatter(PACK / "agents" / "upgrade-verification-engineer.md")
        tools = set(data["tools"])
        prohibited = {
            "Bash(git:*)",
            "Bash(python3:*)",
            "Bash(node:*)",
            "Bash(pnpm:*)",
            "Bash(npm:*)",
        }
        self.assertFalse(prohibited & tools)
        self.assertIn("Bash(git status:*)", tools)
        self.assertNotIn("Bash(git add:*)", tools)
        self.assertNotIn("Bash(git push:*)", tools)
        self.assertNotIn("Bash(npm publish:*)", tools)

    def test_agents_delegate_to_canonical_role_packets(self) -> None:
        role_names = {
            "upgrade-researcher": "researcher.md",
            "upgrade-architect": "architect.md",
            "upgrade-implementation-engineer": "implementation-engineer.md",
            "upgrade-verification-engineer": "verification-engineer.md",
            "upgrade-security-adversary": "security-adversary.md",
        }
        for agent, role in role_names.items():
            text = (PACK / "agents" / f"{agent}.md").read_text(encoding="utf-8")
            self.assertIn(f"references/roles/{role}", text)
            self.assertTrue((PACK / "skills" / "production-upgrade" / "references" / "roles" / role).is_file())


class ToolkitHelperTests(unittest.TestCase):
    def run_helper(self, relative: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PACK / relative), "--self-test"],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_inventory_helper_self_test(self) -> None:
        result = self.run_helper("skills/artifact-validator/scripts/inventory_artifacts.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_evidence_helper_self_test(self) -> None:
        result = self.run_helper("skills/production-upgrade/scripts/audit_evidence.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
