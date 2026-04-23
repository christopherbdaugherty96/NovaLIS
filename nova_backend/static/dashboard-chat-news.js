/* Nova Dashboard - Chat, News, And Interaction Surfaces */

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
      chat: "Outcome-first examples for goals, drafts, research, and follow-through.",
      news: "News actions for summaries, comparisons, and context checks.",
      intro: "Use Intro to understand how Nova works before you start leaning on it.",
      home: "Status checks, explain actions, and project continuity threads.",
      workspace: "Workspace keeps project continuity, structure, and recent decisions together.",
      memory: "Memory stays explicit, inspectable, and revocable.",
      trust: "Trust keeps recent actions, boundaries, and runtime health visible.",
      settings: "Settings keeps setup choices, voice checks, and comfort controls in one place.",
      agent: "Agent keeps home-agent templates, delivery modes, and recent runs visible.",
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

function appendUsageStrip(container, usageMeta) {
  const meta = (usageMeta && typeof usageMeta === "object") ? usageMeta : null;
  if (!meta) return;

  const summary = String(meta.summary || "").trim();
  const routeLabel = String(meta.route_label || "").trim();
  const modelLabel = String(meta.model_label || "").trim();
  const budgetLabel = String(meta.budget_state_label || "").trim();
  const estimatedCost = Number(meta.estimated_cost_usd || 0);
  const exactTokens = Number(meta.exact_total_tokens || 0);
  const estimatedTokens = Number(meta.estimated_total_tokens || 0);

  if (!summary && !routeLabel && !modelLabel) return;

  const strip = document.createElement("div");
  strip.className = "message-usage-strip";

  if (summary) {
    const copy = document.createElement("div");
    copy.className = "message-usage-summary";
    copy.textContent = summary;
    strip.appendChild(copy);
  }

  const chips = document.createElement("div");
  chips.className = "message-usage-chips";

  if (routeLabel) {
    const routeChip = document.createElement("span");
    routeChip.className = `usage-badge ${meta.metered ? "usage-badge-metered" : "usage-badge-local"}`;
    routeChip.textContent = routeLabel;
    chips.appendChild(routeChip);
  }

  if (modelLabel) {
    const modelChip = document.createElement("span");
    modelChip.className = "usage-badge";
    modelChip.textContent = modelLabel;
    chips.appendChild(modelChip);
  }

  if (exactTokens > 0) {
    const tokenChip = document.createElement("span");
    tokenChip.className = "usage-badge";
    tokenChip.textContent = `${exactTokens.toLocaleString()} exact tokens`;
    chips.appendChild(tokenChip);
  } else if (estimatedTokens > 0) {
    const tokenChip = document.createElement("span");
    tokenChip.className = "usage-badge";
    tokenChip.textContent = `${estimatedTokens.toLocaleString()} est. tokens`;
    chips.appendChild(tokenChip);
  }

  if (estimatedCost > 0) {
    const costChip = document.createElement("span");
    costChip.className = "usage-badge usage-badge-metered";
    costChip.textContent = `$${estimatedCost.toFixed(4)}`;
    chips.appendChild(costChip);
  }

  if (budgetLabel) {
    const budgetChip = document.createElement("span");
    budgetChip.className = "usage-badge";
    budgetChip.textContent = budgetLabel;
    chips.appendChild(budgetChip);
  }

  if (chips.children.length > 0) {
    strip.appendChild(chips);
  }

  container.appendChild(strip);
}

function extractMessageHighlights(text) {
  const raw = String(text || "").trim();
  if (!raw) return null;

  const readLine = (pattern) => {
    const match = raw.match(pattern);
    return match ? String(match[1] || "").trim() : "";
  };

  const bottomLine =
    readLine(/^Bottom line:\s*(.+)$/im) ||
    readLine(/^Summary:\s*(.+)$/im) ||
    readLine(/^Main point:\s*(.+)$/im) ||
    readLine(/^Key takeaway:\s*(.+)$/im);
  const mainGap = readLine(/^Main gap:\s*(.+)$/im);
  const bestCorrection = readLine(/^Best correction:\s*(.+)$/im);

  if (!bottomLine && !mainGap && !bestCorrection) return null;
  return { bottomLine, mainGap, bestCorrection };
}

