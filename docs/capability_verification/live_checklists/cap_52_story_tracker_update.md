# Live Test Checklist — Cap 52: story_tracker_update
Phase 5 of 6 · Priority: High (persistent_change)

## Test 1 — Track a story
1. Type: `track story AI regulation`
2. ✅ Nova confirms story is now being tracked
3. ✅ Check Trust page — `ACTION_COMPLETED` logged for story_tracker_update

## Test 2 — Follow phrasing
1. Type: `follow story electric vehicles`
2. ✅ Story added to tracking

## Test 3 — Update tracked stories
1. Type: `update tracked stories`
2. ✅ Nova fetches fresh data for all tracked stories

## Test 4 — Stop tracking
1. Type: `stop tracking AI regulation`
2. ✅ Story removed from tracking list

## Sign-off
```
python scripts/certify_capability.py live-signoff 52
python scripts/certify_capability.py lock 52
```
