"""Tests for routine_graph.py — core RoutineGraph objects.

Four invariants under test:
  1. RoutineBlock and RoutineGraph validation (name/blocks required)
  2. RoutineRun and RoutineReceipt are frozen non-authorizing dataclasses
  3. execution_performed=False and authorization_granted=False are enforced,
     not settable by callers
  4. to_dict() output shape is correct and always emits False for auth fields
"""

from __future__ import annotations

import pytest

from src.routine.routine_graph import (
    RoutineBlock,
    RoutineGraph,
    RoutineReceipt,
    RoutineRun,
    _receipt_id,
    _run_id,
    _utc_now,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _block(name: str = "step_one") -> RoutineBlock:
    return RoutineBlock(name=name, description="Does something.", output_label="out")


def _graph(*names: str) -> RoutineGraph:
    blocks = tuple(_block(n) for n in (names or ("step_one",)))
    return RoutineGraph(name="test_graph", blocks=blocks)


def _run(**kwargs) -> RoutineRun:
    defaults: dict = {
        "run_id": "RUN-ABCD1234",
        "graph_name": "test_graph",
        "started_at": "2026-05-03T10:00:00+00:00",
        "completed_at": "2026-05-03T10:00:01+00:00",
        "blocks_run": ("step_one",),
        "outputs": {},
        "warnings": (),
    }
    defaults.update(kwargs)
    return RoutineRun(**defaults)


def _receipt(**kwargs) -> RoutineReceipt:
    defaults: dict = {
        "receipt_id": "RR-ABCD1234",
        "run_id": "RUN-ABCD1234",
        "graph_name": "test_graph",
        "completed_at": "2026-05-03T10:00:01+00:00",
        "blocks_run": ("step_one",),
        "sources_consulted": ("memory",),
        "warnings": (),
    }
    defaults.update(kwargs)
    return RoutineReceipt(**defaults)


# ---------------------------------------------------------------------------
# RoutineBlock
# ---------------------------------------------------------------------------

def test_routine_block_creates():
    b = RoutineBlock(name="gather_memory", description="Load memory.", output_label="memory_items")
    assert b.name == "gather_memory"
    assert b.output_label == "memory_items"


def test_routine_block_empty_name_raises():
    with pytest.raises(ValueError, match="name must not be empty"):
        RoutineBlock(name="", description="x", output_label="out")


def test_routine_block_empty_output_label_raises():
    with pytest.raises(ValueError, match="output_label must not be empty"):
        RoutineBlock(name="step", description="x", output_label="")


def test_routine_block_is_frozen():
    b = _block()
    with pytest.raises((AttributeError, TypeError)):
        b.name = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# RoutineGraph
# ---------------------------------------------------------------------------

def test_routine_graph_creates():
    g = _graph("step_one", "step_two")
    assert g.name == "test_graph"
    assert len(g.blocks) == 2


def test_routine_graph_empty_name_raises():
    with pytest.raises(ValueError, match="name must not be empty"):
        RoutineGraph(name="", blocks=(_block(),))


def test_routine_graph_empty_blocks_raises():
    with pytest.raises(ValueError, match="at least one block"):
        RoutineGraph(name="g", blocks=())


def test_routine_graph_block_names():
    g = _graph("alpha", "beta", "gamma")
    assert g.block_names == ("alpha", "beta", "gamma")


def test_routine_graph_is_frozen():
    g = _graph()
    with pytest.raises((AttributeError, TypeError)):
        g.name = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# RoutineRun — non-authorizing invariants
# ---------------------------------------------------------------------------

def test_routine_run_execution_performed_always_false():
    run = _run(execution_performed=True)
    assert run.execution_performed is False


def test_routine_run_authorization_granted_always_false():
    run = _run(authorization_granted=True)
    assert run.authorization_granted is False


def test_routine_run_is_frozen():
    run = _run()
    with pytest.raises((AttributeError, TypeError)):
        run.execution_performed = True  # type: ignore[misc]


def test_routine_run_empty_run_id_raises():
    with pytest.raises(ValueError, match="run_id must not be empty"):
        _run(run_id="")


def test_routine_run_to_dict_shape():
    run = _run(warnings=("no_memory_items",))
    d = run.to_dict()
    assert d["execution_performed"] is False
    assert d["authorization_granted"] is False
    assert d["run_id"] == "RUN-ABCD1234"
    assert d["graph_name"] == "test_graph"
    assert d["blocks_run"] == ["step_one"]
    assert d["warnings"] == ["no_memory_items"]
    assert isinstance(d["outputs"], dict)


def test_routine_run_to_dict_auth_fields_are_always_false():
    # Even if somehow a caller tried to pass True, to_dict always emits False
    run = _run()
    d = run.to_dict()
    assert d["execution_performed"] is False
    assert d["authorization_granted"] is False


def test_routine_run_to_dict_outputs_is_deep_copy():
    # Mutating to_dict() output must not affect the original
    run = _run(outputs={"key": "value"})
    d = run.to_dict()
    d["outputs"]["key"] = "mutated"
    assert run.outputs["key"] == "value"


# ---------------------------------------------------------------------------
# RoutineReceipt — non-authorizing invariants
# ---------------------------------------------------------------------------

def test_routine_receipt_execution_performed_always_false():
    r = _receipt(execution_performed=True)
    assert r.execution_performed is False


def test_routine_receipt_authorization_granted_always_false():
    r = _receipt(authorization_granted=True)
    assert r.authorization_granted is False


def test_routine_receipt_is_frozen():
    r = _receipt()
    with pytest.raises((AttributeError, TypeError)):
        r.execution_performed = True  # type: ignore[misc]


def test_routine_receipt_empty_receipt_id_raises():
    with pytest.raises(ValueError, match="receipt_id must not be empty"):
        _receipt(receipt_id="")


def test_routine_receipt_empty_run_id_raises():
    with pytest.raises(ValueError, match="run_id must not be empty"):
        _receipt(run_id="")


def test_routine_receipt_to_dict_shape():
    r = _receipt(sources_consulted=("memory", "receipts"), warnings=())
    d = r.to_dict()
    assert d["receipt_id"] == "RR-ABCD1234"
    assert d["run_id"] == "RUN-ABCD1234"
    assert d["graph_name"] == "test_graph"
    assert d["sources_consulted"] == ["memory", "receipts"]
    assert d["warnings"] == []
    assert d["execution_performed"] is False
    assert d["authorization_granted"] is False


# ---------------------------------------------------------------------------
# ID / timestamp helpers
# ---------------------------------------------------------------------------

def test_run_id_format():
    rid = _run_id()
    assert rid.startswith("RUN-")
    assert len(rid) == 12  # "RUN-" + 8 hex chars


def test_receipt_id_format():
    rid = _receipt_id()
    assert rid.startswith("RR-")
    assert len(rid) == 11  # "RR-" + 8 hex chars


def test_run_ids_are_unique():
    ids = {_run_id() for _ in range(20)}
    assert len(ids) == 20


def test_receipt_ids_are_unique():
    ids = {_receipt_id() for _ in range(20)}
    assert len(ids) == 20


def test_utc_now_is_iso_string():
    ts = _utc_now()
    assert "T" in ts
    assert "+" in ts or "Z" in ts or ts.endswith("00:00")
