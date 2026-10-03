# dolt-mcp-vcs

**One plugin for every make and model of Dolt.** Point it at any workspace and it answers the
first question that matters — *what kind of Dolt database am I working with?* — then does the
work: version-control verbs (branch / merge / diff / log / `AS OF` / data-PR awareness) over
the [`dolthub/dolt-mcp`](https://github.com/dolthub/dolt-mcp) server, with a verb-class
mutation gate that keeps destructive operations recommend-only.

> **Formerly `beads-dolt`** — same plugin, renamed to its Dolt-first identity. The rename is
> **non-breaking**: the GitHub repo URL redirects, the `beads-dolt` marketplace install slug
> still resolves (a deprecated catalog alias), and `/beads-dolt` is still an accepted trigger.
> The [beads (`bd`) task tracker](https://github.com/gastownhall/beads) ships as **use-case
> adapter #1**.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U5S225PTME)

## Why this exists

The Dolt ecosystem is no longer one product. There is classic **Dolt** (MySQL wire, GA),
**Doltgres** (Postgres wire), **DoltLite** (an embeddable SQLite fork with a prolly-tree
engine, alpha), and **DumboDB** (a Mongo-wire experiment on Dolt's storage engine) — and a
single machine routinely hosts several *modes* of the same flavor at once: classic `.dolt/`
repos, live `dolt sql-server` processes (which bind **ephemeral ports that differ from
config.yaml**), and embedded single-writer stores owned by another tool. Every existing
integration assumes you already know which of these you have and hand-writes the connection
config to match.

This plugin removes that assumption. **Detection is Step 0**: a stdlib-only detector
(`scripts/dolt-detect.py`) probes the directory layout, the process table (reading the
*actual* bound port from `/proc`, never a config file), file headers, and the wire — and
returns ranked findings, each one a ready-to-use connection descriptor. What it cannot
confirm it reports as unconfirmed; what it does not find it names as "not a Dolt database"
with the list of what was checked. Nothing is guessed.

## The detection contract

| flavor | mode | Detected by | Do-work posture |
|---|---|---|---|
| `dolt` | `repo` | `.dolt/` directory (classic repo layout) | full CLI verbs (log/diff/branch/`AS OF`) |
| `dolt` | `server` | live `dolt sql-server` (cwd-matched, **actual bound port via `/proc`** — never config.yaml), or a MySQL-wire greeting cross-checked against live processes | MySQL wire via the pinned `dolt-mcp-server` |
| `dolt` | `embedded` | `.beads/embeddeddolt/<p>/.dolt` layout or `.beads/metadata.json` `dolt_mode:"embedded"` | **read-only** CLI verbs — the single-writer `.lock` is owned by the embedding tool (e.g. `bd`); mutation refused with the reason |
| `doltgres` | `server` | Postgres-wire / version signature containing `Doltgres` | Postgres wire via `--doltgres` (derived from the descriptor — never hardcoded) |
| `doltlite` | `file` | single-file DB whose header carries the chunk-store magic `b"CTLD"` (LE `0x444C5443`, verified against [`dolthub/doltlite`](https://github.com/dolthub/doltlite) `src/chunk_store.h`); plain-SQLite headers are noted, **not** claimed | detect + report; local `doltlite` CLI verbs; alpha ⇒ read-only; no wire (decision 6) |
| `dumbo` | `server` | `dumbo` process / Mongo-wire version string containing `Dumbo` | detect + report only (experimental, fail-closed) |
| *(none)* | — | nothing matched | honest negative + what was checked |

Mixed layouts (a workspace with **both** `.beads/dolt/` and `.beads/embeddeddolt/` — migrated
state) return **both** findings, ranked live-server > repo > embedded > file. A plain-SQLite
runtime file paired with a `dolt/` system-of-record sidecar (the DoltLite-shaped pattern) is
recorded as evidence on the repo finding.

Detection output **is** a connection descriptor (`flavor`/`mode`/`endpoint`/`database`/
`creds-ref`/`maturity`), so it composes with everything downstream with zero hand-written
config:

```bash
python3 scripts/dolt-detect.py                          # what am I looking at? (read-only)
python3 scripts/dolt-detect.py --json                   # machine-readable findings + evidence
python3 scripts/dolt-detect.py --emit-descriptor        # write connection.descriptor.json
python3 scripts/dolt-mcp-client.py \
    --descriptor connection.descriptor.json list_databases   # connect — flavor honored
```

## What's in the plugin

- **A skill** (`/dolt-mcp-vcs`, also `/beads-dolt`) — Step 0 detection, then routed work:
  DoltHub visibility diagnosis (the near-universal cause is *no remote configured*), the
  `bd dolt remote add` + push fix, the JSONL throttle/export model, and dispatch to the
  agents below.
- **Expert agents** — grounded in a live-fetched (never frozen) reference of Dolt internals
  (`references/dolt-internals.md`):
  - `dolt-sync-advisor` — DoltHub remotes, `bd dolt push`/`pull`, backup vs push, federation, drift.
  - `bead-epic-auditor` — subtree/epic-closure audits (which epics have all children closed).
  - `bead-dependency-mapper` — dependency graphs, cycles, critical path (SQL via the Dolt MCP).
  - `bead-recovery-specialist` — rapid-write-race recovery, embedded↔server mode migration, dolt-server incidents.
  - `beads-guru` — general bd/Dolt expertise and the three-layer mirror discipline.
- **A wired Dolt MCP server** (`.mcp.json`) — the official
  [`dolthub/dolt-mcp`](https://github.com/dolthub/dolt-mcp) server (a ~40-tool
  version-control surface — fetch the exact list live, never freeze it), least-privilege
  wired.
- **The safety layer** — `scripts/dolt-mcp-guard.py`, the plugin's MCP **entrypoint**: a
  stdio proxy that wraps `dolt-mcp-server` and enforces the mutation posture ON the wire.
  Destructive tools (push / pull / both merges / `reset --hard` / branch-delete /
  `DROP DATABASE`) are refused before they reach the server and filtered out of
  `tools/list`; every `query`/`exec` passes the verb-class statement classifier
  (`scripts/sql_classifier.py`); safe-write SQL through `exec` additionally requires
  `DOLT_MCP_ALLOW_MUTATION=1`. (Until 2026-08-19 this posture was enforced only on the
  `dolt-mcp-client.py` path — a bare `dolt-mcp-server` registration exposed the
  destructive verbs ungated. Register through the guard; see § Wire the MCP server.)

## Declared mutation posture

- **Reads** execute freely.
- **Safe writes** (INSERT/UPDATE/DELETE …) require an explicit `--allow-mutation`, a
  non-`main` agent branch, and a GA/beta flavor maturity.
- **History-affecting statements** (push / merge / `reset --hard` / branch-delete /
  `DROP DATABASE` / unknown `CALL`) are **always refused** — recommend-only. Enforced at
  BOTH boundaries: the client path (`dolt-mcp-client.py`) and the MCP wire itself
  (`dolt-mcp-guard.py`); proven by `tests/test_dolt_mcp_guard.py`, which drives the guard
  over real JSON-RPC.
- **Pre-GA flavors** (`doltlite` alpha, `dumbo` experimental) are held read-only by the
  maturity gate and have **no wired connection** (fail-closed descriptor stubs, decision 6).
- **Embedded stores** are never written — the single-writer lock belongs to the embedding
  tool.
- The detector itself is **read-only**: it never starts, stops, or writes to any database.

## Install

Any consumer, no estate-specific assumptions:

1. **The plugin** — install `dolt-mcp-vcs` from the marketplace (the `beads-dolt` slug still
   resolves), or clone this repo into your plugins directory.
2. **The MCP server binary** (needed for wire work only — detection and CLI-verb work run
   without it), **pinned** — never `@latest`:
   ```bash
   go install github.com/dolthub/dolt-mcp/mcp/cmd/dolt-mcp-server@v0.3.6   # native (Go)
   # or
   docker pull dolthub/dolt-mcp:v0.3.6                                     # container
   # or grab the v0.3.6 release binary from https://github.com/dolthub/dolt-mcp/releases
   ```
   Pinned module `github.com/dolthub/dolt-mcp v0.3.6` verifies against the Go checksum
   database as `h1:uwjh1zf0er51VBT6uY3tI7JLj5pYxWyk9uB6CYQOhfU=`. A version bump is proposed
   by the `dolt-watch` routine and reviewed — never auto-trusted.
3. **Wire the MCP server THROUGH THE GUARD** — never register the bare binary (that
   exposes drop_database/reset-hard/push as ungated live tools):
   ```json
   "dolt-mcp-vcs": {
     "command": "python3",
     "args": ["<plugin>/scripts/dolt-mcp-guard.py", "--",
              "dolt-mcp-server", "--stdio", "--dolt",
              "--host", "127.0.0.1", "--port", "3308",
              "--user", "root", "--database", "beads"]
   }
   ```
4. **Detect** — `python3 scripts/dolt-detect.py` (stdlib-only; no other dependency).
5. **For the beads adapter**: [`bd`](https://github.com/gastownhall/beads) ≥ 1.0.4 with a
   Dolt-backed workspace.

## Configuration

Zero config is the default path: `dolt-detect.py --emit-descriptor` writes
`connection.descriptor.json` and every downstream tool honors it. Environment overrides
remain available:

| Env var | Default | Notes |
|---|---|---|
| `DOLT_HOST` | `127.0.0.1` | Dolt servers here are loopback-bound. |
| `DOLT_PORT` | `3308` | Prefer the detector: live servers bind ephemeral ports that differ from config.yaml. |
| `DOLT_USER` | `root` | bd's default. |
| `DOLT_DATABASE` | `beads` | Your workspace's database name. |
| `DOLT_PASSWORD` | _(empty)_ | Resolved via `creds-ref` pointers (`env:`/`sops:`/`pass:`) — never a literal in config. |
| `DOLT_FLAVOR` | `dolt` | Or let `--descriptor` supply it. |

### Authentication

DoltHub pushes authenticate with a dolt creds keypair (`dolt login`), or
`DOLT_REMOTE_USER`/`DOLT_REMOTE_PASSWORD`. The MCP connection uses `DOLT_USER`/`DOLT_PASSWORD`
(bd's local server is unauthenticated by default — user `root`, empty password).

## Built on

- **[Dolt](https://github.com/dolthub/dolt) / [DoltHub](https://www.dolthub.com)** — the
  version-controlled SQL database family: [Doltgres](https://github.com/dolthub/doltgresql),
  [DoltLite](https://github.com/dolthub/doltlite), DumboDB. The MCP server is
  [`dolthub/dolt-mcp`](https://github.com/dolthub/dolt-mcp).
- **[beads](https://github.com/gastownhall/beads)** — the `bd` task tracker (use-case
  adapter #1).

## How it was evaluated

This plugin was run end-to-end through the [Intent Eval Platform](https://github.com/jeremylongshore/intent-eval-lab) — deterministic gates → behavioral eval (real model) → kernel-validated Evidence Bundle → ship/no-ship decision. The full evidence and the ship/no-ship decision are recorded in [`DOGFOOD.md`](./DOGFOOD.md); the methodology write-up is the platform's [case study](https://github.com/jeremylongshore/intent-eval-lab/blob/main/000-docs/088-RR-LAND-beads-dolt-external-adopter-convergence-proof-2026-06-20.md). (The eval even surfaced — and we fixed — a bug in the platform's own evidence emitter.)

## License

Apache-2.0. See [LICENSE](./LICENSE).
