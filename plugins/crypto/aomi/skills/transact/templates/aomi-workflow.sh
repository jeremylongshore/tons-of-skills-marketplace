#!/usr/bin/env bash
#
# aomi-workflow.sh — Reusable bash functions for the canonical aomi flow:
#                    chat → list → simulate → sign → verify
#
# Usage:
#   1. Copy this file to your project (or source it from your dotfiles).
#   2. Set USER_ADDR and (optionally) AOMI_CHAIN_ID in your shell environment.
#   3. Source the file: `source aomi-workflow.sh`
#   4. Use the functions below. Each handles a complete flow with safety checks.
#
# Dependencies:
#   - @aomi-labs/client v0.4.2+ (`aomi --version` or `npx @aomi-labs/client@latest --version`)
#   - jq (for tx-list parsing)
#
# Conventions:
#   - All functions return non-zero on failure.
#   - Functions never auto-sign without confirmation.
#   - Credential setup is NOT automated — `aomi wallet set`, `aomi secret add`,
#     `--api-key`, `--private-key` must be run by the user, never by this script.

set -euo pipefail

# ============================================================================
# Configuration (override in your shell, not here)
# ============================================================================

: "${USER_ADDR:?USER_ADDR must be set to your wallet address (0x...)}"
: "${AOMI_CHAIN_ID:=1}"             # Default to Ethereum mainnet
: "${AOMI_CMD:=aomi}"               # Override to "npx @aomi-labs/client@latest" if not installed globally

# ============================================================================
# Detection: aomi vs npx @aomi-labs/client@latest
# ============================================================================

aomi_detect() {
    if command -v aomi >/dev/null 2>&1; then
        AOMI_CMD="aomi"
    else
        AOMI_CMD="npx @aomi-labs/client@latest"
        echo "[aomi-workflow] aomi not found on PATH — using: $AOMI_CMD" >&2
    fi
    echo "[aomi-workflow] using: $AOMI_CMD" >&2
}

aomi_check_version() {
    local version
    version=$($AOMI_CMD --version 2>/dev/null || echo "unknown")
    echo "[aomi-workflow] CLI version: $version" >&2

    case "$version" in
        0.4.[2-9]*|0.4.[1-9][0-9]*|0.[5-9].*|[1-9].*)
            ;;
        *)
            echo "[aomi-workflow] WARNING: version is $version, this script requires 0.4.2+" >&2
            echo "[aomi-workflow] on older builds the account commands and local AA signing differ" >&2
            echo "[aomi-workflow] upgrade with: npm install -g @aomi-labs/client@latest" >&2
            ;;
    esac
}

# ============================================================================
# Core flow: chat → list → simulate → sign → verify
# ============================================================================

# Send an intent and return what's queued.
#
# Usage: aomi_chat "swap 1 USDC for WETH on Uniswap" [--new-session]
aomi_chat() {
    local message="${1:?message required}"
    shift || true

    $AOMI_CMD chat "$message" \
        --public-key "$USER_ADDR" \
        --chain "$AOMI_CHAIN_ID" \
        "$@"
}

# Same, but force a fresh session (use on the FIRST command of a new task).
aomi_chat_new() {
    aomi_chat "$@" --new-session
}

# Print all currently pending tx-N entries.
aomi_pending() {
    $AOMI_CMD tx list
}

# Extract pending tx ids that match `Batch [...] passed`.
# Skips orphans from earlier failed attempts.
aomi_pending_passing() {
    $AOMI_CMD tx list \
        | grep -B1 'Batch.*passed' \
        | grep -oE 'tx-[0-9]+' \
        | sort -u
}

# Simulate a list of tx ids as a batch.
#
# Usage: aomi_simulate tx-1 tx-2
aomi_simulate() {
    if [ $# -eq 0 ]; then
        echo "[aomi-workflow] usage: aomi_simulate tx-1 [tx-2 ...]" >&2
        return 2
    fi
    $AOMI_CMD tx simulate "$@"
}

# Sign a list of tx ids. Confirms with the user first.
#
# Usage: aomi_sign tx-1 tx-2 [extra-flags...]
aomi_sign() {
    if [ $# -eq 0 ]; then
        echo "[aomi-workflow] usage: aomi_sign tx-1 [tx-2 ...] [--rpc-url <url>]" >&2
        return 2
    fi

    echo "[aomi-workflow] About to sign:" >&2
    for arg in "$@"; do
        case "$arg" in
            tx-*) echo "  - $arg" >&2 ;;
        esac
    done

    read -p "Continue? [y/N] " yn
    case "$yn" in
        [Yy]*) $AOMI_CMD tx sign "$@" ;;
        *)     echo "[aomi-workflow] aborted." >&2; return 1 ;;
    esac
}

