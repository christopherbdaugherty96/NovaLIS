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

### Frozen closure scope

The final mechanism-closure sweep covers supported production/runtime and setup
surfaces only:

- Python HTTP creation through Requests/sessions and `urllib`, including DNS,
  sockets, redirects, prepared requests, and failure evidence;
- environment and platform proxy discovery, bypass rules, and proxy credentials;
- ambient credentials such as `.netrc` / `NETRC` and credentials injected after
  caller arguments are formed;
- every supported installer/launcher child capable of networking: all Ollama CLI
  invocations, pip, winget, browser/application handoffs, and startup probes;
- supported browser-side external requests and delegated OpenClaw/provider paths;
- credentials or sensitive values carried in origin URLs, query, header, body,
  proxy, or persisted error fields.

Developer-only certification/audit scripts, tests, archived/quarantined code,
inactive future paths, and hypothetical mechanisms are outside this closure
scope. A concrete production defect found later is tracked separately unless it
invalidates an inventory claim about one of the supported surfaces above.

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
| Cap 62 governed second opinion | DeepSeek, same endpoint | Normal user-facing route: `ExternalReasoningExecutor` -> `ResponseVerificationExecutor` -> `DeepSeekBridge` -> provider -> mediator cap 62 | Explicit answer/exchange and review prompt; API key | `ExternalReasoningExecutor` first checks `external_reasoning_enabled`; lower layers then check cap 62, key, and usage budget | Local paused result when the setting denies; otherwise mediator and provider-usage events | On the normal governed cap-62 route, a disabled `external_reasoning_enabled` setting returns locally before the bridge and makes zero network attempts | **Yes on the normal cap-62 executor route; not an invariant of the lower-level provider/transport** | Existing caller-side setting gate is real and must be preserved, but other callers of `DeepSeekBridge` and direct lower-level calls do not inherit it; the final egress boundary still lacks provider-neutral Data-Out policy/evidence |
| OpenClaw metered summarization fallback (within cap 63 runs) | OpenAI Responses API, `api.openai.com/v1/responses` | `OpenAIResponsesLane` -> `NetworkMediator.request` using cap 62 | Full task-report prompt, system prompt, task content; OpenAI key | Caller normally invokes `plan_for_openclaw_fallback`: routing mode `budgeted_fallback`, `metered_openai_enabled`, key, budget. `summarize_task_report` itself only requires the key | Mediator metadata plus provider-usage result | The normal caller returns deterministic/local output when the plan denies. A direct method caller could skip the plan | **Yes on the normal OpenClaw caller; not guaranteed at the transport method** | Policy is caller-side rather than an invariant at final egress |
| Local chat / local reasoning / OpenClaw local summary | Configured Ollama-compatible endpoint, every redirect target, **and any effective proxy** | `LLMManager` -> `ModelNetworkMediator` -> default `requests.Session.request` / `.post` | Prompts/context and generated output; no hosted-provider key by default. Userinfo in `OLLAMA_URL` can become an origin `Authorization` header. Environment or OS proxy configuration can route prompt-bearing traffic through a proxy even when the initial host is local/private | Only the initial endpoint must resolve to loopback/private/link-local. The Requests session retains `trust_env=True` and automatic redirects, so a local endpoint can redirect a prompt-bearing 307/308 request to a public host; proxy discovery and origin-URL credentials are also not independently authorized | `MODEL_NETWORK_CALL` / `MODEL_NETWORK_CALL_FAILED` stores the complete model URL, so origin userinfo can be persisted; evidence does not record redirect targets or effective proxy intermediaries | An initially invalid/public endpoint fails before the request; an allowed private endpoint may still redirect externally or use an unclassified proxy/credential | **No for automatic redirects, discovered proxies, or origin-URL credentials** | Not safely local/private until origin credentials and effective routing are classified, automatic redirects are disabled or every hop is authorized before send, and every persisted URL is sanitized |

### Search, news, weather, commerce, and provider setup

