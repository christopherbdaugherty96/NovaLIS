# Baseline CI Unblock Reconciliation - 2026-06-08

Status: baseline CI hygiene only.

Scope: unblock baseline checks so PR #235 can be reviewed safely after it is
rebased or updated.

## Purpose

This workstream is separate from PR #235:

```text
PR #235 = Obsidian authority-tier overlay
this PR = baseline CI hygiene / blocker isolation
future PR = Second Brain Slice 1 implementation
```

It does not replace or start Second Brain Slice 1.

## Safe Fixes

Allowed baseline CI fixes in this lane:

```text
behavior-preserving Ruff cleanup
declaring dependencies already imported by existing code
documenting live-credential CI blockers
```

## Shopify Live P5 Boundary

Cap 65 Shopify P5 live tests require:

```text
NOVA_SHOPIFY_SHOP_DOMAIN
NOVA_SHOPIFY_ACCESS_TOKEN
```

When those secrets are absent, failing live P5 tests are a CI configuration or
repository-secret blocker. Missing credentials must not be treated as a live
proof pass.

This lane does not:

```text
fake Shopify live proof
remove live certification tests
weaken Cap 65 governance
change Cap 65 runtime behavior
change capability_locks.json
claim new certification evidence
```

## Preserved Boundaries

This work does not add:

```text
runtime behavior expansion
capability changes
authority expansion
scheduler or background loop
OpenClaw integration
API, MCP, vector DB, or dashboard graph
Second Brain runtime implementation
external writes
```

## Follow-Up

After baseline CI hygiene and any required repository secret configuration are
handled, PR #235 should be rebased or updated and rerun. Only then should it be
marked ready for review.
