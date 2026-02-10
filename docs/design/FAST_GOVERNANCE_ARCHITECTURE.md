> ## 🔒 PHASE-3.5 STATUS UPDATE — CLOSED
>
> **Phase-3.5 is formally COMPLETE and CLOSED.**  
> All Phase-3.5 acceptance criteria have been mechanically verified and CI-enforced, including execution quarantine, Governor containment, passive confirmation gating, and runtime refusal proofs.
>
> This document may reference Phase-3.5 as “active” for historical context only.  
> **No Phase-3.5 work remains open.** Phase-4 remains hard-locked pending a separate unlock artifact.
>
> **Authoritative closure record:** `docs/PHASE_3.5_CLOSURE.md`
-----------------------------------------------
ARCHITECTURAL PATTERN — NON-EXECUTING

This document describes governance performance principles.
It does not define Nova’s runtime behavior.
------------------------------------------------


Nova Fast Governance Architecture

Silent Execution, Explainable on Demand

Document ID: NOVA-ARCH-GOV-2024.1
Status: Canonical Architecture Pattern (Locked)
Phase Compatibility: 3.5 → 4.x (All Governor-based systems)
Authority: Architecture Council (Constitutional Amendment 4.9.1)
Effective: Immediate for all new governance implementations

---

1. Problem Statement

1.1 Current Industry Failure Pattern

AI systems conflate three concerns:

