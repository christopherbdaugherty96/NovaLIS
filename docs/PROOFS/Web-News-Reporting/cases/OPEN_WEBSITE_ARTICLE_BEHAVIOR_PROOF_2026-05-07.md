# Open Website / Article Behavior Proof - 2026-05-07

Status: pass for command boundary / screenshot blocked

## Request Coverage

- `open website notaurl`
- valid website open prompt evidence from prior confirmation flow
- Browser Use screenshot attempt against `http://127.0.0.1:8000`

## What Happened

Malformed single-label input such as `notaurl` is rejected before confirmation:

```text
I couldn't verify 'notaurl' as a valid website before confirmation.
```

Valid website targets remain confirmation-bound before opening. Browser screenshot proof was attempted, but Browser Use failed before page interaction with:

```text
failed to write kernel assets: The system cannot find the path specified. (os error 3)
```

## What Did Not Happen

- Invalid input did not get normalized into a valid-looking URL.
- No browser open occurred for malformed input.
- No browser/computer-use capability was added to Nova.
- No screenshot was faked through an unrelated browser path.

## Governance Boundary

Open website behavior remains confirmation-bound and does not create broad browsing, computer-use, account, external-write, or autonomous authority.

## Evidence

- `docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/ui_followup_probe.json`
- `docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/browser_screenshot_followup_attempt.txt`
- `docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/followup_combined_pytest_results.txt`

## Regression Coverage

- `nova_backend/tests/utils/test_web_target_planner.py`
- `nova_backend/tests/websocket/test_session_handler_proof_blockers.py`

## Remaining Follow-Up

- Fix Browser Use/iab runtime asset setup before demanding screenshot/click proof.
- Add screenshot-only proof after browser capture works.
