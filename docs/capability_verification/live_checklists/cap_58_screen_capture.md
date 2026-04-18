# Live Test Checklist — Cap 58: screen_capture
Phase 5 of 6 · Priority: High (persistent_change — stores screenshot file)

## Test 1 — Take a screenshot
1. Have something visible on screen (a browser window, document, etc.)
2. Type: `take a screenshot`
3. ✅ Nova confirms screenshot was taken
4. ✅ Response mentions what was captured (app name, window title, or similar)
5. ✅ No desktop flash or visual disruption

## Test 2 — Alternative phrasing
1. Type: `capture the screen`
2. ✅ Same result

## Test 3 — Ledger check
1. Go to Trust page
2. ✅ `SCREEN_CAPTURE_TAKEN` or similar event is logged

## Test 4 — Capture dependencies missing
1. If pyautogui or PIL is not installed, verify Nova gives a clear
   "missing dependency" message rather than a crash

## Sign-off
```
python scripts/certify_capability.py live-signoff 58
python scripts/certify_capability.py lock 58
```
