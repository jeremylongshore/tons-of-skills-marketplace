#!/usr/bin/env bash
#
# make_icns.sh - Build a macOS .icns app icon from a single source image.
#
# Accepts an SVG or PNG (ideally >=1024x1024, square, with ~10% transparent
# margin) and produces a complete .icns via the standard iconutil workflow:
#   source -> 1024px PNG -> .iconset (16/32/64/128/256/512 + @2x) -> .icns
#
# Usage:
#   make_icns.sh <input-image> <output.icns>
#
# Examples:
#   make_icns.sh AppIcon.svg AppIcon.icns
#   make_icns.sh artwork@1024.png build/AppIcon.icns
#
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"

usage() {
  cat <<EOF
Usage: ${SCRIPT_NAME} <input-image> <output.icns>

  <input-image>   Path to a source SVG or PNG. PNG should be >= 1024x1024
                   and square. SVG will be rendered to 1024px PNG first.
  <output.icns>    Path to write the final .icns file (parent dir must exist
                   or will be created).

Examples:
  ${SCRIPT_NAME} AppIcon.svg AppIcon.icns
  ${SCRIPT_NAME} artwork.png build/AppIcon.icns

Requires macOS tools: qlmanage, sips, iconutil, file (all ship with macOS).
EOF
}

log()  { printf '[make_icns] %s\n' "$*" >&2; }
die()  { printf '[make_icns] ERROR: %s\n' "$*" >&2; exit 1; }

if [[ $# -eq 0 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 2 ]]; then
  usage
  die "expected exactly 2 arguments, got $#"
fi

INPUT="$1"
OUTPUT="$2"

# --- Validate environment -------------------------------------------------

for tool in sips iconutil file; do
  command -v "$tool" >/dev/null 2>&1 || die "required tool '$tool' not found (this script requires macOS)"
done

# qlmanage is only required for SVG input; checked lazily below.

[[ -e "$INPUT" ]] || die "input file does not exist: $INPUT"
[[ -r "$INPUT" ]] || die "input file is not readable: $INPUT"
[[ -s "$INPUT" ]] || die "input file is empty: $INPUT"

case "$OUTPUT" in
  *.icns) ;;
  *) die "output path must end in .icns, got: $OUTPUT" ;;
esac

OUTPUT_DIR="$(dirname "$OUTPUT")"
mkdir -p "$OUTPUT_DIR" || die "could not create output directory: $OUTPUT_DIR"

# --- Temp workspace + cleanup ---------------------------------------------

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/make_icns.XXXXXX")" || die "could not create temp dir"
ICONSET="${WORKDIR}/icon.iconset"
mkdir -p "$ICONSET"

cleanup() {
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

# --- Step 1: get a 1024x1024 PNG source -----------------------------------

EXT="${INPUT##*.}"
EXT_LOWER="$(printf '%s' "$EXT" | tr '[:upper:]' '[:lower:]')"
BASE_PNG="${WORKDIR}/source_1024.png"

case "$EXT_LOWER" in
  svg)
    command -v qlmanage >/dev/null 2>&1 || die "qlmanage not found; required to render SVG input (this script requires macOS)"
    log "Rendering SVG to 1024px PNG via qlmanage..."
    # qlmanage writes <basename>.png into -o dir, not the exact path we want.
    if ! qlmanage -t -s 1024 -o "$WORKDIR" "$INPUT" >/dev/null 2>&1; then
      die "qlmanage failed to render '$INPUT'. Try opening it in Preview/a browser first, or flatten it to PNG."
    fi
    QL_NAME="$(basename "$INPUT").png"
    QL_OUTPUT="${WORKDIR}/${QL_NAME}"
    if [[ ! -s "$QL_OUTPUT" ]]; then
      die "qlmanage produced no (or empty) output for '$INPUT'. Common cause: SVG references external files/fonts that qlmanage's sandboxed renderer cannot resolve, producing a blank image. Flatten the SVG (inline all refs) or export a PNG from your design tool instead."
    fi
    cp "$QL_OUTPUT" "$BASE_PNG"
    ;;
  png)
    cp "$INPUT" "$BASE_PNG"
    ;;
  *)
    die "unsupported input format '.$EXT_LOWER'. Provide an .svg or .png file."
    ;;
esac

# --- Step 2: validate dimensions ------------------------------------------

read -r WIDTH HEIGHT < <(sips -g pixelWidth -g pixelHeight "$BASE_PNG" 2>/dev/null \
  | awk '/pixelWidth:/{w=$2} /pixelHeight:/{h=$2} END{print w, h}')

if [[ -z "${WIDTH:-}" || -z "${HEIGHT:-}" ]]; then
  die "could not read image dimensions from '$BASE_PNG' via sips"
fi

log "Source image resolved to ${WIDTH}x${HEIGHT}px"

if [[ "$WIDTH" != "$HEIGHT" ]]; then
  log "WARNING: source is not square (${WIDTH}x${HEIGHT}). sips will scale non-uniformly, distorting the icon. Consider padding to a square canvas first."
fi

if (( WIDTH < 1024 || HEIGHT < 1024 )); then
  log "WARNING: source is ${WIDTH}x${HEIGHT}, smaller than the recommended 1024x1024. Upscaling will soften/blur the largest icon sizes (512, 512@2x). Provide a >=1024px source for best results."
fi

# --- Step 3: generate all iconset sizes -----------------------------------

log "Generating iconset sizes into ${ICONSET}..."

declare -a SIZES=(16 32 128 256 512)

for SZ in "${SIZES[@]}"; do
  sips -z "$SZ" "$SZ" "$BASE_PNG" --out "${ICONSET}/icon_${SZ}x${SZ}.png" >/dev/null
  SZ2X=$(( SZ * 2 ))
  sips -z "$SZ2X" "$SZ2X" "$BASE_PNG" --out "${ICONSET}/icon_${SZ}x${SZ}@2x.png" >/dev/null
done
# 1024 is only needed as the 512@2x variant, already produced above.

log "Iconset contents:"
ls "$ICONSET" | sed 's/^/  /' >&2

# --- Step 4: compile to .icns ----------------------------------------------

log "Compiling .icns via iconutil..."
if ! iconutil -c icns "$ICONSET" -o "$OUTPUT"; then
  die "iconutil failed to compile iconset at '$ICONSET'"
fi

[[ -s "$OUTPUT" ]] || die "iconutil reported success but output file is missing/empty: $OUTPUT"

log "Done: $OUTPUT"
file "$OUTPUT" >&2

exit 0
