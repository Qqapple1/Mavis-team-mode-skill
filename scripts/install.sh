#!/usr/bin/env bash
# Install Mavis Team Mode skill into Zcode
#
# Works on:
#   - Linux (any distro with bash 3.2+, git, python3)
#   - macOS (bash 3.2+ works out of the box)
#   - Windows (Git Bash, WSL bash) — symlink may downgrade to copy on Git Bash
#
# Usage:
#   bash install.sh              Install (clone + symlink/copy + verify)
#   bash install.sh --uninstall  Remove the skill
#   bash install.sh --help       Show help
#   bash install.sh --version    Show installer version
#   bash install.sh --doctor     Check current install state without changing
#   bash install.sh --no-verify  Skip post-install verification
#   bash install.sh --copy       Force copy instead of symlink (Windows safe)
#
# Env vars:
#   MAVIS_TEAM_REPO   Git URL to clone (default: GitHub)
#   MAVIS_TEAM_DIR    Where to clone (default: $HOME/mavis-team-mode-skill)
#   MAVIS_TEAM_REF    Git ref to checkout (branch/tag/SHA) after clone
#   MAVIS_TEAM_NO_COLOR  Set to non-empty to disable color output
#   MAVIS_TEAM_FORCE_COPY  Set to non-empty to force copy over symlink
#
# Idempotent: re-running is safe and just `git pull`s + recreates link.

set -euo pipefail

# ---- Version ----
INSTALLER_VERSION="1.3.7"

# ---- Platform detection ----
detect_platform() {
  case "$(uname -s 2>/dev/null || echo unknown)" in
    Linux*)   echo "linux" ;;
    Darwin*)  echo "macos" ;;
    MINGW*)   echo "windows-gitbash" ;;
    MSYS*)    echo "windows-gitbash" ;;
    CYGWIN*)  echo "windows-cygwin" ;;
    *)        echo "unknown" ;;
  esac
}
PLATFORM="$(detect_platform)"

# ---- Config ----
REPO_URL="${MAVIS_TEAM_REPO:-https://github.com/Qqapple1/Mavis-team-mode-skill.git}"
SKILL_NAME="mavis-team-mode"

# Path defaults: handle Windows $HOME
if [ -n "${MAVIS_TEAM_DIR:-}" ]; then
  INSTALL_DIR="$MAVIS_TEAM_DIR"
else
  INSTALL_DIR="$HOME/mavis-team-mode-skill"
fi
ZCODE_SKILLS_DIR="$HOME/.zcode/skills"
ZCODE_LINK="$ZCODE_SKILLS_DIR/$SKILL_NAME"
GIT_REF="${MAVIS_TEAM_REF:-}"

# Force copy (Windows-safe) if requested
FORCE_COPY=""
if [ -n "${MAVIS_TEAM_FORCE_COPY:-}" ] || [ "${1:-}" = "--copy" ]; then
  FORCE_COPY="1"
fi

# ---- Colors (respect NO_COLOR and non-TTY) ----
if [ -n "${MAVIS_TEAM_NO_COLOR:-}" ] || [ ! -t 1 ]; then
  C_RESET=""
  C_BLUE=""; C_GREEN=""; C_YELLOW=""; C_RED=""
else
  C_RESET=$'\033[0m'
  C_BLUE=$'\033[1;34m'
  C_GREEN=$'\033[1;32m'
  C_YELLOW=$'\033[1;33m'
  C_RED=$'\033[1;31m'
fi

log()  { printf "%s[i]%s %s\n" "$C_BLUE" "$C_RESET" "$*"; }
ok()   { printf "%s[✓]%s %s\n" "$C_GREEN" "$C_RESET" "$*"; }
warn() { printf "%s[!]%s %s\n" "$C_YELLOW" "$C_RESET" "$*"; }
err()  { printf "%s[✗]%s %s\n" "$C_RED" "$C_RESET" "$*" >&2; }
die()  { err "$*"; exit 1; }

