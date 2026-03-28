# Phase 7 Same-Session Review Followthrough Triad Runtime Slice
Updated: 2026-03-28
Status: Live

## Purpose
This slice closes the gap between Nova's governed second-opinion review lane and the user-visible follow-up prompts that were already being suggested in chat.

The new behavior keeps the whole flow inside the same governed session:
- Nova gives the original answer
- the bounded DeepSeek review lane critiques it
- Nova can then respond from that review in the same sandbox
- Nova can also run that whole review-plus-final flow from one explicit command

This is still advisory-only reasoning. It does not widen authority, create a second free-running agent, or introduce autonomous action.

## What changed
- Nova now preserves the pre-review answer before the second-opinion lane overwrites the active response state.
- Nova now stores a normalized review-followthrough snapshot for the most recent verification / second-opinion report.
- Nova now supports explicit same-session followthrough commands:
  - `final answer`
  - `summarize the gaps only`
  - `return to Nova's original answer`
- Nova now supports one-tap explicit triad commands:
  - `second opinion and final answer`
  - `review and final answer`
  - `review this and give final answer`
- Nova now accepts legacy phrasing like `ask Nova to revise the answer` for backward compatibility.
- The second-opinion surface now uses the clearer suggestion label `Nova final answer`.

## Runtime files
- `nova_backend/src/conversation/review_followthrough.py`
- `nova_backend/src/websocket/session_handler.py`
- `nova_backend/src/executors/response_verification_executor.py`
- `nova_backend/src/executors/external_reasoning_executor.py`
- `nova_backend/src/ledger/event_types.py`
- `nova_backend/src/brain_server.py`

## Behavior boundary
This runtime slice does allow:
- same-session review-aware revision
- same-session gap summaries
- same-session restore of Nova's original answer
- explicit one-command review plus final-answer flow

This runtime slice does not allow:
- DeepSeek to become an independent execution agent
- a second agent to take actions directly
- bypassing the Governor
- hidden authority escalation

## Ledger visibility
This slice adds explicit ledger event coverage for review followthrough:
- `REASONING_REVIEW_AUTO_FINALIZED`
- `REASONING_REVIEW_REVISED`
- `REASONING_REVIEW_SUMMARIZED`
- `REASONING_REVIEW_ORIGINAL_RESTORED`

## Verification commands
Run from `nova_backend/`.

- `python -m pytest tests\\executors\\test_response_verification_executor.py tests\\executors\\test_external_reasoning_executor.py -q`
- `python -m pytest tests\\phase45\\test_brain_server_followups_and_voice.py::test_deepseek_button_builds_bounded_second_opinion_context tests\\phase45\\test_brain_server_followups_and_voice.py::test_second_opinion_followthrough_generates_nova_final_answer tests\\phase45\\test_brain_server_followups_and_voice.py::test_second_opinion_followthrough_can_summarize_gaps_and_restore_original_answer tests\\phase45\\test_brain_server_followups_and_voice.py::test_second_opinion_and_final_answer_runs_in_one_explicit_command -q`
- `python -m pytest tests\\phase7\\test_phase7_runtime_contract.py -q`
- `python -m py_compile src\\conversation\\review_followthrough.py src\\websocket\\session_handler.py src\\executors\\response_verification_executor.py src\\executors\\external_reasoning_executor.py src\\brain_server.py`

## Latest verification snapshot
- executor review-lane bundle: `10 passed`
- websocket review-followthrough subset: `4 passed`
- phase7 runtime-contract bundle: `4 passed`
- focused compile pass: passed

## Plain-language truth
Nova can now do the safe version of "me and two AI" inside one governed runtime:
- Nova answers
- the bounded review lane critiques
- Nova can answer again from that critique
- or the user can explicitly ask Nova to run the whole critique-plus-final-answer flow in one step

DeepSeek still stays advisory-only.
Nova still stays the authority-presenting assistant.
