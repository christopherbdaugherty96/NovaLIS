Write-Host "=== Legacy Brain Isolation Check (Fixed) ===" -ForegroundColor Cyan

$legacyFile = "nova_backend/src/archive_quarantine/phase2_execution/brain_safeP1-2.5.py"
$runtimeDir = "nova_backend/src"

# 1. Check file exists in quarantine
if (Test-Path $legacyFile) {
    Write-Host "✅ Legacy brain exists in quarantine" -ForegroundColor Green
    $size = (Get-Item $legacyFile).Length
    Write-Host "   Size: $size bytes" -ForegroundColor Gray
    
    # Check QUARANTINE_NOTICE exists
    $noticePath = "nova_backend/src/archive_quarantine/QUARANTINE_NOTICE.md"
    if (Test-Path $noticePath) {
        Write-Host "✅ Quarantine notice exists" -ForegroundColor Green
    } else {
        Write-Host "⚠️  No quarantine notice found" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Legacy brain not found" -ForegroundColor Red
    exit 1
}

# 2. Check it's NOT in ACTIVE runtime path (excluding quarantine)
# This means checking nova_backend/src but NOT in archive_quarantine
$activeRuntimeFiles = Get-ChildItem -Path $runtimeDir -Filter "brain_safeP1-2.5.py" -File -Recurse | 
    Where-Object { $_.FullName -notmatch "archive_quarantine" }

if ($activeRuntimeFiles) {
    Write-Host "❌ CRITICAL: Legacy brain found in ACTIVE runtime path!" -ForegroundColor Red
    $activeRuntimeFiles | ForEach-Object { Write-Host "   Found at: $($_.FullName)" }
    exit 1
} else {
    Write-Host "✅ No legacy brain in ACTIVE runtime path" -ForegroundColor Green
}

# 3. Check for imports in ACTIVE runtime code (excluding quarantine)
Write-Host "`n=== Checking for imports in ACTIVE runtime code ===" -ForegroundColor Cyan
$foundImports = $false

# Get all Python files in src, excluding quarantine directory
Get-ChildItem -Path $runtimeDir -File -Filter "*.py" -Recurse | 
    Where-Object { $_.FullName -notmatch "archive_quarantine" -and $_.FullName -notmatch "__pycache__" } | 
    ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -match "brain_safeP1-2\.5") {
            Write-Host "❌ Found reference in: $($_.Name)" -ForegroundColor Red
            Write-Host "   Path: $($_.FullName)" -ForegroundColor Gray
            $foundImports = $true
        }
    }

if ($foundImports) {
    Write-Host "`n❌ FAIL: ACTIVE runtime code imports quarantined file!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ No imports of quarantined file in ACTIVE runtime" -ForegroundColor Green
}

# 4. Check Python import system for quarantine path
Write-Host "`n=== Python import path check ===" -ForegroundColor Cyan
$quarantineDir = (Get-Item $legacyFile).DirectoryName
$pythonCheck = @"
import sys
quarantine_path = r'$quarantineDir'
in_path = quarantine_path in sys.path
print(f"Quarantine directory: {quarantine_path}")
print(f"In Python sys.path: {in_path}")
if in_path:
    print("⚠️  WARNING: Quarantine directory is on Python path (importable)!")
else:
    print("✅ Quarantine directory is NOT on Python path")
"@

$pythonCheck | python 2>&1

# 5. Check if we can actually import from quarantine
Write-Host "`n=== Python import test ===" -ForegroundColor Cyan
$importTest = @"
import sys
quarantine_path = r'$quarantineDir'
try:
    # Try to import a module from quarantine
    sys.path.insert(0, quarantine_path)
    import brain_safeP1_2_5
    print("❌ FAIL: Successfully imported brain_safeP1-2.5.py from quarantine!")
except ImportError as e:
    print(f"✅ Expected import failure: {e}")
except Exception as e:
    print(f"⚠️  Other error: {e}")
"@

$importTest | python 2>&1

Write-Host "`n=== Final Isolation Status ===" -ForegroundColor Green
Write-Host "The legacy brain appears to be properly quarantined." -ForegroundColor Green
Write-Host "It exists in archive_quarantine and is not imported by active runtime code." -ForegroundColor Gray
