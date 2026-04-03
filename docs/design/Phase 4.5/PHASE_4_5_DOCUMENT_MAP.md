# Phase 4.5 Document Map

Status:
- active UX, speech, perception, and assistant-utility design layer

## Purpose

Phase 4.5 is where Nova shifts from internal architecture toward:
- usability
- friendliness
- speech and input naturalness
- explain-this and screen-help direction
- visible assistant product polish

This folder contains both:
- active design inputs that still matter
- preserved raw notes from the same design era
- a small number of future-leaning support notes that still preserve useful context

## Read This First

- `docs/design/Phase 4.5/NOVA_USER_FRIENDLINESS_TODO_2026-04-02.md`
- `docs/design/Phase 4.5/NOVA_USER_EXPERIENCE_IMPROVEMENT_PLAN_2026-03-26.md`
- `docs/design/Phase 4.5/NOVA_WAKE_WORD_SCREEN_CONTEXT_IMPLEMENTATION.md`
- `docs/design/Phase 4.5/SPEECH_AND_INPUT_NATURALNESS_PLAN_2026-03-20.md`

These are the clearest high-value guides for current interpretation.

## Current High-Value Product Inputs

- `docs/design/Phase 4.5/NOVA_CONNECTIONS_SETUP_UI_REDESIGN.md`
  Setup page redesign: user profile (name, nickname, email, rules), interactive
  provider connection cards (3 states: connected/key-needed/not-set-up),
  inline save-and-test flow, per-card disconnect, and disconnect-all reset.
  Profile save writes a protected user_identity record to governed_memory_store.
  Grounded status: profile and connection cards are now shipped; the remaining
  Phase 4.5 gap is setup/readiness polish around those live surfaces.

- `docs/design/Phase 4.5/NOVA_USER_FRIENDLINESS_TODO_2026-04-02.md`
- `docs/design/Phase 4.5/NOVA_USER_EXPERIENCE_IMPROVEMENT_PLAN_2026-03-26.md`
- `docs/design/Phase 4.5/NOVA_WAKE_WORD_SCREEN_CONTEXT_IMPLEMENTATION.md`
- `docs/design/Phase 4.5/SPEECH_AND_INPUT_NATURALNESS_PLAN_2026-03-20.md`
- `docs/design/Phase 4.5/NOVA_STYLE_LAYER_PLAN_2026-03-20.md`

## Supporting UX And Utility Inputs

- `docs/design/Phase 4.5/NOVA_ASSISTANT_UTILITY_AND_UI_AUDIT_2026-03-20.md`
- `docs/design/Phase 4.5/NOVA_LOCAL_PROJECT_AND_ASSISTANT_UTILITY_AUDIT_2026-03-20.md`
- `docs/design/Phase 4.5/NOVA_LOCAL_PROJECT_VISUAL_EXPLAINER_PLAN_2026-03-21.md`
- `docs/design/Phase 4.5/NOVA_CHATBOX_HELPER_BUTTONS_CLEANUP_NOTE_2026-03-21.md`
- `docs/design/Phase 4.5/NOVA_TTS_REGRESSION_NOTE_2026-03-21.md`
- `docs/design/Phase 4.5/RUNTIME_ALIGNMENT_NOTE_2026-03-07.md`

## Preserved Raw Source Notes

- the orb note in this folder
- the UI framework note in this folder
- the constitutional design note in this folder
- the historical Phase-4.5 roadmap note in this folder
- `docs/design/Phase 4.5/Nova Personal Intelligence Hub Arch.txt`

These should be kept as source material, not treated as the first reading path.

During the 2026-04-02 second-pass cleanup, the deprecated `UI_FRAMEWORK.md.txt` pointer file was moved to:
- `docs/design/archive/redundant_placeholders_2026-04-02/`

Important interpretation:
- the orb and UI framework notes still carry useful non-directive UI and presence rules
- the historical Phase-4.5 roadmap remains framing, not current authority
- `Nova Personal Intelligence Hub Arch.txt` is future-leaning and should be read as early hub or home-assistant direction, not as Phase-4.5 runtime intent

## Interpretation Rule

When reading the Phase-4.5 folder:
- start with the friendliness, UX-improvement, wake-word, and speech-naturalness documents
- use audits and cleanup notes as implementation support
- preserve the raw notes as historical design material, not runtime truth
