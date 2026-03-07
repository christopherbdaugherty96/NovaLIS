/* Nova Dashboard - User-Friendly Runtime UX */

let ws = null;
let pendingThoughtMessageId = null;
let messageMeta = new Map();
let waitingForAssistant = false;
let latestNewsItems = [];
let newsExpanded = false;
let sttState = "READY";
let mediaRecorder = null;
let silenceTimer = null;
let morningState = {
  weather: "Loading...",
  news: "Loading...",
  system: "Loading...",
  calendar: "Coming soon",
};
let trustState = {
  mode: "Local-only",
  lastExternalCall: "None",
  dataEgress: "Read-only requests only",
  failureState: "Normal",
  consecutiveFailures: 0,
};

const API_BASE = "http://127.0.0.1:8000";
const STORAGE_KEYS = {
  firstRunDone: "nova_first_run_done",
  quickActions: "nova_quick_actions",
  uiLargeText: "nova_ui_large_text",
  uiHighContrast: "nova_ui_high_contrast",
};

const QUICK_ACTIONS = [
  { id: "brief", label: "Brief", command: "Morning." },
  { id: "weather", label: "Weather", command: "weather" },
  { id: "news", label: "News", command: "news" },
  { id: "system", label: "System", command: "System status." },
  { id: "search", label: "Search", command: "search for " },
  { id: "open", label: "Open", command: "open " },
];

const COMMAND_SUGGESTIONS = [
  "weather",
  "news",
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
  "weather",
  "news",
  "morning brief",
  "summarize all headlines",
  "track story AI regulation",
  "update tracked stories",
  "search for eclipse dates",
  "open youtube",
  "open documents",
  "system check",
  "speak that",
  "set volume 40",
  "set brightness 50",
];

function $(id) { return document.getElementById(id); }
function clear(el) { if (el) el.innerHTML = ""; }
function extractDomain(url) { return (url || "").replace(/^https?:\/\//, "").split("/")[0].trim().toLowerCase(); }

function setOrbStatus(state) {
  sttState = state;
  const el = $("orb-status");
  if (el) el.textContent = state;
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

function getSelectedQuickActions() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEYS.quickActions) || "[]");
    if (Array.isArray(stored) && stored.length) return stored;
  } catch (_) {}
  return QUICK_ACTIONS.map((a) => a.id);
}

function saveSelectedQuickActions(ids) {
  localStorage.setItem(STORAGE_KEYS.quickActions, JSON.stringify(ids));
}

