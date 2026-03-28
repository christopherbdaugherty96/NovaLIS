# Key Skill Reliability Matrix
Updated: 2026-03-27

## What This Document Is
This is a practical reliability checkpoint for Nova's most important everyday skills.

It is not constitutional law and it is not the generated runtime fingerprint.
It is a plain-language validation record showing:
- which key skills were checked
- what was improved recently
- what the current runtime readiness looks like
- what still needs real-device confirmation

## Scope Of This Checkpoint
This pass focused on the skills and runtimes that matter most in normal use:
- weather
- news
- calendar
- governed web search
- news intelligence / brief generation
- screen analysis
- TTS
- STT
- voice presentation
- bounded general chat fallback
- governed memory surface

## What Was Improved In The Recent Hardening Passes
### Weather
- broader weather/forecast trigger coverage
- clearer degraded states when the provider is not configured
- more useful widget metadata for setup and availability

### News
- summary text now reflects the actual news result more honestly
- empty-feed states now surface as unavailable instead of generic success copy
- widget data now includes source/category counts

### Calendar
- no longer collides with schedule-management commands
- clearer connected vs not-connected states
- setup hints are surfaced instead of silent failure

### Voice Output (TTS)
- speech success is now ledgered after real render success instead of being marked rendered too early
- speech failure is now ledgered explicitly
- voice status now includes speech-input readiness too, not just speech output

### Voice Input (STT)
- STT runtime can now report whether ffmpeg and the local Vosk model are actually ready
- router failure handling now logs cleanly instead of printing to stdout
- STT short-circuits earlier when the local model is not present

## Validation Result
### Focused Voice And Status Pass
The focused speech/status regression bundle passed:
- `23 passed`
- `2 passed` for the targeted voice-status / voice-check conversation slice
- `15 passed` for system-status diagnostics coverage

### Broader Key Skill Pass
The broader key-skill reliability bundle passed:
- `63 passed`

This bundle covered:
- weather skill
- news skill
- calendar skill
- web search executor
- news intelligence executor
- screen analysis executor
- TTS executor
- STT engine/router
- voice agent
- bounded general chat fallback

### Governed Memory Pass
The focused governed-memory executor suite also passed:
- `10 passed`

## Current Readiness Snapshot
### Weather
- Status: Ready
- Notes: now degrades more honestly when provider setup is missing

### News
- Status: Ready
- Notes: empty/unavailable news states are clearer than before

### Calendar
- Status: Ready with connector caveat
- Notes: runtime behavior is cleaner, but real usefulness still depends on a configured local `.ics` path

### Web Search
- Status: Ready
- Notes: governed search remains answer-first with source follow-up paths

### News Intelligence
- Status: Ready
- Notes: headline/brief/report flows are covered by focused executor tests

### Screen Analysis
- Status: Ready with privacy UX caveat
- Notes: governed analysis path is working, but the larger consent/preview UX is still a product gap

### Memory
- Status: Ready
- Notes: governed memory list/show/save/edit/delete surfaces remain covered and active

### TTS
- Status: Ready on preferred engine in this local runtime
- Local runtime note: Piper is ready
- Local runtime note: fallback `pyttsx3` is unavailable on this machine
- Important caveat: audible output still requires an actual voice check on the device

### STT
- Status: Ready in this local runtime
- Local runtime note: bundled `ffmpeg` was found
- Local runtime note: the local Vosk model directory exists
- Important caveat: microphone/device quality still depends on real input conditions

## What "Ready" Means Here
In this document, `Ready` means:
- the governed path exists
- focused tests passed
- the runtime surface behaves honestly when degraded

It does not mean:
- every external connector is configured
- every local machine has identical audio hardware behavior
- every future workflow is finished

## Remaining Honest Gaps
- audible TTS still needs literal device confirmation
- STT still needs real-mic quality confirmation in normal room conditions
- calendar usefulness still depends on a real `.ics` source
- screen-analysis consent/preview UX is still not complete
- richer connector-backed workflows remain later work

## Best Short Summary
Nova's key daily-use skills are in a materially stronger place now.

The core outcome from this checkpoint is:
- the major everyday skills are covered
- degraded states are more honest
- speech input/output runtime truth is better
- the local runtime on this machine has a ready Piper path and a ready STT path
- final audible confidence is still a real-device validation step, not something the code alone can prove
