/* =========================================================
   NovaLIS Dashboard — Phase 3 (Observer Only)
   ========================================================= */

/* =========================================================
   1. GLOBAL STATE
   ========================================================= */

let ws = null;
let pendingThoughtMessageId = null;
let messageMeta = new Map();
let waitingForAssistant = false;

// PHASE-3 STT STATE (UI-ONLY, DESCRIPTIVE)
let sttState = "READY"; // READY | LISTENING | PAUSED | PROCESSING
let mediaRecorder = null;
let silenceTimer = null;

// Transport-only base (adjust if same-origin)
const API_BASE = "http://127.0.0.1:8000";

/* =========================================================
   ORB STATUS (TEXT ONLY — NOT A CONTROL PLANE)
   ========================================================= */

function setOrbStatus(state) {
  sttState = state;
  const el = document.getElementById("orb-status");
  if (el) el.textContent = state;
  // NOTE: PAUSED is descriptive only. No logic depends on this.
}

/* =========================================================
   2. DOM HELPERS
   ========================================================= */

function $(id) {
  return document.getElementById(id);
}

function clear(el) {
  if (el) el.innerHTML = "";
}

// Guarded WebSocket send (calm failure)
function safeWSSend(message) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return false;
  ws.send(JSON.stringify(message));
  return true;
}


function setThinkingBar(visible) {
  const bar = $("thinking-bar");
  if (!bar) return;
  bar.style.display = visible ? "block" : "none";
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
  overlay.innerHTML = `
    <div class="thought-title">Escalation reasoning</div>
    <ul>${reasons || "<li>No reason codes available</li>"}</ul>
  `;

  const rect = anchor.getBoundingClientRect();
  overlay.style.left = `${Math.min(window.innerWidth - 300, rect.left)}px`;
  overlay.style.top = `${rect.bottom + 8}px`;
  overlay.style.display = "block";
}

function bindThoughtIndicator(button, messageId) {
  button.addEventListener("click", () => {
    if (!messageId) return;
    if (!safeWSSend({ type: "get_thought", message_id: messageId })) return;
    pendingThoughtMessageId = messageId;
  });
}

/* =========================================================
   3. WEATHER WIDGET (CANONICAL)
   Expects: { type:"weather", data:{...} }
   ========================================================= */

function renderWeatherWidget(data) {
  const container = $("weather-widget");
  if (!container) return;

  clear(container);

  if (!data || typeof data !== "object") {
    container.textContent = "Weather unavailable.";
    return;
  }

  const line = document.createElement("div");
  line.className = "weather-line";
  line.textContent = data.summary || "Weather unavailable.";
  container.appendChild(line);
}

/* =========================================================
   4. NEWS WIDGET (PHASE-3 CANONICAL)
   Expects: { type:"news", items:[...] }
   ========================================================= */

function renderNewsWidget(items) {
  const list = $("news-list");
  if (!list) return;

  clear(list);

  if (!Array.isArray(items) || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "No headlines available.";
    list.appendChild(li);
    return;
  }

  items.forEach(item => {
    const li = document.createElement("li");

    const a = document.createElement("a");
    a.href = item.url;
    a.textContent = item.title;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    li.appendChild(a);

    if (item.source) {
      const src = document.createElement("span");
      src.className = "news-source";
      src.textContent = ` (${item.source})`;
      li.appendChild(src);
    }

    list.appendChild(li);
  });
}

/* =========================================================
   5. SEARCH WIDGET (PHASE‑4)
   Expects: { type:"search", data:{ results:[{title,url}] } }
   ========================================================= */

function renderSearchWidget(data) {
  // Optional dedicated container – if it exists, use it.
  const container = $("search-widget");
  if (container) {
    clear(container);
    if (!data || !Array.isArray(data.results) || data.results.length === 0) {
      container.textContent = "No results found.";
      return;
    }
    data.results.forEach(item => {
      const div = document.createElement("div");
      div.className = "search-result";
      const a = document.createElement("a");
      a.href = item.url;
      a.textContent = item.title;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      div.appendChild(a);
      container.appendChild(div);
    });
  } else {
    // Fallback: show each result as a chat message
    if (!data || !Array.isArray(data.results) || data.results.length === 0) {
      appendChatMessage("assistant", "No results found.");
      return;
    }
    data.results.forEach(item => {
      appendChatMessage("assistant", `${item.title}\n${item.url}`);
    });
  }
}

/* =========================================================
   6. CHAT (USER-INITIATED ONLY)
   ========================================================= */

