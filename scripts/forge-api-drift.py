#!/usr/bin/env python3
"""Compare a captured forge tool-name surface with bounded, inert upstream source.

This inspects the official public catalogue, never imports it or calls a workspace.
Exit 0: no captured name disappeared; 1: name drift; 2: incomplete/unverified.
"""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = re.compile(r"[a-z][a-z0-9_]{0,63}\Z")
SHA = re.compile(r"[a-f0-9]{40}\Z")
REPOSITORY = "makeplane/plane-mcp-server"
REGISTRY = "plane_mcp/tools/registry.py"
MAX_BODY = 512 * 1024
MAX_TOTAL = 8 * 1024 * 1024
MAX_RESOURCES = 40


class Unverified(ValueError):
    """No inference of absence is permitted."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Unverified("UPSTREAM_REDIRECT_REFUSED")


class PublicSource:
    def __init__(self):
        self.deadline = time.monotonic() + 120
        self.total = 0
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def get(self, url):
        if not url.startswith(
            (
                "https://api.github.com/repos/" + REPOSITORY + "/",
                "https://raw.githubusercontent.com/" + REPOSITORY + "/",
            )
        ):
            raise Unverified("UPSTREAM_URL_REFUSED")
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise Unverified("UPSTREAM_DEADLINE_EXCEEDED")
        if self.total >= MAX_TOTAL:
            raise Unverified("UPSTREAM_SIZE_EXCEEDED")
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "forge-api-drift/1"})
            with self.opener.open(request, timeout=min(8, remaining)) as response:
                if response.status != 200:
                    raise Unverified("UPSTREAM_NON_200")
                chunks, received = [], 0
                while True:
                    if time.monotonic() > self.deadline:
                        raise Unverified("UPSTREAM_DEADLINE_EXCEEDED")
                    chunk = response.read1(min(65536, MAX_BODY + 1 - received, MAX_TOTAL + 1 - self.total))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    received += len(chunk)
                    self.total += len(chunk)
                    if received > MAX_BODY or self.total > MAX_TOTAL:
                        raise Unverified("UPSTREAM_SIZE_EXCEEDED")
                body = b"".join(chunks)
            if time.monotonic() > self.deadline:
                raise Unverified("UPSTREAM_DEADLINE_EXCEEDED")
            return body
        except (OSError, urllib.error.URLError) as exc:
            raise Unverified("UPSTREAM_FETCH_FAILED") from exc


def assignments(source):
    try:
        if len(source) > MAX_BODY:
            raise Unverified("CATALOGUE_SIZE_EXCEEDED")
        tree = ast.parse(source)
        values = {}
        for node in tree.body:
            if isinstance(node, ast.Assign):
                targets, value = node.targets, node.value
            elif isinstance(node, ast.AnnAssign):
                targets, value = [node.target], node.value
            else:
                continue
            for target in targets:
                if isinstance(target, ast.Name) and target.id in {"NAME", "LEGACY", "LEGACY_UNMAPPED", "RESOURCES"}:
                    if target.id in values:
                        raise Unverified("CATALOGUE_DUPLICATE_ASSIGNMENT")
                    values[target.id] = value
        return values
    except (SyntaxError, UnicodeError, RecursionError, ValueError) as exc:
        raise Unverified("CATALOGUE_PARSE_FAILED") from exc


def literal(node):
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError, RecursionError) as exc:
        raise Unverified("CATALOGUE_NON_LITERAL") from exc


def names_valid(names):
    return all(isinstance(name, str) and NAME.fullmatch(name) for name in names)


def catalogue(fetch):
    """fetch(path) returns pinned bytes; parse registered modules, not directory guesses."""
    registry = fetch(REGISTRY)
    resources = assignments(registry).get("RESOURCES")
    if not isinstance(resources, ast.Tuple) or not 1 <= len(resources.elts) <= MAX_RESOURCES:
        raise Unverified("REGISTRY_SHAPE_CHANGED")
    modules = [node.id if isinstance(node, ast.Name) else "" for node in resources.elts]
    if not names_valid(modules) or len(modules) != len(set(modules)):
        raise Unverified("REGISTRY_NAMES_INVALID")
    advertised, aliases, unmapped = set(), {}, {}
    hashes = {REGISTRY: hashlib.sha256(registry).hexdigest()}
    for module in modules:
        path = f"plane_mcp/tools/{module}.py"
        source = fetch(path)
        hashes[path] = hashlib.sha256(source).hexdigest()
        values = assignments(source)
        if "NAME" not in values or "LEGACY" not in values:
            raise Unverified("RESOURCE_SHAPE_CHANGED")
        name, legacy = literal(values["NAME"]), literal(values["LEGACY"])
        retired = literal(values["LEGACY_UNMAPPED"]) if "LEGACY_UNMAPPED" in values else {}
        if not names_valid([name]) or name in advertised:
            raise Unverified("RESOURCE_NAME_INVALID")
        if not isinstance(legacy, dict) or not isinstance(retired, dict):
            raise Unverified("LEGACY_SHAPE_CHANGED")
        if not names_valid(legacy) or not names_valid(legacy.values()) or not names_valid(retired):
            raise Unverified("LEGACY_NAMES_INVALID")
        if any(not isinstance(reason, str) or not reason for reason in retired.values()):
            raise Unverified("UNMAPPED_REASON_INVALID")
        if set(legacy) & (set(aliases) | set(unmapped)) or set(retired) & (set(aliases) | set(unmapped) | set(legacy)):
            raise Unverified("LEGACY_COLLISION")
        advertised.add(name)
        aliases.update({old: {"tool": name, "action": action} for old, action in legacy.items()})
        unmapped.update(retired)
    if advertised & (set(aliases) | set(unmapped)):
        raise Unverified("CATALOGUE_COLLISION")
    return advertised, aliases, unmapped, hashes


def captured_names(research):
    try:
        section = research.split("## Gate 3 — API surface research\n", 1)[1].split("## Gate 4", 1)[0]
    except IndexError as exc:
        raise Unverified("RESEARCH_SECTION_MISSING") from exc
    names = re.findall(r"^- `([a-z][a-z0-9_]+)`", section, re.M)
    if not names or len(names) != len(set(names)):
        raise Unverified("RESEARCH_NAMES_INVALID")
    return names


def inspect(root, entry, public=None):
    plugin = entry.get("plugin", "")
    result = {"plugin": plugin, "status": "UNVERIFIED"}
    try:
        if not re.fullmatch(r"plugins/[a-z0-9-]{1,80}/[a-z0-9-]{1,80}", plugin):
            raise Unverified("PLUGIN_PATH_INVALID")
        research_path = root / plugin / ".forge/research.md"
        research = research_path.read_bytes()
        digest = hashlib.sha256(research).hexdigest()
        result["research_sha256"] = digest
        if digest != entry.get("research_sha256"):
            raise Unverified("RESEARCH_BASELINE_CHANGED")
        expected = captured_names(research.decode("utf-8"))
        if expected != entry.get("captured_tools") or not names_valid(expected):
            raise Unverified("CAPTURED_TOOLS_MISMATCH")
        if entry.get("probe") != {
            "kind": "plane-python-catalogue",
            "repository": REPOSITORY,
            "branch": "main",
            "registry": REGISTRY,
        }:
            raise Unverified("PROBE_UNSUPPORTED")
        public = public or PublicSource()
        commit = json.loads(public.get(f"https://api.github.com/repos/{REPOSITORY}/commits/main"))["sha"]
        if not isinstance(commit, str) or not SHA.fullmatch(commit):
            raise Unverified("UPSTREAM_REVISION_INVALID")
        result["upstream_commit"] = commit

        def fetch(path):
            return public.get(f"https://raw.githubusercontent.com/{REPOSITORY}/{commit}/{path}")

        advertised, aliases, unmapped, hashes = catalogue(fetch)
        available = advertised | set(aliases)
        missing = sorted(set(expected) - available)
        result.update(
            status="NAME_DRIFT" if missing else "NO_NAME_DRIFT",
            missing_tools=missing,
            declared_aliases={name: aliases[name] for name in expected if name in aliases},
            explicitly_unmapped=sorted(set(expected) & set(unmapped)),
            source_sha256=hashes,
            captured_tool_count=len(expected),
        )
    except (Unverified, OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        result["reason"] = str(exc) if isinstance(exc, Unverified) else "PROBE_INPUT_OR_SOURCE_INVALID"
    return result


def run(root, config, public=None):
    if config.get("schema_version") != 1 or not isinstance(config.get("plugins"), list):
        raise Unverified("CONFIG_SCHEMA_INVALID")
    entries = config["plugins"]
    if not entries or len(entries) > 40 or any(not isinstance(entry, dict) for entry in entries):
        raise Unverified("CONFIG_ENTRIES_INVALID")
    configured = [entry.get("plugin") for entry in entries]
    if len(configured) != len(set(configured)):
        raise Unverified("CONFIG_DUPLICATE_PLUGIN")
    discovered = {
        str(path.parent.parent.relative_to(root)) for path in (root / "plugins").glob("*/*/.forge/research.md")
    }
    public = public or PublicSource()
    rows = [inspect(root, entry, public) for entry in entries]
    for plugin in sorted(discovered - set(configured)):
        rows.append({"plugin": plugin, "status": "UNVERIFIED", "reason": "NO_REVIEWED_PROBE"})
    return {
        "schema_version": 1,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "scope": "public source tool-name catalogue; not live API execution or parameter compatibility",
        "results": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "scripts/forge-api-surfaces.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = run(ROOT, json.loads(args.config.read_text()))
    except (Unverified, OSError, ValueError, TypeError) as exc:
        report = {
            "schema_version": 1,
            "results": [],
            "status": "UNVERIFIED",
            "reason": str(exc) if isinstance(exc, Unverified) else "CONFIG_INVALID",
        }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    statuses = {row["status"] for row in report["results"]}
    if report.get("status") == "UNVERIFIED" or "UNVERIFIED" in statuses or not statuses:
        return 2
    return 1 if "NAME_DRIFT" in statuses else 0


if __name__ == "__main__":
    raise SystemExit(main())
