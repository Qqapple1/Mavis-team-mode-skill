#!/usr/bin/env bash
# Package Mavis Team Mode skill for different platforms.
#
# Produces 5 archives under dist/:
#   1. {ver}-core.zip          - Cross-platform core (no installer scripts)
#                                38 files: SKILL.md + agents + examples + ...
#                                For: browsing source, embedding into other tools
#   2. {ver}-bash.tar.gz       - bash + cross-platform (Linux/macOS/Git Bash/WSL)
#                                41 files: core + install.sh + validate.sh + package.sh
#                                For: most users on Unix-like systems
#   3. {ver}-windows.zip       - PowerShell + cross-platform
#                                41 files: core + install.ps1 + validate.ps1 + run_e2e.ps1
#                                For: Windows users without Git Bash
#   4. {ver}-source.tar.gz     - Full source (including CI workflow + Issue templates)
#                                48 files: everything
#                                For: contributors, CI, GitHub release auto-attach
#   5. {ver}-source.zip        - Same as 4 but zip (for Windows contributors)
#
# Usage:
#   bash scripts/package.sh                  # uses version from SKILL.md
#   bash scripts/package.sh --version=1.3.12  # override version
#   bash scripts/package.sh --dry-run        # show what would be packaged, no write

set -euo pipefail

# ---- Args ----
VERSION_OVERRIDE=""
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --version=*) VERSION_OVERRIDE="${arg#*=}" ;;
    --dry-run)   DRY_RUN=1 ;;
    --help|-h)
      sed -n '2,25p' "$0"
      exit 0
      ;;
    *) echo "Unknown arg: $arg (try --help)" >&2; exit 1 ;;
  esac
done

# ---- Locate repo root ----
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# ---- Detect version ----
if [ -n "$VERSION_OVERRIDE" ]; then
  VERSION="$VERSION_OVERRIDE"
else
  VERSION=$(grep '^version:' SKILL.md | head -1 | awk '{print $2}' | tr -d '"' | tr -d "'")
  if [ -z "$VERSION" ]; then
    echo "ERROR: could not detect version from SKILL.md, use --version=X.Y.Z" >&2
    exit 1
  fi
fi

NAME="mavis-team-mode-skill"
DIST="$REPO_ROOT/dist"
STAGE="$REPO_ROOT/.package-stage"

# ---- OS noise filter (excluded from any archive) ----
# These are accidental artifacts that pollute release archives if a
# developer builds on macOS or Windows. Filter them out before staging.
OS_NOISE_FILES=(
  ".DS_Store"
  "Thumbs.db"
  "desktop.ini"
  ".AppleDouble"
  ".LSOverride"
  "._*"
)

# Filter helper: returns the input array with any OS-noise entries removed.
filter_noise() {
  local item
  for item in "$@"; do
    local base
    base=$(basename "$item")
    local skip=0
    for noise in "${OS_NOISE_FILES[@]}"; do
      # shellcheck disable=SC2053  # intentional glob compare
      if [[ "$base" == $noise ]]; then
        skip=1
        break
      fi
    done
    if [ "$skip" = "0" ]; then
      printf '%s\n' "$item"
    fi
  done
}

# ---- Clean ----
if [ "$DRY_RUN" = "0" ]; then
  rm -rf "$DIST" "$STAGE"
  mkdir -p "$DIST"
fi

# ---- File classification ----
# All files are listed RELATIVE to REPO_ROOT.
# Each list is independent — pick one to package.

# CORE: cross-platform files (no installer)
CORE_FILES=(
  SKILL.md
  README.md
  INSTALL.md
  VALIDATION.md
  CHANGELOG.md
  CONTRIBUTING.md
  SECURITY.md
  LICENSE
  index.html
  Makefile
  .gitignore
  .shellcheckrc
  agents/leader.md
  agents/verifier.md
  agents/worker-coder.md
  agents/worker-tester.md
  agents/worker-researcher.md
  agents/worker-doc-writer.md
  agents/worker-reviewer.md
  examples/bug-hunt.md
  examples/new-feature.md
  examples/refactor-large-module.md
  examples/research-then-implement.md
  examples/prototype-todo-app/README.md
  examples/prototype-todo-app/server/server.py
  examples/prototype-todo-app/client/index.html
  examples/prototype-todo-app/test_e2e.py
  examples/prototype-todo-app/test_e2e_extended.py
  examples/prototype-todo-app/test_e2e_advanced.py
  references/verification-checklist.md
  references/troubleshooting.md
  references/deepseek-setup.md
  docs/ADR-001-team-mode-recreation.md
  docs/ADR-002-security.md
  docs/ARCHITECTURE.md
  docs/PERFORMANCE.md
  docs/PLATFORMS.md
  scripts/validate_yaml.py
  scripts/benchmark_tokens.py
)

