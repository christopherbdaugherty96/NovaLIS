Write-Host "=== Legacy Brain Isolation Check ===" -ForegroundColor Cyan

$legacyFile = "nova_backend/src/archive_quarantine/phase2_execution/brain_safeP1-2.5.py"
$runtimeDir = "nova_backend/src"

# 1. Check file exists
if (Test-Path $legacyFile) {
    Write-Host "✅ Legacy brain exists in quarantine" -ForegroundColor Green
    $size = (Get-Item $legacyFile).Length
    Write-Host "   Size: $size bytes" -ForegroundColor Gray
} else {
    Write-Host "❌ Legacy brain not found" -ForegroundColor Red
    exit 1
}

# 2. Check it's NOT in runtime path
$runtimeBrain = Get-ChildItem -Path $runtimeDir -Filter "brain_safeP1-2.5.py" -Recurse -ErrorAction SilentlyContinue
if ($runtimeBrain) {
    Write-Host "❌ CRITICAL: Legacy brain found in runtime path!" -ForegroundColor Red
    $runtimeBrain | ForEach-Object { Write-Host "   Found at: $($_.FullName)" }
    exit 1
} else {
    Write-Host "✅ No legacy brain in runtime path" -ForegroundColor Green
}

# 3. Check for imports in runtime code
Write-Host "`n=== Checking for imports in runtime code ===" -ForegroundColor Cyan
$foundImports = $false
Get-ChildItem -Path $runtimeDir -File -Filter "*.py" -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -notmatch "archive_quarantine" -and $_.FullName -notmatch "__pycache__"
} | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -match "brain_safeP1-2\.5") {
        Write-Host "❌ Found reference in: $($_.Name)" -ForegroundColor Red
        Write-Host "   Path: $($_.FullName)" -ForegroundColor Gray
        $foundImports = $true
    }
}

if ($foundImports) {
    Write-Host "`n❌ FAIL: Runtime code imports quarantined file!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ No imports of quarantined file found" -ForegroundColor Green
}

# 4. Quick check of Python import system
Write-Host "`n=== Python import path check ===" -ForegroundColor Cyan
$pythonCheck = @"
import sys
quarantine_path = r'$((Get-Item $legacyFile).DirectoryName)'
in_path = quarantine_path in sys.path
print(f"Quarantine path in sys.path: {in_path}")
if in_path:
    print(f"WARNING: Quarantine directory is importable!")
"@

$pythonCheck | python 2>&1

Write-Host "`n=== Isolation Status: PASS ===" -ForegroundColor Green
Write-Host "The legacy brain is properly quarantined and should not be importable."
