# NovaLIS Quickstart

Run Nova locally from source and reach a first success.

## What you need

- Windows 10 or 11 (primary target; macOS and Linux are source-development only)
- Python 3.10, 3.11, or 3.12
- [Ollama](https://ollama.com) running locally, with the default model pulled:

  ```bash
  ollama pull gemma4:e4b
  ```

Optional features (external reasoning, metered providers, Shopify reports, calendar files)
need their own keys or settings and are off until you configure them.

## Install

```bash
git clone https://github.com/christopherbdaugherty96/NovaLIS.git
cd NovaLIS
pip install -e .
```

## Start

```bash
nova-start
```

Open `http://127.0.0.1:8000` in your browser.

On Windows you can also use the launcher, which waits for the backend and opens the dashboard
in an app-style window when Edge or Chrome is available:

```bat
start_nova.bat
```

Stop the backend with `stop_nova.bat`.

## Keep it local

Nova is designed to be reachable only from the machine it runs on.

- Leave `NOVA_HOST` unset (it defaults to `127.0.0.1`). Do not set it to `0.0.0.0` or a LAN
  address.
- Do not put Nova behind a tunnel, reverse proxy, or port forward.
- Remote access is not supported in this release.

## First run

Nova pins the exact local model it talks to. On first run, and whenever the model, its
settings, or Nova's prompt change, model-backed replies stay blocked until you confirm the
model by typing `confirm model update` in the chat. The confirmation is recorded in Nova's
ledger.

Start Ollama before Nova, and confirm only while Ollama is running. If Nova cannot reach Ollama
it cannot read the model's fingerprint; confirming in that state unlocks inference without a real
fingerprint, and no second confirmation is requested when Ollama comes back during that session.

## First commands

1. `What works today?`
2. `What capabilities are active?`
3. `Summarize today's news.`
4. `remember: My preferred tone is concise.`
5. `Draft an email to test@example.com about tomorrow.`

## Installer

No installer is currently published. Do not build one from a working copy that has been used
to run Nova: runtime data such as memory, settings, and keys is written under
`nova_backend/src/data/` in a source checkout. Installer builds must come from a clean export of
an exact commit.

## If something breaks

- Confirm `pip install -e .` completed and `nova-start` is on your PATH.
- Confirm Ollama is running and the model is pulled.
- Check the terminal output.
- Check [Known Limitations](docs/product/KNOWN_LIMITATIONS.md) and the generated
  [Current Runtime State](docs/current_runtime/CURRENT_RUNTIME_STATE.md).
