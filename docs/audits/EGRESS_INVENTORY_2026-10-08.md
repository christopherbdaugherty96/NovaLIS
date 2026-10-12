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
| Cap 65 Shopify read-only connector | Host configured by `NOVA_SHOPIFY_SHOP_DOMAIN`; intended to be the store's Shopify Admin GraphQL endpoint but currently accepts an arbitrary public host | `HttpShopifyConnector._gql` builds `https://<configured-domain>/admin/api/<version>/graphql.json` and creates a mediator per call | GraphQL query/variables; configured domain; Shopify Admin access-token header; returned store/order/inventory data. A malicious or mistaken non-Shopify host receives the token and query | Cap 65 enabled and connector configuration; the constructor strips a scheme but does not constrain the normalized host to an approved Shopify Admin domain; no common Data-Out decision | Mediator metadata; higher-level connector errors | Disabled cap stops mediator call, but an enabled cap can prepare and send the credential-bearing request to any configured host | Yes for cap disable; no provider/destination-policy guarantee | Credential-bearing mediated read with a caller-configurable destination. Normalize and require an approved Shopify Admin host before request preparation; reject userinfo, ports, paths, and non-Shopify hosts before constructing headers/body or invoking the mediator |
| Runtime-state persistence | Effective root selected by `NOVA_RUNTIME_DIR`, the source-tree `src` root, the `LOCALAPPDATA/Nova` writable fallback, or the home-directory `AppData/Local/Nova` fallback; every candidate may be UNC, redirected, mapped/network-drive, reparse-backed, or remotely mounted | `runtime_root` / `runtime_path`, `canonical_user_data_root`, and downstream ledger, connections, memory, durability, and state stores resolve/create and perform ordinary filesystem operations | Provider keys, ledger events, memory, receipts, snapshots, connection state, screenshots, and other sensitive runtime data | The override and every default/fallback candidate are accepted without proving effective backing local; `runtime_root` creates the selected root, while canonical durability paths call `resolve`; no disclosure decision or remote-storage receipt exists | Ordinary storage receipts describe application state, not whether the filesystem transported it off-device | An unset override is not proof of locality: resolution, directory creation, or a later write can authenticate to and transmit through remote backing even when every HTTP/process boundary denies | **No** | Classify **every** effective override/default/fallback root before `resolve`, writability/existence probes, `mkdir`, or storage access; authorize remote storage or fail closed. `UNKNOWN`/`DENY` must touch none of the candidates |
| FastAPI startup runtime snapshot writer | Seven installation-relative files under `PROJECT_ROOT/docs/current_runtime/`: `CURRENT_RUNTIME_STATE.md`, `GOVERNANCE_MATRIX.md`, `SKILL_SURFACE_MAP.md`, `BYPASS_SURFACES.md`, `RUNTIME_FINGERPRINT.md`, `GOVERNANCE_MATRIX_TREE.md`, and `ROUTE_PROTECTION_COVERAGE.md`; the project/install root may be UNC, mapped/network-drive, reparse-backed, or remotely mounted | Every `brain_server._lifespan()` startup calls `write_current_runtime_state_snapshot()`, which runs the runtime truth audit, calls `mkdir`, writes the current-state document, and calls `write_runtime_governance_docs()` to create/write the six companion documents | Generated runtime and governance truth, path metadata, source/runtime fingerprint evidence, and ambient network-share authentication | The startup call is unconditional; exceptions are caught and logged, but no locality classification or disclosure decision precedes the audit, directory creation, or writes. The Windows installer does not package `docs/`, so a supported install attempts to create this tree under `{app}` | Startup log records success or failure, not a pre-write locality/disclosure decision | Startup may probe, create, or write through network-backed installation storage; under a non-elevated Program Files install it may instead fail and log after the attempted operation | **No** | Classify the project/install backing without touching the target before the runtime audit or any path operation. `DENY`/`UNKNOWN` must perform no probe, `mkdir`, or write to the snapshot or any companion document |
| Goal state | Installation-relative `nova_backend/data/goals.json`; the installation root may itself be a UNC path, mapped/network drive, or remote mount | Import constructs `_GOALS_FILE` from `Path(__file__).resolve`; module singleton `GoalStore()` immediately calls `read_json_state`; `_save` calls `mkdir`, `open`, and `replace` | Goal titles, steps, statuses, permission envelopes, ledger references, timestamps, path metadata, and ambient share authentication | This store bypasses `runtime_root`; neither the installation root nor the goal path is classified before import-time resolution/read or later writes. The durability ownership record already marks it as migration-required | Goal records are application state, not remote-storage disclosure evidence | Merely importing the singleton can resolve/read a network-backed path; create/update can persist goal content remotely even when HTTP egress is denied | **No** | Supported setup must establish a locally backed installation root before Nova imports runtime code. Until this store migrates to governed runtime storage, classify/authorize its backing before the first path resolution, read, directory creation, temporary write, or replace; `DENY`/`UNKNOWN` touches none |
| Caps 52/53 story tracker state | Installation-relative `nova_workspace/story_tracker/`; the installation root may itself be network-backed | `StoryTrackerExecutor` derives `PROJECT_ROOT` with `Path(__file__).resolve`; `_read_json` uses `read_json_state`; `_write_json` calls `mkdir` and `write_text` for topics, graph, and per-story snapshots | Tracked topics, relationship links, story snapshots/events, timestamps, source-derived content, path metadata, and ambient share authentication | This store bypasses `runtime_root`; its backing is not classified before path construction/read/write. The durability ownership record already marks it as migration-required | Capability outcomes describe tracker operations, not whether state crossed a remote filesystem | View/update operations can probe/read/write a network-backed installation tree before any disclosure decision | **No** | Establish a locally backed installation root before runtime startup and classify/authorize the story-store backing before its first path operation; `DENY`/`UNKNOWN` must precede `resolve`, `read_json_state`, `mkdir`, `write_text`, or any story read/write. Migration is later implementation work, not part of this inventory |
| Cap 57 local calendar snapshot and calendar connection check | Path selected by `NOVA_CALENDAR_ICS_PATH`; intended to be a local `.ics` file but may be UNC/network-mounted storage | `connections_api._check_calendar` calls `Path.exists`; `CalendarSkill._calendar_path` calls `exists`/`is_file`, then `_read_events_for_range` calls `read_text` | Filesystem path; OS/network-share authentication metadata; calendar contents returned over the mounted transport | Cap 57 governance applies to the skill invocation, but the configured path is accepted without proving local backing; the settings health check is outside the capability path | Capability result/widget and settings status; no remote-filesystem disclosure decision or transport evidence | Existence/type checks alone can initiate remote access and credential authentication before calendar content is read | **No** for a remote path | Treat network-backed calendar access as external disclosure. Verify local backing or authorize the remote-storage destination before `exists`, `is_file`, or `read_text`; deny/unknown must touch none of them |
| STT upload transcription | Temporary directory selected by the OS/Python tempfile configuration, including `TEMP`; intended to be local but may resolve to UNC or network-mounted storage | `/stt/transcribe` -> `transcribe_bytes` -> `tempfile.TemporaryDirectory`, then `open(..., "wb")` writes the uploaded audio and ffmpeg writes converted WAV data | Raw user audio, converted audio, path metadata, and ambient network-share authentication | Route is local-only and transcription is local, but the temporary-storage backing is not classified before directory creation/write | No disclosure decision or receipt for temporary-storage transport | `TemporaryDirectory` creation or the first audio write can authenticate to and persist sensitive audio on remote storage | **No** for remote temp backing | Verify temp backing is local or authorize the remote-storage destination before `TemporaryDirectory`; `DENY`/`UNKNOWN` must create no directory/file and invoke no ffmpeg process |
| Live-screen frame analysis | Temporary file location selected by the OS/Python tempfile configuration, including `TEMP`; intended to be local but may resolve to UNC or network-mounted storage | `/api/live-screen/analyze` -> `tempfile.NamedTemporaryFile`, then OCR/vision analysis reads the saved frame | Sensitive shared-screen image bytes, path metadata, and ambient network-share authentication | Route protection is local-only, but temporary-storage locality is not checked before file creation/write | No disclosure decision or receipt for temporary-storage transport | `NamedTemporaryFile` can authenticate to and persist a screen frame remotely before analysis | **No** for remote temp backing | Verify temp backing is local or authorize the remote-storage destination before `NamedTemporaryFile`; `DENY`/`UNKNOWN` must create/write no file and invoke no OCR/vision reader |
| Cap 18 and ordinary Piper speech output | Model path selected by `NOVA_PIPER_MODEL_PATH` and WAV output under `TEMP`/the platform temp directory; either may be network-backed | Cap 18 `execute_tts()` and ordinary `nova_speak()` both reach `SpeechRenderer.render`; `inspect_voice_runtime()` reaches `_voice_preferred_engine_status` without rendering | Model-path metadata and ambient share authentication; model bytes read by Piper; synthesized user speech written to the WAV output path | Voice readiness and rendering treat model/output paths as local without backing classification. The status path calls `model_file.exists`; render calls `exists`, constructs the output path, then launches Piper | Speech events describe rendering/playback outcome, not remote-storage disclosure; readiness has no disclosure receipt | The readiness probe alone can authenticate to remote storage. Rendering can read a remote model and persist synthesized speech remotely before playback/cleanup | **No** for remote model or temp backing | Classify both model and output backing before the first `exists` or output-path operation. `DENY`/`UNKNOWN` must not probe the model, create/write/unlink the WAV, launch Piper, or start playback; cover cap 18, `nova_speak`, and readiness independently |
| Cap 60 explain selected file | Arbitrary path supplied through selected/working-context `file_path`; may resolve to UNC, mapped drive, or remote mount | `ExplainAnythingExecutor._explain_file` calls `Path.exists`, `is_file`, and `open`/`read` | Path metadata, ambient network-share authentication, and selected file contents returned over remote storage | Cap 60 governance controls invocation, but path backing is not classified before filesystem access | Capability outcome evidence; no remote-filesystem disclosure decision or transport evidence | `exists`/`is_file` can initiate remote access before the file is opened; remote content is then read into Nova | **No** for a remote path | Verify local backing or authorize the remote-storage destination before the first path operation; `DENY`/`UNKNOWN` must not call `exists`, `is_file`, `open`, or `read` |
| Cap 32 and runtime-settings disk health | Home-drive anchor derived from `Path.home().anchor`; on Windows the home may be UNC/network-backed | `OSDiagnosticsExecutor.execute` (cap 32) and `_runtime_health_projection` (including `/api/settings/runtime`) call `shutil.disk_usage` on that anchor | Filesystem/share metadata and ambient network-share authentication; returned capacity/usage figures | Cap 32 governs its explicit invocation, but settings health is outside that capability path and neither route classifies the anchor backing before `disk_usage` | Diagnostics/settings evidence reports health, not remote-filesystem disclosure | A routine status/settings read can contact SMB/network storage before any decision; denying later diagnostics output cannot undo it | **No** for remote/unknown home backing | Classify the lexical home anchor and trusted backing metadata before `disk_usage`; `DENY`/`UNKNOWN` must not call it and should return bounded `unknown` resource health without touching the share |
| Cap 22 open folder/path | Explicit `path` or preset user folder; preset/allowed roots may be redirected, mapped, reparse-backed, or remotely mounted | `OpenFolderExecutor.execute` calls `exists` before `SystemControlExecutor.open_path_result`; allowed-root/path normalization can call `resolve`, `is_dir`, and related probes before OS handoff | Requested path metadata, ambient share authentication, and the delegated path handed to the OS | Cap 22 and system-control rules govern the eventual handoff, but explicit and preset branches touch the filesystem before backing/locality is established | Action outcome records launch acceptance/visibility, not preliminary remote filesystem access | Remote access/authentication can occur even if the later launcher or allowed-root check rejects the request | **No** for remote backing | Classify explicit, preset, redirected-folder, allowed-root, symlink/junction/reparse, and mount backing before `resolve`, `exists`, type checks, or handoff; deny/unknown touches none |
| Local-project chat and inspection | Explicit project target, current working directory, working-context selected file, remembered `last_object`, and discovered project roots | `_resolve_existing_local_path`, `_candidate_local_project_paths`, and `_resolve_local_project_path`, followed by project summary/map/architecture helpers using `resolve`, `exists`, `is_dir`, `is_file`, `iterdir`, and `read_text` | Path metadata, ambient share authentication, directory structure, project files, README/architecture/source excerpts | User-facing local-project handlers are read-only, but neither explicit nor remembered/discovered candidates prove local backing before resolution and inspection | Chat/project widgets summarize inspected data; no remote-filesystem disclosure decision or transport evidence | Resolution, marker checks, enumeration, and reads can authenticate to or retrieve data from remote storage before any later response | **No** for remote backing | Classify explicit targets and every working-context/remembered/discovered candidate before the first resolve/probe; authorize remote storage or fail closed before enumeration, nested inspection, or reads |
| Google Workspace OAuth setup, refresh, identity, revoke | Google OAuth token, userinfo, and revoke endpoints | `GoogleAuthSession` -> `NetworkMediator.connection_request` | Authorization code, client credentials, refresh/access token, redirect URI; bearer token for identity | Static provider/operation/method/URL allowlist and rate/SSRF controls; deliberately no capability/Governor check | `CONNECTION_NETWORK_CALL` / failure metadata, without payload/header values | Non-allowlisted operation is rejected before transport. There is no global Data-Out deny | No | Explicit setup exception; needs a setup-specific disclosure decision at the same final boundary |
| Settings connection health: OpenAI | OpenAI models endpoint | Direct `requests.get` in `connections_api.py` | Saved API key in bearer header | Local administrative API call after save/test; no mediator, capability, or provider Data-Out check | Health status in connection store; no durable network/disclosure receipt | No Data-Out deny path | **No** | Documented direct-network exception and hard bypass |
| Settings connection health: Brave | Brave Search | Direct `requests.get` in `connections_api.py` | Literal query `test`; subscription token | Same as above | Same as above | No Data-Out deny path | **No** | Hard bypass |
| Settings connection health: NewsAPI | NewsAPI headlines | Direct `requests.get` in `connections_api.py` | Country/page size; API key in query parameters | Same as above | Same as above | No Data-Out deny path | **No** | Hard bypass; credential is placed in URL query data |
| Settings connection health: Visual Crossing | Visual Crossing forecast | Direct `requests.get` in `connections_api.py` | Fixed `london` location; API key in query parameters | Same as above | Same as above | No Data-Out deny path | **No** | Hard bypass; credential is placed in URL query data |

