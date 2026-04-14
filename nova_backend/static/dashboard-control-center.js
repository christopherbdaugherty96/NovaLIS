/* Nova Dashboard - Control Center Surfaces */

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
  const fromRuntime = String(settingsRuntimeState.setupMode || "").trim().toLowerCase();
  if (["local", "bring_your_own_key", "managed_cloud"].includes(fromRuntime)) {
    return fromRuntime;
  }
  const stored = String(localStorage.getItem(STORAGE_KEYS.setupMode) || "local").trim().toLowerCase();
  return ["local", "bring_your_own_key", "managed_cloud"].includes(stored) ? stored : "local";
}

function applyRuntimeSettingsPayload(data) {
  const payload = (data && typeof data === "object" && data.settings && typeof data.settings === "object")
    ? data.settings
    : (data && typeof data === "object" ? data : {});
  const setupMode = ["local", "bring_your_own_key", "managed_cloud"].includes(String(payload.setup_mode || "").trim().toLowerCase())
    ? String(payload.setup_mode || "").trim().toLowerCase()
    : "local";
  settingsRuntimeState.loaded = true;
  settingsRuntimeState.setupMode = setupMode;
  settingsRuntimeState.setupModeLabel = String(payload.setup_mode_label || getSetupModeMeta(setupMode).label).trim() || getSetupModeMeta(setupMode).label;
  settingsRuntimeState.setupModeBadge = String(payload.setup_mode_badge || getSetupModeMeta(setupMode).badge).trim() || getSetupModeMeta(setupMode).badge;
  settingsRuntimeState.setupModeDescription = String(payload.setup_mode_description || getSetupModeMeta(setupMode).copy).trim() || getSetupModeMeta(setupMode).copy;
  settingsRuntimeState.permissions = (payload.permissions && typeof payload.permissions === "object")
    ? { ...payload.permissions }
    : {
      external_reasoning_enabled: true,
      remote_bridge_enabled: true,
      home_agent_enabled: true,
      home_agent_scheduler_enabled: false,
      metered_openai_enabled: false,
    };
  settingsRuntimeState.permissionCards = Array.isArray(payload.permission_cards)
    ? payload.permission_cards.map((item) => ({ ...item }))
    : [];
  settingsRuntimeState.providerPolicy = (payload.provider_policy && typeof payload.provider_policy === "object")
    ? { ...payload.provider_policy }
    : { ...settingsRuntimeState.providerPolicy };
  settingsRuntimeState.providerPolicyCards = Array.isArray(payload.provider_policy_cards)
    ? payload.provider_policy_cards.map((item) => ({ ...item }))
    : [];
  settingsRuntimeState.usageBudget = (payload.usage_budget && typeof payload.usage_budget === "object")
    ? { ...payload.usage_budget }
    : { ...settingsRuntimeState.usageBudget };
  settingsRuntimeState.usageBudgetCards = Array.isArray(payload.usage_budget_cards)
    ? payload.usage_budget_cards.map((item) => ({ ...item }))
    : [];
  settingsRuntimeState.assistivePolicy = (payload.assistive_policy && typeof payload.assistive_policy === "object")
    ? { ...payload.assistive_policy }
    : { ...settingsRuntimeState.assistivePolicy };
  settingsRuntimeState.assistivePolicyCards = Array.isArray(payload.assistive_policy_cards)
    ? payload.assistive_policy_cards.map((item) => ({ ...item }))
    : [];
  settingsRuntimeState.history = Array.isArray(payload.history) ? payload.history.map((item) => ({ ...item })) : [];
  settingsRuntimeState.summary = String(payload.summary || "").trim() || "Runtime settings loaded.";
  settingsRuntimeState.updatedAt = String(payload.updated_at || "").trim();
  settingsRuntimeState.lastHydratedAt = Date.now();
  localStorage.setItem(STORAGE_KEYS.setupMode, setupMode);

  if (data && typeof data === "object") {
    if (data.bridge && typeof data.bridge === "object") {
      trustReviewState.bridgeRuntime = { ...data.bridge };
    }
    if (data.connections && typeof data.connections === "object") {
      trustReviewState.connectionRuntime = { ...data.connections };
    }
    if (data.reasoning && typeof data.reasoning === "object") {
      trustReviewState.reasoningRuntime = { ...data.reasoning };
    }
  }
}

async function requestSettingsRuntimeRefresh(force = false) {
  const now = Date.now();
  if (
    !force
    && settingsRuntimeState.loaded
    && (now - Number(settingsRuntimeState.lastHydratedAt || 0)) < 15000
  ) {
    return;
  }

  settingsRuntimeState.loading = true;
  try {
    const res = await fetch(`${API_BASE}/api/settings/runtime`);
    if (!res.ok) throw new Error("settings_runtime_unavailable");
    const data = await res.json();
    applyRuntimeSettingsPayload(data);
    renderIntroPage();
    renderHomeLaunchWidget();
    renderTrustCenterPage();
    renderSettingsPage();
  } catch (_err) {
    if (!settingsRuntimeState.loaded) {
      settingsRuntimeState.summary = "Runtime settings are unavailable right now. Nova is using the local recommended defaults.";
    }
  } finally {
    settingsRuntimeState.loading = false;
  }
}

function applyOpenClawAgentPayload(data) {
  const wasLoaded = openClawAgentState.loaded;
  const payload = (data && typeof data === "object" && data.agent && typeof data.agent === "object")
    ? data.agent
    : (data && typeof data === "object" ? data : {});
  openClawAgentState.loaded = true;
  openClawAgentState.summary = String(payload.summary || "").trim() || "Nova can run tasks you review and approve before they take effect.";
  openClawAgentState.snapshot = { ...payload };
  openClawAgentState.templates = Array.isArray(payload.templates) ? payload.templates.map((item) => ({ ...item })) : [];
  openClawAgentState.activeRun = (payload.active_run && typeof payload.active_run === "object")
    ? { ...payload.active_run }
    : null;
  openClawAgentState.deliveryInbox = Array.isArray(payload.delivery_inbox) ? payload.delivery_inbox.map((item) => ({ ...item })) : [];
  openClawAgentState.recentRuns = Array.isArray(payload.recent_runs) ? payload.recent_runs.map((item) => ({ ...item })) : [];
  openClawAgentState.lastHydratedAt = Date.now();

  if (data && typeof data === "object") {
    if (data.bridge && typeof data.bridge === "object") {
      trustReviewState.bridgeRuntime = { ...data.bridge };
    }
    if (data.connections && typeof data.connections === "object") {
      trustReviewState.connectionRuntime = { ...data.connections };
    }
    if (data.settings && typeof data.settings === "object") {
      settingsRuntimeState.permissions = (data.settings.permissions && typeof data.settings.permissions === "object")
        ? { ...settingsRuntimeState.permissions, ...data.settings.permissions }
        : settingsRuntimeState.permissions;
    }
  }
  syncOpenClawDeliveryChatSurface(openClawAgentState.deliveryInbox, { initialLoad: !wasLoaded });
}

function syncOpenClawDeliveryChatSurface(items, { initialLoad = false } = {}) {
  const rows = Array.isArray(items) ? items : [];
  if (initialLoad) {
    rows.forEach((item) => {
      const id = String(item && item.id || "").trim();
      if (id) surfacedOpenClawDeliveryIds.add(id);
    });
    return;
  }

  rows.forEach((item) => {
    const id = String(item && item.id || "").trim();
    if (!id || surfacedOpenClawDeliveryIds.has(id)) return;
    surfacedOpenClawDeliveryIds.add(id);

    if (String(item && item.triggered_by || "").trim() !== "scheduler") return;
    const delivery = (item && item.delivery_channels && typeof item.delivery_channels === "object")
      ? item.delivery_channels
      : {};
    const message = String(item && (item.presented_message || item.summary) || "").trim();
    const usageMeta = (item && item.usage_meta && typeof item.usage_meta === "object")
      ? item.usage_meta
      : null;
    if (delivery.chat && message) {
      appendChatMessage("assistant", message, null, "Scheduled brief", null, usageMeta);
    }
  });
}

async function requestOpenClawAgentRefresh(force = false) {
  const now = Date.now();
  if (
    !force
    && openClawAgentState.loaded
    && (now - Number(openClawAgentState.lastHydratedAt || 0)) < 15000
  ) {
    return;
  }
  openClawAgentState.loading = true;
  try {
    const res = await fetch(`${API_BASE}/api/openclaw/agent/status`);
    if (!res.ok) throw new Error("openclaw_agent_unavailable");
    const data = await res.json();
    applyOpenClawAgentPayload(data);
    renderOpenClawDeliveryWidget();
    renderOpenClawAgentPage();
    renderIntroPage();
    renderSettingsPage();
    renderTrustCenterPage();
  } catch (_err) {
    if (!openClawAgentState.loaded) {
      openClawAgentState.summary = "Agent status is unavailable right now. Try refreshing in a moment.";
    }
  } finally {
    openClawAgentState.loading = false;
  }
}

async function setOpenClawAgentDeliveryMode(templateId, deliveryMode) {
  try {
    const res = await fetch(`${API_BASE}/api/openclaw/agent/templates/${encodeURIComponent(templateId)}/delivery`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ delivery_mode: deliveryMode }),
    });
    if (!res.ok) throw new Error("openclaw_agent_delivery_failed");
    const data = await res.json();
    applyOpenClawAgentPayload(data);
    renderOpenClawDeliveryWidget();
    renderOpenClawAgentPage();
    renderSettingsPage();
    renderTrustCenterPage();
  } catch (_err) {
    appendChatMessage("assistant", "I couldn't update that agent delivery mode right now.", null, "Agent");
  }
}

async function setOpenClawAgentScheduleEnabled(templateId, enabled) {
  try {
    const res = await fetch(`${API_BASE}/api/openclaw/agent/templates/${encodeURIComponent(templateId)}/schedule`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: !!enabled }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = String((data && data.detail) || "I couldn't update that agent schedule right now.").trim();
      appendChatMessage("assistant", detail, null, "Agent");
      return;
    }
    applyOpenClawAgentPayload(data);
    renderOpenClawDeliveryWidget();
    renderOpenClawAgentPage();
    renderSettingsPage();
    renderTrustCenterPage();
    if (enabled) {
      const schedulerReady = !!(data && data.agent && data.agent.scheduler_permission_enabled);
      appendChatMessage(
        "assistant",
        schedulerReady
          ? "Schedule enabled. Nova will run that template at its planned local time."
          : "Schedule saved. Turn on the scheduler in Settings when you want timed runs to start.",
        null,
        "Agent"
      );
    } else {
      appendChatMessage("assistant", "Schedule paused for that template.", null, "Agent");
    }
  } catch (_err) {
    appendChatMessage("assistant", "I couldn't update that agent schedule right now.", null, "Agent");
  }
}

