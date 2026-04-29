# Environment Catalog

This catalog defines the worlds Nova may reason about entering.

An environment is not automatically available just because the brain names it.

The Governor, capability registry, setup state, confirmation requirements, and proof rules still decide whether the environment can be entered.

## Trust / Authority Tiers

| Tier | Meaning | Examples |
|---|---|---|
| L0 | Local internal reasoning/read | local conversation, runtime truth, local docs |
| L1 | Network read-only | web search, open public website, news/weather |
| L2 | Account read | calendar read, Shopify read-only if configured |
| L3 | Local/device effect | brightness, volume, screen capture, file/folder open |
| L4 | External-effect draft | email draft, calendar draft, browser form preview |
| L5 | Account write / external submission | send email, submit form, Shopify write, purchase |

## Local Internal Environments

- `local_conversation`
- `local_runtime_truth`
- `local_memory`
- `local_project_docs`
- `local_ledger`
- `local_dashboard`

## Local Machine Environments

- `local_filesystem`
- `local_screen`
- `local_os_controls`
- `local_mail_client`
- `local_audio_voice`

## Network Read Environments

- `web_search`
- `website_open`
- `news_api`
- `weather_api`
- `calendar_read`
- `shopify_read_only`

## Browser Environments

- `openclaw_isolated_browser`
- `browser_use_test_browser`
- `personal_browser_session`
- `remote_browser`

## External Effect Environments

- `email_draft`
- `email_send_future`
- `shopify_write_future`
- `calendar_write_future`
- `form_submit`
- `purchase_payment`
- `account_change`

## Granular Browser Rule

`openclaw_isolated_browser` and `personal_browser_session` must stay separate.

The isolated browser is the preferred governed automation lane.

The personal browser session is higher risk because it may include logged-in accounts, cookies, private data, and account permissions.

## Current Truth Note

Naming an environment here does not mean Nova currently implements it.