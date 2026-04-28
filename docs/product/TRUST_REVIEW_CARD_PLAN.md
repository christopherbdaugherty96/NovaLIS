# Trust Review Card Plan

## Purpose

The highest-value missing proof layer in Nova is visible action review.

Users should not need to inspect source code or backend logs to understand what the system did.

## What The Card Should Show

For any governed action, a Trust Review Card can display:

1. User request
2. Detected intent
3. Capability selected
4. Why it was allowed or blocked
5. Whether confirmation was required
6. Result summary
7. Timestamp / receipt link

## Example

```text
Request: Draft an email to John
Intent: create_draft
Capability: send_email_draft
Status: Allowed with confirmation
Result: Draft opened in local mail client
```

## Why It Matters

- Converts invisible governance into visible value
- Builds user trust faster
- Makes demos clearer
- Helps debugging
- Distinguishes Nova from generic agent wrappers

## Scope Guidance

Start small:

- latest action card
- recent receipts list
- blocked action explanation
- confirmation state

Do not wait for a perfect dashboard redesign.

## Truth Constraint

The UI should reflect real ledgered events and runtime decisions, not mock data or marketing claims.