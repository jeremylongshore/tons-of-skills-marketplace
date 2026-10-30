"""Hostile regression tests for PR prescreen plugin scoping."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


_SCRIPT = Path(__file__).with_name("scope.py")
_SPEC = importlib.util.spec_from_file_location("_pr_prescreen_scope", _SCRIPT)
_SCOPE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _SCOPE
_SPEC.loader.exec_module(_SCOPE)


def _manifest(plugin: Path, value: dict | None = None) -> Path:
    path = plugin / ".claude-plugin" / "plugin.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value or {"name": plugin.name}), encoding="utf-8")
    return path


def _mcp(plugin: Path, value: dict | None = None) -> Path:
    path = plugin / ".mcp.json"
    path.write_text(
        json.dumps(
            value
            or {
                "mcpServers": {
                    plugin.name: {
                        "name": plugin.name,
                        "type": "stdio",
                        "command": "node",
                        "args": [],
                        "env": {},
                        "description": "A canonical test MCP server",
                        "version": "1.0.0",
                        "enabled": True,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    return path


def _catalog(root: Path, sources: list[str]) -> Path:
    path = root / ".claude-plugin/marketplace.extended.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"plugins": [{"source": f"./{source}"} for source in sources]}),
        encoding="utf-8",
    )
    return path


def _supplement(results: list[dict], changed_dirs: list[str], *, pr_root: Path) -> tuple[list[dict], list[str]]:
    _catalog(pr_root, changed_dirs)
    return _SCOPE.supplement_results(results, changed_dirs, pr_root=pr_root)


def _workflow_step(name: str) -> str:
    workflow_path = _SCRIPT.parents[2] / ".github/workflows/pr-prescreen.yml"
    workflow = yaml.safe_load(workflow_path.read_text())
    return next(step["run"] for step in workflow["jobs"]["validate"]["steps"] if step.get("name") == name)


class ScopeTests(unittest.TestCase):
    def test_workflow_uses_only_immutable_base_tooling(self) -> None:
        workflow = (_SCRIPT.parents[2] / ".github/workflows/pr-prescreen.yml").read_text()
        self.assertIn('"$SCOPE_SCRIPT" discover', workflow)
        self.assertIn('"$SCOPE_SCRIPT" supplement', workflow)
        self.assertIn("python3 base/scripts/validate-skills-schema.py --marketplace --json --repo-root pr", workflow)
        self.assertIn('if [ "$PLUGIN_LINES" = "0" ]', workflow)
        self.assertIn('((.previous_filename // "") | startswith("plugins/"))', workflow)
        self.assertEqual(workflow.count("/tmp/no-plugin-changes"), 3)
        self.assertIn("printf '[]\\n' > /tmp/filtered-results.json", workflow)
        self.assertIn(": > /tmp/structure-signals.txt", workflow)
        self.assertIn(": > /tmp/hard-blocks.txt", workflow)
        self.assertIn("immutable base scope helper is unavailable", workflow)
        self.assertNotIn("SCOPE_SCRIPT=pr/", workflow)
        self.assertNotIn(".prescreen-validator.py", workflow)
        self.assertNotIn("install -m 0644", workflow)

    def test_workflow_resolves_dispatch_head_base_and_all_file_pages(self) -> None:
        workflow = (_SCRIPT.parents[2] / ".github/workflows/pr-prescreen.yml").read_text()
        self.assertIn('gh api "repos/${{ github.repository }}/pulls/$PR_NUMBER"', workflow)
        self.assertIn("ref: ${{ steps.pr.outputs.head_sha }}", workflow)
        self.assertIn("ref: ${{ steps.pr.outputs.base_sha }}", workflow)
        self.assertIn("gh api --paginate --slurp", workflow)
        self.assertIn("| jq 'add' > /tmp/pr-files.json", workflow)
        self.assertIn('if [ "$VALIDATOR_EXIT" -ne 0 ]', workflow)
        self.assertIn('"$SCOPE_SCRIPT" check-deletions', workflow)
        self.assertNotIn("grep -q", workflow)

    def test_workflow_zero_plugin_bootstrap_produces_complete_artifacts_without_base_helper(self) -> None:
        artifact_paths = [
            Path("/tmp/no-plugin-changes"),
            Path("/tmp/validator.log"),
            Path("/tmp/validator-parsed.json"),
            Path("/tmp/filtered-results.json"),
            Path("/tmp/structure-signals.txt"),
            Path("/tmp/diff-step-signals.txt"),
            Path("/tmp/hard-blocks.txt"),
        ]
        try:
            for path in artifact_paths:
                path.unlink(missing_ok=True)
            Path("/tmp/no-plugin-changes").touch()
            Path("/tmp/diff-step-signals.txt").touch()
            with tempfile.TemporaryDirectory() as tmp:
                for name in (
                    "Run validator against PR tree (full --json sweep)",
                    "Detect structural hard-block signals",
                ):
                    result = subprocess.run(
                        ["bash", "-c", _workflow_step(name)],
                        cwd=tmp,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(Path("/tmp/filtered-results.json").read_text()), [])
            self.assertEqual(Path("/tmp/structure-signals.txt").read_text(), "")
            self.assertEqual(Path("/tmp/hard-blocks.txt").read_text(), "")
        finally:
            for path in artifact_paths:
                path.unlink(missing_ok=True)

    def test_workflow_rename_out_of_plugins_invokes_immutable_scope_helper(self) -> None:
        artifact_paths = [
            Path("/tmp/no-plugin-changes"),
            Path("/tmp/pr-files.json"),
            Path("/tmp/pr-files.txt"),
            Path("/tmp/changed-plugins.txt"),
            Path("/tmp/deleted-plugins.txt"),
            Path("/tmp/diff-step-signals.txt"),
        ]
        try:
            for path in artifact_paths:
                path.unlink(missing_ok=True)
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                bin_dir = root / "bin"
                bin_dir.mkdir()
                gh = bin_dir / "gh"
                gh.write_text(
                    "#!/bin/sh\n"
                    'printf \'%s\\n\' \'[[{"filename":"000-docs/moved.json",'
                    '"previous_filename":"plugins/mcp/a2a-client/.claude-plugin/plugin.json",'
                    '"status":"renamed"}]]\'\n'
                )
                gh.chmod(0o755)
                helper = root / "base/scripts/pr-prescreen/scope.py"
                helper.parent.mkdir(parents=True)
                helper.write_text(
                    "import pathlib, sys\n"
                    "args = sys.argv\n"
                    "for flag in ('--changed-output', '--deleted-output'):\n"
                    "    pathlib.Path(args[args.index(flag) + 1]).touch()\n"
                    "pathlib.Path('scope-invoked').touch()\n"
                )
                (root / "pr").mkdir()
                script = _workflow_step("Compute changed plugin paths")
                script = script.replace("${{ github.repository }}", "owner/repo")
                script = script.replace("${{ steps.pr.outputs.number }}", "1")
                github_output = root / "github-output"
                result = subprocess.run(
                    ["bash", "-c", script],
                    cwd=root,
                    env={**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "GITHUB_OUTPUT": str(github_output)},
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((root / "scope-invoked").is_file())
                self.assertFalse(Path("/tmp/no-plugin-changes").exists())
        finally:
            for path in artifact_paths:
                path.unlink(missing_ok=True)

    def test_category_support_file_is_not_a_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pr/plugins/mcp").mkdir(parents=True)
            (root / "base/plugins/mcp").mkdir(parents=True)
            (root / "pr/plugins/mcp/destructive-policies.json").write_text("{}")
            changed, deleted, count = _SCOPE.discover_plugin_dirs(
                [{"filename": "plugins/mcp/destructive-policies.json", "status": "modified"}],
                pr_root=root / "pr",
                base_root=root / "base",
            )
        self.assertEqual((changed, deleted, count), ([], [], 1))

    def test_new_cataloged_plugin_root_symlink_is_scoped_for_hard_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "outside"
            target.mkdir()
            candidate = root / "pr/plugins/mcp/evil"
            candidate.parent.mkdir(parents=True)
            candidate.symlink_to(target, target_is_directory=True)
            _catalog(root / "pr", ["plugins/mcp/evil"])
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                [{"filename": "plugins/mcp/evil", "status": "added"}],
                pr_root=root / "pr",
                base_root=root / "base",
            )
            signals = _SCOPE.validate_deleted_plugins(deleted, pr_root=root / "pr")
        self.assertEqual(changed, [])
        self.assertEqual(deleted, ["plugins/mcp/evil"])
        self.assertTrue(any("symlink or non-directory" in signal for signal in signals))
        self.assertTrue(any("still has exact catalog source" in signal for signal in signals))

    def test_three_part_regular_cataloged_plugin_root_is_changed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _manifest(root / "pr/plugins/mcp/regular-plugin")
            _catalog(root / "pr", ["plugins/mcp/regular-plugin"])
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                [{"filename": "plugins/mcp/regular-plugin", "status": "added"}],
                pr_root=root / "pr",
                base_root=root / "base",
            )
        self.assertEqual(changed, ["plugins/mcp/regular-plugin"])
        self.assertEqual(deleted, [])

    def test_real_support_directories_are_excluded_by_missing_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            entries = []
            for relative in (
                "plugins/mcp/.greptile/config.json",
                "plugins/saas-packs/scripts/generate-skill-db.py",
                "plugins/saas-packs/_templates/slots/S01.md.j2",
            ):
                path = root / "pr" / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("support")
                entries.append({"filename": relative, "status": "modified"})
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                entries, pr_root=root / "pr", base_root=root / "base"
            )
        self.assertEqual(changed, [])
        self.assertEqual(deleted, [])

    def test_cataloged_axiom_without_root_marker_is_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "pr/plugins/skill-enhancers/axiom"
            (plugin / "plugins/axiom/skills").mkdir(parents=True)
            (plugin / "plugins/axiom/skills/example.md").write_text("nested component")
            _catalog(root / "pr", ["plugins/skill-enhancers/axiom"])
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                [{"filename": "plugins/skill-enhancers/axiom/README.md", "status": "modified"}],
                pr_root=root / "pr",
                base_root=root / "base",
            )
        self.assertEqual(changed, ["plugins/skill-enhancers/axiom"])
        self.assertEqual(deleted, [])

    def test_same_basename_catalog_source_does_not_spoof_exact_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/mcp/shared-name"
            _manifest(plugin)
            _mcp(plugin)
            _catalog(root, ["plugins/security/shared-name"])
            results, signals = _SCOPE.supplement_results([], ["plugins/mcp/shared-name"], pr_root=root)
        self.assertEqual(len(results), 1)
        self.assertTrue(any("Missing exact catalog source" in signal for signal in signals))

    def test_real_mcp_plugin_and_support_file_yield_only_plugin_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "pr/plugins/mcp/a2a-client"
            _manifest(plugin)
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                [
                    {"filename": "plugins/mcp/a2a-client/src/index.ts", "status": "added"},
                    {"filename": "plugins/mcp/destructive-policies.json", "status": "modified"},
                ],
                pr_root=root / "pr",
                base_root=root / "base",
            )
        self.assertEqual(changed, ["plugins/mcp/a2a-client"])
        self.assertEqual(deleted, [])

    def test_partial_deletion_inside_existing_plugin_remains_changed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _manifest(root / "pr/plugins/mcp/a2a-client")
            _manifest(root / "base/plugins/mcp/a2a-client")
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                [{"filename": "plugins/mcp/a2a-client/old.ts", "status": "removed"}],
                pr_root=root / "pr",
                base_root=root / "base",
            )
        self.assertEqual(changed, ["plugins/mcp/a2a-client"])
        self.assertEqual(deleted, [])

    def test_deleted_manifest_with_remaining_plugin_root_is_not_full_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "pr/plugins/mcp/a2a-client"
            plugin.mkdir(parents=True)
            (plugin / "README.md").write_text("still here")
            _manifest(root / "base/plugins/mcp/a2a-client")
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                [
                    {
                        "filename": "plugins/mcp/a2a-client/.claude-plugin/plugin.json",
                        "status": "removed",
                    }
                ],
                pr_root=root / "pr",
                base_root=root / "base",
            )
        self.assertEqual(changed, ["plugins/mcp/a2a-client"])
        self.assertEqual(deleted, [])

    def test_fully_absent_plugin_is_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pr").mkdir()
            _manifest(root / "base/plugins/mcp/old-plugin")
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                [{"filename": "plugins/mcp/old-plugin/README.md", "status": "removed"}],
                pr_root=root / "pr",
                base_root=root / "base",
            )
        self.assertEqual(changed, [])
        self.assertEqual(deleted, ["plugins/mcp/old-plugin"])

    def test_base_plugin_replaced_by_symlink_enters_deletion_integrity_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _manifest(root / "base/plugins/mcp/old-plugin")
            _catalog(root / "base", ["plugins/mcp/old-plugin"])
            target = root / "outside"
            target.mkdir()
            candidate = root / "pr/plugins/mcp/old-plugin"
            candidate.parent.mkdir(parents=True)
            candidate.symlink_to(target, target_is_directory=True)
            _catalog(root / "pr", ["plugins/mcp/old-plugin"])
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                [{"filename": "plugins/mcp/old-plugin/README.md", "status": "modified"}],
                pr_root=root / "pr",
                base_root=root / "base",
            )
        self.assertEqual(changed, [])
        self.assertEqual(deleted, ["plugins/mcp/old-plugin"])

    def test_cross_plugin_rename_scopes_new_and_deleted_old_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _manifest(root / "pr/plugins/mcp/new-plugin")
            _manifest(root / "base/plugins/mcp/old-plugin")
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                [
                    {
                        "filename": "plugins/mcp/new-plugin/src/index.ts",
                        "previous_filename": "plugins/mcp/old-plugin/src/index.ts",
                        "status": "renamed",
                    }
                ],
                pr_root=root / "pr",
                base_root=root / "base",
            )
        self.assertEqual(changed, ["plugins/mcp/new-plugin"])
        self.assertEqual(deleted, ["plugins/mcp/old-plugin"])

    def test_cross_plugin_rename_scopes_old_root_when_it_still_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _manifest(root / "pr/plugins/mcp/new-plugin")
            _manifest(root / "pr/plugins/mcp/old-plugin")
            _manifest(root / "base/plugins/mcp/old-plugin")
            changed, deleted, _count = _SCOPE.discover_plugin_dirs(
                [
                    {
                        "filename": "plugins/mcp/new-plugin/src/index.ts",
                        "previous_filename": "plugins/mcp/old-plugin/src/index.ts",
                        "status": "renamed",
                    }
                ],
                pr_root=root / "pr",
                base_root=root / "base",
            )
        self.assertEqual(changed, ["plugins/mcp/new-plugin", "plugins/mcp/old-plugin"])
        self.assertEqual(deleted, [])

    def test_valid_non_skill_mcp_plugin_gets_neutral_structural_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/mcp/a2a-client"
            _manifest(plugin)
            _mcp(plugin)
            results, signals = _supplement([], ["plugins/mcp/a2a-client"], pr_root=root)
        self.assertEqual(signals, [])
        self.assertEqual(len(results), 1)
        self.assertIsNone(results[0]["grade"])
        self.assertIsNone(results[0]["score"])
        self.assertEqual(results[0]["component_type"], "plugin-structure")

    def test_manifest_name_contract_fails_for_skill_and_non_skill_plugins(self) -> None:
        for name, with_skill in (("", False), ("Bad Name", False), ("", True), ("Bad Name", True)):
            with self.subTest(name=name, with_skill=with_skill), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plugin = root / "plugins/mcp/name-contract"
                _manifest(plugin, {"name": name})
                validator_results: list[dict] = []
                if with_skill:
                    skill = plugin / "skills/check/SKILL.md"
                    skill.parent.mkdir(parents=True)
                    skill.write_text("---\nname: check\ndescription: Valid test skill description\n---\n")
                    validator_results.append(
                        {"path": str(skill), "score": 95, "grade": "A", "errors": 0, "warnings": 0}
                    )
                results, signals = _supplement(validator_results, ["plugins/mcp/name-contract"], pr_root=root)
            self.assertTrue(any("non-empty kebab-case" in signal for signal in signals))

    def test_mcp_marketplace_required_fields_fail_closed(self) -> None:
        canonical = {
            "name": "server",
            "type": "stdio",
            "command": "node",
            "args": [],
            "env": {},
            "description": "Canonical MCP server",
            "version": "1.0.0",
            "enabled": True,
        }
        for field in ("type", "command", "args", "env", "description", "version", "enabled"):
            with self.subTest(field=field):
                config = dict(canonical)
                del config[field]
                errors = _SCOPE._validate_mcp_servers({"server": config}, "test MCP")
                self.assertTrue(any(field in error for error in errors), errors)
        self.assertTrue(_SCOPE._validate_mcp_servers({"Bad Name": canonical}, "test MCP"))
        invalid_version = dict(canonical, version="1.0")
        self.assertTrue(
            any(
                "strict SemVer" in error
                for error in _SCOPE._validate_mcp_servers({"server": invalid_version}, "test MCP")
            )
        )
        for mutation, expected in (
            ({"description": "${SECRET}"}, "unsafe"),
            ({"description": "x" * 1025}, "1024"),
            ({"version": "1.0.0-01"}, "SemVer"),
            ({"metadata": []}, "metadata"),
            ({"when_to_use": "legacy"}, "deprecated"),
        ):
            with self.subTest(mutation=mutation):
                errors = _SCOPE._validate_mcp_servers({"server": dict(canonical, **mutation)}, "test MCP")
                self.assertTrue(any(expected in error for error in errors), errors)

    def test_invalid_manifest_version_type_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/mcp/broken-version"
            _manifest(plugin, {"name": "broken-version", "version": 7})
            results, signals = _supplement([], ["plugins/mcp/broken-version"], pr_root=root)
        self.assertEqual(results, [])
        self.assertTrue(any("Field 'version' must be string" in signal for signal in signals))

    def test_inline_http_mcp_without_url_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/mcp/broken-inline"
            _manifest(
                plugin,
                {
                    "name": "broken-inline",
                    "mcpServers": {
                        "remote": {
                            "name": "remote",
                            "type": "http",
                            "command": "node",
                            "args": [],
                            "env": {},
                            "description": "Remote MCP server",
                            "version": "1.0.0",
                            "enabled": True,
                        }
                    },
                },
            )
            results, signals = _supplement([], ["plugins/mcp/broken-inline"], pr_root=root)
        self.assertEqual(results, [])
        self.assertTrue(any("requires a non-empty url" in signal for signal in signals))

    def test_malformed_hooks_shape_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/mcp/broken-hooks"
            _manifest(plugin)
            hooks = plugin / "hooks/hooks.json"
            hooks.parent.mkdir()
            hooks.write_text(json.dumps({"hooks": {"PreToolUse": []}}))
            results, signals = _supplement([], ["plugins/mcp/broken-hooks"], pr_root=root)
        self.assertEqual(results, [])
        self.assertTrue(any("must contain a non-empty array" in signal for signal in signals))

    def test_malformed_agent_and_command_fail_closed_without_skills(self) -> None:
        for component in ("agents", "commands"):
            with self.subTest(component=component), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plugin = root / "plugins/mcp/broken-component"
                _manifest(plugin)
                _mcp(plugin)
                artifact = plugin / component / "broken.md"
                artifact.parent.mkdir(parents=True)
                artifact.write_text("No frontmatter here")
                results, signals = _supplement([], ["plugins/mcp/broken-component"], pr_root=root)
            self.assertEqual(results, [])
            self.assertTrue(any("No frontmatter found" in signal for signal in signals))

    def test_deleted_root_symlink_and_stale_exact_catalog_both_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "outside"
            target.mkdir()
            candidate = root / "plugins/mcp/old-plugin"
            candidate.parent.mkdir(parents=True)
            candidate.symlink_to(target, target_is_directory=True)
            _catalog(root, ["plugins/mcp/old-plugin"])
            signals = _SCOPE.validate_deleted_plugins(["plugins/mcp/old-plugin"], pr_root=root)
        self.assertTrue(any("symlink or non-directory" in signal for signal in signals))
        self.assertTrue(any("still has exact catalog source" in signal for signal in signals))

    def test_malformed_inline_hooks_shape_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/mcp/broken-inline-hooks"
            _manifest(
                plugin,
                {
                    "name": "broken-inline-hooks",
                    "hooks": {"PreToolUse": [{"hooks": "not-an-array"}]},
                },
            )
            results, signals = _supplement([], ["plugins/mcp/broken-inline-hooks"], pr_root=root)
        self.assertEqual(results, [])
        self.assertTrue(any("hooks must be a non-empty array" in signal for signal in signals))

    def test_nested_symlink_artifacts_fail_closed(self) -> None:
        for case in ("manifest", "mcp", "hooks"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                plugin = root / "plugins/mcp/symlinked"
                outside = root / "outside"
                outside.mkdir()
                if case == "manifest":
                    target = outside / "plugin.json"
                    target.write_text(json.dumps({"name": "symlinked"}))
                    link = plugin / ".claude-plugin/plugin.json"
                    link.parent.mkdir(parents=True)
                    link.symlink_to(target)
                else:
                    _manifest(plugin)
                    if case == "mcp":
                        target = outside / ".mcp.json"
                        target.write_text(json.dumps({"mcpServers": {"x": {"command": "node"}}}))
                        (plugin / ".mcp.json").symlink_to(target)
                    else:
                        target = outside / "hooks.json"
                        target.write_text(json.dumps({"hooks": {}}))
                        (plugin / "hooks").symlink_to(outside, target_is_directory=True)
                results, signals = _supplement([], ["plugins/mcp/symlinked"], pr_root=root)
                self.assertEqual(results, [])
                self.assertTrue(any("no symlink components" in signal for signal in signals))

    def test_dangling_manifest_parent_symlink_on_skill_plugin_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/security/symlinked"
            skill = plugin / "skills/check/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: check\n---\n")
            (plugin / ".claude-plugin").symlink_to(root / "missing", target_is_directory=True)
            validator_result = {
                "path": str(skill),
                "score": 95,
                "grade": "A",
                "errors": 0,
                "warnings": 0,
            }
            results, signals = _supplement([validator_result], ["plugins/security/symlinked"], pr_root=root)
        self.assertEqual(len(results), 1)
        self.assertTrue(any(".claude-plugin" in signal and "no symlink" in signal for signal in signals))

    def test_a_skill_result_does_not_hide_invalid_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/security/example"
            _manifest(plugin, {"name": "example", "version": 4})
            skill = plugin / "skills/check/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: check\ndescription: example\n---\n")
            validator_result = {
                "path": str(skill),
                "score": 95,
                "grade": "A",
                "errors": 0,
                "warnings": 0,
            }
            results, signals = _supplement([validator_result], ["plugins/security/example"], pr_root=root)
        self.assertEqual(len(results), 1)
        self.assertTrue(any("Field 'version' must be string" in signal for signal in signals))

    def test_skill_bearing_plugin_without_validator_result_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins/security/example"
            _manifest(plugin)
            skill = plugin / "skills/check/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: check\n---\n")
            results, signals = _supplement([], ["plugins/security/example"], pr_root=root)
        self.assertEqual(results, [])
        self.assertEqual(
            signals, ["prescreen-internal-error: validator produced no result for plugins/security/example"]
        )


class OwnedHookDocumentationTests(unittest.TestCase):
    """Tracking metadata is not a native runtime enforcement/disablement test."""

    ROOT = _SCRIPT.parents[2]
    PLUGINS = {
        "plugins/devops/jeremy-github-actions-gcp": {"PreToolUse": (True, True)},
        "plugins/examples/formatter": {"PostToolUse": (True, False), "PreToolUse": (False, False)},
    }

    def documents(self):
        for relative, intent in self.PLUGINS.items():
            path = self.ROOT / relative / "hooks/hooks.json"
            yield relative, intent, json.loads(path.read_text())

    def test_owned_hook_roots_pass_existing_structural_gate(self):
        for relative in self.PLUGINS:
            with self.subTest(plugin=relative):
                self.assertEqual(_SCOPE.validate_plugin_structure(self.ROOT / relative, relative, has_skills=True), [])

    def test_handler_metadata_preserves_declared_intent_including_disabled_pre_hook(self):
        for relative, intent, document in self.documents():
            for event, (enabled, blocking) in intent.items():
                with self.subTest(plugin=relative, event=event):
                    group = document["hooks"][event][0]
                    handler = group["hooks"][0]
                    self.assertIs(group["enabled"], enabled)
                    self.assertIs(handler["enabled"], enabled)
                    self.assertIs(handler["blocking"], blocking)
                    self.assertIs(handler["continueOnError"], not blocking)

    def test_missing_or_string_tracking_metadata_still_fails_closed(self):
        for relative, intent, document in self.documents():
            for event in intent:
                for field in ("enabled", "blocking"):
                    for replacement in (None, "false"):
                        with self.subTest(plugin=relative, event=event, field=field, value=replacement):
                            mutated = copy.deepcopy(document)
                            handler = mutated["hooks"][event][0]["hooks"][0]
                            if replacement is None:
                                handler.pop(field, None)
                            else:
                                handler[field] = replacement
                            self.assertEqual(
                                _SCOPE._validate_hooks(mutated, relative),
                                [f"{relative} event {event!r} group 0 handler 0 {field} must be boolean"],
                            )

    def test_command_paths_with_spaces_remain_one_shell_argument(self):
        for relative, intent, document in self.documents():
            for event in intent:
                with self.subTest(plugin=relative, event=event):
                    command = document["hooks"][event][0]["hooks"][0]["command"]
                    expanded = command.replace("${CLAUDE_PLUGIN_ROOT}", "/tmp/plugin with spaces")
                    arguments = shlex.split(expanded)
                    self.assertEqual(len(arguments), 1)
                    self.assertTrue(arguments[0].startswith("/tmp/plugin with spaces/scripts/"))
                    script = arguments[0].removeprefix("/tmp/plugin with spaces/")
                    self.assertTrue((self.ROOT / relative / script).is_file())


if __name__ == "__main__":
    unittest.main()
