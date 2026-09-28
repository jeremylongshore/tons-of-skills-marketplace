#!/usr/bin/env python3
"""
dolt-sync.py — one-way exporter: freshie/inventory.sqlite → Dolt → DoltHub.

Freshie's runtime format stays SQLite (zero consumer rewrites); the Dolt repo
at freshie/dolt/freshie/ is the versioned system of record, pushed to the
public DoltHub database <org>/freshie-inventory. This script is the ONLY
writer of the Dolt repo — never hand-edit it, never merge DoltHub PRs or
web-edit the public database (local is the sole writer).

Protocol per inventory cycle:
    python3 freshie/scripts/rebuild-inventory.py
    python3 scripts/validate-skills-schema.py --marketplace --populate-db freshie/inventory.sqlite
    python3 freshie/scripts/dolt-sync.py

What one sync does:
  1. Takes an flock (freshie/dolt/.sync.lock); refuses to start if a Dolt
     sql-server holds the repo open. Clears any dead prior run with
     `dolt reset --hard` + `dolt clean` (reset alone leaves never-committed
     tables behind).
  2. Snapshots the SQLite DB (VACUUM INTO a tmpfs copy) so every table export
     reads one consistent point in time. Gates table MEMBERSHIP against
     EXPORT_ALLOWLIST (also in --dry-run): any table not deliberately
     allowlisted is a hard failure — everything exported becomes permanent
     public DoltHub history, so an unknown table (e.g. j-rig runtime tables
     from pointing j-rig at the inventory DB) must never publish silently.
  3. Translates the schema (see translate rules below) and creates any table
     missing from the Dolt repo. Existing Dolt schemas are left alone — a
     schema-mismatch abort from `dolt table import -r` is a free parity gate;
     pass --recreate-tables to drop + recreate on legitimate schema change.
  4. Pumps every table: `sqlite3 -header -csv` → `dolt table import -r`.
     NULL vs '' needs no sentinel — the sqlite3 emitter writes NULL as an
     unquoted empty field and '' as a quoted "" pair, which is exactly the
     dialect Dolt's CSV reader distinguishes (verified against dolt 2.1.10;
     the (NULL,'') canary re-proves it on every run). If the canary ever
     fails, tables containing empty strings are routed through batched
     multi-row INSERTs instead (never `dolt sql -b`, a documented no-op).
     No --pk on import: it is silently ignored with -r; PKs live in the DDL.
  5. Gates before committing: per-table COUNT(*) parity (hard fail),
     float-tolerant aggregate checksums on every REAL column, and per-row
     MD5 byte checksums on the JSON-bearing TEXT columns.
  6. Writes the tracked compact export: freshie/grades.csv (one row per
     skill, deterministic sort) + freshie/grade-histogram.json. Their git
     diff is the "skill X went B→A" story — the append-only run_id model
     means `dolt diff run-7 run-8` shows added rows, not cell changes;
     history queries against Dolt are `WHERE run_id = N` / `AS OF 'run-N'`.
  7. Commits (`--skip-empty`), tags run-<N> (N = MAX(discovery_runs.id))
     only when the tag would sit on a commit that actually carries run N.
  8. Runs the fail-closed post-commit receipt step before any remote push:
     stamps the Dolt commit hash and exact grades.csv digest into
     grade-histogram.json (artifact → immutable-revision traceability) and
     emits freshie/reports/run-delta-<N>.json via run-delta.py
     (DOLT_DIFF_SUMMARY/DOLT_DIFF_STAT schema-vs-data classification per
     table + run-over-run grade regressions + immutable export/evidence
     snapshots), printing a one-line summary a GitHub-Actions step can
     consume. Receipt failure blocks publication; the local Dolt commit
     remains recoverable. Default inert beyond the report;
     --alert-on-regression makes an otherwise-successful sync exit 4 when
     grades regressed.
  9. Pushes main AND the tag (tags do not ride along on a branch push)
     — plus any older local tag a prior failed push stranded (reconciled
     against the DoltHub API's dolt_tags, best-effort). Push failure with
     valid creds exits non-zero and loud — a silently unpushed Dolt repo is
     single-copy history on an OOM-prone box.
 10. Runs `dolt gc` under the same flock every GC_EVERY_N_SYNCS syncs or
     when the repo directory doubles since the last gc (no auto-GC runs on
     the import path in this Dolt build).

Schema translation rules (SQLite → Dolt/MySQL dialect):
  - every identifier backtick-quoted
  - AUTOINCREMENT stripped entirely (ids always come from the data; kills
    the explicit-id-0 rewrite class in the INSERT fallback path)
  - INTEGER → BIGINT, REAL → DOUBLE, TIMESTAMP → DATETIME(6) (stored values
    are ISO-8601 with microseconds), TEXT → LONGTEXT
  - EXCEPT: a TEXT column that is part of the PRIMARY KEY → VARCHAR(255),
    guarded by a MAX(LENGTH(col)) <= 255 assert (npm package names are
    spec-capped at 214)
  - UNIQUE constraints keep their LONGTEXT columns (Dolt indexes TEXT
    natively — laxer than MySQL); non-unique indexes over TEXT columns get
    a (255) prefix
  - DEFAULT CURRENT_TIMESTAMP on a DATETIME(6) column becomes
    DEFAULT CURRENT_TIMESTAMP(6) (MySQL requires matching precision)
  - any BLOB column is a hard failure; ENUM is never emitted;
    sqlite_sequence is skipped

Restore path (DoltHub → local SQLite):
    dolt clone jeremylongshore/freshie-inventory && cd freshie-inventory
    dolt sql -r csv -q "SELECT * FROM skill_compliance" > skill_compliance.csv
    sqlite3 new.sqlite ".import --csv skill_compliance.csv skill_compliance"

Vocabulary: the DoltHub push is what makes the data durable and visible;
it is not "backup" (borg on the VPS is backup). Pushing requires DoltHub
creds from `dolt login` (a creds keypair on the operator box) — this script
implements NO env-var/CI credential path (no --user/DOLT_REMOTE_PASSWORD),
by design: local is the sole writer and CI never pushes. Any environment
that creates commits still needs a commit identity:
`dolt config --global --add user.name ...` / user.email.

Usage:
    python3 freshie/scripts/dolt-sync.py [--db PATH] [--no-push] [--dry-run]
        [--recreate-tables] [--gc] [--org ORG] [--repo NAME]

Exit codes: 0 ok · 1 gate/translation failure · 2 lock contention ·
            3 push failure (loud, actionable) ·
            4 sync succeeded but grade regressions were detected
              (only with --alert-on-regression).
"""

from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import io
import json
import math
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Derive the repo root from this file's location (freshie/scripts/dolt-sync.py)
# so the script works from any cwd, including git worktrees.
REPO_ROOT = Path(__file__).resolve().parents[2]
DB_DEFAULT = REPO_ROOT / "freshie" / "inventory.sqlite"
DOLT_PARENT = REPO_ROOT / "freshie" / "dolt"
DOLT_DB_NAME = "freshie"  # directory name == Dolt SQL database name
GRADES_CSV = REPO_ROOT / "freshie" / "grades.csv"
GRADE_HISTOGRAM = REPO_ROOT / "freshie" / "grade-histogram.json"

DEFAULT_ORG = os.environ.get("DOLTHUB_ORG", "jeremylongshore")
DEFAULT_REPO = "freshie-inventory"
CREDS_ENDPOINT = "doltremoteapi.dolthub.com:443"

SKIP_TABLES = frozenset({"sqlite_sequence"})

