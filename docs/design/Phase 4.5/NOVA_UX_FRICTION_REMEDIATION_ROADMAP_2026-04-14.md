# Nova UX Friction Remediation Roadmap

Updated: 2026-04-14
Status: Active remediation plan
Source: Deep product audit of frontend, docs, and runtime surfaces

## Core Diagnosis

Nova mixes three modes of being in the same product surface:
1. A calm assistant for everyday use
2. A transparent governed system
3. An advanced local operator workspace

These can coexist, but the boundaries are too visible too early. The main user pain is:
- Too much to understand before the first win
- Too much internal syntax in the product surface
- Too much operator responsibility when setup or connection goes wrong
- A few places where the UI sounds more mature than the live runtime really is

## P1 Fixes (Highest friction, implement first)

### P1-A: Wake-word and live-help copy overpromises
**Problem:** UI frames live help as "Say Hey Nova and ask naturally" and "Let Nova stay with this screen," which reads like a dependable ambient assistant. The implementation depends on browser permissions, screen share, microphone, STT, and looped session flow. Gap becomes immediate trust friction.
**Files:** index.html (lines 123, 128, 135, 145, 170), dashboard.js (lines 832, 1008, 1030)
**Fix:** Rewrite copy to describe current experience conservatively. Frame as "experimental" or "when available." Replace "ask naturally" with honest description of what works now.

### P1-B: Syntax-first examples instead of outcome-first phrasing
**Problem:** Quick actions and help examples use syntax-heavy phrases like `policy create ...`, `dismiss schedule SCH-0000-0000`, `pattern opt in`, `thread detail deployment issue`. User must learn Nova's nouns before getting value.
**Files:** dashboard-config.js (lines 134-262)
**Fix:** Lead with outcome-first phrasing. Move syntax-heavy commands to an advanced/power-user section. Keep the first examples as goals, not commands.

### P1-C: Startup failure recovery is repo-operator-shaped
**Problem:** Main stuck state is "Connecting" with guidance to "restart Nova locally" using shell scripts. First failure path assumes user understands local process management.
**Files:** index.html (lines 26-28, 347), dashboard.js (line 1894)
**Fix:** Add in-product recovery guidance that works for non-technical users. Show what to try first (wait, refresh), escalate to technical steps only if needed.

## P2 Fixes (Important but less acute)

### P2-A: Too many top-level nav destinations
**Problem:** 10 nav items, several conceptually overlapping for new users.
**Files:** dashboard-config.js (line 29), Guide 14
**Fix:** Consider progressive disclosure or soft-grouping for admin surfaces.

### P2-B: Settings defaults show more-ready-than-real state
**Problem:** settingsRuntimeState defaults to enabled before real payload arrives.
**Files:** dashboard.js (line 150)
**Fix:** Default permissions to false or "unknown" until runtime truth loads.

### P2-C: Chat surface cognitive load
**Problem:** Too many widgets competing before user gets first success.
**Files:** index.html (lines 67, 120, 164, 168)
**Fix:** Simplify initial chat surface, progressive reveal of power features.

### P2-D: Workspace language too technical
**Problem:** Workspace talks in "thread detail," "memory save thread," "health state" — task-tracker internals.
**Files:** dashboard-workspace.js (lines 33, 81, 183, 278)
**Fix:** Reframe around "continue what I was working on" and "pick up where I left off."

### P2-E: OpenClaw user-facing model still complex
**Problem:** Agent surface asks users to understand templates, delivery modes, scheduler settings, quiet-hours.
**Files:** dashboard-control-center.js (lines 116, 210, 257)
**Fix:** Simplify to "reviewable help" framing.

## P3 Fixes (Polish and consistency)

### P3-A: Trust doc mismatch for openclaw_execute
**Problem:** CURRENT_RUNTIME_STATE.md says openclaw_execute "runs a named read-only template through the governed network path" but project_snapshot is a bounded local-read path.
**Files:** CURRENT_RUNTIME_STATE.md (line 83), runtime_auditor.py
**Fix:** Update capability 63 description in the auditor to be accurate about both network and local templates.

### P3-B: Inconsistent product language
**Problem:** Frontend guide describes calm everyday tool, but UI uses "Policies," "Trust Center," "Pattern review," "Bridge status," "operator-health."
**Files:** Guide 14, index.html, dashboard-chat-news.js
**Fix:** Audit all surface labels for consistency with calm assistant framing.

## Implementation Order
1. P1-A: Live-help copy (conservative rewrite)
2. P1-B: Command suggestions (outcome-first)
3. P1-C: Startup recovery (in-product guidance)
4. P2-B: Settings defaults (safe initial state)
5. P3-A: Trust doc accuracy (openclaw_execute description)
6. P2-D: Workspace language (outcome framing)
7. P2-A, P2-C, P2-E: Progressive disclosure (larger UX work)
8. P3-B: Label consistency audit

## Applied So Far

Completed in the current remediation sequence:
- P1-A: live-help copy now frames the feature more conservatively and honestly
- P1-B: command discovery now leads with outcome-first language instead of Nova syntax
- P1-C: startup recovery now escalates from wait -> refresh -> backend check -> full restart
- P2-B: advanced runtime settings now default to a safer not-yet-ready state until runtime truth loads
- P3-A: OpenClaw capability wording now reflects both governed-network and bounded local-read paths
- P2-D: Workspace language now centers ongoing work, saved notes, and next steps instead of internal thread/memory jargon
- P2-E / P3-B partial: Policies, Trust rule messaging, and Home/Workspace overlap have been softened toward calmer user-facing language

Still best left for later:
- deeper top-level navigation simplification
- stronger progressive disclosure for admin-style surfaces
- fuller Home vs Workspace structural simplification beyond wording
- a final whole-product label consistency pass across every page
