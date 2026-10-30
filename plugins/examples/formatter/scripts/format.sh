#!/bin/bash
# ============================================================================
# Script: format.sh
# Purpose: Auto-format code files after Write/Edit operations using Prettier
# Hook: PostToolUse (Write|Edit)
# Author: claude-code-examples
# Version: 2.0.0
# Last Updated: 2025-10-11
# ============================================================================
#
# DESCRIPTION:
#   This script is triggered by PostToolUse hooks when Claude uses Write or
#   Edit tools. It automatically formats supported file types using Prettier
#   to ensure consistent code style across the project.
#
# USAGE:
#   Called automatically by hooks system, receives tool data via stdin
#   Can also be run manually: ./format.sh < tool-output.json
#
# SUPPORTED FILE TYPES:
#   JavaScript (.js, .jsx), TypeScript (.ts, .tsx), JSON (.json),
#   CSS (.css, .scss, .less), Markdown (.md, .mdx), HTML (.html),
#   Vue (.vue), Svelte (.svelte), YAML (.yaml, .yml)
#
# REQUIREMENTS:
#   - Node.js and npm/npx installed
#   - Prettier (installed globally or locally)
#   - jq for JSON parsing
#
# EXIT CODES:
#   0 - Success (formatted or skipped appropriately)
#   1 - General error
#   2 - Missing dependencies
#   3 - File not found or not accessible
#   4 - Formatting failed but non-critical
# ============================================================================

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# ----------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
readonly LOG_DIR="${PLUGIN_ROOT}/logs"
readonly LOG_FILE="${LOG_DIR}/formatter-$(date +%Y%m%d).log"
readonly DEBUG="${FORMATTER_DEBUG:-false}"
readonly MAX_FILE_SIZE_KB=1000  # Skip files larger than 1MB for performance

# Supported file extensions (can be overridden by config)
readonly -a SUPPORTED_EXTENSIONS=(
    "js" "jsx" "ts" "tsx" "json"
    "css" "scss" "less" "md" "mdx"
    "yaml" "yml" "html" "vue" "svelte"
)

# Prettier options (can be overridden by .prettierrc)
readonly PRETTIER_OPTIONS="--single-quote --trailing-comma es5 --print-width 100"

# ----------------------------------------------------------------------------
# LOGGING FUNCTIONS
# ----------------------------------------------------------------------------

# Ensure log directory exists
mkdir -p "$LOG_DIR" 2>/dev/null || true

# Log message with timestamp
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

    echo "[${timestamp}] [${level}] ${message}" >> "${LOG_FILE}"

    if [[ "$DEBUG" == "true" ]]; then
        echo "[${level}] ${message}" >&2
    fi
}

log_info() {
    log "INFO" "$@"
}

log_error() {
    log "ERROR" "$@"
}

log_debug() {
    if [[ "$DEBUG" == "true" ]]; then
        log "DEBUG" "$@"
    fi
}

# ----------------------------------------------------------------------------
# DEPENDENCY CHECKS
# ----------------------------------------------------------------------------

check_dependencies() {
    local missing_deps=()

    # Check for jq
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi

    # Check for Node.js/npx
    if ! command -v npx &> /dev/null; then
        if ! command -v node &> /dev/null; then
            missing_deps+=("node/npx")
        fi
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        echo "Error: Missing required dependencies: ${missing_deps[*]}" >&2
        echo "Please install them to use the formatter plugin" >&2
        exit 2
    fi
}

# ----------------------------------------------------------------------------
# FILE VALIDATION
# ----------------------------------------------------------------------------

is_supported_file() {
    local file="$1"
    local extension="${file##*.}"

    for supported_ext in "${SUPPORTED_EXTENSIONS[@]}"; do
        if [[ "$extension" == "$supported_ext" ]]; then
            return 0
        fi
    done

    return 1
}

should_format_file() {
    local file="$1"

    # Check if file exists and is readable
    if [[ ! -f "$file" ]]; then
        log_debug "File not found: $file"
        return 1
    fi

    if [[ ! -r "$file" ]]; then
        log_error "File not readable: $file"
        return 1
    fi

    # Check file size
    local file_size_kb=$(du -k "$file" | cut -f1)
    if [[ $file_size_kb -gt $MAX_FILE_SIZE_KB ]]; then
        log_info "Skipping large file (${file_size_kb}KB): $file"
        return 1
    fi

    # Check if it's a supported file type
    if ! is_supported_file "$file"; then
        log_debug "Unsupported file type: $file"
        return 1
    fi

    # Check for .prettierignore
    if [[ -f "${file%/*}/.prettierignore" ]]; then
        if grep -q "^$(basename "$file")$" "${file%/*}/.prettierignore" 2>/dev/null; then
            log_info "File excluded by .prettierignore: $file"
            return 1
        fi
    fi

    # Skip node_modules, dist, build directories
    if [[ "$file" == *"node_modules"* ]] || \
       [[ "$file" == *"dist"* ]] || \
       [[ "$file" == *"build"* ]] || \
       [[ "$file" == *".min."* ]]; then
        log_debug "Skipping generated/vendor file: $file"
        return 1
    fi

    return 0
}