| Caller / capability | Provider and destination | Transport creation point | Data and credentials disclosed | Current check | Evidence today | DENY behavior today | Zero attempt on provider-off? | Boundary status |
|---|---|---|---|---|---|---|---|---|
| Cap 16 web search and source reads | Brave Search, DuckDuckGo, and result-page hosts | `WebSearchExecutor` -> `NetworkMediator.request` | Search query; Brave token for Brave calls; selected result URLs for source reads | Cap 16 enabled; key selects Brave, otherwise DuckDuckGo; no provider-neutral Data-Out check | One mediator event per successful call/failure class | Disabled cap stops mediator calls; no provider-off policy exists | No provider-policy guarantee | Mediated but not Data-Out governed |
| Cap 48 source search | Brave Search or DuckDuckGo | `MultiSourceReportingExecutor` -> `NetworkMediator.request` with cap 48 | Report query; Brave token when configured | Cap 48 enabled; provider chosen from key availability | Mediator events for search calls | Disabled cap stops at mediator; no provider-off policy exists | No provider-policy guarantee | Mediated but combined with separate nested DeepSeek egress |
| Cap 56 news / RSS | Multiple publisher RSS endpoints | `fetch_rss_headlines` -> `NetworkMediator.request` | Feed URL requests; normally no credential | Cap 56 enabled; fixed/configured source list | Mediator events per request | Disabled cap stops mediator calls | Yes for cap disable; no broader destination policy | Mediated external feed reads; distinct from caps 49/50 source-page reads |
| Cap 49 headline and story-page summary | Article/source hosts selected from the cached news surface | `NewsIntelligenceExecutor.execute_summary` -> `_collect_source_packets` or `_summarize_story_page` -> `_fetch_source_text` -> `NetworkMediator.request` with cap 49 | Selected source URLs and ordinary HTTP request metadata; returned article text is then passed to the local analysis lane | Cap 49 enabled; cached headline selection and bounded source-read limits; no provider-neutral destination/Data-Out check | Mediator events for each source-page read; result/summary evidence at the capability layer | Disabled cap stops execution; no source/destination Data-Out deny exists | Yes for cap disable; no provider/destination-policy guarantee | Mediated external source reads owned by cap 49, not cap 56 |
| Cap 50 daily intelligence brief with `read_sources` | Article/source hosts selected from cached headlines | `NewsIntelligenceExecutor.execute_brief` -> `_collect_source_packets` -> `_fetch_source_text` -> `NetworkMediator.request` with cap 50 | Up to the bounded set of selected source URLs and ordinary HTTP request metadata; returned excerpts feed local brief synthesis | Cap 50 enabled and `read_sources` requested; bounded source-read limits; no provider-neutral destination/Data-Out check | Mediator events for each source-page read; brief result evidence at the capability layer | Disabled cap stops execution; actions that reuse cached clusters do not read sources, but a source-reading brief has no Data-Out deny | Yes for cap disable; no provider/destination-policy guarantee | Conditional mediated external source reads owned by cap 50, not cap 56 |
| Cap 55 weather | Visual Crossing | `WeatherService` -> `NetworkMediator.request` | User/default location and forecast scope; weather API key as query parameter | Cap 55 enabled and key present; no provider-neutral Data-Out check | Success metadata omits params/key, but on HTTP failure `NetworkMediator` persists raw `str(exception)` in `NETWORK_CALL_FAILED`; Requests can include the fully prepared credential-bearing URL in that text. Tracked as current P1 defect #461 | Missing key or disabled cap prevents request; an attempted request can persist the query credential on failure | Cap disable yes; provider-off no | Mediated, but failure evidence is not secret-safe today; location is personal data requiring disclosure classification |
| Cap 65 Shopify read-only connector | User's Shopify Admin GraphQL endpoint | `HttpShopifyConnector._gql` creates a mediator per call | GraphQL query/variables; shop domain; Admin access token header; returned store/order/inventory data | Cap 65 enabled; connector configuration; no common Data-Out decision | Mediator metadata; higher-level connector errors | Disabled cap stops mediator call | Yes for cap disable; no provider-policy guarantee | Mediated external read with credential and tenant-data disclosure |
| Google Workspace OAuth setup, refresh, identity, revoke | Google OAuth token, userinfo, and revoke endpoints | `GoogleAuthSession` -> `NetworkMediator.connection_request` | Authorization code, client credentials, refresh/access token, redirect URI; bearer token for identity | Static provider/operation/method/URL allowlist and rate/SSRF controls; deliberately no capability/Governor check | `CONNECTION_NETWORK_CALL` / failure metadata, without payload/header values | Non-allowlisted operation is rejected before transport. There is no global Data-Out deny | No | Explicit setup exception; needs a setup-specific disclosure decision at the same final boundary |
| Settings connection health: OpenAI | OpenAI models endpoint | Direct `requests.get` in `connections_api.py` | Saved API key in bearer header | Local administrative API call after save/test; no mediator, capability, or provider Data-Out check | Health status in connection store; no durable network/disclosure receipt | No Data-Out deny path | **No** | Documented direct-network exception and hard bypass |
| Settings connection health: Brave | Brave Search | Direct `requests.get` in `connections_api.py` | Literal query `test`; subscription token | Same as above | Same as above | No Data-Out deny path | **No** | Hard bypass |
| Settings connection health: NewsAPI | NewsAPI headlines | Direct `requests.get` in `connections_api.py` | Country/page size; API key in query parameters | Same as above | Same as above | No Data-Out deny path | **No** | Hard bypass; credential is placed in URL query data |
| Settings connection health: Visual Crossing | Visual Crossing forecast | Direct `requests.get` in `connections_api.py` | Fixed `london` location; API key in query parameters | Same as above | Same as above | No Data-Out deny path | **No** | Hard bypass; credential is placed in URL query data |

