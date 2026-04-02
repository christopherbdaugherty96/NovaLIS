from __future__ import annotations

import asyncio
import json
import re
import uuid
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from src.utils.local_request_guard import describe_websocket_rebinding_violation


async def run_websocket_session(ws: WebSocket, deps: Any) -> None:
    """Run Nova's websocket session loop using the assembled runtime module as deps."""
    log = deps.log
    RUNTIME_GOVERNOR = deps.RUNTIME_GOVERNOR
    build_general_chat_skill = deps.build_general_chat_skill
    _Phase42PersonalityAgent = deps._Phase42PersonalityAgent
    WorkingContextStore = deps.WorkingContextStore
    ProjectThreadStore = deps.ProjectThreadStore
    NotificationScheduleStore = deps.NotificationScheduleStore
    PatternReviewStore = deps.PatternReviewStore
    AtomicPolicyStore = deps.AtomicPolicyStore
    failure_ladder = deps.failure_ladder
    send_chat_message = deps.send_chat_message
    send_trust_status = deps.send_trust_status
    send_chat_done = deps.send_chat_done
    GovernorMediator = deps.GovernorMediator
    WS_INPUT_MAX_BYTES = deps.WS_INPUT_MAX_BYTES
    ws_send = deps.ws_send
    thought_store = deps.thought_store
    CLARIFY_PROMPTS = deps.CLARIFY_PROMPTS
    SessionRouter = deps.SessionRouter
    _prune_topic_stack = deps._prune_topic_stack
    _clarification_suggestions = deps._clarification_suggestions
    _is_hard_action_command = deps._is_hard_action_command
    _topic_stack_message = deps._topic_stack_message
    CAPABILITY_HELP_RE = deps.CAPABILITY_HELP_RE
    _capability_help_message = deps._capability_help_message
    TIME_QUERY_RE = deps.TIME_QUERY_RE
    _render_local_time_message = deps._render_local_time_message
    _prepare_explicit_memory_save_params = deps._prepare_explicit_memory_save_params
    invoke_governed_capability = deps.invoke_governed_capability
    _action_result_message = deps._action_result_message
    _action_result_payload = deps._action_result_payload
    send_memory_item_widget = deps.send_memory_item_widget
    send_memory_list_widget = deps.send_memory_list_widget
    send_memory_overview_widget = deps.send_memory_overview_widget
    _structure_long_message = deps._structure_long_message
    _maybe_handle_local_codebase_summary_request = deps._maybe_handle_local_codebase_summary_request
    _maybe_handle_local_architecture_report_request = deps._maybe_handle_local_architecture_report_request
    _maybe_handle_local_project_structure_map_request = deps._maybe_handle_local_project_structure_map_request
    _maybe_prepare_local_open_request = deps._maybe_prepare_local_open_request
    _maybe_handle_local_project_request = deps._maybe_handle_local_project_request
    WORKSPACE_HOME_RE = deps.WORKSPACE_HOME_RE
    send_workspace_home_widget = deps.send_workspace_home_widget
    _render_workspace_home_message = deps._render_workspace_home_message
    WORKSPACE_BOARD_RE = deps.WORKSPACE_BOARD_RE
    OPERATIONAL_CONTEXT_RE = deps.OPERATIONAL_CONTEXT_RE
    ASSISTIVE_NOTICES_RE = deps.ASSISTIVE_NOTICES_RE
    DISMISS_ASSISTIVE_NOTICE_RE = deps.DISMISS_ASSISTIVE_NOTICE_RE
    RESOLVE_ASSISTIVE_NOTICE_RE = deps.RESOLVE_ASSISTIVE_NOTICE_RE
    RESET_OPERATIONAL_CONTEXT_RE = deps.RESET_OPERATIONAL_CONTEXT_RE
    send_operational_context_widget = deps.send_operational_context_widget
    send_assistive_notices_widget = deps.send_assistive_notices_widget
    apply_assistive_notice_state_update = deps.apply_assistive_notice_state_update
    _render_operational_context_message = deps.render_operational_context_message
    _render_assistive_notices_message = deps.render_assistive_notices_message
    _reset_operational_session_state = deps._reset_operational_session_state
    send_thread_map_widget = deps.send_thread_map_widget
    send_thread_detail_widget = deps.send_thread_detail_widget
    TRUST_CENTER_RE = deps.TRUST_CENTER_RE
    _render_trust_center_message = deps._render_trust_center_message
    BRIDGE_STATUS_RE = deps.BRIDGE_STATUS_RE
    _render_bridge_status_message = deps._render_bridge_status_message
    OSDiagnosticsExecutor = deps.OSDiagnosticsExecutor
    CONNECTION_STATUS_RE = deps.CONNECTION_STATUS_RE
    _render_connection_status_message = deps._render_connection_status_message
    VOICE_STATUS_RE = deps.VOICE_STATUS_RE
    inspect_voice_runtime = deps.inspect_voice_runtime
    _render_voice_runtime_message = deps._render_voice_runtime_message
    VOICE_CHECK_RE = deps.VOICE_CHECK_RE
    SHOW_THREADS_RE = deps.SHOW_THREADS_RE
    MOST_BLOCKED_PROJECT_RE = deps.MOST_BLOCKED_PROJECT_RE
    WHY_RECOMMENDATION_RE = deps.WHY_RECOMMENDATION_RE
    CREATE_THREAD_RE = deps.CREATE_THREAD_RE
    CONTINUE_THREAD_RE = deps.CONTINUE_THREAD_RE
    _canonical_thread_reference = deps._canonical_thread_reference
    PROJECT_STATUS_RE = deps.PROJECT_STATUS_RE
    BIGGEST_BLOCKER_RE = deps.BIGGEST_BLOCKER_RE
    THREAD_DETAIL_RE = deps.THREAD_DETAIL_RE
    ATTACH_THREAD_RE = deps.ATTACH_THREAD_RE
    ATTACH_ACTIVE_THREAD_RE = deps.ATTACH_ACTIVE_THREAD_RE
    _build_thread_attachment_summary = deps._build_thread_attachment_summary
    DECISION_THREAD_RE = deps.DECISION_THREAD_RE
    _remember_topic = deps._remember_topic
    voice_experience_agent = deps.voice_experience_agent
    VOICE_ACK_CONFIG = deps.VOICE_ACK_CONFIG
    resolve_pending_escalation_reply = deps.resolve_pending_escalation_reply
    _maybe_auto_speak_for_voice_turn = deps._maybe_auto_speak_for_voice_turn
    speech_state = deps.speech_state
    stop_speaking = deps.stop_speaking
    NovaStyleContract = deps.NovaStyleContract
    _make_shorter_followup = deps._make_shorter_followup
    PHASE42_HELP_COMMANDS = deps.PHASE42_HELP_COMMANDS
    _extract_phase42_query = deps._extract_phase42_query
    PHASE_4_2_ENABLED = deps.PHASE_4_2_ENABLED
    _build_phase42_agents = deps._build_phase42_agents
    invoke_governed_text_command = deps.invoke_governed_text_command
    _extract_sources_from_results = deps._extract_sources_from_results
    _extract_source_links = deps._extract_source_links
    send_widget_message = deps.send_widget_message
    TONE_STATUS_COMMANDS = deps.TONE_STATUS_COMMANDS
    interface_personality_agent = deps.interface_personality_agent
    _log_ledger_event = deps._log_ledger_event
    _render_tone_profile_message = deps._render_tone_profile_message
    send_tone_profile_widget = deps.send_tone_profile_widget
    TONE_SET_RE = deps.TONE_SET_RE
    _parse_tone_set_body = deps._parse_tone_set_body
    ToneProfileStore = deps.ToneProfileStore
    TONE_RESET_RE = deps.TONE_RESET_RE
    SHOW_SCHEDULES_COMMANDS = deps.SHOW_SCHEDULES_COMMANDS
    _process_due_notification_delivery = deps._process_due_notification_delivery
    _render_notification_schedule_message = deps._render_notification_schedule_message
    send_notification_schedule_widget = deps.send_notification_schedule_widget
    NOTIFICATION_SETTINGS_COMMANDS = deps.NOTIFICATION_SETTINGS_COMMANDS
    _render_notification_settings_message = deps._render_notification_settings_message
    SET_QUIET_HOURS_RE = deps.SET_QUIET_HOURS_RE
    _parse_clock_time = deps._parse_clock_time
    _format_policy_clock_value = deps._format_policy_clock_value
    CLEAR_QUIET_HOURS_RE = deps.CLEAR_QUIET_HOURS_RE
    SET_NOTIFICATION_RATE_LIMIT_RE = deps.SET_NOTIFICATION_RATE_LIMIT_RE
    SCHEDULE_BRIEF_RE = deps.SCHEDULE_BRIEF_RE
    _parse_schedule_datetime = deps._parse_schedule_datetime
    _format_local_schedule_time = deps._format_local_schedule_time
    REMIND_ME_RE = deps.REMIND_ME_RE
    RESCHEDULE_SCHEDULE_RE = deps.RESCHEDULE_SCHEDULE_RE
    CANCEL_SCHEDULE_RE = deps.CANCEL_SCHEDULE_RE
    DISMISS_SCHEDULE_RE = deps.DISMISS_SCHEDULE_RE
    PATTERN_OPT_IN_RE = deps.PATTERN_OPT_IN_RE
    send_pattern_review_widget = deps.send_pattern_review_widget
    PATTERN_OPT_OUT_RE = deps.PATTERN_OPT_OUT_RE
    PATTERN_STATUS_COMMANDS = deps.PATTERN_STATUS_COMMANDS
    _render_pattern_review_message = deps._render_pattern_review_message
    PATTERN_REVIEW_RE = deps.PATTERN_REVIEW_RE
    ACCEPT_PATTERN_RE = deps.ACCEPT_PATTERN_RE
    DISMISS_PATTERN_RE = deps.DISMISS_PATTERN_RE
    POLICY_STATUS_COMMANDS = deps.POLICY_STATUS_COMMANDS
    _build_policy_capability_readiness_snapshot = deps._build_policy_capability_readiness_snapshot
    _render_policy_overview_message = deps._render_policy_overview_message
    send_policy_overview_widget = deps.send_policy_overview_widget
    POLICY_CAPABILITY_MAP_COMMANDS = deps.POLICY_CAPABILITY_MAP_COMMANDS
    _render_policy_capability_map_message = deps._render_policy_capability_map_message
    POLICY_CREATE_RE = deps.POLICY_CREATE_RE
    _compile_atomic_policy_template = deps._compile_atomic_policy_template
    _describe_policy_trigger = deps._describe_policy_trigger
    _describe_policy_action = deps._describe_policy_action
    send_policy_item_widget = deps.send_policy_item_widget
    POLICY_SHOW_RE = deps.POLICY_SHOW_RE
    _render_policy_detail_message = deps._render_policy_detail_message
    POLICY_SIMULATE_RE = deps.POLICY_SIMULATE_RE
    _render_policy_simulation_message = deps._render_policy_simulation_message
    send_policy_simulation_widget = deps.send_policy_simulation_widget
    POLICY_RUN_ONCE_RE = deps.POLICY_RUN_ONCE_RE
    _render_policy_run_message = deps._render_policy_run_message
    send_policy_run_widget = deps.send_policy_run_widget
    POLICY_DELETE_RE = deps.POLICY_DELETE_RE
    Invocation = deps.Invocation
    _build_second_opinion_review_text = deps._build_second_opinion_review_text
    _prepare_memory_bridge_params = deps._prepare_memory_bridge_params
    _memory_confirmation_prompt = deps._memory_confirmation_prompt
    plan_web_open = deps.plan_web_open
    _extract_topic_candidate = deps._extract_topic_candidate
    _derive_recommendation_reason = deps._derive_recommendation_reason
    _tone_domain_for_capability = deps._tone_domain_for_capability
    resolve_speakable_text = deps.resolve_speakable_text
    send_token_budget_update = deps.send_token_budget_update
    Clarification = deps.Clarification
    record_correction = deps.record_correction
    run_general_chat_fallback = deps.run_general_chat_fallback
    _select_relevant_memory_context = deps._select_relevant_memory_context
    _tone_domain_for_skill = deps._tone_domain_for_skill
    response_formatter = deps.response_formatter
    build_review_followthrough_snapshot = deps.build_review_followthrough_snapshot
    build_revised_answer_from_review = deps.build_revised_answer_from_review
    render_original_answer = deps.render_original_answer
    summarize_review_gaps = deps.summarize_review_gaps
    _conversation_suggestions = deps._conversation_suggestions
    violation = describe_websocket_rebinding_violation(ws)
    if violation:
        log.warning("Rejected websocket session due to non-local Host/Origin: %s", violation)
        await ws.close(code=1008, reason="Local Nova websocket access requires loopback Host/Origin.")
        return
    await ws.accept()
    log.info("WebSocket connected")

    session_id = str(uuid.uuid4())
    governor = RUNTIME_GOVERNOR
    general_chat_skill = build_general_chat_skill(network=governor.network)
    personality_agent = _Phase42PersonalityAgent() if _Phase42PersonalityAgent is not None else None
    working_context = WorkingContextStore(session_id=session_id, ledger=governor.ledger)
    project_threads = ProjectThreadStore(session_id=session_id, ledger=governor.ledger)
    notification_schedules = NotificationScheduleStore()
    pattern_reviews = PatternReviewStore()
    policy_drafts = AtomicPolicyStore()
    session_context = []
    session_state = {
        "session_id": session_id,
        "turn_count": 0,
        "escalation_count": 0,
        "last_escalation_turn": None,
        "deep_mode_disabled": False,
        "show_thinking_hints": True,
        "presence_mode": False,
        "pending_escalation": None,
        "deep_mode_armed": False,
        "deep_mode_last_armed_turn": None,
        "last_input_channel": "text",
        "last_response": "",
        "last_clarification_turn": None,
        "last_object": "",
        "news_cache": [],
        "news_categories": {},
        "last_sources": [],
        "last_source_links": [],
        "last_news_story_index": None,
        "topic_memory_map": {},
        "last_brief_clusters": [],
        "pending_web_open": None,
        "pending_governed_confirm": None,
        "pending_interpret_confirm": None,
        "analysis_documents": [],
        "last_analysis_doc_id": None,
        "last_intent_family": "",
        "last_mode": "",
        "session_mode_override": "",
        "topic_stack": [],
        "active_topic": "",
        "trust_status": failure_ladder.initial_status(),
        "last_calendar_summary": "",
        "last_calendar_events": [],
        "working_context": working_context.to_dict(),
        "project_thread_active": "",
        "last_recommendation_reason": "",
        "thread_map_last": {},
        "last_memory_overview": {},
        "last_memory_list": {},
        "last_memory_item_id": "",
        "last_memory_item": {},
        "last_policy_overview": {},
        "last_policy_item_id": "",
        "last_policy_item": {},
        "last_policy_simulation": {},
        "last_policy_run": {},
        "last_workspace_home": {},
        "last_operational_context": {},
        "last_assistive_notices": {},
        "assistive_notice_state": {"items": {}},
        "last_reasoning_review": {},
        "last_review_followthrough": {},
        "last_project_structure_map": {},
        "last_thread_detail": {},
        "last_memory_context": [],
        "last_tone_snapshot": {},
        "last_schedule_overview": {},
        "last_pattern_review": {},
        "general_chat_context": [],
        "general_chat_summary": {},
        "conversation_context": {},
    }

    await send_chat_message(ws, "Hello. How can I help?")
    await send_trust_status(ws, session_state["trust_status"])
    await send_chat_done(ws)

    async def _complete_immediate_turn(
        message: str,
        *,
        suggested_actions: list[dict[str, str]] | None = None,
        remember_response: bool = True,
        remembered_response: str | None = None,
        speakable_message: str | None = None,
        tone_domain: str | None = None,
    ) -> None:
        clean_message = str(message or "")
        remembered = str(remembered_response if remembered_response is not None else clean_message)
        if remember_response and remembered.strip():
            session_state["last_response"] = remembered
        presented_message = await send_chat_message(
            ws,
            clean_message,
            suggested_actions=suggested_actions,
            tone_domain=tone_domain,
        )
        await send_chat_done(ws)
        _maybe_auto_speak_for_voice_turn(
            session_state,
            str(speakable_message if speakable_message is not None else presented_message or "").strip(),
        )
        session_state["turn_count"] += 1

    async def _complete_silent_widget_refresh() -> None:
        await send_chat_done(ws)

    REVIEW_FINAL_COMMANDS = {
        "final answer",
        "nova final answer",
        "final answer from review",
        "ask nova to revise the answer",
        "revise the answer using this review",
        "revise your last answer using this verification report",
    }
    REVIEW_AUTO_FINAL_COMMANDS = {
        "second opinion and final answer",
        "second opinion then final answer",
        "review and final answer",
        "review this and give final answer",
        "double check and final answer",
        "double check and give final answer",
        "run second opinion and final answer",
    }
    REVIEW_GAPS_COMMANDS = {
        "summarize the gaps only",
        "summarize the review gaps",
        "summarize the issues only",
    }
    REVIEW_ORIGINAL_COMMANDS = {
        "return to nova's original answer",
        "return to the original answer",
        "show nova's original answer",
    }

    def _latest_session_user_query() -> str:
        for item in reversed(session_context):
            if not isinstance(item, dict):
                continue
            if str(item.get("role") or "").strip().lower() != "user":
                continue
            content = str(item.get("content") or "").strip()
            if content:
                return content
        return ""

    def _remember_review_exchange(user_text: str, assistant_text: str) -> None:
        nonlocal session_context
        session_context.extend(
            [
                {"role": "user", "content": str(user_text or "").strip()},
                {"role": "assistant", "content": str(assistant_text or "").strip()},
            ]
        )
        context_limit = 40 if session_state.get("presence_mode") else 20
        session_context = session_context[-context_limit:]

    async def _maybe_handle_review_auto_final(command_lowered: str) -> bool:
        normalized = str(command_lowered or "").strip().lower()
        if normalized not in REVIEW_AUTO_FINAL_COMMANDS:
            return False

        source_answer = str(session_state.get("last_response") or "").strip()
        review_text = _build_second_opinion_review_text(session_context, session_state)
        if not review_text:
            review_text = source_answer
        if not review_text:
            await _complete_immediate_turn(
                "I need a recent Nova answer first before I can run a second opinion and final answer pass.",
                remember_response=False,
            )
            return True

        review_source_prompt = _latest_session_user_query()
        action_result = await invoke_governed_capability(
            governor,
            62,
            {
                "text": review_text,
                "session_id": session_id,
            },
        )
        action_message = _action_result_message(action_result)
        action_payload = _action_result_payload(action_result)

        if action_result.success:
            session_state["trust_status"] = failure_ladder.record_local_success(
                session_state.get("trust_status", {})
            )
        else:
            session_state["trust_status"] = failure_ladder.record_failure(
                session_state.get("trust_status", {}),
                reason="Temporary issue",
                external=False,
            )
        await send_trust_status(ws, session_state["trust_status"])

        if not action_result.success or not isinstance(action_payload, dict):
            await _complete_immediate_turn(
                action_message or "Governed second opinion is unavailable right now.",
                remember_response=False,
            )
            return True

        session_state["last_reasoning_review"] = dict(action_payload)
        snapshot = build_review_followthrough_snapshot(
            payload=action_payload,
            source_answer=source_answer,
            source_prompt=review_source_prompt,
        )
        session_state["last_review_followthrough"] = snapshot

        final_message = build_revised_answer_from_review(
            snapshot,
            session_id=session_id,
            request_id=f"review-auto-final-{uuid.uuid4()}",
        )
        if not final_message:
            await _complete_immediate_turn(
                "I completed the review, but I couldn't build the final revised answer right now.",
                remember_response=False,
                suggested_actions=[
                    {"label": "Summarize gaps", "command": "summarize the gaps only"},
                    {"label": "Original answer", "command": "return to Nova's original answer"},
                ],
            )
            return True

        review_summary = summarize_review_gaps(snapshot)
        combined_message = (
            "Second opinion summary:\n"
            f"{review_summary}\n\n"
            "Nova final answer:\n"
            f"{final_message}"
        ).strip()
        _log_ledger_event(
            governor,
            "REASONING_REVIEW_AUTO_FINALIZED",
            {
                "session_id": session_id,
                "review_kind": str(snapshot.get("review_kind") or "").strip(),
                "had_source_answer": bool(source_answer),
            },
        )
        await _complete_immediate_turn(
            combined_message,
            suggested_actions=[
                {"label": "Summarize gaps", "command": "summarize the gaps only"},
                {"label": "Original answer", "command": "return to Nova's original answer"},
            ],
            remembered_response=final_message,
            speakable_message=final_message,
        )
        _remember_review_exchange(normalized, final_message)
        return True

    async def _maybe_handle_review_followthrough(command_lowered: str) -> bool:
        normalized = str(command_lowered or "").strip().lower()
        if normalized not in REVIEW_FINAL_COMMANDS | REVIEW_GAPS_COMMANDS | REVIEW_ORIGINAL_COMMANDS:
            return False

        snapshot = dict(session_state.get("last_review_followthrough") or {})
        if not snapshot:
            await _complete_immediate_turn(
                "I don't have a recent review to work from yet. Ask for a second opinion first.",
                remember_response=False,
            )
            return True

        if normalized in REVIEW_FINAL_COMMANDS:
            if not str(snapshot.get("source_answer") or "").strip():
                await _complete_immediate_turn(
                    (
                        "I can use that review to summarize the gaps, but I do not have a Nova answer "
                        "preserved for a final rewrite. Ask for a fresh second opinion on Nova's answer first."
                    ),
                    remember_response=False,
                    suggested_actions=[
                        {"label": "Summarize gaps", "command": "summarize the gaps only"},
                    ],
                )
                return True

            revised_message = build_revised_answer_from_review(
                snapshot,
                session_id=session_id,
                request_id=f"review-followthrough-{uuid.uuid4()}",
            )
            if not revised_message:
                await _complete_immediate_turn(
                    "I couldn't build a final revised answer from that review right now.",
                    remember_response=False,
                )
                return True
            _log_ledger_event(
                governor,
                "REASONING_REVIEW_REVISED",
                {
                    "session_id": session_id,
                    "review_kind": str(snapshot.get("review_kind") or "").strip(),
                    "had_source_answer": bool(str(snapshot.get("source_answer") or "").strip()),
                },
            )
            await _complete_immediate_turn(
                revised_message,
                suggested_actions=[
                    {"label": "Summarize gaps", "command": "summarize the gaps only"},
                    {"label": "Original answer", "command": "return to Nova's original answer"},
                ],
            )
            _remember_review_exchange(normalized, revised_message)
            return True

        if normalized in REVIEW_GAPS_COMMANDS:
            gap_summary = summarize_review_gaps(snapshot)
            _log_ledger_event(
                governor,
                "REASONING_REVIEW_SUMMARIZED",
                {
                    "session_id": session_id,
                    "review_kind": str(snapshot.get("review_kind") or "").strip(),
                    "top_issue": str(snapshot.get("top_issue") or "").strip(),
                },
            )
            await _complete_immediate_turn(
                gap_summary,
                suggested_actions=[
                    {"label": "Nova final answer", "command": "final answer"},
                    {"label": "Original answer", "command": "return to Nova's original answer"},
                ],
            )
            _remember_review_exchange(normalized, gap_summary)
            return True

        original_message = render_original_answer(snapshot)
        if not original_message:
            await _complete_immediate_turn(
                "I do not have Nova's original answer preserved for that review yet.",
                remember_response=False,
                suggested_actions=[
                    {"label": "Summarize gaps", "command": "summarize the gaps only"},
                ],
            )
            return True
        _log_ledger_event(
            governor,
            "REASONING_REVIEW_ORIGINAL_RESTORED",
            {
                "session_id": session_id,
                "review_kind": str(snapshot.get("review_kind") or "").strip(),
            },
        )
        await _complete_immediate_turn(
            original_message,
            suggested_actions=[
                {"label": "Nova final answer", "command": "final answer"},
                {"label": "Summarize gaps", "command": "summarize the gaps only"},
            ],
        )
        _remember_review_exchange(normalized, original_message)
        return True

    try:
        while True:
            GovernorMediator.clear_stale_sessions()
            raw = await ws.receive_text()
            raw_bytes = raw.encode("utf-8")
            if len(raw_bytes) > WS_INPUT_MAX_BYTES:
                log.warning("WebSocket input rejected: %d bytes exceeds limit %d", len(raw_bytes), WS_INPUT_MAX_BYTES)
                await ws_send(ws, {"type": "error", "code": "input_too_long", "message": "Input exceeds maximum allowed length."})
                continue

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                log.warning("WebSocket input rejected: malformed JSON")
                await ws_send(ws, {"type": "error", "code": "invalid_json", "message": "Malformed request."})
                continue

            msg_type = (msg.get("type") or "chat").strip().lower()
            channel = (msg.get("channel") or "text").strip().lower()
            invocation_source = (msg.get("invocation_source") or "").strip().lower()
            silent_widget_refresh = bool(msg.get("silent_widget_refresh"))
            if channel not in {"voice", "text"}:
                channel = "text"
            if invocation_source not in {"voice", "text", "ui", "news_surface", "deepseek_button", "openclaw_bridge"}:
                invocation_source = "voice" if channel == "voice" else "text"

            if msg_type == "get_thought":
                message_id = (msg.get("message_id") or "").strip()
                thought_data = thought_store.get(session_id, message_id) if message_id else None
                if thought_data is None:
                    await ws_send(ws, {"type": "error", "message": "Thought data not found or expired"})
                else:
                    await ws_send(ws, {"type": "thought", "data": thought_data, "message_id": message_id})
                continue

            raw_text = (msg.get("text") or "").strip()
            if not raw_text:
                await _complete_immediate_turn(CLARIFY_PROMPTS["ready_prompt"], remember_response=False)
                continue

            session_state["last_input_channel"] = channel
            interpreted_confirmation_consumed = False

            pending_interpret_confirm = session_state.get("pending_interpret_confirm")
            if pending_interpret_confirm:
                interpret_decision = SessionRouter.route_pending_web_confirmation(raw_text)
                if interpret_decision.action == "confirm":
                    raw_text = str(pending_interpret_confirm.get("interpreted_text") or "").strip()
                    session_state["pending_interpret_confirm"] = None
                    interpreted_confirmation_consumed = True
                    if not raw_text:
                        await _complete_immediate_turn(
                            "Thanks. I lost the interpreted command. Please say it again.",
                            remember_response=False,
                        )
                        continue
                elif interpret_decision.action == "cancel":
                    session_state["pending_interpret_confirm"] = None
                    await _complete_immediate_turn(
                        "No problem. I canceled that action. Please say it again in your own words.",
                        remember_response=False,
                    )
                    continue
                else:
                    await _complete_immediate_turn(
                        "I want to make sure I heard you right. Reply 'yes' to continue or 'no' to cancel.",
                        remember_response=False,
                    )
                    continue

            route_context = SessionRouter.normalize_and_route(raw_text, session_state)
            if route_context.is_empty:
                await _complete_immediate_turn(SessionRouter.ready_prompt(), remember_response=False)
                continue

            text = route_context.text
            lowered = route_context.lowered
            decision = route_context.decision
            _prune_topic_stack(session_state, session_state["turn_count"])

            gate = SessionRouter.evaluate_gate(decision, session_state, session_state["turn_count"])
            if gate.handled:
                if gate.apply_override:
                    session_state["session_mode_override"] = gate.apply_override
                if gate.clear_override:
                    session_state["session_mode_override"] = ""
                if gate.set_clarification_turn:
                    session_state["last_clarification_turn"] = session_state["turn_count"]
                await _complete_immediate_turn(
                    gate.message,
                    suggested_actions=_clarification_suggestions(gate.message),
                    remember_response=False,
                )
                continue
            if not decision.blocked_by_policy and not decision.needs_clarification:
                session_state["last_intent_family"] = decision.intent_family
                session_state["last_mode"] = decision.mode.value
            working_context.apply_user_turn(
                text=text,
                channel=invocation_source,
                intent_family=decision.intent_family,
            )
            session_state["working_context"] = working_context.to_dict()

            if (
                channel == "voice"
                and not interpreted_confirmation_consumed
                and route_context.normalization_changed
                and _is_hard_action_command(text)
            ):
                interpreted_text = text.rstrip(".").strip()
                session_state["pending_interpret_confirm"] = {"interpreted_text": interpreted_text}
                await _complete_immediate_turn(
                    (
                        f'I heard: "{interpreted_text}".\n'
                        "Should I run that action?\n"
                        "Reply 'yes' to continue or 'no' to cancel."
                    ),
                    remember_response=False,
                )
                continue

            command_text = re.sub(r"[.?!]+$", "", text).strip()
            command_lowered = re.sub(r"[.?!]+$", "", lowered).strip()

            if await _maybe_handle_review_auto_final(command_lowered):
                continue
            if await _maybe_handle_review_followthrough(command_lowered):
                continue

            if command_lowered in {
                "topic stack",
                "current topic",
                "what are we discussing",
                "what topic are we on",
            }:
                await _complete_immediate_turn(_topic_stack_message(session_state, session_state["turn_count"]))
                continue

            if CAPABILITY_HELP_RE.match(command_text):
                await _complete_immediate_turn(
                    _capability_help_message(),
                    suggested_actions=[
                        {"label": "System status", "command": "system status"},
                        {"label": "Today's news", "command": "today's news"},
                        {"label": "Audit this repo", "command": "audit this repo"},
                        {"label": "Open documents", "command": "open documents"},
                    ],
                )
                continue

            if TIME_QUERY_RE.match(command_text):
                await _complete_immediate_turn(
                    _render_local_time_message(),
                    suggested_actions=[
                        {"label": "System status", "command": "system status"},
                        {"label": "Today's news", "command": "today's news"},
                    ],
                )
                continue

            explicit_memory_command_text = (
                text
                if re.match(r"^\s*(?:save|remember)\s+(?:this|that)\s*[:\-]", text, re.IGNORECASE)
                else command_text
            )
            explicit_memory_ok, explicit_memory_params, explicit_memory_message = _prepare_explicit_memory_save_params(
                command_text=explicit_memory_command_text,
                session_state=session_state,
                project_threads=project_threads,
                session_id=session_id,
            )
            if explicit_memory_ok:
                if explicit_memory_message:
                    await _complete_immediate_turn(
                        explicit_memory_message,
                        suggested_actions=[
                            {"label": "Save with text", "command": "remember this: <text>"},
                            {"label": "List memories", "command": "list memories"},
                        ],
                        remember_response=False,
                    )
                    continue

                action_result = await invoke_governed_capability(governor, 61, explicit_memory_params)
                action_message = _action_result_message(action_result)
                action_payload = _action_result_payload(action_result)
                if action_message:
                    session_state["last_response"] = action_message
                if isinstance(action_payload, dict):
                    memory_item = action_payload.get("memory_item")
                    if isinstance(memory_item, dict):
                        await send_memory_item_widget(
                            ws,
                            session_state,
                            item=memory_item,
                        )
                    memory_items = action_payload.get("memory_items")
                    if isinstance(memory_items, list):
                        await send_memory_list_widget(
                            ws,
                            session_state,
                            items=memory_items,
                        )
                if action_result.success:
                    await send_memory_overview_widget(ws, session_state)
                await send_chat_message(
                    ws,
                    _structure_long_message(action_message),
                    suggested_actions=[
                        {"label": "List memories", "command": "list memories"},
                        {"label": "Memory overview", "command": "memory overview"},
                    ],
                    tone_domain="continuity",
                )
                await send_chat_done(ws)
                session_state["turn_count"] += 1
                continue

            local_codebase_response = _maybe_handle_local_codebase_summary_request(
                command_text,
                working_context=working_context,
                session_state=session_state,
            )
            if local_codebase_response is not None:
                project_message, project_suggestions, resolved_path = local_codebase_response
                if resolved_path:
                    session_state["last_object"] = resolved_path
                    working_context.apply_patch(
                        {
                            "last_relevant_object": resolved_path,
                            "current_step": "local_codebase_summary",
                        },
                        source="local_codebase_summary",
                    )
                    session_state["working_context"] = working_context.to_dict()
                await _complete_immediate_turn(project_message, suggested_actions=project_suggestions)
                continue

            local_architecture_report = _maybe_handle_local_architecture_report_request(
                command_text,
                working_context=working_context,
                session_state=session_state,
            )
            if local_architecture_report is not None:
                project_message, project_suggestions, resolved_path = local_architecture_report
                if resolved_path:
                    session_state["last_object"] = resolved_path
                    working_context.apply_patch(
                        {
                            "last_relevant_object": resolved_path,
                            "current_step": "local_architecture_report",
                        },
                        source="local_architecture_report",
                    )
                    session_state["working_context"] = working_context.to_dict()
                await _complete_immediate_turn(project_message, suggested_actions=project_suggestions)
                continue

            local_structure_map_response = _maybe_handle_local_project_structure_map_request(
                command_text,
                working_context=working_context,
                session_state=session_state,
            )
            if local_structure_map_response is not None:
                project_message, project_suggestions, resolved_path, structure_widget = local_structure_map_response
                if resolved_path:
                    session_state["last_object"] = resolved_path
                    session_state["last_project_structure_map"] = dict(structure_widget or {})
                    working_context.apply_patch(
                        {
                            "last_relevant_object": resolved_path,
                            "current_step": "local_project_structure_map",
                        },
                        source="local_project_structure_map",
                    )
                    session_state["working_context"] = working_context.to_dict()
                await ws_send(ws, structure_widget)
                if silent_widget_refresh:
                    await _complete_silent_widget_refresh()
                else:
                    await _complete_immediate_turn(project_message, suggested_actions=project_suggestions)
                continue

            local_open_request = _maybe_prepare_local_open_request(
                command_text,
                working_context=working_context,
                session_state=session_state,
            )
            if local_open_request is not None:
                open_message, open_suggestions, open_params = local_open_request
                if isinstance(open_params, dict):
                    session_state["pending_governed_confirm"] = {
                        "capability_id": 22,
                        "params": dict(open_params),
                    }
                await _complete_immediate_turn(open_message, suggested_actions=open_suggestions)
                continue

            local_project_response = _maybe_handle_local_project_request(
                command_text,
                working_context=working_context,
                session_state=session_state,
            )
            if local_project_response is not None:
                project_message, project_suggestions, resolved_path = local_project_response
                if resolved_path:
                    session_state["last_object"] = resolved_path
                    working_context.apply_patch(
                        {
                            "last_relevant_object": resolved_path,
                            "current_step": "local_project_overview",
                        },
                        source="local_project_overview",
                    )
                    session_state["working_context"] = working_context.to_dict()
                await _complete_immediate_turn(project_message, suggested_actions=project_suggestions)
                continue

            if WORKSPACE_HOME_RE.match(command_text):
                workspace_widget = await send_workspace_home_widget(ws, session_state, project_threads)
                await send_assistive_notices_widget(ws, session_state, project_threads, explicit_request=False)
                if silent_widget_refresh:
                    await _complete_silent_widget_refresh()
                else:
                    suggested_actions = list(workspace_widget.get("recommended_actions") or [])
                    await _complete_immediate_turn(
                        _render_workspace_home_message(workspace_widget),
                        suggested_actions=suggested_actions,
                    )
                continue

            if OPERATIONAL_CONTEXT_RE.match(command_text):
                operational_widget = await send_operational_context_widget(ws, session_state, project_threads)
                await send_assistive_notices_widget(ws, session_state, project_threads, explicit_request=False)
                if silent_widget_refresh:
                    await _complete_silent_widget_refresh()
                else:
                    suggested_actions = list(operational_widget.get("recommended_actions") or [])
                    await _complete_immediate_turn(
                        _render_operational_context_message(operational_widget),
                        suggested_actions=suggested_actions,
                        tone_domain="continuity",
                    )
                continue

            if RESET_OPERATIONAL_CONTEXT_RE.match(command_text):
                working_context.reset()
                project_threads.reset()
                session_state["working_context"] = working_context.to_dict()
                _reset_operational_session_state(
                    session_state,
                    working_context_snapshot=session_state["working_context"],
                )
                _log_ledger_event(
                    governor,
                    "OPERATIONAL_CONTEXT_RESET",
                    {
                        "session_id": session_id,
                        "memory_preserved": True,
                    },
                )
                await send_operational_context_widget(ws, session_state, project_threads)
                await send_assistive_notices_widget(ws, session_state, project_threads, explicit_request=False)
                await send_workspace_home_widget(ws, session_state, project_threads)
                await send_thread_map_widget(ws, project_threads, session_state)
                await send_trust_status(ws, session_state["trust_status"])
                if silent_widget_refresh:
                    await _complete_silent_widget_refresh()
                else:
                    await _complete_immediate_turn(
                        (
                            "Operational context reset.\n\n"
                            "Session continuity was cleared. Durable governed memory was preserved."
                        ),
                        suggested_actions=[
                            {"label": "Workspace Home", "command": "workspace home"},
                            {"label": "Operational context", "command": "operational context"},
                            {"label": "Memory overview", "command": "memory overview"},
                        ],
                        tone_domain="continuity",
                    )
                continue

            if WORKSPACE_BOARD_RE.match(command_text):
                workspace_widget = await send_workspace_home_widget(ws, session_state, project_threads)
                thread_map_widget = await send_thread_map_widget(ws, project_threads, session_state)
                focus_thread_name = str(dict(workspace_widget.get("focus_thread") or {}).get("name") or "").strip()
                if not focus_thread_name:
                    focus_thread_name = str(
                        dict((list(thread_map_widget.get("threads") or []) or [{}])[0]).get("name") or ""
                    ).strip()
                if focus_thread_name:
                    await send_thread_detail_widget(
                        ws,
                        session_state,
                        project_threads,
                        thread_name=focus_thread_name,
                    )
                structure_map = _maybe_handle_local_project_structure_map_request(
                    "show structure map",
                    working_context=working_context,
                    session_state=session_state,
                )
                if structure_map is not None:
                    _, _, resolved_path, structure_widget = structure_map
                    if resolved_path:
                        session_state["last_project_structure_map"] = dict(structure_widget or {})
                    await ws_send(ws, structure_widget)
                await send_assistive_notices_widget(ws, session_state, project_threads, explicit_request=False)
                if silent_widget_refresh:
                    await _complete_silent_widget_refresh()
                else:
                    await _complete_immediate_turn(
                        _render_workspace_home_message(workspace_widget),
                        suggested_actions=list(workspace_widget.get("recommended_actions") or []),
                    )
                continue

            if TRUST_CENTER_RE.match(command_text):
                await send_trust_status(ws, session_state["trust_status"])
                await send_assistive_notices_widget(ws, session_state, project_threads, explicit_request=False)
                if silent_widget_refresh:
                    await _complete_silent_widget_refresh()
                else:
                    trust_message, trust_suggestions = _render_trust_center_message(
                        session_state.get("trust_status", {})
                    )
                    await _complete_immediate_turn(
                        trust_message,
                        suggested_actions=trust_suggestions,
                        tone_domain="system",
                )
                continue

            if ASSISTIVE_NOTICES_RE.match(command_text):
                notices_widget = await send_assistive_notices_widget(
                    ws,
                    session_state,
                    project_threads,
                    explicit_request=not silent_widget_refresh,
                )
                if silent_widget_refresh:
                    await _complete_silent_widget_refresh()
                else:
                    await _complete_immediate_turn(
                        _render_assistive_notices_message(notices_widget),
                        suggested_actions=list(notices_widget.get("recommended_actions") or []),
                        tone_domain="continuity",
                    )
                continue

            dismiss_assistive_match = DISMISS_ASSISTIVE_NOTICE_RE.match(command_text)
            if dismiss_assistive_match:
                notice_id = str(dismiss_assistive_match.group(1) or "").strip()
                updated, notice = apply_assistive_notice_state_update(
                    session_state,
                    notice_id=notice_id,
                    status="dismissed",
                )
                await send_assistive_notices_widget(
                    ws,
                    session_state,
                    project_threads,
                    explicit_request=True,
                )
                if not updated:
                    await _complete_immediate_turn(
                        "I couldn't find that active assistive notice. Open Assistive Notices first, then dismiss it from the current list.",
                        suggested_actions=[
                            {"label": "Assistive notices", "command": "assistive notices"},
                            {"label": "Operational context", "command": "operational context"},
                        ],
                        tone_domain="continuity",
                    )
                else:
                    deps._log_ledger_event(
                        RUNTIME_GOVERNOR,
                        "ASSISTIVE_NOTICE_DISMISSED",
                        {
                            "notice_id": str(notice.get("id") or ""),
                            "notice_type": str(notice.get("type") or ""),
                            "session_id": str(session_state.get("session_id") or ""),
                        },
                    )
                    await _complete_immediate_turn(
                        "Assistive notice dismissed for this continuity window. Nova will keep it hidden unless the underlying condition changes.",
                        suggested_actions=[
                            {"label": "Assistive notices", "command": "assistive notices"},
                            {"label": "Operational context", "command": "operational context"},
                        ],
                        tone_domain="continuity",
                    )
                continue

            resolve_assistive_match = RESOLVE_ASSISTIVE_NOTICE_RE.match(command_text)
            if resolve_assistive_match:
                notice_id = str(resolve_assistive_match.group(1) or "").strip()
                updated, notice = apply_assistive_notice_state_update(
                    session_state,
                    notice_id=notice_id,
                    status="resolved",
                )
                await send_assistive_notices_widget(
                    ws,
                    session_state,
                    project_threads,
                    explicit_request=True,
                )
                if not updated:
                    await _complete_immediate_turn(
                        "I couldn't find that active assistive notice. Open Assistive Notices first, then resolve it from the current list.",
                        suggested_actions=[
                            {"label": "Assistive notices", "command": "assistive notices"},
                            {"label": "Operational context", "command": "operational context"},
                        ],
                        tone_domain="continuity",
                    )
                else:
                    deps._log_ledger_event(
                        RUNTIME_GOVERNOR,
                        "ASSISTIVE_NOTICE_RESOLVED",
                        {
                            "notice_id": str(notice.get("id") or ""),
                            "notice_type": str(notice.get("type") or ""),
                            "session_id": str(session_state.get("session_id") or ""),
                        },
                    )
                    await _complete_immediate_turn(
                        "Assistive notice marked resolved for this continuity window. If the condition returns, Nova may surface it again.",
                        suggested_actions=[
                            {"label": "Assistive notices", "command": "assistive notices"},
                            {"label": "Workspace home", "command": "workspace home"},
                        ],
                        tone_domain="continuity",
                    )
                continue

            if BRIDGE_STATUS_RE.match(command_text):
                await send_trust_status(ws, session_state["trust_status"])
                bridge_message, bridge_suggestions = _render_bridge_status_message(
                    OSDiagnosticsExecutor._bridge_status_details()
                )
                await _complete_immediate_turn(
                    bridge_message,
                    suggested_actions=bridge_suggestions,
                    tone_domain="system",
                )
                continue

            if CONNECTION_STATUS_RE.match(command_text):
                await send_trust_status(ws, session_state["trust_status"])
                connection_message, connection_suggestions = _render_connection_status_message(
                    OSDiagnosticsExecutor._connection_status_details()
                )
                await _complete_immediate_turn(
                    connection_message,
                    suggested_actions=connection_suggestions,
                    tone_domain="system",
                )
                continue

            if VOICE_STATUS_RE.match(command_text):
                snapshot = inspect_voice_runtime()
                await send_trust_status(ws, session_state["trust_status"])
                message, suggestions = _render_voice_runtime_message(snapshot, check_mode=False)
                await _complete_immediate_turn(
                    message,
                    suggested_actions=suggestions,
                    tone_domain="system",
                )
                continue

            if VOICE_CHECK_RE.match(command_text):
                test_phrase = (
                    "Nova voice check complete. If you can hear this, spoken output is working on this device."
                )
                action_result = await invoke_governed_capability(
                    governor,
                    18,
                    {
                        "text": test_phrase,
                        "session_id": session_id,
                    },
                )
                if hasattr(action_result, "success") and getattr(action_result, "success", False):
                    session_state["trust_status"] = failure_ladder.record_local_success(
                        session_state.get("trust_status", {})
                    )
                else:
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Voice check failed",
                        external=False,
                    )
                snapshot = inspect_voice_runtime()
                await send_trust_status(ws, session_state["trust_status"])
                message, suggestions = _render_voice_runtime_message(snapshot, check_mode=True)
                await _complete_immediate_turn(
                    message,
                    suggested_actions=suggestions,
                    tone_domain="system",
                )
                continue

            if SHOW_THREADS_RE.match(command_text):
                await send_thread_map_widget(ws, project_threads, session_state)
                if silent_widget_refresh:
                    await _complete_silent_widget_refresh()
                else:
                    await _complete_immediate_turn(project_threads.render_map_message())
                continue

            if MOST_BLOCKED_PROJECT_RE.match(text):
                found, blocked_message = project_threads.render_most_blocked()
                if found:
                    await send_thread_map_widget(ws, project_threads, session_state)
                    top_name = project_threads.most_blocked_thread_name()
                    suggested: list[dict[str, str]] = [{"label": "Show threads", "command": "show threads"}]
                    if top_name:
                        suggested = [
                            {"label": f"Continue {top_name}", "command": f"continue my {top_name}"},
                            {"label": f"Project status", "command": f"project status {top_name}"},
                            {"label": "Save thread memory", "command": f"memory save thread {top_name}"},
                            {"label": "Show threads", "command": "show threads"},
                        ]
                    await _complete_immediate_turn(blocked_message, suggested_actions=suggested)
                else:
                    await _complete_immediate_turn(blocked_message)
                continue

            if WHY_RECOMMENDATION_RE.match(text):
                reason = str(session_state.get("last_recommendation_reason") or "").strip()
                if reason:
                    await _complete_immediate_turn(f"Why this recommendation\n\n{reason}")
                else:
                    await _complete_immediate_turn(
                        "I do not have a recent recommendation context yet. Ask for analysis first (for example, 'explain this').",
                        remember_response=False,
                    )
                continue

            create_thread_match = CREATE_THREAD_RE.match(text)
            if create_thread_match:
                thread_name = str(create_thread_match.group("name") or "").strip()
                created = project_threads.ensure_thread(
                    thread_name,
                    goal=str(working_context.to_dict().get("task_goal") or "").strip(),
                )
                session_state["project_thread_active"] = created.name
                await send_thread_map_widget(ws, project_threads, session_state)
                await _complete_immediate_turn(
                    (
                        f"Thread ready: {created.name}.\n"
                        "You can now say 'save this as part of "
                        f"{created.name}' to attach progress updates."
                    ),
                )
                continue

            continue_thread_match = CONTINUE_THREAD_RE.match(text)
            if continue_thread_match:
                thread_name = str(continue_thread_match.group("name") or "").strip()
                if _canonical_thread_reference(thread_name) in {"this", "it", "thread"}:
                    thread_name = project_threads.active_thread_name() or session_state.get("project_thread_active") or ""
                found, brief = project_threads.render_brief(thread_name)
                if found:
                    session_state["project_thread_active"] = project_threads.active_thread_name()
                    await send_thread_map_widget(ws, project_threads, session_state)
                    await _complete_immediate_turn(
                        brief,
                        suggested_actions=[
                            {"label": "Save this update", "command": f"save this as part of {project_threads.active_thread_name()}"},
                            {"label": "Save thread memory", "command": f"memory save thread {project_threads.active_thread_name()}"},
                            {"label": "List thread memory", "command": f"memory list thread {project_threads.active_thread_name()}"},
                            {"label": "Show threads", "command": "show threads"},
                        ],
                    )
                else:
                    if not project_threads.has_threads() and decision.intent_family == "followup":
                        pass
                    else:
                        await _complete_immediate_turn(brief, remember_response=False)
                        continue
                if found:
                    continue

            status_thread_match = PROJECT_STATUS_RE.match(text)
            if status_thread_match:
                requested_name = str(status_thread_match.group("name") or "").strip()
                thread_name = requested_name
                if _canonical_thread_reference(requested_name) in {"this", "it", "thread", "project"}:
                    thread_name = project_threads.active_thread_name() or str(session_state.get("project_thread_active") or "").strip()
                    if not thread_name:
                        await send_chat_message(
                            ws,
                            "I do not have an active project thread yet. Try 'show threads' or 'create thread <name>'.",
                            suggested_actions=[
                                {"label": "Show threads", "command": "show threads"},
                                {"label": "Create thread", "command": "create thread current project"},
                            ],
                        )
                        await send_chat_done(ws)
                        continue
                found, status_text = project_threads.render_status(thread_name)
                if found:
                    session_state["project_thread_active"] = project_threads.active_thread_name()
                    await send_thread_map_widget(ws, project_threads, session_state)
                    active = project_threads.active_thread_name()
                    await send_chat_message(
                        ws,
                        status_text,
                        suggested_actions=[
                            {"label": "Thread detail", "command": f"thread detail {active}"},
                            {"label": "Biggest blocker", "command": f"biggest blocker in {active}"},
                            {"label": "Save thread memory", "command": f"memory save thread {active}"},
                            {"label": "List thread memory", "command": f"memory list thread {active}"},
                            {"label": "Continue thread", "command": f"continue my {active}"},
                            {"label": "Show threads", "command": "show threads"},
                        ],
                    )
                    await send_chat_done(ws)
                    continue
                if not project_threads.has_threads() and decision.intent_family == "followup":
                    pass
                else:
                    await send_chat_message(ws, status_text)
                    await send_chat_done(ws)
                    continue

            blocker_thread_match = BIGGEST_BLOCKER_RE.match(text)
            if blocker_thread_match:
                thread_name = str(blocker_thread_match.group("name") or "").strip()
                if not thread_name or _canonical_thread_reference(thread_name) in {"this", "it", "thread", "project"}:
                    thread_name = project_threads.active_thread_name() or str(session_state.get("project_thread_active") or "").strip()
                found, blocker_text = project_threads.render_biggest_blocker(thread_name)
                if found:
                    session_state["project_thread_active"] = project_threads.active_thread_name()
                    await send_thread_map_widget(ws, project_threads, session_state)
                    active = project_threads.active_thread_name()
                    await send_chat_message(
                        ws,
                        blocker_text,
                        suggested_actions=[
                            {"label": "Thread detail", "command": f"thread detail {active}"},
                            {"label": "Project status", "command": f"project status {active}"},
                            {"label": "Save this update", "command": f"save this as part of {active}"},
                            {"label": "Save decision memory", "command": f"memory save decision for {active}: "},
                            {"label": "Save thread memory", "command": f"memory save thread {active}"},
                            {"label": "Show threads", "command": "show threads"},
                        ],
                    )
                    await send_chat_done(ws)
                    continue
                if not project_threads.has_threads() and decision.intent_family == "followup":
                    pass
                else:
                    await send_chat_message(ws, blocker_text)
                    await send_chat_done(ws)
                    continue

            detail_thread_match = THREAD_DETAIL_RE.match(text)
            if detail_thread_match:
                thread_name = str(detail_thread_match.group("name") or "").strip()
                if _canonical_thread_reference(thread_name) in {"this", "it", "thread", "project"}:
                    thread_name = project_threads.active_thread_name() or str(session_state.get("project_thread_active") or "").strip()
                detail_widget = await send_thread_detail_widget(
                    ws,
                    session_state,
                    project_threads,
                    thread_name=thread_name,
                )
                if detail_widget is not None:
                    detail = dict(detail_widget.get("thread") or {})
                    if silent_widget_refresh:
                        await _complete_silent_widget_refresh()
                        continue
                    latest_decision = str(detail.get("latest_decision") or "").strip() or "No decision recorded yet."
                    latest_blocker = str(detail.get("latest_blocker") or "").strip() or "No blocker recorded."
                    await send_chat_message(
                        ws,
                        (
                            f"{str(detail.get('name') or 'Thread')} - Detail Snapshot\n\n"
                            f"Latest decision: {latest_decision}\n"
                            f"Latest blocker: {latest_blocker}"
                        ),
                        suggested_actions=[
                            {"label": "Project status", "command": f"project status {str(detail.get('name') or '').strip()}"},
                            {"label": "Biggest blocker", "command": f"biggest blocker in {str(detail.get('name') or '').strip()}"},
                            {"label": "List memory", "command": f"memory list thread {str(detail.get('name') or '').strip()}"},
                            {"label": "Save decision", "command": f"memory save decision for {str(detail.get('name') or '').strip()}: "},
                        ],
                    )
                    await send_chat_done(ws)
                    continue
                if not project_threads.has_threads() and decision.intent_family == "followup":
                    pass
                else:
                    await send_chat_message(ws, "I could not find that project thread yet.")
                    await send_chat_done(ws)
                    continue

            attach_thread_match = ATTACH_THREAD_RE.match(text)
            if ATTACH_ACTIVE_THREAD_RE.match(text):
                active_thread = project_threads.active_thread_name() or str(session_state.get("project_thread_active") or "").strip()
                if not active_thread:
                    await send_chat_message(
                        ws,
                        "I do not have an active thread yet. Say 'create thread <name>' first.",
                    )
                    await send_chat_done(ws)
                    continue
                summary, next_steps, default_category = _build_thread_attachment_summary(
                    session_state=session_state,
                    working_context=working_context,
                )
                attached = project_threads.attach_update(
                    thread_name=active_thread,
                    summary=summary,
                    category=default_category,
                    goal_hint=str(working_context.to_dict().get("task_goal") or "").strip(),
                    next_steps=next_steps,
                )
                session_state["project_thread_active"] = attached.name
                await send_thread_map_widget(ws, project_threads, session_state)
                await send_chat_message(
                    ws,
                    f"Saved to active thread {attached.name}: {summary}",
                )
                await send_chat_done(ws)
                continue

            if attach_thread_match:
                thread_name = str(attach_thread_match.group("name") or "").strip()
                summary, next_steps, default_category = _build_thread_attachment_summary(
                    session_state=session_state,
                    working_context=working_context,
                )
                attached = project_threads.attach_update(
                    thread_name=thread_name,
                    summary=summary,
                    category=default_category,
                    goal_hint=str(working_context.to_dict().get("task_goal") or "").strip(),
                    next_steps=next_steps,
                )
                session_state["project_thread_active"] = attached.name
                await send_thread_map_widget(ws, project_threads, session_state)
                await send_chat_message(
                    ws,
                    (
                        f"Saved to thread: {attached.name}.\n"
                        f"Update: {summary}"
                    ),
                )
                await send_chat_done(ws)
                continue

            decision_thread_match = DECISION_THREAD_RE.match(text)
            if decision_thread_match:
                decision_text = str(decision_thread_match.group("decision") or "").strip()
                thread_name = str(decision_thread_match.group("name") or "").strip()
                attached = project_threads.add_decision(thread_name=thread_name, decision=decision_text)
                session_state["project_thread_active"] = attached.name
                await send_thread_map_widget(ws, project_threads, session_state)
                await send_chat_message(
                    ws,
                    f"Decision recorded in {attached.name}: {decision_text}",
                )
                await send_chat_done(ws)
                continue

            if not decision.blocked_by_policy and not decision.needs_clarification:
                _remember_topic(
                    session_state,
                    text,
                    decision.intent_family,
                    session_state["turn_count"],
                )

            if lowered in {
                "deep mode",
                "deep analysis",
                "deep thought",
                "deep think",
                "go deeper",
                "think deeper",
                "challenge this",
                "pressure test this",
            }:
                session_state["deep_mode_armed"] = True
                session_state["deep_mode_last_armed_turn"] = session_state.get("turn_count", 0)
                await send_chat_message(
                    ws,
                    "Deep analysis is armed for your next request. Ask your question when ready.",
                )
                await send_chat_done(ws)
                continue

            if lowered in {"stop deep mode", "cancel deep mode", "reset deep mode"}:
                session_state["deep_mode_armed"] = False
                session_state["pending_escalation"] = None
                await send_chat_message(ws, "Deep analysis canceled.")
                await send_chat_done(ws)
                continue

            pending_web_open = session_state.get("pending_web_open")
            pending_governed_confirm = session_state.get("pending_governed_confirm")
            if pending_governed_confirm:
                confirm_decision = SessionRouter.route_pending_web_confirmation(lowered)
                if confirm_decision.action == "confirm":
                    capability_id = int(pending_governed_confirm.get("capability_id") or 0)
                    params = dict(pending_governed_confirm.get("params") or {})
                    params["confirmed"] = True
                    params.setdefault("session_id", session_id)
                    action_result = await invoke_governed_capability(governor, capability_id, params)
                    session_state["pending_governed_confirm"] = None
                    outgoing_message = _structure_long_message(_action_result_message(action_result))
                    if outgoing_message:
                        session_state["last_response"] = outgoing_message
                    await send_chat_message(ws, outgoing_message)
                    await send_chat_done(ws)
                    continue
                if confirm_decision.action == "cancel":
                    session_state["pending_governed_confirm"] = None
                    await send_chat_message(ws, "Cancelled pending action.")
                    await send_chat_done(ws)
                    continue
                await send_chat_message(
                    ws,
                    "I still have a confirmation pending. Reply 'yes' to proceed or 'no' to cancel.",
                )
                await send_chat_done(ws)
                continue

            if pending_web_open:
                web_decision = SessionRouter.route_pending_web_confirmation(lowered)
                if web_decision.action == "confirm":
                    action_result = await invoke_governed_capability(
                        governor,
                        17,
                        {**pending_web_open, "confirmed": True, "session_id": session_id},
                    )
                    session_state["pending_web_open"] = None
                    action_payload = _action_result_payload(action_result)
                    outgoing_message = _structure_long_message(_action_result_message(action_result))
                    if action_result.success and isinstance(action_payload, dict):
                        opened_domain = str(action_payload.get("opened_domain") or "").strip()
                        if opened_domain:
                            session_state["last_sources"] = [opened_domain]
                    await send_chat_message(ws, outgoing_message)
                    await send_chat_done(ws)
                    continue
                if web_decision.action == "cancel":
                    session_state["pending_web_open"] = None
                    await send_chat_message(ws, "Cancelled website open request.")
                    await send_chat_done(ws)
                    continue
                await send_chat_message(
                    ws,
                    "I still have your website open request pending. Reply 'yes' to open or 'no' to cancel.",
                )
                await send_chat_done(ws)
                continue

            if channel == "voice" and msg_type == "chat":
                ack_payload = voice_experience_agent.build_ack_payload(
                    VOICE_ACK_CONFIG,
                    mode=decision.mode.value,
                )
                if ack_payload is not None:
                    await ws_send(ws, ack_payload)

            micro_ack = str(decision.micro_ack or "").strip()
            if micro_ack and not silent_widget_refresh:
                await send_chat_message(ws, micro_ack)

            if lowered in {"open downloads", "open documents"}:
                session_state["last_object"] = lowered.replace("open ", "")

            # --- Escalation handling (fixed: clear pending on all outcomes) ---
            if session_state["pending_escalation"]:
                escalation_outcome = await resolve_pending_escalation_reply(
                    lowered,
                    session_state=session_state,
                    general_chat_skill=general_chat_skill,
                )
                if escalation_outcome.skill_result is not None:
                    forced_result = escalation_outcome.skill_result
                    message_id = None
                    esc = (forced_result.data or {}).get("escalation", {})
                    if esc.get("escalated") and esc.get("thought_data"):
                        message_id = str(uuid.uuid4())
                        thought_store.put(session_id, message_id, esc["thought_data"])
                    await send_chat_message(ws, forced_result.message, message_id=message_id)
                    await send_chat_done(ws)
                    session_context.extend(escalation_outcome.context_entries)
                    context_limit = 40 if session_state.get("presence_mode") else 20
                    session_context = session_context[-context_limit:]
                    if getattr(forced_result, "success", False):
                        session_state["trust_status"] = failure_ladder.record_local_success(
                            session_state.get("trust_status", {})
                        )
                    else:
                        session_state["trust_status"] = failure_ladder.record_failure(
                            session_state.get("trust_status", {}),
                            reason="Temporary issue",
                            external=False,
                        )
                    await send_trust_status(ws, session_state["trust_status"])
                    _maybe_auto_speak_for_voice_turn(session_state, forced_result.message)
                    session_state["turn_count"] += 1
                    continue
                if escalation_outcome.handled:
                    await send_chat_message(ws, escalation_outcome.message)
                    await send_chat_done(ws)
                    continue

            # --- Phaseâ€‘2 immediate commands ---
            if lowered == "stop":
                speech_state.stop()
                stop_speaking()
                await send_chat_message(ws, "Okay.")
                await send_chat_done(ws)
                continue

            if lowered == "repeat":
                last = speech_state.last_spoken_text
                if last:
                    await send_chat_message(
                        ws,
                        f"{NovaStyleContract.spoken_acknowledgement('confirm')}\n\n{last}",
                    )
                else:
                    await send_chat_message(ws, NovaStyleContract.spoken_repeat_prompt())
                await send_chat_done(ws)
                continue

            if lowered in {"thanks", "thank you", "thank you nova", "thank you, nova"}:
                await send_chat_message(ws, "You're welcome.")
                await send_chat_done(ws)
                continue

            if lowered in {"show sources", "show sources for your last response", "sources"}:
                last_sources = list(session_state.get("last_sources") or [])
                if not last_sources:
                    await send_chat_message(
                        ws,
                        "I don't have citation sources for the last response. "
                        "Use a governed web search or news request, then ask for sources.",
                    )
                else:
                    lines = ["Sources for last response:"]
                    lines.extend(f"{i + 1}. {src}" for i, src in enumerate(last_sources))
                    await send_chat_message(ws, "\n".join(lines))
                await send_chat_done(ws)
                continue

            if lowered in {
                "shorter",
                "shorter version",
                "make that shorter",
                "simplify that",
                "summarize your last response",
                "shorter version of your last response",
                "tldr",
                "tl;dr",
            }:
                prior = str(session_state.get("last_response") or "").strip()
                if not prior:
                    await send_chat_message(ws, "I don't have a previous response to shorten yet.")
                else:
                    short = _make_shorter_followup(prior)
                    session_state["last_response"] = short
                    await send_chat_message(ws, short)
                await send_chat_done(ws)
                continue

            if lowered in {
                "confirm model update",
                "confirm model",
                "approve model update",
                "unlock model",
            }:
                try:
                    from src.llm.llm_gateway import (
                        confirm_model_update as confirm_llm_model_update,
                        is_model_update_pending as llm_model_update_pending,
                    )

                    was_pending_update = llm_model_update_pending()
                    did_confirm_update = confirm_llm_model_update()
                except Exception:
                    was_pending_update = False
                    did_confirm_update = False

                if did_confirm_update:
                    await send_chat_message(
                        ws,
                        "Model update confirmed. Local model responses are now unblocked.",
                    )
                elif was_pending_update:
                    await send_chat_message(
                        ws,
                        "Model update confirmation is still pending. Please try again.",
                    )
                else:
                    await send_chat_message(ws, "No model update confirmation is pending.")
                await send_chat_done(ws)
                continue

            if lowered in PHASE42_HELP_COMMANDS:
                await send_chat_message(
                    ws,
                    (
                        "Use 'phase42: <question>' or 'orthogonal analysis: <question>' "
                        "to run the orthogonal agent stack."
                    ),
                )
                await send_chat_done(ws)
                continue

            phase42_query = _extract_phase42_query(text)
            if phase42_query is not None:
                if not PHASE_4_2_ENABLED or personality_agent is None:
                    await send_chat_message(
                        ws,
                        "Phase 4.2 runtime is locked in this build profile.",
                    )
                    await send_chat_done(ws)
                    continue

                if session_state.get("deep_mode_armed"):
                    personality_agent.arm_deep_mode()
                    session_state["deep_mode_armed"] = False
                    session_state["deep_mode_last_armed_turn"] = session_state.get("turn_count", 0)

                context_payload = {
                    "session_id": session_id,
                    "turn_count": session_state.get("turn_count", 0),
                    "last_response": session_state.get("last_response", ""),
                    "last_sources": list(session_state.get("last_sources") or []),
                    "last_mode": session_state.get("last_mode", ""),
                    "last_intent_family": session_state.get("last_intent_family", ""),
                }

                try:
                    phase42_message = await asyncio.to_thread(
                        personality_agent.run,
                        phase42_query,
                        _build_phase42_agents(),
                        context_payload,
                    )
                except RuntimeError:
                    phase42_message = "Phase 4.2 runtime is locked in this build profile."
                except Exception:
                    phase42_message = "Phase 4.2 analysis is currently unavailable."

                session_state["last_response"] = phase42_message
                speech_state.last_spoken_text = phase42_message
                session_state["trust_status"] = failure_ladder.record_local_success(
                    session_state.get("trust_status", {})
                )
                await send_chat_message(ws, phase42_message, apply_personality=False)
                await send_trust_status(ws, session_state["trust_status"])
                await send_chat_done(ws)
                _maybe_auto_speak_for_voice_turn(session_state, phase42_message)

                session_context.extend(
                    [
                        {"role": "user", "content": text},
                        {"role": "assistant", "content": phase42_message},
                    ]
                )
                context_limit = 40 if session_state.get("presence_mode") else 20
                session_context = session_context[-context_limit:]
                session_state["turn_count"] += 1
                continue

            if lowered in {"weather", "weather update", "current weather"}:
                _, weather_result = await invoke_governed_text_command(
                    governor,
                    "weather",
                    session_id,
                )
                if weather_result is None:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "Weather is currently unavailable.", tone_domain="daily")
                    await ws_send(
                        ws,
                        {
                            "type": "weather",
                            "data": {
                                "summary": "Weather is currently unavailable.",
                                "temperature": None,
                                "condition": "Unavailable",
                                "location": "Local",
                                "forecast": "",
                                "alerts": [],
                            },
                        },
                    )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=True,
                        last_external_call="Weather update",
                    )
                    await send_trust_status(ws, session_state["trust_status"])
                    await send_chat_done(ws)
                    continue
                weather_widget = {}
                if isinstance(weather_result.data, dict):
                    weather_widget = dict(weather_result.data.get("widget") or {})

                if weather_result.success:
                    message = _structure_long_message(weather_result.message)
                    if not silent_widget_refresh:
                        session_state["last_response"] = message
                        await send_chat_message(ws, message, tone_domain="daily")
                    if isinstance(weather_widget, dict) and weather_widget.get("type") == "weather":
                        await ws_send(ws, weather_widget)
                    else:
                        await ws_send(
                            ws,
                            {
                                "type": "weather",
                                "data": {
                                    "summary": message,
                                    "temperature": None,
                                    "condition": "",
                                    "location": "Local",
                                    "forecast": "",
                                    "alerts": [],
                                },
                            },
                        )
                    session_state["trust_status"] = failure_ladder.record_external_success(
                        session_state.get("trust_status", {}),
                        "Weather update",
                    )
                else:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "Weather is currently unavailable.", tone_domain="daily")
                    if isinstance(weather_widget, dict) and weather_widget.get("type") == "weather":
                        await ws_send(ws, weather_widget)
                    else:
                        await ws_send(
                            ws,
                            {
                                "type": "weather",
                                "data": {
                                    "summary": "Weather is currently unavailable.",
                                    "temperature": None,
                                    "condition": "Unavailable",
                                    "location": "Local",
                                    "forecast": "",
                                    "alerts": [],
                                },
                            },
                        )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=True,
                        last_external_call="Weather update",
                    )
                await send_trust_status(ws, session_state["trust_status"])
                await send_chat_done(ws)
                continue

            if lowered in {"news", "headlines", "latest news", "top news"}:
                _, news_result = await invoke_governed_text_command(
                    governor,
                    "news",
                    session_id,
                )
                if news_result is None:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "News is currently unavailable.", tone_domain="daily")
                    await ws_send(
                        ws,
                        {
                            "type": "news",
                            "items": [],
                            "summary": "News is currently unavailable.",
                            "categories": {},
                        },
                    )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=True,
                        last_external_call="News update",
                    )
                    await send_trust_status(ws, session_state["trust_status"])
                    await send_chat_done(ws)
                    continue
                news_widget = {}
                if isinstance(news_result.data, dict):
                    news_widget = dict(news_result.data.get("widget") or {})

                if news_result.success:
                    message = _structure_long_message(news_result.message)
                    if not silent_widget_refresh:
                        session_state["last_response"] = message
                        await send_chat_message(ws, message, tone_domain="daily")
                    if isinstance(news_widget, dict) and news_widget.get("type") == "news":
                        items = list(news_widget.get("items") or [])
                        categories = dict(news_widget.get("categories") or {})
                        session_state["news_cache"] = items
                        session_state["news_categories"] = categories
                        session_state["last_sources"] = _extract_sources_from_results(items)
                        session_state["last_source_links"] = _extract_source_links(items)
                        await ws_send(ws, news_widget)
                    else:
                        await ws_send(
                            ws,
                            {
                                "type": "news",
                                "items": [],
                                "summary": "News is currently unavailable.",
                                "categories": {},
                            },
                        )
                    session_state["trust_status"] = failure_ladder.record_external_success(
                        session_state.get("trust_status", {}),
                        "News update",
                    )
                else:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "News is currently unavailable.", tone_domain="daily")
                    if isinstance(news_widget, dict) and news_widget.get("type") == "news":
                        await ws_send(ws, news_widget)
                    else:
                        await ws_send(
                            ws,
                            {
                                "type": "news",
                                "items": [],
                                "summary": "News is currently unavailable.",
                                "categories": {},
                            },
                        )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=True,
                        last_external_call="News update",
                    )
                await send_trust_status(ws, session_state["trust_status"])
                await send_chat_done(ws)
                continue

            if lowered in {
                "calendar",
                "calendar update",
                "agenda",
                "schedule",
                "todays schedule",
                "today's schedule",
                "todays calendar",
                "today's calendar",
            }:
                _, calendar_result = await invoke_governed_text_command(
                    governor,
                    "calendar",
                    session_id,
                )
                if calendar_result is None:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "Calendar is currently unavailable.", tone_domain="daily")
                    await send_widget_message(
                        ws,
                        "calendar",
                        "Calendar is currently unavailable.",
                        {"type": "calendar", "summary": "Unavailable.", "events": []},
                    )
                    await send_chat_done(ws)
                    continue
                calendar_widget = {}
                if isinstance(calendar_result.data, dict):
                    calendar_widget = dict(calendar_result.data.get("widget") or {})
                if calendar_result.success:
                    message = _structure_long_message(calendar_result.message)
                    if not silent_widget_refresh:
                        session_state["last_response"] = message
                        await send_chat_message(ws, message, tone_domain="daily")
                    if isinstance(calendar_widget, dict) and calendar_widget.get("type") == "calendar":
                        await send_widget_message(ws, "calendar", message, calendar_widget)
                        session_state["last_calendar_summary"] = str(calendar_widget.get("summary") or "")
                        session_state["last_calendar_events"] = list(calendar_widget.get("events") or [])
                    else:
                        await send_widget_message(
                            ws,
                            "calendar",
                            message,
                            {"type": "calendar", "summary": message, "events": []},
                        )
                else:
                    if not silent_widget_refresh:
                        await send_chat_message(ws, "Calendar is currently unavailable.", tone_domain="daily")
                    if isinstance(calendar_widget, dict) and calendar_widget.get("type") == "calendar":
                        await send_widget_message(
                            ws,
                            "calendar",
                            "Calendar is currently unavailable.",
                            calendar_widget,
                        )
                    else:
                        await send_widget_message(
                            ws,
                            "calendar",
                            "Calendar is currently unavailable.",
                            {"type": "calendar", "summary": "Unavailable.", "events": []},
                        )
                await send_chat_done(ws)
                continue

            if lowered in {"system", "system status", "system check"}:
                _, action_result = await invoke_governed_text_command(
                    governor,
                    "system status",
                    session_id,
                )
                if action_result is None:
                    failure_message = "System diagnostics are currently unavailable."
                    if not silent_widget_refresh:
                        await send_chat_message(ws, failure_message, tone_domain="system")
                    await ws_send(
                        ws,
                        {
                            "type": "system",
                            "summary": failure_message,
                            "data": {"status": "unavailable"},
                        },
                    )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=False,
                    )
                    await send_trust_status(ws, session_state["trust_status"])
                    await send_chat_done(ws)
                    continue
                if action_result.success:
                    action_message = _action_result_message(action_result)
                    action_payload = _action_result_payload(action_result)
                    message = _structure_long_message(action_message)
                    if not silent_widget_refresh:
                        session_state["last_response"] = message
                        await send_chat_message(ws, message, tone_domain="system")
                    await ws_send(
                        ws,
                        {
                            "type": "system",
                            "summary": message,
                            "data": action_payload,
                        },
                    )
                    session_state["trust_status"] = failure_ladder.record_local_success(
                        session_state.get("trust_status", {})
                    )
                else:
                    failure_message = "System diagnostics are currently unavailable."
                    if not silent_widget_refresh:
                        await send_chat_message(ws, failure_message, tone_domain="system")
                    await ws_send(
                        ws,
                        {
                            "type": "system",
                            "summary": failure_message,
                            "data": {"status": "unavailable"},
                        },
                    )
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=False,
                    )
                await send_trust_status(ws, session_state["trust_status"])
                await send_chat_done(ws)
                continue

            if lowered in TONE_STATUS_COMMANDS:
                snapshot = interface_personality_agent.tone_snapshot()
                _log_ledger_event(
                    governor,
                    "TONE_PROFILE_VIEWED",
                    {
                        "global_profile": str(snapshot.get("global_profile") or "balanced"),
                        "override_count": int(snapshot.get("override_count") or 0),
                    },
                )
                if not silent_widget_refresh:
                    await send_chat_message(
                        ws,
                        _render_tone_profile_message(snapshot),
                        tone_domain="system",
                    )
                await send_tone_profile_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            tone_set_match = TONE_SET_RE.match(text)
            if tone_set_match:
                domain, profile, ok = _parse_tone_set_body(tone_set_match.group("body"))
                if not ok:
                    await send_chat_message(
                        ws,
                        "I couldn't parse that tone setting yet.\n\nTry next:\n- tone set concise\n- tone set research detailed\n- tone set system formal",
                        tone_domain="system",
                    )
                    await send_chat_done(ws)
                    continue

                if domain == "global":
                    snapshot = interface_personality_agent.set_global_tone(profile)
                    message = f"Global tone set to {profile}."
                else:
                    snapshot = interface_personality_agent.set_domain_tone(domain, profile)
                    label = ToneProfileStore.DOMAIN_DEFINITIONS.get(domain, domain.title())
                    message = f"{label} tone set to {profile}."

                _log_ledger_event(
                    governor,
                    "TONE_PROFILE_UPDATED",
                    {
                        "domain": domain,
                        "profile": profile,
                        "global_profile": str(snapshot.get("global_profile") or "balanced"),
                        "override_count": int(snapshot.get("override_count") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    f"{message}\n\n{str(snapshot.get('summary') or '').strip()}",
                    tone_domain="system",
                )
                await send_tone_profile_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            tone_reset_match = TONE_RESET_RE.match(text)
            if tone_reset_match:
                body = str(tone_reset_match.group("body") or "").strip().lower()
                body = re.sub(r"^(?:domain|for)\s+", "", body).strip()
                body = body.rstrip(".?!").strip()
                if not body or body == "all":
                    snapshot = interface_personality_agent.reset_all_tone()
                    message = "Tone settings reset to the default profile."
                    reset_domain = "all"
                else:
                    if body not in ToneProfileStore.DOMAIN_DEFINITIONS:
                        await send_chat_message(
                            ws,
                            "I couldn't find that tone domain yet.\n\nTry next:\n- tone reset research\n- tone reset system\n- tone reset all",
                            tone_domain="system",
                        )
                        await send_chat_done(ws)
                        continue
                    snapshot = interface_personality_agent.reset_domain_tone(body)
                    label = ToneProfileStore.DOMAIN_DEFINITIONS.get(body, body.title())
                    message = f"{label} tone reset to the global profile."
                    reset_domain = body

                _log_ledger_event(
                    governor,
                    "TONE_PROFILE_RESET",
                    {
                        "domain": reset_domain,
                        "global_profile": str(snapshot.get("global_profile") or "balanced"),
                        "override_count": int(snapshot.get("override_count") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    f"{message}\n\n{str(snapshot.get('summary') or '').strip()}",
                    tone_domain="system",
                )
                await send_tone_profile_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if lowered in SHOW_SCHEDULES_COMMANDS:
                snapshot = notification_schedules.summarize()
                if silent_widget_refresh:
                    snapshot = _process_due_notification_delivery(governor, notification_schedules, snapshot)
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_VIEWED",
                    {
                        "active_count": int(snapshot.get("active_count") or 0),
                        "due_count": int(snapshot.get("due_count") or 0),
                    },
                )
                if not silent_widget_refresh:
                    await send_chat_message(
                        ws,
                        _render_notification_schedule_message(snapshot),
                        tone_domain="system",
                    )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if lowered in NOTIFICATION_SETTINGS_COMMANDS:
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_VIEWED",
                    {
                        "active_count": int(snapshot.get("active_count") or 0),
                        "due_count": int(snapshot.get("due_count") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    _render_notification_settings_message(snapshot),
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            set_quiet_hours_match = SET_QUIET_HOURS_RE.match(text)
            if set_quiet_hours_match:
                try:
                    start_hour, start_minute = _parse_clock_time(set_quiet_hours_match.group("start"))
                    end_hour, end_minute = _parse_clock_time(set_quiet_hours_match.group("end"))
                except ValueError as exc:
                    await send_chat_message(ws, str(exc), tone_domain="system")
                    await send_chat_done(ws)
                    continue
                policy = notification_schedules.update_policy(
                    quiet_hours_enabled=True,
                    quiet_hours_start=f"{start_hour:02d}:{start_minute:02d}",
                    quiet_hours_end=f"{end_hour:02d}:{end_minute:02d}",
                )
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_POLICY_UPDATED",
                    {
                        "quiet_hours_enabled": True,
                        "quiet_hours_start": str(policy.get("quiet_hours_start") or ""),
                        "quiet_hours_end": str(policy.get("quiet_hours_end") or ""),
                        "max_deliveries_per_hour": int(policy.get("max_deliveries_per_hour") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    (
                        "Quiet hours updated.\n"
                        f"Window: {_format_policy_clock_value(str(policy.get('quiet_hours_start') or ''))} to "
                        f"{_format_policy_clock_value(str(policy.get('quiet_hours_end') or ''))}\n\n"
                        f"{_render_notification_settings_message(snapshot)}"
                    ),
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if CLEAR_QUIET_HOURS_RE.match(text):
                policy = notification_schedules.update_policy(quiet_hours_enabled=False)
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_POLICY_UPDATED",
                    {
                        "quiet_hours_enabled": False,
                        "quiet_hours_start": str(policy.get("quiet_hours_start") or ""),
                        "quiet_hours_end": str(policy.get("quiet_hours_end") or ""),
                        "max_deliveries_per_hour": int(policy.get("max_deliveries_per_hour") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    f"Quiet hours cleared.\n\n{_render_notification_settings_message(snapshot)}",
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            set_rate_limit_match = SET_NOTIFICATION_RATE_LIMIT_RE.match(text)
            if set_rate_limit_match:
                rate_limit = max(1, min(int(set_rate_limit_match.group("count") or 1), 12))
                policy = notification_schedules.update_policy(max_deliveries_per_hour=rate_limit)
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_POLICY_UPDATED",
                    {
                        "quiet_hours_enabled": bool(policy.get("quiet_hours_enabled")),
                        "quiet_hours_start": str(policy.get("quiet_hours_start") or ""),
                        "quiet_hours_end": str(policy.get("quiet_hours_end") or ""),
                        "max_deliveries_per_hour": int(policy.get("max_deliveries_per_hour") or 0),
                    },
                )
                await send_chat_message(
                    ws,
                    f"Notification rate limit updated to {rate_limit} per hour.\n\n{_render_notification_settings_message(snapshot)}",
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            schedule_brief_match = SCHEDULE_BRIEF_RE.match(text)
            if schedule_brief_match:
                try:
                    scheduled_for = _parse_schedule_datetime(
                        schedule_brief_match.group("time"),
                        recurrence="daily",
                    )
                except ValueError as exc:
                    await send_chat_message(ws, str(exc), tone_domain="system")
                    await send_chat_done(ws)
                    continue
                item = notification_schedules.create_schedule(
                    kind="daily_brief",
                    title="Daily brief",
                    body="Run your scheduled daily brief.",
                    recurrence="daily",
                    next_run_at=scheduled_for,
                    command="morning brief",
                )
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_CREATED",
                    {
                        "schedule_id": item["id"],
                        "kind": item["kind"],
                        "recurrence": item["recurrence"],
                    },
                )
                await send_chat_message(
                    ws,
                    (
                        f"Daily brief scheduled: {item['id']}\n"
                        f"Next run: {_format_local_schedule_time(scheduled_for)}\n\n"
                        f"{str(snapshot.get('summary') or '').strip()}"
                    ),
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            remind_me_match = REMIND_ME_RE.match(text)
            if remind_me_match:
                recurrence = "daily" if remind_me_match.group("daily") else "once"
                try:
                    scheduled_for = _parse_schedule_datetime(
                        remind_me_match.group("time"),
                        recurrence=recurrence,
                    )
                except ValueError as exc:
                    await send_chat_message(ws, str(exc), tone_domain="system")
                    await send_chat_done(ws)
                    continue
                reminder_body = str(remind_me_match.group("body") or "").strip()
                item = notification_schedules.create_schedule(
                    kind="reminder",
                    title=f"Reminder: {reminder_body[:80]}",
                    body=reminder_body,
                    recurrence=recurrence,
                    next_run_at=scheduled_for,
                )
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_CREATED",
                    {
                        "schedule_id": item["id"],
                        "kind": item["kind"],
                        "recurrence": item["recurrence"],
                    },
                )
                await send_chat_message(
                    ws,
                    (
                        f"Reminder scheduled: {item['id']}\n"
                        f"Text: {reminder_body}\n"
                        f"Next run: {_format_local_schedule_time(scheduled_for)}\n\n"
                        f"{str(snapshot.get('summary') or '').strip()}"
                    ),
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            reschedule_schedule_match = RESCHEDULE_SCHEDULE_RE.match(text)
            if reschedule_schedule_match:
                schedule_id = str(reschedule_schedule_match.group("schedule_id") or "").strip().upper()
                existing = notification_schedules.get_schedule(schedule_id)
                if existing is None:
                    await send_chat_message(ws, "I could not find that schedule ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                recurrence = str(existing.get("recurrence") or "once").strip().lower() or "once"
                try:
                    scheduled_for = _parse_schedule_datetime(
                        reschedule_schedule_match.group("time"),
                        recurrence=recurrence,
                    )
                except ValueError as exc:
                    await send_chat_message(ws, str(exc), tone_domain="system")
                    await send_chat_done(ws)
                    continue
                item = notification_schedules.reschedule_schedule(schedule_id, next_run_at=scheduled_for)
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_UPDATED",
                    {
                        "schedule_id": schedule_id,
                        "kind": str(item.get("kind") or ""),
                        "recurrence": str(item.get("recurrence") or ""),
                    },
                )
                await send_chat_message(
                    ws,
                    (
                        f"Schedule updated: {schedule_id}\n"
                        f"Next run: {_format_local_schedule_time(scheduled_for)}\n\n"
                        f"{str(snapshot.get('summary') or '').strip()}"
                    ),
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            cancel_schedule_match = CANCEL_SCHEDULE_RE.match(text)
            if cancel_schedule_match:
                schedule_id = str(cancel_schedule_match.group("schedule_id") or "").strip().upper()
                try:
                    item = notification_schedules.cancel_schedule(schedule_id)
                except KeyError:
                    await send_chat_message(ws, "I could not find that schedule ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_CANCELLED",
                    {"schedule_id": schedule_id, "kind": str(item.get("kind") or "")},
                )
                await send_chat_message(
                    ws,
                    f"Schedule cancelled: {schedule_id}\n\n{str(snapshot.get('summary') or '').strip()}",
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            dismiss_schedule_match = DISMISS_SCHEDULE_RE.match(text)
            if dismiss_schedule_match:
                schedule_id = str(dismiss_schedule_match.group("schedule_id") or "").strip().upper()
                try:
                    item = notification_schedules.dismiss_schedule(schedule_id)
                except KeyError:
                    await send_chat_message(ws, "I could not find that schedule ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                snapshot = notification_schedules.summarize()
                _log_ledger_event(
                    governor,
                    "NOTIFICATION_SCHEDULE_DISMISSED",
                    {"schedule_id": schedule_id, "kind": str(item.get("kind") or "")},
                )
                if bool(item.get("active")):
                    _log_ledger_event(
                        governor,
                        "NOTIFICATION_SCHEDULE_UPDATED",
                        {
                            "schedule_id": schedule_id,
                            "kind": str(item.get("kind") or ""),
                            "recurrence": str(item.get("recurrence") or ""),
                        },
                    )
                await send_chat_message(
                    ws,
                    f"Schedule dismissed: {schedule_id}\n\n{str(snapshot.get('summary') or '').strip()}",
                    tone_domain="system",
                )
                await send_notification_schedule_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if PATTERN_OPT_IN_RE.match(text):
                snapshot = pattern_reviews.set_opt_in(True)
                _log_ledger_event(
                    governor,
                    "PATTERN_DETECTION_OPTED_IN",
                    {"active_count": int(snapshot.get("active_count") or 0)},
                )
                await send_chat_message(
                    ws,
                    (
                        "Pattern review enabled.\n\n"
                        "Nova will only generate pattern proposals when you explicitly ask for them.\n"
                        "Try next:\n"
                        "- review patterns\n"
                        "- review patterns for deployment issue\n"
                        "- pattern status"
                    ),
                    tone_domain="system",
                )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if PATTERN_OPT_OUT_RE.match(text):
                snapshot = pattern_reviews.set_opt_in(False)
                _log_ledger_event(
                    governor,
                    "PATTERN_DETECTION_OPTED_OUT",
                    {"active_count": int(snapshot.get("active_count") or 0)},
                )
                await send_chat_message(
                    ws,
                    "Pattern review disabled. Existing queued proposals have been cleared.",
                    tone_domain="system",
                )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if lowered in PATTERN_STATUS_COMMANDS:
                snapshot = pattern_reviews.snapshot()
                _log_ledger_event(
                    governor,
                    "PATTERN_REVIEW_VIEWED",
                    {
                        "opt_in_enabled": bool(snapshot.get("opt_in_enabled")),
                        "active_count": int(snapshot.get("active_count") or 0),
                    },
                )
                if not silent_widget_refresh:
                    await send_chat_message(
                        ws,
                        _render_pattern_review_message(snapshot),
                        tone_domain="system",
                    )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            pattern_review_match = PATTERN_REVIEW_RE.match(text)
            if pattern_review_match:
                snapshot = pattern_reviews.snapshot()
                if not bool(snapshot.get("opt_in_enabled")):
                    await send_chat_message(
                        ws,
                        "Pattern review is off right now. Say 'pattern opt in' first if you want Nova to generate advisory pattern proposals.",
                        tone_domain="system",
                    )
                    await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                    await send_chat_done(ws)
                    continue

                requested_thread = str(pattern_review_match.group("name") or "").strip()
                resolved_thread_name = ""
                if requested_thread:
                    found, resolved_name, _ = project_threads.resolve_thread_identity(requested_thread)
                    resolved_thread_name = resolved_name if found else requested_thread

                from src.memory.governed_memory_store import GovernedMemoryStore

                thread_summaries = project_threads.list_summaries()
                memory_insights = GovernedMemoryStore().summarize_thread_insights()
                snapshot = pattern_reviews.generate_review(
                    thread_summaries=thread_summaries,
                    memory_insights=memory_insights,
                    thread_name=resolved_thread_name,
                )
                _log_ledger_event(
                    governor,
                    "PATTERN_REVIEW_GENERATED",
                    {
                        "active_count": int(snapshot.get("active_count") or 0),
                        "thread_name": resolved_thread_name,
                    },
                )
                await send_chat_message(
                    ws,
                    _render_pattern_review_message(snapshot),
                    tone_domain="continuity",
                )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            accept_pattern_match = ACCEPT_PATTERN_RE.match(text)
            if accept_pattern_match:
                pattern_id = str(accept_pattern_match.group("pattern_id") or "").strip().upper()
                try:
                    snapshot, proposal = pattern_reviews.accept_proposal(pattern_id)
                except KeyError:
                    await send_chat_message(ws, "I could not find that pattern ID in the current review queue.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                _log_ledger_event(
                    governor,
                    "PATTERN_PROPOSAL_ACCEPTED",
                    {"pattern_id": pattern_id, "kind": str(proposal.get("kind") or "")},
                )
                suggested_commands = [
                    {"label": command.title(), "command": command}
                    for command in list(proposal.get("suggested_commands") or [])[:3]
                ]
                await send_chat_message(
                    ws,
                    (
                        f"Pattern accepted for review: {str(proposal.get('title') or '').strip()}\n\n"
                        "No action has been taken automatically. Use an explicit command if you want to act on this proposal."
                    ),
                    tone_domain="continuity",
                    suggested_actions=suggested_commands or None,
                )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            dismiss_pattern_match = DISMISS_PATTERN_RE.match(text)
            if dismiss_pattern_match:
                pattern_id = str(dismiss_pattern_match.group("pattern_id") or "").strip().upper()
                try:
                    snapshot, proposal = pattern_reviews.dismiss_proposal(pattern_id)
                except KeyError:
                    await send_chat_message(ws, "I could not find that pattern ID in the current review queue.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                _log_ledger_event(
                    governor,
                    "PATTERN_PROPOSAL_DISMISSED",
                    {"pattern_id": pattern_id, "kind": str(proposal.get("kind") or "")},
                )
                await send_chat_message(
                    ws,
                    f"Pattern dismissed: {str(proposal.get('title') or '').strip()}",
                    tone_domain="continuity",
                )
                await send_pattern_review_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if lowered in POLICY_STATUS_COMMANDS:
                snapshot = policy_drafts.overview()
                snapshot["policy_capability_readiness"] = _build_policy_capability_readiness_snapshot()
                _log_ledger_event(
                    governor,
                    "POLICY_DRAFT_VIEWED",
                    {"active_count": int(snapshot.get("active_count") or 0)},
                )
                if not silent_widget_refresh:
                    await send_chat_message(
                        ws,
                        _render_policy_overview_message(snapshot),
                        tone_domain="system",
                    )
                await send_policy_overview_widget(ws, session_state, snapshot=snapshot)
                await send_chat_done(ws)
                continue

            if lowered in POLICY_CAPABILITY_MAP_COMMANDS:
                readiness_snapshot = _build_policy_capability_readiness_snapshot()
                _log_ledger_event(
                    governor,
                    "POLICY_CAPABILITY_MAP_VIEWED",
                    {
                        "safe_now_count": len(list(readiness_snapshot.get("safe_now") or [])),
                        "allowed_later_count": len(list(readiness_snapshot.get("allowed_later") or [])),
                    },
                )
                message, suggestions = _render_policy_capability_map_message(readiness_snapshot)
                if not silent_widget_refresh:
                    await send_chat_message(
                        ws,
                        message,
                        tone_domain="system",
                        suggested_actions=suggestions,
                    )
                await send_trust_status(ws, session_state.get("trust_status", {}))
                await send_policy_overview_widget(
                    ws,
                    session_state,
                    snapshot={
                        **policy_drafts.overview(),
                        "policy_capability_readiness": readiness_snapshot,
                    },
                )
                await send_chat_done(ws)
                continue

            policy_create_match = POLICY_CREATE_RE.match(command_text)
            if policy_create_match:
                try:
                    compiled_policy = _compile_atomic_policy_template(
                        policy_create_match.group("schedule"),
                        policy_create_match.group("action"),
                        policy_create_match.group("time"),
                    )
                except ValueError as exc:
                    await send_chat_message(ws, str(exc), tone_domain="system")
                    await send_chat_done(ws)
                    continue

                validation = governor.validate_atomic_policy(compiled_policy)
                _log_ledger_event(
                    governor,
                    "POLICY_VALIDATED",
                    {
                        "valid": bool(validation.valid),
                        "capability_id": int(dict(compiled_policy.get("action") or {}).get("capability_id") or 0),
                        "trigger_type": str(dict(compiled_policy.get("trigger") or {}).get("type") or ""),
                    },
                )
                if not validation.valid:
                    _log_ledger_event(
                        governor,
                        "POLICY_VALIDATION_REJECTED",
                        {
                            "reason_count": len(list(validation.reasons or [])),
                            "capability_id": int(dict(compiled_policy.get("action") or {}).get("capability_id") or 0),
                        },
                    )
                    rejection_lines = ["Policy draft rejected", ""]
                    rejection_lines.extend(f"- {str(reason).strip()}" for reason in list(validation.reasons or []) if str(reason).strip())
                    rejection_lines.extend(
                        [
                            "",
                            "Try next:",
                            "- policy create weekday calendar snapshot at 8:00 am",
                            "- policy create daily weather snapshot at 7:30 am",
                        ]
                    )
                    await send_chat_message(ws, "\n".join(rejection_lines), tone_domain="system")
                    await send_chat_done(ws)
                    continue

                item = policy_drafts.create_draft(policy=compiled_policy, validation_result=validation)
                _log_ledger_event(
                    governor,
                    "POLICY_DRAFT_CREATED",
                    {
                        "policy_id": str(item.get("policy_id") or ""),
                        "capability_id": int(dict(item.get("action") or {}).get("capability_id") or 0),
                        "trigger_type": str(dict(item.get("trigger") or {}).get("type") or ""),
                    },
                )
                await send_chat_message(
                    ws,
                    (
                        f"Policy draft created: {str(item.get('policy_id') or '').strip()}\n"
                        f"Trigger: {_describe_policy_trigger(item.get('trigger'))}\n"
                        f"Action: {_describe_policy_action(item.get('action'))}\n"
                        "State: draft (disabled)\n\n"
                        "This slice stores and validates draft policies. You can now simulate them and manually review-run safe ones once, but trigger execution is not active yet.\n\n"
                        f"{str(policy_drafts.overview().get('summary') or '').strip()}"
                    ),
                    tone_domain="system",
                )
                await send_policy_overview_widget(ws, session_state, snapshot=policy_drafts.overview())
                await send_policy_item_widget(ws, session_state, item=item)
                await send_chat_done(ws)
                continue

            policy_show_match = POLICY_SHOW_RE.match(command_text)
            if policy_show_match:
                policy_id = str(policy_show_match.group("policy_id") or "").strip().upper()
                item = policy_drafts.get_policy(policy_id)
                if item is None or str(item.get("state") or "") == "deleted":
                    await send_chat_message(ws, "I could not find that policy draft ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                _log_ledger_event(
                    governor,
                    "POLICY_DRAFT_VIEWED",
                    {"policy_id": policy_id, "state": str(item.get("state") or "draft")},
                )
                await send_chat_message(
                    ws,
                    _render_policy_detail_message(item),
                    tone_domain="system",
                )
                await send_policy_item_widget(ws, session_state, item=item)
                await send_chat_done(ws)
                continue

            policy_simulate_match = POLICY_SIMULATE_RE.match(command_text)
            if policy_simulate_match:
                policy_id = str(policy_simulate_match.group("policy_id") or "").strip().upper()
                item = policy_drafts.get_policy(policy_id)
                if item is None or str(item.get("state") or "") == "deleted":
                    await send_chat_message(ws, "I could not find that policy draft ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue

                decision = governor.simulate_atomic_policy(item)
                item = policy_drafts.record_simulation(policy_id, decision.as_dict())
                await send_chat_message(
                    ws,
                    _render_policy_simulation_message(decision.as_dict()),
                    tone_domain="system",
                )
                await send_policy_item_widget(ws, session_state, item=item)
                await send_policy_simulation_widget(ws, session_state, decision=decision.as_dict())
                await send_policy_overview_widget(ws, session_state, snapshot=policy_drafts.overview())
                await send_chat_done(ws)
                continue

            policy_run_match = POLICY_RUN_ONCE_RE.match(command_text)
            if policy_run_match:
                policy_id = str(policy_run_match.group("policy_id") or "").strip().upper()
                if not str(policy_run_match.group("once") or "").strip():
                    await send_chat_message(
                        ws,
                        f"Manual delegated review runs need explicit confirmation.\n\nTry next:\n- policy run {policy_id} once",
                        tone_domain="system",
                    )
                    await send_chat_done(ws)
                    continue

                item = policy_drafts.get_policy(policy_id)
                if item is None or str(item.get("state") or "") == "deleted":
                    await send_chat_message(ws, "I could not find that policy draft ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue

                decision, policy_result = governor.run_atomic_policy_once(item)
                policy_payload = _action_result_payload(policy_result)
                item = policy_drafts.record_manual_run(
                    policy_id,
                    decision.as_dict(),
                    {
                        "success": bool(policy_result.success),
                        "message": _action_result_message(policy_result),
                        "request_id": str(policy_result.request_id or "").strip(),
                        "authority_class": str(policy_result.authority_class or "read_only").strip(),
                        "external_effect": bool(policy_result.external_effect),
                        "reversible": bool(policy_result.reversible),
                    },
                )
                await send_chat_message(
                    ws,
                    _render_policy_run_message(decision.as_dict(), policy_result),
                    tone_domain="system",
                )
                await send_policy_item_widget(ws, session_state, item=item)
                await send_policy_run_widget(
                    ws,
                    session_state,
                    decision=decision.as_dict(),
                    action_result=policy_result,
                )
                await send_policy_overview_widget(ws, session_state, snapshot=policy_drafts.overview())

                if (
                    isinstance(policy_payload, dict)
                    and "widget" in policy_payload
                    and policy_result.success
                ):
                    await ws_send(ws, policy_payload["widget"])
                elif int(dict(item.get("action") or {}).get("capability_id") or 0) == 32 and policy_result.success:
                    if isinstance(policy_payload, dict):
                        await ws_send(ws, {"type": "system", "data": policy_payload, "summary": _action_result_message(policy_result)})

                await send_chat_done(ws)
                continue

            policy_delete_match = POLICY_DELETE_RE.match(command_text)
            if policy_delete_match:
                policy_id = str(policy_delete_match.group("policy_id") or "").strip().upper()
                confirmed = bool(str(policy_delete_match.group("confirm") or "").strip())
                if not confirmed:
                    await send_chat_message(
                        ws,
                        f"Deleting a policy draft needs confirmation.\n\nTry next:\n- policy delete {policy_id} confirm",
                        tone_domain="system",
                    )
                    await send_chat_done(ws)
                    continue
                try:
                    item = policy_drafts.delete_policy(policy_id)
                except KeyError:
                    await send_chat_message(ws, "I could not find that policy draft ID yet.", tone_domain="system")
                    await send_chat_done(ws)
                    continue
                _log_ledger_event(
                    governor,
                    "POLICY_DRAFT_DELETED",
                    {"policy_id": policy_id, "state": str(item.get("state") or "deleted")},
                )
                await send_chat_message(
                    ws,
                    f"Policy draft deleted: {policy_id}\n\n{str(policy_drafts.overview().get('summary') or '').strip()}",
                    tone_domain="system",
                )
                await send_policy_overview_widget(ws, session_state, snapshot=policy_drafts.overview())
                await send_chat_done(ws)
                continue

            if lowered in {"morning", "morning brief", "brief"}:
                weather_summary = "Weather unavailable."
                news_summary = "No headline summary available right now."
                system_line = "System status unavailable."
                calendar_line = "Calendar unavailable."

                _, weather_result = await invoke_governed_text_command(
                    governor,
                    "weather",
                    session_id,
                )
                if weather_result is not None and weather_result.success:
                    weather_summary = weather_result.message
                    if isinstance(weather_result.data, dict):
                        widget = weather_result.data.get("widget")
                        if isinstance(widget, dict):
                            await ws_send(ws, widget)
                    session_state["trust_status"] = failure_ladder.record_external_success(
                        session_state.get("trust_status", {}),
                        "Weather update",
                    )
                    await send_trust_status(ws, session_state["trust_status"])

                _, news_result = await invoke_governed_text_command(
                    governor,
                    "news",
                    session_id,
                )
                if news_result is not None and news_result.success and isinstance(news_result.data, dict):
                    news_widget = news_result.data.get("widget")
                    if isinstance(news_widget, dict):
                        news_summary = str(news_widget.get("summary") or news_summary)
                        items = list(news_widget.get("items") or [])
                        session_state["news_cache"] = items
                        session_state["news_categories"] = dict(news_widget.get("categories") or {})
                        session_state["last_sources"] = _extract_sources_from_results(items)
                        session_state["last_source_links"] = _extract_source_links(items)
                        await ws_send(ws, news_widget)
                    session_state["trust_status"] = failure_ladder.record_external_success(
                        session_state.get("trust_status", {}),
                        "News update",
                    )
                    await send_trust_status(ws, session_state["trust_status"])

                _, system_result = await invoke_governed_text_command(
                    governor,
                    "system status",
                    session_id,
                )
                if system_result is not None and system_result.success:
                    system_line = system_result.message
                    if isinstance(system_result.data, dict):
                        await ws_send(
                            ws,
                            {
                                "type": "system",
                                "summary": system_line,
                                "data": dict(system_result.data),
                            },
                        )
                    session_state["trust_status"] = failure_ladder.record_local_success(
                        session_state.get("trust_status", {})
                    )
                    await send_trust_status(ws, session_state["trust_status"])
                else:
                    session_state["trust_status"] = failure_ladder.record_failure(
                        session_state.get("trust_status", {}),
                        reason="Temporary issue",
                        external=False,
                    )
                    await send_trust_status(ws, session_state["trust_status"])

                _, calendar_result = await invoke_governed_text_command(
                    governor,
                    "calendar",
                    session_id,
                )
                if calendar_result is not None and calendar_result.success and isinstance(calendar_result.data, dict):
                    calendar_widget = calendar_result.data.get("widget")
                    if isinstance(calendar_widget, dict):
                        calendar_line = str(
                            calendar_widget.get("summary")
                            or calendar_result.message
                            or calendar_line
                        )
                        session_state["last_calendar_summary"] = calendar_line
                        session_state["last_calendar_events"] = list(calendar_widget.get("events") or [])
                        await send_widget_message(
                            ws,
                            "calendar",
                            calendar_result.message,
                            calendar_widget,
                        )
                    else:
                        calendar_line = calendar_result.message

                morning_brief = (
                    "Executive Brief\n"
                    f"- Weather: {weather_summary}\n"
                    f"- System: {system_line}\n"
                    f"- News: {news_summary}\n"
                    f"- Calendar: {calendar_line}"
                )
                await send_chat_message(ws, morning_brief, tone_domain="daily")
                await send_chat_done(ws)
                continue

            # --- Manual Session Presence Mode Controls (Tier-B explicit only) ---
            if lowered in {"stay in conversation mode", "conversation mode on", "enable conversation mode"}:
                session_state["presence_mode"] = True
                await send_chat_message(ws, "Conversation mode enabled for this session.")
                await send_chat_done(ws)
                continue

            if lowered in {"conversation mode off", "disable conversation mode", "exit conversation mode"}:
                session_state["presence_mode"] = False
                await send_chat_message(ws, "Conversation mode disabled for this session.")
                await send_chat_done(ws)
                continue

            # --- Governor mediation ---
            mediated_text = GovernorMediator.mediate(text)
            governed_parse_text = (
                raw_text
                if re.match(
                    r"^\s*(?:edit|update)\s+(?:(?:that|last|recent)\s+memory|memory\s+[A-Za-z0-9\-_]+)\s*:",
                    raw_text,
                    re.IGNORECASE,
                )
                or re.match(
                    r"^\s*memory\s+supersede\s+[A-Za-z0-9\-_]+\s+with\s+[^:]{1,120}\s*:",
                    raw_text,
                    re.IGNORECASE,
                )
                else mediated_text
            )

            # --- Phaseâ€‘4 governed invocation detection ---
            inv_result = GovernorMediator.parse_governed_invocation(governed_parse_text, session_id=session_id)
            if inv_result is None and lowered in {"more", "tell me more", "more please"}:
                try:
                    last_story_index = int(session_state.get("last_news_story_index") or 0)
                except Exception:
                    last_story_index = 0
                if last_story_index > 0:
                    inv_result = Invocation(
                        capability_id=49,
                        params={"action": "story_page_summary", "story_index": last_story_index},
                    )

            if isinstance(inv_result, Invocation):
                capability_id = inv_result.capability_id
                params = dict(inv_result.params)
                params.setdefault("session_id", session_id)
                if invocation_source == "deepseek_button" and capability_id == 31:
                    capability_id = 62
                if capability_id == 18 and not params.get("text"):
                    params["text"] = session_state.get("last_response", "")
                if capability_id == 31 and not params.get("text"):
                    if not params.get("text"):
                        params["text"] = session_state.get("last_response", "")
                if capability_id == 62 and not params.get("text"):
                    params["text"] = _build_second_opinion_review_text(session_context, session_state)
                    if not params.get("text"):
                        params["text"] = session_state.get("last_response", "")
                if capability_id in {49, 50, 51, 52, 53}:
                    if not session_state.get("news_cache"):
                        _, snapshot_result = await invoke_governed_text_command(
                            governor,
                            "news",
                            session_id,
                        )
                        if (
                            snapshot_result is not None
                            and snapshot_result.success
                            and isinstance(snapshot_result.data, dict)
                        ):
                            snapshot_widget = snapshot_result.data.get("widget")
                            if isinstance(snapshot_widget, dict):
                                items = list(snapshot_widget.get("items") or [])
                                categories = dict(snapshot_widget.get("categories") or {})
                                session_state["news_cache"] = items
                                session_state["news_categories"] = categories
                                session_state["last_sources"] = _extract_sources_from_results(items)
                                session_state["last_source_links"] = _extract_source_links(items)
                                await ws_send(ws, snapshot_widget)
                    params.setdefault("headlines", list(session_state.get("news_cache") or []))
                    params.setdefault("categories", dict(session_state.get("news_categories") or {}))
                    params.setdefault("topic_history", dict(session_state.get("topic_memory_map") or {}))
                    if capability_id == 49 and str(params.get("action") or "").strip().lower() == "story_page_summary":
                        try:
                            resolved_story_index = int(params.get("story_index") or 0)
                        except Exception:
                            resolved_story_index = 0
                        if resolved_story_index <= 0:
                            try:
                                resolved_story_index = int(session_state.get("last_news_story_index") or 0)
                            except Exception:
                                resolved_story_index = 0
                        if resolved_story_index <= 0:
                            await send_chat_message(
                                ws,
                                "I need a story number first. Try 'summary of story 1' after loading news headlines.",
                            )
                            await send_chat_done(ws)
                            continue
                        params["story_index"] = resolved_story_index
                    if capability_id == 50:
                        params.setdefault("brief_clusters", list(session_state.get("last_brief_clusters") or []))
                if capability_id == 17:
                    source_index = params.get("source_index")
                    if source_index is not None:
                        try:
                            source_idx = int(source_index) - 1
                        except Exception:
                            source_idx = -1
                        source_links = session_state.get("last_source_links") or []
                        if 0 <= source_idx < len(source_links):
                            params["resolved_url"] = str(source_links[source_idx].get("url") or "")
                            params["source_label"] = str(source_links[source_idx].get("source") or "")
                        else:
                            await send_chat_message(ws, "I couldn't find that source index. Ask for sources first.")
                            await send_chat_done(ws)
                            continue
                if capability_id == 54:
                    params.setdefault("analysis_documents", list(session_state.get("analysis_documents") or []))
                    if params.get("doc_id") in {None, ""} and session_state.get("last_analysis_doc_id") is not None:
                        params["doc_id"] = session_state.get("last_analysis_doc_id")
                if capability_id in {58, 59, 60}:
                    params["invocation_source"] = invocation_source
                    if capability_id == 60:
                        params.setdefault("working_context", working_context.for_explain())
                    else:
                        params.setdefault("working_context", working_context.to_dict())
                if capability_id == 61:
                    prepared_ok, prepared_params, prepared_message = _prepare_memory_bridge_params(
                        params=params,
                        project_threads=project_threads,
                        session_state=session_state,
                        session_id=session_id,
                    )
                    if not prepared_ok:
                        await send_chat_message(ws, prepared_message)
                        await send_chat_done(ws)
                        continue
                    params = prepared_params
                    memory_action = str(params.get("action") or "").strip().lower()
                    if memory_action in {"delete", "unlock", "supersede"} and not params.get("confirmed"):
                        session_state["pending_governed_confirm"] = {
                            "capability_id": capability_id,
                            "params": dict(params),
                        }
                        await send_chat_message(
                            ws,
                            _memory_confirmation_prompt(memory_action, params),
                        )
                        await send_chat_done(ws)
                        continue

                if capability_id == 22 and not params.get("confirmed"):
                    target = str(params.get("target") or "").strip()
                    path = str(params.get("path") or "").strip()
                    resource = path or target or "that location"
                    session_state["pending_governed_confirm"] = {
                        "capability_id": capability_id,
                        "params": dict(params),
                    }
                    await send_chat_message(
                        ws,
                        (
                            f"Open {resource}?\n"
                            "This action needs confirmation.\n"
                            "Reply 'yes' to proceed or 'no' to cancel."
                        ),
                    )
                    await send_chat_done(ws)
                    continue

                if capability_id == 17:
                    plan = plan_web_open(params)
                    if not plan.get("ok"):
                        await send_chat_message(ws, str(plan.get("message") or "I couldn't resolve that website."))
                        await send_chat_done(ws)
                        continue
                    if plan.get("requires_confirmation") and not params.get("confirmed") and not params.get("preview"):
                        session_state["pending_web_open"] = {
                            "target": params.get("target", ""),
                            "resolved_url": plan.get("url", ""),
                            "preview": bool(params.get("preview")),
                        }
                        await send_chat_message(
                            ws,
                            (
                                f"Open {plan.get('domain', plan.get('url', 'this website'))}?\n"
                                f"URL: {plan.get('url', '')}\n"
                                "Reply 'yes' to open or 'no' to cancel."
                            ),
                        )
                        await send_chat_done(ws)
                        continue

                review_followthrough_source_answer = ""
                review_followthrough_source_prompt = ""
                if capability_id in {31, 62}:
                    review_followthrough_source_prompt = _latest_session_user_query()
                    last_response = str(session_state.get("last_response") or "").strip()
                    if capability_id == 62:
                        review_followthrough_source_answer = last_response
                    elif last_response and str(params.get("text") or "").strip() == last_response:
                        review_followthrough_source_answer = last_response

                action_result = await invoke_governed_capability(governor, capability_id, params)
                action_message = _action_result_message(action_result)
                action_payload = _action_result_payload(action_result)
                if isinstance(action_payload, dict) and "budget_state" in action_payload:
                    await send_token_budget_update(ws, action_result)
                track_topic_hint = ""
                if capability_id == 50 and params.get("action") == "track_cluster":
                    if isinstance(action_payload, dict):
                        track_topic_hint = str(action_payload.get("track_topic") or "").strip()
                if isinstance(action_payload, dict):
                    context_snapshot = action_payload.get("context_snapshot")
                    if isinstance(context_snapshot, dict):
                        working_context.apply_snapshot(context_snapshot)
                    working_context_delta = action_payload.get("working_context_delta")
                    if isinstance(working_context_delta, dict):
                        working_context.apply_patch(
                            working_context_delta,
                            source=f"capability_{capability_id}",
                        )
                    topic_map = action_payload.get("topic_map")
                    if isinstance(topic_map, dict):
                        session_state["topic_memory_map"] = topic_map
                    widget = action_payload.get("widget")
                    if isinstance(widget, dict) and widget.get("type") == "search":
                        search_data = widget.get("data") if isinstance(widget.get("data"), dict) else {}
                        results = search_data.get("results") if isinstance(search_data, dict) else []
                        if isinstance(results, list):
                            session_state["last_sources"] = _extract_sources_from_results(results)
                            session_state["last_source_links"] = _extract_source_links(results)
                    if isinstance(widget, dict) and widget.get("type") == "news":
                        items = list(widget.get("items") or [])
                        session_state["news_cache"] = items
                        session_state["news_categories"] = dict(widget.get("categories") or {})
                        session_state["last_sources"] = _extract_sources_from_results(items)
                        session_state["last_source_links"] = _extract_source_links(items)
                    if isinstance(widget, dict) and widget.get("type") == "calendar":
                        session_state["last_calendar_summary"] = str(widget.get("summary") or "")
                        session_state["last_calendar_events"] = list(widget.get("events") or [])
                    analysis_docs = action_payload.get("analysis_documents")
                    if isinstance(analysis_docs, list):
                        session_state["analysis_documents"] = analysis_docs
                    if capability_id == 61:
                        memory_item = action_payload.get("memory_item")
                        if isinstance(memory_item, dict):
                            await send_memory_item_widget(
                                ws,
                                session_state,
                                item=memory_item,
                            )
                            links = dict(memory_item.get("links") or {})
                            linked_thread = str(links.get("project_thread_name") or "").strip()
                            if linked_thread:
                                session_state["project_thread_active"] = linked_thread
                        memory_items = action_payload.get("memory_items")
                        if isinstance(memory_items, list):
                            await send_memory_list_widget(
                                ws,
                                session_state,
                                items=memory_items,
                                filters={
                                    "tier": str(params.get("tier") or "").strip().lower(),
                                    "scope": str(params.get("scope") or "").strip().lower(),
                                    "thread_name": str(params.get("thread_name") or "").strip(),
                                    "thread_key": str(params.get("thread_key") or "").strip(),
                                },
                            )
                        overview_data = action_payload.get("memory_overview")
                        if isinstance(overview_data, dict):
                            await send_memory_overview_widget(
                                ws,
                                session_state,
                                overview=overview_data,
                            )
                        elif action_result.success:
                            await send_memory_overview_widget(ws, session_state)
                    sources = action_payload.get("sources")
                    if isinstance(sources, list) and sources:
                        session_state["last_sources"] = [str(src) for src in sources[:10]]
                    if capability_id == 17 and isinstance(action_payload.get("opened_domain"), str):
                        session_state["last_sources"] = [action_payload.get("opened_domain")]
                    brief_clusters = action_payload.get("brief_clusters")
                    if isinstance(brief_clusters, list):
                        session_state["last_brief_clusters"] = brief_clusters
                        flattened_links: list[dict[str, str]] = []
                        for cluster in brief_clusters:
                            if not isinstance(cluster, dict):
                                continue
                            for item in (cluster.get("items") or []):
                                if not isinstance(item, dict):
                                    continue
                                url = str(item.get("url") or "").strip()
                                if not url:
                                    continue
                                flattened_links.append(
                                    {
                                        "url": url,
                                        "source": str(item.get("source") or "").strip(),
                                        "title": str(item.get("title") or "").strip(),
                                    }
                                )
                        if flattened_links:
                            session_state["last_source_links"] = _extract_source_links(flattened_links)
                    if "document_id" in action_payload:
                        session_state["last_analysis_doc_id"] = action_payload.get("document_id")
                        working_context.set_open_report_id(action_payload.get("document_id"))

                if capability_id == 22 and action_result.success:
                    opened_path = str(params.get("path") or "").strip()
                    if opened_path:
                        working_context.set_selected_file(opened_path)

                session_state["working_context"] = working_context.to_dict()

                if capability_id in {31, 62}:
                    if action_result.success and isinstance(action_payload, dict):
                        session_state["last_review_followthrough"] = build_review_followthrough_snapshot(
                            payload=action_payload,
                            source_answer=review_followthrough_source_answer,
                            source_prompt=review_followthrough_source_prompt,
                        )
                    else:
                        session_state["last_review_followthrough"] = {}

                suppress_silent_chat = bool(
                    silent_widget_refresh
                    and capability_id == 61
                    and str(params.get("action") or "").strip().lower() in {"overview", "list", "show"}
                )

                if capability_id != 18 and action_message and not suppress_silent_chat:
                    session_state["last_response"] = action_message

                if capability_id in {16, 48, 55, 56}:
                    if action_result.success:
                        session_state["trust_status"] = failure_ladder.record_external_success(
                            session_state.get("trust_status", {}),
                            "Governed web search",
                        )
                    else:
                        session_state["trust_status"] = failure_ladder.record_failure(
                            session_state.get("trust_status", {}),
                            reason="Temporary issue",
                            external=True,
                            last_external_call="Governed web search",
                        )
                else:
                    if action_result.success:
                        session_state["trust_status"] = failure_ladder.record_local_success(
                            session_state.get("trust_status", {})
                        )
                    else:
                        session_state["trust_status"] = failure_ladder.record_failure(
                            session_state.get("trust_status", {}),
                            reason="Temporary issue",
                            external=False,
                        )
                await send_trust_status(ws, session_state["trust_status"])

                message_confidence: Optional[str] = None
                message_suggestions: list[dict[str, str]] | None = None
                if capability_id == 31 and isinstance(action_payload, dict):
                    accuracy_label = str(action_payload.get("verification_accuracy_label") or "").strip()
                    confidence_label = str(action_payload.get("verification_confidence_label") or "").strip()
                    review_followthrough = dict(session_state.get("last_review_followthrough") or {})
                    followthrough_ready = bool(str(review_followthrough.get("source_answer") or "").strip())
                    if accuracy_label:
                        message_confidence = f"Claim reliability {accuracy_label}"
                    elif confidence_label:
                        message_confidence = f"Verification {confidence_label}"
                    if action_payload.get("verification_recommended") is True:
                        message_suggestions = []
                        if followthrough_ready:
                            message_suggestions.append({"label": "Nova final answer", "command": "final answer"})
                            message_suggestions.append(
                                {"label": "Original answer", "command": "return to Nova's original answer"}
                            )
                        else:
                            message_suggestions.append(
                                {"label": "Re-check with sources", "command": "show sources for your last response"}
                            )
                        message_suggestions.append({"label": "Summarize gaps", "command": "summarize the gaps only"})
                if capability_id == 49 and isinstance(action_payload, dict):
                    story_index = int(action_payload.get("story_index") or 0)
                    if story_index > 0:
                        session_state["last_news_story_index"] = story_index
                        if not message_suggestions:
                            message_suggestions = [
                                {"label": "More", "command": "more"},
                                {"label": "Summarize all", "command": "summarize all headlines"},
                                {"label": "Today's brief", "command": "today's news"},
                            ]
                    elif action_result.success:
                        widget = action_payload.get("widget")
                        if isinstance(widget, dict):
                            widget_data = widget.get("data")
                            if isinstance(widget_data, dict):
                                indices = widget_data.get("indices")
                                if isinstance(indices, list) and indices:
                                    try:
                                        session_state["last_news_story_index"] = int(indices[0])
                                    except Exception:
                                        pass
                    related_pairs = action_payload.get("related_pairs")
                    if isinstance(related_pairs, list) and related_pairs:
                        pair = next((p for p in related_pairs if isinstance(p, dict)), {})
                        left = int(pair.get("left_index") or 0)
                        right = int(pair.get("right_index") or 0)
                        if left > 0 and right > 0:
                            message_suggestions = [
                                {"label": f"Compare {left} vs {right}", "command": f"compare headlines {left} and {right}"},
                                {"label": "Summarize all", "command": "summarize all headlines"},
                                {"label": "Today's brief", "command": "today's news"},
                            ]
                if capability_id == 50 and track_topic_hint and not message_suggestions:
                    message_suggestions = [
                        {"label": "Track this story", "command": f"track story {track_topic_hint}"},
                        {"label": "Show topic map", "command": "show topic map"},
                        {"label": "Today's brief", "command": "today's news"},
                    ]
                if capability_id in {49, 50} and not action_result.success and not message_suggestions:
                    message_suggestions = [
                        {"label": "Refresh headlines", "command": "today's news"},
                        {"label": "Retry brief", "command": "daily brief"},
                        {"label": "Summarize headlines", "command": "summarize all headlines"},
                    ]
                if capability_id == 61 and action_result.success and isinstance(action_payload, dict):
                    memory_item = action_payload.get("memory_item")
                    if isinstance(memory_item, dict):
                        item_id = str(memory_item.get("id") or "").strip()
                        links = dict(memory_item.get("links") or {})
                        linked_thread = str(links.get("project_thread_name") or "").strip()
                        suggestion_items: list[dict[str, str]] = []
                        if item_id:
                            suggestion_items.append({"label": "Show memory item", "command": f"memory show {item_id}"})
                            suggestion_items.append(
                                {"label": "Edit memory", "command": f"edit memory {item_id}: <updated text>"}
                            )
                            suggestion_items.append({"label": "Delete memory", "command": f"delete memory {item_id}"})
                        if linked_thread:
                            suggestion_items.append(
                                {"label": f"Continue {linked_thread}", "command": f"continue my {linked_thread}"}
                            )
                            suggestion_items.append(
                                {"label": f"Memory for {linked_thread}", "command": f"memory list thread {linked_thread}"}
                            )
                        suggestion_items.append({"label": "Memory overview", "command": "memory overview"})
                        if suggestion_items:
                            message_suggestions = suggestion_items
                if capability_id == 62 and isinstance(action_payload, dict):
                    session_state["last_reasoning_review"] = dict(action_payload)
                    accuracy_label = str(action_payload.get("reasoning_accuracy_label") or "").strip()
                    confidence_label = str(action_payload.get("reasoning_confidence_label") or "").strip()
                    if accuracy_label:
                        message_confidence = f"Second opinion {accuracy_label}"
                    elif confidence_label:
                        message_confidence = f"Review confidence {confidence_label}"
                    if not message_suggestions:
                        message_suggestions = [
                            {"label": "Nova final answer", "command": "final answer"},
                            {"label": "Summarize gaps", "command": "summarize the gaps only"},
                            {"label": "Return to answer", "command": "return to Nova's original answer"},
                        ]

                recommendation_reason = ""
                if action_result.success and capability_id in {54, 59, 60}:
                    suggested_thread = project_threads.suggest_thread_name(
                        preferred_name=str(session_state.get("project_thread_active") or ""),
                        context_hint=working_context.followup_target(),
                    )
                    extra_actions: list[dict[str, str]] = []
                    if suggested_thread:
                        extra_actions.append(
                            {
                                "label": f"Save to {suggested_thread}",
                                "command": f"save this as part of {suggested_thread}",
                            }
                        )
                        extra_actions.append(
                            {
                                "label": f"Continue {suggested_thread}",
                                "command": f"continue my {suggested_thread}",
                            }
                        )
                    else:
                        thread_hint = _extract_topic_candidate(str(working_context.followup_target() or text)) or "current project"
                        extra_actions.append(
                            {
                                "label": "Create project thread",
                                "command": f"create thread {thread_hint}",
                            }
                        )
                    recommendation_reason = _derive_recommendation_reason(
                        capability_id=capability_id,
                        action_result=action_result,
                        working_context=working_context,
                    )
                    if recommendation_reason:
                        session_state["last_recommendation_reason"] = recommendation_reason
                        extra_actions.append(
                            {"label": "Why this recommendation", "command": "why this recommendation"}
                        )
                    extra_actions.append({"label": "Show threads", "command": "show threads"})
                    if message_suggestions:
                        merged = list(message_suggestions) + extra_actions
                    else:
                        merged = extra_actions
                    deduped: list[dict[str, str]] = []
                    seen_commands: set[str] = set()
                    for item in merged:
                        cmd = str(item.get("command") or "").strip().lower()
                        if not cmd or cmd in seen_commands:
                            continue
                        seen_commands.add(cmd)
                        deduped.append(item)
                    message_suggestions = deduped[:4]

                outgoing_message = _structure_long_message(action_message)
                if not outgoing_message.strip() and capability_id == 18 and action_result.success:
                    outgoing_message = "Speaking now."
                if recommendation_reason:
                    outgoing_message = (
                        f"{outgoing_message}\n\n"
                        "Why this recommendation\n"
                        f"- {recommendation_reason}"
                    )
                if not suppress_silent_chat:
                    await send_chat_message(
                        ws,
                        outgoing_message,
                        confidence=message_confidence,
                        suggested_actions=message_suggestions,
                        tone_domain=_tone_domain_for_capability(capability_id),
                    )

                if (
                    isinstance(action_payload, dict)
                    and "widget" in action_payload
                    and (action_result.success or capability_id in {55, 56, 57})
                ):
                    await ws_send(ws, action_payload["widget"])
                elif capability_id == 32 and action_result.success and isinstance(action_payload, dict):
                    await ws_send(ws, {"type": "system", "data": action_payload, "summary": action_message})

                await send_chat_done(ws)

                # Autoâ€‘speak for voice input (only if not a TTS invocation)
                if (session_state.get("last_input_channel") == "voice"
                        and action_result.success
                        and capability_id != 18):
                    speak_text = resolve_speakable_text(action_result) or outgoing_message
                    _maybe_auto_speak_for_voice_turn(session_state, speak_text)
                elif session_state.get("last_input_channel") == "voice" and capability_id == 18:
                    session_state["last_input_channel"] = None
                session_state["turn_count"] += 1
                continue

            elif isinstance(inv_result, Clarification):
                await send_chat_message(
                    ws,
                    inv_result.message,
                    suggested_actions=_clarification_suggestions(inv_result.message),
                )
                await send_chat_done(ws)
                _maybe_auto_speak_for_voice_turn(session_state, inv_result.message)
                session_state["turn_count"] += 1
                continue

            # --- inv_result is None â€“ proceed to Phaseâ€‘3.5 handling ---

            # --- Quick Corrections ---
            if mediated_text.startswith("Correction:"):
                correction_text = mediated_text[len("Correction:"):].strip()
                if correction_text:
                    record_correction(correction_text)
                await send_chat_message(ws, "Okay. Correction noted.")
                await send_chat_done(ws)
                continue

            # --- Bounded advisory general-chat fallback ---
            skill_result = await run_general_chat_fallback(
                mediated_text,
                general_chat_skill=general_chat_skill,
                session_state=session_state,
                session_context=session_context,
                project_threads=project_threads,
                select_relevant_memory_context=_select_relevant_memory_context,
            )

            if skill_result:
                skill_name = getattr(skill_result, "skill", "") or ""
                skill_tone_domain = _tone_domain_for_skill(skill_name)
                message = getattr(skill_result, "message", "") or ""
                widget_data = getattr(skill_result, "widget_data", None)
                result_data = getattr(skill_result, "data", {}) or {}

                if skill_name == "general_chat" and result_data.get("speakable_text"):
                    message = str(message or "").strip()
                    result_data["speakable_text"] = str(result_data.get("speakable_text") or message)
                    result_data["structured_data"] = dict(result_data.get("structured_data") or {})
                else:
                    payload = response_formatter.format_payload(
                        message,
                        speakable_text=(result_data.get("speakable_text") or ""),
                        structured_data=(result_data.get("structured_data") or {}),
                    )
                    message = _structure_long_message(payload["user_message"])
                    result_data["speakable_text"] = payload["speakable_text"]
                    result_data["structured_data"] = payload["structured_data"]

                speech_state.last_spoken_text = str(result_data.get("speakable_text") or message or "").strip()
                session_state["last_response"] = message
                if skill_name == "general_chat" and isinstance(result_data.get("conversation_context"), dict):
                    session_state["conversation_context"] = dict(result_data.get("conversation_context") or {})

                escalation = result_data.get("escalation", {})
                if escalation.get("ask_user"):
                    session_state["pending_escalation"] = (
                        escalation.get("original_query", mediated_text),
                        escalation.get("context_snapshot", session_context[-5:]),
                        escalation.get("heuristic_result", {}),
                    )
                    await send_chat_message(ws, message, tone_domain=skill_tone_domain)
                    await send_chat_done(ws)
                    _maybe_auto_speak_for_voice_turn(
                        session_state,
                        str(result_data.get("speakable_text") or message or "").strip(),
                    )
                    continue

                message_id = None
                if escalation.get("escalated") and escalation.get("thought_data"):
                    message_id = str(uuid.uuid4())
                    thought_store.put(session_id, message_id, escalation["thought_data"])
                    session_state["escalation_count"] += 1
                    session_state["last_escalation_turn"] = session_state["turn_count"]
                    session_state["deep_mode_armed"] = False

                    if isinstance(widget_data, dict) and "type" in widget_data:
                        if widget_data.get("type") == "news":
                            items = list(widget_data.get("items") or [])
                            categories = dict(widget_data.get("categories") or {})
                            session_state["news_cache"] = items
                            session_state["news_categories"] = categories
                            session_state["last_sources"] = _extract_sources_from_results(items)
                            session_state["last_source_links"] = _extract_source_links(items)
                        await ws_send(ws, widget_data)
                elif skill_name == "news" and isinstance(widget_data, dict):
                    items = widget_data.get("items", [])
                    session_state["news_cache"] = list(items)
                    session_state["news_categories"] = dict(widget_data.get("categories") or {})
                    session_state["last_sources"] = _extract_sources_from_results(list(items))
                    session_state["last_source_links"] = _extract_source_links(list(items))
                    await send_widget_message(ws, "news", message, widget_data)
                elif skill_name == "weather" and isinstance(widget_data, dict):
                    await send_widget_message(ws, "weather", message, widget_data)
                elif skill_name == "calendar" and isinstance(widget_data, dict):
                    session_state["last_calendar_summary"] = str(widget_data.get("summary") or "")
                    session_state["last_calendar_events"] = list(widget_data.get("events") or [])
                    await send_widget_message(ws, "calendar", message, widget_data)
                else:
                    await send_chat_message(
                        ws,
                        message,
                        message_id=message_id,
                        tone_domain=skill_tone_domain,
                    )

                if skill_name in {"weather", "news"}:
                    if getattr(skill_result, "success", False):
                        session_state["trust_status"] = failure_ladder.record_external_success(
                            session_state.get("trust_status", {}),
                            f"{skill_name} request",
                        )
                    else:
                        session_state["trust_status"] = failure_ladder.record_failure(
                            session_state.get("trust_status", {}),
                            reason="Temporary issue",
                            external=True,
                            last_external_call=f"{skill_name} request",
                        )
                elif skill_name:
                    if getattr(skill_result, "success", False):
                        session_state["trust_status"] = failure_ladder.record_local_success(
                            session_state.get("trust_status", {})
                        )
                    else:
                        session_state["trust_status"] = failure_ladder.record_failure(
                            session_state.get("trust_status", {}),
                            reason="Temporary issue",
                            external=False,
                        )
                await send_trust_status(ws, session_state["trust_status"])

                await send_chat_done(ws)

                # Autoâ€‘speak for voice input
                if (session_state.get("last_input_channel") == "voice"
                        and getattr(skill_result, "success", True)):   # assume success if not present
                    _maybe_auto_speak_for_voice_turn(
                        session_state,
                        str(result_data.get("speakable_text") or message or "").strip(),
                    )

                new_turn = [{"role": "user", "content": mediated_text}, {"role": "assistant", "content": message}]
                session_context.extend(new_turn)
                context_limit = 40 if session_state.get("presence_mode") else 20
                session_context = session_context[-context_limit:]
                if skill_name == "general_chat":
                    chat_context = list(session_state.get("general_chat_context") or [])
                    chat_context.extend(new_turn)
                    if hasattr(general_chat_skill, "roll_context_forward"):
                        session_state["general_chat_context"] = general_chat_skill.roll_context_forward(
                            chat_context,
                            session_state,
                        )
                    else:
                        session_state["general_chat_context"] = chat_context
                session_state["turn_count"] += 1
                continue

            # --- Fallback ---
            fallback_message = response_formatter.friendly_fallback()
            session_state["last_response"] = fallback_message
            await send_chat_message(
                ws,
                fallback_message,
                suggested_actions=_conversation_suggestions(session_state),
            )
            await send_chat_done(ws)
            _maybe_auto_speak_for_voice_turn(session_state, fallback_message)
            session_state["turn_count"] += 1

    except WebSocketDisconnect:
        log.info("WebSocket disconnected")
    finally:
        thought_store.clear_session(session_id)
        GovernorMediator.clear_session(session_id)
