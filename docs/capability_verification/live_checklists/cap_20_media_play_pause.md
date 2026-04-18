# Live Test Checklist — Cap 20: media_play_pause
Phase 5 of 6 · Priority: Medium (reversible_local)

## Pre-conditions
- [ ] A media player is open (Spotify, Windows Media Player, VLC, etc.)
- [ ] Media is loaded and either playing or paused

## Test 1 — Play
1. Pause your media manually
2. Type: `play`
3. ✅ Media starts playing OR Nova gives platform-specific message

## Test 2 — Pause
1. With media playing, type: `pause`
2. ✅ Media pauses OR Nova gives platform-specific message

## Note on platform support
Media controls use platform APIs. On Windows, play/pause may not be available.
Nova should respond with a clear "not available on this device" message rather
than crashing.

## Sign-off
```
python scripts/certify_capability.py live-signoff 20
python scripts/certify_capability.py lock 20
```