function renderMessageHighlights(container, highlights) {
  if (!container || !highlights) return;

  const rows = [
    ["Bottom line", highlights.bottomLine],
    ["Main gap", highlights.mainGap],
    ["Best correction", highlights.bestCorrection],
  ].filter(([, value]) => String(value || "").trim());
  if (!rows.length) return;

  const card = document.createElement("div");
  card.className = "message-highlight-card";

  rows.forEach(([label, value]) => {
    const row = document.createElement("div");
    row.className = "message-highlight-row";

    const labelNode = document.createElement("div");
    labelNode.className = "message-highlight-label";
    labelNode.textContent = label;
    row.appendChild(labelNode);

    const valueNode = document.createElement("div");
    valueNode.className = "message-highlight-value";
    valueNode.textContent = String(value || "").trim();
    row.appendChild(valueNode);

    card.appendChild(row);
  });

  container.appendChild(card);
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
    raw.startsWith("INTELLIGENCE BRIEF") ||
    raw.startsWith("DETAILED STORY ANALYSIS") ||
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
    "Open Questions",
    "Strategic Snapshot",
    "Top Findings",
    "Cross-Story Insight",
    "Cross-Story Insights",
    "Sources",
    "Signals to Watch",
    "Timeline",
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

function buildStructuredReportFromBrief(brief = {}) {
  if (!brief || typeof brief !== "object") return null;

  const topic = String(brief.topic || "").trim();
  const summary = String(brief.summary || "").trim();
  const keyFindings = Array.isArray(brief.key_findings) ? brief.key_findings : [];
  const supportingSources = Array.isArray(brief.supporting_sources) ? brief.supporting_sources : [];
  const contradictions = Array.isArray(brief.contradictions) ? brief.contradictions : [];
  const sourceCredibility = Array.isArray(brief.source_credibility) ? brief.source_credibility : [];
  const confidenceFactors = brief.confidence_factors && typeof brief.confidence_factors === "object"
    ? brief.confidence_factors
    : {};
  const counterAnalysis = String(brief.counter_analysis || "").trim();
  const confidence = Number(brief.confidence);
  const contractStatus = String(brief.contract_status || "").trim();
  const validationStatus = String(brief.validation_status || "").trim();
  const fallbackReason = String(brief.fallback_reason || "").trim();
  const sections = [];

  const pushSection = (heading, rows) => {
    const normalizedRows = Array.isArray(rows)
      ? rows.map((row) => String(row || "").trim()).filter(Boolean)
      : [];
    if (!normalizedRows.length) return;
    sections.push({ heading, rows: normalizedRows });
  };

  pushSection("Summary", summary ? [summary] : []);
  pushSection("Key Findings", keyFindings);
  pushSection("Supporting Sources", supportingSources);
  pushSection("Contradictions", contradictions);
  pushSection(
    "Confidence",
    Number.isFinite(confidence) ? [`Confidence score: ${confidence.toFixed(2)}`] : [],
  );
  pushSection(
    "Source Credibility",
    sourceCredibility.map((row) => {
      const source = String(row && row.source || "").trim();
      const classification = String(row && row.classification || "unknown").trim() || "unknown";
      const score = Number(row && row.score);
      const scoreLabel = Number.isFinite(score) ? ` (${score.toFixed(2)})` : "";
      return `${source || "Unknown source"}: ${classification}${scoreLabel}`;
    }),
  );
  pushSection(
    "Confidence Factors",
    Object.entries(confidenceFactors).map(([label, value]) => {
      const cleanLabel = String(label || "").replace(/_/g, " ").trim();
      const numeric = Number(value);
      const valueLabel = Number.isFinite(numeric) ? numeric.toFixed(2) : String(value || "").trim();
      return `${cleanLabel}: ${valueLabel}`;
    }),
  );
  pushSection("Counter Analysis", counterAnalysis ? [counterAnalysis] : []);
  pushSection(
    "Validation Status",
    [
      contractStatus ? `Contract status: ${contractStatus}` : "",
      validationStatus ? `Validation status: ${validationStatus}` : "",
      fallbackReason ? `Fallback reason: ${fallbackReason}` : "",
    ],
  );

  if (!sections.length) return null;
  return {
    title: topic ? `NOVA INTELLIGENCE BRIEF: ${topic}` : "NOVA INTELLIGENCE BRIEF",
    sections,
  };
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

function getBriefGroundingLabel() {
  if (latestBriefWidgetState.sourcePagesRead > 0) {
    if (latestBriefWidgetState.placeholderClusterCount > 0) return "Degraded";
    if (latestBriefWidgetState.omittedClusterCount > 0) return "Partial";
    return "Grounded";
  }
  return "Headline only";
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

  const chipRow = document.createElement("div");
  chipRow.className = "memory-detail-chip-row";
  [
    getBriefGroundingLabel(),
    String(story.sources || "").trim() ? "Named sources" : "Source summary pending",
  ].forEach((label) => {
    const chip = document.createElement("span");
    chip.className = "memory-detail-chip";
    chip.textContent = label;
    chipRow.appendChild(chip);
  });
  card.appendChild(chipRow);

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
    msg.includes("operational context") ||
    msg.includes("assistive notices") ||
    msg.includes("trust center") ||
    msg.includes("volume ")
  );
}

function deriveSuggestedActions(text) {
  const msg = (text || "").toLowerCase();

  if (!msg.trim()) return [];
  if (isOperationalMessage(text)) return [];

  if (msg.includes("not sure what you'd like me to do") || msg.includes("could you clarify")) {
    return [
      { label: "Start simple", command: "Help me start with one simple step." },
      { label: "Today's brief", command: "daily brief" },
      { label: "Open documents", command: "open documents" },
    ];
  }

  if (msg.includes("intelligence brief") || msg.includes("daily situation overview") || msg.includes("executive brief")) {
    return [
      { label: "What matters most?", command: "What matters most from your last response?" },
      { label: "3 bullet version", command: "Summarize your last response in 3 bullets." },
      { label: "Best next step", command: "Based on your last response, what should I do next?" },
    ];
  }

  if (msg.includes("weather")) {
    return [
      { label: "Do I need anything?", command: "Based on the weather, what do I need to know before I go out?" },
      { label: "Forecast", command: "show weather forecast" },
      { label: "Today's brief", command: "daily brief" },
    ];
  }

  if (msg.includes("news") || msg.includes("headline")) {
    return [
      { label: "What matters most?", command: "What matters most from these headlines?" },
      { label: "Quick brief", command: "summarize all headlines in plain language" },
      { label: "Today's brief", command: "daily brief" },
    ];
  }

  if (msg.includes("research") || msg.includes("search") || msg.includes("sources") || msg.includes("coverage")) {
    return [
      { label: "Explain simply", command: "Explain your last response in plain language." },
      { label: "What matters most?", command: "What matters most from your last response?" },
      { label: "Best next step", command: "What should I do next based on your last response?" },
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

  if (message.length > 220) {
    const simpleBtn = document.createElement("button");
    simpleBtn.type = "button";
    simpleBtn.className = "assistant-action-btn";
    simpleBtn.textContent = "Explain simply";
    simpleBtn.addEventListener("click", () => injectUserText("Explain your last response in plain language.", "text"));
    row.appendChild(simpleBtn);
    added += 1;
  }

  if (message.length > 180 || /plan|option|recommend|important|summary|brief/i.test(message)) {
    const whatMattersBtn = document.createElement("button");
    whatMattersBtn.type = "button";
    whatMattersBtn.className = "assistant-action-btn";
    whatMattersBtn.textContent = "What matters most?";
    whatMattersBtn.addEventListener("click", () => injectUserText("What matters most from your last response?", "text"));
    row.appendChild(whatMattersBtn);
    added += 1;
  }

  if (/goal|step|plan|workflow|next|should|could|option/i.test(message)) {
    const nextStepBtn = document.createElement("button");
    nextStepBtn.type = "button";
    nextStepBtn.className = "assistant-action-btn";
    nextStepBtn.textContent = "Best next step";
    nextStepBtn.addEventListener("click", () => injectUserText("What should I do next based on your last response?", "text"));
    row.appendChild(nextStepBtn);
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

function appendChatMessage(role, text, messageId = null, confidence = "", suggestedActions = null, usageMeta = null) {
  const chat = $("chat-log");
  if (!chat) return;

  let msgText = String(text || "");
  if (role === "assistant" && activeManualTurnId) {
    const turnKey = `${activeManualTurnId}:${msgText.trim()}`;
    if (turnKey && turnKey === lastAssistantTurnKey) return;
    lastAssistantTurnKey = turnKey;
  } else {
    lastAssistantTurnKey = "";
  }
  if (role === "assistant" && msgText.trim() === "Hello. How can I help?") {
    msgText = "Tell me what you're trying to get done, and I'll help with the next step.";
    const firstAssistant = chat.querySelector(".chat-assistant span");
    if (firstAssistant && firstAssistant.textContent.trim() === msgText) {
      return;
    }
  }

  const div = document.createElement("div");
  div.className = `chat-${role}`;

  const highlights = role === "assistant" ? extractMessageHighlights(msgText) : null;
  if (highlights) {
    renderMessageHighlights(div, highlights);
  }

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
    appendUsageStrip(div, usageMeta);
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
    updateWorkflowFocusFromAssistant(msgText);
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
  summary.textContent = (summaryText || "").trim() || "Headlines are ready. Start with the first story or ask Nova for a quick brief.";
}

function renderInlineNewsSummary(text, { pending = false, compact = false } = {}) {
  const clean = String(text || "").trim();
  if (!clean && !pending) return null;

  const panel = document.createElement("div");
  panel.className = compact ? "news-inline-summary compact" : "news-inline-summary";
  if (pending) panel.classList.add("pending");

  const title = document.createElement("div");
  title.className = "news-inline-summary-title";
  title.textContent = pending ? "Working on a quick take..." : "Quick take";
  panel.appendChild(title);

  const body = document.createElement("div");
  body.className = "news-inline-summary-body";
  body.textContent = pending ? "Nova is reading this story and turning it into a plain-language summary." : clean;
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
  summarizeCategoryBtn.textContent = "Quick take";
  summarizeCategoryBtn.addEventListener("click", () => {
    latestNewsSummaryState.pendingCategories[categoryKey] = true;
    renderNewsCategoryPage(categoryKey, bucket);
    requestInlineAssistantAction(`summarize ${categoryKey} news`, `Reading ${titleText} and pulling out what matters most.`, "news_surface");
  });
  categoryActions.appendChild(summarizeCategoryBtn);
  const researchCategoryBtn = document.createElement("button");
  researchCategoryBtn.type = "button";
  researchCategoryBtn.className = "assistant-action-btn";
  researchCategoryBtn.textContent = "See wider coverage";
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
    openSource.textContent = "Open story";
    actions.appendChild(openSource);
    const summarizeArticleBtn = document.createElement("button");
    summarizeArticleBtn.type = "button";
    summarizeArticleBtn.className = "assistant-action-btn";
    summarizeArticleBtn.textContent = "See wider coverage";
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
    if (index === 0) li.classList.add("news-item-primary");

    const titleRow = document.createElement("div");
    titleRow.className = "news-item-title-row";
    if (index === 0) {
      const kicker = document.createElement("span");
      kicker.className = "news-story-kicker";
      kicker.textContent = "Start here";
      titleRow.appendChild(kicker);
    }

    const badge = document.createElement("span");
    badge.className = "citation-index";
    badge.textContent = `[${storyIndex}]`;
    titleRow.appendChild(badge);

    const a = document.createElement("a");
    a.href = item.url;
    a.className = "news-item-title";
    a.textContent = item.title || "Untitled story";
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    titleRow.appendChild(a);
    li.appendChild(titleRow);

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
    summarizeBtn.textContent = "Quick take";
    summarizeBtn.addEventListener("click", () => {
      latestNewsSummaryState.pendingStories[storyIndex] = true;
      renderNewsWidget(latestNewsItems, $("news-summary")?.textContent || "", latestNewsCategories);
      requestInlineAssistantAction(`summary of article ${storyIndex}`, `Reading story ${storyIndex} and pulling out the key points.`, "news_surface");
    });
    row.appendChild(summarizeBtn);

    const compareBtn = document.createElement("button");
    compareBtn.type = "button";
    compareBtn.className = "assistant-action-btn";
    compareBtn.textContent = "See wider coverage";
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
  const structuredBrief = data && typeof data.structured_brief === "object" ? data.structured_brief : null;
  const structuredReport = buildStructuredReportFromBrief(structuredBrief);
  if (container) {
    clear(container);
    container.classList.remove("active");

    if (!results.length && !structuredReport) {
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
    container.appendChild(header);

    const focusTopic = queryText || String(results[0]?.title || structuredBrief?.topic || "").trim();
    const summaryText = String((data && data.summary) || structuredBrief?.summary || "").trim();
    if (structuredReport) {
      renderStructuredReport(container, structuredReport);
    } else {
      const quickAnswer = document.createElement("div");
      quickAnswer.className = "search-quick-answer";

      const quickAnswerTitle = document.createElement("div");
      quickAnswerTitle.className = "search-quick-answer-title";
      quickAnswerTitle.textContent = "Quick answer";
      quickAnswer.appendChild(quickAnswerTitle);

      const quickAnswerBody = document.createElement("p");
      quickAnswerBody.className = "search-widget-summary";
      quickAnswerBody.textContent = summaryText || `I found ${results.length} place${results.length === 1 ? "" : "s"} to start. Open the first result if you want the fastest overview.`;
      quickAnswer.appendChild(quickAnswerBody);

      if (results[0]) {
        const quickAnswerMeta = document.createElement("p");
        quickAnswerMeta.className = "search-quick-answer-meta";
        const bestTitle = String(results[0].title || "the first result").trim();
        const bestSource = extractDomain(results[0].url) || "the web";
        quickAnswerMeta.textContent = `Best place to start: ${bestTitle} from ${bestSource}.`;
        quickAnswer.appendChild(quickAnswerMeta);
      }
      container.appendChild(quickAnswer);
    }

    if (focusTopic) {
      const guideActions = document.createElement("div");
      guideActions.className = "search-widget-actions search-widget-actions-primary";

      [
        { label: "Explain simply", prompt: `Explain ${focusTopic} in plain language.` },
        { label: "What matters most?", prompt: `What matters most about ${focusTopic} right now?` },
        { label: "Best next step", prompt: `What should I do next if I want to understand ${focusTopic}?` },
      ].forEach((item) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "assistant-action-btn";
        btn.textContent = item.label;
        btn.addEventListener("click", () => injectUserText(item.prompt, "text"));
        guideActions.appendChild(btn);
      });

      container.appendChild(guideActions);
    }

    if (results.length) {
      const sourcesSection = document.createElement("div");
      sourcesSection.className = "search-sources-section";

      const sourcesToggleRow = document.createElement("div");
      sourcesToggleRow.className = "search-widget-actions";

      const sourcesToggle = document.createElement("button");
      sourcesToggle.type = "button";
      sourcesToggle.className = "assistant-action-btn";
      sourcesToggle.textContent = `See where this came from (${results.length})`;
      sourcesToggle.setAttribute("aria-expanded", "false");
      sourcesToggleRow.appendChild(sourcesToggle);

      const sourceList = document.createElement("div");
      sourceList.className = "search-sources-list";
      sourceList.hidden = true;

      sourcesToggle.addEventListener("click", () => {
        const expanded = sourceList.hidden;
        sourceList.hidden = !expanded;
        sourcesToggle.setAttribute("aria-expanded", expanded ? "true" : "false");
        sourcesToggle.textContent = expanded ? "Hide sources" : `See where this came from (${results.length})`;
      });

      results.forEach((item, index) => {
        const div = document.createElement("div");
        div.className = "search-result";
        if (index === 0) div.classList.add("search-result-primary");

        const titleRow = document.createElement("div");
        titleRow.className = "search-result-title";

        if (index === 0) {
          const startBadge = document.createElement("span");
          startBadge.className = "search-start-badge";
          startBadge.textContent = "Start here";
          titleRow.appendChild(startBadge);
        }

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

        const openBtn = document.createElement("a");
        openBtn.className = "assistant-action-btn";
        openBtn.href = item.url;
        openBtn.target = "_blank";
        openBtn.rel = "noopener noreferrer";
        openBtn.textContent = "Open story";
        actions.appendChild(openBtn);

        const quickTakeBtn = document.createElement("button");
        quickTakeBtn.type = "button";
        quickTakeBtn.className = "assistant-action-btn";
        quickTakeBtn.textContent = "Quick take";
        quickTakeBtn.addEventListener("click", () => injectUserText(`Give me a quick take on ${item.title}.`, "text"));
        actions.appendChild(quickTakeBtn);

        const compareBtn = document.createElement("button");
        compareBtn.type = "button";
        compareBtn.className = "assistant-action-btn";
        compareBtn.textContent = "See wider coverage";
        compareBtn.addEventListener("click", () => injectUserText(`research latest coverage of ${queryText || item.title}`, "text"));
        actions.appendChild(compareBtn);
        div.appendChild(actions);
        sourceList.appendChild(div);
      });
      sourcesSection.appendChild(sourcesToggleRow);
      sourcesSection.appendChild(sourceList);
      container.appendChild(sourcesSection);
    }

    const suggested = Array.isArray(data && data.suggested_actions) ? data.suggested_actions : [];
    if (suggested.length) {
      const actionRow = document.createElement("div");
      actionRow.className = "search-widget-actions";
      const actionLabel = document.createElement("span");
      actionLabel.className = "search-widget-actions-label";
      actionLabel.textContent = "More ways to ask:";
      actionRow.appendChild(actionLabel);
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
  if (tryRouteLiveHelpCommand(clean, { echoUserMessage: true, updateFocus: true })) return;
  if (channel === "text" && tryHandleLocalPageCommand(clean)) return;

  manualTurnInFlight = true;
  manualTurnAssistantSeen = false;
  manualTurnStartedAt = Date.now();
  manualTurnCounter += 1;
  activeManualTurnId = `ui-turn-${manualTurnStartedAt}-${manualTurnCounter}`;
  suppressWidgetHydrationUntil = manualTurnStartedAt + 30000;
  clearStartupHydrationTimers();
  stopWidgetAutoRefresh();

  appendChatMessage("user", clean);
  waitingForAssistant = true;
  const loadingHint = loadingHintForInput(clean);
  setLoadingHint(loadingHint);
  setThinkingBar(true);
  updateWorkflowFocusFromUserInput(clean);
  updateWorkflowFocusProgress(loadingHint);

  if (!safeWSSend({ text: clean, channel, turn_id: activeManualTurnId }, { queueIfUnavailable: true })) {
    appendChatMessage(
      "assistant",
      "Connection is waking back up. I queued your message and will send it as soon as Nova reconnects.",
      null,
      "System status",
    );
  }
}

function requestInlineAssistantAction(text, statusText = "", invocationSource = "ui_surface") {
  const clean = String(text || "").trim();
  if (!clean) return false;
  if (tryRouteLiveHelpCommand(clean, { echoUserMessage: false, updateFocus: true })) return true;

  waitingForAssistant = true;
  const loadingHint = statusText || loadingHintForInput(clean);
  setLoadingHint(loadingHint);
  setThinkingBar(true);
  updateWorkflowFocusFromUserInput(clean);
  updateWorkflowFocusProgress(loadingHint);

  if (!safeWSSend({ text: clean, invocation_source: invocationSource }, { queueIfUnavailable: true })) {
    appendChatMessage(
      "assistant",
      "Connection is waking back up. I queued that request and will send it as soon as Nova reconnects.",
      null,
      "System status",
    );
    return false;
  }

  return true;
}

function requestDeepSeekSecondOpinion() {
  appendChatMessage("user", "Second opinion");
  waitingForAssistant = true;
  setLoadingHint("Checking a second opinion on the recent exchange...");
  setThinkingBar(true);
  updateWorkflowFocusFromUserInput("Second opinion on the recent exchange");
  updateWorkflowFocusProgress("Checking a second opinion on the recent exchange...");

  if (!safeWSSend({ text: "second opinion", invocation_source: "deepseek_button" }, { queueIfUnavailable: true })) {
    appendChatMessage(
      "assistant",
      "Connection is waking back up. I queued the second-opinion request and will send it as soon as Nova reconnects.",
      null,
      "System status",
    );
  }
}

async function startSTT() {
  if (liveHelpState.active || liveHelpState.starting) {
    appendChatMessage(
      "assistant",
      "Live screen help is already listening for \"Hey Nova.\" Stop live help first if you want to use the regular Talk button instead.",
      null,
      "Voice input",
    );
    return;
  }
  if (mediaRecorder) return;
  if (!navigator.mediaDevices || !window.MediaRecorder) {
    flashPTTError();
    return;
  }

  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
  catch {
    flashPTTError();
    return;
  }

  setOrbStatus("LISTENING");
  setPTTButtonState("recording");
  const options = getPreferredAudioRecorderOptions();

  if (!options || !options.mimeType) {
    stream.getTracks().forEach((t) => t.stop());
    setOrbStatus("READY");
    flashPTTError();
    return;
  }

  mediaRecorder = new MediaRecorder(stream, options);
  const chunks = [];

  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) {
      chunks.push(e.data);
      setOrbStatus("LISTENING");
      setPTTButtonState("recording");
      clearTimeout(silenceTimer);
      silenceTimer = setTimeout(() => setOrbStatus("PAUSED"), 1200);
    }
  };

  mediaRecorder.onstop = async () => {
    clearTimeout(silenceTimer);
    silenceTimer = null;
    setOrbStatus("PROCESSING");
    setPTTButtonState("sending");

    try {
      const blob = new Blob(chunks, { type: mediaRecorder.mimeType });
      const result = await transcribeRecordedAudioBlob(blob, "speech.webm");

      if (!result.ok) {
        appendChatMessage(
          "assistant",
          "I couldn't process that recording. Please try again.",
          null,
          "Voice input",
        );
        flashPTTError();
        return;
      }

      if (result.error) {
        appendChatMessage("assistant", String(result.error), null, "Voice input");
        flashPTTError();
        return;
      }

      const transcript = String(result.transcript || "").trim();
      if (transcript) {
        const wakeWordState = normalizeHeyNovaWakeWordTranscript(transcript);
        if (wakeWordState.matched && !wakeWordState.command) {
          appendChatMessage(
            "assistant",
            `I'm here. Say "${HEY_NOVA_WAKE_WORD}" followed by what you want, or just press Talk again and say the request directly.`,
            null,
            "Voice input",
          );
          return;
        }
        const spokenCommand = String(wakeWordState.matched ? (wakeWordState.command || "") : transcript).trim();
        if (!spokenCommand) {
          appendChatMessage(
            "assistant",
            "I didn't catch the request clearly. Try again and say it in one short phrase.",
            null,
            "Voice input",
          );
          return;
        }
        injectUserText(spokenCommand, "voice");
      } else {
        appendChatMessage(
          "assistant",
          "I didn't catch that. Try speaking a bit slower or closer to the mic.",
          null,
          "Voice input",
        );
        flashPTTError();
      }
    } finally {
      if (stream) stream.getTracks().forEach((t) => t.stop());
      mediaRecorder = null;
      chunks.length = 0;
      setOrbStatus("READY");
      if (!($("ptt-btn") && $("ptt-btn").classList.contains("mic-error"))) {
        setPTTButtonState("idle");
      }
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
  if (mediaRecorder && mediaRecorder.state === "recording") {
    setPTTButtonState("sending");
    mediaRecorder.stop();
  }
}

function clearStartupHydrationTimers() {
  startupHydrationTimers.forEach((timer) => clearTimeout(timer));
  startupHydrationTimers = [];
}

function clearWebSocketReconnectTimer() {
  if (!wsReconnectTimer) return;
  clearTimeout(wsReconnectTimer);
  wsReconnectTimer = null;
}

function scheduleWebSocketReconnect(delayMs = 250) {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;
  if (wsReconnectTimer) return;
  wsReconnectTimer = setTimeout(() => {
    wsReconnectTimer = null;
    connectWebSocket();
  }, delayMs);
}

function queueUserMessageForReconnect(message) {
  const payload = (message && typeof message === "object" && !Array.isArray(message)) ? { ...message } : null;
  if (!payload) return;
  queuedUserMessages.push(payload);
  if (queuedUserMessages.length > 8) {
    queuedUserMessages = queuedUserMessages.slice(-8);
  }
}

function flushQueuedUserMessages() {
  if (!ws || ws.readyState !== WebSocket.OPEN || queuedUserMessages.length === 0) return;
  const pending = queuedUserMessages.slice();
  queuedUserMessages = [];
  pending.forEach((payload) => {
    safeWSSend(payload);
  });
}

function queueStartupHydration(delayMs, task) {
  const timer = setTimeout(() => {
    startupHydrationTimers = startupHydrationTimers.filter((entry) => entry !== timer);
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    try {
      task();
    } catch (_) {
      // Startup hydration should never block chat readiness.
    }
  }, delayMs);
  startupHydrationTimers.push(timer);
}

function scheduleStartupHydration() {
  clearStartupHydrationTimers();

  queueStartupHydration(250, () => {
    safeWSSend({ text: "weather", silent_widget_refresh: true });
    safeWSSend({ text: "calendar", silent_widget_refresh: true });
  });

  queueStartupHydration(800, () => {
    safeWSSend({ text: "news", silent_widget_refresh: true });
    loadConnectionsData();
  });

  queueStartupHydration(1600, () => {
    requestOpenClawAgentRefresh(true);
    requestSettingsRuntimeRefresh(true);
    refreshPrivacyPanel();
  });

  queueStartupHydration(2600, () => {
    safeWSSend({ text: "system status", silent_widget_refresh: true });
    safeWSSend({ text: "workspace home", silent_widget_refresh: true });
    safeWSSend({ text: "operational context", silent_widget_refresh: true });
  });

  queueStartupHydration(3600, () => {
    safeWSSend({ text: "assistive notices", silent_widget_refresh: true });
    safeWSSend({ text: "show structure map", silent_widget_refresh: true });
    safeWSSend({ text: "trust center", silent_widget_refresh: true });
    safeWSSend({ text: "policy overview", silent_widget_refresh: true });
    safeWSSend({ text: "tone status", silent_widget_refresh: true });
    safeWSSend({ text: "notification status", silent_widget_refresh: true });
    safeWSSend({ text: "pattern status", silent_widget_refresh: true });
  });
}

function hydrateDashboardWidgets() {
  const now = Date.now();
  if (manualTurnInFlight || waitingForAssistant || now < suppressWidgetHydrationUntil) return;
  if (now - lastWidgetHydrationAt < WIDGET_HYDRATE_MIN_INTERVAL_MS) return;
  lastWidgetHydrationAt = now;

  safeWSSend({ text: "weather", silent_widget_refresh: true });
  safeWSSend({ text: "news", silent_widget_refresh: true });
  safeWSSend({ text: "system status", silent_widget_refresh: true });
  safeWSSend({ text: "calendar", silent_widget_refresh: true });
  safeWSSend({ text: "memory overview", silent_widget_refresh: true });
  safeWSSend({ text: "show threads", silent_widget_refresh: true });
  safeWSSend({ text: "workspace home", silent_widget_refresh: true });
  safeWSSend({ text: "operational context", silent_widget_refresh: true });
  safeWSSend({ text: "assistive notices", silent_widget_refresh: true });
  safeWSSend({ text: "show structure map", silent_widget_refresh: true });
  safeWSSend({ text: "trust center", silent_widget_refresh: true });
  safeWSSend({ text: "policy overview", silent_widget_refresh: true });
  safeWSSend({ text: "tone status", silent_widget_refresh: true });
  safeWSSend({ text: "notification status", silent_widget_refresh: true });
  safeWSSend({ text: "pattern status", silent_widget_refresh: true });
  requestOpenClawAgentRefresh();
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
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;
  clearWebSocketReconnectTimer();
  ws = new WebSocket(`${WS_BASE}/ws`);
  renderHeaderStatus(activePageState);

  ws.onopen = () => {
    clearStartupHydrationTimers();
    flushQueuedUserMessages();
    renderHeaderStatus(activePageState);
    renderIntroPage();
    renderHomeLaunchWidget();
    renderSettingsPage();
    startWidgetAutoRefresh();
    startMorningFallbackTimer();
    scheduleStartupHydration();
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
        renderHomeLaunchWidget();
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
      case "operational_context":
        renderOperationalContextWidget(msg);
        break;
      case "assistive_notices":
        renderAssistiveNoticesWidget(msg);
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
      case "run_status":
        applyOpenClawRunStatusEvent(msg.data || {});
        break;
      case "chat":
        if (manualTurnInFlight && msg.turn_id && msg.turn_id !== activeManualTurnId) break;
        if (manualTurnInFlight) manualTurnAssistantSeen = true;
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
      case "token_budget_update":
        if (msg.data && typeof msg.data === "object") {
          renderTokenBudgetBar(msg.data);
        }
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
          renderHomeLaunchWidget();
          renderTrustPanel(msg.data || {});
          renderTrustCenterPage();
        }
        break;
      case "chat_done":
        if (manualTurnInFlight && msg.turn_id && msg.turn_id !== activeManualTurnId) break;
        if (manualTurnInFlight && !manualTurnAssistantSeen) {
          if (Date.now() - manualTurnStartedAt < 60000) break;
          manualTurnInFlight = false;
          manualTurnStartedAt = 0;
          activeManualTurnId = "";
        }
        if (manualTurnInFlight && manualTurnAssistantSeen) {
          manualTurnInFlight = false;
          manualTurnAssistantSeen = false;
          manualTurnStartedAt = 0;
          activeManualTurnId = "";
          startWidgetAutoRefresh();
        }
        waitingForAssistant = false;
        setLoadingHint("");
        setThinkingBar(false);
        if (workflowFocusState.awaitingResponse) {
          workflowFocusState.status = "Ready";
          workflowFocusState.awaitingResponse = false;
          renderWorkflowFocusWidget();
        }
        break;
      case "thought":
        if (pendingThoughtMessageId && msg.message_id === pendingThoughtMessageId) {
          const anchor = messageMeta.get(msg.message_id);
          if (anchor) showThoughtOverlay(anchor, msg.data || {});
          pendingThoughtMessageId = null;
        }
        break;
      case "error":
        manualTurnInFlight = false;
        manualTurnAssistantSeen = false;
        manualTurnStartedAt = 0;
        activeManualTurnId = "";
        waitingForAssistant = false;
        setThinkingBar(false);
        appendChatMessage("assistant", translateError(msg.code, msg.message), null, "System status");
        updateWorkflowFocusFromError(translateError(msg.code, msg.message));
        break;
    }
  };

  ws.onclose = () => {
    manualTurnInFlight = false;
    manualTurnAssistantSeen = false;
    manualTurnStartedAt = 0;
    activeManualTurnId = "";
    waitingForAssistant = false;
    setThinkingBar(false);
    clearStartupHydrationTimers();
    stopWidgetAutoRefresh();
    renderHeaderStatus(activePageState);
    renderIntroPage();
    renderSettingsPage();
    if (ackResetTimer) {
      clearTimeout(ackResetTimer);
      ackResetTimer = null;
    }
    scheduleWebSocketReconnect(1200);
  };

  ws.onerror = () => {
    // onerror always precedes onclose — onclose will schedule reconnect.
    // Just surface a brief console note so browser devtools show the failure.
    console.warn("[Nova] WebSocket error — connection will close and reconnect.");
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
    agent: $("page-agent"),
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
    if (name === target) {
      el.scrollTop = 0;
    }
  });

  const main = document.querySelector(".main");
  if (main) main.scrollTop = 0;
  window.scrollTo({ top: 0, left: 0, behavior: "auto" });

  document.querySelectorAll(".header-menu-page-btn, .primary-nav-btn").forEach((btn) => {
    const active = btn.dataset.page === target;
    btn.classList.toggle("active", active);
    btn.setAttribute("aria-pressed", active ? "true" : "false");
  });

  activePageState = target;
  const workspaceCurrent = $("workspace-current-label");
  if (workspaceCurrent) {
    workspaceCurrent.textContent = PAGE_LABELS[target] || "Chat";
  }
  renderHeaderStatus(target);

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
  if (target === "agent") {
    requestOpenClawAgentRefresh(true);
    renderOpenClawAgentPage();
  }
  if (target === "trust") {
    safeWSSend({ text: "trust center", silent_widget_refresh: true });
    safeWSSend({ text: "system status", silent_widget_refresh: true });
  }
  if (target === "intro") {
    requestSettingsRuntimeRefresh();
    renderIntroPage();
    loadProfileData();
    loadConnectionsData();
  }
  if (target === "settings") {
    safeWSSend({ text: "trust center", silent_widget_refresh: true });
    safeWSSend({ text: "system status", silent_widget_refresh: true });
    requestSettingsRuntimeRefresh(true);
    renderSettingsPage();
    loadProfileData();
    loadConnectionsData();
  }

  if (latestNewsItems.length > 0) {
    renderNewsWidget(latestNewsItems, $("news-summary")?.textContent || "", latestNewsCategories);
  } else {
    setNewsExpandButton();
  }
}

// ============================================================
// CONNECTION CARDS — load, render, save, test, disconnect
// ============================================================

let _connectionsData = [];   // last fetched snapshot from GET /api/settings/connections

function getConnectionCardProviders() {
  return Array.isArray(_connectionsData) ? _connectionsData : [];
}

function getConnectionCardProvider(providerId) {
  const target = String(providerId || "").trim().toLowerCase();
  if (!target) return null;
  return getConnectionCardProviders().find((provider) => String(provider && provider.id || "").trim().toLowerCase() === target) || null;
}

function getConnectionCardStats() {
  const providers = getConnectionCardProviders();
  const saved = providers.filter((provider) => provider && provider.has_key === true);
  const connected = saved.filter((provider) => provider && provider.connected === true);
  const failed = saved.filter((provider) => provider && provider.connected !== true);
  return {
    loaded: providers.length > 0,
    totalProviders: providers.length,
    savedCount: saved.length,
    connectedCount: connected.length,
    failedCount: failed.length,
  };
}

function getConnectionHealthyCount() {
  const stats = getConnectionCardStats();
  return stats.loaded ? stats.connectedCount : 0;
}

function buildConnectionsSummaryCopy() {
  const stats = getConnectionCardStats();
  if (!stats.loaded) {
    return "Connect your API keys so Nova can access web search, news, weather, and cloud reasoning. All keys stay on this device.";
  }
  if (!stats.savedCount) {
    return "Nova is ready to stay local-first. Add connections only when you want live search, weather, news, calendar, or cloud reasoning.";
  }
  if (stats.failedCount) {
    return `${stats.connectedCount} connection${stats.connectedCount === 1 ? "" : "s"} healthy and ${stats.failedCount} need attention. Open a card below to test, fix, or disconnect it.`;
  }
  return `${stats.connectedCount} connection${stats.connectedCount === 1 ? "" : "s"} healthy. These connections stay on this device and can be reviewed or disconnected any time.`;
}

async function loadConnectionsData() {
  try {
    const res = await fetch("/api/settings/connections");
    if (!res.ok) return;
    _connectionsData = await res.json();
    renderConnectionCards();
    renderIntroPage();
    renderSettingsPage();
    renderHomeLaunchWidget();
  } catch (_) {
    // silently ignore — cards will stay empty until next load
  }
}

function renderConnectionCards() {
  const grid = $("connection-cards-grid");
  const summary = $("connections-summary");
  if (summary) {
    summary.textContent = buildConnectionsSummaryCopy();
  }
  if (!grid) return;
  clear(grid);

  if (!Array.isArray(_connectionsData) || _connectionsData.length === 0) {
    const empty = document.createElement("p");
    empty.className = "workspace-board-section-copy";
    empty.textContent = "Connection status unavailable — server not responding.";
    grid.appendChild(empty);
    return;
  }

  _connectionsData.forEach((provider) => {
    grid.appendChild(_buildConnectionCard(provider));
  });
}

function _buildConnectionCard(provider) {
  const isConnected = provider.connected === true;
  const hasKey = provider.has_key === true;
  const needsKey = !isConnected;

  const stateClass = isConnected ? "conn-card--connected" : hasKey ? "conn-card--needed" : "conn-card--setup";
  const stateLabel = isConnected ? "Connected" : hasKey ? "Key saved" : "Not set up";

  const card = document.createElement("div");
  card.className = `conn-card ${stateClass}`;
  card.dataset.providerId = provider.id;

  // Header
  const header = document.createElement("div");
  header.className = "conn-card-header";

  const dot = document.createElement("span");
  dot.className = "conn-card-dot";

  const label = document.createElement("span");
  label.className = "conn-card-label";
  label.textContent = provider.label;

  const badge = document.createElement("span");
  badge.className = "conn-card-state-badge";
  badge.textContent = stateLabel;

  header.appendChild(dot);
  header.appendChild(label);
  header.appendChild(badge);
  card.appendChild(header);

  // Description
  if (provider.description) {
    const desc = document.createElement("p");
    desc.className = "conn-card-desc";
    desc.textContent = provider.description;
    card.appendChild(desc);
  }

  // Key hint (connected only)
  if (isConnected && provider.key_hint) {
    const hint = document.createElement("div");
    hint.className = "conn-card-hint";
    hint.textContent = `Key: ${provider.key_hint}`;
    card.appendChild(hint);
  }

  // Health status line
  const health = document.createElement("div");
  health.className = "conn-card-health" + (isConnected ? " ok" : "");
  health.dataset.healthEl = "1";
  if (isConnected && provider.health_detail) {
    health.textContent = provider.health_detail;
  } else if (hasKey && !isConnected && provider.health_detail) {
    health.className = "conn-card-health err";
    health.textContent = provider.health_detail;
  }
  card.appendChild(health);

  // Key input area (shown for non-connected cards, or toggled by Connect button)
  const inputSection = document.createElement("div");
  inputSection.dataset.inputSection = "1";
  inputSection.hidden = isConnected;  // connected cards start with input hidden

  const inputRow = document.createElement("div");
  inputRow.className = "conn-card-input-row";

  const inputType = provider.kind === "api_key" ? "password" : "text";
  const keyInput = document.createElement("input");
  keyInput.type = inputType;
  keyInput.className = "conn-card-input";
  keyInput.placeholder = provider.placeholder || "Paste key…";
  keyInput.setAttribute("autocomplete", "off");
  keyInput.dataset.keyInput = "1";
  inputRow.appendChild(keyInput);
  inputSection.appendChild(inputRow);

  if (provider.privacy_note) {
    const privacy = document.createElement("p");
    privacy.className = "conn-card-privacy";
    privacy.textContent = provider.privacy_note;
    inputSection.appendChild(privacy);
  }

  card.appendChild(inputSection);

  // Actions
  const actions = document.createElement("div");
  actions.className = "conn-card-actions";

  if (isConnected) {
    // Test button
    const testBtn = document.createElement("button");
    testBtn.type = "button";
    testBtn.className = "conn-card-btn";
    testBtn.textContent = "Test connection";
    testBtn.addEventListener("click", () => _testConnection(card, provider.id));
    actions.appendChild(testBtn);

    // Disconnect button
    const disconnectBtn = document.createElement("button");
    disconnectBtn.type = "button";
    disconnectBtn.className = "conn-card-btn conn-card-btn--danger";
    disconnectBtn.textContent = "Disconnect";
    disconnectBtn.addEventListener("click", () => _disconnectProvider(provider.id));
    actions.appendChild(disconnectBtn);
  } else if (hasKey) {
    // Key exists but health failed — show re-save + test
    const saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.className = "conn-card-btn conn-card-btn--primary";
    saveBtn.textContent = "Save & Test";
    saveBtn.addEventListener("click", () => _saveAndTest(card, provider.id, keyInput));
    actions.appendChild(saveBtn);

    const disconnectBtn = document.createElement("button");
    disconnectBtn.type = "button";
    disconnectBtn.className = "conn-card-btn conn-card-btn--danger";
    disconnectBtn.textContent = "Disconnect";
    disconnectBtn.addEventListener("click", () => _disconnectProvider(provider.id));
    actions.appendChild(disconnectBtn);
  } else {
    // Not set up — show Connect toggle
    const connectBtn = document.createElement("button");
    connectBtn.type = "button";
    connectBtn.className = "conn-card-btn conn-card-btn--primary";
    connectBtn.textContent = "Connect";
    connectBtn.dataset.connectToggle = "1";
    connectBtn.addEventListener("click", () => {
      inputSection.hidden = false;
      connectBtn.hidden = true;

      const saveBtn = document.createElement("button");
      saveBtn.type = "button";
      saveBtn.className = "conn-card-btn conn-card-btn--primary";
      saveBtn.textContent = "Save & Test";
      saveBtn.addEventListener("click", () => _saveAndTest(card, provider.id, keyInput));
      actions.appendChild(saveBtn);

      const cancelBtn = document.createElement("button");
      cancelBtn.type = "button";
      cancelBtn.className = "conn-card-btn";
      cancelBtn.textContent = "Cancel";
      cancelBtn.addEventListener("click", () => {
        inputSection.hidden = true;
        connectBtn.hidden = false;
        saveBtn.remove();
        cancelBtn.remove();
        keyInput.value = "";
        _setCardHealth(card, "", "");
      });
      actions.appendChild(cancelBtn);

      keyInput.focus();
    });
    actions.appendChild(connectBtn);
  }

  card.appendChild(actions);
  return card;
}

function _setCardHealth(card, msg, type) {
  const el = card.querySelector("[data-health-el]");
  if (!el) return;
  el.className = "conn-card-health" + (type ? " " + type : "");
  el.textContent = msg;
}

async function _saveAndTest(card, providerId, keyInput) {
  const key = keyInput.value.trim();
  if (!key) {
    _setCardHealth(card, "Please enter a key first.", "err");
    return;
  }

  _setCardHealth(card, "Saving and testing…", "checking");

  try {
    const res = await fetch(`/api/settings/connections/${providerId}/key`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key }),
    });
    const data = await res.json();
    if (!res.ok) {
      _setCardHealth(card, data.detail || "Save failed", "err");
      return;
    }
    if (data.ok) {
      _setCardHealth(card, data.detail || "Connected.", "ok");
      // Refresh all cards so state reflects the new connection
      await loadConnectionsData();
    } else {
      _setCardHealth(card, data.detail || "Key saved but health check failed.", "err");
    }
  } catch (_) {
    _setCardHealth(card, "Network error — could not reach server.", "err");
  }
}

async function _testConnection(card, providerId) {
  _setCardHealth(card, "Testing…", "checking");
  try {
    const res = await fetch(`/api/settings/connections/${providerId}/test`, {
      method: "POST",
    });
    const data = await res.json();
    if (!res.ok) {
      _setCardHealth(card, data.detail || "Test failed", "err");
      return;
    }
    _setCardHealth(card, data.detail || (data.ok ? "Connected." : "Check failed."), data.ok ? "ok" : "err");
  } catch (_) {
    _setCardHealth(card, "Network error.", "err");
  }
}

async function _disconnectProvider(providerId) {
  try {
    const res = await fetch(`/api/settings/connections/${providerId}`, { method: "DELETE" });
    if (res.ok) {
      await loadConnectionsData();
    }
  } catch (_) {
    // silently ignore
  }
}

function setupConnectionCardHandlers() {
  const refreshBtn = $("btn-connections-refresh");
  if (refreshBtn) refreshBtn.addEventListener("click", loadConnectionsData);

  const resetAllBtn = $("btn-reset-all");
  const resetTrigger = $("connection-reset-trigger");
  const resetConfirm = $("connection-reset-confirm");

  if (resetAllBtn) {
    resetAllBtn.addEventListener("click", () => {
      if (resetTrigger) resetTrigger.hidden = true;
      if (resetConfirm) resetConfirm.hidden = false;
    });
  }

  const resetCancelBtn = $("btn-reset-cancel");
  if (resetCancelBtn) {
    resetCancelBtn.addEventListener("click", () => {
      if (resetTrigger) resetTrigger.hidden = false;
      if (resetConfirm) resetConfirm.hidden = true;
    });
  }

  const resetConfirmBtn = $("btn-reset-confirm");
  if (resetConfirmBtn) {
    resetConfirmBtn.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/settings/connections/all", {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ confirmed: true }),
        });
        if (res.ok) {
          if (resetTrigger) resetTrigger.hidden = false;
          if (resetConfirm) resetConfirm.hidden = true;
          await loadConnectionsData();
        }
      } catch (_) {
        // silently ignore
      }
    });
  }
}

