# Active Screen Command Layer

Status: future design plan / not shipped runtime capability

This folder captures the future idea that Nova should use the active visible screen as first context when explicitly activated by the user.

This is not a claim that Nova currently has broad screen navigation authority. It is a planning artifact.

---

## Core Idea

Nova should eventually be able to treat the current visible screen as first context when activated.

Best framing:

```text
Activated screen awareness first.
Governed navigation second.
External action only with approval.
```

This is larger than browser research. It applies to:

- browser pages
- web apps
- desktop apps
- files and folders
- dashboards
- forms
- visible application state

The goal is not constant surveillance. The goal is activation-based awareness.

---

## What This Means In Human Terms

The user activates Nova by voice or command.

Nova gets basic awareness of what is currently visible:

- active app
- window title
- browser URL when available
- visible page/app structure
- major headings/buttons/links/forms
- selected text when available
- basic visual context

Nova does not deeply read or act on everything immediately. It gets enough context to understand where the user is and waits for the user's request.

Example:

```text
User activates Nova while looking at a website.
Nova knows the active page context.
User says: Walk me through this page.
Nova explains the visible page and can guide safe navigation.
```

---

## Difference From Web Search

`governed_web_search` is for search and source lookup.

Active Screen Command Layer is for the user's current visible context.

They are different jobs:

```text
Web search finds information.
Active screen context understands what the user is currently looking at.
Screen-guided command helps navigate what is visible.
```

Do not replace governed web search with this.

---

## Difference From Browser Research

Browser Research Mode is browser-specific.

Active Screen Command Layer is broader. It can apply to the full visible desktop, including browser and non-browser apps.

Browser research may become one specialized workflow under this broader screen-aware command layer.

---

## Proposed Layering

### 1. Active Screen Context

Nova can identify basic visible context when activated.

Allowed examples:

- detect active app/window
- identify page title or URL if browser
- identify visible buttons/headings/links/forms
- summarize the visible screen when asked

### 2. Screen Explanation

Nova explains what is visible.

Allowed examples:

- What am I looking at?
- Summarize this page.
- What are the main buttons here?
- What does this form ask for?

### 3. Screen-Guided Command Mode

Nova helps navigate by voice command.

Allowed examples:

- click safe navigation links
- open menus
- go back/forward
- open public links
- inspect visible page sections
- compare this page with a previous page

### 4. External Effect Actions

Actions that change the world require separate explicit capabilities and approvals.

Examples:

- submit form
- send message
- buy item
- upload file
- delete record
- publish content
- change settings
- change DNS
- deploy site

---

## Core Rule

```text
Seeing is not permission to act.
```

Nova may use the active screen as context after activation, but authority still comes only from governed capabilities, approval policy, and the execution spine.

---

## Activation Model

This system should be activation-based.

Nova should not continuously monitor the screen by default.

Recommended model:

```text
User activates Nova
-> Nova captures basic screen context
-> Nova waits for user instruction
-> Nova explains, guides, or requests governed action
```

Possible activation commands:

- Nova, what am I looking at?
- Nova, walk me through this.
- Nova, help me navigate this page.
- Nova, find the pricing button.
- Nova, compare this site to the last one.

---

## Initial Safe Scope

Allowed first version:

- explicit request-time screen capture
- active window/app detection
- visible-page explanation
- safe link/navigation guidance
- public-page walkthrough
- read-only inspection
- source/page summary

Blocked first version:

- continuous background screen monitoring
- hidden capture loop
- account sign-in
- form submission
- purchases
- uploads
- downloads without approval
- messages/comments/posts
- deleting data
- changing settings
- publishing or deploying

---

## Risk Tiers

### Tier 0 — Context Only

- active app name
- window title
- page title
- visible context summary

No external effect.

### Tier 1 — Read Visible Screen

- inspect visible text
- identify buttons/links/forms
- summarize page/app

Privacy-sensitive but no external action.

### Tier 2 — Guided Navigation

- suggest where the user should click
- guide the user step-by-step

Human still acts.

### Tier 3 — Controlled Navigation

- Nova clicks safe navigation links
- opens non-destructive menus
- goes back/forward
- opens public links

Requires governed capability and ledger entry.

### Tier 4 — External Effect

- submit
- send
- buy
- delete
- upload
- publish
- change settings
- deploy

Requires separate explicit capability, strong approval, and receipt.

---

## Relationship To Existing Runtime Surfaces

This idea expands from existing related surfaces:

- screen_capture
- screen_analysis
- explain_anything
- open_website
- openclaw_execute
- governed_web_search

Current runtime truth remains authoritative. This document describes a future integrated UX and command layer.

---

## Voice UX

The user should be able to command Nova naturally:

```text
Nova, walk me through this page.
Nova, what should I click next?
Nova, inspect this competitor site.
Nova, compare this page to the last one.
Nova, find the contact form but do not submit it.
```

Nova should answer in voice for simple guidance and open dashboard/review for risky actions.

---

## Example Auralis Workflow

Task:

```text
Nova, walk through this competitor website and tell me what they do better than our client.
```

Allowed:

- inspect homepage
- click services page
- click pricing page if public
- inspect contact page without submitting
- identify CTA patterns
- summarize strengths and weaknesses
- recommend Auralis strategy

Blocked:

- submit contact form
- download protected assets
- log into accounts
- send messages
- change anything on the site

---

## Implementation Direction

Do not start by giving Nova broad desktop control.

Recommended order:

1. Define active screen context object.
2. Define visible-screen explanation output.
3. Build request-time screen context snapshot.
4. Add voice command routing for explain/walkthrough requests.
5. Add read-only browser/page walkthrough.
6. Add governed controlled navigation with strict allowlist.
7. Add dashboard Trust Panel review for any state-changing command.
8. Defer external actions until separate capabilities exist.

---

## Honest Framing

Best framing:

```text
Nova can use the active screen as context when activated, then help explain or navigate within governed limits.
```

Avoid:

- Nova watches everything
- Nova can control anything it sees
- browser autonomy
- unrestricted desktop automation
- silent screen monitoring

---

## Bottom Line

This is a strong future direction because it lets Nova feel present in the user's actual workflow.

The safe Nova version is:

```text
Activation-based screen awareness.
Read/explain first.
Guided navigation second.
Controlled clicking only with governed capability.
External effects only with explicit approval and receipts.
```
