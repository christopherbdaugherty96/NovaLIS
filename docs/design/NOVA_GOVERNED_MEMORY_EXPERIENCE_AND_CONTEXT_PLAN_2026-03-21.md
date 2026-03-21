# Nova Governed Memory Experience And Context Plan
Date: 2026-03-21
Status: Planning packet only; current product-improvement roadmap with later Phase-9 and Phase-10 extensions
Scope: Improve explicit memory save/use flows, memory management UX, and contextual use of governed memories without widening authority or introducing hidden adaptive learning

## Purpose
This packet captures a specific product goal:

Nova should handle explicit memory much better.

That means the user should be able to:
- say `save this`
- say `remember this`
- view saved memories clearly
- edit or delete memories easily
- trust that Nova can use saved memories for context when they are relevant

This is not runtime truth.
It is a product and design roadmap for making governed memory more useful, more visible, and more trustworthy.

## Core Product Direction
The best overall memory shape is:

1. memory is explicit
2. memory is governed
3. memory is inspectable
4. memory is editable
5. memory is deletable
6. memory can be used as context when relevant
7. memory does not silently become adaptive learning

That means Nova should feel more like:
- "I can remember what you explicitly asked me to remember, and you can see and control it."

and less like:
- "I might be learning things in the background and you cannot tell why."

## Current Product Problems To Fix

### 1. Explicit Save/Remember Flows Need To Feel Stronger
Phrases like:
- `save this`
- `remember this`
- `remember that`
- `save this for later`

should feel natural and dependable.

The better experience is:
- Nova clearly identifies what is about to be saved
- Nova confirms the memory in plain language
- the memory becomes visible and manageable afterward

### 2. Saved Memories Need Better Visibility
Users need a clear place to:
- see saved memories
- understand what is active
- inspect the stored content
- understand why a memory exists

If memory exists but is hard to inspect, trust suffers.

### 3. Edit/Delete Flows Need To Be Easy
Governed memory is only trustworthy if the user can correct it.

Users should be able to:
- edit a memory
- delete a memory
- understand the effect of those actions

The system should not make memory feel permanent or buried.

### 4. Memory Should Actually Help Conversation Context
If the user explicitly saved something important, Nova should be able to use it when relevant.

That does not mean:
- blindly injecting everything into every answer
- overclaiming memory use
- hidden personality learning

It means:
- relevant memories can help with context
- Nova stays grounded in what was explicitly saved
- memory use remains bounded and reviewable

## Best Product Recommendation

### Make Memory Explicit And Controllable
The product should present memory as something the user controls.

That means:
- clear save flows
- clear memory list
- clear edit/delete actions
- clear use of saved memory in context

### Make Memory A Useful Working Surface, Not Just A Hidden Store
Memory should not only exist behind commands.

It should have a useful surface where the user can:
- review saved items
- inspect titles and contents
- edit items
- delete items
- understand which items are active or locked

### Use Memory As Context, Not As Hidden Identity Drift
Nova should use explicit memories to support context.

Examples:
- preferences the user explicitly saved
- project-relevant facts the user asked Nova to keep
- durable notes the user wants recalled later

But that should remain different from:
- adaptive personality shaping
- silent preference learning
- hidden long-term behavioral drift

## Best UX Shape

### 1. Strong Save/Remember Replies
When the user says:
- `save this`
- `remember this`

Nova should respond clearly with:
- what it is saving
- the memory title or label if relevant
- confirmation that it was stored
- what the user can do next

Examples of useful next actions:
- `show memories`
- `edit memory`
- `delete memory`

### 2. Clear Memory List Surface
There should be a straightforward way to view memories, such as:
- `memory list`
- a memory panel or memory page

The list should show:
- title
- short preview
- state
- created/updated info if useful

### 3. Easy Memory Detail View
Each saved memory should be easy to inspect in full.

The detail view should allow:
- viewing full content
- editing
- deleting
- understanding whether it is active, locked, or deferred

### 4. Friendly Edit/Delete Flows
Edit/delete should feel simple and reversible where possible.

The UX should make it easy to:
- correct a memory
- remove outdated information
- keep the memory set clean

### 5. Contextual Use Should Feel Helpful, Not Creepy
When Nova uses memory in context, it should feel like:
- relevant support
- better continuity
- less repetition for the user

It should not feel like:
- unnecessary repetition of saved facts
- random resurfacing
- hidden behavior shaping

## Best Memory-Use Recommendation

### Explicit Memories Should Be Eligible Context
If a memory was explicitly saved, Nova should be able to retrieve it when:
- the current request makes it relevant
- the memory helps answer the question
- the memory clearly belongs to the active project or topic

