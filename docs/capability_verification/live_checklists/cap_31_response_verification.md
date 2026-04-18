# Live Test Checklist — Cap 31: response_verification
Phase 5 of 6 · Priority: Medium (read_only_local)

## Test 1 — Verify a prior answer
1. Ask Nova a factual question (e.g., "what is the capital of France?")
2. Get a response
3. Type: `verify that`
4. ✅ Nova gives a verification analysis — not just repeats the answer
5. ✅ Response notes confidence level or points out any issues

## Test 2 — Verify with text
1. Type: `verify the claim that water boils at 100 degrees Celsius at sea level`
2. ✅ Nova verifies the claim with reasoning

## Test 3 — Fact-check phrasing
1. Type: `fact check this: the moon is made of cheese`
2. ✅ Nova clearly marks it false with explanation

## Sign-off
```
python scripts/certify_capability.py live-signoff 31
python scripts/certify_capability.py lock 31
```
