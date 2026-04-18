# Live Test Checklist — Cap 49: headline_summary
Phase 5 of 6 · Priority: Medium (read_only_network)

## Test 1 — Summarize all headlines
1. Navigate to News page (or type `news` first to load headlines)
2. Type: `summarize all`
3. ✅ Summary of current headlines returned

## Test 2 — Category summary
1. Type: `summarize tech news`
2. ✅ Tech category headlines summarized

## Test 3 — By index
1. After loading headlines, type: `summarize 1 and 2`
2. ✅ Headlines 1 and 2 summarized

## Test 4 — Story page summary
1. Type: `summary of story 1`
2. ✅ Detailed summary of first headline returned

## Sign-off
```
python scripts/certify_capability.py live-signoff 49
python scripts/certify_capability.py lock 49
```
