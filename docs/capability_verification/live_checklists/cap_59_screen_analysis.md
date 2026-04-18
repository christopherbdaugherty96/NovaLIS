# Live Test Checklist — Cap 59: screen_analysis
Phase 5 of 6 · Priority: Medium (read_only_local)

## Test 1 — Analyze the screen
1. Have something meaningful on screen (a document, website, error message)
2. Type: `analyze this screen`
3. ✅ Nova analyzes what's on screen and explains it
4. ✅ Response is relevant to what was visible

## Test 2 — Explain a specific element
1. Type: `explain this screen`
2. ✅ Nova describes what it sees in detail

## Test 3 — Read the screen
1. Type: `read this screen`
2. ✅ Nova reads visible text or explains visible content

## Sign-off
```
python scripts/certify_capability.py live-signoff 59
python scripts/certify_capability.py lock 59
```
