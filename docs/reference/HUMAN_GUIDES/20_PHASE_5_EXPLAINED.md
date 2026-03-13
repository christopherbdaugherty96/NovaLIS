# Phase 5 Explained
Updated: 2026-03-13

## What Phase 5 Is
Phase 5 is the part of Nova that turns short-lived help into durable, governed continuity.

It is the layer that lets Nova:
- remember explicit things you ask it to preserve
- keep track of project threads during the current workspace session
- show what is blocked and what changed
- let you control response style without changing authority
- surface your own reminders and scheduled updates
- review repeated work patterns only when you opt in

## What Phase 5 Is Not
Phase 5 is not:
- hidden personalization
- background memory collection
- autonomous reminders based on observation alone
- silent adaptation
- an unlock for delegated autonomy

## The Everyday Meaning
Before Phase 5, Nova could help in a moment.
With Phase 5, Nova can help across a longer stretch of work.
It does that through a combination of session-scoped thread continuity and durable governed memory.

That means a user can do things like:
- continue a project thread
- save a decision into memory
- review what is blocked
- check what Nova remembers
- tune how Nova answers in different domains
- create a daily brief or reminder
- review a suggested pattern without Nova acting on it automatically

## The Five Main Pieces

### 1. Governed memory
Memory is explicit, inspectable, and revocable.
Nova does not silently decide what should become durable memory.

### 2. Project continuity
Threads let Nova keep a stable picture of ongoing work in the current workspace session.
That includes blockers, decisions, health, and linked memory.

Durable cross-session continuity comes from governed memory, not from a hidden persistent thread store.

### 3. Response style control
Users can choose a global response style and domain-specific overrides.
This changes presentation, not authority.

### 4. User-directed scheduling
Schedules exist only because the user created them.
They can be reviewed, cancelled, rescheduled, rate-limited, and placed inside quiet hours.

### 5. Opt-in pattern review
Pattern review is advisory only.
It gives proposals for review; it does not auto-apply them.

## What Is Closed Now
For the current repository state, the trust-facing Phase-5 package is closed.

That closed package includes:
- memory
- continuity
- tone controls
- notification scheduling
- pattern review

## What Is Still Deferred
Some ideas are still intentionally outside the closed package.
The clearest current example is declarative identity/preferences.
That remains deferred until it gets its own separate design and approval path.

Other not-added tracks are deferred in:
- `docs/PROOFS/Phase-6/PHASE_6_DEFERRED_FROM_PHASE_5_2026-03-13.md`

## If You Want The Technical Version
Use:
- `docs/current_runtime/PHASE_5_RUNTIME_SURFACE.md`
- `docs/PROOFS/Phase-5/PHASE_5_IMPLEMENTATION_MAP_2026-03-13.md`
- `docs/PROOFS/Phase-5/PHASE_5_CLOSED_ACT_2026-03-13.md`
