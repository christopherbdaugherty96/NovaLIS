from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass, field
from typing import Any

from src.conversation.conversation_router import ConversationRouter
from src.conversation.response_style_router import InputNormalizer
from src.debug.cognitive_trace import CognitiveTrace
from src.governor.governor import Governor
from src.governor.governor_mediator import Clarification, GovernorMediator, Invocation
from src.skill_registry import SkillRegistry


SHORTEN_ALIASES = {
    "shorter",
    "shorter version",
    "make that shorter",
    "summarize your last response",
    "summarize that",
    "tldr",
    "tl;dr",
}


@dataclass
class TranscriptTurn:
    user_message: str
    nova_response: str
    decision_mode: str = ""
    intent_family: str = ""
    continuation_detected: bool = False
    should_escalate: bool = False
    policy_blocked: bool = False
    clarification_triggered: bool = False
    capability_triggered: int | None = None
    capability_executor: str = ""
    governor_decision: str = ""
    execution_time_ms: float = 0.0
    errors: list[str] = field(default_factory=list)
    trace_id: str = ""
    trace_steps: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ConversationTranscript:
    turns: list[TranscriptTurn] = field(default_factory=list)

    def capability_sequence(self) -> list[int]:
        return [t.capability_triggered for t in self.turns if t.capability_triggered is not None]


def _shorten_text(text: str, max_sentences: int = 2, max_chars: int = 260) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    normalized = re.sub(r"\s+", " ", raw).strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", normalized) if s.strip()]
    short = " ".join(sentences[:max_sentences]).strip() if sentences else normalized
    if len(short) > max_chars:
        short = short[: max_chars - 3].rstrip() + "..."
    return short


