/* Nova Dashboard - User-Friendly Runtime UX */

let ws = null;
let pendingThoughtMessageId = null;
let messageMeta = new Map();
let waitingForAssistant = false;
let activePageState = "chat";
let latestNewsItems = [];
let latestNewsCategories = {};
let latestNewsSummaryState = {
  storySummaries: {},
  categorySummaries: {},
  comparisonSummary: "",
  pendingStories: {},
  pendingCategories: {},
};
let latestBriefWidgetState = {
  headlineCount: 0,
  sourcePagesRead: 0,
  clusterCount: 0,
  placeholderClusterCount: 0,
  omittedClusterCount: 0,
};
let newsExpanded = false;
let selectedNewsCategoryKey = "";
let sttState = "READY";
let mediaRecorder = null;
let silenceTimer = null;
let ackResetTimer = null;
let lastWidgetHydrationAt = 0;
let widgetRefreshTimer = null;
let morningFallbackTimer = null;
let startupHydrationTimers = [];
let wsReconnectTimer = null;
let queuedUserMessages = [];
let manualTurnInFlight = false;
let manualTurnAssistantSeen = false;
let manualTurnStartedAt = 0;
let manualTurnCounter = 0;
let activeManualTurnId = "";
let lastAssistantTurnKey = "";
let suppressWidgetHydrationUntil = 0;
let morningState = {
  weather: "Loading...",
  news: "Loading...",
  system: "Loading...",
  calendar: "Loading...",
};
let memoryPendingActionState = null;
let memoryOverviewState = {
  summary: "No durable memory saved yet. Memory becomes persistent only when you explicitly save it.",
  snapshot: {},
};
let memoryCenterState = {
  items: [],
  selectedId: "",
  selectedItem: null,
  filters: {
    tier: "",
    scope: "",
    thread_name: "",
    thread_key: "",
  },
  summary: "Load the governed memory list to browse durable items and inspect one in detail.",
  lastHydratedAt: 0,
};
let policyCenterState = {
  summary: "No rules yet. Create one when you want Nova to prepare a reviewed helper rule.",
  overview: {},
  items: [],
  selectedId: "",
  selectedItem: null,
  readiness: {},
  selectedReadinessKey: "",
  simulation: null,
  runResult: null,
  lastHydratedAt: 0,
};
let toneState = {
  summary: "Global tone: balanced. No domain overrides.",
  snapshot: {},
};
let notificationState = {
  summary: "No schedules yet. Create one explicitly when you want Nova to remind you.",
  snapshot: {},
};
let patternReviewState = {
  summary: "Pattern review is off. Opt in if you want Nova to look for repeated thread and memory patterns.",
  snapshot: {},
};
let operatorHealthState = {
  summary: "Loading runtime health...",
  snapshot: {},
};
let capabilityDiscoveryState = {
  summary: "Loading live capabilities...",
  snapshot: {},
};
let trustState = {
  mode: "Local-only",
  lastExternalCall: "None",
  dataEgress: "Read-only requests only",
  failureState: "Normal",
  consecutiveFailures: 0,
};
let trustReviewState = {
  summary: "Live review of recent actions and network activity will appear here.",
  receipts: [],
  activity: [],
  blocked: [],
  selectedReceiptKey: "",
  selectedActivityKey: "",
  selectedBlockedKey: "",
  policyReadiness: {},
  selectedPolicyCapabilityKey: "",
  voiceRuntime: {},
  reasoningRuntime: {},
  bridgeRuntime: {},
  connectionRuntime: {},
};
let threadMapState = {
  summary: "No project threads yet. Save work updates to start continuity.",
  activeThread: "",
  threads: [],
  detail: null,
};
let workspaceHomeState = {
  summary: "Home is preparing the work you are most likely to want next.",
  snapshot: {},
  lastHydratedAt: 0,
};
let operationalContextState = {
  summary: "Operational context keeps session continuity visible and resettable.",
  snapshot: {},
  lastHydratedAt: 0,
};
let assistiveNoticeState = {
  summary: "Assistive notices will appear here when Nova can offer bounded help without taking silent action.",
  snapshot: {},
  lastHydratedAt: 0,
};
let projectVisualizerState = {
  summary: "Open the structure map to see the repo as a human-friendly system view.",
  snapshot: {},
  lastHydratedAt: 0,
};
let openClawAgentState = {
  loaded: false,
  loading: false,
  summary: "Loading home-agent foundations...",
  snapshot: {},
  templates: [],
  activeRun: null,
  deliveryInbox: [],
  recentRuns: [],
  lastHydratedAt: 0,
};
const surfacedOpenClawDeliveryIds = new Set();
let settingsRuntimeState = {
  loaded: false,
  loading: false,
  summary: "Loading runtime settings...",
  setupMode: "local",
  setupModeLabel: "Local Mode",
  setupModeBadge: "Offline-first",
  setupModeDescription: "Nova stays local-first, private, and cost-free by default.",
  permissions: {
    external_reasoning_enabled: false,
    remote_bridge_enabled: false,
    home_agent_enabled: false,
    home_agent_scheduler_enabled: false,
    metered_openai_enabled: false,
  },
  permissionCards: [],
  providerPolicy: {
    routing_mode: "local_first",
    routing_mode_label: "Local-first (Recommended)",
    preferred_openai_model: "gpt-5.4-mini",
    preferred_openai_model_label: "GPT-5.4 mini",
    metered_openai_enabled: false,
    summary: "Nova stays local-first by default. Any paid or remote lane should stay optional, visible, and budgeted.",
  },
  providerPolicyCards: [],
  usageBudget: {
    daily_metered_token_budget: 4000,
    warning_ratio: 0.8,
    summary: "Metered usage budget will appear here after the next refresh.",
  },
  usageBudgetCards: [],
  assistivePolicy: {
    assistive_notice_mode: "suggestive",
    assistive_notice_mode_label: "Suggestive",
    summary: "Suggestive. Notice, ask, then assist should remain the governing sequence.",
  },
  assistivePolicyCards: [],
  history: [],
  updatedAt: "",
  lastHydratedAt: 0,
};
let workflowFocusState = {
  goal: "Start with something simple like \"Build me a landing page for my business.\"",
  status: "Ready",
  copy: "Tell Nova the outcome you want, and it will turn that into the next steps.",
  now: "Nova is ready to turn your idea into a workflow.",
  next: "You can start broad. Nova will draft, explain, and pause when a choice matters.",
  lastUserInput: "",
  awaitingResponse: false,
};
let liveHelpState = {
  active: false,
  starting: false,
  processing: false,
  screenStream: null,
  audioStream: null,
  audioRecorder: null,
  cycleTimer: null,
  stopTimer: null,
  videoEl: null,
  canvasEl: null,
  status: "Off",
  copy: "Start live screen help when you want Nova to follow one shared screen and listen for \"Hey Nova\" during that session.",
  screenLabel: "No screen shared yet.",
  voiceLabel: 'Waiting to start. When live help is on, say "Hey Nova" before a request.',
  lastHeard: "Nothing heard yet.",
  lastResult: "No live explanation yet.",
  lastCommandSignature: "",
  lastCommandAt: 0,
  firstAnalysisDone: false,
  pendingInitialCommand: "",
  lastAnalysis: null,
};

const {
  API_BASE,
  WS_BASE,
  HEY_NOVA_WAKE_WORD,
  STORAGE_KEYS,
  PAGE_LABELS,
  PRIMARY_NAV_ITEMS,
  MORNING_FALLBACK_TIMEOUT_MS,
  QUICK_ACTIONS_BY_PAGE,
  COMMAND_SUGGESTIONS,
  HELP_EXAMPLES,
  COMMAND_DISCOVERY_GROUPS,
  LONG_MESSAGE_CHAR_LIMIT,
  LONG_MESSAGE_LINE_LIMIT,
  LONG_MESSAGE_SENTENCE_LIMIT,
  URL_PATTERN,
  WIDGET_HYDRATE_MIN_INTERVAL_MS,
  WIDGET_AUTO_REFRESH_INTERVAL_MS,
} = window.NOVA_DASHBOARD_CONFIG;

