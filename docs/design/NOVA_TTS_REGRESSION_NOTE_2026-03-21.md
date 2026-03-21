# Nova TTS Regression Note
Date: 2026-03-21
Status: Product/runtime regression note only
Scope: Preserve the current user-observed speech regression where speech input still works but spoken output does not

## Regression Summary
Current observed behavior:
- SST works
- TTS back to the user does not

In plain English:
- Nova can still hear or receive spoken input
- Nova is not speaking the response back

## Why This Note Matters
This is a meaningful regression because it breaks the full speech loop.

The user experience becomes:
- speech in works
- speech out does not

That makes voice interaction feel incomplete even if the assistant still answers on screen.

## Product Interpretation
Treat this as a speech-output response-path regression, not as proof that the entire speech system is down.

The likely product framing is:
- speech-to-text / spoken input path still alive
- text-to-speech / spoken output path regressed

## Recommended Fix Scope
When this is addressed, keep the scope narrow:
- verify the response still reaches the TTS trigger path
- verify TTS generation still happens
- verify playback/output is still connected
- verify silent failure is not swallowing the final speech step

Do not broaden this into a full speech architecture rewrite unless the investigation shows a deeper break.

## Placement
This belongs in the current product regression track.

It is not a Phase 7 reasoning item.
It is not a Phase 8 execution-expansion item.

## Suggested Future Branch
- `codex/tts-regression-stage1-output-restore`

## Success Condition
Voice interaction returns to a complete loop:
- user can speak to Nova
- Nova answers on screen
- Nova also speaks the answer back
