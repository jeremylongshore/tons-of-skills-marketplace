"""A first-party MCP server's declared `version` must be what the server reports.

The marketplace MCP contract (kernel authoring/v2 IS overlay, mirrored by the PR
pre-screen) requires `name`, `description`, `version` and `enabled` on every
server entry. A hand-typed `version` would drift silently, so this test launches
each first-party bundle alone in an empty directory, sends `initialize`, and
checks the reported serverInfo name and version against `.mcp.json`.

Mirrors (directories with `.source.json`) are owned upstream and skipped.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MCP_DIR = ROOT / "plugins" / "mcp"
PLUGIN_ROOT = "${CLAUDE_PLUGIN_ROOT}/"


def declared_node_servers():
    for plugin in sorted(p for p in MCP_DIR.iterdir() if p.is_dir()):
        config = plugin / ".mcp.json"
        if not config.is_file() or (plugin / ".source.json").exists():
            continue
        for name, server in json.loads(config.read_text(encoding="utf-8")).get("mcpServers", {}).items():
            if server.get("command") == "node" and "version" in server:
                yield plugin, name, server


def server_info(script: Path) -> dict:
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "ci", "version": "1"}},
    }
    with tempfile.TemporaryDirectory() as scratch:
        copy = Path(scratch) / script.name
        shutil.copyfile(script, copy)
        result = subprocess.run(
            ["node", str(copy)], input=json.dumps(request) + "\n", capture_output=True, text=True, timeout=30
        )
    for line in result.stdout.splitlines():
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message.get("id") == 1:
            return message["result"]["serverInfo"]
    raise AssertionError(f"{script} gave no initialize response: {result.stderr[-500:]}")


class McpDeclaredServerVersions(unittest.TestCase):
    def test_declared_name_and_version_match_the_running_server(self):
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        servers = list(declared_node_servers())
        self.assertGreaterEqual(len(servers), 6)
        for plugin, name, server in servers:
            with self.subTest(plugin=plugin.name, server=name):
                target = server["args"][0]
                self.assertTrue(target.startswith(PLUGIN_ROOT))
                info = server_info(plugin / target[len(PLUGIN_ROOT) :])
                self.assertEqual(info.get("name"), name)
                self.assertEqual(info.get("version"), server["version"])


if __name__ == "__main__":
    unittest.main()
