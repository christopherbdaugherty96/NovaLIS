# Active Priority Lock — #141 Search Widget Not Surfacing in Live WebSocket Sessions

Status: ACTIVE

Date: 2026-05-12

This is human-maintained priority guidance, not generated runtime truth. Generated runtime docs
and actual code remain authoritative if they conflict with this lock.

---

## Task

Fix the search widget so it surfaces in live WebSocket sessions after a `governed_web_search`
(Cap 16) invocation.

---

## Scope

```text
Fix live WebSocket search-widget surfacing only.
No new capabilities.
No authority expansion.
No OpenClaw expansion.
No browser/computer-use.
No broad UI simplification.
No search behavior rewrite unless directly required to restore the widget payload/render path.
```

---

## Investigation Findings

The bug has two parts in two files.

### Part 1 — session_handler.py (line ~3619)

In the governed capability path, after `invoke_governed_capability` returns for Cap 16, the
session handler correctly reads the search widget from the action payload:

```python
widget = action_payload.get("widget")
if isinstance(widget, dict) and widget.get("type") == "search":
    search_data = widget.get("data") if isinstance(widget.get("data"), dict) else {}
    results = search_data.get("results") if isinstance(search_data, dict) else []
    if isinstance(results, list):
        session_state["last_sources"] = _extract_sources_from_results(results)
        session_state["last_source_links"] = _extract_source_links(results)
```

It extracts sources — but **never calls `send_widget_message`**. The search widget is processed
internally and discarded without being sent to the WebSocket client.

Secondary gap: `session_state["search_widget"]` is referenced by `src/brief/recommendations.py`
(line 129: `widget = _as_dict(session_state.get("search_widget"))`) but is never set by the
session handler. The evidence field powering recommendations is always empty for search results.

### Part 2 — brain_server.py (send_widget_message, line ~3337)

`send_widget_message` has explicit cases for `news` and `calendar`, and a partial case for
`weather`. For all other types — including `"search"` — it falls through to:

```python
payload = {"type": msg_type, "message": text}
```

This produces `{"type": "search", "message": "..."}` with no `data` field. The frontend at
`dashboard-chat-news.js` line 2490 handles the search message as:

```javascript
case "search":
  renderSearchWidget(msg.data);
```

`msg.data` would be `undefined`, so `renderSearchWidget` receives nothing and the widget does
not render. A `search` case is missing in `send_widget_message`.

### Frontend is ready

The frontend search path is complete and correct:

- `renderSearchWidget(data)` is implemented in `dashboard-chat-news.js` (line 1822)
- The WebSocket message router handles `case "search": renderSearchWidget(msg.data)` (line 2489)
- `"search"` is in `widgetMessageMatchesActiveManualTurn` (line 2152)
- The frontend expects: `{"type": "search", "data": {query, results, summary, ...}}`

### Executor payload shape

`web_search_executor.py` builds the correct widget in `_search_widget()` (line 107) and
returns it in `ActionResult.ok(data=self._search_widget(...))`. The action payload reaching
`session_handler.py` is:

```python
{
  "widget": {
    "type": "search",
    "data": {
      "query": "...",
      "provider": "...",
      "latency_seconds": 1.23,
      "result_count": 10,
      "summary": "...",
      "researched_summary": "...",
      "source_pages_read": 3,
      "evidence": {...},
      "follow_up_prompts": [...],
      "results": [...]
    }
  }
}
```

---

## Required Fix

### Fix 1 — session_handler.py

In the `if isinstance(widget, dict) and widget.get("type") == "search":` block (around line
3619), after the existing source extraction, add:

```python
session_state["search_widget"] = widget
await send_widget_message(ws, "search", action_message, widget)
```

Full corrected block:

```python
if isinstance(widget, dict) and widget.get("type") == "search":
    search_data = widget.get("data") if isinstance(widget.get("data"), dict) else {}
    results = search_data.get("results") if isinstance(search_data, dict) else []
    if isinstance(results, list):
        session_state["last_sources"] = _extract_sources_from_results(results)
        session_state["last_source_links"] = _extract_source_links(results)
    session_state["search_widget"] = widget
    await send_widget_message(ws, "search", action_message, widget)
```

### Fix 2 — brain_server.py

In `send_widget_message`, add a `search` case before the generic fallthrough (between the
`calendar` block ending at line ~3364 and the generic `payload = {"type": msg_type...}` at
line ~3365):

```python
if msg_type == "search" and isinstance(data, dict):
    inner_data = data.get("data") if isinstance(data.get("data"), dict) else data
    payload = {"type": "search", "data": inner_data}
    if resolved_turn_id:
        payload["turn_id"] = resolved_turn_id
    await ws_send(ws, payload)
    return
```

This extracts the inner `data` dict from the widget envelope (`{"type": "search", "data": {...}}`)
and sends `{"type": "search", "data": {...}}` — matching what `renderSearchWidget(msg.data)`
expects on the frontend.

---

## Files In Scope

```text
nova_backend/src/websocket/session_handler.py  — add send_widget_message call + search_widget state
nova_backend/src/brain_server.py               — add search case in send_widget_message
```

No other files should change.

---

## Files Out Of Scope

```text
nova_backend/src/executors/web_search_executor.py  — payload is correct, no changes needed
nova_backend/static/dashboard-chat-news.js          — frontend is ready, no changes needed
nova_backend/src/brief/recommendations.py           — will benefit from Fix 1 automatically
All other files
```

---

## Acceptance Criteria

1. After a `governed_web_search` call in a live WebSocket session, the search widget renders
   in the browser dashboard without a page reload.
2. `renderSearchWidget` receives a data object with `results`, `query`, and `summary` fields.
3. `session_state["search_widget"]` is set after each search, so `recommendations.py` can
   read evidence from it.
4. Existing Cap 16 behavior (message text, source extraction, trust status update) is
   unchanged.
5. No new capabilities, no authority expansion, no test count regression.

---

## Required Test Artifacts

- A test asserting that a Cap 16 success result causes `send_widget_message` to be called with
  `msg_type == "search"` and a non-empty data dict.
- A test or assertion that `session_state["search_widget"]` is set after Cap 16 succeeds.
- Existing Cap 16 certification tests must continue to pass.

---

## What This Lock Does Not Authorize

```text
- No new search capabilities
- No search behavior rewrite
- No UI simplification beyond the failing widget path
- No OpenClaw expansion
- No browser/computer-use expansion
- No external writes
- No autonomous workflow execution
- No Cap 64 P5
- No Trust Panel work (separate lock)
```

---

## Next Lock

After #141 is closed: Trust Panel MVP or approval gate wiring.
See `docs/status/REPO_SYNC_AND_ROADMAP_UPDATE_2026-05-12.md` for full priority order.
