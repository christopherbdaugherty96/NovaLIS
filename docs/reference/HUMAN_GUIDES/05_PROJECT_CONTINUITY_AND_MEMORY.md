# Project Continuity and Memory
Updated: 2026-03-25

## Why This Part Matters
A lot of AI systems can answer one prompt well.
Very few can help you continue real work across time.

This is where Nova starts to feel different.

Nova now supports five closely related ideas:
- working context
- project continuity threads
- governed memory
- calm scheduling
- opt-in pattern review

They are connected, but they are not the same thing.

For the current repository state, this trust-facing Phase-5 package is closed as a real runtime layer, and the explicit memory surface has since become stronger on top of that baseline.

## 1. Working Context
Working context is the short-term picture of what is happening right now.

It can include things like:
- the active app
- the active page
- the visible object or file
- the current task
- the last relevant turn

Working context helps Nova understand follow-ups such as:
- `help me do it`
- `what should I click next?`
- `explain this`

Working context is not the same as long-term memory.
It is session-scoped and task-oriented.

## 2. Project Continuity Threads
Threads let Nova help with ongoing work inside the current workspace session.

A thread can carry things like:
- project name
- current goal
- latest blocker
- health state
- latest decision
- recent changes
- linked memory

Important boundary:
- the live thread surface is session-scoped
- durable continuity across sessions comes from governed memory and the thread-memory bridge

This means Nova can answer questions like:
- `continue my deployment issue`
- `project status deployment issue`
- `biggest blocker in deployment issue`
- `which project is most blocked right now`
- `thread detail deployment issue`

The thread map and thread detail view make Nova feel more like a workspace than a chat transcript.

## 3. Governed Memory
Memory in Nova is explicit and governed.

That means:
- the user chooses what to save
- the memory system is visible and inspectable
- deletion and edit flows require the appropriate explicit action or confirmation
- persistence is not supposed to happen silently

This is different from systems that quietly absorb everything into hidden memory.

Nova's memory model is closer to:
- deliberate filing
- durable project context
- explicit preservation of decisions and artifacts

Nova can show a governed memory overview so the user can inspect:
- how many durable items exist
- how many are active, locked, or deferred
- how those items are split across general, project, and ops scopes
- which threads have linked memory
- what was saved most recently

Nova also gives governed memory its own dedicated dashboard page so this review surface does not have to compete with the Home-page cards.

## 4. The New Explicit Save / Remember Layer
Nova now has a stronger everyday memory layer on top of the older memory-overview surface.

This means Nova can now handle natural flows like:
- `save this`
- `remember this`
- `remember this: Client supplies alcohol; Pour Social does not sell alcohol.`
- `list memories`
- `show that memory`
- `edit that memory: <updated text>`
- `delete that memory`

Important boundary:
- this is still explicit
- Nova does not autosave
- Nova does not silently convert ordinary chat into memory
- destructive or mutating changes still require clear user action

## 5. The Thread-Memory Bridge
One of the most important continuity changes is the bridge between threads and governed memory.

This means Nova can preserve:
- thread snapshots
- thread decisions
- durable thread-linked memory history

Examples:
- `memory overview`
- `memory save thread deployment issue`
- `memory save decision for deployment issue: inspect PYTHONPATH first`
- `memory list thread deployment issue`

This matters because a project is not just a series of notes.
It is also:
- decisions
- rationale
- blockers
- preserved progress

## 6. Bounded Relevant Memory Use
Nova can now use clearly relevant explicit memory as a bounded chat aid.

That means:
- a memory that directly matches the current question may be used as a small context hint
- unrelated questions do not automatically drag in saved memory
- memory remains separate from Nova's identity or personality

This is a very important trust boundary.
Nova is supposed to feel helpful, not creepy.

## 7. What This Feels Like In Practice
A realistic Nova continuity flow now looks like this:
- you continue a thread
- Nova shows the current blocker and latest decision
- you save a new decision
- the thread's memory count increases
- you ask for `memory overview`
- Nova shows the current durable memory state and linked threads
- later you ask a directly related question
- Nova can use the clearly relevant saved memory without pretending it remembers everything

That is the beginning of a real personal continuity system.

## 8. The Big Difference Between Context, Threads, and Memory
The easiest way to understand them is this:

Working context:
- what is happening right now

Thread continuity:
- what is happening in this project in the current workspace session

Governed memory:
- what the user explicitly chose to preserve across time

Together, these three layers let Nova feel more coherent without becoming hidden or uncontrolled.

## 9. Calm Scheduling
Phase 5 also includes explicit scheduling for daily briefs and reminders.

This is not meant to make Nova proactive in a hidden way.
It is meant to make Nova easier to live with day to day while keeping the same governance model.

What the user can do:
- schedule a daily brief
- create a one-time reminder
- create a daily reminder
- inspect current schedules
- inspect notification policy settings
- set quiet hours
- set a notification rate limit
- reschedule schedules
- dismiss due items
- cancel schedules they no longer want

Important boundary:
- schedules are explicit
- schedules are inspectable
- schedules are cancellable
- scheduled items do not auto-run actions on the user's behalf

## 10. Pattern Review
Phase 5 also includes an explicit pattern-review layer for ongoing work.

This is not hidden behavior.
Nova only generates pattern proposals after the user opts in and explicitly asks for a review.

What Nova can propose:
- a blocked thread without a next step
- a repeated blocker theme across threads
- durable context that may still need a clearer saved decision

Important boundary:
- pattern review is opt-in
- proposals are advisory
- proposals are discardable
- no proposal executes anything automatically