# User Ready Status

This page translates internal phase/capability status into plain-language user readiness.

## Works Now (Expected Core Paths)
- Local chat / assistant interaction
- Documentation-guided setup and startup
- Runtime status documentation
- Governed capability framework
- Research / reporting surfaces (varies by local setup and keys)
- Memory governance surfaces
- Dashboard experience

## Experimental / Advanced
- OpenClaw governed worker runtime
- Screen capture / screen analysis workflows
- Connector-based workflows
- Advanced operator automations
- Some write-capable or mutation workflows

## Requires Local Setup
- Ollama / local models
- Optional API keys or connectors (weather, news, Shopify)
- OS-specific controls (brightness, media, volume)
- Voice input (STT): Vosk model at `nova_backend/models/vosk-model-small-en-us-0.15/`
- Voice output (TTS): Piper binary + `.onnx` model file + `NOVA_PIPER_MODEL_PATH` env var; pyttsx3 is a fallback on Windows
- ICS calendar: local `.ics` file path must be configured for `calendar_snapshot`

## Not Yet Implemented
- Email inbox reading — the email connector interface exists but is a stub; inbox access is not connected
- Trust Panel dashboard UI — not yet built; the receipt data API (`GET /api/trust/receipts`) is live, but no in-dashboard card renders it yet

## Not Yet Product-Ready
- One-click mainstream installer
- Guided first-run wizard
- Fully polished trust surface for all actions
- Broad nontechnical onboarding
- Mainstream consumer release readiness

## Guidance
If you are technical and comfortable with local tooling, Nova may already be useful. If you expect a polished consumer install-and-go product, treat Nova as early software.