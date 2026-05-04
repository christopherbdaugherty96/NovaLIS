# First 5 Minutes With Nova

This guide helps a new user evaluate Nova quickly.

## Minute 1: Confirm It Runs
- Start Nova
- Open the local dashboard
- Ask: What works today?

## Minute 2: Test Everyday Value
Try:
- What's the weather in Belleville?
- Summarize today's news
- Help me plan my day

## Minute 3: Test Memory
Try:
- `remember: My preferred tone is concise`
- `review memories`
- `why-used`

Check:
- A receipt is created when memory is saved
- Memory is only used after explicit save/review paths
- Nova can explain why memory was used

Boundary:
- Memory provides context only
- Memory does not authorize actions

## Minute 4: Test Planning
Try:
- `Plan my week`

Check:
- A structured plan is created
- An approval decision can be recorded
- A receipt exists

Boundary:
- This is a proposal only
- No actions are executed from the plan

## Minute 5: Test Governance and Practical Action
Try:
- Explain how actions are controlled
- What capabilities are active?
- Draft an email to `test@example.com` about tomorrow

Check:
- Email opens as a local draft only
- Nova does not send anything
- Governed actions produce visible proof

Then inspect the proof surface:
- Open `http://localhost:8000/api/trust/receipts` after a governed action
- Check whether a recent receipt event is visible
- Use the dashboard Action Receipts surface when available, but treat the receipt API as the direct proof source

## Decide Honestly
Ask yourself:
- Did it feel understandable?
- Did it feel useful?
- Did it feel controlled?
- Did memory, planning, and receipts make the system more inspectable?
- What friction blocked adoption?

## Reminder
Nova should be judged on clarity, trust, and bounded usefulness — not only raw feature count.

Conversation context and memory can help Nova understand. They do not authorize actions. Planning produces proposals and approval records, not execution. Email draft opens a local mail client draft; Nova does not send email autonomously.
