/* Nova Dashboard - User-Friendly Runtime UX */

let ws = null;
let pendingThoughtMessageId = null;
let messageMeta = new Map();
let waitingForAssistant = false;
let latestNewsItems = [];
let latestNewsCategories = {};
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
let trustState = {
  mode: "Local-only",
  lastExternalCall: "None",
  dataEgress: "Read-only requests only",
  failureState: "Normal",
  consecutiveFailures: 0,
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
};

const QUICK_ACTIONS_BY_PAGE = {
  chat: [
    { id: "chat_brief", label: "Today's brief", command: "today's news" },
    { id: "chat_weather", label: "Weather", command: "weather" },
    { id: "chat_search", label: "Search web", command: "search latest technology news" },
    { id: "chat_system", label: "System status", command: "system status" },
    { id: "chat_doc_create", label: "New analysis doc", command: "create analysis report on global technology policy updates" },
    { id: "chat_doc_list", label: "List analysis docs", command: "list analysis docs" },
  ],
  news: [
    { id: "news_get", label: "Get headlines", command: "news", stayOnPage: true },
    { id: "news_sum", label: "Summarize all", command: "summarize all headlines", stayOnPage: true },
    { id: "news_brief", label: "Daily brief", command: "today's news", stayOnPage: true },
    { id: "news_compare", label: "Compare stories", command: "compare headlines 1 and 2", stayOnPage: true },
  ],
  home: [
    { id: "home_system", label: "System status", command: "system status", switchToPage: "chat" },
    { id: "home_calendar", label: "Calendar", command: "calendar", switchToPage: "chat" },
    { id: "home_weather", label: "Weather", command: "weather", switchToPage: "chat" },
  ],
};

