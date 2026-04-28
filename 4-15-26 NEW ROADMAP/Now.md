# NOW.md — Superseded Sprint Notes

Date updated: 2026-04-28

Status: historical/current sprint record, **not the active priority source**.

This file previously tracked the installer / Cap 64 close-out sprint. That work is preserved, but the active owner priority changed on 2026-04-27.

Use these files first:

```text
4-15-26 NEW ROADMAP/CURRENT_PRIORITY_OVERRIDE_2026-04-27.md
4-15-26 NEW ROADMAP/NOVA_CONSOLIDATED_ROADMAP_2026-04-28.md
4-15-26 NEW ROADMAP/BackLog.md
```

---

## Current Active Priority

The active implementation task is:

```text
Build the minimal RequestUnderstanding trust/action-history review card.
```

Current active sequence:

```text
1. Build RequestUnderstanding trust/action-history review card.
2. Re-run live conversation checks when a faster local model, longer timeout, or stable provider lane is available.
3. Fix narrow RequestUnderstanding routing bypasses, starting with paused-scope thread-continuation cases.
4. Start local capability signoff matrix after conversation visibility is stable.
5. Add OpenClawMediator skeleton only after conversation visibility and local capability limits are clearer.
6. Revisit Google connector/email direction before unpausing Cap 64 P5.
```

Final rule:

> **Conversation first, visibility next, hands later.**

---

## Superseded Sprint Goal

Previous sprint goal:

```text
Non-developer installs and runs Nova in 5 minutes.
```

This remains important future/product work, but it is not the active next task while conversation/trust visibility is being stabilized.

---

## Paused Or Not Active From The Older Sprint

Do not actively run these from older NOW notes unless the owner explicitly unpauses them:

```text
Cap 64 P5 live checklist
Cap 64 live signoff
Cap 64 P6 lock
mail-client live testing
standalone email expansion outside Google connector alignment
Cap 65 / Shopify P5 live work
installer close-out work as the primary sprint
Auralis / website merger work
broad OpenClaw execution
Google connector implementation
ElevenLabs implementation
background reasoning jobs
governed learning persistence
```

Preserve completed work and evidence. Do not delete previous Cap 64, Cap 65, installer, trust backend, or OpenClaw hardening records.

---

## Preserved Historical Notes

The previous contents of this file recorded useful sprint history, including:

```text
Cap 64 confirmation gate fix
Cap 64 P5 readiness notes before pause
Cap 65 P1-P4 automated verification and P5 credential blocker
trust receipt backend hardening
Windows verification work
installer validation blockers
OpenClaw governance hardening progress
Cap 65 Shopify intelligence report progress
```

Those details are preserved in git history and related docs/checklists. Current task selection should follow the priority override and consolidated roadmap, not the older Cap 64/installer sprint ordering.

---

## Current Roadmap Link

For the clean readable roadmap, use:

```text
4-15-26 NEW ROADMAP/NOVA_CONSOLIDATED_ROADMAP_2026-04-28.md
```

For detailed follow-up items and paused scopes, use:

```text
4-15-26 NEW ROADMAP/BackLog.md
```
