#!/usr/bin/env python3
"""
rebuild-inventory.py — Versioned repository scanner for claude-code-plugins.

Inserts the next unpublished discovery run into the Freshie inventory SQLite
database after checking its lineage against committed Dolt history.

Usage:
    python3 rebuild-inventory.py [--dry-run] [--db PATH] [--run-id N]

Flags:
    --dry-run     Show what would be scanned; do not write to DB.
    --db PATH     Path to the inventory SQLite file.
                  Default: ./inventory.sqlite (relative to script location).
    --run-id N    Select an unpublished run_id (default: auto-detect next).
    --diff-only   Print run comparison and exit without scanning.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_identity


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Derive the repo root from this file's location (freshie/scripts/…) so the
# scanner works from any checkout, including git worktrees — a hardcoded
# absolute path silently scanned the MAIN checkout when run from a worktree.
REPO_ROOT = Path(__file__).resolve().parents[2]
DB_DEFAULT = Path(__file__).parent.parent / "inventory.sqlite"

SKIP_DIRS: frozenset[str] = frozenset(
    {
        "node_modules",
        "dist",
        "__pycache__",
        ".git",
        "freshie",
        ".pnpm-store",
        ".pnpm",
        "coverage",
        ".nyc_output",
    }
)

# marketplace/src is website source — skip it; only scan marketplace/scripts
SKIP_PATHS: tuple[str, ...] = (
    "marketplace/src",
    "marketplace/node_modules",
    "marketplace/dist",
)

# Tables that are populated by the validator tool — leave completely untouched
VALIDATOR_TABLES: frozenset[str] = frozenset({"skill_compliance", "agent_compliance", "plugin_compliance"})

# Tables whose rows are entirely NPM-registry data — separate scan tool
NPM_TABLES: frozenset[str] = frozenset(
    {
        "npm_discovery_runs",
        "npm_dist_tags",
        "npm_download_stats",
        "npm_fetch_log",
        "npm_package_dependencies",
        "npm_packages",
        "npm_publish_history_summary",
        "npm_version_comparisons",
        "npm_versions",
        "repo_package_sources",
    }
)

# All user-data tables that get a run_id column
RUN_ID_TABLES: list[str] = [
    "packs",
    "plugins",
    "skills",
    "plugin_companions",
    "pack_metadata",
    "frontmatter_fields",
    "frontmatter_values",
    "frontmatter_shapes",
    "plugin_fields",
    "plugin_values",
    "plugin_shapes",
    "skill_files",
    "skill_structure_shapes",
    "unique_filenames",
    "unique_subdirs",
    "unique_extensions",
    "content_signals",
    "pack_aggregates",
    "command_files",
    "agent_files",
    "duplicate_files",
    "cross_references",
    "anomalies",
    "restructure_observations",
    "field_registry",
    "root_files",
    "scripts",
    "validators",
    "validator_checks",
    "docs",
    "ci_workflows",
    "marketplace_catalog",
    "planned_skills",
    "root_skills_files",
    "skill_database_vendors",
    "plugin_templates",
]


# ---------------------------------------------------------------------------
# Helpers — path / filesystem
# ---------------------------------------------------------------------------


def should_skip(path: Path) -> bool:
    """Return True if any path component is in the skip list."""
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return True
    rel = str(path.relative_to(REPO_ROOT)) if path.is_absolute() else str(path)
    for skip in SKIP_PATHS:
        if rel.startswith(skip):
            return True
    return False


def count_lines(path: Path) -> int:
    try:
        return sum(1 for _ in path.open("r", encoding="utf-8", errors="replace"))
    except OSError:
        return 0


def word_count(text: str) -> int:
    return len(text.split())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def rel(path: Path) -> str:
    """Return a canonical repository-relative path or refuse the input.

    Freshie rows are durable and publicly exported to Dolt, so recording an
    absolute checkout path would make identical trees differ by machine or
    worktree name.  Resolving both sides also prevents a symlink inside the
    checkout from smuggling an outside path into the inventory.
    """
    resolved_root = REPO_ROOT.resolve()
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError as exc:
        raise ValueError(
            f"refusing path outside repository root: {resolved_path} "
            f"(repository root: {resolved_root})"
        ) from exc


def git_commit_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


# ---------------------------------------------------------------------------
# Helpers — YAML frontmatter parser (no external deps)
# ---------------------------------------------------------------------------


def _parse_yaml_value(raw: str) -> Any:
    """
    Parse a single YAML scalar. Handles: null, booleans, ints, floats,
    quoted strings, bare strings, and bracketed lists.
    """
    v = raw.strip()
    if v in ("null", "~", ""):
        return None
    if v in ("true", "True", "TRUE"):
        return True
    if v in ("false", "False", "FALSE"):
        return False
    # Bracketed inline list
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1]
        return [_parse_yaml_value(item) for item in inner.split(",") if item.strip()]
    # Quoted string
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    # Numeric
    try:
        if "." in v:
            return float(v)
        return int(v)
    except ValueError:
        pass
    return v


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """
    Extract YAML frontmatter from Markdown text.

    Returns (frontmatter_dict, body_text).
    Handles: scalars, block scalars (| and >), inline lists, and multiline
    block sequences (- item).

    The block-scalar bug from the original recon is fixed here: we exit a
    block scalar only when we see a non-indented key: line OR the closing ---.
    """
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    # Find closing ---
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}, text

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])

    result: dict[str, Any] = {}
    current_key: str | None = None
    current_value_lines: list[str] = []
    in_block_scalar = False
    block_type: str = ""  # '|' or '>'
    in_sequence: bool = False  # multiline block sequence

    KEY_RE = re.compile(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)")

    def flush_current():
        nonlocal current_key, current_value_lines, in_block_scalar, in_sequence, block_type
        if current_key is None:
            return
        if in_block_scalar:
            joined = "\n".join(current_value_lines)
            result[current_key] = joined.strip()
        elif in_sequence:
            result[current_key] = [v.lstrip("- ").strip() for v in current_value_lines]
        else:
            result[current_key] = _parse_yaml_value(" ".join(current_value_lines).strip())
        current_key = None
        current_value_lines = []
        in_block_scalar = False
        in_sequence = False
        block_type = ""

    for line in fm_lines:
        # Non-indented key: value line ends any active block
        m = KEY_RE.match(line)
        if m and (not line.startswith(" ") and not line.startswith("\t")):
            flush_current()
            current_key = m.group(1)
            raw_val = m.group(2).strip()
            if raw_val in ("|", ">"):
                in_block_scalar = True
                block_type = raw_val
            elif raw_val == "":
                # Could be a sequence on next lines
                in_sequence = True
            else:
                current_value_lines = [raw_val]
            continue

        # Indented continuation
        stripped = line.strip()
        if in_block_scalar:
            current_value_lines.append(line.rstrip())
        elif in_sequence and stripped.startswith("-"):
            current_value_lines.append(stripped)
        elif current_key and not in_block_scalar and not in_sequence:
            # Continuation of a scalar (folded)
            current_value_lines.append(stripped)

    flush_current()
    return result, body


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------


def open_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# Authoritative discovery-table schema, captured from the live inventory.sqlite
# (2026-07-14). Lets a fresh environment (e.g. the promote-curated.yml
# `rebuild_inventory: true` dispatch, where the untracked sqlite blob is always
# absent) bootstrap a working DB instead of exiting 1. Idempotent — every
# statement is CREATE TABLE IF NOT EXISTS, so running it against an existing DB
# is a no-op. The validator's --populate-db creates its own compliance tables;
# the NPM tables belong to a separate scan tool.
SCHEMA_DDL: tuple[str, ...] = (
    """CREATE TABLE IF NOT EXISTS discovery_runs (
        id INTEGER PRIMARY KEY, run_date TEXT, commit_hash TEXT,
        total_packs INTEGER, total_plugins INTEGER, total_skills INTEGER,
        total_files INTEGER, total_root_files INTEGER)""",
    """CREATE TABLE IF NOT EXISTS packs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT,
        plugin_count INTEGER, skill_count INTEGER, file_count INTEGER,
        has_readme INTEGER, has_changelog INTEGER, has_package_json INTEGER,
        category_indicator TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS plugins (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT,
        pack_name TEXT, has_readme INTEGER, has_package_json INTEGER,
        plugin_json_shape TEXT, file_count INTEGER, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT,
        pack_name TEXT, plugin_name TEXT, structure_shape TEXT,
        file_count INTEGER, has_references INTEGER, has_scripts INTEGER,
        has_assets INTEGER, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS plugin_companions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, plugin_path TEXT,
        plugin_json_path TEXT, pack_name TEXT,
        has_readme INTEGER, has_package_json INTEGER, has_mcp_json INTEGER,
        has_src_dir INTEGER, has_commands_dir INTEGER,
        has_agents_dir INTEGER, has_skills_dir INTEGER, file_count INTEGER,
        run_id INTEGER, has_hooks_dir INTEGER, has_lsp_json INTEGER,
        has_settings_json INTEGER, has_license INTEGER, has_changelog INTEGER)""",
    """CREATE TABLE IF NOT EXISTS pack_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pack_name TEXT,
        files_present TEXT, category_indicators TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS frontmatter_fields (
        id INTEGER PRIMARY KEY AUTOINCREMENT, field_name TEXT, data_types TEXT,
        count INTEGER, percentage REAL, unique_value_count INTEGER,
        value_pattern TEXT, sample_values_json TEXT, blank_count INTEGER,
        run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS frontmatter_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT, skill_path TEXT,
        field_name TEXT, raw_value TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS frontmatter_shapes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, keys TEXT,
        count INTEGER, key_count INTEGER, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS plugin_fields (
        id INTEGER PRIMARY KEY AUTOINCREMENT, field_name TEXT, data_types TEXT,
        count INTEGER, percentage REAL, unique_value_count INTEGER,
        sample_values_json TEXT, blank_count INTEGER, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS plugin_values (
        id INTEGER PRIMARY KEY AUTOINCREMENT, plugin_path TEXT,
        field_name TEXT, raw_value TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS plugin_shapes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, keys TEXT,
        count INTEGER, key_count INTEGER, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS skill_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, filename TEXT,
        extension TEXT, size_bytes INTEGER, parent_skill TEXT,
        relative_path TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS skill_structure_shapes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, shape_description TEXT,
        skill_count INTEGER, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS unique_filenames (
        id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, count INTEGER,
        run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS unique_subdirs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, subdir_name TEXT, count INTEGER,
        run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS unique_extensions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, extension TEXT, count INTEGER,
        run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS content_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, skill_path TEXT, pack_name TEXT,
        plugin_name TEXT, line_count INTEGER, word_count INTEGER,
        code_block_count INTEGER, comment_only_code_block_count INTEGER,
        import_code_block_count INTEGER, url_code_block_count INTEGER,
        real_url_count INTEGER, real_import_count INTEGER,
        placeholder_step INTEGER, placeholder_todo INTEGER,
        placeholder_implementation INTEGER, placeholder_add INTEGER,
        placeholder_your INTEGER, placeholder_api_key INTEGER,
        placeholder_token INTEGER, placeholder_api_example INTEGER,
        placeholder_example INTEGER, placeholder_table_error INTEGER,
        run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS pack_aggregates (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pack_name TEXT,
        skill_count INTEGER, total_lines INTEGER, total_words INTEGER,
        total_code_blocks INTEGER, total_comment_only INTEGER,
        total_placeholders INTEGER, total_real_urls INTEGER,
        total_real_imports INTEGER, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS command_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT, plugin_path TEXT, pack_name TEXT, plugin_name TEXT,
        filename TEXT, fm_name TEXT, fm_description TEXT, fm_shortcut TEXT,
        fm_category TEXT, fm_difficulty TEXT, fm_all_keys TEXT,
        line_count INTEGER, word_count INTEGER, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS agent_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT, plugin_path TEXT, pack_name TEXT, plugin_name TEXT,
        filename TEXT, fm_name TEXT, fm_description TEXT,
        fm_capabilities TEXT, fm_expertise_level TEXT, fm_activation_priority TEXT,
        fm_effort TEXT, fm_max_turns INTEGER, fm_disallowed_tools TEXT,
        fm_all_keys TEXT, line_count INTEGER, word_count INTEGER,
        run_id INTEGER, fm_tools TEXT, fm_skills TEXT, fm_memory TEXT,
        fm_background INTEGER, fm_isolation TEXT, fm_permission_mode TEXT)""",
    """CREATE TABLE IF NOT EXISTS duplicate_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT, sha256 TEXT,
        file_count INTEGER, file_paths_json TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS cross_references (
        id INTEGER PRIMARY KEY AUTOINCREMENT, source_path TEXT,
        target_path_or_entity TEXT, linkage_type TEXT,
        direct_or_inferred TEXT, confidence TEXT, evidence TEXT,
        run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS anomalies (
        id INTEGER PRIMARY KEY AUTOINCREMENT, anomaly_type TEXT,
        path TEXT, count INTEGER, evidence TEXT, notes TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS restructure_observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT, observation_type TEXT,
        paths_json TEXT, evidence TEXT, category TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS field_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT, field_name TEXT,
        source TEXT, data_type TEXT, found_in_count INTEGER,
        found_in_total INTEGER, value_patterns TEXT, example TEXT,
        validated_by TEXT, notes TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS root_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, extension TEXT,
        line_count INTEGER, size_bytes INTEGER, inferred_purpose TEXT,
        run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, language TEXT,
        purpose TEXT, script_type TEXT, arguments TEXT, inputs TEXT,
        outputs TEXT, dependencies TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS validators (
        id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, entity_type TEXT,
        checks_json TEXT, fields_read TEXT, scoring_behavior TEXT,
        cli_flags TEXT, output_format TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS validator_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, validator_path TEXT,
        field_checked TEXT, rule_description TEXT, scoring_behavior TEXT,
        run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS docs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT, doc_type TEXT,
        apparent_subject TEXT, subject_type TEXT, line_count INTEGER,
        word_count INTEGER, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS ci_workflows (
        id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, name TEXT,
        triggers TEXT, jobs_json TEXT, scripts_called TEXT, env_vars TEXT,
        run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS marketplace_catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, source TEXT, description TEXT, version TEXT,
        category TEXT, keywords TEXT, author TEXT,
        components TEXT, verification TEXT,
        featured INTEGER, mcp_tools TEXT, plugin_count INTEGER,
        pricing TEXT, zcf_metadata TEXT, external_sync TEXT,
        all_keys TEXT, raw_json TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS planned_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT, filename TEXT, extension TEXT,
        line_count INTEGER, word_count INTEGER, size_bytes INTEGER,
        apparent_skill_name TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS root_skills_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT, filename TEXT, extension TEXT,
        line_count INTEGER, word_count INTEGER, size_bytes INTEGER,
        parent_dir TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS skill_database_vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT, path TEXT, file_count INTEGER,
        total_size_bytes INTEGER, file_extensions TEXT,
        sample_fields TEXT, run_id INTEGER)""",
    """CREATE TABLE IF NOT EXISTS plugin_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT, filename TEXT, extension TEXT,
        line_count INTEGER, size_bytes INTEGER, template_type TEXT,
        run_id INTEGER)""",
)


def bootstrap_schema(conn: sqlite3.Connection) -> None:
    """Create every discovery table that does not exist yet (idempotent)."""
    cursor = conn.cursor()
    for ddl in SCHEMA_DDL:
        cursor.execute(ddl)
    conn.commit()


def purge_incomplete_latest_run(conn: sqlite3.Connection) -> None:
    """Purge the newest discovery run if it never completed (crash recovery).

    The discovery_runs row is inserted BEFORE scanning and its totals are only
    filled by the final UPDATE, so NULL totals on the newest run = a crashed
    half-run. Left in place, the default rerun would compute MAX(id)+1 and the
    phantom partial run would be exported permanently into the append-only Dolt
    system of record (and --populate-db would stamp compliance rows onto it).
    Only the NEWEST run is eligible: an older incomplete run has already been
    exported, and deleting it locally would rewrite published Dolt history.
    """
    row = conn.execute(
        "SELECT id, total_skills, total_files FROM discovery_runs ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return
    if row["total_skills"] is None and row["total_files"] is None:
        print(
            f"  WARNING: newest run_id={row['id']} has NULL totals — a crashed "
            f"half-run. Purging it before starting (its id will be reused)."
        )
        purge_run(conn, row["id"])


def migrate_add_run_id(conn: sqlite3.Connection) -> None:
    """
    Add run_id INTEGER column to every target table that doesn't have it yet,
    then tag all existing rows as run_id=1.
    """
    cursor = conn.cursor()
    for table in RUN_ID_TABLES:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            continue
        # Check if run_id column already present
        cursor.execute(f"PRAGMA table_info({table})")
        cols = {row["name"] for row in cursor.fetchall()}
        if "run_id" not in cols:
            print(f"  [migrate] ALTER TABLE {table} ADD COLUMN run_id INTEGER")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN run_id INTEGER")
            cursor.execute(f"UPDATE {table} SET run_id=1 WHERE run_id IS NULL")
    conn.commit()


def purge_run(conn: sqlite3.Connection, run_id: int) -> None:
    """Delete all rows tagged with run_id from every target table (idempotent re-runs)."""
    cursor = conn.cursor()
    for table in RUN_ID_TABLES:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            continue
        cursor.execute(f"PRAGMA table_info({table})")
        cols = {row["name"] for row in cursor.fetchall()}
        if "run_id" in cols:
            cursor.execute(f"DELETE FROM {table} WHERE run_id=?", (run_id,))
    # Remove discovery run record itself
    cursor.execute("DELETE FROM discovery_runs WHERE id=?", (run_id,))
    conn.commit()


def next_run_id(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT MAX(id) FROM discovery_runs").fetchone()
    return (row[0] or 0) + 1


# ---------------------------------------------------------------------------
# Scanner — Group 1: Packs, Plugins, Skills
# ---------------------------------------------------------------------------


def _walk_plugin_dir(plugin_dir: Path) -> tuple[int, int, int]:
    """Return (skill_count, file_count, command_count) for a plugin directory."""
    skills = 0
    files = 0
    skills_dir = plugin_dir / "skills"
    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if item.is_dir():
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    skills += 1
    for p in plugin_dir.rglob("*"):
        if p.is_file() and not should_skip(p):
            files += 1
    return skills, files, 0


def scan_packs_plugins_skills(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
) -> tuple[int, int, int]:
    """Scan plugins/ tree; populate packs, plugins, skills, plugin_companions."""
    plugins_dir = REPO_ROOT / "plugins"
    total_packs = 0
    total_plugins = 0
    total_skills = 0

    # Enumerate all "pack" directories.
    # A pack is any direct child of plugins/ (including mcp, saas-packs as special packs,
    # and nested packs like saas-packs/adobe-pack).
    pack_dirs: list[Path] = []

    for child in sorted(plugins_dir.iterdir()):
        if not child.is_dir():
            continue
        name = child.name
        if name in SKIP_DIRS:
            continue
        if name == "packages":
            continue  # packages/ under plugins is unusual; skip
        # saas-packs is one pack (consistent with run_id=1 definition)
        # Individual saas packs are plugins within it, not separate packs
        pack_dirs.append(child)

    print(f"  Found {len(pack_dirs)} packs")

    for pack_dir in pack_dirs:
        pack_name = pack_dir.name
        pack_rel = rel(pack_dir)

        # Is this pack itself a plugin (has .claude-plugin/plugin.json at root)?
        pack_has_plugin_json = (pack_dir / ".claude-plugin" / "plugin.json").exists()

        # Find all plugin directories within this pack
        plugin_dirs: list[Path] = []

        if pack_has_plugin_json:
            # The pack itself is the only plugin
            plugin_dirs.append(pack_dir)
        elif (pack_dir / "skills").exists() and not pack_has_plugin_json:
            # SaaS pack: skills are direct children of pack/skills/
            # No sub-plugin directories; treat pack as the plugin container
            plugin_dirs.append(pack_dir)
        else:
            # Regular pack: walk for sub-dirs that have .claude-plugin/plugin.json
            for sub in sorted(pack_dir.iterdir()):
                if sub.is_dir() and not sub.name.startswith(".") and sub.name not in SKIP_DIRS:
                    if (sub / ".claude-plugin" / "plugin.json").exists():
                        plugin_dirs.append(sub)

        # Count pack-level totals
        pack_plugin_count = len(plugin_dirs)
        pack_skill_count = 0
        pack_file_count = 0
        for p in pack_dir.rglob("*"):
            if p.is_file() and not should_skip(p):
                pack_file_count += 1

        pack_has_readme = int((pack_dir / "README.md").exists())
        pack_has_changelog = int((pack_dir / "CHANGELOG.md").exists())
        pack_has_pkg_json = int((pack_dir / "package.json").exists())
        category_indicator = pack_dir.parent.name if pack_dir.parent.name != "plugins" else pack_name

        # Insert pack row (we'll update skill_count after scanning plugins)
        if not dry_run:
            conn.execute(
                """INSERT INTO packs
                   (run_id, name, path, plugin_count, skill_count, file_count,
                    has_readme, has_changelog, has_package_json, category_indicator)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    run_id,
                    pack_name,
                    pack_rel,
                    pack_plugin_count,
                    0,  # updated below
                    pack_file_count,
                    pack_has_readme,
                    pack_has_changelog,
                    pack_has_pkg_json,
                    category_indicator,
                ),
            )

        # Scan each plugin
        for plugin_dir in plugin_dirs:
            plugin_name = plugin_dir.name
            plugin_rel = rel(plugin_dir)
            p_has_readme = int((plugin_dir / "README.md").exists())
            p_has_pkg_json = int((plugin_dir / "package.json").exists())
            p_has_mcp_json = int((plugin_dir / ".mcp.json").exists() or (plugin_dir / "mcp" / ".mcp.json").exists())
            p_has_src = int((plugin_dir / "src").exists())
            p_has_commands = int((plugin_dir / "commands").exists())
            p_has_agents = int((plugin_dir / "agents").exists())
            p_has_skills = int((plugin_dir / "skills").exists())
            p_file_count = sum(1 for p in plugin_dir.rglob("*") if p.is_file() and not should_skip(p))

            # Plugin JSON shape
            pjson_path = plugin_dir / ".claude-plugin" / "plugin.json"
            plugin_json_shape = ""
            if pjson_path.exists():
                try:
                    pjson = json.loads(pjson_path.read_text(encoding="utf-8"))
                    plugin_json_shape = ",".join(sorted(pjson.keys()))
                except Exception:
                    plugin_json_shape = "parse_error"

            # Scan skills for this plugin.
            # Only directories that contain a SKILL.md file are skills — bare
            # subdirectories like `skills/skill-adapter/` (helper code shipped
            # alongside skills) are NOT skills. Counting them inflates the
            # skills total and creates rows that the validator's compliance
            # walker (which keys off SKILL.md) cannot match — see issue #594.
            skill_dirs: list[Path] = []
            skills_dir = plugin_dir / "skills"
            if skills_dir.exists():
                for skill_sub in sorted(skills_dir.iterdir()):
                    if skill_sub.is_dir() and skill_sub.name not in SKIP_DIRS and (skill_sub / "SKILL.md").exists():
                        skill_dirs.append(skill_sub)

            plugin_skill_count = len(skill_dirs)
            pack_skill_count += plugin_skill_count

            if not dry_run:
                conn.execute(
                    """INSERT INTO plugins
                       (run_id, name, path, pack_name, has_readme, has_package_json,
                        plugin_json_shape, file_count)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        run_id,
                        plugin_name,
                        plugin_rel,
                        pack_name,
                        p_has_readme,
                        p_has_pkg_json,
                        plugin_json_shape,
                        p_file_count,
                    ),
                )
                conn.execute(
                    """INSERT INTO plugin_companions
                       (run_id, plugin_path, plugin_json_path, pack_name,
                        has_readme, has_package_json, has_mcp_json,
                        has_src_dir, has_commands_dir, has_agents_dir,
                        has_skills_dir, file_count)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        run_id,
                        plugin_rel,
                        rel(pjson_path) if pjson_path.exists() else "",
                        pack_name,
                        p_has_readme,
                        p_has_pkg_json,
                        p_has_mcp_json,
                        p_has_src,
                        p_has_commands,
                        p_has_agents,
                        p_has_skills,
                        p_file_count,
                    ),
                )

            # Insert skill rows
            for skill_dir in skill_dirs:
                skill_name = skill_dir.name
                skill_rel = rel(skill_dir)
                s_files = list(f for f in skill_dir.rglob("*") if f.is_file())
                s_file_count = len(s_files)

                # Structure shape
                subdirs_in_skill = sorted(d.name for d in skill_dir.iterdir() if d.is_dir())
                has_skill_md = int((skill_dir / "SKILL.md").exists())
                has_refs = int((skill_dir / "references").exists())
                has_scripts = int((skill_dir / "scripts").exists())
                has_assets = int((skill_dir / "assets").exists())

                parts_list = []
                if has_skill_md:
                    parts_list.append("SKILL.md")
                parts_list.extend(subdirs_in_skill)
                structure_shape = "+".join(parts_list) if parts_list else "empty"

                if not dry_run:
                    conn.execute(
                        """INSERT INTO skills
                           (run_id, name, path, pack_name, plugin_name,
                            structure_shape, file_count,
                            has_references, has_scripts, has_assets)
                           VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (
                            run_id,
                            skill_name,
                            skill_rel,
                            pack_name,
                            plugin_name,
                            structure_shape,
                            s_file_count,
                            has_refs,
                            has_scripts,
                            has_assets,
                        ),
                    )

                total_skills += 1

            total_plugins += 1

        # Update pack skill_count
        if not dry_run:
            conn.execute(
                "UPDATE packs SET skill_count=? WHERE run_id=? AND name=?",
                (pack_skill_count, run_id, pack_name),
            )

        # Pack metadata
        files_present = []
        for p in pack_dir.iterdir():
            if p.is_file():
                files_present.append(p.name)
        cat_indicators = [child.name for child in pack_dir.iterdir() if child.is_dir() and child.name not in SKIP_DIRS][
            :10
        ]

        if not dry_run:
            conn.execute(
                """INSERT INTO pack_metadata
                   (run_id, pack_name, files_present, category_indicators)
                   VALUES (?,?,?,?)""",
                (
                    run_id,
                    pack_name,
                    json.dumps(sorted(files_present)),
                    json.dumps(sorted(cat_indicators)),
                ),
            )

        total_packs += 1

    if not dry_run:
        conn.commit()

    print(f"  Packs: {total_packs}, Plugins: {total_plugins}, Skills: {total_skills}")
    return total_packs, total_plugins, total_skills


# ---------------------------------------------------------------------------
# Scanner — Group 2: Frontmatter
# ---------------------------------------------------------------------------


def _collect_skill_mds() -> list[Path]:
    skill_mds = []
    for p in (REPO_ROOT / "plugins").rglob("SKILL.md"):
        if not should_skip(p):
            skill_mds.append(p)
    return skill_mds


def _collect_command_mds() -> list[Path]:
    result = []
    for p in (REPO_ROOT / "plugins").rglob("commands/*.md"):
        if not should_skip(p):
            result.append(p)
    return result


def _collect_agent_mds() -> list[Path]:
    result = []
    for p in (REPO_ROOT / "plugins").rglob("agents/*.md"):
        if not should_skip(p):
            result.append(p)
    return result


def scan_frontmatter(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
    skill_mds: list[Path],
) -> None:
    """Populate frontmatter_values, frontmatter_fields, frontmatter_shapes."""
    print(f"  Parsing frontmatter from {len(skill_mds)} SKILL.md files...")

    # field -> list of values
    field_values: dict[str, list[Any]] = defaultdict(list)
    shape_counter: dict[str, int] = defaultdict(int)

    batch: list[tuple] = []
    for skill_md in skill_mds:
        try:
            text = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm, _ = parse_frontmatter(text)
        if not fm:
            continue

        skill_path = rel(skill_md)
        keys_sorted = ",".join(sorted(fm.keys()))
        shape_counter[keys_sorted] += 1

        for field, value in fm.items():
            raw_val = str(value) if value is not None else ""
            field_values[field].append(raw_val)
            batch.append((run_id, skill_path, field, raw_val))

    if not dry_run and batch:
        conn.executemany(
            "INSERT INTO frontmatter_values (run_id, skill_path, field_name, raw_value) VALUES (?,?,?,?)",
            batch,
        )

    # Aggregate field stats
    total_skills = len(skill_mds)
    field_batch: list[tuple] = []
    for field, values in field_values.items():
        unique_vals = set(values)
        blank_count = sum(1 for v in values if not v.strip())
        data_types = ",".join(
            sorted(
                {
                    ("int" if v.lstrip("-").isdigit() else "float" if re.match(r"^-?\d+\.\d+$", v) else "str")
                    for v in values
                    if v.strip()
                }
            )
        )
        sample = json.dumps(list(unique_vals)[:5])
        pct = round(len(values) / total_skills * 100, 2) if total_skills else 0.0
        field_batch.append(
            (
                run_id,
                field,
                data_types or "str",
                len(values),
                pct,
                len(unique_vals),
                sample,
                blank_count,
            )
        )

    if not dry_run and field_batch:
        conn.executemany(
            """INSERT INTO frontmatter_fields
               (run_id, field_name, data_types, count, percentage,
                unique_value_count, sample_values_json, blank_count)
               VALUES (?,?,?,?,?,?,?,?)""",
            field_batch,
        )

    # Shapes
    shape_batch = [(run_id, keys, count, len(keys.split(",")) if keys else 0) for keys, count in shape_counter.items()]
    if not dry_run and shape_batch:
        conn.executemany(
            "INSERT INTO frontmatter_shapes (run_id, keys, count, key_count) VALUES (?,?,?,?)",
            shape_batch,
        )

    if not dry_run:
        conn.commit()

    print(f"  Frontmatter: {len(field_values)} unique fields, {len(shape_counter)} shapes")


def scan_plugin_frontmatter(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
) -> None:
    """Populate plugin_values, plugin_fields, plugin_shapes from plugin.json files."""
    pjson_files = [p for p in (REPO_ROOT / "plugins").rglob(".claude-plugin/plugin.json") if not should_skip(p)]
    print(f"  Parsing {len(pjson_files)} plugin.json files...")

    field_values: dict[str, list[str]] = defaultdict(list)
    shape_counter: dict[str, int] = defaultdict(int)
    batch: list[tuple] = []

    for pjson_path in pjson_files:
        try:
            pjson = json.loads(pjson_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        plugin_path = rel(pjson_path.parent.parent)
        keys_sorted = ",".join(sorted(pjson.keys()))
        shape_counter[keys_sorted] += 1
        for field, value in pjson.items():
            raw = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
            field_values[field].append(raw)
            batch.append((run_id, plugin_path, field, raw))

    if not dry_run and batch:
        conn.executemany(
            "INSERT INTO plugin_values (run_id, plugin_path, field_name, raw_value) VALUES (?,?,?,?)",
            batch,
        )

    total = len(pjson_files)
    field_batch = []
    for field, values in field_values.items():
        unique_vals = set(values)
        blank = sum(1 for v in values if not v.strip())
        pct = round(len(values) / total * 100, 2) if total else 0.0
        field_batch.append(
            (
                run_id,
                field,
                "mixed",
                len(values),
                pct,
                len(unique_vals),
                json.dumps(list(unique_vals)[:5]),
                blank,
            )
        )

    if not dry_run and field_batch:
        conn.executemany(
            """INSERT INTO plugin_fields
               (run_id, field_name, data_types, count, percentage,
                unique_value_count, sample_values_json, blank_count)
               VALUES (?,?,?,?,?,?,?,?)""",
            field_batch,
        )

    shape_batch = [(run_id, keys, count, len(keys.split(",")) if keys else 0) for keys, count in shape_counter.items()]
    if not dry_run and shape_batch:
        conn.executemany(
            "INSERT INTO plugin_shapes (run_id, keys, count, key_count) VALUES (?,?,?,?)",
            shape_batch,
        )

    if not dry_run:
        conn.commit()


# ---------------------------------------------------------------------------
# Scanner — Group 3: Skill file analysis
# ---------------------------------------------------------------------------


PLACEHOLDER_PATTERNS: dict[str, re.Pattern] = {
    "placeholder_step": re.compile(r"\bStep\s+\d+\b", re.I),
    "placeholder_todo": re.compile(r"\bTODO\b"),
    "placeholder_implementation": re.compile(r"\bImplementation\b", re.I),
    "placeholder_add": re.compile(r"\bAdd\s+your\b", re.I),
    "placeholder_your": re.compile(r"\bYour\s+\w+\s+here\b", re.I),
    "placeholder_api_key": re.compile(r"\bYOUR_API_KEY\b|\byour_api_key\b"),
    "placeholder_token": re.compile(r"\bYOUR_TOKEN\b|\byour_token\b"),
    "placeholder_api_example": re.compile(r"\bapi[-_]example\b", re.I),
    "placeholder_example": re.compile(r"\bEXAMPLE\b"),
    "placeholder_table_error": re.compile(r"\|\s*Error\s*\|", re.I),
}

URL_RE = re.compile(r'https?://[^\s\)>\]"\'`]+')
IMPORT_RE = re.compile(r"^(?:import|from)\s+\S", re.M)
CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.M)


def analyze_skill_content(text: str) -> dict[str, int]:
    """Extract content signals from SKILL.md body text."""
    lines = text.splitlines()
    words = len(text.split())
    code_blocks = CODE_BLOCK_RE.findall(text)
    cb_count = len(code_blocks)
    comment_only = sum(1 for cb in code_blocks if cb.strip().strip("`").strip().startswith("#"))
    import_cbs = sum(1 for cb in code_blocks if IMPORT_RE.search(cb))
    real_urls = URL_RE.findall(text)
    real_url_count = len(real_urls)
    url_cbs = sum(1 for cb in code_blocks if URL_RE.search(cb))
    real_imports = len(IMPORT_RE.findall(text))

    signals: dict[str, int] = {
        "line_count": len(lines),
        "word_count": words,
        "code_block_count": cb_count,
        "comment_only_code_block_count": comment_only,
        "import_code_block_count": import_cbs,
        "url_code_block_count": url_cbs,
        "real_url_count": real_url_count,
        "real_import_count": real_imports,
    }
    for key, pattern in PLACEHOLDER_PATTERNS.items():
        signals[key] = len(pattern.findall(text))
    return signals


def scan_skill_files(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
    skill_mds: list[Path],
) -> None:
    """Populate skill_files, skill_structure_shapes, unique_*, content_signals, pack_aggregates."""
    print("  Scanning skill file trees...")

    # Collect all skill directories
    skill_dirs: set[Path] = set()
    for skill_md in skill_mds:
        skill_dirs.add(skill_md.parent)

    # Also scan non-SKILL.md skill dirs (references-only)
    for p in (REPO_ROOT / "plugins").rglob("skills"):
        if p.is_dir() and not should_skip(p):
            for sub in p.iterdir():
                if sub.is_dir():
                    skill_dirs.add(sub)

    all_filenames: dict[str, int] = defaultdict(int)
    all_subdirs: dict[str, int] = defaultdict(int)
    all_extensions: dict[str, int] = defaultdict(int)
    shape_counter: dict[str, int] = defaultdict(int)

    skill_file_batch: list[tuple] = []
    content_batch: list[tuple] = []

    # Pack aggregates accumulator
    pack_agg: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "skill_count": 0,
            "total_lines": 0,
            "total_words": 0,
            "total_code_blocks": 0,
            "total_comment_only": 0,
            "total_placeholders": 0,
            "total_real_urls": 0,
            "total_real_imports": 0,
        }
    )

    for skill_dir in sorted(skill_dirs):
        skill_path = rel(skill_dir)

        # Determine pack name from path
        parts = skill_dir.parts
        try:
            plugins_idx = parts.index("plugins")
            pack_name_raw = parts[plugins_idx + 1]
            if pack_name_raw == "saas-packs" and len(parts) > plugins_idx + 2:
                pack_name_raw = parts[plugins_idx + 2]
        except (ValueError, IndexError):
            pack_name_raw = "unknown"

        # Plugin name
        try:
            skills_idx = next(i for i, p in enumerate(parts) if p == "skills" and i > 1)
            plugin_name = parts[skills_idx - 1]
        except StopIteration:
            plugin_name = "unknown"

        # Shape from subdirs
        subdirs_in_skill = sorted(d.name for d in skill_dir.iterdir() if d.is_dir())
        has_skill_md = int((skill_dir / "SKILL.md").exists())
        shape_parts: list[str] = []
        if has_skill_md:
            shape_parts.append("SKILL.md")
        shape_parts.extend(subdirs_in_skill)
        shape_key = "+".join(shape_parts) if shape_parts else "empty"
        shape_counter[shape_key] += 1

        for d in subdirs_in_skill:
            all_subdirs[d] += 1

        for f in skill_dir.rglob("*"):
            if not f.is_file() or should_skip(f):
                continue
            fname = f.name
            ext = f.suffix.lower()
            size = file_size(f)
            all_filenames[fname] += 1
            all_extensions[ext if ext else "(none)"] += 1
            f_rel = str(f.relative_to(skill_dir))
            skill_file_batch.append((run_id, rel(f), fname, ext, size, skill_path, f_rel))

        # Content signals from SKILL.md
        skill_md_path = skill_dir / "SKILL.md"
        if skill_md_path.exists():
            try:
                raw = skill_md_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                raw = ""
            _, body = parse_frontmatter(raw)
            sigs = analyze_skill_content(body)

            placeholder_total = sum(v for k, v in sigs.items() if k.startswith("placeholder_"))

            agg = pack_agg[pack_name_raw]
            agg["skill_count"] += 1
            agg["total_lines"] += sigs["line_count"]
            agg["total_words"] += sigs["word_count"]
            agg["total_code_blocks"] += sigs["code_block_count"]
            agg["total_comment_only"] += sigs["comment_only_code_block_count"]
            agg["total_placeholders"] += placeholder_total
            agg["total_real_urls"] += sigs["real_url_count"]
            agg["total_real_imports"] += sigs["real_import_count"]

            content_batch.append(
                (
                    run_id,
                    skill_path,
                    pack_name_raw,
                    plugin_name,
                    sigs["line_count"],
                    sigs["word_count"],
                    sigs["code_block_count"],
                    sigs["comment_only_code_block_count"],
                    sigs["import_code_block_count"],
                    sigs["url_code_block_count"],
                    sigs["real_url_count"],
                    sigs["real_import_count"],
                    sigs.get("placeholder_step", 0),
                    sigs.get("placeholder_todo", 0),
                    sigs.get("placeholder_implementation", 0),
                    sigs.get("placeholder_add", 0),
                    sigs.get("placeholder_your", 0),
                    sigs.get("placeholder_api_key", 0),
                    sigs.get("placeholder_token", 0),
                    sigs.get("placeholder_api_example", 0),
                    sigs.get("placeholder_example", 0),
                    sigs.get("placeholder_table_error", 0),
                )
            )

    if not dry_run:
        if skill_file_batch:
            conn.executemany(
                """INSERT INTO skill_files
                   (run_id, path, filename, extension, size_bytes, parent_skill, relative_path)
                   VALUES (?,?,?,?,?,?,?)""",
                skill_file_batch,
            )
        if content_batch:
            conn.executemany(
                """INSERT INTO content_signals
                   (run_id, skill_path, pack_name, plugin_name, line_count, word_count,
                    code_block_count, comment_only_code_block_count,
                    import_code_block_count, url_code_block_count,
                    real_url_count, real_import_count,
                    placeholder_step, placeholder_todo, placeholder_implementation,
                    placeholder_add, placeholder_your, placeholder_api_key,
                    placeholder_token, placeholder_api_example,
                    placeholder_example, placeholder_table_error)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                content_batch,
            )

        # Shape summary
        shape_rows = [(run_id, shape, count) for shape, count in shape_counter.items()]
        conn.executemany(
            "INSERT INTO skill_structure_shapes (run_id, shape_description, skill_count) VALUES (?,?,?)",
            shape_rows,
        )

        # Unique filename/subdir/extension
        conn.executemany(
            "INSERT INTO unique_filenames (run_id, filename, count) VALUES (?,?,?)",
            [(run_id, fn, cnt) for fn, cnt in all_filenames.items()],
        )
        conn.executemany(
            "INSERT INTO unique_subdirs (run_id, subdir_name, count) VALUES (?,?,?)",
            [(run_id, sd, cnt) for sd, cnt in all_subdirs.items()],
        )
        conn.executemany(
            "INSERT INTO unique_extensions (run_id, extension, count) VALUES (?,?,?)",
            [(run_id, ext, cnt) for ext, cnt in all_extensions.items()],
        )

        # Pack aggregates
        conn.executemany(
            """INSERT INTO pack_aggregates
               (run_id, pack_name, skill_count, total_lines, total_words,
                total_code_blocks, total_comment_only, total_placeholders,
                total_real_urls, total_real_imports)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            [
                (
                    run_id,
                    pack_name,
                    agg["skill_count"],
                    agg["total_lines"],
                    agg["total_words"],
                    agg["total_code_blocks"],
                    agg["total_comment_only"],
                    agg["total_placeholders"],
                    agg["total_real_urls"],
                    agg["total_real_imports"],
                )
                for pack_name, agg in pack_agg.items()
            ],
        )
        conn.commit()

    print(
        f"  Skill files: {len(skill_file_batch)}, Content signals: {len(content_batch)}, Shapes: {len(shape_counter)}"
    )


# ---------------------------------------------------------------------------
# Scanner — Group: Commands and Agents
# ---------------------------------------------------------------------------


def scan_commands_agents(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
) -> tuple[int, int]:
    """Populate command_files and agent_files."""
    cmd_files = _collect_command_mds()
    agent_files_list = _collect_agent_mds()
    print(f"  Commands: {len(cmd_files)}, Agents: {len(agent_files_list)}")

    cmd_batch: list[tuple] = []
    for cmd_path in cmd_files:
        try:
            text = cmd_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm, body = parse_frontmatter(text)
        lines = text.splitlines()
        wc = word_count(text)

        # Derive every durable identity from the repository-relative path.
        # Absolute Path.parts includes the checkout prefix and previously
        # leaked it into command_files.plugin_path.
        command_rel = Path(rel(cmd_path))
        parts = command_rel.parts
        try:
            plugins_idx = parts.index("plugins")
            pack = parts[plugins_idx + 1]
            if pack == "saas-packs" and len(parts) > plugins_idx + 2:
                pack = parts[plugins_idx + 2]
            # plugin is the dir that contains the commands/ subdir
            cmd_idx = next(i for i, p in enumerate(parts) if p == "commands")
            plugin = parts[cmd_idx - 1]
            plugin_path = Path(*parts[:cmd_idx]).as_posix()
        except (ValueError, StopIteration, IndexError):
            pack = "unknown"
            plugin = "unknown"
            plugin_path = ""

        cmd_batch.append(
            (
                run_id,
                command_rel.as_posix(),
                plugin_path,
                pack,
                plugin,
                cmd_path.name,
                str(fm.get("name", "")),
                str(fm.get("description", "")),
                str(fm.get("shortcut", "")),
                str(fm.get("category", "")),
                str(fm.get("difficulty", "")),
                ",".join(sorted(fm.keys())),
                len(lines),
                wc,
            )
        )

    agent_batch: list[tuple] = []
    for agent_path in agent_files_list:
        try:
            text = agent_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm, body = parse_frontmatter(text)
        lines = text.splitlines()
        wc = word_count(text)

        agent_rel = Path(rel(agent_path))
        parts = agent_rel.parts
        try:
            plugins_idx = parts.index("plugins")
            pack = parts[plugins_idx + 1]
            if pack == "saas-packs" and len(parts) > plugins_idx + 2:
                pack = parts[plugins_idx + 2]
            agents_idx = next(i for i, p in enumerate(parts) if p == "agents")
            plugin = parts[agents_idx - 1]
            plugin_path = Path(*parts[:agents_idx]).as_posix()
        except (ValueError, StopIteration, IndexError):
            pack = "unknown"
            plugin = "unknown"
            plugin_path = ""

        caps_raw = fm.get("capabilities", [])
        caps_str = json.dumps(caps_raw) if isinstance(caps_raw, list) else str(caps_raw)

        agent_batch.append(
            (
                run_id,
                agent_rel.as_posix(),
                plugin_path,
                pack,
                plugin,
                agent_path.name,
                str(fm.get("name", "")),
                str(fm.get("description", "")),
                caps_str,
                str(fm.get("expertise_level", "")),
                str(fm.get("activation_priority", "")),
                str(fm.get("effort", "")),
                fm.get("maxTurns") or fm.get("max_turns"),
                json.dumps(fm.get("disallowedTools", fm.get("disallowed_tools", []))),
                ",".join(sorted(fm.keys())),
                len(lines),
                wc,
            )
        )

    if not dry_run:
        if cmd_batch:
            conn.executemany(
                """INSERT INTO command_files
                   (run_id, path, plugin_path, pack_name, plugin_name,
                    filename, fm_name, fm_description, fm_shortcut,
                    fm_category, fm_difficulty, fm_all_keys,
                    line_count, word_count)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                cmd_batch,
            )
        if agent_batch:
            conn.executemany(
                """INSERT INTO agent_files
                   (run_id, path, plugin_path, pack_name, plugin_name,
                    filename, fm_name, fm_description, fm_capabilities,
                    fm_expertise_level, fm_activation_priority,
                    fm_effort, fm_max_turns, fm_disallowed_tools,
                    fm_all_keys, line_count, word_count)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                agent_batch,
            )
        conn.commit()

    return len(cmd_batch), len(agent_batch)


# ---------------------------------------------------------------------------
# Scanner — Group 4: Documentation
# ---------------------------------------------------------------------------

DOC_SKIP_PATTERNS = frozenset({"node_modules", "dist", "__pycache__", ".git", "freshie", "marketplace/src"})


def infer_doc_type(path: Path) -> tuple[str, str, str]:
    """Return (doc_type, apparent_subject, subject_type)."""
    name_lower = path.name.lower()
    relative_path = Path(rel(path))
    parent = "repository" if relative_path.parent == Path(".") else relative_path.parent.name

    if name_lower == "readme.md":
        return "readme", parent, "plugin" if (path.parent.parent / ".claude-plugin").exists() else "directory"
    if name_lower == "changelog.md":
        return "changelog", parent, "plugin"
    if name_lower in ("claude.md", "agents.md"):
        return "guidance", name_lower.replace(".md", ""), "configuration"
    if name_lower == "skill.md":
        return "skill", path.parent.name, "skill"
    if "plan" in name_lower:
        return "plan", path.stem, "planning"
    if "tutorial" in name_lower:
        return "tutorial", path.stem, "tutorial"
    if "summary" in name_lower or "report" in name_lower:
        return "report", path.stem, "output"
    if "methodology" in name_lower or "design" in name_lower:
        return "methodology", path.stem, "reference"
    return "doc", path.stem, "general"


def scan_docs(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
) -> int:
    """Populate docs table with all .md files."""
    print("  Scanning docs...")
    batch: list[tuple] = []

    for md_path in REPO_ROOT.rglob("*.md"):
        if should_skip(md_path):
            continue
        # Skip marketplace/src
        rel_str = rel(md_path)
        if rel_str.startswith("marketplace/src"):
            continue
        try:
            text = md_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lc = len(text.splitlines())
        wc = word_count(text)
        doc_type, subject, subject_type = infer_doc_type(md_path)
        batch.append((run_id, rel_str, doc_type, subject, subject_type, lc, wc))

    if not dry_run and batch:
        conn.executemany(
            """INSERT INTO docs
               (run_id, path, doc_type, apparent_subject, subject_type, line_count, word_count)
               VALUES (?,?,?,?,?,?,?)""",
            batch,
        )
        conn.commit()

    print(f"  Docs: {len(batch)}")
    return len(batch)


# ---------------------------------------------------------------------------
# Scanner — Group 5: Scripts and CI
# ---------------------------------------------------------------------------

SCRIPT_EXTS = {".sh", ".py", ".mjs", ".js", ".ts"}


def infer_script_purpose(path: Path) -> tuple[str, str]:
    """Return (purpose, script_type)."""
    name = path.name.lower()
    if "validate" in name or "check" in name:
        return "validation", "utility"
    if "build" in name:
        return "build", "build"
    if "sync" in name:
        return "data-sync", "utility"
    if "test" in name:
        return "testing", "test"
    if "generate" in name or "discover" in name:
        return "code-generation", "generator"
    if "deploy" in name:
        return "deployment", "deployment"
    if "install" in name:
        return "installation", "utility"
    if "benchmark" in name or "perf" in name:
        return "benchmarking", "utility"
    if "audit" in name:
        return "audit", "utility"
    return "general", "script"


def detect_script_language(path: Path) -> str:
    ext = path.suffix.lower()
    mapping = {
        ".py": "python",
        ".sh": "bash",
        ".mjs": "javascript-esm",
        ".js": "javascript",
        ".ts": "typescript",
    }
    return mapping.get(ext, "unknown")


def scan_scripts_ci(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
) -> tuple[int, int]:
    """Populate scripts and ci_workflows tables."""
    script_paths: list[Path] = []

    # scripts/ directory
    scripts_dir = REPO_ROOT / "scripts"
    if scripts_dir.exists():
        for p in scripts_dir.rglob("*"):
            if p.is_file() and p.suffix in SCRIPT_EXTS and not should_skip(p):
                script_paths.append(p)

    # marketplace/scripts/
    mkt_scripts = REPO_ROOT / "marketplace" / "scripts"
    if mkt_scripts.exists():
        for p in mkt_scripts.rglob("*"):
            if p.is_file() and p.suffix in SCRIPT_EXTS and not should_skip(p):
                script_paths.append(p)

    # Root-level .sh and .py files
    for p in REPO_ROOT.iterdir():
        if p.is_file() and p.suffix in {".sh", ".py"}:
            script_paths.append(p)

    # packages/ — only top-level scripts
    packages_dir = REPO_ROOT / "packages"
    if packages_dir.exists():
        for pkg in packages_dir.iterdir():
            if pkg.is_dir():
                for p in pkg.iterdir():
                    if p.is_file() and p.suffix in SCRIPT_EXTS:
                        script_paths.append(p)

    script_batch: list[tuple] = []
    for sp in script_paths:
        purpose, script_type = infer_script_purpose(sp)
        lang = detect_script_language(sp)
        try:
            text = sp.read_text(encoding="utf-8", errors="replace")
            # Extract simple shebang deps
            first_line = text.splitlines()[0] if text.strip() else ""
            deps = ""
            if first_line.startswith("#!"):
                deps = first_line.split("/")[-1]
        except OSError:
            text = ""
            deps = ""
        script_batch.append(
            (
                run_id,
                rel(sp),
                lang,
                purpose,
                script_type,
                "",
                "",
                "",
                deps,
            )
        )

    # CI workflows
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    ci_batch: list[tuple] = []
    if workflows_dir.exists():
        for wf in sorted(workflows_dir.glob("*.yml")):
            try:
                text = wf.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            # Simple YAML extraction for workflow name, triggers, jobs
            name_m = re.search(r"^name\s*:\s*(.+)$", text, re.M)
            wf_name = name_m.group(1).strip().strip('"').strip("'") if name_m else wf.stem

            # Extract triggers (on: block)
            triggers_m = re.search(r"^on\s*:\s*\n((?:  .+\n)+)", text, re.M)
            triggers = triggers_m.group(0)[:200] if triggers_m else ""
            if not triggers:
                on_m = re.search(r"^on\s*:\s*\[(.+)\]", text, re.M)
                triggers = on_m.group(1) if on_m else ""

            # Extract job names
            jobs_m = re.findall(r"^  ([a-zA-Z0-9_\-]+)\s*:", text, re.M)
            jobs = json.dumps(jobs_m[:20])

            # Scripts referenced
            scripts_called = ",".join(
                set(re.findall(r"(?:node|python3?|bash|sh)\s+([\w./\-]+\.(?:mjs|js|py|sh))", text))
            )[:500]

            # Env vars
            env_vars = ",".join(set(re.findall(r"\$\{\{?\s*env\.([A-Z_]+)", text)))[:500]

            ci_batch.append(
                (
                    run_id,
                    wf.name,
                    wf_name,
                    triggers[:500],
                    jobs,
                    scripts_called,
                    env_vars,
                )
            )

    if not dry_run:
        if script_batch:
            conn.executemany(
                """INSERT INTO scripts
                   (run_id, path, language, purpose, script_type,
                    arguments, inputs, outputs, dependencies)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                script_batch,
            )
        if ci_batch:
            conn.executemany(
                """INSERT INTO ci_workflows
                   (run_id, filename, name, triggers, jobs_json,
                    scripts_called, env_vars)
                   VALUES (?,?,?,?,?,?,?)""",
                ci_batch,
            )
        conn.commit()

    print(f"  Scripts: {len(script_batch)}, CI workflows: {len(ci_batch)}")
    return len(script_batch), len(ci_batch)


# ---------------------------------------------------------------------------
# Scanner — Group 6: Structural analysis
# ---------------------------------------------------------------------------


def scan_duplicate_files(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
) -> int:
    """Hash all skill files and detect duplicates."""
    print("  Hashing skill files for duplicate detection...")
    hash_to_paths: dict[str, list[str]] = defaultdict(list)

    for skill_md in (REPO_ROOT / "plugins").rglob("SKILL.md"):
        if should_skip(skill_md):
            continue
        h = sha256_file(skill_md)
        hash_to_paths[h].append(rel(skill_md))

    dupes = {h: paths for h, paths in hash_to_paths.items() if len(paths) > 1}
    batch = [(run_id, h, len(paths), json.dumps(sorted(paths))) for h, paths in dupes.items()]

    if not dry_run and batch:
        conn.executemany(
            "INSERT INTO duplicate_files (run_id, sha256, file_count, file_paths_json) VALUES (?,?,?,?)",
            batch,
        )
        conn.commit()

    print(f"  Duplicate file groups: {len(batch)}")
    return len(batch)


def scan_anomalies(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
    pack_info: dict[str, dict],
) -> int:
    """Detect anomalies: zero-skill packs, plugins without skills dir, stray files."""
    print("  Detecting anomalies...")
    batch: list[tuple] = []

    # Zero-skill packs
    for pack_name, info in pack_info.items():
        if info["skill_count"] == 0:
            batch.append(
                (
                    run_id,
                    "zero-skill-pack",
                    info["path"],
                    0,
                    f"Pack '{pack_name}' has no skills",
                    "May be a template, docs-only, or transitional pack",
                )
            )

    # Plugins without skills dir.
    # Suppress when another structural signal explains the absence:
    # MCP plugin (.mcp.json), command-only (commands/), hook-only (hooks/),
    # or agent-only (agents/). Per issue #599: those are legitimately
    # skill-less by design, not anomalous. Filing them masks real anomalies.
    def _has_alternative_layout(plugin_dir: Path) -> bool:
        if (plugin_dir / ".mcp.json").exists():
            return True
        if (plugin_dir / "mcp" / ".mcp.json").exists():
            return True
        for d in ("commands", "hooks", "agents"):
            sub = plugin_dir / d
            if sub.is_dir() and any(sub.iterdir()):
                return True
        return False

    for pjson in (REPO_ROOT / "plugins").rglob(".claude-plugin/plugin.json"):
        if should_skip(pjson):
            continue
        plugin_dir = pjson.parent.parent
        if (plugin_dir / "skills").exists():
            continue
        if _has_alternative_layout(plugin_dir):
            continue
        batch.append(
            (
                run_id,
                "plugin-no-skills-dir",
                rel(plugin_dir),
                0,
                f"Plugin at {rel(plugin_dir)} has no skills/ directory and no alternative layout",
                "No commands/, hooks/, agents/, or .mcp.json detected — likely actually empty",
            )
        )

    # Stray .pyc files
    pyc_files = [p for p in REPO_ROOT.rglob("*.pyc") if not should_skip(p)]
    if pyc_files:
        batch.append(
            (
                run_id,
                "stray-pyc-files",
                str(REPO_ROOT),
                len(pyc_files),
                f"{len(pyc_files)} .pyc files found outside __pycache__",
                "Should be excluded by .gitignore",
            )
        )

    # SKILL.md files with no frontmatter
    no_fm = []
    for skill_md in (REPO_ROOT / "plugins").rglob("SKILL.md"):
        if should_skip(skill_md):
            continue
        try:
            text = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not text.startswith("---"):
            no_fm.append(rel(skill_md))
    if no_fm:
        batch.append(
            (
                run_id,
                "skill-no-frontmatter",
                json.dumps(no_fm[:20]),
                len(no_fm),
                f"{len(no_fm)} SKILL.md files lack frontmatter",
                "Required by spec",
            )
        )

    if not dry_run and batch:
        conn.executemany(
            """INSERT INTO anomalies
               (run_id, anomaly_type, path, count, evidence, notes)
               VALUES (?,?,?,?,?,?)""",
            batch,
        )
        conn.commit()

    print(f"  Anomalies: {len(batch)}")
    return len(batch)


def scan_cross_references(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
) -> int:
    """Detect cross-references: skills mentioned in CI, scripts called in workflows."""
    print("  Detecting cross-references...")
    batch: list[tuple] = []

    # CI workflows → scripts
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    if workflows_dir.exists():
        for wf in workflows_dir.glob("*.yml"):
            try:
                text = wf.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for script_match in re.finditer(r"([\w./\-]+\.(?:mjs|js|py|sh))", text):
                script_path = script_match.group(1)
                # Only include if it looks like a relative path
                if "/" in script_path:
                    batch.append(
                        (
                            run_id,
                            rel(wf),
                            script_path,
                            "workflow-calls-script",
                            "direct",
                            "high",
                            f"Referenced in {wf.name}",
                        )
                    )

    # Skill cross-references via markdown links
    for skill_md in (REPO_ROOT / "plugins").rglob("SKILL.md"):
        if should_skip(skill_md):
            continue
        try:
            text = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for link_match in re.finditer(r"\[([^\]]+)\]\(([^)]+\.md)\)", text):
            target = link_match.group(2)
            if not target.startswith("http"):
                batch.append(
                    (
                        run_id,
                        rel(skill_md),
                        target,
                        "skill-references-file",
                        "direct",
                        "high",
                        f"Markdown link to {target}",
                    )
                )

    if not dry_run and batch:
        conn.executemany(
            """INSERT INTO cross_references
               (run_id, source_path, target_path_or_entity, linkage_type,
                direct_or_inferred, confidence, evidence)
               VALUES (?,?,?,?,?,?,?)""",
            batch[:5000],  # cap to avoid enormous batches
        )
        conn.commit()

    print(f"  Cross-references: {min(len(batch), 5000)} (capped)")
    return len(batch)


# ---------------------------------------------------------------------------
# Scanner — Group 7: Root files
# ---------------------------------------------------------------------------

ROOT_PURPOSES: dict[str, str] = {
    ".gitignore": "version-control",
    ".gitattributes": "version-control",
    "pnpm-lock.yaml": "dependency-lock",
    "package.json": "package-manifest",
    "pnpm-workspace.yaml": "monorepo-config",
    "CLAUDE.md": "ai-guidance",
    "AGENTS.md": "ai-guidance",
    "README.md": "documentation",
    "LICENSE": "license",
    "sources.yaml": "external-sync-config",
}


def scan_root_files(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
) -> int:
    """Populate root_files with top-level repo files."""
    batch: list[tuple] = []
    for p in sorted(REPO_ROOT.iterdir()):
        if not p.is_file():
            continue
        purpose = ROOT_PURPOSES.get(
            p.name,
            "lock-file"
            if p.suffix in (".lock", ".yaml", ".yml") and p.stem not in ("sources",)
            else "root-config"
            if p.suffix in (".json", ".toml", ".yaml", ".yml")
            else "script"
            if p.suffix in (".py", ".sh")
            else "documentation"
            if p.suffix == ".md"
            else "other",
        )
        lc = count_lines(p)
        size = file_size(p)
        batch.append((run_id, rel(p), p.suffix or "(none)", lc, size, purpose))

    if not dry_run and batch:
        conn.executemany(
            "INSERT INTO root_files (run_id, path, extension, line_count, size_bytes, inferred_purpose) VALUES (?,?,?,?,?,?)",
            batch,
        )
        conn.commit()

    print(f"  Root files: {len(batch)}")
    return len(batch)


# ---------------------------------------------------------------------------
# Scanner — Group 8: Marketplace catalog
# ---------------------------------------------------------------------------


def scan_marketplace_catalog(
    run_id: int,
    conn: sqlite3.Connection,
    dry_run: bool,
) -> int:
    """Populate marketplace_catalog from marketplace.extended.json."""
    ext_json_path = REPO_ROOT / ".claude-plugin" / "marketplace.extended.json"
    if not ext_json_path.exists():
        print("  marketplace.extended.json not found — skipping catalog")
        return 0

    try:
        data = json.loads(ext_json_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ERROR reading marketplace.extended.json: {e}")
        return 0

    plugins_list = data.get("plugins", []) if isinstance(data, dict) else data
    batch: list[tuple] = []

    for entry in plugins_list:
        if not isinstance(entry, dict):
            continue
        author_raw = entry.get("author", {})
        author_str = json.dumps(author_raw) if isinstance(author_raw, dict) else str(author_raw)
        keywords_raw = entry.get("keywords", [])
        keywords_str = json.dumps(keywords_raw)
        components_raw = entry.get("components", {})
        verification_raw = entry.get("verification", {})
        pricing_raw = entry.get("pricing", {})
        zcf_raw = entry.get("zcf_metadata", {})
        ext_sync_raw = entry.get("external_sync", {})

        batch.append(
            (
                run_id,
                entry.get("name", ""),
                entry.get("source", ""),
                entry.get("description", ""),
                entry.get("version", ""),
                entry.get("category", ""),
                keywords_str,
                author_str,
                json.dumps(components_raw),
                json.dumps(verification_raw),
                int(bool(entry.get("featured", False))),
                json.dumps(entry.get("mcpTools", [])),
                entry.get("pluginCount")
                or (components_raw.get("skills", 0) if isinstance(components_raw, dict) else 0),
                json.dumps(pricing_raw),
                json.dumps(zcf_raw),
                json.dumps(ext_sync_raw),
                ",".join(sorted(entry.keys())),
                json.dumps(entry),
            )
        )

    if not dry_run and batch:
        conn.executemany(
            """INSERT INTO marketplace_catalog
               (run_id, name, source, description, version, category,
                keywords, author, components, verification,
                featured, mcp_tools, plugin_count, pricing,
                zcf_metadata, external_sync, all_keys, raw_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            batch,
        )
        conn.commit()

    print(f"  Marketplace catalog entries: {len(batch)}")
    return len(batch)


# ---------------------------------------------------------------------------
# Scanner — Misc tables: planned_skills, root_skills_files, validators,
#           plugin_templates, skill_database_vendors, field_registry
# ---------------------------------------------------------------------------


def scan_planned_skills(run_id: int, conn: sqlite3.Connection, dry_run: bool) -> int:
    """Scan planned-skills/ for skill definition files."""
    planned_dir = REPO_ROOT / "planned-skills"
    if not planned_dir.exists():
        return 0
    batch = []
    for p in planned_dir.rglob("*"):
        if p.is_file() and not should_skip(p):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            lc = len(text.splitlines())
            wc = word_count(text)
            # Infer skill name
            fm, _ = parse_frontmatter(text) if p.suffix == ".md" else ({}, text)
            apparent_name = fm.get("name", "") or p.stem
            batch.append((run_id, rel(p), p.name, p.suffix, lc, wc, file_size(p), apparent_name))
    if not dry_run and batch:
        conn.executemany(
            """INSERT INTO planned_skills
               (run_id, path, filename, extension, line_count, word_count, size_bytes, apparent_skill_name)
               VALUES (?,?,?,?,?,?,?,?)""",
            batch,
        )
        conn.commit()
    return len(batch)


def scan_root_skills_files(run_id: int, conn: sqlite3.Connection, dry_run: bool) -> int:
    """Scan skills/ at repo root."""
    root_skills = REPO_ROOT / "skills"
    if not root_skills.exists():
        return 0
    batch = []
    for p in root_skills.rglob("*"):
        if p.is_file() and not should_skip(p):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""
            lc = len(text.splitlines())
            wc = word_count(text)
            batch.append((run_id, rel(p), p.name, p.suffix, lc, wc, file_size(p), p.parent.name))
    if not dry_run and batch:
        conn.executemany(
            """INSERT INTO root_skills_files
               (run_id, path, filename, extension, line_count, word_count, size_bytes, parent_dir)
               VALUES (?,?,?,?,?,?,?,?)""",
            batch,
        )
        conn.commit()
    return len(batch)


def scan_validators(run_id: int, conn: sqlite3.Connection, dry_run: bool) -> int:
    """Scan for validator scripts and populate validators + validator_checks."""
    batch_v: list[tuple] = []
    batch_vc: list[tuple] = []

    validator_scripts = []
    for ext in (".py", ".mjs", ".js"):
        for p in REPO_ROOT.rglob(f"*validat*{ext}"):
            if not should_skip(p):
                validator_scripts.append(p)
        for p in REPO_ROOT.rglob(f"*check*{ext}"):
            if not should_skip(p):
                validator_scripts.append(p)

    for vp in validator_scripts:
        try:
            text = vp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        # Detect entity type
        entity_type = "unknown"
        for keyword in ("skill", "plugin", "agent", "command", "workflow"):
            if keyword in text.lower():
                entity_type = keyword
                break

        # Detect CLI flags
        flags = re.findall(r"--[\w-]+", text)
        flags_str = ",".join(sorted(set(flags))[:20])

        # Detect output format
        output_fmt = "json" if "json.dumps" in text or "JSON" in text else "text"

        # Detect fields read
        fields_read = ",".join(list(set(re.findall(r'["\']([a-z][a-z_\-]+)["\']', text)))[:20])

        batch_v.append(
            (
                run_id,
                rel(vp),
                entity_type,
                json.dumps([]),  # checks_json — would need deeper parsing
                fields_read,
                "warn-or-fail",
                flags_str,
                output_fmt,
            )
        )

        # Extract simple checks
        for check_m in re.finditer(r"#\s*(check|rule|validate)\s*:?\s*(.+)", text, re.I):
            batch_vc.append((run_id, rel(vp), "", check_m.group(2)[:200], "warn"))

    if not dry_run:
        if batch_v:
            conn.executemany(
                """INSERT INTO validators
                   (run_id, path, entity_type, checks_json, fields_read,
                    scoring_behavior, cli_flags, output_format)
                   VALUES (?,?,?,?,?,?,?,?)""",
                batch_v,
            )
        if batch_vc:
            conn.executemany(
                """INSERT INTO validator_checks
                   (run_id, validator_path, field_checked, rule_description, scoring_behavior)
                   VALUES (?,?,?,?,?)""",
                batch_vc,
            )
        conn.commit()

    return len(batch_v)


def scan_plugin_templates(run_id: int, conn: sqlite3.Connection, dry_run: bool) -> int:
    """Scan templates/ directory."""
    templates_dir = REPO_ROOT / "templates"
    if not templates_dir.exists():
        return 0
    batch = []
    for p in templates_dir.rglob("*"):
        if p.is_file() and not should_skip(p):
            # Detect template type
            template_type = "generic"
            stem_lower = p.stem.lower()
            if "skill" in stem_lower:
                template_type = "skill"
            elif "command" in stem_lower:
                template_type = "command"
            elif "agent" in stem_lower:
                template_type = "agent"
            elif "plugin" in stem_lower:
                template_type = "plugin"
            elif "mcp" in stem_lower:
                template_type = "mcp"

            batch.append(
                (
                    run_id,
                    rel(p),
                    p.name,
                    p.suffix,
                    count_lines(p),
                    file_size(p),
                    template_type,
                )
            )
    if not dry_run and batch:
        conn.executemany(
            """INSERT INTO plugin_templates
               (run_id, path, filename, extension, line_count, size_bytes, template_type)
               VALUES (?,?,?,?,?,?,?)""",
            batch,
        )
        conn.commit()
    return len(batch)


def scan_skill_database_vendors(run_id: int, conn: sqlite3.Connection, dry_run: bool) -> int:
    """Detect database vendor references inside skill files."""
    vendor_patterns: dict[str, re.Pattern] = {
        "postgresql": re.compile(r"postgresql|psycopg2|pg\b", re.I),
        "mysql": re.compile(r"mysql|mysqlclient|PyMySQL", re.I),
        "sqlite": re.compile(r"sqlite3|\.db\b", re.I),
        "mongodb": re.compile(r"mongodb|pymongo|MongoClient", re.I),
        "redis": re.compile(r"redis|RedisClient", re.I),
        "bigquery": re.compile(r"bigquery|google\.cloud\.bigquery", re.I),
        "firestore": re.compile(r"firestore|firebase_admin", re.I),
        "elasticsearch": re.compile(r"elasticsearch|Elasticsearch", re.I),
        "snowflake": re.compile(r"snowflake|snowflake-connector", re.I),
        "duckdb": re.compile(r"duckdb", re.I),
    }
    vendor_hits: dict[str, list[str]] = defaultdict(list)
    vendor_sizes: dict[str, int] = defaultdict(int)
    vendor_exts: dict[str, set[str]] = defaultdict(set)

    for skill_md in (REPO_ROOT / "plugins").rglob("SKILL.md"):
        if should_skip(skill_md):
            continue
        try:
            text = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for vendor, pat in vendor_patterns.items():
            if pat.search(text):
                vendor_hits[vendor].append(rel(skill_md))
                vendor_sizes[vendor] += file_size(skill_md)
                vendor_exts[vendor].add(".md")

    batch = [
        (
            run_id,
            vendor,
            json.dumps(paths[:10]),
            len(paths),
            vendor_sizes[vendor],
            ",".join(vendor_exts[vendor]),
            "",
        )
        for vendor, paths in vendor_hits.items()
    ]

    if not dry_run and batch:
        conn.executemany(
            """INSERT INTO skill_database_vendors
               (run_id, vendor_name, path, file_count, total_size_bytes,
                file_extensions, sample_fields)
               VALUES (?,?,?,?,?,?,?)""",
            batch,
        )
        conn.commit()

    return len(batch)


def scan_field_registry(run_id: int, conn: sqlite3.Connection, dry_run: bool) -> int:
    """Build a field registry from observed frontmatter fields across all SKILL.md files."""
    # Aggregate from frontmatter_values already written
    if dry_run:
        return 0

    rows = conn.execute(
        """SELECT field_name, COUNT(*) as cnt,
                  COUNT(DISTINCT raw_value) as uv,
                  MIN(raw_value) as sample
           FROM frontmatter_values
           WHERE run_id=?
           GROUP BY field_name""",
        (run_id,),
    ).fetchall()

    total = conn.execute(
        "SELECT COUNT(DISTINCT skill_path) FROM frontmatter_values WHERE run_id=?",
        (run_id,),
    ).fetchone()[0]

    batch = [
        (
            run_id,
            row["field_name"],
            "SKILL.md",
            "text",
            row["cnt"],
            total,
            "",
            str(row["sample"])[:100],
            "parse_frontmatter()",
            "",
        )
        for row in rows
    ]

    if batch:
        conn.executemany(
            """INSERT INTO field_registry
               (run_id, field_name, source, data_type, found_in_count,
                found_in_total, value_patterns, example, validated_by, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            batch,
        )
        conn.commit()

    return len(batch)


# ---------------------------------------------------------------------------
# Diff report
# ---------------------------------------------------------------------------


def print_diff_report(db_path: Path) -> None:
    """Compare run_id=1 vs run_id=2 across key tables."""
    conn = open_db(db_path)

    print()
    print("=" * 50)
    print("=== CHANGES SINCE RUN 1 ===")
    print("=" * 50)

    # Discovery runs summary
    runs = conn.execute("SELECT id, run_date, commit_hash FROM discovery_runs ORDER BY id").fetchall()
    for run in runs:
        print(f"  Run {run['id']}: {run['run_date']} @ {run['commit_hash']}")
    print()

    table_labels = {
        "packs": "Packs",
        "plugins": "Plugins",
        "skills": "Skills",
        "skill_files": "Skill files",
        "frontmatter_values": "Frontmatter values",
        "command_files": "Command files",
        "agent_files": "Agent files",
        "content_signals": "Content signal rows",
        "docs": "Doc files",
        "scripts": "Script files",
        "ci_workflows": "CI workflows",
        "marketplace_catalog": "Marketplace entries",
        "duplicate_files": "Duplicate file groups",
        "anomalies": "Anomalies",
        "cross_references": "Cross-references",
    }

    for table, label in table_labels.items():
        try:
            r1 = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE run_id=1").fetchone()[0]
            r2 = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE run_id=2").fetchone()[0]
            delta = r2 - r1
            sign = "+" if delta >= 0 else ""
            print(f"  {label:<28} {r1:>6} → {r2:>6}  ({sign}{delta})")
        except sqlite3.OperationalError:
            pass

    conn.close()
    print()


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def print_run_summary(conn: sqlite3.Connection, run_id: int) -> None:
    """Print per-table row counts for run_id."""
    print()
    print(f"{'=' * 50}")
    print(f"=== SUMMARY: run_id={run_id} ===")
    print(f"{'=' * 50}")

    for table in sorted(RUN_ID_TABLES):
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE run_id=?", (run_id,)).fetchone()[0]
            if count > 0:
                print(f"  {table:<40} {count:>6}")
        except sqlite3.OperationalError:
            pass
    print()


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def run_scan(args: argparse.Namespace) -> None:
    db_path = Path(args.db)
    dry_run: bool = args.dry_run

    # Check lineage before open_db enables WAL, schema creation, or a purge.
    # Derive the default from the selected runtime DB, not the source checkout.
    dolt_dir = args.dolt_dir or db_path.parent / "dolt" / "freshie"
    run_identity.preflight(
        db_path, dolt_dir, REPO_ROOT / "freshie" / "grade-histogram.json",
        rebuild=True, requested_run=args.run_id,
    )

    fresh_db = not db_path.exists()
    if fresh_db:
        # Bootstrap instead of exiting 1: inventory.sqlite is untracked, so any
        # fresh environment (CI runner, new checkout) starts without it — the
        # promote-curated.yml `rebuild_inventory: true` dispatch was structurally
        # impossible until this. bootstrap_schema is idempotent (IF NOT EXISTS).
        print(f"Database not found at {db_path} — bootstrapping a fresh schema.")
        db_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Database: {db_path}")
    print(f"Repo:     {REPO_ROOT}")
    print(f"Dry run:  {dry_run}")
    print()

    conn = open_db(db_path)

    # Step 0: Ensure the discovery schema exists (no-op on an established DB).
    bootstrap_schema(conn)

    # Step 1: Migrate schema — add run_id to all target tables
    print("[Step 1] Migrating schema (adding run_id columns)...")
    if not dry_run:
        migrate_add_run_id(conn)
    print("  Done.")

    # Step 1.5: Crash recovery — purge a crashed half-run (newest run with NULL
    # totals) so it is neither exported into append-only Dolt as a permanent
    # phantom nor left occupying MAX(id) for --populate-db to stamp onto.
    if not dry_run and not args.run_id:
        purge_incomplete_latest_run(conn)

    # Step 2: Determine run_id
    if args.run_id:
        run_id = args.run_id
    else:
        run_id = next_run_id(conn)
    print(f"\n[Step 2] Target run_id: {run_id}")

    # Step 3: Purge any existing rows for this run_id (idempotent)
    if not dry_run:
        existing = conn.execute("SELECT id FROM discovery_runs WHERE id=?", (run_id,)).fetchone()
        if existing:
            print(f"  Purging existing run_id={run_id} rows (idempotent re-run)...")
            purge_run(conn, run_id)
            print("  Purge complete.")

    # Step 4: Insert discovery_runs record
    commit_hash = git_commit_hash()
    run_date = datetime.now(timezone.utc).isoformat()
    print(f"\n[Step 3] Inserting discovery_runs record (commit={commit_hash})...")
    if not dry_run:
        conn.execute(
            "INSERT INTO discovery_runs (id, run_date, commit_hash) VALUES (?,?,?)",
            (run_id, run_date, commit_hash),
        )
        conn.commit()

    # Step 5: Scan packs / plugins / skills
    print("\n[Step 4] Scanning packs, plugins, skills...")
    total_packs, total_plugins, total_skills = scan_packs_plugins_skills(run_id, conn, dry_run)

    # Build pack info for anomaly detection
    pack_info: dict[str, dict] = {}
    if not dry_run:
        for row in conn.execute("SELECT name, path, skill_count FROM packs WHERE run_id=?", (run_id,)).fetchall():
            pack_info[row["name"]] = {
                "path": row["path"],
                "skill_count": row["skill_count"],
            }

    # Step 6: Collect SKILL.md paths (used by multiple scan groups)
    print("\n[Step 5] Parsing frontmatter...")
    skill_mds = _collect_skill_mds()
    scan_frontmatter(run_id, conn, dry_run, skill_mds)
    scan_plugin_frontmatter(run_id, conn, dry_run)

    # Step 7: Skill file analysis
    print("\n[Step 6] Analyzing skill files...")
    scan_skill_files(run_id, conn, dry_run, skill_mds)

    # Step 8: Commands and agents
    print("\n[Step 7] Scanning commands and agents...")
    cmd_count, agent_count = scan_commands_agents(run_id, conn, dry_run)

    # Step 9: Docs
    print("\n[Step 8] Scanning documentation...")
    scan_docs(run_id, conn, dry_run)

    # Step 10: Scripts and CI
    print("\n[Step 9] Scanning scripts and CI workflows...")
    scan_scripts_ci(run_id, conn, dry_run)

    # Step 11: Structural analysis
    print("\n[Step 10] Structural analysis...")
    scan_duplicate_files(run_id, conn, dry_run)
    scan_anomalies(run_id, conn, dry_run, pack_info)
    scan_cross_references(run_id, conn, dry_run)

    # Step 12: Root files
    print("\n[Step 11] Scanning root files...")
    total_root_files = scan_root_files(run_id, conn, dry_run)

    # Step 13: Marketplace catalog
    print("\n[Step 12] Scanning marketplace catalog...")
    scan_marketplace_catalog(run_id, conn, dry_run)

    # Step 14: Misc tables
    print("\n[Step 13] Scanning misc tables...")
    planned_count = scan_planned_skills(run_id, conn, dry_run)
    root_skills_count = scan_root_skills_files(run_id, conn, dry_run)
    val_count = scan_validators(run_id, conn, dry_run)
    tmpl_count = scan_plugin_templates(run_id, conn, dry_run)
    vendor_count = scan_skill_database_vendors(run_id, conn, dry_run)
    registry_count = scan_field_registry(run_id, conn, dry_run)
    print(
        f"  Planned skills: {planned_count}, Root skill files: {root_skills_count}, "
        f"Validators: {val_count}, Templates: {tmpl_count}, "
        f"Vendors: {vendor_count}, Registry fields: {registry_count}"
    )

    # Step 15: Update discovery_runs totals
    if not dry_run:
        total_files = conn.execute("SELECT COUNT(*) FROM skill_files WHERE run_id=?", (run_id,)).fetchone()[0]
        conn.execute(
            """UPDATE discovery_runs
               SET total_packs=?, total_plugins=?, total_skills=?,
                   total_files=?, total_root_files=?
               WHERE id=?""",
            (total_packs, total_plugins, total_skills, total_files, total_root_files, run_id),
        )
        conn.commit()
        print(f"\n  Updated discovery_runs totals for run_id={run_id}")

    # Print summary
    if not dry_run:
        print_run_summary(conn, run_id)

    conn.close()

    # Diff report
    if not dry_run:
        print_diff_report(db_path)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    global REPO_ROOT

    parser = argparse.ArgumentParser(
        description="Rebuild inventory DB with a new versioned discovery run.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--db",
        default=str(DB_DEFAULT),
        help="Path to the inventory SQLite database (default: freshie/inventory.sqlite)",
    )
    parser.add_argument(
        "--dolt-dir",
        type=Path,
        help="committed discovery authority (default: DB parent/dolt/freshie); required when stored elsewhere",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="repository root to inventory (default: this checkout)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and report without writing to DB",
    )
    parser.add_argument(
        "--run-id",
        type=int,
        default=None,
        help="Select an unpublished run_id; committed history cannot be replaced (default: next)",
    )
    parser.add_argument(
        "--diff-only",
        action="store_true",
        help="Print diff report between existing runs and exit",
    )
    args = parser.parse_args()
    REPO_ROOT = args.repo_root.resolve()

    if args.diff_only:
        print_diff_report(Path(args.db))
        return

    try:
        run_scan(args)
    except run_identity.IdentityError as exc:
        print(f"Freshie run identity refused: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
