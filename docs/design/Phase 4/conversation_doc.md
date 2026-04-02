Below is a **single, detailed design document** for **Option C: Hybrid auto-detection + manual override**, plus an explicit **file-by-file modification plan** tailored to your current Nova shape (Phase-4 runtime, Governor spine, `brain_server.py`, `governor_mediator.py`, capability 16/17/18, conversation subsystem, proofs/CI already hardened).

---

# NOVA — CONVERSATION MODE ROUTER v1.0

**Hybrid Auto-Detect + Manual Override (Option C)**
**Status:** Design-Unlocked / Implementation-Ready
**Scope:** Conversation quality only (no authority expansion)
**Non-Goals:** autonomy, background cognition, learning, persistent persona, silent action inference

## 0. Executive Summary

Nova will gain *more conversational skill* by adding a **Conversation Mode Router** that classifies each user message into a small set of **conversation modes** and applies a mode-specific response style.

**Option C** means:

1. **Auto-detect** the best mode per message using deterministic rules (no learning).
2. Allow **manual override** commands like:

* “brainstorm mode”
* “work mode”
* “casual mode”
* “analysis mode”
* “reset mode”

3. Manual override persists only in **session memory** (ephemeral), not long-term memory.

Actions remain governed exactly as before:

* If the message is a governed invocation, Governor handles it.
* If it *might* be an action but ambiguous, Nova asks **one** clarification before acting.
* Conversation can never execute tools or actions.

Outcome:

* “How are you doing?” feels human and simple.
* “Let’s brainstorm features” becomes expansive.
* “Break down this bug” becomes structured.
* “Open Pandora” stays an action (with confirmation when ambiguous).

---

## 1. Key User Experience Behaviors

### 1.1 Social / Casual (“How are you?”)

Nova should respond in a **friendly-professional** tone without emotional simulation.

Example:
User: “How are you doing?”
Nova: “Running normally. What do you want to work on?”

Rules:

* No “I’m an AI…” disclaimers
* No “I don’t have feelings” lectures
* Keep it short unless user asks more

### 1.2 Work Style / Technical Collaboration

Example:
User: “Help me debug this condensation layer.”
Nova: “Okay. What’s the current behavior you want, and what’s the failure case?”

Rules:

* Ask for missing context if required
* Provide structured breakdowns

### 1.3 Brainstorming

Example:
User: “Throw ideas at me for better conversation.”
Nova: “Here are 10 directions… (grouped).”

Rules:

* Encourage breadth, multiple options
* Still not persuasive or manipulative
* No action execution implied

### 1.4 Analytical / Deep Reasoning

Example:
User: “Give me an in-depth comparison of X vs Y.”
Nova: Produces multi-section structured analysis.
If deep analysis service is unavailable, Nova **falls back** to a local structured answer, instead of repeating “unavailable.”

### 1.5 Action Mode (Open/Search/Speak)

Example:
User: “Open Pandora”
Nova: Executes cap 17 if exact match/preset mapping; otherwise clarifies once.

Key rule:

* If ambiguous: clarify before action.
* If clear: execute.

---

## 2. Conversation Modes (Small Fixed Set)

Use a bounded enum:

* `SOCIAL` — greetings, “how are you”, identity, light chat
* `CASUAL_QA` — random questions, light curiosity
* `WORK` — “let’s do”, “break down”, “debug”, “plan the steps”
* `BRAINSTORM` — “ideas”, “possibilities”, “what could we do”
* `ANALYSIS` — deeper reasoning, comparisons, long-form explanation
* `ACTION` — explicit governed invocation intent
* `UNKNOWN` — cannot classify safely → clarify or simple fallback

This is intentionally small. Bigger mode sets become unstable and “agent-like.”

---

## 3. High-Level Routing Order (Critical)

This order prevents authority drift:

### Step 1 — Governor Invocation Check (Already Exists)

* Parse governed invocation (`search`, `open`, etc.)
* If detected → send to Governor → return.

### Step 2 — Manual Mode Override Commands

If user explicitly sets a mode:

* “brainstorm mode”
* “work mode”
* “analysis mode”
* “casual mode”
* “social mode”
* “reset mode”
  Then:
* set `session_mode_override = MODE` (ephemeral)
* respond with a short confirmation
* do not execute any actions

### Step 3 — Auto Mode Detection

If no override command was issued on this turn:

* compute deterministic classification based on phrases/keywords + simple features
* result is `auto_mode`

### Step 4 — Resolve Mode (Override > Auto)

* If override is set: `mode = override`
* Else: `mode = auto_mode`

