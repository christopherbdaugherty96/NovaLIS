# Vault Structure

Status: Draft template
Date: 2026-06-08
Source: User-directed build prompt
Reason: Define an Obsidian structure that supports context without authority drift

## Authority Notice

This structure is a context template. It does not authorize Nova execution or
replace the repo's current priority and runtime truth.

## Root Layout

```text
00_HOME/
01_CURRENT_PRIORITY/
02_PROJECTS/
03_BUSINESS/
04_DECISIONS/
05_AI_HANDOFFS/
06_OUTPUT_REVIEW/
07_ROADMAPS/
08_ARCHIVE/
```

## Nova Project Notes

```text
02_PROJECTS/NovaLIS/Nova Vision.md
02_PROJECTS/NovaLIS/Nova Governance Boundaries.md
02_PROJECTS/NovaLIS/Nova Current Runtime Truth.md
02_PROJECTS/NovaLIS/Nova Active Priority.md
02_PROJECTS/NovaLIS/Nova Decision Log.md
02_PROJECTS/NovaLIS/Nova Session Handoff.md
02_PROJECTS/NovaLIS/Nova Known Risks.md
02_PROJECTS/NovaLIS/Nova Deferred Work.md
```

## Business Project Notes

```text
03_BUSINESS/Auralis Digital Master Context.md
03_BUSINESS/RJ Print Master Context.md
03_BUSINESS/Lucid Creations Master Context.md
03_BUSINESS/Shopify Commerce Plan.md
03_BUSINESS/Printify Product Pipeline.md
03_BUSINESS/Business Operations Backlog.md
03_BUSINESS/AI Work Queue.md
```

## Required Metadata

Each note should include:

```text
Status:
Date:
Source:
Reason:
Authority Tier:
Review Required:
```

## Bridge Rule

Business needs do not automatically become Nova runtime requirements.

Required path:

```text
Business need
-> proposal
-> review
-> approved scope
-> branch/PR
-> tests/proof
-> merge
-> runtime/governance path if execution is involved
```
