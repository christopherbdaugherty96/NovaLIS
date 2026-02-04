Write-Host "=== Phase 3.5 Constitutional Gates ===" -ForegroundColor Cyan

# Gate 1: No execution in runtime
Write-Host "`n[Gate 1] Checking for execution code..." -ForegroundColor Yellow
if (Test-Path "nova_backend/src/execution") {
    Write-Host "❌ FAIL: Execution code in runtime path" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS: No execution code in runtime" -ForegroundColor Green

# Gate 2: No legacy brain in runtime  
Write-Host "`n[Gate 2] Checking for legacy brain..." -ForegroundColor Yellow
$legacyBrain = Get-ChildItem "nova_backend/src" -Filter "*brain_safeP1-2.5.py" -Recurse -ErrorAction SilentlyContinue | 
    Where-Object { $_.FullName -notmatch "archive_quarantine" }
if ($legacyBrain) {
    Write-Host "❌ FAIL: Legacy brain in runtime" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS: Legacy brain properly quarantined" -ForegroundColor Green

# Gate 3: ConfirmationGate has message field
Write-Host "`n[Gate 3] Checking ConfirmationGate API..." -ForegroundColor Yellow
$gateCheck = @"
import sys
sys.path.insert(0, 'nova_backend/src')
try:
    from gates.confirmation_gate import GateResult
    result = GateResult(message="Test", confirmed=True)
    if result.message == "Test":
        print("PASS")
    else:
        print("FAIL")
except Exception:
    print("FAIL")
"@
$result = $gateCheck | python 2>&1
if ($result -match "FAIL") {
    Write-Host "❌ FAIL: ConfirmationGate API issue" -ForegroundColor Red
    exit 1
}
Write-Host "✅ PASS: ConfirmationGate API correct" -ForegroundColor Green

Write-Host "`n=== All Phase 3.5 gates passed ===" -ForegroundColor Green
