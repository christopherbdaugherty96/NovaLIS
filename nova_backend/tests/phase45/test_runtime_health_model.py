from src.runtime_health import resolve_runtime_health

HEALTHY_COMPONENTS = {
    "process_state": "running",
    "core_state": "available",
    "model_inference_state": "available",
    "resource_state": "healthy",
}


def test_http_timeout_beats_trust_normal():
    health = resolve_runtime_health(
        http_timed_out=True,
        websocket_state="open",
        trust_failure_state="Normal",
        **HEALTHY_COMPONENTS,
    )

    assert health.state == "Unavailable"
    assert "timed out" in health.what_happened
    assert "restart Nova" in health.what_next


def test_manual_turn_timeout_beats_working_state_without_claiming_completion():
    health = resolve_runtime_health(
        manual_turn_state="Timed Out",
        websocket_state="open",
        trust_failure_state="Normal",
        **HEALTHY_COMPONENTS,
    )

    assert health.state == "Degraded"
    assert "active turn timed out" in health.reason
    assert "may not have completed" in health.what_is_happening


def test_recovering_stays_visible_after_unavailable():
    health = resolve_runtime_health(
        recovering=True,
        websocket_state="open",
        trust_failure_state="Normal",
        **HEALTHY_COMPONENTS,
    )

    assert health.state == "Recovering"
    assert "Wait for Healthy" in health.what_next


def test_unknown_operator_health_does_not_become_healthy():
    health = resolve_runtime_health(
        operator_health_unknown=True,
        websocket_state="open",
        trust_failure_state="Normal",
        **HEALTHY_COMPONENTS,
    )

    assert health.state == "Connecting"
    assert "not refreshed" in health.reason


def test_trust_degraded_maps_to_canonical_degraded():
    health = resolve_runtime_health(
        websocket_state="open",
        trust_failure_state="Degraded",
        **HEALTHY_COMPONENTS,
    )

    assert health.state == "Degraded"
    assert health.what_next


def test_available_core_and_available_model_is_healthy():
    health = resolve_runtime_health(**HEALTHY_COMPONENTS)

    assert health.state == "Healthy"
    assert health.process_state == "running"
    assert health.core_state == "available"
    assert health.model_inference_state == "available"


def test_available_core_and_locked_model_is_degraded():
    health = resolve_runtime_health(
        **{**HEALTHY_COMPONENTS, "model_inference_state": "blocked"}
    )

    assert health.state == "Degraded"
    assert health.reason == "Local model inference is locked."


def test_available_core_and_unavailable_model_is_degraded():
    health = resolve_runtime_health(
        **{**HEALTHY_COMPONENTS, "model_inference_state": "unavailable"}
    )

    assert health.state == "Degraded"
    assert health.reason == "Local model inference is unavailable."


def test_core_runtime_failure_is_critical():
    health = resolve_runtime_health(
        **{**HEALTHY_COMPONENTS, "core_state": "unavailable"}
    )

    assert health.state == "Critical"
    assert "core" in health.reason.lower()


def test_missing_component_evidence_does_not_become_healthy():
    health = resolve_runtime_health()

    assert health.state == "Degraded"
    assert health.process_state == "unknown"
    assert health.core_state == "unknown"
    assert health.model_inference_state == "unknown"


def test_resource_pressure_is_degraded_not_core_critical():
    health = resolve_runtime_health(
        **{**HEALTHY_COMPONENTS, "resource_state": "critical"}
    )

    assert health.state == "Degraded"
    assert health.resource_state == "critical"
