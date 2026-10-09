# Nova outbound-egress inventory (2026-10-08)

Status: inventory and design input only. This document changes no runtime behavior.

Audited baseline: `origin/main` at `bab4a6cf1f200eebfad5af166b242d7e9ccdd963`.

## Purpose and boundary

This inventory identifies where Nova can cause data or credentials to leave the
process or machine. It is the review gate before provider-neutral Data-Out
enforcement. It does not authorize implementation, approve an exception, or claim
that the current provider controls are custody controls.

The audit used runtime source, generated runtime truth, the capability registry,
and existing governance tests. It searched HTTP clients, local-model clients,
browser and OS handoffs, subprocess creation, OAuth setup, connector code, and
browser-side JavaScript. The existing runtime auditor's requests-library scan is
useful but narrower: it does not establish the absence of `urllib`, sockets,
browser/OS delegation, subprocess-owned networking, or browser-side requests.

## Executive finding

There is no single provider-neutral Data-Out decision today.

`NetworkMediator` is the main external HTTP(S) choke point. It validates the
capability, rate, URL, DNS result, redirects, and timeout, then records request
metadata after success or selected failures. It does **not** ask whether the
provider is enabled for Data-Out, classify the disclosed data, or record an
allow/deny disclosure decision before transport. A capability being enabled is
therefore not equivalent to permission to disclose data to its provider.

The known user-visible failure follows directly from that split: the DeepSeek
setting is not a universal egress control. General chat and capabilities 31, 48,
and 54 can reach `DeepSeekBridge` and capability 62 when a key is configured even
when the user-facing DeepSeek/provider setting is off. The default budget policy's
`enabled` field is visibility vocabulary, not enforcement; the DeepSeek hard
budget gate considers usage limits, not that field.

There are also real paths outside `NetworkMediator`: provider health checks,
local-model traffic, browser/mail-client handoffs, local status probes, subprocess
and application launches, and an inactive landing-page Formspree placeholder.
Those paths require an explicit disposition; they cannot be covered by renaming
the existing HTTP mediator.

## Inventory

### External model and conversation paths