### Tool, browser, process, and non-runtime surfaces

| Caller / surface | Destination / owner | Transport creation point | Data disclosed | Current check and evidence | DENY / zero-attempt status | Disposition for Data-Out design |
|---|---|---|---|---|---|---|
| Proxy intermediary and proxy authentication (cross-cutting) | Host selected by `HTTP_PROXY`, `HTTPS_PROXY`, or `ALL_PROXY` (and lowercase forms), or by OS proxy configuration such as Windows Internet Settings, unless bypassed | Default Requests sessions/calls and `urllib` openers use `urllib.request.getproxies()`, which can consult both process environment and platform configuration; launcher tools such as `curl` can also consult proxy settings. Requests can derive `Proxy-Authorization` from userinfo in the effective proxy URL during adapter handling | Whatever payload and credentials the proxied caller sends; proxy URL userinfo can become a transmitted proxy credential after ordinary caller/prepared-request inspection. For HTTPS the proxy observes the connection destination; plain HTTP proxying can expose request content | No common effective-route classification, complete proxy-source disablement, proxy-credential classification, or proxy-specific disclosure evidence | A URL-host allow decision does not deny the proxy intermediary, prove a direct connection, or authorize credentials injected for the proxy | The final boundary must disable/bypass **all** platform and environment proxy discovery where direct routing is required, or derive, classify, authorize, and evidence every effective proxy plus proxy-credential **presence** before send; values must never enter evidence |
| Ambient Requests authentication and netrc storage (cross-cutting) | Host credentials selected from `~/.netrc` or the file named by `NETRC`; the authentication file itself may be UNC/network-mounted or reached through a redirected home | With `Session.trust_env=True` and no explicit auth, `Session.prepare_request()` calls Requests netrc discovery, which can probe/open the authentication file before the fully prepared HTTP request exists | Filesystem path and ambient share authentication during discovery; netrc username/password later become an `Authorization` header even though absent from caller inputs | No backing classification before netrc discovery/read, no final-boundary check of the fully prepared request, and no netrc-specific evidence | Caller-input validation can pass, then preparation can already cause remote-filesystem egress before injecting a credential | Governed boundaries should disable ambient netrc **before preparation**. If intentionally supported, safely classify/authorize the netrc backing before any existence/read operation, then prepare without I/O beyond that approved file and authorize the injected credential before DNS/socket/send; `DENY`/`UNKNOWN` touches no netrc path |
| Ambient Requests CA-bundle storage (cross-cutting) | Certificate bundle selected by `REQUESTS_CA_BUNDLE` or `CURL_CA_BUNDLE`; the file may be UNC/network-mounted or reached through redirected storage | With `trust_env=True`, Requests merges environment settings and `HTTPAdapter.cert_verify` probes/uses the selected CA-bundle path before the HTTPS send | Bundle-path metadata, CA file contents read over the filesystem, and ambient network-share authentication | No backing classification or disclosure decision precedes CA-bundle existence/type validation and read | A request can be denied for its HTTP destination only after the client has already touched an external filesystem path | Disable ambient CA-bundle selection at governed boundaries or safely classify/authorize the effective bundle backing before its first probe/read; `DENY`/`UNKNOWN` must not call `exists`, `is_file`, `stat`, `open`, or read on that path |
| Ambient TLS key logging (cross-cutting) | File selected by `SSLKEYLOGFILE`; it may be UNC/network-mounted or reached through redirected storage | urllib3 can assign the path to `SSLContext.keylog_filename` during TLS-context construction, causing the TLS stack to open/write it as sessions are established | TLS session secrets, path metadata, and ambient network-share authentication | No backing classification, disclosure decision, or evidence precedes TLS-context use of the path | An otherwise allowed HTTPS request can persist decryption material externally before or during transport | Disable TLS key logging before TLS-context creation, or explicitly authorize both the verified backing and session-secret disclosure before any path use; `DENY`/`UNKNOWN` creates no using context and performs no probe/open/write |
| Inherited subprocess environment (cross-cutting) | Every supported child process: ffmpeg, Piper/media players, system/app/browser launchers, Ollama, pip, winget, and Nova/startup children | `subprocess.run` / `subprocess.Popen` without an explicit scrubbed `env` inherits `os.environ`; `ConnectionsStore` injects saved provider keys into that process environment at startup and when keys change | Provider API keys and other unrelated secrets/configuration, plus proxy/netrc/CA environment controls; a networking child may transmit them independently | Process/capability admission generally classifies command/arguments, not the exact environment inherited by the child | Denying network intent while allowing process launch still discloses all inherited environment variables to the child; child networking remains outside Nova's proof | Build a minimal boundary-owned child environment and classify/authorize every retained credential/config category before process creation. `DENY`/`UNKNOWN` must prevent `run`/`Popen`; values never enter evidence. Do not pass unrelated provider keys merely because the parent process holds them |
| `/phase-status` source-identity Git children | Local Git executable and source tree; executable discovery may itself use `PATH` | `audit_api._runtime_build_identity` runs four Git commands (`rev-parse`, unstaged diff, staged diff, and untracked files) for every phase-status response without an explicit `env` | Entire inherited parent environment, including saved provider keys; source-root path and Git arguments | Route is local/status-only, but does not scrub the child environment or classify executable lookup | A readiness/status request can disclose unrelated credentials to four children without an explicit external action | Include all four calls in process policy: classify executable discovery, build one minimal credential-free environment, and admit command/arguments/environment before the first child; denial returns bounded unavailable identity without launching Git |
| PATH-backed executable discovery (cross-cutting) | Every directory in `PATH`, including UNC, mapped-drive, redirected, reparse-backed, mounted, relative, empty/current-directory, or unverifiable entries | STT uses `shutil.which("ffmpeg")`; TTS uses it for Piper/players/PowerShell/ffplay; `SystemControlExecutor` uses it for volume/media/brightness tools; `start_daemon.py` uses it for `nova-start`; shell/bootstrap paths use `command -v`, PowerShell command resolution, or bare command invocation for Python, curl, openers, winget, Ollama, and related tools | Search paths, ambient network-share authentication, discovered executable location, and later arguments/environment if launched | Lookup is generally treated as harmless local discovery and occurs before the process/handoff decision; search-root backing is not classified | A later process denial does not undo SMB/NFS access during executable discovery or shell resolution | Parse/classify every effective search directory without probing it; reject relative/empty/current-directory and `DENY`/`UNKNOWN` backing before `shutil.which`, `command -v`, `Get-Command`, or bare-command resolution. Govern discovery separately from exact executable/process admission |
| Cap 63 OpenClaw network tools | Weather, RSS/news, web search, source pages | Allowlisted tool implementations use `MeteredNetworkProxy`, then `NetworkMediator` | Tool query, location, source URL, provider keys as applicable | Manual envelope preflight and per-run network-call budget; mediator receipts | Envelope/capability limits can deny before mediator; no provider-neutral Data-Out decision | Keep tool allowlist, but require every tool request to carry a disclosure decision into the final mediator. Budget is not custody |
| Cap 63 OpenClaw model fallback | OpenAI, described above | `OpenAIResponsesLane` | Task report and key | Caller-side routing/permission/budget plan | Normal caller has pre-call denial; final method does not enforce it | Move/duplicate the decisive policy at final egress so alternate callers cannot bypass it |
| Webpage launch capability | Default browser and arbitrary planned HTTPS site | `webbrowser.open(url)` | Destination URL; browser subsequently sends its own headers/cookies and may load the site | URL planner plus capability/Governor path; `WEBPAGE_LAUNCH` receipt records handoff result | A denied capability can stop handoff. After handoff Nova cannot prove zero connections or payload behavior | Treat handing a URL to the OS as egress initiation. Gate before `webbrowser.open`; receipt must say “delegated/opened,” never “site reached” |
| Email draft capability | Default mail client via `mailto:` | `webbrowser.open(mailto_uri)` | Recipient, subject, and full draft body are handed to another application | Governed draft/open flow; draft event exists | A denied action can stop handoff. Nova cannot prove whether the mail client synchronizes or sends after handoff | Gate before OS handoff; classify as disclosure to a local external application, distinct from email transmission |
| System/app/file launch | Arbitrary installed application selected by bounded system-control logic | `os.startfile` or `subprocess.run` | File path/arguments; launched application may independently use the network | Governed system-control action and OS process result, not child-network mediation | Nova can deny process launch; after launch it cannot observe/prove the child's network attempts | Do not claim child traffic is mediated. Gate the delegated action and mark child-owned networking outside proof unless a separately controlled proxy exists |
| STT executable and TTS/media player | Configured local binaries / OS player | `subprocess.run` / `subprocess.Popen` | Audio path/data and process arguments; no network is requested by Nova code | Local execution configuration and executor controls | Nova does not inspect whether a user-supplied binary networks | Classify as subprocess-owned behavior. No external-provider PASS may be inferred from process launch alone |
| Ollama availability status | Nominal loopback `localhost:11434/api/tags` **and any effective proxy** | Direct default `urllib.request.urlopen` in `provider_status.py` | Status probe URL and ordinary HTTP metadata; no prompt or provider credential, but an external proxy receives the nominally local request | Fixed loopback origin, but the default urllib opener can inherit environment or OS proxy configuration; no effective-route check or durable network receipt | No provider Data-Out policy; reading provider status can contact an external proxy when loopback is not bypassed | Local-only exception is valid only after proving direct loopback routing. Otherwise classify/authorize the proxy or deny before `urlopen`; never infer local-only from the origin URL alone |
| Startup Ollama probe | Configurable `OLLAMA_URL` plus any proxy selected by `urllib` | `scripts/start_daemon.py` calls `urllib.request.urlopen` before starting the backend and while polling a newly launched Ollama process | Probe URL and ordinary HTTP metadata; no prompt payload, but a nonlocal URL or proxy causes pre-runtime outbound traffic | No loopback/private validation, common mediator, capability check, disclosure decision, or durable receipt | The attempt occurs before Nova's runtime boundary exists; failure is swallowed and may be followed by launching/polling `ollama serve` | Hard pre-start bypass. The launcher must prove a direct local/private destination or deny without calling `urlopen`; it must not inherit an unclassified proxy route |
| Python-launcher Nova readiness, Windows browser discovery, and browser handoff | Loopback-validated `NOVA_HOST`/`NOVA_PORT`, any proxy selected by `urllib`, Edge/Chrome candidates derived from `ProgramFiles`, `ProgramFiles(x86)`, and `LOCALAPPDATA`, and the default browser | `scripts/start_daemon.py` polls `HEALTH_ENDPOINT`; Windows app-window mode then calls `exists()` on each executable candidate before `subprocess.Popen`, otherwise it calls `webbrowser.open(BASE_URL)` | Readiness URL and HTTP metadata; candidate path metadata and ambient share authentication; dashboard URL handed to another application | Host validation does not disable/classify proxies. Browser candidate roots may be UNC, mapped, redirected, reparse-backed, or unknown and are probed before any handoff admission; delegation has no disclosure decision or durable receipt | Blocking `Popen`/`webbrowser.open` does not prevent earlier SMB/network access from `browser.exists()`; after handoff Nova cannot prove navigation behavior | Treat executable discovery and application handoff as separate decisions. Classify every candidate root before the first `exists()`; `DENY`/`UNKNOWN` probes no candidate. Separately prove a direct loopback route and authorize the later `Popen`/default-browser handoff |
| Shell-launcher readiness and dashboard handoff | Configurable `NOVA_HOST`/`NOVA_PORT`, any proxy selected by `curl` or `urllib`, any additional URL/proxy/credential loaded by ambient curl configuration, and the OS default browser | `start_nova.sh` calls `curl` or Python `urllib.request.urlopen` for `/phase-status`, then delegates the dashboard URL through `xdg-open` or `open`; current `curl -fsS` permits automatic loading of `~/.curlrc` | Readiness URL and ordinary HTTP metadata; dashboard URL handed to another application. A nonloopback host, proxy, or ambient curl-configured transfer can make the launcher perform external transport or disclose credentials | No launcher-local loopback validation, curl configuration disablement, common mediator, disclosure decision, or durable receipt before readiness or handoff | Readiness can attempt traffic beyond the intended loopback URL before the backend proves its locality; browser handoff can independently cause navigation | Hard pre-runtime/delegated bypass. Invoke curl with `-q`/`--disable` as its first argument and prove a direct loopback target with proxies bypassed/disabled before readiness; otherwise touch neither HTTP client nor dashboard opener |
| Installer and launcher Ollama CLI | Endpoint selected by `OLLAMA_HOST`, Ollama's model registry, and any other networking owned by the installed `ollama` executable | `nova_bootstrap.ps1` invokes `ollama --version`; `fetch_models.py` invokes `ollama --version`, `ollama list`, and `ollama pull <model>`; `start_daemon.py` can launch `ollama serve` | Version/list probes can disclose request metadata to a remote `OLLAMA_HOST`; pull discloses the model identifier and uses child-owned credentials/configuration; downloaded model bytes return to Ollama's store. `ollama serve` is a local process launch, not proof of local-only child behavior | `-SkipModel` skips `fetch_models.py` but not the bootstrap `ollama --version` probe. No invocation has a Nova disclosure decision/receipt, and Nova does not mediate the child transport | Any Ollama CLI invocation can occur before Nova's runtime boundary; denying only `pull` does not stop version/list probes | Reviewed setup/launcher exception only: classify `OLLAMA_HOST`, require authorization before **any** Ollama subprocess, constrain commands/model identifiers, record delegated outcome truthfully, and never claim child traffic is mediated or zero-attempt after handoff |
| Installer Python dependency acquisition | PyPI/package indexes and any proxy or alternate index used by pip | `installer/windows/nova_bootstrap.ps1` runs the venv interpreter with `-m pip install --upgrade pip`, then `-m pip install -e <install-dir>`; an uncached editable install may resolve and download project dependencies | Package names, versions, platform/Python metadata, index/proxy credentials configured for pip, and downloaded packages | Required by the supported bootstrap path; no Nova runtime boundary, disclosure decision, or durable receipt. Pip owns resolution and transport | The bootstrap invokes pip before Nova starts; without an explicit offline/deny mode, external attempts can occur | Reviewed setup exception only: make online dependency acquisition explicit and separately skippable/offline-capable, authorize before subprocess launch, prefer a locked/verified artifact source, record delegated outcome only, and never claim Nova mediated pip traffic |
| Installer prerequisite acquisition | Microsoft winget sources, Python/Ollama package sources, and child-owned redirects/CDNs | `installer/windows/nova_bootstrap.ps1` can run `winget install Python.Python.3.12` and `winget install Ollama.Ollama` when prerequisites are absent | Package identifiers, platform/device metadata exposed by winget, configured source credentials, and downloaded installers/packages | Supported noninteractive bootstrap accepts required agreements and invokes winget before Nova exists; no disclosure decision or Nova receipt | A fresh install can make external attempts automatically unless a preflight denial/offline mode stops before winget invocation | Reviewed setup exception only: detect missing prerequisites, disclose the required online acquisition, require explicit setup authorization or fail with offline/manual instructions, constrain package IDs/sources, and record only delegated process outcome |
| Windows shortcut creation | Effective Start Menu and optional desktop shell folders, which may be redirected to UNC/network-backed storage independently of the installation root | Standalone `nova_bootstrap.ps1` derives the Start Menu folder from `APPDATA`, calls `Test-Path`/`New-Item`, and saves a WScript `.lnk`; Inno Setup independently writes `{group}` and optional `{autodesktop}` icons | Shortcut target/arguments and description, installation paths, filesystem metadata, and ambient network-share authentication | `-SkipShortcut` covers only the standalone bootstrap branch used by Inno; neither path classifies the effective shell-folder backing before probing/creating/writing | A local `-InstallDir` can still produce SMB/network access and remote shortcut persistence during setup | Classify every effective Start Menu/desktop shell-folder destination before `Test-Path`, directory creation, COM `CreateShortcut`/`Save`, or Inno `[Icons]` processing; `DENY`/`UNKNOWN` skips shortcut creation without touching the destination and reports local/manual instructions |
| Landing-page waitlist form | Formspree placeholder endpoint | Browser-side `fetch` in static landing script when a real form ID is configured | Email address entered on landing page | Placeholder configuration; outside backend mediator/ledger | Browser makes the request directly | Separate website/privacy surface. It must not be represented as governed Nova runtime egress |
| Landing-page GitHub source link | `https://github.com/christopherbdaugherty96/NovaLIS` | A user clicks the `/landing` anchor in `static/landing/index.html`; the browser owns navigation and the resulting request | Destination URL, ordinary browser request metadata, and any GitHub-scoped cookies the browser elects to send | User-initiated, browser-owned website navigation; Nova performs no runtime transport or OS/browser handoff for the click | Browser-owned navigation is outside Nova's runtime ledger and Data-Out evidence | Explicitly **excluded** from Nova's runtime Data-Out zero-attempt contract; no denial proof is required. Nova does not control the browser after the user clicks | Classify separately from Nova-initiated `webbrowser.open` or other delegated egress; retain as a website/privacy disclosure rather than a governed runtime path |
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
    persistence defect is tracked separately as #461. `NetworkMediatorError` also
    interpolates the same raw exception into its propagated message, so #461 must
    prove the secret cannot escape into any downstream persisted evidence path,
    not only the first ledger event, before the Data-Out slices begin.
