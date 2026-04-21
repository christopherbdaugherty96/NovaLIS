"""
NovaLIS Core Configuration (Phase 1)

This file defines explicit, intentional defaults for Nova’s
local-first, reliability-focused behavior.

Design principles:
- Deterministic
- Privacy-first
- No silent inference
- No background autonomy
"""

"""
NovaLIS Backend Configuration

Authoritative configuration for NovaLIS.
This file defines system identity, communication rules, and operational defaults.

NovaLIS is a local intelligence system.
Not a chatbot. Not a personality. Not a service.
"""


import os
import re
import logging
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from src.utils.persistent_state import runtime_root

# ==================== VERSION ====================

__version__ = "1.0.0"
__system_name__ = "NovaLIS"
__description__ = "Local Intelligence System"

# ==================== PATHS ====================

BASE_DIR = Path(__file__).resolve().parent
RUNTIME_ROOT = runtime_root(__file__)
DATA_DIR = RUNTIME_ROOT / "data"
LOG_DIR = RUNTIME_ROOT / "logs"
MODELS_DIR = RUNTIME_ROOT / "models"
MEMORY_DIR = RUNTIME_ROOT / "memory"

for d in (DATA_DIR, LOG_DIR, MODELS_DIR, MEMORY_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ==================== LOGGING ====================

logger = logging.getLogger("novalis.config")

# ==================== MODEL PROVIDER ====================

class ModelProvider(str, Enum):
    OLLAMA = "ollama"
    LOCAL_FILE = "local_file"
    DUMMY = "dummy"

def parse_model_provider(value: str) -> ModelProvider:
    v = (value or "").strip().lower()
    return (
        ModelProvider(v)
        if v in ModelProvider._value2member_map_
        else ModelProvider.OLLAMA
    )

MODEL_PROVIDER: ModelProvider = parse_model_provider(
    os.getenv("MODEL_PROVIDER", "ollama")
)

# ==================== GOVERNANCE ====================

#Execution authority must be structural, not config‑driven

# ==================== WEB SEARCH GOVERNANCE ====================
# Phase‑3.5: explicit, read‑only, user‑invoked online retrieval

WEB_SEARCH_ENABLED = os.getenv("WEB_SEARCH_ENABLED", "true").lower() == "true"

WEB_SEARCH_TRIGGERS = [
    "search for",
    "search the web for",
    "look up",
    "find online",
    "check online for",
]

WEB_SEARCH_MAX_RESULTS = 3

# Explicit online mode guard – future‑proofing for all online capabilities
ONLINE_ACCESS_ALLOWED = WEB_SEARCH_ENABLED

# ==================== OLLAMA ====================

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
OLLAMA_FALLBACK_MODEL = os.getenv("OLLAMA_FALLBACK_MODEL", "gemma4:e2b")
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "5m")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))

# ==================== SYSTEM PROMPT ====================
# Single source of truth: src/llm/system_prompt.py
# The LLM manager uses that module directly. This re-export exists so that
# any code importing from nova_config gets the same prompt.
# For conversation, general_chat.py builds a richer prompt (BASE_CONTRACT +
# tone + mode + self-awareness + memory) and passes it as system_prompt to
# the LLM gateway, which overrides this default.

from src.llm.system_prompt import SYSTEM_PROMPT  # noqa: F401

# ==================== COMMUNICATION PROFILES ====================

COMMUNICATION_PROFILES: Dict[str, Dict[str, Any]] = {
    "minimal": {
        "max_tokens": 256,
        "temperature": 0.3,
        "description": "Brief, factual output",
    },
    "balanced": {
        "max_tokens": 512,
        "temperature": 0.68,
        "description": "Clear, complete responses (default)",
    },
    "conversational": {
        "max_tokens": 512,
        "temperature": 0.75,
        "description": "Short, natural responses with a little more presence",
    },
    "detailed": {
        "max_tokens": 1024,
        "temperature": 0.72,
        "description": "Expanded explanations when explicitly requested",
    },
    "task_report": {
        "max_tokens": 384,
        "temperature": 0.55,
        "description": "Calm, compact task and briefing delivery",
    },
}

DEFAULT_PROFILE = os.getenv("DEFAULT_PROFILE", "balanced").lower()
if DEFAULT_PROFILE not in COMMUNICATION_PROFILES:
    DEFAULT_PROFILE = "balanced"

MAX_RESPONSE_TOKENS = COMMUNICATION_PROFILES[DEFAULT_PROFILE]["max_tokens"]
TEMPERATURE = COMMUNICATION_PROFILES[DEFAULT_PROFILE]["temperature"]

TOP_P = 0.9
FREQUENCY_PENALTY = 0.0
PRESENCE_PENALTY = 0.0

# ==================== SKILLS ====================

@dataclass
class SkillConfig:
    enabled: bool = True
    name: str = ""
    description: str = ""
    api_key: Optional[str] = None
    extra: Dict[str, str] = field(default_factory=dict)

# Locked ambient location
DEFAULT_LOCATION = os.getenv(
    "DEFAULT_LOCATION",
    "Ann Arbor, MI, USA"
)

SKILLS: Dict[str, SkillConfig] = {
    "weather": SkillConfig(
        name="Weather",
        description="Local weather information",
        api_key=os.getenv("WEATHER_API_KEY") or None,
        extra={
            "default_location": DEFAULT_LOCATION,
            "units": os.getenv("WEATHER_UNITS", "imperial"),
            "cache_seconds": "900",
        },
    ),
    "news": SkillConfig(
        name="News",
        description="Current headlines",
        api_key=os.getenv("NEWS_API_KEY") or None,
        extra={
            "max_items": "5",
        },
    ),
    "system": SkillConfig(
        name="System",
        description="System status and diagnostics",
    ),
}

# ==================== VOICE ====================

@dataclass
class VoiceSettings:
    enabled: bool = False
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 0.8

VOICE_SETTINGS = VoiceSettings()

# ==================== ORB ====================

@dataclass
class OrbSettings:
    enabled: bool = True
    reactivity: str = "subtle"
    animation_speed: float = 1.0
    ambient_presence: bool = True
    pulse_on_processing: bool = True

ORB_SETTINGS = OrbSettings()

# ==================== TONE SAFEGUARD ====================

def apply_tone_safeguard(text: str) -> str:
    """
    Final defensive pass to prevent tone violations.
    This should never replace the system prompt.
    """
    if not text:
        return text

    allowlist = (
        "Got it.",
        "Done.",
        "On it.",
        "Sure thing.",
        "Here's what I found.",
        "Worth noting:",
        "Heads up:",
        "One thing -",
    )
    if any(text.startswith(prefix) for prefix in allowlist):
        return text.strip()

    fillers = (
        "Sure!", "Absolutely!", "Of course!",
        "Happy to help!", "No problem!", "You're welcome!",
    )

    for f in fillers:
        if text.startswith(f):
            text = text[len(f):].lstrip()

    # Remove emojis conservatively
    text = re.sub(r"[^\x00-\x7F]+", "", text)

    return text.strip()

# ==================== PHASE-2 ACTION ALLOWLISTS ====================

ALLOWED_FOLDERS = {
    "downloads": r"C:\Users\Chris\Downloads",
    "documents": r"C:\Users\Chris\Documents",
}

ALLOWED_APPS = {
    "notepad": r"C:\Windows\System32\notepad.exe",
    "calculator": r"C:\Windows\System32\calc.exe",
}
