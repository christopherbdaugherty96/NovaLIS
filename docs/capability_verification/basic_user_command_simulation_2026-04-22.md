# Basic User Command Simulation - 2026-04-22

## Scope

Live WebSocket simulation of first-user style commands:

- Greeting and capability discovery
- Local folder open request
- Brightness and volume controls
- Governed memory save, recall, list, and delete
- Confirmation behavior around local actions

Backend was started with:

```powershell
python scripts/start_daemon.py --no-browser
```

Model lock was cleared through:

```powershell
POST /api/settings/model/confirm
```

## Result

Status: PARTIAL

The basic conversation shell, local controls, and explicit governed memory save/recall path worked. The main issue is confirmation UX: Nova tells users to reply `yes`, but `yes` did not execute the pending folder-open action. `confirm` did.

## Passing Probes

- `hello` returned a warm greeting.
- `what can you do?` returned the live capability surface.
- `open documents` correctly asked for confirmation before opening a local folder.
- `confirm` after `open documents` opened `C:\Users\Chris\Documents`.
- `turn brightness up` and `turn brightness down` returned successful local-control responses.
- `turn volume down` and `turn volume up` returned successful local-control responses.
- `memory save preference: temporary verification codeword is cerulean anvil` saved memory `MEM-20260423-031802-9CFA`.
- `what is my temporary verification codeword?` recalled `cerulean anvil`.
- `memory list` showed the saved item while present.
- `delete memory MEM-20260423-031802-9CFA` plus `confirm` deleted the test memory.
- `memory list` after deletion returned no memory items for that filter.

## Issues Found

1. Confirmation prompt mismatch:
   - Prompt: `Open documents? This action needs confirmation. Reply 'yes' to proceed or 'no' to cancel.`
   - Actual: `yes` did not proceed. It returned `Gotcha. What should I continue from?`
   - Actual working command: `confirm`.

2. Pending confirmation blocks unrelated requests:
   - After `open documents`, follow-up prompts like `turn brightness up`, `turn volume down`, memory save, and memory recall were all intercepted by the pending confirmation state until it was cleared.
   - This is expected for safety, but the broken `yes` path makes it feel like Nova is stuck.

3. Post-action stale confirmation echo:
   - Brightness and volume commands executed immediately.
   - Sending `confirm` after those immediate actions produced stale/odd responses such as `Brightness up, got it.`
   - This suggests the confirmation/follow-up interpreter is over-eager after already-completed local controls.

4. Natural recall can hallucinate when the save did not happen:
   - Before the explicit memory save succeeded, `do you remember my favorite test snack?` answered with an unrelated older snack memory.
   - After explicit governed memory save, the unique codeword recall worked.

## Cleanup

- Brightness was moved back down after the brightness-up test.
- Volume was moved back up after the volume-down test.
- Temporary memory `MEM-20260423-031802-9CFA` was deleted.

## Recommended Next Fix

Fix confirmation handling so `yes` and `no` behave exactly as the confirmation prompt says, or change the prompt to advertise `confirm`/`cancel`. The better product behavior is to support both:

- yes / confirm / proceed
- no / cancel / stop