function $(id) { return document.getElementById(id); }
function clear(el) { if (el) el.innerHTML = ""; }
function extractDomain(url) { return (url || "").replace(/^https?:\/\//, "").split("/")[0].trim().toLowerCase(); }

function getNewsPreviewLimit() {
  const newsPage = $("page-news");
  const onNewsPage = !!(newsPage && !newsPage.hidden);
  return onNewsPage ? 4 : 3;
}

function formatNewsFreshness(published) {
  const raw = String(published || "").trim();
  if (!raw) return "";

  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return "";

  const diffMs = Date.now() - date.getTime();
  if (diffMs < 0 || diffMs < 60 * 1000) return "Updated just now";
  if (diffMs < 60 * 60 * 1000) return `Updated ${Math.round(diffMs / (60 * 1000))}m ago`;
  if (diffMs < 24 * 60 * 60 * 1000) return `Updated ${Math.round(diffMs / (60 * 60 * 1000))}h ago`;
  return `Updated ${date.toLocaleDateString([], { month: "short", day: "numeric" })}`;
}

function formatThreadTimestamp(value) {
  const raw = String(value || "").trim();
  if (!raw) return "";
  const date = new Date(raw);
  if (Number.isNaN(date.getTime())) return raw;
  return date.toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatOpenClawRunTimestamp(value) {
  return formatThreadTimestamp(value) || "Unknown time";
}

function getOpenClawActiveRun() {
  const activeRun = openClawAgentState.activeRun;
  return activeRun && typeof activeRun === "object" ? activeRun : null;
}

function buildOpenClawActiveRunSummary(activeRun) {
  if (!activeRun) return "No home-agent runs are active right now.";
  const startedLabel = formatOpenClawRunTimestamp(activeRun.started_at);
  const channels = [];
  if (activeRun.delivery_channels && activeRun.delivery_channels.chat) channels.push("chat");
  if (activeRun.delivery_channels && activeRun.delivery_channels.widget) channels.push("page");
  const source = formatOpenClawTriggerLabel(activeRun.triggered_by);
  const statusLabel = String(activeRun.status_label || "Running now").trim() || "Running now";
  return [
    `${String(activeRun.title || "Run").trim() || "Run"} is ${statusLabel.toLowerCase()}.`,
    `${source} ${startedLabel}`,
    channels.length ? `shows in ${channels.join(" + ")}` : "",
  ].filter(Boolean).join(" · ");
}

function getOpenClawEnvelopePreview(template) {
  const preview = (template && typeof template.envelope_preview === "object")
    ? template.envelope_preview
    : {};
  return preview && typeof preview === "object" ? preview : {};
}

function buildOpenClawBudgetLines(preview) {
  const data = (preview && typeof preview === "object") ? preview : {};
  const lines = [];
  if (String(data.scope_summary || "").trim()) lines.push(String(data.scope_summary || "").trim());
  if (String(data.budget_summary || "").trim()) lines.push(String(data.budget_summary || "").trim());
  return lines;
}

function buildOpenClawBudgetUsageLine(usage) {
  const data = (usage && typeof usage === "object") ? usage : {};
  return String(data.summary || "").trim();
}

function formatOpenClawDeliveryModeLabel(mode) {
  const value = String(mode || "").trim().toLowerCase();
  if (value === "hybrid") return "chat + page";
  if (value === "chat") return "chat only";
  return "page only";
}

function formatOpenClawTriggerLabel(triggeredBy) {
  return String(triggeredBy || "").trim() === "scheduler" ? "scheduled" : "started manually";
}

function buildNewsItemSnippet(item) {
  const summary = String(item?.summary || "").trim();
  const title = String(item?.title || "").trim();
  if (summary) {
    const normalizedSummary = summary.replace(/\s+/g, " ").trim().toLowerCase();
    const normalizedTitle = title.replace(/\s+/g, " ").trim().toLowerCase();
    if (normalizedSummary && normalizedSummary !== normalizedTitle) return summary;
  }
  if (!title) return "No synopsis available for this headline.";
  return "Open this story if you want the fuller explanation behind the headline.";
}

function normalizePageKey(page) {
  if (page === "ops") return "home";
  return Object.prototype.hasOwnProperty.call(PAGE_LABELS, page) ? page : "chat";
}

function getInitialPage() {
  const firstRunDone = localStorage.getItem(STORAGE_KEYS.firstRunDone) === "1";
  if (!firstRunDone) return "intro";
  return normalizePageKey(localStorage.getItem(STORAGE_KEYS.activePage) || "chat");
}

function getHeaderConnectionPresentation() {
  const readyState = ws ? ws.readyState : WebSocket.CONNECTING;
  if (readyState === WebSocket.CONNECTING) {
    return { tone: "connecting", label: "Connecting" };
  }
  if (readyState !== WebSocket.OPEN) {
    return { tone: "reconnecting", label: "Reconnecting" };
  }

  const failureState = String(trustState.failureState || "").trim().toLowerCase();
  if (failureState && failureState !== "normal") {
    return { tone: "degraded", label: "Degraded" };
  }

  const connectionSummary = String((trustReviewState.connectionRuntime && trustReviewState.connectionRuntime.summary) || "").trim().toLowerCase();
  const trustMode = String(trustState.mode || "").trim().toLowerCase();
  if (connectionSummary.includes("local") || trustMode.includes("local")) {
    return { tone: "connected", label: "Local-only" };
  }

  return { tone: "connected", label: "Connected" };
}

function renderHeaderStatus(page = activePageState) {
  const normalizedPage = normalizePageKey(page);
  const context = $("header-page-context");
  if (context) {
    context.textContent = `Nova / ${PAGE_LABELS[normalizedPage] || "Chat"}`;
  }

  const chip = $("header-connection-chip");
  const label = $("header-connection-label");
  if (!chip || !label) return;

  const presentation = getHeaderConnectionPresentation();
  chip.classList.remove("status-connected", "status-connecting", "status-reconnecting", "status-degraded");
  chip.classList.add(`status-${presentation.tone}`);
  label.textContent = presentation.label;
}

function injectPrimaryNav() {
  const host = $("primary-nav-strip");
  if (!host || host.children.length > 0) return;

  PRIMARY_NAV_ITEMS.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "primary-nav-btn";
    button.dataset.page = item.page;
    button.textContent = item.label;
    button.setAttribute("aria-pressed", "false");
    host.appendChild(button);
  });
}

function setPTTButtonState(state = "idle") {
  const btn = $("ptt-btn");
  if (!btn) return;

  const safeState = ["idle", "recording", "sending", "error"].includes(state) ? state : "idle";
  btn.classList.remove("mic-idle", "mic-recording", "mic-sending", "mic-error");
  btn.classList.add(`mic-${safeState}`);

  const wakeWordHint = isHeyNovaWakeWordEnabled()
    ? `Press to record and speak normally. Saying "${HEY_NOVA_WAKE_WORD}" is optional here, but still used during live help.`
    : "Press to record a short voice question.";

  const labels = {
    idle: { text: "Talk", title: wakeWordHint },
    recording: { text: "Listening", title: `Nova is listening. Start with "${HEY_NOVA_WAKE_WORD}" and press again to stop.` },
    sending: { text: "Sending", title: "Sending your voice request to Nova" },
    error: { text: "Mic issue", title: "Voice input is unavailable right now" },
  };
  const next = labels[safeState];
  btn.textContent = next.text;
  btn.title = next.title;
  btn.setAttribute("aria-label", next.title);
}

function flashPTTError() {
  setPTTButtonState("error");
  setTimeout(() => {
    if (!mediaRecorder) setPTTButtonState("idle");
  }, 1600);
}

function isHeyNovaWakeWordEnabled() {
  return localStorage.getItem(STORAGE_KEYS.voiceWakeWordEnabled) !== "0";
}

function setHeyNovaWakeWordEnabled(enabled) {
  localStorage.setItem(STORAGE_KEYS.voiceWakeWordEnabled, enabled ? "1" : "0");
  setPTTButtonState("idle");
  renderSettingsPage();
  refreshPrivacyPanel();
}

function normalizeHeyNovaWakeWordTranscript(text) {
  const transcript = String(text || "").trim();
  if (!transcript) {
    return { transcript: "", matched: false, command: "" };
  }
  if (!isHeyNovaWakeWordEnabled()) {
    return { transcript, matched: true, command: transcript };
  }

  const wakeWordPrefix = /^\s*(?:hey|hi|okay|ok)[\s,.\-!?:;]*nova\b[\s,.\-!?:;]*/i;
  if (!wakeWordPrefix.test(transcript)) {
    return { transcript, matched: false, command: "" };
  }

  let command = transcript.replace(wakeWordPrefix, "").trim();
  command = command.replace(/^(can you|could you|please|would you)\s+/i, "").trim();
  command = command.replace(/\s+/g, " ").trim();
  return { transcript, matched: true, command };
}

function normalizeLiveHelpCommand(command) {
  let clean = String(command || "").trim().toLowerCase();
  if (!clean) return "";
  clean = clean.replace(/\b(this screen|this page|this tab|this)\b/g, "this page");
  clean = clean.replace(/\bwhat am i seeing\b/g, "what am i looking at");
  clean = clean.replace(/\bread this\b/g, "read the important part");
  clean = clean.replace(/\bsummarize this\b/g, "summarize this page");
  clean = clean.replace(/\s+/g, " ").trim();
  return clean;
}

function getLiveHelpPromptSuggestions() {
  if (!liveHelpState.active) {
    return [
      { label: "Explain this page", command: "explain this page" },
      { label: "What matters here?", command: "what matters most here" },
      { label: "What should I click?", command: "what should i click next" },
    ];
  }
  const analysis = (liveHelpState.lastAnalysis && typeof liveHelpState.lastAnalysis === "object")
    ? liveHelpState.lastAnalysis
    : {};
  const prompts = Array.isArray(analysis.follow_up_prompts) ? analysis.follow_up_prompts : [];
  const fallback = [
    "explain this page",
    "what matters most here",
    "what should i click next",
    "read the important part",
  ];
  const merged = [...prompts, ...fallback];
  const seen = new Set();
  return merged
    .map((item) => String(item || "").trim())
    .filter((item) => item && !seen.has(item) && seen.add(item))
    .slice(0, 4)
    .map((item) => ({
      label: item.charAt(0).toUpperCase() + item.slice(1),
      command: item,
    }));
}

function getPreferredAudioRecorderOptions() {
  if (!window.MediaRecorder || typeof MediaRecorder.isTypeSupported !== "function") return null;
  const options = {};
  if (MediaRecorder.isTypeSupported("audio/webm;codecs=pcm")) options.mimeType = "audio/webm;codecs=pcm";
  else if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) options.mimeType = "audio/webm;codecs=opus";
  else if (MediaRecorder.isTypeSupported("audio/webm")) options.mimeType = "audio/webm";
  return options.mimeType ? options : null;
}

function renderLiveHelpWidget() {
  const badge = $("live-help-status-badge");
  const copy = $("live-help-copy");
  const trustNote = $("live-help-trust-note");
  const screen = $("live-help-screen-value");
  const voice = $("live-help-voice-value");
  const heard = $("live-help-last-heard-value");
  const result = $("live-help-last-result-value");
  const promptHost = $("live-help-prompt-actions");
  const startBtn = $("btn-live-help-start");
  const explainBtn = $("btn-live-help-explain");
  const stopBtn = $("btn-live-help-stop");

  if (badge) {
    badge.textContent = liveHelpState.status;
    badge.classList.toggle("live-help-active", liveHelpState.active);
  }
  if (copy) copy.textContent = liveHelpState.copy;
  if (trustNote) {
    trustNote.textContent = liveHelpState.active
      ? `Nova is only following ${liveHelpState.screenLabel}. End screen sharing or press Stop live help to stop immediately.`
      : 'Nova only follows the screen you choose to share, only during this session, and stops as soon as you stop it or end screen sharing.';
  }
  if (screen) screen.textContent = liveHelpState.screenLabel;
  if (voice) voice.textContent = liveHelpState.voiceLabel;
  if (heard) heard.textContent = liveHelpState.lastHeard;
  if (result) result.textContent = liveHelpState.lastResult;
  if (promptHost) {
    clear(promptHost);
    getLiveHelpPromptSuggestions().forEach((item) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "live-help-prompt-btn";
      button.textContent = item.label;
      button.disabled = liveHelpState.processing || liveHelpState.starting;
      button.addEventListener("click", () => {
        if (liveHelpState.active) {
          requestLiveHelpAnalysis(item.command, { echoUserMessage: false, updateFocus: true });
          return;
        }
        startLiveHelpSession(item.command);
      });
      promptHost.appendChild(button);
    });
  }
  if (startBtn) {
    startBtn.disabled = liveHelpState.active || liveHelpState.starting;
    startBtn.textContent = liveHelpState.starting ? "Starting..." : "Start live help";
  }
  if (explainBtn) {
    explainBtn.disabled = !liveHelpState.active || liveHelpState.processing;
  }
  if (stopBtn) {
    stopBtn.disabled = !liveHelpState.active && !liveHelpState.starting;
  }
}

function syncWorkflowFocusWithLiveHelp(status, nowText, nextText, copyText = "") {
  workflowFocusState.goal = "Understand the shared screen";
  workflowFocusState.status = status || "Live help";
  workflowFocusState.copy = copyText || 'Nova is staying with the shared screen and keeping the next step easy to follow.';
  workflowFocusState.now = compactWorkflowText(nowText, "Following the shared screen.");
  workflowFocusState.next = compactWorkflowText(
    nextText,
    `Say "${HEY_NOVA_WAKE_WORD}" and ask naturally when you want another explanation.`,
  );
  workflowFocusState.lastUserInput = "understand the shared screen";
  workflowFocusState.awaitingResponse = false;
  renderWorkflowFocusWidget();
}

function tryRouteLiveHelpCommand(text, options = {}) {
  if (!liveHelpState.active) return false;
  const clean = normalizeLiveHelpCommand(text);
  if (!clean || !isLiveHelpExplainCommand(clean)) return false;
  requestLiveHelpAnalysis(clean, options);
  return true;
}

function resetLiveHelpRuntimeState() {
  if (liveHelpState.cycleTimer) {
    clearTimeout(liveHelpState.cycleTimer);
    liveHelpState.cycleTimer = null;
  }
  if (liveHelpState.stopTimer) {
    clearTimeout(liveHelpState.stopTimer);
    liveHelpState.stopTimer = null;
  }
  if (liveHelpState.audioRecorder && liveHelpState.audioRecorder.state === "recording") {
    try {
      liveHelpState.audioRecorder.stop();
    } catch (_) {}
  }
  liveHelpState.audioRecorder = null;
  if (liveHelpState.screenStream) {
    liveHelpState.screenStream.getTracks().forEach((track) => track.stop());
  }
  if (liveHelpState.audioStream) {
    liveHelpState.audioStream.getTracks().forEach((track) => track.stop());
  }
  if (liveHelpState.videoEl) {
    try {
      liveHelpState.videoEl.pause();
    } catch (_) {}
    liveHelpState.videoEl.srcObject = null;
  }
  liveHelpState.active = false;
  liveHelpState.starting = false;
  liveHelpState.processing = false;
  liveHelpState.screenStream = null;
  liveHelpState.audioStream = null;
  liveHelpState.videoEl = null;
  liveHelpState.canvasEl = null;
  liveHelpState.screenLabel = "No screen shared yet.";
  liveHelpState.voiceLabel = `Waiting to start. When live help is on, say "${HEY_NOVA_WAKE_WORD}" before a request.`;
  liveHelpState.firstAnalysisDone = false;
  liveHelpState.pendingInitialCommand = "";
  liveHelpState.lastAnalysis = null;
  liveHelpState.lastResult = "No live explanation yet.";
  liveHelpState.lastHeard = "Nothing heard yet.";
}

function stopLiveHelpSession(reason = "", announce = true) {
  const wasActive = liveHelpState.active || liveHelpState.starting;
  resetLiveHelpRuntimeState();
  liveHelpState.status = "Off";
  liveHelpState.copy = "Live screen help is off. Start a session when you want Nova to follow one shared screen and listen for \"Hey Nova\".";
  syncWorkflowFocusWithLiveHelp(
    "Ready",
    "Live screen help is off.",
    "You can keep going in chat or start live help again when you want Nova to stay with a screen.",
    "Nova returned to normal chat mode.",
  );
  renderLiveHelpWidget();
  if (wasActive && announce) {
    appendChatMessage(
      "assistant",
      reason || "Live screen help stopped. Nova is no longer watching the shared screen or listening for wake-word requests.",
      null,
      "Live screen help",
    );
  }
}

function rememberLiveHelpCommand(command) {
  const normalized = String(command || "").trim().toLowerCase();
  if (!normalized) return false;
  const now = Date.now();
  if (
    normalized === liveHelpState.lastCommandSignature &&
    now - Number(liveHelpState.lastCommandAt || 0) < 5000
  ) {
    return true;
  }
  liveHelpState.lastCommandSignature = normalized;
  liveHelpState.lastCommandAt = now;
  return false;
}

