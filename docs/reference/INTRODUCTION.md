# Introduction To Nova

Nova is a local, governed intelligence system. It helps you think, research, and act on your own computer without sending your data to someone else's servers by default and without taking actions you did not approve.

This document is written for non-engineers. For the technical deep dive, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## What Problem Does Nova Solve?

Most AI assistants today are either:

- **cloud-hosted**, meaning conversations, files, and habits leave your machine and are logged on someone else's infrastructure
- **ungoverned**, meaning tool use can feel surprising, irreversible, or opaque

Nova is built around a different promise: intelligence can help, but authority stays bounded and visible.

---

## The Governance Philosophy

Nova's guiding rule is:

> Intelligence may expand. Authority may not expand without explicit unlock.

Practically, this means:

- Nova can read, reason, summarize, and suggest.
- Nova can act on the local machine only through approved capabilities.
- External write-like workflows must be explicit, registered, governed, and user-confirmed.
- Nova can draft an email and open it in the local mail client, but the user reviews and sends manually.
- Every real action is written to an append-only ledger so you can review what happened, when, and why.

---

## What Nova Can Do Today

- Chat with a local LLM hosted by [Ollama](https://ollama.com).
- Fetch and summarize web content through governed network paths.
- Store durable, user-controlled memory with confirmation and management surfaces.
- Perform explicit local controls such as opening websites/folders, speaking text, volume, brightness, and media playback.
- Provide second-opinion review without giving the review lane execution authority.
- Run bounded OpenClaw and connector-backed intelligence workflows when configured.

For exact active capabilities, see [CURRENT_RUNTIME_STATE.md](../current_runtime/CURRENT_RUNTIME_STATE.md).

---

## What Nova Does Not Do By Default

Nova is honest about its limits:

- no autonomous email sending
- no broad calendar writes
- no broad file-content writes
- no hidden background screen capture loop
- no default cloud sync between devices

Broader actions must be added as governed capabilities, not bolted on.

---

## Privacy Model

- Conversations, memory, and ledger data are stored on your machine.
- Data leaves your computer only when you invoke a capability that requires network access.
- Networked capabilities are governed and should be visible in runtime/trust surfaces.
- Nova has no telemetry by default.

---

## Who Is Nova For?

- People who want an assistant that does not watch them.
- People who need to trust software acting on their behalf because they can inspect what it did.
- People who prefer local, owned software over rented cloud tools.
- Operators who want useful automation without hidden authority expansion.

---

## Next Steps

- [Quickstart](../../QUICKSTART.md)
- [Use cases](../../USE_CASES.md)
- [Architecture](ARCHITECTURE.md)
- [Roadmap](../../4-15-26%20NEW%20ROADMAP/MasterRoadMap.md)
