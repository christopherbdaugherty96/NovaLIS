# Live Test Checklist — Cap 32: os_diagnostics
Phase 5 of 6 · Priority: Medium (read_only_local)

## Test 1 — System check
1. Type: `system check`
2. ✅ Nova returns a system status widget
3. ✅ Shows CPU, memory, or similar metrics
4. ✅ Shows Ollama model status (running / not running)
5. ✅ Shows active capabilities count

## Test 2 — Alternative phrasing
1. Type: `how is Nova doing`
2. ✅ Same or similar diagnostic response

## Test 3 — System status question
1. Type: `what is the system status`
2. ✅ Diagnostic response returned

## Sign-off
```
python scripts/certify_capability.py live-signoff 32
python scripts/certify_capability.py lock 32
```
