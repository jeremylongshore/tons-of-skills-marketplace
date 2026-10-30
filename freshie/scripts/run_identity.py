"""Read-only Freshie run-lineage preflight; never creates or repairs authority.

Discovery identities, rather than contiguous run numbers, bind an inventory to
its committed history. Compliance tables may legitimately change for the latest
discovery run. Historical tag repair is deliberately outside this module.
"""

from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = (
    "id",
    "run_date",
    "commit_hash",
    "total_packs",
    "total_plugins",
    "total_skills",
    "total_files",
    "total_root_files",
)
HASH = re.compile(r"[0-9a-v]{32}\Z")
TAG = re.compile(r"run-(0|[1-9][0-9]*)(?:\.([1-9][0-9]*))?\Z")


class IdentityError(RuntimeError):
    """Authority is missing, malformed, unavailable, or contradicts the source."""


def integer(value, label: str, minimum: int = 0) -> int:
    # DoltHub represents BIGINTs as strings; accept only canonical decimals.
    if isinstance(value, str) and re.fullmatch(r"0|[1-9][0-9]*", value):
        value = int(value)
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise IdentityError(f"invalid {label}: {value!r}")
    return value


def histories(rows: list[dict]) -> dict[int, tuple]:
    if not isinstance(rows, list):
        raise IdentityError("discovery history must be a list")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != set(COLUMNS):
            raise IdentityError("discovery history has missing or unexpected fields")
        run = integer(row["id"], "discovery run id", 1)
        if run in result:
            raise IdentityError(f"duplicate discovery run {run}")
        date = row["run_date"]
        commit = row["commit_hash"]
        if not isinstance(date, str) or not isinstance(commit, str) or not commit.strip():
            raise IdentityError(f"missing discovery identity for run {run}")
        try:
            # SQLite ISO timestamps and Dolt DATETIME render differently.
            date = datetime.fromisoformat(date.replace("Z", "+00:00"))
            if date.tzinfo is None:
                date = date.replace(tzinfo=timezone.utc)
            date = date.astimezone(timezone.utc).isoformat()
        except ValueError as exc:
            raise IdentityError(f"invalid discovery timestamp for run {run}") from exc
        totals = tuple(None if row[c] is None else integer(row[c], c) for c in COLUMNS[3:])
        result[run] = (date, commit, *totals)
    return result


def tag_map(rows: list[dict]) -> dict[str, str]:
    if not isinstance(rows, list):
        raise IdentityError("tag authority must be a list")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"tag_name", "tag_hash"}:
            raise IdentityError("tag authority has missing or unexpected fields")
        name, target = row["tag_name"], row["tag_hash"]
        if not isinstance(name, str) or not TAG.fullmatch(name):
            raise IdentityError(f"invalid authoritative run tag {name!r}")
        if not isinstance(target, str) or not HASH.fullmatch(target) or name in result:
            raise IdentityError(f"invalid or duplicate authoritative tag {name!r}")
        result[name] = target
    return result


def dolt_rows(repo: Path, sql: str) -> list[dict]:
    try:
        proc = subprocess.run(
            ["dolt", "sql", "-r", "json", "-q", sql],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        rows = json.loads(proc.stdout)["rows"]
        if not isinstance(rows, list):
            raise ValueError("rows must be a list")
        return rows
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError) as exc:
        raise IdentityError(f"cannot read committed Dolt authority at {repo}: {exc}") from exc


def discovery_query(ref: str) -> str:
    if not HASH.fullmatch(ref):
        raise IdentityError("invalid authority commit hash")
    # Explicit JSON_OBJECT keeps NULL fields (Dolt's ordinary JSON rows omit them).
    fields = ",".join(f"'{c}',`{c}`" for c in COLUMNS)
    return f"SELECT JSON_OBJECT({fields}) AS record FROM discovery_runs AS OF '{ref}' ORDER BY id"


