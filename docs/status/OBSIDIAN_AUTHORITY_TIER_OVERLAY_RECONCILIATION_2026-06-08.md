# Obsidian Authority-Tier Overlay Reconciliation - 2026-06-08

Status: docs/tooling reconciliation.

Scope: generated Obsidian overlay navigation and stale continuity cleanup only.

## Purpose

This note reconciles the authority-tier overlay patch with the current accepted
Second Brain Slice 1 priority lock.

The current accepted implementation lane remains:

```text
Second Brain Slice 1:
schema
frontmatter parser
wikilink extraction
vault health/lint
no-mutation tests
non-authorizing tests
```

This overlay patch does not implement that lane.

## Why This Patch Is Safe

The authority-tier overlay is docs/tooling work. It makes the existing
repo-root Obsidian vault safer by ranking navigation surfaces before broad graph
exploration.

It generates:

```text
_MOCs/AUTHORITY_TIERS.md
```

and links it near the top of:

```text
_MOCs/HOME.md
```

The purpose is:

```text
truth rank before graph browsing
```

## Boundaries

This patch does not authorize or implement:

```text
runtime behavior changes
capability changes
capability_locks.json changes
memory authority
execution authority
MCP tools
REST or WebSocket query surfaces
dashboard graph
vector database
scheduler or background watcher
OpenClaw integration
browser/computer-use expansion
external writes
Second Brain runtime implementation
vault source mutation
```

## Relationship To Second Brain Slice 1

Second Brain Slice 1 remains separate and must stay within the accepted lock:

```text
schema/parser/wikilink/vault health-lint/no-mutation/non-authorizing tests only
```

The authority-tier overlay may help operators read the vault safely, but it is
not a knowledge index, memory layer, search surface, graph runtime, or execution
path.

## Final Rule

```text
Obsidian can help Nova understand.
Obsidian cannot authorize Nova to act.
Knowledge is context, not permission.
Generated runtime docs remain runtime truth.
```