# ----------------------------------------------------------------------------
# PRETTIER FORMATTING
# ----------------------------------------------------------------------------

get_prettier_command() {
    local file="$1"
    local prettier_cmd=""

    # Check for local prettier first
    if [[ -f "node_modules/.bin/prettier" ]]; then
        prettier_cmd="node_modules/.bin/prettier"
        log_debug "Using local prettier"
    elif command -v prettier &> /dev/null; then
        prettier_cmd="prettier"
        log_debug "Using global prettier"
    elif command -v npx &> /dev/null; then
        prettier_cmd="npx --no-install prettier"
        log_debug "Using npx --no-install prettier"
    else
        log_error "Prettier not found"
        return 1
    fi

    echo "$prettier_cmd"
}

format_file() {
    local file="$1"
    local prettier_cmd

    prettier_cmd=$(get_prettier_command "$file")
    if [[ -z "$prettier_cmd" ]]; then
        log_error "Cannot find prettier to format: $file"
        return 4
    fi

    # Check for local .prettierrc
    local config_options=""
    if [[ -f ".prettierrc" ]] || [[ -f ".prettierrc.json" ]] || [[ -f ".prettierrc.js" ]]; then
        log_debug "Using local prettier config"
    else
        config_options="$PRETTIER_OPTIONS"
    fi

    log_info "Formatting: $file"

    # Create backup for safety (deleted on success)
    local backup_file="${file}.formatter-backup"
    cp "$file" "$backup_file" 2>/dev/null || true

    # Run prettier
    if $prettier_cmd --write $config_options "$file" 2>> "$LOG_FILE"; then
        rm -f "$backup_file"  # Remove backup on success
        log_info "Successfully formatted: $file"
        echo "✓ Formatted: $file"
        return 0
    else
        # Restore from backup on failure
        if [[ -f "$backup_file" ]]; then
            mv "$backup_file" "$file"
        fi
        log_error "Failed to format: $file"
        echo "✗ Failed to format: $file" >&2
        return 4
    fi
}

# ----------------------------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------------------------

main() {
    log_info "Formatter hook started"
    log_debug "Working directory: $(pwd)"

    # Native Claude does not interpret this plugin's enabled metadata. The
    # script makes the documented switch an actual application control.
    if command -v jq >/dev/null 2>&1 && ! jq -e \
        '[.hooks.PostToolUse[]? | select(.matcher == "Write|Edit") | .enabled] | length > 0 and all(. == true)' \
        "$PLUGIN_ROOT/hooks/hooks.json" >/dev/null 2>&1; then
        exit 0
    fi

    # Check dependencies
    check_dependencies

    # Read hook data from stdin
    local hook_data
    if ! hook_data=$(cat); then
        log_error "Failed to read hook data from stdin"
        exit 1
    fi

    log_debug "Received formatter hook event"

    # Read the native event first; retain legacy payloads for manual callers.
    local file
    if ! file=$(printf '%s' "$hook_data" | jq -er '
        if has("hook_event_name") then
            if .hook_event_name == "PostToolUse" and
               (.tool_name == "Write" or .tool_name == "Edit") then
                (.tool_input.file_path // .tool_response.filePath // empty)
            else empty end
        else
            (.toolOutput.file // .toolOutput.path // .toolOutput.file_path // .file // .path // .filename // empty)
        end | select(type == "string" and length > 0)
    ' 2>/dev/null); then
        exit 0
    fi

    if [[ -z "$file" ]]; then
        log_debug "No file path found in hook data"
        exit 0  # Not an error, just no file to format
    fi

    log_info "Processing file: $file"

    # Check if we should format this file
    if ! should_format_file "$file"; then
        log_info "Skipping file: $file"
        exit 0
    fi

    # Format the file
    if format_file "$file"; then
        log_info "Formatter hook completed successfully"
        exit 0
    else
        # Non-critical failure (continue on error is set in hooks.json)
        log_error "Formatter hook failed for: $file"
        exit 4
    fi
}

# ----------------------------------------------------------------------------
# ERROR HANDLING
# ----------------------------------------------------------------------------

# Trap errors and log them
trap 'log_error "Script failed at line $LINENO with exit code $?"' ERR

# ----------------------------------------------------------------------------
# SCRIPT ENTRY POINT
# ----------------------------------------------------------------------------

# Only run main if not being sourced (for testing)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