### Relevance Matters
Not every memory should be used every time.

Nova should prefer:
- relevant memory retrieval
- minimal context injection
- memory use tied to the current request

### Memory Should Stay Separate From Session State
It is important to distinguish:

1. session-local conversation state
2. explicit durable governed memory

Session state helps within the current conversation.
Explicit memory survives longer because the user asked for it.

Both matter, but they are not the same thing.

### Memory Use Should Stay Honest
Nova should not imply:
- perfect recall of everything
- hidden background learning
- certainty beyond what was explicitly stored

Instead:
- explicit stored memories can be retrieved
- relevance determines use
- the user stays in control

## Technical Recommendation

### Current Product Track
These improvements belong in the current product-improvement track:
- stronger handling for `save this` and `remember this`
- clearer memory save confirmations
- easier `memory list` / memory detail flows
- edit/delete memory UX improvements
- bounded retrieval of explicit memories for relevant context
- better visibility into stored governed memories

These are current product and trust improvements.
They do not require new authority.

### Phase 9 Extensions
These belong later in Phase 9 governed-node / multi-client coherence:
- memory coherence across clients
- stable governed memory behavior across devices
- stronger node-level continuity of explicit memories
- more robust memory surfaces across different Nova interfaces

Why they belong in Phase 9:
- they are about node-scale coherence
- they go beyond a single local client surface
- they require memory behavior to stay stable across multiple interfaces

### Phase 10 And Later
Only much later should Nova consider:
- user-approved memory weighting
- adaptive retrieval preference tuning
- durable learned preference modeling
- reviewable long-term memory adaptation

Why that belongs later:
- it touches durable learning behavior
- it requires stronger auditability and rollback
- it should not arrive before explicit review and mutation controls

## Phase Boundaries

### Not Hidden Learning
This packet is not a request for:
- silent personality learning
- hidden preference drift
- automatic broad memory extraction from every conversation

Those belong much later, if ever, under explicit reviewable controls.

### Not Execution
This is not a Phase 8 execution item.

Memory use here should remain:
- read/write only within governed memory controls
- not execution authority
- not approval authority

## Recommended Architecture

### 1. Memory Command Understanding Layer
This layer should interpret requests like:
- `save this`
- `remember this`
- `show memories`
- `edit this memory`
- `delete that memory`

It should identify:
- what content is being referred to
- whether clarification is needed
- which memory action the user wants

### 2. Governed Memory Storage Layer
This layer should:
- store explicit memories
- preserve metadata
- support title/content management
- keep memory state clear

Likely surfaces:
- `nova_backend/src/memory/`
- `nova_backend/src/brain_server.py`

### 3. Memory Management UI Layer
This layer should:
- show saved memories clearly
- support viewing, editing, and deleting
- reduce clutter when memory is empty

Likely surfaces:
- `nova_backend/static/dashboard.js`
- memory-related dashboard/UI rendering surfaces

### 4. Memory Retrieval For Context Layer
This layer should:
- retrieve relevant explicit memories
- inject them into context only when useful
- keep retrieval bounded and topic-relevant

This is the main quality improvement for making saved memory actually matter in conversation.

## Best Implementation Order

### Stage 1 - Explicit Save/Remember Flow Cleanup
Goal:
- make `save this` and `remember this` feel dependable and clear

Best scope:
- stronger command interpretation
- clearer confirmation of what was stored
- better next-step guidance

Suggested branch:
- `codex/memory-stage1-save-remember-flow`

### Stage 2 - Memory List / View / Edit / Delete UX
Goal:
- make saved memories easy to inspect and manage

Best scope:
- memory list improvements
- memory detail improvements
- edit/delete flows
- cleaner empty-memory state

Suggested branch:
- `codex/memory-stage2-management-ui`

### Stage 3 - Relevant Memory Retrieval For Context
Goal:
- make explicit memories actually help Nova answer in context

Best scope:
- bounded retrieval of relevant memories
- minimal injection into the active conversation
- no hidden learning expansion

Suggested branch:
- `codex/memory-stage3-context-retrieval`

### Stage 4 - Multi-Client Memory Coherence
Goal:
- keep explicit memory behavior stable across Nova surfaces and clients

Best scope:
- cross-interface memory consistency
- shared memory semantics
- stable retrieval expectations

Suggested branch:
- `codex/phase9-memory-coherence-stage1`

## Recommended Product Rule
The anchor rule for Nova memory should be:

Explicit memories should be easy to save, easy to inspect, easy to change, and genuinely useful in context.
