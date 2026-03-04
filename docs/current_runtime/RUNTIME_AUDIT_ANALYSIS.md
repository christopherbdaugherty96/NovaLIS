# Runtime Governance Audit Analysis (Phase 1)

## Scope and method

This Phase 1 audit is analysis-only and focuses on current runtime truth surfaces without changing execution behavior.

Reviewed areas:
- Capability registry and registry loader
- Governor mediation and execution gate path
- Network mediation enforcement
- DeepSeek bridge and LLM invocation paths
- Skill routing and skill registry behavior
- Runtime auditor and runtime snapshot generation
- Ledger writer and ledger call sites

## A–J governance audit findings

| Item | Finding | Evidence |
| --- | --- | --- |
| A) Capability definitions | Capabilities are defined in `nova_backend/src/config/registry.json` and validated/loaded by `CapabilityRegistry` (`src/governor/capability_registry.py`). Required fields currently include id, name, status, phase_introduced, risk_level, data_exfiltration, enabled. | `registry.json`, `capability_registry.py` |
| B) Authority class representation | No explicit `authority_class` field exists in the runtime registry schema or `Capability` dataclass. Authority is implicit via risk level + invocation type. | `registry.json`, `capability_registry.py` |
| C) Mediator route mapping | Natural-language route mapping is implemented in `GovernorMediator.parse_governed_invocation` with deterministic regex -> capability IDs (16/17/18/19/20/21/22/32/48). | `src/governor/governor_mediator.py` |
| D) Execution gate enforcement | Global execution gate is `GOVERNED_ACTIONS_ENABLED` checked through `ExecuteBoundary.allow_execution()`, enforced in `Governor.handle_governed_invocation`. | `src/governor/execute_boundary/execute_boundary.py`, `src/governor/governor.py` |
| E) NetworkMediator enforcement | Networked execution routes use governor-injected `NetworkMediator`; it enforces capability enabled check, rate limit, URL validation, DNS/private IP checks, timeout, and ledger logging. | `src/governor/network_mediator.py`, `src/governor/governor.py`, networked executors |
| F) DeepSeekBridge LLM invocation | `DeepSeekBridge.analyze()` directly imports and calls `ollama.chat(...)` (model `phi3:mini`), not `LLMManager.generate()`. | `src/conversation/deepseek_bridge.py` |
| G) Skills → capabilities mapping | No explicit runtime map currently exists. Governed capabilities are invoked by `GovernorMediator` path; non-governed skills in `SkillRegistry` use direct skill handlers. `GeneralChatSkill` can escalate to analysis-only DeepSeek path (non-capability). | `src/brain_server.py`, `src/skill_registry.py`, `src/skills/general_chat.py` |
| H) Ledger logging locations | Ledger appends in `LedgerWriter.log_event`. Current runtime calls include governor action lifecycle events and network mediator success/failure events; model update events are in `LLMManager`. | `src/ledger/writer.py`, `src/governor/governor.py`, `src/governor/network_mediator.py`, `src/llm/llm_manager.py` |
| I) Escalation policy runtime representation | Escalation policy exists in `EscalationPolicy` (thresholds + decisions `ALLOW_ANALYSIS_ONLY`/`DENY`/`ASK_USER`) and is used by `GeneralChatSkill`, but not surfaced in runtime snapshot markdown. | `src/conversation/escalation_policy.py`, `src/skills/general_chat.py`, `src/audit/runtime_auditor.py` |
| J) Runtime fingerprint (commit hash) | No git commit hash is currently included in `CURRENT_RUNTIME_STATE.md`; snapshot currently includes generated timestamp + status fields only. | `src/audit/runtime_auditor.py` |

## Existing runtime snapshot coverage

Current snapshot generation (`write_current_runtime_state_snapshot`) includes:
- generated timestamp
- overall audit status
- execution gate boolean
- enabled/disabled capability ID lists
- capability table (`id`, `name`, `enabled`, `status`, `risk_level`, `data_exfiltration`)
- mediator mapped capability IDs
- discrepancy list

Current runtime-truth JSON audit includes:
- registry/runtime-doc enabled set comparison
- mediator mapped IDs from explicit probes
- execution gate signal
- model path signal (`deepseek_uses_ollama_chat_directly`)
- discrepancies with warning/hard_fail levels

## Missing governance visibility surfaces

The following governance/introspection surfaces are currently missing from runtime snapshot output:
- Capability Governance Matrix fields:
  - explicit `authority_class`
  - `confirmation_required`
  - `network_access`
  - explicit execution layer classification
- Governor enforcement summary booleans (queue, timeout guard, DNS rebinding guard, ledger logging active, execution gate active)
- Network surface summary:
  - explicit capabilities that use `NetworkMediator`
  - explicit direct LLM call detections in report body
  - explicit `ALLOW_ANALYSIS_ONLY` surface listing
- Deterministic skill/module → capability routing map
- Runtime fingerprint:
  - git commit hash
  - phase marker

## Current authority classification gaps

- No first-class runtime `authority_class` metadata exists in registry schema or runtime markdown.
- `risk_level` is not equivalent to authority class and does not encode speech-only vs execution vs analysis-only semantics.
- Confirmation policy is partially implied (`risk_level == "confirm"`) but not emitted as a normalized runtime field.

## Implicit bypass surfaces (observed)

- `DeepSeekBridge` directly calls `ollama.chat` and bypasses centralized `LLMManager` path.
- `GeneralChatSkill._run_local_model` also directly calls `ollama.chat` for local chat generation.
- These are non-capability conversational paths and are not currently represented in runtime snapshot governance sections.

## Nondeterministic path usage (observed)

- Runtime snapshot generation uses real-time timestamps (`datetime.now(timezone.utc)`), expected but non-reproducible per run.
- Network operations rely on live DNS resolution and outbound request outcomes in `NetworkMediator`.
- Runtime audit route depends on presence/absence and content freshness of generated markdown file.

## Confirmation: authority expansion status

Audit conclusion: **no explicit authority expansion is detected** in current Phase-4 runtime implementation.

Reasoning:
- Governed action execution remains constrained to known capability IDs routed through `Governor.handle_governed_invocation` and registry-enabled checks.
- No new capability IDs are introduced in current runtime code paths beyond those defined in registry.
- Analysis-only escalation (`ALLOW_ANALYSIS_ONLY`) is conversational output and does not auto-execute governed capabilities.

## Phase 2 implementation guidance (derived from audit)

To satisfy required structural upgrade without behavior changes:
1. Extend runtime snapshot rendering only, derived from current runtime truth.
2. Add deterministic derived classification fields (authority/network/execution-layer) without editing capability logic.
3. Add read-only runtime introspection helpers for governor/network/deepseek/skill routing surfaces.
4. Add tests validating rendered sections and required detections.

No runtime execution semantics should be changed for this upgrade.
