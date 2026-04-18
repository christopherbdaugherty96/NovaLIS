# Live Test Checklist — Cap 57: calendar_snapshot
Phase 5 of 6 · Priority: Medium (read_only_local)

## Test 1 — Today's schedule
1. Type: `what do I have today`
2. ✅ Calendar widget appears
3. ✅ Shows today's events OR clear "no calendar connected" message

## Test 2 — Agenda
1. Type: `my schedule`
2. ✅ Same result

## Test 3 — Tomorrow
1. Type: `what's on tomorrow`
2. ✅ Tomorrow's agenda shown

## Test 4 — Without calendar connected
1. If no calendar is configured, verify Nova gives a helpful setup message
   rather than a crash or blank screen

## Sign-off
```
python scripts/certify_capability.py live-signoff 57
python scripts/certify_capability.py lock 57
```
