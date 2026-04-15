\# Nova – Deep Code-Level Audit \& Execution Brief (2026-04-15)



\*\*Status:\*\* \*\*FROZEN – TACTICAL COMPANION TO MASTER\_ROADMAP.md\*\*

\*\*Role:\*\* Engineering hotspot map. Guidance for Tier 3 refactors.

\*\*Warning:\*\* Do not use this document to expand Tier 1 scope. Installer first.



\---



\## Executive Summary



A line-by-line static analysis of `christopherbdaugherty96/NovaLIS` confirms the strategic roadmap is \*\*exactly correct\*\*. There are no hidden architectural flaws. The friction preventing "product feel" is localized to specific implementation accretions documented here.



\---



\## Part 1: Verified Technical Debt (Code-Level Evidence)



| Issue | Location | Impact on Product |

| :--- | :--- | :--- |

| \*\*Intent Routing Monolith\*\* | `brain\_server.py` (\~L2100-2190) | Hardcoded regex makes the system feel rigid and unchangeable. |

| \*\*God Object\*\* | `session\_handler.py` (3821 lines) | High risk of regression; changes to memory risk breaking persistence. |

| \*\*Missing Python Packaging\*\* | Root directory (no `pyproject.toml`) | Prevents `pip install`; blocks clean installer creation. |

| \*\*Frontend Duplication\*\* | `Nova-Frontend-Dashboard/` vs `nova\_backend/static/` | Changes must be made twice; source of UI drift. |

| \*\*Fail-Silent Errors\*\* | `brain\_server.py` memory search block | User sees "No memories" when the vector store is actually broken. Erodes trust. |

| \*\*Scattered Action Logic\*\* | `actions/`, `agents/`, `api/routes/` | Unclear where to add `send\_email\_draft` (Tier 2.1). |



\---



\## Part 2: Surgical Refactor Guide (Do Not Execute Until Tier 3)



\*This section is for reference when splitting hot files. Ignore until Tier 1 and Tier 2 are complete.\*



\### 2.1 Priority Extraction Order



1\. \*\*IntentRouter Class\*\* (Extract from `brain\_server.py`)

&#x20;  - Move regex dictionary to `config/intents.yaml` or dedicated module.

&#x20;  - Benefit: Reduces main server file by \~200 lines immediately.



2\. \*\*MemoryService Class\*\* (Extract from `session\_handler.py`)

&#x20;  - Isolate vector store interaction and CRUD operations.

&#x20;  - Benefit: Enables better error handling and testing.



3\. \*\*Action Registry Standardization\*\*

&#x20;  - Define clear path: `nova\_backend/src/actions/governed/` for all new mutations.



\### 2.2 Minimal `pyproject.toml` Skeleton (Tier 1.4 Requirement)



```toml

\[build-system]

requires = \["setuptools>=61.0"]

build-backend = "setuptools.build\_meta"



\[project]

name = "novalis"

version = "0.1.0"

dependencies = \[

&#x20;   "fastapi",

&#x20;   "uvicorn",

&#x20;   # ... (extract from requirements.txt)

]



\[project.scripts]

nova-start = "nova\_backend.brain\_server:main"