24. The runtime provider-status probe uses the default urllib opener. Its fixed
    loopback URL can still route through an environment- or OS-configured proxy,
    so status inspection is not a proven local-only exception today.
25. `NOVA_SHOPIFY_SHOP_DOMAIN` is treated as a domain string, but the connector
    does not constrain it to an approved Shopify Admin host before constructing a
    request containing the Admin access token and GraphQL data.
26. Paths configured through `NOVA_RUNTIME_DIR`, `NOVA_CALENDAR_ICS_PATH`,
    `NOVA_PIPER_MODEL_PATH`, the OS/Python temporary directory, caps 22/60, and
    local-project chat/working-context discovery are assumed local without safely
    verifying their effective backing. UNC paths, mapped drives, redirected user
    folders, reparse points/junctions/symlinks, or remote mounts can therefore
    transmit sensitive state, audio, speech, screen frames, calendar/project/file
    data—and trigger OS network authentication—through ordinary filesystem calls.
27. Goal and story state remain installation-relative rather than runtime-rooted:
    `GoalStore` derives `nova_backend/data/goals.json` and constructs a loading
    singleton at import time, while caps 52/53 derive
    `nova_workspace/story_tracker/`. A supported Windows `-InstallDir` can point
    at network-backed storage, and the bootstrap attempts `Start-Transcript`
    there before validating the install root. These stores are already recorded
    as migration obligations, but no current gate proves their installation
    backing local before path resolution, read, or write.
