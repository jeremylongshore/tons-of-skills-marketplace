"""Every first-party MCP plugin must launch a file that ships with the plugin.

The marketplace installs a plugin by copying its directory; it does not run
`npm install` or a build. Bead claude-e1mk.10 found most `plugins/mcp/*`
entries launching `node dist/...` from `.mcp.json` while `dist/` was
gitignored, so the server file did not exist after install, and several used a
path relative to the user's working directory. This pins the fix: a `node`
launch target must be anchored at `${CLAUDE_PLUGIN_ROOT}` and committed.

External mirrors (directories with `.source.json`) are exempt: their launch
contract is owned upstream and fixed there.
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


def first_party_node_launches():
    for plugin in sorted(p for p in MCP_DIR.iterdir() if p.is_dir()):
        config = plugin / ".mcp.json"
        if not config.is_file() or (plugin / ".source.json").exists():
            continue
        servers = json.loads(config.read_text(encoding="utf-8")).get("mcpServers", {})
        for name, server in servers.items():
            if server.get("command") == "node":
                yield plugin, name, server.get("args", [])


class McpLaunchTargets(unittest.TestCase):
    def test_there_are_first_party_node_launches_to_check(self):
        self.assertGreaterEqual(len(list(first_party_node_launches())), 6)

    def test_node_launch_targets_are_plugin_root_anchored_and_committed(self):
        for plugin, name, args in first_party_node_launches():
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
