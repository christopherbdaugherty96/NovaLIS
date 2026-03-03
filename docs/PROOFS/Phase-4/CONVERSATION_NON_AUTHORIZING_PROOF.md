# Conversation Non-Authorizing Proof
Date: 2026-03-03  
Scope: Escalation & Conversation Subsystem

---

## 1. Architecture Separation

Conversation subsystem:

```
src/conversation/
├── complexity_heuristics.py
├── escalation_policy.py
├── response_formatter.py
├── response_style_router.py
├── safety_filter.py
├── thought_store.py
├── deepseek_bridge.py
└── deepseek_safety_wrapper.py
```

**Verified invariants (confirmed against source code):**

- No capability imports in any file under `src/conversation/`
- No `ActionRequest` construction in any file under `src/conversation/`
- No registry access in any file under `src/conversation/`
- No `DecisionToken` creation
- No direct tool invocation
- No `Governor` import or call

Conversation produces only text responses.

Execution requires Governor invocation.

---

## 2. DeepSeekBridge — Local Model Only

`DeepSeekBridge` in `src/conversation/deepseek_bridge.py` uses **local Ollama/phi3:mini** exclusively:

```python
import ollama
response = ollama.chat(
    model="phi3:mini",
    messages=[{"role": "user", "content": prompt}],
    options={"temperature": 0.2, "num_predict": MAX_TOKENS},
)
```

- **No NetworkMediator usage** — `DeepSeekBridge` does not import or call `NetworkMediator`.
- **No external API calls** — no `requests`, `httpx`, or `aiohttp` imports in any conversation module.
- Full DeepSeek cloud API integration is design-only. Not implemented.
- `DeepSeekBridge` is stateless and user-invoked only.

---

## 3. Module Roles (Non-Authorizing)

| Module | Role | Authority? |
|---|---|---|
| `ComplexityHeuristics` | Returns metadata (complexity score, flags) | None — never returns execution authority |
| `EscalationPolicy` | Returns `ALLOW`/`DENY`/`ASK_USER` for deep analysis routing | None — not for capability execution |
| `ResponseStyleRouter` | Deterministic keyword matching for response style selection | None — text routing only |
| `ResponseFormatter` | Formats text output | None — text only |
| `SafetyFilter` | Content safety check | None — returns boolean/modified text |
| `ThoughtStore` | Ephemeral in-session thought accumulation | None — no persistence, no execution |
| `DeepSeekBridge` | Local Ollama analysis call | None — returns text analysis only |
| `DeepSeekSafetyWrapper` | Wraps DeepSeekBridge with safety checks | None — text only |

---

## 4. Escalation Safety

Escalation may:
- Produce deeper analysis
- Format structured output
- Access DeepSeekBridge (local Ollama only)

Escalation may NOT:
- Execute system actions
- Launch executors
- Modify files
- Open network channels directly
- Construct `ActionRequest` objects
- Return capability IDs as execution instructions

`EscalationPolicy` returns `ALLOW`/`DENY`/`ASK_USER` for deep analysis decisions — this is **not** for capability execution authorization.

---

## 5. Injection Resistance

Prompt injection test performed:

Chinese instruction appended within conversation.

Result:
- No action executed
- No authority escalation
- Governor not invoked

System correctly treated content as text.

---

## 6. Fail-Closed Behavior

When deep analysis unavailable:

System returns:
"Deep analysis service temporarily unavailable."

No fallback to unauthorized execution.
No attempt to simulate missing capability.

---

## 7. Authority Boundary Conclusion

Conversation layer is:

Text-only  
Non-executing  
Non-authorizing  
Governor-dependent  
Local-model-only (DeepSeekBridge uses Ollama/phi3:mini; no external network)

All execution authority remains exclusively in the Governor.

End of document.