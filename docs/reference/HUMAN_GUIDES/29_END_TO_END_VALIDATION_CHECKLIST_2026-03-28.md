# End-To-End Validation Checklist
Updated: 2026-03-28
Status: Current operator checklist

## Purpose
This is the practical checklist for deciding whether Nova feels complete end to end.

It is not a phase lock and not a design packet.
It is the day-to-day validation guide for the most important user journeys.

Use it when:
- shipping a new runtime slice
- reviewing whether a phase feels complete in practice
- checking that docs, UI, and runtime behavior still match

## Grounding Rule
Validate Nova in the order a real user experiences it:
1. startup
2. connection and readiness
3. chat
4. memory and continuity
5. voice
6. second-opinion review
7. Trust review
8. Agent and scheduled delivery

If those paths feel clean, Nova is healthy.
If those paths feel confusing, Nova still needs finish work even if the architecture is strong.

## 1. Startup And First Connection
Checklist:
- Nova starts from the documented startup scripts.
- The dashboard loads without a blank or broken shell.
- The user can tell whether Nova is still connecting, ready, or blocked.
- The Intro page explains what is required now, recommended next, and optional later.
- Recovery help for a stuck startup is visible in product.

Pass condition:
- a new user can open Nova and understand what to do next without reading code

## 2. Setup Readiness And Connections
Checklist:
- Settings shows local-first setup mode clearly.
- Connections and provider status surfaces show what is actually configured.
- Weather, calendar, remote bridge, scheduler, and OpenAI lane each show truthful readiness.
- Optional services are described as optional, not as broken required setup.
- Agent setup surfaces match what the runtime really supports.

Pass condition:
- the user can tell what is ready now, what is paused, and what still needs manual setup

## 3. Core Chat Path
Checklist:
- normal questions route and answer cleanly
- answer-first search leads with the answer, not scaffolding
- long-form reasoning outputs lead with a useful takeaway
- fallback language stays calm and truthful when something is unavailable
- no stale references to removed legacy paths appear in chat

Pass condition:
- the user gets a useful answer first and supporting detail second

## 4. Memory And Continuity
Checklist:
- `remember this` saves explicit memory
- `what do you remember` returns the current memory state
- memory export works from both command and Memory page
- `forget this` stays confirmation-backed
- operational context is visible and resettable
- assistive notices stay suggestion-only, visible, and handleable

Pass condition:
- Nova feels continuous without becoming creepy or silently autonomous

## 5. Voice Path
Checklist:
- STT readiness is visible
- TTS readiness is visible
- voice-origin turns auto-speak when expected
- long structured replies are summarized for speech instead of read verbatim
- failure states remain visible when speech cannot render

Pass condition:
- voice feels like a reliable presentation layer, not a second-class add-on

## 6. Second-Opinion And Final-Answer Path
Checklist:
- Nova can answer normally
- `second opinion` produces a governed review
- review output surfaces a bottom line, main gap, and best correction
- `final answer` works from the same-session review state
- `second opinion and final answer` runs the one-step triad flow
- DeepSeek or the bounded reasoning lane never gains execution authority

Pass condition:
- the user can move from answer to review to final answer inside one clean conversation flow

## 7. Trust Review
Checklist:
- Trust shows what Nova did
- Trust shows what stayed blocked
- Trust shows what left the device
- reasoning usage visibility stays truthful
- operational context and assistive history are reviewable
- policy surfaces stay inspectable and manual

Pass condition:
- the user can understand Nova's behavior without reading logs directly

## 8. Agent And OpenClaw Path
Checklist:
- Agent page explains OpenClaw as Nova's worker layer
- manual template runs succeed or fail clearly
- strict preflight is active before a manual run
- delivery inbox receives widget or hybrid results
- recent runs are visible
- schedule enable and pause controls persist
- quiet-hours suppression is visible when policy blocks a due run
- rate-limit suppression is visible when policy blocks repeated runs
- a held scheduled slot runs once policy clears

Pass condition:
- the home-agent surface feels bounded, visible, and operator-safe

## 9. Scheduler Policy Path
Checklist:
- notification policy and scheduler policy use the same quiet-hours and hourly-cap truth
- scheduled runs do not silently disappear when policy blocks them
- suppression reasons are ledgered
- paused global scheduler permission blocks scheduled work cleanly
- scheduled delivery remains a narrow carve-out, not a hidden autonomy path

Pass condition:
- proactive behavior stays controlled by visible policy, not silent background logic

## 10. Platform Correctness
Checklist:
- platform-specific control paths are truthful
- unsupported Windows explicit media commands fail closed rather than acting like toggles
- Linux and macOS local-control paths still behave as documented
- speech runtime readiness matches the real machine state

Pass condition:
- Nova does not claim precise system control where the platform only offers a generic toggle

## 11. Runtime Truth And Docs
Checklist:
- current runtime docs regenerate without drift
- phase maps match live runtime boundaries
- proof packet indexes include the latest shipped slices
- human guides describe current behavior in plain language
- removed legacy surfaces do not keep appearing in runtime docs

Pass condition:
- a maintainer reading the docs gets the same system the user actually runs

## 12. Suggested Focus Order For Ongoing Validation
1. startup and setup readiness
2. chat and second-opinion flow
3. memory and continuity
4. voice on real hardware
5. Trust review
6. Agent manual run
7. Agent scheduled run with suppression and recovery

## Best Honest Use Of This Checklist
Use this document to decide whether the next task should be:
- bug fixing
- finish work
- UX cleanup
- doc correction
- phase widening

If one of the journeys above still feels rough, finish that journey before adding broader autonomy.
