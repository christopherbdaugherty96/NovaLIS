# Second Brain Implementation Blueprint

Status: future implementation handoff / not runtime truth.

This folder turns the Second Brain contracts and Obsidian vault scaffold into a build-ready implementation packet.

It does not add runtime code. It describes the exact future modules, tests, fixtures, data boundaries, and acceptance gates needed once a reviewed priority lock authorizes implementation.

---

## Build Order

```text
01 schemas
02 markdown parser / health
03 deterministic projection index
04 read-only query surface
05 context bridge
06 append-only event feed
07 proposal-only writes
08 living dashboard graph
```

---

## Hard Boundary

```text
Knowledge is context.
Memory is not permission.
The vault is not a receipt ledger.
The dashboard is not an approval surface.
```

Future implementation must remain non-authorizing unless a separate governed capability path explicitly authorizes action.