function isLiveHelpExplainCommand(command) {
  const clean = String(command || "").trim().toLowerCase();
  if (!clean) return false;
  return [
    "explain this",
    "explain this page",
    "explain this screen",
    "what am i looking at",
    "what is this page",
    "what matters most here",
    "read the important part",
    "summarize this page",
    "analyze this",
    "analyze this page",
    "analyze this screen",
    "help me do this",
    "what should i click",
    "what should i do next",
  ].some((pattern) => clean.includes(pattern));
}

async function transcribeRecordedAudioBlob(blob, filename = "speech.webm") {
  const form = new FormData();
  form.append("audio", blob, filename);

  const res = await fetch(`${API_BASE}/stt/transcribe`, { method: "POST", body: form });
  let data = {};
  try {
    data = await res.json();
  } catch (_) {
    data = {};
  }
  return {
    ok: res.ok,
    transcript: String(data.text || "").trim(),
    error: String(data.error || "").trim(),
  };
}

async function captureLiveHelpFrame() {
  if (!liveHelpState.active || !liveHelpState.videoEl || !liveHelpState.canvasEl) return null;
  const video = liveHelpState.videoEl;
  const canvas = liveHelpState.canvasEl;
  const track = liveHelpState.screenStream && liveHelpState.screenStream.getVideoTracks
    ? liveHelpState.screenStream.getVideoTracks()[0]
    : null;

  if (!video.videoWidth || !video.videoHeight) {
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  if (!video.videoWidth || !video.videoHeight) return null;

  const maxWidth = 1600;
  const scale = video.videoWidth > maxWidth ? maxWidth / video.videoWidth : 1;
  canvas.width = Math.max(1, Math.round(video.videoWidth * scale));
  canvas.height = Math.max(1, Math.round(video.videoHeight * scale));
  const ctx = canvas.getContext("2d");
  if (!ctx) return null;
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
  if (!blob) return null;
  return {
    blob,
    filename: "live-screen-help.png",
    sourceLabel: String((track && track.label) || "Shared screen").trim(),
  };
}

async function requestLiveHelpAnalysis(command, options = {}) {
  const clean = normalizeLiveHelpCommand(command);
  if (!clean || !liveHelpState.active) return;
  const {
    echoUserMessage = true,
    updateFocus = true,
  } = (options && typeof options === "object") ? options : {};

  if (echoUserMessage) {
    appendChatMessage("user", clean);
  }
  liveHelpState.processing = true;
  liveHelpState.status = "Explaining";
  liveHelpState.copy = "Nova is looking at the shared screen now.";
  liveHelpState.voiceLabel = "Processing your live help request.";
  if (updateFocus) {
    syncWorkflowFocusWithLiveHelp(
      "Live help",
      "Looking at the shared screen now.",
      "Nova will pull out what matters and the best next move.",
    );
  }
  renderLiveHelpWidget();

  try {
    const capture = await captureLiveHelpFrame();
    if (!capture) {
      throw new Error("I couldn't capture the shared screen frame.");
    }

    const form = new FormData();
    form.append("image", capture.blob, capture.filename);
    form.append("query", clean);
    form.append("source_label", capture.sourceLabel);

    const res = await fetch(`${API_BASE}/api/live-screen/analyze`, { method: "POST", body: form });
    let data = {};
    try {
      data = await res.json();
    } catch (_) {
      data = {};
    }

    if (!res.ok) {
      throw new Error(String(data.detail || "I couldn't analyze the shared screen right now."));
    }

    const summary = String(data.summary || "").trim() || "Live screen help is ready.";
    const nextSteps = Array.isArray(data.next_steps) ? data.next_steps : [];
    const ocrText = String(data.ocr_text || "").trim();
    const whatMatters = String(data.what_matters || "").trim();
    const keyActions = Array.isArray(data.key_actions) ? data.key_actions : [];
    const detailLines = [summary];
    if (whatMatters) {
      detailLines.push("", `What matters: ${whatMatters}`);
    }
    if (keyActions.length) {
      detailLines.push("", `Visible actions: ${keyActions.join(", ")}`);
    }
    if (ocrText) {
      detailLines.push("", `Readable text: ${ocrText.length > 240 ? `${ocrText.slice(0, 237).trim()}...` : ocrText}`);
    }
    if (nextSteps.length) {
      detailLines.push("", "Suggested next steps:");
      nextSteps.slice(0, 4).forEach((step) => detailLines.push(`- ${String(step || "").trim()}`));
    }
    appendChatMessage("assistant", detailLines.join("\n"), null, "Live screen help");
    renderScreenAnalysisInsight({ summary, next_steps: nextSteps });
    liveHelpState.lastAnalysis = {
      ...data,
      summary,
      next_steps: nextSteps,
      what_matters: whatMatters,
      key_actions: keyActions,
    };
    liveHelpState.lastResult = summary;
    liveHelpState.firstAnalysisDone = true;
    liveHelpState.status = "Live";
    liveHelpState.copy = `Screen help is active. Say "${HEY_NOVA_WAKE_WORD}" to ask a follow-up question.`;
    liveHelpState.voiceLabel = `Watching the shared screen. Waiting for "${HEY_NOVA_WAKE_WORD}".`;
    if (updateFocus) {
      syncWorkflowFocusWithLiveHelp(
        "Live help",
        summary,
        nextSteps[0] || `Say "${HEY_NOVA_WAKE_WORD}" and ask what to do next.`,
      );
    }
  } catch (error) {
    const message = String((error && error.message) || "I couldn't analyze the shared screen right now.");
    appendChatMessage("assistant", message, null, "Live screen help");
    liveHelpState.status = "Live";
    liveHelpState.copy = message;
    liveHelpState.voiceLabel = `Watching the shared screen. Waiting for "${HEY_NOVA_WAKE_WORD}".`;
    if (updateFocus) {
      syncWorkflowFocusWithLiveHelp(
        "Needs adjustment",
        message,
        "Try asking again, narrowing the question, or using one of the prompt chips.",
        "Live screen help is still active, but the last explanation needs another pass.",
      );
    }
  } finally {
    liveHelpState.processing = false;
    renderLiveHelpWidget();
  }
}

async function handleLiveHelpTranscript(transcript) {
  const clean = String(transcript || "").trim();
  if (!clean) {
    liveHelpState.voiceLabel = `Listening quietly. Say "${HEY_NOVA_WAKE_WORD}" when you need help.`;
    renderLiveHelpWidget();
    return;
  }

  liveHelpState.lastHeard = clean;
  const wakeWordState = normalizeHeyNovaWakeWordTranscript(clean);
  if (!wakeWordState.matched) {
    liveHelpState.voiceLabel = `Shared screen is live. Start with "${HEY_NOVA_WAKE_WORD}" when you want help.`;
    renderLiveHelpWidget();
    return;
  }

  if (!wakeWordState.command) {
    liveHelpState.voiceLabel = `I'm here. Say "${HEY_NOVA_WAKE_WORD}" followed by what you want.`;
    renderLiveHelpWidget();
    return;
  }

  const normalizedCommand = normalizeLiveHelpCommand(wakeWordState.command);
  if (rememberLiveHelpCommand(normalizedCommand)) {
    liveHelpState.voiceLabel = "That sounded like the same request again, so I left the last result in place.";
    renderLiveHelpWidget();
    return;
  }

  if (isLiveHelpExplainCommand(normalizedCommand)) {
    await requestLiveHelpAnalysis(normalizedCommand);
    return;
  }

  injectUserText(normalizedCommand, "voice");
  liveHelpState.voiceLabel = `Sent "${normalizedCommand}" to Nova.`;
  renderLiveHelpWidget();
}

function scheduleLiveHelpCycle(delayMs = 250) {
  if (!liveHelpState.active) return;
  if (liveHelpState.cycleTimer) clearTimeout(liveHelpState.cycleTimer);
  liveHelpState.cycleTimer = setTimeout(() => {
    startLiveHelpAudioCycle();
  }, delayMs);
}

async function startLiveHelpAudioCycle() {
  if (!liveHelpState.active || liveHelpState.processing || liveHelpState.audioRecorder || !liveHelpState.audioStream) {
    return;
  }

  const options = getPreferredAudioRecorderOptions();
  if (!options) {
    stopLiveHelpSession("This browser cannot keep a live help voice session running on this device.");
    return;
  }

  const chunks = [];
  const recorder = new MediaRecorder(liveHelpState.audioStream, options);
  liveHelpState.audioRecorder = recorder;
  liveHelpState.status = "Listening";
  liveHelpState.voiceLabel = `Listening for "${HEY_NOVA_WAKE_WORD}".`;
  renderLiveHelpWidget();

  recorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      chunks.push(event.data);
    }
  };

  recorder.onstop = async () => {
    const mimeType = recorder.mimeType || "audio/webm";
    liveHelpState.audioRecorder = null;
    if (!liveHelpState.active) return;

    if (!chunks.length) {
      liveHelpState.status = "Live";
      liveHelpState.voiceLabel = `Watching the shared screen. Waiting for "${HEY_NOVA_WAKE_WORD}".`;
      renderLiveHelpWidget();
      scheduleLiveHelpCycle(400);
      return;
    }

    liveHelpState.processing = true;
    liveHelpState.status = "Processing";
    liveHelpState.voiceLabel = "Checking what you said.";
    renderLiveHelpWidget();

    try {
      const blob = new Blob(chunks, { type: mimeType });
      const result = await transcribeRecordedAudioBlob(blob, "live-help.webm");
      if (!result.ok) {
        liveHelpState.voiceLabel = "I couldn't process that live help recording.";
      } else if (result.error) {
        liveHelpState.voiceLabel = result.error;
      } else {
        await handleLiveHelpTranscript(result.transcript);
      }
    } catch (_) {
      liveHelpState.voiceLabel = "I couldn't process that live help recording.";
    } finally {
      liveHelpState.processing = false;
      if (liveHelpState.active) {
        liveHelpState.status = "Live";
        if (!String(liveHelpState.voiceLabel || "").trim()) {
          liveHelpState.voiceLabel = `Watching the shared screen. Waiting for "${HEY_NOVA_WAKE_WORD}".`;
        }
        renderLiveHelpWidget();
        scheduleLiveHelpCycle(350);
      }
    }
  };

  recorder.start(250);
  liveHelpState.stopTimer = setTimeout(() => {
    if (recorder.state === "recording") {
      recorder.stop();
    }
  }, 3200);
}

async function startLiveHelpSession(initialCommand = "explain this page") {
  if (liveHelpState.active || liveHelpState.starting) return;
  if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia || !navigator.mediaDevices.getUserMedia) {
    appendChatMessage("assistant", "Live screen help is unavailable in this browser on this device.", null, "Live screen help");
    return;
  }
  if (mediaRecorder && mediaRecorder.state === "recording") {
    stopSTT();
  }

  liveHelpState.starting = true;
  liveHelpState.status = "Starting";
  liveHelpState.copy = "Choose the screen or tab you want Nova to follow, then approve your microphone.";
  liveHelpState.voiceLabel = "Waiting for your permissions.";
  liveHelpState.pendingInitialCommand = normalizeLiveHelpCommand(initialCommand || "explain this page");
  syncWorkflowFocusWithLiveHelp(
    "Starting live help",
    "Preparing a shared-screen help session.",
    "Choose a screen or tab, then Nova will explain it automatically.",
  );
  renderLiveHelpWidget();

  let screenStream = null;
  let audioStream = null;
  try {
    screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false });
    audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const video = document.createElement("video");
    video.setAttribute("playsinline", "true");
    video.muted = true;
    video.srcObject = screenStream;
    await video.play();

    const canvas = document.createElement("canvas");
    const videoTrack = screenStream.getVideoTracks()[0] || null;
    if (videoTrack) {
      videoTrack.onended = () => stopLiveHelpSession("Screen sharing ended, so live help stopped too.");
    }

    liveHelpState.active = true;
    liveHelpState.starting = false;
    liveHelpState.screenStream = screenStream;
    liveHelpState.audioStream = audioStream;
    liveHelpState.videoEl = video;
    liveHelpState.canvasEl = canvas;
    liveHelpState.status = "Live";
    liveHelpState.copy = `Screen help is on. Say "${HEY_NOVA_WAKE_WORD}" to ask about what is on screen.`;
    liveHelpState.screenLabel = String((videoTrack && videoTrack.label) || "Shared screen").trim();
    liveHelpState.voiceLabel = `Watching the shared screen. Waiting for "${HEY_NOVA_WAKE_WORD}".`;
    syncWorkflowFocusWithLiveHelp(
      "Live help",
      `Following ${liveHelpState.screenLabel}.`,
      "Nova will start with a first explanation automatically, then stay ready for follow-up help.",
    );
    renderLiveHelpWidget();
    appendChatMessage(
      "assistant",
      `Live screen help is on for ${liveHelpState.screenLabel}. Nova will only follow this shared screen during this session, and you can stop it any time. I'll start by explaining what is on the page so you don't need to ask twice.`,
      null,
      "Live screen help",
    );
    scheduleLiveHelpCycle(250);
    setTimeout(() => {
      if (liveHelpState.active && !liveHelpState.processing && !liveHelpState.firstAnalysisDone) {
        requestLiveHelpAnalysis(
          liveHelpState.pendingInitialCommand || "explain this page",
          { echoUserMessage: false, updateFocus: true },
        );
      }
    }, 450);
  } catch (_) {
    if (screenStream) screenStream.getTracks().forEach((track) => track.stop());
    if (audioStream) audioStream.getTracks().forEach((track) => track.stop());
    liveHelpState.starting = false;
    liveHelpState.active = false;
    liveHelpState.status = "Off";
    liveHelpState.copy = "Live screen help did not start. Try again and approve both screen sharing and microphone access.";
    liveHelpState.screenLabel = "No screen shared yet.";
    liveHelpState.voiceLabel = "Permission was denied or canceled.";
    syncWorkflowFocusWithLiveHelp(
      "Needs adjustment",
      "Live screen help did not start.",
      "Try again and approve both screen sharing and microphone access.",
      "Nova needs your permissions before it can stay with a screen.",
    );
    renderLiveHelpWidget();
    appendChatMessage(
      "assistant",
      "Live screen help did not start. Make sure you approve both screen sharing and microphone access.",
      null,
      "Live screen help",
    );
  }
}

