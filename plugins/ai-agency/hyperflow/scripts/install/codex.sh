codex_skill_state() {
  if ! command -v node >/dev/null 2>&1; then printf 'unavailable'; return; fi
  node "$SCRIPT_DIR/scripts/install/codex-skills.mjs" status "$INSTALL_DIR" "$CODEX_SKILLS_ROOT" 2>/dev/null || printf 'unavailable'
}

link_codex_provider() {
  if ! node "$SCRIPT_DIR/scripts/install/codex-skills.mjs" install "$INSTALL_DIR" "$CODEX_SKILLS_ROOT"; then
    warn "Codex: source copy failed; existing skill paths were preserved"
    HOST_FAILURES=$((HOST_FAILURES + 1))
    return
  fi
  HOST_SUCCESSES=$((HOST_SUCCESSES + 1))
  info "Codex: four skill copies ready"
}

remove_codex_owned_copies() {
  if ! command -v node >/dev/null 2>&1; then
    warn "Codex: cannot check owned skill copies without Node.js; preserved them"
    return
  fi
  node "$SCRIPT_DIR/scripts/install/codex-skills.mjs" uninstall "$INSTALL_DIR" "$CODEX_SKILLS_ROOT"
}