| Caller / capability | Provider and destination | Transport creation point | Data and credentials disclosed | Current check | Evidence today | DENY behavior today | Zero attempt on provider-off? | Boundary status |
|---|---|---|---|---|---|---|---|---|
| General chat deep-reason escalation | DeepSeek, `api.deepseek.com/chat/completions` | `DeepSeekReasoningProvider` calls `NetworkMediator.request` (cap 62) | The user message plus constructed analysis prompt/context; DeepSeek API key in `Authorization` | Cap 62 enabled, key present, and hard token/cost budget. No universal DeepSeek/Data-Out toggle check | Mediator success/failure metadata; provider usage estimates; cognitive-operation record. No pre-egress disclosure decision | Cap disabled, missing key, or budget limit returns a local unavailable/fallback result. Provider-off does not deny | **No** | Uses the common HTTP mediator but bypasses the intended provider-policy meaning |
| Cap 31 `response_verification` | DeepSeek, same endpoint | `ResponseVerificationExecutor` -> `DeepSeekBridge` -> provider -> mediator cap 62 | The answer/exchange to verify plus verification instructions; API key | Cap 31 approval/execution controls and cap 62 enabled; no provider-neutral disclosure check | Same cap-62 network/usage evidence; cap 31 metadata describes this surface as local/no-network | No provider Data-Out denial exists | **No** | Nested cap-62 egress; registry/runtime classification understates network use |
| Cap 48 `multi_source_reporting` reasoning | DeepSeek, same endpoint | `MultiSourceReportingExecutor` -> `DeepSeekBridge` -> provider -> mediator cap 62 | Search query, selected findings, and counter-analysis prompt; API key | Cap 48 controls plus cap 62 enabled and budget; no provider-neutral disclosure check | Cap-62 mediator and usage evidence, separate from cap-48 search calls | No provider Data-Out denial exists | **No** | Nested provider call is not represented by one cap-48 disclosure decision |
| Cap 54 `analysis_document` create/explain | DeepSeek, same endpoint | `AnalysisDocumentExecutor` -> `DeepSeekBridge` -> provider -> mediator cap 62 | Topic or selected document section and instructions; API key | Cap 54 controls plus cap 62 enabled and budget; no provider-neutral disclosure check | Cap-62 mediator and usage evidence; cap 54 metadata describes the surface as local/no-network | No provider Data-Out denial exists | **No** | Nested cap-62 egress; registry/runtime classification understates network use |
| Cap 62 external reasoning | DeepSeek, same endpoint | `DeepSeekReasoningProvider` -> `NetworkMediator.request` | Explicit reasoning prompt/context; API key | Cap 62 enabled, key, usage budget | Mediator and provider-usage events | Capability disable/budget can stop the call before `requests.request`; provider setting cannot | Partial only | Closest governed path, but still lacks Data-Out policy/evidence |
| OpenClaw metered summarization fallback (within cap 63 runs) | OpenAI Responses API, `api.openai.com/v1/responses` | `OpenAIResponsesLane` -> `NetworkMediator.request` using cap 62 | Full task-report prompt, system prompt, task content; OpenAI key | Caller normally invokes `plan_for_openclaw_fallback`: routing mode `budgeted_fallback`, `metered_openai_enabled`, key, budget. `summarize_task_report` itself only requires the key | Mediator metadata plus provider-usage result | The normal caller returns deterministic/local output when the plan denies. A direct method caller could skip the plan | **Yes on the normal OpenClaw caller; not guaranteed at the transport method** | Policy is caller-side rather than an invariant at final egress |
| Local chat / local reasoning / OpenClaw local summary | Configured Ollama-compatible endpoint | `LLMManager` -> `ModelNetworkMediator` -> `requests.Session.request` | Prompts/context and generated output; no hosted-provider key by default | Endpoint must resolve to loopback/private/link-local; concurrency and timeout controls | `MODEL_NETWORK_CALL` / `MODEL_NETWORK_CALL_FAILED` metadata | Invalid/public endpoints fail before the request | Yes for invalid/public endpoint | Separate local/private model boundary, not external provider Data-Out; must remain explicitly classified |

### Search, news, weather, commerce, and provider setup

