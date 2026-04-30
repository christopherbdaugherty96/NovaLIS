# YouTubeLIS

YouTubeLIS is a governed YouTube content-production system for creating high-quality videos about the most important and exciting developments in AI and technology.

It is designed to eventually integrate with NovaLIS as a controlled, reviewable content pipeline — not an uncontrolled automation bot.

---

## Core Idea

> Break down the AI race, major breakthroughs, robotics, automation, and how they impact jobs, businesses, and everyday people.

YouTubeLIS is not a generic AI news channel. It is intended to be a signal-focused explainer and story engine.

The channel should prioritize:

- Signal over noise
- Reality over hype
- Explanation over repetition
- Real evidence over vague speculation
- Human impact over technical trivia

---

## System Model

YouTubeLIS should treat each video as a governed planning run:

```text
Idea -> Task Understanding -> Planning Run -> Content Build -> Validation -> Production Plan -> Review Stop
```

NovaLIS may help with thinking, structure, drafting, validation, and production planning. Publishing, account actions, purchases, uploads, and external execution remain human-approved actions.

---

## Content Focus

YouTubeLIS focuses on:

- AI breakthroughs that actually change things
- The AI race between companies, labs, open-source ecosystems, and infrastructure builders
- Robotics and real-world automation
- Job loss, job transformation, and new AI-enabled work
- What is real now versus what is hype
- What may happen next, grounded in visible evidence

---

## Video Style

The preferred format is:

> Real footage for proof + animation for explanation + narration for story.

Videos should feel like short documentary/explainer pieces, not automated filler.

A strong YouTubeLIS video should:

- Show what is actually happening
- Explain it in plain language
- Connect it to why people care
- Separate verified reality from speculation
- End with a grounded takeaway

---

## Repeatable Video Structure

1. Hook
   - Open with the exciting, alarming, or surprising point.

2. Real Evidence
   - Use demos, footage, screenshots, product releases, papers, or public examples when available.

3. Simple Explanation
   - Use animation, overlays, captions, or diagrams to explain what is happening.

4. The AI Race Context
   - Explain who is building it and why the competition matters.

5. Human Impact
   - Explain what this could change for jobs, businesses, creators, workers, or daily life.

6. What Comes Next
   - End with a grounded prediction, open question, or practical takeaway.

---

## NovaLIS Integration

YouTubeLIS should eventually plug into NovaLIS as a governed workflow.

NovaLIS may help with:

- Finding and ranking video ideas
- Generating outlines and scripts
- Structuring claims
- Separating evidence from speculation
- Producing voiceover drafts
- Creating shot lists
- Planning animation overlays
- Coordinating OpenClaw or desktop automation
- Tracking performance after publishing
- Recommending what to double down on

Human approval remains required before publishing, buying tools, using accounts, uploading content, or representing claims as factual.

See `docs/NOVALIS_INTEGRATION.md` for the full planning-run, task-envelope, and live-vs-planned integration model.

---

## Governed Automation Principle

> Maximum useful automation, not uncontrolled automation.

YouTubeLIS should be powerful, but task-scoped and reviewable.

No component should have broad unchecked authority. Any automation should be:

- Declared before execution
- Limited to an approved task scope
- Approved by the user when risk exists
- Stopped when the task is done
- Logged for review

---

## Current Status

Planning and architecture phase.

This repo should not claim to be a complete automated YouTube system until actual workflows, tools, tests, and video production paths exist.

Current honest baseline:

```text
Task Understanding: planning-only model
Task Envelope: planning-only model
Planning Run: target workflow model
Execution integration: not implemented in this repo
Publishing: manual only
```

Start with documentation, workflow design, and one reliable pilot video pipeline.

---

## Documentation Map

- `docs/CONTENT_STRATEGY.md` — niche, audience, pillars, and video formats
- `docs/VIDEO_PIPELINE.md` — production pipeline from idea to publish
- `docs/PLANNING_RUN_TEMPLATE.md` — standard planning-only run format for turning an idea into reviewable artifacts
- `docs/GOVERNED_AUTOMATION.md` — NovaLIS/OpenClaw governance model
- `docs/NOVALIS_INTEGRATION.md` — planning-run, task-envelope, and live-vs-planned NovaLIS integration model
- `docs/FIRST_VIDEO_IDEAS.md` — starter ideas for the first content batch