28. Runtime storage is not selected only by `NOVA_RUNTIME_DIR`. With no override,
    writable-source discovery can fall back to `LOCALAPPDATA/Nova`, and canonical
    durability state independently uses `LOCALAPPDATA` or the home-directory
    fallback. Redirected or network-backed defaults can therefore be resolved,
    created, and populated without any configured override.
29. Ambient netrc is itself a filesystem egress surface. A remote `NETRC` or
    redirected-home `.netrc` can be probed/read by Requests during
    `prepare_request()` before the boundary has a fully prepared request to
    inspect, so merely authorizing injected credentials afterward is too late.
30. Windows shortcut destinations are independent of `-InstallDir`. The
    standalone bootstrap uses `APPDATA` for its Start Menu folder, while Inno
    Setup writes `{group}` and optional `{autodesktop}` entries; redirected shell
    folders can cause remote probes, directory creation, and shortcut writes even
    when the installation root is proven local.
31. Windows app-window browser discovery is a filesystem surface before it is a
    process handoff. Candidate Edge/Chrome executables are derived from
    `ProgramFiles`, `ProgramFiles(x86)`, and `LOCALAPPDATA`, then probed with
    `exists()`. Redirected, mapped, reparse-backed, UNC, or unverifiable roots can
    cause network access and ambient authentication even when the later
    `subprocess.Popen` or default-browser handoff is denied.
