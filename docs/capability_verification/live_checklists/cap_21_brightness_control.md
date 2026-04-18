# Live Test Checklist — Cap 21: brightness_control
Phase 5 of 6 · Priority: Medium (reversible_local)

## Pre-conditions
- [ ] Device has a controllable display (laptop, not external monitor only on some systems)

## Test 1 — Brightness up
1. Type: `brightness up`
2. ✅ Display brightness increases OR clear "not available" message

## Test 2 — Brightness down
1. Type: `make the screen dimmer`
2. ✅ Brightness decreases

## Test 3 — Set specific level
1. Type: `set brightness to 70`
2. ✅ Brightness sets to approximately 70%

## Note
Brightness control requires platform support. On desktop PCs with external
monitors, this may not be available. Verify Nova responds gracefully.

## Sign-off
```
python scripts/certify_capability.py live-signoff 21
python scripts/certify_capability.py lock 21
```
