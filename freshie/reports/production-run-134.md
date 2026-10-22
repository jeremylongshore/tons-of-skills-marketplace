# Freshie production evidence: immutable run 134

Freshie runs on stock SQLite, versions its public inventory with full Dolt, and
publishes that history to DoltHub. A fresh public clone was restored into an
isolated SQLite database on 2026-10-22. The canonical exporter reproduced the
existing Dolt state with **no new commit**, including its NULLs, empty strings,
timestamps, floating-point values, and JSON payloads.

[Machine receipt](production-run-134.json) ·
[SQLite schema](production-run-134-schema.sql) ·
[Public production database](https://www.dolthub.com/repositories/jeremylongshore/freshie-inventory)

| Evidence | Value |
|---|---|
| Immutable tag | `run-134` |
| Dolt commit | `4t297tsals7ijsph4msv9h1ddfk0u41e` |
| Database hash | `n2b7c06cs8c2va70hnk72dhpsd42i2vl` |
| Direct parent / run 133 | `bov00qvmn4v08t28navdolq4sshrekhi` |
| Canonical runtime tables restored | 51 |
| Discovery records retained | 112, with maximum ID 134 |
| Current-run graded skills | 3,491 |
| Grade distribution | A 2,875; B 326; C 132; D 154; F 4 |
| Canonical export parity | 51 table counts, 6 REAL checksums, 3 per-row JSON byte checksums |
| Restore result | SQLite integrity `ok`; exporter `commit created: False` |
| Executed toolchain | Dolt 2.1.10; Python 3.12.3; stock SQLite 3.45.1 |

The public SQL API independently returned the same tag, direct parent, database
hash, and grade counts. Its raw query responses are retained in the receipt.
This proves a named historical revision; it does not describe whatever revision
happens to be latest when this document is read.

## A short demonstration

In a clone of the public database, query an immutable revision and its history:

```bash
dolt sql -q "SELECT grade, COUNT(*) AS skills FROM skill_compliance AS OF '4t297tsals7ijsph4msv9h1ddfk0u41e' WHERE run_id=134 GROUP BY grade ORDER BY grade;"
dolt sql -q "SELECT tag_name, tag_hash FROM dolt_tags WHERE tag_name IN ('run-133','run-134');"
dolt diff run-133 run-134 --stat
```

The SQL answers what the inventory looked like at that revision. The diff shows
what changed between runs. The committed run-delta receipt separates schema
changes, appended rows, and grade regressions. These are demonstrated full-Dolt
features, not claims that a DoltLite experiment powers production.

## Reproduce in an isolated directory

Requirements: the `dolt` and `sqlite3` CLIs, Python's standard-library `sqlite3`,
and a Dolt author identity configured for the canonical exporter. Run from this
Git repository's root. Keep the public clone and output database separate from
any active Freshie runtime. No public push occurs below.

```bash
export FRESHIE_PROOF_DIR="$(mktemp -d)"
mkdir "$FRESHIE_PROOF_DIR/dolt"
dolt clone --single-branch --branch main jeremylongshore/freshie-inventory "$FRESHIE_PROOF_DIR/dolt/freshie"
(cd "$FRESHIE_PROOF_DIR/dolt/freshie" && dolt checkout -b proof-run-134 run-134)
```

Restore only the 51 canonical tables, using the retained stock-SQLite schema.
The seven legacy J-Rig tables in public history are deliberately excluded from
the runtime. Explicit JSON objects preserve null-valued keys, unlike direct
`SELECT *` JSON output in the exercised Dolt CLI. Parameterized inserts preserve
NULL versus empty string; declared timestamps regain their ISO `T` separator.

```python
import json
import os
from pathlib import Path
import sqlite3
import subprocess

proof = Path(os.environ['FRESHIE_PROOF_DIR'])
revision = '4t297tsals7ijsph4msv9h1ddfk0u41e'
destination = proof / 'inventory.sqlite'
# Exclusive creation refuses an existing output, including a symlink.
with destination.open('xb'):
    pass
connection = sqlite3.connect(destination)
connection.executescript(Path('freshie/reports/production-run-134-schema.sql').read_text())
tables = [row[0] for row in connection.execute(
    "SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
)]
assert len(tables) == 51

def query(sql):
    raw = subprocess.check_output(
        ['dolt', 'sql', '-r', 'json', '-q', sql], cwd=proof / 'dolt/freshie'
    )
    return json.loads(raw).get('rows', [])

for table in tables:
    columns = connection.execute(f'PRAGMA table_info("{table}")').fetchall()
    names = [column[1] for column in columns]
    timestamps = {column[1] for column in columns if column[2].upper() == 'TIMESTAMP'}
    projection = ','.join(f"'{name}',`{name}`" for name in names)
    expected = query(f"SELECT COUNT(*) AS n FROM `{table}` AS OF '{revision}'")[0]['n']
    rows = query(f"SELECT JSON_OBJECT({projection}) AS restored_row FROM `{table}` AS OF '{revision}'")
    assert len(rows) == expected, table
    values = []
    for record in rows:
        row = record['restored_row']
        assert set(row) == set(names), table
        for name in timestamps:
            if isinstance(row[name], str):
                row[name] = row[name].replace(' ', 'T', 1)
        values.append(tuple(row[name] for name in names))
    placeholders = ','.join('?' for _ in names)
    connection.executemany(f'INSERT INTO "{table}" VALUES ({placeholders})', values)
    connection.commit()
    assert connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] == expected
    print(table, expected, flush=True)
assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
assert connection.execute('SELECT MAX(id) FROM discovery_runs').fetchone()[0] == 134
connection.close()
```

Then exercise the sole canonical exporter against that isolated clone:

```bash
python3 freshie/scripts/dolt-sync.py \
  --db "$FRESHIE_PROOF_DIR/inventory.sqlite" \
  --dolt-dir "$FRESHIE_PROOF_DIR/dolt/freshie" \
  --repo-root "$PWD" \
  --grades-csv "$FRESHIE_PROOF_DIR/grades.csv" \
  --grade-histogram "$FRESHIE_PROOF_DIR/grade-histogram.json" \
  --reports-dir "$FRESHIE_PROOF_DIR/reports" \
  --no-push
```

Require every parity gate to pass, `commit created: False`, tag `run-134`, and
histogram `dolt_commit` equal to the immutable hash above. A new commit or a
failed gate is a failed reproduction, even if some row counts match. The
exporter's temporary reset/clean operations act only on this disposable clone.
A failed restore leaves its own output for diagnosis; retry in a new proof
directory rather than overwriting any database.

## Limits and the shadow experiment

The recorded SQLite backup SHA identifies the retained local recovery file.
SQLite page layouts can differ in another logically identical reconstruction;
the canonical no-diff export is the cross-engine proof. No database binary,
credentials, or personal runtime state is committed with this evidence.

At the time of this proof, DoltLite was an optional non-production experiment.
That publisher is now [retired](../README.md#retired-shadow-experiment); the
immutable JSON receipt retains its original historical wording. This demonstration did
not create a DoltLite sidecar, register DoltLite credentials, or publish a
DoltLite repository. Freshie's production full-Dolt history remains authoritative.