# On Windows Git Bash, default to copy unless user explicitly wants symlink
# (this block is placed after the warn function definition so shellcheck
# doesn't flag SC2218 'function used before defined')
if [ "$PLATFORM" = "windows-gitbash" ] && [ -z "$FORCE_COPY" ]; then
  FORCE_COPY="1"
  warn "Detected Git Bash on Windows: defaulting to copy mode (not symlink)"
  warn "  To force symlink: set MSYS=winsymlinks:native, or use WSL"
fi

# ---- Cross-platform helpers ----

# Convert to absolute path (handles ../, ./, etc.)
# Works on both GNU and BSD/POSIX readlink
abs_path() {
  local p="$1"
  # Try GNU readlink -f
  if readlink -f "$p" 2>/dev/null; then return; fi
  # Try realpath
  if command -v realpath >/dev/null 2>&1; then
    realpath "$p" 2>/dev/null
    return
  fi
  # Fallback: cd to dir and echo pwd + basename
  local d b
  d=$(dirname "$p")
  b=$(basename "$p")
  (cd "$d" 2>/dev/null && printf "%s/%s\n" "$(pwd)" "$b")
}

# Get directory size in KB (handles symlinks via -L)
dir_size_kb() {
  local d="$1"
  if [ ! -e "$d" ]; then echo 0; return; fi
  # Linux/GNU du: du -skL
  if du -skL "$d" 2>/dev/null | awk '{print $1}' | grep -qE '^[0-9]+$'; then
    du -skL "$d" 2>/dev/null | awk '{print $1}'
    return
  fi
  # BSD/macOS du: du -sk
  du -sk "$d" 2>/dev/null | awk '{print $1}'
}

# Create symlink (Linux/macOS) or copy (Windows-safe)
# On Git Bash without MSYS=winsymlinks:native, ln -s is a "winln" that
# does copy. We detect that and fall back to real copy to be honest.
make_link() {
  local link_path="$1"
  local target="$2"

  if [ -n "$FORCE_COPY" ]; then
    log "Copy mode: $link_path (→ $target)"
    rm -rf "$link_path" 2>/dev/null || true
    cp -r "$target" "$link_path"
    return 0
  fi

  # Try symlink first
  if ln -sfn "$target" "$link_path" 2>/dev/null; then
    # Verify it's actually a symlink (not a copy masquerade)
    if [ -L "$link_path" ]; then
      ok "Symlink: $link_path → $(readlink "$link_path")"
      return 0
    fi
    # Git Bash fallback: ln "succeeded" but it's a copy, not symlink
    warn "ln -s created a copy (not a real symlink) — Windows? Falling back to copy mode"
    FORCE_COPY="1"
    rm -rf "$link_path" 2>/dev/null || true
    cp -r "$target" "$link_path"
    return 0
  fi
  # Symlink failed (e.g. permission denied) — fall back to copy
  warn "Symlink failed, falling back to copy"
  FORCE_COPY="1"
  rm -rf "$link_path" 2>/dev/null || true
  cp -r "$target" "$link_path"
}

# ---- Usage ----
usage() {
  cat <<EOF
Mavis Team Mode installer v${INSTALLER_VERSION}

Usage:
  bash install.sh              Install (clone + link + verify)
  bash install.sh --uninstall  Remove the skill
  bash install.sh --doctor     Check current install state (no changes)
  bash install.sh --version    Show installer version
  bash install.sh --copy       Force copy (Windows safe, no symlink)
  bash install.sh --no-verify  Skip post-install verification
  bash install.sh --help       This help

Environment:
  MAVIS_TEAM_REPO       Git URL (default: GitHub Qqapple1 repo)
  MAVIS_TEAM_DIR        Where to clone (default: \$HOME/mavis-team-mode-skill)
  MAVIS_TEAM_REF        Git ref to checkout after clone
  MAVIS_TEAM_NO_COLOR   Disable color output
  MAVIS_TEAM_FORCE_COPY Force copy over symlink

Detected platform: $PLATFORM

On Windows: Git Bash defaults to copy mode (ln -s there is a "winln"
masquerade). For real symlinks, use WSL or set MSYS=winsymlinks:native.
EOF
}