def decode_history(rows: list[dict]) -> dict[int, tuple]:
    try:
        decoded = [json.loads(r["record"]) if isinstance(r["record"], str) else r["record"] for r in rows]
    except (KeyError, TypeError, ValueError) as exc:
        raise IdentityError("malformed discovery authority response") from exc
    return histories(decoded)


def local_authority(repo: Path) -> dict | None:
    if not (repo / ".dolt").exists():
        return None
    if (repo / ".dolt" / "sql-server.lock").exists():
        raise IdentityError(f"Dolt sql-server holds authority open: {repo}; retry when it is idle")
    head_rows = dolt_rows(repo, "SELECT commit_hash FROM dolt_log LIMIT 1")
    if (
        len(head_rows) != 1
        or not isinstance(head_rows[0], dict)
        or not HASH.fullmatch(str(head_rows[0].get("commit_hash", "")))
    ):
        raise IdentityError("missing or malformed committed Dolt HEAD")
    head = head_rows[0]["commit_hash"]
    tags = tag_map(dolt_rows(repo, "SELECT tag_name,tag_hash FROM dolt_tags"))
    tables = dolt_rows(repo, f"SHOW TABLES AS OF '{head}'")
    if any(not isinstance(row, dict) for row in tables):
        raise IdentityError("malformed committed table inventory")
    has_discovery = any("discovery_runs" in row.values() for row in tables)
    if not has_discovery and tags:
        raise IdentityError("run tags exist without committed discovery history")
    records = decode_history(dolt_rows(repo, discovery_query(head))) if has_discovery else {}
    return {"head": head, "tags": tags, "records": records}


def remote_rows(org: str, repo: str, ref: str, sql: str) -> list[dict]:
    path = "/".join(urllib.parse.quote(v, safe="") for v in (org, repo, ref))
    url = "https://www.dolthub.com/api/v1alpha1/" + path + "?" + urllib.parse.urlencode({"q": sql})
    try:
        # Public authority queries can exceed 20s on a cold DoltHub revision.
        # Bound the wait without treating a timeout as missing/empty history.
        with urllib.request.urlopen(url, timeout=60) as response:
            payload = json.load(response)
        if not isinstance(payload, dict) or payload.get("query_execution_status") != "Success":
            raise ValueError("remote authority query did not succeed")
        rows = payload["rows"]
        if not isinstance(rows, list):
            raise ValueError("remote authority rows missing")
        return rows
    except (OSError, urllib.error.URLError, ValueError, KeyError, TypeError) as exc:
        raise IdentityError(f"cannot verify public Freshie authority for {org}/{repo}: {exc}") from exc


def remote_authority(org: str, repo: str) -> dict:
    heads = remote_rows(org, repo, "main", "SELECT commit_hash FROM dolt_log LIMIT 1")
    if len(heads) != 1 or not isinstance(heads[0], dict) or not HASH.fullmatch(str(heads[0].get("commit_hash", ""))):
        raise IdentityError("missing or malformed public HEAD")
    head = heads[0]["commit_hash"]
    # DoltHub's HTTP ref segment accepts named refs, not commit hashes. Bind
    # the census in SQL AS OF while sending the request through named main.
    records = decode_history(remote_rows(org, repo, "main", discovery_query(head)))
    tags = tag_map(remote_rows(org, repo, "main", "SELECT tag_name,tag_hash FROM dolt_tags"))
    return {"head": head, "tags": tags, "records": records}


def sqlite_history(db: Path) -> dict[int, tuple]:
    if not db.exists():
        return {}
    try:
        with sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            if not conn.execute("SELECT 1 FROM sqlite_schema WHERE name='discovery_runs' AND type='table'").fetchone():
                return {}
            rows = [dict(row) for row in conn.execute("SELECT " + ",".join(COLUMNS) + " FROM discovery_runs")]
    except sqlite3.Error as exc:
        raise IdentityError(f"cannot read SQLite discovery history: {exc}") from exc
    return histories(rows)


