#!/usr/bin/env bash
# Install Mavis Team Mode skill into Zcode
# Usage: bash install.sh [--uninstall] [--help]
#        curl ... | bash
set -euo pipefail

# ---- Config ----
REPO_URL="${MAVIS_TEAM_REPO:-https://github.com/YOUR_USERNAME/mavis-team-mode-skill.git}"
SKILL_NAME="mavis-team-mode"
INSTALL_DIR="${HOME}/mavis-team-mode-skill"
ZCODE_SKILLS_DIR="${HOME}/.zcode/skills"
ZCODE_LINK="${ZCODE_SKILLS_DIR}/${SKILL_NAME}"

# ---- Helpers ----
log()  { printf '\033[1;34m[i]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[✓]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
err()  { printf '\033[1;31m[✗]\033[0m %s\n' "$*" >&2; }

usage() {
  cat <<EOF
Mavis Team Mode installer for Zcode

Usage:
  bash install.sh              Install (clone + symlink)
  bash install.sh --uninstall  Remove the symlink and clone
  bash install.sh --help       Show this help

Env vars:
  MAVIS_TEAM_REPO   Git URL to clone (default: GitHub)
EOF
}

# ---- Args ----
case "${1:-}" in
  --help|-h)  usage; exit 0 ;;
  --uninstall) UNINSTALL=1 ;;
  "") UNINSTALL=0 ;;
  *) err "Unknown arg: $1"; usage; exit 1 ;;
esac

# ---- Uninstall path ----
if [ "$UNINSTALL" = "1" ]; then
  log "Uninstalling ${SKILL_NAME}..."
  if [ -L "$ZCODE_LINK" ]; then
    rm "$ZCODE_LINK"
    ok "Removed symlink: $ZCODE_LINK"
  elif [ -d "$ZCODE_LINK" ]; then
    warn "$ZCODE_LINK is a real directory, not a symlink. Removing it."
    rm -rf "$ZCODE_LINK"
    ok "Removed directory: $ZCODE_LINK"
  else
    warn "Nothing to remove at $ZCODE_LINK"
  fi

  if [ -d "$INSTALL_DIR" ]; then
    log "Removing clone at $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
    ok "Removed clone: $INSTALL_DIR"
  fi
  ok "Uninstall complete. Restart Zcode to pick up changes."
  exit 0
fi

# ---- Install path ----
log "Installing ${SKILL_NAME}..."
echo

# 1. Check git is available
if ! command -v git >/dev/null 2>&1; then
  err "git is not installed. Please install git first."
  exit 1
fi

# 2. Create Zcode skills dir if needed
if [ ! -d "$ZCODE_SKILLS_DIR" ]; then
  log "Creating $ZCODE_SKILLS_DIR..."
  mkdir -p "$ZCODE_SKILLS_DIR"
  ok "Created"
fi

# 3. Clone or update repo
if [ -d "$INSTALL_DIR/.git" ]; then
  log "Repo already cloned at $INSTALL_DIR, pulling latest..."
  cd "$INSTALL_DIR"
  git pull --rebase --autostash || {
    err "git pull failed. Try removing $INSTALL_DIR and re-running."
    exit 1
  }
  ok "Updated"
else
  if [ -d "$INSTALL_DIR" ]; then
    err "$INSTALL_DIR exists but is not a git repo. Remove it and re-run."
    exit 1
  fi
  log "Cloning $REPO_URL to $INSTALL_DIR..."
  git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" || {
    err "git clone failed. Check the URL and your network."
    exit 1
  }
  ok "Cloned"
fi

# 4. Verify required files exist
cd "$INSTALL_DIR"
REQUIRED_FILES=(
  "SKILL.md"
  "agents/leader.md"
  "agents/verifier.md"
  "agents/worker-coder.md"
)
for f in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$f" ]; then
    err "Missing required file: $f"
    exit 1
  fi
done
ok "All required files present"

# 5. Symlink (or remove stale link first)
if [ -L "$ZCODE_LINK" ] || [ -d "$ZCODE_LINK" ]; then
  warn "Existing install found at $ZCODE_LINK, removing..."
  rm -rf "$ZCODE_LINK"
fi
ln -s "$INSTALL_DIR" "$ZCODE_LINK"
ok "Symlinked: $ZCODE_LINK -> $INSTALL_DIR"

# 6. Final check
echo
log "Final check:"
ls -la "$ZCODE_LINK/SKILL.md" >/dev/null && ok "  SKILL.md accessible via symlink"
ls -la "$ZCODE_LINK/agents/" >/dev/null && ok "  agents/ accessible via symlink"

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
  bash $INSTALL_DIR/scripts/install.sh --uninstall
EOF
