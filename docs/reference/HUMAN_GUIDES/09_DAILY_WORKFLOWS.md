# Daily Workflows
Updated: 2026-03-13

## Purpose
This guide shows what Nova looks like in real use.

It is not a technical spec.
It is a set of grounded everyday workflows based on the current runtime surface.

## 1. Morning Check-In

### Goal
Start the day with quick situational awareness.

### A simple flow
1. Ask for a quick news or briefing view:
   - `news`
   - `daily brief`
2. Check immediate context:
   - `weather`
   - `calendar`
   - `system status`

### What this feels like
Nova gives you a practical snapshot of:
- what is happening in the news
- what the day looks like
- whether the system is healthy

### Good follow-ups
- `more on story 1`
- `open source 1`
- `show my calendar`

## 2. Research Session

### Goal
Learn about a current topic and get a more structured answer than a normal search engine gives.

### A simple flow
1. Start with current information:
   - `research robotics startups in warehouse automation`
2. Go deeper:
   - `compare the top 3 search results`
   - `which result is the most reliable source and why`
3. Open a source when needed:
   - `open source 2`

### What this feels like
Nova helps you move from:
- raw search results

to:
- a clearer understanding of the topic
- source comparisons
- stronger confidence about which source to trust

## 3. News Deep Dive

### Goal
Move from headlines to the actual story.

### A simple flow
1. Start with:
   - `news`
2. Pick a story:
   - `more on story 2`
3. If you want the original page:
   - `open source 2`
4. If you want comparison:
   - `compare headlines 1 and 2`

### What this feels like
Nova is not just repeating headlines.
It can use the linked story page when available and give a better summary of the actual article.

## 4. Screen Help Flow

### Goal
Get help with something already visible on screen without copying and pasting everything.

### A simple flow
1. Start with:
   - `explain this`
   - `what is this?`
2. If needed:
   - `analyze this screen`
   - `take a screenshot`
3. Continue with:
   - `what should I click next`
   - `help me do this`

### Good use cases
- a confusing download page
- an error message
- a settings screen
- a chart or graph
- a technical article

## 5. Debugging Workflow

### Goal
Use Nova as a continuity-aware helper while you troubleshoot something real.

### A simple flow
1. Create or enter a thread:
   - `create thread deployment issue`
   - `continue my deployment issue`
2. Ask about the current state:
   - `project status deployment issue`
   - `biggest blocker in deployment issue`
3. If the issue is visible:
   - `explain this`
4. Preserve an important conclusion:
   - `memory save decision for deployment issue: inspect path before rebuild`

### What this feels like
Nova helps you:
- understand the problem
- keep the thread of the work
- avoid losing the important decision you just made

## 6. Document and Analysis Workflow

### Goal
Turn a topic or document into something easier to work with.

### A simple flow
1. Create an analysis document:
   - `create analysis report on the EU AI Act`
2. Review the list:
   - `list analysis docs`
3. Narrow down:
   - `summarize doc 1`
   - `explain section 2 of doc 1`
4. Sanity-check a claim:
   - `verify this`

### What this feels like
Nova becomes a structured reading and explanation layer rather than just a chat answer.

## 7. Project Continuity Workflow

### Goal
Pick up ongoing work without re-explaining everything.

### A simple flow
1. Open the current work:
   - `show threads`
   - `continue my deployment issue`
2. Ask where the project stands:
   - `thread detail deployment issue`
   - `project status deployment issue`
   - `why this recommendation`
3. Save something important:
   - `save this as part of deployment issue`
   - `memory save decision for deployment issue: ...`

### What this feels like
Nova stops feeling like a blank chat box and starts feeling like a workspace with memory and continuity.

## 8. Governed Memory Workflow

### Goal
Preserve important context on purpose.

### A simple flow
1. Save an item:
   - `memory save deployment fix: confirm PYTHONPATH in container`
2. Review saved items:
   - `memory list`
   - `memory show mem_123`
3. Preserve a thread specifically:
   - `memory save thread deployment issue`
   - `memory list thread deployment issue`
4. Change memory state if needed:
   - `memory lock mem_123`
   - `memory defer mem_123`
   - `memory unlock mem_123 confirm`

### What this feels like
Memory behaves like deliberate filing, not hidden silent learning.

## 9. Local Computer Help Workflow

### Goal
Use Nova for bounded everyday computer actions.

### A simple flow
1. Ask for local state:
   - `system status`
2. Open something:
   - `open downloads`
   - `open github`
3. Adjust the environment:
   - `volume up`
   - `pause`
   - `set brightness to 60`

### What this feels like
Nova acts like a governed computer helper rather than a broad uncontrolled agent.

## 10. Scheduled Updates Workflow

### Goal
Let Nova support a daily rhythm without turning into a background actor.

### A simple flow
1. Create a recurring daily check-in:
   - `schedule daily brief at 8:00 am`
2. Create a work reminder:
   - `remind me at 2:00 pm to review deployment issue`
   - `remind me daily at 9:00 am to review project threads`
3. Inspect the current schedule surface:
   - `show schedules`
   - `notification status`
4. Clean up when needed:
   - `dismiss schedule SCH-123`
   - `cancel schedule SCH-123`

### What this feels like
Nova becomes easier to live with daily, but still stays calm.

The important difference is:
- schedules are explicit
- schedule items surface quietly
- scheduled actions do not automatically execute for you

## 11. Pattern Review Workflow

### Goal
Review repeated work themes deliberately without letting Nova turn those themes into autonomous behavior.

### A simple flow
1. Turn the review layer on:
   - `pattern opt in`
2. Ask Nova to generate a review queue:
   - `review patterns`
   - `review patterns for deployment issue`
3. Inspect the proposals:
   - `pattern status`
4. Resolve the queue:
   - `accept pattern PAT-123`
   - `dismiss pattern PAT-123`

### What this feels like
Nova becomes more reflective about your work, but still stays under your control.

The important difference is:
- review is opt-in
- proposals are advisory
- nothing runs automatically just because a pattern was found

## 12. Best Ways To Use Nova Right Now

Nova is strongest today when you use it for:
- explanation
- research
- ongoing work continuity
- explicit memory preservation

## 13. Project Review Workflow

### Goal
Use Nova as a governed project reviewer before asking it to change code.

### A simple flow
1. Start with a local understanding pass:
   - `summarize this repo`
   - `audit this repo`
   - `create analysis report on Nova architecture`
2. Use the Agent page project-analysis lane when available:
   - run `Project Snapshot`
3. Continue with the smallest safe next step:
   - ask for the biggest gap
   - ask for the safest improvement
   - ask for a patch proposal later when that lane is live

### What this feels like
Nova should first help you understand the project clearly, then later help you change it safely.
- explicit scheduled support for daily routines
- explicit review of repeated work patterns
- bounded local assistance

Nova is less about magic hidden automation and more about:
- clarity
- continuity
- calm rhythm
- governed help

## Short Version
If you want one simple mental model, it is this:

Nova helps you:
- understand what is happening
- continue what you were doing
- preserve what matters
- surface what you chose to be reminded about

while keeping authority under explicit user control.
