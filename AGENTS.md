# AGENTS.md

Guidance for AI agents working on NovaLIS.

Start here before editing the repo.

## Core Rule

Intelligence is not authority.

Nova's reasoning layers may clarify, plan, search, summarize, and propose. Runtime execution still goes through the Governor, capability registry, execution boundaries, and receipts.

## Current Priority

Read `.agent_context/current_priority.md`.

As of this Brain package, the active priority remains Cap 16 search reliability and conversation/search proof. Cap 64 P5 remains paused until that proof path is stable.

## Required Context Files

Read these before making brain/governance changes:

- `docs/brain.md`
- `docs/brain/README.md`
- `.agent_context/brain_loop.md`
- `.agent_context/environments.md`
- `.agent_context/governance.md`
- `.agent_context/current_priority.md`

## Do Not

- add execution capabilities without explicit request
- bypass GovernorMediator
- treat memory as permission
- claim conceptual docs are implemented runtime behavior
- mark Cap 64 or Cap 65 complete without live proof
- add Shopify writes or email sending under existing read/draft capabilities

## Repo Truth Rule

Generated runtime docs and implementation beat roadmap language.

When exact current status matters, verify against code and generated runtime truth.