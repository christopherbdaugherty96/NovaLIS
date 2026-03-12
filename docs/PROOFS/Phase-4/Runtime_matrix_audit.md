Implemented: audit-only review (no file modifications).

I ran a code-level extraction of the NovaLIS runtime surfaces you listed and built the matrices below from current source, then compared those findings against canonical docs.

Table 1 -- Capability Surface Matrix
ID	Name	Enabled	Mediator Trigger(s)	Governor Route	Executor	Real Side Effect?	Risk Level
16	governed_web_search	true	search ..., search for ..., look up ..., research ...; clarification flow (What would you like to search for?)	_execute if req.capability_id == 16	WebSearchExecutor	Yes (network call through NetworkMediator)	low
17	open_website	true	open <name>	elif req.capability_id == 17	WebpageLaunchExecutor	Yes (webbrowser.open)	low
18	speak_text	true	speak that, read that, say it	elif req.capability_id == 18	execute_tts	Yes (local TTS/audio), if text is present	low
19	volume_up_down	true	volume up, volume down, set volume <level>	elif req.capability_id == 19	VolumeExecutor	No concrete OS call in executor (message-only)	low
20	media_play_pause	true	play, pause, resume	elif req.capability_id == 20	MediaExecutor	No concrete OS call in executor (message-only)	low
21	brightness_control	true	brightness up, brightness down, set brightness <level>	elif req.capability_id == 21	BrightnessExecutor	No concrete OS call in executor (message-only)	low
22	open_file_folder	false	`open documents	downloads	desktop	pictures`	elif req.capability_id == 22
32	os_diagnostics	true	system check, system status	elif req.capability_id == 32	OSDiagnosticsExecutor	Partial real effect (shutil.disk_usage("/"), local read)	low
48	multi_source_reporting	false	report <q>, summarize <q>	elif req.capability_id == 48	MultiSourceReportingExecutor	Would perform network reads if enabled; currently blocked by registry enable gate	low
Capability metadata and enabled/risk values come from registry.json, mediator triggers from GovernorMediator, and routes from Governor._execute.
Executor side-effect reality comes from executor implementations themselves (real call vs message-only).

Table 2 -- User-Facing Command Strings
Raw Trigger Phrase	Normalized Form	Capability ID	Source File	Regex?
search ... / search for ... / look up ... / research ...	trailing punctuation stripped before parse	16	governor_mediator.py	Yes (SEARCH_RE)
open <name>	<name> lowercased into target	17	governor_mediator.py	Yes (OPEN_RE)
open documents/downloads/desktop/pictures	folder lowercased	22	governor_mediator.py	Yes (OPEN_FOLDER_RE)
speak that / read that / say it	exact phrase match	18	governor_mediator.py	Yes (re.match)
volume up / volume down	action mapped to up/down	19	governor_mediator.py	Yes (re.match)
set volume <0-999>	level parsed as int	19	governor_mediator.py	Yes (SET_VOLUME_RE)
brightness up / brightness down	action mapped to up/down	21	governor_mediator.py	Yes (re.match)
set brightness <0-999>	level parsed as int	21	governor_mediator.py	Yes (SET_BRIGHTNESS_RE)
play / pause / resume	lowercased action	20	governor_mediator.py	Yes (re.match)
system check / system status	exact phrase class	32	governor_mediator.py	Yes (re.match)
report <q> / summarize <q>	query trimmed	48	governor_mediator.py	Yes (SET_REPORT_RE)
Search-intent without query	clarification prompt: "What would you like to search for?"	16	governor_mediator.py	Yes (re.search)
Source extraction from mediator parser and regex definitions.

Table 3 -- Ledger Event Types
Event Type	Source File	Fail-Closed?	Used By
ACTION_ATTEMPTED	ledger/event_types.py	Yes (writer allowlist)	Governor pre-exec log
ACTION_COMPLETED	ledger/event_types.py	Yes	Governor post-exec log
SEARCH_QUERY	ledger/event_types.py	Yes	Governor cap 16 query audit
WEBPAGE_LAUNCH	ledger/event_types.py	Yes	Webpage launch executor
EXTERNAL_NETWORK_CALL	ledger/event_types.py	Yes	NetworkMediator success path
NETWORK_CALL_FAILED	ledger/event_types.py	Yes	NetworkMediator failure paths
MODEL_UPDATED	ledger/event_types.py	Yes	LLM manager(s)
EXECUTION_TIMEOUT	ledger/event_types.py	Yes	Governor timeout path
EXECUTION_MEMORY_EXCEEDED	ledger/event_types.py	Yes	Governor memory limit path
All event names are centrally allowlisted; unknown event names raise LedgerWriteFailed, i.e., fail-closed write behavior at the writer boundary.
Runtime emit points are in governor, network mediator, webpage executor, and llm manager files.