def require_lineage(source: dict[int, tuple], authority: dict[int, tuple]) -> None:
    for run, identity in authority.items():
        if source.get(run) != identity:
            raise IdentityError(f"SQLite discovery history is missing or differs from authoritative run {run}")
    floor = max(authority, default=0)
    if any(run <= floor and run not in authority for run in source):
        raise IdentityError("SQLite introduces an unrecognized historical discovery run")


def tag_floor(tags: dict[str, str]) -> int:
    return max((int(TAG.fullmatch(name)[1]) for name in tags), default=0)


def require_tag_agreement(local: dict[str, str], remote: dict[str, str]) -> None:
    for name, target in remote.items():
        if local.get(name) != target:
            raise IdentityError(f"local/public tag mapping differs or is missing: {name}; restore verified authority")


def established_receipt(histogram: Path) -> bool:
    if not histogram.exists():
        return False
    try:
        payload = json.loads(histogram.read_text())
        run = integer(payload["run_id"], "grade receipt run")
        return run > 0 or bool(payload.get("dolt_commit"))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise IdentityError(f"cannot verify established grade receipt {histogram}") from exc


def preflight(
    db: Path,
    dolt_dir: Path,
    histogram: Path,
    *,
    rebuild=False,
    requested_run=None,
    public: tuple[str, str] | None = None,
) -> dict[int, tuple]:
    """Check existing history without opening any writable database or making refs.

    Offline bootstrap is allowed only where neither committed history nor an
    established grade receipt exists. Public exports additionally verify remote
    authority; no-push historical restores use their selected local authority.
    """
    source = sqlite_history(db)
    local = local_authority(dolt_dir)
    records = local["records"] if local else {}
    tags = local["tags"] if local else {}
    if not records and established_receipt(histogram):
        raise IdentityError(
            f"established grade receipt but no committed discovery authority at {dolt_dir}; "
            "restore verified history or select --dolt-dir explicitly"
        )
    require_lineage(source, records)
    floor = max(max(records, default=0), tag_floor(tags))
    if public is not None:
        remote = remote_authority(*public)
        require_lineage(records, remote["records"])
        require_tag_agreement(tags, remote["tags"])
        require_lineage(source, remote["records"])
        if local is None or not dolt_rows(
            dolt_dir, f"SELECT commit_hash FROM dolt_log WHERE commit_hash='{remote['head']}'"
        ):
            raise IdentityError("public HEAD is not in local committed ancestry; restore verified history")
        floor = max(floor, max(remote["records"], default=0), tag_floor(remote["tags"]))
    latest = max(source, default=0)
    if rebuild:
        if requested_run is None and latest and source[latest][-3:-1] == (None, None):
            # Rebuild purges a crashed incomplete newest run. Never purge a
            # committed run, even if that historical record has NULL totals.
            if latest <= floor:
                raise IdentityError("refusing to purge an authoritative incomplete discovery run")
            latest = max((run for run in source if run != latest), default=0)
        candidate = integer(requested_run, "requested run id", 1) if requested_run is not None else latest + 1
        if candidate <= floor:
            raise IdentityError(f"rebuild run {candidate} must exceed authoritative run floor {floor}")
    elif latest < max(records, default=0):
        raise IdentityError("source run precedes committed authority")
    elif latest <= floor and latest != max(records, default=0):
        raise IdentityError(f"source run {latest} collides with authoritative run floor {floor}")
    elif public is not None and latest < floor:
        raise IdentityError(f"public export run {latest} precedes authoritative run floor {floor}")
    return source


def verify_snapshot(snapshot: Path, approved_history: dict[int, tuple]) -> None:
    """Bind the actual export input to the source identity approved pre-write."""
    if sqlite_history(snapshot) != approved_history:
        raise IdentityError("discovery history changed after preflight; refusing unapproved export snapshot")
