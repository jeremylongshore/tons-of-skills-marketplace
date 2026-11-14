package_version_from_stdin() {
  awk '
    function finish_string() {
      if (capture_version) {
        version_token = token
        capture_version = 0
      } else if (depth == 1) {
        candidate = token
      }
      token = ""
    }
    {
      for (position = 1; position <= length($0); position++) {
        character = substr($0, position, 1)
        if (in_string) {
          if (escaped) { escaped = 0; token = token character; continue }
          if (character == "\\") { escaped = 1; token = token character; continue }
          if (character == "\"") { in_string = 0; finish_string(); continue }
          token = token character
          continue
        }
        if (expect_version) {
          if (character ~ /[[:space:]]/) continue
          if (character == "\"") {
            in_string = 1
            token = ""
            capture_version = 1
            expect_version = 0
            continue
          }
          expect_version = 0
          candidate = ""
        }
        if (candidate != "") {
          if (character ~ /[[:space:]]/) continue
          if (character == ":") {
            if (candidate == "version") {
              expect_version = 1
              version_seen = 1
              version_token = ""
            }
            else candidate = ""
            continue
          }
          candidate = ""
        }
        if (character == "\"") { in_string = 1; token = ""; continue }
        if (character == "{" || character == "[") depth++
        else if (character == "}" || character == "]") depth--
      }
    }
    END {
      if (version_seen && version_token ~ /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/) print version_token
    }
  '
}
package_version() {
  package_version_from_stdin < "$1"
}
package_json_is_valid_from_stdin() {
  awk '
    function skip_whitespace(   character) {
      while (position <= document_length) {
        character = substr(document, position, 1)
        if (character !~ /[[:space:]]/) break
        position++
      }
    }
    function parse_string(   character, escaped, offset) {
      if (substr(document, position, 1) != "\"") return 0
      position++
      while (position <= document_length) {
        character = substr(document, position, 1)
        if (character == "\"") { position++; return 1 }
        if (character ~ /[[:cntrl:]]/) return 0
        if (character == "\\") {
          position++
          if (position > document_length) return 0
          escaped = substr(document, position, 1)
          if (escaped == "u") {
            for (offset = 1; offset <= 4; offset++) {
              position++
              character = substr(document, position, 1)
              if (character !~ /[0-9A-Fa-f]/) return 0
            }
          } else if (escaped != "\"" && escaped != "\\" && escaped != "/" && escaped != "b" && escaped != "f" && escaped != "n" && escaped != "r" && escaped != "t") {
            return 0
          }
        }
        position++
      }
      return 0
    }
    function parse_number(   remaining) {
      remaining = substr(document, position)
      if (!match(remaining, /^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?/)) return 0
      position += RLENGTH
      return 1
    }
    function parse_literal(literal) {
      if (substr(document, position, length(literal)) != literal) return 0
      position += length(literal)
      return 1
    }
    function parse_value(   character) {
      skip_whitespace()
      character = substr(document, position, 1)
      if (character == "{") return parse_object()
      if (character == "[") return parse_array()
      if (character == "\"") return parse_string()
      if (character == "-" || character ~ /[0-9]/) return parse_number()
      if (character == "t") return parse_literal("true")
      if (character == "f") return parse_literal("false")
      if (character == "n") return parse_literal("null")
      return 0
    }
    function parse_object(   character) {
      position++
      skip_whitespace()
      if (substr(document, position, 1) == "}") { position++; return 1 }
      while (1) {
        if (!parse_string()) return 0
        skip_whitespace()
        if (substr(document, position, 1) != ":") return 0
        position++
        if (!parse_value()) return 0
        skip_whitespace()
        character = substr(document, position, 1)
        if (character == "}") { position++; return 1 }
        if (character != ",") return 0
        position++
        skip_whitespace()
      }
    }
    function parse_array(   character) {
      position++
      skip_whitespace()
      if (substr(document, position, 1) == "]") { position++; return 1 }
      while (1) {
        if (!parse_value()) return 0
        skip_whitespace()
        character = substr(document, position, 1)
        if (character == "]") { position++; return 1 }
        if (character != ",") return 0
        position++
        skip_whitespace()
      }
    }
    { document = document $0 "\n" }
    END {
      document_length = length(document)
      position = 1
      if (!parse_value()) exit 1
      skip_whitespace()
      if (position <= document_length) exit 1
    }
  '
}

package_json_is_valid() {
  package_json_is_valid_from_stdin < "$1"
}

