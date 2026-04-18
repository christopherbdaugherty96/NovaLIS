# Live Test Checklist — Cap 54: analysis_document
Phase 5 of 6 · Priority: Medium (read_only_local)

## Test 1 — Create a document
1. Type: `create a report on the state of AI in healthcare`
2. ✅ Analysis document created (takes up to 2.5 minutes — LLM generation)
3. ✅ Document has sections (findings, analysis, etc.)

## Test 2 — List documents
1. Type: `list my analysis docs`
2. ✅ Document list returned showing the one just created

## Test 3 — Summarize a document
1. Type: `summarize doc 1`
2. ✅ Compact summary of document 1 returned

## Test 4 — Explain a section
1. Type: `explain section 1`
2. ✅ Section 1 of the most recent doc explained in more depth

## Sign-off
```
python scripts/certify_capability.py live-signoff 54
python scripts/certify_capability.py lock 54
```
