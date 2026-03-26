/* Nova Dashboard - User-Friendly Runtime UX */

let ws = null;
let pendingThoughtMessageId = null;
let messageMeta = new Map();
let waitingForAssistant = false;
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
let morningState = {
  weather: "Loading...",
  news: "Loading...",
  system: "Loading...",
  calendar: "Loading...",
};
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
  summary: "No policy drafts yet. Create one explicitly when you want to prepare a delegated policy.",
  overview: {},
  items: [],
  selectedId: "",
  selectedItem: null,
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
  activity: [],
  blocked: [],
  selectedActivityKey: "",
  selectedBlockedKey: "",
  voiceRuntime: {},
};
let threadMapState = {
  summary: "No project threads yet. Save work updates to start continuity.",
  activeThread: "",
  threads: [],
  detail: null,
};
let workspaceHomeState = {
  summary: "Workspace home is preparing your latest project context.",
  snapshot: {},
  lastHydratedAt: 0,
};
let projectVisualizerState = {
  summary: "Open the structure map to see the repo as a human-friendly system view.",
  snapshot: {},
  lastHydratedAt: 0,
};

const API_BASE = `${window.location.protocol}//${window.location.host}`;
const WS_BASE = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`;
const STORAGE_KEYS = {
  firstRunDone: "nova_first_run_done",
  quickActions: "nova_quick_actions",
  hintsExpanded: "nova_hints_expanded",
  uiLargeText: "nova_ui_large_text",
  uiHighContrast: "nova_ui_high_contrast",
  uiCompactDensity: "nova_ui_compact_density",
  activePage: "nova_active_page",
  morningExpanded: "nova_morning_expanded",
  setupMode: "nova_setup_mode",
};

const PAGE_LABELS = {
  chat: "Chat",
  news: "News",
  intro: "Intro",
  home: "Home",
  workspace: "Workspace",
  memory: "Memory",
  policy: "Policies",
  trust: "Trust",
  settings: "Settings",
};

const QUICK_ACTIONS_BY_PAGE = {
  chat: [
    { id: "chat_brief", label: "Today's brief", command: "daily brief" },
    { id: "chat_weather", label: "Weather", command: "weather" },
    { id: "chat_search", label: "Search web", command: "search latest technology news" },
    { id: "chat_system", label: "System status", command: "system status" },
    { id: "chat_explain", label: "Explain this", command: "explain this" },
    { id: "chat_help_this", label: "Help me do this", command: "help me do this" },
    { id: "chat_threads", label: "Show threads", command: "show threads" },
    { id: "chat_thread_status", label: "Project status", command: "project status this" },
    { id: "chat_most_blocked", label: "Most blocked", command: "which project is most blocked right now" },
    { id: "chat_thread_memory", label: "Thread memory", command: "memory list thread this" },
    { id: "chat_memory_overview", label: "Memory overview", command: "memory overview" },
    { id: "chat_tone", label: "Tone settings", command: "tone status" },
    { id: "chat_schedules", label: "Schedules", command: "show schedules" },
    { id: "chat_patterns", label: "Pattern review", command: "pattern status" },
    { id: "chat_doc_create", label: "New analysis doc", command: "create analysis report on global technology policy updates" },
    { id: "chat_doc_list", label: "List analysis docs", command: "list analysis docs" },
  ],
  news: [
    { id: "news_get", label: "Get headlines", command: "news", stayOnPage: true },
    { id: "news_sum", label: "Source brief", command: "today's news", switchToPage: "chat" },
    { id: "news_brief", label: "Daily brief", command: "daily brief", stayOnPage: true },
    { id: "news_compare", label: "Compare stories", command: "compare headlines 1 and 2", stayOnPage: true },
    { id: "news_explain_page", label: "Explain this page", command: "what is this page" },
  ],
  intro: [
    { id: "intro_home", label: "Open Home", switchToPage: "home", command: "workspace home", stayOnPage: true },
    { id: "intro_workspace", label: "Open Workspace", switchToPage: "workspace", command: "workspace board", stayOnPage: true },
    { id: "intro_trust", label: "Open Trust", switchToPage: "trust", command: "trust center", stayOnPage: true },
    { id: "intro_settings", label: "Open Settings", switchToPage: "settings", command: "voice status", stayOnPage: true },
    { id: "intro_brief", label: "Today's brief", command: "daily brief", switchToPage: "chat" },
  ],
  home: [
    { id: "home_system", label: "System status", command: "system status", switchToPage: "chat" },
    { id: "home_calendar", label: "Calendar", command: "calendar", switchToPage: "chat" },
    { id: "home_weather", label: "Weather", command: "weather", switchToPage: "chat" },
    { id: "home_explain", label: "Explain this", command: "explain this", switchToPage: "chat" },
    { id: "home_capture", label: "Analyze screen", command: "analyze this screen", switchToPage: "chat" },
    { id: "home_threads", label: "Show threads", command: "show threads", switchToPage: "chat" },
    { id: "home_thread_status", label: "Project status", command: "project status this", switchToPage: "chat" },
    { id: "home_most_blocked", label: "Most blocked", command: "which project is most blocked right now", switchToPage: "chat" },
    { id: "home_memory_overview", label: "Memory overview", command: "memory overview", switchToPage: "memory" },
    { id: "home_tone", label: "Tone settings", command: "tone status", switchToPage: "chat" },
    { id: "home_schedules", label: "Schedules", command: "show schedules", switchToPage: "chat" },
    { id: "home_patterns", label: "Pattern review", command: "pattern status", switchToPage: "chat" },
  ],
  workspace: [
    { id: "workspace_board", label: "Workspace board", command: "workspace board", stayOnPage: true },
    { id: "workspace_threads", label: "Show threads", command: "show threads", switchToPage: "chat" },
    { id: "workspace_status", label: "Project status", command: "project status this", switchToPage: "chat" },
    { id: "workspace_visual", label: "Structure map", command: "show structure map", stayOnPage: true },
    { id: "workspace_architecture", label: "Architecture report", command: "create analysis report on this repo architecture", switchToPage: "chat" },
  ],
  memory: [
    { id: "memory_page_overview", label: "Overview", command: "memory overview", stayOnPage: true },
    { id: "memory_page_list", label: "List memory", command: "list memories", switchToPage: "chat" },
    { id: "memory_page_threads", label: "Thread memory", command: "memory list thread this", switchToPage: "chat" },
    { id: "memory_page_save", label: "Save decision", command: "memory save decision for deployment issue: verify next step", switchToPage: "chat" },
  ],
  policy: [
    { id: "policy_page_overview", label: "Refresh drafts", command: "policy overview", stayOnPage: true },
    { id: "policy_page_calendar", label: "Create calendar draft", command: "policy create weekday calendar snapshot at 8:00 am", stayOnPage: true },
    { id: "policy_page_weather", label: "Create weather draft", command: "policy create daily weather snapshot at 7:30 am", stayOnPage: true },
    { id: "policy_page_trust", label: "Trust center", command: "trust center", switchToPage: "trust", stayOnPage: true },
  ],
  trust: [
    { id: "trust_refresh", label: "Refresh trust", command: "trust center", stayOnPage: true },
    { id: "trust_system", label: "System status", command: "system status", switchToPage: "chat" },
    { id: "trust_memory", label: "Memory overview", command: "memory overview", switchToPage: "memory" },
    { id: "trust_workspace", label: "Workspace home", command: "workspace home", switchToPage: "chat" },
    { id: "trust_policies", label: "Policies", command: "policy overview", switchToPage: "policy", stayOnPage: true },
    { id: "trust_settings", label: "Settings", command: "voice status", switchToPage: "settings", stayOnPage: true },
  ],
  settings: [
    { id: "settings_voice", label: "Voice status", command: "voice status", switchToPage: "chat" },
    { id: "settings_voice_check", label: "Voice check", command: "voice check", switchToPage: "chat" },
    { id: "settings_trust", label: "Trust center", command: "trust center", switchToPage: "trust", stayOnPage: true },
    { id: "settings_policies", label: "Policies", command: "policy overview", switchToPage: "policy", stayOnPage: true },
    { id: "settings_intro", label: "Introduction", switchToPage: "intro", command: "workspace home", stayOnPage: true },
  ],
};

const COMMAND_SUGGESTIONS = [
  "morning brief",
  "summarize all headlines",
  "summary of article 1",
    "summarize politics news",
    "summarize global news",
    "summarize crypto news",
  "explain this",
  "help me do this",
  "show threads",
  "intro",
  "settings",
  "workspace home",
  "workspace board",
  "policy overview",
  "policy center",
  "policy create weekday calendar snapshot at 8:00 am",
  "trust center",
  "voice status",
  "voice check",
  "show structure map",
  "visualize this repo",
  "continue my deployment issue",
  "project status deployment issue",
  "biggest blocker in deployment issue",
  "thread detail deployment issue",
  "which project is most blocked right now",
  "memory save thread deployment issue",
  "memory list thread deployment issue",
  "memory overview",
  "tone status",
  "tone set concise",
  "tone set research detailed",
  "tone reset all",
  "show schedules",
  "schedule daily brief at 8:00 am",
  "remind me at 2:00 pm to review deployment issue",
  "dismiss schedule SCH-0000-0000",
  "pattern opt in",
  "pattern status",
  "review patterns",
  "dismiss pattern PAT-0000-0000",
  "memory save decision for deployment issue: verify PYTHONPATH in container",
  "why this recommendation",
  "which one should I download",
  "update tracked stories",
  "show relationship graph",
  "search for local weather alerts",
  "open github",
  "open documents",
  "system status",
  "speak that",
  "volume up",
  "brightness down",
  "play",
  "pause",
];

const HELP_EXAMPLES = [
  "morning brief",
  "summarize all headlines",
  "summary of article 1",
    "summarize politics news",
    "summarize global news",
    "summarize crypto news",
  "explain this",
  "help me do this",
  "show threads",
  "workspace home",
  "workspace board",
  "trust center",
  "show structure map",
  "save this as part of deployment issue",
  "continue my deployment issue",
  "project status deployment issue",
  "biggest blocker in deployment issue",
  "thread detail deployment issue",
  "which project is most blocked right now",
  "memory save thread deployment issue",
  "memory list thread deployment issue",
  "memory overview",
  "tone status",
  "tone set concise",
  "tone set research detailed",
  "tone reset all",
  "show schedules",
  "schedule daily brief at 8:00 am",
  "remind me daily at 9:00 am to review project threads",
  "cancel schedule SCH-0000-0000",
  "pattern opt in",
  "pattern status",
  "review patterns",
  "dismiss pattern PAT-0000-0000",
  "memory save decision for deployment issue: verify PYTHONPATH in container",
  "why this recommendation",
  "which one should I download",
  "research a topic",
  "create analysis report on AI regulation",
  "list analysis docs",
  "summarize doc 1",
  "explain section 2 of doc 1",
  "update tracked stories",
  "search for eclipse dates",
  "open youtube",
  "open documents",
  "system check",
  "speak that",
  "set volume 40",
  "set brightness 50",
];
const COMMAND_DISCOVERY_GROUPS = [
  { label: "Daily", commands: ["brief", "summarize all headlines", "show snapshot details"] },
  { label: "Research", commands: ["research a topic", "summarize all headlines", "show sources"] },
  { label: "Context", commands: ["explain this", "help me do this", "which one should i download"] },
  { label: "Continuity", commands: ["show threads", "save this as part of deployment issue", "continue my deployment issue"] },
  { label: "Thread insight", commands: ["project status deployment issue", "biggest blocker in deployment issue", "thread detail deployment issue"] },
  { label: "Thread memory", commands: ["memory overview", "memory save thread deployment issue", "memory list thread deployment issue"] },
  { label: "Response style", commands: ["tone status", "tone set concise", "tone set research detailed"] },
  { label: "Schedules", commands: ["show schedules", "schedule daily brief at 8:00 am", "remind me at 2:00 pm to review deployment issue"] },
  { label: "Pattern review", commands: ["pattern opt in", "pattern status", "review patterns"] },
  { label: "System", commands: ["system status", "open documents", "volume up"] },
];
const LONG_MESSAGE_CHAR_LIMIT = 280;
const LONG_MESSAGE_LINE_LIMIT = 4;
const LONG_MESSAGE_SENTENCE_LIMIT = 2;
const URL_PATTERN = /(https?:\/\/[^\s<]+)/gi;
const WIDGET_HYDRATE_MIN_INTERVAL_MS = 15000;
const WIDGET_AUTO_REFRESH_INTERVAL_MS = 5 * 60 * 1000;

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

function buildNewsItemSnippet(item) {
  const summary = String(item?.summary || "").trim();
  const title = String(item?.title || "").trim();
  if (summary) {
    const normalizedSummary = summary.replace(/\s+/g, " ").trim().toLowerCase();
    const normalizedTitle = title.replace(/\s+/g, " ").trim().toLowerCase();
    if (normalizedSummary && normalizedSummary !== normalizedTitle) return summary;
  }
  if (!title) return "No synopsis available for this headline.";
  return `Open the source summary for webpage-level context beyond the headline.`;
}

function normalizePageKey(page) {
  if (page === "ops") return "home";
  return Object.prototype.hasOwnProperty.call(PAGE_LABELS, page) ? page : "chat";
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
    appendChatMessage("assistant", "Connection is not ready yet. Please wait a second and try again.", null, "System status");
    return false;
  }
  return true;
}

function hydrateMemoryManagement(force = false) {
  const now = Date.now();
  if (!force && now - Number(memoryCenterState.lastHydratedAt || 0) < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  memoryCenterState.lastHydratedAt = now;
  sendSilentMemoryCommand("memory overview");
  sendSilentMemoryCommand("list memories");
}

function requestWorkspaceHomeRefresh(force = false) {
  const now = Date.now();
  if (!force && now - Number(workspaceHomeState.lastHydratedAt || 0) < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  workspaceHomeState.lastHydratedAt = now;
  safeWSSend({ text: "workspace home", silent_widget_refresh: true });
}

function requestProjectStructureMapRefresh(force = false) {
  const now = Date.now();
  if (!force && now - Number(projectVisualizerState.lastHydratedAt || 0) < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  projectVisualizerState.lastHydratedAt = now;
  safeWSSend({ text: "show structure map", silent_widget_refresh: true });
}

function requestPolicyOverviewRefresh(force = false) {
  const now = Date.now();
  if (!force && now - Number(policyCenterState.lastHydratedAt || 0) < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  policyCenterState.lastHydratedAt = now;
  safeWSSend({ text: "policy overview", silent_widget_refresh: true });
}

function requestPolicyDetail(policyId) {
  const clean = String(policyId || "").trim().toUpperCase();
  if (!clean) return;
  policyCenterState.selectedId = clean;
  safeWSSend({ text: `policy show ${clean}`, silent_widget_refresh: true });
}

function requestWorkspaceThreadDetail(threadName) {
  const clean = String(threadName || "").trim();
  if (!clean) return;
  threadMapState.activeThread = clean;
  safeWSSend({ text: `thread detail ${clean}`, silent_widget_refresh: true });
}

function getSetupMode() {
  const stored = String(localStorage.getItem(STORAGE_KEYS.setupMode) || "local").trim().toLowerCase();
  return ["local", "bring_your_own_key", "managed_cloud"].includes(stored) ? stored : "local";
}

function setSetupMode(mode) {
  const normalized = String(mode || "").trim().toLowerCase();
  const nextMode = ["local", "bring_your_own_key", "managed_cloud"].includes(normalized) ? normalized : "local";
  localStorage.setItem(STORAGE_KEYS.setupMode, nextMode);
  renderIntroPage();
  renderSettingsPage();
}

function getSetupModeMeta(mode = getSetupMode()) {
  if (mode === "bring_your_own_key") {
    return {
      label: "Bring Your Own API Key",
      badge: "Manual cloud",
      copy: "You control provider choice, billing, and limits. Nova should only use paid APIs when you knowingly configure them.",
    };
  }
  if (mode === "managed_cloud") {
    return {
      label: "Managed Cloud Access",
      badge: "Guided setup",
      copy: "This is the easiest long-term setup path, but it still needs an explicit account and visible usage controls before it should be treated as active.",
    };
  }
  return {
    label: "Local Mode",
    badge: "Offline-first",
    copy: "Nova stays local-first, private, and cost-free by default. This is the safest current setup for everyday use.",
  };
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
    if (!editInput.dataset.userEdited) {
      editInput.value = "";
    }
    detailNote.textContent = "Memory remains explicit and user-owned. Edit, unlock, and delete still require the governed confirmation flow.";
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
  detailNote.textContent = selected.deleted
    ? "This memory item has been deleted. Refresh the list to inspect the current durable set."
    : "Edit, unlock, and delete stay governed. The page prepares the command, and Nova still confirms destructive changes.";
}

function renderPersonalLayerWidget() {
  const summary = $("personal-layer-summary");
  const grid = $("personal-layer-grid");
  if (!summary || !grid) return;

  const memoryTotal = Number((memoryOverviewState.snapshot && memoryOverviewState.snapshot.total_count) || 0);
  const dueCount = Array.isArray(notificationState.snapshot && notificationState.snapshot.due_items)
    ? notificationState.snapshot.due_items.length
    : 0;
  const upcomingCount = Array.isArray(notificationState.snapshot && notificationState.snapshot.upcoming_items)
    ? notificationState.snapshot.upcoming_items.length
    : 0;
  const patternCount = Array.isArray(patternReviewState.snapshot && patternReviewState.snapshot.proposals)
    ? patternReviewState.snapshot.proposals.length
    : 0;

  summary.textContent = [
    memoryOverviewState.summary || "Memory is ready for explicit saves.",
    toneState.summary || "Tone is balanced.",
  ].filter(Boolean).slice(0, 2).join(" ");

  clear(grid);
  [
    {
      title: "Memory",
      copy: memoryOverviewState.summary || "No durable memory saved yet.",
      chips: [`${memoryTotal} durable item${memoryTotal === 1 ? "" : "s"}`],
      action: () => setActivePage("memory"),
      actionLabel: "Open page",
    },
    {
      title: "Tone",
      copy: toneState.summary || "Global tone: balanced.",
      chips: [String((toneState.snapshot && toneState.snapshot.global_profile_label) || "Balanced")],
      action: () => showToneModal(),
      actionLabel: "Settings",
    },
    {
      title: "Schedules",
      copy: notificationState.summary || "No schedules yet.",
      chips: [
        dueCount > 0 ? `${dueCount} due now` : "No items due",
        upcomingCount > 0 ? `${upcomingCount} upcoming` : "No upcoming",
      ],
      action: () => showScheduleModal(),
      actionLabel: "Review",
    },
    {
      title: "Pattern Review",
      copy: patternReviewState.summary || "Pattern review is off.",
      chips: [
        Boolean(patternReviewState.snapshot && patternReviewState.snapshot.opt_in_enabled) ? "Opted in" : "Opted out",
        patternCount > 0 ? `${patternCount} proposal${patternCount === 1 ? "" : "s"}` : "No proposals",
      ],
      action: () => injectUserText("pattern status", "text"),
      actionLabel: "Status",
    },
  ].forEach((entry) => {
    const tile = document.createElement("div");
    tile.className = "personal-layer-tile";

    const title = document.createElement("div");
    title.className = "personal-layer-title";
    title.textContent = entry.title;
    tile.appendChild(title);

    const copy = document.createElement("div");
    copy.className = "personal-layer-copy";
    copy.textContent = entry.copy;
    tile.appendChild(copy);

    const chipRow = document.createElement("div");
    chipRow.className = "personal-layer-chip-row";
    entry.chips.filter(Boolean).forEach((chipText) => {
      const chip = document.createElement("span");
      chip.className = "confidence-badge";
      chip.textContent = chipText;
      chipRow.appendChild(chip);
    });
    tile.appendChild(chipRow);

    const actionBtn = document.createElement("button");
    actionBtn.type = "button";
    actionBtn.className = "assistant-action-btn";
    actionBtn.textContent = entry.actionLabel;
    actionBtn.addEventListener("click", entry.action);
    tile.appendChild(actionBtn);

    grid.appendChild(tile);
  });
}

function setOrbStatus(state) {
  sttState = state;
  const el = $("orb-status");
  if (el) el.textContent = state;
}

function handleVoiceAck(message) {
  const spokenAck = String(message || "Got it.").trim() || "Got it.";
  setOrbStatus("HEARD");
  setLoadingHint(`${spokenAck} Thinking...`);
  setThinkingBar(true);
  if (ackResetTimer) clearTimeout(ackResetTimer);
  ackResetTimer = setTimeout(() => {
    if (sttState === "HEARD") setOrbStatus("PROCESSING");
    ackResetTimer = null;
  }, 1200);
}

function setLoadingHint(text = "") {
  const bar = $("thinking-bar");
  if (!bar) return;
  bar.textContent = text || "Processing";
}

function setThinkingBar(visible) {
  const bar = $("thinking-bar");
  if (!bar) return;
  bar.style.display = visible ? "block" : "none";
}

function loadingHintForInput(text) {
  const q = (text || "").toLowerCase();
  if (q.includes("search") || q.includes("look up") || q.includes("research")) return "Checking online sources";
  if (q.includes("morning") || q.includes("brief")) return "Preparing your brief";
  if (q.includes("explain this") || q.includes("what is this") || q.includes("analyze this") || q.includes("screenshot")) return "Analyzing visible context";
  return "Processing";
}

function safeWSSend(message) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return false;
  const payload = (message && typeof message === "object" && !Array.isArray(message)) ? { ...message } : message;
  if (payload && typeof payload === "object" && !Array.isArray(payload) && typeof payload.text === "string") {
    const channel = String(payload.channel || "text").toLowerCase();
    payload.channel = channel === "voice" ? "voice" : "text";
    if (!payload.invocation_source) {
      payload.invocation_source = payload.channel === "voice" ? "voice" : "ui";
    }
  }
  ws.send(JSON.stringify(payload));
  return true;
}

function renderMorningPanel() {
  const weather = $("morning-weather");
  const news = $("morning-news");
  const system = $("morning-system");
  const calendar = $("morning-calendar");
  if (weather) weather.textContent = morningState.weather;
  if (news) news.textContent = morningState.news;
  if (system) system.textContent = morningState.system;
  if (calendar) calendar.textContent = morningState.calendar;
}

function renderContextInsight(summaryText, steps = []) {
  const summary = $("context-insight-summary");
  const stepsHost = $("context-insight-steps");
  if (summary) {
    const text = String(summaryText || "").trim();
    summary.textContent = text || "Use \"explain this\" and Nova will summarize what it sees.";
  }
  if (!stepsHost) return;
  clear(stepsHost);
  const items = Array.isArray(steps) ? steps : [];
  items.slice(0, 4).forEach((step) => {
    const clean = String(step || "").trim();
    if (!clean) return;
    const li = document.createElement("li");
    li.textContent = clean;
    stepsHost.appendChild(li);
  });
}

function renderScreenCaptureInsight(data) {
  const bounds = (data && data.bounds) || {};
  const width = Number(bounds.width);
  const height = Number(bounds.height);
  const sizeText = Number.isFinite(width) && Number.isFinite(height) ? `${Math.round(width)}x${Math.round(height)}` : "requested size";
  renderContextInsight(`Captured the screen region around your cursor (${sizeText}).`, [
    "Say \"explain this\" to get an interpretation.",
  ]);
}

function renderScreenAnalysisInsight(data) {
  const summary = String((data && data.summary) || "").trim() || "Screen analysis completed.";
  const steps = Array.isArray(data && data.next_steps) ? data.next_steps : [];
  renderContextInsight(summary, steps);
}

function renderFileExplanationInsight(data) {
  const filePath = String((data && data.file_path) || "").trim();
  const summary = String((data && data.summary) || "").trim();
  const name = filePath ? filePath.split(/[\\/]/).pop() : "file";
  const title = summary || `File explanation ready for ${name}.`;
  renderContextInsight(title, filePath ? [`Source file: ${filePath}`] : []);
}

function renderThreadMapWidget(data = {}) {
  const summary = $("thread-map-summary");
  const listHost = $("thread-map-list");
  const active = String((data && data.active_thread) || "").trim();
  const threads = Array.isArray(data && data.threads) ? data.threads : [];
  threadMapState.activeThread = active;
  threadMapState.threads = threads.map((item) => ({ ...(item || {}) }));

  if (summary) {
    if (!threads.length) {
      summary.textContent = "No project threads yet. Save work updates to start continuity.";
    } else if (active) {
      summary.textContent = `Active thread: ${active}`;
    } else {
      summary.textContent = `${threads.length} project thread${threads.length === 1 ? "" : "s"} available.`;
    }
    threadMapState.summary = summary.textContent;
  }
  if (!listHost) return;
  clear(listHost);
  const detailPanel = $("thread-detail-panel");
  if (detailPanel && threads.length === 0) {
    detailPanel.hidden = true;
  }

  threads.slice(0, 8).forEach((thread) => {
    const name = String((thread && thread.name) || "").trim();
    if (!name) return;
    const li = document.createElement("li");
    li.className = "thread-map-item";
    if (active && name === active) li.classList.add("active");

    const heading = document.createElement("div");
    heading.className = "thread-map-heading";

    const title = document.createElement("div");
    title.className = "thread-map-title";
    title.textContent = name;
    heading.appendChild(title);

    const memoryCountRaw = Number((thread && thread.memory_count) || 0);
    const memoryCount = Number.isFinite(memoryCountRaw) ? Math.max(0, Math.round(memoryCountRaw)) : 0;
    const memoryBadge = document.createElement("button");
    memoryBadge.type = "button";
    memoryBadge.className = "thread-memory-badge";
    memoryBadge.textContent = `Memory: ${memoryCount}`;
    memoryBadge.addEventListener("click", () => injectUserText(`memory list thread ${name}`, "text"));
    heading.appendChild(memoryBadge);

    li.appendChild(heading);

    const goal = String((thread && thread.goal) || "").trim();
    const artifactCount = Number((thread && thread.artifact_count) || 0);
    const blockerCount = Number((thread && thread.blocker_count) || 0);
    const latestBlocker = String((thread && thread.latest_blocker) || "").trim();
    const latestDecision = String((thread && thread.latest_decision) || "").trim();
    const lastMemoryUpdated = String((thread && thread.last_memory_updated_at) || "").trim();
    const changeSummary = String((thread && thread.change_summary) || "").trim();
    const healthState = String((thread && thread.health_state) || "").trim().toUpperCase();
    const healthReason = String((thread && thread.health_reason) || "").trim();
    const meta = document.createElement("div");
    meta.className = "thread-map-meta";
    if (goal) {
      meta.textContent = `${goal} | health ${healthState || "AT-RISK"} | artifacts ${artifactCount} | blockers ${blockerCount}`;
    } else {
      meta.textContent = `health ${healthState || "AT-RISK"} | artifacts ${artifactCount} | blockers ${blockerCount}`;
    }
    li.appendChild(meta);
    if (healthReason) {
      const reason = document.createElement("div");
      reason.className = "thread-map-meta";
      reason.textContent = `Why: ${healthReason}`;
      li.appendChild(reason);
    }
    if (latestBlocker) {
      const blocker = document.createElement("div");
      blocker.className = "thread-map-meta";
      blocker.textContent = `Latest blocker: ${latestBlocker}`;
      li.appendChild(blocker);
    }
    if (latestDecision) {
      const decision = document.createElement("div");
      decision.className = "thread-map-meta thread-map-insight";
      decision.textContent = `Latest decision: ${latestDecision}`;
      li.appendChild(decision);
    }
    if (lastMemoryUpdated) {
      const memoryUpdate = document.createElement("div");
      memoryUpdate.className = "thread-map-meta";
      memoryUpdate.textContent = `Last memory update: ${formatThreadTimestamp(lastMemoryUpdated)}`;
      li.appendChild(memoryUpdate);
    }
    if (changeSummary) {
      const changed = document.createElement("div");
      changed.className = "thread-map-meta thread-map-change";
      changed.textContent = changeSummary;
      li.appendChild(changed);
    }

    const decisionRow = document.createElement("div");
    decisionRow.className = "thread-decision-row";
    decisionRow.hidden = true;

    const decisionInput = document.createElement("input");
    decisionInput.type = "text";
    decisionInput.className = "thread-decision-input";
    decisionInput.placeholder = "Save a decision for this thread...";
    decisionInput.maxLength = 320;
    decisionRow.appendChild(decisionInput);

    const decisionSaveBtn = document.createElement("button");
    decisionSaveBtn.type = "button";
    decisionSaveBtn.textContent = "Save decision";
    decisionSaveBtn.addEventListener("click", () => {
      const decisionText = String(decisionInput.value || "").replace(/\s+/g, " ").trim();
      if (!decisionText) {
        decisionInput.focus();
        return;
      }
      injectUserText(`memory save decision for ${name}: ${decisionText}`, "text");
      decisionInput.value = "";
      decisionRow.hidden = true;
    });
    decisionRow.appendChild(decisionSaveBtn);

    const decisionCancelBtn = document.createElement("button");
    decisionCancelBtn.type = "button";
    decisionCancelBtn.textContent = "Cancel";
    decisionCancelBtn.addEventListener("click", () => {
      decisionInput.value = "";
      decisionRow.hidden = true;
    });
    decisionRow.appendChild(decisionCancelBtn);

    decisionInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        decisionSaveBtn.click();
      } else if (event.key === "Escape") {
        event.preventDefault();
        decisionCancelBtn.click();
      }
    });

    li.appendChild(decisionRow);

    const actions = document.createElement("div");
    actions.className = "thread-map-actions";

    const continueBtn = document.createElement("button");
    continueBtn.type = "button";
    continueBtn.textContent = "Continue";
    continueBtn.addEventListener("click", () => injectUserText(`continue my ${name}`, "text"));
    actions.appendChild(continueBtn);

    const attachBtn = document.createElement("button");
    attachBtn.type = "button";
    attachBtn.textContent = "Attach latest";
    attachBtn.addEventListener("click", () => injectUserText(`save this as part of ${name}`, "text"));
    actions.appendChild(attachBtn);

    const statusBtn = document.createElement("button");
    statusBtn.type = "button";
    statusBtn.textContent = "Status";
    statusBtn.addEventListener("click", () => injectUserText(`project status ${name}`, "text"));
    actions.appendChild(statusBtn);

    const saveMemoryBtn = document.createElement("button");
    saveMemoryBtn.type = "button";
    saveMemoryBtn.textContent = "Save memory";
    saveMemoryBtn.addEventListener("click", () => injectUserText(`memory save thread ${name}`, "text"));
    actions.appendChild(saveMemoryBtn);

    const listMemoryBtn = document.createElement("button");
    listMemoryBtn.type = "button";
    listMemoryBtn.textContent = `List memory (${memoryCount})`;
    listMemoryBtn.addEventListener("click", () => injectUserText(`memory list thread ${name}`, "text"));
    actions.appendChild(listMemoryBtn);

    const decisionBtn = document.createElement("button");
    decisionBtn.type = "button";
    decisionBtn.textContent = "Save decision";
    decisionBtn.addEventListener("click", () => {
      decisionRow.hidden = !decisionRow.hidden;
      if (!decisionRow.hidden) {
        decisionInput.focus();
      }
    });
    actions.appendChild(decisionBtn);

    const detailBtn = document.createElement("button");
    detailBtn.type = "button";
    detailBtn.textContent = "Details";
    detailBtn.addEventListener("click", () => injectUserText(`thread detail ${name}`, "text"));
    actions.appendChild(detailBtn);

    li.appendChild(actions);
    listHost.appendChild(li);
  });

  requestWorkspaceHomeRefresh();
  renderWorkspaceBoardPage();
}

function renderWorkspaceHomeWidget(data = {}) {
  if (data && typeof data === "object" && Object.keys(data).length) {
    workspaceHomeState.snapshot = { ...workspaceHomeState.snapshot, ...data };
    workspaceHomeState.summary = String(data.summary || workspaceHomeState.summary).trim() || workspaceHomeState.summary;
  }

  const summary = $("workspace-home-summary");
  const focusHost = $("workspace-home-focus");
  const gridHost = $("workspace-home-grid");
  const docsHost = $("workspace-home-docs");
  const actionsHost = $("workspace-home-actions");
  if (!summary || !focusHost || !gridHost || !docsHost || !actionsHost) return;

  const snapshot = workspaceHomeState.snapshot || {};
  const focus = (snapshot && typeof snapshot.focus_thread === "object") ? snapshot.focus_thread : {};
  const recentDocs = Array.isArray(snapshot.recent_documents) ? snapshot.recent_documents : [];
  const recentActivity = Array.isArray(snapshot.recent_activity) ? snapshot.recent_activity : [];
  const recentMemory = Array.isArray(snapshot.recent_memory_items) ? snapshot.recent_memory_items : [];
  const blockedConditions = Array.isArray(snapshot.blocked_conditions) ? snapshot.blocked_conditions : [];
  const recommendedActions = Array.isArray(snapshot.recommended_actions) ? snapshot.recommended_actions : [];
  const recentThreads = Array.isArray(snapshot.recent_threads) ? snapshot.recent_threads : [];

  summary.textContent = workspaceHomeState.summary || "Workspace home is preparing your latest project context.";

  clear(focusHost);
  const focusName = String(focus.name || "").trim();
  if (focusName) {
    const title = document.createElement("div");
    title.className = "workspace-home-focus-title";
    title.textContent = focusName;
    focusHost.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "workspace-home-focus-meta";
    const metaParts = [];
    const goal = String(focus.goal || "").trim();
    const healthState = String(focus.health_state || "").trim().toUpperCase();
    if (goal) metaParts.push(goal);
    if (healthState) metaParts.push(`Health ${healthState}`);
    if (Number.isFinite(Number(focus.memory_count || 0))) metaParts.push(`Memory ${Number(focus.memory_count || 0)}`);
    meta.textContent = metaParts.join(" · ");
    focusHost.appendChild(meta);

    const healthReason = String(focus.health_reason || "").trim();
    if (healthReason) {
      const why = document.createElement("div");
      why.className = "workspace-home-focus-copy";
      why.textContent = `Why: ${healthReason}`;
      focusHost.appendChild(why);
    }

    const blocker = String(focus.latest_blocker || "").trim();
    if (blocker) {
      const blockerRow = document.createElement("div");
      blockerRow.className = "workspace-home-focus-copy";
      blockerRow.textContent = `Current blocker: ${blocker}`;
      focusHost.appendChild(blockerRow);
    }

    const nextAction = String(focus.latest_next_action || "").trim();
    if (nextAction) {
      const nextRow = document.createElement("div");
      nextRow.className = "workspace-home-focus-copy workspace-home-focus-next";
      nextRow.textContent = `Next step: ${nextAction}`;
      focusHost.appendChild(nextRow);
    }

    const latestDecision = String(focus.latest_decision || "").trim();
    if (latestDecision) {
      const decisionRow = document.createElement("div");
      decisionRow.className = "workspace-home-focus-copy";
      decisionRow.textContent = `Latest decision: ${latestDecision}`;
      focusHost.appendChild(decisionRow);
    }
  } else {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
    empty.textContent = "No focus project yet. Start with a repo summary, create a thread, or save a work update into memory.";
    focusHost.appendChild(empty);
  }

  clear(gridHost);
  [
    {
      title: "Project Threads",
      value: `${Number(snapshot.thread_count || 0)}`,
      copy: recentThreads.length
        ? recentThreads.slice(0, 2).map((item) => String(item.name || "").trim()).filter(Boolean).join(" · ")
        : "No project threads yet.",
    },
    {
      title: "Project Memory",
      value: `${Number(snapshot.project_memory_total || 0)}`,
      copy: `${Number(snapshot.memory_total || 0)} total durable item${Number(snapshot.memory_total || 0) === 1 ? "" : "s"}`,
    },
    {
      title: "Reports",
      value: `${recentDocs.length}`,
      copy: recentDocs.length
        ? recentDocs.map((doc) => `Doc ${doc.id}`).join(" · ")
        : "No analysis docs in this session yet.",
    },
    {
      title: "Recent Actions",
      value: `${recentActivity.length}`,
      copy: recentActivity.length
        ? recentActivity.slice(0, 2).map((item) => String(item.title || "Runtime event").trim()).join(" · ")
        : "No recent runtime activity captured here yet.",
    },
  ].forEach((item) => {
    const card = document.createElement("div");
    card.className = "workspace-home-stat";

    const heading = document.createElement("div");
    heading.className = "workspace-home-stat-title";
    heading.textContent = item.title;
    card.appendChild(heading);

    const value = document.createElement("div");
    value.className = "workspace-home-stat-value";
    value.textContent = item.value;
    card.appendChild(value);

    const copy = document.createElement("div");
    copy.className = "workspace-home-stat-copy";
    copy.textContent = item.copy;
    card.appendChild(copy);

    gridHost.appendChild(card);
  });

  clear(docsHost);
  if (recentDocs.length) {
    recentDocs.forEach((doc) => {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "workspace-home-doc";
      row.addEventListener("click", () => {
        setActivePage("chat");
        injectUserText(`summarize doc ${doc.id}`, "text");
      });

      const title = document.createElement("div");
      title.className = "workspace-home-doc-title";
      title.textContent = `Doc ${doc.id}: ${String(doc.title || "").trim()}`;
      row.appendChild(title);

      const copy = document.createElement("div");
      copy.className = "workspace-home-doc-copy";
      copy.textContent = String(doc.summary || doc.topic || "Open in chat for the current summary.").trim();
      row.appendChild(copy);

      docsHost.appendChild(row);
    });
  } else if (recentMemory.length) {
    recentMemory.forEach((item) => {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "workspace-home-doc";
      row.addEventListener("click", () => {
        setActivePage("memory");
        sendSilentMemoryCommand(`memory show ${String(item.id || "").trim()}`);
      });

      const title = document.createElement("div");
      title.className = "workspace-home-doc-title";
      title.textContent = String(item.title || item.id || "Memory item").trim();
      row.appendChild(title);

      const copy = document.createElement("div");
      copy.className = "workspace-home-doc-copy";
      copy.textContent = `Recent memory${item.updated_at ? ` · ${formatThreadTimestamp(item.updated_at)}` : ""}`;
      row.appendChild(copy);

      docsHost.appendChild(row);
    });
  } else {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
    empty.textContent = "Reports and recent project memory will appear here as you use Nova on ongoing work.";
    docsHost.appendChild(empty);
  }

  if (blockedConditions.length) {
    const blocked = document.createElement("div");
    blocked.className = "workspace-home-blocked";
    blocked.textContent = `Blocked now: ${blockedConditions.map((item) => String(item.label || item.area || "Condition").trim()).filter(Boolean).join(" · ")}`;
    docsHost.appendChild(blocked);
  }

  clear(actionsHost);
  const actions = recommendedActions.length
    ? recommendedActions
    : [
        { label: "Show threads", command: "show threads" },
        { label: "Memory overview", command: "memory overview" },
        { label: "List analysis docs", command: "list analysis docs" },
      ];
  actions.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "assistant-action-btn";
    button.textContent = String(item.label || "Run").trim();
    button.addEventListener("click", () => {
      const command = String(item.command || "").trim();
      if (!command) return;
      setActivePage("chat");
      injectUserText(command, "text");
    });
    actionsHost.appendChild(button);
  });

  renderWorkspaceBoardPage();
}

function renderProjectStructureMapWidget(data = {}) {
  if (data && typeof data === "object" && Object.keys(data).length) {
    projectVisualizerState.snapshot = { ...projectVisualizerState.snapshot, ...data };
    projectVisualizerState.summary = String(data.summary || projectVisualizerState.summary).trim() || projectVisualizerState.summary;
  }

  const summary = $("project-structure-summary");
  const tree = $("project-structure-tree");
  const highlightHost = $("project-structure-highlights");
  const graphSummary = $("project-structure-graph-summary");
  const graphHost = $("project-structure-graph");
  const relationsHost = $("project-structure-relations");
  const legendHost = $("project-structure-legend");
  const note = $("project-structure-note");
  const actionsHost = $("project-structure-actions");
  if (!summary || !tree || !highlightHost || !note || !actionsHost) {
    renderWorkspaceBoardPage();
    return;
  }

  const snapshot = projectVisualizerState.snapshot || {};
  const treeLines = Array.isArray(snapshot.tree_lines) ? snapshot.tree_lines : [];
  const highlights = Array.isArray(snapshot.highlights) ? snapshot.highlights : [];
  const actions = Array.isArray(snapshot.recommended_actions) ? snapshot.recommended_actions : [];
  const graphNodes = Array.isArray(snapshot.graph_nodes) ? snapshot.graph_nodes : [];
  const graphEdges = Array.isArray(snapshot.graph_edges) ? snapshot.graph_edges : [];
  const graphLegend = Array.isArray(snapshot.graph_legend) ? snapshot.graph_legend : [];

  summary.textContent = projectVisualizerState.summary || "Open the structure map to see the repo as a human-friendly system view.";
  tree.textContent = treeLines.length
    ? treeLines.join("\n")
    : "No structure map loaded yet. Use Refresh map to build one for the current workspace.";
  if (graphSummary) {
    graphSummary.textContent = String(snapshot.graph_summary || "Structured graph output will appear here once Nova has mapped the current workspace.").trim();
  }
  note.textContent = String(snapshot.note || "This structure map is read-only and meant to help people understand the codebase faster.").trim();

  clear(highlightHost);
  if (!highlights.length) {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
    empty.textContent = "Key nodes will appear here after the structure map loads.";
    highlightHost.appendChild(empty);
  } else {
    highlights.forEach((item) => {
      const card = document.createElement("div");
      card.className = "workspace-spotlight-card";

      const title = document.createElement("div");
      title.className = "workspace-spotlight-title";
      title.textContent = String(item.label || "Key node").trim();
      card.appendChild(title);

      const copy = document.createElement("div");
      copy.className = "workspace-spotlight-copy";
      copy.textContent = String(item.detail || "").trim();
      card.appendChild(copy);

      highlightHost.appendChild(card);
    });
  }

  if (graphHost) {
    clear(graphHost);
    if (!graphNodes.length) {
      const empty = document.createElement("div");
      empty.className = "workspace-home-empty";
      empty.textContent = "Structured nodes will appear here after the map is refreshed.";
      graphHost.appendChild(empty);
    } else {
      graphNodes.slice(0, 12).forEach((node) => {
        const card = document.createElement("div");
        card.className = "workspace-spotlight-card";

        const title = document.createElement("div");
        title.className = "workspace-spotlight-title";
        title.textContent = String(node.label || node.id || "Node").trim();
        card.appendChild(title);

        const copy = document.createElement("div");
        copy.className = "workspace-spotlight-copy";
        const parts = [
          String(node.type || "").trim(),
          String(node.group || "").trim(),
          String(node.path || "").trim(),
        ].filter(Boolean);
        copy.textContent = parts.join(" · ") || "Structured node";
        card.appendChild(copy);

        graphHost.appendChild(card);
      });
    }
  }

  if (relationsHost) {
    clear(relationsHost);
    if (!graphEdges.length) {
      const empty = document.createElement("div");
      empty.className = "workspace-home-empty";
      empty.textContent = "Structured relationships will appear here once Nova has enough repo context.";
      relationsHost.appendChild(empty);
    } else {
      graphEdges.slice(0, 10).forEach((edge) => {
        const row = document.createElement("div");
        row.className = "project-structure-relation";
        row.textContent = [
          String(edge.from_label || edge.from || "").trim() || "Source",
          String(edge.label || "connects to").trim(),
          String(edge.to_label || edge.to || "").trim() || "Target",
        ].join(" -> ");
        relationsHost.appendChild(row);
      });
    }
  }

  if (legendHost) {
    clear(legendHost);
    if (!graphLegend.length) {
      const chip = document.createElement("div");
      chip.className = "memory-detail-chip";
      chip.textContent = "Read-only explainer";
      legendHost.appendChild(chip);
    } else {
      graphLegend.forEach((item) => {
        const chip = document.createElement("div");
        chip.className = "memory-detail-chip";
        chip.textContent = String(item || "").trim();
        legendHost.appendChild(chip);
      });
    }
  }

  clear(actionsHost);
  [
    ...actions,
    { label: "Refresh map", command: "show structure map" },
  ].slice(0, 4).forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "assistant-action-btn";
    button.textContent = String(item.label || "Run").trim();
    button.addEventListener("click", () => {
      const command = String(item.command || "").trim();
      if (!command) return;
      if (command === "show structure map") {
        requestProjectStructureMapRefresh(true);
        return;
      }
      setActivePage("chat");
      injectUserText(command, "text");
    });
    actionsHost.appendChild(button);
  });

  renderWorkspaceBoardPage();
}

function renderWorkspaceBoardPage() {
  const summary = $("workspace-board-summary");
  const focusHost = $("workspace-board-focus");
  const statsHost = $("workspace-board-stats");
  const threadHost = $("workspace-board-threads");
  const decisionHost = $("workspace-board-decisions");
  const feedHost = $("workspace-board-feed");
  const actionsHost = $("workspace-board-actions");
  if (!summary || !focusHost || !statsHost || !threadHost || !feedHost || !actionsHost) return;

  const workspace = workspaceHomeState.snapshot || {};
  const focus = (workspace && typeof workspace.focus_thread === "object") ? workspace.focus_thread : {};
  const structure = projectVisualizerState.snapshot || {};
  const threads = Array.isArray(threadMapState.threads) && threadMapState.threads.length
    ? threadMapState.threads
    : Array.isArray(workspace.recent_threads) ? workspace.recent_threads : [];
  const selectedThread = (threadMapState.detail && typeof threadMapState.detail.thread === "object")
    ? threadMapState.detail.thread
    : {};
  const selectedThreadName = String(selectedThread.name || threadMapState.activeThread || focus.name || "").trim();
  const recentDocs = Array.isArray(workspace.recent_documents) ? workspace.recent_documents : [];
  const recentMemory = Array.isArray(workspace.recent_memory_items) ? workspace.recent_memory_items : [];
  const recentDecisions = Array.isArray(workspace.recent_decisions_feed) ? workspace.recent_decisions_feed : [];

  summary.textContent = workspaceHomeState.summary || "Workspace Board keeps project continuity, memory, and reports in one view.";

  clear(focusHost);
  const focusName = String(focus.name || "").trim();
  if (!focusName) {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
    empty.textContent = "No focus project yet. Start with a repo summary, a thread, or a structure map.";
    focusHost.appendChild(empty);
  } else {
    [
      `Focus project: ${focusName}`,
      String(focus.goal || "").trim() ? `Goal: ${String(focus.goal || "").trim()}` : "",
      String(focus.health_state || "").trim() ? `Health: ${String(focus.health_state || "").trim().toUpperCase()}` : "",
      String(focus.latest_blocker || "").trim() ? `Current blocker: ${String(focus.latest_blocker || "").trim()}` : "",
      String(focus.latest_next_action || "").trim() ? `Next step: ${String(focus.latest_next_action || "").trim()}` : "",
    ].filter(Boolean).forEach((line, index) => {
      const row = document.createElement("div");
      row.className = index === 0 ? "workspace-home-focus-title" : "workspace-home-focus-copy";
      row.textContent = line;
      focusHost.appendChild(row);
    });
  }

  clear(statsHost);
  [
    ["Threads", `${Number(workspace.thread_count || threads.length || 0)}`],
    ["Project memory", `${Number(workspace.project_memory_total || 0)}`],
    ["Recent reports", `${recentDocs.length}`],
    ["Visual map", Array.isArray(structure.tree_lines) && structure.tree_lines.length ? "Ready" : "Not loaded"],
  ].forEach(([label, value]) => {
    statsHost.appendChild(createOverviewChip(label, value));
  });

  clear(threadHost);
  if (!threads.length) {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
    empty.textContent = "Project threads will appear here after you start saving work into a thread.";
    threadHost.appendChild(empty);
  } else {
    threads.slice(0, 4).forEach((thread) => {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "workspace-spotlight-card";
      const threadName = String(thread.name || "").trim();
      if (threadName && threadName === selectedThreadName) {
        card.classList.add("active");
      }
      card.addEventListener("click", () => {
        if (!threadName) return;
        setActivePage("workspace");
        requestWorkspaceThreadDetail(threadName);
      });

      const title = document.createElement("div");
      title.className = "workspace-spotlight-title";
      title.textContent = threadName || "Project thread";
      card.appendChild(title);

      const copy = document.createElement("div");
      copy.className = "workspace-spotlight-copy";
      const parts = [
        String(thread.goal || "").trim(),
        String(thread.health_state || "").trim() ? `Health ${String(thread.health_state || "").trim().toUpperCase()}` : "",
        Number.isFinite(Number(thread.memory_count || 0)) ? `Memory ${Number(thread.memory_count || 0)}` : "",
      ].filter(Boolean);
      copy.textContent = parts.join(" · ") || "Open in chat for thread detail.";
      card.appendChild(copy);

      threadHost.appendChild(card);
    });
  }

  if (decisionHost) {
    clear(decisionHost);
    if (!recentDecisions.length) {
      const empty = document.createElement("div");
      empty.className = "workspace-home-empty";
      empty.textContent = "Recent project decisions will appear here as threads mature.";
      decisionHost.appendChild(empty);
    } else {
      recentDecisions.slice(0, 6).forEach((item) => {
        const row = document.createElement("div");
        row.className = "workspace-spotlight-card";

        const title = document.createElement("div");
        title.className = "workspace-spotlight-title";
        title.textContent = String(item.thread_name || item.name || "Project thread").trim();
        row.appendChild(title);

        const copy = document.createElement("div");
        copy.className = "workspace-spotlight-copy";
        copy.textContent = [
          String(item.decision || item.latest_decision || "").trim(),
          String(item.updated_at ? formatThreadTimestamp(item.updated_at) : "").trim(),
        ].filter(Boolean).join(" · ") || "Recent decision";
        row.appendChild(copy);

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "assistant-action-btn";
        btn.textContent = "Open thread";
        btn.addEventListener("click", () => {
          const name = String(item.thread_name || item.name || "").trim();
          if (!name) return;
          setActivePage("workspace");
          requestWorkspaceThreadDetail(name);
        });
        row.appendChild(btn);

        decisionHost.appendChild(row);
      });
    }
  }

  clear(feedHost);
  const feedItems = recentDocs.length
    ? recentDocs.map((doc) => ({
        title: `Doc ${doc.id}: ${String(doc.title || "").trim()}`,
        copy: String(doc.summary || doc.topic || "Recent analysis document.").trim(),
        command: `summarize doc ${doc.id}`,
      }))
    : recentMemory.map((item) => ({
        title: String(item.title || item.id || "Memory item").trim(),
        copy: "Recent project memory",
        command: `memory show ${String(item.id || "").trim()}`,
        page: "memory",
      }));
  if (!feedItems.length) {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
    empty.textContent = "Recent reports and saved project memory will appear here as you use Nova.";
    feedHost.appendChild(empty);
  } else {
    feedItems.slice(0, 4).forEach((item) => {
      const row = document.createElement("button");
      row.type = "button";
      row.className = "workspace-home-doc";
      row.addEventListener("click", () => {
        if (item.page) setActivePage(item.page);
        else setActivePage("chat");
        injectUserText(item.command, "text");
      });

      const title = document.createElement("div");
      title.className = "workspace-home-doc-title";
      title.textContent = item.title;
      row.appendChild(title);

      const copy = document.createElement("div");
      copy.className = "workspace-home-doc-copy";
      copy.textContent = item.copy;
      row.appendChild(copy);

      feedHost.appendChild(row);
    });
  }

  clear(actionsHost);
  [
    { label: "Refresh workspace", fn: () => requestWorkspaceHomeRefresh(true) },
    { label: "Show structure map", fn: () => requestProjectStructureMapRefresh(true) },
    selectedThreadName
      ? { label: "Selected thread", fn: () => requestWorkspaceThreadDetail(selectedThreadName) }
      : { label: "Show threads", fn: () => { setActivePage("chat"); injectUserText("show threads", "text"); } },
    { label: "Trust center", fn: () => setActivePage("trust") },
    { label: "Settings", fn: () => setActivePage("settings") },
  ].forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "assistant-action-btn";
    button.textContent = item.label;
    button.addEventListener("click", item.fn);
    actionsHost.appendChild(button);
  });
}

function populateThreadDetailSurface(prefix, data = {}) {
  const panel = $(`${prefix}-panel`);
  const title = $(`${prefix}-title`);
  const summary = $(`${prefix}-summary`);
  const blocked = $(`${prefix}-blocked`);
  const next = $(`${prefix}-next`);
  const why = $(`${prefix}-why`);
  const decisionsHost = $(`${prefix}-decisions`);
  const memoryHost = $(`${prefix}-memory`);
  if (!panel || !title || !summary || !blocked || !next || !why || !decisionsHost || !memoryHost) return false;

  const thread = (data && typeof data.thread === "object") ? data.thread : {};
  const memoryItems = Array.isArray(data && data.memory_items) ? data.memory_items : [];
  const recentDecisions = Array.isArray(data && data.recent_decisions) ? data.recent_decisions : [];
  const whyBlocked = String((data && data.why_blocked) || "").trim();
  const nextStep = String((data && data.next_step) || "").trim();
  const whyNext = String((data && data.why_next_step) || "").trim();

  const name = String(thread.name || "").trim() || "Thread Detail";
  const health = String(thread.health_state || "").trim().toUpperCase() || "AT-RISK";
  const goal = String(thread.goal || "").trim() || "Goal not set.";
  const blockerText = String(thread.latest_blocker || "").trim() || "No blocker recorded.";
  const decisionText = String(thread.latest_decision || "").trim() || "No decision recorded.";
  const latestMemoryUpdate = formatThreadTimestamp(thread.last_memory_updated_at || "");

  title.textContent = `${name} - Detail`;
  summary.textContent = `Goal: ${goal} | Health: ${health} | Latest decision: ${decisionText}`;
  blocked.textContent = whyBlocked || `Blocked context: ${blockerText}`;
  next.textContent = `Next step: ${nextStep || "No next step recorded."}`;
  why.textContent = whyNext ? `Why this next step: ${whyNext}` : "Why this next step: not available yet.";

  clear(decisionsHost);
  const decisionsLabel = document.createElement("div");
  decisionsLabel.textContent = "Recent decisions:";
  decisionsHost.appendChild(decisionsLabel);
  if (!recentDecisions.length) {
    const empty = document.createElement("div");
    empty.textContent = "No recent decisions recorded.";
    decisionsHost.appendChild(empty);
  } else {
    const list = document.createElement("ul");
    recentDecisions.slice(-4).reverse().forEach((entry) => {
      const item = document.createElement("li");
      item.textContent = String(entry || "").trim();
      list.appendChild(item);
    });
    decisionsHost.appendChild(list);
  }

  clear(memoryHost);
  if (!memoryItems.length) {
    memoryHost.textContent = "Recent memory: none linked yet.";
  } else {
    const label = document.createElement("div");
    label.textContent = latestMemoryUpdate
      ? `Recent memory items (last update ${latestMemoryUpdate}):`
      : "Recent memory items:";
    memoryHost.appendChild(label);

    const list = document.createElement("div");
    list.className = "thread-detail-memory-list";
    memoryItems.slice(0, 5).forEach((item) => {
      const id = String((item && item.id) || "").trim();
      const itemTitle = String((item && item.title) || "").trim() || id;
      const updated = formatThreadTimestamp(item && item.updated_at);
      if (!id) return;
      const row = document.createElement("div");
      row.className = "thread-detail-memory-row";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = itemTitle;
      btn.addEventListener("click", () => injectUserText(`memory show ${id}`, "text"));
      row.appendChild(btn);
      if (updated) {
        const ts = document.createElement("span");
        ts.className = "thread-detail-memory-time";
        ts.textContent = updated;
        row.appendChild(ts);
      }
      list.appendChild(row);
    });
    memoryHost.appendChild(list);
  }

  panel.hidden = false;
  return true;
}

function renderThreadDetailWidget(data = {}) {
  threadMapState.detail = (data && typeof data === "object") ? { ...data } : null;
  const thread = (data && typeof data.thread === "object") ? data.thread : {};
  const name = String(thread.name || "").trim();
  if (name) {
    threadMapState.activeThread = name;
  }

  populateThreadDetailSurface("thread-detail", data);
  populateThreadDetailSurface("workspace-thread-detail", data);
  renderWorkspaceBoardPage();
}

function renderMemoryOverviewWidget(data = {}) {
  memoryOverviewState.snapshot = (data && typeof data === "object") ? { ...data } : {};
  memoryOverviewState.summary = String((data && data.summary) || "No durable memory saved yet. Memory becomes persistent only when you explicitly save it.").trim();

  const summary = $("memory-overview-summary");
  const tierRow = $("memory-overview-tier-row");
  const scopeRow = $("memory-overview-scope-row");
  const linkedHost = $("memory-overview-linked");
  const recentHost = $("memory-overview-recent");
  const note = $("memory-overview-note");
  const total = Number((data && data.total_count) || 0);
  const tiers = (data && typeof data.tier_counts === "object" && data.tier_counts) ? data.tier_counts : {};
  const scopes = (data && typeof data.scope_counts === "object" && data.scope_counts) ? data.scope_counts : {};
  const linkedThreads = Array.isArray(data && data.linked_threads) ? data.linked_threads : [];
  const recentItems = Array.isArray(data && data.recent_items) ? data.recent_items : [];
  const summaryText = String((data && data.summary) || "").trim();
  const inspectabilityNote = String((data && data.inspectability_note) || "").trim();

  const pageSummary = $("memory-page-summary");
  if (pageSummary) pageSummary.textContent = summaryText || "Memory becomes durable only when you explicitly save it.";
  if (!summary || !tierRow || !linkedHost || !recentHost || !note) {
    renderPersonalLayerWidget();
    requestWorkspaceHomeRefresh();
    return;
  }

  summary.textContent = memoryOverviewState.summary;
  note.textContent = inspectabilityNote || "Memory is explicit, inspectable, and revocable.";

  clear(tierRow);
  const tierEntries = [
    { label: "Active", value: Number(tiers.active || 0) },
    { label: "Locked", value: Number(tiers.locked || 0) },
    { label: "Deferred", value: Number(tiers.deferred || 0) },
  ];
  tierEntries.forEach((entry) => {
    tierRow.appendChild(createOverviewChip(entry.label, entry.value));
  });

  if (scopeRow) {
    clear(scopeRow);
    [
      { label: "Core", value: Number(scopes.nova_core || scopes.general || 0) },
      { label: "Project", value: Number(scopes.project || 0) },
      { label: "Ops", value: Number(scopes.ops || 0) },
    ].forEach((entry) => {
      scopeRow.appendChild(createOverviewChip(entry.label, entry.value));
    });
  }

  clear(linkedHost);
  const linkedLabel = document.createElement("div");
  linkedLabel.className = "memory-overview-label";
  linkedLabel.textContent = "Linked threads";
  linkedHost.appendChild(linkedLabel);
  if (!linkedThreads.length) {
    const empty = document.createElement("div");
    empty.className = "memory-overview-empty";
    empty.textContent = total > 0
      ? "No thread-linked memory items yet."
      : "Thread-linked memory will appear here after you save project memory.";
    linkedHost.appendChild(empty);
  } else {
    const list = document.createElement("div");
    list.className = "memory-overview-list";
    linkedThreads.slice(0, 4).forEach((thread) => {
      const name = String((thread && thread.thread_name) || "").trim();
      const count = Number((thread && thread.memory_count) || 0);
      const latestTitle = String((thread && thread.latest_title) || "").trim();
      const updatedAt = formatThreadTimestamp(thread && thread.last_memory_updated_at);
      if (!name) return;
      const row = document.createElement("div");
      row.className = "memory-overview-row";

      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = `${name} (${count})`;
      btn.addEventListener("click", () => injectUserText(`memory list thread ${name}`, "text"));
      row.appendChild(btn);

      const meta = document.createElement("span");
      meta.className = "memory-overview-meta";
      let metaText = latestTitle ? `Latest: ${latestTitle}` : "No recent title available.";
      if (updatedAt) metaText += ` · ${updatedAt}`;
      meta.textContent = metaText;
      row.appendChild(meta);

      list.appendChild(row);
    });
    linkedHost.appendChild(list);
  }

  clear(recentHost);
  const recentLabel = document.createElement("div");
  recentLabel.className = "memory-overview-label";
  recentLabel.textContent = "Recent memory";
  recentHost.appendChild(recentLabel);
  if (!recentItems.length) {
    const empty = document.createElement("div");
    empty.className = "memory-overview-empty";
    empty.textContent = "No recent memory items yet.";
    recentHost.appendChild(empty);
  } else {
    const list = document.createElement("div");
    list.className = "memory-overview-list";
    recentItems.slice(0, 5).forEach((item) => {
      const id = String((item && item.id) || "").trim();
      const title = String((item && item.title) || "").trim() || id;
      const tier = String((item && item.tier) || "").trim().toLowerCase() || "active";
      const threadName = String((item && item.thread_name) || "").trim();
      const updatedAt = formatThreadTimestamp(item && item.updated_at);
      if (!id) return;

      const row = document.createElement("div");
      row.className = "memory-overview-row";

      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = title;
      btn.addEventListener("click", () => injectUserText(`memory show ${id}`, "text"));
      row.appendChild(btn);

      const meta = document.createElement("span");
      meta.className = "memory-overview-meta";
      let metaText = `${tier}`;
      if (threadName) metaText += ` · ${threadName}`;
      if (updatedAt) metaText += ` · ${updatedAt}`;
      meta.textContent = metaText;
      row.appendChild(meta);

      list.appendChild(row);
    });
    recentHost.appendChild(list);
  }

  renderPersonalLayerWidget();
  if (!memoryCenterState.summary || !Array.isArray(memoryCenterState.items) || memoryCenterState.items.length === 0) {
    memoryCenterState.summary = summaryText || memoryOverviewState.summary;
    setMemoryCenterStatus(memoryCenterState.summary || "Memory is ready for explicit saves and review.");
  }
  renderMemoryCenterSurface();
  requestWorkspaceHomeRefresh();
}

function renderMemoryListWidget(data = {}) {
  const items = Array.isArray(data && data.items) ? data.items : [];
  const filters = (data && typeof data.filters === "object" && data.filters) ? data.filters : {};
  memoryCenterState.items = items.map((item) => normalizeMemoryItem(item)).filter((item) => item.id);
  memoryCenterState.filters = {
    tier: String(filters.tier || "").trim().toLowerCase(),
    scope: String(filters.scope || "").trim().toLowerCase(),
    thread_name: String(filters.thread_name || "").trim(),
    thread_key: String(filters.thread_key || "").trim(),
  };
  memoryCenterState.summary = String((data && data.summary) || "").trim() || describeMemoryFilter(memoryCenterState.filters);
  if (!memoryCenterState.selectedId && memoryCenterState.items.length > 0) {
    memoryCenterState.selectedId = memoryCenterState.items[0].id;
  } else if (memoryCenterState.selectedId && !memoryCenterState.items.some((item) => item.id === memoryCenterState.selectedId)) {
    memoryCenterState.selectedId = memoryCenterState.items.length > 0 ? memoryCenterState.items[0].id : "";
    if (!memoryCenterState.selectedId) memoryCenterState.selectedItem = null;
  }
  setMemoryCenterStatus(memoryCenterState.summary || "Governed memory list refreshed.");
  renderMemoryCenterSurface();
}

function renderMemoryItemWidget(data = {}) {
  const item = normalizeMemoryItem((data && data.item) || {});
  if (!item.id) return;
  memoryCenterState.selectedId = item.id;
  memoryCenterState.selectedItem = item;
  upsertMemoryCenterItem(item);
  setMemoryCenterStatus(item.deleted ? `Removed ${item.title || item.id} from the durable memory set.` : `Selected ${item.title || item.id}.`);
  renderMemoryCenterSurface();
}

function renderPolicyCenterPage() {
  const summary = $("policy-center-summary");
  const statsHost = $("policy-center-stats");
  const listHost = $("policy-center-list");
  const detailHost = $("policy-center-detail");
  const simulationHost = $("policy-center-simulation");
  const runHost = $("policy-center-run");
  if (!summary || !statsHost || !listHost || !detailHost || !simulationHost || !runHost) return;

  const overview = (policyCenterState.overview && typeof policyCenterState.overview === "object")
    ? policyCenterState.overview
    : {};
  const items = Array.isArray(policyCenterState.items) ? policyCenterState.items : [];
  const selected = policyCenterState.selectedItem
    || items.find((item) => String(item.policy_id || "").trim() === String(policyCenterState.selectedId || "").trim())
    || items[0]
    || null;
  if (selected && !policyCenterState.selectedItem) {
    policyCenterState.selectedItem = selected;
    policyCenterState.selectedId = String(selected.policy_id || "").trim();
  }

  summary.textContent = policyCenterState.summary
    || "Policy drafts stay disabled until you explicitly review them. Nova does not run them in the background.";

  clear(statsHost);
  [
    ["Drafts", `${Math.max(0, Number(overview.draft_count || 0))}`],
    ["Simulations", `${Math.max(0, Number(overview.simulation_count || 0))}`],
    ["Manual runs", `${Math.max(0, Number(overview.manual_run_count || 0))}`],
    ["Mode", "Manual review only"],
  ].forEach(([label, value]) => {
    const card = document.createElement("div");
    card.className = "workspace-home-stat";
    const heading = document.createElement("div");
    heading.className = "workspace-home-stat-title";
    heading.textContent = label;
    const amount = document.createElement("div");
    amount.className = "workspace-home-stat-value";
    amount.textContent = value;
    card.appendChild(heading);
    card.appendChild(amount);
    statsHost.appendChild(card);
  });

  clear(listHost);
  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
    empty.textContent = "No policy drafts yet. Use the starter actions above to create a safe review draft.";
    listHost.appendChild(empty);
  } else {
    items.forEach((item) => {
      const policyId = String(item.policy_id || "").trim();
      if (!policyId) return;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "trust-activity-item";
      if (String(policyCenterState.selectedId || "").trim() === policyId) button.classList.add("active");
      button.addEventListener("click", () => {
        policyCenterState.selectedId = policyId;
        policyCenterState.selectedItem = null;
        renderPolicyCenterPage();
        requestPolicyDetail(policyId);
      });

      const title = document.createElement("div");
      title.className = "trust-activity-title";
      title.textContent = String(item.name || policyId).trim();
      button.appendChild(title);

      const meta = document.createElement("div");
      meta.className = "trust-activity-meta";
      meta.textContent = [
        String(item.state || "draft").trim(),
        String(item.trigger_summary || "").trim(),
        `sim ${Math.max(0, Number(item.simulation_count || 0))}`,
        `runs ${Math.max(0, Number(item.manual_run_count || 0))}`,
      ].filter(Boolean).join(" · ");
      button.appendChild(meta);

      listHost.appendChild(button);
    });
  }

  clear(detailHost);
  if (!selected) {
    const empty = document.createElement("div");
    empty.className = "trust-empty";
    empty.textContent = "Select a draft to inspect its trigger, action, and envelope.";
    detailHost.appendChild(empty);
  } else {
    [
      ["ID", String(selected.policy_id || "").trim()],
      ["Name", String(selected.name || "").trim()],
      ["State", String(selected.state || "draft").trim()],
      ["Trigger", String(selected.trigger_summary || "").trim()],
      ["Action", String(selected.action_summary || "").trim()],
      ["Created by", String(selected.created_by || "user").trim()],
    ].forEach(([label, value], index) => {
      const row = document.createElement("div");
      row.className = index === 0 ? "workspace-home-focus-title" : "workspace-home-focus-copy";
      row.textContent = `${label}: ${value || "Unknown"}`;
      detailHost.appendChild(row);
    });

    const envelope = (selected.envelope && typeof selected.envelope === "object") ? selected.envelope : {};
    const envelopeRow = document.createElement("div");
    envelopeRow.className = "workspace-home-focus-copy";
    envelopeRow.textContent = `Envelope: ${Math.max(0, Number(envelope.max_runs_per_hour || 0))}/hour · ${Math.max(0, Number(envelope.max_runs_per_day || 0))}/day · timeout ${Math.max(0, Number(envelope.timeout_seconds || 0))}s · network ${envelope.network_allowed ? "allowed" : "off"}`;
    detailHost.appendChild(envelopeRow);

    const note = document.createElement("div");
    note.className = "workspace-home-focus-copy";
    note.textContent = String(selected.foundation_note || "Stored as a disabled draft. Trigger execution is not active.");
    detailHost.appendChild(note);

    const warnings = Array.isArray(selected.warnings) ? selected.warnings : [];
    warnings.slice(0, 3).forEach((warning) => {
      const row = document.createElement("div");
      row.className = "trust-activity-reason";
      row.textContent = `Warning: ${String(warning || "").trim()}`;
      detailHost.appendChild(row);
    });

    const actionRow = document.createElement("div");
    actionRow.className = "workspace-board-actions-toolbar";
    [
      { label: "Show in chat", fn: () => injectUserText(`policy show ${selected.policy_id}`, "text") },
      { label: "Simulate", fn: () => injectUserText(`policy simulate ${selected.policy_id}`, "text") },
      { label: "Run once", fn: () => injectUserText(`policy run ${selected.policy_id} once`, "text") },
      { label: "Delete", fn: () => injectUserText(`policy delete ${selected.policy_id} confirm`, "text") },
    ].forEach((action) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = action.label;
      button.addEventListener("click", action.fn);
      actionRow.appendChild(button);
    });
    detailHost.appendChild(actionRow);
  }

  clear(simulationHost);
  const simulation = (policyCenterState.simulation && typeof policyCenterState.simulation === "object")
    ? policyCenterState.simulation
    : null;
  if (!simulation) {
    const empty = document.createElement("div");
    empty.className = "trust-empty";
    empty.textContent = "Simulation results will appear here after you run a policy simulation.";
    simulationHost.appendChild(empty);
  } else {
    [
      ["Policy", String(simulation.policy_name || simulation.policy_id || "").trim()],
      ["Trigger", String(simulation.trigger || "").trim()],
      ["Action", String(simulation.action || "").trim()],
      ["Verdict", String(simulation.governor_verdict || "").trim()],
      ["Readiness", String(simulation.readiness_label || "").trim()],
      ["Capability class", String(simulation.capability_class || "").trim()],
      ["Delegation class", String(simulation.delegation_class || "").trim()],
    ].forEach(([label, value], index) => {
      const row = document.createElement("div");
      row.className = index === 0 ? "workspace-home-focus-title" : "workspace-home-focus-copy";
      row.textContent = `${label}: ${value || "Unknown"}`;
      simulationHost.appendChild(row);
    });

    const reasoning = Array.isArray(simulation.reasoning) ? simulation.reasoning : [];
    reasoning.slice(0, 5).forEach((reason) => {
      const row = document.createElement("div");
      row.className = "trust-activity-reason";
      row.textContent = String(reason || "").trim();
      simulationHost.appendChild(row);
    });
  }

  clear(runHost);
  const runResult = (policyCenterState.runResult && typeof policyCenterState.runResult === "object")
    ? policyCenterState.runResult
    : null;
  if (!runResult || !runResult.result) {
    const empty = document.createElement("div");
    empty.className = "trust-empty";
    empty.textContent = "Manual review-run results will appear here after you explicitly run a safe draft once.";
    runHost.appendChild(empty);
  } else {
    [
      ["Policy", String(runResult.policy_id || "").trim()],
      ["Success", runResult.result.success ? "yes" : "no"],
      ["Authority class", String(runResult.result.authority_class || "").trim()],
      ["External effect", runResult.result.external_effect ? "yes" : "no"],
      ["Message", String(runResult.result.message || "").trim()],
    ].forEach(([label, value], index) => {
      const row = document.createElement("div");
      row.className = index === 0 ? "workspace-home-focus-title" : "workspace-home-focus-copy";
      row.textContent = `${label}: ${value || "Unknown"}`;
      runHost.appendChild(row);
    });
    if (String(runResult.result.request_id || "").trim()) {
      const requestRow = document.createElement("div");
      requestRow.className = "trust-activity-meta";
      requestRow.textContent = `Request ID: ${String(runResult.result.request_id || "").trim()}`;
      runHost.appendChild(requestRow);
    }
  }
}

function renderPolicyOverviewWidget(data = {}) {
  policyCenterState.overview = (data && typeof data === "object") ? { ...data } : {};
  policyCenterState.summary = String((data && data.summary) || policyCenterState.summary).trim() || policyCenterState.summary;
  policyCenterState.items = Array.isArray(data && data.items) ? data.items.slice() : [];
  if (!policyCenterState.selectedId && policyCenterState.items.length > 0) {
    policyCenterState.selectedId = String(policyCenterState.items[0].policy_id || "").trim();
  } else if (
    policyCenterState.selectedId
    && !policyCenterState.items.some((item) => String(item.policy_id || "").trim() === String(policyCenterState.selectedId || "").trim())
  ) {
    policyCenterState.selectedId = policyCenterState.items.length > 0 ? String(policyCenterState.items[0].policy_id || "").trim() : "";
    if (!policyCenterState.selectedId) policyCenterState.selectedItem = null;
  }
  if (
    policyCenterState.selectedId
    && (
      !policyCenterState.selectedItem
      || String(policyCenterState.selectedItem.policy_id || "").trim() !== String(policyCenterState.selectedId || "").trim()
    )
  ) {
    requestPolicyDetail(policyCenterState.selectedId);
  }
  renderPolicyCenterPage();
}

function renderPolicyItemWidget(data = {}) {
  const item = (data && data.item && typeof data.item === "object") ? { ...data.item } : null;
  const policyId = String((item && item.policy_id) || "").trim();
  if (!policyId) return;
  policyCenterState.selectedId = policyId;
  policyCenterState.selectedItem = item;
  const summaryItem = {
    policy_id: policyId,
    name: String(item.name || "").trim(),
    state: String(item.state || "draft").trim(),
    trigger_summary: String(item.trigger_summary || "").trim(),
    action_summary: String(item.action_summary || "").trim(),
    simulation_count: Number(item.simulation_count || 0),
    manual_run_count: Number(item.manual_run_count || 0),
    created_by: String(item.created_by || "user").trim(),
    envelope: item.envelope || {},
    warnings: Array.isArray(item.warnings) ? item.warnings.slice() : [],
    foundation_note: String(item.foundation_note || "").trim(),
  };
  const existingIndex = policyCenterState.items.findIndex((entry) => String(entry.policy_id || "").trim() === policyId);
  if (existingIndex >= 0) {
    policyCenterState.items.splice(existingIndex, 1, summaryItem);
  } else {
    policyCenterState.items.unshift(summaryItem);
  }
  renderPolicyCenterPage();
}

function renderPolicySimulationWidget(data = {}) {
  const payload = (data && data.data && typeof data.data === "object") ? data.data : {};
  policyCenterState.simulation = { ...payload };
  if (String(payload.policy_id || "").trim()) {
    policyCenterState.selectedId = String(payload.policy_id || "").trim();
  }
  renderPolicyCenterPage();
}

function renderPolicyRunWidget(data = {}) {
  policyCenterState.runResult = (data && typeof data === "object") ? { ...data } : null;
  if (data && String(data.policy_id || "").trim()) {
    policyCenterState.selectedId = String(data.policy_id || "").trim();
  }
  renderPolicyCenterPage();
}

function buildToneProfileButtons(currentProfile, onSelect) {
  const row = document.createElement("div");
  row.className = "tone-choice-row";
  const profiles = Array.isArray(toneState.snapshot.profile_options) ? toneState.snapshot.profile_options : [];
  profiles.forEach((item) => {
    const profileId = String(item.id || "").trim().toLowerCase();
    if (!profileId) return;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tone-choice-btn";
    if (profileId === String(currentProfile || "").trim().toLowerCase()) {
      btn.classList.add("active");
    }
    btn.textContent = String(item.label || profileId);
    btn.title = String(item.description || "");
    btn.addEventListener("click", () => onSelect(profileId));
    row.appendChild(btn);
  });
  return row;
}

function renderToneOverviewWidget(data = {}) {
  toneState.snapshot = (data && typeof data === "object") ? { ...data } : {};
  toneState.summary = String((data && data.summary) || "Global tone: balanced. No domain overrides.").trim();

  const summary = $("tone-overview-summary");
  const globalHost = $("tone-overview-global");
  const overridesHost = $("tone-overview-overrides");
  const historyHost = $("tone-overview-history");
  const note = $("tone-overview-note");
  if (summary) summary.textContent = toneState.summary;
  if (note) note.textContent = String((data && data.inspectability_note) || "Tone changes are explicit, inspectable, and resettable.");

  if (globalHost) {
    clear(globalHost);
    const chip = document.createElement("div");
    chip.className = "tone-global-chip";
    const label = String((data && data.global_profile_label) || (data && data.global_profile) || "Balanced").trim();
    const overrideCount = Number((data && data.override_count) || 0);
    chip.textContent = overrideCount > 0 ? `Global ${label} · ${overrideCount} override${overrideCount === 1 ? "" : "s"}` : `Global ${label}`;
    globalHost.appendChild(chip);
  }

  if (overridesHost) {
    clear(overridesHost);
    const label = document.createElement("div");
    label.className = "tone-overview-label";
    label.textContent = "Domain overrides";
    overridesHost.appendChild(label);
    const overrides = Array.isArray(data && data.domain_overrides) ? data.domain_overrides : [];
    if (!overrides.length) {
      const empty = document.createElement("div");
      empty.className = "tone-overview-empty";
      empty.textContent = "No domain overrides yet.";
      overridesHost.appendChild(empty);
    } else {
      const list = document.createElement("div");
      list.className = "tone-overview-list";
      overrides.slice(0, 5).forEach((item) => {
        const row = document.createElement("div");
        row.className = "tone-overview-row";
        const title = document.createElement("div");
        title.className = "tone-overview-meta";
        title.textContent = `${String(item.label || item.domain || "Domain")}: ${String(item.profile_label || item.profile || "Balanced")}`;
        row.appendChild(title);
        const btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = "Reset";
        btn.addEventListener("click", () => injectUserText(`tone reset ${String(item.domain || "").trim()}`, "text"));
        row.appendChild(btn);
        list.appendChild(row);
      });
      overridesHost.appendChild(list);
    }
  }

  if (historyHost) {
    clear(historyHost);
    const label = document.createElement("div");
    label.className = "tone-overview-label";
    label.textContent = "Recent changes";
    historyHost.appendChild(label);
    const history = Array.isArray(data && data.history) ? data.history : [];
    if (!history.length) {
      const empty = document.createElement("div");
      empty.className = "tone-overview-empty";
      empty.textContent = "No tone changes recorded yet.";
      historyHost.appendChild(empty);
    } else {
      const list = document.createElement("ul");
      list.className = "tone-history-list";
      history.slice(0, 4).forEach((item) => {
        const li = document.createElement("li");
        const summaryText = String(item.summary || "").trim();
        const timestamp = formatThreadTimestamp(item.timestamp || "");
        li.textContent = timestamp ? `${summaryText} (${timestamp})` : summaryText;
        list.appendChild(li);
      });
      historyHost.appendChild(list);
    }
  }

  refreshToneModal();
  renderPersonalLayerWidget();
}

function refreshToneModal() {
  const overlay = $("tone-modal");
  if (!overlay) return;

  const snapshot = toneState.snapshot || {};
  const summary = $("tone-modal-summary");
  const globalHost = $("tone-modal-global");
  const domainHost = $("tone-modal-domains");
  const historyHost = $("tone-modal-history");

  if (summary) {
    summary.textContent = String(snapshot.summary || "Global tone: balanced. No domain overrides.").trim();
  }

  if (globalHost) {
    clear(globalHost);
    const heading = document.createElement("div");
    heading.className = "tone-modal-section-title";
    heading.textContent = "Global tone";
    globalHost.appendChild(heading);
    globalHost.appendChild(
      buildToneProfileButtons(snapshot.global_profile || "balanced", (profile) => {
        injectUserText(`tone set ${profile}`, "text");
      })
    );
  }

  if (domainHost) {
    clear(domainHost);
    const domains = Array.isArray(snapshot.domain_options) ? snapshot.domain_options : [];
    const overrides = Array.isArray(snapshot.domain_overrides) ? snapshot.domain_overrides : [];
    const overrideMap = new Map();
    overrides.forEach((item) => {
      overrideMap.set(String(item.domain || "").trim().toLowerCase(), String(item.profile || "").trim().toLowerCase());
    });
    domains.forEach((item) => {
      const domainId = String(item.id || "").trim().toLowerCase();
      if (!domainId) return;
      const row = document.createElement("div");
      row.className = "tone-domain-row";

      const title = document.createElement("div");
      title.className = "tone-domain-title";
      title.textContent = String(item.label || domainId);
      row.appendChild(title);

      const current = overrideMap.get(domainId) || snapshot.global_profile || "balanced";
      row.appendChild(
        buildToneProfileButtons(current, (profile) => {
          injectUserText(`tone set ${domainId} ${profile}`, "text");
        })
      );

      const resetBtn = document.createElement("button");
      resetBtn.type = "button";
      resetBtn.className = "tone-reset-btn";
      resetBtn.textContent = "Reset";
      resetBtn.disabled = !overrideMap.has(domainId);
      resetBtn.addEventListener("click", () => injectUserText(`tone reset ${domainId}`, "text"));
      row.appendChild(resetBtn);

      domainHost.appendChild(row);
    });
  }

  if (historyHost) {
    clear(historyHost);
    const history = Array.isArray(snapshot.history) ? snapshot.history : [];
    if (!history.length) {
      historyHost.textContent = "No tone changes recorded yet.";
    } else {
      const list = document.createElement("ul");
      list.className = "tone-history-list";
      history.slice(0, 6).forEach((item) => {
        const li = document.createElement("li");
        const summaryText = String(item.summary || "").trim();
        const timestamp = formatThreadTimestamp(item.timestamp || "");
        li.textContent = timestamp ? `${summaryText} (${timestamp})` : summaryText;
        list.appendChild(li);
      });
      historyHost.appendChild(list);
    }
  }
}

function showToneModal() {
  let overlay = $("tone-modal");
  if (!overlay) {
    const shell = createModalShell("tone-modal", "Response Style");
    overlay = shell.overlay;
    const card = shell.card;

    const summary = document.createElement("p");
    summary.id = "tone-modal-summary";
    summary.className = "tone-modal-summary";
    card.appendChild(summary);

    const globalHost = document.createElement("div");
    globalHost.id = "tone-modal-global";
    globalHost.className = "tone-modal-section";
    card.appendChild(globalHost);

    const domainTitle = document.createElement("div");
    domainTitle.className = "tone-modal-section-title";
    domainTitle.textContent = "Domain overrides";
    card.appendChild(domainTitle);

    const domains = document.createElement("div");
    domains.id = "tone-modal-domains";
    domains.className = "tone-modal-domains";
    card.appendChild(domains);

    const historyTitle = document.createElement("div");
    historyTitle.className = "tone-modal-section-title";
    historyTitle.textContent = "Recent changes";
    card.appendChild(historyTitle);

    const history = document.createElement("div");
    history.id = "tone-modal-history";
    history.className = "tone-modal-history";
    card.appendChild(history);

    const actions = document.createElement("div");
    actions.className = "modal-actions";

    const refreshBtn = document.createElement("button");
    refreshBtn.type = "button";
    refreshBtn.textContent = "Refresh";
    refreshBtn.addEventListener("click", () => {
      safeWSSend({ text: "tone status", silent_widget_refresh: true });
    });
    actions.appendChild(refreshBtn);

    const resetBtn = document.createElement("button");
    resetBtn.type = "button";
    resetBtn.textContent = "Reset all";
    resetBtn.addEventListener("click", () => {
      injectUserText("tone reset all", "text");
    });
    actions.appendChild(resetBtn);

    card.appendChild(actions);
  }

  if (!toneState.snapshot || !toneState.snapshot.global_profile) {
    safeWSSend({ text: "tone status", silent_widget_refresh: true });
  }
  refreshToneModal();
  overlay.style.display = "flex";
}

function renderNotificationOverviewWidget(data = {}) {
  notificationState.snapshot = (data && typeof data === "object") ? { ...data } : {};
  notificationState.summary = String((data && data.summary) || "No schedules yet. Create one explicitly when you want Nova to remind you.").trim();

  const summary = $("notification-overview-summary");
  const dueHost = $("notification-overview-due");
  const upcomingHost = $("notification-overview-upcoming");
  const note = $("notification-overview-note");

  if (summary) summary.textContent = notificationState.summary;
  if (note) note.textContent = String((data && data.inspectability_note) || "Schedules are explicit, inspectable, and cancellable.");

  if (dueHost) {
    clear(dueHost);
    const label = document.createElement("div");
    label.className = "notification-overview-label";
    label.textContent = "Due now";
    dueHost.appendChild(label);
    const dueItems = Array.isArray(data && data.due_items) ? data.due_items : [];
    if (!dueItems.length) {
      const empty = document.createElement("div");
      empty.className = "notification-overview-empty";
      empty.textContent = "No schedules are due right now.";
      dueHost.appendChild(empty);
    } else {
      const list = document.createElement("div");
      list.className = "notification-overview-list";
      dueItems.forEach((item) => {
        const row = document.createElement("div");
        row.className = "notification-overview-row";

        const title = document.createElement("div");
        title.className = "notification-overview-meta";
        const when = String(item.next_run_label || "").trim();
        title.textContent = when ? `${String(item.title || "")} (${when})` : String(item.title || "");
        row.appendChild(title);

        const actions = document.createElement("div");
        actions.className = "notification-row-actions";
        const command = String(item.command || "").trim();
        if (command) {
          const runBtn = document.createElement("button");
          runBtn.type = "button";
          runBtn.textContent = "Run";
          runBtn.addEventListener("click", () => injectUserText(command, "text"));
          actions.appendChild(runBtn);
        }
        const dismissBtn = document.createElement("button");
        dismissBtn.type = "button";
        dismissBtn.textContent = "Dismiss";
        dismissBtn.addEventListener("click", () => injectUserText(`dismiss schedule ${String(item.id || "")}`, "text"));
        actions.appendChild(dismissBtn);

        row.appendChild(actions);
        list.appendChild(row);
      });
      dueHost.appendChild(list);
    }
  }

  if (upcomingHost) {
    clear(upcomingHost);
    const label = document.createElement("div");
    label.className = "notification-overview-label";
    label.textContent = "Upcoming";
    upcomingHost.appendChild(label);
    const upcomingItems = Array.isArray(data && data.upcoming_items) ? data.upcoming_items : [];
    if (!upcomingItems.length) {
      const empty = document.createElement("div");
      empty.className = "notification-overview-empty";
      empty.textContent = "No upcoming schedules yet.";
      upcomingHost.appendChild(empty);
    } else {
      const list = document.createElement("div");
      list.className = "notification-overview-list";
      upcomingItems.forEach((item) => {
        const row = document.createElement("div");
        row.className = "notification-overview-row";

        const title = document.createElement("div");
        title.className = "notification-overview-meta";
        const when = String(item.next_run_label || "").trim();
        const recurrence = String(item.recurrence || "").trim();
        title.textContent = `${String(item.title || "")}${when ? ` (${when})` : ""}${recurrence ? ` · ${recurrence}` : ""}`;
        row.appendChild(title);

        const actions = document.createElement("div");
        actions.className = "notification-row-actions";
        const cancelBtn = document.createElement("button");
        cancelBtn.type = "button";
        cancelBtn.textContent = "Cancel";
        cancelBtn.addEventListener("click", () => injectUserText(`cancel schedule ${String(item.id || "")}`, "text"));
        actions.appendChild(cancelBtn);
        row.appendChild(actions);

        list.appendChild(row);
      });
      upcomingHost.appendChild(list);
    }
  }

  renderPersonalLayerWidget();
}

function renderPatternReviewWidget(data = {}) {
  patternReviewState.snapshot = (data && typeof data === "object") ? { ...data } : {};
  patternReviewState.summary = String((data && data.summary) || "Pattern review is off. Opt in if you want Nova to look for repeated thread and memory patterns.").trim();

  const summary = $("pattern-review-summary");
  const queueHost = $("pattern-review-queue");
  const historyHost = $("pattern-review-history");
  const note = $("pattern-review-note");
  const optBtn = $("btn-home-pattern-opt");
  const reviewBtn = $("btn-home-pattern-review");

  if (summary) summary.textContent = patternReviewState.summary;
  if (note) note.textContent = String((data && data.inspectability_note) || "Pattern review is opt-in, advisory, and discardable.").trim();

  const optInEnabled = Boolean(data && data.opt_in_enabled);
  if (optBtn) {
    optBtn.textContent = optInEnabled ? "Opt out" : "Opt in";
  }
  if (reviewBtn) {
    reviewBtn.disabled = !optInEnabled;
  }

  if (queueHost) {
    clear(queueHost);
    const label = document.createElement("div");
    label.className = "pattern-review-label";
    label.textContent = "Review queue";
    queueHost.appendChild(label);

    const proposals = Array.isArray(data && data.proposals) ? data.proposals : [];
    if (!proposals.length) {
      const empty = document.createElement("div");
      empty.className = "pattern-review-empty";
      empty.textContent = optInEnabled
        ? "No active proposals are waiting for review."
        : "Opt in first when you want Nova to generate pattern proposals.";
      queueHost.appendChild(empty);
    } else {
      const list = document.createElement("div");
      list.className = "pattern-review-list";
      proposals.slice(0, 4).forEach((item) => {
        const row = document.createElement("div");
        row.className = "pattern-review-row";

        const title = document.createElement("div");
        title.className = "pattern-review-title";
        title.textContent = String(item.title || "Pattern proposal").trim();
        row.appendChild(title);

        const body = document.createElement("div");
        body.className = "pattern-review-meta";
        body.textContent = String(item.summary || "").trim();
        row.appendChild(body);

        const evidence = Array.isArray(item.evidence) ? item.evidence : [];
        if (evidence.length) {
          const evidenceLine = document.createElement("div");
          evidenceLine.className = "pattern-review-evidence";
          evidenceLine.textContent = `Evidence: ${String(evidence[0] || "").trim()}`;
          row.appendChild(evidenceLine);
        }

        const linkedThreads = Array.isArray(item.linked_threads) ? item.linked_threads.filter(Boolean) : [];
        if (linkedThreads.length) {
          const links = document.createElement("div");
          links.className = "pattern-review-threads";
          links.textContent = `Threads: ${linkedThreads.join(", ")}`;
          row.appendChild(links);
        }

        const actions = document.createElement("div");
        actions.className = "pattern-review-actions";

        const suggestedCommands = Array.isArray(item.suggested_commands) ? item.suggested_commands.filter(Boolean) : [];
        if (suggestedCommands.length) {
          const reviewAction = document.createElement("button");
          reviewAction.type = "button";
          reviewAction.textContent = "Open context";
          reviewAction.addEventListener("click", () => injectUserText(String(suggestedCommands[0]), "text"));
          actions.appendChild(reviewAction);
        }

        const acceptBtn = document.createElement("button");
        acceptBtn.type = "button";
        acceptBtn.textContent = "Accept";
        acceptBtn.addEventListener("click", () => injectUserText(`accept pattern ${String(item.id || "").trim()}`, "text"));
        actions.appendChild(acceptBtn);

        const dismissBtn = document.createElement("button");
        dismissBtn.type = "button";
        dismissBtn.textContent = "Dismiss";
        dismissBtn.addEventListener("click", () => injectUserText(`dismiss pattern ${String(item.id || "").trim()}`, "text"));
        actions.appendChild(dismissBtn);

        row.appendChild(actions);
        list.appendChild(row);
      });
      queueHost.appendChild(list);
    }
  }

  if (historyHost) {
    clear(historyHost);
    const label = document.createElement("div");
    label.className = "pattern-review-label";
    label.textContent = "Recent decisions";
    historyHost.appendChild(label);

    const history = Array.isArray(data && data.recent_decisions) ? data.recent_decisions : [];
    if (!history.length) {
      const empty = document.createElement("div");
      empty.className = "pattern-review-empty";
      empty.textContent = "No pattern review decisions recorded yet.";
      historyHost.appendChild(empty);
    } else {
      const list = document.createElement("ul");
      list.className = "pattern-review-history-list";
      history.slice(0, 4).forEach((item) => {
        const li = document.createElement("li");
        const stamp = formatThreadTimestamp(item.timestamp || "");
        const text = String(item.summary || "").trim();
        li.textContent = stamp ? `${text} (${stamp})` : text;
        list.appendChild(li);
      });
      historyHost.appendChild(list);
    }
  }

  renderPersonalLayerWidget();
}

function showScheduleModal() {
  let overlay = $("schedule-modal");
  if (!overlay) {
    const shell = createModalShell("schedule-modal", "Schedule an Update");
    overlay = shell.overlay;
    const card = shell.card;

    const intro = document.createElement("p");
    intro.textContent = "Create explicit reminder and brief schedules. Nova will surface them quietly without running actions automatically.";
    card.appendChild(intro);

    const typeLabel = document.createElement("label");
    typeLabel.className = "tone-modal-section-title";
    typeLabel.textContent = "Type";
    card.appendChild(typeLabel);

    const typeSelect = document.createElement("select");
    typeSelect.id = "schedule-modal-type";
    typeSelect.className = "modal-search";
    typeSelect.innerHTML = [
      '<option value="daily_brief">Daily brief</option>',
      '<option value="reminder">Reminder</option>',
    ].join("");
    card.appendChild(typeSelect);

    const timeLabel = document.createElement("label");
    timeLabel.className = "tone-modal-section-title";
    timeLabel.textContent = "Time";
    card.appendChild(timeLabel);

    const timeInput = document.createElement("input");
    timeInput.id = "schedule-modal-time";
    timeInput.type = "time";
    timeInput.className = "modal-search";
    timeInput.value = "08:00";
    card.appendChild(timeInput);

    const recurrenceLabel = document.createElement("label");
    recurrenceLabel.className = "tone-modal-section-title";
    recurrenceLabel.textContent = "Reminder frequency";
    card.appendChild(recurrenceLabel);

    const recurrenceSelect = document.createElement("select");
    recurrenceSelect.id = "schedule-modal-recurrence";
    recurrenceSelect.className = "modal-search";
    recurrenceSelect.innerHTML = [
      '<option value="once">Once</option>',
      '<option value="daily">Daily</option>',
    ].join("");
    card.appendChild(recurrenceSelect);

    const bodyLabel = document.createElement("label");
    bodyLabel.className = "tone-modal-section-title";
    bodyLabel.textContent = "Reminder text";
    card.appendChild(bodyLabel);

    const bodyInput = document.createElement("input");
    bodyInput.id = "schedule-modal-body";
    bodyInput.type = "text";
    bodyInput.className = "modal-search";
    bodyInput.placeholder = "Review deployment issue";
    card.appendChild(bodyInput);

    const syncFields = () => {
      const isReminder = typeSelect.value === "reminder";
      recurrenceSelect.disabled = !isReminder;
      bodyInput.disabled = !isReminder;
      bodyInput.placeholder = isReminder ? "Review deployment issue" : "Daily brief will run when you choose.";
    };
    typeSelect.addEventListener("change", syncFields);
    syncFields();

    const actions = document.createElement("div");
    actions.className = "modal-actions";

    const saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.textContent = "Create schedule";
    saveBtn.addEventListener("click", () => {
      const timeValue = String(timeInput.value || "").trim();
      if (!timeValue) return;
      if (typeSelect.value === "daily_brief") {
        injectUserText(`schedule daily brief at ${timeValue}`, "text");
      } else {
        const reminderText = String(bodyInput.value || "").trim();
        if (!reminderText) return;
        const recurrence = recurrenceSelect.value === "daily" ? "daily " : "";
        injectUserText(`remind me ${recurrence}at ${timeValue} to ${reminderText}`, "text");
      }
      overlay.style.display = "none";
    });
    actions.appendChild(saveBtn);

    const showBtn = document.createElement("button");
    showBtn.type = "button";
    showBtn.textContent = "Show schedules";
    showBtn.addEventListener("click", () => {
      injectUserText("show schedules", "text");
      overlay.style.display = "none";
    });
    actions.appendChild(showBtn);

    card.appendChild(actions);
  }

  overlay.style.display = "flex";
}

function formatSystemSummary(data, summary = "") {
  const fallback = String(summary || "System status ready.").trim() || "System status ready.";
  if (!data || typeof data !== "object") return fallback;

  const phase = String(data.phase_display || "").trim();
  const health = String(data.health_state || "").trim();
  const cpu = Number(data.cpu_percent);
  const memory = Number(data.memory_percent);
  const disk = Number(data.disk_percent);
  const network = String(data.network_status || "").trim();
  const modelAvailability = String(data.model_availability || "").trim().toLowerCase();
  const modelReady = data.model_ready;
  const modelNote = String(data.model_note || "").trim();
  const modelRemediation = String(data.model_remediation || "").trim();
  const toneProfile = String(data.tone_global_profile || "").trim();
  const toneOverrideCount = Number(data.tone_override_count);
  const locks = Number(data.locks_active_count);

  const parts = [];
  if (phase) parts.push(`Phase ${phase}`);
  if (health) parts.push(`Health ${health}`);
  if (Number.isFinite(cpu)) parts.push(`CPU ${Math.round(cpu)}%`);
  if (Number.isFinite(memory)) parts.push(`Memory ${Math.round(memory)}%`);
  if (Number.isFinite(disk)) parts.push(`Disk ${Math.round(disk)}%`);
  if (network) parts.push(`Network ${network}`);
  if (toneProfile) {
    const toneLabel = toneProfile.charAt(0).toUpperCase() + toneProfile.slice(1);
    if (Number.isFinite(toneOverrideCount) && toneOverrideCount > 0) {
      parts.push(`Tone ${toneLabel} +${Math.round(toneOverrideCount)} override${toneOverrideCount === 1 ? "" : "s"}`);
    } else {
      parts.push(`Tone ${toneLabel}`);
    }
  }
  if (modelAvailability && modelAvailability !== "available") {
    parts.push(`Model ${modelAvailability}`);
  } else if (modelReady === false) {
    parts.push("Model not ready");
  }
  if (Number.isFinite(locks) && locks > 0) {
    parts.push(`Locks ${Math.round(locks)}`);
  }

  let rendered = parts.length ? parts.join(" · ") : fallback;
  if ((modelAvailability && modelAvailability !== "available") || modelReady === false) {
    const detail = modelRemediation || modelNote;
    if (detail) rendered = `${rendered}. ${detail}`;
  }

  return rendered;
}

function setMorningPanelExpanded(expanded) {
  const details = $("morning-details");
  const btn = $("btn-morning-toggle");
  if (!details || !btn) return;
  details.hidden = !expanded;
  btn.textContent = expanded ? "Hide details" : "Show details";
  btn.setAttribute("aria-expanded", expanded ? "true" : "false");
  localStorage.setItem(STORAGE_KEYS.morningExpanded, expanded ? "1" : "0");
}

function setupMorningWidgetToggle() {
  const btn = $("btn-morning-toggle");
  if (!btn) return;
  const expanded = localStorage.getItem(STORAGE_KEYS.morningExpanded) === "1";
  setMorningPanelExpanded(expanded);
  btn.addEventListener("click", () => {
    const isExpanded = btn.getAttribute("aria-expanded") === "true";
    setMorningPanelExpanded(!isExpanded);
  });
}

function renderOperatorHealthWidget(data = {}) {
  operatorHealthState.snapshot = (data && typeof data === "object") ? { ...data } : {};
  operatorHealthState.summary = String((data && data.operator_health_summary) || "Loading runtime health...").trim();

  const summary = $("operator-health-summary");
  const gridHost = $("operator-health-grid");
  const locksHost = $("operator-health-locks");
  const reasonsHost = $("operator-health-reasons");
  if (summary) summary.textContent = operatorHealthState.summary;

  if (gridHost) {
    clear(gridHost);
    const rows = [
      ["Phase", String(data.phase_display || `Phase ${data.build_phase || "unknown"}`).trim() || "Unknown"],
      ["Governor", String(data.governor_status || "Unknown").trim() || "Unknown"],
      ["Execution Boundary", String(data.execution_boundary_status || "Unknown").trim() || "Unknown"],
      ["Model", String(data.model_availability || "Unknown").trim() || "Unknown"],
      ["Network Mediator", String(data.network_mediator_status || "Unknown").trim() || "Unknown"],
      ["Voice", String(data.voice_status || "Unknown").trim() || "Unknown"],
      ["Memory", String(data.memory_summary || data.memory_status || "Unknown").trim() || "Unknown"],
      [
        "Policies",
        `Drafts ${Math.max(0, Number(data.policy_draft_count) || 0)} · Sims ${Math.max(0, Number(data.policy_simulation_count) || 0)} · Runs ${Math.max(0, Number(data.policy_manual_run_count) || 0)}`
      ],
      ["Ledger", `${String(data.ledger_integrity || "Unknown").trim() || "Unknown"} · ${Math.max(0, Number(data.ledger_entries_today) || 0)} today`],
      ["Locks", `${Math.max(0, Number(data.locks_active_count) || 0)} active`],
    ];

    rows.forEach(([labelText, valueText]) => {
      const row = document.createElement("div");
      row.className = "operator-health-row";

      const label = document.createElement("div");
      label.className = "operator-health-label";
      label.textContent = labelText;
      row.appendChild(label);

      const value = document.createElement("div");
      value.className = "operator-health-value";
      value.textContent = valueText;
      row.appendChild(value);

      gridHost.appendChild(row);
    });
  }

  if (locksHost) {
    clear(locksHost);
    const label = document.createElement("div");
    label.className = "operator-health-section-label";
    label.textContent = "Blocked Conditions";
    locksHost.appendChild(label);

    const items = Array.isArray(data.blocked_conditions) ? data.blocked_conditions : [];
    if (!items.length) {
      const empty = document.createElement("div");
      empty.className = "operator-health-empty";
      empty.textContent = "No blocked conditions reported.";
      locksHost.appendChild(empty);
    } else {
      const list = document.createElement("div");
      list.className = "operator-health-list";
      items.forEach((item) => {
        const row = document.createElement("div");
        row.className = "operator-health-item";

        const title = document.createElement("div");
        title.className = "operator-health-item-title";
        title.textContent = `${String(item.label || item.area || "Condition").trim()}: ${String(item.status || "unknown").trim()}`;
        row.appendChild(title);

        const reason = document.createElement("div");
        reason.className = "operator-health-item-meta";
        reason.textContent = String(item.reason || "").trim() || "No reason available.";
        row.appendChild(reason);

        list.appendChild(row);
      });
      locksHost.appendChild(list);
    }
  }

  if (reasonsHost) {
    clear(reasonsHost);
    const label = document.createElement("div");
    label.className = "operator-health-section-label";
    label.textContent = "System Reason";
    reasonsHost.appendChild(label);

    const items = Array.isArray(data.system_reasons) ? data.system_reasons : [];
    if (!items.length) {
      const empty = document.createElement("div");
      empty.className = "operator-health-empty";
      empty.textContent = "No system reasons available.";
      reasonsHost.appendChild(empty);
    } else {
      const list = document.createElement("div");
      list.className = "operator-health-list";
      items.forEach((item) => {
        const row = document.createElement("div");
        row.className = "operator-health-item";

        const title = document.createElement("div");
        title.className = "operator-health-item-title";
        title.textContent = `${String(item.area || "system").replace(/_/g, " ")}: ${String(item.status || "unknown").trim()}`;
        row.appendChild(title);

        const reason = document.createElement("div");
        reason.className = "operator-health-item-meta";
        reason.textContent = String(item.reason || "").trim() || "No reason available.";
        row.appendChild(reason);

        list.appendChild(row);
      });
      reasonsHost.appendChild(list);
    }
  }

  renderTrustCenterPage();
}

function renderCapabilitySurfaceWidget(data = {}) {
  capabilityDiscoveryState.snapshot = (data && typeof data === "object") ? { ...data } : {};
  capabilityDiscoveryState.summary = String((data && data.capability_surface_summary) || "Loading live capabilities...").trim();

  const summary = $("capability-surface-summary");
  const groupsHost = $("capability-surface-groups");
  if (summary) summary.textContent = capabilityDiscoveryState.summary;
  if (!groupsHost) return;

  clear(groupsHost);
  const groups = Array.isArray(data.available_capability_surface) ? data.available_capability_surface : [];
  if (!groups.length) {
    const empty = document.createElement("div");
    empty.className = "capability-surface-empty";
    empty.textContent = "No live capability groups are available right now.";
    groupsHost.appendChild(empty);
    return;
  }

  groups.forEach((group) => {
    const card = document.createElement("section");
    card.className = "capability-surface-group";

    const header = document.createElement("div");
    header.className = "capability-surface-group-header";

    const title = document.createElement("h4");
    title.className = "capability-surface-category";
    title.textContent = String(group.category || "Capabilities").trim() || "Capabilities";
    header.appendChild(title);

    const count = document.createElement("span");
    count.className = "confidence-badge";
    const actionCount = Array.isArray(group.actions) ? group.actions.length : 0;
    count.textContent = `${actionCount} live`;
    header.appendChild(count);
    card.appendChild(header);

    const items = Array.isArray(group.items) ? group.items : [];
    if (items.length) {
      const actionsHost = document.createElement("div");
      actionsHost.className = "capability-surface-actions";

      items.forEach((item) => {
        const labelText = String(item.action || "").trim();
        const promptText = String(item.prompt || "").trim();
        if (!labelText) return;

        const button = document.createElement("button");
        button.type = "button";
        button.className = "capability-surface-action";
        button.textContent = labelText;
        if (promptText) {
          button.title = promptText;
          button.addEventListener("click", () => runCapabilityPrompt(promptText));
        } else {
          button.disabled = true;
        }
        actionsHost.appendChild(button);
      });

      card.appendChild(actionsHost);
    } else {
      const list = document.createElement("ul");
      list.className = "capability-surface-list";
      const actions = Array.isArray(group.actions) ? group.actions : [];
      actions.forEach((action) => {
        const item = document.createElement("li");
        item.textContent = String(action || "").trim();
        if (item.textContent) list.appendChild(item);
      });

      if (!list.childNodes.length) {
        const item = document.createElement("li");
        item.textContent = "No live actions listed.";
        list.appendChild(item);
      }

      card.appendChild(list);
    }
    groupsHost.appendChild(card);
  });

  renderTrustCenterPage();
}

function runCapabilityPrompt(prompt) {
  const clean = String(prompt || "").trim();
  if (!clean) return;
  setActivePage("chat");
  injectUserText(clean, "text");
}

function renderTrustPanel(data = {}) {
  if (data && typeof data === "object") {
    trustReviewState.summary = String(data.trust_review_summary || trustReviewState.summary).trim() || trustReviewState.summary;
    trustReviewState.activity = Array.isArray(data.recent_runtime_activity) ? data.recent_runtime_activity.slice() : trustReviewState.activity;
    trustReviewState.blocked = Array.isArray(data.blocked_conditions) ? data.blocked_conditions.slice() : trustReviewState.blocked;
    trustReviewState.voiceRuntime = (data.voice_runtime && typeof data.voice_runtime === "object")
      ? { ...data.voice_runtime }
      : trustReviewState.voiceRuntime;
    if (!trustReviewState.selectedActivityKey && trustReviewState.activity.length) {
      const first = trustReviewState.activity[0];
      trustReviewState.selectedActivityKey = String(first.request_id || first.ledger_ref || first.title || "0").trim();
    }
    if (!trustReviewState.selectedBlockedKey && trustReviewState.blocked.length) {
      const firstBlocked = trustReviewState.blocked[0];
      trustReviewState.selectedBlockedKey = String(firstBlocked.label || firstBlocked.area || "0").trim();
    }
  }

  const mode = $("trust-mode");
  const lastCall = $("trust-last-call");
  const egress = $("trust-egress");
  const failure = $("trust-failure");
  const summary = $("trust-summary");
  const activityHost = $("trust-recent-activity");
  const blockedHost = $("trust-blocked");
  if (mode) mode.textContent = trustState.mode;
  if (lastCall) lastCall.textContent = trustState.lastExternalCall;
  if (egress) egress.textContent = trustState.dataEgress;
  if (failure) failure.textContent = trustState.failureState;
  if (summary) summary.textContent = trustReviewState.summary;

  if (activityHost) {
    clear(activityHost);
    const label = document.createElement("div");
    label.className = "trust-section-label";
    label.textContent = "Recent Activity";
    activityHost.appendChild(label);

    if (!trustReviewState.activity.length) {
      const empty = document.createElement("div");
      empty.className = "trust-empty";
      empty.textContent = "No recent ledger-backed activity yet.";
      activityHost.appendChild(empty);
    } else {
      const list = document.createElement("div");
      list.className = "trust-activity-list";
      trustReviewState.activity.slice(0, 6).forEach((item) => {
        const row = document.createElement("div");
        row.className = "trust-activity-item";
        const outcome = String(item.outcome || "").trim().toLowerCase() || "info";
        row.dataset.outcome = outcome;

        const titleRow = document.createElement("div");
        titleRow.className = "trust-activity-title-row";

        if (outcome && outcome !== "info") {
          const badge = document.createElement("span");
          badge.className = `trust-activity-outcome trust-activity-outcome-${outcome}`;
          badge.textContent = outcome === "issue" ? "Needs attention" : "Success";
          titleRow.appendChild(badge);
        }

        const title = document.createElement("div");
        title.className = "trust-activity-title";
        title.textContent = String(item.title || "Runtime event").trim() || "Runtime event";
        titleRow.appendChild(title);
        row.appendChild(titleRow);

        const meta = document.createElement("div");
        meta.className = "trust-activity-meta";
        const kind = String(item.kind || "system").trim() || "system";
        const detail = String(item.detail || "").trim();
        const timestamp = String(item.timestamp || "").trim();
        meta.textContent = [kind, detail, timestamp].filter(Boolean).join(" - ");
        row.appendChild(meta);

        const reason = String(item.reason || "").trim();
        if (reason) {
          const reasonRow = document.createElement("div");
          reasonRow.className = "trust-activity-reason";
          reasonRow.textContent = `Why: ${reason}`;
          row.appendChild(reasonRow);
        }

        const effect = String(item.effect || "").trim();
        if (effect) {
          const effectRow = document.createElement("div");
          effectRow.className = "trust-activity-effect";
          effectRow.textContent = `Effect: ${effect}`;
          row.appendChild(effectRow);
        }

        const requestId = String(item.request_id || "").trim();
        if (requestId) {
          const requestRow = document.createElement("div");
          requestRow.className = "trust-activity-correlation";
          requestRow.textContent = `Request: ${requestId}`;
          row.appendChild(requestRow);
        }

        const ledgerRef = String(item.ledger_ref || "").trim();
        if (ledgerRef) {
          const ledgerRow = document.createElement("div");
          ledgerRow.className = "trust-activity-correlation";
          ledgerRow.textContent = `Ledger: ${ledgerRef}`;
          row.appendChild(ledgerRow);
        }

        list.appendChild(row);
      });
      activityHost.appendChild(list);
    }
  }

  if (blockedHost) {
    clear(blockedHost);
    const label = document.createElement("div");
    label.className = "trust-section-label";
    label.textContent = "Currently Blocked";
    blockedHost.appendChild(label);

    if (!trustReviewState.blocked.length) {
      const empty = document.createElement("div");
      empty.className = "trust-empty";
      empty.textContent = "No blocked conditions reported.";
      blockedHost.appendChild(empty);
    } else {
      const list = document.createElement("div");
      list.className = "trust-activity-list";
      trustReviewState.blocked.slice(0, 3).forEach((item) => {
        const row = document.createElement("div");
        row.className = "trust-activity-item";

        const title = document.createElement("div");
        title.className = "trust-activity-title";
        title.textContent = `${String(item.label || item.area || "Condition").trim()}: ${String(item.status || "unknown").trim()}`;
        row.appendChild(title);

        const reason = document.createElement("div");
        reason.className = "trust-activity-meta";
        reason.textContent = String(item.reason || "").trim() || "No reason available.";
        row.appendChild(reason);

        list.appendChild(row);
      });
      blockedHost.appendChild(list);
    }
  }

  requestWorkspaceHomeRefresh();
  renderTrustCenterPage();
  renderSettingsPage();
}

function renderTrustCenterPage() {
  const summary = $("trust-center-summary");
  const mode = $("trust-center-mode");
  const lastCall = $("trust-center-last-call");
  const egress = $("trust-center-egress");
  const failure = $("trust-center-failure");
  const activityHost = $("trust-center-activity");
  const activityDetail = $("trust-center-activity-detail");
  const blockedHost = $("trust-center-blocked");
  const blockedDetail = $("trust-center-blocked-detail");
  const healthSummary = $("trust-center-health-summary");
  const healthGrid = $("trust-center-health-grid");
  const capabilitySummary = $("trust-center-capability-summary");
  const capabilityHost = $("trust-center-capability-groups");
  const voiceSummary = $("trust-center-voice-summary");
  const voiceGrid = $("trust-center-voice-grid");
  if (!summary || !mode || !lastCall || !egress || !failure || !activityHost || !blockedHost || !healthSummary || !healthGrid || !capabilitySummary || !capabilityHost) return;

  summary.textContent = trustReviewState.summary || "Trust review keeps recent governed actions, blocked conditions, and failure state in one place.";
  mode.textContent = trustState.mode || "Local-only";
  lastCall.textContent = trustState.lastExternalCall || "None";
  egress.textContent = trustState.dataEgress || "Read-only requests only";
  failure.textContent = trustState.failureState || "Normal";

  clear(activityHost);
  if (!trustReviewState.activity.length) {
    const empty = document.createElement("div");
    empty.className = "trust-empty";
    empty.textContent = "Recent governed actions will appear here as Nova works.";
    activityHost.appendChild(empty);
  } else {
    trustReviewState.activity.slice(0, 12).forEach((item, index) => {
      const key = String(item.request_id || item.ledger_ref || item.title || index).trim();
      const row = document.createElement("button");
      row.type = "button";
      row.className = "trust-activity-item";
      if (trustReviewState.selectedActivityKey === key) row.classList.add("active");
      row.dataset.outcome = String(item.outcome || "").trim().toLowerCase() || "info";
      row.addEventListener("click", () => {
        trustReviewState.selectedActivityKey = key;
        renderTrustCenterPage();
      });

      const title = document.createElement("div");
      title.className = "trust-activity-title";
      title.textContent = String(item.title || "Runtime event").trim() || "Runtime event";
      row.appendChild(title);

      const meta = document.createElement("div");
      meta.className = "trust-activity-meta";
      meta.textContent = [
        String(item.kind || "").trim(),
        String(item.timestamp || "").trim(),
      ].filter(Boolean).join(" · ") || "Ledger-backed runtime activity";
      row.appendChild(meta);

      const detail = String(item.detail || "").trim();
      if (detail) {
        const detailRow = document.createElement("div");
        detailRow.className = "trust-activity-reason";
        detailRow.textContent = detail;
        row.appendChild(detailRow);
      }

      activityHost.appendChild(row);
    });
  }

  if (activityDetail) {
    clear(activityDetail);
    const selected = trustReviewState.activity.find((item, index) => {
      const key = String(item.request_id || item.ledger_ref || item.title || index).trim();
      return key === trustReviewState.selectedActivityKey;
    }) || trustReviewState.activity[0];

    if (!selected) {
      const empty = document.createElement("div");
      empty.className = "trust-empty";
      empty.textContent = "Select a governed action to see why it happened and what effect it had.";
      activityDetail.appendChild(empty);
    } else {
      [
        ["Title", String(selected.title || "Runtime event").trim() || "Runtime event"],
        ["Kind", String(selected.kind || "system").trim() || "system"],
        ["When", String(selected.timestamp || "Unknown").trim() || "Unknown"],
        ["Why", String(selected.reason || selected.detail || "No reason recorded.").trim() || "No reason recorded."],
        ["Effect", String(selected.effect || "No external effect").trim() || "No external effect"],
        ["Request", String(selected.request_id || "Not recorded").trim() || "Not recorded"],
        ["Ledger", String(selected.ledger_ref || "Not recorded").trim() || "Not recorded"],
      ].forEach(([label, value]) => {
        const row = document.createElement("div");
        row.className = "operator-health-row";

        const labelEl = document.createElement("div");
        labelEl.className = "operator-health-label";
        labelEl.textContent = label;
        row.appendChild(labelEl);

        const valueEl = document.createElement("div");
        valueEl.className = "operator-health-value";
        valueEl.textContent = value;
        row.appendChild(valueEl);

        activityDetail.appendChild(row);
      });
    }
  }

  clear(blockedHost);
  if (!trustReviewState.blocked.length) {
    const empty = document.createElement("div");
    empty.className = "trust-empty";
    empty.textContent = "No blocked conditions are active right now.";
    blockedHost.appendChild(empty);
  } else {
    trustReviewState.blocked.slice(0, 8).forEach((item, index) => {
      const key = String(item.label || item.area || index).trim();
      const row = document.createElement("button");
      row.type = "button";
      row.className = "trust-activity-item";
      if (trustReviewState.selectedBlockedKey === key) row.classList.add("active");
      row.addEventListener("click", () => {
        trustReviewState.selectedBlockedKey = key;
        renderTrustCenterPage();
      });

      const title = document.createElement("div");
      title.className = "trust-activity-title";
      title.textContent = `${String(item.label || item.area || "Condition").trim()}: ${String(item.status || "unknown").trim()}`;
      row.appendChild(title);

      const copy = document.createElement("div");
      copy.className = "trust-activity-meta";
      copy.textContent = String(item.reason || "").trim() || "No reason available.";
      row.appendChild(copy);

      blockedHost.appendChild(row);
    });
  }

  if (blockedDetail) {
    clear(blockedDetail);
    const selectedBlocked = trustReviewState.blocked.find((item, index) => {
      const key = String(item.label || item.area || index).trim();
      return key === trustReviewState.selectedBlockedKey;
    }) || trustReviewState.blocked[0];

    if (!selectedBlocked) {
      const empty = document.createElement("div");
      empty.className = "trust-empty";
      empty.textContent = "Select a blocked condition to see what boundary Nova is honoring.";
      blockedDetail.appendChild(empty);
    } else {
      [
        ["Boundary", String(selectedBlocked.label || selectedBlocked.area || "Condition").trim() || "Condition"],
        ["Status", String(selectedBlocked.status || "unknown").trim() || "unknown"],
        ["Why blocked", String(selectedBlocked.reason || "No reason available.").trim() || "No reason available."],
      ].forEach(([label, value]) => {
        const row = document.createElement("div");
        row.className = "operator-health-row";

        const labelEl = document.createElement("div");
        labelEl.className = "operator-health-label";
        labelEl.textContent = label;
        row.appendChild(labelEl);

        const valueEl = document.createElement("div");
        valueEl.className = "operator-health-value";
        valueEl.textContent = value;
        row.appendChild(valueEl);

        blockedDetail.appendChild(row);
      });
    }
  }

  healthSummary.textContent = operatorHealthState.summary || "Loading runtime health...";
  clear(healthGrid);
  [
    ["Governor", String((operatorHealthState.snapshot && operatorHealthState.snapshot.governor_status) || "Unknown")],
    ["Boundary", String((operatorHealthState.snapshot && operatorHealthState.snapshot.execution_boundary_status) || "Unknown")],
    ["Network", String((operatorHealthState.snapshot && operatorHealthState.snapshot.network_mediator_status) || "Unknown")],
    ["Voice", String((operatorHealthState.snapshot && operatorHealthState.snapshot.voice_status) || "Unknown")],
    ["Memory", String((operatorHealthState.snapshot && operatorHealthState.snapshot.memory_summary) || (operatorHealthState.snapshot && operatorHealthState.snapshot.memory_status) || "Unknown")],
    ["Model", String((operatorHealthState.snapshot && operatorHealthState.snapshot.model_availability) || "Unknown")],
  ].forEach(([label, value]) => {
    healthGrid.appendChild(createOverviewChip(label, value));
  });

  capabilitySummary.textContent = capabilityDiscoveryState.summary || "Loading live capabilities...";
  clear(capabilityHost);
  const groups = Array.isArray(capabilityDiscoveryState.snapshot && capabilityDiscoveryState.snapshot.available_capability_surface)
    ? capabilityDiscoveryState.snapshot.available_capability_surface
    : [];
  if (!groups.length) {
    const empty = document.createElement("div");
    empty.className = "trust-empty";
    empty.textContent = "Capability groups will appear here after the next runtime refresh.";
    capabilityHost.appendChild(empty);
  } else {
    groups.slice(0, 4).forEach((group) => {
      const card = document.createElement("div");
      card.className = "workspace-spotlight-card";

      const title = document.createElement("div");
      title.className = "workspace-spotlight-title";
      title.textContent = String(group.label || group.category || "Capability group").trim();
      card.appendChild(title);

      const copy = document.createElement("div");
      copy.className = "workspace-spotlight-copy";
      const entries = Array.isArray(group.items)
        ? group.items.slice(0, 4).map((item) => String(item.action || item.label || item.name || "").trim()).filter(Boolean)
        : [];
      copy.textContent = entries.length ? entries.join(" · ") : "Live governed actions appear here.";
      card.appendChild(copy);

      capabilityHost.appendChild(card);
    });
  }

  if (voiceSummary && voiceGrid) {
    const voice = (trustReviewState.voiceRuntime && typeof trustReviewState.voiceRuntime === "object")
      ? trustReviewState.voiceRuntime
      : {};
    voiceSummary.textContent = [
      String(voice.summary || "").trim(),
      String(voice.last_status || voice.last_attempt_status || "").trim(),
    ].filter(Boolean).join(" · ") || "Voice status will appear here after the next trust refresh.";

    clear(voiceGrid);
    [
      ["Preferred", String(voice.preferred_engine || "Piper").trim() || "Piper"],
      ["Preferred status", String(voice.preferred_status || "Unknown").trim() || "Unknown"],
      ["Fallback", String(voice.fallback_engine || "pyttsx3").trim() || "pyttsx3"],
      ["Fallback status", String(voice.fallback_status || "Unknown").trim() || "Unknown"],
      ["Last attempt", String(voice.last_attempt_status || "No voice check yet").trim() || "No voice check yet"],
      ["Last engine", String(voice.last_engine || "None").trim() || "None"],
    ].forEach(([label, value]) => {
      voiceGrid.appendChild(createOverviewChip(label, value));
    });
  }
}

function markExternalCall(label) {
  const now = new Date();
  const ts = now.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  trustState.mode = "Online";
  trustState.lastExternalCall = `${label} at ${ts}`;
  trustState.dataEgress = "Read-only external request";
  trustState.consecutiveFailures = 0;
  trustState.failureState = "Normal";
  renderTrustPanel();
}

function markLocalMode() {
  if (trustState.mode !== "Online") {
    trustState.mode = "Local-only";
    trustState.dataEgress = "No external call in this step";
    renderTrustPanel();
  }
}

function markFailure(reason = "Temporary issue") {
  trustState.consecutiveFailures += 1;
  if (trustState.consecutiveFailures >= 3) {
    trustState.failureState = "Offline-safe mode";
    trustState.mode = "Local-only";
    trustState.dataEgress = "External calls paused after repeated failures";
  } else if (trustState.consecutiveFailures >= 2) {
    trustState.failureState = "Degraded";
  } else {
    trustState.failureState = reason;
  }
  renderTrustPanel();
}

function markRecovered() {
  if (trustState.consecutiveFailures > 0) {
    trustState.consecutiveFailures = 0;
    trustState.failureState = "Recovered";
    renderTrustPanel();
    setTimeout(() => {
      trustState.failureState = "Normal";
      renderTrustPanel();
    }, 1500);
  }
}

function maybeMarkReactiveFailureFromText(text) {
  const msg = (text || "").toLowerCase();
  const failed = (
    msg.includes("timed out") ||
    msg.includes("temporarily unavailable") ||
    msg.includes("network issue") ||
    msg.includes("couldn't complete") ||
    msg.includes("can't do that right now")
  );
  if (failed) {
    markFailure("Temporary issue");
  }
}

function getActivePage() {
  const stored = localStorage.getItem(STORAGE_KEYS.activePage) || "chat";
  return QUICK_ACTIONS_BY_PAGE[stored] ? stored : "chat";
}

function getQuickActionsForPage(page = getActivePage()) {
  return QUICK_ACTIONS_BY_PAGE[page] || QUICK_ACTIONS_BY_PAGE.chat;
}

function quickActionsStorageKey(page) {
  return `${STORAGE_KEYS.quickActions}_${page}`;
}

function getSelectedQuickActions(page = getActivePage(), actions = getQuickActionsForPage(page)) {
  const validIds = new Set((actions || []).map((action) => action.id));
  try {
    const stored = JSON.parse(localStorage.getItem(quickActionsStorageKey(page)) || "[]");
    if (Array.isArray(stored) && stored.length) {
      const filtered = stored.filter((id) => validIds.has(id));
      if (filtered.length) return filtered;
    }
  } catch (_) {}
  return (actions || []).map((a) => a.id);
}

function saveSelectedQuickActions(page, ids) {
  localStorage.setItem(quickActionsStorageKey(page), JSON.stringify(ids));
}

function isHintsExpanded() {
  return localStorage.getItem(STORAGE_KEYS.hintsExpanded) === "1";
}

function setHintsExpanded(expanded) {
  localStorage.setItem(STORAGE_KEYS.hintsExpanded, expanded ? "1" : "0");
}

function applyHintsPanelState() {
  const host = $("quick-actions");
  const toggle = $("btn-hints-toggle");
  const expanded = isHintsExpanded();
  if (host) host.hidden = !expanded;
  if (toggle) {
    toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
    toggle.textContent = expanded ? "Hide ideas" : "Need ideas?";
  }
}

function setupHintsPanelToggle() {
  const toggle = $("btn-hints-toggle");
  if (!toggle || toggle.dataset.bound === "1") {
    applyHintsPanelState();
    return;
  }

  toggle.dataset.bound = "1";
  toggle.addEventListener("click", () => {
    const next = !isHintsExpanded();
    setHintsExpanded(next);
    applyHintsPanelState();
  });
  applyHintsPanelState();
}

function runQuickAction(action, page = getActivePage()) {
  const input = $("chat-input");
  const found = getQuickActionsForPage(page).find((a) => a.id === action);
  if (!found) return;

  if (found.switchToPage) {
    setActivePage(found.switchToPage);
  } else if (!found.stayOnPage && page !== "chat") {
    setActivePage("chat");
  }

  if (found.prefill) {
    if (input) {
      input.focus();
      input.value = found.command;
    }
    return;
  }

  injectUserText(found.command, "text");
}

function renderQuickActions() {
  const host = $("quick-actions");
  if (!host) return;
  clear(host);

  const page = getActivePage();
  const actions = getQuickActionsForPage(page);
  const selected = new Set(getSelectedQuickActions(page, actions));
  actions.filter((a) => selected.has(a.id)).forEach((action) => {
    const btn = document.createElement("button");
    btn.className = "quick-action-btn";
    btn.type = "button";
    btn.dataset.action = action.id;
    btn.textContent = action.label;
    btn.addEventListener("click", () => runQuickAction(action.id, page));
    host.appendChild(btn);
  });

  const copy = document.querySelector(".hints-copy");
  if (copy) {
    const hintText = {
      chat: "Starter prompts for everyday chat and explain mode.",
      news: "News actions for summaries, comparisons, and context checks.",
      intro: "Use Intro to understand how Nova works before you start leaning on it.",
      home: "Status checks, explain actions, and project continuity threads.",
      workspace: "Workspace keeps project continuity, structure, and recent decisions together.",
      memory: "Memory stays explicit, inspectable, and revocable.",
      trust: "Trust keeps recent actions, boundaries, and runtime health visible.",
      settings: "Settings keeps setup choices, voice checks, and comfort controls in one place.",
    };
    copy.textContent = hintText[page] || hintText.chat;
  }

  const customize = document.createElement("button");
  customize.className = "quick-action-btn ghost";
  customize.type = "button";
  customize.id = "btn-quick-customize";
  customize.textContent = "Choose";
  customize.addEventListener("click", showQuickCustomizeModal);
  host.appendChild(customize);
  applyHintsPanelState();
}

function appendConfidenceBadge(container, label) {
  const badge = document.createElement("span");
  badge.className = "confidence-badge";
  badge.textContent = label;
  container.appendChild(badge);
}

function deriveSourceCount(text) {
  const raw = String(text || "");
  const explicit = /Sources used:\s*(\d+)/i.exec(raw);
  if (explicit) return Number(explicit[1]) || 0;

  const lines = raw.split(/\r?\n/);
  const sourceLines = lines.filter((line) => /^\s*\d+\.\s+/.test(line) || /^\s*-\s+[a-z0-9.-]+\.[a-z]{2,}/i.test(line));
  return sourceLines.length;
}

function appendTrustStrip(container, text, confidenceLabel = "") {
  const strip = document.createElement("div");
  strip.className = "message-trust-strip";

  const mode = trustState.mode || "Local-only";
  const sourceCount = deriveSourceCount(text);
  const confidence = String(confidenceLabel || "").trim() || "Standard";
  const parts = [
    `Mode: ${mode}`,
    `Sources: ${sourceCount > 0 ? sourceCount : "n/a"}`,
    `Confidence: ${confidence}`,
  ];
  strip.textContent = parts.join(" | ");
  container.appendChild(strip);
}

function shouldCollapseMessage(text) {
  const raw = String(text || "");
  if (!raw.trim()) return false;
  if (/https?:\/\/\S+/i.test(raw)) return false;
  const lines = raw.split(/\r?\n/).filter((line) => line.trim().length > 0);
  return raw.length > LONG_MESSAGE_CHAR_LIMIT || lines.length > LONG_MESSAGE_LINE_LIMIT;
}

function buildMessagePreview(text) {
  const raw = String(text || "").trim();
  if (!raw) return "";

  const paragraphLines = raw.split(/\r?\n/).filter((line) => line.trim().length > 0);
  if (paragraphLines.length > 1) {
    const previewLines = paragraphLines.slice(0, 2).join("\n");
    if (previewLines.length > LONG_MESSAGE_CHAR_LIMIT) {
      return `${previewLines.slice(0, LONG_MESSAGE_CHAR_LIMIT - 3).trimEnd()}...`;
    }
    return `${previewLines.trimEnd()}...`;
  }

  const normalized = raw.replace(/\s+/g, " ").trim();
  const sentences = normalized.split(/(?<=[.!?])\s+/).filter(Boolean);
  const shortBySentence = sentences.slice(0, LONG_MESSAGE_SENTENCE_LIMIT).join(" ").trim();
  if (shortBySentence && shortBySentence.length >= 60) {
    if (shortBySentence.length > LONG_MESSAGE_CHAR_LIMIT) {
      return `${shortBySentence.slice(0, LONG_MESSAGE_CHAR_LIMIT - 3).trimEnd()}...`;
    }
    return shortBySentence.endsWith("...") ? shortBySentence : `${shortBySentence}...`;
  }

  return `${normalized.slice(0, LONG_MESSAGE_CHAR_LIMIT - 3).trimEnd()}...`;
}

function summarizeSentence(text, maxLength = 140) {
  const normalized = String(text || "").replace(/\s+/g, " ").trim();
  if (!normalized) return "";

  const firstSentence = normalized.split(/(?<=[.!?])\s+/).filter(Boolean)[0] || normalized;
  if (firstSentence.length <= maxLength) {
    return firstSentence;
  }
  return `${firstSentence.slice(0, maxLength - 3).trimEnd()}...`;
}

function appendLinkedText(container, text) {
  const raw = String(text || "");
  const lines = raw.split(/\r?\n/);

  lines.forEach((line, lineIndex) => {
    URL_PATTERN.lastIndex = 0;
    let cursor = 0;
    let match = URL_PATTERN.exec(line);

    if (!match) {
      container.appendChild(document.createTextNode(line));
    } else {
      while (match) {
        const url = match[0];
        const start = match.index;
        if (start > cursor) {
          container.appendChild(document.createTextNode(line.slice(cursor, start)));
        }
        const link = document.createElement("a");
        link.href = url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = url;
        link.className = "chat-inline-link";
        container.appendChild(link);
        cursor = start + url.length;
        match = URL_PATTERN.exec(line);
      }
      if (cursor < line.length) {
        container.appendChild(document.createTextNode(line.slice(cursor)));
      }
    }

    if (lineIndex < lines.length - 1) {
      container.appendChild(document.createElement("br"));
    }
  });
}

function parseStructuredReport(text) {
  const raw = String(text || "").trim();
  if (!raw) return null;

  const isReport =
    raw.startsWith("NOVA MULTI-SOURCE REPORT") ||
    raw.startsWith("NOVA INTELLIGENCE BRIEF");
  if (!isReport) return null;

  const lines = raw.split(/\r?\n/);
  const title = lines[0].trim();
  const sections = [];
  let current = null;

  const sectionHeaders = new Set([
    "Summary",
    "Key Findings",
    "Supporting Sources",
    "Contradictions",
    "Strategic Snapshot",
    "Top Findings",
    "Cross-Story Insight",
    "Cross-Story Insights",
    "Sources",
    "Confidence",
    "Source Credibility",
    "Confidence Factors",
    "Counter Analysis",
    "Narrative Threads",
    "Topic Clusters",
    "Detailed Story Briefs",
    "Analyst Note",
  ]);

  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i].trim();
    if (!line || /^-+$/.test(line)) continue;
    if (sectionHeaders.has(line)) {
      if (current) sections.push(current);
      current = { heading: line, rows: [] };
      continue;
    }
    if (!current) {
      current = { heading: "Overview", rows: [] };
    }
    current.rows.push(line);
  }
  if (current) sections.push(current);
  return { title, sections };
}

function collectReportSources(report) {
  const sourceHeadings = new Set(["Sources", "Supporting Sources", "Source Credibility"]);
  const rows = [];
  (report.sections || []).forEach((section) => {
    if (!section || !sourceHeadings.has(section.heading)) return;
    (section.rows || []).forEach((row) => {
      const clean = String(row || "").trim();
      if (!clean) return;
      rows.push(clean.replace(/^\d+\.\s+/, "").replace(/^-\s+/, ""));
    });
  });
  return Array.from(new Set(rows)).slice(0, 12);
}

function parseDailyBriefV2(text) {
  const raw = String(text || "").trim();
  if (!raw.startsWith("NOVA DAILY INTELLIGENCE BRIEF")) return null;

  const lines = raw.split(/\r?\n/).map((line) => line.trim());
  const stories = [];
  let current = null;
  let confidence = "";
  let sourcesUsed = "";
  let coverage = "";

  lines.forEach((line) => {
    if (!line) return;
    const storyMatch = /^Story\s+(\d+):\s+(.+)$/i.exec(line);
    if (storyMatch) {
      if (current) stories.push(current);
      current = {
        id: Number(storyMatch[1]),
        title: storyMatch[2].trim(),
        summary: "",
        implication: "",
        sources: "",
      };
      return;
    }

    if (current && line.startsWith("Summary:")) {
      current.summary = line.replace(/^Summary:\s*/i, "").trim();
      return;
    }
    if (current && line.startsWith("Implication:")) {
      current.implication = line.replace(/^Implication:\s*/i, "").trim();
      return;
    }
    if (current && line.startsWith("Sources:")) {
      current.sources = line.replace(/^Sources:\s*/i, "").trim();
      return;
    }

    if (line.startsWith("Confidence:")) {
      confidence = line.replace(/^Confidence:\s*/i, "").trim();
      return;
    }
    if (line.startsWith("Sources used:")) {
      sourcesUsed = line.replace(/^Sources used:\s*/i, "").trim();
      return;
    }
    if (line.startsWith("Coverage:")) {
      coverage = line.replace(/^Coverage:\s*/i, "").trim();
    }
  });
  if (current) stories.push(current);
  if (!stories.length) return null;

  return { title: "Today's Intelligence Brief", stories, confidence, sourcesUsed, coverage };
}

function normalizeBriefWidgetData(data = {}) {
  const toCount = (value) => {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return 0;
    return Math.max(0, Math.trunc(numeric));
  };

  return {
    headlineCount: toCount(data.headline_count),
    sourcePagesRead: toCount(data.source_pages_read),
    clusterCount: toCount(data.cluster_count),
    placeholderClusterCount: toCount(data.placeholder_cluster_count),
    omittedClusterCount: toCount(data.omitted_cluster_count),
  };
}

function createBriefStat(label, value) {
  const stat = document.createElement("div");
  stat.className = "brief-status-stat";

  const statLabel = document.createElement("div");
  statLabel.className = "brief-status-label";
  statLabel.textContent = label;
  stat.appendChild(statLabel);

  const statValue = document.createElement("div");
  statValue.className = "brief-status-value";
  statValue.textContent = String(value);
  stat.appendChild(statValue);

  return stat;
}

function renderIntelligenceBriefWidget(data = {}) {
  if (data && typeof data === "object" && Object.keys(data).length > 0) {
    latestBriefWidgetState = {
      ...latestBriefWidgetState,
      ...normalizeBriefWidgetData(data),
    };
  }

  const badge = $("brief-grounding-badge");
  const summary = $("brief-summary");
  const stats = $("brief-stats");
  const note = $("brief-grounding-note");
  if (!badge || !summary || !stats || !note) return;

  clear(stats);

  const state = latestBriefWidgetState;
  const hasBrief = state.headlineCount > 0 || state.sourcePagesRead > 0 || state.clusterCount > 0;
  if (!hasBrief) {
    badge.textContent = "Awaiting brief";
    summary.textContent = "Run a daily brief or source-grounded brief to pin the latest briefing status here.";
    note.textContent = "This panel will distinguish headline-only, grounded, and degraded placeholder brief states.";
    return;
  }

  let badgeText = "Headline";
  let summaryText = `Latest daily brief used ${state.headlineCount} headline(s).`;
  let noteText = "This path is headline-grounded, not source-page-grounded.";
  let pageSummaryText = "Latest daily brief is ready. This pass is headline-grounded only.";

  if (state.sourcePagesRead > 0) {
    badgeText = "Grounded";
    summaryText = `Latest source-grounded brief used ${state.sourcePagesRead} source page(s) across ${state.clusterCount || 0} topic cluster(s).`;
    noteText = "Story cards below reflect the latest brief captured in chat.";
    pageSummaryText = "Latest source-grounded brief is ready.";

    if (state.placeholderClusterCount > 0) {
      badgeText = "Degraded";
      summaryText = `${summaryText} ${state.placeholderClusterCount} cluster(s) are placeholder summaries.`;
      noteText = "Placeholder summaries appear when source-grounded synthesis is unavailable, but source coverage is still shown.";
      pageSummaryText = "Latest source-grounded brief is usable, but placeholder summaries are in use.";
    } else if (state.omittedClusterCount > 0) {
      badgeText = "Partial";
      noteText = `${state.omittedClusterCount} topic cluster(s) were omitted due to incomplete source-grounded synthesis.`;
      pageSummaryText = "Latest source-grounded brief is partial because some topic clusters were omitted.";
    }
  }

  badge.textContent = badgeText;
  summary.textContent = summaryText;
  note.textContent = noteText;
  updateNewsSummary(pageSummaryText);

  [
    ["Headlines", state.headlineCount],
    ["Source pages", state.sourcePagesRead],
    ["Clusters", state.clusterCount],
    ["Placeholder", state.placeholderClusterCount],
    ["Omitted", state.omittedClusterCount],
  ].forEach(([label, value]) => {
    stats.appendChild(createBriefStat(label, value));
  });
}

function createBriefCardElement(story, compact = false) {
  const card = document.createElement("div");
  card.className = "brief-card";

  const heading = document.createElement("div");
  heading.className = "brief-card-heading";
  heading.textContent = `Story ${story.id} - ${story.title}`;
  card.appendChild(heading);

  const summary = document.createElement("div");
  summary.className = "brief-card-row";
  summary.textContent = `Summary: ${story.summary || "No summary available."}`;
  card.appendChild(summary);

  const implication = document.createElement("div");
  implication.className = "brief-card-row";
  implication.textContent = `Implication: ${story.implication || "No implication provided."}`;
  card.appendChild(implication);

  const sources = document.createElement("div");
  sources.className = "brief-card-row brief-card-sources";
  sources.textContent = `Sources: ${story.sources || "Unknown"}`;
  card.appendChild(sources);

  const actions = document.createElement("div");
  actions.className = "brief-card-actions";
  const expand = document.createElement("button");
  expand.type = "button";
  expand.className = "assistant-action-btn";
  expand.textContent = "Expand";
  expand.addEventListener("click", () => injectUserText(`expand story ${story.id}`, "text"));
  actions.appendChild(expand);

  const track = document.createElement("button");
  track.type = "button";
  track.className = "assistant-action-btn";
  track.textContent = "Track";
  track.addEventListener("click", () => injectUserText(`track story ${story.id}`, "text"));
  actions.appendChild(track);

  const compare = document.createElement("button");
  compare.type = "button";
  compare.className = "assistant-action-btn";
  compare.textContent = "Compare";
  const compareTarget = story.id === 1 ? 2 : 1;
  compare.addEventListener("click", () => injectUserText(`compare ${story.id} and ${compareTarget}`, "text"));
  actions.appendChild(compare);

  card.appendChild(actions);
  if (compact) {
    card.classList.add("brief-card-compact");
  }
  return card;
}

function renderSidebarBrief(brief) {
  const empty = $("brief-sidebar-empty");
  const cards = $("brief-sidebar-cards");
  if (!cards) return;
  clear(cards);

  if (!brief || !Array.isArray(brief.stories) || brief.stories.length === 0) {
    if (empty) empty.style.display = "block";
    return;
  }

  if (empty) empty.style.display = "none";
  brief.stories.slice(0, 4).forEach((story) => {
    cards.appendChild(createBriefCardElement(story, true));
  });
}

function renderDailyBriefV2(container, brief) {
  const wrap = document.createElement("div");
  wrap.className = "daily-brief";

  const title = document.createElement("div");
  title.className = "daily-brief-title";
  title.textContent = brief.title;
  wrap.appendChild(title);

  brief.stories.forEach((story) => {
    wrap.appendChild(createBriefCardElement(story, false));
  });

  const meta = document.createElement("div");
  meta.className = "daily-brief-meta";
  meta.textContent = `Confidence: ${brief.confidence || "Medium"} | Sources used: ${brief.sourcesUsed || "N/A"} | Coverage: ${brief.coverage || "General"}`;
  wrap.appendChild(meta);

  container.appendChild(wrap);
  renderSidebarBrief(brief);
}

function renderStructuredReport(container, report) {
  const wrap = document.createElement("div");
  wrap.className = "structured-report";

  const title = document.createElement("div");
  title.className = "structured-report-title";
  title.textContent = report.title;
  wrap.appendChild(title);

  const actions = document.createElement("div");
  actions.className = "structured-report-actions";

  const copyBtn = document.createElement("button");
  copyBtn.type = "button";
  copyBtn.className = "assistant-action-btn";
  copyBtn.textContent = "Copy sources";
  copyBtn.addEventListener("click", async () => {
    const sources = collectReportSources(report);
    if (!sources.length) {
      copyBtn.textContent = "No sources";
      setTimeout(() => { copyBtn.textContent = "Copy sources"; }, 1200);
      return;
    }
    try {
      await navigator.clipboard.writeText(sources.join("\n"));
      copyBtn.textContent = "Copied";
    } catch (_) {
      copyBtn.textContent = "Copy failed";
    }
    setTimeout(() => { copyBtn.textContent = "Copy sources"; }, 1200);
  });
  actions.appendChild(copyBtn);

  const followupBtn = document.createElement("button");
  followupBtn.type = "button";
  followupBtn.className = "assistant-action-btn";
  followupBtn.textContent = "Follow-up analysis";
  followupBtn.addEventListener("click", () => {
    injectUserText("phase42: follow up on this report with deeper analysis", "text");
  });
  actions.appendChild(followupBtn);
  wrap.appendChild(actions);

  report.sections.forEach((section) => {
    const card = document.createElement("div");
    card.className = "structured-section";

    const header = document.createElement("div");
    header.className = "structured-section-header";

    const h = document.createElement("div");
    h.className = "structured-section-heading";
    h.textContent = section.heading;
    header.appendChild(h);

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "structured-section-toggle";
    toggle.textContent = "Collapse";
    toggle.setAttribute("aria-expanded", "true");
    header.appendChild(toggle);
    card.appendChild(header);

    const list = document.createElement("div");
    list.className = "structured-section-body";
    section.rows.forEach((row) => {
      const p = document.createElement("div");
      p.className = "structured-row";
      p.textContent = row;
      list.appendChild(p);
    });
    toggle.addEventListener("click", () => {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      list.hidden = expanded;
      toggle.setAttribute("aria-expanded", expanded ? "false" : "true");
      toggle.textContent = expanded ? "Expand" : "Collapse";
    });
    card.appendChild(list);
    wrap.appendChild(card);
  });

  container.appendChild(wrap);
}

function isOperationalMessage(text) {
  const msg = (text || "").toLowerCase();
  return (
    msg.includes("opened ") ||
    msg.includes("opened path:") ||
    msg.includes("system diagnostics") ||
    msg.includes("system status") ||
    msg.includes("volume ")
  );
}

function deriveSuggestedActions(text) {
  const msg = (text || "").toLowerCase();

  if (!msg.trim()) return [];
  if (isOperationalMessage(text)) return [];

  if (msg.includes("not sure what you'd like me to do") || msg.includes("could you clarify")) {
    return [
      { label: "Today's brief", command: "daily brief" },
      { label: "Weather", command: "weather" },
      { label: "Open documents", command: "open documents" },
    ];
  }

  if (msg.includes("intelligence brief") || msg.includes("daily situation overview") || msg.includes("executive brief")) {
    return [
      { label: "Summarize in bullets", command: "summarize this brief in 3 bullets" },
      { label: "Expand story 1", command: "expand story 1" },
    ];
  }

  if (msg.includes("weather")) {
    return [
      { label: "Forecast", command: "show weather forecast" },
      { label: "Today's brief", command: "daily brief" },
    ];
  }

  if (msg.includes("news") || msg.includes("headline")) {
    return [
      { label: "Summarize all", command: "summarize all headlines" },
      { label: "Today's brief", command: "daily brief" },
    ];
  }

  return [];
}

function renderSuggestedActions(parent, suggestions) {
  if (!Array.isArray(suggestions) || suggestions.length === 0) return;

  const row = document.createElement("div");
  row.className = "assistant-actions";

  suggestions.slice(0, 3).forEach((item) => {
    if (!item || !item.command || !item.label) return;
    const b = document.createElement("button");
    b.type = "button";
    b.className = "assistant-action-btn";
    b.textContent = item.label;
    b.addEventListener("click", () => injectUserText(item.command, "text"));
    row.appendChild(b);
  });

  if (row.childElementCount > 0) {
    parent.appendChild(row);
  }
}

function ensurePinnedSection(chat) {
  let section = $("pinned-messages");
  if (section) return section;
  section = document.createElement("div");
  section.id = "pinned-messages";
  section.className = "pinned-messages";
  section.style.display = "none";
  chat.insertBefore(section, chat.firstChild);
  return section;
}

function refreshPinnedVisibility() {
  const section = $("pinned-messages");
  if (!section) return;
  section.style.display = section.childElementCount > 0 ? "block" : "none";
}

function addMessageUtilities(messageEl, text) {
  const row = document.createElement("div");
  row.className = "message-utilities";

  const copyBtn = document.createElement("button");
  copyBtn.type = "button";
  copyBtn.className = "message-utility-btn";
  copyBtn.textContent = "Copy";
  copyBtn.addEventListener("click", async () => {
    const payload = String(text || "").trim();
    if (!payload) return;
    try {
      await navigator.clipboard.writeText(payload);
      copyBtn.textContent = "Copied";
      setTimeout(() => { copyBtn.textContent = "Copy"; }, 1200);
    } catch (_) {
      copyBtn.textContent = "Copy failed";
      setTimeout(() => { copyBtn.textContent = "Copy"; }, 1200);
    }
  });
  row.appendChild(copyBtn);

  const pinBtn = document.createElement("button");
  pinBtn.type = "button";
  pinBtn.className = "message-utility-btn";
  pinBtn.textContent = "Pin";
  pinBtn.setAttribute("aria-pressed", "false");
  pinBtn.addEventListener("click", () => {
    const chat = $("chat-log");
    if (!chat) return;
    const pinnedSection = ensurePinnedSection(chat);
    const pinned = messageEl.dataset.pinned === "true";
    if (pinned) {
      messageEl.dataset.pinned = "false";
      messageEl.classList.remove("chat-pinned");
      pinBtn.textContent = "Pin";
      pinBtn.setAttribute("aria-pressed", "false");
      chat.appendChild(messageEl);
    } else {
      messageEl.dataset.pinned = "true";
      messageEl.classList.add("chat-pinned");
      pinBtn.textContent = "Unpin";
      pinBtn.setAttribute("aria-pressed", "true");
      pinnedSection.appendChild(messageEl);
    }
    refreshPinnedVisibility();
    chat.scrollTop = chat.scrollHeight;
  });
  row.appendChild(pinBtn);

  messageEl.appendChild(row);
}

function appendAssistantActions(parent, text, suggestedActions = null) {
  const operational = isOperationalMessage(text);
  const suggestions = Array.isArray(suggestedActions) && suggestedActions.length
    ? suggestedActions
    : deriveSuggestedActions(text);
  renderSuggestedActions(parent, suggestions);
  if (Array.isArray(suggestions) && suggestions.length) return;

  const message = String(text || "").trim();
  if (!message || operational) return;

  const row = document.createElement("div");
  row.className = "assistant-actions";
  let added = 0;

  if (message.length > 320) {
    const shortBtn = document.createElement("button");
    shortBtn.type = "button";
    shortBtn.className = "assistant-action-btn";
    shortBtn.textContent = "Shorter";
    shortBtn.addEventListener("click", () => injectUserText("Please give a shorter version of your last response.", "text"));
    row.appendChild(shortBtn);
    added += 1;
  }

  if (/source|reuters|bbc|ap|link|reference/i.test(message)) {
    const sourcesBtn = document.createElement("button");
    sourcesBtn.type = "button";
    sourcesBtn.className = "assistant-action-btn";
    sourcesBtn.textContent = "Show sources";
    sourcesBtn.addEventListener("click", () => injectUserText("Show sources for your last response.", "text"));
    row.appendChild(sourcesBtn);
    added += 1;
  }

  if (added > 0) {
    parent.appendChild(row);
  }
}

function appendChatMessage(role, text, messageId = null, confidence = "", suggestedActions = null) {
  const chat = $("chat-log");
  if (!chat) return;

  const msgText = String(text || "");
  if (role === "assistant" && msgText.trim() === "Hello. How can I help?") {
    const firstAssistant = chat.querySelector(".chat-assistant span");
    if (firstAssistant && firstAssistant.textContent.trim() === "Hello. How can I help?") {
      return;
    }
  }

  const div = document.createElement("div");
  div.className = `chat-${role}`;

  const dailyBrief = role === "assistant" ? parseDailyBriefV2(msgText) : null;
  const structured = role === "assistant" ? parseStructuredReport(msgText) : null;
  if (dailyBrief) {
    renderDailyBriefV2(div, dailyBrief);
  } else if (structured) {
    renderStructuredReport(div, structured);
  } else {
    const textNode = document.createElement("span");
    if (role === "assistant" && shouldCollapseMessage(msgText)) {
      const preview = buildMessagePreview(msgText);
      textNode.textContent = preview;
      textNode.dataset.fullText = msgText;
      textNode.dataset.previewText = preview;
      textNode.dataset.expanded = "false";
      div.appendChild(textNode);

      const expandBtn = document.createElement("button");
      expandBtn.type = "button";
      expandBtn.className = "message-expand-btn";
      expandBtn.textContent = "Show more";
      expandBtn.setAttribute("aria-expanded", "false");
      expandBtn.addEventListener("click", () => {
        const expanded = textNode.dataset.expanded === "true";
        textNode.textContent = expanded ? textNode.dataset.previewText : textNode.dataset.fullText;
        textNode.dataset.expanded = expanded ? "false" : "true";
        expandBtn.textContent = expanded ? "Show more" : "Show less";
        expandBtn.setAttribute("aria-expanded", expanded ? "false" : "true");
      });
      div.appendChild(expandBtn);
    } else {
      appendLinkedText(textNode, msgText);
      div.appendChild(textNode);
    }
  }

  if (confidence && role === "assistant") {
    appendConfidenceBadge(div, confidence);
  }
  if (role === "assistant") {
    appendTrustStrip(div, msgText, confidence);
  }

  if (role === "assistant" && messageId) {
    messageMeta.set(messageId, div);
    const thoughtBtn = document.createElement("button");
    thoughtBtn.className = "thought-indicator";
    thoughtBtn.type = "button";
    thoughtBtn.textContent = "i";
    thoughtBtn.title = "Show reasoning";
    thoughtBtn.addEventListener("click", () => {
      if (!messageId) return;
      if (!safeWSSend({ type: "get_thought", message_id: messageId })) return;
      pendingThoughtMessageId = messageId;
    });
    div.appendChild(thoughtBtn);
  }

  if (role === "assistant") {
    addMessageUtilities(div, msgText);
    appendAssistantActions(div, text || "", suggestedActions);
  }

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function appendPlainAssistantMessage(text) {
  const chat = $("chat-log");
  if (!chat) return;

  const div = document.createElement("div");
  div.className = "chat-assistant";
  const span = document.createElement("span");
  span.textContent = String(text || "");
  div.appendChild(span);
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function ensureSingleWelcomeMessage() {
  const chat = $("chat-log");
  if (!chat || chat.children.length > 0) return;
  appendPlainAssistantMessage("Hello. How can I help?");
}

function showThoughtOverlay(anchor, thoughtData) {
  let overlay = document.getElementById("thought-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "thought-overlay";
    overlay.className = "thought-overlay";
    document.body.appendChild(overlay);
  }

  const reasonSummary = String(thoughtData.reason_summary || "").trim();
  const reasons = (thoughtData.reason_codes || []).map((code) => `<li>${String(code).replace(/_/g, " ")}</li>`).join("");
  const mode = String(thoughtData.mode || "").trim();
  const tokens = Number(thoughtData.suggested_tokens || 0);
  const heuristic = thoughtData.heuristic || {};
  const complexity = Number(heuristic.complexity_score || 0);
  const depth = Number(heuristic.depth_opportunity_score || 0);
  const ambiguity = Number(heuristic.ambiguity_score || 0);
  const rows = [];

  if (mode) rows.push(`<li>Mode: ${mode}</li>`);
  if (tokens > 0) rows.push(`<li>Token budget: ${tokens}</li>`);
  if (complexity > 0) rows.push(`<li>Complexity score: ${complexity.toFixed(2)}</li>`);
  if (depth > 0) rows.push(`<li>Depth score: ${depth.toFixed(2)}</li>`);
  if (ambiguity > 0) rows.push(`<li>Ambiguity score: ${ambiguity.toFixed(2)}</li>`);

  const summaryHtml = reasonSummary ? `<div class="thought-summary">${reasonSummary}</div>` : "";
  const detailsHtml = rows.length ? `<ul>${rows.join("")}</ul>` : "";
  const reasonsHtml = `<ul>${reasons || "<li>No reason codes available</li>"}</ul>`;
  overlay.innerHTML = `<div class="thought-title">Escalation reasoning</div>${summaryHtml}${detailsHtml}${reasonsHtml}`;

  const rect = anchor.getBoundingClientRect();
  overlay.style.left = `${Math.min(window.innerWidth - 300, rect.left)}px`;
  overlay.style.top = `${rect.bottom + 8}px`;
  overlay.style.display = "block";
}

function renderWeatherCard(container, data, options = {}) {
  if (!container) return;
  clear(container);

  const compact = Boolean(options.compact);
  const inline = options.layout === "header";
  container.classList.toggle("weather-widget-compact", compact);
  container.classList.toggle("weather-widget-inline", inline);

  const headingTag = compact || inline ? "h4" : "h3";
  const heading = document.createElement(headingTag);
  heading.textContent = String(options.heading || "Weather").trim() || "Weather";
  container.appendChild(heading);

  const line = document.createElement("div");
  line.className = "weather-line";
  line.textContent = (data && data.summary) || "Weather unavailable.";
  container.appendChild(line);

  const forecast = String((data && data.forecast) || "").trim();
  if (forecast && options.showForecast !== false) {
    const forecastLine = document.createElement("div");
    forecastLine.className = "weather-forecast";
    forecastLine.textContent = inline ? summarizeSentence(forecast, 140) : forecast;
    container.appendChild(forecastLine);
  }

  const alerts = Array.isArray(data?.alerts) ? data.alerts.filter((item) => String(item || "").trim()) : [];
  if (alerts.length > 0 && options.showAlerts !== false) {
    const alertWrap = document.createElement("div");
    alertWrap.className = "weather-alerts";

    const alertTitle = document.createElement("div");
    alertTitle.className = "weather-alert-title";
    alertTitle.textContent = "Forecast Alerts";
    alertWrap.appendChild(alertTitle);

    alerts.slice(0, 2).forEach((alert) => {
      const row = document.createElement("div");
      row.className = "weather-alert-item";
      row.textContent = String(alert);
      alertWrap.appendChild(row);
    });

    container.appendChild(alertWrap);
  }

  const meta = document.createElement("div");
  meta.className = "weather-meta";
  if (!compact && !inline) {
    appendConfidenceBadge(meta, "Local read-only");
    if (alerts.length === 0) {
      appendConfidenceBadge(meta, "No active alerts");
    }
  } else if (alerts.length > 0) {
    const alertChip = document.createElement("span");
    alertChip.className = "confidence-badge";
    alertChip.textContent = `${alerts.length} alert${alerts.length === 1 ? "" : "s"}`;
    meta.appendChild(alertChip);
  }
  const updated = String((data && data.updated_at) || "").trim();
  if (updated) {
    const stamp = document.createElement("span");
    stamp.textContent = `Updated ${updated}`;
    meta.appendChild(stamp);
  }
  container.appendChild(meta);
}

function renderWeatherWidget(data) {
  const container = $("weather-widget");
  if (!container) return;

  renderWeatherCard(container, data, {
    compact: true,
    showForecast: true,
    showAlerts: false,
    layout: "header",
  });

  morningState.weather = String((data && data.summary) || "Weather unavailable.").trim();
  renderMorningPanel();
}

function runNewsSearch() {
  const input = $("news-search-input");
  const query = String((input && input.value) || "").trim();
  if (!query) return;
  if (input) input.value = "";
  setActivePage("chat");
  injectUserText(`research latest coverage of ${query}`, "text");
}

function openPatternReview() {
  setActivePage("chat");
  injectUserText("review patterns", "text");
}

function updateNewsSummary(summaryText) {
  const summary = $("news-summary");
  if (!summary) return;
  summary.textContent = (summaryText || "").trim() || "Headlines loaded. Use source-grounded brief or article summaries when you want webpage-level context.";
}

function renderInlineNewsSummary(text, { pending = false, compact = false } = {}) {
  const clean = String(text || "").trim();
  if (!clean && !pending) return null;

  const panel = document.createElement("div");
  panel.className = compact ? "news-inline-summary compact" : "news-inline-summary";
  if (pending) panel.classList.add("pending");

  const title = document.createElement("div");
  title.className = "news-inline-summary-title";
  title.textContent = pending ? "Working on this summary..." : "Source-grounded summary";
  panel.appendChild(title);

  const body = document.createElement("div");
  body.className = "news-inline-summary-body";
  body.textContent = pending ? "Nova is reading the source and preparing an inline summary for this card." : clean;
  panel.appendChild(body);
  return panel;
}

function getOrderedNewsCategoryKeys(categories) {
  const safeCategories = (categories && typeof categories === "object") ? categories : {};
  const preferred = ["global", "local", "politics", "tech", "crypto"];
  const keys = Object.keys(safeCategories).filter((key) => {
    const bucket = safeCategories[key];
    return Array.isArray(bucket && bucket.items) && bucket.items.length > 0;
  });
  return [
    ...preferred.filter((key) => keys.includes(key)),
    ...keys.filter((key) => !preferred.includes(key)),
  ];
}

function updateNewsSummaryState(data = {}) {
  const payload = (data && typeof data === "object") ? data : {};
  const selection = String(payload.selection || "").trim().toLowerCase();
  const storyIndex = Number(payload.story_index || 0);
  const categoryKey = String(payload.category_key || "").trim().toLowerCase();
  const summaryText = String(payload.summary_text || "").trim();

  if (selection === "story_page" && storyIndex > 0) {
    delete latestNewsSummaryState.pendingStories[storyIndex];
    if (summaryText) latestNewsSummaryState.storySummaries[storyIndex] = summaryText;
  }

  if (selection === "category" && categoryKey) {
    delete latestNewsSummaryState.pendingCategories[categoryKey];
    if (summaryText) latestNewsSummaryState.categorySummaries[categoryKey] = summaryText;
  }

  if (payload.comparison && summaryText) {
    latestNewsSummaryState.comparisonSummary = summaryText;
  }
}

function renderNewsSummaryWidget(data = {}) {
  updateNewsSummaryState(data);
  renderNewsWidget(latestNewsItems, $("news-summary")?.textContent || "", latestNewsCategories);
}

function renderNewsCategoryPage(categoryKey, bucket) {
  const page = $("news-category-page");
  const empty = $("news-category-page-empty");
  if (!page || !empty) return;
  clear(page);

  const items = Array.isArray(bucket && bucket.items) ? bucket.items : [];
  if (!categoryKey || items.length === 0) {
    empty.hidden = false;
    page.hidden = true;
    return;
  }

  empty.hidden = true;
  page.hidden = false;

  const titleText = String((bucket && bucket.title) || categoryKey || "").trim() || "News";
  const summaryText = String((bucket && bucket.summary) || "").trim();

  const header = document.createElement("div");
  header.className = "news-category-page-header";

  const titleWrap = document.createElement("div");
  const title = document.createElement("h5");
  title.className = "news-category-page-title";
  title.textContent = titleText;
  titleWrap.appendChild(title);
  if (summaryText) {
    const summary = document.createElement("p");
    summary.className = "news-category-page-summary";
    summary.textContent = summaryText;
    titleWrap.appendChild(summary);
  }
  header.appendChild(titleWrap);

  const count = document.createElement("span");
  count.className = "confidence-badge";
  count.textContent = `${items.length} source${items.length === 1 ? "" : "s"}`;
  header.appendChild(count);

  page.appendChild(header);

  const categoryActions = document.createElement("div");
  categoryActions.className = "news-item-actions";
  const summarizeCategoryBtn = document.createElement("button");
  summarizeCategoryBtn.type = "button";
  summarizeCategoryBtn.className = "assistant-action-btn";
  summarizeCategoryBtn.textContent = "Summarize here";
  summarizeCategoryBtn.addEventListener("click", () => {
    latestNewsSummaryState.pendingCategories[categoryKey] = true;
    renderNewsCategoryPage(categoryKey, bucket);
    requestInlineAssistantAction(`summarize ${categoryKey} news`, `Reading ${titleText} and preparing an inline summary.`, "news_surface");
  });
  categoryActions.appendChild(summarizeCategoryBtn);
  const researchCategoryBtn = document.createElement("button");
  researchCategoryBtn.type = "button";
  researchCategoryBtn.className = "assistant-action-btn";
  researchCategoryBtn.textContent = "Research topic";
  researchCategoryBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText(`research latest ${titleText}`, "text");
  });
  categoryActions.appendChild(researchCategoryBtn);
  page.appendChild(categoryActions);

  const categoryInlineSummary = renderInlineNewsSummary(
    latestNewsSummaryState.categorySummaries[categoryKey] || "",
    { pending: Boolean(latestNewsSummaryState.pendingCategories[categoryKey]) }
  );
  if (categoryInlineSummary) {
    page.appendChild(categoryInlineSummary);
  }

  const list = document.createElement("ol");
  list.className = "news-category-page-list";

  items.forEach((item) => {
    const row = document.createElement("li");
    row.className = "news-category-page-item";

    const link = document.createElement("a");
    link.className = "news-category-link";
    link.href = item.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = String(item.title || "Untitled headline");
    row.appendChild(link);

    const itemSummary = document.createElement("p");
    itemSummary.className = "news-category-item-summary";
    const snippet = buildNewsItemSnippet(item);
    itemSummary.textContent = snippet.length > 140 ? `${snippet.slice(0, 137)}...` : snippet;
    row.appendChild(itemSummary);

    const actions = document.createElement("div");
    actions.className = "news-item-actions";
    const openSource = document.createElement("a");
    openSource.className = "assistant-action-btn";
    openSource.href = item.url;
    openSource.target = "_blank";
    openSource.rel = "noopener noreferrer";
    openSource.textContent = "Open source";
    actions.appendChild(openSource);
    const summarizeArticleBtn = document.createElement("button");
    summarizeArticleBtn.type = "button";
    summarizeArticleBtn.className = "assistant-action-btn";
    summarizeArticleBtn.textContent = "Research coverage";
    summarizeArticleBtn.addEventListener("click", () => {
      const topic = String(item.title || "").trim();
      if (!topic) return;
      setActivePage("chat");
      injectUserText(`research latest coverage of ${topic}`, "text");
    });
    actions.appendChild(summarizeArticleBtn);
    const videoUrl = String(item.video_url || "").trim();
    if (videoUrl) {
      const watchLink = document.createElement("a");
      watchLink.className = "assistant-action-btn";
      watchLink.href = videoUrl;
      watchLink.target = "_blank";
      watchLink.rel = "noopener noreferrer";
      watchLink.textContent = "Watch video";
      actions.appendChild(watchLink);
    }
    row.appendChild(actions);

    const meta = document.createElement("div");
    meta.className = "news-category-meta";
    const source = document.createElement("span");
    source.className = "domain-badge";
    source.textContent = String((item.source || "").trim() || "Source");
    meta.appendChild(source);
    const freshness = formatNewsFreshness(item.published);
    if (freshness) {
      const freshnessBadge = document.createElement("span");
      freshnessBadge.className = "confidence-badge";
      freshnessBadge.textContent = freshness;
      meta.appendChild(freshnessBadge);
    }
    row.appendChild(meta);
    list.appendChild(row);
  });

  page.appendChild(list);
}

function renderNewsCategoryGrid(categories) {
  const nav = $("news-category-nav");
  const countLabel = $("news-category-count");
  if (!nav) return;
  clear(nav);

  const safeCategories = (categories && typeof categories === "object") ? categories : {};
  const displayKeys = getOrderedNewsCategoryKeys(safeCategories);
  if (countLabel) {
    countLabel.textContent = `${displayKeys.length} categor${displayKeys.length === 1 ? "y" : "ies"}`;
  }

  if (displayKeys.length === 0) {
    selectedNewsCategoryKey = "";
    renderNewsCategoryPage("", null);
    return;
  }

  if (!selectedNewsCategoryKey || !displayKeys.includes(selectedNewsCategoryKey)) {
    selectedNewsCategoryKey = displayKeys[0];
  }

  displayKeys.forEach((key) => {
    const bucket = safeCategories[key];
    const items = Array.isArray(bucket && bucket.items) ? bucket.items : [];
    const titleText = String((bucket && bucket.title) || key || "").trim() || "News";
    if (items.length === 0) return;

    const tab = document.createElement("button");
    tab.type = "button";
    tab.className = "news-category-tab";
    if (key === selectedNewsCategoryKey) tab.classList.add("active");

    const label = document.createElement("span");
    label.className = "news-category-title";
    label.textContent = titleText;
    tab.appendChild(label);

    const count = document.createElement("span");
    count.className = "confidence-badge";
    count.textContent = String(items.length);
    tab.appendChild(count);

    tab.addEventListener("click", () => {
      selectedNewsCategoryKey = key;
      renderNewsCategoryGrid(latestNewsCategories);
    });

    nav.appendChild(tab);
  });

  renderNewsCategoryPage(selectedNewsCategoryKey, safeCategories[selectedNewsCategoryKey]);
}

function setNewsExpandButton() {
  const btn = $("btn-news-expand");
  if (!btn) return;
  const hasExtra = latestNewsItems.length > getNewsPreviewLimit();
  btn.style.display = hasExtra ? "inline-block" : "none";
  btn.textContent = newsExpanded ? "Show brief" : "Expand details";
  btn.setAttribute("aria-pressed", newsExpanded ? "true" : "false");
}

function renderNewsWidget(items, summaryText = "", categories = null) {
  const list = $("news-list");
  if (!list) return;
  clear(list);
  if (categories && typeof categories === "object") {
    latestNewsCategories = categories;
  }

  if (!Array.isArray(items) || items.length === 0) {
    latestNewsItems = [];
    const li = document.createElement("li");
    li.textContent = "No headlines available.";
    list.appendChild(li);
    updateNewsSummary("No headlines are available to summarize right now.");
    morningState.news = "No headlines available.";
    renderMorningPanel();
    renderNewsCategoryGrid(latestNewsCategories);
    setNewsExpandButton();
    return;
  }

  latestNewsItems = items.slice();
  updateNewsSummary(summaryText);
  morningState.news = (summaryText || items[0]?.title || "Headlines available.").trim();
  renderMorningPanel();

  const previewLimit = getNewsPreviewLimit();
  const visibleItems = newsExpanded ? latestNewsItems : latestNewsItems.slice(0, previewLimit);
  visibleItems.forEach((item, index) => {
    const storyIndex = index + 1;
    const li = document.createElement("li");

    const badge = document.createElement("span");
    badge.className = "citation-index";
    badge.textContent = `[${storyIndex}]`;
    li.appendChild(badge);

    const a = document.createElement("a");
    a.href = item.url;
    a.className = "news-item-title";
    a.textContent = item.title || "Untitled story";
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    li.appendChild(a);

    const summary = document.createElement("p");
    summary.className = "news-item-summary";
    const itemSnippet = buildNewsItemSnippet(item);
    summary.textContent = itemSnippet.length > 180 ? `${itemSnippet.slice(0, 177)}...` : itemSnippet;
    li.appendChild(summary);

    const meta = document.createElement("div");
    meta.className = "news-item-meta";

    const sourceBadge = document.createElement("span");
    sourceBadge.className = "domain-badge";
    sourceBadge.textContent = (item.source || "").trim() || "Unknown source";
    meta.appendChild(sourceBadge);

    const freshness = formatNewsFreshness(item.published);
    if (freshness) {
      const freshnessBadge = document.createElement("span");
      freshnessBadge.className = "confidence-badge";
      freshnessBadge.textContent = freshness;
      meta.appendChild(freshnessBadge);
    }

    li.appendChild(meta);

    const row = document.createElement("div");
    row.className = "news-item-actions";

    const summarizeBtn = document.createElement("button");
    summarizeBtn.type = "button";
    summarizeBtn.className = "assistant-action-btn";
    summarizeBtn.textContent = "Summarize here";
    summarizeBtn.addEventListener("click", () => {
      latestNewsSummaryState.pendingStories[storyIndex] = true;
      renderNewsWidget(latestNewsItems, $("news-summary")?.textContent || "", latestNewsCategories);
      requestInlineAssistantAction(`summary of article ${storyIndex}`, `Reading article ${storyIndex} and preparing an inline summary.`, "news_surface");
    });
    row.appendChild(summarizeBtn);

    const compareBtn = document.createElement("button");
    compareBtn.type = "button";
    compareBtn.className = "assistant-action-btn";
    compareBtn.textContent = "Research this";
    compareBtn.addEventListener("click", () => {
      const topic = String(item.title || "").trim();
      if (!topic) return;
      setActivePage("chat");
      injectUserText(`research latest coverage of ${topic}`, "text");
    });
    row.appendChild(compareBtn);

    const videoUrl = String(item.video_url || "").trim();
    if (videoUrl) {
      const watchLink = document.createElement("a");
      watchLink.className = "assistant-action-btn";
      watchLink.href = videoUrl;
      watchLink.target = "_blank";
      watchLink.rel = "noopener noreferrer";
      watchLink.textContent = "Watch video";
      row.appendChild(watchLink);
    }

    li.appendChild(row);

    const storyInlineSummary = renderInlineNewsSummary(
      latestNewsSummaryState.storySummaries[storyIndex] || "",
      { pending: Boolean(latestNewsSummaryState.pendingStories[storyIndex]), compact: true }
    );
    if (storyInlineSummary) {
      li.appendChild(storyInlineSummary);
    }

    list.appendChild(li);
  });

  renderNewsCategoryGrid(latestNewsCategories);
  setNewsExpandButton();
}

function renderSearchWidget(data) {
  const container = $("search-widget");
  const results = Array.isArray(data && data.results) ? data.results : [];
  if (container) {
    clear(container);
    container.classList.remove("active");

    if (!results.length) {
      return;
    }

    container.classList.add("active");
    const header = document.createElement("div");
    header.className = "search-widget-header";

    const queryLabel = document.createElement("p");
    queryLabel.className = "search-widget-query";
    const queryText = String((data && data.query) || "").trim();
    queryLabel.textContent = queryText ? `Results for "${queryText}"` : "Web search results";
    header.appendChild(queryLabel);

    const meta = document.createElement("div");
    meta.className = "search-widget-meta";
    appendConfidenceBadge(meta, `${results.length} result${results.length === 1 ? "" : "s"}`);
    if (data && Number(data.source_pages_read || 0) > 0) {
      appendConfidenceBadge(meta, `${Number(data.source_pages_read)} page${Number(data.source_pages_read) === 1 ? "" : "s"} read`);
    }
    if (data && data.provider) appendConfidenceBadge(meta, String(data.provider));
    if (data && typeof data.latency_seconds === "number" && data.latency_seconds > 0) {
      appendConfidenceBadge(meta, `${Number(data.latency_seconds).toFixed(1)}s`);
    }
    header.appendChild(meta);

    if (data && data.summary) {
      const summary = document.createElement("p");
      summary.className = "search-widget-summary";
      summary.textContent = String(data.summary);
      header.appendChild(summary);
    }
    container.appendChild(header);

    const sourcesSection = document.createElement("div");
    sourcesSection.className = "search-sources-section";

    const sourcesToggleRow = document.createElement("div");
    sourcesToggleRow.className = "search-widget-actions";

    const sourcesToggle = document.createElement("button");
    sourcesToggle.type = "button";
    sourcesToggle.className = "assistant-action-btn";
    sourcesToggle.textContent = `Show sources (${results.length})`;
    sourcesToggle.setAttribute("aria-expanded", "false");
    sourcesToggleRow.appendChild(sourcesToggle);

    const sourceList = document.createElement("div");
    sourceList.className = "search-sources-list";
    sourceList.hidden = true;

    sourcesToggle.addEventListener("click", () => {
      const expanded = sourceList.hidden;
      sourceList.hidden = !expanded;
      sourcesToggle.setAttribute("aria-expanded", expanded ? "true" : "false");
      sourcesToggle.textContent = expanded ? "Hide sources" : `Show sources (${results.length})`;
    });

    results.forEach((item, index) => {
      const div = document.createElement("div");
      div.className = "search-result";

      const titleRow = document.createElement("div");
      titleRow.className = "search-result-title";

      const idx = document.createElement("span");
      idx.className = "citation-index";
      idx.textContent = `[${index + 1}]`;
      titleRow.appendChild(idx);

      const a = document.createElement("a");
      a.href = item.url;
      a.textContent = item.title;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      titleRow.appendChild(a);

      const domain = extractDomain(item.url);
      if (domain) {
        const domainBadge = document.createElement("span");
        domainBadge.className = "domain-badge";
        domainBadge.textContent = domain;
        titleRow.appendChild(domainBadge);
      }

      appendConfidenceBadge(titleRow, "Web result");
      div.appendChild(titleRow);

      const snippet = String(item.snippet || "").trim();
      if (snippet) {
        const snippetEl = document.createElement("p");
        snippetEl.className = "search-result-snippet";
        snippetEl.textContent = snippet;
        div.appendChild(snippetEl);
      }

      const actions = document.createElement("div");
      actions.className = "search-result-actions";

      const summarizeBtn = document.createElement("button");
      summarizeBtn.type = "button";
      summarizeBtn.className = "assistant-action-btn";
      summarizeBtn.textContent = "Research this topic";
      summarizeBtn.addEventListener("click", () => injectUserText(`research ${item.title}`, "text"));
      actions.appendChild(summarizeBtn);

      if (index === 0 && results.length > 1) {
        const compareBtn = document.createElement("button");
        compareBtn.type = "button";
        compareBtn.className = "assistant-action-btn";
        compareBtn.textContent = "Brief this topic";
        compareBtn.addEventListener("click", () => injectUserText(`create an intelligence brief on ${queryText || item.title}`, "text"));
        actions.appendChild(compareBtn);
      }
      div.appendChild(actions);
      sourceList.appendChild(div);
    });
    sourcesSection.appendChild(sourcesToggleRow);
    sourcesSection.appendChild(sourceList);
    container.appendChild(sourcesSection);

    const suggested = Array.isArray(data && data.suggested_actions) ? data.suggested_actions : [];
    if (suggested.length) {
      const actionRow = document.createElement("div");
      actionRow.className = "search-widget-actions";
      suggested.slice(0, 3).forEach((item) => {
        const label = String((item && item.label) || "").trim();
        const prompt = String((item && item.prompt) || "").trim();
        if (!label || !prompt) return;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "assistant-action-btn";
        btn.textContent = label;
        btn.addEventListener("click", () => injectUserText(prompt, "text"));
        actionRow.appendChild(btn);
      });
      if (actionRow.childElementCount) container.appendChild(actionRow);
    }
    return;
  }

  if (!results.length) {
    appendChatMessage("assistant", "I could not find reliable results for that.", null, "Web result");
    return;
  }

  results.forEach((item, index) => {
    const domain = extractDomain(item.url);
    const snippet = String(item.snippet || "").trim();
    appendChatMessage(
      "assistant",
      `[${index + 1}] ${item.title} (${domain || "source"})\n${item.url}${snippet ? `\n${snippet}` : ""}`,
      null,
      "Web result",
    );
  });
}

function translateError(code, message) {
  const map = {
    input_too_long: "That message is a bit long. Try one short sentence first.",
    invalid_json: "I couldn't read that request. Please try again.",
  };
  return map[code] || message || "Something went wrong. Please try again.";
}

function tryHandleLocalPageCommand(text) {
  const clean = String(text || "").trim().toLowerCase();
  if (!clean) return false;

  const localRoutes = [
    { pattern: /^(intro|introduction|get(ting)? started|welcome)$/i, page: "intro", reply: "Opening the Introduction page so you can see what Nova is, how it works, and the safest way to start." },
    { pattern: /^(settings|open settings|show settings|preferences|setup options)$/i, page: "settings", reply: "Opening Settings so you can review setup mode, voice status, privacy, and comfort controls." },
    { pattern: /^(policy center|policy review|open policies)$/i, page: "policy", reply: "Opening Policies so you can inspect drafts, simulations, and one-shot review runs without enabling background automation." },
  ];

  const found = localRoutes.find((item) => item.pattern.test(clean));
  if (!found) return false;

  appendChatMessage("user", text);
  setActivePage(found.page);
  appendChatMessage("assistant", found.reply, null, "System status");
  return true;
}

function injectUserText(text, channel = "text") {
  const clean = (text || "").trim();
  if (!clean) return;
  if (channel === "text" && tryHandleLocalPageCommand(clean)) return;

  appendChatMessage("user", clean);
  waitingForAssistant = true;
  setLoadingHint(loadingHintForInput(clean));
  setThinkingBar(true);

  if (!safeWSSend({ text: clean, channel })) {
    waitingForAssistant = false;
    setThinkingBar(false);
    appendChatMessage("assistant", "Connection is not ready yet. Please wait a second and try again.", null, "System status");
  }
}

function requestInlineAssistantAction(text, statusText = "", invocationSource = "ui_surface") {
  const clean = String(text || "").trim();
  if (!clean) return false;

  waitingForAssistant = true;
  setLoadingHint(statusText || loadingHintForInput(clean));
  setThinkingBar(true);

  if (!safeWSSend({ text: clean, invocation_source: invocationSource })) {
    waitingForAssistant = false;
    setThinkingBar(false);
    appendChatMessage("assistant", "Connection is not ready yet. Please wait a second and try again.", null, "System status");
    return false;
  }

  return true;
}

function requestDeepSeekSecondOpinion() {
  appendChatMessage("user", "DeepSeek second opinion");
  waitingForAssistant = true;
  setLoadingHint("DeepSeek is reviewing the recent exchange.");
  setThinkingBar(true);

  if (!safeWSSend({ text: "verify", invocation_source: "deepseek_button" })) {
    waitingForAssistant = false;
    setThinkingBar(false);
    appendChatMessage("assistant", "Connection is not ready yet. Please wait a second and try again.", null, "System status");
  }
}

async function startSTT() {
  if (mediaRecorder) return;
  if (!navigator.mediaDevices || !window.MediaRecorder) return;

  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
  catch { return; }

  setOrbStatus("LISTENING");
  const options = {};
  if (MediaRecorder.isTypeSupported("audio/webm;codecs=pcm")) options.mimeType = "audio/webm;codecs=pcm";
  else if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) options.mimeType = "audio/webm;codecs=opus";
  else if (MediaRecorder.isTypeSupported("audio/webm")) options.mimeType = "audio/webm";

  if (!options.mimeType) {
    stream.getTracks().forEach((t) => t.stop());
    setOrbStatus("READY");
    return;
  }

  mediaRecorder = new MediaRecorder(stream, options);
  const chunks = [];

  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) {
      chunks.push(e.data);
      setOrbStatus("LISTENING");
      clearTimeout(silenceTimer);
      silenceTimer = setTimeout(() => setOrbStatus("PAUSED"), 1200);
    }
  };

  mediaRecorder.onstop = async () => {
    clearTimeout(silenceTimer);
    silenceTimer = null;
    setOrbStatus("PROCESSING");

    try {
      const blob = new Blob(chunks, { type: mediaRecorder.mimeType });
      const form = new FormData();
      form.append("audio", blob, "speech.webm");

      const res = await fetch(`${API_BASE}/stt/transcribe`, { method: "POST", body: form });
      let data = {};
      try {
        data = await res.json();
      } catch (_) {
        data = {};
      }

      if (!res.ok) {
        appendChatMessage(
          "assistant",
          "I couldn't process that recording. Please try again.",
          null,
          "Voice input",
        );
        return;
      }

      if (data.error) {
        appendChatMessage("assistant", String(data.error), null, "Voice input");
        return;
      }

      const transcript = String(data.text || "").trim();
      if (transcript) {
        injectUserText(transcript, "voice");
      } else {
        appendChatMessage(
          "assistant",
          "I didn't catch that. Try speaking a bit slower or closer to the mic.",
          null,
          "Voice input",
        );
      }
    } finally {
      if (stream) stream.getTracks().forEach((t) => t.stop());
      mediaRecorder = null;
      chunks.length = 0;
      setOrbStatus("READY");
    }
  };

  mediaRecorder.start(250);
}

function stopSTT() {
  clearTimeout(silenceTimer);
  silenceTimer = null;
  if (ackResetTimer) {
    clearTimeout(ackResetTimer);
    ackResetTimer = null;
  }
  if (mediaRecorder && mediaRecorder.state === "recording") mediaRecorder.stop();
}

function hydrateDashboardWidgets() {
  const now = Date.now();
  if (now - lastWidgetHydrationAt < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  lastWidgetHydrationAt = now;

  safeWSSend({ text: "weather", silent_widget_refresh: true });
  safeWSSend({ text: "news", silent_widget_refresh: true });
  safeWSSend({ text: "system status", silent_widget_refresh: true });
  safeWSSend({ text: "calendar", silent_widget_refresh: true });
  safeWSSend({ text: "memory overview", silent_widget_refresh: true });
  safeWSSend({ text: "show threads", silent_widget_refresh: true });
  safeWSSend({ text: "workspace home", silent_widget_refresh: true });
  safeWSSend({ text: "show structure map", silent_widget_refresh: true });
  safeWSSend({ text: "trust center", silent_widget_refresh: true });
  safeWSSend({ text: "policy overview", silent_widget_refresh: true });
  safeWSSend({ text: "tone status", silent_widget_refresh: true });
  safeWSSend({ text: "notification status", silent_widget_refresh: true });
  safeWSSend({ text: "pattern status", silent_widget_refresh: true });
}

function startWidgetAutoRefresh() {
  if (widgetRefreshTimer) clearInterval(widgetRefreshTimer);
  widgetRefreshTimer = setInterval(() => {
    if (!document.hidden) hydrateDashboardWidgets();
  }, WIDGET_AUTO_REFRESH_INTERVAL_MS);
}

function stopWidgetAutoRefresh() {
  if (!widgetRefreshTimer) return;
  clearInterval(widgetRefreshTimer);
  widgetRefreshTimer = null;
}

function connectWebSocket() {
  ws = new WebSocket(`${WS_BASE}/ws`);

  ws.onopen = () => {
    refreshPrivacyPanel();
    hydrateDashboardWidgets();
    startWidgetAutoRefresh();
  };

  ws.onmessage = (e) => {
    let msg;
    try { msg = JSON.parse(e.data); }
    catch { return; }

    switch (msg.type) {
      case "weather":
        renderWeatherWidget(msg.data);
        break;
      case "news":
        latestNewsSummaryState = {
          storySummaries: {},
          categorySummaries: {},
          comparisonSummary: "",
          pendingStories: {},
          pendingCategories: {},
        };
        renderNewsWidget(msg.items, msg.summary || "", msg.categories || {});
        break;
      case "news_summary":
        renderNewsSummaryWidget(msg.data || {});
        break;
      case "intelligence_brief":
        renderIntelligenceBriefWidget(msg.data || {});
        break;
      case "search":
        renderSearchWidget(msg.data);
        break;
      case "system":
        morningState.system = formatSystemSummary(msg.data || {}, msg.summary || "System status ready.");
        renderMorningPanel();
        renderOperatorHealthWidget(msg.data || {});
        renderCapabilitySurfaceWidget(msg.data || {});
        renderTrustPanel(msg.data || {});
        break;
      case "calendar":
        morningState.calendar = msg.summary || msg.message || "No events scheduled today.";
        renderMorningPanel();
        break;
      case "screen_capture":
        renderScreenCaptureInsight(msg.data || {});
        break;
      case "screen_analysis":
        renderScreenAnalysisInsight(msg.data || {});
        break;
      case "file_explanation":
        renderFileExplanationInsight(msg.data || {});
        break;
      case "thread_map":
        renderThreadMapWidget(msg);
        break;
      case "workspace_home":
        renderWorkspaceHomeWidget(msg);
        break;
      case "project_structure_map":
        renderProjectStructureMapWidget(msg);
        break;
      case "thread_detail":
        renderThreadDetailWidget(msg);
        break;
      case "memory_overview":
        renderMemoryOverviewWidget(msg);
        break;
      case "memory_list":
        renderMemoryListWidget(msg);
        break;
      case "memory_item":
        renderMemoryItemWidget(msg);
        break;
      case "policy_overview":
        renderPolicyOverviewWidget(msg);
        break;
      case "policy_item":
        renderPolicyItemWidget(msg);
        break;
      case "policy_simulation":
        renderPolicySimulationWidget(msg);
        break;
      case "policy_run":
        renderPolicyRunWidget(msg);
        break;
      case "tone_profile":
        renderToneOverviewWidget(msg);
        break;
      case "notification_schedule":
        renderNotificationOverviewWidget(msg);
        break;
      case "pattern_review":
        renderPatternReviewWidget(msg);
        break;
      case "chat":
        appendChatMessage(
          "assistant",
          msg.message,
          msg.message_id || null,
          msg.confidence || "",
          msg.suggested_actions || null
        );
        break;
      case "ack":
        handleVoiceAck(msg.message || "");
        break;
      case "trust_status":
        if (msg.data && typeof msg.data === "object") {
          trustState.mode = msg.data.mode || trustState.mode;
          trustState.lastExternalCall = msg.data.last_external_call || trustState.lastExternalCall;
          trustState.dataEgress = msg.data.data_egress || trustState.dataEgress;
          trustState.failureState = msg.data.failure_state || trustState.failureState;
          if (Number.isFinite(Number(msg.data.consecutive_failures))) {
            trustState.consecutiveFailures = Math.max(0, Number(msg.data.consecutive_failures));
          }
          renderTrustPanel(msg.data || {});
        }
        break;
      case "chat_done":
        waitingForAssistant = false;
        setLoadingHint("");
        setThinkingBar(false);
        break;
      case "thought":
        if (pendingThoughtMessageId && msg.message_id === pendingThoughtMessageId) {
          const anchor = messageMeta.get(msg.message_id);
          if (anchor) showThoughtOverlay(anchor, msg.data || {});
          pendingThoughtMessageId = null;
        }
        break;
      case "error":
        waitingForAssistant = false;
        setThinkingBar(false);
        appendChatMessage("assistant", translateError(msg.code, msg.message), null, "System status");
        break;
    }
  };

  ws.onclose = () => {
    waitingForAssistant = false;
    setThinkingBar(false);
    stopWidgetAutoRefresh();
    if (ackResetTimer) {
      clearTimeout(ackResetTimer);
      ackResetTimer = null;
    }
    setTimeout(connectWebSocket, 2000);
  };
}

function setupSidebarTabs() {
  const tabs = document.querySelectorAll(".rail-tab");
  if (!tabs || tabs.length === 0) return;

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const panelId = tab.dataset.panel;
      if (!panelId) return;

      if (panelId === "help-modal") {
        showHelpModal();
        return;
      }

      const news = $("news-widget");
      const trust = $("trust-panel");
      const brief = $("brief-widget");
      const guide = $("guide-widget");
      const panels = [news, trust, brief, guide].filter(Boolean);
      if (panels.length === 0) return;

      panels.forEach((p) => { p.hidden = true; });
      const target = $(panelId);
      if (target) target.hidden = false;

      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
    });
  });
}

function setActivePage(page) {
  const pages = {
    chat: $("page-chat"),
    news: $("page-news"),
    intro: $("page-intro"),
    home: $("page-home"),
    workspace: $("page-workspace"),
    memory: $("page-memory"),
    policy: $("page-policy"),
    trust: $("page-trust"),
    settings: $("page-settings"),
  };
  const target = normalizePageKey(page);

  Object.entries(pages).forEach(([name, el]) => {
    if (!el) return;
    el.hidden = name !== target;
  });

  document.querySelectorAll(".header-menu-page-btn").forEach((btn) => {
    const active = btn.dataset.page === target;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
  });

  const workspaceCurrent = $("workspace-current-label");
  if (workspaceCurrent) {
    workspaceCurrent.textContent = PAGE_LABELS[target] || "Chat";
  }

  localStorage.setItem(STORAGE_KEYS.activePage, target);
  renderQuickActions();

  if (target === "memory") {
    hydrateMemoryManagement();
  }
  if (target === "policy") {
    requestPolicyOverviewRefresh(true);
    if (policyCenterState.selectedId && !policyCenterState.selectedItem) {
      requestPolicyDetail(policyCenterState.selectedId);
    }
    renderPolicyCenterPage();
  }
  if (target === "home") {
    requestWorkspaceHomeRefresh(true);
  }
  if (target === "workspace") {
    requestWorkspaceHomeRefresh(true);
    requestProjectStructureMapRefresh(true);
  }
  if (target === "trust") {
    safeWSSend({ text: "trust center", silent_widget_refresh: true });
    safeWSSend({ text: "system status", silent_widget_refresh: true });
  }
  if (target === "intro") {
    renderIntroPage();
  }
  if (target === "settings") {
    safeWSSend({ text: "trust center", silent_widget_refresh: true });
    safeWSSend({ text: "system status", silent_widget_refresh: true });
    renderSettingsPage();
  }

  if (latestNewsItems.length > 0) {
    renderNewsWidget(latestNewsItems, $("news-summary")?.textContent || "", latestNewsCategories);
  } else {
    setNewsExpandButton();
  }
}

function setupPageNavigation() {
  const buttons = document.querySelectorAll(".header-menu-page-btn");
  if (!buttons || buttons.length === 0) return;

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      closeHeaderMenus();
      setActivePage(btn.dataset.page || "chat");
    });
  });

  const stored = localStorage.getItem(STORAGE_KEYS.activePage) || "chat";
  setActivePage(stored);
}

function sendChat() {
  const input = $("chat-input");
  if (!input) return;
  injectUserText(input.value, "text");
  input.value = "";
}

function ensureDatalist() {
  const input = $("chat-input");
  if (!input) return;

  let list = $("command-suggestions");
  if (!list) {
    list = document.createElement("datalist");
    list.id = "command-suggestions";
    document.body.appendChild(list);
  }

  clear(list);
  COMMAND_SUGGESTIONS.forEach((item) => {
    const opt = document.createElement("option");
    opt.value = item;
    list.appendChild(opt);
  });

  input.setAttribute("list", "command-suggestions");
}

function createModalShell(id, title) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.id = id;
  overlay.style.display = "none";

  const card = document.createElement("div");
  card.className = "modal-card";

  const h = document.createElement("h3");
  h.textContent = title;
  card.appendChild(h);

  const close = document.createElement("button");
  close.type = "button";
  close.className = "modal-close";
  close.textContent = "Close";
  close.addEventListener("click", () => { overlay.style.display = "none"; });

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.style.display = "none";
  });

  card.appendChild(close);
  overlay.appendChild(card);
  document.body.appendChild(overlay);
  return { overlay, card };
}

function showFirstRunGuide(force = false) {
  if (!force && localStorage.getItem(STORAGE_KEYS.firstRunDone) === "1") return;

  const existing = $("first-run-modal");
  if (existing) existing.remove();

  const { overlay, card } = createModalShell("first-run-modal", "Welcome to Nova");

  const intro = document.createElement("p");
  intro.className = "first-run-intro";
  intro.textContent = "Nova is a governed personal intelligence system. It helps with research, explanation, memory, and workspace continuity while keeping you in control of every meaningful action.";
  card.appendChild(intro);

  const pillars = document.createElement("div");
  pillars.className = "first-run-pillars";
  [
    ["Read the Introduction", "See what Nova is, what it can do, and why it stays invocation-bound."],
    ["Review Settings", "Choose Local Mode or a future cloud path, then review privacy, accessibility, and voice status."],
    ["Use Workspace and Trust", "Workspace keeps project continuity together. Trust shows what happened, why it happened, and what stayed blocked."],
  ].forEach(([titleText, bodyText]) => {
    const panel = document.createElement("div");
    panel.className = "first-run-pillar";

    const title = document.createElement("div");
    title.className = "first-run-pillar-title";
    title.textContent = titleText;
    panel.appendChild(title);

    const body = document.createElement("div");
    body.className = "first-run-pillar-copy";
    body.textContent = bodyText;
    panel.appendChild(body);

    pillars.appendChild(panel);
  });
  card.appendChild(pillars);

  const steps = document.createElement("ol");
  steps.className = "help-list";
  [
    "Open Introduction to understand Nova's boundaries, setup modes, and first commands.",
    "Open Settings to choose your preferred setup mode and review voice, privacy, and accessibility controls.",
    "Open Workspace to see project threads, reports, recent decisions, and the structure map together.",
    "Use explicit phrases like \"remember this\" when you want something saved durably.",
  ].forEach((label) => {
    const li = document.createElement("li");
    li.textContent = label;
    steps.appendChild(li);
  });
  card.appendChild(steps);

  const trustNote = document.createElement("p");
  trustNote.className = "first-run-note";
  trustNote.textContent = "Important: Nova stays invocation-bound. It can help broadly, but effectful actions still remain governed and inspectable.";
  card.appendChild(trustNote);

  const row = document.createElement("div");
  row.className = "modal-actions";

  [
    {
      label: "Open Introduction",
      fn: () => {
        setActivePage("intro");
      },
    },
    {
      label: "Open Settings",
      fn: () => {
        setActivePage("settings");
      },
    },
    {
      label: "Open Workspace",
      fn: () => {
        setActivePage("workspace");
      },
    },
    {
      label: "Open Trust",
      fn: () => {
        setActivePage("trust");
      },
    },
    {
      label: "Try Morning Brief",
      fn: () => {
        setActivePage("chat");
        injectUserText("daily brief", "text");
      },
    },
  ].forEach((item) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = item.label;
    b.addEventListener("click", () => {
      item.fn();
      overlay.style.display = "none";
      localStorage.setItem(STORAGE_KEYS.firstRunDone, "1");
    });
    row.appendChild(b);
  });

  const done = document.createElement("button");
  done.type = "button";
  done.textContent = "Got it";
  done.addEventListener("click", () => {
    overlay.style.display = "none";
    localStorage.setItem(STORAGE_KEYS.firstRunDone, "1");
  });
  row.appendChild(done);

  card.appendChild(row);
  overlay.style.display = "flex";
}

function showFirstRunGuideIfNeeded() {
  showFirstRunGuide(false);
}

function renderIntroPage() {
  const modeBadge = $("intro-current-mode-badge");
  const modeCopy = $("intro-current-mode-copy");
  const currentMode = getSetupModeMeta();
  if (modeBadge) modeBadge.textContent = currentMode.badge;
  if (modeCopy) modeCopy.textContent = `${currentMode.label}: ${currentMode.copy}`;
}

function renderSettingsPage() {
  const modeHost = $("settings-mode-cards");
  const modeSummary = $("settings-current-mode-summary");
  const voiceSummary = $("settings-voice-summary");
  const voiceGrid = $("settings-voice-grid");
  const setupMode = getSetupMode();
  const currentMode = getSetupModeMeta(setupMode);

  if (modeSummary) {
    modeSummary.textContent = `${currentMode.label}. ${currentMode.copy}`;
  }

  if (modeHost) {
    clear(modeHost);
    [
      {
        id: "local",
        title: "Local Mode",
        badge: "Free · Offline-first",
        copy: "Uses local models and keeps Nova private by default. This is the best current everyday mode.",
      },
      {
        id: "bring_your_own_key",
        title: "Bring Your Own API Key",
        badge: "Manual cloud",
        copy: "Lets you bring your own provider later while keeping cost visibility and local control.",
      },
      {
        id: "managed_cloud",
        title: "Managed Cloud Access",
        badge: "Later guided setup",
        copy: "The easiest long-term setup path. Keep this as a saved preference until the full managed flow is live.",
      },
    ].forEach((entry) => {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "settings-mode-card";
      if (setupMode === entry.id) card.classList.add("active");
      card.addEventListener("click", () => setSetupMode(entry.id));

      const title = document.createElement("div");
      title.className = "settings-mode-title";
      title.textContent = entry.title;
      card.appendChild(title);

      const badge = document.createElement("div");
      badge.className = "settings-mode-badge";
      badge.textContent = entry.badge;
      card.appendChild(badge);

      const copy = document.createElement("div");
      copy.className = "settings-mode-copy";
      copy.textContent = entry.copy;
      card.appendChild(copy);

      modeHost.appendChild(card);
    });
  }

  const largeText = $("settings-toggle-large-text");
  if (largeText) largeText.checked = localStorage.getItem(STORAGE_KEYS.uiLargeText) === "1";
  const highContrast = $("settings-toggle-high-contrast");
  if (highContrast) highContrast.checked = localStorage.getItem(STORAGE_KEYS.uiHighContrast) === "1";
  const compactDensity = $("settings-toggle-compact-density");
  if (compactDensity) compactDensity.checked = localStorage.getItem(STORAGE_KEYS.uiCompactDensity) === "1";

  if (voiceSummary && voiceGrid) {
    const voice = (trustReviewState.voiceRuntime && typeof trustReviewState.voiceRuntime === "object")
      ? trustReviewState.voiceRuntime
      : {};
    voiceSummary.textContent = [
      String(voice.summary || "").trim() || "Run Voice Check to confirm spoken output on this device.",
      String(voice.last_attempt_status || "").trim(),
      String(voice.last_engine || "").trim(),
    ].filter(Boolean).join(" · ");

    clear(voiceGrid);
    [
      ["Preferred engine", String(voice.preferred_engine || "Piper").trim() || "Piper"],
      ["Preferred status", String(voice.preferred_status || "Unknown").trim() || "Unknown"],
      ["Fallback engine", String(voice.fallback_engine || "pyttsx3").trim() || "pyttsx3"],
      ["Fallback status", String(voice.fallback_status || "Unknown").trim() || "Unknown"],
      ["Last attempt", String(voice.last_attempt_status || "No voice check yet").trim() || "No voice check yet"],
      ["Last engine", String(voice.last_engine || "None").trim() || "None"],
    ].forEach(([label, value]) => {
      voiceGrid.appendChild(createOverviewChip(label, value));
    });
  }
}

function renderCommandDiscovery() {
  const host = $("command-groups");
  if (!host) return;
  clear(host);

  COMMAND_DISCOVERY_GROUPS.forEach((group) => {
    const groupEl = document.createElement("div");
    groupEl.className = "command-group";

    const label = document.createElement("div");
    label.className = "command-group-label";
    label.textContent = group.label;
    groupEl.appendChild(label);

    const row = document.createElement("div");
    row.className = "command-chip-row";
    (group.commands || []).forEach((cmd) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "command-chip";
      chip.textContent = cmd;
      chip.addEventListener("click", () => injectUserText(cmd, "text"));
      row.appendChild(chip);
    });

    groupEl.appendChild(row);
    host.appendChild(groupEl);
  });
}

function showHelpModal() {
  let overlay = $("help-modal");
  if (!overlay) {
    const shell = createModalShell("help-modal", "How to ask Nova");
    overlay = shell.overlay;
    const card = shell.card;

    const about = document.createElement("p");
    about.textContent = "Nova helps with weather, news, research summaries, and simple system requests when you ask.";
    card.appendChild(about);

    const groupsWrap = document.createElement("div");
    groupsWrap.className = "command-groups";
    COMMAND_DISCOVERY_GROUPS.forEach((group) => {
      const groupEl = document.createElement("div");
      groupEl.className = "command-group";

      const label = document.createElement("div");
      label.className = "command-group-label";
      label.textContent = group.label;
      groupEl.appendChild(label);

      const row = document.createElement("div");
      row.className = "command-chip-row";
      (group.commands || []).forEach((cmd) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "command-chip";
        chip.textContent = cmd;
        chip.addEventListener("click", () => {
          injectUserText(cmd, "text");
          overlay.style.display = "none";
        });
        row.appendChild(chip);
      });

      groupEl.appendChild(row);
      groupsWrap.appendChild(groupEl);
    });
    card.appendChild(groupsWrap);

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Search examples";
    input.className = "modal-search";

    const ul = document.createElement("ul");
    ul.className = "help-list";

    const render = (q = "") => {
      clear(ul);
      HELP_EXAMPLES.filter((x) => x.toLowerCase().includes(q.toLowerCase())).forEach((example) => {
        const li = document.createElement("li");
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = example;
        b.addEventListener("click", () => {
          injectUserText(example, "text");
          overlay.style.display = "none";
        });
        li.appendChild(b);
        ul.appendChild(li);
      });
    };

    input.addEventListener("input", () => render(input.value || ""));
    card.appendChild(input);
    card.appendChild(ul);
    render();
  }
  overlay.style.display = "flex";
}

async function refreshPrivacyPanel() {
  const items = {
    listening: "Off (only when you press mic)",
    background: "Off",
    network: "Only when asked",
    execution: "Governed",
  };

  try {
    const res = await fetch(`${API_BASE}/phase-status`);
    if (res.ok) {
      const data = await res.json();
      items.execution = data.execution_enabled ? "Enabled through governor" : "Disabled";
    }
  } catch (_) {}

  const host = $("privacy-list");
  if (!host) return;
  clear(host);

  Object.entries(items).forEach(([k, v]) => {
    const li = document.createElement("li");
    li.textContent = `${k}: ${v}`;
    host.appendChild(li);
  });
}

function showPrivacyModal() {
  let overlay = $("privacy-modal");
  if (!overlay) {
    const shell = createModalShell("privacy-modal", "Privacy and Safety");
    overlay = shell.overlay;
    const card = shell.card;

    const ul = document.createElement("ul");
    ul.id = "privacy-list";
    ul.className = "privacy-list";
    card.appendChild(ul);
  }

  refreshPrivacyPanel();
  overlay.style.display = "flex";
}

function applyAccessibilityFromStorage() {
  const body = document.body;
  if (!body) return;

  const largeText = localStorage.getItem(STORAGE_KEYS.uiLargeText) === "1";
  const highContrast = localStorage.getItem(STORAGE_KEYS.uiHighContrast) === "1";
  const compactDensity = localStorage.getItem(STORAGE_KEYS.uiCompactDensity) === "1";
  body.classList.toggle("a11y-large-text", largeText);
  body.classList.toggle("a11y-high-contrast", highContrast);
  body.classList.toggle("density-compact", compactDensity);
}

function showAccessibilityModal() {
  let overlay = $("accessibility-modal");
  if (!overlay) {
    const shell = createModalShell("accessibility-modal", "Accessibility");
    overlay = shell.overlay;
    const card = shell.card;

    const row = document.createElement("div");
    row.className = "toggle-grid";

    const mkToggle = (label, key) => {
      const wrap = document.createElement("label");
      wrap.className = "toggle-item";
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = localStorage.getItem(key) === "1";
      cb.addEventListener("change", () => {
        localStorage.setItem(key, cb.checked ? "1" : "0");
        applyAccessibilityFromStorage();
      });
      const span = document.createElement("span");
      span.textContent = label;
      wrap.appendChild(cb);
      wrap.appendChild(span);
      return wrap;
    };

    row.appendChild(mkToggle("Large text", STORAGE_KEYS.uiLargeText));
    row.appendChild(mkToggle("High contrast", STORAGE_KEYS.uiHighContrast));
    row.appendChild(mkToggle("Compact density", STORAGE_KEYS.uiCompactDensity));
    card.appendChild(row);
  }

  overlay.style.display = "flex";
}

function showQuickCustomizeModal() {
  let overlay = $("quick-customize-modal");
  if (overlay) overlay.remove();

  const page = getActivePage();
  const actions = getQuickActionsForPage(page);

  const shell = createModalShell("quick-customize-modal", "Customize quick actions");
  overlay = shell.overlay;
  const card = shell.card;

  const selected = new Set(getSelectedQuickActions(page, actions));
  const row = document.createElement("div");
  row.className = "toggle-grid";

  actions.forEach((a) => {
    const wrap = document.createElement("label");
    wrap.className = "toggle-item";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = selected.has(a.id);
    cb.addEventListener("change", () => {
      if (cb.checked) selected.add(a.id);
      else selected.delete(a.id);
    });

    const span = document.createElement("span");
    span.textContent = a.label;
    wrap.appendChild(cb);
    wrap.appendChild(span);
    row.appendChild(wrap);
  });

  const save = document.createElement("button");
  save.type = "button";
  save.textContent = "Save";
  save.addEventListener("click", () => {
    const ids = actions.map((a) => a.id).filter((id) => selected.has(id));
    saveSelectedQuickActions(page, ids.length ? ids : actions.map((a) => a.id));
    renderQuickActions();
    overlay.style.display = "none";
  });

  card.appendChild(row);
  card.appendChild(save);

  overlay.style.display = "flex";
}

function createHeaderMenu(id, title, currentText = "", currentId = "") {
  const details = document.createElement("details");
  details.className = "header-menu";
  details.id = id;

  const summary = document.createElement("summary");
  summary.className = "header-menu-toggle";
  summary.innerHTML = currentText
    ? `${title} <span class="header-menu-current" id="${currentId || `${id}-current-label`}">${currentText}</span>`
    : title;
  details.appendChild(summary);

  const panel = document.createElement("div");
  panel.className = "header-menu-panel";
  details.appendChild(panel);

  return { details, panel };
}

function injectHeaderMenus() {
  const host = $("header-menu-strip");
  if (!host || host.children.length > 0) return;

  const workspaceMenu = createHeaderMenu("workspace-menu", "Workspace", "Chat", "workspace-current-label");
  const workspaceLabel = document.createElement("div");
  workspaceLabel.className = "header-menu-label";
  workspaceLabel.textContent = "Views";
  workspaceMenu.panel.appendChild(workspaceLabel);

  const workspaceGrid = document.createElement("div");
  workspaceGrid.className = "header-menu-grid";
  [
    { label: "Chat", page: "chat" },
    { label: "News", page: "news" },
    { label: "Intro", page: "intro" },
    { label: "Home", page: "home" },
    { label: "Workspace", page: "workspace" },
    { label: "Memory", page: "memory" },
    { label: "Policies", page: "policy" },
    { label: "Trust", page: "trust" },
    { label: "Settings", page: "settings" },
  ].forEach((item) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "header-menu-item header-menu-page-btn";
    btn.dataset.page = item.page;
    btn.textContent = item.label;
    workspaceGrid.appendChild(btn);
  });
  workspaceMenu.panel.appendChild(workspaceGrid);
  host.appendChild(workspaceMenu.details);

  const controlsMenu = createHeaderMenu("controls-menu", "Controls");
  const controlsLabel = document.createElement("div");
  controlsLabel.className = "header-menu-label";
  controlsLabel.textContent = "Panels";
  controlsMenu.panel.appendChild(controlsLabel);
  const controlsGrid = document.createElement("div");
  controlsGrid.className = "header-menu-grid";
  [
    { label: "Help", fn: showHelpModal },
    { label: "First steps", fn: () => showFirstRunGuide(true) },
    { label: "Introduction", fn: () => setActivePage("intro") },
    { label: "Settings", fn: () => setActivePage("settings") },
    { label: "Tone", fn: showToneModal },
    { label: "Schedule", fn: showScheduleModal },
    { label: "Privacy", fn: showPrivacyModal },
    { label: "Accessibility", fn: showAccessibilityModal },
  ].forEach((item) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "header-menu-item";
    btn.textContent = item.label;
    btn.addEventListener("click", () => {
      closeHeaderMenus();
      item.fn();
    });
    controlsGrid.appendChild(btn);
  });
  controlsMenu.panel.appendChild(controlsGrid);
  host.appendChild(controlsMenu.details);

  const actionsMenu = createHeaderMenu("actions-menu", "Actions");
  const actionsLabel = document.createElement("div");
  actionsLabel.className = "header-menu-label";
  actionsLabel.textContent = "Quick runs";
  actionsMenu.panel.appendChild(actionsLabel);
  const actionsGrid = document.createElement("div");
  actionsGrid.className = "header-menu-grid";
  [
    { label: "System status", command: "system status", page: "chat" },
    { label: "Trust center", page: "trust", fn: () => setActivePage("trust") },
    { label: "Workspace board", page: "workspace", fn: () => setActivePage("workspace") },
    { label: "Explain this", command: "explain this", page: "chat" },
    { label: "Memory overview", command: "memory overview", page: "memory" },
    { label: "Show schedules", command: "show schedules", page: "chat" },
    { label: "Pattern status", command: "pattern status", page: "chat" },
    { label: "Review patterns", fn: openPatternReview },
    { label: "Today's news", command: "today's news", page: "chat" },
  ].forEach((item) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "header-menu-item";
    btn.textContent = item.label;
    btn.addEventListener("click", () => {
      closeHeaderMenus();
      if (item.fn) {
        item.fn();
        return;
      }
      if (item.page) setActivePage(item.page);
      injectUserText(item.command, "text");
    });
    actionsGrid.appendChild(btn);
  });
  actionsMenu.panel.appendChild(actionsGrid);
  host.appendChild(actionsMenu.details);
}

window.addEventListener("DOMContentLoaded", () => {
  applyAccessibilityFromStorage();
  injectHeaderMenus();
  setOrbStatus("READY");
  ensureDatalist();
  renderMorningPanel();
  renderContextInsight("");
  renderThreadMapWidget({});
  renderMemoryOverviewWidget({});
  renderToneOverviewWidget({});
  renderNotificationOverviewWidget({});
  renderPatternReviewWidget({});
  renderOperatorHealthWidget({});
  renderCapabilitySurfaceWidget({});
  renderTrustPanel();
  renderWorkspaceHomeWidget({});
  renderProjectStructureMapWidget({});
  renderWorkspaceBoardPage();
  renderPolicyCenterPage();
  renderTrustCenterPage();
  renderIntroPage();
  renderSettingsPage();
  renderIntelligenceBriefWidget();
  renderPersonalLayerWidget();
  renderQuickActions();
  setupHintsPanelToggle();
  renderCommandDiscovery();
  setupMorningWidgetToggle();
  setupPageNavigation();
  connectWebSocket();
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) hydrateDashboardWidgets();
  });
  window.addEventListener("focus", hydrateDashboardWidgets);
  ensureSingleWelcomeMessage();
  showFirstRunGuideIfNeeded();

  const sendBtn = $("send-btn");
  if (sendBtn) sendBtn.addEventListener("click", sendChat);

  const deepSeekBtn = $("deepseek-btn");
  if (deepSeekBtn) deepSeekBtn.addEventListener("click", requestDeepSeekSecondOpinion);

  const input = $("chat-input");
  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendChat();
    });
  }

  const newsBtn = $("btn-news");
  if (newsBtn) newsBtn.addEventListener("click", () => safeWSSend({ text: "news" }));

  const newsSummaryBtn = $("btn-news-summary");
  if (newsSummaryBtn) {
    newsSummaryBtn.addEventListener("click", () => {
      setActivePage("chat");
      injectUserText("today's news", "text");
    });
  }

  const newsRefreshBtn = $("btn-news-refresh");
  if (newsRefreshBtn) newsRefreshBtn.addEventListener("click", () => safeWSSend({ text: "news", silent_widget_refresh: true }));

  const newsSearchBtn = $("btn-news-search");
  if (newsSearchBtn) newsSearchBtn.addEventListener("click", runNewsSearch);

  const newsSearchInput = $("news-search-input");
  if (newsSearchInput) {
    newsSearchInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") runNewsSearch();
    });
  }

  const newsExpandBtn = $("btn-news-expand");
  if (newsExpandBtn) {
    newsExpandBtn.addEventListener("click", () => {
      newsExpanded = !newsExpanded;
      renderNewsWidget(latestNewsItems, $("news-summary")?.textContent || "", latestNewsCategories);
    });
  }

  const homeBriefBtn = $("btn-home-brief");
  if (homeBriefBtn) {
    homeBriefBtn.addEventListener("click", () => {
      setActivePage("chat");
      injectUserText("morning brief", "text");
    });
  }

  const homeExplainBtn = $("btn-home-explain");
  if (homeExplainBtn) {
    homeExplainBtn.addEventListener("click", () => {
      setActivePage("chat");
      injectUserText("explain this", "text");
    });
  }

  const homeResearchBtn = $("btn-home-research");
  if (homeResearchBtn) {
    homeResearchBtn.addEventListener("click", () => {
      setActivePage("chat");
      injectUserText("research latest technology policy updates", "text");
    });
  }

  const homeContinueProjectBtn = $("btn-home-continue-project");
  if (homeContinueProjectBtn) {
    homeContinueProjectBtn.addEventListener("click", () => {
      setActivePage("chat");
      injectUserText("show threads", "text");
    });
  }

  const homeThreadsBtn = $("btn-home-threads");
  if (homeThreadsBtn) homeThreadsBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("show threads", "text");
  });

  const homeMemoryPageBtn = $("btn-home-memory-page");
  if (homeMemoryPageBtn) homeMemoryPageBtn.addEventListener("click", () => setActivePage("memory"));

  const homeToneStatusBtn = $("btn-home-tone-status");
  if (homeToneStatusBtn) {
    homeToneStatusBtn.addEventListener("click", () => showToneModal());
  }

  const homeSchedulesBtn = $("btn-home-schedules");
  if (homeSchedulesBtn) {
    homeSchedulesBtn.addEventListener("click", () => showScheduleModal());
  }

  const homePatternStatusBtn = $("btn-home-pattern-status");
  if (homePatternStatusBtn) {
    homePatternStatusBtn.addEventListener("click", () => {
      setActivePage("chat");
      injectUserText("pattern status", "text");
    });
  }

  const homeSystemStatusBtn = $("btn-home-system-status");
  if (homeSystemStatusBtn) {
    homeSystemStatusBtn.addEventListener("click", () => {
      setActivePage("chat");
      injectUserText("system status", "text");
    });
  }

  const homeWorkspacePageBtn = $("btn-home-workspace-page");
  if (homeWorkspacePageBtn) homeWorkspacePageBtn.addEventListener("click", () => setActivePage("workspace"));

  const homeTrustPageBtn = $("btn-home-trust-page");
  if (homeTrustPageBtn) homeTrustPageBtn.addEventListener("click", () => setActivePage("trust"));

  const introHomeBtn = $("btn-intro-open-home");
  if (introHomeBtn) introHomeBtn.addEventListener("click", () => setActivePage("home"));

  const introWorkspaceBtn = $("btn-intro-open-workspace");
  if (introWorkspaceBtn) introWorkspaceBtn.addEventListener("click", () => setActivePage("workspace"));

  const introTrustBtn = $("btn-intro-open-trust");
  if (introTrustBtn) introTrustBtn.addEventListener("click", () => setActivePage("trust"));

  const introSettingsBtn = $("btn-intro-open-settings");
  if (introSettingsBtn) introSettingsBtn.addEventListener("click", () => setActivePage("settings"));

  const introBriefBtn = $("btn-intro-daily-brief");
  if (introBriefBtn) introBriefBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("daily brief", "text");
  });

  const workspaceHomeRefreshBtn = $("btn-workspace-home-refresh");
  if (workspaceHomeRefreshBtn) {
    workspaceHomeRefreshBtn.addEventListener("click", () => requestWorkspaceHomeRefresh(true));
  }

  const workspaceBoardRefreshBtn = $("btn-workspace-board-refresh");
  if (workspaceBoardRefreshBtn) workspaceBoardRefreshBtn.addEventListener("click", () => requestWorkspaceHomeRefresh(true));

  const workspaceBoardThreadsBtn = $("btn-workspace-board-threads");
  if (workspaceBoardThreadsBtn) workspaceBoardThreadsBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("show threads", "text");
  });

  const workspaceBoardVisualBtn = $("btn-workspace-board-visual");
  if (workspaceBoardVisualBtn) workspaceBoardVisualBtn.addEventListener("click", () => requestProjectStructureMapRefresh(true));

  const workspaceBoardArchitectureBtn = $("btn-workspace-board-architecture");
  if (workspaceBoardArchitectureBtn) workspaceBoardArchitectureBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("create analysis report on this repo architecture", "text");
  });

  const trustCenterRefreshBtn = $("btn-trust-center-refresh");
  if (trustCenterRefreshBtn) trustCenterRefreshBtn.addEventListener("click", () => {
    safeWSSend({ text: "trust center", silent_widget_refresh: true });
    safeWSSend({ text: "system status", silent_widget_refresh: true });
  });

  const trustCenterSystemBtn = $("btn-trust-center-system");
  if (trustCenterSystemBtn) trustCenterSystemBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("system status", "text");
  });

  const trustCenterWorkspaceBtn = $("btn-trust-center-workspace");
  if (trustCenterWorkspaceBtn) trustCenterWorkspaceBtn.addEventListener("click", () => setActivePage("workspace"));

  const trustCenterMemoryBtn = $("btn-trust-center-memory");
  if (trustCenterMemoryBtn) trustCenterMemoryBtn.addEventListener("click", () => setActivePage("memory"));

  const trustCenterVoiceCheckBtn = $("btn-trust-center-voice-check");
  if (trustCenterVoiceCheckBtn) trustCenterVoiceCheckBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("voice check", "text");
  });

  const trustCenterSettingsBtn = $("btn-trust-center-settings");
  if (trustCenterSettingsBtn) trustCenterSettingsBtn.addEventListener("click", () => setActivePage("settings"));

  const settingsOpenIntroBtn = $("btn-settings-open-intro");
  if (settingsOpenIntroBtn) settingsOpenIntroBtn.addEventListener("click", () => setActivePage("intro"));

  const settingsOpenTrustBtn = $("btn-settings-open-trust");
  if (settingsOpenTrustBtn) settingsOpenTrustBtn.addEventListener("click", () => setActivePage("trust"));

  const settingsOpenHomeBtn = $("btn-settings-open-home");
  if (settingsOpenHomeBtn) settingsOpenHomeBtn.addEventListener("click", () => setActivePage("home"));

  const settingsOpenPrivacyBtn = $("btn-settings-open-privacy");
  if (settingsOpenPrivacyBtn) settingsOpenPrivacyBtn.addEventListener("click", showPrivacyModal);

  const settingsOpenAccessibilityBtn = $("btn-settings-open-accessibility");
  if (settingsOpenAccessibilityBtn) settingsOpenAccessibilityBtn.addEventListener("click", showAccessibilityModal);

  const settingsVoiceStatusBtn = $("btn-settings-voice-status");
  if (settingsVoiceStatusBtn) settingsVoiceStatusBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("voice status", "text");
  });

  const settingsVoiceCheckBtn = $("btn-settings-voice-check");
  if (settingsVoiceCheckBtn) settingsVoiceCheckBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("voice check", "text");
  });

  const settingsToggleLargeText = $("settings-toggle-large-text");
  if (settingsToggleLargeText) settingsToggleLargeText.addEventListener("change", () => {
    localStorage.setItem(STORAGE_KEYS.uiLargeText, settingsToggleLargeText.checked ? "1" : "0");
    applyAccessibilityFromStorage();
    renderSettingsPage();
  });

  const settingsToggleHighContrast = $("settings-toggle-high-contrast");
  if (settingsToggleHighContrast) settingsToggleHighContrast.addEventListener("change", () => {
    localStorage.setItem(STORAGE_KEYS.uiHighContrast, settingsToggleHighContrast.checked ? "1" : "0");
    applyAccessibilityFromStorage();
    renderSettingsPage();
  });

  const settingsToggleCompactDensity = $("settings-toggle-compact-density");
  if (settingsToggleCompactDensity) settingsToggleCompactDensity.addEventListener("change", () => {
    localStorage.setItem(STORAGE_KEYS.uiCompactDensity, settingsToggleCompactDensity.checked ? "1" : "0");
    applyAccessibilityFromStorage();
    renderSettingsPage();
  });

  const memoryOverviewBtn = $("btn-memory-overview");
  if (memoryOverviewBtn) memoryOverviewBtn.addEventListener("click", () => sendSilentMemoryCommand("memory overview"));

  const memoryListBtn = $("btn-memory-list");
  if (memoryListBtn) memoryListBtn.addEventListener("click", () => {
    sendSilentMemoryCommand("list memories");
  });

  const memoryThreadsBtn = $("btn-memory-threads");
  if (memoryThreadsBtn) memoryThreadsBtn.addEventListener("click", () => {
    sendSilentMemoryCommand("memory list thread this");
  });

  const memoryRefreshBtn = $("btn-memory-refresh");
  if (memoryRefreshBtn) memoryRefreshBtn.addEventListener("click", () => {
    hydrateMemoryManagement(true);
  });

  const memoryReviewListBtn = $("btn-memory-review-list");
  if (memoryReviewListBtn) memoryReviewListBtn.addEventListener("click", () => sendSilentMemoryCommand("list memories"));

  const memoryListAllBtn = $("btn-memory-list-all");
  if (memoryListAllBtn) memoryListAllBtn.addEventListener("click", () => sendSilentMemoryCommand("list memories"));

  const memoryListActiveBtn = $("btn-memory-list-active");
  if (memoryListActiveBtn) memoryListActiveBtn.addEventListener("click", () => sendSilentMemoryCommand("memory list active"));

  const memoryListLockedBtn = $("btn-memory-list-locked");
  if (memoryListLockedBtn) memoryListLockedBtn.addEventListener("click", () => sendSilentMemoryCommand("memory list locked"));

  const memoryListDeferredBtn = $("btn-memory-list-deferred");
  if (memoryListDeferredBtn) memoryListDeferredBtn.addEventListener("click", () => sendSilentMemoryCommand("memory list deferred"));

  const memoryListCurrentThreadBtn = $("btn-memory-list-current-thread");
  if (memoryListCurrentThreadBtn) memoryListCurrentThreadBtn.addEventListener("click", () => sendSilentMemoryCommand("memory list thread this"));

  const memoryListRefreshSilentBtn = $("btn-memory-list-refresh-silent");
  if (memoryListRefreshSilentBtn) memoryListRefreshSilentBtn.addEventListener("click", () => {
    const filters = memoryCenterState.filters || {};
    if (String(filters.thread_name || "").trim()) {
      sendSilentMemoryCommand(`memory list thread ${String(filters.thread_name || "").trim()}`);
      return;
    }
    if (String(filters.thread_key || "").trim()) {
      sendSilentMemoryCommand(`memory list thread ${String(filters.thread_key || "").trim()}`);
      return;
    }
    if (String(filters.tier || "").trim()) {
      sendSilentMemoryCommand(`memory list ${String(filters.tier || "").trim()}`);
      return;
    }
    sendSilentMemoryCommand("list memories");
  });

  const memoryEditInput = $("memory-edit-input");
  if (memoryEditInput) {
    memoryEditInput.addEventListener("input", () => {
      memoryEditInput.dataset.userEdited = "true";
    });
  }

  const memoryDetailShowChatBtn = $("btn-memory-detail-show-chat");
  if (memoryDetailShowChatBtn) memoryDetailShowChatBtn.addEventListener("click", () => {
    const selected = getSelectedMemoryItem();
    if (!selected || !selected.id) return;
    injectUserText(`memory show ${selected.id}`, "text");
  });

  const memoryDetailEditBtn = $("btn-memory-detail-edit");
  if (memoryDetailEditBtn) memoryDetailEditBtn.addEventListener("click", () => {
    const selected = getSelectedMemoryItem();
    if (!selected || !selected.id || !memoryEditInput) return;
    const nextValue = String(memoryEditInput.value || "").trim();
    if (!nextValue) return;
    injectUserText(`edit memory ${selected.id}: ${nextValue}`, "text");
  });

  const memoryDetailLockBtn = $("btn-memory-detail-lock");
  if (memoryDetailLockBtn) memoryDetailLockBtn.addEventListener("click", () => {
    const selected = getSelectedMemoryItem();
    if (!selected || !selected.id) return;
    injectUserText(`memory lock ${selected.id}`, "text");
  });

  const memoryDetailUnlockBtn = $("btn-memory-detail-unlock");
  if (memoryDetailUnlockBtn) memoryDetailUnlockBtn.addEventListener("click", () => {
    const selected = getSelectedMemoryItem();
    if (!selected || !selected.id) return;
    injectUserText(`memory unlock ${selected.id}`, "text");
  });

  const memoryDetailDeferBtn = $("btn-memory-detail-defer");
  if (memoryDetailDeferBtn) memoryDetailDeferBtn.addEventListener("click", () => {
    const selected = getSelectedMemoryItem();
    if (!selected || !selected.id) return;
    injectUserText(`memory defer ${selected.id}`, "text");
  });

  const memoryDetailDeleteBtn = $("btn-memory-detail-delete");
  if (memoryDetailDeleteBtn) memoryDetailDeleteBtn.addEventListener("click", () => {
    const selected = getSelectedMemoryItem();
    if (!selected || !selected.id) return;
    injectUserText(`delete memory ${selected.id}`, "text");
  });

  const policyRefreshBtn = $("btn-policy-refresh");
  if (policyRefreshBtn) policyRefreshBtn.addEventListener("click", () => {
    requestPolicyOverviewRefresh(true);
  });

  const policyCreateCalendarBtn = $("btn-policy-create-calendar");
  if (policyCreateCalendarBtn) policyCreateCalendarBtn.addEventListener("click", () => {
    injectUserText("policy create weekday calendar snapshot at 8:00 am", "text");
  });

  const policyCreateWeatherBtn = $("btn-policy-create-weather");
  if (policyCreateWeatherBtn) policyCreateWeatherBtn.addEventListener("click", () => {
    injectUserText("policy create daily weather snapshot at 7:30 am", "text");
  });

  const policyOpenTrustBtn = $("btn-policy-open-trust");
  if (policyOpenTrustBtn) policyOpenTrustBtn.addEventListener("click", () => {
    setActivePage("trust");
    safeWSSend({ text: "trust center", silent_widget_refresh: true });
  });

  const policyOpenSettingsBtn = $("btn-policy-open-settings");
  if (policyOpenSettingsBtn) policyOpenSettingsBtn.addEventListener("click", () => {
    setActivePage("settings");
  });

  const micBtn = $("ptt-btn");
  if (micBtn) {
    micBtn.addEventListener("click", () => {
      const isRecording = mediaRecorder && mediaRecorder.state === "recording";
      if (!isRecording) startSTT();
      else stopSTT();
    });
  }
});