### Tool, browser, process, and non-runtime surfaces

| Caller / surface | Destination / owner | Transport creation point | Data disclosed | Current check and evidence | DENY / zero-attempt status | Disposition for Data-Out design |
|---|---|---|---|---|---|---|
| Proxy intermediary and proxy authentication (cross-cutting) | Host selected by `HTTP_PROXY`, `HTTPS_PROXY`, or `ALL_PROXY` (and lowercase forms), or by OS proxy configuration such as Windows Internet Settings, unless bypassed | Default Requests sessions/calls and `urllib` openers use `urllib.request.getproxies()`, which can consult both process environment and platform configuration; launcher tools such as `curl` can also consult proxy settings. Requests can derive `Proxy-Authorization` from userinfo in the effective proxy URL during adapter handling | Whatever payload and credentials the proxied caller sends; proxy URL userinfo can become a transmitted proxy credential after ordinary caller/prepared-request inspection. For HTTPS the proxy observes the connection destination; plain HTTP proxying can expose request content | No common effective-route classification, complete proxy-source disablement, proxy-credential classification, or proxy-specific disclosure evidence | A URL-host allow decision does not deny the proxy intermediary, prove a direct connection, or authorize credentials injected for the proxy | The final boundary must disable/bypass **all** platform and environment proxy discovery where direct routing is required, or derive, classify, authorize, and evidence every effective proxy plus proxy-credential **presence** before send; values must never enter evidence |
| Ambient Requests authentication (cross-cutting) | Host credentials selected from `~/.netrc` or the file named by `NETRC` | Requests can apply netrc authentication while preparing a request when `Session.trust_env=True` and explicit auth is absent | Username/password become an `Authorization` header even though that header was not present in the caller's inputs | No boundary check of the fully prepared request and no netrc-specific evidence | Caller-input validation can pass before Requests injects a credential | Disable ambient netrc authentication at governed boundaries, or validate and authorize the fully prepared request—including the injected header—before any DNS/socket/send operation |
| Cap 63 OpenClaw network tools | Weather, RSS/news, web search, source pages | Allowlisted tool implementations use `MeteredNetworkProxy`, then `NetworkMediator` | Tool query, location, source URL, provider keys as applicable | Manual envelope preflight and per-run network-call budget; mediator receipts | Envelope/capability limits can deny before mediator; no provider-neutral Data-Out decision | Keep tool allowlist, but require every tool request to carry a disclosure decision into the final mediator. Budget is not custody |
| Cap 63 OpenClaw model fallback | OpenAI, described above | `OpenAIResponsesLane` | Task report and key | Caller-side routing/permission/budget plan | Normal caller has pre-call denial; final method does not enforce it | Move/duplicate the decisive policy at final egress so alternate callers cannot bypass it |
| Webpage launch capability | Default browser and arbitrary planned HTTPS site | `webbrowser.open(url)` | Destination URL; browser subsequently sends its own headers/cookies and may load the site | URL planner plus capability/Governor path; `WEBPAGE_LAUNCH` receipt records handoff result | A denied capability can stop handoff. After handoff Nova cannot prove zero connections or payload behavior | Treat handing a URL to the OS as egress initiation. Gate before `webbrowser.open`; receipt must say “delegated/opened,” never “site reached” |
| Email draft capability | Default mail client via `mailto:` | `webbrowser.open(mailto_uri)` | Recipient, subject, and full draft body are handed to another application | Governed draft/open flow; draft event exists | A denied action can stop handoff. Nova cannot prove whether the mail client synchronizes or sends after handoff | Gate before OS handoff; classify as disclosure to a local external application, distinct from email transmission |
| System/app/file launch | Arbitrary installed application selected by bounded system-control logic | `os.startfile` or `subprocess.run` | File path/arguments; launched application may independently use the network | Governed system-control action and OS process result, not child-network mediation | Nova can deny process launch; after launch it cannot observe/prove the child's network attempts | Do not claim child traffic is mediated. Gate the delegated action and mark child-owned networking outside proof unless a separately controlled proxy exists |
| STT executable and TTS/media player | Configured local binaries / OS player | `subprocess.run` / `subprocess.Popen` | Audio path/data and process arguments; no network is requested by Nova code | Local execution configuration and executor controls | Nova does not inspect whether a user-supplied binary networks | Classify as subprocess-owned behavior. No external-provider PASS may be inferred from process launch alone |
| Ollama availability status | Nominal loopback `localhost:11434/api/tags` **and any effective proxy** | Direct default `urllib.request.urlopen` in `provider_status.py` | Status probe URL and ordinary HTTP metadata; no prompt or provider credential, but an external proxy receives the nominally local request | Fixed loopback origin, but the default urllib opener can inherit environment or OS proxy configuration; no effective-route check or durable network receipt | No provider Data-Out policy; reading provider status can contact an external proxy when loopback is not bypassed | Local-only exception is valid only after proving direct loopback routing. Otherwise classify/authorize the proxy or deny before `urlopen`; never infer local-only from the origin URL alone |
| Startup Ollama probe | Configurable `OLLAMA_URL` plus any proxy selected by `urllib` | `scripts/start_daemon.py` calls `urllib.request.urlopen` before starting the backend and while polling a newly launched Ollama process | Probe URL and ordinary HTTP metadata; no prompt payload, but a nonlocal URL or proxy causes pre-runtime outbound traffic | No loopback/private validation, common mediator, capability check, disclosure decision, or durable receipt | The attempt occurs before Nova's runtime boundary exists; failure is swallowed and may be followed by launching/polling `ollama serve` | Hard pre-start bypass. The launcher must prove a direct local/private destination or deny without calling `urlopen`; it must not inherit an unclassified proxy route |
| Python-launcher Nova readiness and browser handoff | Loopback-validated `NOVA_HOST`/`NOVA_PORT`, any proxy selected by `urllib`, and Edge/Chrome/default browser | `scripts/start_daemon.py` polls `HEALTH_ENDPOINT` with `urllib.request.urlopen`, then uses `subprocess.Popen` for Edge/Chrome app mode or `webbrowser.open(BASE_URL)` | Readiness URL and ordinary HTTP metadata; dashboard URL handed to another application | `require_loopback_bind_host` validates the URL host, but readiness does not disable/classify proxies and browser delegation has no disclosure decision or durable handoff receipt | A proxy can turn the readiness probe into external egress; after browser handoff Nova cannot prove navigation behavior | Prove a direct loopback route before readiness and handoff. On denial, touch neither `urlopen`, Edge/Chrome process launch, nor `webbrowser.open` |
| Shell-launcher readiness and dashboard handoff | Configurable `NOVA_HOST`/`NOVA_PORT`, any proxy selected by `curl` or `urllib`, any additional URL/proxy/credential loaded by ambient curl configuration, and the OS default browser | `start_nova.sh` calls `curl` or Python `urllib.request.urlopen` for `/phase-status`, then delegates the dashboard URL through `xdg-open` or `open`; current `curl -fsS` permits automatic loading of `~/.curlrc` | Readiness URL and ordinary HTTP metadata; dashboard URL handed to another application. A nonloopback host, proxy, or ambient curl-configured transfer can make the launcher perform external transport or disclose credentials | No launcher-local loopback validation, curl configuration disablement, common mediator, disclosure decision, or durable receipt before readiness or handoff | Readiness can attempt traffic beyond the intended loopback URL before the backend proves its locality; browser handoff can independently cause navigation | Hard pre-runtime/delegated bypass. Invoke curl with `-q`/`--disable` as its first argument and prove a direct loopback target with proxies bypassed/disabled before readiness; otherwise touch neither HTTP client nor dashboard opener |
| Installer and launcher Ollama CLI | Endpoint selected by `OLLAMA_HOST`, Ollama's model registry, and any other networking owned by the installed `ollama` executable | `nova_bootstrap.ps1` invokes `ollama --version`; `fetch_models.py` invokes `ollama --version`, `ollama list`, and `ollama pull <model>`; `start_daemon.py` can launch `ollama serve` | Version/list probes can disclose request metadata to a remote `OLLAMA_HOST`; pull discloses the model identifier and uses child-owned credentials/configuration; downloaded model bytes return to Ollama's store. `ollama serve` is a local process launch, not proof of local-only child behavior | `-SkipModel` skips `fetch_models.py` but not the bootstrap `ollama --version` probe. No invocation has a Nova disclosure decision/receipt, and Nova does not mediate the child transport | Any Ollama CLI invocation can occur before Nova's runtime boundary; denying only `pull` does not stop version/list probes | Reviewed setup/launcher exception only: classify `OLLAMA_HOST`, require authorization before **any** Ollama subprocess, constrain commands/model identifiers, record delegated outcome truthfully, and never claim child traffic is mediated or zero-attempt after handoff |
| Installer Python dependency acquisition | PyPI/package indexes and any proxy or alternate index used by pip | `installer/windows/nova_bootstrap.ps1` runs the venv interpreter with `-m pip install --upgrade pip`, then `-m pip install -e <install-dir>`; an uncached editable install may resolve and download project dependencies | Package names, versions, platform/Python metadata, index/proxy credentials configured for pip, and downloaded packages | Required by the supported bootstrap path; no Nova runtime boundary, disclosure decision, or durable receipt. Pip owns resolution and transport | The bootstrap invokes pip before Nova starts; without an explicit offline/deny mode, external attempts can occur | Reviewed setup exception only: make online dependency acquisition explicit and separately skippable/offline-capable, authorize before subprocess launch, prefer a locked/verified artifact source, record delegated outcome only, and never claim Nova mediated pip traffic |
| Installer prerequisite acquisition | Microsoft winget sources, Python/Ollama package sources, and child-owned redirects/CDNs | `installer/windows/nova_bootstrap.ps1` can run `winget install Python.Python.3.12` and `winget install Ollama.Ollama` when prerequisites are absent | Package identifiers, platform/device metadata exposed by winget, configured source credentials, and downloaded installers/packages | Supported noninteractive bootstrap accepts required agreements and invokes winget before Nova exists; no disclosure decision or Nova receipt | A fresh install can make external attempts automatically unless a preflight denial/offline mode stops before winget invocation | Reviewed setup exception only: detect missing prerequisites, disclose the required online acquisition, require explicit setup authorization or fail with offline/manual instructions, constrain package IDs/sources, and record only delegated process outcome |
| Landing-page waitlist form | Formspree placeholder endpoint | Browser-side `fetch` in static landing script when a real form ID is configured | Email address entered on landing page | Placeholder configuration; outside backend mediator/ledger | Browser makes the request directly | Separate website/privacy surface. It must not be represented as governed Nova runtime egress |
| Archived quarantine code | Historical OpenAI/STT and phase-3.5 handlers | Non-imported archived source | Historical only | Excluded from current runtime | Not applicable unless restored | Keep excluded, and add a regression that restored runtime imports trigger inventory review |

