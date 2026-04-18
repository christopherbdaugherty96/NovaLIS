# Live Test Checklist — Cap 22: open_file_folder
Phase 5 of 6 · Priority: Medium-High (reversible_local, requires_confirmation)

## Test 1 — Open Downloads folder
1. Type: `open my downloads folder`
2. ✅ Confirmation prompt appears
3. Click Confirm
4. ✅ File Explorer opens to Downloads folder

## Test 2 — Open Documents
1. Type: `open documents`
2. Confirm
3. ✅ Documents folder opens

## Test 3 — Open Desktop
1. Type: `open desktop`
2. Confirm
3. ✅ Desktop folder opens

## Test 4 — Open a specific file (if available)
1. Type: `open file C:\Users\<you>\Documents\some_file.txt`
2. ✅ Confirmation appears, then file opens in default app

## Test 5 — Confirmation gate
1. Type: `open my downloads folder`
2. Dismiss the confirmation prompt — do NOT confirm
3. ✅ Folder does NOT open

## Sign-off
```
python scripts/certify_capability.py live-signoff 22
python scripts/certify_capability.py lock 22
```
