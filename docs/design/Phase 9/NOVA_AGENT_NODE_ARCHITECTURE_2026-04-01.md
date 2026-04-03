# Nova — Agent over Contained Intelligence: Honest Assessment & Path Forward
Updated: 2026-04-01

---

## Is Nova Currently an "Agent over Contained Intelligence"?

**Partially yes** — but it is currently structured more as a **governed tool executor** than a true agent.

---

## What Nova IS Right Now

| Property | Status | Notes |
|---|---|---|
| Governed | ✅ | The Governor is a real constitutional authority layer — all execution passes through a single choke point |
| Local-first | ✅ | All intelligence runs on your machine via Ollama |
| Contained | ✅ | Hard capability boundaries, ledger-audited, budget-gated (Phase 9) |
| Agent-like | ✅ | OpenClaw does multi-step planning: collect → summarize → deliver |
| Node-ready foundation | ✅ | The WebSocket protocol, ledger, and executor architecture are designed for distribution |

## What Nova is NOT Yet

| Property | Status | Notes |
|---|---|---|
| True autonomous agent | ❌ | Nova cannot self-initiate goals or chain multi-step reasoning on its own without user prompt |
| A node | ❌ | No peer-to-peer or inter-node communication layer yet |
| Owned intelligence | ❌ | `gemma2:2b` via Ollama is a small model being called as a service — Nova routes through it but does not own or grow it |

---

## The Core Constraint: Local Model Intelligence Ceiling

The local model is the binding constraint on agentic capability. Here is the honest picture:

| What Nova runs | Model | VRAM needed | What you get |
|---|---|---|---|
| Default | `gemma2:2b` | ~2–3 GB | Fast, basic reasoning |
| Fallback | `phi3:mini` | ~2–3 GB | Similar quality |
| Real step up | `gemma2:9b` | ~6–8 GB | Much better reasoning |
| Serious step up | `llama3.1:8b` | ~6–8 GB | Very capable |
| Agent-grade | `llama3.1:70b` | ~40–48 GB | True agentic reasoning |
| Node-viable | `mistral:7b` / `mixtral:8x7b` | 5–48 GB | Good for routing tasks |

If your GPU cannot push past 2b or mini models without crawling, the intelligence ceiling is genuinely low — not because the code is broken, but because the foundation model is small.

---

## The Path Forward: Agent → Node

### Phase NOW (current)
```
Nova = Governed Shell → calls gemma2:2b → returns result
Problem: gemma2:2b is not capable enough for real agentic reasoning chains
```

### Phase NEXT (no GPU upgrade required)
```
Nova = Agent Shell → routes complex tasks to cloud model via API key
                     (GPT-4o, Claude Sonnet, Gemini)

The code already has this:
  nova_backend/src/providers/openai_responses_lane.py

Currently: used only as a fallback for OpenClaw briefing tasks
Should be: promoted to PRIMARY reasoning engine for tasks that exceed
           local model capability, governed by existing budget system

Cost: ~$0.01–0.05 per complex conversation
Result: Real intelligence without GPU upgrade
```

### Phase AFTER (node-ready)
```
Nova = Node → exposes a governed API endpoint
              Other Nova instances or services call YOUR Nova as a specialist node

Already in place:
  - WebSocket ↔ REST bridge architecture (brain_server.py + session_handler.py)
  - Ledger with full audit trail per action
  - Capability registry is structured for distributed routing

Still needed:
  - WebSocket → REST bridge for external callers
  - Node discovery protocol
  - Trust protocol between nodes (governor-to-governor handshake)
```

---

## The Immediate Recommendation

**Promote `openai_responses_lane.py` to primary reasoning engine for complex tasks.**

Nova already has the infrastructure — it just needs to be activated as the default for reasoning-heavy requests:

```
Small/fast things (gemma2:2b) → handled locally          ✅ already works
Complex reasoning, agentic tasks → routed to GPT-4o/Claude via OpenAI lane  ✅ code exists, needs wiring
Budgeted and logged just like everything else             ✅ Phase 9 budget gate already enforces this
No GPU upgrade needed                                     ✅
```

**What this requires:**
1. Set `OPENAI_API_KEY` in your `.env` (now documented in `.env.example`)
2. Set `MODEL_PROVIDER=auto` to enable the routing logic
3. The existing `provider_usage_store` and Phase 9 budget gate apply automatically — no new governance needed

---

## Architectural Reality Check

Nova's codebase is already structured for the agent-node future:

- **Governor**: Single authority choke point — suitable as the trust broker in a node network
- **Capability registry**: JSON-driven, extensible — nodes can declare their own capability surfaces
- **Ledger**: Append-only audit trail — provides accountability across node boundaries
- **Budget gate**: Token-aware — prevents runaway costs in automated chains
- **OpenClaw executor**: Already does multi-step template execution — the pattern for agent chains

The missing pieces are soft (model quality, cloud routing config) not hard (architecture). The hard infrastructure is in place.

---

## What "Agent over Contained Intelligence" Means for Nova

Nova is not an agent **yet** in the autonomous sense. It is a **governed intelligence surface** — a shell that can be upgraded to agentic reasoning by:

1. Connecting better intelligence (larger local model or cloud API)
2. Enabling multi-step planning chains (extend OpenClaw templates)
3. Adding peer trust protocols (node-to-node governor handshake)

The governance layer — the thing that makes this safe — is already mature. The intelligence layer is the current ceiling.

---

## Decision Point

| Choice | Trade-off | Recommendation |
|---|---|---|
| Stay fully local (`gemma2:2b`) | Free, private, limited reasoning | Keep as default; acceptable for simple tasks |
| Add cloud reasoning (`OPENAI_API_KEY` + `MODEL_PROVIDER=auto`) | ~$0.01–0.05/complex task, full intelligence | **Do this now** — infrastructure ready |
| GPU upgrade to 8b+ model | One-time cost, fully private, real capability | Future option when budget allows |
| Build node protocol | High effort, enables distributed Nova | Phase 10+ roadmap item |