function startMorningFallbackTimer() {
  if (morningFallbackTimer) clearTimeout(morningFallbackTimer);
  morningFallbackTimer = setTimeout(() => {
    let changed = false;
    if (morningState.weather === "Loading...") {
      morningState.weather = "Weather unavailable right now.";
      changed = true;
    }
    if (morningState.news === "Loading...") {
      morningState.news = "News unavailable right now.";
      changed = true;
    }
    if (morningState.system === "Loading...") {
      morningState.system = "System status unavailable right now.";
      changed = true;
    }
    if (morningState.calendar === "Loading...") {
      morningState.calendar = "Calendar not connected yet.";
      changed = true;
    }
    if (changed) renderMorningPanel();
  }, MORNING_FALLBACK_TIMEOUT_MS);
}

function clearMemoryInlineConfirmation() {
  memoryPendingActionState = null;
  const panel = $("memory-inline-confirmation");
  const text = $("memory-inline-confirmation-text");
  if (panel) panel.hidden = true;
  if (text) text.textContent = "Confirm this governed memory action.";
}

function queueMemoryInlineConfirmation(actionLabel, command, detailText = "") {
  memoryPendingActionState = {
    actionLabel: String(actionLabel || "Confirm action").trim(),
    command: String(command || "").trim(),
    detailText: String(detailText || "").trim(),
  };

  const panel = $("memory-inline-confirmation");
  const text = $("memory-inline-confirmation-text");
  if (text) {
    text.textContent = memoryPendingActionState.detailText
      || `${memoryPendingActionState.actionLabel}. Nova will still route the request through the governed path.`;
  }
  if (panel) panel.hidden = false;
}

function closeHeaderMenus() {
  document.querySelectorAll(".header-menu[open]").forEach((menu) => {
    menu.removeAttribute("open");
  });
}

function createOverviewChip(label, value) {
  const chip = document.createElement("div");
  chip.className = "memory-overview-tier";
  const renderedValue = Number.isFinite(value) ? value : (String(value || "").trim() || "0");
  chip.textContent = `${label}: ${renderedValue}`;
  return chip;
}

function getConnectionRuntimeItem(label) {
  const connections = (trustReviewState.connectionRuntime && typeof trustReviewState.connectionRuntime === "object")
    ? trustReviewState.connectionRuntime
    : {};
  const items = Array.isArray(connections.items) ? connections.items : [];
  const target = String(label || "").trim().toLowerCase();
  return items.find((item) => String(item && item.label || "").trim().toLowerCase() === target) || null;
}

function getSetupReadinessItems() {
  const wsReady = !!(ws && ws.readyState === WebSocket.OPEN);
  const headerConnection = getHeaderConnectionPresentation();
  const currentMode = getSetupModeMeta();
  const profile = getProfileSetupState();
  const localModelItem = getConnectionRuntimeItem("Local model route");
  const localModelValue = String(localModelItem && localModelItem.value || "").trim()
    || (settingsRuntimeState.loaded ? "Awaiting trust refresh" : "Checking");
  const localModelNote = String(localModelItem && localModelItem.note || "").trim()
    || "Nova can still help with reliable local actions while it finishes checking the deeper local model path.";
  const localModelLower = localModelValue.toLowerCase();
  const localModelReady = ["available", "ready"].some((token) => localModelLower.includes(token));

  const voice = (trustReviewState.voiceRuntime && typeof trustReviewState.voiceRuntime === "object")
    ? trustReviewState.voiceRuntime
    : {};
  const voiceLastAttempt = String(voice.last_attempt_status || "").trim();
  const voicePreferredStatus = String(voice.preferred_status || "").trim().toLowerCase();
  const voiceInputStatus = String(voice.stt_status || "").trim().toLowerCase();
  const voiceChecked = !!voiceLastAttempt && voiceLastAttempt.toLowerCase() !== "no voice check yet";
  const voiceReady = voiceChecked && (voicePreferredStatus === "ready" || voiceInputStatus === "ready");
  const voiceStatusLabel = voiceChecked
    ? (voiceReady ? "Checked" : voiceLastAttempt)
    : "Check recommended";
  const voiceCopy = voiceChecked
    ? (
      String(voice.summary || "").trim()
      || "Voice runtime has been inspected on this device."
    )
    : "Run one voice check to confirm audible output on this device. This is recommended, not required.";

  const legacyConnections = (trustReviewState.connectionRuntime && typeof trustReviewState.connectionRuntime === "object")
    ? trustReviewState.connectionRuntime
    : {};
  const connectionStats = getConnectionCardStats();
  const providerCount = connectionStats.loaded
    ? connectionStats.savedCount
    : Number(legacyConnections.configured_provider_count || 0);
  const connectedProviderCount = connectionStats.loaded
    ? connectionStats.connectedCount
    : providerCount;
  const failedProviderCount = connectionStats.loaded
    ? connectionStats.failedCount
    : 0;
  const openaiRuntime = (legacyConnections.openai_runtime && typeof legacyConnections.openai_runtime === "object")
    ? legacyConnections.openai_runtime
    : {};
  const bridgeRuntime = (trustReviewState.bridgeRuntime && typeof trustReviewState.bridgeRuntime === "object")
    ? trustReviewState.bridgeRuntime
    : {};
  const agentRuntime = (legacyConnections.agent_runtime && typeof legacyConnections.agent_runtime === "object")
    ? legacyConnections.agent_runtime
    : ((openClawAgentState.snapshot && typeof openClawAgentState.snapshot === "object") ? openClawAgentState.snapshot : {});
  const calendarProvider = getConnectionCardProvider("calendar");
  const calendarConnected = calendarProvider
    ? calendarProvider.connected === true
    : !!(legacyConnections.calendar_connected || (openClawAgentState.snapshot && openClawAgentState.snapshot.setup && openClawAgentState.snapshot.setup.calendar_connected));
  const calendarNeedsAttention = !!(calendarProvider && calendarProvider.has_key && !calendarProvider.connected);

  return [
    {
      key: "profile_identity",
      group: "Required now",
      title: "Your profile",
      status: profile.hasIdentity ? "Saved" : "Set your name",
      tone: profile.hasIdentity ? "ready" : "attention",
      ready: profile.hasIdentity,
      copy: profile.hasIdentity
        ? `Nova knows who you are${profile.displayName ? ` as ${profile.displayName}` : ""} and can address you naturally from the start.`
        : "Open Settings and add your name first. It makes the rest of setup feel more personal and gives Nova a better default voice and memory context.",
    },
    {
      key: "runtime_connection",
      group: "Required now",
      title: "Runtime connection",
      status: wsReady ? "Connected" : headerConnection.label,
      tone: wsReady ? "ready" : "attention",
      ready: wsReady,
      copy: wsReady
        ? "The dashboard is connected to the local Nova runtime."
        : "Nova is still starting up. If this stays on Connecting for more than a moment, restart the local runtime and refresh the dashboard.",
    },
    {
      key: "local_model_route",
      group: "Required now",
      title: "Local model route",
      status: localModelValue,
      tone: localModelReady ? "ready" : "attention",
      ready: localModelReady,
      copy: localModelNote,
    },
    {
      key: "setup_mode",
      group: "Required now",
      title: "Setup mode",
      status: currentMode.label,
      tone: "ready",
      ready: true,
      copy: currentMode.copy,
    },
    {
      key: "voice_check",
      group: "Recommended",
      title: "Voice check",
      status: voiceStatusLabel,
      tone: voiceReady ? "ready" : "attention",
      ready: voiceReady,
      copy: voiceCopy,
    },
    {
      key: "provider_keys",
      group: "Optional later",
      title: "Connections",
      status: providerCount
        ? (failedProviderCount ? `${connectedProviderCount}/${providerCount} healthy` : `${providerCount} configured`)
        : "Optional",
      tone: failedProviderCount ? "attention" : providerCount ? "optional-ready" : "optional",
      ready: true,
      copy: providerCount
        ? (
          failedProviderCount
            ? `${connectedProviderCount} saved connection${connectedProviderCount === 1 ? "" : "s"} ${connectedProviderCount === 1 ? "is" : "are"} healthy and ${failedProviderCount} need attention in Settings.`
            : "Your saved connections look healthy. You can review, test, or remove them any time from Settings."
        )
        : (
          String(openaiRuntime.summary || "").trim()
          || "Nova can stay fully local. Add a connection later only when you want live data or an optional cloud lane."
        ),
    },
    {
      key: "remote_bridge",
      group: "Optional later",
      title: "Remote bridge",
      status: String(bridgeRuntime.status_label || "Optional").trim() || "Optional",
      tone: bridgeRuntime.enabled ? "optional-ready" : "optional",
      ready: true,
      copy: String(bridgeRuntime.summary || "").trim()
        || "Remote access is optional and stays gated even when you turn it on.",
    },
    {
      key: "home_agent",
      group: "Optional later",
      title: "Home agent",
      status: String(agentRuntime.status_label || "Foundation live").trim() || "Foundation live",
      tone: settingsRuntimeState.permissions && settingsRuntimeState.permissions.home_agent_enabled
        ? "optional-ready"
        : "optional",
      ready: true,
      copy: String(agentRuntime.summary || "").trim()
        || "Home Agent stays inside Nova's governed operator surface and is never required for basic chat use.",
    },
    {
      key: "calendar",
      group: "Optional later",
      title: "Calendar",
      status: calendarConnected
        ? "Connected"
        : calendarNeedsAttention
          ? "Needs attention"
          : "Not connected",
      tone: calendarConnected
        ? "optional-ready"
        : calendarNeedsAttention
          ? "attention"
          : "optional",
      ready: true,
      copy: calendarConnected
        ? (String((calendarProvider && calendarProvider.health_detail) || "").trim() || "Calendar is connected and available to morning brief and evening digest.")
        : calendarNeedsAttention
          ? (String(calendarProvider.health_detail || "").trim() || "Calendar path is saved but needs attention in Settings.")
          : "Calendar is optional. Add your local .ics file path in Connections when you want schedule-aware briefs and daily summaries.",
    },
  ];
}

function buildSetupReadinessSummary(items = []) {
  const rows = Array.isArray(items) ? items : [];
  const required = rows.filter((item) => item.group === "Required now");
  const requiredReadyCount = required.filter((item) => item.ready).length;
  const recommended = rows.filter((item) => item.group === "Recommended");
  const recommendedReadyCount = recommended.filter((item) => item.ready).length;
  const byKey = Object.fromEntries(rows.map((item) => [item.key, item]));
  const profileReady = !!(byKey.profile_identity && byKey.profile_identity.ready);
  const healthyConnections = getConnectionHealthyCount();
  if (profileReady && healthyConnections > 0) {
    return [
      "You are in a good place to begin.",
      `${healthyConnections} connection${healthyConnections === 1 ? "" : "s"} ${healthyConnections === 1 ? "is" : "are"} healthy.`,
      recommended.length
        ? `${recommendedReadyCount} of ${recommended.length} recommended checks are complete.`
        : "",
    ].filter(Boolean).join(" ");
  }
  if (!profileReady) {
    return [
      "Start by telling Nova your name.",
      `${requiredReadyCount} of ${required.length || 0} setup checks are already ready on this device.`,
      "After that, add a connection only if you want live data or optional cloud help.",
    ].filter(Boolean).join(" ");
  }
  if (healthyConnections === 0) {
    return [
      "Your profile is saved.",
      "Add one healthy connection for live data, or stay fully local and keep going.",
      recommended.length
        ? `${recommendedReadyCount} of ${recommended.length} recommended checks are complete.`
        : "",
    ].filter(Boolean).join(" ");
  }
  return [
      `${requiredReadyCount} of ${required.length || 0} required checks are ready.`,
      recommended.length
        ? `${recommendedReadyCount} of ${recommended.length} recommended checks are complete.`
        : "",
    "Optional extras can wait until you actually want them.",
  ].filter(Boolean).join(" ");
}

