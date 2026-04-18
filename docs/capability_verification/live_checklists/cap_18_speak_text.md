# Live Test Checklist — Cap 18: speak_text
Phase 5 of 6 · Priority: Medium (reversible_local)

## Pre-conditions
- [ ] Speakers or headphones connected and working
- [ ] System volume is not muted

## Test 1 — Speak last response
1. Ask Nova any question — get a chat response
2. Type: `read that out loud`
3. ✅ Nova speaks the response aloud (TTS plays)
4. ✅ Audio is clear, not garbled

## Test 2 — Alternative trigger
1. Type: `say it`
2. ✅ Same behavior

## Test 3 — Nothing to speak
1. Fresh session, no prior response
2. Type: `speak that`
3. ✅ Nova handles gracefully (message about nothing to speak, no crash)

## Sign-off
```
python scripts/certify_capability.py live-signoff 18
python scripts/certify_capability.py lock 18
```
