/* Nova Dashboard - Workspace And Continuity Surfaces */

function openWorkspaceThread(threadName) {
  const clean = String(threadName || "").trim();
  if (!clean) return;
  setActivePage("workspace");
  requestWorkspaceThreadDetail(clean);
}

function continueWorkspaceThread(threadName) {
  const clean = String(threadName || "").trim();
  if (!clean) return;
  setActivePage("chat");
  injectUserText(`continue my ${clean}`, "text");
}

function getContinuityThreads(limit = 2) {
  const workspace = workspaceHomeState.snapshot || {};
  const focus = (workspace && typeof workspace.focus_thread === "object") ? workspace.focus_thread : {};
  const selectedThread = (threadMapState.detail && typeof threadMapState.detail.thread === "object")
    ? threadMapState.detail.thread
    : {};
  const recentThreads = Array.isArray(workspace.recent_threads) ? workspace.recent_threads : [];
  const mappedThreads = Array.isArray(threadMapState.threads) ? threadMapState.threads : [];
  const seen = new Set();
  const rows = [];

  [focus, selectedThread, ...mappedThreads, ...recentThreads].forEach((thread) => {
    const name = String(thread && thread.name || "").trim();
    if (!name) return;
    const key = name.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    rows.push({ ...(thread || {}), name });
  });

  return rows.slice(0, limit);
}

function describeContinuityThread(thread = {}) {
  const parts = [];
  const goal = String(thread.goal || "").trim();
  const blocker = String(thread.latest_blocker || "").trim();
  const nextAction = String(thread.latest_next_action || "").trim();
  const health = String(thread.health_state || "").trim();
  const memoryCount = Number(thread.memory_count || 0);

  if (goal) parts.push(goal);
  if (blocker) parts.push(`Blocked on ${blocker}`);
  else if (nextAction) parts.push(`Next: ${nextAction}`);
  if (health) parts.push(`Status: ${health.toUpperCase()}`);
  if (Number.isFinite(memoryCount) && memoryCount > 0) parts.push(`${memoryCount} memory item${memoryCount === 1 ? "" : "s"}`);

  return parts.join(" | ") || "Ready to continue.";
}

function createContinuityResumeCard(thread = {}, label = "Resume") {
  const card = document.createElement("button");
  card.type = "button";
  card.className = "workspace-spotlight-card workspace-resume-card";

  const title = document.createElement("div");
  title.className = "workspace-spotlight-title";
  title.textContent = String(thread.name || "Project thread").trim() || "Project thread";
  card.appendChild(title);

  const badge = document.createElement("span");
  badge.className = "settings-mode-badge";
  badge.textContent = label;
  card.appendChild(badge);

  const copy = document.createElement("div");
  copy.className = "workspace-spotlight-copy";
  copy.textContent = describeContinuityThread(thread);
  card.appendChild(copy);

  const action = document.createElement("div");
  action.className = "intro-success-action";
  action.textContent = "Open in workspace";
  card.appendChild(action);

  card.addEventListener("click", () => openWorkspaceThread(thread.name));
  return card;
}

function renderFocusActionRow(host, thread = {}, options = {}) {
  if (!host) return;
  clear(host);
  const name = String(thread.name || "").trim();
  if (!name) return;

  const actions = [
    {
      label: options.primaryLabel || "Resume in chat",
      fn: () => continueWorkspaceThread(name),
      emphasis: true,
    },
    {
      label: "Open workspace",
      fn: () => openWorkspaceThread(name),
    },
  ];

  actions.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    if (item.emphasis) button.className = "assistant-action-btn";
    button.textContent = item.label;
    button.addEventListener("click", item.fn);
    host.appendChild(button);
  });
}