version_is_less() {
  local left="$1" right="$2" left_major left_minor left_patch right_major right_minor right_patch pair x y
  IFS=. read -r left_major left_minor left_patch <<< "$left"
  IFS=. read -r right_major right_minor right_patch <<< "$right"
  for pair in "$left_major $right_major" "$left_minor $right_minor" "$left_patch $right_patch"; do
    read -r x y <<< "$pair"
    if [ "${#x}" -lt "${#y}" ]; then return 0; fi
    if [ "${#x}" -gt "${#y}" ]; then return 1; fi
    if [ "$x" != "$y" ]; then
      if [[ "$x" < "$y" ]]; then return 0; fi
      return 1
    fi
  done
  return 1
}

validate_checkout() {
  local checkout="${1:-$INSTALL_DIR}" remote skill command version
  is_git_checkout "$checkout" || { warn "Not a Git checkout: $checkout"; return 1; }
  remote="$(git -C "$checkout" config --get remote.origin.url 2>/dev/null || true)"
  is_hyperflow_remote "$remote" || {
    warn "Install path is not the Hyperflow repository: $checkout"
    return 1
  }
  [ -f "$checkout/package.json" ] || {
    warn "Incomplete Hyperflow checkout: missing package.json"
    return 1
  }
  package_json_is_valid "$checkout/package.json" || {
    warn "Invalid Hyperflow checkout: package.json must be valid JSON"
    return 1
  }
  version="$(package_version "$checkout/package.json")"
  [ -n "$version" ] || {
    warn "Invalid Hyperflow checkout: package.json must declare a semver version"
    return 1
  }
  for skill in "${CORE_SKILLS[@]}"; do
    [ -f "$checkout/skills/$skill/SKILL.md" ] || {
      warn "Incomplete Hyperflow checkout: missing skills/$skill/SKILL.md"
      return 1
    }
  done
  [ -f "$checkout/runtime/cli.mjs" ] || { warn "Incomplete Hyperflow checkout: missing runtime/cli.mjs"; return 1; }
  for command in "${CORE_COMMANDS[@]}"; do
    [ -f "$checkout/commands/$command.md" ] || { warn "Incomplete Hyperflow checkout: missing commands/$command.md"; return 1; }
  done
}

validate_update_checkout() {
  local checkout="${1:-$INSTALL_DIR}"
  if validate_checkout "$checkout" >/dev/null 2>&1; then return 0; fi
  validate_legacy_checkout_for_update "$checkout"
}

validate_legacy_checkout_for_update() {
  local checkout="$1" remote version skills
  is_git_checkout "$checkout" || return 1
  remote="$(git -C "$checkout" config --get remote.origin.url 2>/dev/null || true)"
  is_hyperflow_remote "$remote" || return 1
  [ -f "$checkout/package.json" ] && package_json_is_valid "$checkout/package.json" || return 1
  version="$(package_version "$checkout/package.json")"
  case "$version" in 6.*) ;; *) return 1 ;; esac
  skills="$(git -C "$checkout" ls-tree -d --name-only HEAD:skills 2>/dev/null | LC_ALL=C sort | tr '\n' ' ' | sed 's/ $//')"
  [ "$skills" = 'audit deploy dispatch handoff hyperflow plan trace' ] || return 1
  for skill in "${LEGACY_SKILLS[@]}"; do
    git -C "$checkout" cat-file -e "HEAD:skills/$skill/SKILL.md" 2>/dev/null || return 1
  done
  git -C "$checkout" cat-file -e HEAD:README.md 2>/dev/null || return 1
  git -C "$checkout" cat-file -e HEAD:install.sh 2>/dev/null
}

validate_fetched_checkout() {
  local skill command incoming_version
  git -C "$INSTALL_DIR" cat-file -e FETCH_HEAD:package.json 2>/dev/null || {
    warn "Fetched origin/main is incomplete: missing package.json; leaving checkout unchanged."
    exit 1
  }
  if ! git -C "$INSTALL_DIR" show FETCH_HEAD:package.json | package_json_is_valid_from_stdin; then
    warn "Fetched origin/main is invalid: package.json must be valid JSON; leaving checkout unchanged."
    exit 1
  fi
  incoming_version="$(git -C "$INSTALL_DIR" show FETCH_HEAD:package.json | package_version_from_stdin)"
  [ -n "$incoming_version" ] || {
    warn "Fetched origin/main is invalid: package.json must declare a semver version; leaving checkout unchanged."
    exit 1
  }
  for skill in "${CORE_SKILLS[@]}"; do
    git -C "$INSTALL_DIR" cat-file -e "FETCH_HEAD:skills/$skill/SKILL.md" 2>/dev/null || {
      warn "Fetched origin/main is incomplete: missing skills/$skill/SKILL.md; leaving checkout unchanged."
      exit 1
    }
  done
  git -C "$INSTALL_DIR" cat-file -e FETCH_HEAD:runtime/cli.mjs 2>/dev/null || { warn "Fetched origin/main is incomplete: missing runtime/cli.mjs; leaving checkout unchanged."; exit 1; }
  for command in "${CORE_COMMANDS[@]}"; do
    git -C "$INSTALL_DIR" cat-file -e "FETCH_HEAD:commands/$command.md" 2>/dev/null || { warn "Fetched origin/main is incomplete: missing commands/$command.md; leaving checkout unchanged."; exit 1; }
  done
}

