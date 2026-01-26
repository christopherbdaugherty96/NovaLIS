"""
Nova Message Protocol v1 (NMPv1)

Standardized message formats for WebSocket communication between
Nova Backend and Nova Dashboard.

This version:
✔ Preserves original dataclass structures (ChatStart, ChatChunk, etc.)
✔ Adds NMPv1Message (unified message object)
✔ Adds NMPv1MessageType enum
✔ Adds parse_message() and serialize_message()
✔ Fully compatible with brain_server.py (streaming system)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


# ============================================================
# ENUM: Message Types (Official NMPv1)
# ============================================================

class NMPv1MessageType(str, Enum):
    CHAT = "chat"
    CHAT_START = "chat_start"
    CHAT_CHUNK = "chat_chunk"
    CHAT_DONE = "chat_done"
    CHAT_STOPPED = "chat_stopped"

    SKILL_RESPONSE = "skill_response"
    WIDGET_UPDATE = "widget_update"

    ORB_STATE = "orb_state"
    SYSTEM = "system"
    ERROR = "error"

    COMMAND = "command"
    STOP = "stop"


# ============================================================
# UNIFIED MESSAGE CLASS (Used by parser)
# ============================================================

@dataclass
class NMPv1Message:
    type: str
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    state: Optional[str] = None
    message: Optional[str] = None
    skill: Optional[str] = None
    widget: Optional[str] = None
    command: Optional[str] = None
    args: Optional[Dict[str, Any]] = None


# ============================================================
# ORIGINAL MESSAGE TYPES (You had these — keeping them)
# ============================================================

# ---------- Incoming From UI ----------

@dataclass
class ChatMessage:
    type: str
    content: str


@dataclass
class CommandMessage:
    type: str
    command: str


@dataclass
class StopMessage:
    type: str = "stop"


# ---------- Outgoing To Dashboard ----------

@dataclass
class ChatStart:
    type: str = "chat_start"


@dataclass
class ChatChunk:
    type: str = "chat_chunk"
    content: str = ""


@dataclass
class ChatDone:
    type: str = "chat_done"


@dataclass
class OrbState:
    type: str = "orb_state"
    state: str = "idle"


@dataclass
class SkillResponse:
    type: str = "skill_response"
    skill: str = "unknown"
    message: str = ""
    data: Optional[Dict[str, Any]] = None


@dataclass
class WidgetUpdate:
    type: str = "widget_update"
    widget: str = ""
    data: Optional[Dict[str, Any]] = None


@dataclass
class ErrorMessage:
    type: str = "error"
    message: str = ""


# ============================================================
# PARSING HELPERS
# ============================================================

def parse_message(raw: Dict[str, Any]) -> NMPv1Message:
    """
    Convert incoming WebSocket dict → unified NMPv1Message object.
    Safe for all message types.
    """
    return NMPv1Message(
        type=raw.get("type", ""),
        content=raw.get("content"),
        data=raw.get("data"),
        state=raw.get("state"),
        message=raw.get("message"),
        skill=raw.get("skill"),
        widget=raw.get("widget"),
        command=raw.get("command"),
        args=raw.get("args"),
    )


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def serialize_message(msg_type: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Convert Python values → dict ready for WebSocket send.
    Consistent with NMPv1 format.
    """
    payload = {"type": msg_type}
    payload.update(kwargs)
    return payload