# ---------------------------------------------------------------------------
# PUBLIC-EXPORT ALLOWLIST — every table this sync publishes to the PUBLIC
# DoltHub database must be named here DELIBERATELY. This is a membership gate
# in the same spirit as the BLOB hard-fail: an unknown table in
# inventory.sqlite is a hard failure, never a silent publish. It exists
# because j-rig's runtime tables leaked into the public run-9.1 push (51 rows
# of LLM eval output) purely because nothing gated table membership.
#
# The set below is the intended CMDB system-of-record: the exact 51 tables of
# run-8, the first Dolt sync (verified via `SHOW TABLES AS OF 'run-8'`) —
# freshie/README.md § "Database design" describes the same 51-table model.
#
# Adding a table? Add it here in the same PR that introduces it, with a
# reviewer confirming it is fit for PERMANENT PUBLIC history (Dolt history is
# never rewritten). Tool-runtime tables (j-rig etc.) do NOT belong here —
# route those tools through a /dev/shm scratch DB (scripts/run-jrig-eval.sh).
EXPORT_ALLOWLIST = frozenset({
    "agent_compliance",
    "agent_files",
    "anomalies",
    "ci_workflows",
    "command_files",
    "content_signals",
    "cross_references",
    "discovery_runs",
    "docs",
    "duplicate_files",
    "field_registry",
    "forge_proofs",
    "frontmatter_fields",
    "frontmatter_shapes",
    "frontmatter_values",
    "marketplace_catalog",
    "npm_discovery_runs",
    "npm_dist_tags",
    "npm_download_stats",
    "npm_fetch_log",
    "npm_package_dependencies",
    "npm_packages",
    "npm_publish_history_summary",
    "npm_version_comparisons",
    "npm_versions",
    "pack_aggregates",
    "pack_metadata",
    "packs",
    "planned_skills",
    "plugin_companions",
    "plugin_compliance",
    "plugin_fields",
    "plugin_shapes",
    "plugin_templates",
    "plugin_values",
    "plugins",
    "repo_package_sources",
    "restructure_observations",
    "root_files",
    "root_skills_files",
    "scripts",
    "skill_compliance",
    "skill_database_vendors",
    "skill_files",
    "skill_structure_shapes",
    "skills",
    "unique_extensions",
    "unique_filenames",
    "unique_subdirs",
    "validator_checks",
    "validators",
})

# j-rig's own runtime schema (created by `j-rig eval --db <path>`). These are
# recognized specifically so the hard-fail message can say exactly how the
# contamination happened and how to clean it up.
JRIG_RUNTIME_TABLES = frozenset({
    "artifacts",
    "criterion_results",
    "run_summaries",
    "runs",
    "skill_human_reviews",
    "skill_usage_events",
    "skill_versions",
})

TYPE_MAP = {
    "INTEGER": "BIGINT",
    "REAL": "DOUBLE",
    "TIMESTAMP": "DATETIME(6)",
    "TEXT": "LONGTEXT",
}
VARCHAR_PK_MAX = 255
TEXT_INDEX_PREFIX = 255

# JSON-bearing TEXT columns that get per-row MD5 byte verification.
# PK column names are discovered from introspection at runtime.
JSON_CHECKSUM_COLUMNS = [
    ("marketplace_catalog", "raw_json"),
    ("ci_workflows", "jobs_json"),
    ("validators", "checks_json"),
]

GC_EVERY_N_SYNCS = 5
GC_SIZE_FACTOR = 2.0
INSERT_BATCH_SIZE = 500
FLOAT_REL_TOL = 1e-9

CANARY_TABLE = "_sync_canary"


class SyncError(Exception):
    """Fatal sync failure (translation, gate, or environment)."""


class PushError(Exception):
    """Push failed after local commit succeeded — history is single-copy."""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def log(msg: str) -> None:
    print(f"[dolt-sync] {msg}", flush=True)


def run(cmd: list[str], cwd: Path | None = None, check: bool = True,
        input_text: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, check=check,
        input=input_text, capture_output=True, text=True,
    )


def dolt(args: list[str], repo: Path, check: bool = True,
         input_text: str | None = None) -> subprocess.CompletedProcess:
    return run(["dolt", *args], cwd=repo, check=check, input_text=input_text)


def dolt_csv_query(repo: Path, sql: str) -> list[list[str]]:
    """Run a query in the Dolt repo, return parsed CSV rows (minus header).

    Parses the raw stdout stream (not splitlines) so quoted multi-line
    fields survive intact.
    """
    proc = dolt(["sql", "-r", "csv", "-q", sql], repo)
    rows = list(csv.reader(io.StringIO(proc.stdout)))
    return rows[1:] if rows else []


# ---------------------------------------------------------------------------
# Schema introspection + translation (pure — unit-tested)
# ---------------------------------------------------------------------------


def introspect_schema(conn: sqlite3.Connection) -> dict[str, dict]:
    """Read tables, columns, PKs, and indexes from a SQLite connection.

    Returns {table: {"columns": [(name, type, notnull, dflt, pk_ordinal)],
                     "indexes": [{"name", "unique", "origin", "cols"}]}}
    """
    tables = [
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        if r[0] not in SKIP_TABLES
    ]
    schema: dict[str, dict] = {}
    for t in tables:
        cols = [
            (r[1], r[2], bool(r[3]), r[4], r[5])
            for r in conn.execute(f'PRAGMA table_info("{t}")')
        ]
        indexes = []
        for idx_row in conn.execute(f'PRAGMA index_list("{t}")'):
            name, unique, origin = idx_row[1], bool(idx_row[2]), idx_row[3]
            icols = [r[2] for r in conn.execute(f'PRAGMA index_info("{name}")')]
            indexes.append(
                {"name": name, "unique": unique, "origin": origin, "cols": icols}
            )
        schema[t] = {"columns": cols, "indexes": indexes}
    return schema


def translate_column_type(table: str, col: str, sqlite_type: str, is_pk: bool) -> str:
    """Map one SQLite column type to the Dolt/MySQL dialect."""
    declared = (sqlite_type or "").strip().upper()
    if "BLOB" in declared:
        raise SyncError(f"{table}.{col}: BLOB columns are not supported — hard fail")
    if declared not in TYPE_MAP:
        raise SyncError(
            f"{table}.{col}: unmapped SQLite type {sqlite_type!r} — extend TYPE_MAP deliberately"
        )
    if declared == "TEXT" and is_pk:
        return f"VARCHAR({VARCHAR_PK_MAX})"
    return TYPE_MAP[declared]


def translate_default(dflt: str, mysql_type: str) -> str:
    """Carry a SQLite DEFAULT into MySQL dialect (precision-matched CURRENT_TIMESTAMP)."""
    if dflt.upper() == "CURRENT_TIMESTAMP" and mysql_type == "DATETIME(6)":
        return "CURRENT_TIMESTAMP(6)"
    return dflt


def scan_type_violations(conn: sqlite3.Connection,
                         schema: dict[str, dict]) -> dict[tuple[str, str], int]:
    """Find columns whose stored data violates their declared type.

    SQLite typing is advisory — a declared-INTEGER column can hold TEXT
    (e.g. YAML-comment cruft captured by the scanner). Dolt's typed columns
    reject such rows, and the system of record must hold what SQLite
    actually holds, so violating non-PK columns are widened to LONGTEXT.
    Returns {(table, column): violating_row_count}. A violation on a PK
    column is a hard failure (widening a key would change identity).
    """
    checks = {
        "INTEGER": "typeof(\"{c}\") NOT IN ('integer', 'null')",
        "REAL": "typeof(\"{c}\") NOT IN ('real', 'integer', 'null')",
        # Stored timestamps are ISO-8601 text; anything not shaped like a
        # datetime cannot enter DATETIME(6).
        "TIMESTAMP": (
            "\"{c}\" IS NOT NULL AND \"{c}\" NOT GLOB "
            "'[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][T ]"
            "[0-9][0-9]:[0-9][0-9]:[0-9][0-9]*'"
        ),
    }
    violations: dict[tuple[str, str], int] = {}
    for table, info in schema.items():
        for name, ctype, _notnull, _dflt, pk_ord in info["columns"]:
            declared = (ctype or "").strip().upper()
            if declared not in checks:
                continue
            predicate = checks[declared].format(c=name)
            count = conn.execute(
                f'SELECT COUNT(*) FROM "{table}" WHERE {predicate}'
            ).fetchone()[0]
            if count:
                if pk_ord > 0:
                    raise SyncError(
                        f"{table}.{name}: {count} rows violate the declared "
                        f"{declared} type on a PRIMARY KEY column — cannot widen a key"
                    )
                violations[(table, name)] = count
    return violations


