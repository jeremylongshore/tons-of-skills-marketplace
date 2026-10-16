"""E4.10 refusal-surface tests for every MCP plugin declaring `refuse`.

A `refuse` declaration in plugins/mcp/destructive-policies.json means "no
destructive tool surface exists." This suite makes that executable: for each
such plugin it pins the registered tool-name surface of the enforcing artifact
and asserts the absence of the specific capabilities that would falsify the
declaration. Adding a destructive tool (or wiring real execution into a
stubbed engine) fails here first, forcing a re-classification instead of a
silent policy drift. The gate (scripts/check-mcp-destructive-policy.mjs)
executes this module and requires it to pass.

dolt-mcp-vcs (recommend-only) has its own wire-level harness:
tests/test_dolt_mcp_guard.py.
"""

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# plugin -> (artifact, tool names that must all be present,
#            forbidden patterns whose appearance falsifies `refuse`)
SURFACES = {
    "conversational-api-debugger": (
        "plugins/mcp/conversational-api-debugger/servers/api-debugger.ts",
        ["load_openapi", "ingest_logs", "explain_failure", "make_repro"],
        ["writeFile", "unlink", "rmSync", "child_process", "execSync"],
    ),
    "databricks-workspace-mcp": (
        [
            "plugins/mcp/databricks-workspace-mcp/src/tools/clusters.ts",
            "plugins/mcp/databricks-workspace-mcp/src/tools/pipelines.ts",
            "plugins/mcp/databricks-workspace-mcp/src/tools/instance-pools.ts",
            "plugins/mcp/databricks-workspace-mcp/src/tools/unity-catalog.ts",
        ],
        ["clusters_list", "clusters_get", "clusters_events", "pipelines_get"],
        ["delete", "terminate", "permanent", "edit_", "create_cluster"],
    ),
    "design-to-code": (
        "plugins/mcp/design-to-code/servers/design-converter.ts",
        ["parse_figma", "analyze_screenshot", "generate_component"],
        ["writeFile", "unlink", "rmSync", "child_process", "fetch("],
    ),
    "governed-second-brain": (
        "plugins/mcp/governed-second-brain/plugin-runtime/governed-brain.cjs",
        ["brain_search", "brain_capture", "brain_govern", "brain_transition"],
        ["brain_delete", "brain_purge", "brain_wipe"],
    ),
    "intent-skills-diagnostic": (
        "plugins/mcp/intent-skills-diagnostic/server-surface.json",
        ["start_here", "scan_setup", "ask_questions", "recommend_skills", "talk_to_intent"],
        ['"readOnlyHint": false', '"destructiveHint": true', '"openWorldHint": true'],
    ),
    "lumera-agent-memory": (
        "plugins/mcp/lumera-agent-memory/src/mcp_server.py",
        ["store_session_to_cascade", "query_memories", "estimate_storage_cost"],
        ["delete_blob", "delete_session", "purge"],
    ),
    "project-health-auditor": (
        "plugins/mcp/project-health-auditor/servers/code-metrics.ts",
        ["list_repo_files", "file_metrics", "git_churn", "map_tests"],
        ["writeFile", "unlink", "rmSync", "child_process", "execSync"],
    ),
    "workflow-orchestrator": (
        "plugins/mcp/workflow-orchestrator/servers/workflow-engine.ts",
        ["create_workflow", "execute_workflow", "get_workflow", "list_workflows"],
        # The executor is a simulated stub; wiring real execution must fail here.
        ['from "child_process"', 'require("child_process")', "execSync", "spawn("],
    ),
    "x-bug-triage": (
        "plugins/mcp/x-bug-triage/mcp/triage-server/server.ts",
        ["create_draft_issue", "check_existing_issues", "confirm_and_file"],
        ["octokit", "@octokit", "issues.create"],
    ),
}


class RefusalSurfaceTest(unittest.TestCase):
    def load(self, rel):
        path = REPO / rel
        self.assertTrue(path.is_file(), f"enforcing artifact missing: {rel}")
        return path.read_text(encoding="utf-8", errors="replace")

    def test_registry_and_suite_cover_the_same_refuse_set(self):
        registry = json.loads((REPO / "plugins/mcp/destructive-policies.json").read_text())
        declared_refuse = {name for name, entry in registry["policies"].items() if entry["policy"] == "refuse"}
        self.assertEqual(
            declared_refuse,
            set(SURFACES),
            "a refuse declaration and this suite's coverage drifted apart",
        )

    def test_every_refuse_surface_holds(self):
        for plugin, (artifact, expected_tools, forbidden) in SURFACES.items():
            with self.subTest(plugin=plugin):
                files = artifact if isinstance(artifact, list) else [artifact]
                text = "\n".join(self.load(rel) for rel in files)
                for tool in expected_tools:
                    self.assertIn(
                        tool,
                        text,
                        f"{plugin}: pinned tool '{tool}' vanished — surface "
                        "changed, re-classify before editing this pin",
                    )
                for pattern in forbidden:
                    self.assertNotIn(
                        pattern,
                        text,
                        f"{plugin}: forbidden capability '{pattern}' appeared "
                        "in a refuse-declared surface — re-classify the "
                        "policy in destructive-policies.json",
                    )

    def test_x_bug_triage_file_tool_stays_a_stub(self):
        text = self.load("plugins/mcp/x-bug-triage/mcp/triage-server/server.ts")
        self.assertIn("issues/NEW", text, "the synthetic-URL stub marker is gone")


if __name__ == "__main__":
    unittest.main()