// ============================================================
// USER PROFILE — load, populate, save
// ============================================================

let _profileLoaded = false;
let _profileSnapshot = {
  name: "",
  nickname: "",
  email: "",
  display_name: "",
  is_set_up: false,
  preferences: {},
};

function getProfileSetupState() {
  const snapshot = (_profileSnapshot && typeof _profileSnapshot === "object") ? _profileSnapshot : {};
  const displayName = String(snapshot.display_name || snapshot.nickname || snapshot.name || "").trim();
  const hasIdentity = Boolean(snapshot.is_set_up) || Boolean(displayName);
  return {
    hasIdentity,
    displayName,
    name: String(snapshot.name || "").trim(),
    email: String(snapshot.email || "").trim(),
  };
}

function _profileStatus(id, msg, type) {
  const el = $(id);
  if (!el) return;
  el.textContent = msg;
  el.className = "profile-status visible " + (type || "ok");
  clearTimeout(el._fadeTimer);
  el._fadeTimer = setTimeout(() => {
    el.classList.remove("visible");
  }, 3500);
}

async function loadProfileData() {
  try {
    const res = await fetch("/api/profile");
    if (!res.ok) return;
    const data = await res.json();
    _profileSnapshot = (data && typeof data === "object")
      ? {
          ..._profileSnapshot,
          ...data,
          preferences: (data.preferences && typeof data.preferences === "object") ? data.preferences : {},
        }
      : { ..._profileSnapshot };

    const nameEl = $("profile-name");
    const nicknameEl = $("profile-nickname");
    const emailEl = $("profile-email");
    const rulesEl = $("profile-rules");
    const useNameEl = $("profile-pref-use-name");
    const proactiveEl = $("profile-pref-proactive");

    if (nameEl) nameEl.value = data.name || "";
    if (nicknameEl) nicknameEl.value = data.nickname || "";
    if (emailEl) emailEl.value = data.email || "";
    if (rulesEl) rulesEl.value = data.rules || "";

    const prefs = data.preferences || {};
    if (useNameEl) useNameEl.checked = prefs.use_name_in_responses !== false;
    if (proactiveEl) proactiveEl.checked = prefs.proactive_suggestions !== false;

    const style = (prefs.response_style || "balanced").trim().toLowerCase();
    document.querySelectorAll('input[name="response-style"]').forEach((radio) => {
      radio.checked = radio.value === style;
    });

    // Update profile summary — always overwrite so stale name doesn't linger
    const summary = $("profile-summary");
    if (summary) {
      summary.textContent = data.display_name
        ? `Hi, ${data.display_name}. You can update your details below at any time.`
        : "Tell Nova who you are so it can address you correctly and follow your preferences.";
    }

    _profileLoaded = true;
    renderIntroPage();
    renderHomeLaunchWidget();
  } catch (_) {
    // silently ignore — profile panel will just show empty
  }
}