def build_create_table(table: str, info: dict,
                       widen: frozenset[tuple[str, str]] = frozenset()) -> str:
    """Emit the translated CREATE TABLE statement for one table."""
    cols = info["columns"]
    pk_cols = [c[0] for c in sorted((c for c in cols if c[4] > 0), key=lambda c: c[4])]
    type_by_col: dict[str, str] = {}
    lines: list[str] = []
    for name, ctype, notnull, dflt, pk_ord in cols:
        if (table, name) in widen:
            mysql_type = "LONGTEXT"
        else:
            mysql_type = translate_column_type(table, name, ctype, pk_ord > 0)
        type_by_col[name] = mysql_type
        line = f"  `{name}` {mysql_type}"
        if notnull:
            line += " NOT NULL"
        # A widened column drops its DEFAULT: literal defaults are not valid
        # on TEXT-class columns in the MySQL dialect, and all values arrive
        # explicitly from the pump anyway.
        if dflt is not None and (table, name) not in widen:
            line += f" DEFAULT {translate_default(dflt, mysql_type)}"
        lines.append(line)
    if pk_cols:
        lines.append("  PRIMARY KEY (" + ", ".join(f"`{c}`" for c in pk_cols) + ")")
    uniq_n = 0
    for idx in info["indexes"]:
        if idx["origin"] == "pk":
            continue  # covered by the PRIMARY KEY clause
        col_list = ", ".join(f"`{c}`" for c in idx["cols"])
        if idx["unique"]:
            # sqlite autoindex names (sqlite_autoindex_t_N) are not portable;
            # emit a clean deterministic name. TEXT columns stay LONGTEXT —
            # Dolt indexes TEXT natively.
            uniq_n += 1
            name = (
                f"uniq_{table}_{uniq_n}"
                if idx["name"].startswith("sqlite_autoindex")
                else idx["name"]
            )
            lines.append(f"  UNIQUE KEY `{name}` ({col_list})")
        else:
            # Non-unique index: LONGTEXT columns need a prefix length.
            parts = [
                f"`{c}`({TEXT_INDEX_PREFIX})" if type_by_col.get(c) == "LONGTEXT" else f"`{c}`"
                for c in idx["cols"]
            ]
            lines.append(f"  KEY `{idx['name']}` ({', '.join(parts)})")
    return f"CREATE TABLE `{table}` (\n" + ",\n".join(lines) + "\n);"


def text_pk_guards(schema: dict[str, dict]) -> list[tuple[str, str]]:
    """(table, column) pairs that map TEXT → VARCHAR and need a length guard."""
    out = []
    for table, info in schema.items():
        for name, ctype, _notnull, _dflt, pk_ord in info["columns"]:
            if pk_ord > 0 and (ctype or "").strip().upper() == "TEXT":
                out.append((table, name))
    return out


def real_columns(schema: dict[str, dict]) -> dict[str, list[str]]:
    """{table: [REAL column names]} for export wrapping + checksum gates."""
    out: dict[str, list[str]] = {}
    for table, info in schema.items():
        cols = [c[0] for c in info["columns"] if (c[1] or "").strip().upper() == "REAL"]
        if cols:
            out[table] = cols
    return out


# ---------------------------------------------------------------------------
# INSERT fallback (pure SQL generation — unit-tested)
# ---------------------------------------------------------------------------


def sql_literal(value) -> str:
    """Render one Python value as a Dolt/MySQL SQL literal (NULL ≠ '')."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)  # repr round-trips doubles exactly
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace("'", "''")
        return f"'{escaped}'"
    raise SyncError(f"cannot render SQL literal for {type(value).__name__}")


def build_insert_batches(table: str, col_names: list[str], rows: list[tuple],
                         batch_size: int = INSERT_BATCH_SIZE) -> list[str]:
    """Batched multi-row INSERT statements (the canary-failure fallback pump).

    Never uses `dolt sql -b` — that flag is a documented no-op; statements
    are piped to plain `dolt sql` via stdin.
    """
    cols_sql = ", ".join(f"`{c}`" for c in col_names)
    statements = []
    for i in range(0, len(rows), batch_size):
        values = ",\n".join(
            "(" + ", ".join(sql_literal(v) for v in row) + ")"
            for row in rows[i : i + batch_size]
        )
        statements.append(f"INSERT INTO `{table}` ({cols_sql}) VALUES\n{values};")
    return statements


# ---------------------------------------------------------------------------
# Locking
# ---------------------------------------------------------------------------


def acquire_lock(lock_path: Path):
    """Non-blocking flock; returns the open fd (held for process lifetime)."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)  # lock file: owner-only
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        log(f"another sync holds {lock_path} — refusing to start")
        sys.exit(2)
    return fd


def refuse_if_server_running(repo: Path) -> None:
    server_lock = repo / ".dolt" / "sql-server.lock"
    if server_lock.exists():
        raise SyncError(
            f"a dolt sql-server holds {server_lock} — stop it before syncing "
            "(concurrent server + CLI writes corrupt the working set)"
        )
    # Dolt 2.x does not consistently materialize sql-server.lock. Its default
    # integration port is nevertheless the documented single-writer boundary:
    # a live server makes the repository read-only and a CLI exporter otherwise
    # gets partway through its import before failing. Refuse before any snapshot
    # or DDL work when the port is accepting connections.
    try:
        with socket.create_connection(("127.0.0.1", 3308), timeout=0.2):
            raise SyncError(
                "a dolt sql-server holds port 3308 — stop it before syncing "
                "(concurrent server + CLI writes corrupt the working set)"
            )
    except ConnectionRefusedError:
        return
    except TimeoutError:
        # A non-responsive listener cannot prove it is Dolt; preserve the
        # existing lock-file behavior rather than refusing on an unknown host.
        return


# ---------------------------------------------------------------------------
# Dolt repo lifecycle
# ---------------------------------------------------------------------------


def ensure_dolt_identity() -> None:
    for key in ("user.name", "user.email"):
        proc = run(["dolt", "config", "--global", "--get", key], check=False)
        if proc.returncode != 0 or not proc.stdout.strip():
            raise SyncError(
                f"dolt global config missing {key} — run: "
                f"dolt config --global --add {key} <value> "
                "(CI runners need this, or use dolt commit --author)"
            )


def ensure_repo(repo: Path) -> bool:
    """Init the Dolt repo if missing. Returns True if freshly initialized."""
    if (repo / ".dolt").is_dir():
        # Clear any dead prior run. reset --hard alone leaves never-committed
        # tables in the working set; dolt clean removes them.
        dolt(["reset", "--hard"], repo)
        dolt(["clean"], repo)
        return False
    repo.mkdir(parents=True, exist_ok=True)
    dolt(["init"], repo)
    log(f"initialized new Dolt repo at {repo}")
    return True


def head_commit(repo: Path) -> str:
    rows = dolt_csv_query(repo, "SELECT commit_hash FROM dolt_log LIMIT 1")
    return rows[0][0] if rows else ""


def dolt_tables(repo: Path) -> set[str]:
    rows = dolt_csv_query(repo, "SHOW TABLES")
    return {r[0] for r in rows}


# ---------------------------------------------------------------------------
# Canary — proves the NULL vs '' and DATETIME(6) round-trip on every run
# ---------------------------------------------------------------------------


def run_canary(repo: Path, tmpdir: Path) -> bool:
    """Round-trip a (NULL, '', quotes, datetime) fixture through the real
    CSV path. Returns True when the dialect contract holds."""
    fixture_db = tmpdir / "canary.sqlite"
    fixture_csv = tmpdir / "canary.csv"
    if fixture_db.exists():
        fixture_db.unlink()
    conn = sqlite3.connect(fixture_db)
    conn.execute("CREATE TABLE c (id INTEGER PRIMARY KEY, val TEXT, dt TEXT)")
    conn.executemany(
        "INSERT INTO c VALUES (?, ?, ?)",
        [
            (1, None, None),
            (2, "", None),
            (3, "plain", "2026-05-04T00:45:25.457182"),
            (4, 'quotes " and, commas\nand newlines', "2026-01-01T00:00:00"),
        ],
    )
    conn.commit()
    conn.close()

    with open(fixture_csv, "wb") as fh:
        subprocess.run(
            ["sqlite3", "-header", "-csv", str(fixture_db), "SELECT id, val, dt FROM c ORDER BY id;"],
            stdout=fh, check=True,
        )

    dolt(["sql", "-q", f"DROP TABLE IF EXISTS `{CANARY_TABLE}`"], repo)
    dolt(["sql", "-q",
          f"CREATE TABLE `{CANARY_TABLE}` (`id` BIGINT PRIMARY KEY, `val` LONGTEXT, `dt` DATETIME(6))"],
         repo)
    ok = True
    try:
        dolt(["table", "import", "-r", "--file-type", "csv", CANARY_TABLE, str(fixture_csv)], repo)
        rows = dolt_csv_query(
            repo,
            f"SELECT id, (val IS NULL) AS is_null, (val = '') AS is_empty, dt, val "
            f"FROM `{CANARY_TABLE}` ORDER BY id",
        )
        checks = {int(r[0]): r for r in rows}
        ok = (
            len(rows) == 4
            and checks[1][1] == "true"                         # NULL stayed NULL
            and checks[2][1] == "false" and checks[2][2] == "true"  # '' stayed ''
            and checks[3][3] == "2026-05-04 00:45:25.457182"   # microseconds survive
            and checks[4][4] == 'quotes " and, commas\nand newlines'  # quoting survives
        )
    except subprocess.CalledProcessError as exc:
        log(f"canary import failed: {exc.stderr}")
        ok = False
    finally:
        dolt(["sql", "-q", f"DROP TABLE IF EXISTS `{CANARY_TABLE}`"], repo)
    return ok


