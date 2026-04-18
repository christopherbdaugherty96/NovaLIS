# Live Test Checklist — Cap 63: openclaw_execute
Phase 5 of 6 · Priority: Medium (read_only_network)

## Pre-conditions
- [ ] OpenClaw templates are configured
  (at least `morning_brief` template should exist)

## Test 1 — Morning brief template
1. Type: `morning brief`
2. ✅ OpenClaw morning brief executes
3. ✅ Result includes weather, news, calendar sections
4. ✅ Loads in < 45 seconds

## Test 2 — Run a named template
1. Type: `run morning_brief`
2. ✅ Same result

## Test 3 — Unknown template
1. Type: `run nonexistent_template_12345`
2. ✅ Nova gives a clear "template not found" or similar message (no crash)

## Sign-off
```
python scripts/certify_capability.py live-signoff 63
python scripts/certify_capability.py lock 63
```
