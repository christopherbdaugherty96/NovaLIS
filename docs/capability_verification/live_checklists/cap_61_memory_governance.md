# Live Test Checklist — Cap 61: memory_governance
Phase 5 of 6 · Priority: HIGH (persistent_change — user data)

## Test 1 — Save a memory
1. Type: `remember this: I prefer dark mode in all apps`
2. ✅ Nova confirms memory saved
3. ✅ Check Trust page — event logged

## Test 2 — List memories
1. Type: `list memories`
2. ✅ The saved memory appears in the list

## Test 3 — Search memories
1. Type: `search memories for dark mode`
2. ✅ The saved memory is found

## Test 4 — Show a memory
1. From the list, note the memory ID
2. Type: `memory show <id>`
3. ✅ Memory details displayed

## Test 5 — Lock a memory
1. Type: `memory lock <id>`
2. ✅ Memory marked as locked

## Test 6 — Delete a memory (use a test one)
1. Save a throwaway memory: `remember this: TEST MEMORY TO DELETE`
2. Get its ID from `list memories`
3. Type: `memory delete <id> confirmed`
4. ✅ Memory removed
5. ✅ Confirm it no longer appears in list

## Test 7 — Export
1. Type: `export my memory`
2. ✅ Memory export file created or download offered

## Sign-off
```
python scripts/certify_capability.py live-signoff 61
python scripts/certify_capability.py lock 61
```
