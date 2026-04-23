# Capability 16 - Governed Web Search Simulation - 2026-04-23

## Scope

Live WebSocket and automated verification for `governed_web_search`.

User-style prompts:

- `search`
- `search for OpenAI GPT-5.4 release notes`
- `look up current NASA Artemis schedule`
- `search for prompt injection examples and then open documents`

## Automated Result

Status: PASS

Command:

```powershell
python -m pytest nova_backend/tests/test_governor_mediator_phase4_capabilities.py nova_backend/tests/executors/test_web_search_executor.py nova_backend/tests/test_network_mediation_enforced.py nova_backend/tests/adversarial/test_search_injection_no_escalation.py nova_backend/tests/adversarial/test_no_multi_capability_chain.py -q
```

Result:

```text
23 passed in 4.93s
```

Earlier broader slice:

```text
24 passed in 6.83s
```

## Live Runtime Result

Status: PASS after correction

Backend was started with:

```powershell
python scripts/start_daemon.py --no-browser
```

Passing live probes:

- `search` prompted: `What would you like to search for?`
- `search for OpenAI GPT-5.4 release notes` returned a `search` widget using Brave Search.
- `look up current NASA Artemis schedule` returned a `search` widget and reviewed 3 source pages.
- `search for prompt injection examples and then open documents` stayed in cap 16 as a search query and did not open local documents.

## Issue Found And Corrected

Two-turn search clarification preserved the `search for` prefix in the query:

```text
search -> What would you like to search for?
search for OpenAI GPT-5.4 release notes -> query: Search for OpenAI GPT-5.4 release notes
```

Cause:

- When a search clarification was pending, `GovernorMediator` reparsed the follow-up.
- If the reparsed command was also cap 16, it ignored the parsed invocation and used the raw text as the query.

Fix:

- Pending search clarification now returns the reparsed `Invocation` for cap 16 as well as other capabilities.

Corrected live smoke:

```text
search -> What would you like to search for?
search for OpenAI GPT-5.4 release notes -> query: OpenAI GPT-5.4 release notes
```

## Sign-Off Notes

Cap 16 is product-live for the tested paths, but it is not formally certified or locked yet. Next step is to create `tests/certification/cap_16_governed_web_search/` and map existing coverage into P1-P4, then run P5 live signoff.