async function saveProfileIdentity() {
  const name = ($("profile-name") || {}).value || "";
  const nickname = ($("profile-nickname") || {}).value || "";
  const email = ($("profile-email") || {}).value || "";

  try {
    const res = await fetch("/api/profile/identity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, nickname, email }),
    });
    const data = await res.json();
    if (!res.ok) {
      _profileStatus("profile-identity-status", data.detail || "Save failed", "err");
      return;
    }
    _profileStatus("profile-identity-status", "Saved ✓", "ok");
    // Always refresh summary so clearing a name resets to default text
    const summary = $("profile-summary");
    if (summary) {
      summary.textContent = data.display_name
        ? `Hi, ${data.display_name}. You can update your details below at any time.`
        : "Tell Nova who you are so it can address you correctly and follow your preferences.";
    }
    _profileSnapshot = {
      ..._profileSnapshot,
      ...data,
      preferences: (data.preferences && typeof data.preferences === "object") ? data.preferences : (_profileSnapshot.preferences || {}),
    };
    renderIntroPage();
    renderHomeLaunchWidget();
  } catch (_) {
    _profileStatus("profile-identity-status", "Network error", "err");
  }
}

async function saveProfilePreferences() {
  const styleRadio = document.querySelector('input[name="response-style"]:checked');
  const response_style = styleRadio ? styleRadio.value : "balanced";
  const use_name_in_responses = ($("profile-pref-use-name") || {}).checked !== false;
  const proactive_suggestions = ($("profile-pref-proactive") || {}).checked !== false;

  try {
    const res = await fetch("/api/profile/preferences", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ response_style, use_name_in_responses, proactive_suggestions }),
    });
    const data = await res.json();
    if (!res.ok) {
      _profileStatus("profile-prefs-status", data.detail || "Save failed", "err");
      return;
    }
    _profileStatus("profile-prefs-status", "Saved ✓", "ok");
  } catch (_) {
    _profileStatus("profile-prefs-status", "Network error", "err");
  }
}

