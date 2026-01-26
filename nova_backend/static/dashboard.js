/* =========================================================
   NovaLIS Dashboard — Phase 3 (Observer Only)
   ========================================================= */

/* =========================================================
   1. GLOBAL STATE
   ========================================================= */

let ws = null;

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
   5. CHAT (USER-INITIATED ONLY)
   ========================================================= */

function appendChatMessage(role, text) {
  const chat = $("chat-log");
  if (!chat) return;

  const div = document.createElement("div");
  div.className = `chat-${role}`;
  div.textContent = text;

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
  
  // Phase-3 calm: if WS fails, just log, don't spam chat
  if (!safeWSSend({ text: clean })) {
    console.warn("[INGEST] WebSocket not ready - message dropped");
  }
}

/* =========================================================
   6. STT (PUSH-TO-TALK, PHASE-3 SAFE)
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
   7. WEBSOCKET HANDLING (PHASE-3 SAFE)
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
      case "chat":
        appendChatMessage("assistant", msg.message);
        break;
    }
  };

  ws.onclose = () => {
    setTimeout(connectWebSocket, 2000);
  };
}

/* =========================================================
   8. USER INPUT (CHAT + STT)
   ========================================================= */

function sendChat() {
  const input = $("chat-input");
  if (!input) return;

  injectUserText(input.value);
  input.value = "";
}

/* =========================================================
   9. BOOTSTRAP
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