32. Saved provider keys are injected into `os.environ`, while supported
    `subprocess.run`/`Popen` calls normally inherit the entire environment. This
    discloses unrelated credentials to ffmpeg, Piper/players, system/browser
    launchers, Ollama, pip, winget, and other children before any child-owned
    network behavior occurs; command authorization alone does not govern it.
33. Requests also consumes ambient certificate-bundle paths. A network-backed
    `REQUESTS_CA_BUNDLE` or `CURL_CA_BUNDLE` can be probed/read during adapter TLS
    setup, causing remote-filesystem access and ambient authentication before the
    governed HTTPS send. Proxy and netrc coverage does not cover this file path.
34. urllib3 can honor `SSLKEYLOGFILE` during TLS-context construction. A
    network-backed destination can receive TLS session secrets and ambient share
    authentication even when the HTTPS destination itself is authorized; CA
    bundle classification does not govern this write path.
35. `/phase-status` is not process-free: source identity launches four Git
    children without `env=`, exposing the provider-key-bearing parent environment
    unless those calls are explicitly scrubbed and governed.
36. STT/TTS executable discovery probes `PATH` through `shutil.which` before
    process admission. Network-backed, redirected, relative, empty/current-dir,
    or unverifiable search entries can cause filesystem egress even when the
    eventual ffmpeg, Piper, player, or PowerShell launch is denied.
