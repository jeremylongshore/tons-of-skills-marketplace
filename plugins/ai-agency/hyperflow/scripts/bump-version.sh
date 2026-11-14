#!/usr/bin/env bash
# Stamp a prepared release version. This helper never commits, tags, or pushes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ "${HYPERFLOW_RELEASE_PREPARE:-0}" != "1" ]; then
  printf 'Error: use scripts/release.sh; direct version stamping is disabled.\n' >&2
  exit 1
fi

VERSION="${1:-}"
SEMVER_RE='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'
if [[ ! "$VERSION" =~ $SEMVER_RE ]]; then
  printf 'Usage: scripts/bump-version.sh X.Y.Z\n' >&2
  exit 1
fi

if sed --version >/dev/null 2>&1; then
  SED_IN_PLACE=(-i)
else
  SED_IN_PLACE=(-i '')
fi

replace() {
  local expression="$1" file="$2"
  [ -f "$file" ] || return
  sed "${SED_IN_PLACE[@]}" "$expression" "$file"
}

for file in \
  "$ROOT/package.json" \
  "$ROOT/.claude-plugin/plugin.json" \
  "$ROOT/.claude-plugin/marketplace.json" \
  "$ROOT/.codex-plugin/plugin.json"; do
  [ -f "$file" ] || { printf 'Error: missing manifest: %s\n' "$file" >&2; exit 1; }
  replace 's/"version": "[0-9][0-9.]*"/"version": "'"$VERSION"'"/g' "$file"
done

for skill in hyperflow-plan hyperflow-smash hyperflow-crash hyperflow-agents-skill; do
  replace 's/^version: [0-9][0-9.]*/version: '"$VERSION"'/' "$ROOT/skills/$skill/SKILL.md"
done

for file in "$ROOT/AGENTS.md" "$ROOT/CLAUDE.md"; do
  replace 's/hyperflow:doctrine:start version=[0-9][0-9.]*/hyperflow:doctrine:start version='"$VERSION"'/' "$file"
done

replace 's/<code>v[0-9][0-9.]*<\/code>/<code>v'"$VERSION"'<\/code>/g' "$ROOT/README.md"
replace 's/\[!\[version v[0-9][0-9.]*\]/[![version v'"$VERSION"']/' "$ROOT/README.md"
replace 's/badge\/version-v[0-9][0-9.]*-blueviolet/badge\/version-v'"$VERSION"'-blueviolet/g' "$ROOT/README.md"

node - "$VERSION" "$ROOT/CHANGELOG.md" <<'NODE'
const [version, path] = process.argv.slice(2);
const fs = require("node:fs");
const source = fs.readFileSync(path, "utf8");
const marker = "## [Unreleased]\n";
if (!source.includes(marker)) throw new Error("CHANGELOG.md is missing [Unreleased]");
const releaseVersions = [...source.matchAll(/^## \[(\d+\.\d+\.\d+)\]/gm)].map((match) => match[1]);
const previousVersion = releaseVersions[0];
if (!previousVersion) throw new Error("CHANGELOG.md is missing a previous release heading");
const olderVersion = releaseVersions[1];
const date = new Date().toISOString().slice(0, 10);
let updated = source.replace(marker, `${marker}\n## [${version}] — ${date}\n`);
const compareBase = "https://github.com/Mohammed-Abdelhady/hyperflow/compare";
const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
function setReference(text, label, url) {
  const entry = `[${label}]: ${url}`;
  const pattern = new RegExp(`^\\[${escapeRegExp(label)}\\]:.*$`, "m");
  return pattern.test(text) ? text.replace(pattern, entry) : `${text.trimEnd()}\n${entry}\n`;
}

updated = setReference(updated, "Unreleased", `${compareBase}/v${version}...HEAD`);
updated = setReference(updated, version, `${compareBase}/v${previousVersion}...v${version}`);
updated = setReference(
  updated,
  previousVersion,
  olderVersion ? `${compareBase}/v${olderVersion}...v${previousVersion}` : `${compareBase}/v${previousVersion}`,
);
fs.writeFileSync(path, updated);
NODE

printf 'Stamped Hyperflow %s. No commit, tag, or push was created.\n' "$VERSION"