function getSetupNextStepCopy(items = []) {
  const rows = Array.isArray(items) ? items : [];
  const byKey = Object.fromEntries(rows.map((item) => [item.key, item]));
  const healthyConnections = getConnectionHealthyCount();
  if (!byKey.profile_identity || !byKey.profile_identity.ready) {
    return "Start here: open Settings, add your name in Profile, and save it. That gives Nova the right way to address you and makes the rest of setup feel simpler.";
  }
  if (!byKey.runtime_connection || !byKey.runtime_connection.ready) {
    return "Next step: let Nova finish connecting. If the header keeps showing Connecting, restart the local runtime with the startup script for your platform and refresh the dashboard.";
  }
  if (!byKey.local_model_route || !byKey.local_model_route.ready) {
    return "Next step: open Trust or Settings and review the local model route. Nova can still help locally, but deeper reasoning stays limited until that path is healthy.";
  }
  if (healthyConnections === 0) {
    return "Next step: open Connections in Settings and add one useful source like weather, news, or your calendar. Nova can stay local-only, but one healthy connection makes everyday use much nicer.";
  }
  if (!byKey.voice_check || !byKey.voice_check.ready) {
    return "Next step: run one voice check. It confirms spoken output on this device, but it is optional if you prefer text-only use.";
  }
  return "You are ready. Start with explain this, daily brief, or one real task in chat, then open Home, Workspace, or Trust when you want more continuity and visibility.";
}

function getIntroFirstSuccessItems(items = []) {
  const rows = Array.isArray(items) ? items : [];
  const byKey = Object.fromEntries(rows.map((item) => [item.key, item]));
  const profile = getProfileSetupState();
  const runtimeReady = !!(byKey.runtime_connection && byKey.runtime_connection.ready);
  const localReady = !!(byKey.local_model_route && byKey.local_model_route.ready);
  const voiceReady = !!(byKey.voice_check && byKey.voice_check.ready);
  const healthyConnections = getConnectionHealthyCount();

  if (!profile.hasIdentity) {
    return {
      summary: "Start with one simple human step: tell Nova your name. Once that is saved, the rest of onboarding becomes much easier to follow.",
      items: [
        {
          title: "Set your name",
          badge: "Start here",
          copy: "Open Profile in Settings, save your name, and give Nova the basics it needs to address you naturally.",
          actionLabel: "Open Profile",
          action: () => {
            setActivePage("settings");
            loadProfileData();
          },
        },
        {
          title: "Stay local for now",
          badge: "Optional",
          copy: "You do not need any API keys to begin. Nova can already help locally while you finish setup at your own pace.",
          actionLabel: "Open Home",
          action: () => {
            setActivePage("home");
          },
        },
        {
          title: "See what changes later",
          badge: "Next after profile",
          copy: "After your name is saved, the next useful step is adding one healthy connection for weather, news, calendar, or optional cloud reasoning.",
          actionLabel: "Open Connections",
          action: () => {
            setActivePage("settings");
            loadConnectionsData();
          },
        },
      ],
    };
  }

  if (!runtimeReady) {
    return {
      summary: "Nova is still connecting, so the best first move is getting the local runtime healthy. Once that is ready, the rest of the product becomes much easier to explore.",
      items: [
        {
          title: "Refresh setup",
          badge: "Best next move",
          copy: "Check runtime, connection status, and readiness again without leaving this page.",
          actionLabel: "Refresh",
          action: () => {
            requestSettingsRuntimeRefresh(true);
            safeWSSend({ text: "connection status", silent_widget_refresh: true });
            renderIntroPage();
          },
        },
        {
          title: "Open Settings",
          badge: "If it stays stuck",
          copy: "Settings is the quickest place to review connection health and setup mode in one place.",
          actionLabel: "Open Settings",
          action: () => {
            setActivePage("settings");
            requestSettingsRuntimeRefresh(true);
            safeWSSend({ text: "connection status", silent_widget_refresh: true });
          },
        },
        {
          title: "Read startup help",
          badge: "Local recovery",
          copy: "If the header keeps showing Connecting, use the startup steps below and then refresh the dashboard.",
          actionLabel: "Show help",
          action: () => {
            showFirstRunGuide(true);
          },
        },
      ],
    };
  }

  if (!localReady) {
    return {
      summary: "Nova is connected, but the deeper local model route still needs attention. You can still use lighter help while you review route health and trust status.",
      items: [
        {
          title: "Try Explain This",
          badge: "Works now",
          copy: "This is the easiest way to feel Nova help immediately without waiting for every optional surface to be ready.",
          actionLabel: "Explain this",
          action: () => {
            setActivePage("chat");
            injectUserText("explain this", "text");
          },
        },
        {
          title: "Open Trust",
          badge: "Review route health",
          copy: "Trust shows what is healthy, what is blocked, and what Nova is intentionally keeping bounded right now.",
          actionLabel: "Open Trust",
          action: () => {
            setActivePage("trust");
            safeWSSend({ text: "trust center", silent_widget_refresh: true });
            safeWSSend({ text: "system status", silent_widget_refresh: true });
          },
        },
        {
          title: "Review Settings",
          badge: "Fix readiness",
          copy: "Open Settings to inspect the local model route, provider posture, and current operating mode.",
          actionLabel: "Open Settings",
          action: () => {
            setActivePage("settings");
            requestSettingsRuntimeRefresh(true);
          },
        },
      ],
      };
  }

  if (healthyConnections === 0) {
    return {
      summary: `Nice start${profile.displayName ? `, ${profile.displayName}` : ""}. Your profile is saved. The next high-value step is adding one healthy connection so Nova can help with live weather, news, calendar, or optional cloud reasoning when you want it.`,
      items: [
        {
          title: "Add one connection",
          badge: "Best next move",
          copy: "Open Connections and add the one source you will actually use first. Weather, news, and calendar are usually the easiest wins.",
          actionLabel: "Open Connections",
          action: () => {
            setActivePage("settings");
            loadConnectionsData();
          },
        },
        {
          title: "Try local chat anyway",
          badge: "Works now",
          copy: "You do not have to wait. Nova can already explain, brainstorm, draft, and help locally without any added provider.",
          actionLabel: "Open Chat",
          action: () => {
            setActivePage("chat");
          },
        },
        {
          title: "See your setup path",
          badge: "Why this matters",
          copy: "Settings shows which providers are healthy, optional, or still best left alone for now.",
          actionLabel: "Open Settings",
          action: () => {
            setActivePage("settings");
          },
        },
      ],
    };
  }

  const summary = voiceReady
    ? `You're set up${profile.displayName ? `, ${profile.displayName}` : ""}. Nova is ready for everyday use on this device. Start with one outcome you care about and let Nova turn it into the next steps.`
    : `You're set up${profile.displayName ? `, ${profile.displayName}` : ""}. Voice can wait. Text-only use is completely fine while you get your first win.`;

  // Build connection-aware items based on which providers are healthy
  const providers = Array.isArray(_connectionsData) ? _connectionsData : [];
  const byProvider = Object.fromEntries(providers.map((p) => [p.id, p]));
  const liveItems = [];

  const weatherLive = byProvider.weather && byProvider.weather.connected;
  const calendarLive = byProvider.calendar && byProvider.calendar.connected;
  const newsLive = (byProvider.news && byProvider.news.connected) || (byProvider.brave && byProvider.brave.connected);
  const openaiLive = byProvider.openai && byProvider.openai.connected;

  if (weatherLive && calendarLive) {
    liveItems.push({
      title: "Morning brief",
      badge: "Full brief",
      copy: "Weather, calendar events, and top news in one daily summary — pulled fresh from your connected sources.",
      actionLabel: "Morning brief",
      action: () => {
        setActivePage("chat");
        injectUserText("morning brief", "text");
      },
    });
  }
  if (calendarLive) {
    liveItems.push({
      title: "My schedule today",
      badge: "Calendar live",
      copy: "Check today's calendar without leaving Nova. If you just want the quick version, this is the easiest place to start.",
      actionLabel: "Today's schedule",
      action: () => {
        setActivePage("chat");
        injectUserText("today's schedule", "text");
      },
    });
  }
  if (weatherLive && !calendarLive) {
    liveItems.push({
      title: "Today's weather",
      badge: "Live",
      copy: "Current conditions and forecast from your connected weather provider.",
      actionLabel: "Weather",
      action: () => {
        setActivePage("chat");
        injectUserText("weather", "text");
      },
    });
  }
  if (newsLive) {
    liveItems.push({
      title: "Today's news",
      badge: "Live",
      copy: "Top headlines from your connected news source.",
      actionLabel: "Today's news",
      action: () => {
        setActivePage("chat");
        injectUserText("today's news", "text");
      },
    });
  }
  if (openaiLive) {
    liveItems.push({
      title: "Deep research",
      badge: "Cloud",
      copy: "Ask for a grounded, reasoned answer on any topic with OpenAI cloud assist.",
      actionLabel: "Research",
      action: () => {
        setActivePage("chat");
        injectUserText("research ", "text");
      },
    });
  }

  // Core items always available as fallbacks
  const coreItems = [
    {
      title: "Explain anything",
      badge: "Always available",
      copy: "Paste an error, share a file, or describe something on screen — Nova gives you the cause and next move.",
      actionLabel: "Explain this",
      action: () => {
        setActivePage("chat");
        injectUserText("explain this", "text");
      },
    },
    {
      title: "Continue a project",
      badge: "Continuity",
      copy: "If you already have work in motion, Nova can help you pick it back up instead of starting from scratch.",
      actionLabel: "Show threads",
      action: () => {
        setActivePage("chat");
        injectUserText("show threads", "text");
      },
    },
    {
      title: "Research a topic",
      badge: "Local reasoning",
      copy: "Ask Nova to research something and return a grounded answer with sources and follow-up ideas.",
      actionLabel: "Research",
      action: () => {
        setActivePage("chat");
        injectUserText("research latest technology news", "text");
      },
    },
  ];

  // Connection-aware items first, then core to fill up to 4 slots
  const allItems = [...liveItems, ...coreItems].slice(0, 3);

  return { summary, items: allItems };
}

function createIntroFirstSuccessCard(item = {}) {
  const card = document.createElement("button");
  card.type = "button";
  card.className = "workspace-spotlight-card intro-success-card";

  const title = document.createElement("div");
  title.className = "workspace-spotlight-title";
  title.textContent = String(item.title || "Starter action").trim() || "Starter action";
  card.appendChild(title);

  if (String(item.badge || "").trim()) {
    const badge = document.createElement("span");
    badge.className = "settings-mode-badge";
    badge.textContent = String(item.badge || "").trim();
    card.appendChild(badge);
  }

  const copy = document.createElement("div");
  copy.className = "workspace-spotlight-copy";
  copy.textContent = String(item.copy || "").trim() || "A good next move.";
  card.appendChild(copy);

  const actionLabel = document.createElement("div");
  actionLabel.className = "intro-success-action";
  actionLabel.textContent = String(item.actionLabel || "Open").trim() || "Open";
  card.appendChild(actionLabel);

  if (typeof item.action === "function") {
    card.addEventListener("click", item.action);
  }
  return card;
}

function renderIntroFirstSuccessGrid(host, payload = {}) {
  if (!host) return;
  clear(host);
  const items = Array.isArray(payload.items) ? payload.items : [];
  if (!items.length) {
    host.appendChild(createOverviewChip("Starter flow", "Loading"));
    return;
  }
  items.forEach((item) => host.appendChild(createIntroFirstSuccessCard(item)));
}

function getHomeLaunchActions(items = []) {
  const starterItems = Array.isArray(items) ? items.slice(0, 2) : [];
  const mapped = starterItems.map((item) => ({
    label: String(item.actionLabel || item.title || "Open").trim() || "Open",
    action: typeof item.action === "function" ? item.action : () => {},
    emphasis: true,
  }));

  mapped.push(
    {
      label: "Open Workspace",
      action: () => setActivePage("workspace"),
    },
    {
      label: "Open Settings",
      action: () => setActivePage("settings"),
    },
  );

  return mapped;
}