Table 4 -- Network Constraints
Restriction Type	Enforcement Location	Blocking Behavior
Scheme allowlist (http, https)	NetworkMediator._validate_url	Raises NetworkMediatorError for disallowed schemes
Disallowed localhost hosts (localhost, 127.0.0.1, ::1)	NetworkMediator._validate_url	Raises NetworkMediatorError
Private/loopback/link-local IP literal block	NetworkMediator._validate_url	Raises NetworkMediatorError
DNS rebinding hardening via getaddrinfo resolved-IP check	NetworkMediator._validate_url	Raises NetworkMediatorError when resolved to private/loopback/link-local
Per-capability rate limit (50/min)	NetworkMediator._check_rate_limit	Raises NetworkMediatorError("Rate limit exceeded.")
Capability-bound + enabled check	NetworkMediator.request	Raises NetworkMediatorError if unknown/disabled
Request timeout default (5s)	NetworkMediator.request	Request exception path logs NETWORK_CALL_FAILED then raises
All enforced in governor/network_mediator.py.

Table 5 -- Conversation Normalization Map
User Input Variant	Canonical Interpretation	Handler
wether	weather	InputNormalizer.TYPO_REPLACEMENTS
hedlines	headlines	InputNormalizer.TYPO_REPLACEMENTS
serch / seach	search	InputNormalizer.TYPO_REPLACEMENTS
plz	please	InputNormalizer.TYPO_REPLACEMENTS
u	you	InputNormalizer.TYPO_REPLACEMENTS
search food near me mi ann arbor	search for food near me in Ann Arbor, MI	InputNormalizer.normalize phrase substitution
lowercased initial + no terminal punctuation	sentence-cased + appends .	InputNormalizer.normalize
stay in conversation mode / conversation mode on / enable conversation mode	presence mode enabled	brain_server routing
conversation mode off / disable conversation mode / exit conversation mode	presence mode disabled	brain_server routing
escalation responses yes / no / cancel	escalation decision state machine	brain_server pending escalation branch
Normalization and routing are in response_style_router.py and brain_server.py.

Additional Findings
1) Duplication of strings across files
"I can't do that right now." appears repeatedly in Governor failure paths (same file, multiple branches).

"You're welcome." appears in both response templates and explicit brain_server fast-path handling. 

"Here are the latest headlines." appears in skills/news.py and also skills/web_search.py (legacy/alternate skill surface).

2) Registry / mediator / governor mismatch flags
Registry but not mediator: none (all registry IDs 16/17/18/19/20/21/22/32/48 have mediator parse paths).

Mediator but not governor: none (all mediator-emitted IDs have _execute branches).

Governor but not registry: none for routed IDs 16/17/18/19/20/21/22/32/48 (all present in registry).

3) Executors returning success without real side effect
Likely stub success surfaces: VolumeExecutor, MediaExecutor, BrightnessExecutor, and OpenFolderExecutor return success messages but do not invoke OS control/open APIs in these files. 

OSDiagnosticsExecutor does perform real local disk read, but network status is hardcoded text. 

4) Direct model calls bypassing centralized LLM manager
DeepSeekBridge directly imports and calls ollama.chat(...), bypassing src.llm.llm_manager path. 

5) TTS path specifics (speakable text, URL filtering, invocation-bound triggers)
Speakable text resolution prioritizes action_result.data["speakable_text"], then falls back to user_message/message. 

No explicit URL filtering exists in SpeechFormatter (only punctuation/list pacing transforms). 

Invocation-bound TTS trigger phrases are in governor mediator (speak that|read that|say it), while brain_server injects last response text into cap 18 params when missing. 

Docs Cross-Reference (runtime vs doc claims)
docs/NOVA_CAPABILITY_MASTER.md states IDs 22 and 48 have "No live parser mapping," but runtime mediator currently does map both (open-folder and report/summarize patterns).

The same doc's "wired stub" characterization for 19/20/21 matches current executor implementations (message-only behavior).

Checks Run
[OK] rg --files nova_backend/src

[OK] rg -n "log_event\\(\\s*\\\"[A-Z_]+\\\"" nova_backend/src

[OK] rg -n "I can't do that right now\\.|Here are the latest headlines\\.|You're welcome\\." nova_backend/src

[OK] git status --short

[OK] Multiple targeted source inspections via sed -n / nl -ba on governor, mediator, registry, executors, conversation, ledger, voice, and docs files.

No files were modified (audit-only), so no commit and no PR were created.
