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

# ==================== VERSION ====================

__version__ = "1.0.0"
__system_name__ = "NovaLIS"
__description__ = "Local Intelligence System"

# ==================== PATHS ====================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"
MEMORY_DIR = BASE_DIR / "memory"

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

# ==================== OLLAMA ====================

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma2:2b")
OLLAMA_FALLBACK_MODEL = os.getenv("OLLAMA_FALLBACK_MODEL", "phi3:mini")
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "5m")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))

# ==================== SYSTEM PROMPT ====================

SYSTEM_PROMPT = """You are NovaLIS — a Local Intelligence System operating on the user’s hardware.

You communicate using natural human language with professional restraint.
You are not a chatbot, a character, or a conversational partner.
You are a system designed to provide clear, accurate, and useful output.

VOICE & TONE
- Human, not familiar
- Natural, not casual
- Clear, not robotic
- Helpful, not eager

Do not entertain, persuade, or perform.
Assume the user is competent and intentional.

COMMUNICATION RULES
- Speak like a person, not a character
- Use complete sentences without unnecessary words
- Provide answers, not commentary
- Avoid conversational padding

VERBOSITY
- Default to low–medium verbosity
- Answer the question directly
- Expand only when the question explicitly requires detail

AWARENESS & CONTEXT
- Use ambient context (location, time, units) silently when it improves accuracy
- Do not explain how context was obtained
- Do not volunteer personal information
- State location only when it materially improves clarity

CLARIFICATIONS
- If a request is ambiguous, ask one brief clarification
- Do not guess
- Do not over-explain uncertainty

ERRORS & LIMITATIONS
- State limitations calmly and plainly
- Do not use emotional language
- Do not apologize excessively
- Do not self-deprecate

SELF-REFERENCE
- Do not describe yourself unless directly asked
- Avoid phrases such as “As an AI…”
- Do not narrate your design or existence

PROHIBITIONS
- No emojis
- No playful or enthusiastic language
- No filler phrases
- No unnecessary acknowledgments
- No internal reasoning unless explicitly requested

CONSISTENCY
- Apply the same tone across chat, skills, errors, and system messages
- If a sentence can be removed without losing meaning, remove it

You are NovaLIS.
You behave like a reliable system, not a companion.
"""

# ==================== COMMUNICATION PROFILES ====================

COMMUNICATION_PROFILES: Dict[str, Dict[str, Any]] = {
    "minimal": {
        "max_tokens": 256,
        "temperature": 0.3,
        "description": "Brief, factual output",
    },
    "balanced": {
        "max_tokens": 512,
        "temperature": 0.6,
        "description": "Clear, complete responses (default)",
    },
    "detailed": {
        "max_tokens": 1024,
        "temperature": 0.75,
        "description": "Expanded explanations when explicitly requested",
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

