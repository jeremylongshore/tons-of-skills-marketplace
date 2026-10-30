"""Container-only native hook probe with a loopback canned Anthropic response.

The host runner supplies source snapshots, marker dependencies, and a network-none
container. This tests Claude hook execution, not model quality or real Prettier.
"""

import http.server
import threading
import json
import os
import pathlib
import subprocess
import shutil
import time

ROOT = pathlib.Path("/work")
assert sorted(p.name for p in pathlib.Path("/sys/class/net").iterdir()) == ["lo"]
results = []


class API(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
        if "count_tokens" in self.path:
            data = json.dumps({"input_tokens": 1}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        state = self.server.fixture
        state["requests"].append(
            {
                "path": self.path,
                "tool_names": [t.get("name") for t in body.get("tools", [])],
                "message_count": len(body.get("messages", [])),
                "tool_results": [
                    {
                        "tool_use_id": c.get("tool_use_id"),
                        "is_error": c.get("is_error", False),
                        "content": str(c.get("content", ""))[:800],
                    }
                    for m in body.get("messages", [])
                    if isinstance(m.get("content"), list)
                    for c in m["content"]
                    if c.get("type") == "tool_result"
                ],
            }
        )
        op = state["operations"][state["next"]] if state["next"] < len(state["operations"]) else None
        send_tool = op is not None and op["tool"] in [t.get("name") for t in body.get("tools", [])]
        tool_id = "toolu_fixture_" + str(state["next"])
        if send_tool:
            state["sent"] = True
            state["next"] += 1
        content = (
            [{"type": "tool_use", "id": tool_id, "name": op["tool"], "input": op["input"]}]
            if send_tool
            else [{"type": "text", "text": "Fixture complete."}]
        )
        message = {
            "id": "msg_fixture",
            "type": "message",
            "role": "assistant",
            "model": body.get("model", "fixture"),
            "content": content,
            "stop_reason": "tool_use" if send_tool else "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 1, "output_tokens": 1},
        }
        self.send_response(200)
        if not body.get("stream"):
            data = json.dumps(message).encode()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Connection", "close")
        self.end_headers()
        start = {**message, "content": [], "stop_reason": None, "usage": {"input_tokens": 1, "output_tokens": 0}}
        block = content[0]
        events = [
            ("message_start", {"type": "message_start", "message": start}),
            (
                "content_block_start",
                {
                    "type": "content_block_start",
                    "index": 0,
                    "content_block": {**block, **({"input": {}} if send_tool else {"text": ""})},
                },
            ),
            (
                "content_block_delta",
                {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": (
                        {"type": "input_json_delta", "partial_json": json.dumps(op["input"])}
                        if send_tool
                        else {"type": "text_delta", "text": "Fixture complete."}
                    ),
                },
            ),
            ("content_block_stop", {"type": "content_block_stop", "index": 0}),
            (
                "message_delta",
                {
                    "type": "message_delta",
                    "delta": {"stop_reason": message["stop_reason"], "stop_sequence": None},
                    "usage": {"output_tokens": 1},
                },
            ),
            ("message_stop", {"type": "message_stop"}),
        ]
        for event, data in events:
            self.wfile.write(("event: " + event + "\ndata: " + json.dumps(data) + "\n\n").encode())
            self.wfile.flush()
        self.close_connection = True


cases = [
    ("gcp_baseline_denied_input", "baseline", "gcp", "Write", False, False),
    ("gcp_candidate_denied_input", "candidate", "gcp", "Write", False, False),
    ("gcp_candidate_allowed_input", "candidate", "gcp", "Write", True, False),
    ("gcp_candidate_edit_denied", "candidate", "gcp", "Edit", False, False),
    ("gcp_candidate_edit_allowed", "candidate", "gcp", "Edit", True, False),
    ("formatter_write_default", "candidate", "formatter", "Write", True, False),
    ("formatter_default", "candidate", "formatter", "Edit", True, False),
    ("formatter_disabled", "candidate", "formatter", "Edit", False, False),
    ("formatter_pre_enabled", "candidate", "formatter", "Edit", True, True),
]
cases = [case for case in cases if (ROOT / "sources" / case[1]).exists()]
for name, label, plugin, tool, allowed, pre_enabled in cases:
    folder = ROOT / "cases" / name
    project = folder / "project"
    project.mkdir(parents=True)
    installed = folder / "plugin"
    shutil.copytree(ROOT / "sources" / label / plugin, installed)
    marker = folder / "prettier.jsonl"
    target = project / (".github/workflows/probe.yml" if plugin == "gcp" else "with space.js")
    target.parent.mkdir(parents=True, exist_ok=True)
    if plugin == "gcp":
        if tool == "Edit":
            old = "credentials_json" if allowed else "safe_key"
            new = "safe_key" if allowed else "credentials_json"
            target.write_text(old + ": fixture\n")
            input_data = {"file_path": str(target), "old_string": old, "new_string": new}
        else:
            text = (
                "workload_identity_provider: fixture\npermissions:\n  id-token: write\n"
                if allowed
                else "credentials_json: synthetic-fixture-secret\n"
            )
            input_data = {"file_path": str(target), "content": text}
    else:
        if tool == "Edit":
            target.write_text("const fixture=1;\n")
            input_data = {"file_path": str(target), "old_string": "fixture=1", "new_string": "fixture=2"}
        else:
            input_data = {"file_path": str(target), "content": "const fixture=2;\n"}
        cfg = installed / "hooks/hooks.json"
        data = json.loads(cfg.read_text())
        data["hooks"]["PostToolUse"][0]["enabled"] = allowed
        data["hooks"]["PreToolUse"][0]["enabled"] = pre_enabled
        cfg.write_text(json.dumps(data))
    operations = ([{"tool": "Read", "input": {"file_path": str(target)}}] if tool == "Edit" else []) + [
        {"tool": tool, "input": input_data}
    ]
    state = {"operations": operations, "next": 0, "requests": [], "sent": False}
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), API)
    server.fixture = state
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    config = folder / "config"
    config.mkdir()
    env = {
        **os.environ,
        "ANTHROPIC_BASE_URL": "http://127.0.0.1:" + str(server.server_port),
        "ANTHROPIC_API_KEY": "synthetic-fixture-key",
        "CLAUDE_CONFIG_DIR": str(config),
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        "DISABLE_TELEMETRY": "1",
        "DISABLE_ERROR_REPORTING": "1",
        "DISABLE_AUTOUPDATER": "1",
        "HOOK_RUNTIME_MARKER": str(marker),
        "PATH": "/work/bin:/usr/local/bin:/usr/bin:/bin",
    }
    cmd = [
        "claude",
        "--print",
        "--output-format",
        "json",
        "--no-session-persistence",
        "--disable-slash-commands",
        "--setting-sources",
        "",
        "--strict-mcp-config",
        "--mcp-config",
        '{"mcpServers":{}}',
        "--plugin-dir",
        str(installed),
        "--permission-mode",
        "acceptEdits",
        "--allowedTools",
        "Read,Write,Edit",
        "--tools",
        "Read,Write,Edit",
        "--model",
        "sonnet",
        "Perform the requested local fixture tool operation, then finish.",
    ]
    start = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=project, env=env, text=True, capture_output=True, timeout=120)
        (folder / "stdout.txt").write_text(p.stdout)
        (folder / "stderr.txt").write_text(p.stderr)
        out = {
            "case": name,
            "exit": p.returncode,
            "seconds": round(time.monotonic() - start, 2),
            "sent_tool": state["sent"],
            "operations_sent": state["next"],
            "requests": state["requests"],
            "target_exists": target.exists(),
            "target_content": target.read_text() if target.exists() else None,
            "prettier_invocations": [json.loads(x) for x in marker.read_text().splitlines()] if marker.exists() else [],
            "pre_validation_log_exists": (installed / "logs/validate.log").exists(),
        }
    except subprocess.TimeoutExpired:
        out = {
            "case": name,
            "timeout": True,
            "exit": None,
            "operations_sent": state["next"],
            "requests": state["requests"],
            "sent_tool": state["sent"],
            "target_exists": target.exists(),
            "target_content": target.read_text() if target.exists() else None,
            "prettier_invocations": [],
            "pre_validation_log_exists": False,
        }
    finally:
        server.shutdown()
        server.server_close()
    errors = [r for request in out.get("requests", []) for r in request.get("tool_results", []) if r["is_error"]]
    common = out.get("exit") == 0 and out.get("operations_sent") == len(operations)
    if plugin == "gcp" and label == "candidate" and not allowed:
        correct = out["target_content"] == ("safe_key: fixture\n" if tool == "Edit" else None) and any(
            "Workflow policy:" in e["content"] for e in errors
        )
    elif plugin == "gcp":
        expected = "safe_key: fixture\n" if tool == "Edit" else input_data["content"]
        correct = not errors and out["target_content"] == expected
    else:
        calls = out["prettier_invocations"]
        correct = (
            not errors
            and out["target_content"] == ("const fixture = 2;\n" if allowed else "const fixture=2;\n")
            and sum("--write" in c for c in calls) == int(allowed)
            and sum("--check" in c for c in calls) == int(pre_enabled)
            and out["pre_validation_log_exists"] == pre_enabled
        )
    out["passed"] = bool(common and correct)
    results.append(out)
    (ROOT / "results.json").write_text(
        json.dumps(
            {
                "interfaces": ["lo"],
                "native_version": subprocess.check_output(["claude", "--version"], text=True).strip(),
                "cases": results,
                "passed": all(x["passed"] for x in results),
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(out), flush=True)
    if not out["passed"]:
        raise SystemExit("Native hook fixture failed: " + name)
