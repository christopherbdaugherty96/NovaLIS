# Planning Task Preview Live Proof Report

Date: 2026-05-06
Branch: `main`

## Verdict

Pass, with one small docs/runtime-truth alignment edit made.

The live runtime helper now renders planning-only Task Understanding preview, bounded Task Envelope, and session-local Run Preview state for task-like general-chat fallback requests. Casual chat does not receive a preview.

The preview remains docs/planning scaffolding for understanding and continuity only. It is not a Dry Run API, not the full Task Environment Router, not a Brain Trace UI, and not execution authority.

## Live Evidence

Raw transcript:

- `raw/planning_preview_runtime_handoff.json`

Focused tests:

- `raw/focused_pytest_results.txt`
- Command: `python -m pytest tests/conversation/test_task_understanding_preview.py tests/conversation/test_planning_run_preview.py tests/conversation/test_request_understanding_formatter.py -q`
- Result: `42 passed`

Final verification command:

- `python -m pytest tests/conversation/test_task_understanding_preview.py tests/conversation/test_planning_run_preview.py tests/conversation/test_request_understanding_formatter.py tests/test_runtime_auditor.py tests/test_runtime_governance_docs.py -q`
- Result: `69 passed`

## Prompt Cases Captured

| Case | Observed behavior | Status |
| --- | --- | --- |
| `summarize this task` with session context | Renders `simple_task_mode` preview state, uses session context, emits envelope, and records a session-local planning run with `status: planning`. | Pass |
| `make a bounded task envelope` with caller-provided memory | Uses caller-provided stable-memory context and emits allowed/blocked actions. | Pass |
| `turn this script into a scene plan` without script context | Marks `clarification_needed: true` and sets next step to ask one focused clarification. | Pass |
| `hey how are you` | Leaves task preview and run preview absent. | Pass |

## What The Preview Does Now

- Produces a compact Task Understanding prompt block for task-like fallback requests.
- Records goal, context used, constraints, assumptions, confidence, clarification state, and suggested next step.
- Adds a bounded Task Envelope with allowed planning actions and blocked execution actions.
- Renders session-local Run Preview state with `run_id`, `status`, `current_step`, `next_step`, `last_interacted_run_id`, and `focused_run_id`.
- Keeps the private in-memory RunManager out of the skill state passed to general chat.

## Safety Result

The proof evidence shows:

- `planning_only: true`
- `authority_effect: none`
- `execution_performed: false`
- `authorization_granted: false`
- no private `_planning_run_manager` leaked into the general-chat skill state

No Governor call, capability call, OpenClaw/browser launch, file write, email send, calendar action, account action, or persistent run history is created by the preview.

## Still Docs-Only / Future

- Full Task Environment Router
- Dry Run / Plan Preview API
- Brain Trace UI
- runtime/live Capability Contract lookup
- persistent RunManager storage/history
- RunManager execution integration
- Co-Work page integration

## Docs / Runtime Truth Alignment

Small alignment edits were needed after the merge:

- `nova_backend/src/audit/runtime_auditor.py` now emits a generated `Brain Planning Preview` runtime-system entry when the planning preview module exists.
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md` was regenerated and now lists `Brain Planning Preview`.
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md` now notes Task Understanding + Run Preview as an active planning-only supporting surface.

No authority expansion was made.

## Screenshots

No screenshot was needed for this pass because the preview evidence is internal runtime handoff state rather than a stable UI-rendered widget. The raw JSON transcript is the primary proof artifact.
