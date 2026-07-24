# Platform Support

This skill runs on **macOS / Linux / Windows** via multiple installer paths.
This page explains which files are platform-specific, and which release
archive to download for your OS.

> **Honest framing**: I have personally tested the bash + PowerShell
> installers and all e2e tests on Linux. The Windows install + Python
> startup is verified in GitHub Actions Windows runner. **I have not
> personally clicked through every menu in Zcode on every OS** — the
> "skill loads + sub-agent dispatch + Verifier" loop depends on your
> Zcode 3.x behavior, which I can't run in CI.

## File classification

| Category | Files | Used by |
|----------|-------|---------|
| **Cross-platform core** | 38 files: SKILL.md, agents/, examples/, references/, docs/, server.py, client/index.html, test_e2e*.py, validate_yaml.py, benchmark_tokens.py, .md docs, LICENSE, index.html, Makefile | All platforms |
| **bash installer** | + 3: `scripts/install.sh`, `scripts/validate.sh`, `scripts/package.sh` | Linux / macOS / Git Bash / WSL |
| **PowerShell installer** | + 3: `scripts/install.ps1`, `scripts/validate.ps1`, `examples/prototype-todo-app/run_e2e.ps1` | Windows PowerShell 5.1+ |
| **CI / source only** | + 4: `docs/WINDOWS.md`, `.github/ISSUE_TEMPLATE/*.md`, `.github/workflows/validate-skill.yml` | GitHub Actions / contributors |

**Total: 48 files in source, 38-41 in any release archive.**

## Which archive should I download?

| I am a... | Download | Install command |
|-----------|----------|-----------------|
| **macOS user** | `mavis-team-mode-skill-{ver}-bash.tar.gz` | `bash scripts/install.sh` |
| **Linux user** | `mavis-team-mode-skill-{ver}-bash.tar.gz` | `bash scripts/install.sh` |
| **Windows + Git Bash user** | `mavis-team-mode-skill-{ver}-bash.tar.gz` | `bash scripts/install.sh` (default copy mode) |
| **Windows + PowerShell user** (no Git Bash) | `mavis-team-mode-skill-{ver}-windows.zip` | `powershell -ExecutionPolicy Bypass -File scripts\install.ps1` |
| **WSL2 user** | `mavis-team-mode-skill-{ver}-bash.tar.gz` | `bash scripts/install.sh` (WSL = Linux) |
| **Just want to browse / read** (no install) | `mavis-team-mode-skill-{ver}-core.zip` | No install needed |
| **Contributor / CI runner** | `mavis-team-mode-skill-{ver}-source.tar.gz` | `git clone` (or use the source tarball) |

If you're unsure: **download the `bash` archive and use Git Bash** (Windows
users — install from [git-scm.com](https://git-scm.com/download/win)) or
just `bash` from WSL. The bash installer auto-detects your platform and
falls back to copy mode on Windows Git Bash.

## Why split into 5 archives?

Because the bash scripts (`*.sh`) are useless on Windows PowerShell,
and the PowerShell scripts (`*.ps1`) are useless on Linux/macOS bash.
Bundling them all into one archive works, but:

1. **Smaller download** — bash users don't pull 3 useless `.ps1` files
2. **Less confusion** — a Linux user never sees `install.ps1` and
   wonders if they should run it
3. **Cleaner release notes** — you can see "bash release 1.3.17" and
   "Windows release 1.3.17" are the same content, different installer
4. **Easier to verify** — the SHA256SUMS file lists each archive
   independently

## Building archives yourself

```bash
# Show what would be packaged (no write)
bash scripts/package.sh --dry-run

# Build all 5 archives to dist/
bash scripts/package.sh

# Or via Makefile
make package
make package-dry-run
```

After running, `dist/` contains:
```
mavis-team-mode-skill-1.3.17-core.zip        (38 files, ~120KB)
mavis-team-mode-skill-1.3.17-bash.tar.gz     (41 files, ~127KB)
mavis-team-mode-skill-1.3.17-windows.zip     (41 files, ~130KB)
mavis-team-mode-skill-1.3.17-source.tar.gz   (48 files, ~150KB)
mavis-team-mode-skill-1.3.17-source.zip      (48 files, ~155KB)
SHA256SUMS                                  (checksums)
```

## Cross-platform install (one-liner from GitHub)

If you don't want to download an archive at all, you can clone and run
the bash installer on any platform with bash + git:

```bash
# macOS / Linux / Git Bash / WSL
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git ~/mavis-team-mode-skill
bash ~/mavis-team-mode-skill/scripts/install.sh
```

Or for Windows PowerShell:
```powershell
git clone https://github.com/Qqapple1/Mavis-team-mode-skill.git $env:USERPROFILE\mavis-team-mode-skill
powershell -ExecutionPolicy Bypass -File $env:USERPROFILE\mavis-team-mode-skill\scripts\install.ps1
```

## What runs everywhere vs. platform-only

| Action | All OS | bash | PowerShell |
|--------|--------|------|------------|
| Read SKILL.md / agents / docs | ✓ | | |
| Run prototype server (`python3 server/server.py`) | ✓ | | |
| Run e2e tests (`python3 test_e2e.py`) | ✓ | | |
| Run validate_yaml.py | ✓ | | |
| Run benchmark_tokens.py | ✓ | | |
| `bash scripts/install.sh` | | ✓ | |
| `bash scripts/validate.sh` | | ✓ | |
| `bash scripts/package.sh` | | ✓ | |
| `make help/install/test` | needs `make` | | |
| `powershell scripts/install.ps1` | | | ✓ |
| `powershell scripts/validate.ps1` | | | ✓ |
| `powershell examples/.../run_e2e.ps1` | | | ✓ |

## Verification

After install on any platform:

```bash
bash scripts/install.sh --doctor   # or install.ps1 -Doctor
```

Expected: `Doctor: no issues found` (or `Passed: 23` if validate.sh
is invoked directly).

The 48 e2e tests + 23 skill format checks + 15 YAML checks = **86
verification points** (PowerShell: 48 e2e + 24 format + 15 YAML = **87**),
all runnable on any platform with Python 3.8+
(plus bash for the bash installer, or PowerShell for the PowerShell
installer). 3.6/3.7 are EOL.
