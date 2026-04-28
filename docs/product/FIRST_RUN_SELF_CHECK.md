# First Run Self-Check

Use this checklist after starting Nova for the first time.

## Core Checks
- Does `nova-start` launch without errors?
- Can you open `http://localhost:8000`?
- Does the dashboard load?
- Does chat respond?

## Model Checks
- Is Ollama running?
- Are required models installed?
- Are responses reasonably fast on your hardware?

## Feature Checks
Try:
```text
system status
weather
news
daily brief
```

## Local Action Checks
Try:
```text
mute
open downloads
```
Confirm actions are visible and bounded.

## If Something Fails
- Re-read QUICKSTART.md
- Review terminal logs
- Check local model availability
- Confirm optional integrations are configured

## Honest Note
Performance and available features depend on your local setup.
