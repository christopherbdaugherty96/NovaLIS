# NovaLIS Quickstart

Get Nova running locally and try a few safe first commands.

For exact live status after startup, use `docs/current_runtime/CURRENT_RUNTIME_STATE.md`.
For detailed setup help, see `docs/reference/HUMAN_GUIDES/26_LOCAL_SETUP_AND_STARTUP.md`.

---

## What You Need
- Windows is the primary target today
- Python 3.10+
- Ollama installed
- A local checkout folder

Optional features like voice, Shopify, and calendar snapshots need extra setup later.
Core assistant flows should still run without them.

---

## Install

```bash
git clone https://github.com/christopherbdaugherty96/NovaLIS.git
cd NovaLIS
pip install -e .
```

Pull local models used by your configuration:

```bash
ollama pull gemma4:e4b
ollama pull gemma2:2b
```

---

## Start Nova

```bash
nova-start
```

Open in browser:

```text
http://localhost:8000
```

---

## First Things To Try

```text
system status
what can you do
weather
news
daily brief
```

Local actions:

```text
open downloads
mute
pause
```

Draft workflow:

```text
draft an email to test@example.com about the weekly update
```

Nova should help draft it. You review before sending.

---

## If Something Breaks

### UI does not open
- confirm `nova-start` is running
- open `http://localhost:8000`
- check terminal logs

### Model issues
- confirm Ollama is running
- confirm models are pulled
- retry after startup settles

### Action blocked
- it may require confirmation
- try clearer wording
- check trust/runtime surfaces

---

## Next Reading
- `USE_CASES.md`
- `docs/INDEX.md`
- `docs/reference/ARCHITECTURE.md`