37. The same PATH-backed discovery class extends beyond STT/TTS. System control
    probes volume/media/brightness tools, `start_daemon.py` probes `nova-start`,
    and supported shell/bootstrap launchers resolve Python, curl, browser openers,
    winget, Ollama, and other bare commands before process admission.
38. Cap 32 and the runtime-settings health projection call `shutil.disk_usage`
    on `Path.home().anchor`. A UNC/network-backed Windows home can therefore be
    contacted—with ambient SMB authentication—during ordinary diagnostics or a
    settings read, independently of runtime-state storage.

## Required common enforcement contract

The implementation lane should introduce one provider-neutral contract, not a
set of provider-specific toggle checks.

Before **any** external transport creation, network-backed filesystem operation,
or delegated egress handoff, the final in-process boundary must receive an
immutable request containing:

- initiating capability/caller and request/session/action identifiers;
- caller-declared provider/purpose plus the normalized destination and destination
  class **derived by the boundary from the actual transport URL or configured
  filesystem path and its verified backing**;
- transport class (`http`, OAuth setup, browser handoff, mail-client handoff,
  subprocess/application handoff, network-backed filesystem, or local/private
  model/storage);
- boundary-verified data categories being disclosed (for example prompt,
  conversation context, location, search query, document text, task report, shop
  data, OAuth material), bound to the actual body, parameters, and headers;
- boundary-verified credential categories and presence, never credential values;
- for subprocess/application handoffs, the exact boundary-built environment and
  credential/configuration categories retained for the child, never values;
- purpose and whether the action is user-initiated, approved, or automatic;
- the applicable owner policy version.

The boundary must reject a caller-declared provider or destination that does not
match the URL- or storage-derived identity. It must also derive the effective
route: a proxy is an additional destination/intermediary, not an invisible
implementation detail. Local/private classification is valid only when the
client is proven not to route through an unclassified proxy. That proof must account for both
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
caller's arguments. Governed HTTP clients should disable ambient netrc auth
before request preparation. If ambient auth is intentionally supported, the
boundary must first classify and authorize the netrc file's effective backing
without probing the untrusted path, then prepare the request without any other
I/O, inspect the resulting method/URL/body/query/header names,
derive the injected credential category, and run policy on that exact prepared
request before DNS, socket creation, or send. Any mutation after authorization
invalidates the decision.

Ambient TLS configuration is also pre-transport input. Governed Requests clients
must disable environment CA-bundle selection or classify and authorize the
effective `REQUESTS_CA_BUNDLE`/`CURL_CA_BUNDLE` backing before any probe or read.
An HTTP destination decision cannot authorize an unverified certificate file on
external storage.

TLS key logging is a separate sensitive-output boundary. Governed clients must
clear `SSLKEYLOGFILE` before TLS-context creation unless policy explicitly
authorizes both the verified file backing and disclosure of TLS session secrets.
An allowed HTTPS destination does not authorize an unverified key-log path.

Subprocess admission must bind the exact child environment as well as the command
and arguments. The boundary must construct a minimal environment, retain only
required non-secret configuration plus explicitly authorized credential
categories, and never persist values. Default inheritance of the parent's
provider-key-bearing `os.environ` is not an acceptable implicit handoff.

Filesystem locality classification must not cross the boundary it is meant to
guard. The preflight may reject lexical UNC/network forms and consult trusted OS
mount/drive metadata, but it must not begin by calling `resolve`, `exists`, `stat`,
directory enumeration, or another operation on the untrusted target. Redirected
folders, mapped drives, junctions/reparse points, symlinks, POSIX mount points, and
backing changes between classification and use must be accounted for. If backing
cannot be established without touching the target, it is `UNKNOWN`, not local;
the authorized operation must also bind/revalidate the effective backing at use.

Remote runtime storage creates a bootstrap dependency: the disclosure boundary
and its denial evidence cannot rely on a ledger rooted in an unverified
`NOVA_RUNTIME_DIR`. Before configured runtime storage is touched, Nova must
establish an independently trusted local evidence sink (or fail closed without
writing to the configured path). A denial receipt written to unauthorized remote
storage would violate the zero-external-attempt claim it is meant to prove.

Installation-relative storage creates an earlier bootstrap dependency. The
supported installer/bootstrap must prove the effective installation backing is
local before `Start-Transcript`, resolving the installation tree, launching Nova,
or importing modules whose constants/singletons resolve and load goal/story
paths. Runtime checks cannot retroactively make execution from a remote install
local. Goal and story storage should later migrate under governed runtime state,
but until then their actual installation-relative paths require the same
fail-closed disclosure/locality decision.

The policy returns `ALLOW`, `DENY`, or `UNKNOWN`. Only `ALLOW` can continue.
`DENY` and `UNKNOWN` must return an explicit local result before DNS resolution,
socket/session/client creation, `requests`/`urllib`, filesystem resolution/probe/
read/write, tempfile creation, `webbrowser.open`, or process launch. Caller-side
checks may improve UX but are not the security boundary. An
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
   adapters, disable ambient netrc before preparation (or pre-authorize its
   verified local/remote backing and injected credential), disable ambient CA
   bundle selection or pre-authorize its verified backing, disable TLS key
   logging before context construction or explicitly authorize its backing and
   session-secret category, classify or disable
   effective proxies, and re-run the complete
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
   provider/destination identities for caps 16/48/55/56/65 and Google OAuth. For
   cap 65, normalize and constrain the configured destination to an approved
   Shopify Admin host before request/header/body preparation; reject userinfo,
   ports, paths, and non-Shopify hosts locally.