## Bypasses and truth gaps

1. Provider health checks call `requests.get` directly and have no durable
   disclosure decision or network receipt.
2. The normal user-facing cap-62 `ExternalReasoningExecutor` correctly checks
   `external_reasoning_enabled` and denies locally before calling the bridge.
   That setting is not enforced by the lower-level DeepSeek provider/transport,
   `DeepSeekBridge`, general chat, or capabilities 31, 48, and 54, so it is not a
   universal provider-neutral Data-Out control.
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
11. Requests and `urllib` can inherit environment and OS proxy configuration.
    On Windows, `urllib.request.getproxies()` can read Internet Settings registry
    proxies even when proxy environment variables are unset. Validating only the
    URL host does not prove that local/private traffic stays local or that
    external traffic reaches only the declared destination.
12. The startup launcher probes configurable `OLLAMA_URL` directly before the
    backend and its mediators exist.
13. The supported macOS/Linux shell launcher derives readiness and dashboard URLs
    from configurable `NOVA_HOST`, can inherit proxy settings, and currently lets
    curl load ambient `~/.curlrc` directives that may add external transfers,
    proxies, or credentials. It can also hand the URL to another application
    before a governed runtime boundary applies.
14. The Python launcher validates `NOVA_HOST` as loopback, but its Nova readiness
    probe can still inherit a proxy and its Edge/Chrome/default-browser handoff is
    delegated behavior outside the mediator.
