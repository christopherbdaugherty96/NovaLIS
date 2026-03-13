# Voice, Screen, and Context
Updated: 2026-03-13

## Why This Matters
One of the biggest shifts in Nova is that it is no longer limited to text-only requests.

Nova is moving toward a much more natural pattern:
- you speak
- Nova understands what you mean
- Nova uses the current screen or file context when asked
- Nova explains what is in front of you

That is what makes Nova feel more like a computer intelligence layer.

## What Is Active Today
The following are active today:
- speech-to-text transcription
- text-to-speech
- bounded screenshot capture on request
- screen analysis on request
- explain-anything mode
- request-time context snapshotting

This means you can already do things like:
- `take a screenshot`
- `analyze this screen`
- `what is this?`
- `explain this page`
- `which one should I download?`

## What Explain Anything Means
Explain-anything mode is Nova's way of turning a vague but natural request into a useful explanation.

When you say something like:
- `explain this`
- `what is this?`
- `what am I looking at?`

Nova tries to answer by using the best available current context.
That may be:
- the visible screen
- the active page
- a selected file

The goal is to let you point at something in your workflow and ask naturally, instead of copying and pasting everything into chat.

## What Screen Capture Means In Nova
Screen capture in Nova is not background surveillance.

It is a request-time capability.
That means it should happen only when the user asks for it.

The runtime is built around:
- bounded capture
- request-time context only
- no hidden looping monitor
- no autonomous follow-up actions

## What Context Means
Nova also uses a request-time context snapshot.
That can include things like:
- active app
- active window title
- browser URL when available
- cursor region
- current screen region

This context helps Nova answer follow-ups more naturally.

It does not mean Nova is silently building a hidden world model in the background.

## Wake Word Status
Wake word is an important planned feature, but it is not fully live runtime yet.

What exists now:
- speech-to-text is active
- text-to-speech is active
- wake word is documented as a planned surface

What does not yet exist as active runtime truth:
- a live always-on wake-word module that is part of the current capability surface

So the right way to describe the current project is:
- voice input is active
- voice output is active
- wake word is planned

## Why This Still Matters Now
Even without live wake word, Nova's current perception features already create a major usability jump.

For example:
- `more on story 2` can summarize the linked article page when available
- `explain this` can analyze the current screen or file
- `which one should I download?` can become a context-aware explanation instead of a generic answer

That is one of the most "magic" parts of the project today.
