# Project Contexts

Project Contexts let Nova reason inside the correct workspace.

They are not permission by themselves.

A project context can shape memory, allowed environments, proof expectations, and suggestions, but execution still goes through the Governor.

## Example Contexts

- NovaLIS
- Pour Social
- Website Business
- Shopify / E-commerce
- Personal Admin
- Career / Learning

## Context Fields

Each project context can eventually define:

```text
goals
memory
docs
active tasks
allowed environments
blocked environments
proof logs
capability profile
suggestion patterns
trust/reputation notes
```

## Rejected Plans / Reputation

If a user rejects a plan, that rejection should become proof for future planning.

Example:

```text
Rejected plan: browser task used personal browser instead of isolated browser.
Future behavior: prefer isolated browser and explicitly ask before personal browser.
```

This is not a social score.

It is a project-local trust and preference record that helps Nova avoid repeating bad plans.

## Project Examples

### NovaLIS

Nova may inspect repo docs/code and suggest patches.

### Shopify / E-commerce

Current truth: Nova may produce read-only Shopify intelligence if configured. It may not write products, orders, refunds, or customer messages unless future governed write capabilities are implemented.

### Pour Social

Nova may draft contracts, menus, pricing calculators, and operating docs. Sending client communications should remain user-reviewed and governed.