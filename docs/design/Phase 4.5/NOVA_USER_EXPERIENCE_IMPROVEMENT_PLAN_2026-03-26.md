# Nova User Experience Improvement Plan
## Repo-Grounded Product Pass

**Date:** March 26, 2026  
**Status:** Approved for implementation  
**Scope:** Frontend usability improvements grounded in the current runtime, not stale historical gaps

---

## 1. Why This Pass Exists

Nova has crossed the line from "engineered system" into "real product," but the current frontend still asks new users to infer too much on their own.

The runtime is now substantially stronger than the older audits implied:

- onboarding exists
- Settings exists and is live
- Trust, Workspace, Memory, Policy, and Intro pages all exist
- the frontend is responsive at several breakpoints
- Enter-to-send already works
- chat auto-scroll already works
- frontend mirror drift is already checked and enforced

That means the next UX pass should not pretend Nova lacks a product surface. It should improve the **clarity, orientation, confidence, and smoothness** of the product that already exists.

This document records the truthful current state and the changes that most improve Nova for a non-technical user.

---

## 2. Current Truth

### 2.1 Already Present

These capabilities already exist in the live frontend/runtime and should not be re-described as missing:

- Intro page (`page-intro`)
- first-run modal (`showFirstRunGuide()`)
- Settings page with live runtime controls
- Help surface / command discovery
- Workspace page and Workspace Home surfaces
- Trust Center
- Policy Review Center
- Memory Center management surface
- landing preview page (`/landing`)
- Enter-to-send in the chat input
- chat auto-scroll to newest appended messages
- responsive CSS breakpoints

### 2.2 What Still Feels Weak to a User

The main remaining UX problems are not missing architecture. They are missing **orientation** and **confidence signals**.

Specifically:

1. navigation is still menu-heavy instead of immediately visible
2. first-run users still land on Chat instead of the stronger Intro surface
3. the thinking bar technically exists but does not read like a clear product feedback signal
4. voice/PTT state exists in CSS but is not surfaced clearly in runtime interaction
5. page identity and connection state are not obvious at the top of the app
6. some snapshot/loading states can stay too vague for too long
7. destructive memory actions still rely on chat/governed confirmation without a clear inline pre-confirm step
8. the DeepSeek button label is still tool-centric instead of user-centric
9. calendar unavailability still reads like passive absence rather than a useful next step

---

## 3. Product Goals

This pass should make Nova feel:

- easier to navigate
- easier to trust
- easier to understand in the first 30 seconds
- more alive while it is processing
- calmer and more self-explanatory without becoming noisy

The goal is not to add hidden automation.  
The goal is to make Nova’s existing governed product feel polished.

---

## 4. UX Changes To Implement

### 4.1 Persistent Primary Navigation

**Problem**  
The current header uses generated menus, which are functional but not ideal for orientation. A new user does not immediately see the full product map.

**Change**
Add a persistent primary navigation strip with visible buttons for:

- Chat
- Home
- News
- Workspace
- Memory
- Policies
- Trust
- Settings
- Intro

**Rules**
- always visible in the header area
- clearly marks the active page
- does not remove the existing header menus; those remain as secondary utilities
- should stay responsive and wrap on smaller screens

**Outcome**
Users can understand Nova’s product structure instantly.

---

### 4.2 Stronger Header Identity and Status

**Problem**  
The header currently says "Nova" but does not clearly show where the user is or whether the app is connected and ready.

**Change**
Add a compact header status cluster that shows:

- current page label
- websocket/runtime connection state
- simple status wording such as:
  - Connected
  - Reconnecting
  - Local-only
  - Degraded

**Rules**
- should be calm, not alarming
- should update from the actual runtime state where possible
- should still degrade gracefully when trust/runtime data is not loaded yet

**Outcome**
Users always know where they are and whether Nova is healthy.

---

### 4.3 Intro-First First Run

**Problem**  
Nova already has a strong Intro page and first-run modal, but new users still default to Chat on first load.

**Change**
On first run, default the active page to `intro` instead of `chat`.

**Rules**
- only when `nova_first_run_done` is not set
- preserve the current stored-page behavior for returning users
- keep the first-run modal; this change complements it rather than replacing it

**Outcome**
The strongest product explanation becomes the first thing a new user sees.

---

### 4.4 Stronger Thinking Feedback

