#!/usr/bin/env bash
# package_app.sh — turn a SwiftPM executable target into a distributable
# .app bundle and an unsigned .dmg, without needing an Xcode project.
#
# Usage:
#   scripts/package_app.sh [options]
#
# Run from the root of a SwiftPM repo (the directory containing Package.swift),
# or pass --repo-root explicitly.
set -euo pipefail
# bash 5.2+ treats '&' in a ${var//pattern/replacement} as "the matched text";
# every replacement below must stay literal, so switch that off (older bash
# does not have the option and behaves literally anyway).
shopt -u patsub_replacement 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_PLIST="${SCRIPT_DIR}/../assets/Info.plist.template"

usage() {
    cat <<'USAGE'
package_app.sh — package a SwiftPM executable as a .app bundle + unsigned .dmg

Options (all have env-var equivalents shown in parens):
  --repo-root PATH        Repo root containing Package.swift (REPO_ROOT). Default: cwd.
  --app-name NAME         App / bundle display name (APP_NAME). Default: auto-detected
                          from the first executable product in Package.swift.
  --product NAME          Swift product name to build, if different from --app-name
                          (PRODUCT_NAME). Default: same as --app-name.
  --bundle-id ID          CFBundleIdentifier (BUNDLE_ID). Default: com.example.<app-name, lowercased>.
  --version STRING        CFBundleVersion / CFBundleShortVersionString (VERSION). Default: 0.1.0.
  --min-os STRING         LSMinimumSystemVersion (MIN_MACOS_VERSION). Default: 13.0.
  --menu-bar              Set LSUIElement=true (no Dock icon, menu-bar-only app) (MENU_BAR_APP=1).
  --icon PATH             Path to a .icns file to embed as CFBundleIconFile (ICON_PATH).
                          Default: <repo-root>/assets/<app-name>.icns if it exists, else none.
  --output-dir PATH       Where to write the timestamped build output (OUTPUT_DIR).
                          Default: <repo-root>/dist.
  --skip-dmg              Build the .app bundle only; skip DMG creation.
  -h, --help              Show this help and exit.

Input rules (the script refuses anything else, to keep paths and the plist safe):
  app/product name   1-255 chars: letters, digits, space, '.', '_', '-'. Must start
                     with a letter or digit, must not end with a space or '.', and
                     must not contain a '..' component. No '/', '\', ':' or control chars.
  bundle id          reverse-DNS: two or more dot-separated labels of letters,
                     digits and '-' (e.g. com.example.myapp), max 255 chars.
  version / min-os   1-3 dot-separated numeric components (e.g. 1.2.3, 13.0).

Examples:
  scripts/package_app.sh
  scripts/package_app.sh --app-name MyMenuBarApp --menu-bar --bundle-id com.acme.mymenubarapp
  scripts/package_app.sh --icon assets/MyApp.icns --version 1.2.0 --min-os 14.0
USAGE
}

die() {
    printf 'error: %s\n' "$*" >&2
    exit 1
}

# ---- input validation ------------------------------------------------------
# All matching is done in the C locale inside a subshell so character ranges
# mean plain ASCII regardless of the caller's LANG/LC_ALL settings.
matches() {
    ( export LC_ALL=C; [[ "$1" =~ $2 ]] )
}

has_control_chars() {
    ( export LC_ALL=C; [[ "$1" =~ [[:cntrl:]] ]] )
}