function renderHomeLaunchWidget() {
  const summary = $("home-launch-summary");
  const actionsHost = $("home-launch-actions");
  const starter = getIntroFirstSuccessItems(getSetupReadinessItems());

  if (summary) {
    summary.textContent = String(starter.summary || "").trim()
      || "Nova is ready for briefings, explain-anything, research, and project continuity.";
  }

  if (!actionsHost) return;
  clear(actionsHost);
  getHomeLaunchActions(starter.items).forEach((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    if (item.emphasis || index === 0) {
      button.className = index === 0 ? "assistant-action-btn home-launch-action-primary" : "assistant-action-btn";
    }
    button.textContent = item.label;
    button.addEventListener("click", item.action);
    actionsHost.appendChild(button);
  });
}

function createSetupReadinessCard(item) {
  const card = document.createElement("div");
  card.className = "workspace-spotlight-card setup-readiness-card";
  if (item && item.tone) {
    card.classList.add(`setup-readiness-${String(item.tone).trim()}`);
  }

  const title = document.createElement("div");
  title.className = "workspace-spotlight-title";
  title.textContent = String(item && item.title || "Setup item").trim() || "Setup item";
  card.appendChild(title);

  const meta = document.createElement("div");
  meta.className = "setup-readiness-meta";

  const group = document.createElement("span");
  group.className = "settings-mode-badge";
  group.textContent = String(item && item.group || "Setup").trim() || "Setup";
  meta.appendChild(group);

  const status = document.createElement("span");
  status.className = "setup-readiness-status";
  if (item && item.tone) {
    status.classList.add(`setup-readiness-status-${String(item.tone).trim()}`);
  }
  status.textContent = String(item && item.status || "Checking").trim() || "Checking";
  meta.appendChild(status);

  card.appendChild(meta);

  const copy = document.createElement("div");
  copy.className = "workspace-spotlight-copy";
  copy.textContent = String(item && item.copy || "").trim() || "Setup detail.";
  card.appendChild(copy);

  return card;
}

function renderSetupReadinessGrid(host, items = []) {
  if (!host) return;
  clear(host);
  const rows = Array.isArray(items) ? items : [];
  if (!rows.length) {
    host.appendChild(createOverviewChip("Setup", "Loading"));
    return;
  }
  rows.forEach((item) => host.appendChild(createSetupReadinessCard(item)));
}

function describeMemoryFilter(filters = {}) {
  const tier = String(filters.tier || "").trim().toLowerCase();
  const scope = String(filters.scope || "").trim().toLowerCase();
  const threadName = String(filters.thread_name || filters.threadName || "").trim();
  const threadKey = String(filters.thread_key || filters.threadKey || "").trim();
  const parts = ["All durable memory"];
  if (tier) parts.push(`tier ${tier}`);
  if (scope) parts.push(`scope ${scope}`);
  if (threadName) parts.push(`thread ${threadName}`);
  else if (threadKey) parts.push(`thread ${threadKey}`);
  return parts.join(" · ");
}

function normalizeMemoryItem(item = {}) {
  return {
    id: String(item.id || "").trim(),
    title: String(item.title || "").trim(),
    body: String(item.body || "").trim(),
    tier: String(item.tier || item.status || "active").trim().toLowerCase(),
    status: String(item.status || item.tier || "active").trim().toLowerCase(),
    scope: String(item.scope || "").trim().toLowerCase(),
    source: String(item.source || "").trim(),
    updated_at: String(item.updated_at || "").trim(),
    created_at: String(item.created_at || "").trim(),
    version: Number(item.version || 0),
    tags: Array.isArray(item.tags) ? item.tags.map((tag) => String(tag || "").trim()).filter(Boolean) : [],
    thread_name: String(item.thread_name || "").trim(),
    thread_key: String(item.thread_key || "").trim(),
    preview: String(item.preview || item.content_display || item.title || item.id || "").trim(),
    content_display: String(item.content_display || item.preview || item.title || item.id || "").trim(),
    deleted: Boolean(item.deleted),
    deleted_at: String(item.deleted_at || "").trim(),
    is_locked: Boolean(item.is_locked),
    unlock_policy: String(item.unlock_policy || "").trim(),
    supersedes: Array.isArray(item.supersedes) ? item.supersedes.map((value) => String(value || "").trim()).filter(Boolean) : [],
    superseded_by: String(item.superseded_by || "").trim(),
  };
}

function upsertMemoryCenterItem(item) {
  const normalized = normalizeMemoryItem(item);
  if (!normalized.id) return;

  const nextItems = Array.isArray(memoryCenterState.items) ? memoryCenterState.items.slice() : [];
  const index = nextItems.findIndex((row) => String(row.id || "").trim() === normalized.id);

  if (normalized.deleted) {
    if (index >= 0) nextItems.splice(index, 1);
    if (memoryCenterState.selectedId === normalized.id) {
      memoryCenterState.selectedId = "";
      memoryCenterState.selectedItem = null;
    }
    memoryCenterState.items = nextItems;
    return;
  }

  if (index >= 0) {
    nextItems[index] = { ...nextItems[index], ...normalized };
  } else {
    nextItems.unshift(normalized);
  }
  nextItems.sort((left, right) => {
    const leftTime = String(left.updated_at || "");
    const rightTime = String(right.updated_at || "");
    return rightTime.localeCompare(leftTime);
  });
  memoryCenterState.items = nextItems.slice(0, 30);
}

function getSelectedMemoryItem() {
  const selectedId = String(memoryCenterState.selectedId || "").trim();
  if (!selectedId) return null;
  const fromList = Array.isArray(memoryCenterState.items)
    ? memoryCenterState.items.find((item) => String(item.id || "").trim() === selectedId)
    : null;
  if (fromList && memoryCenterState.selectedItem) {
    return { ...fromList, ...memoryCenterState.selectedItem };
  }
  return fromList || memoryCenterState.selectedItem || null;
}

function setMemoryCenterStatus(text) {
  const status = $("memory-center-status");
  if (status) status.textContent = text;
}

function sendSilentMemoryCommand(text) {
  const clean = String(text || "").trim();
  if (!clean) return false;
  if (!safeWSSend({ text: clean, silent_widget_refresh: true })) {
    appendChatMessage("assistant", "Still connecting — wait a moment and try again. If this keeps happening, try refreshing the page.", null, "System status");
    return false;
  }
  return true;
}

async function downloadMemoryExport() {
  const pageSummary = $("memory-page-summary");
  const previousSummary = pageSummary ? String(pageSummary.textContent || "").trim() : "";
  if (pageSummary) pageSummary.textContent = "Preparing governed memory export...";

  try {
    const res = await fetch(`${API_BASE}/api/memory/export`);
    if (!res.ok) throw new Error("memory_export_unavailable");
    const payload = await res.json();
    const itemCount = Number((payload && payload.item_count) || 0);
    const exportDate = new Date();
    const yyyy = exportDate.getFullYear();
    const mm = String(exportDate.getMonth() + 1).padStart(2, "0");
    const dd = String(exportDate.getDate()).padStart(2, "0");
    const filename = `nova-memory-export-${yyyy}-${mm}-${dd}.json`;
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    if (pageSummary) {
      pageSummary.textContent = itemCount > 0
        ? `Downloaded ${itemCount} memory item${itemCount === 1 ? "" : "s"}.`
        : "Downloaded an empty memory export snapshot.";
    }
  } catch (_err) {
    if (pageSummary) {
      pageSummary.textContent = "Memory export is unavailable right now. Please try again in a moment.";
    }
  } finally {
    if (pageSummary) {
      const fallbackSummary = previousSummary || "Memory becomes durable only when you explicitly save it.";
      window.setTimeout(() => {
        if (pageSummary.textContent && pageSummary.textContent !== fallbackSummary) {
          pageSummary.textContent = fallbackSummary;
        }
      }, 5000);
    }
  }
}

function hydrateMemoryManagement(force = false) {
  const now = Date.now();
  if (!force && now - Number(memoryCenterState.lastHydratedAt || 0) < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  memoryCenterState.lastHydratedAt = now;
  sendSilentMemoryCommand("memory overview");
  sendSilentMemoryCommand("list memories");
}

function renderMemoryCenterSurface() {
  const filterLabel = $("memory-list-filter-label");
  const listHost = $("memory-list-host");
  const detailEmpty = $("memory-detail-empty");
  const detailHost = $("memory-detail-host");
  const editInput = $("memory-edit-input");
  const detailNote = $("memory-detail-note");
  if (!filterLabel || !listHost || !detailEmpty || !detailHost || !editInput || !detailNote) return;

  const items = Array.isArray(memoryCenterState.items) ? memoryCenterState.items.slice() : [];
  filterLabel.textContent = describeMemoryFilter(memoryCenterState.filters);

  clear(listHost);
  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "memory-overview-empty";
    empty.textContent = "No memory items loaded yet. Use the list controls above to fetch durable items.";
    listHost.appendChild(empty);
  } else {
    items.forEach((item) => {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "memory-list-row";
      if (String(memoryCenterState.selectedId || "").trim() === item.id) {
        row.classList.add("active");
      }
      row.addEventListener("click", () => {
        memoryCenterState.selectedId = item.id;
        clearMemoryInlineConfirmation();
        if (item.body) {
          memoryCenterState.selectedItem = { ...item };
          renderMemoryCenterSurface();
        }
        setMemoryCenterStatus(`Loading ${item.title || item.id}...`);
        sendSilentMemoryCommand(`memory show ${item.id}`);
      });

      const title = document.createElement("div");
      title.className = "memory-list-row-title";
      title.textContent = item.title || item.id;
      row.appendChild(title);

      const preview = document.createElement("div");
      preview.className = "memory-list-row-preview";
      preview.textContent = item.preview || "No preview available.";
      row.appendChild(preview);

      const meta = document.createElement("div");
      meta.className = "memory-list-row-meta";
      const metaParts = [item.status || item.tier || "active"];
      if (item.thread_name) metaParts.push(item.thread_name);
      if (item.updated_at) metaParts.push(formatThreadTimestamp(item.updated_at));
      meta.textContent = metaParts.join(" · ");
      row.appendChild(meta);

      listHost.appendChild(row);
    });
  }

  const selected = getSelectedMemoryItem();
  if (!selected || !selected.id) {
    detailHost.hidden = true;
    clear(detailHost);
    detailEmpty.hidden = false;
    clearMemoryInlineConfirmation();
    if (!editInput.dataset.userEdited) {
      editInput.value = "";
    }
    detailNote.textContent = "Memory remains explicit and user-owned. Inline confirmation appears here before state-changing actions are sent through Nova.";
    return;
  }

  detailEmpty.hidden = true;
  detailHost.hidden = false;
  clear(detailHost);

  const title = document.createElement("div");
  title.className = "memory-detail-title";
  title.textContent = selected.title || selected.id;
  detailHost.appendChild(title);

  const chipRow = document.createElement("div");
  chipRow.className = "memory-detail-chip-row";
  [
    selected.status || selected.tier || "active",
    selected.scope || "project",
    selected.source || "explicit_user_save",
  ].filter(Boolean).forEach((label) => {
    const chip = document.createElement("span");
    chip.className = "memory-detail-chip";
    chip.textContent = label;
    chipRow.appendChild(chip);
  });
  detailHost.appendChild(chipRow);

  const meta = document.createElement("div");
  meta.className = "memory-detail-meta";
  const metaParts = [];
  if (selected.thread_name) metaParts.push(`Thread ${selected.thread_name}`);
  if (selected.version > 0) metaParts.push(`Version ${selected.version}`);
  if (selected.updated_at) metaParts.push(`Updated ${formatThreadTimestamp(selected.updated_at)}`);
  if (selected.deleted_at) metaParts.push(`Deleted ${formatThreadTimestamp(selected.deleted_at)}`);
  meta.textContent = metaParts.join(" · ");
  if (meta.textContent) detailHost.appendChild(meta);

  if (selected.tags.length) {
    const tags = document.createElement("div");
    tags.className = "memory-detail-tags";
    selected.tags.forEach((tag) => {
      const chip = document.createElement("span");
      chip.className = "memory-detail-tag";
      chip.textContent = tag;
      tags.appendChild(chip);
    });
    detailHost.appendChild(tags);
  }

  const body = document.createElement("pre");
  body.className = "memory-detail-body";
  body.textContent = selected.body || selected.preview || "No body stored for this memory item.";
  detailHost.appendChild(body);

  const relationship = [];
  if (selected.supersedes.length) relationship.push(`Supersedes ${selected.supersedes.join(", ")}`);
  if (selected.superseded_by) relationship.push(`Superseded by ${selected.superseded_by}`);
  if (selected.unlock_policy) relationship.push(`Unlock policy ${selected.unlock_policy}`);
  if (relationship.length) {
    const relationText = document.createElement("div");
    relationText.className = "memory-detail-meta";
    relationText.textContent = relationship.join(" · ");
    detailHost.appendChild(relationText);
  }

  if (!editInput.dataset.userEdited || editInput.dataset.sourceId !== selected.id) {
    editInput.value = selected.body || "";
    editInput.dataset.sourceId = selected.id;
    editInput.dataset.userEdited = "";
  }
  const confirmationPanel = $("memory-inline-confirmation");
  const confirmationText = $("memory-inline-confirmation-text");
  if (confirmationPanel) {
    confirmationPanel.hidden = !(memoryPendingActionState && memoryPendingActionState.command);
  }
  if (confirmationText && memoryPendingActionState && memoryPendingActionState.command) {
    confirmationText.textContent = memoryPendingActionState.detailText
      || `${memoryPendingActionState.actionLabel}. Nova will still route the request through the governed path.`;
  }
  detailNote.textContent = selected.deleted
    ? "This memory item has been deleted. Refresh the list to inspect the current durable set."
    : "Edit, lock, unlock, defer, and delete stay governed. This page now adds an inline check before state-changing requests are sent.";
}

