# Install Mavis Team Mode skill into Zcode (Windows PowerShell)
#
# For Windows users who don't have Git Bash or WSL.
# This is a fallback when bash isn't available.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   .\install.ps1 -Uninstall
#   .\install.ps1 -Doctor

param(
    [switch]$Uninstall,
    [switch]$Doctor,
    [switch]$NoVerify,
    [switch]$Help,
    [string]$InstallDir = "$env:USERPROFILE\mavis-team-mode-skill",
    [string]$RepoUrl = "https://github.com/Qqapple1/Mavis-team-mode-skill.git"
)

$VERSION = "1.3.6"
$SKILL_NAME = "mavis-team-mode"
$ZCODE_SKILLS_DIR = "$env:USERPROFILE\.zcode\skills"
$ZCODE_LINK = "$ZCODE_SKILLS_DIR\$SKILL_NAME"

# Colors
function Log($msg) { Write-Host "[i] $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "[OK] $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "[!] $msg" -ForegroundColor Yellow }
function Err($msg)  { Write-Host "[X] $msg" -ForegroundColor Red }
function Die($msg)  { Err $msg; exit 1 }

function Show-Usage {
    @"
Mavis Team Mode installer v$VERSION (PowerShell)

Usage:
  powershell -ExecutionPolicy Bypass -File install.ps1         Install
  powershell -ExecutionPolicy Bypass -File install.ps1 -Uninstall
  powershell -ExecutionPolicy Bypass -File install.ps1 -Doctor

Parameters:
  -InstallDir <path>   Where to clone (default: `$env:USERPROFILE\mavis-team-mode-skill)
  -RepoUrl <url>       Git URL (default: GitHub Qqapple1 repo)
  -NoVerify            Skip post-install validation

Notes:
  - On Windows, this script uses COPY mode (no symlink support here)
  - For real symlinks, use Git Bash or WSL
  - Tested on PowerShell 5.1+ (default on Windows 10/11)
"@
}

if ($Help) { Show-Usage; exit 0 }

function Test-Git {
    return (Get-Command git -ErrorAction SilentlyContinue) -ne $null
}

function Test-Python {
    return (Get-Command python -ErrorAction SilentlyContinue) -ne $null
}

function Invoke-Install {
    Log "Installing $SKILL_NAME (Windows PowerShell)..."
    Write-Host

    if (-not (Test-Git)) {
        Die "git not found in PATH. Install from https://git-scm.com/download/win"
    }
    if (-not (Test-Python)) {
        Warn "python not found in PATH — needed for the prototype server"
        Warn "  Install from https://www.python.org/downloads/windows/"
    }

    # 1. Create Zcode skills dir
    if (-not (Test-Path $ZCODE_SKILLS_DIR)) {
        Log "Creating $ZCODE_SKILLS_DIR..."
        New-Item -ItemType Directory -Path $ZCODE_SKILLS_DIR -Force | Out-Null
        Ok "Created"
    } else {
        Ok "Zcode skills dir exists"
    }

    # 2. Clone or update
    if (Test-Path "$InstallDir\.git") {
        Log "Existing clone found, pulling latest..."
        Push-Location $InstallDir
        try {
            git pull --rebase --autostash 2>&1 | Select-Object -Last 5
        } catch {
            Warn "git pull had issues; continuing with current state"
        }
        Pop-Location
        Ok "Updated"
    } else {
        if (Test-Path $InstallDir) {
            Die "$InstallDir exists but is not a git repo. Remove it and re-run."
        }
        Log "Cloning $RepoUrl..."
        git clone --depth 1 $RepoUrl $InstallDir 2>&1 | Select-Object -Last 5
        if ($LASTEXITCODE -ne 0) {
            Die "git clone failed. Check URL and network."
        }
        Ok "Cloned to $InstallDir"
    }

    # 3. Verify required files
    $missing = 0
    foreach ($f in @("SKILL.md", "agents\leader.md", "agents\verifier.md", "agents\worker-coder.md", "README.md")) {
        if (-not (Test-Path "$InstallDir\$f")) {
            Err "Missing required file: $f"
            $missing = 1
        }
    }
    if ($missing) {
        Die "Repository is missing required files."
    }
    Ok "All required files present"

    # 4. Copy to Zcode skills dir (no symlink on Windows PS)
    if (Test-Path $ZCODE_LINK) {
        Warn "Existing install found at $ZCODE_LINK, removing..."
        Remove-Item -Recurse -Force $ZCODE_LINK
    }
    Log "Copying to $ZCODE_LINK (Windows: copy mode, no symlink)..."
    Copy-Item -Recurse -Path $InstallDir -Destination $ZCODE_LINK -Force
    Ok "Copied"

    # 5. Post-install verify
    if (-not $NoVerify) {
        Write-Host
        Log "Running post-install verification..."
        $validateScript = "$InstallDir\scripts\validate.ps1"
        if (Test-Path $validateScript) {
            & powershell -ExecutionPolicy Bypass -File $validateScript
        } else {
            Warn "validate.ps1 not found, skipping"
        }
    }

    Write-Host
    Ok "Installation complete!"
    Write-Host @"

Next steps:
  1. Restart Zcode (fully quit, not minimize)
  2. Open a new conversation in Zcode
  3. Just talk naturally: '用 mavis team mode 帮我...'
     or 'team mode', '拆成子任务', etc.
  4. See examples/ for worked examples

Install: $InstallDir
Copy:    $ZCODE_LINK

To uninstall later:
  powershell -ExecutionPolicy Bypass -File install.ps1 -Uninstall
"@
}

function Invoke-Uninstall {
    Log "Uninstalling $SKILL_NAME..."
    Write-Host
    if (Test-Path $ZCODE_LINK) {
        Remove-Item -Recurse -Force $ZCODE_LINK
        Ok "Removed $ZCODE_LINK"
    } else {
        Warn "No install at $ZCODE_LINK"
    }
    if (Test-Path $InstallDir) {
        Warn "$InstallDir still exists (your code, kept by default)"
        Warn "Remove manually if desired: Remove-Item -Recurse -Force '$InstallDir'"
    }
    Ok "Uninstall complete."
}

function Invoke-Doctor {
    Log "Doctor: checking current install state (Windows PowerShell)..."
    Write-Host
    $issues = 0
    if (Test-Path $ZCODE_SKILLS_DIR) {
        Ok "Zcode skills dir exists: $ZCODE_SKILLS_DIR"
    } else {
        Warn "Zcode skills dir does not exist: $ZCODE_SKILLS_DIR"
    }
    if (Test-Path $ZCODE_LINK) {
        if (Test-Path "$ZCODE_LINK\SKILL.md") {
            Ok "Install at $ZCODE_LINK contains SKILL.md"
        } else {
            Err "Install at $ZCODE_LINK but no SKILL.md"
            $issues++
        }
    } else {
        Warn "No install at $ZCODE_LINK"
    }
    if (Test-Path "$InstallDir\.git") {
        Ok "Clone exists: $InstallDir"
    } else {
        Warn "No clone at $InstallDir"
    }
    foreach ($f in @("SKILL.md", "agents\leader.md", "agents\verifier.md", "agents\worker-coder.md", "README.md")) {
        if (Test-Path "$InstallDir\$f") {
            Ok "$f present"
        } else {
            Err "$f MISSING"
            $issues++
        }
    }
    Write-Host
    if ($issues -eq 0) {
        Ok "Doctor: no issues found"
        exit 0
    } else {
        Err "Doctor: $issues issue(s) found"
        exit 1
    }
}

if ($Doctor) {
    Invoke-Doctor
} elseif ($Uninstall) {
    Invoke-Uninstall
} else {
    Invoke-Install
}