async function runOpenClawAgentTemplate(templateId) {
  const template = (Array.isArray(openClawAgentState.templates) ? openClawAgentState.templates : [])
    .find((item) => String(item && item.id || "").trim() === String(templateId || "").trim());
  openClawAgentState.activeRun = {
    envelope_id: `optimistic-${Date.now()}`,
    template_id: String(templateId || "").trim(),
    title: String((template && template.title) || "Run").trim() || "Run",
    status: "running",
    status_label: "Starting now",
    triggered_by: "agent_page",
    delivery_mode: String((template && template.delivery_mode) || "widget").trim() || "widget",
    delivery_channels: template && template.delivery_mode === "chat"
      ? { chat: true, widget: false }
      : template && template.delivery_mode === "hybrid"
        ? { chat: true, widget: true }
        : { chat: false, widget: true },
    started_at: new Date().toISOString(),
    summary: "Gathering what this task needs and preparing your result.",
  };
  renderOpenClawDeliveryWidget();
  renderOpenClawAgentPage();
  try {
    const res = await fetch(`${API_BASE}/api/openclaw/agent/templates/${encodeURIComponent(templateId)}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = String((data && data.detail) || "I couldn't run that template right now.").trim();
      appendChatMessage("assistant", detail, null, "Agent");
      return;
    }
    applyOpenClawAgentPayload(data);
    renderOpenClawDeliveryWidget();
    renderOpenClawAgentPage();
    renderSettingsPage();
    renderTrustCenterPage();
    const run = (data && data.run && typeof data.run === "object") ? data.run : {};
    const delivery = (run.delivery_channels && typeof run.delivery_channels === "object") ? run.delivery_channels : {};
    const usageMeta = (run.usage_meta && typeof run.usage_meta === "object") ? run.usage_meta : null;
    if (delivery.chat && String(run.presented_message || "").trim()) {
      appendChatMessage("assistant", String(run.presented_message || "").trim(), null, "Task report", null, usageMeta);
    } else if (delivery.widget) {
      appendChatMessage("assistant", "That run is ready in the Agent delivery inbox.", null, "Agent");
    }
  } catch (_err) {
    openClawAgentState.activeRun = null;
    renderOpenClawDeliveryWidget();
    renderOpenClawAgentPage();
    appendChatMessage("assistant", "I couldn't run that home-agent template right now.", null, "Agent");
  }
}

async function cancelOpenClawActiveRun() {
  try {
    const res = await fetch(`${API_BASE}/api/openclaw/agent/runs/cancel`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = String((data && data.detail) || "No active run to cancel.").trim();
      appendChatMessage("assistant", detail, null, "Agent");
      return;
    }
    applyOpenClawAgentPayload(data);
    renderOpenClawDeliveryWidget();
    renderOpenClawAgentPage();
    appendChatMessage("assistant", "Cancel requested. The run will stop at the next checkpoint.", null, "Agent");
  } catch (_err) {
    appendChatMessage("assistant", "I couldn't cancel the active run right now.", null, "Agent");
  }
}

async function dismissOpenClawDelivery(deliveryId) {
  try {
    const res = await fetch(`${API_BASE}/api/openclaw/agent/delivery/${encodeURIComponent(deliveryId)}/dismiss`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error("openclaw_agent_delivery_dismiss_failed");
    const data = await res.json();
    applyOpenClawAgentPayload(data);
    renderOpenClawDeliveryWidget();
    renderOpenClawAgentPage();
    renderSettingsPage();
    renderTrustCenterPage();
  } catch (_err) {
    appendChatMessage("assistant", "I couldn't dismiss that agent delivery right now.", null, "Agent");
  }
}

function reportSettingsError(message) {
  appendChatMessage("assistant", message, null, "Settings");
}

async function setSetupMode(mode) {
  const normalized = String(mode || "").trim().toLowerCase();
  const nextMode = ["local", "bring_your_own_key", "managed_cloud"].includes(normalized) ? normalized : "local";
  try {
    const res = await fetch(`${API_BASE}/api/settings/runtime/setup-mode`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ setup_mode: nextMode }),
    });
    if (!res.ok) throw new Error("setup_mode_update_failed");
    const data = await res.json();
    applyRuntimeSettingsPayload(data);
    renderIntroPage();
    renderTrustCenterPage();
    renderSettingsPage();
  } catch (_err) {
    reportSettingsError("I couldn't update setup mode right now. Nova kept the previous setting.");
  }
}

async function setRuntimePermission(permission, enabled) {
  try {
    const res = await fetch(`${API_BASE}/api/settings/runtime/permissions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ permission, enabled: Boolean(enabled) }),
    });
    if (!res.ok) throw new Error("runtime_permission_update_failed");
    const data = await res.json();
    applyRuntimeSettingsPayload(data);
    renderTrustCenterPage();
    renderSettingsPage();
  } catch (_err) {
    reportSettingsError("I couldn't update that setting right now. Nova kept the previous permission.");
  }
}