15. Requests can add ambient netrc credentials while preparing a request after
    caller-supplied metadata was formed.
16. Windows setup can delegate model download to `ollama pull`; Nova controls the
    subprocess launch, not the child's network transport.
17. Windows bootstrap runs pip upgrade/editable-install commands before Nova
    starts. An uncached install can contact PyPI or configured indexes and
    proxies; those child-owned requests are not currently authorized or evidenced.
18. Windows bootstrap can invoke winget to install Python and Ollama before Nova
    starts. Those prerequisite downloads and their redirects are child-owned
    external traffic with no current disclosure decision or Nova evidence.
19. Ollama CLI checks are not necessarily local: `ollama --version` and `ollama
    list` can contact the service selected by `OLLAMA_HOST`. `-SkipModel` does not
    skip the bootstrap's version probe, so blocking only `ollama pull` is
    insufficient.
20. Requests can derive proxy authentication from userinfo in an effective proxy
    URL during adapter handling. Validating caller headers or ambient netrc alone
    does not classify that subsequently transmitted credential.
21. `ModelNetworkMediator` validates only the initial endpoint and permits
    Requests to follow redirects automatically. A local/private endpoint can
    redirect a prompt-bearing POST to a public destination without a new policy
    decision.
22. Userinfo embedded in `OLLAMA_URL` can become an origin `Authorization` header,
    while model success/failure evidence currently persists the complete URL.
    The credential is therefore both unclassified for transmission and unsafe in
    durable evidence.
