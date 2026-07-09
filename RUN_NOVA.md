# Run Nova

This is the shortest path from a fresh checkout to seeing Nova run.

Nova is an alpha local app. Windows is the primary target today.

## Requirements

- Python 3.10 or newer
- Git
- A local checkout of this repository
- Optional: local model/runtime setup for LLM-backed answers

## Install

```bash
git clone https://github.com/christopherbdaugherty96/NovaLIS.git
cd NovaLIS
pip install -e .
```

For development and proof checks:

```bash
pip install -e ".[dev]"
```

## Start

```bash
nova-start
```

Then open:

```text
http://127.0.0.1:8000/
```

On Windows, this repo also includes:

```bat
start_nova.bat
```

To stop the local backend:

```bat
stop_nova.bat
```

## First Prompts

Try these in the dashboard:

```text
What works today?
Explain what Nova can do.
What is 12 * 8?
Summarize today's news.
Draft an email to test@example.com about a quick hello.
```

Expected shape:

- local informational prompts should answer without creating external effects
- news/search/weather may depend on local network/configuration
- email draft should stop at a confirmation boundary before opening a local mail client draft
- unsupported connectors should degrade honestly instead of pretending to work

## One-Command Proof

Run:

```bash
python scripts/prove_runtime_truth.py
```

Expected output includes lines like:

```text
PASS: backend app imports
PASS: dashboard root returns 200
PASS: websocket /ws accepts a connection
PASS: capability registry loads active capabilities
PASS: cap 64 requires confirmation
PASS: Governor blocks cap 64 without confirmation
```

The proof command uses FastAPI's in-process test client. It does not need to keep a browser or server process open.

## If It Fails

Check:

- Python version
- dependency install
- whether another process is already using port 8000
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `RUNTIME_TRUTH.md`
- `GOVERNANCE_PROOF.md`
