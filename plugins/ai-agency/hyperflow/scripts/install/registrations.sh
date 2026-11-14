canonical_checkout() {
  (cd "$INSTALL_DIR" 2>/dev/null && pwd -P)
}

resolved_link_target() {
  local link="$1" value="$2" path parent
  case "$value" in
    /*) path="$value" ;;
    *) path="$(dirname "$link")/$value" ;;
  esac
  parent="$(cd "$(dirname "$path")" 2>/dev/null && pwd -P)" || return 1
  printf '%s/%s' "$parent" "$(basename "$path")"
}

is_owned_skill_link() {
  local link="$1" skill="$2" value actual expected checkout
  [ -L "$link" ] || return 1
  value="$(readlink "$link")"
  actual="$(resolved_link_target "$link" "$value")" || return 1
  checkout="$(canonical_checkout)" || return 1
  expected="$checkout/skills/$skill"
  [ "$actual" = "$expected" ]
}

link_points_into_checkout() {
  local link="$1" value actual checkout
  [ -L "$link" ] || return 1
  value="$(readlink "$link")"
  actual="$(resolved_link_target "$link" "$value")" || return 1
  checkout="$(canonical_checkout)" || return 1
  case "$actual" in "$checkout"/skills/*) return 0 ;; esac
  return 1
}

command_owned_by_checkout() {
  local target="$1" checkout marker
  [ -f "$target" ] && [ ! -L "$target" ] || return 1
  checkout="$(canonical_checkout)" || return 1
  marker="<!-- hyperflow-owned-command v1 root=$checkout -->"
  grep -Fqx "$marker" "$target"
}

link_state() {
  local root="$1" skill target state owned=0 bad=0 conflicts=0 legacy=0
  for skill in "${CORE_SKILLS[@]}"; do
    target="$root/$skill"
    if is_owned_skill_link "$target" "$skill" && [ -f "$INSTALL_DIR/skills/$skill/SKILL.md" ]; then
      owned=$((owned + 1))
    elif [ -L "$target" ] && link_points_into_checkout "$target"; then
      bad=$((bad + 1))
    elif [ -L "$target" ] || [ -e "$target" ]; then
      conflicts=$((conflicts + 1))
    fi
  done
  for skill in "${LEGACY_SKILLS[@]}"; do
    target="$root/$skill"
    [ -e "$target" ] || [ -L "$target" ] || continue
    if is_owned_skill_link "$target" "$skill" || link_points_into_checkout "$target"; then legacy=1; else conflicts=$((conflicts + 1)); fi
  done
  if [ "$conflicts" -gt 0 ]; then state='conflict'
  elif [ "$owned" -eq "${#CORE_SKILLS[@]}" ] && [ "$bad" -eq 0 ] && [ "$legacy" -eq 0 ]; then state='complete'
  elif [ "$owned" -eq 0 ] && [ "$bad" -eq 0 ] && [ "$legacy" -eq 0 ]; then state='none'
  else state='partial'
  fi
  printf '%s' "$state"
}

command_state() {
  local root="$1" command target owned=0 bad=0 conflicts=0
  for command in "${CORE_COMMANDS[@]}"; do
    target="$root/$command.md"
    if command_owned_by_checkout "$target"; then owned=$((owned + 1))
    elif [ -e "$target" ] || [ -L "$target" ]; then conflicts=$((conflicts + 1))
    fi
  done
  if [ "$conflicts" -gt 0 ]; then printf 'conflict'
  elif [ "$owned" -eq "${#CORE_COMMANDS[@]}" ] && [ "$bad" -eq 0 ]; then printf 'complete'
  elif [ "$owned" -eq 0 ] && [ "$bad" -eq 0 ]; then printf 'none'
  else printf 'partial'
  fi
}

render_command() {
  local source="$1" target="$2" checkout
  checkout="$(canonical_checkout)" || return 1
  checkout="${checkout//\\/\\\\}"
  checkout="${checkout//&/\\&}"
  checkout="${checkout//|/\\|}"
  sed "s|@HYPERFLOW_PLUGIN_ROOT@|$checkout|g" "$source" > "$target"
}

rollback_provider() {
  local backup_dir="$1" target kind index
  local failed=0
  for ((index=${#targets[@]} - 1; index >= 0; index--)); do
    target="${targets[index]}"
    kind="${prior_kinds[index]}"
    case "$kind" in
      absent) rm -f -- "$target" || failed=1 ;;
      link) rm -f -- "$target" && ln -s -- "$(cat "$backup_dir/$index")" "$target" || failed=1 ;;
      file) cp -- "$backup_dir/$index" "$target" || failed=1 ;;
    esac
  done
  rm -r -- "$backup_dir"
  return "$failed"
}

link_provider() {
  local label="$1" target_root="$2" add_commands="${3:-false}" skill command target source current backup_dir
  local conflicts=0 rollback_failed index kind registered_command_count=0
  local -a targets=() prior_kinds=() prior_values=() legacy_targets=("") legacy_values=("")
  local -a registered_skills=()
  for skill in "${CORE_SKILLS[@]}"; do
    target="$target_root/skills/$skill"
    if [ -L "$target" ] && is_owned_skill_link "$target" "$skill"; then kind='link'; prior_values+=("$(readlink "$target")")
    elif [ -e "$target" ] || [ -L "$target" ]; then kind='conflict'; prior_values+=(""); conflicts=$((conflicts + 1))
    else kind='absent'; prior_values+=("")
    fi
    targets+=("$target"); prior_kinds+=("$kind")
  done
  if [ "$add_commands" = true ]; then
    for command in "${CORE_COMMANDS[@]}"; do
      target="$target_root/commands/$command.md"
      if command_owned_by_checkout "$target"; then kind='file'
      elif [ -e "$target" ] || [ -L "$target" ]; then kind='conflict'; conflicts=$((conflicts + 1))
      else kind='absent'
      fi
      targets+=("$target"); prior_kinds+=("$kind"); prior_values+=("")
    done
  fi
  for skill in "${LEGACY_SKILLS[@]}"; do
    target="$target_root/skills/$skill"
    if [ -L "$target" ] && is_owned_skill_link "$target" "$skill"; then
      legacy_targets+=("$target"); legacy_values+=("$(readlink "$target")")
    elif [ -e "$target" ] || [ -L "$target" ]; then
      warn "$label: preserving foreign legacy path: $target"
    fi
  done
  if [ "$conflicts" -gt 0 ]; then
    warn "$label: $conflicts foreign skill or command path conflict(s); provider was not changed"
    HOST_FAILURES=$((HOST_FAILURES + 1)); return
  fi

  backup_dir="$(mktemp -d "${TMPDIR:-/tmp}/hyperflow-install.XXXXXX")"
  for ((index=0; index<${#targets[@]}; index++)); do
    case "${prior_kinds[index]}" in
      link) printf '%s' "${prior_values[index]}" > "$backup_dir/$index" ;;
      file) cp -- "${targets[index]}" "$backup_dir/$index" ;;
    esac
  done

  for skill in "${CORE_SKILLS[@]}"; do
    source="$INSTALL_DIR/skills/$skill"; target="$target_root/skills/$skill"
    if ! mkdir -p -- "$(dirname "$target")"; then
      rollback_provider "$backup_dir" && rollback_failed=0 || rollback_failed=1
      warn "$label: skill registration failed; rollback status=$rollback_failed"
      HOST_FAILURES=$((HOST_FAILURES + 1)); return
    fi
    if [ -L "$target" ] && ! rm -- "$target"; then
      rollback_provider "$backup_dir" && rollback_failed=0 || rollback_failed=1
      warn "$label: skill registration failed; rollback status=$rollback_failed"
      HOST_FAILURES=$((HOST_FAILURES + 1)); return
    fi
    if ! ln -s -- "$source" "$target"; then
      rollback_provider "$backup_dir" targets prior_kinds && rollback_failed=0 || rollback_failed=1
      warn "$label: skill linking failed; rollback status=$rollback_failed"
      HOST_FAILURES=$((HOST_FAILURES + 1)); return
    fi
    registered_skills+=("$target")
  done
  if [ "$add_commands" = true ]; then
    for command in "${CORE_COMMANDS[@]}"; do
      source="$INSTALL_DIR/commands/$command.md"; target="$target_root/commands/$command.md"
      local rendered="$backup_dir/rendered-$command.md"
      if ! mkdir -p -- "$(dirname "$target")" || ! render_command "$source" "$rendered" || ! mv -- "$rendered" "$target"; then
        rollback_provider "$backup_dir" && rollback_failed=0 || rollback_failed=1
        warn "$label: command registration failed; rollback status=$rollback_failed"
        HOST_FAILURES=$((HOST_FAILURES + 1)); return
      fi
      registered_command_count=$((registered_command_count + 1))
    done
  fi

  local migration_failed=0
  for target in "${legacy_targets[@]}"; do [ -z "$target" ] || rm -- "$target" || migration_failed=1; done
  if [ "$migration_failed" -gt 0 ]; then
    for ((index=1; index<${#legacy_targets[@]}; index++)); do
      target="${legacy_targets[index]}"
      [ -e "$target" ] || [ -L "$target" ] || ln -s -- "${legacy_values[index]}" "$target" || rollback_failed=1
    done
    rollback_provider "$backup_dir" targets prior_kinds || rollback_failed=1
    warn "$label: legacy migration failed; rollback status=$rollback_failed"
    HOST_FAILURES=$((HOST_FAILURES + 1)); return
  fi
  rm -r -- "$backup_dir"
  HOST_SUCCESSES=$((HOST_SUCCESSES + 1))
  info "$label: ${#registered_skills[@]} skills and $registered_command_count commands ready"
}

link_detected_providers() {
  if host_detected opencode; then
    link_provider "OpenCode" "$OPENCODE_ROOT" true
  fi
  if host_detected claude_code; then
    link_provider "Claude Code" "$CLAUDE_ROOT"
  fi
  if host_detected codex; then
    link_codex_provider
  fi
  if host_detected antigravity; then
    link_provider "Antigravity" "$ANTIGRAVITY_ROOT"
  fi
  if host_detected cursor; then
    link_provider "Cursor" "$CURSOR_ROOT"
  fi
  if host_detected pi; then
    link_provider "Pi" "$PI_ROOT"
  fi
}

remove_owned_links() {
  local root skill command target removed=0
  local -a roots=("$OPENCODE_ROOT" "$CLAUDE_ROOT" "$CODEX_ROOT" "$ANTIGRAVITY_ROOT" "$CURSOR_ROOT" "$PI_ROOT")
  for root in "${roots[@]}"; do
    for skill in "${CORE_SKILLS[@]}" "${LEGACY_SKILLS[@]}"; do
      target="$root/skills/$skill"
      if is_owned_skill_link "$target" "$skill"; then rm -- "$target" && removed=$((removed + 1)); fi
    done
  done
  remove_codex_owned_copies
  for command in "${CORE_COMMANDS[@]}"; do
    target="$OPENCODE_ROOT/commands/$command.md"
    if command_owned_by_checkout "$target"; then rm -- "$target" && removed=$((removed + 1)); fi
  done
  info "Removed $removed owned Hyperflow registrations"
  info "Kept $INSTALL_DIR and all project .hyperflow data"
}
