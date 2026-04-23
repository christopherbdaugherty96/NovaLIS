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

Status: PASS after correction

The basic conversation shell, local controls, and explicit governed memory save/recall path worked. The confirmation UX issue found in the first pass has been corrected: `yes` now executes a pending folder-open action as prompted.

## Passing Probes

- `hello` returned a warm greeting.
- `what can you do?` returned the live capability surface.
- `open documents` correctly asked for confirmation before opening a local folder.
- `yes` after `open documents` opened `C:\Users\Chris\Documents` after the correction.
- `confirm` after `open documents` opened `C:\Users\Chris\Documents`.
- `turn brightness up` and `turn brightness down` returned successful local-control responses.
- `turn volume down` and `turn volume up` returned successful local-control responses.
- `memory save preference: temporary verification codeword is cerulean anvil` saved memory `MEM-20260423-031802-9CFA`.
- `what is my temporary verification codeword?` recalled `cerulean anvil`.
- `memory list` showed the saved item while present.
- `delete memory MEM-20260423-031802-9CFA` plus `confirm` deleted the test memory.
- `memory list` after deletion returned no memory items for that filter.

## Issues Found

1. Confirmation prompt mismatch - corrected:
   - Prompt: `Open documents? This action needs confirmation. Reply 'yes' to proceed or 'no' to cancel.`
   - First-pass actual: `yes` did not proceed. It returned `Gotcha. What should I continue from?`
   - Corrected actual: `yes` opened `C:\Users\Chris\Documents`.
   - `confirm` still works.

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

Keep confirmation handling covered in regression tests so pending action replies are consumed before normal clarification/follow-up routing. Supported confirmation/cancel words should remain:

- yes / confirm / proceed
- no / cancel / stop

## Correction Verification

Applied correction:

- Pending governed action and website-open confirmations are handled before normal conversation routing.
- Added regression coverage for `open documents` followed by `yes` without bypassing normal gates.

Verification:

```powershell
python -m pytest nova_backend/tests/conversation nova_backend/tests/test_general_chat_behavior.py nova_backend/tests/phase45/test_brain_server_basic_conversation.py nova_backend/tests/test_brain_server_session_cleanup.py -q
```

Result:

```text
340 passed in 27.82s
```

Live smoke:

```text
open documents -> Open documents? This action needs confirmation. Reply 'yes' to proceed or 'no' to cancel.
yes -> Okay. Opened your documents folder: C:\Users\Chris\Documents
```