/* ── Goal Cards (display-only prototype) ───────────────────────────── */

/**
 * Goal card data — fetched from /api/goals.
 * No execution, no scheduler, no backend authority.
 * Planning is not authority. Goal state is not permission.
 *
 * _DEMO_GOAL_CARDS_FALLBACK is kept as fallback data only — used
 * when the API is unreachable during local development.
 * Once the API responds, fetched goal data replaces it.
 */
var _goalCardsData = null;   // null = not yet fetched
var _goalCardsFetchState = "idle"; // idle | loading | loaded | error

function _fetchGoalCards() {
  if (_goalCardsFetchState === "loading") return;
  _goalCardsFetchState = "loading";
  _renderGoalLoadingState();

  fetch("/api/goals")
    .then(function (resp) {
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      return resp.json();
    })
    .then(function (data) {
      _goalCardsData = Array.isArray(data.goals) ? data.goals : [];
      _goalCardsFetchState = "loaded";
      renderGoalCardsPage();
      renderGoalStatusLegend();
    })
    .catch(function (err) {
      console.warn("Goal Cards API unavailable, using demo data:", err);
      _goalCardsData = _DEMO_GOAL_CARDS_FALLBACK;
      _goalCardsFetchState = "error";
      renderGoalCardsPage();
      renderGoalStatusLegend();
    });
}

function _renderGoalLoadingState() {
  var container = $("goal-cards-container");
  var emptyState = $("goal-cards-empty");
  if (!container) return;
  container.innerHTML =
    '<div class="goal-loading-state" aria-live="polite">'
    + '<p class="goal-loading-text">Loading goals…</p>'
    + '</div>';
  if (emptyState) emptyState.hidden = true;
}

function _getGoalCards() {
  if (_goalCardsData !== null) return _goalCardsData;
  return _DEMO_GOAL_CARDS_FALLBACK;
}

const _DEMO_GOAL_CARDS_FALLBACK = [
  {
    goal_id: "goal_auralis_launch_001",
    title: "Prepare Auralis Shopify launch",
    status: "planning",
    created_at: "2026-05-22T12:00:00Z",
    updated_at: "2026-05-22T14:30:00Z",
    steps: [
      {
        step_id: "step_001",
        title: "Run read-only Shopify intelligence report",
        status: "completed",
        required_capability: 65,
        approval_required: false,
      },
      {
        step_id: "step_002",
        title: "Summarize products, inventory, and order signals",
        status: "completed",
        required_capability: null,
        approval_required: false,
      },
      {
        step_id: "step_003",
        title: "Draft a launch checklist",
        status: "running",
        required_capability: null,
        approval_required: false,
      },
      {
        step_id: "step_004",
        title: "Draft outreach email for user review",
        status: "planned",
        required_capability: 64,
        approval_required: true,
      },
      {
        step_id: "step_005",
        title: "Wait for user approval before any external effect",
        status: "planned",
        required_capability: null,
        approval_required: true,
      },
    ],
    permission_envelope: {
      allowed_capabilities: [
        { id: 16, name: "Web search" },
        { id: 22, name: "Open folder" },
        { id: 64, name: "Email draft" },
        { id: 65, name: "Shopify read" },
      ],
      blocked_actions: [
        "Shopify writes",
        "Printify",
        "Purchases",
        "Publishing",
        "Browser control",
        "Customer messages",
      ],
      requires_confirmation: [22, 64],
    },
    ledger_refs: [
      { type: "ACTION_COMPLETED", capability_id: 65,
        summary: "Shopify intelligence report (read-only)" },
      { type: "ACTION_COMPLETED", capability_id: null,
        summary: "Product/inventory summary generated" },
    ],
  },
  {
    goal_id: "goal_repo_cleanup_002",
    title: "Clean up Nova repo continuity",
    status: "completed",
    created_at: "2026-05-21T09:00:00Z",
    updated_at: "2026-05-22T00:23:00Z",
    steps: [
      {
        step_id: "step_010",
        title: "Review current priority and active TODO docs",
        status: "completed",
        required_capability: null,
        approval_required: false,
      },
      {
        step_id: "step_011",
        title: "Identify stale or conflicting docs",
        status: "completed",
        required_capability: null,
        approval_required: false,
      },
      {
        step_id: "step_012",
        title: "Draft cleanup plan",
        status: "completed",
        required_capability: null,
        approval_required: false,
      },
      {
        step_id: "step_013",
        title: "Apply changes after approval",
        status: "completed",
        required_capability: 22,
        approval_required: true,
      },
    ],
    permission_envelope: {
      allowed_capabilities: [
        { id: 16, name: "Web search" },
        { id: 22, name: "Open folder" },
      ],
      blocked_actions: [
        "Delete branches",
        "Merge PRs",
        "Modify runtime",
        "Change locks",
      ],
      requires_confirmation: [22],
    },
    ledger_refs: [
      { type: "ACTION_COMPLETED", capability_id: 22,
        summary: "Opened docs folder for review" },
    ],
  },
  {
    goal_id: "goal_blocked_example_003",
    title: "Set up Printify integration",
    status: "blocked",
    created_at: "2026-05-22T15:00:00Z",
    updated_at: "2026-05-22T15:00:00Z",
    steps: [
      {
        step_id: "step_020",
        title: "Connect Printify API",
        status: "blocked",
        required_capability: null,
        approval_required: true,
      },
    ],
    permission_envelope: {
      allowed_capabilities: [],
      blocked_actions: [
        "Printify API",
        "External writes",
        "Product creation",
        "Order management",
      ],
      requires_confirmation: [],
    },
    ledger_refs: [],
  },
];

const STEP_INDICATORS = {
  planned: "○",
  proposed: "?",
  waiting_for_approval: "!",
  approved: "✓",
  running: "▶",
  completed: "✓",
  failed: "✗",
  blocked: "‒",
  skipped: "–",
  canceled: "–",
};

/* ── Goal Card local display-state ─────────────────────────────────── */
/* Pure frontend state: expand/collapse, selection, filtering, sorting.
 * No execution authority. No backend persistence.
 * localStorage used only for UI preferences (expanded cards, filters). */

var _goalDisplayState = {
  expandedCards: {},   // goal_id → true/false
  selectedCard: null,  // goal_id or null
  activeFilter: null,  // status string or null (show all)
  sortMode: "updated", // "updated" or "status"
};

function _loadGoalDisplayState() {
  try {
    var raw = localStorage.getItem("nova_goal_display_state");
    if (raw) {
      var parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object") {
        _goalDisplayState.expandedCards = parsed.expandedCards || {};
        _goalDisplayState.activeFilter = parsed.activeFilter || null;
        _goalDisplayState.sortMode = parsed.sortMode || "updated";
      }
    }
  } catch (_e) { /* ignore corrupt localStorage */ }
}

function _saveGoalDisplayState() {
  try {
    localStorage.setItem("nova_goal_display_state", JSON.stringify({
      expandedCards: _goalDisplayState.expandedCards,
      activeFilter: _goalDisplayState.activeFilter,
      sortMode: _goalDisplayState.sortMode,
    }));
  } catch (_e) { /* quota or private browsing */ }
}

function _toggleGoalExpanded(goalId) {
  _goalDisplayState.expandedCards[goalId] =
    !_goalDisplayState.expandedCards[goalId];
  _saveGoalDisplayState();
  renderGoalCardsPage();
}

function _selectGoalCard(goalId) {
  _goalDisplayState.selectedCard =
    _goalDisplayState.selectedCard === goalId ? null : goalId;
  renderGoalCardsPage();
}

function _setGoalFilter(status) {
  _goalDisplayState.activeFilter =
    _goalDisplayState.activeFilter === status ? null : status;
  _saveGoalDisplayState();
  renderGoalCardsPage();
}

function _setGoalSort(mode) {
  _goalDisplayState.sortMode = mode;
  _saveGoalDisplayState();
  renderGoalCardsPage();
}

function _getGoalProgress(goal) {
  if (!Array.isArray(goal.steps) || goal.steps.length === 0) {
    return { completed: 0, total: 0, pct: 0 };
  }
  var completed = goal.steps.filter(function (s) {
    return s.status === "completed";
  }).length;
  return {
    completed: completed,
    total: goal.steps.length,
    pct: Math.round((completed / goal.steps.length) * 100),
  };
}

var GOAL_STATUS_ORDER = {
  running: 0, waiting_for_approval: 1, ready: 2, planning: 3,
  blocked: 4, paused: 5, draft: 6, completed: 7, canceled: 8, failed: 9,
};

function _sortGoals(goals, mode) {
  var sorted = goals.slice();
  if (mode === "status") {
    sorted.sort(function (a, b) {
      var oa = GOAL_STATUS_ORDER[a.status] != null
        ? GOAL_STATUS_ORDER[a.status] : 99;
      var ob = GOAL_STATUS_ORDER[b.status] != null
        ? GOAL_STATUS_ORDER[b.status] : 99;
      if (oa !== ob) return oa - ob;
      return (b.updated_at || "").localeCompare(a.updated_at || "");
    });
  } else {
    sorted.sort(function (a, b) {
      return (b.updated_at || "").localeCompare(a.updated_at || "");
    });
  }
  return sorted;
}

/* ── End display-state helpers ────────────────────────────────────── */