function runQuickAction(action) {
  const input = $("chat-input");
  const found = QUICK_ACTIONS.find((a) => a.id === action);
  if (!found) return;

  if (action === "search" || action === "open") {
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

  const selected = new Set(getSelectedQuickActions());
  QUICK_ACTIONS.filter((a) => selected.has(a.id)).forEach((action) => {
    const btn = document.createElement("button");
    btn.className = "quick-action-btn";
    btn.type = "button";
    btn.dataset.action = action.id;
    btn.textContent = action.label;
    btn.addEventListener("click", () => runQuickAction(action.id));
    host.appendChild(btn);
  });

  const customize = document.createElement("button");
  customize.className = "quick-action-btn ghost";
  customize.type = "button";
  customize.id = "btn-quick-customize";
  customize.textContent = "Customize";
  customize.addEventListener("click", showQuickCustomizeModal);
  host.appendChild(customize);
}

function appendConfidenceBadge(container, label) {
  const badge = document.createElement("span");
  badge.className = "confidence-badge";
  badge.textContent = label;
  container.appendChild(badge);
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

  if (msg.includes("intelligence brief") || msg.includes("daily situation overview") || msg.includes("executive brief")) {
    return [
      { label: "Deeper analysis", command: "Analyze the top story in more depth." },
      { label: "Related stories", command: "Show related stories for the top headline." },
      { label: "Short summary", command: "Summarize this brief in 3 bullets." },
    ];
  }

  if (msg.includes("weather")) {
    return [
      { label: "Forecast", command: "Show weather forecast." },
      { label: "Morning brief", command: "Morning brief." },
      { label: "News", command: "news" },
    ];
  }

  if (msg.includes("not sure what you'd like me to do")) {
    return [
      { label: "Show brief", command: "brief" },
      { label: "Search web", command: "search for " },
      { label: "System status", command: "system status" },
    ];
  }

  if (msg.includes("news") || msg.includes("headline")) {
    return [
      { label: "Summarize all", command: "summarize all headlines" },
      { label: "Story tracker", command: "update tracked stories" },
      { label: "Compare stories", command: "compare stories ai regulation and semiconductor export controls" },
    ];
  }

  return [
    { label: "Brief", command: "brief" },
    { label: "Weather", command: "weather" },
    { label: "News", command: "news" },
  ];
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

function appendAssistantActions(parent, text, suggestedActions = null) {
  const operational = isOperationalMessage(text);
  const suggestions = Array.isArray(suggestedActions) && suggestedActions.length
    ? suggestedActions
    : deriveSuggestedActions(text);
  renderSuggestedActions(parent, suggestions);

  if (operational) {
    const row = document.createElement("div");
    row.className = "assistant-actions";
    const repeatBtn = document.createElement("button");
    repeatBtn.type = "button";
    repeatBtn.className = "assistant-action-btn";
    repeatBtn.textContent = "Repeat";
    repeatBtn.addEventListener("click", () => injectUserText("Please repeat that.", "text"));
    row.appendChild(repeatBtn);
    parent.appendChild(row);
    return;
  }

  const row = document.createElement("div");
  row.className = "assistant-actions";

  const actions = [
    { label: "Repeat", fn: () => injectUserText("Please repeat that.", "text") },
    { label: "Show sources", fn: () => injectUserText("Show sources for your last response.", "text") },
  ];
  actions.splice(1, 0, { label: "Shorter", fn: () => injectUserText("Please give a shorter version of your last response.", "text") });

  actions.forEach((item) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "assistant-action-btn";
    b.textContent = item.label;
    b.addEventListener("click", item.fn);
    row.appendChild(b);
  });

  parent.appendChild(row);
}

function appendChatMessage(role, text, messageId = null, confidence = "", suggestedActions = null) {
  const chat = $("chat-log");
  if (!chat) return;

  const div = document.createElement("div");
  div.className = `chat-${role}`;

  const textNode = document.createElement("span");
  const msgText = String(text || "");
  const LONG_TEXT_THRESHOLD = 420;
  if (role === "assistant" && msgText.length > LONG_TEXT_THRESHOLD) {
    const preview = msgText.slice(0, LONG_TEXT_THRESHOLD).trimEnd() + "...";
    textNode.textContent = preview;
    textNode.dataset.fullText = msgText;
    textNode.dataset.previewText = preview;
    textNode.dataset.expanded = "false";
    div.appendChild(textNode);

    const expandBtn = document.createElement("button");
    expandBtn.type = "button";
    expandBtn.className = "message-expand-btn";
    expandBtn.textContent = "Show more";
    expandBtn.addEventListener("click", () => {
      const expanded = textNode.dataset.expanded === "true";
      textNode.textContent = expanded ? textNode.dataset.previewText : textNode.dataset.fullText;
      textNode.dataset.expanded = expanded ? "false" : "true";
      expandBtn.textContent = expanded ? "Show more" : "Show less";
    });
    div.appendChild(expandBtn);
  } else {
    textNode.textContent = msgText;
    div.appendChild(textNode);
  }

  if (confidence && role === "assistant") {
    appendConfidenceBadge(div, confidence);
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
    appendAssistantActions(div, text || "", suggestedActions);
  }

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function showThoughtOverlay(anchor, thoughtData) {
  let overlay = document.getElementById("thought-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "thought-overlay";
    overlay.className = "thought-overlay";
    document.body.appendChild(overlay);
  }

  const reasons = (thoughtData.reason_codes || []).map((code) => `<li>${code.replace(/_/g, " ")}</li>`).join("");
  overlay.innerHTML = `<div class="thought-title">Escalation reasoning</div><ul>${reasons || "<li>No reason codes available</li>"}</ul>`;

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

  const meta = document.createElement("div");
  meta.className = "weather-meta";
  appendConfidenceBadge(meta, "Local read-only");
  container.appendChild(meta);

  const btn = document.createElement("button");
  btn.id = "btn-weather-update";
  btn.type = "button";
  btn.textContent = "Update";
  btn.addEventListener("click", () => safeWSSend({ text: "weather" }));
  container.appendChild(btn);
}

function updateNewsSummary(summaryText) {
  const summary = $("news-summary");
  if (!summary) return;
  summary.textContent = (summaryText || "").trim() || "Headlines loaded. Press 'Summarize headlines' for a briefing.";
}

function setNewsExpandButton() {
  const btn = $("btn-news-expand");
  if (!btn) return;
  const hasExtra = latestNewsItems.length > 3;
  btn.style.display = hasExtra ? "inline-block" : "none";
  btn.textContent = newsExpanded ? "Show brief" : "Expand details";
  btn.setAttribute("aria-pressed", newsExpanded ? "true" : "false");
}

function renderNewsWidget(items, summaryText = "") {
  const list = $("news-list");
  if (!list) return;
  clear(list);

  if (!Array.isArray(items) || items.length === 0) {
    latestNewsItems = [];
    const li = document.createElement("li");
    li.textContent = "No headlines available.";
    list.appendChild(li);
    updateNewsSummary("No headlines are available to summarize right now.");
    morningState.news = "No headlines available.";
    renderMorningPanel();
    setNewsExpandButton();
    return;
  }

  latestNewsItems = items.slice();
  updateNewsSummary(summaryText);
  morningState.news = (summaryText || items[0]?.title || "Headlines available.").trim();
  renderMorningPanel();

  const visibleItems = newsExpanded ? latestNewsItems : latestNewsItems.slice(0, 3);
  visibleItems.forEach((item, index) => {
    const li = document.createElement("li");

    const badge = document.createElement("span");
    badge.className = "citation-index";
    badge.textContent = `[${index + 1}]`;
    li.appendChild(badge);

    const a = document.createElement("a");
    a.href = item.url;
    const sourceLabel = (item.source || "").trim();
    a.textContent = sourceLabel ? `[${sourceLabel}] ${item.title}` : item.title;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    li.appendChild(a);

    const domain = extractDomain(item.url);
    if (domain) {
      const domainBadge = document.createElement("span");
      domainBadge.className = "domain-badge";
      domainBadge.textContent = domain;
      li.appendChild(domainBadge);
    }

    const conf = document.createElement("span");
    conf.className = "confidence-badge";
    conf.textContent = "Web result";
    li.appendChild(conf);

    list.appendChild(li);
  });

  setNewsExpandButton();
}

function renderSearchWidget(data) {
  const container = $("search-widget");
  if (container) {
    clear(container);

    if (!data || !Array.isArray(data.results) || data.results.length === 0) {
      container.textContent = "I could not find reliable results for that.";
      return;
    }

    data.results.forEach((item, index) => {
      const div = document.createElement("div");
      div.className = "search-result";

      const idx = document.createElement("span");
      idx.className = "citation-index";
      idx.textContent = `[${index + 1}]`;
      div.appendChild(idx);

      const a = document.createElement("a");
      a.href = item.url;
      a.textContent = item.title;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      div.appendChild(a);

      const domain = extractDomain(item.url);
      if (domain) {
        const domainBadge = document.createElement("span");
        domainBadge.className = "domain-badge";
        domainBadge.textContent = domain;
        div.appendChild(domainBadge);
      }

      appendConfidenceBadge(div, "Web result");
      container.appendChild(div);
    });
    return;
  }

  if (!data || !Array.isArray(data.results) || data.results.length === 0) {
    appendChatMessage("assistant", "I could not find reliable results for that.", null, "Web result");
    return;
  }

  data.results.forEach((item, index) => {
    const domain = extractDomain(item.url);
    appendChatMessage("assistant", `[${index + 1}] ${item.title} (${domain || "source"})\n${item.url}`, null, "Web result");
  });
}

function translateError(code, message) {
  const map = {
    input_too_long: "That message is a bit too long. Try a shorter sentence.",
    invalid_json: "I could not read that request. Please try again.",
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
      if (res.ok) {
        const data = await res.json();
        if (data.text && data.text.trim()) injectUserText(data.text, "voice");
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
  if (mediaRecorder && mediaRecorder.state === "recording") mediaRecorder.stop();
}

function connectWebSocket() {
  ws = new WebSocket("ws://127.0.0.1:8000/ws");

  ws.onopen = () => {
    trustState.mode = "Local-only";
    trustState.failureState = "Normal";
    trustState.consecutiveFailures = 0;
    renderTrustPanel();
    safeWSSend({ text: "weather" });
    safeWSSend({ text: "news" });
    safeWSSend({ text: "system status" });
    refreshPrivacyPanel();
  };

  ws.onmessage = (e) => {
    let msg;
    try { msg = JSON.parse(e.data); }
    catch { return; }

    switch (msg.type) {
      case "weather":
        renderWeatherWidget(msg.data);
        markExternalCall("Weather");
        markRecovered();
        break;
      case "news":
        renderNewsWidget(msg.items, msg.summary || "");
        markExternalCall("News");
        markRecovered();
        break;
      case "search":
        renderSearchWidget(msg.data);
        markExternalCall("Web search");
        markRecovered();
        break;
      case "system":
        morningState.system = msg.summary || "System status ready.";
        renderMorningPanel();
        markLocalMode();
        break;
      case "chat":
        appendChatMessage(
          "assistant",
          msg.message,
          msg.message_id || null,
          msg.confidence || "",
          msg.suggested_actions || null
        );
        maybeMarkReactiveFailureFromText(msg.message || "");
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
        markFailure("Temporary issue");
        appendChatMessage("assistant", translateError(msg.code, msg.message), null, "System status");
        break;
    }
  };

  ws.onclose = () => {
    waitingForAssistant = false;
    setThinkingBar(false);
    markFailure("Disconnected");
    setTimeout(connectWebSocket, 2000);
  };
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
  p.textContent = "Start with one of these:";
  card.appendChild(p);

  const row = document.createElement("div");
  row.className = "modal-actions";

  [
    { label: "Get weather", cmd: "weather" },
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

function showHelpModal() {
  let overlay = $("help-modal");
  if (!overlay) {
    const shell = createModalShell("help-modal", "How to ask Nova");
    overlay = shell.overlay;
    const card = shell.card;

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
  body.classList.toggle("a11y-large-text", largeText);
  body.classList.toggle("a11y-high-contrast", highContrast);
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
    card.appendChild(row);
  }

  overlay.style.display = "flex";
}

function showQuickCustomizeModal() {
  let overlay = $("quick-customize-modal");
  if (!overlay) {
    const shell = createModalShell("quick-customize-modal", "Customize quick actions");
    overlay = shell.overlay;
    const card = shell.card;

    const selected = new Set(getSelectedQuickActions());
    const row = document.createElement("div");
    row.className = "toggle-grid";

    QUICK_ACTIONS.forEach((a) => {
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
      const ids = QUICK_ACTIONS.map((a) => a.id).filter((id) => selected.has(id));
      saveSelectedQuickActions(ids.length ? ids : QUICK_ACTIONS.map((a) => a.id));
      renderQuickActions();
      overlay.style.display = "none";
    });

    card.appendChild(row);
    card.appendChild(save);
  }

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
  ensureDatalist();
  renderMorningPanel();
  renderTrustPanel();
  renderQuickActions();
  connectWebSocket();
  showFirstRunGuideIfNeeded();

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
      renderNewsWidget(latestNewsItems, $("news-summary")?.textContent || "");
    });
  }

  const weatherBtn = $("btn-weather-update");
  if (weatherBtn) weatherBtn.addEventListener("click", () => safeWSSend({ text: "weather" }));

  const micBtn = $("ptt-btn");
  if (micBtn) {
    micBtn.addEventListener("click", () => {
      const isRecording = mediaRecorder && mediaRecorder.state === "recording";
      if (!isRecording) startSTT();
      else stopSTT();
    });
  }
});
