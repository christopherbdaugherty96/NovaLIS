# Provider State Contract v1

Status: beta truth contract for the existing provider snapshot and presentation surfaces.

This contract defines how Nova may describe provider configuration and health. It is a
read-only truth contract; it does not grant authority, add a provider, or change the
Governor, capability registry, execution boundary, or network boundary.

## Fields

The existing `ConnectionsStore` snapshot remains the source of these fields:

- `configured`: a stored credential or non-empty environment value exists.
- `has_key`: a credential is persisted in Nova's local provider state.
- `environment_configured`: the provider environment variable is non-empty. A stored
  credential may also be copied into the process environment, so this field does not
  identify the source by itself.
- `configuration_source`: `stored`, `environment`, or `none`; persisted state wins when
  both a stored value and an environment value are present.
- `health_ok`: `true`, `false`, or `null`. `null` means that provider health is not
  currently verified, including immediately after saving a credential.
- `connected`: `true` only for a stored credential whose latest health result is
  explicitly `true`. Environment-only configuration is never represented as connected.

No new persisted state, freshness timer, or verification cache is introduced by this
contract. Existing `health_ok=null` is the unverified state.

## State matrix

| Configuration | `health_ok` | `configured` | `connected` | User-facing meaning |
| --- | --- | --- | --- | --- |
| none | any absent state | false | false | unavailable / not configured |
| environment-only | `null` | true | false | configured and attemptable; not verified or live |
| environment-only | known failed | true | false | unavailable for the suggestion surface |
| stored | `null` | true | false | configured; needs verification; still attemptable |
| stored | `true` | true | true | connected / verified |
| stored | `false` | true | false | known failed / needs attention |

The suggestion gate may expose a configured provider for an attempt when it is not known
to have failed (`health_ok` is not `false`). That does not authorize the UI to call it
connected, verified, fresh, live, or successful before the relevant operation supplies
that evidence.

## Presentation rules

- `connected`, `verified`, `fresh`, and `live` require corresponding evidence.
- Environment-only providers may be shown as `Configured` or `Available`, never as
  `Connected`, `Verified`, `Fresh`, or `Live` solely because an environment value exists.
- Stored providers with `health_ok=null` may be shown as `Needs verification` or
  `Configured`, not `Connected` or `Live`.
- Known-failed providers must not appear in provider-gated suggestions or Intro cards.
- A successful provider health check supports provider verification; it does not claim
  that a later data response is fresh.

The Settings connection card, header Quick runs, page suggestions, and Intro cards use
these rules. Runtime execution and capability authorization remain governed by their
existing boundaries.