function createGoalCardElement(goal) {
  var isExpanded = !!_goalDisplayState.expandedCards[goal.goal_id];
  var isSelected = _goalDisplayState.selectedCard === goal.goal_id;
  var progress = _getGoalProgress(goal);

  const card = document.createElement("article");
  card.className = "goal-card";
  if (isExpanded) card.classList.add("goal-card--expanded");
  if (isSelected) card.classList.add("goal-card--selected");
  card.dataset.goalId = goal.goal_id;
  card.dataset.goalStatus = goal.status || "draft";

  // Header: title + progress + status badge (always visible)
  const header = document.createElement("div");
  header.className = "goal-card-header";
  header.style.cursor = "pointer";
  header.setAttribute("role", "button");
  header.setAttribute("aria-expanded", String(isExpanded));
  header.setAttribute("tabindex", "0");
  header.title = isExpanded ? "Collapse details" : "Expand details";

  // Expand chevron
  const chevron = document.createElement("span");
  chevron.className = "goal-card-chevron";
  chevron.textContent = isExpanded ? "▾" : "▸";
  chevron.setAttribute("aria-hidden", "true");
  header.appendChild(chevron);

  const title = document.createElement("h4");
  title.className = "goal-card-title";
  title.textContent = String(goal.title || "Untitled goal").trim();
  header.appendChild(title);

  const badge = document.createElement("span");
  badge.className = "goal-card-status";
  badge.dataset.status = goal.status || "draft";
  badge.textContent = (goal.status || "draft").replace(/_/g, " ");
  header.appendChild(badge);

  // Click header to expand/collapse
  header.addEventListener("click", function (e) {
    e.stopPropagation();
    _toggleGoalExpanded(goal.goal_id);
  });
  header.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      _toggleGoalExpanded(goal.goal_id);
    }
  });

  card.appendChild(header);

  // Progress bar (always visible, below header)
  if (progress.total > 0) {
    const progressWrap = document.createElement("div");
    progressWrap.className = "goal-card-progress";

    const progressBar = document.createElement("div");
    progressBar.className = "goal-card-progress-bar";

    const progressFill = document.createElement("div");
    progressFill.className = "goal-card-progress-fill";
    progressFill.style.width = progress.pct + "%";
    progressFill.dataset.goalStatus = goal.status || "draft";
    progressBar.appendChild(progressFill);
    progressWrap.appendChild(progressBar);

    const progressLabel = document.createElement("span");
    progressLabel.className = "goal-card-progress-label";
    progressLabel.textContent = progress.completed + "/" + progress.total
      + " steps";
    progressWrap.appendChild(progressLabel);

    card.appendChild(progressWrap);
  }

  // Collapsible body
  const body = document.createElement("div");
  body.className = "goal-card-body";
  if (!isExpanded) body.hidden = true;

  // Steps
  if (Array.isArray(goal.steps) && goal.steps.length > 0) {
    const stepsLabel = document.createElement("p");
    stepsLabel.className = "goal-card-section-label";
    stepsLabel.textContent = "Steps";
    body.appendChild(stepsLabel);

    const stepsList = document.createElement("div");
    stepsList.className = "goal-card-steps";

    goal.steps.forEach(function (step) {
      const stepEl = document.createElement("div");
      stepEl.className = "goal-card-step";
      stepEl.dataset.stepStatus = step.status || "planned";

      const indicator = document.createElement("span");
      indicator.className = "goal-card-step-indicator";
      indicator.textContent = STEP_INDICATORS[step.status] || "·";
      stepEl.appendChild(indicator);

      const stepTitle = document.createElement("span");
      stepTitle.className = "goal-card-step-title";
      stepTitle.textContent = String(step.title || "").trim();
      if (step.approval_required && step.status !== "completed") {
        stepTitle.textContent += " (approval required)";
      }
      stepEl.appendChild(stepTitle);

      stepsList.appendChild(stepEl);
    });

    body.appendChild(stepsList);
  }

  // Permission envelope
  var env = goal.permission_envelope;
  if (env) {
    const envLabel = document.createElement("p");
    envLabel.className = "goal-card-section-label";
    envLabel.textContent = "What Nova can / can’t do";
    body.appendChild(envLabel);

    const envGrid = document.createElement("div");
    envGrid.className = "goal-card-envelope";

    // Allowed column
    if (Array.isArray(env.allowed_capabilities)
        && env.allowed_capabilities.length > 0) {
      const allowedCol = document.createElement("div");
      allowedCol.className = "goal-card-envelope-col";

      const allowedLabel = document.createElement("p");
      allowedLabel.className = "goal-card-section-label";
      allowedLabel.textContent = "Allowed";
      allowedCol.appendChild(allowedLabel);

      const allowedTags = document.createElement("div");
      allowedTags.className = "goal-card-tag-list";
      env.allowed_capabilities.forEach(function (cap) {
        const tag = document.createElement("span");
        tag.className = "goal-card-tag allowed";
        tag.textContent = cap.name || ("Cap " + cap.id);
        allowedTags.appendChild(tag);
      });
      allowedCol.appendChild(allowedTags);
      envGrid.appendChild(allowedCol);
    }

    // Blocked column
    if (Array.isArray(env.blocked_actions)
        && env.blocked_actions.length > 0) {
      const blockedCol = document.createElement("div");
      blockedCol.className = "goal-card-envelope-col";

      const blockedLabel = document.createElement("p");
      blockedLabel.className = "goal-card-section-label";
      blockedLabel.textContent = "Blocked";
      blockedCol.appendChild(blockedLabel);

      const blockedTags = document.createElement("div");
      blockedTags.className = "goal-card-tag-list";
      env.blocked_actions.forEach(function (action) {
        const tag = document.createElement("span");
        tag.className = "goal-card-tag blocked";
        tag.textContent = String(action);
        blockedTags.appendChild(tag);
      });
      blockedCol.appendChild(blockedTags);
      envGrid.appendChild(blockedCol);
    }

    body.appendChild(envGrid);
  }

  // Receipt references
  if (Array.isArray(goal.ledger_refs) && goal.ledger_refs.length > 0) {
    const receiptsLabel = document.createElement("p");
    receiptsLabel.className = "goal-card-section-label";
    receiptsLabel.textContent = "Receipts";
    body.appendChild(receiptsLabel);

    const receiptsList = document.createElement("div");
    receiptsList.className = "goal-card-receipts";

    goal.ledger_refs.forEach(function (ref) {
      const receiptEl = document.createElement("div");
      receiptEl.className = "goal-card-receipt";

      const dot = document.createElement("span");
      dot.className = "goal-card-receipt-dot";
      dot.classList.add(
        ref.type === "ACTION_COMPLETED" ? "completed" : "attempted"
      );
      receiptEl.appendChild(dot);

      if (ref.capability_id != null) {
        const capBadge = document.createElement("span");
        capBadge.className = "goal-card-receipt-cap";
        capBadge.textContent = "Cap " + ref.capability_id;
        receiptEl.appendChild(capBadge);
      }

      const text = document.createElement("span");
      text.textContent = String(ref.summary || ref.type || "");
      receiptEl.appendChild(text);

      receiptsList.appendChild(receiptEl);
    });

    body.appendChild(receiptsList);
  }

  // Actions (inert UI only — display-only prototype)
  // Hide on completed/canceled cards where Pause/Cancel are semantically wrong
  var hideActions = goal.status === "completed"
    || goal.status === "canceled";
  if (!hideActions) {
    const actions = document.createElement("div");
    actions.className = "goal-card-actions";

    var pauseBtn = document.createElement("button");
    pauseBtn.type = "button";
    pauseBtn.className = "goal-card-action-btn";
    pauseBtn.textContent = goal.status === "paused" ? "Resume" : "Pause";
    pauseBtn.disabled = true;
    pauseBtn.title = "Display only — not connected to execution yet";
    pauseBtn.setAttribute("aria-label",
      (goal.status === "paused" ? "Resume" : "Pause")
      + " (display only)");
    actions.appendChild(pauseBtn);

    var cancelBtn = document.createElement("button");
    cancelBtn.type = "button";
    cancelBtn.className = "goal-card-action-btn destructive";
    cancelBtn.textContent = "Cancel";
    cancelBtn.disabled = true;
    cancelBtn.title = "Display only — not connected to execution yet";
    cancelBtn.setAttribute("aria-label", "Cancel (display only)");
    actions.appendChild(cancelBtn);

    body.appendChild(actions);
  }

  // Updated timestamp
  if (goal.updated_at) {
    const updated = document.createElement("div");
    updated.className = "goal-card-updated";
    try {
      updated.textContent = "Updated "
        + new Date(goal.updated_at).toLocaleString();
    } catch (_e) {
      updated.textContent = "Updated " + goal.updated_at;
    }
    body.appendChild(updated);
  }

  card.appendChild(body);

  // Click card body to select (not the header, which toggles expand)
  card.addEventListener("click", function () {
    _selectGoalCard(goal.goal_id);
  });

  return card;
}

var GOAL_STATUS_LEGEND = [
  { key: "draft", label: "Draft" },
  { key: "planning", label: "Planning" },
  { key: "waiting", label: "Waiting for approval" },
  { key: "ready", label: "Ready" },
  { key: "running", label: "Running" },
  { key: "paused", label: "Paused" },
  { key: "completed", label: "Completed" },
  { key: "blocked", label: "Blocked" },
  { key: "canceled", label: "Canceled" },
];

function renderGoalStatusLegend() {
  var legendWidget = $("goal-status-legend");
  if (!legendWidget) return;
  var host = legendWidget.querySelector(".goal-legend-items");
  if (!host) return;
  host.innerHTML = "";

  // Only show statuses that exist in the current goal set
  var goals = _getGoalCards();
  var activeStatuses = {};
  if (Array.isArray(goals)) {
    goals.forEach(function (g) {
      activeStatuses[g.status || "draft"] = true;
    });
  }

  // If a filter is active, always show that status in the legend
  if (_goalDisplayState.activeFilter) {
    activeStatuses[_goalDisplayState.activeFilter] = true;
  }

  var visibleEntries = GOAL_STATUS_LEGEND.filter(function (entry) {
    return !!activeStatuses[entry.key];
  });

  visibleEntries.forEach(function (entry) {
    var item = document.createElement("span");
    item.className = "goal-legend-item";
    item.style.cursor = "pointer";
    item.title = "Filter by " + entry.label;
    if (_goalDisplayState.activeFilter === entry.key) {
      item.classList.add("goal-legend-item--active");
    }

    var dot = document.createElement("span");
    dot.className = "goal-legend-dot";
    dot.dataset.legend = entry.key;
    item.appendChild(dot);

    var label = document.createElement("span");
    label.textContent = entry.label;
    item.appendChild(label);

    item.addEventListener("click", function () {
      _setGoalFilter(entry.key);
    });

    host.appendChild(item);
  });
}

function _renderGoalToolbar() {
  var existing = $("goal-toolbar");
  if (existing) existing.remove();

  var toolbar = document.createElement("div");
  toolbar.id = "goal-toolbar";
  toolbar.className = "goal-toolbar";

  // Sort toggle
  var sortGroup = document.createElement("div");
  sortGroup.className = "goal-toolbar-group";

  var sortLabel = document.createElement("span");
  sortLabel.className = "goal-toolbar-label";
  sortLabel.textContent = "Sort:";
  sortGroup.appendChild(sortLabel);

  ["updated", "status"].forEach(function (mode) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "goal-toolbar-btn";
    if (_goalDisplayState.sortMode === mode) {
      btn.classList.add("active");
    }
    btn.textContent = mode === "updated" ? "Last updated" : "By status";
    btn.addEventListener("click", function () { _setGoalSort(mode); });
    sortGroup.appendChild(btn);
  });

  toolbar.appendChild(sortGroup);

  // Filter indicator
  if (_goalDisplayState.activeFilter) {
    var clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.className = "goal-toolbar-btn goal-toolbar-clear";
    clearBtn.textContent = "Clear filter: "
      + _goalDisplayState.activeFilter.replace(/_/g, " ");
    clearBtn.addEventListener("click", function () {
      _setGoalFilter(null);
    });
    toolbar.appendChild(clearBtn);
  }

  return toolbar;
}

function renderGoalCardsPage() {
  _loadGoalDisplayState();

  var container = $("goal-cards-container");
  var emptyState = $("goal-cards-empty");
  if (!container) return;

  container.innerHTML = "";

  // If not yet fetched, trigger a fetch and show loading
  if (_goalCardsData === null && _goalCardsFetchState === "idle") {
    _fetchGoalCards();
    return;
  }

  // Show visible fallback notice when API failed
  if (_goalCardsFetchState === "error") {
    var notice = document.createElement("div");
    notice.className = "goal-fallback-notice";
    notice.setAttribute("role", "status");
    notice.textContent =
      "Showing demo goals because local goal storage is unavailable.";
    container.appendChild(notice);
  }

  var goals = _getGoalCards();
  var hasGoals = Array.isArray(goals) && goals.length > 0;

  // Filter
  if (_goalDisplayState.activeFilter && hasGoals) {
    goals = goals.filter(function (g) {
      return g.status === _goalDisplayState.activeFilter;
    });
  }

  // Sort
  goals = _sortGoals(goals, _goalDisplayState.sortMode);

  var hasVisible = goals.length > 0;

  if (emptyState) {
    emptyState.hidden = hasVisible;
    if (!hasVisible && _goalDisplayState.activeFilter) {
      emptyState.hidden = false;
      var emptyTitle = emptyState.querySelector(".goal-empty-title");
      if (emptyTitle) {
        emptyTitle.textContent = "No "
          + _goalDisplayState.activeFilter.replace(/_/g, " ")
          + " goals";
      }
    }
  }

  // Insert toolbar before cards
  var heroWidget = container.parentElement
    && container.parentElement.querySelector(".goal-page-hero");
  var toolbarEl = _renderGoalToolbar();
  if (heroWidget && heroWidget.nextSibling) {
    // Insert after legend, before container
    var legendEl = $("goal-status-legend");
    var insertBefore = legendEl
      ? legendEl.nextSibling : container;
    container.parentElement.insertBefore(toolbarEl, insertBefore);
  }

  if (hasVisible) {
    goals.forEach(function (goal) {
      container.appendChild(createGoalCardElement(goal));
    });
  }

  renderGoalStatusLegend();
}

/* ── End Goal Cards ────────────────────────────────────────────────── */

/* Control-center surfaces moved to dashboard-control-center.js. */

/* Chat, news, and general interaction surfaces moved to dashboard-chat-news.js. */
