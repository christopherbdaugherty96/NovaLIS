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

## Minute 3: Test Governance
Try:
- Explain how actions are controlled
- What capabilities are active?
- Why was that action blocked?

Then inspect the proof surface:
- Open `http://localhost:8000/api/trust/receipts` after a governed action
- Check whether a recent receipt event is visible
- Use the dashboard Action Receipts surface when available, but treat the receipt API as the direct proof source

## Minute 4: Test Practical Action
Try:
- Draft an email to `test@example.com` about tomorrow
  - Confirm only if you want to test local draft opening
  - Close the draft without sending
- Turn this into a checklist
- Search the web and cite sources

## Minute 5: Decide Honestly
Ask yourself:
- Did it feel understandable?
- Did it feel useful?
- Did it feel controlled?
- Did Action Receipts or trust receipts make governed actions inspectable?
- What friction blocked adoption?

## Reminder
Nova should be judged on clarity, trust, and bounded usefulness — not only raw feature count.

Conversation context and memory can help Nova understand. They do not authorize actions. Email draft opens a local mail client draft; Nova does not send email autonomously.