# ---- Argument parsing ----
ACTION="install"
DO_VERIFY=1
case "${1:-}" in
  --help|-h)  usage; exit 0 ;;
  --version)  echo "Mavis Team Mode installer v${INSTALLER_VERSION}"; exit 0 ;;
  --uninstall) ACTION="uninstall" ;;
  --doctor)    ACTION="doctor" ;;
  --no-verify) ACTION="install"; DO_VERIFY=0 ;;
  --copy)      ACTION="install"; FORCE_COPY="1" ;;
  "")          ACTION="install" ;;
  *) die "Unknown arg: $1 (try --help)" ;;
esac

# ---- Signal handlers ----
# Ensure Ctrl+C / SIGTERM / install-time errors give a clean message and
# non-zero exit, instead of leaving a half-cloned repo or partial link.
# We only install these traps once we know the action (so --help/--version
# aren't burdened), and we do NOT trap in --doctor mode (read-only).
cleanup_on_signal() {
  printf '\n' >&2
  err "Interrupted. $INSTALL_DIR or $ZCODE_LINK may be in a partial state."
  err "Re-run with the same arguments to resume, or 'bash install.sh --uninstall' to clean up."
  exit 130  # 128 + SIGINT(2)
}
if [ "$ACTION" = "install" ] || [ "$ACTION" = "uninstall" ]; then
  trap 'cleanup_on_signal' INT TERM
fi

# ---- Prerequisite checks ----
check_prereqs() {
  local missing=0
  if ! command -v git >/dev/null 2>&1; then
    err "Required command not found: git"
    missing=1
  fi
  if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    warn "python3 not found in PATH — needed for the prototype server"
    warn "  Install from https://www.python.org/downloads/ (Windows)"
    warn "  Or 'brew install python3' (macOS)"
    warn "  Or 'sudo apt install python3' (Linux)"
    missing=1
  fi
  if [ "$missing" -ne 0 ]; then
    if [ "$ACTION" = "doctor" ]; then
      warn "Some prereqs missing (continuing doctor mode)"
      return 0
    fi
    die "Install missing prerequisites first."
  fi
}

# ---- Safe removal: handle read-only files + nested dirs ----
safe_rm() {
  local target="$1"
  if [ ! -e "$target" ] && [ ! -L "$target" ]; then
    return 0
  fi
  rm -rf "$target" 2>/dev/null && return 0
  chmod -R u+w "$target" 2>/dev/null || true
  rm -rf "$target" 2>/dev/null && return 0
  # Last resort: rm each file
  find "$target" -type f -delete 2>/dev/null
  find "$target" -depth -type d -empty -delete 2>/dev/null
  [ ! -e "$target" ] && [ ! -L "$target" ]
}