| Caller / capability | Provider and destination | Transport creation point | Data and credentials disclosed | Current check | Evidence today | DENY behavior today | Zero attempt on provider-off? | Boundary status |
|---|---|---|---|---|---|---|---|---|
| Cap 16 web search and source reads | Brave Search, DuckDuckGo, and result-page hosts | `WebSearchExecutor` -> `NetworkMediator.request` | Search query; Brave token for Brave calls; selected result URLs for source reads | Cap 16 enabled; key selects Brave, otherwise DuckDuckGo; no provider-neutral Data-Out check | One mediator event per successful call/failure class | Disabled cap stops mediator calls; no provider-off policy exists | No provider-policy guarantee | Mediated but not Data-Out governed |
| Cap 48 source search | Brave Search or DuckDuckGo | `MultiSourceReportingExecutor` -> `NetworkMediator.request` with cap 48 | Report query; Brave token when configured | Cap 48 enabled; provider chosen from key availability | Mediator events for search calls | Disabled cap stops at mediator; no provider-off policy exists | No provider-policy guarantee | Mediated but combined with separate nested DeepSeek egress |
| Cap 56 news / RSS | Multiple publisher RSS endpoints and article/source hosts | `fetch_rss_headlines` and `NewsIntelligenceExecutor` -> `NetworkMediator.request` | Feed URL requests and source-page requests; normally no credential | Cap 56 enabled; fixed/configured source list | Mediator events per request | Disabled cap stops mediator calls | Yes for cap disable; no broader destination policy | Mediated external reads |
| Cap 55 weather | Visual Crossing | `WeatherService` -> `NetworkMediator.request` | User/default location and forecast scope; weather API key as query parameter | Cap 55 enabled and key present; no provider-neutral Data-Out check | Mediator event includes URL but not params/key | Missing key or disabled cap prevents request | Cap disable yes; provider-off no | Mediated; location is personal data requiring disclosure classification |
| Cap 65 Shopify read-only connector | User's Shopify Admin GraphQL endpoint | `HttpShopifyConnector._gql` creates a mediator per call | GraphQL query/variables; shop domain; Admin access token header; returned store/order/inventory data | Cap 65 enabled; connector configuration; no common Data-Out decision | Mediator metadata; higher-level connector errors | Disabled cap stops mediator call | Yes for cap disable; no provider-policy guarantee | Mediated external read with credential and tenant-data disclosure |
| Google Workspace OAuth setup, refresh, identity, revoke | Google OAuth token, userinfo, and revoke endpoints | `GoogleAuthSession` -> `NetworkMediator.connection_request` | Authorization code, client credentials, refresh/access token, redirect URI; bearer token for identity | Static provider/operation/method/URL allowlist and rate/SSRF controls; deliberately no capability/Governor check | `CONNECTION_NETWORK_CALL` / failure metadata, without payload/header values | Non-allowlisted operation is rejected before transport. There is no global Data-Out deny | No | Explicit setup exception; needs a setup-specific disclosure decision at the same final boundary |
| Settings connection health: OpenAI | OpenAI models endpoint | Direct `requests.get` in `connections_api.py` | Saved API key in bearer header | Local administrative API call after save/test; no mediator, capability, or provider Data-Out check | Health status in connection store; no durable network/disclosure receipt | No Data-Out deny path | **No** | Documented direct-network exception and hard bypass |
| Settings connection health: Brave | Brave Search | Direct `requests.get` in `connections_api.py` | Literal query `test`; subscription token | Same as above | Same as above | No Data-Out deny path | **No** | Hard bypass |
| Settings connection health: NewsAPI | NewsAPI headlines | Direct `requests.get` in `connections_api.py` | Country/page size; API key in query parameters | Same as above | Same as above | No Data-Out deny path | **No** | Hard bypass; credential is placed in URL query data |
| Settings connection health: Visual Crossing | Visual Crossing forecast | Direct `requests.get` in `connections_api.py` | Fixed `london` location; API key in query parameters | Same as above | Same as above | No Data-Out deny path | **No** | Hard bypass; credential is placed in URL query data |

### Tool, browser, process, and non-runtime surfaces

| Caller / surface | Destination / owner | Transport creation point | Data disclosed | Current check and evidence | DENY / zero-attempt status | Disposition for Data-Out design |
|---|---|---|---|---|---|---|
| Cap 63 OpenClaw network tools | Weather, RSS/news, web search, source pages | Allowlisted tool implementations use `MeteredNetworkProxy`, then `NetworkMediator` | Tool query, location, source URL, provider keys as applicable | Manual envelope preflight and per-run network-call budget; mediator receipts | Envelope/capability limits can deny before mediator; no provider-neutral Data-Out decision | Keep tool allowlist, but require every tool request to carry a disclosure decision into the final mediator. Budget is not custody |
| Cap 63 OpenClaw model fallback | OpenAI, described above | `OpenAIResponsesLane` | Task report and key | Caller-side routing/permission/budget plan | Normal caller has pre-call denial; final method does not enforce it | Move/duplicate the decisive policy at final egress so alternate callers cannot bypass it |
| Webpage launch capability | Default browser and arbitrary planned HTTPS site | `webbrowser.open(url)` | Destination URL; browser subsequently sends its own headers/cookies and may load the site | URL planner plus capability/Governor path; `WEBPAGE_LAUNCH` receipt records handoff result | A denied capability can stop handoff. After handoff Nova cannot prove zero connections or payload behavior | Treat handing a URL to the OS as egress initiation. Gate before `webbrowser.open`; receipt must say “delegated/opened,” never “site reached” |
| Email draft capability | Default mail client via `mailto:` | `webbrowser.open(mailto_uri)` | Recipient, subject, and full draft body are handed to another application | Governed draft/open flow; draft event exists | A denied action can stop handoff. Nova cannot prove whether the mail client synchronizes or sends after handoff | Gate before OS handoff; classify as disclosure to a local external application, distinct from email transmission |
| System/app/file launch | Arbitrary installed application selected by bounded system-control logic | `os.startfile` or `subprocess.run` | File path/arguments; launched application may independently use the network | Governed system-control action and OS process result, not child-network mediation | Nova can deny process launch; after launch it cannot observe/prove the child's network attempts | Do not claim child traffic is mediated. Gate the delegated action and mark child-owned networking outside proof unless a separately controlled proxy exists |
| STT executable and TTS/media player | Configured local binaries / OS player | `subprocess.run` / `subprocess.Popen` | Audio path/data and process arguments; no network is requested by Nova code | Local execution configuration and executor controls | Nova does not inspect whether a user-supplied binary networks | Classify as subprocess-owned behavior. No external-provider PASS may be inferred from process launch alone |
| Ollama availability status | Loopback `localhost:11434/api/tags` | Direct `urllib.request.urlopen` in `provider_status.py` | Local HTTP request only | Fixed loopback endpoint; no durable network receipt | No provider Data-Out policy; local attempt occurs when status is read | Explicit local-only exception; keep outside external Data-Out while testing that it cannot become nonlocal |
| Landing-page waitlist form | Formspree placeholder endpoint | Browser-side `fetch` in static landing script when a real form ID is configured | Email address entered on landing page | Placeholder configuration; outside backend mediator/ledger | Browser makes the request directly | Separate website/privacy surface. It must not be represented as governed Nova runtime egress |
| Archived quarantine code | Historical OpenAI/STT and phase-3.5 handlers | Non-imported archived source | Historical only | Excluded from current runtime | Not applicable unless restored | Keep excluded, and add a regression that restored runtime imports trigger inventory review |

