# Nova TTS Regression Note
Date: 2026-03-26
Status: Product/runtime note; code-path mitigation landed, final device confidence still pending
Scope: Preserve the current speech-output status where the runtime path is stronger than before, but final real-device confidence is still not treated as fully closed

## Current Summary
Current observed state is now:
- STT works
- TTS code paths are stronger than before
- voice-origin turns can auto-speak through the shared runtime speech helper
- preferred local rendering now has a fallback into the governed TTS executor engine
- final real-device spoken-output confidence is still not considered fully closed

In plain English:
- Nova can still hear or receive spoken input
- Nova is much better positioned to speak the response back
- but the last mile still depends on the specific local device/audio setup

## What Improved On `main` (2026-03-26)
The current runtime now:
- auto-speaks voice-origin responses through the shared Nova speech helper
- prefers the stronger local Piper-backed renderer
- falls back to the TTS executor engine when the preferred renderer cannot play
- keeps the TTS authority surface sealed under the governor path

That means:
- the code path is materially stronger than before
- fallback behavior is cleaner than before
- the product is closer to a complete voice loop than it was

## Why This Note Still Matters
This is still an important product note because voice is one of the most obvious quality signals to a non-technical user.

The user experience should become:
- speech in works
- Nova answers on screen
- Nova also speaks the answer back

That feels complete.

## Product Interpretation
Treat this as:
- a partly mitigated speech-output issue
- not proof that the whole speech system is down
- not proof that the problem is solved on every device yet

The likely product framing is:
- speech-to-text / spoken input path is alive
- text-to-speech / spoken output path is substantially improved
- final device-confidence validation is still the remaining gap

## Placement
This belongs in the current product/runtime quality track.

It is not a Phase 7 reasoning item.
It is not a Phase 8 execution-expansion item.

## Suggested Future Branch
- `codex/tts-regression-stage2-device-confidence`

## Success Condition
Voice interaction returns to a clearly complete loop for real use:
- user can speak to Nova
- Nova answers on screen
- Nova also speaks the answer back
- the team is confident that this holds on the intended device setups
