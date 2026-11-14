REPO_URL="https://github.com/Mohammed-Abdelhady/hyperflow.git"
INSTALL_DIR="${HYPERFLOW_HOME:-$HOME/.hyperflow/repo}"
# OpenCode normally uses ~/.config/opencode; OPENCODE_CONFIG_DIR can override it.
OPENCODE_ROOT="${OPENCODE_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode}"
CLAUDE_ROOT="$HOME/.claude"
CODEX_ROOT="${CODEX_HOME:-$HOME/.codex}"
ANTIGRAVITY_ROOT="$HOME/.gemini/config"
CURSOR_ROOT="$HOME/.cursor"
PI_ROOT="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
CLAUDE_SKILLS_ROOT="$CLAUDE_ROOT/skills"
CODEX_SKILLS_ROOT="$CODEX_ROOT/skills"
ANTIGRAVITY_SKILLS_ROOT="$ANTIGRAVITY_ROOT/skills"
CURSOR_SKILLS_ROOT="$CURSOR_ROOT/skills"
PI_SKILLS_ROOT="$PI_ROOT/skills"
# Symlink targets must be absolute: a relative HYPERFLOW_HOME would otherwise
# be resolved relative to the host's skills directory instead of this checkout.
case "$INSTALL_DIR" in
  /*) ;;
  *) INSTALL_DIR="$PWD/$INSTALL_DIR" ;;
esac
case "$OPENCODE_ROOT" in
  /*) ;;
  *) OPENCODE_ROOT="$PWD/$OPENCODE_ROOT" ;;
esac
for variable in CODEX_ROOT CURSOR_ROOT PI_ROOT; do
  value="${!variable}"
  case "$value" in
    /*) ;;
    *) printf -v "$variable" '%s/%s' "$PWD" "$value" ;;
  esac
done
CODEX_SKILLS_ROOT="$CODEX_ROOT/skills"
CURSOR_SKILLS_ROOT="$CURSOR_ROOT/skills"
PI_SKILLS_ROOT="$PI_ROOT/skills"
CORE_SKILLS=(hyperflow-plan hyperflow-smash hyperflow-crash hyperflow-agents-skill)
CORE_COMMANDS=(hyperflow-plan hyperflow-smash hyperflow-crash hyperflow-agents-skill)
LEGACY_SKILLS=(hyperflow plan dispatch trace audit deploy handoff)
ACTION="install"
STATUS_CHECK=0
STATUS_JSON=0
HOST_FAILURES=0
HOST_SUCCESSES=0

info() { printf '> %s\n' "$1"; }
warn() { printf '! %s\n' "$1" >&2; }

is_git_checkout() {
  [ -d "$1/.git" ] || [ -f "$1/.git" ]
}

current_branch() {
  git -C "$1" symbolic-ref --quiet --short HEAD 2>/dev/null || true
}

usage() {
  printf '%s\n' \
    "Usage: install.sh [--link-only | --status [--check] [--json] | --uninstall | --help]" \
    "" \
    "Links four skills for detected supported hosts and registers OpenCode commands." \
    "Foreign registrations, shared skills, project .hyperflow data, and provider" \
    "credentials are preserved. No workflow is executed."
}

host_detected() {
  case "$1" in
    opencode) [ -d "$OPENCODE_ROOT" ] || command -v opencode >/dev/null 2>&1 ;;
    claude_code) [ -d "$CLAUDE_ROOT" ] || command -v claude >/dev/null 2>&1 ;;
    codex) [ -d "$CODEX_ROOT" ] || command -v codex >/dev/null 2>&1 ;;
    antigravity) [ -d "$ANTIGRAVITY_ROOT" ] || [ -d "$HOME/.gemini/antigravity" ] ;;
    cursor) [ -d "$CURSOR_ROOT" ] || command -v cursor >/dev/null 2>&1 ;;
    pi) [ -d "$PI_ROOT" ] || command -v pi >/dev/null 2>&1 ;;
    *) return 1 ;;
  esac
}

json_string() {
  local value="$1" escaped="" character
  while [ -n "$value" ]; do
    character="${value%"${value#?}"}"
    value="${value#?}"
    case "$character" in
      \\) escaped+="\\\\" ;;
      '"') escaped+='\"' ;;
      $'\b') escaped+='\b' ;;
      $'\f') escaped+='\f' ;;
      $'\n') escaped+='\n' ;;
      $'\r') escaped+='\r' ;;
      $'\t') escaped+='\t' ;;
      *)
        local code escaped_character
        printf -v code '%d' "'$character"
        if [ "$code" -lt 32 ]; then
          printf -v escaped_character '\\u%04x' "$code"
          escaped+="$escaped_character"
        else
          escaped+="$character"
        fi
        ;;
    esac
  done
  printf '"%s"' "$escaped"
}

print_status() {
  local checkout_state='missing' readiness='unavailable'
  local current_version='' tracking_version='' update_available='null'
  local opencode_detected=false claude_detected=false codex_detected=false
  local antigravity_detected=false cursor_detected=false pi_detected=false
  local opencode_links='not detected' opencode_commands='not detected'
  local claude_links='not detected' codex_links='not detected'
  local antigravity_links='not detected' cursor_links='not detected' pi_links='not detected'
  local healthy=false

  if [ -e "$INSTALL_DIR" ] && ! is_git_checkout "$INSTALL_DIR"; then
    checkout_state='not a Git checkout'
  elif [ -d "$INSTALL_DIR" ] || [ -f "$INSTALL_DIR" ]; then
    if ! command -v git >/dev/null 2>&1; then
      checkout_state='Git unavailable'
    elif validate_checkout >/dev/null 2>&1; then
      checkout_state='valid'
    else
      checkout_state='invalid'
    fi
  fi
  if [ "$checkout_state" = 'valid' ]; then
    current_version="$(package_version "$INSTALL_DIR/package.json")"
    if [ -n "$(git -C "$INSTALL_DIR" status --porcelain --untracked-files=all)" ]; then
      readiness='blocked (dirty checkout)'
    else
      local branch
      branch="$(current_branch "$INSTALL_DIR")"
      if [ -z "$branch" ]; then
        readiness='blocked (detached HEAD)'
      elif [ "$branch" != 'main' ]; then
        readiness="blocked (branch=$branch; expected main)"
      elif ! git -C "$INSTALL_DIR" rev-parse --verify refs/remotes/origin/main >/dev/null 2>&1; then
        readiness='unknown (origin/main is not available locally)'
      elif ! validate_tracking_checkout refs/remotes/origin/main; then
        readiness='blocked (origin/main is incomplete or invalid)'
      else
        tracking_version="$(git -C "$INSTALL_DIR" show refs/remotes/origin/main:package.json | package_version_from_stdin)"
        if [ "$(git -C "$INSTALL_DIR" rev-parse HEAD)" = "$(git -C "$INSTALL_DIR" rev-parse refs/remotes/origin/main)" ]; then update_available=false; else update_available=true; fi
        if ! git -C "$INSTALL_DIR" merge-base --is-ancestor HEAD refs/remotes/origin/main; then
          readiness='blocked (diverged from origin/main)'
        elif version_is_less "$tracking_version" "$current_version"; then
          readiness="blocked (origin/main version regresses $current_version -> $tracking_version)"
        else
          readiness='ready (branch=main)'
        fi
      fi
    fi
  else
    readiness="unavailable (checkout $checkout_state)"
  fi

  if [ "$checkout_state" = 'valid' ] && [ "$readiness" = 'ready (branch=main)' ]; then healthy=true; fi
  if host_detected opencode; then
    opencode_detected=true
    opencode_links="$(link_state "$OPENCODE_ROOT/skills")"
    opencode_commands="$(command_state "$OPENCODE_ROOT/commands")"
  fi
  if host_detected claude_code; then
    claude_detected=true
    claude_links="$(link_state "$CLAUDE_SKILLS_ROOT")"
  fi
  if host_detected codex; then
    codex_detected=true
    codex_links="$(codex_skill_state)"
  fi
  if host_detected antigravity; then antigravity_detected=true; antigravity_links="$(link_state "$ANTIGRAVITY_SKILLS_ROOT")"; fi
  if host_detected cursor; then cursor_detected=true; cursor_links="$(link_state "$CURSOR_SKILLS_ROOT")"; fi
  if host_detected pi; then pi_detected=true; pi_links="$(link_state "$PI_SKILLS_ROOT")"; fi
  if [ "$healthy" = true ]; then
    if [ "$opencode_detected" = true ] && { [ "$opencode_links" != complete ] || [ "$opencode_commands" != complete ]; }; then healthy=false; fi
    if [ "$claude_detected" = true ] && [ "$claude_links" != complete ]; then healthy=false; fi
    if [ "$codex_detected" = true ] && [ "$codex_links" != complete ]; then healthy=false; fi
    if [ "$antigravity_detected" = true ] && [ "$antigravity_links" != complete ]; then healthy=false; fi
    if [ "$cursor_detected" = true ] && [ "$cursor_links" != complete ]; then healthy=false; fi
    if [ "$pi_detected" = true ] && [ "$pi_links" != complete ]; then healthy=false; fi
  fi

  if [ "$STATUS_JSON" = "1" ]; then
    printf '{'
    printf '"checkout_path":'; json_string "$INSTALL_DIR"
    printf ',"checkout_state":'; json_string "$checkout_state"
    printf ',"update_readiness":'; json_string "$readiness"
    printf ',"versions":{"current":'
    if [ -n "$current_version" ]; then json_string "$current_version"; else printf 'null'; fi
    printf ',"tracking":'
    if [ -n "$tracking_version" ]; then json_string "$tracking_version"; else printf 'null'; fi
    printf '},"update_available":%s' "$update_available"
    printf ',"healthy":%s' "$healthy"
    printf ',"skill_links":{"opencode":{"detected":%s,"root":' "$opencode_detected"
    if [ "$opencode_detected" = true ]; then json_string "$OPENCODE_ROOT"; else printf 'null'; fi
    printf ',"state":'; json_string "$opencode_links"
    printf '},"claude_code":{"detected":%s,"root":' "$claude_detected"
    if [ "$claude_detected" = true ]; then json_string "$CLAUDE_ROOT"; else printf 'null'; fi
    printf ',"state":'; json_string "$claude_links"
    printf '},"codex":{"detected":%s,"root":' "$codex_detected"
    if [ "$codex_detected" = true ]; then json_string "$CODEX_ROOT"; else printf 'null'; fi
    printf ',"state":'; json_string "$codex_links"
    printf '},"antigravity":{"detected":%s,"root":' "$antigravity_detected"
    if [ "$antigravity_detected" = true ]; then json_string "$ANTIGRAVITY_ROOT"; else printf 'null'; fi
    printf ',"state":'; json_string "$antigravity_links"
    printf '},"cursor":{"detected":%s,"root":' "$cursor_detected"
    if [ "$cursor_detected" = true ]; then json_string "$CURSOR_ROOT"; else printf 'null'; fi
    printf ',"state":'; json_string "$cursor_links"
    printf '},"pi":{"detected":%s,"root":' "$pi_detected"
    if [ "$pi_detected" = true ]; then json_string "$PI_ROOT"; else printf 'null'; fi
    printf ',"state":'; json_string "$pi_links"
    printf '}},"command_files":{"opencode":{"detected":%s,"root":' "$opencode_detected"
    if [ "$opencode_detected" = true ]; then json_string "$OPENCODE_ROOT"; else printf 'null'; fi
    printf ',"state":'; json_string "$opencode_commands"
    printf '}},"read_only":true}\n'
  else
    printf 'Hyperflow installer status (read-only)\n'
    printf 'Checkout: %s\n' "$INSTALL_DIR"
    printf 'Checkout state: %s\n' "$checkout_state"
    printf 'Update readiness: %s\n' "$readiness"
    printf 'Current version: %s\n' "${current_version:-unavailable}"
    printf 'Cached origin/main version: %s\n' "${tracking_version:-unavailable}"
    if [ "$update_available" = 'null' ]; then printf 'Update available: unknown\n'; else printf 'Update available: %s\n' "$update_available"; fi
    printf 'OpenCode skill links: %s\n' "$opencode_links"
    printf 'OpenCode command files: %s\n' "$opencode_commands"
    printf 'Claude Code skill links: %s\n' "$claude_links"
    printf 'Codex skill links: %s\n' "$codex_links"
    printf 'Antigravity skill links: %s\n' "$antigravity_links"
    printf 'Cursor skill links: %s\n' "$cursor_links"
    printf 'Pi skill links: %s\n' "$pi_links"
    printf 'No fetch, plugin operation, directory creation, workflow execution, or link change was performed.\n'
  fi
  if [ "$STATUS_CHECK" = "1" ]; then [ "$healthy" = true ]; fi
}

is_hyperflow_remote() {
  case "$1" in
    "$REPO_URL"|https://github.com/Mohammed-Abdelhady/hyperflow|git@github.com:Mohammed-Abdelhady/hyperflow.git|git@github.com:Mohammed-Abdelhady/hyperflow|ssh://git@github.com/Mohammed-Abdelhady/hyperflow.git|ssh://git@github.com/Mohammed-Abdelhady/hyperflow)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}
