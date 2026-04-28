# Trust Review Card Spec

## Purpose
Turn Nova's governance model into a visible user experience before or during meaningful actions.

## Core Goal
Help users understand:
- what Nova understood
- what Nova can do
- what requires approval
- what will happen next
- what happened after execution

## Card States

## 1. Understanding
Show before action planning.

Fields:
- Request summary
- Interpreted intent
- Confidence (optional)
- Missing information (if any)

## 2. Proposed Action
Show available next step.

Fields:
- Capability to be used
- Why this capability matches
- Confirmation required: Yes / No
- Expected result
- Risk level (Low / Medium / High)

## 3. Execution Result
Show after completion.

Fields:
- Action attempted
- Result status
- Human-readable outcome
- Time completed
- Ledger reference (optional)

## 4. Refusal / Blocked
Show when Nova should not proceed.

Fields:
- Reason blocked
- What user can do next
- Safer alternative if available

## UX Rules
- Must be human-readable
- Must not expose internal jargon first
- Must not imply authority beyond real capability
- Must make approval obvious
- Must help trust, not add clutter

## Example Flow
User: open downloads

Card:
- Understood request: Open Downloads folder
- Planned action: Use local file capability
- Confirmation: Not required
- Result: Downloads opened successfully

## Success Condition
Users can clearly see what Nova understood, what it plans to do, and what happened.
