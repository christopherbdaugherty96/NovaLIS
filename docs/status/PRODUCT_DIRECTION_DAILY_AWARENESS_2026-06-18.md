# Nova Product Direction: Governed Daily Awareness Assistant

**Date:** 2026-06-18
**Status:** Active — Phase 1 in progress

---

## Core Identity

Nova is a **governed daily awareness assistant**. Intelligence proposes,
Nova governs, you decide. The larger goal is a broad Jarvis-style
assistant with a real governed backend, but the immediate product must
be useful within the first 30 seconds of opening.

## What Nova Is Not (Yet)

- Not autonomous — no writes to Shopify, Printify, or social platforms
- Not a browser/computer-use expansion tool
- Not a broad agent execution platform
- No random capabilities — every feature must be governed and honest

## Guiding Principles

1. **Mirror the user's day, not the backend modules**
2. **Opening Nova should be useful within 30 seconds**
3. **Never promise what Nova cannot deliver**
4. **Graceful degradation over silent failure**
5. **Read-only awareness first, governed action second**

---

## Daily Awareness Loop — The Product Surface

The default open screen renders a Daily Awareness Brief without
requiring any command. Seven sections, each independently optional:

| Section | Source | Status |
|---------|--------|--------|
| Weather (with practical impact) | Governed weather capability | Live |
| News by subject (grouped, why-it-matters) | Brave Search via governor | Live |
| Calendar (today's events) | Local .ics via governor | Live |
| Current project state (blocker, last step, next move) | Session state | Live |
| Shopify snapshot (read-only metrics) | Shopify connector | Live if configured |
| Printify snapshot | Not built | Stub — honest about absence |
| What changed since last session | Ledger receipts | Live |

Each section reports its own status: `ok`, `not_configured`,
`not_available`, or `empty`. The brief renders all sections with
unavailable ones dimmed rather than hidden.

---

## Implementation Status

### Phase 1: Daily Awareness Loop (Current)

**Completed 2026-06-18:**

1. **Fixed chat_stream frontend handling (P0)**
   - Added `case "chat_stream"` to WebSocket message handler
   - Built streaming chat bubble with `appendStreamChunk()` /
     `finalizeStreamBubble()` functions
   - Added pulsing dot CSS indicator during streaming
   - Stream bubbles keyed by `turn_id` for concurrency safety
   - `chat_done` finalizes open stream bubbles automatically
   - Files: `dashboard-chat-news.js`, `dashboard-surfaces.css`

2. **Fixed silent reminder failures**
   - Reminder response now honestly discloses that background delivery
     does not exist yet
   - Changed "Reminder scheduled" → "Reminder saved" with honesty note
   - File: `session_handler.py` (line ~2855)

3. **Hidden unconfigured Second Opinion button**
   - Button hidden by default (`style="display:none"`)
   - Only shown when OpenAI connection is confirmed healthy
   - `updateSecondOpinionVisibility()` called on every connection
     data refresh
   - Files: `index.html`, `dashboard-chat-news.js`

4. **Built Daily Awareness Brief backend**
   - New module: `nova_backend/src/brief/awareness_brief.py`
   - `compose_awareness_brief()` assembles all 7 sections
   - Each section builder handles missing data gracefully
   - Non-authorizing, read-only, no LLM calls
   - WebSocket event type: `awareness_brief`
   - Intent triggers: "awareness brief", "daily awareness", "awareness"
   - Fires automatically on startup hydration (250ms after connect)
   - File: `session_handler.py` (awareness brief handler block)

5. **Built Daily Awareness Brief frontend**
   - `renderAwarenessBrief()` renders structured card in chat log
   - Sections with status != "ok" are dimmed
   - Status icons: ✓ (ok), — (not configured), • (unavailable/empty)
   - Metadata line shows available/total section count
   - CSS in `dashboard-surfaces.css`

### Phase 2: Speed and Trust (Next)

- Startup hydration race optimization
- Trust panel integration with awareness brief
- Connection health badges on brief sections
- Brief caching to avoid re-fetching on tab refocus

### Phase 3: Awareness Dashboard (Future)

- Dedicated Today page replacing the current Home page
- Sections become expandable cards
- Deep-dive links on news items
- Historical brief comparison

### Phase 4: Simplify Navigation (Future)

- Reduce 11 pages to essential surfaces
- Outcome-first language in all UI copy
- Remove internal nouns from user-facing text

---

## Boundary — Preserve Verbatim

> Do not make Nova more autonomous yet. Make it more aware, honest,
> and useful. No Shopify writes yet. No Printify writes yet. No social
> posting yet. No browser/computer-use expansion yet. No broad agent
> execution yet. No more random capabilities.

This boundary is active until explicitly revised by the user.
