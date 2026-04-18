# Live Test Checklist — Cap 19: volume_up_down
Phase 5 of 6 · Priority: Medium (reversible_local)

## Test 1 — Volume up
1. Type: `volume up`
2. ✅ System volume increases (check volume indicator in taskbar)

## Test 2 — Volume down
1. Type: `volume down`
2. ✅ System volume decreases

## Test 3 — Set specific level
1. Type: `set volume to 50`
2. ✅ System volume sets to 50%

## Test 4 — Numeric shorthand
1. Type: `volume 30`
2. ✅ Volume sets to 30%

## Test 5 — Mute (if platform supports it)
1. Type: `mute`
2. ✅ Volume mutes OR Nova gives a clear "not available on this device" message

## Sign-off
```
python scripts/certify_capability.py live-signoff 19
python scripts/certify_capability.py lock 19
```
