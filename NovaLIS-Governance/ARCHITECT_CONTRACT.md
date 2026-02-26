\# NovaLIS Architect Contract



Status: Active Governance Artifact  

Scope: Repository Structural \& Authority Invariants  

Enforcement: CI-Validated  



---



\## 1. Constitutional Supremacy



The single source of truth for Nova is:



NOVA COMPLETE CONSTITUTIONAL BLUEPRINT 1.8.md



All architectural decisions, code structure, and execution behavior must conform to this document.



If any implementation contradicts the Blueprint, the Blueprint prevails.



---



\## 2. Intelligence–Authority Separation



Nova enforces a strict separation between:



\- Intelligence (analysis, reasoning, formatting, conversation)

\- Authority (execution, external effects, state mutation)



Execution authority is granted only through the Governor.



No module may directly execute system, network, or TTS actions outside the Governor.



---



\## 3. Governor Supremacy



All executable capabilities must:



\- Be registered in `src/config/registry.json`

\- Route through `Governor.handle\_governed\_invocation`

\- Pass ExecuteBoundary validation

\- Be logged to the immutable ledger



No direct executor imports are permitted in conversation, skill, or frontend layers.



---



\## 4. Phase Discipline



Phase status is binding.



\- Phase 3.5: Sealed

\- Phase 4: Governed Execution only

\- Future phases require explicit constitutional unlock artifacts



No implementation may exceed the current phase authority scope.



---



\## 5. Repository Structural Invariants



The following must always exist at repository root:



\- REPO\_MAP.md

\- CONTRIBUTING.md

\- NovaLIS-Governance/



These artifacts define governance surface and prevent structural drift.



---



\## 6. CI Enforcement



Governance checks in `.github/workflows/governance-check.yml` act as:



\- Structural firewall

\- Authority boundary verification

\- Artifact presence enforcement



CI must remain enabled and passing before any merge.



---



End of Architect Contract.