### Step 5 — Mode-Specific Response Policy

* SOCIAL: short friendly line + prompt
* WORK: structured questions + plan
* BRAINSTORM: grouped options
* ANALYSIS: long structured answer
* CASUAL_QA: normal short answer
* UNKNOWN: one clarification question

### Step 6 — Ambiguity Guard (Action-Like but Unclear)

If message contains an action verb (open/search/speak) but is not a valid invocation:

* ask one clarifying question
* do not guess-execute

---

## 4. Deterministic Mode Classifier (No Learning)

### 4.1 Inputs

* raw text
* channel: `voice` or `text`
* minimal session context: last mode, last intent, last executed capability (ephemeral only)

### 4.2 Features (Simple & Deterministic)

* keyword presence (exact token match)
* question mark / interrogatives (“what”, “why”, “how”)
* action verbs (“open”, “search”, “look up”, “speak”)
* “brainstorm” cues (“ideas”, “possibilities”, “options”)
* “work” cues (“debug”, “fix”, “build”, “implement”, “step by step”)
* “analysis” cues (“compare”, “deep dive”, “in-depth”, “pros and cons”)
* “social” cues (“hello”, “how are you”, “good morning”)
* speech fragment cues (very short, low content words, ASR artifacts)

### 4.3 Output

* mode enum
* confidence bucket: `HIGH | MED | LOW` (still deterministic)
* if LOW: prefer clarification unless it’s a safe SOCIAL reply

### 4.4 “Never Escalate” List

Do not route to “analysis escalation service” for:

* “what can you do”
* “who are you”
* greetings
* simple clarifications
* action confirmations

These should always be local.

---

## 5. Manual Override Protocol (Option C)

### 5.1 Commands (Fixed Phrase Bank)

* “brainstorm mode”
* “work mode”
* “analysis mode”
* “casual mode”
* “social mode”
* “default mode”
* “reset mode”
* “stop mode”

### 5.2 Behavior

* Setting a mode persists for the session until changed/reset.
* It affects *how* Nova responds, not *what it is allowed to do*.
* Override never enables actions; Governor still governs.

### 5.3 Response Examples

User: “brainstorm mode”
Nova: “Okay. Brainstorming mode.”

User: “reset mode”
Nova: “Okay. Back to default.”

---

## 6. Ambiguity & Clarification (One-Strike Rule)

When the user intent is unclear, Nova must ask **one** clarification question, then stop.

Examples:

* “open” → “What should I open?”
* “pandora” → “Do you mean open Pandora in the browser?”
* “search breaking news” (if no results) → “Do you want me to search the web for breaking news, or show cached headlines?”

Key: **No second question.** If still unclear after one reply:

* fall back to safest interpretation OR refuse.

---

## 7. Escalation / “Deep Analysis Service” Failures

Problem you saw:

* “Deep analysis unavailable” triggered too often.

Fix:

* Escalation only on `ANALYSIS` mode with high confidence, OR explicit phrase: “deep analysis”, “deep dive”, “in-depth”.

If escalation fails:

* fall back to local structured answer (still helpful)
* do not repeat “unavailable” loops

---

## 8. Tests Required (Proof-Grade)

Add tests to prevent regressions:

### 8.1 Mode Classifier Tests

* “how are you” → SOCIAL
* “give me ideas for…” → BRAINSTORM
* “break this into steps” → WORK
* “compare x vs y” → ANALYSIS
* “open facebook” → ACTION (governed invocation)

### 8.2 Ambiguity Tests

* “open” → clarification; no action
* “pandora” → clarification; no hallucination
* “i can pandora” (voice fragment) → clarification; no escalation

### 8.3 Never Escalate Tests

* “what can you do” → local help response; no escalation call

### 8.4 Safety/Authority Tests

* injection text embedded → no action
* escalation cannot call executors

---

# 9. File-by-File Implementation Plan

Below is the concrete set of file changes. I’m listing them in a way that matches your current repo conventions (Nova Phase-4 runtime).

## 9.1 Create / Modify Conversation Subsystem Files

### A) **NEW** `nova_backend/src/conversation/modes.py`

* Define `ConversationMode` enum
* Define `ModeOverrideCommand` parsing

### B) **NEW** `nova_backend/src/conversation/mode_classifier.py`

* Deterministic classifier function:

  * `classify(text: str, channel: str, context: SessionContext) -> ModeResult`

### C) **NEW** `nova_backend/src/conversation/mode_router.py`

* Routing logic implementing the ordering rules
* Output: `ConversationDecision`

  * mode
  * response_style
  * needs_clarification (bool)
  * clarification_question (optional)