# ---------------------------------------------------------------------------
# Pump
# ---------------------------------------------------------------------------


def export_table_csv(db_path: Path, table: str, columns: list[str],
                     wrap_real: list[str], out_csv: Path) -> None:
    """Export one table via the sqlite3 CLI CSV emitter (the verified dialect).

    REAL columns are exported through printf('%.17g') so doubles round-trip
    bit-exactly (the CLI's default %!.15g can drop the last ulp); the CASE
    guard keeps NULLs as NULLs (sqlite printf would render NULL as 0).
    """
    select_parts = []
    for name in columns:
        if name in wrap_real:
            select_parts.append(
                f"CASE WHEN \"{name}\" IS NULL THEN NULL "
                f"ELSE printf('%.17g', \"{name}\") END AS \"{name}\""
            )
        else:
            select_parts.append(f'"{name}"')
    sql = f'SELECT {", ".join(select_parts)} FROM "{table}";'
    with open(out_csv, "wb") as fh:
        subprocess.run(["sqlite3", "-header", "-csv", str(db_path), sql], stdout=fh, check=True)


def table_has_empty_strings(conn: sqlite3.Connection, table: str,
                            text_cols: list[str]) -> bool:
    for col in text_cols:
        row = conn.execute(
            f'SELECT 1 FROM "{table}" WHERE "{col}" = \'\' LIMIT 1'
        ).fetchone()
        if row:
            return True
    return False


def pump_table_inserts(conn: sqlite3.Connection, repo: Path, table: str,
                       columns: list[str]) -> None:
    """Deterministic fallback pump: DELETE + batched INSERTs via stdin."""
    col_list = ", ".join('"{}"'.format(c) for c in columns)
    rows = conn.execute(f'SELECT {col_list} FROM "{table}"').fetchall()
    statements = [f"DELETE FROM `{table}`;"]
    statements.extend(build_insert_batches(table, columns, rows))
    dolt(["sql"], repo, input_text="\n".join(statements))


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def gate_export_allowlist(tables) -> None:
    """Hard-fail if the source DB carries any table not on EXPORT_ALLOWLIST.

    Everything this sync exports becomes PERMANENT PUBLIC DoltHub history, so
    table membership is a gate, not a discovery. Pure function over the table
    names — unit-tested.
    """
    unexpected = sorted(set(tables) - EXPORT_ALLOWLIST)
    if not unexpected:
        log(f"gate: export allowlist OK ({len(set(tables))} tables, all allowlisted)")
        return
    jrig = [t for t in unexpected if t in JRIG_RUNTIME_TABLES]
    other = [t for t in unexpected if t not in JRIG_RUNTIME_TABLES]
    parts = [
        f"{len(unexpected)} table(s) in the source DB are NOT on the public-export "
        f"allowlist — refusing to publish them to public DoltHub history "
        f"(which is never rewritten)."
    ]
    if jrig:
        parts.append(
            f"j-rig runtime tables: {jrig}. These mean j-rig was pointed at the "
            f"inventory DB directly. Route evals through scripts/run-jrig-eval.sh "
            f"(j-rig writes to a /dev/shm scratch DB; only the forge_proofs verdict "
            f"row reaches the inventory), then drop the stray tables: "
            + " ".join(
                f"sqlite3 <db> 'DROP TABLE \"{t}\";'" for t in jrig
            )
        )
    if other:
        parts.append(
            f"unrecognized tables: {other}. Either add each to EXPORT_ALLOWLIST "
            f"deliberately (reviewer confirms it is fit for permanent public "
            f"history) or drop it from the source DB."
        )
    raise SyncError(" ".join(parts))


