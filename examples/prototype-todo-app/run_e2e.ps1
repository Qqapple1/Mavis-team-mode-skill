# Run e2e tests for prototype server (Windows PowerShell)
param(
    [string]$ServerPath = ".\server\server.py",
    [int]$Port = 8765
)

Write-Host "=== Mavis Team Mode — e2e tests (Windows PowerShell) ==="
Write-Host

# Check python
$python = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $python) {
    $python = (Get-Command python3 -ErrorAction SilentlyContinue)
}
if (-not $python) {
    Write-Host "[X] python not found in PATH" -ForegroundColor Red
    exit 1
}

# Start server in background
Write-Host "[i] Starting server on port $Port..." -ForegroundColor Cyan
$server = Start-Process -FilePath $python.Name -ArgumentList $ServerPath -PassThru -NoNewWindow -RedirectStandardOutput ".\server.log" -RedirectStandardError ".\server.err.log"
Write-Host "  Server PID: $($server.Id)"

# Wait for it to come up
$ready = $false
for ($i = 0; $i -lt 10; $i++) {
    Start-Sleep -Seconds 1
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/api/health" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        # still starting
    }
}

if (-not $ready) {
    Write-Host "[X] Server did not come up within 10 seconds" -ForegroundColor Red
    Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "[OK] Server is up" -ForegroundColor Green
Write-Host

# Run tests
$totalPass = 0
$totalFail = 0
foreach ($testFile in @("test_e2e.py", "test_e2e_extended.py", "test_e2e_advanced.py")) {
    $path = ".\$testFile"
    if (-not (Test-Path $path)) {
        Write-Host "[i] $testFile not found, skipping" -ForegroundColor Yellow
        continue
    }
    Write-Host "[i] Running $testFile..." -ForegroundColor Cyan
    $output = & $python.Name $path 2>&1
    $output | ForEach-Object { Write-Host $_ }
    $lastLines = $output | Select-Object -Last 3
    foreach ($line in $lastLines) {
        if ($line -match "Passed:\s*(\d+)") {
            $totalPass += [int]$matches[1]
        }
        if ($line -match "Failed:\s*(\d+)") {
            $totalFail += [int]$matches[1]
        }
    }
    Write-Host
}

# Cleanup
Write-Host "[i] Stopping server..." -ForegroundColor Cyan
Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue

Write-Host "=== Summary ==="
Write-Host "Passed: $totalPass"
Write-Host "Failed: $totalFail"
if ($totalFail -gt 0) {
    exit 1
}
Write-Host "All tests passed."
