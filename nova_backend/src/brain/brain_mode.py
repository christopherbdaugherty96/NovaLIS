"""Brain mode contracts and safe trace.

Responsibilities:
  - Define a mode for each type of Brain engagement
  - Specify per-mode contract (can/cannot, context requirements, output constraints)
  - Classify incoming queries into the correct mode
  - Produce a BrainTrace that explains structure without leaking private reasoning

Non-responsibilities:
  - Must not execute any action
  - Must not authorize any capability
  - Must not expose private LLM chain-of-thought
  - Must not mutate session state

Non-authorizing frozen dataclasses:
  BrainTrace.execution_performed, BrainTrace.authorization_granted, and
  BrainTrace.private_reasoning_exposed are enforced False in __post_init__
  and cannot be set by callers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


# ---------------------------------------------------------------------------
# BrainMode
# ---------------------------------------------------------------------------

class BrainMode(str, Enum):
    """Recognized engagement modes for the Brain."""

    BRAINSTORM = "brainstorm"
    REPO_REVIEW = "repo_review"
    IMPLEMENTATION = "implementation"
    MERGE = "merge"
    PLANNING = "planning"
    ACTION_REVIEW = "action_review"
    CASUAL = "casual"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)


# ---------------------------------------------------------------------------
# ModeContract
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ModeContract:
    """Static contract for one BrainMode.

    Describes what the Brain is allowed to produce in this mode and what it
    must never do. Contracts are vocabulary for planning and review only —
    looking one up does not authorize or execute anything.
    """

    mode: BrainMode
    description: str
    can: tuple[str, ...]
    cannot: tuple[str, ...]
    requires_context_before_recommending: bool
    may_produce_code: bool
    may_produce_plan: bool
    may_produce_review: bool
    may_mutate_repo: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": str(self.mode),
            "description": self.description,
            "can": list(self.can),
            "cannot": list(self.cannot),
            "requires_context_before_recommending": self.requires_context_before_recommending,
            "may_produce_code": self.may_produce_code,
            "may_produce_plan": self.may_produce_plan,
            "may_produce_review": self.may_produce_review,
            "may_mutate_repo": self.may_mutate_repo,
        }


# ---------------------------------------------------------------------------
# Mode contract registry
# ---------------------------------------------------------------------------

CONTRACTS: dict[BrainMode, ModeContract] = {
    BrainMode.BRAINSTORM: ModeContract(
        mode=BrainMode.BRAINSTORM,
        description=(
            "Exploratory thinking — ideas, alternatives, hypotheticals. "
            "No repo mutations; no execution. Safe to run before committing to a direction."
        ),
        can=(
            "generate and compare options",
            "list trade-offs and risks",
            "ask clarifying questions",
            "produce a candidate outline or skeleton",
            "reference existing code or docs without modifying them",
        ),
        cannot=(
            "write or modify files",
            "commit or push to repo",
            "authorize capabilities",
            "execute OpenClaw or browser tools",
            "treat a brainstorm output as a confirmed plan",
        ),
        requires_context_before_recommending=False,
        may_produce_code=False,
        may_produce_plan=True,
        may_produce_review=False,
        may_mutate_repo=False,
    ),

    BrainMode.REPO_REVIEW: ModeContract(
        mode=BrainMode.REPO_REVIEW,
        description=(
            "Read the current repo state before making any recommendation. "
            "No changes until review is complete."
        ),
        can=(
            "read files, diffs, and git history",
            "identify inconsistencies, drift, or missing tests",
            "report findings with file:line references",
            "recommend actions without executing them",
        ),
        cannot=(
            "recommend changes without first reading current state",
            "write or modify files as part of the review",
            "treat prior session context as current repo truth without verifying",
            "authorize execution",
        ),
        requires_context_before_recommending=True,
        may_produce_code=False,
        may_produce_plan=False,
        may_produce_review=True,
        may_mutate_repo=False,
    ),

    BrainMode.IMPLEMENTATION: ModeContract(
        mode=BrainMode.IMPLEMENTATION,
        description=(
            "Focused code or doc changes within the agreed scope. "
            "Scope is fixed at entry — no unilateral expansion."
        ),
        can=(
            "write, edit, or delete files within the stated scope",
            "run compile checks and test suites",
            "commit changes with descriptive messages",
            "raise a flag if a scope boundary is about to be crossed",
        ),
        cannot=(
            "expand scope without explicit user approval",
            "merge PRs or push to main unilaterally",
            "add features, refactors, or abstractions beyond the stated task",
            "authorize capabilities outside the current task",
        ),
        requires_context_before_recommending=True,
        may_produce_code=True,
        may_produce_plan=False,
        may_produce_review=False,
        may_mutate_repo=True,
    ),

    BrainMode.MERGE: ModeContract(
        mode=BrainMode.MERGE,
        description=(
            "Validate and merge a branch or PR. "
            "Must confirm tests pass and no destructive flags before proceeding."
        ),
        can=(
            "check PR status and CI results",
            "rebase or squash with user approval",
            "merge to main after user confirms readiness",
            "list any open blocking issues",
        ),
        cannot=(
            "force-push main",
            "merge without confirming tests pass",
            "delete remote branches without explicit user approval",
            "bypass PR review hooks",
        ),
        requires_context_before_recommending=True,
        may_produce_code=False,
        may_produce_plan=False,
        may_produce_review=True,
        may_mutate_repo=True,
    ),

    BrainMode.PLANNING: ModeContract(
        mode=BrainMode.PLANNING,
        description=(
            "Design and document a course of action. "
            "Output is a plan, spec, or roadmap — not executable steps."
        ),
        can=(
            "produce structured plans with phases and exit criteria",
            "reference existing architecture and constraints",
            "identify risks and open questions",
            "recommend sequencing without committing to it",
        ),
        cannot=(
            "treat a plan as an executed decision",
            "modify code or repo state",
            "authorize capabilities or execution",
            "overclaim implementation status from planning docs",
        ),
        requires_context_before_recommending=False,
        may_produce_code=False,
        may_produce_plan=True,
        may_produce_review=False,
        may_mutate_repo=False,
    ),

    BrainMode.ACTION_REVIEW: ModeContract(
        mode=BrainMode.ACTION_REVIEW,
        description=(
            "Evaluate a proposed action before it is taken. "
            "Produce a risk/benefit assessment; the user decides."
        ),
        can=(
            "describe what an action would do and its blast radius",
            "flag irreversibility, shared-state impact, or authorization requirements",
            "recommend a safer alternative or confirmation step",
            "produce a summary the user can act on",
        ),
        cannot=(
            "execute the action being reviewed",
            "approve the action on behalf of the user",
            "bypass Governor or authority-check flows",
            "treat review output as authorization",
        ),
        requires_context_before_recommending=True,
        may_produce_code=False,
        may_produce_plan=False,
        may_produce_review=True,
        may_mutate_repo=False,
    ),

    BrainMode.CASUAL: ModeContract(
        mode=BrainMode.CASUAL,
        description="Conversational turns with no technical subject or action intent.",
        can=(
            "respond naturally to greetings, thanks, and off-topic remarks",
            "ask what the user needs next",
        ),
        cannot=(
            "infer a technical task from a social turn",
            "execute actions",
            "authorize capabilities",
        ),
        requires_context_before_recommending=False,
        may_produce_code=False,
        may_produce_plan=False,
        may_produce_review=False,
        may_mutate_repo=False,
    ),

    BrainMode.UNKNOWN: ModeContract(
        mode=BrainMode.UNKNOWN,
        description="Mode could not be determined — treat as read-only until classified.",
        can=(
            "ask a clarifying question to determine intent",
            "return a candidate mode with low confidence",
        ),
        cannot=(
            "execute actions",
            "authorize capabilities",
            "write or modify files",
        ),
        requires_context_before_recommending=False,
        may_produce_code=False,
        may_produce_plan=False,
        may_produce_review=False,
        may_mutate_repo=False,
    ),
}


def get_contract(mode: BrainMode) -> ModeContract:
    """Return the ModeContract for the given mode.

    Always returns a contract — falls back to UNKNOWN if mode is not registered
    (defensive, should not happen with a known BrainMode value).
    """
    return CONTRACTS.get(mode, CONTRACTS[BrainMode.UNKNOWN])


# ---------------------------------------------------------------------------
# Mode classification
# ---------------------------------------------------------------------------

# Signal patterns — ordered from most specific to least specific
_BRAINSTORM_RE = re.compile(
    r"\b(brainstorm|what if|ideas? for|explore|alternatives?|options? for|what could|"
    r"what would|hypothetical|imagine if|think through|how might)\b",
    re.IGNORECASE,
)
_REPO_REVIEW_RE = re.compile(
    r"\b(review|audit|check|inspect|read the code|what does .{1,30} do|"
    r"explain (the |this )?(code|function|class|module|file)|"
    r"look at|is .{1,30} correct|does .{1,30} match)\b",
    re.IGNORECASE,
)
_IMPLEMENTATION_RE = re.compile(
    r"\b(implement|build|add|create|write|fix|refactor|update|change|modify|"
    r"patch|delete|remove|rename|move|replace|generate code)\b",
    re.IGNORECASE,
)
_MERGE_RE = re.compile(
    r"\b(merge|pull request|PR #?\d+|ready to merge|squash|rebase|land (the |this )?branch)\b",
    re.IGNORECASE,
)
_PLANNING_RE = re.compile(
    r"\b(plan|roadmap|design|spec|architecture|how should (we|i)|"
    r"what('s| is) the (approach|strategy|design)|outline|phase)\b",
    re.IGNORECASE,
)
_ACTION_REVIEW_RE = re.compile(
    r"\b(should (i|we) (run|execute|do|push|deploy|delete|drop)|"
    r"is it safe to|approve|authorize|risk of|blast radius|"
    r"what happens if (i|we) (run|execute|push|delete|drop))\b",
    re.IGNORECASE,
)
_CASUAL_RE = re.compile(
    r"^(hi|hello|hey|thanks|thank you|ok|okay|got it|sure|"
    r"sounds good|great|perfect|nice|cool|awesome|yep|nope|yes|no)[.!?]?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ModeClassification:
    """Result of classifying a query into a brain mode."""

    mode: BrainMode
    confidence: float          # 0.0 – 1.0
    signal: str                # which pattern or heuristic matched
    contract: ModeContract

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": str(self.mode),
            "confidence": self.confidence,
            "signal": self.signal,
            "contract": self.contract.to_dict(),
        }


def classify_mode(query: str) -> ModeClassification:
    """Classify a query string into a BrainMode.

    Uses lightweight regex matching — no LLM call, no external effects.
    Returns the most specific match; falls back to UNKNOWN with confidence 0.0.
    """
    text = (query or "").strip()

    if _CASUAL_RE.match(text):
        return ModeClassification(
            mode=BrainMode.CASUAL,
            confidence=0.95,
            signal="casual_pattern",
            contract=get_contract(BrainMode.CASUAL),
        )
    if _MERGE_RE.search(text):
        return ModeClassification(
            mode=BrainMode.MERGE,
            confidence=0.90,
            signal="merge_pattern",
            contract=get_contract(BrainMode.MERGE),
        )
    if _ACTION_REVIEW_RE.search(text):
        return ModeClassification(
            mode=BrainMode.ACTION_REVIEW,
            confidence=0.85,
            signal="action_review_pattern",
            contract=get_contract(BrainMode.ACTION_REVIEW),
        )
    if _BRAINSTORM_RE.search(text):
        return ModeClassification(
            mode=BrainMode.BRAINSTORM,
            confidence=0.80,
            signal="brainstorm_pattern",
            contract=get_contract(BrainMode.BRAINSTORM),
        )
    if _REPO_REVIEW_RE.search(text):
        return ModeClassification(
            mode=BrainMode.REPO_REVIEW,
            confidence=0.80,
            signal="repo_review_pattern",
            contract=get_contract(BrainMode.REPO_REVIEW),
        )
    if _PLANNING_RE.search(text):
        return ModeClassification(
            mode=BrainMode.PLANNING,
            confidence=0.75,
            signal="planning_pattern",
            contract=get_contract(BrainMode.PLANNING),
        )
    if _IMPLEMENTATION_RE.search(text):
        return ModeClassification(
            mode=BrainMode.IMPLEMENTATION,
            confidence=0.75,
            signal="implementation_pattern",
            contract=get_contract(BrainMode.IMPLEMENTATION),
        )

    return ModeClassification(
        mode=BrainMode.UNKNOWN,
        confidence=0.0,
        signal="no_pattern_matched",
        contract=get_contract(BrainMode.UNKNOWN),
    )


# ---------------------------------------------------------------------------
# BrainTrace
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BrainTrace:
    """Safe structural trace of a Brain turn.

    Records what mode was active, what context sources were used, and what
    structural decisions were made. Does NOT expose private LLM reasoning,
    internal prompt text, or chain-of-thought.

    Non-authorizing: execution_performed, authorization_granted, and
    private_reasoning_exposed are always False — enforced in __post_init__.
    """

    trace_id: str
    mode: BrainMode
    composed_at: str
    context_sources: tuple[str, ...]   # authority labels from ContextPack items
    decision_notes: tuple[str, ...]    # structural decisions made (not reasoning)
    warnings: tuple[str, ...]          # structural concerns about the turn

    # Non-authorizing invariants — cannot be overridden by callers
    execution_performed: bool = False
    authorization_granted: bool = False
    private_reasoning_exposed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "execution_performed", False)
        object.__setattr__(self, "authorization_granted", False)
        object.__setattr__(self, "private_reasoning_exposed", False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "mode": str(self.mode),
            "composed_at": self.composed_at,
            "context_sources": list(self.context_sources),
            "decision_notes": list(self.decision_notes),
            "warnings": list(self.warnings),
            "execution_performed": self.execution_performed,
            "authorization_granted": self.authorization_granted,
            "private_reasoning_exposed": self.private_reasoning_exposed,
        }


def compose_brain_trace(
    *,
    mode: BrainMode,
    context_sources: list[str] | None = None,
    decision_notes: list[str] | None = None,
    warnings: list[str] | None = None,
) -> BrainTrace:
    """Compose a BrainTrace for the current turn.

    Safe to call in any mode — produces a structural record only.
    Never calls an LLM, executes an action, or authorizes a capability.
    """
    return BrainTrace(
        trace_id=f"BT-{uuid4().hex[:8].upper()}",
        mode=mode,
        composed_at=datetime.now(timezone.utc).isoformat(),
        context_sources=tuple(context_sources or []),
        decision_notes=tuple(decision_notes or []),
        warnings=tuple(warnings or []),
    )
