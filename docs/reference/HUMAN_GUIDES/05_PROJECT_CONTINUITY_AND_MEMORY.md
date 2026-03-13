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

They are connected, but they are not the same thing.

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

## 4. The Thread-Memory Bridge
One of the most important recent changes is the bridge between threads and governed memory.

This means Nova can now preserve:
- thread snapshots
- thread decisions
- durable thread-linked memory history

Examples:
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
