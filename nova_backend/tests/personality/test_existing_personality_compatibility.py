"""Compatibility tests verifying existing personality behavior is unchanged.

Phase 1A must not regress existing tone profiles, text cleanup,
authority replacement, or user-facing behavior.
"""
from __future__ import annotations

from pathlib import Path

from src.personality.interface_agent import PersonalityInterfaceAgent
from src.personality.nova_style_contract import NovaStyleContract
from src.personality.tone_profile_store import ToneProfileStore


def test_existing_authority_replacement_unchanged():
    agent = PersonalityInterfaceAgent()
    out = agent.present("I recommend that you restart the service.")
    lowered = out.lower()
    assert "i recommend" not in lowered
    assert "reasonable option" in lowered


def test_existing_emotional_dampening_unchanged():
    agent = PersonalityInterfaceAgent()
    out = agent.present("Don't worry, I'm here for you!")
    lowered = out.lower()
    assert "don't worry" not in lowered
    assert "i'm here for you" not in lowered


def test_existing_system_token_stripping_unchanged():
    agent = PersonalityInterfaceAgent()
    out = agent.present("Done. <function_call name='test'/> capability_id: 42")
    lowered = out.lower()
    assert "<function_call" not in lowered
    assert "capability_id" not in lowered


def test_existing_tone_profiles_unchanged():
    profiles = ToneProfileStore.PROFILE_DEFINITIONS
    assert "balanced" in profiles
    assert "concise" in profiles
    assert "detailed" in profiles
    assert "formal" in profiles


def test_existing_tone_domains_unchanged():
    domains = ToneProfileStore.DOMAIN_DEFINITIONS
    assert "general" in domains
    assert "system" in domains
    assert "research" in domains
    assert "daily" in domains
    assert "continuity" in domains


def test_existing_formal_profile_unchanged(tmp_path: Path):
    store = ToneProfileStore(tmp_path / "tone.json")
    store.set_global_profile("formal")
    agent = PersonalityInterfaceAgent(tone_store=store)
    out = agent.present("It's ready. Let's continue.")
    lowered = out.lower()
    assert "it's" not in lowered
    assert "it is" in lowered


def test_existing_style_contract_filler_removal():
    out = NovaStyleContract.normalize("Absolutely, here is the answer.")
    assert not out.lower().startswith("absolutely")


def test_existing_style_contract_inline_replacements():
    out = NovaStyleContract.normalize("I can absolutely do that for you gladly.")
    lowered = out.lower()
    assert "absolutely" not in lowered
    assert "gladly" not in lowered


def test_existing_personality_agent_class_exists():
    from src.personality.core import PersonalityAgent
    agent = PersonalityAgent()
    assert hasattr(agent, "run")
    assert hasattr(agent, "arm_deep_mode")