**Problem**  
The current thinking bar is a thin animated line with generic text. It technically works, but it does not feel like clear feedback.

**Change**
Turn the thinking bar into a visible status pill/banner that:

- shows explicit text
- reads like active progress
- stays lightweight

Example copy:

- Nova is thinking...
- Checking online sources...
- Reading the page...
- Preparing your brief...

**Rules**
- keep it compact
- preserve reduced-motion support
- no fake progress percentages

**Outcome**
Nova feels responsive rather than silent.

---

### 4.5 Chat Input Clarity

**Problem**  
Enter already sends, but the input and send controls do not explain themselves enough.

**Change**
Improve the chat bar with:

- input title/hint that Enter sends
- Send button title/hint
- better visible label for the second-opinion button

**Rules**
- keep the layout simple
- use user-centric wording
- avoid exposing provider jargon as the primary label

**Outcome**
The chat bar feels easier and less tool-like.

---

### 4.6 Voice/PTT Feedback

**Problem**  
Voice input exists, and CSS already includes mic state classes, but the runtime does not clearly toggle them for the user.

**Change**
Add explicit mic state transitions in the UI:

- idle
- recording
- sending
- error

Also improve button wording/tooltip copy.

**Rules**
- should track the actual PTT lifecycle
- should not imply continuous listening
- should remain compatible with the existing orb status model

**Outcome**
Users know when Nova is listening and when it stopped.

---

### 4.7 Morning Snapshot Fallbacks

**Problem**  
The snapshot rows begin at "Loading..." and can feel indefinite when a source is unavailable.

**Change**
Add a timed fallback that replaces stuck loading states with plain-language status:

- Weather unavailable
- News unavailable
- System status unavailable
- Calendar not connected yet

For calendar, add a useful next-step surface such as:

- Connect calendar in Settings

**Rules**
- fallback should appear only after a reasonable timeout
- live results should still replace the fallback when data eventually arrives

**Outcome**
Users get clarity instead of dead-end loading text.

---

### 4.8 Safer Inline Memory Action Confirmation

**Problem**  
The current Memory page says destructive actions remain governed, but the first visible click on Delete/Unlock/Defer is still abrupt.

**Change**
Add an inline confirmation strip in the Memory detail area before the governed command is sent.

**Applies to**
- delete
- unlock
- defer
- optionally lock if needed for consistency

**Rules**
- the inline confirmation is a UI safeguard
- the governed backend confirmation flow still remains authoritative where applicable
- the UI should clearly say what will happen next

**Outcome**
Users are less likely to trigger accidental destructive or state-changing commands.

---

### 4.9 Better News Surface Labels

**Problem**  
News cards already show source/freshness in places, but the product should be more explicit about whether a result is grounded or just a headline-level state.

**Change**
Improve news card/status language so users can tell:

- source origin
- grounding state
- whether the brief is headline-only, grounded, or degraded

**Rules**
- reuse existing grounded/degraded status concepts
- keep badges small and readable

**Outcome**
The News page better communicates trust and evidence quality.

---

## 5. What Is Intentionally Deferred

These are important, but not part of this first frontend polish slice:

- full provider key entry and connector setup UX
- memory export/download pipeline
- multi-user/profile support
- screen-capture crop preview/consent overlay
- richer mobile-first redesign beyond the current responsive breakpoints
- full calendar connector flow

They should remain documented as follow-on product work, not silently implied as complete.

---

## 6. Implementation Order

### Pass 1 — Highest immediate product value

1. persistent primary nav
2. header page/status cluster
3. intro-first default on first run
4. stronger thinking bar
5. improved chat-bar labels and titles
6. PTT state feedback
7. morning snapshot fallback states
8. inline memory confirmations

### Pass 2 — Surface quality refinements

1. news grounding/source badge improvements
2. stronger calendar connect funnel
3. additional responsive polish where needed

---

## 7. Success Criteria

This pass is successful when:

- a new user can tell where to click within seconds
- the app no longer feels like it starts in the middle of the product
- waiting states are understandable
- the mic has an obvious active/inactive state
- destructive memory actions feel safer
- the header gives persistent orientation and runtime confidence

---

## 8. Canonical Outcome

This UX pass does not change Nova’s core philosophy.

It makes Nova’s philosophy legible.

Nova should still feel:

- governed
- explicit
- visible
- user-controlled

But it should also feel:

- clearer
- calmer
- more welcoming
- more complete as a product
