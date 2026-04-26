# NovaLIS Quickstart

This guide gets a development checkout running and gives you a few safe first commands to verify the system.

For exact runtime truth after startup, use [docs/current_runtime/CURRENT_RUNTIME_STATE.md](docs/current_runtime/CURRENT_RUNTIME_STATE.md).

---

## Prerequisites

- Windows is the primary development target today.
- Python 3.10 or newer.
- Ollama installed for local model use.
- A writable checkout directory, such as `C:\Nova-Project`.

Optional connector features may need additional environment variables. Core local flows should still start without those connectors.

Optional features with additional requirements:

| Feature | What you need |
|---|---|
| Voice input (STT) | Vosk model at `nova_backend/models/vosk-model-small-en-us-0.15/` |
| Voice output (TTS) | Piper binary in PATH or at `nova_backend/tools/piper/piper.exe`; set `NOVA_PIPER_MODEL_PATH` to your `.onnx` model file |
| Calendar snapshot | An `.ics` calendar file; configure its path via the Nova Settings connector surface |
| Shopify intelligence | `NOVA_SHOPIFY_SHOP_DOMAIN` and `NOVA_SHOPIFY_ACCESS_TOKEN` env vars |

Run `system status` after startup to see which features are active on your machine.

---

## Install

```bash
git clone https://github.com/christopherbdaugherty96/NovaLIS.git
cd NovaLIS
pip install -e .
```

Pull the local model expected by your runtime configuration:

```bash
ollama pull gemma4:e4b
ollama pull gemma2:2b
```

---

## Start Nova

```bash
nova-start
```

Open:

```text
http://localhost:8000
```

First startup can take a little longer while local services and model checks settle.

---

## First Commands To Try

Start with low-risk read-only and local-control commands:

- `system status`
- `news`
- `daily brief`
- `weather`
- `open downloads`
- `pause`
- `mute`
- `what can you do`

Then try a governed draft workflow:

```text
draft an email to test@example.com about the weekly update
```

Nova should prepare a draft and require user review. Nova does not send email autonomously.

---

## Runtime State On Windows

Nova separates installed code from mutable runtime state.

- A repo/dev run from a writable checkout can keep runtime state with the checkout.
- An installed run from `C:\Program Files\Nova` must write mutable state under `%LOCALAPPDATA%\Nova`.

Mutable state includes settings, memory, usage tracking, model locks, policy data, OpenClaw runtime state, notifications, captures, and ledger files.

---

## Troubleshooting

If the dashboard does not open:

- confirm `nova-start` is still running
- try `http://localhost:8000`
- check the terminal output for port or model errors
- run `system status` once the UI loads

If Ollama fails:

- confirm Ollama is running
- confirm the expected model is pulled
- retry the command after the local model server settles

If an action is blocked:

- check whether it needs confirmation
- check the Trust or policy surface
- prefer explicit wording, such as `open downloads` instead of `open it`

If you need to run Nova on a non-default port or interface:

- set `NOVA_HOST` to override the bind address (default: `127.0.0.1`)
- set `NOVA_PORT` to override the port (default: `8000`)
- Nova defaults to loopback-only; binding to a non-loopback address removes the DNS rebinding protection

---

## Next Reading

- [Use cases](USE_CASES.md)
- [Docs index](docs/INDEX.md)
- [Architecture](docs/reference/ARCHITECTURE.md)
- [Capability verification](docs/reference/HUMAN_GUIDES/33_CAPABILITY_VERIFICATION_GUIDE.md)
