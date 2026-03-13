# FAQ and Troubleshooting
Updated: 2026-03-13

## Purpose
This guide answers common practical questions about using Nova.

It is written for normal day-to-day use.
It is not a technical audit or design document.

## 1. Is wake word live yet?
Not as active runtime truth yet.

Current state:
- typed input is active
- push-to-talk speech transcription is active
- text-to-speech is active
- wake word is planned, but not currently a live runtime capability

So the right way to describe Nova today is:
- voice input works
- voice output works
- wake word is still a planned surface

## 2. Why didn't Nova do anything automatically?
Usually because Nova is designed not to act automatically.

Nova is built around explicit invocation.
That means it should not:
- silently execute actions
- silently save memory
- silently monitor the screen
- silently continue tasks in the background

If you want Nova to do something, ask directly.

## 3. Why didn't Nova save that automatically?
Because memory in Nova is meant to be explicit.

Nova's memory model is designed to behave more like:
- deliberate filing
- saved decisions
- preserved project context

and less like:
- hidden passive memory
- automatic background learning

If something matters enough to preserve, use a memory command such as:
- `memory save ...`
- `memory save thread <name>`
- `memory save decision for <thread>: ...`

## 4. Why did Nova answer, but not take action?
Because explanation and execution are separate in Nova.

Nova can often:
- explain
- summarize
- guide
- recommend a next step

without automatically performing the next action.

This is intentional.
It helps keep the system governed and predictable.

## 5. Why did Nova say it couldn't do that right now?
There are a few common reasons:
- the capability may not support that request yet
- the request may need clearer wording
- a local dependency may not be available
- a networked feature may be temporarily unavailable
- the model may be unavailable or blocked

Good recovery steps:
- ask `system status`
- rephrase the request more directly
- try a simpler version of the command

## 6. Why does `system status` matter so much?
Because it is one of the best quick health checks in Nova.

It can help show:
- overall health state
- CPU, memory, and disk load
- network status
- model readiness

If Nova seems off, `system status` is often the best first check.

## 7. Why did screen help not work?
Common reasons:
- the request did not clearly invoke the screen path
- the visible content was hard to read
- the screen region did not contain enough text or signal
- the context was ambiguous

Good recovery steps:
- `take a screenshot`
- `analyze this screen`
- `explain this`
- be more specific, such as `explain this error`

## 8. Does Nova watch my screen all the time?
No, not in the intended current model.

Screen capture and screen analysis are request-time features.
They are meant to happen when you explicitly ask.

That means Nova should not behave like:
- a passive screen watcher
- a background surveillance loop
- a hidden monitoring process

## 9. Why did Nova ask me to be more specific?
Because some requests are naturally ambiguous.

Examples:
- `open it`
- `save this`
- `explain that`

If the current context is not clear enough, Nova may need:
- a clearer target
- a thread name
- a specific story number
- a specific file or page

## 10. Why didn't `more on story 2` work the way I expected?
That command works best when Nova has current headline and source data available from the active news session.

Best flow:
1. ask for `news`
2. then ask `more on story 2`

That gives Nova the story index and the linked source context it needs.

## 11. Why didn't `continue my <project>` find the project?
Usually because:
- the thread was never created
- the name is too different from the saved thread
- the thread context is weaker than expected

Good recovery steps:
- `show threads`
- `create thread <name>`
- then `continue my <name>`

## 12. What is the difference between a thread and memory?
This is one of the most important Nova concepts.

A thread is:
- ongoing work context
- project continuity
- current blocker/decision/status view

Memory is:
- explicit long-term preservation
- governed saved context
- durable record of something the user chose to keep

Short version:
- thread = active workstream
- memory = explicit preserved record

## 13. Why does Nova sometimes suggest a next step instead of doing it?
Because Nova is designed to help without silently taking authority.

That means it often behaves like:
- explain first
- suggest next step
- wait for explicit instruction if action is needed

That is intentional, not a bug in the design philosophy.

## 14. What should I try if I am not sure how to ask?
Start with one of these:
- `news`
- `weather`
- `calendar`
- `system status`
- `explain this`
- `continue my <project>`
- `memory list`

Then use follow-ups from there.

## 15. What are Nova's strongest use cases right now?
Today Nova is strongest at:
- research and summary work
- story and article follow-up
- screen explanation
- project continuity
- explicit governed memory
- bounded local computer help

## 16. What is the best way to preserve something important?
Use an explicit memory command.

Examples:
- `memory save deployment fix: confirm PYTHONPATH in container`
- `memory save thread deployment issue`
- `memory save decision for deployment issue: inspect path before rebuild`

## 17. What if I just want the simplest possible way to use Nova?
Use this pattern:

1. ask directly
2. check the result
3. use a clear follow-up
4. save important project decisions explicitly

Examples:
- `news`
- `more on story 1`
- `explain this`
- `continue my deployment issue`
- `memory save decision for deployment issue: ...`

## Short Version
If Nova seems confusing, remember these three things:

- Nova usually waits for explicit instruction
- Nova separates explanation from action
- Nova treats memory as something you save on purpose
