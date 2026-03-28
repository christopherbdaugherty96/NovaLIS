# Project Continuity and Memory
Updated: 2026-03-27

## Why This Part Matters
A lot of AI systems can answer one prompt well.
Very few can help you continue real work across time.

This is where Nova starts to feel different.

Nova now supports five closely related ideas:
- working context
- project continuity threads
- governed memory
- operational remembrance visibility
- bounded assistive noticing
- workspace home
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

The thread map, thread detail view, and new Workspace Home surface make Nova feel more like a workspace than a chat transcript.

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
- `what do you remember`
- `remember this: Client supplies alcohol; Pour Social does not sell alcohol.`
- `list memories`
- `memory export`
- `show that memory`
- `edit that memory: <updated text>`
- `delete that memory`
- `forget this`

Important boundary:
- this is still explicit
- Nova does not autosave
- Nova does not silently convert ordinary chat into memory
- destructive or mutating changes still require clear user action

## 5. The New Memory Center
The dedicated Memory page is no longer just an overview card.

It now acts as a governed memory management surface where the user can:
- browse durable memory items
- filter by active / locked / deferred
- inspect a selected memory item in full
- export a governed JSON snapshot
- review thread linkage, source, version, and tags
- prepare governed actions like edit, lock, unlock, defer, and delete

Important boundary:
- the page does not bypass governance
- silent page refresh is used only to keep the page clean while reviewing memory
- mutating actions still route through the normal governed confirmation path when required

## 6. The Thread-Memory Bridge
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

## 7. Bounded Relevant Memory Use
Nova can now use clearly relevant explicit memory as a bounded chat aid.

That means:
- a memory that directly matches the current question may be used as a small context hint
- unrelated questions do not automatically drag in saved memory
- memory remains separate from Nova's identity or personality

This is a very important trust boundary.
Nova is supposed to feel helpful, not creepy.

## 8. What This Feels Like In Practice
A realistic Nova continuity flow now looks like this:
- you continue a thread
- Nova shows the current blocker and latest decision
- you save a new decision
- the thread's memory count increases
- you ask for `memory overview`
- Nova shows the current durable memory state and linked threads
- you open the Memory page and browse the list without cluttering chat
- you inspect one memory item in full before deciding whether to edit or delete it
- later you ask a directly related question
- Nova can use the clearly relevant saved memory without pretending it remembers everything

That is the beginning of a real personal continuity system.

## 9. Workspace Home
Nova now also has a calmer Workspace Home surface on the Home page.

This surface brings together:
- the active project thread
- current blocker and next step
- latest project decision
- recent project-linked memory
- recent analysis documents
- recent trust activity and blocked conditions

This matters because continuity is not only about remembering.
It is also about helping the user re-enter work without having to reconstruct everything from scratch.

Important boundary:
- Workspace Home does not gain new authority
- it is a visibility and next-step surface
- all recommended actions still route through the normal governed command path

## 10. Operational Context
Nova now also exposes operational remembrance more directly.

This surface is for session continuity, not durable user memory.

It can show things like:
- current goal
- current step
- active thread
- active topic
- selected file
- recent continuity anchors

You can access it with:
- `operational context`
- `continuity status`

You can also clear it explicitly with:
- `reset operational context`

You can also review the current noticing layer explicitly with:
- `assistive notices`

Important boundary:
- reset clears session continuity
- reset does not delete governed personal memory
- this is inspectable continuity, not hidden autonomy

## 11. Assistive Notices
Nova now has a first bounded assistive-noticing slice.

This slice is intentionally narrow:
- visible in Home and Trust
- visible in Settings through an assistive-noticing mode control
- available explicitly through `assistive notices`
- limited to observations and suggestions

Right now, Nova can surface things like:
- a blocker without a next step
- repeated runtime issues
- ongoing work without a continuity anchor yet
- trust conditions in the highest-awareness mode

Important boundary:
- this is still `notice -> ask -> assist`
- Nova does not silently act from these notices
- Nova does not silently save memory because of them
- Silent mode suppresses unsolicited notice surfacing
- repeated notices now cool down by notice type instead of resurfacing on every refresh
- surfaced notices can now be dismissed or marked resolved for the current continuity window
- handled notices remain reviewable in Trust for the current continuity window

## 12. The Big Difference Between Context, Threads, Memory, Workspace Home, and Operational Context
The easiest way to understand them is this:

Working context:
- what is happening right now

Thread continuity:
- what is happening in this project in the current workspace session

Governed memory:
- what the user explicitly chose to preserve across time

Workspace Home:
- the calmer product surface that brings those pieces together into one place

Operational Context:
- the explicit review/reset surface for session continuity itself

Together, these four layers let Nova feel more coherent without becoming hidden or uncontrolled.

## 12.1 Assistive Modes
Assistive noticing now has four visible modes in Settings:
- `Silent`
- `Suggestive`
- `Workflow Assist`
- `High Awareness`

What changes between them:
- `Silent` keeps unsolicited notices hidden unless you explicitly open them
- `Suggestive` focuses on low-risk repeated friction and missing-next-step cues
- `Workflow Assist` adds stronger continuity nudges like missing project anchors
- `High Awareness` adds the widest bounded set, including current trust-condition cues

Important boundary:
- the mode changes what Nova may surface
- it does not grant new authority
- even in `High Awareness`, Nova is still not supposed to silently decide or act

## 13. Calm Scheduling
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

## 14. Pattern Review
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