6. **Runtime and installation-relative storage, temporary files, and selected local files.** Before resolving,
   creating, checking, reading, or writing runtime/calendar paths, the
   installation-relative goal and story stores, tempfile roots, Piper
   model/output paths, cap 22/60 paths, or local-project explicit,
   working-context, remembered, preset, allowed-root, or discovered paths, derive
   whether the effective filesystem backing is local without first touching the
   target. Treat UNC paths, mapped/network drives, redirected folders,
   junctions/reparse points/symlinks, and remote mounts as external destinations
   requiring an explicit disclosure decision; fail closed on `DENY` or
   unverifiable backing before the first filesystem or child-process operation.
   Establish a trusted local evidence sink before any configured runtime root.
   Classify every effective runtime-root candidate, including `LOCALAPPDATA` and
   home-directory defaults, before resolution, creation, or storage access.
   Require a verified local installation backing before bootstrap logging,
   runtime import, `GoalStore` singleton construction, or caps 52/53 story-store
   access; later migrate both repository-relative stores under governed runtime
   state rather than treating their current location as implicitly local. Treat
   every `PATH` search directory as another untrusted filesystem root and admit
   executable discovery separately from the resulting process launch. Classify
   the home-drive anchor before cap 32 or settings-health `disk_usage`; return
   bounded unknown health on `DENY`/`UNKNOWN` without probing the target.
7. **Delegated egress and setup shell folders.** Gate browser, mail-client, app,
   subprocess, and shortcut handoffs before delegation; classify effective
   redirected Start Menu/desktop destinations before either bootstrap or Inno
   Setup probes/creates/writes them, and skip locally on `DENY`/`UNKNOWN`.
   Construct and authorize a minimal exact environment for every child; scrub
   unrelated provider keys, proxy/netrc/CA controls, and other secrets rather
   than inheriting `os.environ`. This includes every `/phase-status` Git command,
   not only visibly external tools. Use truthful handoff-only receipts. Define which child-owned
   networking is out of proof rather than claiming it is blocked. Treat installer
   every Ollama CLI invocation (`--version`, `list`, `pull`, and launcher
   `serve`), pip dependency acquisition, and winget prerequisite acquisition as
   explicit setup/launcher exceptions with pre-launch decisions, bounded
   commands/package/model identifiers and sources or locked artifacts,
   offline/skip paths, and delegated-outcome evidence.
8. **Local model and startup paths.** Disable/bypass environment proxies for
   traffic classified as local/private (or authorize the proxy as a separate
   destination), and fail closed on a nonlocal, ambiguous, or proxied
   `OLLAMA_URL` before the Python launcher's first probe. Reject or authorize
   origin userinfo, sanitize model URLs in evidence, and disable automatic model
   redirects or reauthorize every hop before the redirected send. Apply the same
   direct loopback proof to `start_nova.sh` before either readiness HTTP or
   dashboard handoff; require `curl -q`/`--disable` as the first curl argument so
   ambient curl configuration cannot add transfers, proxies, or credentials.
   Apply the direct-loopback proof to `provider_status.py` before its Ollama
   availability `urlopen` as well. On Windows app-window startup, classify
   `ProgramFiles`, `ProgramFiles(x86)`, and `LOCALAPPDATA` browser-candidate
   backing before executable discovery; only then may the independently governed
   application handoff be considered.
9. **Static enforcement and generated truth.** Expand network-mechanism scanning
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
   touched after denial. For every process boundary, also capture the exact `env`
   argument and fail if it is omitted or contains an undeclared provider secret.
   Use the real ledger/event taxonomy for decision evidence.
2. **Real caller regressions:** exercise general chat and capabilities 31, 48,
   49, 50, 54, 62, 63, plus caps 16, 55, 56, and 65, proving the final transport
   spy sees zero calls. Cap 48 must prove both its search and nested reasoning
   legs. Cap 49 must cover both selected-headline packets and the direct
   story-page action. Cap 50 must cover the `read_sources` brief path. Cap 65 must
   set `NOVA_SHOPIFY_SHOP_DOMAIN` to a non-Shopify host and prove rejection occurs
   before token/header/body preparation, mediator construction, DNS, or transport.
3. **Setup regressions:** save/test provider credentials and Google OAuth
   operations under denial; prove no direct or mediated request occurs and no
   credential appears in evidence.
4. **Remote-filesystem regressions:** configure `NOVA_RUNTIME_DIR`, then repeat
   with it unset while `LOCALAPPDATA` and the home-directory fallback separately
   resolve to remote/redirected backing. Also configure
   `NOVA_CALENDAR_ICS_PATH`, the effective tempfile root (`TEMP`/platform
   equivalent), `NOVA_PIPER_MODEL_PATH`, cap 22 explicit and preset folders, cap
   60's selected `file_path`, and local-project explicit/working-context/
   remembered targets as Windows UNC/network-drive/redirected/reparse-backed
   paths and POSIX remote mounts/symlinks. Exercise runtime-root selection and
   canonical durability-root selection plus runtime-state persistence,
   calendar connection/read, `/stt/transcribe`, `/api/live-screen/analyze`, Piper
   readiness, cap 18, ordinary `nova_speak`, caps 22/60, and every local-project
   summary/map/architecture inspection path. Prove the classifier itself performs
   no target `resolve`/`stat`/probe and that authorization occurs before
   `TemporaryDirectory`, `NamedTemporaryFile`, `mkdir`, `exists`, `is_file`,
   `iterdir`, `open`, `read_text`, ledger/key/state writes, Piper/ffmpeg/OCR/vision
   invocation, playback, or OS handoff. `DENY`/`UNKNOWN` touches none. Separately
   prove no default/fallback candidate is resolved, probed, created, or written
   before its backing decision. Prove denial evidence uses the trusted local bootstrap sink rather than the
   unverified configured runtime root, and revalidate backing at authorized use.
   Separately run the supported Windows bootstrap with `-InstallDir` on UNC,
   mapped/network-drive, and reparse-backed storage and prove `DENY`/`UNKNOWN`
   occurs before `Start-Transcript`, install-tree resolution, dependency/model
   subprocesses, or Nova launch. With the installation/repository root classified
   as remote, exercise `GoalStore` import/initial load/create/update and caps
   52/53 story view/update paths; prove the decision precedes `Path.resolve`,
   `read_json_state`, `mkdir`, `open`, `write_text`, temporary-file replacement,
   and every goal/story read or write. These regressions lock the current paths;
   migration into governed runtime storage remains a later implementation slice.
   Also set `ProgramFiles`, `ProgramFiles(x86)`, and `LOCALAPPDATA` independently
   to UNC, mapped-drive, redirected, reparse-backed, and unknown locations while
   selecting Windows app-window mode. Prove denial occurs before the first Edge/
   Chrome candidate `exists()` call; executable discovery must not be conflated
   with the later process/browser handoff decision.
   Populate `PATH` with UNC, mapped-drive, redirected, reparse-backed, mounted,
   relative, empty/current-directory, and unknown entries before local entries;
   exercise STT, every Piper/player readiness/render path, system-control volume/
   media/brightness tools, `nova-start`, and supported shell/bootstrap command
   resolution. Prove denial occurs before `shutil.which`, `command -v`,
   `Get-Command`, bare-command resolution, or any candidate probe. Separately
   authorize the discovered executable and its process launch. Set the Windows
   home anchor to UNC/network-backed and unknown locations; exercise cap 32 and
   `/api/settings/runtime` health and prove denial precedes `shutil.disk_usage`
   while returning bounded unknown resource health.