async function saveProfileRules() {
  const rules = ($("profile-rules") || {}).value || "";

  try {
    const res = await fetch("/api/profile/rules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rules }),
    });
    const data = await res.json();
    if (!res.ok) {
      _profileStatus("profile-rules-status", data.detail || "Save failed", "err");
      return;
    }
    _profileStatus("profile-rules-status", "Saved ✓", "ok");
  } catch (_) {
    _profileStatus("profile-rules-status", "Network error", "err");
  }
}

function setupProfileHandlers() {
  const saveIdentityBtn = $("btn-profile-save-identity");
  if (saveIdentityBtn) saveIdentityBtn.addEventListener("click", saveProfileIdentity);

  const savePrefsBtn = $("btn-profile-save-prefs");
  if (savePrefsBtn) savePrefsBtn.addEventListener("click", saveProfilePreferences);

  const saveRulesBtn = $("btn-profile-save-rules");
  if (saveRulesBtn) saveRulesBtn.addEventListener("click", saveProfileRules);
}

function setupPageNavigation() {
  const buttons = document.querySelectorAll(".header-menu-page-btn, .primary-nav-btn");
  if (!buttons || buttons.length === 0) return;

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      closeHeaderMenus();
      setActivePage(btn.dataset.page || "chat");
    });
  });

  setActivePage(getInitialPage());
}