23. `NETWORK_CALL_FAILED` currently stores raw exception text. For callers such
    as WeatherService that place credentials in query parameters, Requests can
    include the credential-bearing prepared URL in that text. This reachable P1
    persistence defect is tracked separately as #461 and must be repaired before
    the provider-neutral Data-Out slices begin.
24. The runtime provider-status probe uses the default urllib opener. Its fixed
    loopback URL can still route through an environment- or OS-configured proxy,
    so status inspection is not a proven local-only exception today.

## Required common enforcement contract

The implementation lane should introduce one provider-neutral contract, not a
set of provider-specific toggle checks.

Before **any** external transport creation or delegated egress handoff, the final
in-process boundary must receive an immutable request containing:

- initiating capability/caller and request/session/action identifiers;
- caller-declared provider/purpose plus the normalized destination and destination
  class **derived by the boundary from the actual transport URL**;
- transport class (`http`, OAuth setup, browser handoff, mail-client handoff,
  subprocess/application handoff, or local/private model);
- boundary-verified data categories being disclosed (for example prompt,
  conversation context, location, search query, document text, task report, shop
  data, OAuth material), bound to the actual body, parameters, and headers;
- boundary-verified credential categories and presence, never credential values;
- purpose and whether the action is user-initiated, approved, or automatic;
- the applicable owner policy version.

The boundary must reject a caller-declared provider or destination that does not
match the URL-derived identity. It must also derive the effective route: a proxy
is an additional destination/intermediary, not an invisible implementation
detail. Local/private classification is valid only when the client is proven not
to route through an unclassified proxy. That proof must account for both
environment variables and platform proxy sources (including Windows Internet
Settings), rather than treating an empty proxy environment as direct routing.
If the effective proxy URL contains credentials, the boundary must derive and
authorize proxy-credential presence before adapter send; it must never persist
the userinfo or generated `Proxy-Authorization` value.

Origin URLs must not be treated as harmless destination strings. The boundary
must reject unsupported userinfo or derive and authorize origin-credential
presence before preparation/send. Durable evidence must store a normalized,
sanitized destination with userinfo and credential-bearing query values removed.

The boundary must not trust free-form caller labels for disclosed data or
credentials. Boundary-owned typed adapters for each supported request shape must
map the actual body fields, query parameters, and header names to disclosure and
credential categories. An undeclared, omitted, extra, ambiguous, or
adapter-unknown outgoing field fails closed. Evidence stores only verified
categories/presence and safe structural metadata, never payload or credential
values.

Validation must cover the request that will actually be sent, not only the
caller's arguments. Governed HTTP clients should disable ambient netrc auth. If
ambient auth is intentionally supported, the boundary must prepare the request
without performing I/O, inspect the resulting method/URL/body/query/header names,
derive the injected credential category, and run policy on that exact prepared
request before DNS, socket creation, or send. Any mutation after authorization
invalidates the decision.

The policy returns `ALLOW`, `DENY`, or `UNKNOWN`. Only `ALLOW` can continue.
`DENY` and `UNKNOWN` must return an explicit local result before DNS resolution,
socket/session/client creation, `requests`/`urllib`, `webbrowser.open`, or process
launch. Caller-side checks may improve UX but are not the security boundary. An
HTTP redirect is a new destination in **every governed HTTP client**, including
`NetworkMediator` and `ModelNetworkMediator`: the boundary must derive and
authorize every redirect target after reading `Location` and **before** issuing
the next request.
Authorization of the original URL never carries across a redirect hop.
Original headers, parameters, credentials, and bodies also do not automatically
carry across hops. On a cross-origin redirect, origin-bound fields must be stripped
by default. Any retained or reconstructed field set—even on a same-origin
redirect—must pass the typed adapter and a new decision for the exact next-hop
method, URL, body, parameters, and headers before transmission.

The decision must produce durable evidence without payloads or secrets:
decision, provider/destination class, data categories, caller/capability,
purpose, policy version, correlation identifiers, and reason. Transport outcome
evidence remains separate and must pass a boundary-owned sanitizer before any
ledger write. Raw exception strings and credential-bearing URLs are not safe
evidence; query values, userinfo, credential/header values, and other secret-bearing
fields must be removed or replaced with bounded classifications. For delegated
actions, outcome vocabulary must stop
at what Nova observed (for example `browser_handoff_accepted`) and must not imply
that a site loaded, mail was sent, or a child process made no network calls.

