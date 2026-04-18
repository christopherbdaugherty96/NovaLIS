# Live Test Checklists

This folder contains one checklist per capability. You run through the
checklist manually with Nova running on your machine, then sign off with:

```
python scripts/certify_capability.py live-signoff {cap_id}
```

## Prerequisites for every live test

1. Nova is running — `nova-start` or `python -m uvicorn src.brain_server:app`
2. Browser is open at `http://localhost:8000`
3. Ollama is running with a model loaded (`ollama run gemma4:e4b`)

## After sign-off

Once you sign off a capability, you can lock it:

```
python scripts/certify_capability.py status        # check current state
python scripts/certify_capability.py lock {cap_id} # lock if all phases pass
```

## Order of priority (lock these first)

| Priority | Cap ID | Name | Reason |
|---|---|---|---|
| 1 | 64 | send_email_draft | external_effect=True, persistent_change |
| 2 | 61 | memory_governance | persistent_change — user data |
| 3 | 58 | screen_capture | persistent_change — screen data |
| 4 | 52 | story_tracker_update | persistent_change — tracked data |
| 5 | 22 | open_file_folder | requires_confirmation |
| 6 | 32 | os_diagnostics | always-on diagnostic |
| 7-26 | All others | reversible/read-only caps | Lower risk |