### D) **MODIFY** `nova_backend/src/conversation/escalation_policy.py` (or equivalent)

* Add “never escalate” intents list
* Gate escalation only to ANALYSIS mode (high confidence or explicit request)
* Add fallback: if escalation fails, return local structured answer

### E) **MODIFY** `nova_backend/src/conversation/response_formatter.py` (or equivalent)

* Add mode-specific templates:

  * SOCIAL tone
  * WORK structured prompts
  * BRAINSTORM grouped output formatting
  * ANALYSIS section headers
* Remove robotic disclaimers in default replies

### F) **MODIFY** `nova_backend/src/conversation/session_state.py` (or similar; if you don’t have it, add)

* Add ephemeral:

  * `mode_override: Optional[ConversationMode]`
  * `last_mode: ConversationMode`
  * `last_intent: Optional[str]`
* Persist only in memory (current process session), not disk

> If you don’t currently have a `conversation/` directory, implement these under whatever directory holds your escalation/formatter logic today.

---

## 9.2 Modify Routing Entry Point

### G) **MODIFY** `nova_backend/src/brain_server.py`

Where you currently:

* mediate text
* detect governed invocation
* fallback to conversation

Update flow to:

1. `GovernorMediator.mediate()`
2. `GovernorMediator.parse_governed_invocation()`

   * if invocation: execute action path (unchanged)
3. Else: pass to **ModeRouter** to generate response:

   * apply manual override if command
   * otherwise auto classify
   * if needs clarification: send question
   * else: format response based on mode

Also ensure channel metadata continues to be passed through (you already fixed this).

---

## 9.3 Modify Mediator for Mode Commands (Optional)

### H) **OPTIONAL** `nova_backend/src/governor/governor_mediator.py`

You can keep mode commands out of mediator entirely (cleaner), but if you want:

* Add a lightweight detector for “mode commands” to route to conversation mode layer.
* Do **not** mix mode logic into governed invocation parsing.

I recommend: keep this in `conversation/mode_router.py`, not mediator.

---

## 9.4 Add Tests

### I) **NEW** `nova_backend/tests/conversation/test_mode_classifier.py`

* tests mapping phrases → expected modes

### J) **NEW** `nova_backend/tests/conversation/test_mode_override.py`

* tests “brainstorm mode” sets override, persists, reset clears

### K) **NEW** `nova_backend/tests/conversation/test_ambiguity_clarification.py`

* “open” → asks “What should I open?”
* “pandora” → asks confirmation

### L) **MODIFY** existing `nova_backend/tests/adversarial/test_conversation_non_authorizing.py`

* add cases that ensure mode router never triggers Governor execution
* ensure injection still inert

---

## 9.5 Update Proof Docs After Implementation

After you implement, update/add:

* `docs/PROOFS/Phase-4/CONVERSATION_NON_AUTHORIZING_PROOF.md`

  * prove no new authority expansion
  * show grep results: no executor imports in conversation layer
  * show tests passing

---

# 10. Acceptance Criteria (What “Done” Means)

## Functional

* “How are you” returns short friendly response every time
* Brainstorm requests produce grouped options
* Work requests produce structured steps/questions
* Random questions get normal answers without escalation spam
* “deep analysis unavailable” appears only when explicitly requested and still falls back locally

## Safety / Governance

* No automatic actions from fuzzy intent
* Ambiguous action phrases always clarify once before executing
* Conversation layer has no executor imports
* All tests pass (existing 43 + new tests)

---

# 11. Minimal “Mode Phrase Bank” (Start Small)

Start with this small fixed list:

### SOCIAL

* hello, hi, hey, good morning, good evening, how are you, what’s up

### WORK

* break down, step by step, debug, fix, implement, refactor, plan, design

### BRAINSTORM

* brainstorm, ideas, options, possibilities, what could we do, directions

### ANALYSIS

* deep dive, in-depth, compare, pros and cons, tradeoffs, analyze

### MODE OVERRIDE

* “brainstorm mode”, “work mode”, “analysis mode”, “casual mode”, “reset mode”

---

# 12. Why This Solves Your Actual Pain

This directly fixes what you saw in the transcript:

* “coming what you can do” → routes to SOCIAL/CASUAL_QA with a clean help response
* “i can pandora” → routes to clarification: “Do you mean open Pandora?”
* “opens door” → routes to ambiguity clarification, not hallucination
* “deep analysis unavailable” → only appears on real deep requests; otherwise stays local
* Tone becomes human-readable without becoming a “personality”

---