Local/private model traffic requires an explicit policy class rather than an
implicit exemption. It may follow a different default, but both the endpoint and
effective route must be proven local/private before it receives that
classification. The startup launcher must enforce the same property before its
first `urlopen`, even though the backend is not running yet.

## Proposed implementation slices

These are review-sized slices, in order. None is implemented by this inventory.
The current failure-evidence credential leak is a separate narrow P1 (#461):
after this inventory merges, repair and prove that hotfix before Slice 1.

1. **Pure policy and evidence vocabulary.** Add immutable disclosure request and
   decision types, provider/destination classification, data-category vocabulary,
   durable allow/deny evidence, and fail-closed behavior when policy/evidence is
   unavailable.
2. **Final HTTP boundary.** Enforce the contract inside `NetworkMediator.request`,
   `connection_request`, and `ModelNetworkMediator` immediately before URL
   validation/DNS/client use.
   Derive destination identity from the transport URL, verify caller metadata,
   bind categories to actual outgoing fields through boundary-owned typed
   adapters, classify or disable effective proxies, and re-run the complete
   decision for every redirect target and exact field set before the next request.
   Strip origin-bound fields by default on cross-origin redirects. Prohibit silent
   defaults for external destinations.
3. **Known model leak closure.** Route general chat, caps 31/48/54/62, and the
   OpenAI fallback through the final-boundary decision while preserving cap 62's
   existing `external_reasoning_enabled` caller gate. Align capability/runtime
   truth with their actual network behavior.
4. **Administrative setup and health.** Replace direct health-check requests with
   an explicitly governed setup/health transport using the same disclosure
   decision and evidence contract.
5. **Search/weather/news/commerce/connectors.** Add precise data categories and
   provider/destination identities for caps 16/48/55/56/65 and Google OAuth.
6. **Delegated egress.** Gate browser, mail-client, app, and subprocess handoffs
   before delegation; use truthful handoff-only receipts. Define which child-owned
   networking is out of proof rather than claiming it is blocked. Treat installer
   every Ollama CLI invocation (`--version`, `list`, `pull`, and launcher
   `serve`), pip dependency acquisition, and winget prerequisite acquisition as
   explicit setup/launcher exceptions with pre-launch decisions, bounded
   commands/package/model identifiers and sources or locked artifacts,
   offline/skip paths, and delegated-outcome evidence.
7. **Local model and startup paths.** Disable/bypass environment proxies for
   traffic classified as local/private (or authorize the proxy as a separate
   destination), and fail closed on a nonlocal, ambiguous, or proxied
   `OLLAMA_URL` before the Python launcher's first probe. Reject or authorize
   origin userinfo, sanitize model URLs in evidence, and disable automatic model
   redirects or reauthorize every hop before the redirected send. Apply the same
   direct loopback proof to `start_nova.sh` before either readiness HTTP or
   dashboard handoff; require `curl -q`/`--disable` as the first curl argument so
   ambient curl configuration cannot add transfers, proxies, or credentials.
   Apply the direct-loopback proof to `provider_status.py` before its Ollama
   availability `urlopen` as well.
8. **Static enforcement and generated truth.** Expand network-mechanism scanning
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
   49, 50, 54, 62, 63, plus caps 16, 55, 56, and 65, proving the final transport
   spy sees zero calls. Cap 48 must prove both its search and nested reasoning
   legs. Cap 49 must cover both selected-headline packets and the direct
   story-page action. Cap 50 must cover the `read_sources` brief path.
3. **Setup regressions:** save/test provider credentials and Google OAuth
   operations under denial; prove no direct or mediated request occurs and no
   credential appears in evidence.
4. **Delegation regressions:** deny webpage, mail draft, and system/app launch;
   prove the OS handoff function is untouched.
5. **Local/private classification tests:** prove loopback/private model traffic is
   classified separately and that public, DNS-rebound, ambiguous, or
   environment-proxied endpoints do not inherit the local exemption. Set
   `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY` (including lowercase forms)
   without a matching `NO_PROXY` / `no_proxy`, then separately configure a
   Windows Internet Settings proxy with those variables absent. Prove neither
   case can earn a local/private classification or cause prompt, DNS, proxy, or
   session activity after denial. Use an effective proxy URL with userinfo and
   prove proxy-credential presence is classified and authorized before adapter
   send while no credential value enters evidence.
   Configure `OLLAMA_URL` with fake userinfo and prove the origin credential is
   denied or explicitly classified before send, and absent from all persisted
   model success/failure evidence.
   Exercise `_ollama_status()` with environment and Windows system proxies lacking
   a loopback bypass; prove the effective proxy is classified/authorized or
   `urllib.request.urlopen` remains untouched. A direct-loopback case must remain
   the separately proven local exception.
6. **Startup proof:** run Python-launcher decision logic with a nonlocal
   `OLLAMA_URL`, a relative/invalid URL, and a local URL subject to an environment
   proxy. Prove `urllib.request.urlopen` and process launch are untouched on
   denial. For the same Python launcher, prove its Nova `HEALTH_ENDPOINT` polling,
   Edge/Chrome `Popen`, and `webbrowser.open` are untouched when the effective
   route is proxied or unverified. Exercise `start_nova.sh` with
   nonloopback/invalid `NOVA_HOST` and with `http_proxy`/`HTTP_PROXY` lacking a
   matching `NO_PROXY`; prove `curl`, Python `urlopen`, `xdg-open`, and `open` are
   all untouched. Supply an ambient curl config containing an external URL,
   proxy, and credentials, and prove the launcher's curl invocation places
   `-q`/`--disable` first so none can be loaded or attempted. Valid direct-loopback
   probes and handoffs remain separately tested local exceptions.
7. **Redirect and identity tests:** run against both the external HTTP mediator
   and the local-model mediator. Allow the initial URL, return a redirect to a
   denied provider/destination, and prove the second request is never issued and
   the denial is recorded. Supply caller metadata that disagrees with the actual
   URL and prove rejection before DNS/client use. On a cross-origin redirect,
   prove authorization/API headers, query credentials, and request bodies are not
   reused. Where a same-origin or explicitly reconstructed redirect retains any
   field, prove a new decision binds the exact next-hop method/URL/fields. Cover
   cross-host and same-provider redirects because policy may distinguish
   destination classes. For the model path specifically, return a 307/308 from an
   allowed private endpoint to a public host and prove the prompt-bearing POST is
   never sent to the redirect target.
8. **Disclosure binding tests:** omit or mislabel a document body, prompt/context
   field, location/query parameter, OAuth form field, bearer/API-key header, and
   an adapter-unknown extra field. Prove each fails before DNS/client use. Then
   prove each supported typed adapter derives the expected categories from the
   actual outgoing structure without persisting values. Configure `~/.netrc` or
   `NETRC` for the destination and prove ambient credentials are either disabled
   or appear in the fully prepared request's verified credential categories;
   prove no post-decision credential injection is possible.
9. **Installer/launcher setup exception tests:** deny, skip, or select offline
   setup and prove no Ollama subprocess (`--version`, `list`, `pull`, or `serve`),
   pip install, or `winget install` is launched. Cover `-SkipModel`, remote
   `OLLAMA_HOST`, missing-Python, and missing-Ollama branches. On explicit allow,
   validate bounded commands/package/model identifiers and sources or a locked
   artifact source, and record only delegated launch/outcome evidence; do not
   assert that Nova controlled child sockets, redirects, or payloads.
10. **Evidence-hygiene regression:** use a fake Visual Crossing query credential,
   force an HTTP failure through the real `LedgerWriter`, and prove the credential,
   prepared query values, and raw exception text never reach `ledger.jsonl` or any
   other persisted failure evidence. Run it red against the #461 pre-fix code.
11. **Static mechanism test:** scan runtime imports/calls for HTTP clients, sockets,
   browser handoffs, and process launch. A new surface must either use the common
   boundary or appear as an unresolved inventory failure.
12. **End-to-end session proof:** through the real websocket/session route, turn a
   provider off, invoke each user-visible route, and assert an explicit local
   denial, a durable decision record, and zero transport attempts.
13. **Negative proof:** run each new regression against `bab4a6c` or the relevant
   pre-fix slice and retain the failure evidence in the PR.

## Review gate

Implementation should not start until a closure review confirms that every
supported runtime/setup egress mechanism in the frozen closure scope has an
inventory disposition, every credential- and proxy-derived route has a
disposition, every delegated boundary is identified, and there are no unresolved
P0/P1 omissions or misclassifications on those surfaces. The common contract must
be able to enforce denial at the last in-process point before transport or
delegation.

Once that gate passes, wording improvements, P2/P3 polish, developer-only tools,
archived code, future paths, and speculative mechanisms do not reopen #460. A
new concrete runtime defect becomes a separate issue unless it invalidates the
safety claim made by this inventory.

The next lane is provider-neutral Data-Out implementation test-first. It is not
authorized by this document alone.