## Bypasses and truth gaps

1. Provider health checks call `requests.get` directly and have no durable
   disclosure decision or network receipt.
2. DeepSeek's user-facing/provider-policy state is not checked by the external
   reasoning provider, bridge, general chat, or capabilities 31, 48, and 54.
3. Capabilities 31 and 54 are described as local/no-network in registry-generated
   truth while their runtime executors can invoke DeepSeek through cap 62.
4. Cap 48 has two independently governed-looking paths—search as cap 48 and
   reasoning as cap 62—with no single disclosure decision covering the action.
5. `OpenAIResponsesLane.summarize_task_report` relies on its caller to run the
   policy plan first.
6. `NetworkMediator` emits transport outcome metadata after a call or selected
   failure, but no durable pre-egress allow/deny decision. A failed receipt also
   does not undo an already-completed network request.
7. Google connection setup is intentionally outside capability execution. Its
   static endpoint allowlist is useful, but it is not consent to disclose OAuth
   credentials.
8. Browser/mail/app/subprocess handoffs leave Nova's observable boundary. Current
   success receipts prove a handoff, not a connection, send, or remote outcome.
9. The runtime auditor's direct-network report is requests-library-specific and
   does not cover all mechanisms listed here.
10. The default provider-budget objects include `enabled`, but budget-state
    computation does not use it. The field must not be treated as an egress gate.

## Required common enforcement contract

The implementation lane should introduce one provider-neutral contract, not a
set of provider-specific toggle checks.

Before **any** external transport creation or delegated egress handoff, the final
in-process boundary must receive an immutable request containing:

- initiating capability/caller and request/session/action identifiers;
- provider and normalized destination/destination class;
- transport class (`http`, OAuth setup, browser handoff, mail-client handoff,
  subprocess/application handoff, or local/private model);
- data categories being disclosed (for example prompt, conversation context,
  location, search query, document text, task report, shop data, OAuth material);
- credential category, never the credential value;
- purpose and whether the action is user-initiated, approved, or automatic;
- the applicable owner policy version.

The policy returns `ALLOW`, `DENY`, or `UNKNOWN`. Only `ALLOW` can continue.
`DENY` and `UNKNOWN` must return an explicit local result before DNS resolution,
socket/session/client creation, `requests`/`urllib`, `webbrowser.open`, or process
launch. Caller-side checks may improve UX but are not the security boundary.

The decision must produce durable evidence without payloads or secrets:
decision, provider/destination class, data categories, caller/capability,
purpose, policy version, correlation identifiers, and reason. Transport outcome
evidence remains separate. For delegated actions, outcome vocabulary must stop
at what Nova observed (for example `browser_handoff_accepted`) and must not imply
that a site loaded, mail was sent, or a child process made no network calls.

