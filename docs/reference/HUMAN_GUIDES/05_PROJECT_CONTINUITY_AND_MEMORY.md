# Project Continuity and Memory
Updated: 2026-03-13

## Why This Part Matters
A lot of AI systems can answer one prompt well.
Very few can help you continue real work across time.

This is where Nova starts to feel different.

Nova now supports three related ideas:
- working context
- project continuity threads
- governed memory
- manual response-style controls
- user-directed notification scheduling
- opt-in pattern review

They are connected, but they are not the same thing.

For the current repository state, this trust-facing Phase-5 package is closed as a real runtime layer.

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
Threads let Nova help with ongoing work over time.

A thread can carry things like:
- project name
- current goal
- latest blocker
- health state
- latest decision
- recent changes
- linked memory

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
- deletion and unlock flows require the appropriate explicit action
- persistence is not supposed to happen silently

This is different from systems that quietly absorb everything into hidden memory.

Nova's memory model is closer to:
- deliberate filing
- durable project context
- explicit preservation of decisions and artifacts

Nova can also show a governed memory overview so the user can inspect:
- how many durable items exist
- how many are active, locked, or deferred
- which threads have linked memory
- what was saved most recently

## 4. The Thread-Memory Bridge
One of the most important recent changes is the bridge between threads and governed memory.

This means Nova can now preserve:
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

## 5. What This Feels Like In Practice
A realistic Nova continuity flow now looks like this:
- you continue a thread
- Nova shows the current blocker and latest decision
- you save a new decision
- the thread's memory count increases
- you ask for `memory overview`
- Nova shows the current durable memory state and linked threads
- later you come back and Nova can show the durable context again

That is the beginning of a real personal continuity system.

## 6. The Big Difference Between Context, Threads, and Memory
The easiest way to understand them is this:

Working context:
- what is happening right now

Thread continuity:
- what is happening in this project over time

Governed memory:
- what the user explicitly chose to preserve across time

Together, these three layers let Nova feel more coherent without becoming hidden or uncontrolled.

## 7. Response Style Controls
Phase 5 now also includes a manual response-style layer built on Nova's presentation personality.

This means the user can explicitly inspect and change how Nova presents information without changing what Nova is allowed to do.

Current supported tone profiles:
- balanced
- concise
- detailed
- formal

Current supported domains:
- general chat
- system and diagnostics
- research and analysis
- weather/news/calendar
- projects, threads, and memory

Important boundary:
- these are explicit user-controlled settings
- they are inspectable and resettable
- they are not hidden adaptive behavior

Examples:
- `tone status`
- `tone set concise`
- `tone set research detailed`
- `tone reset research`
- `tone reset all`

## 8. Calm Scheduling
Phase 5 now also includes explicit scheduling for daily briefs and reminders.

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

Examples:
- `show schedules`
- `notification status`
- `notification settings`
- `schedule daily brief at 8:00 am`
- `remind me at 2:00 pm to review deployment issue`
- `remind me daily at 9:00 am to review project threads`
- `set quiet hours from 10:00 pm to 7:00 am`
- `set notification rate limit 2 per hour`
- `reschedule schedule SCH-123 to 3:00 pm`

Important boundary:
- schedules are explicit
- schedules are inspectable
- schedules are cancellable
- scheduled items do not auto-run actions on the user's behalf

## 9. Pattern Review
Phase 5 now also includes an explicit pattern-review layer for ongoing work.

This is not hidden behavior.
Nova only generates pattern proposals after the user opts in and explicitly asks for a review.

What Nova can propose:
- a blocked thread without a next step
- a repeated blocker theme across threads
- durable context that may still need a clearer saved decision

Examples:
- `pattern opt in`
- `pattern status`
- `review patterns`
- `review patterns for deployment issue`
- `dismiss pattern PAT-...`

Important boundary:
- pattern review is opt-in
- proposals are advisory
- proposals are discardable
- no proposal executes anything automatically