# BASH: add bash installer + validator + packager
BASH_FILES=(
  "${CORE_FILES[@]}"
  scripts/install.sh
  scripts/validate.sh
  scripts/package.sh
)

# WINDOWS: add PowerShell scripts + Windows-specific docs
WINDOWS_FILES=(
  "${CORE_FILES[@]}"
  scripts/install.ps1
  scripts/validate.ps1
  examples/prototype-todo-app/run_e2e.ps1
  docs/WINDOWS.md
)

# SOURCE: everything (adds CI + Issue templates)
SOURCE_FILES=(
  "${BASH_FILES[@]}"
  "${WINDOWS_FILES[@]}"  # includes all PS files + WINDOWS.md
  .github/ISSUE_TEMPLATE/bug_report.md
  .github/ISSUE_TEMPLATE/feature_request.md
  .github/workflows/validate-skill.yml
)
# Dedupe source list. macOS still ships bash 3.2 by default, and
# bash 3.2 has no `mapfile` / `readarray` builtins. Use a portable
# `while read` loop instead (works on bash 3.2+).
deduped=()
while IFS= read -r line; do
  deduped+=("$line")
done < <(printf '%s\n' "${SOURCE_FILES[@]}" | sort -u)
SOURCE_FILES=("${deduped[@]}")
unset deduped

# ---- Sanity check ----
missing=0
for f in "${SOURCE_FILES[@]}"; do
  if [ ! -e "$f" ]; then
    echo "ERROR: file in package list but not on disk: $f" >&2
    missing=$((missing+1))
  fi
done
if [ "$missing" -gt 0 ]; then
  echo "Aborting: $missing missing files" >&2
  exit 1
fi

# ---- Tar/zip helper ----
package() {
  local label="$1"
  local outname="$2"   # basename for display (e.g. "bash", "windows")
  local outfile="$3"
  local format="$4"  # tar.gz | zip
  shift 4
  local files=("$@")

  echo
  echo "=== $label ==="
  echo "  Files: ${#files[@]}"
  echo "  Output: $outfile"
  echo "  Format: $format"

  if [ "$DRY_RUN" = "1" ]; then
    printf '    %s\n' "${files[@]}"
    return
  fi

  # Stage files into a clean dir
  rm -rf "$STAGE"
  mkdir -p "$STAGE/$NAME-$VERSION"
  local staged_count=0
  local skipped_noise=()
  for f in "${files[@]}"; do
    local base
    base=$(basename "$f")
    local skip=0
    for noise in "${OS_NOISE_FILES[@]}"; do
      # shellcheck disable=SC2053  # intentional glob compare
      if [[ "$base" == $noise ]]; then
        skip=1
        skipped_noise+=("$f")
        break
      fi
    done
    if [ "$skip" = "1" ]; then
      continue
    fi
    # Preserve directory structure
    mkdir -p "$STAGE/$NAME-$VERSION/$(dirname "$f")"
    cp "$f" "$STAGE/$NAME-$VERSION/$f"
    staged_count=$((staged_count + 1))
  done
  if [ "${#skipped_noise[@]}" -gt 0 ]; then
    echo "  Filtered ${#skipped_noise[@]} OS noise file(s): ${skipped_noise[*]}"
  fi

  # Verify chmod +x for scripts (so users can run after untar)
  # Only mark executables for the appropriate platform
  case "$label" in
    *bash*)
      chmod +x "$STAGE/$NAME-$VERSION/scripts/install.sh" \
               "$STAGE/$NAME-$VERSION/scripts/validate.sh" \
               "$STAGE/$NAME-$VERSION/scripts/package.sh" 2>/dev/null || true
      ;;
    *Windows*)
      # PS1 doesn't need +x
      ;;
    *source*)
      chmod +x "$STAGE/$NAME-$VERSION/scripts/install.sh" \
               "$STAGE/$NAME-$VERSION/scripts/validate.sh" \
               "$STAGE/$NAME-$VERSION/scripts/package.sh" 2>/dev/null || true
      ;;
  esac

  # Write a small README inside the package pointing to right installer
  cat > "$STAGE/$NAME-$VERSION/PACKAGE.txt" <<EOF