async function setRuntimeProviderPolicy(patch = {}) {
  try {
    const res = await fetch(`${API_BASE}/api/settings/runtime/provider-policy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patch || {}),
    });
    if (!res.ok) throw new Error("runtime_provider_policy_update_failed");
    const data = await res.json();
    applyRuntimeSettingsPayload(data);
    renderTrustCenterPage();
    renderSettingsPage();
  } catch (_err) {
    reportSettingsError("I couldn't update the local-first AI routing policy right now.");
  }
}

async function setRuntimeUsageBudget(dailyMeteredTokenBudget, warningRatio = null) {
  try {
    const payload = { daily_metered_token_budget: Number(dailyMeteredTokenBudget || 0) };
    if (warningRatio !== null && warningRatio !== undefined) {
      payload.warning_ratio = Number(warningRatio);
    }
    const res = await fetch(`${API_BASE}/api/settings/runtime/usage-budget`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("runtime_usage_budget_update_failed");
    const data = await res.json();
    applyRuntimeSettingsPayload(data);
    renderTrustCenterPage();
    renderSettingsPage();
  } catch (_err) {
    reportSettingsError("I couldn't update the metered usage budget right now.");
  }
}

async function setAssistiveNoticeMode(mode) {
  try {
    const res = await fetch(`${API_BASE}/api/settings/runtime/assistive-mode`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assistive_notice_mode: mode }),
    });
    if (!res.ok) throw new Error("assistive_mode_update_failed");
    const data = await res.json();
    applyRuntimeSettingsPayload(data);
    renderTrustCenterPage();
    renderSettingsPage();
    requestAssistiveNoticesRefresh(true);
  } catch (_err) {
    reportSettingsError("I couldn't update assistive noticing mode right now.");
  }
}

async function resetRuntimeSettings() {
  try {
    const res = await fetch(`${API_BASE}/api/settings/runtime/reset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error("runtime_settings_reset_failed");
    const data = await res.json();
    applyRuntimeSettingsPayload(data);
    renderIntroPage();
    renderTrustCenterPage();
    renderSettingsPage();
  } catch (_err) {
    reportSettingsError("I couldn't restore the recommended defaults right now.");
  }
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
    memoryTotal > 0 ? `${memoryTotal} memory item${memoryTotal === 1 ? "" : "s"} saved.` : "No durable memory saved yet.",
    dueCount > 0 ? `${dueCount} schedule${dueCount === 1 ? "" : "s"} due now.` : "Nothing urgent is due.",
  ].filter(Boolean).join(" ");

  clear(grid);
  [
    {
      title: "Memory",
      copy: memoryTotal > 0 ? "Your saved memory is there when you want continuity." : "Memory stays empty until you explicitly save something.",
      chips: [`${memoryTotal} durable item${memoryTotal === 1 ? "" : "s"}`],
      action: () => setActivePage("memory"),
      actionLabel: "Open page",
    },
    {
      title: "Tone",
      copy: "Tone and response style stay easy to review and adjust.",
      chips: [String((toneState.snapshot && toneState.snapshot.global_profile_label) || "Balanced")],
      action: () => showToneModal(),
      actionLabel: "Settings",
    },
    {
      title: "Schedules",
      copy: dueCount > 0 ? "You have reminders waiting for review." : "Schedules stay quiet until something needs attention.",
      chips: [
        dueCount > 0 ? `${dueCount} due now` : "No items due",
        upcomingCount > 0 ? `${upcomingCount} upcoming` : "No upcoming",
      ],
      action: () => showScheduleModal(),
      actionLabel: "Review",
    },
    {
      title: "Pattern Review",
      copy: Boolean(patternReviewState.snapshot && patternReviewState.snapshot.opt_in_enabled)
        ? "Pattern review is on, but it stays advisory."
        : "Pattern review stays off unless you opt in.",
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
  bar.textContent = text || "Nova is thinking...";
}

function setThinkingBar(visible) {
  const bar = $("thinking-bar");
  if (!bar) return;
  bar.style.display = visible ? "flex" : "none";
  bar.setAttribute("aria-hidden", visible ? "false" : "true");
}

function renderTokenBudgetBar(data) {
  const bar = $("token-budget-bar");
  if (!bar) return;
  const budgetState = String(data.budget_state || "normal").trim();
  const remaining = Number(data.budget_remaining_tokens || 0);
  const label = String(data.budget_state_label || "").trim();

  if (budgetState === "limit") {
    bar.className = "token-budget-bar token-budget-bar--limit";
    bar.textContent = `Token budget reached — network actions paused. Reset in Settings → Usage.`;
    bar.style.display = "flex";
    bar.setAttribute("aria-hidden", "false");
  } else if (budgetState === "warning") {
    bar.className = "token-budget-bar token-budget-bar--warning";
    bar.textContent = `Token budget low — ${remaining.toLocaleString()} tokens remaining today.`;
    bar.style.display = "flex";
    bar.setAttribute("aria-hidden", "false");
  } else {
    bar.style.display = "none";
    bar.setAttribute("aria-hidden", "true");
    bar.className = "token-budget-bar";
    bar.textContent = "";
  }
}

function loadingHintForInput(text) {
  const q = (text || "").toLowerCase();
  if (q.includes("search") || q.includes("look up") || q.includes("research")) return "Checking online sources";
  if (q.includes("morning") || q.includes("brief") || q.includes("plan my day")) return "Preparing your brief";
  if (q.includes("explain this") || q.includes("what is this") || q.includes("analyze this") || q.includes("screenshot")) return "Analyzing visible context";
  if (q.includes("build") || q.includes("create") || q.includes("make") || q.includes("website") || q.includes("landing page")) return "Turning your idea into a build plan";
  if (q.includes("help me") || q.includes("plan")) return "Turning your goal into the next steps";
  return "Turning your request into the next step";
}

function compactWorkflowText(text, fallback = "") {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  if (!clean) return fallback;
  if (clean.length <= 150) return clean;
  return `${clean.slice(0, 147).trimEnd()}...`;
}

function extractWorkflowSentence(text, fallback = "") {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  if (!clean) return fallback;
  const match = clean.match(/(.+?[.!?])(?:\s|$)/);
  return compactWorkflowText(match ? match[1] : clean, fallback);
}

function workflowRequiresHighApproval(text) {
  const q = String(text || "").toLowerCase();
  return [
    "pay",
    "purchase",
    "buy",
    "checkout",
    "card",
    "wire",
    "send email",
    "email this",
    "publish",
    "post this",
    "sign in",
    "log in",
    "login",
    "domain",
  ].some((token) => q.includes(token));
}

function nextWorkflowHintForInput(text) {
  const q = String(text || "").toLowerCase();
  if (workflowRequiresHighApproval(q)) {
    return "Expect a clear approval checkpoint before Nova touches logins, publishing, or money.";
  }
  if (q.includes("build") || q.includes("create") || q.includes("make") || q.includes("website") || q.includes("page")) {
    return "Nova should draft the structure first, then help you refine it before the bigger build steps.";
  }
  if (q.includes("research") || q.includes("search") || q.includes("look up")) {
    return "Nova should bring back sources, a summary, and a suggested next move.";
  }
  if (q.includes("explain")) {
    return "Nova should explain what it sees first, then help you decide the next action.";
  }
  return "Nova should either give you the result, ask one useful follow-up, or show the next checkpoint.";
}

function workflowStatusForGoal(text) {
  const q = String(text || "").toLowerCase();
  if (!q) return "Ready";
  if (q.includes("build") || q.includes("create") || q.includes("make")) return "Planning";
  if (q.includes("research") || q.includes("search") || q.includes("look up")) return "Researching";
  if (q.includes("explain") || q.includes("analyze")) return "Reviewing";
  return "In progress";
}

function renderWorkflowFocusWidget() {
  const badge = $("workflow-focus-status-badge");
  const copy = $("workflow-focus-copy");
  const goal = $("workflow-focus-goal");
  const now = $("workflow-focus-now");
  const next = $("workflow-focus-next");
  const showStepsBtn = $("btn-workflow-show-steps");

  if (badge) badge.textContent = workflowFocusState.status || "Ready";
  if (copy) copy.textContent = workflowFocusState.copy || "Tell Nova the outcome you want, and it will turn that into the next steps.";
  if (goal) goal.textContent = workflowFocusState.goal || "Start with something simple like \"Build me a landing page for my business.\"";
  if (now) now.textContent = workflowFocusState.now || "Nova is ready to turn your idea into a workflow.";
  if (next) next.textContent = workflowFocusState.next || "You can start broad. Nova will draft, explain, and pause when a choice matters.";
  if (showStepsBtn) showStepsBtn.disabled = !String(workflowFocusState.lastUserInput || "").trim();
}

function resetWorkflowFocusState() {
  workflowFocusState = {
    goal: "Start with something simple like \"Build me a landing page for my business.\"",
    status: "Ready",
    copy: "Tell Nova the outcome you want, and it will turn that into the next steps.",
    now: "Nova is ready to turn your idea into a workflow.",
    next: "You can start broad. Nova will draft, explain, and pause when a choice matters.",
    lastUserInput: "",
    awaitingResponse: false,
  };
  renderWorkflowFocusWidget();
}

function updateWorkflowFocusFromUserInput(text) {
  const clean = String(text || "").trim();
  if (!clean) return;
  workflowFocusState.goal = compactWorkflowText(clean, workflowFocusState.goal);
  workflowFocusState.status = workflowStatusForGoal(clean);
  workflowFocusState.copy = "Nova is treating your last request as the current focus and will keep the next step visible.";
  workflowFocusState.now = compactWorkflowText(loadingHintForInput(clean), "Turning your request into the next step");
  workflowFocusState.next = nextWorkflowHintForInput(clean);
  workflowFocusState.lastUserInput = clean;
  workflowFocusState.awaitingResponse = true;
  renderWorkflowFocusWidget();
}

function updateWorkflowFocusProgress(text) {
  const clean = compactWorkflowText(text, "");
  if (!clean) return;
  workflowFocusState.now = clean;
  if (workflowFocusState.awaitingResponse && workflowFocusState.status === "Ready") {
    workflowFocusState.status = "In progress";
  }
  renderWorkflowFocusWidget();
}

function updateWorkflowFocusFromAssistant(text) {
  const clean = String(text || "").trim();
  if (!clean) return;
  workflowFocusState.status = "Ready for review";
  workflowFocusState.copy = "Nova finished the current step. You can refine it, move forward, or switch goals at any time.";
  workflowFocusState.now = extractWorkflowSentence(clean, "Nova finished the current step.");
  workflowFocusState.next = workflowRequiresHighApproval(workflowFocusState.lastUserInput)
    ? "If the next step affects logins, publishing, or money, Nova should pause for a fresh approval."
    : "Ask for edits, a deeper pass, or the next step when you are ready.";
  workflowFocusState.awaitingResponse = false;
  renderWorkflowFocusWidget();
}

function updateWorkflowFocusFromError(message) {
  workflowFocusState.status = "Needs adjustment";
  workflowFocusState.copy = "The current step hit a snag, but the goal is still in focus.";
  workflowFocusState.now = compactWorkflowText(message, "Something went wrong with the current step.");
  workflowFocusState.next = "Try rephrasing the goal, trimming the request, or asking Nova for a smaller next step.";
  workflowFocusState.awaitingResponse = false;
  renderWorkflowFocusWidget();
}

function safeWSSend(message, options = {}) {
  const queueIfUnavailable = Boolean(options && options.queueIfUnavailable);
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    if (queueIfUnavailable && message && typeof message === "object" && !Array.isArray(message)) {
      queueUserMessageForReconnect(message);
      scheduleWebSocketReconnect();
    }
    return false;
  }
  const payload = (message && typeof message === "object" && !Array.isArray(message)) ? { ...message } : message;
  if (payload && typeof payload === "object" && !Array.isArray(payload) && typeof payload.text === "string") {
    const channel = String(payload.channel || "text").toLowerCase();
    payload.channel = channel === "voice" ? "voice" : "text";
    if (!payload.invocation_source) {
      payload.invocation_source = payload.channel === "voice" ? "voice" : "ui";
    }
  }
  try {
    ws.send(JSON.stringify(payload));
  } catch (_) {
    if (queueIfUnavailable && payload && typeof payload === "object" && !Array.isArray(payload)) {
      queueUserMessageForReconnect(payload);
      scheduleWebSocketReconnect();
    }
    return false;
  }
  return true;
}

function renderMorningPanel() {
  const weather = $("morning-weather");
  const news = $("morning-news");
  const system = $("morning-system");
  const calendar = $("morning-calendar");
  const calendarConnectBtn = $("btn-morning-calendar-connect");
  if (weather) weather.textContent = morningState.weather;
  if (news) news.textContent = morningState.news;
  if (system) system.textContent = morningState.system;
  if (calendar) calendar.textContent = morningState.calendar;
  if (calendarConnectBtn) {
    const calendarText = String(morningState.calendar || "").trim().toLowerCase();
    calendarConnectBtn.hidden = !(calendarText.includes("not connected") || calendarText.includes("connect"));
  }
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

/* Workspace and continuity surfaces moved to dashboard-workspace.js. */

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
      const latestDecision = String((thread && thread.latest_decision) || "").trim();
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
      if (latestDecision) metaText += ` · Decision: ${latestDecision}`;
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
  const readinessSummary = $("policy-center-readiness-summary");
  const readinessLimit = $("policy-center-readiness-limit");
  const readinessHost = $("policy-center-readiness");
  const listHost = $("policy-center-list");
  const detailHost = $("policy-center-detail");
  const simulationHost = $("policy-center-simulation");
  const runHost = $("policy-center-run");
  if (!summary || !statsHost || !readinessSummary || !readinessLimit || !readinessHost || !listHost || !detailHost || !simulationHost || !runHost) return;

  const overview = (policyCenterState.overview && typeof policyCenterState.overview === "object")
    ? policyCenterState.overview
    : {};
  const items = Array.isArray(policyCenterState.items) ? policyCenterState.items : [];
  const readiness = getPolicyReadinessBuckets(policyCenterState.readiness);
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

  readinessSummary.textContent = readiness.summary || "Capability delegation guidance will appear here after the next policy refresh.";
  readinessLimit.textContent = readiness.currentLimit;
  clear(readinessHost);
  [
    { label: "Safe now", items: readiness.safeNow },
    { label: "Later", items: readiness.allowedLater },
    { label: "Explicit only", items: readiness.manualOnly },
  ].forEach((group) => {
    const card = document.createElement("div");
    card.className = "workspace-spotlight-card";

    const title = document.createElement("div");
    title.className = "workspace-spotlight-title";
    title.textContent = `${group.label} (${group.items.length})`;
    card.appendChild(title);

    const copy = document.createElement("div");
    copy.className = "workspace-spotlight-copy";
    copy.textContent = group.items.length
      ? group.items.slice(0, 4).map((item) => String(item.name || "").trim()).filter(Boolean).join(" · ")
      : "None right now.";
    card.appendChild(copy);

    group.items.slice(0, 4).forEach((item) => {
      const key = String(item.capability_id || "").trim();
      if (!key) return;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "assistant-action-btn";
      button.textContent = String(item.name || key).trim();
      if (policyCenterState.selectedReadinessKey === key) button.classList.add("active");
      button.addEventListener("click", () => {
        policyCenterState.selectedReadinessKey = key;
        renderPolicyCenterPage();
      });
      card.appendChild(button);
    });

    readinessHost.appendChild(card);
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

    const topology = (selected.topology && typeof selected.topology === "object") ? selected.topology : {};
    [
      ["Capability", String(topology.name || "Not mapped").trim() || "Not mapped"],
      ["Authority class", String(topology.authority_class || "unknown").trim() || "unknown"],
      ["Delegation class", String(topology.delegation_class || "observational").trim() || "observational"],
      ["Policy-delegatable", String(topology.policy_delegatable || "no").trim() || "no"],
      ["Within current limit", String(topology.within_current_limit || "no").trim() || "no"],
      ["Network required", String(topology.network_required || "no").trim() || "no"],
      ["Persistent change", String(topology.persistent_change || "no").trim() || "no"],
      ["External effect", String(topology.external_effect || "no").trim() || "no"],
      ["Why", String(topology.why || topology.envelope_notes || "No topology note available.").trim() || "No topology note available."],
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

      detailHost.appendChild(row);
    });

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
      ["Capability", String(simulation.capability_name || simulation.capability_id || "").trim()],
      ["Verdict", String(simulation.governor_verdict || "").trim()],
      ["Readiness", String(simulation.readiness_label || "").trim()],
      ["Capability class", String(simulation.capability_class || "").trim()],
      ["Delegation class", String(simulation.delegation_class || "").trim()],
      ["Envelope", String(simulation.envelope_summary || "").trim()],
      ["Current limit", String(simulation.current_authority_limit || "").trim()],
      ["Blocked reason", String(simulation.blocked_reason || "").trim()],
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
      ["Status", String(runResult.result.status || "").trim()],
      ["Reversible", runResult.result.reversible ? "yes" : "no"],
      ["External effect", runResult.result.external_effect ? "yes" : "no"],
      ["Outcome reason", String(runResult.result.outcome_reason || "").trim()],
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
  policyCenterState.readiness = (data && data.policy_capability_readiness && typeof data.policy_capability_readiness === "object")
    ? { ...data.policy_capability_readiness }
    : policyCenterState.readiness;
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
  if (!policyCenterState.selectedReadinessKey) {
    const readiness = getPolicyReadinessBuckets(policyCenterState.readiness);
    const firstCandidate = []
      .concat(readiness.safeNow, readiness.allowedLater, readiness.manualOnly)[0];
    if (firstCandidate) policyCenterState.selectedReadinessKey = String(firstCandidate.capability_id || "").trim();
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
    topology: item.topology || {},
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
  operatorHealthState.summary = String((data && data.operator_health_summary) || "Loading system health...").trim();

  const summary = $("operator-health-summary");
  const gridHost = $("operator-health-grid");
  const locksHost = $("operator-health-locks");
  const reasonsHost = $("operator-health-reasons");
  if (summary) {
    const governor = String(data.governor_status || "Unknown").trim() || "Unknown";
    const boundary = String(data.execution_boundary_status || "Unknown").trim() || "Unknown";
    const model = String(data.model_availability || "Unknown").trim() || "Unknown";
    summary.textContent = `Governor ${governor} · Boundary ${boundary} · Model ${model}`;
  }

  if (gridHost) {
    clear(gridHost);
    const rows = [
      ["Governor", String(data.governor_status || "Unknown").trim() || "Unknown"],
      ["Boundary", String(data.execution_boundary_status || "Unknown").trim() || "Unknown"],
      ["Model", String(data.model_availability || "Unknown").trim() || "Unknown"],
      ["Voice", String(data.voice_status || "Unknown").trim() || "Unknown"],
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
      items.slice(0, 2).forEach((item) => {
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
      items.slice(0, 1).forEach((item) => {
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

  renderHeaderStatus(activePageState);
  renderIntroPage();
  renderSettingsPage();
  renderTrustCenterPage();
}

function renderCapabilitySurfaceWidget(data = {}) {
  capabilityDiscoveryState.snapshot = (data && typeof data === "object") ? { ...data } : {};
  capabilityDiscoveryState.summary = String((data && data.capability_surface_summary) || "Loading live capabilities...").trim();

  const summary = $("capability-surface-summary");
  const groupsHost = $("capability-surface-groups");
  if (summary) {
    const groupsCount = Array.isArray(data.available_capability_surface) ? data.available_capability_surface.length : 0;
    summary.textContent = groupsCount
      ? `${groupsCount} capability group${groupsCount === 1 ? "" : "s"} are available right now.`
      : "Capabilities will appear here when Nova is ready to use them.";
  }
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

  groups.slice(0, 3).forEach((group) => {
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

      items.slice(0, 3).forEach((item) => {
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
    trustReviewState.policyReadiness = (data.policy_capability_readiness && typeof data.policy_capability_readiness === "object")
      ? { ...data.policy_capability_readiness }
      : trustReviewState.policyReadiness;
    trustReviewState.voiceRuntime = (data.voice_runtime && typeof data.voice_runtime === "object")
      ? { ...data.voice_runtime }
      : trustReviewState.voiceRuntime;
    trustReviewState.reasoningRuntime = (data.reasoning_runtime && typeof data.reasoning_runtime === "object")
      ? { ...data.reasoning_runtime }
      : trustReviewState.reasoningRuntime;
    trustReviewState.bridgeRuntime = (data.bridge_runtime && typeof data.bridge_runtime === "object")
      ? { ...data.bridge_runtime }
      : trustReviewState.bridgeRuntime;
    trustReviewState.connectionRuntime = (data.connection_runtime && typeof data.connection_runtime === "object")
      ? { ...data.connection_runtime }
      : trustReviewState.connectionRuntime;
    if (!trustReviewState.selectedActivityKey && trustReviewState.activity.length) {
      const first = trustReviewState.activity[0];
      trustReviewState.selectedActivityKey = String(first.request_id || first.ledger_ref || first.title || "0").trim();
    }
    if (!trustReviewState.selectedBlockedKey && trustReviewState.blocked.length) {
      const firstBlocked = trustReviewState.blocked[0];
      trustReviewState.selectedBlockedKey = String(firstBlocked.label || firstBlocked.area || "0").trim();
    }
    if (!trustReviewState.selectedPolicyCapabilityKey) {
      const readiness = trustReviewState.policyReadiness || {};
      const firstCandidate = []
        .concat(Array.isArray(readiness.safe_now) ? readiness.safe_now : [])
        .concat(Array.isArray(readiness.allowed_later) ? readiness.allowed_later : [])
        .concat(Array.isArray(readiness.manual_only) ? readiness.manual_only : [])[0];
      if (firstCandidate) trustReviewState.selectedPolicyCapabilityKey = String(firstCandidate.capability_id || "").trim();
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
  if (summary) {
    const activityCount = trustReviewState.activity.length;
    const blockedCount = trustReviewState.blocked.length;
    summary.textContent = [
      trustState.mode || "Local-only",
      blockedCount > 0 ? `${blockedCount} boundary${blockedCount === 1 ? "" : "issues"} active` : "No active boundary issues",
      activityCount > 0 ? `${activityCount} recent event${activityCount === 1 ? "" : "s"}` : "No recent events",
    ].filter(Boolean).join(" · ");
  }

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
      trustReviewState.activity.slice(0, 3).forEach((item) => {
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
        title.textContent = String(item.title || "Action").trim() || "Action";
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
      trustReviewState.blocked.slice(0, 2).forEach((item) => {
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

function getPolicyReadinessBuckets(snapshot = {}) {
  const readiness = (snapshot && typeof snapshot === "object") ? snapshot : {};
  return {
    summary: String(readiness.summary || "").trim(),
    currentLimit: String(readiness.current_authority_limit || "").trim() || "Unknown",
    safeNow: Array.isArray(readiness.safe_now) ? readiness.safe_now : [],
    allowedLater: Array.isArray(readiness.allowed_later) ? readiness.allowed_later : [],
    manualOnly: Array.isArray(readiness.manual_only) ? readiness.manual_only : [],
  };
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
  const policySummary = $("trust-center-policy-summary");
  const policyLimit = $("trust-center-policy-limit");
  const policyGroups = $("trust-center-policy-groups");
  const policyDetail = $("trust-center-policy-detail");
  const capabilitySummary = $("trust-center-capability-summary");
  const capabilityHost = $("trust-center-capability-groups");
  const voiceSummary = $("trust-center-voice-summary");
  const voiceGrid = $("trust-center-voice-grid");
  const reasoningSummary = $("trust-center-reasoning-summary");
  const reasoningGrid = $("trust-center-reasoning-grid");
  const bridgeSummary = $("trust-center-bridge-summary");
  const bridgeGrid = $("trust-center-bridge-grid");
  if (!summary || !mode || !lastCall || !egress || !failure || !activityHost || !blockedHost || !healthSummary || !healthGrid || !policySummary || !policyLimit || !policyGroups || !policyDetail || !capabilitySummary || !capabilityHost) return;

  summary.textContent = [
    String(trustReviewState.summary || "").trim(),
    "Use this page to confirm what Nova did, what it refused, and whether anything left the device.",
  ].filter(Boolean).join(" ") || "Use this page to confirm what Nova did, what it refused, and whether anything left the device.";
  mode.textContent = trustState.mode || "Local-only";
  lastCall.textContent = trustState.lastExternalCall || "None";
  egress.textContent = trustState.dataEgress || "Read-only requests only";
  failure.textContent = trustState.failureState || "Normal";

  clear(activityHost);
  if (!trustReviewState.activity.length) {
    const empty = document.createElement("div");
    empty.className = "trust-empty";
    empty.textContent = "As you use Nova, recent governed actions will appear here so you can confirm what happened.";
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
      title.textContent = String(item.title || "Action").trim() || "Action";
      row.appendChild(title);

      const meta = document.createElement("div");
      meta.className = "trust-activity-meta";
      meta.textContent = [
        String(item.kind || "").trim(),
        String(item.timestamp || "").trim(),
      ].filter(Boolean).join(" · ") || "Recent activity";
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
      empty.textContent = "Select a governed action to see what happened, why it ran, and what effect it had.";
      activityDetail.appendChild(empty);
    } else {
      const reasoningRows = [];
      if (String(selected.reasoning_provider || "").trim()) {
        reasoningRows.push(["Reasoning provider", String(selected.reasoning_provider || "").trim()]);
      }
      if (String(selected.reasoning_route || "").trim()) {
        reasoningRows.push(["Reasoning route", String(selected.reasoning_route || "").trim()]);
      }
      if (String(selected.reasoning_authority || "").trim()) {
        reasoningRows.push(["Reasoning authority", String(selected.reasoning_authority || "").trim()]);
      }
      if (String(selected.reasoning_governance_note || "").trim()) {
        reasoningRows.push(["Reasoning note", String(selected.reasoning_governance_note || "").trim()]);
      }
      const detailRows = [
        ["Title", String(selected.title || "Action").trim() || "Action"],
        ["Kind", String(selected.kind || "system").trim() || "system"],
        ["Status", String(selected.status || "unknown").trim() || "unknown"],
        ["When", String(selected.timestamp || "Unknown").trim() || "Unknown"],
        ["Capability", String(selected.capability_name || selected.capability_id || "Not recorded").trim() || "Not recorded"],
        ["Authority", String(selected.authority_class || "Not recorded").trim() || "Not recorded"],
        ["Reversible", String(selected.reversible || "Not recorded").trim() || "Not recorded"],
        ["External effect", String(selected.external_effect || "Not recorded").trim() || "Not recorded"],
        ...reasoningRows,
        ["Why", String(selected.reason || selected.detail || "No reason recorded.").trim() || "No reason recorded."],
        ["Effect", String(selected.effect || "No external effect").trim() || "No external effect"],
        ["Request", String(selected.request_id || "Not recorded").trim() || "Not recorded"],
        ["Ledger", String(selected.ledger_ref || "Not recorded").trim() || "Not recorded"],
      ];
      detailRows.forEach(([label, value]) => {
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
    empty.textContent = "No active boundaries need your attention right now.";
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
      empty.textContent = "Select a blocked condition to see which boundary Nova is honoring and what you can do next.";
      blockedDetail.appendChild(empty);
    } else {
      [
        ["Boundary", String(selectedBlocked.label || selectedBlocked.area || "Condition").trim() || "Condition"],
        ["Status", String(selectedBlocked.status || "unknown").trim() || "unknown"],
        ["Why blocked", String(selectedBlocked.reason || "No reason available.").trim() || "No reason available."],
        ["Next step", String(selectedBlocked.next_step || "No action needed right now.").trim() || "No action needed right now."],
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

  const readiness = getPolicyReadinessBuckets(trustReviewState.policyReadiness);
  policySummary.textContent = readiness.summary || "Capability delegation rules will appear here after the next trust refresh.";
  policyLimit.textContent = readiness.currentLimit;
  clear(policyGroups);
  [
    { label: "Safe now", items: readiness.safeNow },
    { label: "Later", items: readiness.allowedLater },
    { label: "Explicit only", items: readiness.manualOnly },
  ].forEach((group) => {
    const card = document.createElement("div");
    card.className = "workspace-spotlight-card";

    const title = document.createElement("div");
    title.className = "workspace-spotlight-title";
    title.textContent = `${group.label} (${group.items.length})`;
    card.appendChild(title);

    const copy = document.createElement("div");
    copy.className = "workspace-spotlight-copy";
    copy.textContent = group.items.length
      ? group.items.slice(0, 4).map((item) => String(item.name || "").trim()).filter(Boolean).join(" · ")
      : "None right now.";
    card.appendChild(copy);

    group.items.slice(0, 4).forEach((item) => {
      const key = String(item.capability_id || "").trim();
      if (!key) return;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "assistant-action-btn";
      btn.textContent = String(item.name || key).trim();
      if (trustReviewState.selectedPolicyCapabilityKey === key) btn.classList.add("active");
      btn.addEventListener("click", () => {
        trustReviewState.selectedPolicyCapabilityKey = key;
        renderTrustCenterPage();
      });
      card.appendChild(btn);
    });

    policyGroups.appendChild(card);
  });

  clear(policyDetail);
  const policySelected = []
    .concat(readiness.safeNow, readiness.allowedLater, readiness.manualOnly)
    .find((item) => String(item.capability_id || "").trim() === String(trustReviewState.selectedPolicyCapabilityKey || "").trim())
    || readiness.safeNow[0]
    || readiness.allowedLater[0]
    || readiness.manualOnly[0];
  if (!policySelected) {
    const empty = document.createElement("div");
    empty.className = "trust-empty";
    empty.textContent = "Delegation rules will appear here after the next runtime refresh.";
    policyDetail.appendChild(empty);
  } else {
    [
      ["Capability", String(policySelected.name || policySelected.capability_id || "Unknown").trim() || "Unknown"],
      ["Authority class", String(policySelected.authority_class || "unknown").trim() || "unknown"],
      ["Delegation class", String(policySelected.delegation_class || "observational").trim() || "observational"],
      ["Policy-delegatable", String(policySelected.policy_delegatable || "no").trim() || "no"],
      ["Within current limit", String(policySelected.within_current_limit || "no").trim() || "no"],
      ["Network required", String(policySelected.network_required || "no").trim() || "no"],
      ["Persistent change", String(policySelected.persistent_change || "no").trim() || "no"],
      ["External effect", String(policySelected.external_effect || "no").trim() || "no"],
      ["Why", String(policySelected.why || policySelected.envelope_notes || "No note available.").trim() || "No note available."],
    ].forEach(([label, value]) => {
      const row = document.createElement("div");
      row.className = "operator-health-row";
      const labelEl = document.createElement("div");
      labelEl.className = "operator-health-label";
      labelEl.textContent = label;
      const valueEl = document.createElement("div");
      valueEl.className = "operator-health-value";
      valueEl.textContent = value;
      row.appendChild(labelEl);
      row.appendChild(valueEl);
      policyDetail.appendChild(row);
    });
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
    const wakeWordEnabled = isHeyNovaWakeWordEnabled();
    voiceSummary.textContent = [
      String(voice.summary || "").trim(),
      wakeWordEnabled ? `Wake word available: "${HEY_NOVA_WAKE_WORD}"` : "Wake word off",
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
      ["Wake word", wakeWordEnabled ? `${HEY_NOVA_WAKE_WORD} available for live help` : "Wake word off"],
    ].forEach(([label, value]) => {
      voiceGrid.appendChild(createOverviewChip(label, value));
    });
  }

  if (reasoningSummary && reasoningGrid) {
    const reasoning = (trustReviewState.reasoningRuntime && typeof trustReviewState.reasoningRuntime === "object")
      ? trustReviewState.reasoningRuntime
      : {};
    reasoningSummary.textContent = [
      String(reasoning.summary || "").trim(),
      String(reasoning.reasoning_summary_line || "").trim(),
      String(reasoning.last_used || "").trim() && `Last used: ${String(reasoning.last_used || "").trim()}`,
      String(reasoning.usage_budget_state_label || "").trim() && `Usage: ${String(reasoning.usage_budget_state_label || "").trim()}`,
    ].filter(Boolean).join(" · ") || "Governed second-opinion status will appear here after the next trust refresh.";

    clear(reasoningGrid);
    [
      ["Provider", String(reasoning.provider_label || reasoning.provider || "DeepSeek").trim() || "DeepSeek"],
      ["Route", String(reasoning.route_label || "Governed second-opinion lane").trim() || "Governed second-opinion lane"],
      ["Authority", String(reasoning.authority_label || "Advisory only").trim() || "Advisory only"],
      ["Mode", String(reasoning.mode || "second_opinion").trim() || "second_opinion"],
      ["Availability", String(reasoning.status || "Unknown").trim() || "Unknown"],
      ["Last outcome", String(reasoning.last_outcome || "Not recorded").trim() || "Not recorded"],
      ["Bottom line", String(reasoning.reasoning_summary_line || "Not recorded").trim() || "Not recorded"],
      ["Main gap", String(reasoning.top_issue || "No major gap recorded").trim() || "No major gap recorded"],
      ["Best correction", String(reasoning.top_correction || "No specific correction recorded").trim() || "No specific correction recorded"],
      ["Estimated tokens today", `${Number(reasoning.usage_estimated_total_tokens || 0).toLocaleString()} ${String(reasoning.usage_measurement_label || "estimated tokens").toLowerCase()}`],
      ["Budget state", String(reasoning.usage_budget_state_label || "Normal").trim() || "Normal"],
      ["Budget remaining", `${Number(reasoning.usage_budget_remaining_tokens || 0).toLocaleString()} tokens`],
      ["Cost tracking", String(reasoning.usage_cost_tracking_label || "Exact cost tracking is not live yet").trim() || "Exact cost tracking is not live yet"],
    ].forEach(([label, value]) => {
      reasoningGrid.appendChild(createOverviewChip(label, value));
    });
  }

  if (bridgeSummary && bridgeGrid) {
    const bridge = (trustReviewState.bridgeRuntime && typeof trustReviewState.bridgeRuntime === "object")
      ? trustReviewState.bridgeRuntime
      : {};
    bridgeSummary.textContent = [
      String(bridge.summary || "").trim(),
      String(bridge.scope || "").trim(),
    ].filter(Boolean).join(" · ") || "Remote bridge status will appear here after the next trust refresh.";

    clear(bridgeGrid);
    [
      ["Status", String(bridge.status_label || bridge.status || "Unknown").trim() || "Unknown"],
      ["Transport", String(bridge.transport || "HTTP").trim() || "HTTP"],
      ["Authentication", String(bridge.auth || "Unknown").trim() || "Unknown"],
      ["Scope", String(bridge.scope || "Read and reasoning only").trim() || "Read and reasoning only"],
      ["Effectful actions", String(bridge.effectful_actions || "Blocked").trim() || "Blocked"],
      ["Continuity", String(bridge.continuity || "Stateless").trim() || "Stateless"],
      ["Endpoint", String(bridge.endpoint || "/api/openclaw/bridge/message").trim() || "/api/openclaw/bridge/message"],
    ].forEach(([label, value]) => {
      bridgeGrid.appendChild(createOverviewChip(label, value));
    });
  }

  renderOperationalContextWidget();
  requestOperationalContextRefresh();
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

function renderOpenClawDeliveryFeed(host, items = [], emptyText = "No agent deliveries are waiting right now.") {
  if (!host) return;
  clear(host);
  const rows = Array.isArray(items) ? items : [];
  if (!rows.length) {
    const empty = document.createElement("div");
    empty.className = "memory-detail-empty";
    empty.textContent = emptyText;
    host.appendChild(empty);
    return;
  }

  rows.forEach((item) => {
    const row = document.createElement("div");
    row.className = "trust-center-activity-item";

    const title = document.createElement("strong");
    title.textContent = String(item.title || "Delivery").trim() || "Delivery";

    const meta = document.createElement("div");
    const createdLabel = String(item.created_at || "").trim()
      ? new Date(String(item.created_at || "").trim()).toLocaleString()
      : "Unknown time";
    const channels = [];
    if (item.delivery_channels && item.delivery_channels.chat) channels.push("chat");
    if (item.delivery_channels && item.delivery_channels.widget) channels.push("page");
    meta.textContent = [
      createdLabel,
      formatOpenClawTriggerLabel(item.triggered_by),
      channels.length ? `shown in ${channels.join(" + ")}` : "",
      formatOpenClawDeliveryModeLabel(item.delivery_mode),
    ].filter(Boolean).join(" · ");

    const body = document.createElement("p");
    body.className = "workspace-board-section-copy";
    body.textContent = String(item.presented_message || item.summary || "").trim() || "Agent delivery recorded.";

    const actions = document.createElement("div");
    actions.className = "workspace-board-actions-toolbar";

    const openBtn = document.createElement("button");
    openBtn.type = "button";
    openBtn.textContent = "Open agent";
    openBtn.addEventListener("click", () => setActivePage("agent"));
    actions.appendChild(openBtn);

    if (item.delivery_channels && item.delivery_channels.chat) {
      const chatBtn = document.createElement("button");
      chatBtn.type = "button";
      chatBtn.textContent = "Go to chat";
      chatBtn.addEventListener("click", () => setActivePage("chat"));
      actions.appendChild(chatBtn);
    }

    const dismissBtn = document.createElement("button");
    dismissBtn.type = "button";
    dismissBtn.textContent = "Dismiss";
    dismissBtn.addEventListener("click", () => dismissOpenClawDelivery(String(item.id || "").trim()));
    actions.appendChild(dismissBtn);

    row.appendChild(title);
    row.appendChild(meta);
    row.appendChild(body);
    row.appendChild(actions);
    host.appendChild(row);
  });
}

function renderOpenClawDeliveryWidget() {
  const summary = $("agent-delivery-home-summary");
  const host = $("agent-delivery-list");
  const snapshot = (openClawAgentState.snapshot && typeof openClawAgentState.snapshot === "object")
    ? openClawAgentState.snapshot
    : {};
  const items = Array.isArray(openClawAgentState.deliveryInbox) ? openClawAgentState.deliveryInbox : [];
  const activeRun = getOpenClawActiveRun();

  if (summary) {
    summary.textContent = activeRun
      ? buildOpenClawActiveRunSummary(activeRun)
      : (String(snapshot.delivery_summary || "").trim() || "No agent deliveries are waiting right now.");
  }
  renderOpenClawDeliveryFeed(host, items, "No home-agent deliveries are waiting right now.");
}

function renderOpenClawAgentPage() {
  const summary = $("agent-page-summary");
  const runtimeGrid = $("agent-runtime-grid");
  const setupSummary = $("agent-setup-summary");
  const setupGrid = $("agent-setup-grid");
  const deliverySummary = $("agent-delivery-summary");
  const templateList = $("agent-template-list");
  const inboxSummary = $("agent-inbox-summary");
  const inboxList = $("agent-inbox-list");
  const runSummary = $("agent-run-summary");
  const runList = $("agent-run-list");
  const snapshot = (openClawAgentState.snapshot && typeof openClawAgentState.snapshot === "object")
    ? openClawAgentState.snapshot
    : {};
  const activeRun = getOpenClawActiveRun();
  const setup = (snapshot.setup && typeof snapshot.setup === "object")
    ? snapshot.setup
    : {};
  const permissionEnabled = !!(settingsRuntimeState.permissions && settingsRuntimeState.permissions.home_agent_enabled);
  const schedulerPermissionEnabled = !!(settingsRuntimeState.permissions && settingsRuntimeState.permissions.home_agent_scheduler_enabled);

  if (summary) {
    const runnableCount = Array.isArray(setup.runnable_template_ids) ? setup.runnable_template_ids.length : 0;
    const summaryBits = [
      String(openClawAgentState.summary || "").trim() || "Nova can run tasks you review and approve before they take effect.",
      permissionEnabled
        ? (runnableCount
          ? `${runnableCount} task${runnableCount === 1 ? "" : "s"} available to run.`
          : "Agent is on, but no tasks are ready yet.")
        : "Turn on the Agent in Settings to start running tasks.",
      activeRun ? buildOpenClawActiveRunSummary(activeRun) : "",
      schedulerPermissionEnabled
        ? "The narrow scheduler is available where a template is ready for it."
        : "Scheduling stays paused until you enable it in Settings.",
      String(snapshot.personality_summary || "").trim(),
    ];
    summary.textContent = summaryBits.filter(Boolean).join(" ");
  }

  if (runtimeGrid) {
    clear(runtimeGrid);
    [
      ["Status", String(snapshot.status_label || "Foundation live").trim() || "Foundation live"],
      ["How it runs", permissionEnabled ? (schedulerPermissionEnabled ? "Run now + scheduled briefings" : "Run now only") : "Paused in Settings"],
      ["Templates", `${Number(snapshot.template_count || 0)} total`],
      ["Ready to run", `${Number(snapshot.manual_run_count || 0)} ready`],
      ["Current task", activeRun ? (String(activeRun.title || "Run").trim() || "Run") : "None"],
      ["Safety checks", String(snapshot.strict_foundation_label || "Manual preflight active").trim() || "Manual preflight active"],
      ["Deliveries ready", `${Number(snapshot.delivery_ready_count || 0)} waiting`],
      ["How results appear", "Results can show up in chat, on this page, or both"],
      ["Background schedule", String(snapshot.scheduler_status_label || (schedulerPermissionEnabled ? "Enabled" : "Paused")).trim() || "Paused"],
      ["Schedules", String(snapshot.schedule_summary || "No template schedules enabled yet").trim() || "No template schedules enabled yet"],
    ].forEach(([label, value]) => {
      runtimeGrid.appendChild(createOverviewChip(label, value));
    });
  }

  if (setupSummary && setupGrid) {
    const guidanceBits = [];
    if (!permissionEnabled) {
      guidanceBits.push("Agent is paused in Settings.");
    } else if (Array.isArray(setup.runnable_template_ids) && setup.runnable_template_ids.length) {
      guidanceBits.push(`${setup.runnable_template_ids.length} task${setup.runnable_template_ids.length === 1 ? "" : "s"} can run right now.`);
    } else {
      guidanceBits.push("No tasks are ready to run on this device yet.");
    }
    if (!setup.local_model_ready) guidanceBits.push("The local summarizer is not ready yet.");
    if (!setup.weather_provider_configured) guidanceBits.push("Weather is optional and not configured.");
    if (!setup.calendar_connected) guidanceBits.push("Calendar is optional and not connected.");
    if (activeRun) guidanceBits.push(`${String(activeRun.title || "Run").trim() || "Run"} is currently running.`);
    setupSummary.textContent = [
      String(setup.summary || "").trim(),
      guidanceBits.join(" "),
    ].filter(Boolean).join(" ") || "Setup details will appear here after the next refresh.";
    clear(setupGrid);
    [
      ["Overall readiness", String(setup.status_label || "Unknown").trim() || "Unknown"],
      ["Ready to run", `${Array.isArray(setup.runnable_template_ids) ? setup.runnable_template_ids.length : 0} template(s)`],
      ["Schedule-ready", `${Array.isArray(setup.schedule_ready_template_ids) ? setup.schedule_ready_template_ids.length : 0} template(s)`],
      ["Local summarizer", setup.local_model_ready ? "Ready" : "Fallback mode"],
      ["Weather source", setup.weather_provider_configured ? "Configured" : "Optional"],
      ["Calendar source", setup.calendar_connected ? "Connected" : "Optional"],
      ["Remote access", setup.remote_bridge_enabled ? "Enabled" : (setup.remote_bridge_token_configured ? "Paused" : "Not configured")],
      ["Scheduler permission", setup.scheduler_permission_enabled ? "Enabled" : "Paused"],
    ].forEach(([label, value]) => {
      setupGrid.appendChild(createOverviewChip(label, value));
    });
  }

  if (deliverySummary) {
    deliverySummary.textContent = [
      String(snapshot.delivery_model_summary || "").trim(),
      "Choose whether results stay on the page, land in chat, or do both.",
    ].filter(Boolean).join(" ") || "Delivery preferences will appear here after the next agent refresh.";
  }

  if (inboxSummary) {
    inboxSummary.textContent = [
      String(snapshot.delivery_summary || "").trim(),
      "Review these before they fade into normal history.",
    ].filter(Boolean).join(" ") || "No completed surface deliveries are waiting right now.";
  }

  renderOpenClawDeliveryFeed(
    inboxList,
    Array.isArray(openClawAgentState.deliveryInbox) ? openClawAgentState.deliveryInbox : [],
    "No completed surface deliveries are waiting right now."
  );

  if (templateList) {
    clear(templateList);
    const templates = Array.isArray(openClawAgentState.templates) ? openClawAgentState.templates : [];
    if (!templates.length) {
      const empty = document.createElement("div");
      empty.className = "memory-detail-empty";
      empty.textContent = "No tasks are available yet.";
      templateList.appendChild(empty);
    } else {
      templates.forEach((template) => {
        const card = document.createElement("div");
        card.className = "widget page-card trust-center-panel openclaw-agent-card"
          + (!template.manual_run_available ? " openclaw-agent-card--unavailable" : "");

        const titleRow = document.createElement("div");
        titleRow.className = "workspace-board-section-header";
        const titleWrap = document.createElement("div");
        const title = document.createElement("div");
        title.className = "workspace-home-section-title";
        title.textContent = String(template.title || "Template").trim() || "Template";
        const copy = document.createElement("p");
        copy.className = "workspace-board-section-copy";
        copy.textContent = String(template.description || "").trim() || "Saved task.";
        titleWrap.appendChild(title);
        titleWrap.appendChild(copy);
        titleRow.appendChild(titleWrap);
        card.appendChild(titleRow);

        const chipRow = document.createElement("div");
        chipRow.className = "memory-detail-chip-row";
        const displayedScheduleStatus = !schedulerPermissionEnabled && template.schedule_enabled
          ? "Scheduled (paused globally)"
          : (String(template.schedule_status || template.next_run_label || "Paused").trim() || "Paused");
        [
          ["Category", String(template.category || "Task").trim() || "Task"],
          ["Availability", String(template.availability_label || "Unknown").trim() || "Unknown"],
          ["Delivery", formatOpenClawDeliveryModeLabel(template.delivery_mode)],
          ["Schedule", displayedScheduleStatus],
        ].forEach(([label, value]) => chipRow.appendChild(createOverviewChip(label, value)));
        card.appendChild(chipRow);

        const meta = document.createElement("p");
        meta.className = "first-run-note";
        const scheduleBits = [
          String(template.availability_reason || "").trim(),
          String(template.schedule_label || "").trim(),
          String(template.next_run_label || "").trim(),
          String(template.last_scheduled_outcome || "").trim()
            ? `Last scheduled run: ${String(template.last_scheduled_outcome || "").trim()}`
            : "",
          String(template.last_scheduled_note || "").trim(),
          (!schedulerPermissionEnabled && template.schedule_enabled) ? "Global scheduler is paused in Settings." : "",
        ].filter(Boolean);
        meta.textContent = scheduleBits.join(" · ");
        card.appendChild(meta);

        const tools = document.createElement("div");
        tools.className = "memory-detail-chip-row";
        (Array.isArray(template.tools_allowed) ? template.tools_allowed : []).forEach((tool) => {
          tools.appendChild(createOverviewChip("Tool", String(tool || "").trim() || "tool"));
        });
        card.appendChild(tools);

        const envelopePreview = getOpenClawEnvelopePreview(template);
        const previewCopy = document.createElement("p");
        previewCopy.className = "first-run-note";
        previewCopy.textContent = buildOpenClawBudgetLines(envelopePreview).join(" ")
          || "This task will show its safety limits here when it is ready.";
        card.appendChild(previewCopy);

        const previewChips = document.createElement("div");
        previewChips.className = "memory-detail-chip-row";
        [
          ["Steps", String(envelopePreview.max_steps || template.max_steps || 0)],
          ["Web requests", String(envelopePreview.max_network_calls || template.max_network_calls || 0)],
          ["Local files", String(envelopePreview.max_files_touched || template.max_files_touched || 0)],
          ["Can make changes", Number(envelopePreview.max_bytes_written || template.max_bytes_written || 0) > 0 ? "Yes" : "No"],
        ].forEach(([label, value]) => previewChips.appendChild(createOverviewChip(label, value)));
        card.appendChild(previewChips);

        const actions = document.createElement("div");
        actions.className = "workspace-board-actions-toolbar";

        const runBtn = document.createElement("button");
        runBtn.type = "button";
        const isThisTemplateRunning = !!activeRun && String(activeRun.template_id || "").trim() === String(template.id || "").trim();
        const cancelRequested = isThisTemplateRunning && !!(activeRun && activeRun.cancel_requested);
        runBtn.textContent = cancelRequested ? "Cancelling\u2026" : (isThisTemplateRunning ? "Running\u2026" : "Run now");
        runBtn.disabled = !permissionEnabled || !template.manual_run_available || !!activeRun;
        if (isThisTemplateRunning) {
          runBtn.classList.add(cancelRequested ? "openclaw-btn--cancelling" : "openclaw-btn--running");
        } else if (!template.manual_run_available) {
          runBtn.title = String(template.availability_reason || "This template requires a connector that is not yet available.").trim();
        } else if (activeRun) {
          runBtn.title = "Wait for the current home-agent run to finish before starting another one.";
        }
        runBtn.addEventListener("click", () => runOpenClawAgentTemplate(String(template.id || "").trim()));
        actions.appendChild(runBtn);

        const scheduleBtn = document.createElement("button");
        scheduleBtn.type = "button";
        if (!template.manual_run_available || !String(template.schedule_clock_local || "").trim()) {
          scheduleBtn.textContent = "Scheduling later";
          scheduleBtn.disabled = true;
        } else {
          scheduleBtn.textContent = template.schedule_enabled ? "Pause schedule" : "Enable schedule";
          if (template.schedule_enabled) {
            scheduleBtn.classList.add("assistant-action-btn");
          }
          scheduleBtn.addEventListener("click", () => setOpenClawAgentScheduleEnabled(String(template.id || "").trim(), !template.schedule_enabled));
        }
        actions.appendChild(scheduleBtn);

        ["widget", "chat", "hybrid"].forEach((mode) => {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.textContent = mode === "hybrid" ? "Chat + page" : mode === "chat" ? "Chat only" : "Page only";
          if (String(template.delivery_mode || "").trim() === mode) {
            btn.classList.add("assistant-action-btn");
          }
          btn.addEventListener("click", () => setOpenClawAgentDeliveryMode(String(template.id || "").trim(), mode));
          actions.appendChild(btn);
        });

        card.appendChild(actions);
        templateList.appendChild(card);
      });
    }
  }

  if (runSummary) {
    const recentRuns = Array.isArray(openClawAgentState.recentRuns) ? openClawAgentState.recentRuns : [];
    runSummary.textContent = activeRun
      ? `${buildOpenClawActiveRunSummary(activeRun)} Recent history stays just below so you can compare the live run against completed ones.`
      : recentRuns.length
        ? `Showing the latest ${recentRuns.length} home-agent runs so you can confirm what happened and how each result was delivered.`
        : "No home-agent runs are recorded yet. Start with a manual briefing template.";
  }

  if (runList) {
    clear(runList);
    const recentRuns = Array.isArray(openClawAgentState.recentRuns) ? openClawAgentState.recentRuns : [];
    if (activeRun) {
      const cancelRequested = !!(activeRun.cancel_requested);
      const activeItem = document.createElement("div");
      activeItem.className = "trust-center-activity-item"
        + (cancelRequested ? " openclaw-run-item--cancelling" : " openclaw-run-item--running");
      const activeTitle = document.createElement("strong");
      activeTitle.textContent = cancelRequested
        ? `${String(activeRun.title || "Run").trim() || "Run"} (Cancelling\u2026)`
        : `${String(activeRun.title || "Run").trim() || "Run"} (Running now)`;
      const activeMeta = document.createElement("div");
      activeMeta.textContent = [
        formatOpenClawRunTimestamp(activeRun.started_at),
        formatOpenClawTriggerLabel(activeRun.triggered_by),
        String(activeRun.status_label || "Running now").trim() || "Running now",
      ].filter(Boolean).join(" · ");
      const activeBody = document.createElement("p");
      activeBody.className = "workspace-board-section-copy";
      activeBody.textContent = cancelRequested
        ? "Cancel requested — the run will stop at the next safe checkpoint."
        : (String(activeRun.summary || "Gathering what it needs and preparing your result.").trim()
          || "Gathering what it needs and preparing your result.");
      const activeBudget = document.createElement("div");
      activeBudget.className = "memory-detail-empty";
      activeBudget.textContent = [
        String(activeRun.scope_summary || "").trim(),
        String(activeRun.budget_summary || "").trim(),
        buildOpenClawBudgetUsageLine(activeRun.budget_usage),
      ].filter(Boolean).join(" ");
      const activeActions = document.createElement("div");
      activeActions.className = "workspace-board-actions-toolbar";
      const cancelBtn = document.createElement("button");
      cancelBtn.type = "button";
      cancelBtn.textContent = cancelRequested ? "Cancelling\u2026" : "Cancel run";
      cancelBtn.disabled = cancelRequested;
      if (!cancelRequested) {
        cancelBtn.classList.add("openclaw-btn--cancel");
        cancelBtn.addEventListener("click", () => cancelOpenClawActiveRun());
      }
      activeActions.appendChild(cancelBtn);
      activeItem.appendChild(activeTitle);
      activeItem.appendChild(activeMeta);
      activeItem.appendChild(activeBody);
      if (activeBudget.textContent) activeItem.appendChild(activeBudget);
      activeItem.appendChild(activeActions);
      runList.appendChild(activeItem);
    }
    if (!recentRuns.length) {
      const empty = document.createElement("div");
      empty.className = "memory-detail-empty";
      empty.textContent = activeRun
        ? "The current run is visible above. Completed history will appear here after it finishes."
        : "Run a manual briefing template to see operator history here.";
      runList.appendChild(empty);
    } else {
      recentRuns.forEach((run) => {
        const runStatus = String(run.status || "completed").trim();
        const isFailed = runStatus === "failed";
        const isCancelled = runStatus === "cancelled";
        const item = document.createElement("div");
        item.className = "trust-center-activity-item"
          + (isFailed ? " openclaw-run-item--failed" : "")
          + (isCancelled ? " openclaw-run-item--cancelled" : "");
        const title = document.createElement("strong");
        title.textContent = String(run.title || "Run").trim() || "Run";
        const meta = document.createElement("div");
        const startedLabel = String(run.started_at || "").trim()
          ? new Date(String(run.started_at || "").trim()).toLocaleString()
          : "Unknown time";
        const channels = [];
        if (run.delivery_channels && run.delivery_channels.chat) channels.push("chat");
        if (run.delivery_channels && run.delivery_channels.widget) channels.push("page");
        meta.textContent = [
          startedLabel,
          formatOpenClawTriggerLabel(run.triggered_by),
          isFailed ? "failed" : (isCancelled ? "cancelled" : (Number(run.estimated_total_tokens || 0) > 0 ? `${Number(run.estimated_total_tokens || 0).toLocaleString()} estimated tokens` : "")),
          channels.length && !isFailed && !isCancelled ? `shown in ${channels.join(" + ")}` : "",
        ].filter(Boolean).join(" · ");
        const body = document.createElement("p");
        body.className = "workspace-board-section-copy";
        body.textContent = String(run.presented_message || run.summary || "").trim()
          || (isFailed ? "This task did not complete." : (isCancelled ? "This task was cancelled before it finished." : "This task finished and was recorded."));
        const budget = document.createElement("div");
        budget.className = "memory-detail-empty";
        budget.textContent = [
          String(run.scope_summary || "").trim(),
          String(run.budget_summary || "").trim(),
          buildOpenClawBudgetUsageLine(run.budget_usage),
        ].filter(Boolean).join(" ");
        item.appendChild(title);
        item.appendChild(meta);
        item.appendChild(body);
        if (budget.textContent) item.appendChild(budget);
        runList.appendChild(item);
      });
    }
  }
}

function renderSettingsPage() {
  const modeHost = $("settings-mode-cards");
  const modeSummary = $("settings-current-mode-summary");
  const setupSummary = $("settings-setup-summary");
  const setupGrid = $("settings-setup-grid");
  const setupNextStep = $("settings-setup-next-step");
  const permissionSummary = $("settings-permission-summary");
  const permissionGrid = $("settings-permission-grid");
  const historyHost = $("settings-history-list");
  const voiceSummary = $("settings-voice-summary");
  const voiceGrid = $("settings-voice-grid");
  const reasoningSummary = $("settings-reasoning-summary");
  const reasoningGrid = $("settings-reasoning-grid");
  const assistiveSummary = $("settings-assistive-summary");
  const assistiveGrid = $("settings-assistive-grid");
  const aiRoutingSummary = $("settings-ai-routing-summary");
  const aiRoutingGrid = $("settings-ai-routing-grid");
  const setupMode = getSetupMode();
  const currentMode = getSetupModeMeta(setupMode);
  const checklistItems = getSetupReadinessItems();

  if (modeSummary) {
    modeSummary.textContent = `${currentMode.label}. ${currentMode.copy}`;
  }

  if (setupSummary) {
    setupSummary.textContent = buildSetupReadinessSummary(checklistItems);
  }
  renderSetupReadinessGrid(setupGrid, checklistItems);
  if (setupNextStep) {
    setupNextStep.textContent = getSetupNextStepCopy(checklistItems);
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
        availabilityNote: "Setup flow not yet available. You can save this as your preference now.",
      },
      {
        id: "managed_cloud",
        title: "Managed Cloud Access",
        badge: "Later guided setup",
        copy: "The easiest long-term setup path. Keep this as a saved preference until the full managed flow is live.",
        availabilityNote: "Setup flow not yet available. You can save this as your preference now.",
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

      if (entry.availabilityNote) {
        const availNote = document.createElement("div");
        availNote.className = "first-run-note";
        availNote.textContent = entry.availabilityNote;
        card.appendChild(availNote);
      }

      modeHost.appendChild(card);
    });
  }

  const largeText = $("settings-toggle-large-text");
  if (largeText) largeText.checked = localStorage.getItem(STORAGE_KEYS.uiLargeText) === "1";
  const highContrast = $("settings-toggle-high-contrast");
  if (highContrast) highContrast.checked = localStorage.getItem(STORAGE_KEYS.uiHighContrast) === "1";
  const compactDensity = $("settings-toggle-compact-density");
  if (compactDensity) compactDensity.checked = localStorage.getItem(STORAGE_KEYS.uiCompactDensity) === "1";

  if (permissionSummary) {
    const statusBits = [
      settingsRuntimeState.summary,
      settingsRuntimeState.updatedAt ? `Updated ${new Date(settingsRuntimeState.updatedAt).toLocaleString()}` : "",
    ].filter(Boolean);
    permissionSummary.textContent = statusBits.join(" · ") || "Governed runtime permissions will appear here.";
  }

  if (permissionGrid) {
    clear(permissionGrid);
    const cards = Array.isArray(settingsRuntimeState.permissionCards) ? settingsRuntimeState.permissionCards : [];
    if (!cards.length) {
      permissionGrid.appendChild(createOverviewChip("Runtime permissions", "Loading"));
    } else {
      cards.forEach((item) => {
        const card = document.createElement("div");
        card.className = "workspace-home-focus settings-permission-card";

        const title = document.createElement("div");
        title.className = "workspace-home-focus-title";
        title.textContent = String(item.label || "Permission").trim() || "Permission";
        card.appendChild(title);

        const status = document.createElement("div");
        status.className = "workspace-home-focus-meta";
        status.textContent = String(item.status_label || (item.enabled ? "Enabled" : "Paused")).trim();
        card.appendChild(status);

        const copy = document.createElement("div");
        copy.className = "workspace-home-focus-copy";
        copy.textContent = String(item.description || item.summary || "").trim() || "Governed runtime permission.";
        card.appendChild(copy);

        const actionRow = document.createElement("div");
        actionRow.className = "workspace-board-actions-toolbar";
        const actionBtn = document.createElement("button");
        actionBtn.type = "button";
        actionBtn.textContent = item.enabled ? "Pause" : "Enable";
        actionBtn.addEventListener("click", () => setRuntimePermission(item.id, !item.enabled));
        actionRow.appendChild(actionBtn);
        card.appendChild(actionRow);

        permissionGrid.appendChild(card);
      });
    }
  }

  if (historyHost) {
    clear(historyHost);
    const history = Array.isArray(settingsRuntimeState.history) ? settingsRuntimeState.history : [];
    if (!history.length) {
      const empty = document.createElement("div");
      empty.className = "workspace-home-empty";
      empty.textContent = "No settings changes recorded yet. Change setup mode or a permission to create an audit trail.";
      historyHost.appendChild(empty);
    } else {
      history.slice(0, 6).forEach((item) => {
        const row = document.createElement("div");
        row.className = "workspace-home-focus settings-history-row";

        const title = document.createElement("div");
        title.className = "workspace-home-focus-title";
        title.textContent = `${String(item.action || "updated").replaceAll("_", " ")} · ${String(item.target || "runtime_settings").replaceAll("_", " ")}`;
        row.appendChild(title);

        const meta = document.createElement("div");
        meta.className = "workspace-home-focus-meta";
        meta.textContent = [
          item.timestamp ? new Date(item.timestamp).toLocaleString() : "",
          String(item.source || "settings_page").replaceAll("_", " "),
        ].filter(Boolean).join(" · ");
        row.appendChild(meta);

        const copy = document.createElement("div");
        copy.className = "workspace-home-focus-copy";
        copy.textContent = `Changed from ${JSON.stringify(item.old_value)} to ${JSON.stringify(item.new_value)}.`;
        row.appendChild(copy);

        historyHost.appendChild(row);
      });
    }
  }

  if (voiceSummary && voiceGrid) {
    const voice = (trustReviewState.voiceRuntime && typeof trustReviewState.voiceRuntime === "object")
      ? trustReviewState.voiceRuntime
      : {};
    const wakeWordEnabled = isHeyNovaWakeWordEnabled();
    voiceSummary.textContent = [
      String(voice.summary || "").trim() || "Run Voice Check to confirm spoken output on this device.",
      wakeWordEnabled ? `Wake word available: "${HEY_NOVA_WAKE_WORD}"` : "Wake word off",
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
      ["Wake word", wakeWordEnabled ? `${HEY_NOVA_WAKE_WORD} available for live help` : "Wake word off"],
    ].forEach(([label, value]) => {
      voiceGrid.appendChild(createOverviewChip(label, value));
    });

    const wakeWordCard = document.createElement("div");
    wakeWordCard.className = "workspace-home-focus settings-permission-card";

    const wakeWordTitle = document.createElement("div");
    wakeWordTitle.className = "workspace-home-focus-title";
    wakeWordTitle.textContent = "Wake word";
    wakeWordCard.appendChild(wakeWordTitle);

    const wakeWordStatus = document.createElement("div");
    wakeWordStatus.className = "workspace-home-focus-meta";
    wakeWordStatus.textContent = wakeWordEnabled ? `${HEY_NOVA_WAKE_WORD} available during live help` : "Off";
    wakeWordCard.appendChild(wakeWordStatus);

    const wakeWordCopy = document.createElement("div");
    wakeWordCopy.className = "workspace-home-focus-copy";
    wakeWordCopy.textContent = wakeWordEnabled
      ? `Talk button recordings send your spoken request directly. "${HEY_NOVA_WAKE_WORD}" is still useful during live help when Nova is staying with a shared screen.`
      : "Talk button recordings send whatever you say. Turn the wake word back on if you want live-help sessions to wait for a spoken guardrail.";
    wakeWordCard.appendChild(wakeWordCopy);

    const wakeWordActions = document.createElement("div");
    wakeWordActions.className = "workspace-board-actions-toolbar";
    const wakeWordToggleBtn = document.createElement("button");
    wakeWordToggleBtn.type = "button";
    wakeWordToggleBtn.textContent = wakeWordEnabled ? "Turn off live-help wake word" : `Enable ${HEY_NOVA_WAKE_WORD} for live help`;
    wakeWordToggleBtn.addEventListener("click", () => setHeyNovaWakeWordEnabled(!wakeWordEnabled));
    wakeWordActions.appendChild(wakeWordToggleBtn);
    wakeWordCard.appendChild(wakeWordActions);

    voiceGrid.appendChild(wakeWordCard);
  }

  if (reasoningSummary && reasoningGrid) {
    const reasoning = (trustReviewState.reasoningRuntime && typeof trustReviewState.reasoningRuntime === "object")
      ? trustReviewState.reasoningRuntime
      : {};
    reasoningSummary.textContent = [
      String(reasoning.summary || "").trim() || "Second opinions stay advisory-only and visible when used.",
      String(reasoning.reasoning_summary_line || "").trim(),
      String(reasoning.settings_permission || "").trim() ? `Settings: ${String(reasoning.settings_permission || "").trim()}` : "",
      String(reasoning.switching_note || "").trim(),
      String(reasoning.usage_budget_state_label || "").trim() ? `Usage: ${String(reasoning.usage_budget_state_label || "").trim()}` : "",
    ].filter(Boolean).join(" · ");

    clear(reasoningGrid);
    [
      ["Current provider", String(reasoning.provider_label || reasoning.provider || "DeepSeek").trim() || "DeepSeek"],
      ["Current route", String(reasoning.route_label || "Governed second-opinion lane").trim() || "Governed second-opinion lane"],
      ["Authority", String(reasoning.authority_label || "Advisory only").trim() || "Advisory only"],
      ["Availability", String(reasoning.status_label || reasoning.status || "Unknown").trim() || "Unknown"],
      ["Settings permission", String(reasoning.settings_permission || "enabled").trim() || "enabled"],
      ["Last used", String(reasoning.last_used || "Not used yet").trim() || "Not used yet"],
      ["Bottom line", String(reasoning.reasoning_summary_line || "Not recorded").trim() || "Not recorded"],
      ["Main gap", String(reasoning.top_issue || "No major gap recorded").trim() || "No major gap recorded"],
      ["Best correction", String(reasoning.top_correction || "No specific correction recorded").trim() || "No specific correction recorded"],
      ["Estimated tokens today", `${Number(reasoning.usage_estimated_total_tokens || 0).toLocaleString()} ${String(reasoning.usage_measurement_label || "estimated tokens").toLowerCase()}`],
      ["Budget state", String(reasoning.usage_budget_state_label || "Normal").trim() || "Normal"],
      ["Budget remaining", `${Number(reasoning.usage_budget_remaining_tokens || 0).toLocaleString()} tokens`],
      ["Cost tracking", String(reasoning.usage_cost_tracking_label || "Exact cost tracking is not live yet").trim() || "Exact cost tracking is not live yet"],
      ["Provider switching", "Later"],
    ].forEach(([label, value]) => {
      reasoningGrid.appendChild(createOverviewChip(label, value));
    });
  }

  if (assistiveSummary && assistiveGrid) {
    const assistivePolicy = (settingsRuntimeState.assistivePolicy && typeof settingsRuntimeState.assistivePolicy === "object")
      ? settingsRuntimeState.assistivePolicy
      : {};
    assistiveSummary.textContent = [
      String(assistivePolicy.summary || "").trim() || "Assistive noticing policy will appear here after the next settings refresh.",
      "Notice, ask, then assist.",
    ].filter(Boolean).join(" · ");

    clear(assistiveGrid);
    const cards = Array.isArray(settingsRuntimeState.assistivePolicyCards) ? settingsRuntimeState.assistivePolicyCards : [];
    if (!cards.length) {
      assistiveGrid.appendChild(createOverviewChip("Assistive noticing", "Loading"));
    } else {
      cards.forEach((item) => {
        const card = document.createElement("div");
        card.className = "workspace-home-focus settings-permission-card";

        const title = document.createElement("div");
        title.className = "workspace-home-focus-title";
        title.textContent = String(item.label || "Assistive noticing").trim() || "Assistive noticing";
        card.appendChild(title);

        const status = document.createElement("div");
        status.className = "workspace-home-focus-meta";
        status.textContent = String(item.value_label || item.value || "").trim() || "Configured";
        card.appendChild(status);

        const copy = document.createElement("div");
        copy.className = "workspace-home-focus-copy";
        copy.textContent = String(item.description || "").trim() || "Bounded assistive noticing policy.";
        card.appendChild(copy);

        const actionRow = document.createElement("div");
        actionRow.className = "workspace-board-actions-toolbar";
        const options = Array.isArray(item.options) ? item.options : [];
        options.slice(0, 4).forEach((option) => {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.textContent = String(option.label || option.value || "Set").trim() || "Set";
          btn.addEventListener("click", () => setAssistiveNoticeMode(option.value));
          actionRow.appendChild(btn);
        });
        card.appendChild(actionRow);

        assistiveGrid.appendChild(card);
      });
    }
  }

  if (aiRoutingSummary && aiRoutingGrid) {
    const providerPolicy = (settingsRuntimeState.providerPolicy && typeof settingsRuntimeState.providerPolicy === "object")
      ? settingsRuntimeState.providerPolicy
      : {};
    const usageBudget = (settingsRuntimeState.usageBudget && typeof settingsRuntimeState.usageBudget === "object")
      ? settingsRuntimeState.usageBudget
      : {};
    aiRoutingSummary.textContent = [
      String(providerPolicy.summary || "").trim() || "Nova should stay local-first by default.",
      String(usageBudget.summary || "").trim(),
    ].filter(Boolean).join(" · ");

    clear(aiRoutingGrid);
    const cards = []
      .concat(Array.isArray(settingsRuntimeState.providerPolicyCards) ? settingsRuntimeState.providerPolicyCards : [])
      .concat(Array.isArray(settingsRuntimeState.usageBudgetCards) ? settingsRuntimeState.usageBudgetCards : []);

    if (!cards.length) {
      aiRoutingGrid.appendChild(createOverviewChip("AI routing", "Loading"));
    } else {
      cards.forEach((item) => {
        const card = document.createElement("div");
        card.className = "workspace-home-focus settings-permission-card";

        const title = document.createElement("div");
        title.className = "workspace-home-focus-title";
        title.textContent = String(item.label || "Policy").trim() || "Policy";
        card.appendChild(title);

        const status = document.createElement("div");
        status.className = "workspace-home-focus-meta";
        status.textContent = String(item.value_label || item.value || "").trim() || "Configured";
        card.appendChild(status);

        const copy = document.createElement("div");
        copy.className = "workspace-home-focus-copy";
        copy.textContent = String(item.description || "").trim() || "Local-first AI policy.";
        card.appendChild(copy);

        const actionRow = document.createElement("div");
        actionRow.className = "workspace-board-actions-toolbar";
        const options = Array.isArray(item.options) ? item.options : [];
        options.slice(0, 3).forEach((option) => {
          const btn = document.createElement("button");
          btn.type = "button";
          btn.textContent = String(option.label || option.value || "Set").trim() || "Set";
          btn.addEventListener("click", () => {
            const actionKind = String(item.action_kind || "").trim();
            if (actionKind === "routing_mode") {
              setRuntimeProviderPolicy({ routing_mode: option.value });
            } else if (actionKind === "preferred_openai_model") {
              setRuntimeProviderPolicy({ preferred_openai_model: option.value });
            } else if (actionKind === "daily_metered_token_budget") {
              setRuntimeUsageBudget(option.value, usageBudget.warning_ratio);
            } else if (actionKind === "warning_ratio") {
              setRuntimeUsageBudget(usageBudget.daily_metered_token_budget, option.value);
            }
          });
          actionRow.appendChild(btn);
        });
        card.appendChild(actionRow);

        aiRoutingGrid.appendChild(card);
      });
    }
  }

}
