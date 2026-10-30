#!/bin/bash

# validate-format.sh - Pre-format validation script
# Checks if files are already properly formatted to avoid unnecessary changes
# Part of the formatter plugin for Claude Code
# Version: 1.0.0
# Author: Claude Code Formatter Plugin

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
DEBUG="${FORMATTER_DEBUG:-false}"
LOG_FILE="${PLUGIN_ROOT}/logs/validate.log"

# This optional native hook is disabled by default. Claude tolerates but does
# not enforce group-level enabled metadata, so skip before logs or npx calls.
# Explicit filename / CLAUDE_FILE_PATH invocations remain manual checks.
if [[ $# -eq 0 && -z "${CLAUDE_FILE_PATH:-}" ]]; then
    if ! command -v jq >/dev/null 2>&1 || ! jq -e \
        '[.hooks.PreToolUse[]? | select(.matcher == "Edit") | .enabled] | length > 0 and all(. == true)' \
        "$PLUGIN_ROOT/hooks/hooks.json" >/dev/null 2>&1; then
        exit 0
    fi
    if ! FILE_TO_VALIDATE=$(jq -er '
        select(.hook_event_name == "PreToolUse" and .tool_name == "Edit") |
        .tool_input.file_path | select(type == "string" and length > 0)
    '); then
        exit 0
    fi
    set -- "$FILE_TO_VALIDATE"
fi

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
COLOR_RESET='\033[0m' # No Color

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Debug logging
debug() {
    if [ "$DEBUG" = "true" ]; then
        echo "[DEBUG] $(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
    fi
}

# Info logging
info() {
    echo -e "${BLUE}[INFO]${COLOR_RESET} $1"
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Success logging
success() {
    echo -e "${GREEN}[SUCCESS]${COLOR_RESET} $1"
    echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Warning logging
warn() {
    echo -e "${YELLOW}[WARN]${COLOR_RESET} $1"
    echo "[WARN] $(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Error logging
error() {
    echo -e "${RED}[ERROR]${COLOR_RESET} $1"
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if file should be validated
should_validate() {
    local file="$1"
    local ext="${file##*.}"

    # Supported extensions
    case "$ext" in
        js|jsx|ts|tsx|json|css|scss|less|md|mdx|yaml|yml|html|vue|svelte)
            return 0
            ;;
        *)
            debug "Skipping unsupported file type: $ext"
            return 1
            ;;
    esac
}

# Check if prettier is available
check_prettier() {
    if command -v prettier > /dev/null 2>&1; then
        debug "Found global prettier"
        echo "prettier"
    elif command -v npx > /dev/null 2>&1; then
        if npx --no-install prettier --version > /dev/null 2>&1; then
            debug "Using npx --no-install prettier"
            echo "npx --no-install prettier"
        else
            debug "Prettier not found via npx"
            echo ""
        fi
    else
        debug "No prettier available"
        echo ""
    fi
}

# Validate file formatting
validate_file() {
    local file="$1"
    local prettier_cmd="$2"

    if [ -z "$prettier_cmd" ]; then
        warn "Prettier not available, skipping validation"
        return 0
    fi

    debug "Validating $file with $prettier_cmd"

    # Check if file is already formatted
    if $prettier_cmd --check "$file" > /dev/null 2>&1; then
        success "✓ File is already properly formatted: $(basename "$file")"
        return 0
    else
        warn "⚠ File needs formatting: $(basename "$file")"
        return 1
    fi
}

# Main validation function
main() {
    info "Starting format validation..."
    debug "Plugin root: $PLUGIN_ROOT"
    debug "Script arguments: $*"

    # Check for prettier
    PRETTIER_CMD=$(check_prettier)

    if [ -z "$PRETTIER_CMD" ]; then
        error "Prettier is not installed. Please install it to use format validation."
        error "Install with: npm install -g prettier"
        exit 1
    fi

    debug "Using prettier command: $PRETTIER_CMD"

    # Get file to validate from arguments or environment
    FILE_TO_VALIDATE="${1:-${CLAUDE_FILE_PATH:-}}"

    if [ -z "$FILE_TO_VALIDATE" ]; then
        warn "No file specified for validation"
        exit 0
    fi

    if [ ! -f "$FILE_TO_VALIDATE" ]; then
        error "File not found: $FILE_TO_VALIDATE"
        exit 1
    fi

    # Check if file should be validated
    if ! should_validate "$FILE_TO_VALIDATE"; then
        info "File type not supported for validation: $FILE_TO_VALIDATE"
        exit 0
    fi

    # Validate the file
    if validate_file "$FILE_TO_VALIDATE" "$PRETTIER_CMD"; then
        success "Validation complete - file is properly formatted"
        exit 0
    else
        warn "Validation complete - file needs formatting"
        # Don't fail, just warn
        exit 0
    fi
}

# Run main function
main "$@"
