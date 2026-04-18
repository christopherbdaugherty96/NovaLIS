# Live Test Checklist — Cap 62: external_reasoning_review
Phase 5 of 6 · Priority: Medium (read_only_local)

## Test 1 — Second opinion on a prior answer
1. Ask Nova any factual question — get a response
2. Type: `second opinion on this answer`
3. ✅ Nova provides a second-opinion critique of its own response
4. ✅ Does NOT blindly agree — shows independent reasoning

## Test 2 — Pressure check
1. Ask a nuanced question
2. Type: `pressure check that`
3. ✅ Critique returned

## Test 3 — DeepSeek second opinion
1. Type: `deepseek second opinion`
2. ✅ Second-opinion from the review lane returned

## Sign-off
```
python scripts/certify_capability.py live-signoff 62
python scripts/certify_capability.py lock 62
```