def demote_unretained_forge_proofs(conn: sqlite3.Connection) -> list[tuple[int, str]]:
    """Downgrade ledger claims whose primary artifact is absent or hash-invalid.

    This runs against the writable local ledger before the exporter snapshots it.
    An E2/E3 claim without retrievable primary bytes is E0 by definition; keeping
    it at a stronger class until a later run would republish a false claim.
    """
    tables = {
        row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    if "forge_proofs" not in tables:
        return []
    columns = {row[1] for row in conn.execute("PRAGMA table_info(forge_proofs)")}
    required = {"id", "evidence_class", "artifact_uri", "artifact_sha256"}
    missing = sorted(required - columns)
    if missing:
        raise SyncError(
            "forge_proofs evidence schema is too old for safe export; run the "
            f"validator migration first (missing: {', '.join(missing)})"
        )

    demoted: list[tuple[int, str]] = []
    rows = conn.execute(
        "SELECT id, evidence_class, artifact_uri, artifact_sha256 FROM forge_proofs"
    ).fetchall()
    for row_id, evidence_class, uri, expected_hash in rows:
        reason = None
        if not isinstance(uri, str) or not uri:
            reason = "E0-PRIMARY-ARTIFACT-UNRETAINED"
        elif not isinstance(expected_hash, str):
            reason = "E0-PRIMARY-ARTIFACT-HASH-MISSING"
        elif len(expected_hash) != 64 or any(ch not in "0123456789abcdef" for ch in expected_hash.lower()):
            reason = "E0-PRIMARY-ARTIFACT-HASH-MISSING"
        else:
            try:
                artifact = Path(uri)
                actual_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
                if actual_hash != expected_hash.lower():
                    reason = "E0-PRIMARY-ARTIFACT-HASH-MISMATCH"
            except OSError:
                reason = "E0-PRIMARY-ARTIFACT-UNRETAINED"
        if reason and evidence_class != "E0":
            conn.execute("UPDATE forge_proofs SET evidence_class = 'E0' WHERE id = ?", (row_id,))
            demoted.append((int(row_id), reason))
    return demoted


def gate_row_counts(conn: sqlite3.Connection, repo: Path, tables: list[str]) -> None:
    for t in tables:
        want = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        got_rows = dolt_csv_query(repo, f"SELECT COUNT(*) FROM `{t}`")
        got = int(got_rows[0][0])
        if want != got:
            raise SyncError(f"row-count parity failed on {t}: sqlite={want} dolt={got}")
    log(f"gate: row-count parity OK across {len(tables)} tables")


def gate_real_checksums(conn: sqlite3.Connection, repo: Path,
                        reals: dict[str, list[str]]) -> None:
    for table, cols in reals.items():
        for col in cols:
            w_cnt, w_sum = conn.execute(
                f'SELECT COUNT("{col}"), COALESCE(SUM("{col}"), 0.0) FROM "{table}"'
            ).fetchone()
            rows = dolt_csv_query(
                repo,
                f"SELECT COUNT(`{col}`), COALESCE(SUM(`{col}`), 0.0) FROM `{table}`",
            )
            g_cnt, g_sum = int(rows[0][0]), float(rows[0][1])
            if w_cnt != g_cnt or not math.isclose(
                float(w_sum), g_sum, rel_tol=FLOAT_REL_TOL, abs_tol=FLOAT_REL_TOL
            ):
                raise SyncError(
                    f"REAL checksum failed on {table}.{col}: "
                    f"sqlite=({w_cnt},{w_sum}) dolt=({g_cnt},{g_sum})"
                )
    n = sum(len(v) for v in reals.values())
    log(f"gate: float-tolerant checksums OK on {n} REAL columns")


def gate_json_checksums(conn: sqlite3.Connection, repo: Path,
                        schema: dict[str, dict]) -> None:
    checked: list[str] = []
    skipped: list[str] = []
    for table, col in JSON_CHECKSUM_COLUMNS:
        if table not in schema:
            skipped.append(f"{table}.{col}")
            continue
        pk_cols = [
            c[0] for c in sorted(
                (c for c in schema[table]["columns"] if c[4] > 0), key=lambda c: c[4]
            )
        ]
        if len(pk_cols) != 1:
            raise SyncError(f"JSON checksum gate needs a single-column PK on {table}")
        pk = pk_cols[0]
        want: dict[str, str] = {}
        for key, val in conn.execute(f'SELECT "{pk}", "{col}" FROM "{table}"'):
            want[str(key)] = (
                "" if val is None else hashlib.md5(val.encode("utf-8")).hexdigest()
            )
        got: dict[str, str] = {}
        for row in dolt_csv_query(repo, f"SELECT `{pk}`, MD5(`{col}`) FROM `{table}`"):
            got[row[0]] = row[1]
        if want != got:
            diff = {k for k in set(want) | set(got) if want.get(k) != got.get(k)}
            sample = sorted(diff)[:5]
            raise SyncError(
                f"JSON byte checksum failed on {table}.{col}: "
                f"{len(diff)} mismatched rows (sample PKs: {sample})"
            )
        checked.append(f"{table}.{col}")
    # Only claim OK for columns actually verified — a listed table missing
    # from this database means byte verification did NOT run for it, and the
    # log line is evidence an operator relies on.
    for miss in skipped:
        log(f"WARNING: JSON checksum column {miss} not present in this "
            f"database — SKIPPED (no byte verification ran for it; update "
            f"JSON_CHECKSUM_COLUMNS if the table was renamed)")
    log(f"gate: per-row MD5 byte checksums OK on {len(checked)} JSON "
        f"columns ({', '.join(checked) if checked else 'none checked'})")


def gate_run_completeness(conn: sqlite3.Connection, run_id: int) -> None:
    """Refuse to export a phantom half-run into the append-only Dolt history.

    rebuild-inventory writes the discovery_runs totals only as the LAST step of
    a successful scan, so NULL totals on the newest run mean a crashed scan
    left partial rows across the run-tagged tables. Exporting would freeze the
    phantom into public Dolt history forever (2026-07-14 ops review); the
    rebuild script now purges the phantom on its next default rerun.
    """
    if not run_id:
        return  # empty DB — nothing to judge (main already tags run-0 honestly)
    try:
        row = conn.execute(
            "SELECT total_skills FROM discovery_runs WHERE id=?", (run_id,)
        ).fetchone()
    except sqlite3.OperationalError:
        return  # legacy schema without totals columns — cannot judge, do not block
    if row is not None and row[0] is None:
        raise SyncError(
            f"discovery run {run_id} is incomplete (totals were never written — "
            f"a crashed scan left a phantom half-run). Re-run "
            f"freshie/scripts/rebuild-inventory.py (it purges the newest phantom "
            f"and rescans) before syncing to Dolt."
        )
    if row is None:
        raise SyncError(f"discovery run {run_id} is missing from discovery_runs")
    try:
        actual_skills = conn.execute(
            "SELECT COUNT(*) FROM skills WHERE run_id=?", (run_id,)
        ).fetchone()[0]
    except sqlite3.OperationalError as exc:
        raise SyncError(
            "cannot verify discovery run coherence: skills.run_id is required "
            "to compare discovery_runs.total_skills"
        ) from exc
    declared_skills = row[0]
    if declared_skills != actual_skills:
        raise SyncError(
            f"discovery run {run_id} skill-count mismatch: header total_skills="
            f"{declared_skills}, skills rows={actual_skills}. Re-run "
            "freshie/scripts/rebuild-inventory.py before syncing to Dolt."
        )


def gate_varchar_lengths(conn: sqlite3.Connection, guards: list[tuple[str, str]]) -> None:
    for table, col in guards:
        max_len = conn.execute(
            f'SELECT COALESCE(MAX(LENGTH("{col}")), 0) FROM "{table}"'
        ).fetchone()[0]
        if max_len > VARCHAR_PK_MAX:
            raise SyncError(
                f"{table}.{col}: MAX(LENGTH) = {max_len} exceeds VARCHAR({VARCHAR_PK_MAX})"
            )
    log(f"gate: VARCHAR length guard OK on {len(guards)} TEXT primary keys")


# ---------------------------------------------------------------------------
# Tracked compact export — the diffable "skill X went B→A" story
# ---------------------------------------------------------------------------


def normalize_grade_export_path(skill_path: str, repo_root: Path = REPO_ROOT) -> str:
    """Return the portable repository-relative form required by grades.csv."""
    candidate = Path(skill_path)
    if candidate.is_absolute():
        try:
            candidate = candidate.relative_to(repo_root.resolve())
        except ValueError as exc:
            raise SyncError(
                f"skill_compliance path escapes repository and cannot be exported: {skill_path}"
            ) from exc
    normalized = candidate.as_posix()
    if not normalized or normalized == "." or normalized.startswith("../"):
        raise SyncError(f"invalid skill_compliance export path: {skill_path}")
    return normalized


def write_grades_export(conn: sqlite3.Connection, run_id: int,
                        csv_path: Path = GRADES_CSV,
                        histogram_path: Path = GRADE_HISTOGRAM,
                        repo_root: Path = REPO_ROOT) -> None:
    # No run_id column in the CSV rows on purpose: it would change on every
    # row every sync, drowning the grade-movement diff this file exists to
    # tell. The current run_id lives in grade-histogram.json.
    #
    # Scoped to the CURRENT run only. The old latest-per-skill_path-across-
    # all-runs query kept skills deleted from the repo alive forever as ghost
    # rows (102 of them by run 9 — e.g. hyperflow's skills/amplify, gone from
    # disk since run 7, still counted in the public histogram). grades.csv
    # claims to be "current corpus grades"; only the current run's rows are.
    db_rows = conn.execute(
        """
        SELECT skill_path, grade, score
        FROM skill_compliance
        WHERE run_id = ?
        ORDER BY skill_path
        """,
        (run_id,),
    ).fetchall()
    if not db_rows:
        total = conn.execute("SELECT COUNT(*) FROM skill_compliance").fetchone()[0]
        if total:
            raise SyncError(
                f"skill_compliance has no rows for run {run_id} but {total} rows "
                f"overall — refusing to overwrite {csv_path.name} with an empty "
                f"export. Run the validator --populate-db step for run {run_id} "
                f"before syncing."
            )
    rows = [
        (normalize_grade_export_path(skill_path, repo_root), grade, score)
        for skill_path, grade, score in db_rows
    ]
    if len({skill_path for skill_path, _, _ in rows}) != len(rows):
        raise SyncError(
            f"skill_compliance has duplicate repository-relative paths for run {run_id}; "
            "refusing ambiguous grade export"
        )
    rows.sort(key=lambda row: row[0])
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    histogram_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["skill_path", "grade", "score"])
        writer.writerows(rows)

    histogram: dict[str, int] = {}
    for _, grade, _ in rows:
        key = grade if grade else "ungraded"
        histogram[key] = histogram.get(key, 0) + 1
    payload = {
        "run_id": run_id,
        "total": len(rows),
        "grades": {k: histogram[k] for k in sorted(histogram)},
    }
    histogram_path.write_text(json.dumps(payload, indent=2) + "\n")
    log(f"wrote {csv_path.name} ({len(rows)} skills) + {histogram_path.name}")


