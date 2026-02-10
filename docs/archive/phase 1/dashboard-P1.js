(function () {
  const WS_URL = "ws://localhost:18080/ws";

  const chatLog = document.getElementById("chat-log");
  const chatInput = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");

  const btnWeatherUpdate = document.getElementById("btn-weather-update");
  const btnNews = document.getElementById("btn-news");

  const weatherLine = document.getElementById("weather-line");
  const weatherAlerts = document.getElementById("weather-alerts");
  const weatherUpdated = document.getElementById("weather-updated");
  const weatherDetailsLink = document.getElementById("weather-details-link");

  const newsList = document.getElementById("news-list");

  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function addLine(label, text) {
    const row = document.createElement("div");
    row.className = "chat-line";
    row.innerHTML = `<span class="chat-label">${escapeHtml(label)}</span> ${escapeHtml(text)}`;
    chatLog.appendChild(row);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  function renderWeather(data, message) {
    weatherLine.textContent = message || "—";
    weatherAlerts.innerHTML = "";
    weatherDetailsLink.style.display = "none";

    if (data?.alerts?.length) {
      const div = document.createElement("div");
      div.className = `weather-alert ${data.severity || "advisory"}`;
      div.textContent = data.alerts[0];
      weatherAlerts.appendChild(div);

      if (data.alert_source_url) {
        weatherDetailsLink.href = data.alert_source_url;
        weatherDetailsLink.style.display = "inline-block";
      }
    }

    weatherUpdated.textContent =
      "Updated " +
      new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  }

  function renderNews(data) {
    newsList.innerHTML = "";
    for (const h of data?.headlines || []) {
      const li = document.createElement("li");
      li.innerHTML = `
        <a class="news-link" href="${escapeHtml(h.url)}" target="_blank" rel="noreferrer">
          ${escapeHtml(h.title)}
        </a>
        <span class="news-source">${escapeHtml(h.source)}</span>
      `;
      newsList.appendChild(li);
    }
  }

  function sendText(text) {
    if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;
    addLine("you", text);
    ws.send(text);
    chatInput.value = "";
  }

  const ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    // ✅ AUTO WEATHER ON LOAD (Step 2)
    ws.send("weather");
  };

   ws.onmessage = (evt) => {
    let msg;
    try {
      msg = JSON.parse(evt.data);
    } catch {
      return;
    }

    // ----------------------------------
    // End-of-turn marker (Phase-1 safe)
    // ----------------------------------
    if (msg.type === "chat_done") {
      return;
    }

    // ----------------------------------
    // Skill responses
    // ----------------------------------
    if (msg.type === "skill_response") {
      if (msg.skill === "weather") {
        renderWeather(msg.data || {}, msg.message || "");
      } else if (msg.skill === "news") {
        addLine("system", "Latest headlines are shown.");
        renderNews(msg.data || {});
      } else {
        addLine(msg.skill || "system", msg.message || "");
      }
    }
  };

  // ----------------------------------
  // Input + button handlers
  // ----------------------------------

  sendBtn.onclick = () => {
    sendText(chatInput.value);
  };

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendText(chatInput.value);
    }
  });

  if (btnWeatherUpdate) {
    btnWeatherUpdate.onclick = () => sendText("weather");
  }

  if (btnNews) {
    btnNews.onclick = () => sendText("news");
  }

})();