class ConversationSimulator:
    """Runs scripted user conversations through Nova's real routing pipeline."""

    def __init__(self, *, include_trace: bool = False) -> None:
        self.governor = Governor()
        self.skill_registry = SkillRegistry(network=self.governor.network)
        self._last_response = ""
        self._last_intent_family = ""
        self._last_object = ""
        self._include_trace = bool(include_trace)

    @staticmethod
    def _executor_for_capability(capability_id: int) -> str:
        mapping = {
            16: "web_search_executor",
            17: "webpage_launch_executor",
            18: "tts_executor",
            19: "volume_executor",
            20: "media_executor",
            21: "brightness_executor",
            22: "open_folder_executor",
            31: "response_verification_executor",
            32: "os_diagnostics_executor",
            48: "multi_source_reporting_executor",
            49: "news_intelligence_executor.execute_summary",
            50: "news_intelligence_executor.execute_brief",
            51: "news_intelligence_executor.execute_topic_map",
            52: "story_tracker_executor.execute_update",
            53: "story_tracker_executor.execute_view",
            54: "analysis_document_executor",
        }
        return mapping.get(int(capability_id), "")

    async def run_simulation_async(self, script: list[str]) -> ConversationTranscript:
        transcript = ConversationTranscript()
        for raw in script:
            turn = await self._process_turn(raw or "")
            transcript.turns.append(turn)
        return transcript

    def run_simulation(self, script: list[str]) -> ConversationTranscript:
        return asyncio.run(self.run_simulation_async(script))

    async def _process_turn(self, raw_text: str) -> TranscriptTurn:
        started = time.perf_counter()
        trace = CognitiveTrace() if self._include_trace else None
        if trace is not None:
            trace.record("input_received", {"raw_input": str(raw_text or "")})
        text = InputNormalizer.normalize(raw_text).strip()
        lowered = text.lower().rstrip(".?!")
        decision = ConversationRouter.route(
            text,
            {
                "last_response": self._last_response,
                "last_intent_family": self._last_intent_family,
                "last_object": self._last_object,
            },
        )
        if trace is not None:
            trace.record("input_normalizer", {"normalized_input": text, "lowered": lowered})
            trace.record(
                "conversation_router",
                {
                    "mode": decision.mode.value,
                    "should_escalate": bool(decision.should_escalate),
                    "blocked_by_policy": bool(decision.blocked_by_policy),
                    "needs_clarification": bool(decision.needs_clarification),
                },
            )

        if decision.blocked_by_policy:
            response = "I can't help with that request."
            self._last_response = response
            elapsed = (time.perf_counter() - started) * 1000
            if trace is not None:
                trace.record("policy_block", {"reason": decision.policy_reason or "policy_blocked"})
            return TranscriptTurn(
                user_message=raw_text,
                nova_response=response,
                decision_mode=decision.mode.value,
                intent_family=decision.intent_family,
                continuation_detected=decision.continuation_detected,
                should_escalate=decision.should_escalate,
                policy_blocked=True,
                governor_decision="policy_block",
                execution_time_ms=round(elapsed, 3),
                trace_id=trace.trace_id if trace is not None else "",
                trace_steps=list(trace.steps) if trace is not None else [],
            )

        if decision.needs_clarification:
            response = decision.clarification_prompt or "Could you clarify that?"
            self._last_response = response
            elapsed = (time.perf_counter() - started) * 1000
            if trace is not None:
                trace.record("clarification_returned", {"message": response})
            return TranscriptTurn(
                user_message=raw_text,
                nova_response=response,
                decision_mode=decision.mode.value,
                intent_family=decision.intent_family,
                continuation_detected=decision.continuation_detected,
                should_escalate=decision.should_escalate,
                clarification_triggered=True,
                governor_decision="clarification",
                execution_time_ms=round(elapsed, 3),
                trace_id=trace.trace_id if trace is not None else "",
                trace_steps=list(trace.steps) if trace is not None else [],
            )

        self._last_intent_family = decision.intent_family
        if decision.resolved_text:
            text = decision.resolved_text.strip()
            lowered = text.lower().rstrip(".?!")
        if lowered in {"open downloads", "open documents"}:
            self._last_object = lowered.replace("open ", "")

        if lowered in SHORTEN_ALIASES:
            shortened = _shorten_text(self._last_response)
            response = shortened or "I don't have a previous response to shorten yet."
            self._last_response = response
            elapsed = (time.perf_counter() - started) * 1000
            if trace is not None:
                trace.record("conversation_followup", {"type": "shorten_last_response"})
            return TranscriptTurn(
                user_message=raw_text,
                nova_response=response,
                decision_mode=decision.mode.value,
                intent_family=decision.intent_family,
                continuation_detected=decision.continuation_detected,
                should_escalate=decision.should_escalate,
                governor_decision="conversation_followup",
                execution_time_ms=round(elapsed, 3),
                trace_id=trace.trace_id if trace is not None else "",
                trace_steps=list(trace.steps) if trace is not None else [],
            )

        mediated_text = GovernorMediator.mediate(text)
        if trace is not None:
            trace.record("governor_mediator.mediate", {"mediated_text": mediated_text})
        parsed = GovernorMediator.parse_governed_invocation(mediated_text)
        if trace is not None:
            trace.record(
                "governor_mediator.parse",
                {
                    "invocation_detected": isinstance(parsed, Invocation),
                    "clarification": isinstance(parsed, Clarification),
                },
            )

        if isinstance(parsed, Clarification):
            self._last_response = parsed.message
            elapsed = (time.perf_counter() - started) * 1000
            if trace is not None:
                trace.record("clarification_returned", {"message": parsed.message})
            return TranscriptTurn(
                user_message=raw_text,
                nova_response=parsed.message,
                decision_mode=decision.mode.value,
                intent_family=decision.intent_family,
                continuation_detected=decision.continuation_detected,
                should_escalate=decision.should_escalate,
                clarification_triggered=True,
                governor_decision="clarification",
                execution_time_ms=round(elapsed, 3),
                trace_id=trace.trace_id if trace is not None else "",
                trace_steps=list(trace.steps) if trace is not None else [],
            )

        if isinstance(parsed, Invocation):
            if trace is not None:
                trace.record(
                    "governor_invocation",
                    {
                        "capability_id": parsed.capability_id,
                        "params": dict(parsed.params),
                    },
                )
            action_result = self.governor.handle_governed_invocation(parsed.capability_id, dict(parsed.params))
            response = str(action_result.message or "").strip()
            self._last_response = response
            errors: list[str] = []
            if not action_result.success:
                errors.append(response or "governed invocation failed")
            elapsed = (time.perf_counter() - started) * 1000
            executor_name = self._executor_for_capability(parsed.capability_id)
            if trace is not None:
                trace.record(
                    "executor_dispatch",
                    {
                        "capability_id": parsed.capability_id,
                        "executor": executor_name,
                        "success": bool(action_result.success),
                        "latency_ms": round(elapsed, 3),
                    },
                )
            return TranscriptTurn(
                user_message=raw_text,
                nova_response=response,
                decision_mode=decision.mode.value,
                intent_family=decision.intent_family,
                continuation_detected=decision.continuation_detected,
                should_escalate=decision.should_escalate,
                capability_triggered=parsed.capability_id,
                capability_executor=executor_name,
                governor_decision="governed_invocation",
                execution_time_ms=round(elapsed, 3),
                errors=errors,
                trace_id=trace.trace_id if trace is not None else "",
                trace_steps=list(trace.steps) if trace is not None else [],
            )

        # Phase-3.5 fallback path through real skills registry.
        for skill in self.skill_registry.skills:
            if not skill.can_handle(mediated_text):
                continue
            maybe = skill.handle(mediated_text)
            result = await maybe if hasattr(maybe, "__await__") else maybe
            if result is None:
                continue
            response = str(getattr(result, "message", "") or "").strip()
            self._last_response = response
            elapsed = (time.perf_counter() - started) * 1000
            if trace is not None:
                trace.record(
                    "skill_fallback",
                    {
                        "skill": str(getattr(skill, "name", "")),
                        "success": True,
                        "latency_ms": round(elapsed, 3),
                    },
                )
            return TranscriptTurn(
                user_message=raw_text,
                nova_response=response,
                decision_mode=decision.mode.value,
                intent_family=decision.intent_family,
                continuation_detected=decision.continuation_detected,
                should_escalate=decision.should_escalate,
                governor_decision="skill_fallback",
                execution_time_ms=round(elapsed, 3),
                trace_id=trace.trace_id if trace is not None else "",
                trace_steps=list(trace.steps) if trace is not None else [],
            )

        fallback = "I'm not sure what you'd like me to do with that."
        self._last_response = fallback
        elapsed = (time.perf_counter() - started) * 1000
        if trace is not None:
            trace.record("no_route_fallback", {"latency_ms": round(elapsed, 3)})
        return TranscriptTurn(
            user_message=raw_text,
            nova_response=fallback,
            decision_mode=decision.mode.value,
            intent_family=decision.intent_family,
            continuation_detected=decision.continuation_detected,
            should_escalate=decision.should_escalate,
            governor_decision="no_route_fallback",
            execution_time_ms=round(elapsed, 3),
            trace_id=trace.trace_id if trace is not None else "",
            trace_steps=list(trace.steps) if trace is not None else [],
        )


def run_simulation(script: list[str], *, include_trace: bool = False) -> ConversationTranscript:
    return ConversationSimulator(include_trace=include_trace).run_simulation(script)