validate_tracking_checkout() {
  local ref="$1" skill command tracking_version
  git -C "$INSTALL_DIR" rev-parse --verify "$ref^{commit}" >/dev/null 2>&1 || return 1
  git -C "$INSTALL_DIR" cat-file -e "$ref:package.json" 2>/dev/null || return 1
  git -C "$INSTALL_DIR" show "$ref:package.json" | package_json_is_valid_from_stdin || return 1
  tracking_version="$(git -C "$INSTALL_DIR" show "$ref:package.json" | package_version_from_stdin)" || return 1
  [ -n "$tracking_version" ] || return 1
  for skill in "${CORE_SKILLS[@]}"; do
    git -C "$INSTALL_DIR" cat-file -e "$ref:skills/$skill/SKILL.md" 2>/dev/null || return 1
  done
  git -C "$INSTALL_DIR" cat-file -e "$ref:runtime/cli.mjs" 2>/dev/null || return 1
  for command in "${CORE_COMMANDS[@]}"; do
    git -C "$INSTALL_DIR" cat-file -e "$ref:commands/$command.md" 2>/dev/null || return 1
  done
}

clone_or_update() {
  if is_git_checkout "$INSTALL_DIR"; then
    local current_version incoming_version branch
    validate_update_checkout || {
      warn "Incomplete Hyperflow checkout: only a valid current layout or known clean-updatable v6 layout can update."
      exit 1
    }
    if [ -n "$(git -C "$INSTALL_DIR" status --porcelain --untracked-files=all)" ]; then
      warn "Refusing to update dirty checkout: $INSTALL_DIR"
      warn "Commit or stash local changes before rerunning the installer."
      exit 1
    fi
    branch="$(current_branch "$INSTALL_DIR")"
    if [ "$branch" != 'main' ]; then
      warn "Refusing to update checkout on ${branch:-detached HEAD}; source-managed updates require the main branch."
      warn "Switch the checkout to main before rerunning the installer."
      exit 1
    fi
    info "Updating $INSTALL_DIR"
    if ! git -C "$INSTALL_DIR" fetch --quiet origin main; then
      warn "Unable to fetch origin/main; leaving checkout unchanged."
      exit 1
    fi
    validate_fetched_checkout
    current_version="$(package_version "$INSTALL_DIR/package.json")"
    incoming_version="$(git -C "$INSTALL_DIR" show FETCH_HEAD:package.json | package_version_from_stdin)"
    if [ -z "$current_version" ] || [ -z "$incoming_version" ]; then
      warn "Unable to determine valid package versions for the update; leaving checkout unchanged."
      exit 1
    fi
    if version_is_less "$incoming_version" "$current_version"; then
      warn "Refusing version-regressing update $current_version -> $incoming_version; leaving checkout unchanged."
      exit 1
    fi
    if ! git -C "$INSTALL_DIR" merge-base --is-ancestor HEAD FETCH_HEAD; then
      warn "Refusing non-fast-forward update: local checkout has diverged from origin/main."
      warn "Re-clone or reconcile the checkout manually before rerunning the installer."
      exit 1
    fi
    if ! git -C "$INSTALL_DIR" merge --ff-only --quiet FETCH_HEAD; then
      warn "Unable to fast-forward origin/main; leaving checkout unchanged."
      exit 1
    fi
    validate_checkout
    return
  fi

  if [ -e "$INSTALL_DIR" ]; then
    warn "Install path exists and is not a Hyperflow checkout: $INSTALL_DIR"
    exit 1
  fi

  info "Installing to $INSTALL_DIR"
  mkdir -p "$(dirname "$INSTALL_DIR")"
  local staging_root
  staging_root="$(mktemp -d "${INSTALL_DIR}.tmp.XXXXXX")" || {
    warn "Temp directory failed."
    exit 1
  }
  if ! git clone --quiet --depth 1 "$REPO_URL" "$staging_root" || ! validate_checkout "$staging_root"; then
    rm -r -- "$staging_root"
    warn "Clone failed."
    exit 1
  fi
  if ! mv -- "$staging_root" "$INSTALL_DIR"; then
    rm -r -- "$staging_root"
    warn "Activation failed."
    exit 1
  fi
}