5. **Delegation regressions:** deny webpage, mail draft, and system/app launch;
   prove the OS handoff function is untouched. For Windows dashboard app mode,
   separately prove discovery admission before all candidate probes and handoff
   admission before `subprocess.Popen` or `webbrowser.open`. Seed `os.environ`
   with fake saved-provider keys, then allow each supported ffmpeg, Piper/player,
   system/browser, Ollama, pip, winget, and startup child in turn; prove its exact
   boundary-built environment contains only authorized categories and never the
   unrelated fake keys. Exercise all four `/phase-status` Git commands under the
   same proof and require bounded unavailable identity when denied. On
   `DENY`/`UNKNOWN`, prove no child is created.
6. **Local/private classification tests:** prove loopback/private model traffic is
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
7. **Startup proof:** run Python-launcher decision logic with a nonlocal
   `OLLAMA_URL`, a relative/invalid URL, and a local URL subject to an environment
   proxy. Prove `urllib.request.urlopen` and process launch are untouched on
   denial. For the same Python launcher, prove its Nova `HEALTH_ENDPOINT` polling,
   Edge/Chrome candidate `exists`, `Popen`, and `webbrowser.open` are untouched
   when the route or candidate backing is unverified. Exercise `start_nova.sh` with
   nonloopback/invalid `NOVA_HOST` and with `http_proxy`/`HTTP_PROXY` lacking a
   matching `NO_PROXY`; prove `curl`, Python `urlopen`, `xdg-open`, and `open` are
   all untouched. Supply an ambient curl config containing an external URL,
   proxy, and credentials, and prove the launcher's curl invocation places
   `-q`/`--disable` first so none can be loaded or attempted. Valid direct-loopback
   probes and handoffs remain separately tested local exceptions.
8. **Redirect and identity tests:** run against both the external HTTP mediator
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
9. **Disclosure binding tests:** omit or mislabel a document body, prompt/context
   field, location/query parameter, OAuth form field, bearer/API-key header, and
   an adapter-unknown extra field. Prove each fails before DNS/client use. Then
   prove each supported typed adapter derives the expected categories from the
   actual outgoing structure without persisting values. Configure `~/.netrc` or
   `NETRC` for the destination, including UNC/network-mounted and redirected-home
   files, and prove ambient auth is disabled before preparation or its backing is
   classified/authorized before any existence/read operation. Then prove any
   injected credential appears in the fully prepared request's verified categories;
   prove no post-decision credential injection is possible. Separately point
   `REQUESTS_CA_BUNDLE` and `CURL_CA_BUNDLE` at UNC/network-mounted,
   redirected, reparse-backed, and unknown files; prove ambient selection is
   disabled or backing authorization occurs before any existence/type probe or
   read, and that `DENY`/`UNKNOWN` touches neither bundle nor HTTP transport.
   Point `SSLKEYLOGFILE` at the same remote/unknown backing classes and prove it
   is cleared before TLS-context creation or explicitly authorized for backing
   and session-secret disclosure; denial creates no using context and performs
   no probe/open/write or HTTPS transport.
10. **Installer/launcher setup exception tests:** deny, skip, or select offline
   setup and prove no Ollama subprocess (`--version`, `list`, `pull`, or `serve`),
   pip install, or `winget install` is launched. Cover `-SkipModel`, remote
   `OLLAMA_HOST`, missing-Python, and missing-Ollama branches. On explicit allow,
   validate bounded commands/package/model identifiers and sources or a locked
   artifact source, and record only delegated launch/outcome evidence; do not
   assert that Nova controlled child sockets, redirects, or payloads. Independently
   redirect `APPDATA`, the Start Menu group, and the optional desktop shell folder
   to UNC/network-backed locations while keeping `-InstallDir` local; prove denial
   precedes `Test-Path`, `New-Item`, WScript `CreateShortcut`/`Save`, and Inno icon
   creation, and that the installer continues without touching those destinations.
11. **Evidence-hygiene regression:** use a fake Visual Crossing query credential,
   force an HTTP failure through the real `LedgerWriter`, and prove the credential,
   prepared query values, and raw exception text never reach `ledger.jsonl` or any
   other persisted failure evidence. Also prove the propagated
   `NetworkMediatorError` message is sanitized before any downstream caller can
   persist it. Run both paths red against the #461 pre-fix code.
12. **Static mechanism test:** scan runtime imports/calls for HTTP clients, sockets,
    browser handoffs, process launch, tempfile creation, and configured,
    user-selected, remembered, preset, or discovered filesystem roots/files that
    can resolve to network-backed storage, including default/fallback data roots,
    ambient authentication files, setup shell folders, and executable discovery
    roots. Also scan subprocess calls for omitted/unbounded child environments and
    HTTP clients for ambient CA-bundle/key-log consumption, plus executable
    discovery APIs such as `shutil.which`, shell/PowerShell command resolution,
    and storage diagnostics such as `shutil.disk_usage`. A new surface must either use the
    common boundary or appear as an unresolved inventory failure.
13. **End-to-end session proof:** through the real websocket/session route, turn a
   provider off, invoke each user-visible route, and assert an explicit local
   denial, a durable decision record, and zero transport attempts.
14. **Negative proof:** run each new regression against `bab4a6c` or the relevant
   pre-fix slice and retain the failure evidence in the PR.

## Review gate

Implementation should not start until a closure review confirms that every
supported runtime/setup egress mechanism in the frozen closure scope has an
inventory disposition, every credential- and proxy-derived route has a
disposition, every delegated boundary is identified, and there are no unresolved
P0/P1 omissions or misclassifications on those surfaces. The common contract must
be able to enforce denial at the last in-process point before transport or
delegation.

Reopen the inventory only for a verified P0 or P1 omission or material
misclassification involving a supported, reachable runtime or setup path that
can transmit data, credentials, or sensitive filesystem evidence. A completely
missing path counts even when it contradicts no existing statement.
Hypothetical paths, archived code, developer-only tools, and wording-only
improvements do not reopen it. Track those separately.

The next lane is provider-neutral Data-Out implementation test-first. It is not
authorized by this document alone.
