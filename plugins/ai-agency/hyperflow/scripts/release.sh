#!/usr/bin/env bash
# Create a local release commit and annotated tag. Pushing is always separate.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

DRY_RUN=0
REQUESTED=""
SEMVER_RE='^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'

usage() {
  printf '%s\n' \
    "Usage: scripts/release.sh [major|minor|patch|X.Y.Z] [--dry-run]" \
    "" \
    "Without an argument, the bump is inferred from conventional commits:" \
    "BREAKING or ! -> major, feat -> minor, fix/perf/refactor -> patch." \
    "The script validates, stamps, commits, and tags locally. It never pushes."
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --help|-h) usage; exit 0 ;;
    major|minor|patch) [ -z "$REQUESTED" ] || { printf 'Error: multiple versions supplied.\n' >&2; exit 1; }; REQUESTED="$1" ;;
    [0-9]*.[0-9]*.[0-9]*) [ -z "$REQUESTED" ] || { printf 'Error: multiple versions supplied.\n' >&2; exit 1; }; REQUESTED="$1" ;;
    *) printf 'Error: unknown argument: %s\n' "$1" >&2; usage; exit 1 ;;
  esac
  shift
done

command -v git >/dev/null 2>&1 || { printf 'Error: git is required.\n' >&2; exit 1; }
command -v node >/dev/null 2>&1 || { printf 'Error: Node.js is required.\n' >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { printf 'Error: npm is required.\n' >&2; exit 1; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { printf 'Error: not a git worktree.\n' >&2; exit 1; }
BRANCH="$(git symbolic-ref --quiet --short HEAD)" || { printf 'Error: detached HEAD releases are blocked.\n' >&2; exit 1; }

if [ -n "$(git status --porcelain)" ]; then
  printf 'Error: release requires a clean worktree. Commit each task first.\n' >&2
  exit 1
fi

CURRENT="$(node -p "JSON.parse(require('fs').readFileSync('package.json','utf8')).version")"
[[ "$CURRENT" =~ $SEMVER_RE ]] || { printf 'Error: package version is not strict semver: %s\n' "$CURRENT" >&2; exit 1; }

CURRENT_TAG="v$CURRENT"
LAST_TAG=""
if git rev-parse -q --verify "refs/tags/$CURRENT_TAG" >/dev/null && git merge-base --is-ancestor "$CURRENT_TAG" HEAD; then
  LAST_TAG="$CURRENT_TAG"
elif [ -z "$REQUESTED" ]; then
  printf 'Error: current tag %s is unavailable; specify major, minor, patch, or an exact version explicitly.\n' "$CURRENT_TAG" >&2
  exit 1
fi
if [ -n "$LAST_TAG" ]; then
  COMMITS="$(git log --format='%s%n%b' "$LAST_TAG"..HEAD)"
else
  COMMITS="$(git log --format='%s%n%b' HEAD)"
fi

if [ -z "$COMMITS" ]; then
  printf 'Nothing to release.\n'
  exit 0
fi

if [ -z "$REQUESTED" ]; then
  if printf '%s\n' "$COMMITS" | grep -qE 'BREAKING CHANGE|^[a-z]+(\([^)]*\))?!:'; then
    REQUESTED="major"
  elif printf '%s\n' "$COMMITS" | grep -qE '^feat(\([^)]*\))?:'; then
    REQUESTED="minor"
  elif printf '%s\n' "$COMMITS" | grep -qE '^(fix|perf|refactor)(\([^)]*\))?:'; then
    REQUESTED="patch"
  else
    printf 'Nothing release-worthy since %s.\n' "${LAST_TAG:-repository start}"
    exit 0
  fi
fi

IFS=. read -r MAJOR MINOR PATCH <<< "$CURRENT"
case "$REQUESTED" in
  major) VERSION="$((MAJOR + 1)).0.0" ;;
  minor) VERSION="$MAJOR.$((MINOR + 1)).0" ;;
  patch) VERSION="$MAJOR.$MINOR.$((PATCH + 1))" ;;
  *) VERSION="$REQUESTED" ;;
esac

[[ "$VERSION" =~ $SEMVER_RE ]] || { printf 'Error: release version is not strict semver: %s\n' "$VERSION" >&2; exit 1; }
IFS=. read -r NEXT_MAJOR NEXT_MINOR NEXT_PATCH <<< "$VERSION"
if sed -n '/^## \[Unreleased\]/,/^## \[[0-9]/p' CHANGELOG.md | grep -q '^### Migration$' && (( NEXT_MAJOR <= MAJOR )); then
  printf 'Error: the Unreleased migration boundary requires a major version greater than %s.\n' "$CURRENT" >&2
  exit 1
fi
if (( NEXT_MAJOR < MAJOR )) \
  || (( NEXT_MAJOR == MAJOR && NEXT_MINOR < MINOR )) \
  || (( NEXT_MAJOR == MAJOR && NEXT_MINOR == MINOR && NEXT_PATCH <= PATCH )); then
  printf 'Error: release version %s must be greater than %s.\n' "$VERSION" "$CURRENT" >&2
  exit 1
fi

if git rev-parse -q --verify "refs/tags/v$VERSION" >/dev/null; then
  printf 'Error: tag v%s already exists.\n' "$VERSION" >&2
  exit 1
fi

printf 'Release plan: %s -> %s on %s\n' "$CURRENT" "$VERSION" "$BRANCH"
if [ -n "$LAST_TAG" ]; then
  git diff --check "$LAST_TAG...HEAD"
else
  EMPTY_TREE="$(git hash-object -t tree /dev/null)"
  git diff --check "$EMPTY_TREE" HEAD
fi
npm run validate-plugin
npm run unittest
npm run evals
bash -n install.sh scripts/*.sh scripts/install/*.sh

if [ "$DRY_RUN" = "1" ]; then
  printf 'Dry run complete. No files, commits, tags, or remotes changed.\n'
  exit 0
fi

HYPERFLOW_RELEASE_PREPARE=1 "$SCRIPT_DIR/bump-version.sh" "$VERSION"
npm run validate-plugin
npm run unittest
npm run evals
bash -n install.sh scripts/*.sh scripts/install/*.sh
git diff --check

release_files=(
  package.json
  .claude-plugin/plugin.json
  .claude-plugin/marketplace.json
  .codex-plugin/plugin.json
  skills/hyperflow-plan/SKILL.md
  skills/hyperflow-smash/SKILL.md
  skills/hyperflow-crash/SKILL.md
  skills/hyperflow-agents-skill/SKILL.md
  AGENTS.md
  CLAUDE.md
  README.md
  CHANGELOG.md
)

existing_files=()
for file in "${release_files[@]}"; do
  [ -f "$file" ] && existing_files+=("$file")
done
git add -- "${existing_files[@]}"

git diff --cached --quiet && { printf 'Error: version stamping produced no staged change.\n' >&2; exit 1; }
git commit -m "chore(release): v$VERSION"
git tag -a "v$VERSION" -m "Hyperflow v$VERSION"

printf 'Local release v%s created. Nothing was pushed.\n' "$VERSION"
printf 'After explicit approval, push with:\n'
printf '  git push origin %s\n' "$BRANCH"
printf '  git push origin v%s\n' "$VERSION"
