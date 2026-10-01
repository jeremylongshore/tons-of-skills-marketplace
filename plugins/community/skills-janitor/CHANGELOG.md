# Changelog

## v1.8.0 (2026-09-30)

Final feature release: the project moves to maintenance mode. Claude Code now covers the core use case natively: `/skill-doctor` (per-skill context cost and usage, never-invoked skills), `/doctor` (unused skills, MCP servers and plugins against their context cost, with fixes) and `/doctor prompt-audit` (outdated or conflicting instructions in CLAUDE.md, skills, agents and commands). If you only use Claude Code and only want to trim context, use those.

The janitor stays for what still isn't built in: the security scan, the pre-install check, duplicate detection, Codex support and hard deletes. Bug fixes and PRs are still welcome.

### Fixed

Both contributed by [@jerryhuangzq-lang](https://github.com/jerryhuangzq-lang) (#9). Both logged `[FIXED]` and exited 0, so the damage only showed up in the written file.

- **`fix --apply` no longer corrupts block-scalar frontmatter.** The missing-`metadata.version` fix anchored on `^description:`, which also matches the `description: >` / `description: |` header, and spliced the new block straight after it. That ended the scalar early and left frontmatter that no longer parsed as YAML. The block is now inserted just before the closing `---` (LF and CRLF). When no closing delimiter is found, the file is left alone instead of reporting a fix that didn't happen.
- **`fix --apply` no longer writes through symlinked skill dirs.** The plugin guard only inspected the path string, so a symlink into a plugin marketplace clone, `~/.agents/skills` or a personal repo was followed and its target edited. Symlinked skills are now skipped with `[SKIP] name: symlink -> target - edit at source`.
- Regression tests for both (`blocky`, `victim`) in `tests/test_cli_regression.sh`. The block-scalar test asserts position as well as bytes, because the broken placement inserted the same two lines and would have passed a byte-identity check.

### Changed

- README leads with the maintenance-mode status and points to the built-in Claude Code commands.
- Marketplace description refreshed to match the GitHub About text.

## v1.7.1 (2026-08-11)

Patch release: SKILL.md frontmatter parsing is now robust across lint, scan, and fix on real-world collections — CRLF files, apostrophes, and every YAML block-scalar header form. All four fixes contributed by [@lulzpid](https://github.com/lulzpid) (#7), found by running the janitor over a ~440-skill collection. Two of the four were silent data loss; if you ever distrusted a lint report or lost a skill from the inventory, upgrade.

### Fixed

- **Descriptions with an odd number of apostrophes no longer report CRITICAL "Missing 'description' field".** Lint trimmed values through `xargs`, which parses shell quoting and aborts on `the user's` or `Don't`; the failure was swallowed into a phantom finding. Trimming now uses `sed` character classes — apostrophes are just characters.
- **Every YAML block-scalar header form is parsed** (`|`, `>`, with optional chomp indicator and indent digit: `|-`, `>+`, `>2`, `>-2`, …). `description: >-` — the most common form — was previously read as the literal two-character string `>-`, tripping "too short" and "doesn't explain when to trigger".
- **CRLF SKILL.md files no longer vanish from the scan inventory.** A Windows-authored skill's trailing CR split its TSV row under universal newlines and both halves were silently dropped. CRLF tolerance is layered end-to-end: delimiter scans match `^---\r?$`, values are CR-stripped at the point of reading, and the TSV reader pins `newline="\n"` as the last line of defense.
- **`fix --apply` no longer corrupts CRLF files.** The missing-opening-delimiter check compared the raw first line, so a valid `---\r` opener triggered the corrupting path: a duplicate `---` prepended and the real description overwritten with a placeholder. The check now compares CR-stripped; only intended fixes fire.

### Added

- **Regression test harness under `tests/`** — plain bash, no framework, green on macOS bash 3.2. Seam 1 runs the lint/scan/fix CLIs whole under a fixture `$HOME` pinning all four failure modes (including byte-identity after `fix --apply` on a CRLF file); seam 2 tests `extract_description` and the TSV reader per-function.
- **`scripts/tsv_reader.py`** — the scan module's TSV reader extracted into a standalone, importable helper (scan output unchanged).

## v1.7.0 (2026-07-20)

### MCP servers join the triage

- **`scripts/mcp.sh`** — inventories every configured MCP server (user `~/.claude.json`, per-project entries, project `.mcp.json`, plugin-bundled) and cross-references REAL usage from session transcripts (`mcp__server__tool` tool_use records). No invented token numbers — schemas live server-side, so the janitor reports calls, distinct tools used, and last-used. Servers seen in transcripts but no longer configured are listed separately.
- **Swipe deck includes MCP cards.** Unused connected servers rank high (their tool schemas load into context for nothing). Swiping one left removes the entry from its config file with a timestamped `.bak` backup — reversible. Plugin-bundled MCP servers are flagged for plugin review instead.

### Usage tracking got real

Skill usage now also counts actual `Skill` tool_use records from session transcripts — including skills Claude auto-triggered, which the slash-command history never sees. On a machine where the old heuristic found 1 active skill in 4 weeks, transcripts reveal 11.

### Notes

- Transcript scanning adds ~10-15s to `usage`/`value`/deck builds on large transcript trees (pre-filtered by grep and modification time).

## v1.6.0 (2026-07-15)

### `/janitor-security` — prompt-injection and malicious-pattern scan

New command that audits every installed skill (all scopes) for the shapes found in real-world malicious skills: instruction-override phrases ("ignore all previous instructions"), hide-from-the-user directives, instructions concealed in HTML comments or zero-width/bidi unicode, large decodable base64 blobs, and scripts that pipe the network into a shell, decode-and-execute, touch credential stores (`~/.ssh`, `~/.aws`, keychain), call URL shorteners or plain-HTTP endpoints, or upload variable data.

Verdicts are per-skill heuristics — PASS / REVIEW / RISK — with file + evidence for every finding. Calibrated for low noise: legitimate emoji ZWJ sequences, "secretly" as prose, and benign HTML comments don't trip it (on a real 178-skill machine: 2 flagged, both genuinely worth reading).

### Pre-install security in `/janitor-discover`

`precheck` now runs the same scan on the candidate: full-directory scan for local paths (including bundled scripts), fetched-SKILL.md scan for URLs (with an explicit note that scripts aren't fetched — re-check after cloning).

### Fixed

- `precheck` with a `github.com/.../tree/<branch>/<path>` URL computed the raw URL but never downloaded it, so every tree-style precheck failed with "Could not fetch SKILL.md" — a format the help text has advertised since v1.0.

## v1.5.1 (2026-07-11)

Docs-only release: every SKILL.md now follows the emerging marketplace schema (8 frontmatter fields incl. `allowed-tools`/`license`/`compatibility`, plus Overview/Prerequisites/Instructions/Output/Error Handling/Examples/Resources sections). All five skills grade A (93-94/100, 0 errors) on the tonsofskills marketplace validator. Operative instructions are unchanged; descriptions gained only an additive "Trigger with '/command'." sentence.

## v1.5.0 (2026-07-09)

### Honest token costs — always-loaded vs on-demand

Only skill **descriptions** sit permanently in the system prompt; the SKILL.md body loads when a skill triggers (progressive disclosure). Every cost view now reports both numbers separately instead of implying the whole file is context rent:

- `/janitor-value` table: `Always` (description tokens) and `Body` (on-trigger tokens) columns, with an "Always-loaded TOTAL (% of budget)" summary.
- Swipe cards: `Context 213 always · 5,431 on trigger`.
- JSON adds `desc_tokens` / `body_tokens` per skill and `always_loaded_tokens` / `always_pct` totals.

### Subagents are inventoried too

Agents in `~/.claude/agents` and `./.claude/agents` have always-loaded descriptions just like skills — often costing more. `scan.sh` emits an `agents` array and `/janitor-value` reports their always-loaded total.

### Plugin update detection

`scan.sh` plugins now carry `update_available` — the installed commit compared against the marketplace clone's HEAD. `/janitor-report` can tell you which plugins are stale.

### 7x faster scan

`scan.sh` renders the whole JSON in a single python3 pass instead of ~6 processes per skill (55s → ~8s on a 175-skill machine). Paths and all fields are now properly JSON-escaped.

### Fixed

- **`/janitor-fix --prune` never actually matched broken symlinks** — the `"$dir"/*/` glob only yields entries that resolve to directories. Prune now sees and removes them; broken symlinks also appear in the scan inventory, the fix pass, and lint (whose "broken symlink" CRITICAL was unreachable for the same glob reason).
- **`--prune` died silently when a default skills dir was missing** (bare `return` propagating status 1 under `set -e` — same class as the v1.4.1 `add_dir` bug; all five occurrences fixed).
- **Fix 2 (missing closing `---`) could swallow the whole body into frontmatter** when the body contained a column-0 `key:` line (e.g. `usage: run it like this`) — the insertion-point scan is now limited to the leading frontmatter run.
- **Agents/commands double-counted when running from `$HOME`** (`./.claude/agents` is the same directory as `~/.claude/agents`) — realpath dedup added, matching the skills side.
- **Folded/multiline YAML descriptions** (`description: >` / `|`) read as empty everywhere — new shared `extract_description` helper handles block scalars for skills AND agents, so their always-loaded tokens are counted and duplicate detection sees them.
- **Skills with an empty description broke the usage parser** (a stripped trailing tab collapsed the row into the legacy column shape, putting the filesystem path in the description and skipping dedup).
- **Two physical copies of the same skill name produced duplicate swipe cards pointing at one path** (the second copy was undeletable) — the deck now joins tokencost↔scan records by realpath.
- Swipe verdict labels no longer imply body tokens are permanent context cost ("Unused + heavy on trigger — prime delete candidate"), and the apply summary reports "frees X always-loaded + Y on-trigger" instead of a misleading % of context.
- The deck builder's default output is per-process (concurrent runs clobbered a fixed `/tmp` path).
- Duplicate rows in `/janitor-value` for one skill reachable from two roots (Claude + Codex symlink installs) — deduped by realpath, scopes merged.
- GitHub search results are relevance-gated (repo must carry a skill signal in name/description/topics) and ranked by relevance before stars — searching "n8n" no longer returns firecrawl.
- `precheck` with `GITHUB_TOKEN` sent a malformed Authorization header (quoting bug) — code search on private/rate-limited repos works now.
- GNU-only `\s` in lint's seds replaced with portable `[[:space:]]` (BSD sed treated it as a literal `s`).
- `fix.sh` changelog now lives in the plugin's own `data/` dir like every other tool (previously it fabricated `~/.claude/skills/skills-janitor/`, which looked like a skill).

### Removed

- The five v1.2 deprecated aliases (`janitor-audit`, `janitor-usage`, `janitor-tokens`, `janitor-search`, `janitor-precheck`) are gone, as announced. Use `/janitor-report --brief`, `/janitor-value`, `/janitor-discover`.

## v1.4.1 (2026-07-07)

Hotfix release. A deep-dive review found bugs that made v1.2–v1.4 silently broken on most machines. If any janitor command ever exited with no output at all — this is why. Upgrade.

### Fixed

- **Every script died silently on Claude-only installs.** `paths.sh`'s `add_dir` returned non-zero when a default directory was missing (e.g. no `~/.agents/skills` because you don't use Codex), and `set -e` killed the sourcing script before it printed anything. Affected every command since v1.2.0. Also fixed the empty-array-under-`set -u` crash (bash 3.2) for machines with no skill directories at all.
- **Usage tracking looked for conversation history at a non-standard path**, so on standard installs every skill was reported "never used" — which fed the swipe deck the wrong verdicts. History is now resolved from `$CLAUDE_CONFIG_DIR/history.jsonl`, `~/.claude/history.jsonl`, then `~/.claude-account-*/history.jsonl`; a missing file degrades gracefully instead of crashing the Python stage.
- **`/janitor-fix --apply` could corrupt SKILL.md files on macOS.** BSD `sed a\` glued inserted text onto the following line (`description: "..."---`, unclosed frontmatter), and the `name:`/`description:` matchers also hit example frontmatter in skill *bodies*. All frontmatter edits now use awk, anchored to the first match inside the frontmatter only.
- **Bare plugin-skill invocations now count.** `/janitor-audit` in your history is matched to `skills-janitor:janitor-audit`; previously only the fully-qualified form counted, so plugin skills you use daily showed `0×` in `/janitor-value` and the swipe deck.
- **Empty-body detection produced `0\n0`** (`grep -c … || echo 0`) which broke an arithmetic comparison — lint silently dropped its "very little body content" warning.

### Known issues (planned for v1.5)

- `usage.sh` doesn't dedupe skills reachable from two paths (symlinked Claude+Codex installs show duplicate rows).
- Token cost reports the full SKILL.md size; only the description is always-loaded (the body loads on demand). A split cost view is planned.

## v1.4.0 (2026-05-25)

### `/janitor-swipe` — Tinder for your Claude Code skills

A new bash TUI that puts every installed skill into a sorted deck and lets you swipe `keep` / `delete` / `skip` on each one. The deck is sorted "most likely waste first" so the cards you'd actually want to delete appear at the top — most users hit `←` a few times on the heavy-and-unused entries and quit before reviewing the whole list.

The killer ratio: on a typical machine, you can reclaim 30–40% of your skill token cost in under a minute of swiping.

### What you see

Each card shows skill name, position in deck, token cost (% of context budget), usage count and last invoked date, scope, 3-line description, and a verdict label like *"Heavy + unused — likely dead weight"*. The scoring formula prioritizes high-token + zero-usage + stale-last-use combinations.

Controls follow the obvious mappings: arrows or `hjkl` for left/right/down, `u` to undo, `i` to inspect the full description, `q` to quit.

### Honest about what it can delete

User-scope, project-scope, and Codex skills get staged for actual `rm -rf` on the swiped-left list. Plugin-namespaced skills (which can't be individually deleted — they belong to a plugin) get flagged in a separate "plugins to review" section with a hint to run `/plugin uninstall <plugin>` if you swiped delete on enough of its skills. Symlinks are unlinked, never followed.

### Apply screen

After the last card (or `q`), a summary screen shows keep/skip/delete counts, the actual deletion list with paths, the plugin review breakdown, and a prompt:

- `y` — apply deletions immediately, log to `~/.skills-janitor/log.jsonl`
- `N` — cancel, no changes
- `save` — write decisions to `~/.skills-janitor/swipe-<timestamp>.json`; apply later with `swipe.sh --apply <file>`

### Why you have to run it via `!`

The TUI needs an interactive terminal for `read -rsn1` keypress capture. Inside Claude Code, the Bash tool's stdin is non-interactive, so the script detects that and prints a friendly error. The intended invocation is:

```
!bash ~/.claude/skills/skills-janitor/scripts/swipe.sh
```

The `!` prefix routes the command through your real shell, where keypresses work.

### Implementation notes

- Pure bash + python3 (same dependency footprint as the rest of the project), no TUI library
- Bash 3 compatible (macOS default) — no associative arrays, all aggregation via tempfiles
- `set -euo pipefail` throughout, terminal state restored on any exit path
- Edge cases handled: no skills installed, terminal < 50 cols or < 22 rows, no TTY, Ctrl-C mid-swipe, save-and-resume across sessions

### v1.3 aliases still working

The five v1.2 deprecated aliases (`janitor-audit`, `janitor-usage`, `janitor-tokens`, `janitor-search`, `janitor-precheck`) are unchanged. They keep working through v1.4 and will be removed in v1.5.

## v1.3.0 (2026-05-22)

### Plugin skills are now visible

The single biggest correctness fix in this project's history. Through v1.2, Janitor could only see skills under `~/.claude/skills/` (and the Codex equivalent) — plugin-namespaced skills installed via `/plugin install` (e.g. `marketing-skills:image`, `figma:figma-use`, `vercel:nextjs`) were completely invisible to every command.

v1.3 walks the active install path of every entry in `~/.claude/plugins/installed_plugins.json` (and `~/.claude/sources/<source>/skills/` for source-loaded skills), dedups by realpath to avoid double-counting plugins installed at both user and project scope, and uses the active version only (not every cached version under `~/.claude/plugins/cache/`).

Real impact on a typical machine: scanned skill count jumped from 35 → 157, token cost reporting went from "9% of budget" to "123% of budget" (i.e. the user was over their context budget without knowing it).

Affects every command:
- **`scan.sh`** — emits `namespace` and `qualified_name` fields; plugin skills appear as `<plugin>:<skill>`.
- **`detect_dupes.sh`** — surfaces cross-scope user-vs-plugin overlaps (the situation where you installed the `marketing-skills` plugin AND have a redundant user-scope `marketing-seo-audit` copy).
- **`tokencost.sh`** — plugin skills now counted toward total context cost.
- **`usage.sh`** — matches `/marketing-skills:image` style invocations against namespaced skills.

### Commands consolidated 7 → 4

- **`/janitor-report`** (default = full check, `--brief` = inventory only) replaces both `/janitor-audit` and the v1.2 `/janitor-report`.
- **`/janitor-value`** replaces `/janitor-usage` + `/janitor-tokens` — combined view sorted by waste (heavy + unused first), which is the actually-useful question.
- **`/janitor-discover`** replaces `/janitor-search` + `/janitor-precheck` — dispatches by arg shape (keyword → search, URL/path → precheck).
- **`/janitor-fix`** unchanged.

The four removed commands keep working as deprecated aliases for one release; they print a one-line rename notice and delegate to the new equivalent. Aliases will be removed in v1.4.

### Also fixed
- **`scan.sh` no longer double-counts user skills as project skills when run from `$HOME`.** Realpath dedup matches the existing logic for Codex.
- **Plugin-scope label simplified to `"plugin"`** (was previously planned as `"plugin-marketplace"/"plugin-cache"`). Plugin install scope is a property of the plugin, not the skill.
- **`for_each_skill_dir` in `paths.sh` now iterates plugin and source dirs too**, with namespace passed as a 4th callback arg. All consumers (detect_dupes, tokencost, usage, precheck) pick up plugin coverage automatically.

### Migration

| v1.2 command | v1.3 equivalent |
|---|---|
| `/janitor-audit` | `/janitor-report --brief` |
| `/janitor-usage` | `/janitor-value` |
| `/janitor-tokens` | `/janitor-value` |
| `/janitor-search <kw>` | `/janitor-discover <kw>` |
| `/janitor-precheck <url>` | `/janitor-discover <url>` |

## v1.2.0 (2026-04-29)

### Fixed (correctness)
- **`fix.sh --apply` no longer corrupts modern skills.** The repair now recognizes nested `metadata.version` (the canonical layout used by `npx skills add`), not only top-level `version:`. Without this fix, `--apply` would have injected duplicate top-level `version:` lines into every skill that already had `metadata.version`. The repair itself now writes the canonical nested form (`metadata:\n  version: "1.0.0"`) via awk so the appended block doesn't collide with the closing `---` on BSD sed (macOS).
- **`scan.sh` emits valid JSON.** Self-skip of the top-level `skills-janitor` folder previously left a dangling comma (`}\n,\n,\n{`) that broke any JSON consumer. Comma emission moved inside `scan_skill` after the early-return check.
- **`scan.sh` parses `installed_plugins.json` v2 schema.** Claude Code v2 wraps plugins in `{"version": 2, "plugins": {key: [instances]}}`; the previous parser treated it as a flat array and silently produced `"plugins": []` on every modern install. Older flat-array shape kept as a fallback.
- **`detect_dupes.sh` no longer reports symlink shadows as 100% self-duplicates.** Skills resolved to the same `realpath` (e.g. `~/.claude/skills/foo` symlinking to `~/.agents/skills/foo`) are deduped before comparison, eliminating "[100%] foo <-> foo" entries with both scopes labeled `user`.
- **`tokencost.sh` no longer double-counts symlinked skills.** Same realpath dedup; total token cost drops to the actual physical file count.

### Added
- **`detect_dupes.sh` name-collision pass.** Two distinct skill folders with the same name living at different realpaths (the situation that confuses skill triggering) are now flagged in a dedicated section, regardless of description similarity. The previous Jaccard-only check missed exact-name collisions when descriptions diverged.

### Fixed (from prior unreleased)
- **Windows compatibility** - removed dead `/dev/stdin` open in `detect_dupes.sh` that caused `FileNotFoundError` on Windows (Git Bash/MSYS2). The code was a no-op (`pass` body) and the actual data is read via `$TMPFILE` env var.
- **lint: false-positive CRITICAL for support folders** - folders without `SKILL.md` (e.g. `_shared`, `_docs`, `_temp`, plugin subdirs) are now silently skipped instead of emitting a spurious CRITICAL.
- **lint: multiline description parsing** - description values using YAML block scalars (`|`, `>`) are now collected across all indented lines via `awk`, fixing false "description too short" warnings. Long-description threshold raised from 250 → 500 chars to match real-world multi-line descriptions.
- **lint: new check for `disable-model-invocation` skills** - skills that set `disable-model-invocation: true` with a very short description now emit a WARNING, since Claude may not trigger them correctly.

### Known limitations (deferred to v1.3.0)
- Plugin-namespaced skills under `~/.claude/plugins/marketplaces/`, `~/.claude/plugins/cache/`, and `~/.claude/sources/` are still not scanned. Affected skills are invisible to audit/dupes/tokens — tracked separately.
- `usage.sh` natural-language matching is too strict and reports most skills as "never used"; tuning needs design discussion.
- `precheck.sh` URL handling fails on nested-skill repo layouts (e.g. `anthropics/skills`); robust resolver is a separate change.

## v1.1.0 (2026-04-15)

### New
- **Cross-platform support** - works with both Claude Code and OpenAI Codex
- `/janitor-precheck` - check overlap before installing a new skill
- `/janitor-tokens` - show context window token cost per skill

### Changed
- `/janitor-report` now includes lint checks, duplicate detection, and broken skill findings (was separate check/duplicates/cleanup commands)
- `/janitor-fix` gains `--prune` flag for removing broken symlinks and empty dirs
- `/janitor-search` gains `--compare <name>` flag for market comparison

### Removed (merged)
- `/janitor-check` -> use `/janitor-report`
- `/janitor-cleanup` -> use `/janitor-fix --prune`
- `/janitor-duplicates` -> use `/janitor-report`
- `/janitor-compare` -> use `/janitor-search --compare <name>`

## v1.0.0 (2026-03-24)

Initial release with 9 skills: audit, duplicates, check, fix, cleanup, report, usage, search, compare.
