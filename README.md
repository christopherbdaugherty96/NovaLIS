# Nova — Your Local Intelligence System

Nova is a private, offline-capable AI assistant that runs entirely on your
own computer. No cloud, no data harvesting, no surprises.

---

## What it does today

- Chat with a local LLM (via [Ollama](https://ollama.com))
- Search the web (optional — you supply the API key)
- Control your media, volume, and brightness
- Open websites, files, and folders

## Why Nova

- **Your data stays yours** — everything runs on your machine
- **Works without internet** — core features do not require a network
- **Every action is logged and auditable** — an append-only ledger records what Nova did and why

## Quick start

1. Install [Ollama](https://ollama.com) and pull a supported model (e.g. `ollama pull gemma4:e4b`).
2. Clone this repository.
3. From the repo root, run `pip install -e .`
4. Launch Nova with `nova-start`.
5. Open <http://localhost:8000> in your browser.

A one-click Windows installer is on the [roadmap](4-15-26%20NEW%20ROADMAP/MasterRoadMap.md).

## Roadmap

- Windows / macOS installer
- Email drafting (Gmail / Outlook, with explicit permission)
- Calendar read + suggest
- Backup, uninstaller, offline awareness

See [`4-15-26 NEW ROADMAP/MasterRoadMap.md`](4-15-26%20NEW%20ROADMAP/MasterRoadMap.md) for the full plan and [`4-15-26 NEW ROADMAP/Now.md`](4-15-26%20NEW%20ROADMAP/Now.md) for the current sprint.

## Learn more

- [Introduction → what Nova is and why it exists](docs/INTRODUCTION.md)
- [Architecture → how the governance spine works](docs/ARCHITECTURE.md)
- [Landing page / waitlist](http://localhost:8000/landing) (run Nova first, or see `nova_backend/static/landing/`)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

---

*Nova is early software. It is real, it is honest about what it can and cannot do, and it is built for people who want control over their own assistant.*