# Names end up as file names, directory names, the DMG volume name and several
# plist strings, so they get the strictest treatment.
validate_name() {
    local label="$1" value="$2"
    local re='^[A-Za-z0-9][A-Za-z0-9 ._-]*$'
    [[ -n "${value}" ]] || die "${label} must not be empty."
    [[ ${#value} -le 255 ]] || die "${label} is longer than 255 characters."
    if has_control_chars "${value}"; then
        die "${label} contains control characters."
    fi
    case "${value}" in
        */*|*\\*|*:*)
            die "${label} must not contain path separators or ':' (got '${value}')." ;;
        .|..)
            die "${label} must not be a '.' or '..' path component (got '${value}')." ;;
        *" "|*.)
            die "${label} must not end with a space or '.' (got '${value}')." ;;
    esac
    if ! matches "${value}" "${re}"; then
        die "${label} may only contain letters, digits, spaces, '.', '_' and '-', and must start with a letter or digit (got '${value}')."
    fi
    # A '..' surrounded by allowed characters (e.g. "a..b") is a legal file name,
    # but reject a name that is *only* dots/spaces to be safe with mkdir/cp.
    if matches "${value}" '^[. ]+$'; then
        die "${label} must contain at least one letter or digit (got '${value}')."
    fi
}

validate_bundle_id() {
    local value="$1"
    local re='^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$'
    [[ -n "${value}" ]] || die "bundle id must not be empty."
    [[ ${#value} -le 255 ]] || die "bundle id is longer than 255 characters."
    if ! matches "${value}" "${re}"; then
        die "bundle id must be reverse-DNS (letters, digits, '-' in two or more dot-separated labels), e.g. com.example.myapp (got '${value}')."
    fi
}

validate_version() {
    local label="$1" value="$2"
    local re='^[0-9]+(\.[0-9]+){0,2}$'
    [[ -n "${value}" ]] || die "${label} must not be empty."
    if ! matches "${value}" "${re}"; then
        die "${label} must be 1-3 dot-separated numbers, e.g. 1.2.3 (got '${value}')."
    fi
}

# Escape the five XML special characters so a value can never open or close a
# plist element. Validation above already rules these out for names and ids;
# escaping is defence in depth for every value written into the plist.
xml_escape() {
    local s="$1"
    shopt -u patsub_replacement 2>/dev/null || true
    s="${s//&/&amp;}"
    s="${s//</&lt;}"
    s="${s//>/&gt;}"
    s="${s//\"/&quot;}"
    s="${s//\'/&apos;}"
    printf '%s' "${s}"
}

# ---- defaults (overridable by env vars, then by flags) ---------------------
REPO_ROOT="${REPO_ROOT:-$(pwd)}"
APP_NAME="${APP_NAME:-}"
PRODUCT_NAME="${PRODUCT_NAME:-}"
BUNDLE_ID="${BUNDLE_ID:-}"
VERSION="${VERSION:-0.1.0}"
MIN_MACOS_VERSION="${MIN_MACOS_VERSION:-13.0}"
MENU_BAR_APP="${MENU_BAR_APP:-0}"
ICON_PATH="${ICON_PATH:-}"
OUTPUT_DIR="${OUTPUT_DIR:-}"
SKIP_DMG=0

# ---- flag parsing ------------------------------------------------------
need_value() {
    [[ $# -ge 2 ]] || die "option $1 requires a value."
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo-root) need_value "$@"; REPO_ROOT="$2"; shift 2 ;;
        --app-name) need_value "$@"; APP_NAME="$2"; shift 2 ;;
        --product) need_value "$@"; PRODUCT_NAME="$2"; shift 2 ;;
        --bundle-id) need_value "$@"; BUNDLE_ID="$2"; shift 2 ;;
        --version) need_value "$@"; VERSION="$2"; shift 2 ;;
        --min-os) need_value "$@"; MIN_MACOS_VERSION="$2"; shift 2 ;;
        --menu-bar) MENU_BAR_APP=1; shift ;;
        --icon) need_value "$@"; ICON_PATH="$2"; shift 2 ;;
        --output-dir) need_value "$@"; OUTPUT_DIR="$2"; shift 2 ;;
        --skip-dmg) SKIP_DMG=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "error: unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
done

# ---- tool validation -----------------------------------------------------
for tool in swift hdiutil; do
    if ! command -v "${tool}" >/dev/null 2>&1; then
        echo "error: required tool '${tool}' not found on PATH." >&2
        echo "       Install Xcode Command Line Tools: xcode-select --install" >&2
        exit 1
    fi
done

[[ -d "${REPO_ROOT}" ]] || die "repo root does not exist or is not a directory: ${REPO_ROOT}"
REPO_ROOT="$(cd "${REPO_ROOT}" && pwd)"
PACKAGE_SWIFT="${REPO_ROOT}/Package.swift"
if [[ ! -f "${PACKAGE_SWIFT}" ]]; then
    echo "error: no Package.swift found at ${REPO_ROOT}." >&2
    echo "       Run this from a SwiftPM repo root, or pass --repo-root." >&2
    exit 1
fi

# ---- auto-detect app name from Package.swift if not supplied -------------
if [[ -z "${APP_NAME}" ]]; then
    APP_NAME="$(grep -m1 -E '\.executable\([[:space:]]*name:[[:space:]]*"' "${PACKAGE_SWIFT}" \
        | sed -E 's/.*name:[[:space:]]*"([^"]+)".*/\1/' || true)"
    if [[ -z "${APP_NAME}" ]]; then
        echo "error: could not auto-detect app name from Package.swift." >&2
        echo "       Pass it explicitly with --app-name NAME." >&2
        exit 1
    fi
fi

PRODUCT_NAME="${PRODUCT_NAME:-${APP_NAME}}"
BUNDLE_ID="${BUNDLE_ID:-com.example.$(printf '%s' "${APP_NAME}" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9.\n-' '-')}"
OUTPUT_DIR="${OUTPUT_DIR:-${REPO_ROOT}/dist}"

# ---- validate every user-controlled value before touching the filesystem --
validate_name "app name" "${APP_NAME}"
validate_name "product name" "${PRODUCT_NAME}"
validate_bundle_id "${BUNDLE_ID}"
validate_version "version" "${VERSION}"
validate_version "minimum macOS version" "${MIN_MACOS_VERSION}"

if [[ -z "${ICON_PATH}" && -f "${REPO_ROOT}/assets/${APP_NAME}.icns" ]]; then
    ICON_PATH="${REPO_ROOT}/assets/${APP_NAME}.icns"
fi
if [[ -n "${ICON_PATH}" && ! -f "${ICON_PATH}" ]]; then
    die "--icon path does not exist or is not a regular file: ${ICON_PATH}"
fi

LSUIELEMENT_BOOL="false"
if [[ "${MENU_BAR_APP}" == "1" ]]; then
    LSUIELEMENT_BOOL="true"
fi

if [[ ! -f "${TEMPLATE_PLIST}" ]]; then
    die "Info.plist template not found at ${TEMPLATE_PLIST}."
fi

echo "App name:     ${APP_NAME}"
echo "Product:      ${PRODUCT_NAME}"
echo "Bundle ID:    ${BUNDLE_ID}"
echo "Version:      ${VERSION}"
echo "Min macOS:    ${MIN_MACOS_VERSION}"
echo "Menu-bar app: $([[ "${MENU_BAR_APP}" == "1" ]] && echo yes || echo no)"
echo "Icon:         ${ICON_PATH:-<none>}"

# ---- layout ---------------------------------------------------------------
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BUILD_OUTPUT="${OUTPUT_DIR}/${APP_NAME}-${VERSION}-unsigned-${TIMESTAMP}"
APP_BUNDLE="${BUILD_OUTPUT}/${APP_NAME}.app"
DMG_STAGING="${BUILD_OUTPUT}/dmg"
DMG_PATH="${BUILD_OUTPUT}/${APP_NAME}-${VERSION}-unsigned.dmg"

# The DMG staging copy is always scratch. A partially assembled build output
# directory is removed on failure so a broken run never leaves a half-built
# .app behind that looks distributable.
BUILD_OUTPUT_CREATED=0
cleanup() {
    local status=$?
    rm -rf "${DMG_STAGING}"
    if [[ ${status} -ne 0 && "${BUILD_OUTPUT_CREATED}" == "1" ]]; then
        echo "Build failed; removing partial output ${BUILD_OUTPUT}" >&2
        rm -rf "${BUILD_OUTPUT}"
    fi
}
trap cleanup EXIT

cd "${REPO_ROOT}"

# ---- build ------------------------------------------------------------
swift build -c release --product "${PRODUCT_NAME}"
BIN_DIR="$(swift build -c release --show-bin-path)"

if [[ ! -f "${BIN_DIR}/${PRODUCT_NAME}" ]]; then
    die "built binary not found at ${BIN_DIR}/${PRODUCT_NAME}."
fi

# ---- bundle -----------------------------------------------------------
mkdir -p "${APP_BUNDLE}/Contents/MacOS"
mkdir -p "${APP_BUNDLE}/Contents/Resources"
BUILD_OUTPUT_CREATED=1

cp "${BIN_DIR}/${PRODUCT_NAME}" "${APP_BUNDLE}/Contents/MacOS/${APP_NAME}"
chmod 755 "${APP_BUNDLE}/Contents/MacOS/${APP_NAME}"

HAS_ICON=0
if [[ -n "${ICON_PATH}" ]]; then
    cp "${ICON_PATH}" "${APP_BUNDLE}/Contents/Resources/${APP_NAME}.icns"
    HAS_ICON=1
fi

# Render the plist line by line in plain bash: the @@ICON_BLOCK@@ marker line
# expands to zero or two lines, and every scalar placeholder is replaced with
# its XML-escaped value. No sed/awk means no delimiter or metacharacter in a
# value can change the substitution itself.
APP_NAME_XML="$(xml_escape "${APP_NAME}")"
BUNDLE_ID_XML="$(xml_escape "${BUNDLE_ID}")"
VERSION_XML="$(xml_escape "${VERSION}")"
MIN_MACOS_VERSION_XML="$(xml_escape "${MIN_MACOS_VERSION}")"

{
    while IFS= read -r plist_line || [[ -n "${plist_line}" ]]; do
        case "${plist_line}" in
            *"@@ICON_BLOCK@@"*)
                if [[ "${HAS_ICON}" == "1" ]]; then
                    printf '    <key>CFBundleIconFile</key>\n    <string>%s</string>\n' "${APP_NAME_XML}"
                fi
                ;;
            *)
                plist_line="${plist_line//__APP_NAME__/${APP_NAME_XML}}"
                plist_line="${plist_line//__BUNDLE_ID__/${BUNDLE_ID_XML}}"
                plist_line="${plist_line//__VERSION__/${VERSION_XML}}"
                plist_line="${plist_line//__MIN_MACOS_VERSION__/${MIN_MACOS_VERSION_XML}}"
                plist_line="${plist_line//__LSUIELEMENT_BOOL__/${LSUIELEMENT_BOOL}}"
                printf '%s\n' "${plist_line}"
                ;;
        esac
    done < "${TEMPLATE_PLIST}"
} > "${APP_BUNDLE}/Contents/Info.plist"

# Prove the rendered plist is well-formed where a checker is available.
if command -v plutil >/dev/null 2>&1; then
    plutil -lint "${APP_BUNDLE}/Contents/Info.plist" >/dev/null \
        || die "rendered Info.plist failed plutil -lint"
fi

# Clear extended attributes / quarantine flags picked up from the template or
# copied resources, and touch the bundle so Finder/LaunchServices don't serve
# a stale cached icon for a rebuilt app of the same name.
xattr -cr "${APP_BUNDLE}" 2>/dev/null || true
touch "${APP_BUNDLE}"

echo "App bundle:   ${APP_BUNDLE}"

# ---- dmg ----------------------------------------------------------------
if [[ "${SKIP_DMG}" == "1" ]]; then
    echo "Skipping DMG creation (--skip-dmg)."
    exit 0
fi

mkdir -p "${DMG_STAGING}"
cp -R "${APP_BUNDLE}" "${DMG_STAGING}/${APP_NAME}.app"
ln -s /Applications "${DMG_STAGING}/Applications"

hdiutil create \
    -volname "${APP_NAME}" \
    -srcfolder "${DMG_STAGING}" \
    -ov \
    -format UDZO \
    "${DMG_PATH}"

[[ -s "${DMG_PATH}" ]] || die "hdiutil reported success but no DMG was written at ${DMG_PATH}"

echo "Unsigned DMG: ${DMG_PATH}"