# ---- Doctor: check current state without modifying ----
doctor() {
  log "Doctor: checking current install state (platform: $PLATFORM)..."
  echo
  local issues=0

  # 1. Zcode dir
  if [ -d "$ZCODE_SKILLS_DIR" ]; then
    ok "Zcode skills dir exists: $ZCODE_SKILLS_DIR"
  else
    warn "Zcode skills dir does not exist: $ZCODE_SKILLS_DIR"
    warn "  Zcode may not be installed, or you're in a non-standard location"
  fi

  # 2. Link or copy
  if [ -L "$ZCODE_LINK" ]; then
    local target
    target=$(readlink "$ZCODE_LINK" 2>/dev/null || echo "?")
    ok "Symlink: $ZCODE_LINK -> $target"
    if [ -d "$target" ]; then
      ok "  Target dir exists and is accessible"
    else
      err "  Target dir does NOT exist: $target"
      issues=$((issues+1))
    fi
  elif [ -d "$ZCODE_LINK" ]; then
    # Check if it's a real dir (not a copy masquerade)
    if [ -n "$FORCE_COPY" ] || [ ! -L "$ZCODE_LINK" ]; then
      warn "$ZCODE_LINK is a real directory (not a symlink — copy mode or fallback)"
      if [ -f "$ZCODE_LINK/SKILL.md" ]; then
        ok "  Contains SKILL.md — copy looks valid"
      else
        err "  No SKILL.md in this directory"
        issues=$((issues+1))
      fi
    fi
  else
    warn "No install at $ZCODE_LINK"
  fi

  # 3. Clone dir — try ZCODE_LINK (which may be the actual files in copy mode)
  local clone_check_dir="$INSTALL_DIR"
  if [ ! -d "$INSTALL_DIR/.git" ] && [ -d "$ZCODE_LINK/.git" ]; then
    # Copy mode: the .git is in ZCODE_LINK too
    clone_check_dir="$ZCODE_LINK"
  fi
  if [ -d "$clone_check_dir/.git" ]; then
    cd "$clone_check_dir"
    local current branch dirty
    current=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    log "  HEAD: $current on branch '$branch'"
    dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [ "$dirty" -gt 0 ]; then
      warn "  $dirty uncommitted changes (consider committing or stashing)"
    else
      ok "  Working tree clean"
    fi
  elif [ -d "$INSTALL_DIR" ]; then
    warn "$INSTALL_DIR exists but is not a git repo"
  else
    warn "No clone at $INSTALL_DIR"
  fi

  # 4. Required files — check the actual deployed location
  # In copy mode, files are in $ZCODE_LINK; in symlink mode, $INSTALL_DIR
  local check_dir=""
  if [ -d "$ZCODE_LINK" ]; then
    # If $ZCODE_LINK is itself the files (copy mode), use it
    if [ -f "$ZCODE_LINK/SKILL.md" ] && [ ! -L "$ZCODE_LINK" ]; then
      check_dir="$ZCODE_LINK"
    fi
  fi
  if [ -z "$check_dir" ] && [ -d "$INSTALL_DIR" ]; then
    check_dir="$INSTALL_DIR"
  fi
  if [ -z "$check_dir" ]; then
    err "No install found (neither $ZCODE_LINK nor $INSTALL_DIR)"
    issues=$((issues+1))
  else
    for f in SKILL.md agents/leader.md agents/verifier.md agents/worker-coder.md README.md; do
      if [ -f "$check_dir/$f" ]; then
        ok "$f present"
      else
        err "$f MISSING (in $check_dir)"
        issues=$((issues+1))
      fi
    done
  fi

  echo
  if [ "$issues" -eq 0 ]; then
    ok "Doctor: no issues found"
    return 0
  else
    err "Doctor: $issues issue(s) found"
    return 1
  fi
}

# ---- Uninstall ----
uninstall() {
  log "Uninstalling $SKILL_NAME..."
  echo

  if [ -L "$ZCODE_LINK" ] || [ -d "$ZCODE_LINK" ]; then
    if safe_rm "$ZCODE_LINK"; then
      ok "Removed $ZCODE_LINK"
    else
      err "Failed to remove $ZCODE_LINK"
      err "Try manually: rm -rf \"$ZCODE_LINK\""
      return 1
    fi
  else
    warn "No install at $ZCODE_LINK"
  fi

  if [ -d "$INSTALL_DIR" ]; then
    warn "$INSTALL_DIR still exists (your code, kept by default)"
    warn "Remove manually if desired: rm -rf \"$INSTALL_DIR\""
  fi

  echo
  ok "Uninstall complete. Restart Zcode to pick up changes."
  return 0
}

