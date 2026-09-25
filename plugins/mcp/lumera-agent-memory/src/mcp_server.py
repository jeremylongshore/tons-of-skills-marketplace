#!/usr/bin/env python3
"""
Lumera Agent Memory - MCP Server
Durable session memory with Cascade object storage and local FTS index.
"""

import asyncio
import json
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

SERVER_NAME = "lumera-agent-memory"

from security.redact import redact_session
from security.encrypt import encrypt_data, decrypt_data
from cascade.interface import CascadeInterface
from cascade.mock_fs import MockCascadeFS
from index.index import MemoryIndex


class LumeraMemoryServer:
    """MCP server for durable agent memory."""

    def __init__(self):
        self.server: Server
        self.index = MemoryIndex()
        self.cascade_mock = MockCascadeFS()
        self.cascade_live: Optional[CascadeInterface] = None

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register the 4 required MCP tools."""

        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="store_session_to_cascade",
                    description="Extract session from CASS, redact PII/secrets, encrypt client-side, upload to Cascade, index locally",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {"type": "string", "description": "CASS session ID to store"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional tags"},
                            "metadata": {"type": "object", "description": "Optional metadata"},
                            "mode": {"type": "string", "enum": ["mock", "live"], "default": "mock"},
                        },
                        "required": ["session_id"],
                    },
                ),
                Tool(
                    name="query_memories",
                    description="Search local SQLite FTS index for memories (NEVER queries Cascade directly)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query text"},
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional tag filters",
                            },
                            "time_range": {"type": "object", "description": "Optional time range {start, end}"},
                            "limit": {"type": "integer", "default": 10, "description": "Max results"},
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="retrieve_session_from_cascade",
                    description="Fetch encrypted blob from Cascade via URI, decrypt client-side, return session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "cascade_uri": {"type": "string", "description": "Cascade URI from index"},
                            "mode": {"type": "string", "enum": ["mock", "live"], "default": "mock"},
                        },
                        "required": ["cascade_uri"],
                    },
                ),
                Tool(
                    name="estimate_storage_cost",
                    description="Estimate Cascade storage costs for session data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bytes": {"type": "integer", "description": "Data size in bytes"},
                            "redundancy": {"type": "integer", "default": 3, "description": "Replication factor"},
                            "pricing_inputs": {"type": "object", "description": "Optional pricing overrides"},
                        },
                        "required": ["bytes"],
                    },
                ),
            ]

        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Route tool calls to handlers."""

            if name == "store_session_to_cascade":
                result = await self._store_session(arguments)
            elif name == "query_memories":
                result = await self._query_memories(arguments)
            elif name == "retrieve_session_from_cascade":
                result = await self._retrieve_session(arguments)
            elif name == "estimate_storage_cost":
                result = await self._estimate_cost(arguments)
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

    async def _store_session(self, args: dict) -> dict:
        """Store session to Cascade with redaction, encryption, and indexing."""
        session_id = args["session_id"]
        tags = args.get("tags", [])
        metadata = args.get("metadata", {})
        mode = args.get("mode", "mock")

        try:
            # Step 1: Extract from CASS (simulated - would call real CASS API)
            session_data = self._mock_extract_from_cass(session_id)

            # Step 2: Redact secrets/PII
            redacted_data, redaction_report = redact_session(session_data)

            # Step 3: Generate memory card (wow factor)
            memory_card = self._generate_memory_card(redacted_data)

            # Step 4: Encrypt client-side
            crypto_result = encrypt_data(json.dumps(redacted_data))

            # Step 5: Upload to Cascade
            cascade = self.cascade_mock if mode == "mock" else self._get_live_cascade()
            cascade_uri = await cascade.upload_blob(crypto_result.ciphertext, content_type="application/octet-stream")

            # Step 6: Index locally
            indexed = self.index.store_memory(
                session_id=session_id,
                cascade_uri=cascade_uri,
                memory_card=memory_card,
                tags=tags,
                metadata={
                    **metadata,
                    "crypto": {
                        "key_id": crypto_result.key_id,
                        "plaintext_sha256": crypto_result.plaintext_sha256,
                        "ciphertext_sha256": crypto_result.ciphertext_sha256,
                    },
                    "redaction": redaction_report.to_dict(),
                },
            )

            return {
                "ok": True,
                "session_id": session_id,
                "cascade_uri": cascade_uri,
                "indexed": indexed,
                "redaction": {
                    "rules_fired": [{"rule": r.rule_name, "count": r.count} for r in redaction_report.rules_fired]
                },
                "crypto": {
                    "enc": crypto_result.algorithm,
                    "key_id": crypto_result.key_id,
                    "plaintext_sha256": crypto_result.plaintext_sha256,
                    "ciphertext_sha256": crypto_result.ciphertext_sha256,
                    "bytes": len(crypto_result.ciphertext),
                },
                "memory_card": memory_card,
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def _query_memories(self, args: dict) -> dict:
        """Search local FTS index (NEVER queries Cascade)."""
        query = args["query"]
        tags = args.get("tags")
        time_range = args.get("time_range")
        limit = args.get("limit", 10)

        try:
            hits = self.index.search(query=query, tags=tags, time_range=time_range, limit=limit)

            return {
                "ok": True,
                "hits": [
                    {
                        "cass_session_id": hit["session_id"],
                        "cascade_uri": hit["cascade_uri"],
                        "title": hit.get("title", ""),
                        "snippet": hit.get("snippet", ""),
                        "tags": hit.get("tags", []),
                        "created_at": hit["created_at"],
                        "score": hit.get("score", 0.0),
                    }
                    for hit in hits
                ],
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def _retrieve_session(self, args: dict) -> dict:
        """Retrieve and decrypt session from Cascade."""
        cascade_uri = args["cascade_uri"]
        mode = args.get("mode", "mock")

        try:
            # Step 1: Fetch encrypted blob from Cascade
            cascade = self.cascade_mock if mode == "mock" else self._get_live_cascade()
            encrypted_blob = await cascade.download_blob(cascade_uri)

            # Step 2: Get crypto metadata from index
            index_entry = self.index.get_by_cascade_uri(cascade_uri)
            if not index_entry:
                return {"ok": False, "error": "URI not found in local index"}

            expected_sha256 = index_entry["metadata"]["crypto"]["ciphertext_sha256"]

            # Step 3: Decrypt client-side
            session_json = decrypt_data(encrypted_blob, expected_ciphertext_sha256=expected_sha256)
            session_data = json.loads(session_json)

            # Step 4: Return session with memory card
            return {
                "ok": True,
                "cascade_uri": cascade_uri,
                "session": session_data,
                "memory_card": index_entry.get("memory_card"),
                "crypto": {
                    "verified": True,
                    "plaintext_sha256": index_entry["metadata"]["crypto"]["plaintext_sha256"],
                    "ciphertext_sha256": expected_sha256,
                    "key_id": index_entry["metadata"]["crypto"]["key_id"],
                },
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def _estimate_cost(self, args: dict) -> dict:
        """Estimate Cascade storage costs."""
        bytes_size = args["bytes"]
        redundancy = args.get("redundancy", 3)
        pricing = args.get("pricing_inputs", {})

        # Default Cascade pricing (approximate)
        storage_per_gb_month = pricing.get("storage_per_gb_month", 0.02)
        request_per_1k = pricing.get("request_per_1k", 0.0004)

        gb = bytes_size / (1024**3)
        replicated_gb = gb * redundancy

        monthly_storage = replicated_gb * storage_per_gb_month
        # Assume 100 reads/month per session
        estimated_requests = (100 / 1000) * request_per_1k

        return {
            "ok": True,
            "bytes": bytes_size,
            "gb": round(gb, 6),
            "monthly_storage_usd": round(monthly_storage, 4),
            "estimated_request_usd": round(estimated_requests, 4),
            "total_estimated_usd": round(monthly_storage + estimated_requests, 4),
            "assumptions": {
                "redundancy": redundancy,
                "storage_per_gb_month_usd": storage_per_gb_month,
                "request_per_1k_usd": request_per_1k,
                "estimated_reads_per_month": 100,
            },
        }

    def _get_live_cascade(self) -> CascadeInterface:
        """Get live Cascade client (stub for now)."""
        if self.cascade_live is None:
            raise RuntimeError(
                "Live Cascade mode not configured. Required: "
                "LUMERA_CASCADE_ENDPOINT and LUMERA_CASCADE_API_KEY environment variables. "
                "Use mode='mock' for local testing."
            )
        return self.cascade_live

    def _mock_extract_from_cass(self, session_id: str) -> dict:
        """Mock CASS extraction (would call real CASS API)."""
        return {
            "session_id": session_id,
            "messages": [
                {
                    "role": "user",
                    "content": "Deploy the new API with my AWS key AKIAIOSFODNN7EXAMPLE",
                    "timestamp": "2025-01-15T10:30:00Z",
                },
                {
                    "role": "assistant",
                    "content": "I'll help deploy the API. What region?",
                    "timestamp": "2025-01-15T10:30:15Z",
                },
                {
                    "role": "user",
                    "content": "us-east-1, my email is john@example.com for notifications",
                    "timestamp": "2025-01-15T10:31:00Z",
                },
            ],
            "metadata": {"started_at": "2025-01-15T10:30:00Z", "ended_at": "2025-01-15T10:35:00Z"},
        }

    def _generate_memory_card(self, session_data: dict) -> dict:
        """Generate deterministic memory card from session (wow factor)."""
        messages = session_data.get("messages", [])

        # Extract text content
        text_parts = []
        for msg in messages:
            if isinstance(msg.get("content"), str):
                text_parts.append(msg["content"])

        full_text = " ".join(text_parts)

        # Generate title (first user message or summary)
        title = "Untitled Session"
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str) and len(content) > 0:
                    title = content[:80] + ("..." if len(content) > 80 else "")
                    break

        # Extract keywords (simple word frequency)
        words = full_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1

        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        keywords = [w[0] for w in keywords]

        # Extract entities (simple heuristic: capitalized words)
        entities = set()
        for word in full_text.split():
            if word and word[0].isupper() and len(word) > 2:
                entities.add(word)

        # Summary bullets (first 3 messages)
        summary_bullets = []
        for msg in messages[:3]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if isinstance(content, str):
                snippet = content[:100] + ("..." if len(content) > 100 else "")
                summary_bullets.append(f"{role}: {snippet}")

        # Detect decisions and todos (simple keyword matching)
        decisions = []
        todos = []
        for msg in messages:
            content = str(msg.get("content", "")).lower()
            if any(kw in content for kw in ["decided", "decision", "will use", "chosen"]):
                decisions.append(str(msg.get("content", ""))[:100])
            if any(kw in content for kw in ["todo", "need to", "should", "must"]):
                todos.append(str(msg.get("content", ""))[:100])

        # Notable quotes (messages with questions or exclamations)
        notable_quotes = []
        for msg in messages:
            content = str(msg.get("content", ""))
            if "?" in content or "!" in content:
                notable_quotes.append(content[:100])

        return {
            "title": title,
            "summary_bullets": summary_bullets[:3],
            "decisions": decisions[:3],
            "todos": todos[:3],
            "entities": list(entities)[:10],
            "keywords": keywords,
            "notable_quotes": notable_quotes[:3],
        }

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, self.server.create_initialization_options())


async def main():
    """Main entry point."""
    server = LumeraMemoryServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
