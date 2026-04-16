# Introduction to Nova

Nova is a **local, governed intelligence system**. It helps you think,
research, and act on your own computer — without sending your data to
anyone else's servers and without taking actions you did not approve.

This document is written for non-engineers. For the technical deep
dive, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## What problem does Nova solve?

Most AI assistants today are either:

- **Cloud-hosted**, meaning your conversations, files, and habits leave
  your machine and are logged on someone else's infrastructure; or
- **Ungoverned**, meaning when they do act on your behalf they may take
  surprising, irreversible, or opaque steps.

Nova is the opposite: it runs **locally**, and it only takes action
through a visible, auditable path.

## The governance philosophy

Nova's guiding rule is one sentence:

> **Intelligence may expand. Authority may not expand without explicit
> unlock.**

Practically, this means:

- Nova can **read, reason, summarise, and suggest** freely.
- Nova can **act on the local machine** only through a small registry
  of approved capabilities (volume, brightness, open website, etc.).
- Nova currently has **zero external-write capabilities** — it will not
  send an email, post a message, or change a calendar without a future
  explicit capability being built, registered, and unlocked.
- Every real action is written to an **append-only ledger** so you can
  review exactly what happened, when, and why.

## What Nova can do today

- **Chat** with a local LLM hosted by [Ollama](https://ollama.com).
- **Research** — fetch web content and summarise it (with an API key
  you provide).
- **Remember** — durable, user-controlled memory of your projects and
  preferences, with confirmation before storing.
- **Local controls** — open a website, read text aloud, adjust volume,
  switch the media track, change screen brightness, open a file or
  folder.
- **Second opinion** — a separate advisory lane that reviews answers
  without ever being able to act on its own.

## What Nova does **not** yet do

Nova is honest about its limits. As of today:

- **No email sending.** No calendar writes. No file-content writes.
- **No mobile or remote access.** Local machine only.
- **No voice wake-word.** Voice is an early preview.
- **No cloud sync** between devices.

These are on the roadmap, but each one has to be built as a governed
capability — not bolted on.

## Privacy model

- Your conversations, memory, and ledger are stored on your machine.
- The only time data leaves your computer is if **you** invoke a
  capability that requires the network (web search, downloading an
  Ollama model, fetching a page). Each such call is recorded.
- Nova has no telemetry. It does not phone home.

## Who is Nova for?

- People who want an assistant that **does not watch them**.
- People who need to **trust** the software acting on their behalf,
  because they can see what it did.
- People who prefer **local, owned software** over rented cloud tools.

## Next steps

- [Quick start](../README.md#quick-start)
- [Architecture](ARCHITECTURE.md) — for the technical details
- [Roadmap](../4-15-26%20NEW%20ROADMAP/MasterRoadMap.md) — for where
  Nova is going