# ---- Install ----
install() {
  check_prereqs
  log "Installing ${SKILL_NAME} (platform: $PLATFORM)..."
  echo

  # 1. Zcode skills dir
  if [ ! -d "$ZCODE_SKILLS_DIR" ]; then
    log "Creating $ZCODE_SKILLS_DIR..."
    if ! mkdir -p "$ZCODE_SKILLS_DIR" 2>/dev/null; then
      die "Cannot create $ZCODE_SKILLS_DIR. Check permissions."
    fi
    ok "Created"
  else
    ok "Zcode skills dir exists"
  fi

  # 2. Clone or update
  if [ -d "$INSTALL_DIR/.git" ]; then
    log "Existing clone found, pulling latest..."
    cd "$INSTALL_DIR"
    if ! git pull --rebase --autostash 2>&1 | tail -5; then
      warn "git pull had issues; continuing with current state"
    fi
    ok "Updated"
  else
    if [ -d "$INSTALL_DIR" ]; then
      die "$INSTALL_DIR exists but is not a git repo. Remove it and re-run."
    fi
    log "Cloning $REPO_URL..."
    if ! git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" 2>&1 | tail -5; then
      die "git clone failed. Check URL and network."
    fi
    ok "Cloned to $INSTALL_DIR"
  fi

  # 3. Checkout specific ref if requested
  if [ -n "$GIT_REF" ]; then
    log "Checking out ref: $GIT_REF"
    cd "$INSTALL_DIR"
    # Unshallow if needed: shallow clones can't fetch arbitrary refs
    if git rev-parse --is-shallow-repository 2>/dev/null | grep -q true; then
      log "  unshallowing repository to enable ref fetch..."
      git fetch --unshallow origin 2>&1 | tail -3 || true
    fi
    if ! git fetch --depth 1 origin "$GIT_REF" 2>&1 | tail -3; then
      die "Failed to fetch ref $GIT_REF"
    fi
    git checkout "$GIT_REF" 2>&1 | tail -3 || die "Failed to checkout $GIT_REF"
    ok "On ref: $GIT_REF"
  fi

  # 4. Verify required files
  cd "$INSTALL_DIR"
  local missing=0
  for f in SKILL.md agents/leader.md agents/verifier.md agents/worker-coder.md README.md; do
    if [ ! -f "$f" ]; then
      err "Missing required file: $f"
      missing=1
    fi
  done
  if [ "$missing" -ne 0 ]; then
    die "Repository is missing required files. Check the ref you checked out."
  fi
  ok "All required files present"

  # 5. Link or copy (replace existing)
  if [ -L "$ZCODE_LINK" ] || [ -d "$ZCODE_LINK" ]; then
    warn "Existing install found at $ZCODE_LINK, replacing..."
    safe_rm "$ZCODE_LINK"
  fi
  make_link "$ZCODE_LINK" "$INSTALL_DIR"

  # 6. Post-install verify
  if [ "$DO_VERIFY" = "1" ]; then
    echo
    log "Running post-install verification..."
    if [ -x "$INSTALL_DIR/scripts/validate.sh" ]; then
      if "$INSTALL_DIR/scripts/validate.sh"; then
        ok "All checks passed"
      else
        warn "Some validation checks failed. Run validate.sh manually to see details."
      fi
    else
      warn "validate.sh not found or not executable, skipping"
    fi
  fi

  # 7. Final summary
  echo
  ok "Installation complete!"
  echo
  cat <<EOF
Next steps:
  1. Restart Zcode (fully quit, not minimize)
  2. Open a new conversation in Zcode
  3. Just talk naturally: "用 mavis team mode 帮我..."
     or "team mode", "拆成子任务", etc. (Zcode matches the skill description automatically)
  4. See examples/ for worked examples

Platform: $PLATFORM
Link mode: $([ -n "$FORCE_COPY" ] && echo "copy" || echo "symlink")
Install:   $INSTALL_DIR
Link:      $ZCODE_LINK

To uninstall later:
  bash "${INSTALL_DIR}/scripts/install.sh" --uninstall
EOF
}

# ---- Dispatch ----
case "$ACTION" in
  install)   install ;;
  uninstall) uninstall ;;
  doctor)    doctor ;;
  *)         die "Unknown action: $ACTION" ;;
esac
