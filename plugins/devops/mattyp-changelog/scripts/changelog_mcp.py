#!/usr/bin/env python3
import asyncio
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

SERVER_NAME = "mattyp-changelog"


def _safe_relpath(path_str: str) -> Path:
    candidate = Path(path_str)
    if candidate.is_absolute():
        raise ValueError("output_path must be relative")
    resolved = (Path.cwd() / candidate).resolve()
    resolved.relative_to(Path.cwd().resolve())
    return resolved


class MattypChangelogMcp:
    def __init__(self) -> None:
        self.server: Server
        self._register()

    def _register(self) -> None:
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="fetch_changelog_data",
                    description="Fetch structured changelog items from a source (github/slack/git) for a date range.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_type": {"type": "string", "enum": ["github", "slack", "git"]},
                            "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                            "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                            "config": {"type": "object"},
                        },
                        "required": ["source_type", "start_date", "end_date", "config"],
                    },
                ),
                Tool(
                    name="validate_frontmatter",
                    description="Validate YAML frontmatter structure for changelog output.",
                    inputSchema={
                        "type": "object",
                        "properties": {"frontmatter": {"type": "object"}, "schema_path": {"type": "string"}},
                        "required": ["frontmatter"],
                    },
                ),
                Tool(
                    name="write_changelog",
                    description="Write changelog content to a file with safety checks and SHA256 hash.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "output_path": {"type": "string"},
                            "overwrite": {"type": "boolean", "default": False},
                        },
                        "required": ["content", "output_path"],
                    },
                ),
                Tool(
                    name="create_changelog_pr",
                    description="Create a branch + commit for the changelog and optionally open a PR via gh.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "branch_name": {"type": "string"},
                            "commit_message": {"type": "string"},
                            "pr_title": {"type": "string"},
                            "pr_body": {"type": "string"},
                            "base_branch": {"type": "string", "default": "main"},
                            "files": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["branch_name", "commit_message", "pr_title", "pr_body", "files"],
                    },
                ),
                Tool(
                    name="validate_changelog_quality",
                    description="Run deterministic quality checks and return a 0-100 score.",
                    inputSchema={
                        "type": "object",
                        "properties": {"content": {"type": "string"}},
                        "required": ["content"],
                    },
                ),
                Tool(
                    name="get_changelog_config",
                    description="Load and validate .changelog-config.json from the current repo.",
                    inputSchema={
                        "type": "object",
                        "properties": {"config_path": {"type": "string", "default": ".changelog-config.json"}},
                    },
                ),
            ]

        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            if name == "get_changelog_config":
                result = await self._get_config(arguments or {})
            elif name == "fetch_changelog_data":
                result = await self._fetch(arguments or {})
            elif name == "validate_frontmatter":
                result = await self._validate_frontmatter(arguments or {})
            elif name == "write_changelog":
                result = await self._write(arguments or {})
            elif name == "validate_changelog_quality":
                result = await self._quality(arguments or {})
            elif name == "create_changelog_pr":
                result = await self._create_pr(arguments or {})
            else:
                result = {"ok": False, "error": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        async def _on_list_tools(ctx: Any, params: Any) -> ListToolsResult:
            return ListToolsResult(tools=await list_tools())

        async def _on_call_tool(ctx: Any, params: CallToolRequestParams) -> CallToolResult:
            # The 1.x decorator turned a raised exception into an isError result;
            # keep that contract instead of surfacing a protocol error.
            try:
                content = await call_tool(params.name, dict(params.arguments or {}))
                return CallToolResult(content=content)
            except Exception as exc:  # noqa: BLE001 - every failure becomes a tool error result
                payload = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
                text = TextContent(type="text", text=json.dumps(payload, indent=2))
                return CallToolResult(content=[text], is_error=True)

        # MCP Python SDK 2.x: handlers are passed to the constructor; the 1.x
        # @server.list_tools() / @server.call_tool() decorators no longer exist.
        self.server = Server(SERVER_NAME, on_list_tools=_on_list_tools, on_call_tool=_on_call_tool)

    async def _get_config(self, args: dict) -> dict:
        path = Path(args.get("config_path") or ".changelog-config.json")
        if not path.exists():
            return {"ok": False, "error": f"Missing config file: {path}"}
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {"ok": False, "error": f"Invalid JSON: {exc}"}

        errors = []
        if not isinstance(config.get("sources"), list) or not config.get("sources"):
            errors.append("sources must be a non-empty array")
        if not isinstance(config.get("template"), str) or not config.get("template"):
            errors.append("template must be a non-empty string")
        if not isinstance(config.get("output_path"), str) or not config.get("output_path"):
            errors.append("output_path must be a non-empty string")

        valid = len(errors) == 0
        return {"ok": True, "config": config, "validation": {"valid": valid, "errors": errors}}

    async def _fetch(self, args: dict) -> dict:
        source_type = args.get("source_type")
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        cfg = args.get("config") or {}

        if source_type == "git":
            branch = cfg.get("branch", "main")
            try:
                out = subprocess.check_output(
                    ["git", "log", branch, "--since", start_date, "--until", end_date, "--pretty=%H|%s|%an|%cI"],
                    text=True,
                )
                items = []
                for line in out.splitlines():
                    sha, subject, author, ts = (line.split("|", 3) + ["", "", "", ""])[:4]
                    items.append(
                        {
                            "id": sha[:7],
                            "title": subject,
                            "type": "commit",
                            "author": author,
                            "labels": [],
                            "url": "",
                            "timestamp": ts,
                        }
                    )
                return {
                    "ok": True,
                    "data": {
                        "items": items,
                        "count": len(items),
                        "source": "git",
                        "date_range": f"{start_date} to {end_date}",
                    },
                }
            except Exception as exc:
                return {"ok": False, "error": f"git fetch failed: {exc}"}

        if source_type == "github":
            token_env = cfg.get("token_env", "GITHUB_TOKEN")
            if not os.getenv(token_env):
                return {"ok": False, "error": f"Missing GitHub token env var: {token_env}"}
            return {
                "ok": True,
                "data": {
                    "items": [],
                    "count": 0,
                    "source": "github",
                    "date_range": f"{start_date} to {end_date}",
                    "note": "GitHub fetching not yet implemented in MCP v0.1.0",
                },
            }

        if source_type == "slack":
            token_env = cfg.get("token_env", "SLACK_TOKEN")
            if token_env and not os.getenv(token_env):
                return {"ok": False, "error": f"Missing Slack token env var: {token_env}"}
            return {
                "ok": True,
                "data": {
                    "items": [],
                    "count": 0,
                    "source": "slack",
                    "date_range": f"{start_date} to {end_date}",
                    "note": "Slack fetching not yet implemented in MCP v0.1.0",
                },
            }

        return {"ok": False, "error": f"Unsupported source_type: {source_type}"}

    async def _validate_frontmatter(self, args: dict) -> dict:
        fm = args.get("frontmatter")
        if not isinstance(fm, dict):
            return {"ok": False, "valid": False, "errors": ["frontmatter must be an object"], "warnings": []}
        errors = []
        if not fm.get("date"):
            errors.append("Missing required field: date")
        if not fm.get("version"):
            errors.append("Missing required field: version")
        return {"ok": True, "valid": len(errors) == 0, "errors": errors, "warnings": []}

    async def _write(self, args: dict) -> dict:
        content = args.get("content", "")
        output_path = args.get("output_path", "")
        overwrite = bool(args.get("overwrite", False))

        try:
            target = _safe_relpath(output_path)
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

        if target.exists() and not overwrite:
            return {"ok": False, "error": f"Refusing to overwrite existing file: {output_path}"}

        target.write_text(content, encoding="utf-8")
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        lines = content.count("\n") + 1 if content else 0
        return {
            "ok": True,
            "file": {"path": output_path, "sha256": sha256, "lines": lines, "size_bytes": len(content.encode("utf-8"))},
        }

    async def _quality(self, args: dict) -> dict:
        content = args.get("content", "")
        score = 100
        errors = []
        warnings = []

        if not content.lstrip().startswith("---"):
            score -= 30
            errors.append("Missing YAML frontmatter")

        for heading in ["## Highlights", "## Features", "## Fixes"]:
            if heading not in content:
                score -= 10
                warnings.append(f"Missing section: {heading}")

        score = max(0, min(100, score))
        return {"ok": len(errors) == 0, "score": score, "errors": errors, "warnings": warnings}

    async def _create_pr(self, args: dict) -> dict:
        branch = args.get("branch_name")
        commit_message = args.get("commit_message")
        pr_title = args.get("pr_title")
        pr_body = args.get("pr_body")
        base_branch = args.get("base_branch", "main")
        files = args.get("files") or []

        if not branch or not commit_message or not pr_title or not pr_body or not files:
            return {"ok": False, "error": "Missing required fields"}

        try:
            subprocess.check_call(["git", "checkout", "-B", branch])
            subprocess.check_call(["git", "add", *files])
            subprocess.check_call(["git", "commit", "-m", commit_message])
        except Exception as exc:
            return {"ok": False, "error": f"git commit failed: {exc}"}

        pr_url = None
        try:
            subprocess.check_call(["gh", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            pr_out = subprocess.check_output(
                ["gh", "pr", "create", "--base", base_branch, "--head", branch, "--title", pr_title, "--body", pr_body],
                text=True,
            ).strip()
            pr_url = pr_out.splitlines()[-1] if pr_out else None
        except Exception:
            pr_url = None

        return {
            "ok": True,
            "branch": branch,
            "base_branch": base_branch,
            "pr": {"url": pr_url} if pr_url else None,
            "note": "PR creation requires gh auth; if missing, push branch and open PR manually.",
        }


async def main() -> None:
    server = MattypChangelogMcp().server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
