#!/usr/bin/env python3
"""Publish a governed Freshie SQLite snapshot as native DoltLite history."""

from __future__ import annotations

import argparse
import ast
import contextlib
import datetime as dt
import fcntl
import hashlib
import heapq
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Any

try:
    # Must precede sqlite3: this loads libdoltlite into the process.
    import doltlite
except ImportError as exc:  # pragma: no cover - CLI failure is tested in CI
    raise SystemExit(
        "doltlite is required; install the pinned dependency with `python3 -m pip install doltlite==0.50.1`"
    ) from exc

import sqlite3  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DEFAULT = REPO_ROOT / "freshie" / "inventory.sqlite"
TARGET_DEFAULT = REPO_ROOT / "freshie" / "doltlite" / "freshie-inventory.db"
RECEIPTS_DEFAULT = REPO_ROOT / "freshie" / "reports"
SCHEMA_BASELINE_DEFAULT = REPO_ROOT / "freshie" / "doltlite-schema-baseline.json"
CANONICAL_EXPORTER = REPO_ROOT / "freshie" / "scripts" / "dolt-sync.py"
GRADES_CSV = REPO_ROOT / "freshie" / "grades.csv"
HISTOGRAM = REPO_ROOT / "freshie" / "grade-histogram.json"
FULL_DOLT_REPOSITORY = "jeremylongshore/freshie-inventory"
FULL_DOLT_API = "https://www.dolthub.com/api/v1alpha1"
DEFAULT_REMOTE = (
    "https://doltliteremoteapi.dolthub.com/"
    f"{os.environ.get('DOLTHUB_ORG', 'jeremylongshore')}/freshie-inventory-doltlite"
)
PINNED_DOLTLITE = "0.50.1"
HASH_RE = re.compile(r"^[0-9a-v]{32}$")
TABLE_DIGEST_CHUNK_ROWS = 10_000
MAX_SCANNED_VALUE_BYTES = 8 * 1024 * 1024
SECRET_PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{50,}|gh[pousr]_[A-Za-z0-9]{30,})\b")),
    ("openai-key", re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_-]{32,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("anthropic-key", re.compile(r"\bsk-ant-(?:api\d{2}-)?[A-Za-z0-9_-]{32,}\b")),
    ("stripe-live-key", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b")),
    ("gitlab-token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("huggingface-token", re.compile(r"\bhf_[A-Za-z0-9]{30,}\b")),
    ("npm-token", re.compile(r"\bnpm_[A-Za-z0-9]{30,}\b")),
    ("databricks-token", re.compile(r"\bdapi[a-f0-9]{32}\b")),
    ("azure-account-key", re.compile(r"\bAccountKey=[A-Za-z0-9+/]{40,}={0,2}(?:;|\b)")),
    (
        "bearer-token",
        re.compile(r"\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._~-]{24,}\b", re.IGNORECASE),
    ),
)


class SyncError(RuntimeError):
    """A fail-closed publication error."""


def quote_ident(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def json_sha256(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def load_literal_set(path: Path, name: str) -> frozenset[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(isinstance(target, ast.Name) and target.id == name for target in targets):
            continue
        value = node.value
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "frozenset"
            and len(value.args) == 1
        ):
            value = value.args[0]
        return frozenset(str(item) for item in ast.literal_eval(value))
    raise SyncError(f"{name} not found as a literal assignment in {path}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyncError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SyncError(f"JSON object required in {path}")
    return payload


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        temporary.replace(path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as exc:
        if temporary is not None:
            with contextlib.suppress(OSError):
                temporary.unlink()
        raise SyncError(f"cannot atomically write {path}: {exc}") from exc


@contextlib.contextmanager
def process_lock(target: Path) -> Iterator[None]:
    target.parent.mkdir(parents=True, exist_ok=True)
    lock_path = target.parent / f".{target.name}.sync.lock"
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)  # lock file: owner-only
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SyncError(f"another DoltLite sync holds {lock_path}") from exc
        yield
    finally:
        os.close(descriptor)


def snapshot_sqlite(source: Path, destination: Path) -> None:
    if not source.is_file() or source.stat().st_size == 0:
        raise SyncError(f"source inventory is missing or empty: {source}")
    escaped = str(destination).replace("'", "''")
    completed = subprocess.run(
        ["sqlite3", str(source), f".backup '{escaped}'"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SyncError(f"SQLite snapshot failed: {completed.stderr.strip()}")


def stock_connection(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?doltlite_engine=sqlite", uri=True)


def source_tables(connection: sqlite3.Connection, schema: str) -> list[str]:
    return [
        str(row[0])
        for row in connection.execute(
            f"SELECT name FROM {quote_ident(schema)}.sqlite_schema "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]


def gate_membership(tables: Iterable[str], allowlist: frozenset[str]) -> list[str]:
    names = sorted(set(tables))
    unknown = sorted(set(names) - allowlist)
    if unknown:
        raise SyncError("source contains tables not approved for permanent public history: " + ", ".join(unknown))
    return names


def latest_run_id(connection: sqlite3.Connection, schema: str) -> int:
    columns = {row[1] for row in connection.execute(f"PRAGMA {quote_ident(schema)}.table_info(discovery_runs)")}
    run_column = "run_id" if "run_id" in columns else "id" if "id" in columns else None
    if run_column is None:
        raise SyncError(f"{schema}.discovery_runs has neither run_id nor id")
    row = connection.execute(
        f"SELECT MAX({quote_ident(run_column)}) FROM {quote_ident(schema)}.discovery_runs"
    ).fetchone()
    if not row or row[0] is None:
        raise SyncError(f"{schema}.discovery_runs has no run")
    return int(row[0])


def load_canonical_exporter() -> Any:
    spec = importlib.util.spec_from_file_location("freshie_canonical_dolt_sync", CANONICAL_EXPORTER)
    if spec is None or spec.loader is None:
        raise SyncError(f"cannot import canonical exporter {CANONICAL_EXPORTER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_safety_gate(snapshot: Path, run_id: int) -> None:
    canonical = load_canonical_exporter()
    connection = stock_connection(snapshot)
    try:
        canonical.gate_run_completeness(connection, run_id)
        demoted = canonical.demote_unretained_forge_proofs(connection)
        if demoted:
            raise SyncError(
                f"{len(demoted)} forge_proofs row(s) require canonical E0 demotion; "
                "run freshie/scripts/dolt-sync.py before DoltLite publication"
            )
        canonical.gate_tracked_grade_exports(connection, GRADES_CSV, HISTOGRAM, REPO_ROOT)
    except canonical.SyncError as exc:
        raise SyncError(str(exc)) from exc
    finally:
        connection.close()


def dolthub_query(
    repository: str,
    revision: str,
    query: str,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> list[dict[str, Any]]:
    owner, separator, database = repository.partition("/")
    if not separator or not owner or not database:
        raise SyncError(f"invalid full-Dolt repository {repository!r}")
    url = (
        f"{FULL_DOLT_API}/{urllib.parse.quote(owner)}/"
        f"{urllib.parse.quote(database)}/{urllib.parse.quote(revision)}?" + urllib.parse.urlencode({"q": query})
    )
    try:
        with opener(url, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise SyncError(f"full-Dolt authority query failed: {exc}") from exc
    if payload.get("query_execution_status") != "Success":
        raise SyncError(f"full-Dolt authority rejected query: {payload!r}")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise SyncError("full-Dolt authority returned malformed rows")
    return rows


def resolve_full_dolt_lineage(
    run_id: int,
    *,
    repository: str = FULL_DOLT_REPOSITORY,
    query: Callable[[str, str, str], list[dict[str, Any]]] = dolthub_query,
) -> dict[str, Any]:
    ref = f"run-{run_id}"
    tag_rows = query(
        repository,
        "main",
        f"SELECT tag_hash FROM dolt_tags WHERE tag_name='{ref}'",
    )
    if len(tag_rows) != 1:
        raise SyncError(f"full-Dolt authority has no unique immutable {ref} tag")
    commit = str(tag_rows[0].get("tag_hash", ""))
    if not HASH_RE.fullmatch(commit):
        raise SyncError(f"full-Dolt {ref} returned invalid commit {commit!r}")
    # The v1 SQL API path resolves branches, not tags/commit hashes. Pin the
    # data query with AS OF and independently require the commit in dolt_log.
    run_rows = query(
        repository,
        "main",
        f"SELECT MAX(id) AS run_id FROM discovery_runs AS OF '{commit}'",
    )
    log_rows = query(
        repository,
        "main",
        f"SELECT commit_hash FROM dolt_log WHERE commit_hash='{commit}'",
    )
    database_rows = query(
        repository,
        "main",
        f"SELECT dolt_hashof_db('{ref}') AS database_hash",
    )
    parent_rows = query(
        repository,
        "main",
        f"SELECT parent_hash FROM dolt_commit_ancestors WHERE commit_hash='{commit}' AND parent_index=0",
    )
    try:
        resolved_run = int(run_rows[0]["run_id"])
        resolved_head = str(log_rows[0]["commit_hash"])
        database_hash = str(database_rows[0]["database_hash"])
        direct_parent = str(parent_rows[0]["parent_hash"])
    except (IndexError, KeyError, TypeError, ValueError) as exc:
        raise SyncError(f"full-Dolt {ref} returned malformed lineage evidence") from exc
    if resolved_run != run_id:
        raise SyncError(f"full-Dolt {ref} contains latest run {resolved_run}, expected {run_id}")
    if resolved_head != commit:
        raise SyncError(f"full-Dolt {ref} tag/hash mismatch: tag={commit}, revision={resolved_head}")
    if not HASH_RE.fullmatch(database_hash):
        raise SyncError(f"full-Dolt {ref} returned invalid database hash {database_hash!r}")
    if not HASH_RE.fullmatch(direct_parent):
        raise SyncError(f"full-Dolt {ref} returned invalid direct parent {direct_parent!r}")
    return {
        "repository": repository,
        "ref": ref,
        "commit": commit,
        "database_hash": database_hash,
        "direct_parent": direct_parent,
        "run_id": run_id,
        "verified_via": FULL_DOLT_API,
    }


def gate_tracked_full_dolt_receipt(run_id: int, commit: str) -> None:
    """Require the tracked grade receipt to name the resolved public commit."""
    payload = read_json(HISTOGRAM)
    if payload.get("run_id") != run_id or payload.get("dolt_commit") != commit:
        raise SyncError(
            f"tracked grade-histogram full-Dolt receipt does not match the resolved run-{run_id} commit {commit}"
        )


def validate_remote_url(remote_url: str) -> None:
    """Keep credentials and opaque query material out of tracked receipts."""
    parsed = urllib.parse.urlsplit(remote_url)
    if parsed.scheme not in {"https", "file"}:
        raise SyncError("DoltLite remote must use https:// or file://")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise SyncError("DoltLite remote URL must not embed credentials, query parameters, or fragments")


def encode_value(value: Any) -> bytes:
    if value is None:
        body = b"null"
    elif isinstance(value, bytes):
        body = b"blob:" + value
    elif isinstance(value, float):
        body = b"float:" + value.hex().encode("ascii")
    elif isinstance(value, int):
        body = b"int:" + str(value).encode("ascii")
    else:
        body = b"text:" + str(value).encode("utf-8", errors="surrogatepass")
    return len(body).to_bytes(8, "big") + body


def fixed_hashes(path: Path) -> Iterator[bytes]:
    with path.open("rb") as handle:
        while value := handle.read(32):
            if len(value) != 32:
                raise SyncError(f"corrupt table-digest chunk {path}")
            yield value


def table_digest(connection: sqlite3.Connection, schema: str, table: str) -> tuple[int, str]:
    query = f"SELECT * FROM {quote_ident(schema)}.{quote_ident(table)}"
    count = 0
    chunk: list[bytes] = []
    with tempfile.TemporaryDirectory(prefix="freshie-table-digest-") as directory:
        paths: list[Path] = []

        def flush() -> None:
            if not chunk:
                return
            chunk.sort()
            path = Path(directory) / f"{len(paths):08d}.hashes"
            with path.open("wb") as handle:
                handle.writelines(chunk)
            paths.append(path)
            chunk.clear()

        for row in connection.execute(query):
            encoded = b"".join(encode_value(value) for value in row)
            chunk.append(hashlib.sha256(encoded).digest())
            count += 1
            if len(chunk) >= TABLE_DIGEST_CHUNK_ROWS:
                flush()
        flush()
        digest = hashlib.sha256(table.encode("utf-8"))
        if paths:
            for row_hash in heapq.merge(*(fixed_hashes(path) for path in paths)):
                digest.update(row_hash)
        return count, digest.hexdigest()


def table_schema_digest(connection: sqlite3.Connection, schema: str, table: str) -> str:
    rows = connection.execute(
        f"SELECT type,name,tbl_name,sql FROM {quote_ident(schema)}.sqlite_schema "
        "WHERE ((type='table' AND name=?) OR (type='index' AND tbl_name=?)) "
        "AND sql IS NOT NULL ORDER BY type,name",
        (table, table),
    ).fetchall()
    normalized = [[kind, name, table_name, " ".join(str(ddl).split())] for kind, name, table_name, ddl in rows]
    return hashlib.sha256(canonical_json(normalized)).hexdigest()


def table_schema_contract(connection: sqlite3.Connection, schema: str, table: str) -> str:
    columns = connection.execute(f"PRAGMA {quote_ident(schema)}.table_xinfo({quote_ident(table)})").fetchall()
    indexes = []
    for index_row in connection.execute(f"PRAGMA {quote_ident(schema)}.index_list({quote_ident(table)})").fetchall():
        index_columns = connection.execute(
            f"PRAGMA {quote_ident(schema)}.index_xinfo({quote_ident(index_row[1])})"
        ).fetchall()
        indexes.append([list(index_row[1:]), [list(row) for row in index_columns]])
    foreign_keys = connection.execute(f"PRAGMA {quote_ident(schema)}.foreign_key_list({quote_ident(table)})").fetchall()
    contract = {
        "columns": [list(row) for row in columns],
        "indexes": sorted(indexes, key=lambda item: item[0][0]),
        "foreign_keys": [list(row) for row in foreign_keys],
    }
    return hashlib.sha256(canonical_json(contract)).hexdigest()


def schema_baseline_payload(
    connection: sqlite3.Connection,
    schema: str,
    tables: Iterable[str],
    allowlist: frozenset[str],
) -> dict[str, Any]:
    included = sorted(tables)
    records = []
    for table in included:
        column_rows = connection.execute(f"PRAGMA {quote_ident(schema)}.table_xinfo({quote_ident(table)})").fetchall()
        records.append(
            {
                "table": table,
                # Human-readable exposure review surface. The contract hash
                # below additionally covers declared types, nullability, PK
                # ordinals, hidden/generated columns, indexes, and FKs.
                "columns": [row[1] for row in column_rows],
                "schema_contract_sha256": table_schema_contract(connection, schema, table),
            }
        )
    return {
        "schema_version": 2,
        "publication_denominator": {
            "mode": "exact",
            "included_table_count": len(included),
            "allowed_but_excluded_tables": sorted(allowlist - set(included)),
        },
        "tables": records,
    }


def gate_supported_schema(connection: sqlite3.Connection, schema: str) -> None:
    rows = connection.execute(
        f"SELECT type,name FROM {quote_ident(schema)}.sqlite_schema WHERE type IN ('view','trigger') ORDER BY type,name"
    ).fetchall()
    if rows:
        rendered = ", ".join(f"{kind}:{name}" for kind, name in rows)
        raise SyncError("views/triggers require an explicitly implemented DoltLite migration: " + rendered)


def gate_secret_values(connection: sqlite3.Connection, schema: str, tables: Iterable[str]) -> None:
    """Reject high-confidence credential shapes without logging their values."""
    for table in tables:
        columns = [
            str(row[1])
            for row in connection.execute(f"PRAGMA {quote_ident(schema)}.table_xinfo({quote_ident(table)})").fetchall()
        ]
        query = f"SELECT * FROM {quote_ident(schema)}.{quote_ident(table)}"
        for row_number, row in enumerate(connection.execute(query), start=1):
            for column, value in zip(columns, row, strict=True):
                if not isinstance(value, (str, bytes)):
                    continue
                raw = value if isinstance(value, bytes) else value.encode("utf-8", errors="surrogatepass")
                if len(raw) > MAX_SCANNED_VALUE_BYTES:
                    raise SyncError(f"public value exceeds scan limit at {table}.{column} row {row_number}")
                text_value = value.decode("utf-8", errors="ignore") if isinstance(value, bytes) else value
                for pattern_name, pattern in SECRET_PATTERNS:
                    if pattern.search(text_value):
                        raise SyncError(
                            f"secret-shaped {pattern_name} value refused at {table}.{column} row {row_number}"
                        )


def gate_schema_baseline(actual: dict[str, Any], baseline_path: Path, approve_schema_drift: bool) -> str:
    if baseline_path.is_file():
        expected = read_json(baseline_path)
        if expected == actual:
            return json_sha256(actual)
        if not approve_schema_drift:
            old = {row["table"]: row for row in expected.get("tables", [])}
            new = {row["table"]: row for row in actual["tables"]}
            added = sorted(new.keys() - old.keys())
            removed = sorted(old.keys() - new.keys())
            changed = sorted(name for name in new.keys() & old.keys() if new[name] != old[name])
            raise SyncError(
                "unapproved schema/column drift; review and rerun with "
                f"--approve-schema-drift (added={added}, removed={removed}, "
                f"changed={changed})"
            )
    elif not approve_schema_drift:
        raise SyncError(f"schema baseline {baseline_path} is missing; review and rerun with --approve-schema-drift")
    atomic_json(baseline_path, actual)
    return json_sha256(actual)


def gate_publication_denominator(tables: Iterable[str], allowlist: frozenset[str], baseline_path: Path) -> None:
    """Enforce the reviewed table set even when column drift is approved."""
    baseline = read_json(baseline_path)
    records = baseline.get("tables")
    denominator = baseline.get("publication_denominator")
    if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
        raise SyncError(f"schema baseline has no exact table denominator: {baseline_path}")
    expected = [record.get("table") for record in records]
    if not all(isinstance(name, str) and name for name in expected) or len(expected) != len(set(expected)):
        raise SyncError(f"schema baseline has duplicate or invalid table names: {baseline_path}")
    expected_set = set(expected)
    canonical_denominator = {
        "mode": "exact",
        "included_table_count": len(expected),
        "allowed_but_excluded_tables": sorted(allowlist - expected_set),
    }
    if denominator != canonical_denominator or not expected_set <= allowlist:
        raise SyncError(f"schema baseline publication denominator is incomplete or inconsistent: {baseline_path}")
    actual_set = set(tables)
    if actual_set != expected_set:
        raise SyncError(
            "source does not equal the reviewed publication denominator "
            f"(added={sorted(actual_set - expected_set)}, removed={sorted(expected_set - actual_set)})"
        )


def source_table_receipts(connection: sqlite3.Connection, schema: str, tables: Iterable[str]) -> list[dict[str, Any]]:
    receipts = []
    for table in tables:
        row_count, content_hash = table_digest(connection, schema, table)
        receipts.append(
            {
                "table": table,
                "rows": row_count,
                "content_sha256": content_hash,
                "schema_contract_sha256": table_schema_contract(connection, schema, table),
                "source_schema_sha256": table_schema_digest(connection, schema, table),
            }
        )
    return receipts


def source_snapshot_receipt_payload(
    *,
    artifact_name: str,
    backup_sha256: str,
    run_id: int,
    lineage: dict[str, Any],
    schema_baseline_sha256: str,
    table_receipts: list[dict[str, Any]],
    reviewed_by: str,
    reviewed_at: str,
) -> dict[str, Any]:
    """Build the exact body that a human-reviewed source receipt must seal."""
    return {
        "schema_version": 1,
        "review": {
            "status": "approved",
            "reviewed_by": reviewed_by,
            "reviewed_at": reviewed_at,
        },
        "source_artifact": {
            "name": artifact_name,
            "backup_sha256": backup_sha256,
        },
        "run_id": run_id,
        "full_dolt": lineage,
        "schema_baseline_sha256": schema_baseline_sha256,
        "table_receipts_sha256": json_sha256(table_receipts),
        "table_receipts": table_receipts,
    }


def seal_source_snapshot_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(payload)
    sealed["receipt_sha256"] = json_sha256(payload)
    return sealed


def gate_committed_source_receipt(path: Path) -> None:
    """Require an in-repository production receipt to equal its reviewed HEAD blob."""
    try:
        relative = path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise SyncError(f"production source receipt must be tracked under {REPO_ROOT}: {path}") from exc
    relative_text = relative.as_posix()
    tracked = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{relative_text}"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if tracked.returncode != 0:
        raise SyncError(f"source receipt is not committed at HEAD: {relative_text}")
    reviewed = subprocess.run(
        ["git", "show", f"HEAD:{relative_text}"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    try:
        current = path.read_bytes()
    except OSError as exc:
        raise SyncError(f"cannot read source receipt {path}: {exc}") from exc
    if reviewed.returncode != 0 or reviewed.stdout != current:
        raise SyncError(f"source receipt differs from its reviewed HEAD blob: {relative_text}")


def gate_source_snapshot_receipt(
    path: Path,
    *,
    artifact_name: str,
    backup_sha256: str,
    run_id: int,
    lineage: dict[str, Any],
    schema_baseline_sha256: str,
    table_receipts: list[dict[str, Any]],
    allow_untracked: bool = False,
) -> str:
    """Fail closed unless reviewed evidence binds every publication input."""
    if not allow_untracked:
        gate_committed_source_receipt(path)
    receipt = read_json(path)
    receipt_hash = receipt.get("receipt_sha256")
    body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
    if set(receipt) != {
        "schema_version",
        "review",
        "source_artifact",
        "run_id",
        "full_dolt",
        "schema_baseline_sha256",
        "table_receipts_sha256",
        "table_receipts",
        "receipt_sha256",
    }:
        raise SyncError(f"source receipt has an unexpected or incomplete schema: {path}")
    if not isinstance(receipt_hash, str) or receipt_hash != json_sha256(body):
        raise SyncError(f"source receipt seal is missing or invalid: {path}")
    review = receipt.get("review")
    if (
        not isinstance(review, dict)
        or set(review) != {"status", "reviewed_by", "reviewed_at"}
        or review.get("status") != "approved"
        or not isinstance(review.get("reviewed_by"), str)
        or not review["reviewed_by"].strip()
        or not isinstance(review.get("reviewed_at"), str)
        or not review["reviewed_at"].strip()
    ):
        raise SyncError(f"source receipt lacks an explicit human approval: {path}")
    expected = source_snapshot_receipt_payload(
        artifact_name=artifact_name,
        backup_sha256=backup_sha256,
        run_id=run_id,
        lineage=lineage,
        schema_baseline_sha256=schema_baseline_sha256,
        table_receipts=table_receipts,
        reviewed_by=str(review["reviewed_by"]),
        reviewed_at=str(review["reviewed_at"]),
    )
    if body != expected:
        raise SyncError(f"source receipt does not bind the current source snapshot and lineage: {path}")
    return receipt_hash


def schema_objects(
    connection: sqlite3.Connection, schema: str, tables: Iterable[str]
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    approved = set(tables)
    table_ddl: list[tuple[str, str]] = []
    index_ddl: list[tuple[str, str]] = []
    for object_type, name, table_name, ddl in connection.execute(
        f"SELECT type,name,tbl_name,sql FROM {quote_ident(schema)}.sqlite_schema "
        "WHERE sql IS NOT NULL ORDER BY CASE type WHEN 'table' THEN 0 ELSE 1 END,name"
    ):
        if table_name not in approved:
            continue
        if object_type == "table":
            table_ddl.append((name, ddl))
        elif object_type == "index":
            index_ddl.append((name, ddl))
    if {name for name, _ in table_ddl} != approved:
        raise SyncError("could not recover CREATE TABLE SQL for every approved table")
    return table_ddl, index_ddl


def verify_engine(connection: sqlite3.Connection) -> tuple[str, str]:
    engine = str(connection.execute("SELECT doltlite_engine()").fetchone()[0])
    version = str(connection.execute("SELECT dolt_version()").fetchone()[0])
    if engine != "prolly":
        raise SyncError(f"target is not DoltLite format (engine={engine!r})")
    if getattr(doltlite, "__version__", "") != PINNED_DOLTLITE:
        raise SyncError(
            f"expected doltlite Python {PINNED_DOLTLITE}, got {getattr(doltlite, '__version__', 'unknown')}"
        )
    return engine, version


def reset_to_main(connection: sqlite3.Connection) -> None:
    if connection.execute("SELECT active_branch()").fetchone()[0] != "main":
        connection.execute("SELECT dolt_checkout('main')").fetchone()
    if connection.execute("SELECT COUNT(*) FROM dolt_log").fetchone()[0]:
        try:
            connection.execute("SELECT dolt_reset('--hard')").fetchone()
        except sqlite3.OperationalError as exc:
            if "no commit to reset to" not in str(exc):
                raise


def gate_target_ancestry(connection: sqlite3.Connection, run_id: int, allow_run19_bootstrap: bool) -> str | None:
    """Require run N to descend from immutable run N-1."""
    current = f"run-{run_id}"
    current_row = connection.execute("SELECT hash FROM dolt_branches WHERE name=?", (current,)).fetchone()
    head = str(connection.execute("SELECT dolt_hashof('HEAD')").fetchone()[0])
    if current_row:
        if head != current_row[0]:
            raise SyncError(f"main={head} does not equal immutable current {current}={current_row[0]}")
        if run_id == 1:
            return None
        previous = f"run-{run_id - 1}"
        previous_row = connection.execute("SELECT hash FROM dolt_branches WHERE name=?", (previous,)).fetchone()
        parent = str(connection.execute("SELECT dolt_hashof(?)", (f"{current}~",)).fetchone()[0])
        if not previous_row or parent != previous_row[0]:
            raise SyncError(f"existing {current} does not descend from immutable {previous}")
        return parent

    user_commits = connection.execute(
        "SELECT COUNT(*) FROM dolt_log WHERE message NOT LIKE 'Initialize data repository%'"
    ).fetchone()[0]
    if run_id == 1:
        if user_commits:
            raise SyncError("run-1 bootstrap requires an initialization-only target")
        return None
    previous = f"run-{run_id - 1}"
    row = connection.execute("SELECT hash FROM dolt_branches WHERE name=?", (previous,)).fetchone()
    if row:
        if head != row[0]:
            raise SyncError(f"main={head} does not equal immutable predecessor {previous}={row[0]}")
        return str(row[0])
    if run_id == 19 and allow_run19_bootstrap and user_commits == 0:
        return None
    raise SyncError(
        f"missing immutable predecessor branch {previous}; refusing ancestry-loss "
        "bootstrap (run 19 alone may use --bootstrap-run-19)"
    )


def replace_tables(
    connection: sqlite3.Connection,
    tables: list[str],
    table_ddl: list[tuple[str, str]],
    index_ddl: list[tuple[str, str]],
) -> None:
    connection.execute("PRAGMA foreign_keys=OFF")
    previous_isolation = connection.isolation_level
    # DoltLite rejects transactions spanning source and target files. The
    # process lock protects this multi-autocommit working-set operation.
    connection.isolation_level = None
    try:
        for table in reversed(tables):
            connection.execute(f"DROP TABLE IF EXISTS main.{quote_ident(table)}")
        for _, ddl in table_ddl:
            connection.execute(ddl)
        for table in tables:
            connection.execute(f"INSERT INTO {quote_ident(table)} SELECT * FROM source.{quote_ident(table)}")
        for _, ddl in index_ddl:
            connection.execute(ddl)
    except Exception:
        with contextlib.suppress(sqlite3.Error):
            connection.execute("SELECT dolt_reset('--hard')").fetchone()
        raise
    finally:
        connection.isolation_level = previous_isolation


def parity_receipts(
    connection: sqlite3.Connection,
    tables: Iterable[str],
    expected_source: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    receipts = []
    for table in tables:
        source_count, source_digest = table_digest(connection, "source", table)
        target_count, target_digest = table_digest(connection, "main", table)
        if (source_count, source_digest) != (target_count, target_digest):
            raise SyncError(
                f"parity failure for {table}: source={source_count}/{source_digest} "
                f"target={target_count}/{target_digest}"
            )
        source_contract = table_schema_contract(connection, "source", table)
        target_contract = table_schema_contract(connection, "main", table)
        if source_contract != target_contract:
            raise SyncError(f"schema contract failure for {table}: source={source_contract} target={target_contract}")
        receipts.append(
            {
                "table": table,
                "rows": source_count,
                "content_sha256": source_digest,
                "schema_contract_sha256": source_contract,
                "source_schema_sha256": table_schema_digest(connection, "source", table),
                "target_schema_sha256": table_schema_digest(connection, "main", table),
            }
        )
    if expected_source is not None:
        observed_source = [
            {key: value for key, value in receipt.items() if key != "target_schema_sha256"} for receipt in receipts
        ]
        if observed_source != expected_source:
            raise SyncError("attached source no longer matches the reviewed source table receipts")
    return receipts


def commit_if_changed(connection: sqlite3.Connection, message: str) -> tuple[str, bool]:
    dirty = connection.execute("SELECT COUNT(*) FROM dolt_status").fetchone()[0]
    if dirty:
        commit = connection.execute("SELECT dolt_commit('-A','-m',?)", (message,)).fetchone()[0]
        return str(commit), True
    return str(connection.execute("SELECT dolt_hashof('HEAD')").fetchone()[0]), False


def verify_commit_binding(connection: sqlite3.Connection, commit: str, run_id: int, full_dolt_commit: str) -> None:
    row = connection.execute("SELECT message FROM dolt_log WHERE commit_hash=?", (commit,)).fetchone()
    if not row or f"run {run_id};" not in str(row[0]) or f"full-dolt {full_dolt_commit};" not in str(row[0]):
        raise SyncError(
            "DoltLite HEAD predates verified lineage binding; rebuild the unpushed "
            "sidecar from the reviewed run-19 migration root"
        )


def protect_run_branch(connection: sqlite3.Connection, run_id: int, commit: str) -> str:
    branch = f"run-{run_id}"
    existing = connection.execute("SELECT hash FROM dolt_branches WHERE name=?", (branch,)).fetchone()
    if existing:
        if existing[0] != commit:
            raise SyncError(f"immutable {branch} already points to {existing[0]}, not {commit}")
        return branch
    connection.execute("SELECT dolt_branch(?,?)", (branch, commit)).fetchone()
    return branch


def verify_commit_parent(connection: sqlite3.Connection, run_branch: str, expected_parent: str | None) -> None:
    if expected_parent is None:
        return
    actual = str(connection.execute("SELECT dolt_hashof(?)", (f"{run_branch}~",)).fetchone()[0])
    if actual != expected_parent:
        raise SyncError(f"{run_branch} parent {actual} does not match predecessor {expected_parent}")


def configure_remote(connection: sqlite3.Connection, remote_url: str) -> None:
    row = connection.execute("SELECT url FROM dolt_remotes WHERE name='origin'").fetchone()
    if row and row[0] != remote_url:
        raise SyncError(f"origin already points to {row[0]!r}; refusing replacement")
    if not row:
        connection.execute("SELECT dolt_remote('add','origin',?)", (remote_url,)).fetchone()


def push_reference(connection: sqlite3.Connection, branch: str) -> str:
    return str(connection.execute("SELECT dolt_push('origin',?)", (branch,)).fetchone()[0])


def verify_remote_refs(
    remote_url: str,
    expected: dict[str, str],
    run_branch: str,
    expected_parent: str | None,
) -> None:
    with tempfile.TemporaryDirectory(prefix="freshie-doltlite-clone-") as directory:
        clone = sqlite3.connect(Path(directory) / "verification.db")
        try:
            clone.execute("SELECT dolt_clone(?)", (remote_url,)).fetchone()
            actual = {str(name): str(commit) for name, commit in clone.execute("SELECT name,hash FROM dolt_branches")}
            actual_parent = None
            if expected_parent is not None:
                actual_parent = str(clone.execute("SELECT dolt_hashof(?)", (f"{run_branch}~",)).fetchone()[0])
        finally:
            clone.close()
    mismatches = {
        branch: {"expected": commit, "actual": actual.get(branch)}
        for branch, commit in expected.items()
        if actual.get(branch) != commit
    }
    if mismatches:
        raise SyncError(f"clean-clone remote verification failed: {mismatches}")
    if expected_parent is not None and actual_parent != expected_parent:
        raise SyncError(f"clean-clone {run_branch} parent {actual_parent} does not match predecessor {expected_parent}")


def immutable_receipt(path: Path, payload: dict[str, Any]) -> str:
    receipt_hash = json_sha256(payload)
    final = dict(payload)
    final["receipt_sha256"] = receipt_hash
    if path.is_file():
        if read_json(path) != final:
            raise SyncError(f"immutable receipt {path} would change")
    else:
        atomic_json(path, final)
    return receipt_hash


def publication_journal(
    connection: sqlite3.Connection,
    remote_url: str,
    run_branch: str,
    commit: str,
    journal_path: Path,
    receipt_hash: str,
    expected_parent: str | None,
) -> dict[str, Any]:
    refs = {run_branch: commit, "main": commit}
    push_order = [run_branch, "main"]
    if expected_parent is not None:
        predecessor_branch = f"run-{int(run_branch.removeprefix('run-')) - 1}"
        refs[predecessor_branch] = expected_parent
        push_order.insert(0, predecessor_branch)
    if journal_path.is_file():
        journal = read_json(journal_path)
        if (
            journal.get("receipt_sha256") != receipt_hash
            or journal.get("refs") != refs
            or journal.get("remote_url") != remote_url
        ):
            raise SyncError(f"publication journal {journal_path} does not match receipt")
    else:
        journal = {
            "schema_version": 2,
            "receipt_sha256": receipt_hash,
            "remote_url": remote_url,
            "refs": refs,
            "results": {},
            "state": "prepared",
        }
        atomic_json(journal_path, journal)

    try:
        configure_remote(connection, remote_url)
    except (sqlite3.Error, SyncError) as exc:
        journal["state"] = "failed"
        journal["last_error"] = str(exc)
        journal["updated_at"] = utc_now()
        atomic_json(journal_path, journal)
        raise SyncError(f"publication remote configuration failed: {exc}") from exc
    for branch in push_order:
        journal["state"] = f"pushing:{branch}"
        journal["updated_at"] = utc_now()
        atomic_json(journal_path, journal)
        try:
            journal["results"][branch] = push_reference(connection, branch)
        except sqlite3.Error as exc:
            journal["state"] = "partial" if journal["results"] else "failed"
            journal["last_error"] = str(exc)
            journal["updated_at"] = utc_now()
            atomic_json(journal_path, journal)
            raise SyncError(f"publication stopped at {branch}; recover by rerunning --push: {exc}") from exc
        journal["state"] = "partial"
        journal.pop("last_error", None)
        journal["updated_at"] = utc_now()
        atomic_json(journal_path, journal)

    journal["state"] = "verifying"
    journal["updated_at"] = utc_now()
    atomic_json(journal_path, journal)
    try:
        verify_remote_refs(remote_url, refs, run_branch, expected_parent)
    except (sqlite3.Error, SyncError) as exc:
        journal["state"] = "pushed-unverified"
        journal["last_error"] = str(exc)
        journal["updated_at"] = utc_now()
        atomic_json(journal_path, journal)
        raise SyncError(f"refs pushed but clean-clone verification failed; rerun --push: {exc}") from exc
    journal["state"] = "complete"
    journal["verified_at"] = utc_now()
    journal["updated_at"] = journal["verified_at"]
    journal.pop("last_error", None)
    atomic_json(journal_path, journal)
    return journal


def sync_database(
    source: Path,
    target: Path,
    receipt_dir: Path,
    *,
    allowlist: frozenset[str] | None = None,
    schema_baseline: Path = SCHEMA_BASELINE_DEFAULT,
    source_receipt: Path | None = None,
    approve_schema_drift: bool = False,
    allow_run19_bootstrap: bool = False,
    allow_untracked_source_receipt: bool = False,
    remote_url: str | None = None,
    push: bool = False,
) -> dict[str, Any]:
    allowlist = allowlist or load_literal_set(CANONICAL_EXPORTER, "EXPORT_ALLOWLIST")
    configured_remote = remote_url or DEFAULT_REMOTE
    validate_remote_url(configured_remote)
    with process_lock(target):
        with tempfile.TemporaryDirectory(prefix="freshie-doltlite-") as directory:
            snapshot = Path(directory) / "inventory.snapshot.sqlite"
            snapshot_sqlite(source, snapshot)
            source_hash = file_sha256(snapshot)
            source_connection = stock_connection(snapshot)
            try:
                tables = gate_membership(source_tables(source_connection, "main"), allowlist)
                if schema_baseline.is_file():
                    gate_publication_denominator(tables, allowlist, schema_baseline)
                run_id = latest_run_id(source_connection, "main")
                canonical_safety_gate(snapshot, run_id)
                gate_supported_schema(source_connection, "main")
                gate_secret_values(source_connection, "main", tables)
                schema_manifest = schema_baseline_payload(source_connection, "main", tables, allowlist)
                schema_baseline_hash = gate_schema_baseline(schema_manifest, schema_baseline, approve_schema_drift)
                reviewed_table_receipts = source_table_receipts(source_connection, "main", tables)
            finally:
                source_connection.close()

            lineage = resolve_full_dolt_lineage(run_id)
            expected_lineage = {
                "repository": FULL_DOLT_REPOSITORY,
                "ref": f"run-{run_id}",
                "commit": lineage.get("commit"),
                "database_hash": lineage.get("database_hash"),
                "direct_parent": lineage.get("direct_parent"),
                "run_id": run_id,
                "verified_via": FULL_DOLT_API,
            }
            lineage_hashes = ("commit", "database_hash", "direct_parent")
            if lineage != expected_lineage or any(
                not HASH_RE.fullmatch(str(lineage.get(name, ""))) for name in lineage_hashes
            ):
                raise SyncError(f"lineage resolver returned unverified evidence: {lineage}")
            gate_tracked_full_dolt_receipt(run_id, str(lineage["commit"]))
            reviewed_source_receipt = source_receipt or receipt_dir / f"source-snapshot-run-{run_id}.json"
            source_receipt_hash = gate_source_snapshot_receipt(
                reviewed_source_receipt,
                artifact_name=source.name,
                backup_sha256=source_hash,
                run_id=run_id,
                lineage=lineage,
                schema_baseline_sha256=schema_baseline_hash,
                table_receipts=reviewed_table_receipts,
                allow_untracked=allow_untracked_source_receipt,
            )

            connection = sqlite3.connect(target)
            committed = False
            try:
                engine, version = verify_engine(connection)
                reset_to_main(connection)
                expected_parent = gate_target_ancestry(connection, run_id, allow_run19_bootstrap)
                connection.execute("ATTACH DATABASE ? AS source", (str(snapshot),))
                table_ddl, index_ddl = schema_objects(connection, "source", tables)
                current_branch = connection.execute(
                    "SELECT hash FROM dolt_branches WHERE name=?", (f"run-{run_id}",)
                ).fetchone()
                # An immutable run rerun is verification-only. If its source
                # changed, parity fails without creating a stranded local commit.
                if not current_branch:
                    replace_tables(connection, tables, table_ddl, index_ddl)
                table_receipts = parity_receipts(connection, tables, reviewed_table_receipts)
                full_dolt_commit = str(lineage["commit"])
                message = f"freshie doltlite sync: run {run_id}; full-dolt {full_dolt_commit}; sqlite {source_hash}"
                commit, committed = commit_if_changed(connection, message)
                verify_commit_binding(connection, commit, run_id, full_dolt_commit)
                run_branch = protect_run_branch(connection, run_id, commit)
                verify_commit_parent(connection, run_branch, expected_parent)
                database_hash = str(connection.execute("SELECT dolt_hashof_db('HEAD')").fetchone()[0])
                commit_date = str(
                    connection.execute("SELECT date FROM dolt_log WHERE commit_hash=?", (commit,)).fetchone()[0]
                )
                receipt_path = receipt_dir / f"doltlite-run-{run_id}.json"
                journal_path = receipt_dir / f"doltlite-run-{run_id}.publication.json"
                required_refs = {run_branch: commit, "main": commit}
                if expected_parent is not None:
                    required_refs[f"run-{run_id - 1}"] = expected_parent
                payload = {
                    "schema_version": 3,
                    "generated_at": commit_date,
                    "source": {
                        "artifact_name": source.name,
                        "backup_sha256": source_hash,
                        "run_id": run_id,
                        "full_dolt": lineage,
                        "reviewed_receipt": reviewed_source_receipt.name,
                        "reviewed_receipt_sha256": source_receipt_hash,
                        "table_receipts_sha256": json_sha256(reviewed_table_receipts),
                    },
                    "schema_baseline_sha256": schema_baseline_hash,
                    "history": {
                        "bootstrap_run": run_id if run_id == 19 and expected_parent is None else None,
                        "parent_commit": expected_parent,
                    },
                    "doltlite": {
                        "python_package_version": getattr(doltlite, "__version__", None),
                        "engine": engine,
                        "engine_version": version,
                        "commit": commit,
                        "commit_date": commit_date,
                        "database_hash": database_hash,
                        "run_branch": run_branch,
                        "remote_url": configured_remote,
                    },
                    "publication": {
                        "journal": journal_path.name,
                        "required_refs": required_refs,
                    },
                    "tables": table_receipts,
                }
                receipt_hash = immutable_receipt(receipt_path, payload)
                journal = None
                if push:
                    journal = publication_journal(
                        connection,
                        configured_remote,
                        run_branch,
                        commit,
                        journal_path,
                        receipt_hash,
                        expected_parent,
                    )
                result = dict(payload)
                result["receipt_sha256"] = receipt_hash
                result["receipt"] = str(receipt_path)
                result["operation"] = {
                    "commit_created": committed,
                    "push_attempted": push,
                    "publication_state": journal["state"] if journal else "local",
                }
                return result
            except Exception:
                if not committed:
                    with contextlib.suppress(sqlite3.Error):
                        connection.execute("SELECT dolt_reset('--hard')").fetchone()
                raise
            finally:
                connection.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=SOURCE_DEFAULT)
    parser.add_argument("--target", type=Path, default=TARGET_DEFAULT)
    parser.add_argument("--receipt-dir", type=Path, default=RECEIPTS_DEFAULT)
    parser.add_argument("--schema-baseline", type=Path, default=SCHEMA_BASELINE_DEFAULT)
    parser.add_argument(
        "--source-receipt",
        type=Path,
        help="Committed, reviewed source-snapshot receipt (defaults to receipt-dir/source-snapshot-run-N.json)",
    )
    parser.add_argument(
        "--approve-schema-drift",
        action="store_true",
        help="Write a reviewed schema/column baseline before local mutation",
    )
    parser.add_argument(
        "--bootstrap-run-19",
        action="store_true",
        help="Allow run 19 as the reviewed DoltLite migration root",
    )
    parser.add_argument("--remote-url", help="Configure publication target")
    parser.add_argument(
        "--push",
        action="store_true",
        help="Journal, push predecessor/run-N/main, and verify with a clean clone",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = sync_database(
            args.db.resolve(),
            args.target.resolve(),
            args.receipt_dir.resolve(),
            schema_baseline=args.schema_baseline.resolve(),
            source_receipt=args.source_receipt.resolve() if args.source_receipt else None,
            approve_schema_drift=args.approve_schema_drift,
            allow_run19_bootstrap=args.bootstrap_run_19,
            remote_url=args.remote_url,
            push=args.push,
        )
    except (SyncError, sqlite3.Error, OSError, ValueError) as exc:
        print(f"[doltlite-sync] ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