Mavis Team Mode Skill v$VERSION
Package: $label
Files:   ${#files[@]}

To install, see INSTALL.md and pick the right command for your platform.

Quick reference:
  macOS / Linux / Git Bash / WSL:
    bash scripts/install.sh

  Windows PowerShell:
    powershell -ExecutionPolicy Bypass -File scripts/install.ps1

  Manual (any platform):
    See INSTALL.md, section "manual git clone + symlink"

Repository: https://github.com/Qqapple1/Mavis-team-mode-skill
EOF

  # Build archive
  case "$format" in
    tar.gz)
      (cd "$STAGE" && tar -czf "$outfile" "$NAME-$VERSION")
      ;;
    zip)
      (cd "$STAGE" && zip -qr "$outfile" "$NAME-$VERSION")
      ;;
  esac

  # Show size
  if [ -f "$outfile" ]; then
    local size
    size=$(du -h "$outfile" 2>/dev/null | awk '{print $1}')
    # outname is the short variant id (e.g. "bash", "windows") used for log filtering
    echo "  Size: $size  (variant: ${outname})"
  else
    echo "  ERROR: archive not created!" >&2
    exit 1
  fi

  # Self-test: verify archive is openable and contains expected files.
  # Counts the entries that start with our package prefix.
  local actual_count
  case "$format" in
    tar.gz)
      actual_count=$(tar -tzf "$outfile" 2>/dev/null | grep -c "^$NAME-$VERSION/" || true)
      ;;
    zip)
      # Last line of `unzip -l` looks like:
      #   "   205861                     48 files"
      # Field NF-1 is the count when the last field is "files".
      actual_count=$(unzip -l "$outfile" 2>/dev/null | awk '$NF=="files" {print $(NF-1); exit}')
      ;;
  esac
  # Archive should contain at least every staged file (plus implicit dir
  # entries for zip). We only require >= staged_count; an exact equality
  # check is too brittle across tar/zip versions.
  if [ -z "$actual_count" ] || [ "$actual_count" -lt "$staged_count" ]; then
    echo "  ERROR: archive contains $actual_count entries, expected >= $staged_count (after noise filter)" >&2
    exit 1
  fi
  echo "  Self-test: archive opens, $actual_count entries (staged: $staged_count files)"
}

# ---- Build all 4 packages ----
CORE_OUT="$DIST/${NAME}-${VERSION}-core.zip"
BASH_OUT="$DIST/${NAME}-${VERSION}-bash.tar.gz"
WIN_OUT="$DIST/${NAME}-${VERSION}-windows.zip"
SRC_TGZ="$DIST/${NAME}-${VERSION}-source.tar.gz"
SRC_ZIP="$DIST/${NAME}-${VERSION}-source.zip"

package "Core (cross-platform, no installer)" "core"     "$CORE_OUT" zip  "${CORE_FILES[@]}"
package "Bash (Linux/macOS/Git Bash/WSL)"     "bash"     "$BASH_OUT" tar.gz "${BASH_FILES[@]}"
package "Windows (PowerShell native)"          "windows"  "$WIN_OUT"  zip  "${WINDOWS_FILES[@]}"
package "Source (full + CI)"                   "source"   "$SRC_TGZ"  tar.gz "${SOURCE_FILES[@]}"
package "Source (full + CI, zip)"              "source-zip" "$SRC_ZIP" zip  "${SOURCE_FILES[@]}"

# ---- Checksums ----
if [ "$DRY_RUN" = "0" ]; then
  echo
  echo "=== SHA256 checksums ==="
  cd "$DIST"
  for f in *.zip *.tar.gz; do
    [ -f "$f" ] || continue
    sha256sum "$f" 2>/dev/null || shasum -a 256 "$f" 2>/dev/null
  done > SHA256SUMS
  cat SHA256SUMS
fi

# ---- Done ----
echo
echo "=== Done ==="
echo "Output: $DIST/"
ls -la "$DIST/" 2>/dev/null

# ---- Cleanup stage ----
rm -rf "$STAGE"
