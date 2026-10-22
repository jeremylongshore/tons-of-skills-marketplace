"""Every node-launched MCP plugin must launch a file that ships with the plugin.

The marketplace installs a plugin by copying its directory; it does not run
`npm install` or a build. Bead claude-e1mk.10 found most `plugins/mcp/*`
entries launching `node dist/...` from `.mcp.json` while `dist/` was
gitignored, so the server file did not exist after install, and several used a
path relative to the user's working directory. This pins the fix: a `node`
launch target must be anchored at `${CLAUDE_PLUGIN_ROOT}` and committed.

Mirrors are included. Their files come from upstream, but the commit is ours:
a mirrored bundle that is locked in sources.lock.json yet gitignored here
(pr-to-spec's dist/mcp-bundle, caught on #1595) installs without its server.
"""

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MCP_DIR = ROOT / "plugins" / "mcp"
PLUGIN_ROOT = "${CLAUDE_PLUGIN_ROOT}/"


def tracked(path: Path) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def installed_servers(plugin: Path) -> dict:
    """The MCP servers a marketplace install launches.

    A manifest-declared `mcpServers` (in .claude-plugin/plugin.json) is what an
    installed plugin uses; the root .mcp.json applies only when the manifest
    declares none (it may also serve as project-scope config for the repo itself).
    """
    manifest = plugin / ".claude-plugin" / "plugin.json"
    if manifest.is_file():
        declared = json.loads(manifest.read_text(encoding="utf-8")).get("mcpServers")
        if isinstance(declared, dict) and declared:
            return declared
    config = plugin / ".mcp.json"
    if config.is_file():
        return json.loads(config.read_text(encoding="utf-8")).get("mcpServers", {})
    return {}


def node_launches():
    for plugin in sorted(p for p in MCP_DIR.iterdir() if p.is_dir()):
        servers = installed_servers(plugin)
        for name, server in servers.items():
            if server.get("command") == "node":
                yield plugin, name, server.get("args", [])


class McpLaunchTargets(unittest.TestCase):
    def test_there_are_node_launches_to_check(self):
        self.assertGreaterEqual(len(list(node_launches())), 6)

    def test_node_launch_targets_are_plugin_root_anchored_and_committed(self):
        for plugin, name, args in node_launches():
            with self.subTest(plugin=plugin.name, server=name):
                self.assertTrue(args, "node launch needs a script argument")
                target = args[0]
                self.assertTrue(
                    target.startswith(PLUGIN_ROOT),
                    f"{target!r} must start with {PLUGIN_ROOT!r} so it resolves from the installed plugin",
                )
                path = plugin / target[len(PLUGIN_ROOT) :]
                self.assertTrue(path.is_file(), f"{path} does not exist")
                self.assertTrue(tracked(path), f"{path} is not committed, so a marketplace install lacks it")


if __name__ == "__main__":
    unittest.main()