def gate_tracked_grade_exports(conn: sqlite3.Connection, csv_path: Path,
                               histogram_path: Path,
                               repo_root: Path = REPO_ROOT) -> None:
    """Refuse a grade-export pair that does not describe the latest run.

    ``grades.csv`` deliberately omits a per-row run id so its git diff exposes
    grade movement.  ``grade-histogram.json`` is consequently the provenance
    stamp for the pair.  Keep that convenience from becoming a stale-public-
    artifact hazard by checking both the stamp and the CSV cardinality against
    the source inventory before a sync can call the export current.
    """
    row = conn.execute("SELECT MAX(id) FROM discovery_runs").fetchone()
    latest_run_id = int(row[0] or 0)
    if not latest_run_id:
        raise SyncError("cannot verify tracked grade exports: discovery_runs has no run")

    try:
        payload = json.loads(histogram_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(
            f"cannot read tracked grade histogram {histogram_path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SyncError(f"tracked grade histogram {histogram_path} must be a JSON object")

    histogram_run_id = payload.get("run_id")
    if isinstance(histogram_run_id, bool) or not isinstance(histogram_run_id, int):
        raise SyncError(
            f"tracked grade histogram {histogram_path} has invalid run_id "
            f"{histogram_run_id!r}"
        )
    if histogram_run_id != latest_run_id:
        raise SyncError(
            "tracked grade exports are stale: "
            f"grade-histogram.json.run_id={histogram_run_id} but "
            f"MAX(discovery_runs.id)={latest_run_id}"
        )

    source_rows = conn.execute(
        "SELECT skill_path, grade, score FROM skill_compliance WHERE run_id = ?",
        (latest_run_id,),
    ).fetchall()
    expected_rows = sorted(
        (normalize_grade_export_path(path, repo_root), grade, score)
        for path, grade, score in source_rows
    )
    if len({row[0] for row in expected_rows}) != len(expected_rows):
        raise SyncError("cannot verify tracked grade exports: source paths are not unique")
    expected_csv = io.StringIO(newline="")
    writer = csv.writer(expected_csv, lineterminator="\n")
    writer.writerow(["skill_path", "grade", "score"])
    writer.writerows(expected_rows)
    try:
        actual_csv = csv_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SyncError(f"cannot read tracked grades CSV {csv_path}: {exc}") from exc
    if actual_csv != expected_csv.getvalue():
        raise SyncError(
            "tracked grades CSV content does not match the latest skill_compliance run"
        )
    row_count = len(expected_rows)

    histogram_total = payload.get("total")
    if isinstance(histogram_total, bool) or not isinstance(histogram_total, int):
        raise SyncError(
            f"tracked grade histogram {histogram_path} has invalid total {histogram_total!r}"
        )
    if row_count != histogram_total:
        raise SyncError(
            "tracked grade export row-count mismatch: "
            f"grades.csv has {row_count} data rows but "
            f"grade-histogram.json.total={histogram_total}"
        )
    expected_grades: dict[str, int] = {}
    for _, grade, _ in expected_rows:
        key = grade if grade else "ungraded"
        expected_grades[key] = expected_grades.get(key, 0) + 1
    if payload.get("grades") != {
        key: expected_grades[key] for key in sorted(expected_grades)
    }:
        raise SyncError(
            "tracked grade histogram buckets do not match the latest skill_compliance run"
        )
    log(
        "gate: tracked grade exports current "
        f"(run_id={latest_run_id}, rows={row_count})"
    )


# ---------------------------------------------------------------------------
# Commit / tag / push
# ---------------------------------------------------------------------------


def commit_and_tag(repo: Path, run_id: int, source_sha: str) -> tuple[bool, str | None, str]:
    """Commit the working set and tag run-<N>.

    Returns (committed, tag_name, head_hash) — head_hash is HEAD after the
    commit attempt. Whenever tag_name is non-None, head_hash is exactly the
    commit run N's data sits on (fresh commit or crash-retry); when
    tag_name is None (nothing changed AND HEAD is not run N), it is only
    "HEAD at sync time" — consumers must not stamp it as run N's revision.
    """
    before = head_commit(repo)
    dolt(["add", "-A"], repo)
    msg = f"freshie sync: run {run_id} from inventory.sqlite ({source_sha})"
    dolt(["commit", "--skip-empty", "-m", msg], repo)
    after = head_commit(repo)
    committed = after != before

    tag_base = f"run-{run_id}"
    existing = {
        r[0]: r[1] for r in dolt_csv_query(repo, "SELECT tag_name, tag_hash FROM dolt_tags")
    }

    if tag_base in existing and existing[tag_base] == after:
        # Retry after a crash between tag and push — the tag already tells the truth.
        return committed, tag_base, after

    if committed:
        tag = tag_base
        suffix = 0
        while tag in existing:
            # run N was already tagged on an older commit (e.g. compliance
            # re-populated without a new discovery run) — keep history honest
            # with a suffixed tag instead of failing the sync.
            suffix += 1
            tag = f"{tag_base}.{suffix}"
        if suffix:
            log(f"WARNING: tag {tag_base} already exists on an older commit — "
                f"tagging {tag} instead. This usually means one of: (a) a prior "
                f"sync committed+tagged but its PUSH FAILED and was never "
                f"retried — verify {tag_base} actually reached DoltHub "
                f"(SELECT tag_name FROM dolt_tags via the DoltHub API) before "
                f"trusting the public record; or (b) compliance was "
                f"re-populated without a new discovery run. Do not treat this "
                f"suffix as routine.")
        dolt(["tag", tag, "-m", msg], repo)
        return committed, tag, after

    # Nothing changed this run. Only tag HEAD if it demonstrably carries run N
    # (crash-between-commit-and-tag retry); otherwise a tag would lie.
    if tag_base not in existing:
        head_msg_rows = dolt_csv_query(repo, "SELECT message FROM dolt_log LIMIT 1")
        head_msg = head_msg_rows[0][0] if head_msg_rows else ""
        if f"run {run_id} " in head_msg or head_msg.endswith(f"run {run_id}"):
            dolt(["tag", tag_base, "-m", msg], repo)
            return committed, tag_base, after
        log(f"no data changes and HEAD is not run {run_id} — skipping tag")
        return committed, None, after
    return committed, tag_base, after


# ---------------------------------------------------------------------------
# Post-commit structured output (FAIL-CLOSED before remote publication)
# ---------------------------------------------------------------------------


def stamp_dolt_commit(histogram_path: Path, commit_hash: str,
                      grades_csv_path: Path = GRADES_CSV) -> None:
    """Add the Dolt commit hash to the already-written grade histogram.

    Stamped AFTER commit_and_tag because the hash does not exist when
    write_grades_export runs; the histogram is a git-tracked export, not
    part of the Dolt working set, so rewriting it post-commit changes
    nothing about the Dolt history it points at.
    """
    payload = json.loads(histogram_path.read_text())
    payload["dolt_commit"] = commit_hash
    payload["grades_csv_sha256"] = hashlib.sha256(grades_csv_path.read_bytes()).hexdigest()
    histogram_path.write_text(json.dumps(payload, indent=2) + "\n")


def load_run_delta():
    """Import the sibling run-delta.py (hyphenated name → importlib)."""
    import importlib.util
    path = Path(__file__).resolve().parent / "run-delta.py"
    spec = importlib.util.spec_from_file_location("run_delta", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def post_commit_outputs(repo: Path, run_id: int, tag: str | None,
                        head_hash: str, grades_csv_path: Path = GRADES_CSV,
                        histogram_path: Path = GRADE_HISTOGRAM,
                        reports_dir: Path | None = None) -> bool:
    """Stamp the histogram + emit the run-delta report. Returns True when
    grade regressions were found (the --alert-on-regression signal).

    The outputs are part of the publication contract. A failure raises
    SyncError before any remote push; the local commit remains recoverable.
    """
    regressions_found = False
    if tag is None:
        # No tag means HEAD demonstrably does NOT carry run N (the
        # nothing-changed-and-HEAD-is-older path) — stamping that hash into
        # a histogram labeled run N would lie about provenance, so skip
        # both outputs. On the commit and crash-retry paths tag is set and
        # head_hash is exactly the commit the run's data sits on.
        log("post-commit: no run tag this sync — skipping dolt_commit stamp "
            "and run-delta report")
        return regressions_found
    try:
        stamp_dolt_commit(histogram_path, head_hash, grades_csv_path)
        log(f"stamped dolt_commit {head_hash} into {histogram_path.name}")
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(
            f"post-commit grade-export receipt failed before push: {exc}"
        ) from exc
    try:
        run_delta = load_run_delta()
        kwargs = {"reports_dir": reports_dir} if reports_dir is not None else {}
        out_path, report = run_delta.emit(repo, run_id, head_hash, tag, **kwargs)
        log(run_delta.summary_line(report, out_path))
        regressions_found = bool(report["grade_regressions"])
    except Exception as exc:  # noqa: BLE001 — normalize sibling-module errors
        raise SyncError(
            f"post-commit run receipt failed before push: {exc}; regenerate with "
            f"python3 freshie/scripts/run-delta.py --run-id {run_id}"
        ) from exc
    return regressions_found


def ensure_remote(repo: Path, org: str, repo_name: str) -> None:
    proc = dolt(["remote", "-v"], repo)
    target = f"{org}/{repo_name}"
    for line in proc.stdout.splitlines():
        parts = line.split()
        if parts and parts[0] == "origin":
            if target not in line:
                raise SyncError(
                    f"remote 'origin' points elsewhere ({line.strip()}); expected {target}"
                )
            return
    dolt(["remote", "add", "origin", target], repo)
    log(f"added remote origin → {target}")


def check_creds() -> None:
    proc = run(["dolt", "creds", "check", "--endpoint", CREDS_ENDPOINT], check=False)
    if "Success" not in proc.stdout:
        raise PushError(
            "dolt creds check failed — no valid DoltHub key on this machine. "
            "Run `dolt login` (inspect with `dolt creds ls`). Pushing is "
            "operator-box-only: this script has no env-var/CI credential path, "
            "by design — local is the sole writer and CI never pushes.\n"
            + proc.stdout + proc.stderr
        )


def check_repo_exists(org: str, repo_name: str) -> bool | None:
    """Best-effort DoltHub existence probe. None = inconclusive (network)."""
    url = f"https://www.dolthub.com/api/v1alpha1/{org}/{repo_name}"
    proc = run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                "--max-time", "10", url], check=False)
    code = proc.stdout.strip()
    if proc.returncode != 0 or not code.isdigit():
        return None
    return code == "200"


def remote_tags(org: str, repo_name: str) -> set[str] | None:
    """Best-effort DoltHub tag listing via the public SQL API.

    Returns the set of tag names on the remote, or None when inconclusive
    (network failure, unexpected payload). Used to reconcile local tags that a
    prior failed push stranded — see push().
    """
    url = (f"https://www.dolthub.com/api/v1alpha1/{org}/{repo_name}/main"
           f"?q=SELECT+tag_name+FROM+dolt_tags")
    proc = run(["curl", "-s", "--max-time", "10", url], check=False)
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return None
    return {r["tag_name"] for r in rows if isinstance(r, dict) and r.get("tag_name")}


def push(repo: Path, org: str, repo_name: str, tag: str | None) -> None:
    """Gate order: remote → creds → repo-exists → push main → push tag."""
    ensure_remote(repo, org, repo_name)
    check_creds()
    exists = check_repo_exists(org, repo_name)
    create_help = (
        f"create the database on DoltHub first (push never auto-creates): "
        f"https://www.dolthub.com/new — owner {org!r}, name {repo_name!r}, "
        f"visibility public. Scripted (per dolthub.com/docs/products/dolthub/api): "
        f"POST https://www.dolthub.com/api/v1alpha1/database with header "
        f"'authorization: token <api-token>' and body "
        f'{{"ownerName":"{org}","repoName":"{repo_name}","visibility":"public"}}. '
        f"Then re-run this sync."
    )
    if exists is False:
        raise PushError(f"DoltHub database {org}/{repo_name} does not exist — {create_help}")
    if exists is None:
        log("DoltHub existence probe inconclusive (network) — attempting push anyway")

    tags_to_push: list[str] = [tag] if tag else []

    # Retry-safety: a prior sync may have committed+tagged locally and then
    # failed its push (exit 3). If the next inventory cycle runs before a
    # manual retry, that run's tag would otherwise be stranded forever — the
    # old code only ever pushed the CURRENT run's tag. Reconcile: push every
    # local tag the remote is missing, not just this run's.
    remote = remote_tags(org, repo_name)
    if remote is None:
        log("DoltHub tag listing inconclusive (network) — pushing only the "
            "current run's tag; a previously-stranded tag (if any) stays "
            "local until a sync with network access to the DoltHub API")
    else:
        local = {r[0] for r in dolt_csv_query(repo, "SELECT tag_name FROM dolt_tags")}
        stranded = sorted(local - remote - set(tags_to_push))
        if stranded:
            log(f"WARNING: {len(stranded)} local tag(s) never reached DoltHub "
                f"(a prior sync's push failed and was not retried): {stranded} "
                f"— pushing them now")
            tags_to_push.extend(stranded)

    refs = ["main"]
    # Tags do NOT ride along on a branch push; use the explicit refspec
    # form so the tag lands as a tag (a bare name can label the transfer
    # as a branch).
    refs.extend(f"refs/tags/{t}:refs/tags/{t}" for t in tags_to_push)
    for ref in refs:
        proc = dolt(["push", "origin", ref], repo, check=False)
        out = proc.stdout + proc.stderr
        if proc.returncode != 0:
            if "PermissionDenied" in out and "Uploading" in out:
                # The classified miss signature: valid creds, repo missing.
                raise PushError(
                    f"push of {ref} rejected with PermissionDenied after upload "
                    f"started — this is the repo-missing signature, not a creds "
                    f"problem. {create_help}\n{out}"
                )
            raise PushError(f"push of {ref} failed:\n{out}")
        log(f"pushed {ref} → {org}/{repo_name}")


# ---------------------------------------------------------------------------
# GC policy
# ---------------------------------------------------------------------------


def dir_size_bytes(path: Path) -> int:
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def maybe_gc(repo: Path, state_path: Path, force: bool) -> None:
    state = {"syncs_since_gc": 0, "size_after_gc_bytes": 0}
    if state_path.exists():
        try:
            state.update(json.loads(state_path.read_text()))
        except (json.JSONDecodeError, OSError):
            pass
    state["syncs_since_gc"] = int(state.get("syncs_since_gc", 0)) + 1
    size_now = dir_size_bytes(repo)
    baseline = int(state.get("size_after_gc_bytes", 0)) or size_now
    due = (
        force
        or state["syncs_since_gc"] >= GC_EVERY_N_SYNCS
        or size_now > GC_SIZE_FACTOR * baseline
    )
    if due:
        # The sql-server exclusion check ran at lock-acquisition time, but a
        # `dolt sql-server` can have been started against this repo during the
        # multi-minute sync — gc under a live server corrupts the working set.
        # Re-check RIGHT BEFORE gc, and never fail the sync over gc: by this
        # point commit+push already succeeded, so a gc problem is loud-skip,
        # not exit-1 (which would misreport a successful, pushed sync).
        try:
            refuse_if_server_running(repo)
        except SyncError as exc:
            log(f"WARNING: skipping dolt gc — {exc} (the sync itself already "
                f"succeeded; gc will be retried next sync)")
            state_path.write_text(json.dumps(state) + "\n")
            return
        log(f"running dolt gc (syncs_since_gc={state['syncs_since_gc']}, "
            f"size={size_now / 1e6:.0f}MB, baseline={baseline / 1e6:.0f}MB)")
        try:
            dolt(["gc"], repo)
        except subprocess.CalledProcessError as exc:
            log(f"WARNING: dolt gc failed ({(exc.stderr or exc.stdout or '').strip()}) "
                f"— the sync itself already succeeded and was pushed; gc will "
                f"be retried next sync")
            state_path.write_text(json.dumps(state) + "\n")
            return
        state["syncs_since_gc"] = 0
        state["size_after_gc_bytes"] = dir_size_bytes(repo)
    state_path.write_text(json.dumps(state) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def source_git_sha(repo_root: Path = REPO_ROOT) -> str:
    proc = run(["git", "-C", str(repo_root), "rev-parse", "--short", "HEAD"], check=False)
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--db", type=Path, default=DB_DEFAULT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT,
                        help="repository root used to normalize absolute skill paths "
                             "and stamp the source Git SHA")
    parser.add_argument("--dolt-dir", type=Path, default=DOLT_PARENT / DOLT_DB_NAME)
    parser.add_argument("--grades-csv", type=Path, default=GRADES_CSV,
                        help="write the current-run grades CSV here (default: freshie/grades.csv)")
    parser.add_argument("--grade-histogram", type=Path, default=GRADE_HISTOGRAM,
                        help="write the current-run grade histogram here (default: freshie/grade-histogram.json)")
    parser.add_argument("--verify-grade-exports", action="store_true",
                        help="read-only: fail unless tracked grade exports match the latest inventory run")
    parser.add_argument("--reports-dir", type=Path, default=None,
                        help="write run-delta reports here (default: freshie/reports)")
    parser.add_argument("--org", default=DEFAULT_ORG)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--no-push", action="store_true",
                        help="local sync only (commit + tag, no DoltHub push)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the translated DDL and plan; touch nothing")
    parser.add_argument("--recreate-tables", action="store_true",
                        help="drop + recreate Dolt tables whose schema drifted")
    parser.add_argument("--gc", action="store_true", help="force dolt gc this run")
    parser.add_argument("--alert-on-regression", action="store_true",
                        help="exit 4 when the post-commit run-delta finds "
                             "grade regressions (default: report only)")
    args = parser.parse_args()

    if not args.db.exists():
        log(f"source DB not found: {args.db}")
        return 1

    if args.verify_grade_exports:
        conn = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
        try:
            try:
                gate_tracked_grade_exports(
                    conn, args.grades_csv, args.grade_histogram, args.repo_root
                )
            except SyncError as exc:
                log(f"FAILED: {exc}")
                return 1
        finally:
            conn.close()
        return 0

    repo: Path = args.dolt_dir
    lock_fd = None
    tmpdir = None
    try:
        if not args.dry_run:
            lock_fd = acquire_lock(repo.parent / ".sync.lock")
            if (repo / ".dolt").is_dir():
                refuse_if_server_running(repo)
            # This is intentionally before VACUUM INTO: the snapshot is the
            # public-export input and must carry the demoted class, not merely
            # diagnose it after the fact.
            writable = sqlite3.connect(args.db)
            try:
                demoted = demote_unretained_forge_proofs(writable)
                writable.commit()
            finally:
                writable.close()
            if demoted:
                log(f"evidence gate: demoted {len(demoted)} forge_proofs row(s) to E0")

        # Snapshot for read consistency across the whole export.
        shm = Path("/dev/shm")
        tmpdir = Path(tempfile.mkdtemp(
            prefix="dolt-sync-", dir=str(shm) if shm.is_dir() else None
        ))
        snapshot = tmpdir / "inventory-snapshot.sqlite"
        src = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
        src.execute("VACUUM INTO ?", (str(snapshot),))
        src.close()
        conn = sqlite3.connect(f"file:{snapshot}?mode=ro", uri=True)

        schema = introspect_schema(conn)
        tables = sorted(schema)
        # Membership gate FIRST (also in --dry-run): an unknown table must
        # hard-fail before any DDL/plan output normalizes its presence.
        gate_export_allowlist(tables)
        # A source that cannot be exported must fail before environment-
        # dependent publication setup can mask the security refusal.  Once it
        # is known publishable, a real export still requires a configured Dolt
        # identity before it can create or update the destination repository.
        if not args.dry_run:
            ensure_dolt_identity()
        violations = scan_type_violations(conn, schema)
        widen = frozenset(violations)
        for (t, c), n in sorted(violations.items()):
            log(f"type violation: {t}.{c} has {n} rows breaking its declared "
                f"type — widening to LONGTEXT (SQLite typing is advisory; the "
                f"record keeps what SQLite holds)")
        ddls = {t: build_create_table(t, schema[t], widen) for t in tables}
        # Widened REAL columns are text now — exclude them from the printf
        # export wrapper and the float checksum gate (row-count parity and
        # the import itself still cover them).
        reals = {
            t: [c for c in cols if (t, c) not in widen]
            for t, cols in real_columns(schema).items()
        }
        reals = {t: cols for t, cols in reals.items() if cols}
        guards = text_pk_guards(schema)
        run_id_row = conn.execute("SELECT MAX(id) FROM discovery_runs").fetchone()
        run_id = int(run_id_row[0] or 0)

        # A dry run is a publish preflight, not merely a DDL preview.  It must
        # reject the same phantom/internally inconsistent inventory runs that
        # a real export rejects, before printing a plan that could be mistaken
        # for approval to publish.
        gate_run_completeness(conn, run_id)

        if args.dry_run:
            for t in tables:
                print(ddls[t] + "\n")
            log(f"dry run: {len(tables)} tables, run_id={run_id}, "
                f"{sum(len(v) for v in reals.values())} REAL columns, "
                f"{len(guards)} TEXT PKs, {len(widen)} widened columns, "
                f"JSON checks on {[f'{t}.{c}' for t, c in JSON_CHECKSUM_COLUMNS]}")
            return 0

        gate_varchar_lengths(conn, guards)
        ensure_repo(repo)

        canary_ok = run_canary(repo, tmpdir)
        if canary_ok:
            log("canary: NULL/''/DATETIME(6)/quoting round-trip OK — CSV pump")
        else:
            log("canary FAILED — empty-string-bearing tables fall back to INSERT pump")

        existing = dolt_tables(repo)
        for t in tables:
            col_names = [c[0] for c in schema[t]["columns"]]
            if t not in existing:
                dolt(["sql", "-q", ddls[t]], repo)
            elif args.recreate_tables:
                dolt(["sql", "-q", f"DROP TABLE `{t}`"], repo)
                dolt(["sql", "-q", ddls[t]], repo)

            use_insert_fallback = False
            if not canary_ok:
                text_cols = [
                    c[0] for c in schema[t]["columns"]
                    if (c[1] or "").strip().upper() == "TEXT"
                ]
                use_insert_fallback = text_cols and table_has_empty_strings(
                    conn, t, text_cols
                )

            if use_insert_fallback:
                pump_table_inserts(conn, repo, t, col_names)
            else:
                csv_path = tmpdir / f"{t}.csv"
                export_table_csv(snapshot, t, col_names, reals.get(t, []), csv_path)
                if csv_path.stat().st_size == 0:
                    # sqlite3 emits nothing (not even a header) for an empty
                    # table, and dolt refuses an empty file — converge with a
                    # plain DELETE instead.
                    dolt(["sql", "-q", f"DELETE FROM `{t}`"], repo)
                else:
                    proc = dolt(
                        ["table", "import", "-r", "--file-type", "csv", t, str(csv_path)],
                        repo, check=False,
                    )
                    if proc.returncode != 0:
                        raise SyncError(
                            f"import of {t} aborted (schema mismatch is a parity gate — "
                            f"if the SQLite schema legitimately changed, re-run with "
                            f"--recreate-tables):\n{proc.stdout}{proc.stderr}"
                        )
                csv_path.unlink()
        log(f"pumped {len(tables)} tables")

        gate_row_counts(conn, repo, tables)
        gate_real_checksums(conn, repo, reals)
        gate_json_checksums(conn, repo, schema)

        write_grades_export(
            conn, run_id, args.grades_csv, args.grade_histogram, args.repo_root
        )
        gate_tracked_grade_exports(
            conn, args.grades_csv, args.grade_histogram, args.repo_root
        )
        conn.close()

        committed, tag, head_hash = commit_and_tag(
            repo, run_id, source_git_sha(args.repo_root)
        )
        log(f"commit created: {committed}; tag: {tag or '(none)'}")

        # Fail closed before push: the immutable receipt is part of the
        # publication product, not optional observability.
        regressions_found = post_commit_outputs(
            repo, run_id, tag, head_hash, args.grades_csv,
            args.grade_histogram, args.reports_dir
        )

        if args.no_push:
            log("--no-push: skipping DoltHub push (history is LOCAL-ONLY until pushed)")
        else:
            push(repo, args.org, args.repo, tag)

        maybe_gc(repo, repo.parent / ".sync-state.json", args.gc)
        log("sync complete")
        if args.alert_on_regression and regressions_found:
            log("ALERT: grade regressions detected this run — exiting 4 as "
                "requested (--alert-on-regression); the sync itself succeeded")
            return 4
        return 0

    except PushError as exc:
        log(f"PUSH FAILED (history committed locally but NOT on DoltHub): {exc}")
        return 3
    except SyncError as exc:
        log(f"FAILED: {exc}")
        return 1
    except subprocess.CalledProcessError as exc:
        log(f"FAILED: {' '.join(exc.cmd)} → {exc.stderr or exc.stdout}")
        return 1
    finally:
        if tmpdir is not None:
            shutil.rmtree(tmpdir, ignore_errors=True)
        if lock_fd is not None:
            os.close(lock_fd)


if __name__ == "__main__":
    sys.exit(main())