function sendChat() {
  const input = $("chat-input");
  if (!input) return;
  if (waitingForAssistant || manualTurnInFlight) {
    setLoadingHint("Nova is still answering. Give this turn a moment before sending another.");
    setThinkingBar(true);
    input.focus();
    return;
  }
  injectUserText(input.value, "text");
  input.value = "";
}

function setupPrimaryChatControls() {
  const sendBtn = $("send-btn");
  if (sendBtn && sendBtn.dataset.bound !== "1") {
    sendBtn.dataset.bound = "1";
    sendBtn.addEventListener("click", sendChat);
  }

  const deepSeekBtn = $("deepseek-btn");
  if (deepSeekBtn && deepSeekBtn.dataset.bound !== "1") {
    deepSeekBtn.dataset.bound = "1";
    deepSeekBtn.addEventListener("click", requestDeepSeekSecondOpinion);
  }

  const input = $("chat-input");
  if (input && input.dataset.bound !== "1") {
    input.dataset.bound = "1";
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendChat();
    });
  }

  const micBtn = $("ptt-btn");
  if (micBtn && micBtn.dataset.bound !== "1") {
    micBtn.dataset.bound = "1";
    micBtn.addEventListener("click", () => {
      const isRecording = mediaRecorder && mediaRecorder.state === "recording";
      if (!isRecording) startSTT();
      else stopSTT();
    });
  }
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
  intro.textContent = "Nova helps you understand, continue, and organize your work without ever taking control away from you.";
  card.appendChild(intro);

  const readinessSummary = document.createElement("p");
  readinessSummary.className = "first-run-note";
  const checklistItems = getSetupReadinessItems();
  const firstSuccess = getIntroFirstSuccessItems(checklistItems);
  readinessSummary.textContent = buildSetupReadinessSummary(checklistItems);
  card.appendChild(readinessSummary);

  const successIntro = document.createElement("p");
  successIntro.className = "first-run-intro";
  successIntro.textContent = String(firstSuccess.summary || "").trim()
    || "Start with one useful outcome. Nova will help with the rest without making you learn the system first.";
  card.appendChild(successIntro);

  const successGrid = document.createElement("div");
  successGrid.className = "intro-success-grid";
  (Array.isArray(firstSuccess.items) ? firstSuccess.items : []).slice(0, 3).forEach((item) => {
    const cardBtn = createIntroFirstSuccessCard({
      ...item,
      action: () => {
        if (typeof item.action === "function") item.action();
        overlay.style.display = "none";
        localStorage.setItem(STORAGE_KEYS.firstRunDone, "1");
      },
    });
    successGrid.appendChild(cardBtn);
  });
  if (successGrid.childElementCount) {
    card.appendChild(successGrid);
  }

  const pillars = document.createElement("div");
  pillars.className = "first-run-pillars";
  [
    ["Read the Introduction", "See what Nova can do, how it works, and why it stays governed."],
    ["Review Settings", "Choose the setup path that fits you and review voice, privacy, and comfort controls."],
    ["Use Workspace and Trust", "Workspace keeps work together. Trust shows what happened, why it happened, and what stayed blocked."],
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
    "Start with one practical outcome instead of trying to learn the whole system first.",
    "Use Introduction and Home when you want the easiest launch path.",
    "Use Workspace when you want continuity and ongoing project context.",
    "Use Trust and Settings when you want to inspect what is ready, what is blocked, and why.",
    "Use explicit phrases like \"remember this\" only when you want durable memory.",
  ].forEach((label) => {
    const li = document.createElement("li");
    li.textContent = label;
    steps.appendChild(li);
  });
  card.appendChild(steps);

  const magicMoment = document.createElement("div");
  magicMoment.className = "first-run-pillar";
  const magicTitle = document.createElement("div");
  magicTitle.className = "first-run-pillar-title";
  magicTitle.textContent = "One good first move";
  magicMoment.appendChild(magicTitle);
  const magicCopy = document.createElement("div");
  magicCopy.className = "first-run-pillar-copy";
  magicCopy.textContent = "Try \"explain this.\" It is the fastest way to feel Nova become useful without learning the whole system first.";
  magicMoment.appendChild(magicCopy);
  card.appendChild(magicMoment);

  const trustNote = document.createElement("p");
  trustNote.className = "first-run-note";
  trustNote.textContent = "No background automation. No hidden memory. No surprises. Just intelligence under your control.";
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
      label: "Connection Status",
      fn: () => {
        setActivePage("settings");
        safeWSSend({ text: "connection status", silent_widget_refresh: true });
        requestSettingsRuntimeRefresh(true);
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
      label: "Start Here",
      fn: () => {
        setActivePage("home");
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
  const checklistSummary = $("intro-checklist-summary");
  const checklistGrid = $("intro-checklist-grid");
  const nextStepCopy = $("intro-next-step-copy");
  const firstSuccessCopy = $("intro-first-success-copy");
  const firstSuccessGrid = $("intro-first-success-grid");
  const settingsBtn = $("btn-intro-open-settings");
  const connectionsBtn = $("btn-intro-open-connections");
  const openHomeBtn = $("btn-intro-open-home-ready");
  const currentMode = getSetupModeMeta();
  const checklistItems = getSetupReadinessItems();
  const firstSuccess = getIntroFirstSuccessItems(checklistItems);
  const profile = getProfileSetupState();
  const healthyConnections = getConnectionHealthyCount();
  if (modeBadge) modeBadge.textContent = currentMode.badge;
  if (modeCopy) modeCopy.textContent = `Current setup: ${currentMode.label}. ${currentMode.copy}`;
  if (checklistSummary) checklistSummary.textContent = buildSetupReadinessSummary(checklistItems);
  renderSetupReadinessGrid(checklistGrid, checklistItems);
  if (nextStepCopy) nextStepCopy.textContent = getSetupNextStepCopy(checklistItems);
  if (firstSuccessCopy) firstSuccessCopy.textContent = String(firstSuccess.summary || "").trim() || "Nova is checking the easiest high-value move for this device.";
  if (settingsBtn) settingsBtn.textContent = profile.hasIdentity ? "Open Settings" : "Set your name";
  if (connectionsBtn) connectionsBtn.textContent = healthyConnections > 0 ? "Manage connections" : "Add a connection";
  if (openHomeBtn) openHomeBtn.textContent = (profile.hasIdentity && healthyConnections > 0) ? "You're ready — open Home" : "Open Home anyway";
  renderIntroFirstSuccessGrid(firstSuccessGrid, firstSuccess);
  renderHomeLaunchWidget();
}

/* Agent and settings surfaces moved to dashboard-control-center.js. */

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
    listening: isHeyNovaWakeWordEnabled()
      ? `Off in the background (only when you press mic, then say "${HEY_NOVA_WAKE_WORD}")`
      : "Off in the background (only when you press mic)",
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
  const safeInit = (label, fn) => {
    try {
      fn();
    } catch (error) {
      console.error(`[nova-bootstrap] ${label} failed`, error);
    }
  };

  applyAccessibilityFromStorage();
  injectPrimaryNav();
  injectHeaderMenus();
  setupPageNavigation();
  setOrbStatus("READY");
  setPTTButtonState("idle");
  ensureDatalist();
  setupPrimaryChatControls();
  safeInit("connectWebSocket", () => connectWebSocket());
  safeInit("renderMorningPanel", () => renderMorningPanel());
  safeInit("renderWorkflowFocusWidget", () => renderWorkflowFocusWidget());
  safeInit("renderLiveHelpWidget", () => renderLiveHelpWidget());
  safeInit("renderHomeLaunchWidget", () => renderHomeLaunchWidget());
  safeInit("renderHeaderStatus", () => renderHeaderStatus("chat"));
  safeInit("renderContextInsight", () => renderContextInsight(""));
  safeInit("renderThreadMapWidget", () => renderThreadMapWidget({}));
  safeInit("renderMemoryOverviewWidget", () => renderMemoryOverviewWidget({}));
  safeInit("renderToneOverviewWidget", () => renderToneOverviewWidget({}));
  safeInit("renderNotificationOverviewWidget", () => renderNotificationOverviewWidget({}));
  safeInit("renderPatternReviewWidget", () => renderPatternReviewWidget({}));
  safeInit("renderOperatorHealthWidget", () => renderOperatorHealthWidget({}));
  safeInit("renderCapabilitySurfaceWidget", () => renderCapabilitySurfaceWidget({}));
  safeInit("renderTrustPanel", () => renderTrustPanel());
  safeInit("renderWorkspaceHomeWidget", () => renderWorkspaceHomeWidget({}));
  safeInit("renderProjectStructureMapWidget", () => renderProjectStructureMapWidget({}));
  safeInit("renderAssistiveNoticesWidget", () => renderAssistiveNoticesWidget({}));
  safeInit("renderOpenClawDeliveryWidget", () => renderOpenClawDeliveryWidget());
  safeInit("renderWorkspaceBoardPage", () => renderWorkspaceBoardPage());
  safeInit("renderOpenClawAgentPage", () => renderOpenClawAgentPage());
  safeInit("renderPolicyCenterPage", () => renderPolicyCenterPage());
  safeInit("renderTrustCenterPage", () => renderTrustCenterPage());
  safeInit("renderIntroPage", () => renderIntroPage());
  safeInit("renderSettingsPage", () => renderSettingsPage());
  safeInit("renderIntelligenceBriefWidget", () => renderIntelligenceBriefWidget());
  safeInit("renderPersonalLayerWidget", () => renderPersonalLayerWidget());
  safeInit("renderQuickActions", () => renderQuickActions());
  safeInit("setupHintsPanelToggle", () => setupHintsPanelToggle());
  safeInit("renderCommandDiscovery", () => renderCommandDiscovery());
  safeInit("setupMorningWidgetToggle", () => setupMorningWidgetToggle());
  setupProfileHandlers();
  setupConnectionCardHandlers();
  startMorningFallbackTimer();
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) hydrateDashboardWidgets();
  });
  window.addEventListener("focus", hydrateDashboardWidgets);
  window.addEventListener("beforeunload", () => stopLiveHelpSession("", false));
  ensureSingleWelcomeMessage();
  showFirstRunGuideIfNeeded();

  const workflowRefineBtn = $("btn-workflow-refine");
  if (workflowRefineBtn) workflowRefineBtn.addEventListener("click", () => {
    const chatInput = $("chat-input");
    if (!chatInput) return;
    chatInput.focus();
    chatInput.value = workflowFocusState.lastUserInput || "";
    chatInput.select();
  });

  const workflowShowStepsBtn = $("btn-workflow-show-steps");
  if (workflowShowStepsBtn) workflowShowStepsBtn.addEventListener("click", () => {
    const focus = String(workflowFocusState.lastUserInput || "").trim();
    if (!focus) return;
    injectUserText(`Turn this into a step-by-step plan and keep the checkpoints clear: ${focus}`, "text");
  });

  const workflowResetBtn = $("btn-workflow-reset");
  if (workflowResetBtn) workflowResetBtn.addEventListener("click", () => {
    resetWorkflowFocusState();
    const chatInput = $("chat-input");
    if (chatInput) {
      chatInput.focus();
      chatInput.value = "";
    }
  });

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

  const morningCalendarConnectBtn = $("btn-morning-calendar-connect");
  if (morningCalendarConnectBtn) morningCalendarConnectBtn.addEventListener("click", () => {
    setActivePage("settings");
  });

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

  const homeThreadsBtn = $("btn-home-threads");
  if (homeThreadsBtn) homeThreadsBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("show threads", "text");
  });

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

  const introHomeBtn = $("btn-intro-open-home");
  if (introHomeBtn) introHomeBtn.addEventListener("click", () => setActivePage("home"));

  const introSettingsBtn = $("btn-intro-open-settings");
  if (introSettingsBtn) introSettingsBtn.addEventListener("click", () => setActivePage("settings"));

  const introRefreshSetupBtn = $("btn-intro-refresh-setup");
  if (introRefreshSetupBtn) {
    introRefreshSetupBtn.addEventListener("click", () => {
      requestSettingsRuntimeRefresh(true);
      requestOpenClawAgentRefresh(true);
      safeWSSend({ text: "system status", silent_widget_refresh: true });
      safeWSSend({ text: "connection status", silent_widget_refresh: true });
      loadConnectionsData();
    });
  }

  const introOpenConnectionsBtn = $("btn-intro-open-connections");
  if (introOpenConnectionsBtn) {
    introOpenConnectionsBtn.addEventListener("click", () => {
      setActivePage("settings");
      safeWSSend({ text: "connection status", silent_widget_refresh: true });
      requestSettingsRuntimeRefresh(true);
      loadConnectionsData();
    });
  }

  const introOpenHomeReadyBtn = $("btn-intro-open-home-ready");
  if (introOpenHomeReadyBtn) {
    introOpenHomeReadyBtn.addEventListener("click", () => {
      localStorage.setItem(STORAGE_KEYS.firstRunDone, "1");
      setActivePage("home");
    });
  }

  const introLandingBtn = $("btn-intro-open-landing");
  if (introLandingBtn) introLandingBtn.addEventListener("click", () => {
    window.open("/landing", "_blank", "noopener");
  });

  const introBriefBtn = $("btn-intro-daily-brief");
  if (introBriefBtn) introBriefBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("explain this", "text");
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
    safeWSSend({ text: "operational context", silent_widget_refresh: true });
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

  const trustCenterPolicyMapBtn = $("btn-trust-center-policy-map");
  if (trustCenterPolicyMapBtn) trustCenterPolicyMapBtn.addEventListener("click", () => {
    safeWSSend({ text: "what can policies run", silent_widget_refresh: true });
    safeWSSend({ text: "trust center", silent_widget_refresh: true });
  });

  const trustCenterBridgeStatusBtn = $("btn-trust-center-bridge-status");
  if (trustCenterBridgeStatusBtn) trustCenterBridgeStatusBtn.addEventListener("click", () => {
    safeWSSend({ text: "bridge status", silent_widget_refresh: true });
    safeWSSend({ text: "trust center", silent_widget_refresh: true });
  });

  const trustCenterAgentBtn = $("btn-trust-center-agent");
  if (trustCenterAgentBtn) trustCenterAgentBtn.addEventListener("click", () => setActivePage("agent"));

  const trustCenterVoiceCheckBtn = $("btn-trust-center-voice-check");
  if (trustCenterVoiceCheckBtn) trustCenterVoiceCheckBtn.addEventListener("click", () => {
    setActivePage("chat");
    injectUserText("voice check", "text");
  });

  const trustCenterSettingsBtn = $("btn-trust-center-settings");
  if (trustCenterSettingsBtn) trustCenterSettingsBtn.addEventListener("click", () => setActivePage("settings"));

  const operationalContextRefreshBtn = $("btn-operational-context-refresh");
  if (operationalContextRefreshBtn) {
    operationalContextRefreshBtn.addEventListener("click", () => requestOperationalContextRefresh(true));
  }

  const operationalContextResetBtn = $("btn-operational-context-reset");
  if (operationalContextResetBtn) {
    operationalContextResetBtn.addEventListener("click", () => {
      setActivePage("chat");
      injectUserText("reset operational context", "text");
    });
  }

  const assistiveRefreshBtn = $("btn-assistive-notices-refresh");
  if (assistiveRefreshBtn) {
    assistiveRefreshBtn.addEventListener("click", () => requestAssistiveNoticesRefresh(true));
  }

  const assistiveOpenSettingsBtn = $("btn-assistive-open-settings");
  if (assistiveOpenSettingsBtn) {
    assistiveOpenSettingsBtn.addEventListener("click", () => setActivePage("settings"));
  }

  const settingsOpenIntroBtn = $("btn-settings-open-intro");
  if (settingsOpenIntroBtn) settingsOpenIntroBtn.addEventListener("click", () => setActivePage("intro"));

  const settingsOpenTrustBtn = $("btn-settings-open-trust");
  if (settingsOpenTrustBtn) settingsOpenTrustBtn.addEventListener("click", () => setActivePage("trust"));

  const settingsOpenHomeBtn = $("btn-settings-open-home");
  if (settingsOpenHomeBtn) settingsOpenHomeBtn.addEventListener("click", () => setActivePage("home"));

  const settingsOpenAgentBtn = $("btn-settings-open-agent");
  if (settingsOpenAgentBtn) settingsOpenAgentBtn.addEventListener("click", () => setActivePage("agent"));

  const settingsOpenConnectionsBtn = $("btn-settings-open-connections");
  if (settingsOpenConnectionsBtn) settingsOpenConnectionsBtn.addEventListener("click", () => {
    safeWSSend({ text: "connection status", silent_widget_refresh: true });
    requestSettingsRuntimeRefresh(true);
    renderSettingsPage();
    loadConnectionsData();
  });

  const settingsRefreshRuntimeBtn = $("btn-settings-refresh-runtime");
  if (settingsRefreshRuntimeBtn) settingsRefreshRuntimeBtn.addEventListener("click", () => {
    requestSettingsRuntimeRefresh(true);
  });

  const settingsResetDefaultsBtn = $("btn-settings-reset-defaults");
  if (settingsResetDefaultsBtn) settingsResetDefaultsBtn.addEventListener("click", () => {
    resetRuntimeSettings();
  });

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

  const agentRefreshBtn = $("btn-agent-refresh");
  if (agentRefreshBtn) agentRefreshBtn.addEventListener("click", () => requestOpenClawAgentRefresh(true));

  const agentOpenSettingsBtn = $("btn-agent-open-settings");
  if (agentOpenSettingsBtn) agentOpenSettingsBtn.addEventListener("click", () => setActivePage("settings"));

  const agentOpenTrustBtn = $("btn-agent-open-trust");
  if (agentOpenTrustBtn) agentOpenTrustBtn.addEventListener("click", () => setActivePage("trust"));

  const agentOpenHomeBtn = $("btn-agent-open-home");
  if (agentOpenHomeBtn) agentOpenHomeBtn.addEventListener("click", () => setActivePage("home"));

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

  const memoryRecentBtn = $("btn-memory-recent");
  if (memoryRecentBtn) memoryRecentBtn.addEventListener("click", () => {
    sendSilentMemoryCommand("recent memories");
  });

  const memoryThreadsBtn = $("btn-memory-threads");
  if (memoryThreadsBtn) memoryThreadsBtn.addEventListener("click", () => {
    sendSilentMemoryCommand("memory list thread this");
  });

  const memoryExportBtn = $("btn-memory-export");
  if (memoryExportBtn) memoryExportBtn.addEventListener("click", () => {
    downloadMemoryExport();
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
    queueMemoryInlineConfirmation(
      `Lock ${selected.title || selected.id}`,
      `memory lock ${selected.id}`,
      `Lock ${selected.title || selected.id}? Nova will still route this through the governed path.`
    );
    renderMemoryCenterSurface();
  });

  const memoryDetailUnlockBtn = $("btn-memory-detail-unlock");
  if (memoryDetailUnlockBtn) memoryDetailUnlockBtn.addEventListener("click", () => {
    const selected = getSelectedMemoryItem();
    if (!selected || !selected.id) return;
    queueMemoryInlineConfirmation(
      `Unlock ${selected.title || selected.id}`,
      `memory unlock ${selected.id}`,
      `Unlock ${selected.title || selected.id}? Nova will still validate the request before changing it.`
    );
    renderMemoryCenterSurface();
  });

  const memoryDetailDeferBtn = $("btn-memory-detail-defer");
  if (memoryDetailDeferBtn) memoryDetailDeferBtn.addEventListener("click", () => {
    const selected = getSelectedMemoryItem();
    if (!selected || !selected.id) return;
    queueMemoryInlineConfirmation(
      `Defer ${selected.title || selected.id}`,
      `memory defer ${selected.id}`,
      `Defer ${selected.title || selected.id}? Nova will still keep the change inside the governed path.`
    );
    renderMemoryCenterSurface();
  });

  const memoryDetailDeleteBtn = $("btn-memory-detail-delete");
  if (memoryDetailDeleteBtn) memoryDetailDeleteBtn.addEventListener("click", () => {
    const selected = getSelectedMemoryItem();
    if (!selected || !selected.id) return;
    queueMemoryInlineConfirmation(
      `Delete ${selected.title || selected.id}`,
      `delete memory ${selected.id}`,
      `Delete ${selected.title || selected.id}? Nova will still require the governed path for the final request.`
    );
    renderMemoryCenterSurface();
  });

  const memoryInlineConfirmBtn = $("btn-memory-inline-confirm");
  if (memoryInlineConfirmBtn) memoryInlineConfirmBtn.addEventListener("click", () => {
    const command = String((memoryPendingActionState && memoryPendingActionState.command) || "").trim();
    if (!command) return;
    injectUserText(command, "text");
    clearMemoryInlineConfirmation();
    renderMemoryCenterSurface();
  });

  const memoryInlineCancelBtn = $("btn-memory-inline-cancel");
  if (memoryInlineCancelBtn) memoryInlineCancelBtn.addEventListener("click", () => {
    clearMemoryInlineConfirmation();
    renderMemoryCenterSurface();
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

  const policyCreateStatusBtn = $("btn-policy-create-status");
  if (policyCreateStatusBtn) policyCreateStatusBtn.addEventListener("click", () => {
    injectUserText("policy create weekday system status at 8:00 am", "text");
  });

  const policyCapabilityMapBtn = $("btn-policy-capability-map");
  if (policyCapabilityMapBtn) policyCapabilityMapBtn.addEventListener("click", () => {
    safeWSSend({ text: "what can policies run", silent_widget_refresh: true });
    requestPolicyOverviewRefresh(true);
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

  const liveHelpStartBtn = $("btn-live-help-start");
  if (liveHelpStartBtn) liveHelpStartBtn.addEventListener("click", () => {
    startLiveHelpSession();
  });

  const liveHelpExplainBtn = $("btn-live-help-explain");
  if (liveHelpExplainBtn) liveHelpExplainBtn.addEventListener("click", () => {
    if (!liveHelpState.active) return;
    requestLiveHelpAnalysis("explain this page", { echoUserMessage: false, updateFocus: true });
  });

  const liveHelpStopBtn = $("btn-live-help-stop");
  if (liveHelpStopBtn) liveHelpStopBtn.addEventListener("click", () => {
    stopLiveHelpSession();
  });
});