function appendChatMessage(role, text, messageId = null) {
  const chat = $("chat-log");
  if (!chat) return;

  const div = document.createElement("div");
  div.className = `chat-${role}`;

  const textNode = document.createElement("span");
  textNode.textContent = text;
  div.appendChild(textNode);

  if (role === "assistant" && messageId) {
    messageMeta.set(messageId, div);
    const thoughtBtn = document.createElement("button");
    thoughtBtn.className = "thought-indicator";
    thoughtBtn.type = "button";
    thoughtBtn.textContent = "ⓘ";
    thoughtBtn.title = "Show reasoning";
    div.appendChild(thoughtBtn);
    bindThoughtIndicator(thoughtBtn, messageId);
  }

  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

/* =========================================================
   SINGLE INGESTION PATH (Phase-3 Canonical)
   ========================================================= */

function injectUserText(text) {
  const clean = (text || "").trim();
  if (!clean) {
    console.log("[INGEST] Empty input - ignored");
    return;
  }
  
  console.log("[INGEST] Processing:", clean);
  
  // Single canonical path for ALL user input (typed + STT)
  appendChatMessage("user", clean);
  waitingForAssistant = true;
  setThinkingBar(true);
  
  // Phase-3 calm: if WS fails, just log, don't spam chat
  if (!safeWSSend({ text: clean })) {
    console.warn("[INGEST] WebSocket not ready - message dropped");
  }
}

/* =========================================================
   7. STT (PUSH-TO-TALK, PHASE-3 SAFE)
   ========================================================= */

async function startSTT() {
  // Prevent re-entry
  if (mediaRecorder) return;

  if (!navigator.mediaDevices || !window.MediaRecorder) return;

  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch {
    return;
  }

  setOrbStatus("LISTENING");

  const options = {};

// Prefer PCM for Whisper compatibility (Phase-3 safe)
if (MediaRecorder.isTypeSupported("audio/webm;codecs=pcm")) {
  options.mimeType = "audio/webm;codecs=pcm";
}
// Fallback to Opus only if PCM is unavailable
else if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
  options.mimeType = "audio/webm;codecs=opus";
}
// Last-resort fallback
else if (MediaRecorder.isTypeSupported("audio/webm")) {
  options.mimeType = "audio/webm";
}

if (!options.mimeType) {
  console.warn("[STT] No supported audio MIME type");
  stream.getTracks().forEach(t => t.stop());
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
      silenceTimer = setTimeout(() => {
        setOrbStatus("PAUSED"); // UI-only
      }, 1200);
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

      const res = await fetch(`${API_BASE}/stt/transcribe`, {
        method: "POST",
        body: form,
      });

      if (res.ok) {
        const data = await res.json();
console.log("[STT] HTTP ok:", res.ok, "status:", res.status);
console.log("[STT] response:", data);
console.log("[STT RESULT]", JSON.stringify(data.text));

        if (data.text && data.text.trim()) {
  injectUserText(data.text);  // ✅ Single canonical path
} else {
  // Phase-3 calm: silence → do nothing (no chat spam)
  console.log("[STT] Empty transcript - no action");
}
      }
    } finally {
      if (stream) stream.getTracks().forEach(t => t.stop());
      mediaRecorder = null;
      chunks.length = 0;
      setOrbStatus("READY");
    }
  };

  // Timeslice ensures PAUSED/LISTENING are truthful
  mediaRecorder.start(250);
}

function stopSTT() {
  clearTimeout(silenceTimer);
  silenceTimer = null;

  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
}

/* =========================================================
   8. WEBSOCKET HANDLING (PHASE-3 SAFE)
   ========================================================= */

function connectWebSocket() {
  ws = new WebSocket("ws://127.0.0.1:8000/ws");

  ws.onopen = () => {
    safeWSSend({ text: "weather" });
    safeWSSend({ text: "news" });
  };

  ws.onmessage = (e) => {
    let msg;
    try {
      msg = JSON.parse(e.data);
    } catch {
      return;
    }

    switch (msg.type) {
      case "weather":
        renderWeatherWidget(msg.data);
        break;
      case "news":
        renderNewsWidget(msg.items);
        break;
      case "search":
        renderSearchWidget(msg.data);
        break;
      case "chat":
        appendChatMessage("assistant", msg.message, msg.message_id || null);
        break;
      case "chat_done":
        waitingForAssistant = false;
        setThinkingBar(false);
        break;
      case "thought":
        if (pendingThoughtMessageId && msg.message_id === pendingThoughtMessageId) {
          const anchor = messageMeta.get(msg.message_id);
          if (anchor) showThoughtOverlay(anchor, msg.data || {});
          pendingThoughtMessageId = null;
        }
        break;
    }
  };

  ws.onclose = () => {
    waitingForAssistant = false;
    setThinkingBar(false);
    setTimeout(connectWebSocket, 2000);
  };
}

/* =========================================================
   9. USER INPUT (CHAT + STT)
   ========================================================= */

function sendChat() {
  const input = $("chat-input");
  if (!input) return;

  injectUserText(input.value);
  input.value = "";
}

/* =========================================================
   10. BOOTSTRAP
   ========================================================= */

window.addEventListener("DOMContentLoaded", () => {
  connectWebSocket();

  const sendBtn = $("send-btn");
  if (sendBtn) sendBtn.addEventListener("click", sendChat);

  const input = $("chat-input");
  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendChat();
    });
  }

  const micBtn = $("ptt-btn");
  if (micBtn) {
    micBtn.addEventListener("click", () => {
      const isRecording =
        mediaRecorder && mediaRecorder.state === "recording";
      if (!isRecording) startSTT();
      else stopSTT();
    });
  }
});