Local/private model traffic requires an explicit policy class rather than an
implicit exemption. It may follow a different default, but the endpoint must be
proven local/private before it receives that classification.

## Proposed implementation slices

These are review-sized slices, in order. None is implemented by this inventory.

1. **Pure policy and evidence vocabulary.** Add immutable disclosure request and
   decision types, provider/destination classification, data-category vocabulary,
   durable allow/deny evidence, and fail-closed behavior when policy/evidence is
   unavailable.
2. **Final HTTP boundary.** Enforce the contract inside `NetworkMediator.request`
   and `connection_request` immediately before URL validation/DNS/client use.
   Require callers to supply disclosure metadata; prohibit silent defaults for
   external destinations.
3. **Known model leak closure.** Route general chat, caps 31/48/54/62, and the
   OpenAI fallback through the final-boundary decision. Align capability/runtime
   truth with their actual network behavior.
4. **Administrative setup and health.** Replace direct health-check requests with
   an explicitly governed setup/health transport using the same disclosure
   decision and evidence contract.
5. **Search/weather/news/commerce/connectors.** Add precise data categories and
   provider/destination identities for caps 16/48/55/56/65 and Google OAuth.
6. **Delegated egress.** Gate browser, mail-client, app, and subprocess handoffs
   before delegation; use truthful handoff-only receipts. Define which child-owned
   networking is out of proof rather than claiming it is blocked.
7. **Static enforcement and generated truth.** Expand network-mechanism scanning
   beyond `requests`, require every external transport/handoff to name the common
   boundary, and regenerate capability/bypass truth.

Each slice must preserve existing authority/approval gates. Data-Out permission
is an additional necessary condition, never a replacement for capability or
action approval.

## Zero-attempt proof strategy

Every affected path needs a red-before-green regression against this baseline.
For a `DENY` and for an unresolvable/`UNKNOWN` policy result, tests must prove:

```text
policy evaluated before egress
-> network client/session/socket not invoked
-> zero DNS lookup and zero connection attempt
-> zero payload or credential transmission
-> explicit local result
-> durable disclosure-decision evidence
-> no transport-success receipt
```

Required test layers:

1. **Boundary unit tests:** inject spies that fail if `socket.getaddrinfo`,
   `requests.request`, `requests.Session`, session `.request`, `urllib.urlopen`,
   `webbrowser.open`, `os.startfile`, `subprocess.run`, or `subprocess.Popen` is
   touched after denial. Use the real ledger/event taxonomy for decision evidence.
2. **Real caller regressions:** exercise general chat and capabilities 31, 48,
   54, 62, 63, plus caps 16, 55, 56, and 65, proving the final transport spy sees
   zero calls. Cap 48 must prove both its search and nested reasoning legs.
3. **Setup regressions:** save/test provider credentials and Google OAuth
   operations under denial; prove no direct or mediated request occurs and no
   credential appears in evidence.
4. **Delegation regressions:** deny webpage, mail draft, and system/app launch;
   prove the OS handoff function is untouched.
5. **Local/private classification tests:** prove loopback/private model traffic is
   classified separately and that public, DNS-rebound, or ambiguous endpoints do
   not inherit the local exemption.
6. **Static mechanism test:** scan runtime imports/calls for HTTP clients, sockets,
   browser handoffs, and process launch. A new surface must either use the common
   boundary or appear as an unresolved inventory failure.
7. **End-to-end session proof:** through the real websocket/session route, turn a
   provider off, invoke each user-visible route, and assert an explicit local
   denial, a durable decision record, and zero transport attempts.
8. **Negative proof:** run each new regression against `bab4a6c` or the relevant
   pre-fix slice and retain the failure evidence in the PR.

## Review gate

Implementation should not start until review confirms that this inventory has no
missing runtime egress class, that each documented exception has an explicit
disposition, and that the common contract can enforce denial at the last
in-process point before transport or delegation.

The next lane is provider-neutral Data-Out implementation test-first. It is not
authorized by this document alone.
