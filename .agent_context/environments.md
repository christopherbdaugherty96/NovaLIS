# Environment Context

Nova's Brain should reason about environments before execution.

## Current Environment Categories

- local internal: conversation, runtime truth, memory, project docs, ledger, dashboard
- local machine: filesystem, screen, OS controls, mail client, audio/voice
- network read: web search, website open, news, weather, calendar read, Shopify read-only
- browser: OpenClaw isolated browser, test browser, personal browser session
- external effect: email draft, future email send, future Shopify write, future calendar write, form submit, purchase, account change

## Rule

Naming an environment does not mean it is implemented or allowed.

Agents must verify current capability/runtime truth before claiming support.

## OpenClaw Rule

Prefer isolated OpenClaw/browser environments over the user's personal signed-in browser. Personal browser sessions require explicit user approval and stronger proof.