#!/usr/bin/env bash
# Install Mavis Team Mode skill into Zcode
#
# Usage:
#   bash install.sh              Install (clone + symlink + verify)
#   bash install.sh --uninstall  Remove the skill
#   bash install.sh --help       Show help
#   bash install.sh --version    Show installer version
#   bash install.sh --doctor     Check current install state without changing
#   bash install.sh --no-verify  Skip post-install verification
#
# Env vars:
#   MAVIS_TEAM_REPO   Git URL to clone (default: GitHub)
#   MAVIS_TEAM_DIR    Where to clone (default: $HOME/mavis-team-mode-skill)
#   MAVIS_TEAM_REF    Git ref to checkout (branch/tag/SHA) after clone
#   MAVIS_TEAM_NO_COLOR  Set to non-empty to disable color output
#
# Idempotent: re-running is safe and just `git pull`s + recreates symlink.

set -euo pipefail

# ---- Version ----
INSTALLER_VERSION="1.2.0"

# ---- Config ----
REPO_URL="${MAVIS_TEAM_REPO:-https://github.com/Qqapple1/Mavis-team-mode-skill.git}"
SKILL_NAME="mavis-team-mode"
INSTALL_DIR="${MAVIS_TEAM_DIR:-${HOME}/mavis-team-mode-skill}"
ZCODE_SKILLS_DIR="${HOME}/.zcode/skills"
ZCODE_LINK="${ZCODE_SKILLS_DIR}/${SKILL_NAME}"
GIT_REF="${MAVIS_TEAM_REF:-}"

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

# ---- Usage ----
usage() {
  cat <<EOF
Mavis Team Mode installer v${INSTALLER_VERSION}

Usage:
  bash install.sh [options]

Options:
  (none)            Install (clone + symlink + verify)
  --uninstall       Remove the symlink and clone
  --doctor          Diagnose current install state without modifying
  --no-verify       Skip post-install verification step
  --version         Show installer version
  --help, -h        Show this help

Environment:
  MAVIS_TEAM_REPO     Git URL to clone (default: GitHub upstream)
  MAVIS_TEAM_DIR      Clone destination (default: \$HOME/mavis-team-mode-skill)
  MAVIS_TEAM_REF      Git ref to checkout (branch/tag/SHA) after clone
  MAVIS_TEAM_NO_COLOR Disable colored output
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
  "")          ACTION="install" ;;
  *) die "Unknown arg: $1 (try --help)" ;;
esac

# ---- Prerequisite checks ----
check_prereqs() {
  local missing=0
  if ! command -v git >/dev/null 2>&1; then
    err "Required command not found: git"
    missing=1
  fi
  if [ "$missing" -ne 0 ]; then
    die "Install missing prerequisites first."
  fi
}

# ---- Safe removal: handle read-only files + nested dirs ----
safe_rm() {
  # Try standard rm first, then chmod + rm, then individual file rm
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
  log "Doctor: checking current install state..."
  echo
  local issues=0

  # 1. Zcode dir
  if [ -d "$ZCODE_SKILLS_DIR" ]; then
    ok "Zcode skills dir exists: $ZCODE_SKILLS_DIR"
  else
    warn "Zcode skills dir does not exist: $ZCODE_SKILLS_DIR"
    warn "  Zcode may not be installed, or you're in a non-standard location"
  fi

  # 2. Symlink
  if [ -L "$ZCODE_LINK" ]; then
    target=$(readlink "$ZCODE_LINK")
    ok "Symlink: $ZCODE_LINK -> $target"
    if [ -d "$target" ]; then
      ok "  Target dir exists and is accessible"
    else
      err "  Target dir does NOT exist: $target"
      issues=$((issues+1))
    fi
  elif [ -d "$ZCODE_LINK" ]; then
    warn "$ZCODE_LINK is a real directory, not a symlink"
    issues=$((issues+1))
  else
    warn "No install at $ZCODE_LINK"
  fi

  # 3. Clone dir
  if [ -d "$INSTALL_DIR/.git" ]; then
    ok "Clone exists: $INSTALL_DIR"
    cd "$INSTALL_DIR"
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

  # 4. Required files
  for f in SKILL.md agents/leader.md agents/verifier.md; do
    if [ -f "$INSTALL_DIR/$f" ]; then
      ok "$f present"
    else
      err "$f MISSING"
      issues=$((issues+1))
    fi
  done

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
  log "Uninstalling ${SKILL_NAME}..."

  if [ -L "$ZCODE_LINK" ]; then
    rm "$ZCODE_LINK"
    ok "Removed symlink: $ZCODE_LINK"
  elif [ -d "$ZCODE_LINK" ]; then
    warn "$ZCODE_LINK is a real directory, not a symlink. Removing it."
    if safe_rm "$ZCODE_LINK"; then
      ok "Removed directory: $ZCODE_LINK"
    else
      err "Failed to remove $ZCODE_LINK — try: sudo rm -rf $ZCODE_LINK"
    fi
  else
    warn "No symlink at $ZCODE_LINK"
  fi

  if [ -d "$INSTALL_DIR" ]; then
    log "Removing clone at $INSTALL_DIR..."
    if safe_rm "$INSTALL_DIR"; then
      ok "Removed clone: $INSTALL_DIR"
    else
      warn "Could not fully remove $INSTALL_DIR"
      warn "Try: chmod -R u+w \"$INSTALL_DIR\" && rm -rf \"$INSTALL_DIR\""
    fi
  else
    warn "No clone at $INSTALL_DIR"
  fi

  ok "Uninstall complete. Restart Zcode to pick up changes."
}

# ---- Install ----
install() {
  check_prereqs
  log "Installing ${SKILL_NAME}..."
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

  # 5. Symlink (replaces existing)
  if [ -L "$ZCODE_LINK" ] || [ -d "$ZCODE_LINK" ]; then
    warn "Existing install found at $ZCODE_LINK, replacing..."
    safe_rm "$ZCODE_LINK"
  fi
  if ! ln -s "$INSTALL_DIR" "$ZCODE_LINK"; then
    die "Failed to create symlink. Check permissions on $ZCODE_SKILLS_DIR."
  fi
  ok "Symlinked: $ZCODE_LINK -> $INSTALL_DIR"

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
  3. Type: /mavis-team-mode
     Or naturally: "用 team 模式帮我..."
  4. See examples/ for worked examples

To uninstall later:
  bash "${INSTALL_DIR}/scripts/install.sh" --uninstall
EOF
}

# ---- Dispatch ----
case "$ACTION" in
  install)   install ;;
  uninstall) uninstall ;;
  doctor)    doctor ;;
esac
