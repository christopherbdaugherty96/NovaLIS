# Cap 16 Governed Web Search — Certification Proof Packet

Date: 2026-05-10
Branch: `proof/cap-16-certification-lock`

---

## Starting State

From `capability_locks.json` before this branch:

```text
Cap 16 — governed_web_search
  p1_unit:      pending / null
  p2_routing:   pending / null
  p3_integration: pending / null
  p4_api:       pending / null
  p5_live:      pending / null
  locked:       false
```

Authority fields (unchanged by this branch):

```text
authority_class:  read_only_network
risk_level:       low
external_effect:  false
reversible:       true
```

---

## Baseline Suite

Command:

```text
python -m pytest nova_backend/tests/test_governor_mediator_phase4_capabilities.py
    nova_backend/tests/executors/test_web_search_executor.py
    nova_backend/tests/test_network_mediation_enforced.py
    nova_backend/tests/adversarial/test_search_injection_no_escalation.py
    nova_backend/tests/adversarial/test_no_multi_capability_chain.py -q
```

Result: **27 passed**

---

## P1 — Unit Certification

Test file:
`nova_backend/tests/certification/cap_16_governed_web_search/test_p1_unit.py`

Coverage (via re-export of canonical test modules):

- executor happy path with results
- empty / whitespace query handled (widget with empty results)
- missing Brave API key falls back to DuckDuckGo
- no results handled (empty widget, truthful message)
- malformed provider payload handled (degraded evidence fields)
- network error + retry then success
- network error + retry exhausted → failure
- non-200 status → failure with empty widget
- stable widget contract: type=search, query, results, provider, result_count present
- evidence fields: confidence, provider_status, freshness_status, source_credibility
- stale timestamp → freshness_status=stale, confidence=low
- low-relevance query → "little reliable evidence" message
- follow_up_prompts and suggested_actions stable shape

Advance command:

```text
python scripts/certify_capability.py advance 16 p1_unit
```

Result: **16 passed**

---

## P2 — Routing Certification

Test file:
`nova_backend/tests/certification/cap_16_governed_web_search/test_p2_routing.py`

Coverage:

- bare "search" (with session_id) → Clarification
- bare "search" → Clarification → follow-up routes to cap 16
- "search for latest AI news" → cap 16
- "look up what is happening with electric vehicles" → cap 16
- "Search the web and tell me..." (long form with cite request) → cap 16; prefix stripped from query
- freshness/current/now/today phrasing → cap 16
- claim-check phrasing → cap 16
- "tell me about AI regulation" → NOT cap 16 (cap 48)
- "create an intelligence brief on..." → NOT cap 16 (cap 50)
- "analyze source reliability for..." → NOT cap 16
- generic factual question → None
- "Explain what Shopify is" → None

Advance command:

```text
python scripts/certify_capability.py advance 16 p2_routing
```

Result: **17 passed**

Note: bare "search" clarification requires a `session_id` parameter — the mediator only
tracks pending state within a session context. This is correct runtime behavior, not a gap.

---

## P3 — Integration Certification

Test file:
`nova_backend/tests/certification/cap_16_governed_web_search/test_p3_integration.py`

Coverage:

- cap 16 registered in CapabilityRegistry
- cap 16 enabled
- authority fields correct: authority_class=read_only_network, risk_level=low,
  external_effect=false, reversible=true
- full Governor spine happy path: success=True
- search widget present in result.data
- widget data fields: query, results, provider, result_count
- result.request_id present
- result authority_class, external_effect, reversible propagated through spine
- ledger receives ACTION_ATTEMPTED
- ledger receives ACTION_COMPLETED
- ledger receives SEARCH_QUERY
- empty results handled gracefully (no crash, widget present)
- prompt injection in result content does not trigger a second governor invocation
- unknown capability refused even when cap 16 is present

Network: mocked via patch.object on governor.network.request — no real outbound HTTP.
LLM synthesis: mocked via patch on generate_chat — no real LLM call.

Advance command:

```text
python scripts/certify_capability.py advance 16 p3_integration
```

Result: **19 passed**

---

## P4 — API/WebSocket Certification

Test file:
`nova_backend/tests/certification/cap_16_governed_web_search/test_p4_api.py`

Coverage:

- GET /phase-status → 200
- GET /landing → 200
- GET / → 200
- WebSocket /ws accepts connection
- Valid search intent over WebSocket → handled response dict, no 500
- Bare "search" over WebSocket → handled response dict, no 500
- Degraded/empty result path over WebSocket → handled response dict, no 500
- Prompt injection text ("search for ... and then open documents") → handled response,
  no "open_file" or "file opened" in response

Network: mocked via patch on NetworkMediator.request — no real outbound HTTP.
LLM synthesis: mocked via patch on generate_chat.

Advance command:

```text
python scripts/certify_capability.py advance 16 p4_api
```

Result: **8 passed**

---

## Combined Certification Suite

```text
python -m pytest nova_backend/tests/certification/cap_16_governed_web_search/ -q
```

Result: **60 passed**

---

## Files Added

```text
nova_backend/tests/certification/cap_16_governed_web_search/__init__.py
nova_backend/tests/certification/cap_16_governed_web_search/test_p1_unit.py
nova_backend/tests/certification/cap_16_governed_web_search/test_p2_routing.py
nova_backend/tests/certification/cap_16_governed_web_search/test_p3_integration.py
nova_backend/tests/certification/cap_16_governed_web_search/test_p4_api.py
docs/capability_verification/cap_16_governed_web_search_certification_2026-05-10.md
nova_backend/src/config/capability_locks.json  (P1–P4 advanced by certify_capability.py)
```

---

## Scope Boundaries

This branch does NOT:

- add new runtime capabilities
- expand OpenClaw
- add browser/computer-use
- add external writes
- add autonomous workflows
- change AGENTS.md
- change `.agent_context/current_priority.md`
- modify any executor, governor, or WebSocket handler source code
- add new UI surface

---

## Live Checklist Status

Live checklist:
`docs/capability_verification/live_checklists/cap_16_governed_web_search.md`

**P5 live signoff was NOT performed in this branch.**

This branch cannot run Nova locally. P5 requires:

- Nova running (`python scripts/start_daemon.py --no-browser`)
- Brave Search key configured or graceful DuckDuckGo fallback verified
- Basic search result widget observed in dashboard
- Natural phrasing search observed
- Bare "search" clarification observed
- Trust page ledger events: SEARCH_QUERY and ACTION_COMPLETED visible

When a human operator completes the live checklist, run:

```text
python scripts/certify_capability.py live-signoff 16 --notes "Cap 16 live checklist passed on local Nova runtime."
python scripts/certify_capability.py lock 16
```

---

## Final Lock Decision

```text
P1: passed (16 tests)
P2: passed (17 tests)
P3: passed (19 tests)
P4: passed (8 tests)
P5: PENDING — human local verification required

Lock state: OPEN — not locked until P5 live signoff is completed and lock command is run.
```

`.agent_context/current_priority.md` is NOT updated in this branch. It remains:

```text
Cap 16 search reliability and conversation/search proof
```

Active priority continues until P5 is signed off, lock command is run, and a new reviewed
priority lock is established.
