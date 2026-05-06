# Request Understanding Review Card Proof Report

Date: 2026-05-06
Branch: `feature/request-understanding-review-card`

## Verdict

Pass for a payload-contract first implementation.

The branch adds a frozen, non-authorizing `RequestUnderstandingReviewCard` payload and wires it into general-chat fallback only when the existing task-like planning preview exists. Casual chat does not receive the payload.

No UI card is claimed in this pass.

## Live Evidence

Raw payload transcript:

- `raw/request_understanding_review_card_payload.json`

Focused tests:

- `raw/focused_pytest_results.txt`
- Command: `python -m pytest tests/conversation/test_request_understanding_review_card.py tests/conversation/test_planning_run_preview.py tests/conversation/test_task_understanding_preview.py tests/conversation/test_request_understanding_formatter.py -q`
- Result: `51 passed`

Final verification command:

- `python -m pytest tests/conversation/test_request_understanding_review_card.py tests/conversation/test_general_chat_runtime.py tests/conversation/test_planning_run_preview.py tests/conversation/test_task_understanding_preview.py tests/conversation/test_request_understanding_formatter.py -q`
- Result: `63 passed`

## Cases Captured

| Case | Observed behavior | Status |
| --- | --- | --- |
| `summarize this task` with session context | Review card present; includes goal, context, allowed planning actions, blocked execution actions, and non-authorizing invariants. | Pass |
| `make a bounded task envelope` with caller-provided memory | Review card present; uses caller-provided memory context and does not read a new memory/history store. | Pass |
| `turn this script into a scene plan` | Review card present with `clarification_needed: true`, lower confidence, and one focused clarification next step. | Pass |
| `hey how are you` | Review card absent. | Pass |

## Contract

The payload includes:

- request text and request type
- detected mode
- goal
- context used
- constraints and assumptions
- confidence and clarification flag
- suggested next step
- allowed planning actions
- blocked execution actions
- receipt/action-history placeholders
- explicit safety invariants

When no caller-provided receipt/action-history data is available, the card returns:

- `relevant_receipts: []`
- `relevant_action_history: []`
- `history_status: "not_available"`

## Enforced Invariants

The dataclass rejects non-safe values in code:

- `authority_effect` must be `none`
- `execution_performed` must be `false`
- `authorization_granted` must be `false`
- `private_reasoning_exposed` must be `false`

The proof payload shows those values on every review-card case.

## Boundary Result

This branch does not:

- call Governor or capabilities
- call OpenClaw
- launch browser/computer-use
- read or write files from the card builder
- send email
- schedule events
- perform account actions
- create persistent RunManager history
- create a new receipt/action-history store
- add approve, run, execute, continue, or delegate buttons

The review card is an inspectable payload foundation for a future visible trust surface.

## Screenshots

No screenshot was captured because this pass proves the review-card payload contract, not a stable UI widget.