# Full happy path: simulate the passing batch, then sign it.
#
# Usage: aomi_run_pending
#        aomi_run_pending --rpc-url https://base.publicnode.com    # cross-chain sign
aomi_run_pending() {
    local pending
    pending=$(aomi_pending_passing | tr '\n' ' ')

    if [ -z "$(echo "$pending" | tr -d ' ')" ]; then
        echo "[aomi-workflow] no passing-batch tx ids to sign" >&2
        return 0
    fi

    # shellcheck disable=SC2086
    aomi_simulate $pending

    # shellcheck disable=SC2086
    aomi_sign $pending "$@"
}

# ============================================================================
# Session helpers
# ============================================================================

# List sessions with topics + pending counts.
aomi_sessions() {
    $AOMI_CMD session list
}

# Resume + read pending in one shell call (active-session pointer survives).
#
# Usage: aomi_resume 43
aomi_resume() {
    local sid="${1:?session id required}"
    $AOMI_CMD session resume "$sid" > /dev/null && $AOMI_CMD tx list
}

# Find a session by topic substring and resume it.
#
# Usage: aomi_resume_by_topic "bridge to Base"
aomi_resume_by_topic() {
    local topic="${1:?topic substring required}"
    local sid

    sid=$($AOMI_CMD session list \
        | awk -v topic="$topic" 'index($0, topic) {print $1}' \
        | head -1 \
        | sed 's/session-//')

    if [ -z "$sid" ]; then
        echo "[aomi-workflow] no session matching: $topic" >&2
        return 1
    fi

    aomi_resume "$sid"
}

# Clear the active session pointer (next chat starts fresh).
aomi_close() {
    $AOMI_CMD session close
}

# ============================================================================
# Inspection / debug
# ============================================================================

# Show a brief summary of every session state file (session-N.json) under ~/.aomi/sessions.
aomi_session_dump() {
    local dir="${AOMI_STATE_DIR:-$HOME/.aomi}/sessions"

    if [ ! -d "$dir" ]; then
        echo "[aomi-workflow] no session state dir at $dir" >&2
        return 1
    fi

    for f in "$dir"/session-*.json; do
        [ -f "$f" ] || continue
        jq -r '"\(input_filename | split("/") | last): chainId=\(.chainId) pubkey=\(.publicKey // "—") pending=\(.pendingTxs // [] | length) signed=\(.signedTxs // [] | length)"' "$f"
    done
}

# Replay the active session's conversation (backend-sourced).
aomi_log() {
    $AOMI_CMD session log
}

# ============================================================================
# Example end-to-end usage
# ============================================================================
#
# Single-tx flow (no approve, no batch):
#
#   aomi_detect
#   aomi_check_version
#   aomi_chat_new "stake 0.01 ETH with Lido"
#   aomi_pending
#   aomi_run_pending          # simulates + signs the passing batch
#
# Multi-step batch (approve + swap):
#
#   aomi_chat_new "swap 100 USDC for WETH on Uniswap V3"
#   aomi_run_pending
#
# Cross-chain (queued tx is on Base, override RPC for sign):
#
#   aomi_chat_new "bridge 50 USDC from Ethereum to Base via CCTP"
#   aomi_run_pending --rpc-url https://ethereum-rpc.publicnode.com
#
# Recovery — pending txs from a session that closed:
#
#   aomi_resume_by_topic "bridge to Base"
#   aomi_run_pending
#
# Inspect what's on disk:
#
#   aomi_session_dump
#   aomi_log

# ============================================================================
# If invoked directly (not sourced), run a self-test
# ============================================================================

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    aomi_detect
    aomi_check_version
    echo "[aomi-workflow] sourced functions:"
    echo "  - aomi_chat / aomi_chat_new / aomi_pending / aomi_pending_passing"
    echo "  - aomi_simulate / aomi_sign / aomi_run_pending"
    echo "  - aomi_sessions / aomi_resume / aomi_resume_by_topic / aomi_close"
    echo "  - aomi_session_dump / aomi_log"
    echo
    echo "Usage: source ${BASH_SOURCE[0]:-$0}"
fi
