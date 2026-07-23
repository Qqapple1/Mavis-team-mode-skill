#!/usr/bin/env bash
# Validate Mavis Team Mode skill installation
# Usage: bash scripts/validate.sh
set -uo pipefail

SKILL_DIR="${HOME}/.zcode/skills/mavis-team-mode"
PASS=0
FAIL=0

ok()   { printf '\033[1;32m[✓]\033[0m %s\n' "$*"; PASS=$((PASS+1)); }
fail() { printf '\033[1;31m[✗]\033[0m %s\n' "$*"; FAIL=$((FAIL+1)); }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*"; }
info() { printf '\033[1;34m[i]\033[0m %s\n' "$*"; }

echo "=== Mavis Team Mode Skill Validator ==="
echo

# 1. Skill directory exists
info "Checking skill directory: $SKILL_DIR"
if [ ! -d "$SKILL_DIR" ]; then
  fail "Skill directory not found. Run install.sh first."
  exit 1
fi
ok "Skill directory exists"

# 2. SKILL.md exists and is readable
if [ -f "$SKILL_DIR/SKILL.md" ] && [ -r "$SKILL_DIR/SKILL.md" ]; then
  ok "SKILL.md exists and is readable"
else
  fail "SKILL.md missing or not readable"
  exit 1
fi

# 3. SKILL.md has required frontmatter
info "Validating SKILL.md frontmatter..."
if head -1 "$SKILL_DIR/SKILL.md" | grep -q '^---$'; then
  ok "SKILL.md starts with frontmatter delimiter"
else
  fail "SKILL.md does not start with ---"
fi

# 4. Required frontmatter fields
for field in name description version; do
  if grep -q "^${field}:" "$SKILL_DIR/SKILL.md"; then
    ok "SKILL.md has '${field}' field"
  else
    fail "SKILL.md missing '${field}' field"
  fi
done

# 5. name is kebab-case and ≤ 64 chars
name=$(awk '/^name:/{print $2; exit}' "$SKILL_DIR/SKILL.md" | tr -d '"' | tr -d "'")
if [[ "$name" =~ ^[a-z0-9][a-z0-9-]{0,63}$ ]]; then
  ok "SKILL.md name is valid kebab-case: '$name'"
else
  fail "SKILL.md name '$name' is not valid kebab-case (must be lowercase letters/digits/hyphens, 1-64 chars)"
fi

# 6. description exists and is reasonable length
# Handle: description: "..." or description: "..." (multi-line via YAML | or >)
desc=$(awk '
  /^description:[[:space:]]*"/ { gsub(/^description:[[:space:]]*"/, ""); gsub(/"[[:space:]]*$/, ""); print; in_desc=1; next }
  /^description:[[:space:]]*\|/ { in_desc=1; next }
  /^description:[[:space:]]*>/ { in_desc=1; next }
  in_desc && /^[^[:space:]-]/ && !/^description:/ { in_desc=0 }
  in_desc { print }
' "$SKILL_DIR/SKILL.md" | tr -d '\n' | tr -d ' ')
desc_len=${#desc}
if [ "$desc_len" -gt 50 ] && [ "$desc_len" -lt 1100 ]; then
  ok "SKILL.md description length OK ($desc_len chars)"
else
  fail "SKILL.md description length weird: $desc_len chars (should be 50-1024)"
fi

# 7. All agents exist
info "Checking agent files..."
AGENTS=(leader verifier worker-coder worker-tester worker-researcher worker-doc-writer worker-reviewer)
for a in "${AGENTS[@]}"; do
  f="$SKILL_DIR/agents/${a}.md"
  if [ ! -f "$f" ]; then
    fail "Missing agent: agents/${a}.md"
    continue
  fi
  # Check frontmatter
  if ! head -1 "$f" | grep -q '^---$'; then
    fail "agents/${a}.md missing frontmatter"
    continue
  fi
  # Check tools field (Zcode 必需)
  if ! grep -q "^tools:" "$f"; then
    fail "agents/${a}.md missing 'tools:' field (Zcode will not dispatch this agent)"
    continue
  fi
  ok "agents/${a}.md valid"
done

# 8. References exist
info "Checking reference files..."
REFS=(verification-checklist deepseek-setup troubleshooting)
for r in "${REFS[@]}"; do
  if [ -f "$SKILL_DIR/references/${r}.md" ]; then
    ok "references/${r}.md exists"
  else
    fail "Missing reference: references/${r}.md"
  fi
done

# 9. Examples exist
info "Checking example files..."
EXAMPLES=(refactor-large-module bug-hunt new-feature research-then-implement)
for e in "${EXAMPLES[@]}"; do
  if [ -f "$SKILL_DIR/examples/${e}.md" ]; then
    ok "examples/${e}.md exists"
  else
    fail "Missing example: examples/${e}.md"
  fi
done

# 10. Total size sanity check
total_size=$(du -skL "$SKILL_DIR" 2>/dev/null | awk '{print $1}')
if [ "$total_size" -lt 1500 ] && [ "$total_size" -gt 5 ]; then
  ok "Total size looks reasonable: ${total_size}KB"
else
  warn "Total size: ${total_size}KB (expected 5-1500KB for a skill)"
fi

# Summary
echo
echo "=== Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo

if [ "$FAIL" -gt 0 ]; then
  echo "Some checks failed. Please review above."
  exit 1
else
  echo "✓ All checks passed. Skill is properly installed."
  echo
  echo "Restart Zcode, then just talk naturally:"
  echo "  '用 mavis team mode 帮我...'"
  echo "  or 'team mode', '拆成子任务', 'multi-agent', etc."
  echo "(Zcode skills are description-matched — no slash command needed.)"
  exit 0
fi