const COMMAND_SUGGESTIONS = [
  "morning brief",
  "summarize all headlines",
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

function buildNewsItemSnippet(item) {
  const summary = String(item?.summary || "").trim();
  if (summary) return summary;
  const title = String(item?.title || "").trim();
  if (!title) return "No synopsis available for this headline.";
  return `Headline indicates: ${title}`;
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
  return "Processing";
}

function safeWSSend(message) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return false;
  ws.send(JSON.stringify(message));
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

function formatSystemSummary(data, summary = "") {
  const fallback = String(summary || "System status ready.").trim() || "System status ready.";
  if (!data || typeof data !== "object") return fallback;

  const health = String(data.health_state || "").trim();
  const cpu = Number(data.cpu_percent);
  const memory = Number(data.memory_percent);
  const disk = Number(data.disk_percent);
  const network = String(data.network_status || "").trim();

  const parts = [];
  if (health) parts.push(`Health ${health}`);
  if (Number.isFinite(cpu)) parts.push(`CPU ${Math.round(cpu)}%`);
  if (Number.isFinite(memory)) parts.push(`Memory ${Math.round(memory)}%`);
  if (Number.isFinite(disk)) parts.push(`Disk ${Math.round(disk)}%`);
  if (network) parts.push(`Network ${network}`);

  return parts.length ? parts.join(" · ") : fallback;
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

function renderTrustPanel() {
  const mode = $("trust-mode");
  const lastCall = $("trust-last-call");
  const egress = $("trust-egress");
  const failure = $("trust-failure");
  if (mode) mode.textContent = trustState.mode;
  if (lastCall) lastCall.textContent = trustState.lastExternalCall;
  if (egress) egress.textContent = trustState.dataEgress;
  if (failure) failure.textContent = trustState.failureState;
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
      chat: "Starter prompts for everyday chat.",
      news: "News actions for summaries and comparisons.",
      home: "Status and trust checks for your system.",
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
      { label: "Today's brief", command: "today's news" },
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
      { label: "Today's brief", command: "today's news" },
    ];
  }

  if (msg.includes("news") || msg.includes("headline")) {
    return [
      { label: "Summarize all", command: "summarize all headlines" },
      { label: "Today's brief", command: "today's news" },
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

function renderWeatherWidget(data) {
  const container = $("weather-widget");
  if (!container) return;
  clear(container);

  const h = document.createElement("h3");
  h.textContent = "Weather";
  container.appendChild(h);

  const line = document.createElement("div");
  line.className = "weather-line";
  line.textContent = (data && data.summary) || "Weather unavailable.";
  container.appendChild(line);
  morningState.weather = line.textContent;
  renderMorningPanel();

  const forecast = String((data && data.forecast) || "").trim();
  if (forecast) {
    const forecastLine = document.createElement("div");
    forecastLine.className = "weather-forecast";
    forecastLine.textContent = forecast;
    container.appendChild(forecastLine);
  }

  const alerts = Array.isArray(data?.alerts) ? data.alerts.filter((item) => String(item || "").trim()) : [];
  if (alerts.length > 0) {
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
  appendConfidenceBadge(meta, "Local read-only");
  if (alerts.length === 0) {
    appendConfidenceBadge(meta, "No active alerts");
  }
  const updated = String((data && data.updated_at) || "").trim();
  if (updated) {
    const stamp = document.createElement("span");
    stamp.textContent = `Updated ${updated}`;
    meta.appendChild(stamp);
  }
  container.appendChild(meta);
}

function updateNewsSummary(summaryText) {
  const summary = $("news-summary");
  if (!summary) return;
  summary.textContent = (summaryText || "").trim() || "Headlines loaded. Press 'Summarize headlines' for a briefing.";
}

function getOrderedNewsCategoryKeys(categories) {
  const safeCategories = (categories && typeof categories === "object") ? categories : {};
  const preferred = ["global", "political", "breaking", "tech", "markets"];
  const keys = Object.keys(safeCategories).filter((key) => {
    const bucket = safeCategories[key];
    return Array.isArray(bucket && bucket.items) && bucket.items.length > 0;
  });
  return [
    ...preferred.filter((key) => keys.includes(key)),
    ...keys.filter((key) => !preferred.includes(key)),
  ];
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
  summarizeCategoryBtn.textContent = "Summarize category";
  summarizeCategoryBtn.addEventListener("click", () => injectUserText(`summarize ${categoryKey} news`, "text"));
  categoryActions.appendChild(summarizeCategoryBtn);
  page.appendChild(categoryActions);

  const list = document.createElement("ul");
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
    summarizeBtn.textContent = "Summarize this";
    summarizeBtn.addEventListener("click", () => injectUserText(`summarize headline ${storyIndex}`, "text"));
    row.appendChild(summarizeBtn);

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
      summarizeBtn.textContent = "Summarize this";
      summarizeBtn.addEventListener("click", () => injectUserText(`summarize this result: ${item.title}`, "text"));
      actions.appendChild(summarizeBtn);

      if (index === 0 && results.length > 1) {
        const compareBtn = document.createElement("button");
        compareBtn.type = "button";
        compareBtn.className = "assistant-action-btn";
        compareBtn.textContent = "Compare top results";
        compareBtn.addEventListener("click", () => injectUserText("compare the top 3 search results", "text"));
        actions.appendChild(compareBtn);
      }
      div.appendChild(actions);

      container.appendChild(div);
    });

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

function injectUserText(text, channel = "text") {
  const clean = (text || "").trim();
  if (!clean) return;

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
        renderNewsWidget(msg.items, msg.summary || "", msg.categories || {});
        break;
      case "search":
        renderSearchWidget(msg.data);
        break;
      case "system":
        morningState.system = formatSystemSummary(msg.data || {}, msg.summary || "System status ready.");
        renderMorningPanel();
        break;
      case "calendar":
        morningState.calendar = msg.summary || msg.message || "No events scheduled today.";
        renderMorningPanel();
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
          renderTrustPanel();
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
  const normalized = page === "ops" ? "home" : page;
  const pages = {
    chat: $("page-chat"),
    news: $("page-news"),
    home: $("page-home"),
  };
  const target = pages[normalized] ? normalized : "chat";

  Object.entries(pages).forEach(([name, el]) => {
    if (!el) return;
    el.hidden = name !== target;
  });

  document.querySelectorAll(".page-btn").forEach((btn) => {
    const active = btn.dataset.page === target;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
  });

  localStorage.setItem(STORAGE_KEYS.activePage, target);
  renderQuickActions();

    if (latestNewsItems.length > 0) {
      renderNewsWidget(latestNewsItems, $("news-summary")?.textContent || "", latestNewsCategories);
    } else {
      setNewsExpandButton();
    }
}

function setupPageNavigation() {
  const buttons = document.querySelectorAll(".page-btn");
  if (!buttons || buttons.length === 0) return;

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
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

function showFirstRunGuideIfNeeded() {
  if (localStorage.getItem(STORAGE_KEYS.firstRunDone) === "1") return;

  const { overlay, card } = createModalShell("first-run-modal", "Welcome to Nova");
  const p = document.createElement("p");
  p.textContent = "Quick start (about 60 seconds):";
  card.appendChild(p);

  const steps = document.createElement("ol");
  steps.className = "help-list";
  ["Review dashboard snapshot", "Summarize top headlines", "Ask for your daily brief"].forEach((label) => {
    const li = document.createElement("li");
    li.textContent = label;
    steps.appendChild(li);
  });
  card.appendChild(steps);

  const row = document.createElement("div");
  row.className = "modal-actions";

  [
    { label: "Summarize headlines", cmd: "summarize all headlines" },
    { label: "Search something", cmd: "search for local events" },
    { label: "Read last reply", cmd: "speak that" },
  ].forEach((item) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = item.label;
    b.addEventListener("click", () => {
      injectUserText(item.cmd, "text");
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

function injectUtilityButtons() {
  const headerLeft = document.querySelector(".header-left");
  if (!headerLeft || $("utility-bar")) return;

  const bar = document.createElement("div");
  bar.id = "utility-bar";
  bar.className = "utility-bar";

  [
    { id: "btn-help", label: "Help", fn: showHelpModal },
    { id: "btn-privacy", label: "Privacy", fn: showPrivacyModal },
    { id: "btn-accessibility", label: "Accessibility", fn: showAccessibilityModal },
  ].forEach((item) => {
    const b = document.createElement("button");
    b.id = item.id;
    b.type = "button";
    b.className = "utility-btn";
    b.textContent = item.label;
    b.addEventListener("click", item.fn);
    bar.appendChild(b);
  });

  headerLeft.appendChild(bar);
}

window.addEventListener("DOMContentLoaded", () => {
  applyAccessibilityFromStorage();
  injectUtilityButtons();
  setOrbStatus("READY");
  ensureDatalist();
  renderMorningPanel();
  renderTrustPanel();
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

  const sendBtn = $("send-btn");
  if (sendBtn) sendBtn.addEventListener("click", sendChat);

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
      injectUserText("Summarize the news headlines on the dashboard.", "text");
    });
  }

  const newsExpandBtn = $("btn-news-expand");
  if (newsExpandBtn) {
    newsExpandBtn.addEventListener("click", () => {
      newsExpanded = !newsExpanded;
      renderNewsWidget(latestNewsItems, $("news-summary")?.textContent || "", latestNewsCategories);
    });
  }

  const micBtn = $("ptt-btn");
  if (micBtn) {
    micBtn.addEventListener("click", () => {
      const isRecording = mediaRecorder && mediaRecorder.state === "recording";
      if (!isRecording) startSTT();
      else stopSTT();
    });
  }
});
