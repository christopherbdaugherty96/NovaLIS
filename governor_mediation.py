# nova_backend/src/governor_mediation.py
"""
NOVALIS GOVERNOR MEDIATION LAYER
Sole authority between intelligence and execution.
If this fails, system fails closed.
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum
import traceback

from .actions.action_request import ActionRequest
from .actions.action_result import ActionResult, ActionResultType
from .actions.action_types import ActionType
from .gates.confirmation_gate import ConfirmationGate
from .execution.execute_action import ExecuteBoundary
from .llm.llm_manager import LLMManager
from .skill_registry import SkillRegistry

logger = logging.getLogger(__name__)


class GovernorState(Enum):
    """Governor's finite state machine"""
    IDLE = "idle"                     # Awaiting input
    PARSING = "parsing"               # Determining intent
    CONFIRMING = "confirming"         # At confirmation gate
    EXECUTING = "executing"           # In execution boundary
    COMPLETE = "complete"             # Action finished
    FAILED = "failed"                 # Hard stop


class GovernorMediator:
    """
    The Governor. All execution flows through here.
    
    DESIGN RULES (LOCKED):
    1. No LLM output reaches execution without passing through governor
    2. One action per request, period
    3. State resets to IDLE after every action
    4. All failures fail closed (no fallback to direct execution)
    """
    
    def __init__(self, config):
        self.config = config
        self.state = GovernorState.IDLE
        self.current_request_id = None
        
        # Subordinate tools (stateless, replaceable)
        self.llm = LLMManager(config)
        self.confirmation_gate = ConfirmationGate(config)
        self.execute_boundary = ExecuteBoundary(config)
        self.skills = SkillRegistry(config)
        
        # Phase 2 allowed actions only
        self.phase2_actions = {ActionType.OPEN_FOLDER}
        
        logger.info("GovernorMediator initialized - Phase 2.1 enforcement active")
    
    def process_intent(self, user_input: str, context: Optional[Dict] = None) -> ActionResult:
        """
        Main entry point for all user intents.
        Returns ActionResult that MUST be honored by all downstream systems.
        """
        if context is None:
            context = {}
        
        # RESET STATE - One action per request
        self._reset_state()
        
        try:
            # 1. Parse intent (deterministic Phase 2 only)
            action_request = self._parse_intent_phase2(user_input)
            if not action_request:
                return ActionResult(
                    result_type=ActionResultType.REFUSAL,
                    message="Could not parse intent in Phase 2 mode"
                )
            
            # 2. Phase enforcement
            if not self._enforce_phase_restrictions(action_request):
                return ActionResult(
                    result_type=ActionResultType.REFUSAL,
                    message=f"Action {action_request.action_type} not permitted in Phase 2"
                )
            
            # 3. Confirm with user
            self.state = GovernorState.CONFIRMING
            if not self.confirmation_gate.confirm(action_request):
                return ActionResult(
                    result_type=ActionResultType.REFUSAL,
                    message="User declined confirmation"
                )
            
            # 4. Execute (single action boundary)
            self.state = GovernorState.EXECUTING
            result = self.execute_boundary.execute(action_request)
            
            # 5. Clean up and signal completion
            self.state = GovernorState.COMPLETE
            return result
            
        except Exception as e:
            self.state = GovernorState.FAILED
            logger.error(f"Governor failed: {e}\n{traceback.format_exc()}")
            return ActionResult(
                result_type=ActionResultType.FAILURE,
                message=f"Governor system failure: {str(e)}"
            )
    
    def _parse_intent_phase2(self, user_input: str) -> Optional[ActionRequest]:
        """
        Phase 2 intent parsing: deterministic only.
        No LLM, no probabilistic guessing.
        """
        # Simple keyword matching for Phase 2
        # This will be replaced in Phase 3 with proper normalization
        user_lower = user_input.lower().strip()
        
        # OPEN_FOLDER detection
        if "open folder" in user_lower or "show folder" in user_lower:
            # Extract path (simple for now)
            path = self._extract_path(user_lower)
            if not path:
                return None
            
            return ActionRequest(
                action_type=ActionType.OPEN_FOLDER,
                title="Open Folder",
                payload={"path": path}
            )
        
        # Phase 2: Only OPEN_FOLDER is supported
        return None
    
    def _extract_path(self, user_input: str) -> Optional[str]:
        """Simple path extraction for Phase 2"""
        # This is placeholder - will be replaced with proper parsing
        if "desktop" in user_input:
            return "~/Desktop"
        elif "documents" in user_input:
            return "~/Documents"
        return None
    
    def _enforce_phase_restrictions(self, action_request: ActionRequest) -> bool:
        """Enforce Phase 2 action whitelist"""
        return action_request.action_type in self.phase2_actions
    
    def _reset_state(self):
        """Ensure one action per request boundary"""
        self.state = GovernorState.IDLE
        self.current_request_id = None
        # Clear any execution context
        if hasattr(self.execute_boundary, 'reset'):
            self.execute_boundary.reset()
    
    def get_state(self) -> Dict[str, Any]:
        """Governor status for diagnostics"""
        return {
            "state": self.state.value,
            "phase": "2.1",
            "allowed_actions": list(self.phase2_actions),
            "active_request": self.current_request_id
        }


# Singleton Governor instance
_governor_instance = None

def get_governor(config) -> GovernorMediator:
    """Get the singleton Governor instance"""
    global _governor_instance
    if _governor_instance is None:
        _governor_instance = GovernorMediator(config)
    return _governor_instance