function requestWorkspaceHomeRefresh(force = false) {
  const now = Date.now();
  if (!force && now - Number(workspaceHomeState.lastHydratedAt || 0) < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  workspaceHomeState.lastHydratedAt = now;
  safeWSSend({ text: "workspace home", silent_widget_refresh: true });
}

function requestOperationalContextRefresh(force = false) {
  const now = Date.now();
  if (!force && now - Number(operationalContextState.lastHydratedAt || 0) < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  operationalContextState.lastHydratedAt = now;
  safeWSSend({ text: "operational context", silent_widget_refresh: true });
}

function requestAssistiveNoticesRefresh(force = false) {
  const now = Date.now();
  if (!force && now - Number(assistiveNoticeState.lastHydratedAt || 0) < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  assistiveNoticeState.lastHydratedAt = now;
  safeWSSend({ text: "assistive notices", silent_widget_refresh: true });
}

function requestProjectStructureMapRefresh(force = false) {
  const now = Date.now();
  if (!force && now - Number(projectVisualizerState.lastHydratedAt || 0) < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  projectVisualizerState.lastHydratedAt = now;
  safeWSSend({ text: "show structure map", silent_widget_refresh: true });
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
      summary.textContent = "No projects yet. Start working on something and Nova will keep track.";
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
    memoryBadge.textContent = `${memoryCount} saved`;
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
      meta.textContent = `${goal}${blockerCount ? ` | ${blockerCount} blocker${blockerCount === 1 ? "" : "s"}` : ""}`;
    } else {
      meta.textContent = `${healthState || "Needs attention"}${blockerCount ? ` | ${blockerCount} blocker${blockerCount === 1 ? "" : "s"}` : ""}`;
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
    attachBtn.textContent = "Save latest here";
    attachBtn.addEventListener("click", () => injectUserText(`save this as part of ${name}`, "text"));
    actions.appendChild(attachBtn);

    const statusBtn = document.createElement("button");
    statusBtn.type = "button";
    statusBtn.textContent = "Status";
    statusBtn.addEventListener("click", () => injectUserText(`project status ${name}`, "text"));
    actions.appendChild(statusBtn);

    const saveMemoryBtn = document.createElement("button");
    saveMemoryBtn.type = "button";
    saveMemoryBtn.textContent = "Save notes";
    saveMemoryBtn.addEventListener("click", () => injectUserText(`memory save thread ${name}`, "text"));
    actions.appendChild(saveMemoryBtn);

    const listMemoryBtn = document.createElement("button");
    listMemoryBtn.type = "button";
    listMemoryBtn.textContent = `View saved (${memoryCount})`;
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
  const resumeHost = $("workspace-home-resume");
  const gridHost = $("workspace-home-grid");
  const docsHost = $("workspace-home-docs");
  const actionsHost = $("workspace-home-actions");
  if (!summary || !focusHost || !resumeHost || !gridHost || !docsHost || !actionsHost) return;

  const snapshot = workspaceHomeState.snapshot || {};
  const focus = (snapshot && typeof snapshot.focus_thread === "object") ? snapshot.focus_thread : {};
  const recentDocs = Array.isArray(snapshot.recent_documents) ? snapshot.recent_documents : [];
  const recentActivity = Array.isArray(snapshot.recent_activity) ? snapshot.recent_activity : [];
  const recentMemory = Array.isArray(snapshot.recent_memory_items) ? snapshot.recent_memory_items : [];
  const blockedConditions = Array.isArray(snapshot.blocked_conditions) ? snapshot.blocked_conditions : [];
  const recommendedActions = Array.isArray(snapshot.recommended_actions) ? snapshot.recommended_actions : [];
  const recentThreads = Array.isArray(snapshot.recent_threads) ? snapshot.recent_threads : [];
  const continuityThreads = getContinuityThreads(2);

  const focusName = String(focus.name || "").trim();
  const focusNext = String(focus.latest_next_action || "").trim();
  const focusBlocker = String(focus.latest_blocker || "").trim();
  summary.textContent = focusName
    ? `Resume ${focusName}${focusBlocker ? `, which is currently blocked by ${focusBlocker}` : focusNext ? ` with the next step ${focusNext}` : ""}.`
    : (workspaceHomeState.summary || "Home is preparing the work you are most likely to want next.");

  clear(focusHost);
  if (focusName) {
    const title = document.createElement("div");
    title.className = "workspace-home-focus-title";
    title.textContent = `Resume ${focusName}`;
    focusHost.appendChild(title);

    const meta = document.createElement("div");
    meta.className = "workspace-home-focus-meta";
    const metaParts = [];
    const goal = String(focus.goal || "").trim();
    const healthState = String(focus.health_state || "").trim().toUpperCase();
    if (goal) metaParts.push(goal);
    if (healthState) metaParts.push(`Status: ${healthState}`);
    if (Number.isFinite(Number(focus.memory_count || 0)) && Number(focus.memory_count || 0) > 0) metaParts.push(`${Number(focus.memory_count || 0)} saved`);
    meta.textContent = metaParts.join(" | ");
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

    const focusActions = document.createElement("div");
    focusActions.className = "workspace-focus-actions";
    renderFocusActionRow(focusActions, focus, { primaryLabel: "Resume now" });
    focusHost.appendChild(focusActions);
  } else {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
    empty.textContent = "No focus project yet. Start with a repo summary, continue a saved project, or save notes from what you are doing.";
    focusHost.appendChild(empty);
  }

  clear(resumeHost);
  if (!continuityThreads.length) {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
    empty.textContent = "Recent project threads will appear here once Nova has something worth resuming.";
    resumeHost.appendChild(empty);
  } else {
    continuityThreads.forEach((thread, index) => {
      const label = index === 0 ? "Best resume" : "Recent thread";
      resumeHost.appendChild(createContinuityResumeCard(thread, label));
    });
  }

  clear(gridHost);
  [
    {
      title: "Threads",
      value: `${Number(snapshot.thread_count || 0)}`,
      copy: recentThreads.length
        ? recentThreads.slice(0, 2).map((item) => String(item.name || "").trim()).filter(Boolean).join(" | ")
        : "No saved projects yet.",
    },
    {
      title: "Saved notes",
      value: `${Number(snapshot.project_memory_total || 0)}`,
      copy: `${Number(snapshot.memory_total || 0)} saved item${Number(snapshot.memory_total || 0) === 1 ? "" : "s"} total`,
    },
    {
      title: "Reports",
      value: `${recentDocs.length}`,
      copy: recentDocs.length
        ? recentDocs.map((doc) => `Doc ${doc.id}`).join(" | ")
        : "No analysis docs in this session yet.",
    },
    {
      title: "Recent Activity",
      value: `${recentActivity.length}`,
      copy: recentActivity.length
        ? recentActivity.slice(0, 2).map((item) => String(item.title || "Runtime event").trim()).join(" | ")
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
    recentDocs.slice(0, 2).forEach((doc) => {
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
    recentMemory.slice(0, 2).forEach((item) => {
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
      copy.textContent = `Recent memory${item.updated_at ? ` | ${formatThreadTimestamp(item.updated_at)}` : ""}`;
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
    blocked.textContent = `Blocked now: ${blockedConditions.map((item) => String(item.label || item.area || "Condition").trim()).filter(Boolean).join(" | ")}`;
    docsHost.appendChild(blocked);
  }

  clear(actionsHost);
  const actions = recommendedActions.length
    ? recommendedActions.slice(0, 2)
    : [
        { label: focusName ? "Resume focus thread" : "Open threads", command: focusName ? `continue my ${focusName}` : "show threads" },
        { label: "Memory overview", command: "memory overview" },
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
        copy.textContent = parts.join(" | ") || "Structured node";
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
  const focusActionsHost = $("workspace-board-focus-actions");
  const statsHost = $("workspace-board-stats");
  const threadHost = $("workspace-board-threads");
  const decisionHost = $("workspace-board-decisions");
  const feedHost = $("workspace-board-feed");
  const actionsHost = $("workspace-board-actions");
  if (!summary || !focusHost || !focusActionsHost || !statsHost || !threadHost || !feedHost || !actionsHost) return;

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
  const focusName = String(focus.name || "").trim();

  summary.textContent = focusName
    ? `Workspace is centered on ${focusName}${String(focus.latest_next_action || "").trim() ? ` so you can move on the next step quickly.` : "."}`
    : (workspaceHomeState.summary || "Workspace keeps your active work, saved notes, and reports in one view.");

  clear(focusHost);
  clear(focusActionsHost);
  if (!focusName) {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
    empty.textContent = "No focus project yet. Start with a repo summary, a thread, or a structure map.";
    focusHost.appendChild(empty);
  } else {
    const title = document.createElement("div");
    title.className = "workspace-home-focus-title";
    title.textContent = `Resume ${focusName}`;
    focusHost.appendChild(title);

    [
      String(focus.goal || "").trim() ? `${String(focus.goal || "").trim()}` : "",
      String(focus.health_state || "").trim() ? `Status: ${String(focus.health_state || "").trim().toUpperCase()}` : "",
      String(focus.latest_blocker || "").trim() ? `Current blocker: ${String(focus.latest_blocker || "").trim()}` : "",
      String(focus.latest_next_action || "").trim() ? `Next step: ${String(focus.latest_next_action || "").trim()}` : "",
    ].filter(Boolean).forEach((line) => {
      const row = document.createElement("div");
      row.className = "workspace-home-focus-copy";
      row.textContent = line;
      focusHost.appendChild(row);
    });

    renderFocusActionRow(focusActionsHost, focus, { primaryLabel: "Continue in chat" });
  }

  clear(statsHost);
  [
    ["Threads", `${Number(workspace.thread_count || threads.length || 0)}`],
    ["Saved notes", `${Number(workspace.project_memory_total || 0)}`],
    ["Recent reports", `${recentDocs.length}`],
    ["Visual map", Array.isArray(structure.tree_lines) && structure.tree_lines.length ? "Ready" : "Not loaded"],
  ].forEach(([label, value]) => {
    statsHost.appendChild(createOverviewChip(label, value));
  });

  clear(threadHost);
  if (!threads.length) {
    const empty = document.createElement("div");
    empty.className = "workspace-home-empty";
      empty.textContent = "Saved projects will appear here after Nova has something worth helping you continue.";
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
      copy.textContent = describeContinuityThread(thread) || "Open in workspace for thread detail.";
      card.appendChild(copy);

      threadHost.appendChild(card);
    });
  }

  if (decisionHost) {
    clear(decisionHost);
    if (!recentDecisions.length) {
      const empty = document.createElement("div");
      empty.className = "workspace-home-empty";
      empty.textContent = "Recent decisions will appear here as your work takes shape.";
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
        ].filter(Boolean).join(" | ") || "Recent decision";
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

  const operationalContext = (workspace && typeof workspace.operational_context === "object")
    ? workspace.operational_context
    : {};
  renderOperationalContextWidget(operationalContext);
}

function renderOperationalContextWidget(data = {}) {
  if (data && typeof data === "object" && Object.keys(data).length) {
    operationalContextState.snapshot = { ...operationalContextState.snapshot, ...data };
    operationalContextState.summary = String(data.summary || operationalContextState.summary).trim() || operationalContextState.summary;
    operationalContextState.lastHydratedAt = Date.now();
  }

  const snapshot = operationalContextState.snapshot || {};
  const recentTurns = Array.isArray(snapshot.recent_relevant_turns) ? snapshot.recent_relevant_turns : [];
  const recentActivity = Array.isArray(snapshot.recent_activity) ? snapshot.recent_activity : [];
  const blockedConditions = Array.isArray(snapshot.blocked_conditions) ? snapshot.blocked_conditions : [];

  const homeHost = $("workspace-home-operational");
  if (homeHost) {
    clear(homeHost);

    const summary = document.createElement("div");
    summary.className = "workspace-home-doc-copy";
    summary.textContent = operationalContextState.summary || "Operational context is available here after the next refresh.";
    homeHost.appendChild(summary);

    const note = document.createElement("div");
    note.className = "workspace-home-doc-copy";
    note.textContent = String(snapshot.continuity_note || "This is session continuity, not durable personal memory.").trim()
      || "This is session continuity, not durable personal memory.";
    homeHost.appendChild(note);

    const grid = document.createElement("div");
    grid.className = "operator-health-grid";
    [
      ["Focus thread", String(snapshot.active_thread || "None").trim() || "None"],
      ["Goal", String(snapshot.task_goal || "None").trim() || "None"],
      ["Current step", String(snapshot.current_step || "None").trim() || "None"],
      ["Active topic", String(snapshot.active_topic || "None").trim() || "None"],
      ["Selected file", String(snapshot.selected_file || "None").trim() || "None"],
      ["Turns", `${Number(snapshot.turn_count || 0)}`],
    ].forEach(([labelText, valueText]) => {
      const row = document.createElement("div");
      row.className = "operator-health-row";
      const label = document.createElement("div");
      label.className = "operator-health-label";
      label.textContent = labelText;
      const value = document.createElement("div");
      value.className = "operator-health-value";
      value.textContent = valueText;
      row.appendChild(label);
      row.appendChild(value);
      grid.appendChild(row);
    });
    homeHost.appendChild(grid);

    if (recentTurns.length) {
      const turns = document.createElement("div");
      turns.className = "workspace-home-blocked";
      turns.textContent = `Recent turns: ${recentTurns.slice(0, 3).map((item) => String(item || "").trim()).filter(Boolean).join(" | ")}`;
      homeHost.appendChild(turns);
    }
  }

  const trustSummary = $("trust-center-operational-summary");
  const trustGrid = $("trust-center-operational-grid");
  if (trustSummary) {
    trustSummary.textContent = [
      operationalContextState.summary,
      String(snapshot.memory_preserved_on_reset ? "Reset preserves durable memory." : "").trim(),
    ].filter(Boolean).join(" | ") || "Operational context will appear here after the next refresh.";
  }
  if (trustGrid) {
    clear(trustGrid);
    const rows = [
      ["Focus thread", String(snapshot.active_thread || "None").trim() || "None"],
      ["Goal", String(snapshot.task_goal || "None").trim() || "None"],
      ["Current step", String(snapshot.current_step || "None").trim() || "None"],
      ["Task type", String(snapshot.task_type || "None").trim() || "None"],
      ["Active topic", String(snapshot.active_topic || "None").trim() || "None"],
      ["Selected file", String(snapshot.selected_file || "None").trim() || "None"],
      ["Latest object", String(snapshot.last_relevant_object || "None").trim() || "None"],
      ["Open report", String(snapshot.open_report_id || "None").trim() || "None"],
      ["Thread count", `${Number(snapshot.thread_count || 0)}`],
      ["Turn count", `${Number(snapshot.turn_count || 0)}`],
      ["Recent runtime activity", `${recentActivity.length}`],
      ["Blocked conditions", `${blockedConditions.length}`],
    ];
    rows.forEach(([labelText, valueText]) => {
      const row = document.createElement("div");
      row.className = "operator-health-row";
      const label = document.createElement("div");
      label.className = "operator-health-label";
      label.textContent = labelText;
      const value = document.createElement("div");
      value.className = "operator-health-value";
      value.textContent = valueText;
      row.appendChild(label);
      row.appendChild(value);
      trustGrid.appendChild(row);
    });

    if (recentTurns.length) {
      const turns = document.createElement("div");
      turns.className = "trust-activity-reason";
      turns.textContent = `Recent continuity anchors: ${recentTurns.slice(0, 4).map((item) => String(item || "").trim()).filter(Boolean).join(" | ")}`;
      trustGrid.appendChild(turns);
    }
    if (blockedConditions.length) {
      const blocked = document.createElement("div");
      blocked.className = "trust-activity-reason";
      blocked.textContent = `Current blocked conditions: ${blockedConditions.slice(0, 3).map((item) => String(item.label || item.area || "Condition").trim()).filter(Boolean).join(" | ")}`;
      trustGrid.appendChild(blocked);
    }
  }
}

function renderAssistiveNoticesWidget(data = {}) {
  if (data && typeof data === "object" && Object.keys(data).length) {
    assistiveNoticeState.snapshot = { ...assistiveNoticeState.snapshot, ...data };
    assistiveNoticeState.summary = String(data.summary || assistiveNoticeState.summary).trim() || assistiveNoticeState.summary;
    assistiveNoticeState.lastHydratedAt = Date.now();
  }

  const snapshot = assistiveNoticeState.snapshot || {};
  const notices = Array.isArray(snapshot.notices) ? snapshot.notices : [];
  const handledNotices = Array.isArray(snapshot.handled_notices) ? snapshot.handled_notices : [];
  const recommendedActions = Array.isArray(snapshot.recommended_actions) ? snapshot.recommended_actions : [];
  const governanceNote = String(snapshot.governance_note || "").trim()
    || "Notice, ask, then assist remains the governing rule.";
  const suppressedNoticeCount = Number(snapshot.suppressed_notice_count || 0);
  const dismissedNoticeCount = Number(snapshot.dismissed_notice_count || 0);
  const activeNoticeCount = Number(snapshot.active_notice_count || 0);

  const renderNoticeList = (host, { emptyCopy, includeActions = true } = {}) => {
    if (!host) return;
    clear(host);

    const summary = document.createElement("div");
    summary.className = "workspace-home-doc-copy";
    summary.textContent = assistiveNoticeState.summary || "Assistive notices will appear here after the next refresh.";
    host.appendChild(summary);

    const note = document.createElement("div");
    note.className = "workspace-home-doc-copy";
    note.textContent = governanceNote;
    host.appendChild(note);

    if (suppressedNoticeCount > 0 || dismissedNoticeCount > 0 || activeNoticeCount > notices.length) {
      const stateMeta = document.createElement("div");
      stateMeta.className = "workspace-home-focus-meta";
      stateMeta.textContent = [
        suppressedNoticeCount > 0 ? `${suppressedNoticeCount} cooling down` : "",
        dismissedNoticeCount > 0 ? `${dismissedNoticeCount} handled` : "",
        activeNoticeCount > notices.length ? `${activeNoticeCount - notices.length} hidden by current mode` : "",
      ].filter(Boolean).join(" | ");
      host.appendChild(stateMeta);
    }

    if (!notices.length) {
      const empty = document.createElement("div");
      empty.className = "workspace-home-empty";
      empty.textContent = emptyCopy;
      host.appendChild(empty);
    } else {
      notices.slice(0, 4).forEach((item) => {
        const card = document.createElement("div");
        card.className = "workspace-home-focus settings-permission-card";

        const title = document.createElement("div");
        title.className = "workspace-home-focus-title";
        title.textContent = String(item.title || "Assistive notice").trim() || "Assistive notice";
        card.appendChild(title);

        const meta = document.createElement("div");
        meta.className = "workspace-home-focus-meta";
        meta.textContent = [
          String(item.risk_level || "low").trim().toUpperCase(),
          item.requires_permission ? "Ask first" : "Visible only",
        ].filter(Boolean).join(" | ");
        card.appendChild(meta);

        const body = document.createElement("div");
        body.className = "workspace-home-focus-copy";
        body.textContent = String(item.summary || "").trim() || "A bounded assistive notice is active.";
        card.appendChild(body);

        const whyNow = String(item.why_now || "").trim();
        if (whyNow) {
          const why = document.createElement("div");
          why.className = "workspace-home-focus-copy";
          why.textContent = `Why now: ${whyNow}`;
          card.appendChild(why);
        }

        const actions = Array.isArray(item.suggested_actions) ? item.suggested_actions : [];
        if (includeActions && actions.length) {
          const actionRow = document.createElement("div");
          actionRow.className = "workspace-board-actions-toolbar";
          actions.slice(0, 3).forEach((action) => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.textContent = String(action.label || "Open").trim() || "Open";
            btn.addEventListener("click", () => {
              const command = String(action.command || "").trim();
              if (!command) return;
              setActivePage("chat");
              injectUserText(command, "text");
            });
            actionRow.appendChild(btn);
          });
          card.appendChild(actionRow);
        }

        if (includeActions) {
          const stateRow = document.createElement("div");
          stateRow.className = "workspace-board-actions-toolbar";

          const dismissCommand = String(item.dismiss_command || "").trim();
          if (dismissCommand) {
            const dismissBtn = document.createElement("button");
            dismissBtn.type = "button";
            dismissBtn.textContent = "Dismiss";
            dismissBtn.addEventListener("click", () => {
              setActivePage("chat");
              injectUserText(dismissCommand, "text");
            });
            stateRow.appendChild(dismissBtn);
          }

          const resolveCommand = String(item.resolve_command || "").trim();
          if (resolveCommand) {
            const resolveBtn = document.createElement("button");
            resolveBtn.type = "button";
            resolveBtn.textContent = "Mark resolved";
            resolveBtn.addEventListener("click", () => {
              setActivePage("chat");
              injectUserText(resolveCommand, "text");
            });
            stateRow.appendChild(resolveBtn);
          }

          if (stateRow.childNodes.length) {
            card.appendChild(stateRow);
          }
        }

        host.appendChild(card);
      });
    }

    if (includeActions && recommendedActions.length) {
      const actionRow = document.createElement("div");
      actionRow.className = "workspace-home-actions";
      recommendedActions.slice(0, 4).forEach((item) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "assistant-action-btn";
        btn.textContent = String(item.label || "Run").trim() || "Run";
        btn.addEventListener("click", () => {
          const command = String(item.command || "").trim();
          if (!command) return;
          setActivePage("chat");
          injectUserText(command, "text");
        });
        actionRow.appendChild(btn);
      });
      host.appendChild(actionRow);
    }
  };

  const renderHandledList = (host) => {
    if (!host) return;
    clear(host);

    if (!handledNotices.length) {
      const empty = document.createElement("div");
      empty.className = "workspace-home-empty";
      empty.textContent = "No handled assistive notices are recorded in the current continuity window.";
      host.appendChild(empty);
      return;
    }

    handledNotices.slice(0, 4).forEach((item) => {
      const card = document.createElement("div");
      card.className = "workspace-home-focus settings-permission-card";

      const title = document.createElement("div");
      title.className = "workspace-home-focus-title";
      title.textContent = String(item.title || "Handled notice").trim() || "Handled notice";
      card.appendChild(title);

      const meta = document.createElement("div");
      meta.className = "workspace-home-focus-meta";
      meta.textContent = [
        String(item.status || "handled").trim().toUpperCase(),
        String(item.updated_at || "").trim() ? `Updated ${formatThreadTimestamp(String(item.updated_at || "").trim())}` : "",
      ].filter(Boolean).join(" | ");
      card.appendChild(meta);

      const body = document.createElement("div");
      body.className = "workspace-home-focus-copy";
      body.textContent = String(item.summary || "").trim() || "Handled assistive notice.";
      card.appendChild(body);

      host.appendChild(card);
    });
  };

  renderNoticeList(
    $("workspace-home-assistive"),
    {
      emptyCopy: "No bounded assistive notices are active right now.",
      includeActions: true,
    },
  );

  const trustSummary = $("trust-center-assistive-summary");
  if (trustSummary) {
    trustSummary.textContent = [
      assistiveNoticeState.summary,
      String(snapshot.assistive_notice_mode_label || "").trim() ? `Mode: ${String(snapshot.assistive_notice_mode_label || "").trim()}` : "",
    ].filter(Boolean).join(" | ") || "Assistive notices will appear here after the next refresh.";
  }
  renderNoticeList(
    $("trust-center-assistive-list"),
    {
      emptyCopy: "No bounded assistive notices are active right now.",
      includeActions: true,
    },
  );
  renderHandledList($("trust-center-assistive-handled"));
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
