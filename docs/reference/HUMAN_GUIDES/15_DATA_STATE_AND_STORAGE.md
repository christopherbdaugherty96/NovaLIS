# Data, State, and Storage
Updated: 2026-03-13

## Purpose
This guide explains where Nova stores important runtime state and what kind of state it is.

## Big Idea
Nova has different kinds of state, and they should not all be treated the same way.

The most important categories are:
- session-only state
- local runtime data
- governed persistent memory
- append-only ledger history
- generated runtime documentation

## 1. Session-Scoped State
Some Nova state is meant to exist only during an active session.

Examples:
- current working context
- active thread context in memory
- recent dashboard interaction state
- request-time context snapshots
- session analysis documents

This kind of state is useful, but it is not the same thing as long-term preserved memory.

## 2. Ledger Storage
Nova's append-only ledger is stored at:
- `nova_backend/src/data/ledger.jsonl`

This is the main event trail for governed behavior.

It is used to record things like:
- action attempts
- action completion
- network calls
- memory lifecycle events
- perception events

## 3. Governed Memory Storage
Governed memory is stored in a persistent JSON file at:
- `nova_backend/src/data/nova_state/memory/items.json`

This is where explicit long-term memory items live.

Examples of what may be preserved there:
- saved decisions
- durable project context
- explicit memory items created by the user

## 4. Story Tracker Storage
The story tracker stores its local files under:
- `nova_backend/nova_workspace/story_tracker/`

That area is used for things like:
- tracked topics
- story graph data
- stored snapshots of tracked stories

## 5. Project Threads
Project threads are currently session-scoped rather than long-term persistent by default.

That means a thread is best understood as:
- continuity state for ongoing work
- not automatically durable memory unless the user explicitly bridges it into governed memory

## 6. Runtime Documentation
Generated runtime docs live under:
- `docs/current_runtime/`

These are the operational truth surfaces that describe what the live system currently exposes.

## 7. Why This Separation Matters
The separation between these storage types is important.
It prevents Nova from blurring together:
- temporary task context
- ongoing work continuity
- durable memory
- audit history

That separation is a major part of Nova's trust model.