1. Execution (doing the task)
2. Governance (deciding what's allowed)
3. Explanation (justifying decisions)

This leads to:

· Latency penalty (200ms+ for safety checks)
· User frustration (lengthy refusals break flow)
· Trust erosion (verbose ≠ transparent)
· Architectural debt (mixed concerns, impossible to optimize)

1.2 Nova's Constraint

Must maintain:

· Provable governance (mathematically verifiable)
· Minimal latency (human-perceived as instant)
· Full auditability (any decision explained)
· Phase discipline (no capability leakage)

1.3 Hypothesis

Governance can be instant and silent without sacrificing safety or transparency, through architectural separation of concerns.

---

2. Core Insight (Canonical)

2.1 Separation of Concerns

```
Safety Check ≠ Explanation
Governance ≠ User Education
Permission ≠ Persuasion
```

2.2 Human Trust Patterns

· Initial trust: Through visible architecture (transparent design)
· Operational trust: Through consistency (predictable responses)
· Deep trust: Through availability (explanation when needed)

2.3 Key Realization

Systems earn trust by being reliable, not verbose.
OS kernels don't explain permissions—they enforce them.
Users only want explanation when something feels wrong.

---

3. Design Goal

3.1 Behavioral Contract

```
Default:    Fast → Silent → Confident
On Demand:  Detailed → Structured → Verifiable
```

3.2 Performance Targets (Non-Constitutional)

· Hot Path: Target sub-millisecond execution (optimized implementations aim for <0.1ms)
· Cold Path: Target <200ms explanation latency (when requested)
· Memory: Target compact decision representation
· Storage: Append-only audit log (immutable)

3.3 Anti-Goals

· ❌ No automated justification
· ❌ No preemptive explanation
· ❌ No pedagogical tone
· ❌ No moral reasoning in runtime

---

4. Architectural Model: Two-Plane Governor

4.1 System Overview

```
┌─────────────────────────────────────────────┐
│              User Request                    │
└─────────────────┬───────────────────────────┘
                  │
          ┌───────▼────────┐
          │   Hot Path      │ ◀─ Always runs
          │  (Governance)   │    • O(1) operations
          │                 │    • Bitmask checks
          │  Fast decision  │    • Minimal allocations
          └───────┬────────┘    • Deterministic
                  │
          ┌───────┴────────┐
          │   Decision      │
          │  Token (compact)│
          └───────┬────────┘
                  │
         ┌────────▼──────────┐
         │ Execute OR Refuse │
         └───────────────────┘
                  │
         ┌────────▼──────────┐
         │   Cold Path       │ ◀─ Only on demand
         │ (Explainability)  │    • Database lookups
         │                   │    • Rule expansion
         │  Explanations     │    • Structured output
         └───────────────────┘
```

4.2 Hot Path Specification

4.2.1 Characteristics

· Pure function (no side effects)
· Deterministic (same input → same output)
· Memory-safe (minimal allocations)
· Phase-agnostic (works for all phases)

4.2.2 Operations (Ordered)

1. Request classification → Capability ID
2. Phase validation → Current phase
3. Capability check → Allowed? (bool)
4. Rule matching → Rule ID if denied
5. Token generation → Decision hash

4.2.3 Key Properties

· Compact decision representation: Fixed-size token format
· Deterministic hashing: Same inputs produce same token
· Hash-based integrity: Token verifiable via hash

4.2.4 Performance Targets

· Latency: Designed for sub-millisecond execution (actual latency depends on runtime and hardware)
· Throughput: Target high throughput on capable hardware
· Memory: Target minimal resident memory
· CPU: Target low overhead per request

4.3 Cold Path Specification

4.3.1 Trigger Conditions

Only runs when user explicitly requests explanation:

· "Why?"
· "Explain that."
· "What rule blocked this?"
· "Show audit for [token]"

4.3.2 Operations

1. Token validation → Verify integrity
2. Decision lookup → Retrieve from audit log
3. Rule expansion → Convert rule ID → explanation
4. Context addition → Add phase, capability metadata
5. Format selection → Choose output format (raw/human/progressive)

4.3.3 Output Formats

```python
# Format 1: Raw Audit (Developers)
{
    "decision_hash": "a9f3c2...",
    "timestamp": "2024-01-15T10:30:00.123456Z",
    "phase": "3.5",
    "capability_requested": "EXTERNAL_ACTION",
    "capability_id": 0x0010,
    "allowed_mask": 0x000F,
    "rule_violated": "PHASE_3.5_ACTION_BLOCK",
    "rule_text": "External actions require Phase 4.1+",
    "rule_section": "4.1.2",
    "audit_trail": [...]
}

# Format 2: Human Explanation (Consumers)
{
    "summary": "That requires Phase 4.",
    "details": "I can't perform actions yet. That capability unlocks in Phase 4.",
    "suggestion": "You can continue using analysis and information features.",
    "unlock_condition": "Complete Phase 3.5 verification."
}

# Format 3: Progressive (Interactive Q&A)
{
    "tier_1": "That's not available yet.",
    "tier_2": "Action capabilities unlock in Phase 4.",
    "tier_3": "Phase 4 requires completing security verification.",
    "actions": ["View verification checklist", "See roadmap"]
}
```

4.3.4 Performance Requirements

· Latency: <200ms (acceptable for explanation)
· Storage: Append-only WAL (write-ahead log)
· Retention: 90 days minimum (configurable)
· Query: Efficient lookup by token hash

---

5. Implementation Roadmap

Phase 3.5 Implementation (Immediate)

```bash
nova/governance/
├── hot_path/
│   ├── capability_matrix.py     # Precomputed permissions
│   ├── decision_engine.py       # Core decision logic
│   ├── token_generator.py       # Deterministic hashing
│   └── tests/                   # Performance validation
│       ├── test_latency.py      # Validate speed targets
│       └── test_determinism.py  # Same input → same output
├── cold_path/
│   ├── explanation_engine.py    # Rule expansion
│   ├── audit_store.py           # Append-only log
│   ├── query_interface.py       # "Why?" handler
│   └── tests/
│       └── test_explanation.py  # Verify all rule IDs explained
└── integration/
    ├── governor_wrapper.py      # Hot+Cold path coordinator
    └── phase_transitions.py     # Matrix updates on phase change
```

Phase 4.1 Enhancements

· Multi-user support → User-specific capability matrices
· Temporal constraints → Time-of-day based permissions
· Resource limits → Rate limiting per capability
· Enterprise features → LDAP/SSO integration

Phase 4.2+ Extensions

· Parallel reasoning workers → Each worker gets governance check
· Swarm compatibility → Hot path coordinates multiple agents

---

6. Compatibility Matrix

6.1 Phase Support

Phase Hot Path Cold Path Notes
3.5 ✅ Full ✅ Basic Core implementation
4.1 ✅ Enhanced ✅ Advanced Temporal constraints
4.2 ✅ Parallel ✅ Multi-format Swarm support

6.2 System Requirements

· Python 3.10+ (type hints, performance)
· SQLite/PostgreSQL (audit storage)
· Redis (optional, for performance caching)
· Reasonable RAM (implementation-dependent)

---

7. Trust & Security Implications

7.1 Positive Impacts

· Transparency: Every decision has audit trail
· Predictability: Same request → same outcome
· Inspectability: Tokens can be verified independently
· Performance: Minimal latency overhead for safety

7.2 Security Considerations

· Token integrity: Hash-based verification (when correctly implemented)
· Audit log protection: Append-only, integrity-preserving
· Rule matrix verification: Validation of permission sets
· Phase transition controls: Formal approval required

7.3 Threat Model

Designed to prevent (given correct implementation):

· Governance bypass (single choke point)
· Rule tampering (signed matrices)
· Audit log modification (append-only design)
· Latency attacks (constant-time operations)

Implementation-dependent protections:

· Cryptographic guarantees depend on correct request canonicalization
· Trust roots and key management are implementation-defined

---

8. Testing & Validation

8.1 Mandatory Tests

```python
# 1. Determinism test
def test_hot_path_determinism():
    result1 = hot_path(identical_request)
    result2 = hot_path(identical_request)
    assert result1 == result2  # Byte-for-byte equality
    
# 2. Completeness test
def test_all_rules_explainable():
    for rule_id in ALL_RULE_IDS:
        explanation = cold_path.explain(rule_id)
        assert explanation is not None
        assert "human" in explanation
        assert "raw" in explanation
```

8.2 Continuous Validation

· Every commit: Determinism verification
· Every deployment: Rule matrix consistency check
· Weekly: Full explanation completeness audit
· Phase transition: Formal security review

---

9. Canonical Lock Points

9.1 Immutable Specifications

1. Hot path purity → No side effects, ever
2. Decision token compactness → Fixed-size, deterministic, hash-based
3. Audit log append-only → No modifications, no deletions
4. Rule matrix verification → Validation required
5. Phase transition process → Formal approval, no automation

9.2 Configurable Parameters

1. Cold path latency → Can increase with features
2. Audit retention period → 90 days default, configurable
3. Explanation formats → Can add new formats
4. Rule content → Can expand with new phases
5. Performance targets → Implementation-specific optimization

---

10. Swarm System Compatibility

10.1 Architecture Alignment

```
Traditional Swarm:
    Controller → [Worker1, Worker2, Worker3] → Aggregate → Response
    
Nova Swarm:
    Controller → Hot Path → [Worker1, Worker2, Worker3] → 
    Hot Path (aggregate) → Response
```

10.2 Key Differences

· Each worker receives governance check
· Aggregation passes through hot path
· Final decision gets single audit token
· Explanation covers entire decision chain

10.3 Implementation Note

Swarm reasoning enhances intelligence quality but does not change governance structure. Hot path remains single decision point.

---

11. Appendix: Reference Implementation Concepts

```python
# Conceptual hot path design
class HotPathEngine:
    """Hot path decision engine."""
    
    def __init__(self):
        self.capability_matrix = self._load_matrix()
        self.rule_table = self._load_rules()
        
    def decide(self, request: Request) -> Tuple[bool, DecisionToken]:
        """Main hot path entry point. Designed for speed."""
        # 1. Classify request → capability ID
        capability_id = self._classify_request(request)
        
        # 2. Check phase permissions
        current_phase = self._get_current_phase()
        allowed = self._check_permission(capability_id, current_phase)
        
        # 3. Determine rule ID (0 if allowed)
        rule_id = 0 if allowed else self._get_rule_id(capability_id, current_phase)
        
        # 4. Generate decision token
        token = self._generate_token(request, capability_id, rule_id, allowed)
        
        return allowed, token
```

Note: This reference implementation illustrates the architectural pattern. Exact byte layouts and performance characteristics are implementation-specific.

---

12. Document History

Version Date Changes Author
1.0 2024-01-15 Initial specification Architecture Council
1.1 2024-01-16 Added compatibility matrix Technical Committee
1.2 2024-01-17 Adjusted for audit feedback: clarified status, performance targets, security claims, phase compatibility Architecture Council

---

13. Signatories

Architecture Lead: _________________________
Security Review: _________________________
Phase Governance: _________________________

Verification:

· ✅ No autonomy added
· ✅ Governance boundaries preserved
· ✅ Phase discipline maintained
· ✅ Architectural separation of concerns maintained

---

Document Status: 🔒 LOCKED (Canonical Architecture Pattern)
Storage Path: /docs/canon/governance/fast-governance-architecture.md
Next Review: Only on Phase 4.1 unlock request
