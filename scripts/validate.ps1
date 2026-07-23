# Validate Mavis Team Mode skill (Windows PowerShell)
param(
    [string]$SkillDir = "$env:USERPROFILE\.zcode\skills\mavis-team-mode"
)

$PASS = 0
$FAIL = 0

function Ok { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green; $script:PASS++ }
function Fail { param($msg) Write-Host "[FAIL] $msg" -ForegroundColor Red; $script:FAIL++ }
function Warn { param($msg) Write-Host "[!] $msg" -ForegroundColor Yellow }
function Info { param($msg) Write-Host "[i] $msg" -ForegroundColor Cyan }

Write-Host "=== Mavis Team Mode Skill Validator (Windows PowerShell) ==="
Write-Host

Info "Checking skill directory: $SkillDir"
if (Test-Path $SkillDir) {
    Ok "Skill directory exists"
} else {
    Fail "Skill directory not found. Run install.ps1 first."
    exit 1
}

# 1. SKILL.md exists
$skillMd = Join-Path $SkillDir "SKILL.md"
if (Test-Path $skillMd) {
    Ok "SKILL.md exists"
} else {
    Fail "SKILL.md missing"
    exit 1
}

# 2. Read frontmatter
$content = Get-Content $skillMd -Raw
$fm = ""
if ($content -match '(?s)^---\s*\n(.*?)\n---') {
    $fm = $matches[1]
    Ok "SKILL.md has frontmatter"
} else {
    Fail "SKILL.md has no frontmatter"
}

# 3. Frontmatter fields
foreach ($field in @("name", "description", "version")) {
    if ($fm -match "(?m)^$field\s*:") {
        Ok "SKILL.md has '$field' field"
    } else {
        Fail "SKILL.md missing '$field' field"
    }
}

# 4. Agents exist
$agentsDir = Join-Path $SkillDir "agents"
foreach ($a in @("leader", "verifier", "worker-coder", "worker-tester", "worker-researcher", "worker-doc-writer", "worker-reviewer")) {
    $f = Join-Path $agentsDir "$a.md"
    if (Test-Path $f) {
        Ok "agents/$a.md present"
    } else {
        Fail "agents/$a.md MISSING"
    }
}

# 5. References
$refsDir = Join-Path $SkillDir "references"
foreach ($r in @("verification-checklist", "deepseek-setup", "troubleshooting")) {
    $f = Join-Path $refsDir "$r.md"
    if (Test-Path $f) {
        Ok "references/$r.md present"
    } else {
        Fail "references/$r.md MISSING"
    }
}

# 6. Examples
$exDir = Join-Path $SkillDir "examples"
foreach ($e in @("refactor-large-module", "bug-hunt", "new-feature", "research-then-implement")) {
    $f = Join-Path $exDir "$e.md"
    if (Test-Path $f) {
        Ok "examples/$e.md present"
    } else {
        Fail "examples/$e.md MISSING"
    }
}

# 7. Required files
foreach ($f in @("README.md", "LICENSE", "CHANGELOG.md", "scripts\install.ps1")) {
    $p = Join-Path $SkillDir $f
    if (Test-Path $p) {
        Ok "$f present"
    } else {
        Fail "$f MISSING"
    }
}

Write-Host
Write-Host "=== Summary ==="
Write-Host "Passed: $PASS"
Write-Host "Failed: $FAIL"
if ($FAIL -gt 0) {
    exit 1
}
Write-Host "All checks passed. Skill is properly installed."
Write-Host "Restart Zcode to use: '用 mavis team mode 帮我...'"
