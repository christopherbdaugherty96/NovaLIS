import json
import subprocess
from pathlib import Path

from src.conversation.meta_intent_handler import MetaIntentHandler

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "nova_backend" / "static"
MIRROR = ROOT / "Nova-Frontend-Dashboard"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _evaluate_suggestion_availability(providers: dict[str, dict[str, bool]]) -> dict[str, object]:
    source_path = json.dumps(str(STATIC / "dashboard-chat-news.js"))
    dashboard_path = json.dumps(str(STATIC / "dashboard.js"))
    provider_state = json.dumps(providers)
    script = f"""
const fs = require("fs");
const vm = require("vm");
const source = fs.readFileSync({source_path}, "utf8");
const dashboardSource = fs.readFileSync({dashboard_path}, "utf8");
const suggestionSource = source.slice(
  source.indexOf("function isAvailableSuggestionProvider"),
  source.indexOf("function renderQuickActions")
);
const headerStart = source.indexOf("function renderHeaderQuickRuns");
const headerSource = source.slice(headerStart, source.indexOf('window.addEventListener("DOMContentLoaded"', headerStart));
const introStart = dashboardSource.indexOf("function getIntroFirstSuccessItems");
const introSource = dashboardSource.slice(introStart, dashboardSource.indexOf("function createIntroFirstSuccessCard", introStart));
const providers = {provider_state};
const quickRuns = {{
  children: [],
  appendChild(child) {{ this.children.push(child); }},
}};
const context = {{
  threadMapState: {{ threads: [] }},
  getConnectionCardProvider: (providerId) => providers[providerId] || null,
  getConnectionCardProviders: () => Object.entries(providers).map(([id, provider]) => ({{ id, ...provider }})),
  getConnectionHealthyCount: () => Object.values(providers).filter((provider) => provider.connected === true).length,
  getProfileSetupState: () => ({{ hasIdentity: true, displayName: "" }}),
  $: (id) => id === "header-quick-runs" ? quickRuns : null,
  clear: (node) => {{ node.children = []; }},
  document: {{ createElement: () => ({{ addEventListener: () => {{}} }}) }},
}};
vm.runInNewContext(suggestionSource, context);
vm.runInNewContext(headerSource, context);
vm.runInNewContext(introSource, context);
context.renderHeaderQuickRuns();
const intro = context.getIntroFirstSuccessItems([
  {{ key: "runtime_connection", ready: true }},
  {{ key: "local_model_route", ready: true }},
]);
process.stdout.write(JSON.stringify({{
  weather: context.isUserFacingSuggestionAvailable("weather"),
  research: context.isUserFacingSuggestionAvailable("research latest technology news"),
  news: context.isUserFacingSuggestionAvailable("today's news"),
  calendar: context.isUserFacingSuggestionAvailable("today's schedule"),
  quickRuns: quickRuns.children.map((item) => item.textContent),
  introTitles: intro.items.map((item) => item.title),
  introCards: intro.items.map((item) => ({{ title: item.title, badge: item.badge, copy: item.copy }})),
}}));
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def _evaluate_connection_card(provider: dict[str, object]) -> dict[str, str]:
    source_path = json.dumps(str(STATIC / "dashboard-chat-news.js"))
    provider_state = json.dumps(provider)
    script = f"""
const fs = require("fs");
const vm = require("vm");
const source = fs.readFileSync({source_path}, "utf8");
const start = source.indexOf("let _connectionsData = []");
const end = source.indexOf("function _setCardHealth", start);
const connectionSource = source.slice(start, end);
const provider = {provider_state};
const makeNode = () => ({{
  children: [], dataset: {{}}, style: {{}}, className: "", textContent: "", hidden: false,
  appendChild(child) {{ this.children.push(child); return child; }},
  addEventListener() {{}}, setAttribute() {{}}, focus() {{}}, remove() {{}},
}});
const context = {{ document: {{ createElement: makeNode }}, provider }};
vm.runInNewContext(connectionSource + "\\n_connectionsData = [provider];", context);
const card = context._buildConnectionCard(provider);
process.stdout.write(JSON.stringify({{
  summary: context.buildConnectionsSummaryCopy(),
  className: card.className,
  badge: card.children[0].children[2].textContent,
}}));
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def _evaluate_setup_readiness(connection_stats: dict[str, int | bool]) -> dict[str, object]:
    source_path = json.dumps(str(STATIC / "dashboard.js"))
    stats_state = json.dumps(connection_stats)
    script = f"""
const fs = require("fs");
const vm = require("vm");
const source = fs.readFileSync({source_path}, "utf8");
const start = source.indexOf("function getSetupReadinessItems");
const end = source.indexOf("function buildSetupReadinessSummary", start);
const readinessSource = source.slice(start, end);
const connectionStats = {stats_state};
const context = {{
  WebSocket: {{ OPEN: 1 }},
  ws: {{ readyState: 1 }},
  getHeaderConnectionPresentation: () => ({{ label: "Connected" }}),
  getSetupModeMeta: () => ({{ label: "Local", copy: "Local-first setup." }}),
  getProfileSetupState: () => ({{ hasIdentity: true, displayName: "" }}),
  getConnectionRuntimeItem: () => ({{ value: "Available", note: "Local model is ready." }}),
  getConnectionCardStats: () => connectionStats,
  getConnectionCardProvider: () => null,
  getConnectionHealthyCount: () => connectionStats.connectedCount || 0,
  trustReviewState: {{ connectionRuntime: {{}}, voiceRuntime: {{}}, bridgeRuntime: {{}} }},
  settingsRuntimeState: {{ loaded: true, permissions: {{ remote_bridge_enabled: true, home_agent_enabled: true }} }},
  openClawAgentState: {{ snapshot: {{}} }},
}};
vm.runInNewContext(readinessSource, context);
const provider = context.getSetupReadinessItems().find((item) => item.key === "provider_keys");
process.stdout.write(JSON.stringify(provider));
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def test_beta_ui_does_not_advertise_unproven_live_or_builder_claims():
    index = _read(STATIC / "index.html")
    config = _read(STATIC / "dashboard-config.js")
    control = _read(STATIC / "dashboard-control-center.js")
    chat = _read(STATIC / "dashboard-chat-news.js")
    visible_truth = "\n".join((index, config, control, chat))

    for banned in (
        "build me a landing page for my business",
        "Nova finished the current step",
        "Live Screen Help",
        "Start live help",
        'Say "Hey Nova"',
        "Live screen help is already listening",
    ):
        assert banned not in visible_truth

    assert 'id="live-help-widget"' not in index
    assert 'id="btn-live-help-start"' not in index
    assert "startLiveHelpSession(" not in chat


def test_generic_suggestions_exclude_context_and_configuration_only_actions():
    config = _read(STATIC / "dashboard-config.js")
    chat = _read(STATIC / "dashboard-chat-news.js")

    for context_only in (
        "which one should I download",
        "why this recommendation",
        "continue where I left off",
        "what was I working on",
        "which project needs attention",
        "what are my biggest blockers",
    ):
        assert context_only not in config

    for conditional in (
        "show my schedule",
        "check my calendar",
        '"volume up"',
        '"brightness down"',
        '"set volume 40"',
        '"set brightness 50"',
    ):
        assert conditional not in config

    assert 'label: "Draft calendar rule"' in config
    assert 'label: "Draft weather rule"' in config
    assert 'label: "Create calendar rule"' not in config
    assert 'label: "Create weather rule"' not in config
    assert 'q === "calendar"' in chat
    assert 'return isAvailableSuggestionProvider("brave")' in chat
    assert "hasProjectSuggestionContext()" in chat
    assert 'const actions = getQuickActionsForPage(page).filter((action) => isUserFacingSuggestionAvailable(action.command));' in chat
    assert 'q.startsWith("create analysis report")' not in chat


def test_workflow_narration_stays_response_scoped_not_outcome_scoped():
    control = _read(STATIC / "dashboard-control-center.js")
    chat = _read(STATIC / "dashboard-chat-news.js")

    assert "Nova returned a response for the current request." in control
    assert "Response received." in control
    assert "Nova finished the current step" not in control
    assert "Turning your idea into a build plan" not in control
    assert "Planning what would be needed" in control
    assert "build me a landing page for my business" not in chat
    assert 'goal: "Start with something simple like \\"Help me plan my day.\\""' in control


def test_home_filters_stale_internal_and_projectless_state_from_normal_output():
    workspace = _read(STATIC / "dashboard-workspace.js")

    assert "function isStaleDatedWatch" in workspace
    assert ".filter(isUserFacingWorkspaceHomeItem)" in workspace
    assert "function userFacingWorkspaceValue" in workspace
    assert "local_project_structure_map" in workspace
    assert "No project thread is active right now." in workspace
    assert "const homeRows = hasProjectContext" in workspace


def test_remote_bridge_settings_distinguish_permission_from_availability():
    control = _read(STATIC / "dashboard-control-center.js")

    assert "Permission and runtime availability are shown separately." in control
    assert 'Permission: ${item.enabled ? "Enabled" : "Paused"} · Availability: ${availability}' in control
    assert "Unavailable — token not configured" in control
    assert "Permission does not make the bridge available without its token." in control


def test_capability_help_describes_local_first_and_bounded_controls():
    response = MetaIntentHandler().handle("who are you", session_state={"turn_count": 1})

    assert response is not None
    lowered = response.lower()
    assert "local-first" in lowered
    assert "external/network paths are explicit, governed, and visible when used" in lowered
    assert "bounded local controls" in lowered
    assert "everything runs on your machine" not in lowered
    assert "control parts of your computer" not in lowered
    assert "built to run entirely on your own computer" not in lowered
    assert "not one that sends your data somewhere else" not in lowered


def test_frontend_truth_surfaces_remain_byte_synced():
    for name in (
        "index.html",
        "dashboard-config.js",
        "dashboard-control-center.js",
        "dashboard-chat-news.js",
        "dashboard-workspace.js",
        "dashboard.js",
    ):
        assert (STATIC / name).read_bytes() == (MIRROR / name).read_bytes()

def test_page_quick_actions_use_runtime_availability_gating():
    chat_news = _read(STATIC / "dashboard-chat-news.js")

    assert "getQuickActionsForPage(page).filter((action) => isUserFacingSuggestionAvailable(action.command))" in chat_news
    assert 'return isAvailableSuggestionProvider("brave")' in chat_news
    assert 'return isAvailableSuggestionProvider("news")' in chat_news
    assert 'return isAvailableSuggestionProvider("calendar")' in chat_news
    assert 'return isAvailableSuggestionProvider("weather")' in chat_news
    assert 'provider.configuration_source === "stored"' in chat_news
    assert 'provider.configuration_source === "environment"' in chat_news
    assert 'provider.health_ok !== false' in chat_news
    assert "return hasProjectSuggestionContext()" in chat_news


def test_header_quick_runs_refresh_with_provider_availability():
    chat_news = _read(STATIC / "dashboard-chat-news.js")

    assert 'actionsGrid.id = "header-quick-runs"' in chat_news
    assert 'function renderHeaderQuickRuns()' in chat_news
    assert '].filter((item) => isUserFacingSuggestionAvailable(item.command)).forEach((item) => {' in chat_news
    assert 'renderHeaderQuickRuns();' in chat_news
    unavailable = _evaluate_suggestion_availability({})
    assert unavailable["research"] is False
    assert unavailable["news"] is False
    assert "Research a topic" not in unavailable["quickRuns"]
    assert "Today's news" not in unavailable["quickRuns"]

    available = _evaluate_suggestion_availability({"brave": {"connected": True}, "news": {"connected": True}})
    assert available["research"] is True
    assert available["news"] is True
    assert "Research a topic" in available["quickRuns"]
    assert "Today's news" in available["quickRuns"]

    environment_configured = _evaluate_suggestion_availability(
        {
            "brave": {"configured": True, "environment_configured": True, "configuration_source": "environment", "has_key": False, "health_ok": None, "connected": False},
            "news": {"configured": True, "environment_configured": True, "configuration_source": "environment", "has_key": False, "health_ok": None, "connected": False},
        }
    )
    assert environment_configured["research"] is True
    assert environment_configured["news"] is True
    assert "Research a topic" in environment_configured["quickRuns"]
    assert "Today's news" in environment_configured["quickRuns"]


def test_weather_availability_accepts_a_configured_environment_provider_but_not_a_known_failed_one():
    assert _evaluate_suggestion_availability({})["weather"] is False
    assert _evaluate_suggestion_availability({"weather": {"connected": True}})["weather"] is True
    assert _evaluate_suggestion_availability(
        {"weather": {"configured": True, "environment_configured": True, "configuration_source": "environment", "has_key": False, "health_ok": None, "connected": False}}
    )["weather"] is True
    assert _evaluate_suggestion_availability(
        {"weather": {"configured": True, "environment_configured": True, "configuration_source": "stored", "has_key": True, "health_ok": False, "connected": False}}
    )["weather"] is False


def test_stored_provider_failure_stays_unavailable_after_environment_propagation():
    failed_after_save_key = {
        "configured": True,
        "environment_configured": True,
        "configuration_source": "stored",
        "has_key": True,
        "health_ok": False,
        "connected": False,
    }
    healthy_stored = {**failed_after_save_key, "health_ok": True, "connected": True}

    assert _evaluate_suggestion_availability({"weather": failed_after_save_key})["weather"] is False
    assert _evaluate_suggestion_availability({"weather": healthy_stored})["weather"] is True


def test_intro_cards_follow_shared_provider_availability_and_truthful_paths():
    dashboard = _read(STATIC / "dashboard.js")
    environment_configured = _evaluate_suggestion_availability(
        {
            "weather": {"configured": True, "environment_configured": True, "configuration_source": "environment", "has_key": False, "health_ok": None, "connected": False},
            "calendar": {"configured": True, "environment_configured": True, "configuration_source": "environment", "has_key": False, "health_ok": None, "connected": False},
            "news": {"configured": True, "environment_configured": True, "configuration_source": "environment", "has_key": False, "health_ok": None, "connected": False},
            "openai": {"configured": True, "environment_configured": True, "configuration_source": "environment", "has_key": False, "health_ok": None, "connected": False},
        }
    )

    assert "Daily brief" in environment_configured["introTitles"]
    assert "Deep research" not in environment_configured["introTitles"]
    assert 'const weatherPresentation = getSuggestionProviderPresentation("weather");' in dashboard
    assert 'const calendarPresentation = getSuggestionProviderPresentation("calendar");' in dashboard
    assert 'const newsPresentation = getSuggestionProviderPresentation("news");' in dashboard
    assert "if (weatherLive && calendarLive && newsLive)" in dashboard
    assert "OpenAI cloud assist" not in dashboard
    assert "Deep research" not in dashboard
    configured_cards = [
        card for card in environment_configured["introCards"]
        if card["title"] in {"My schedule today", "Today's weather", "Today's news", "Research a topic"}
    ]
    assert all(card["badge"] in {"Configured", "Search configured"} for card in configured_cards)
    assert all(word not in " ".join(card["copy"] for card in environment_configured["introCards"]) for word in ("connected", "fresh", "live"))

    no_news = _evaluate_suggestion_availability(
        {
            "weather": {"configured": True, "environment_configured": True, "configuration_source": "environment", "has_key": False, "health_ok": None, "connected": False},
            "calendar": {"configured": True, "environment_configured": True, "configuration_source": "environment", "has_key": False, "health_ok": None, "connected": False},
        }
    )
    assert "Daily brief" not in no_news["introTitles"]


def test_intro_cards_use_verified_language_only_for_verified_stored_providers():
    stored_unverified = _evaluate_suggestion_availability(
        {
            provider: {"configured": True, "configuration_source": "stored", "has_key": True, "health_ok": None, "connected": False}
            for provider in ("weather", "calendar", "news", "brave")
        }
    )
    unverified_cards = [card for card in stored_unverified["introCards"] if card["title"] != "Explain anything"]
    assert all(card["badge"] in {"Full brief", "Configured", "Search configured"} for card in unverified_cards)

    stored_healthy = _evaluate_suggestion_availability(
        {
            provider: {"configured": True, "configuration_source": "stored", "has_key": True, "health_ok": True, "connected": True}
            for provider in ("weather", "calendar", "news", "brave")
        }
    )
    assert any(card["badge"] == "Verified" for card in stored_healthy["introCards"])
    assert all(word not in " ".join(card["copy"] for card in stored_healthy["introCards"]) for word in ("fresh", "connected"))


def test_privacy_copy_describes_automatic_connected_surface_refreshes():
    chat_news = _read(STATIC / "dashboard-chat-news.js")

    assert 'network: "Only when asked"' not in chat_news
    assert "Enabled connected dashboard surfaces may refresh weather, calendar, or news during startup and refresh." in chat_news


def test_connection_cards_keep_configuration_distinct_from_verified_connection():
    chat_news = _read(STATIC / "dashboard-chat-news.js")

    assert 'const configured = providers.filter((provider) => provider && provider.configured === true);' in chat_news
    assert 'provider.health_ok === null' in chat_news
    assert '"Needs verification"' in chat_news
    assert '"Configured"' in chat_news
    assert 'provider.connected === true' in chat_news

    environment_only = _evaluate_connection_card(
        {"id": "weather", "configured": True, "configuration_source": "environment", "has_key": False, "health_ok": None, "connected": False}
    )
    assert environment_only["badge"] == "Configured"
    assert environment_only["className"] == "conn-card conn-card--needed"
    assert "configured but not verified" in environment_only["summary"]

    stored_unverified = _evaluate_connection_card(
        {"id": "weather", "configured": True, "configuration_source": "stored", "has_key": True, "health_ok": None, "connected": False}
    )
    assert stored_unverified["badge"] == "Needs verification"
    assert "configured but not verified" in stored_unverified["summary"]

    stored_healthy = _evaluate_connection_card(
        {"id": "weather", "configured": True, "configuration_source": "stored", "has_key": True, "health_ok": True, "connected": True}
    )
    assert stored_healthy["badge"] == "Connected"
    assert stored_healthy["className"] == "conn-card conn-card--connected"

    stored_failed = _evaluate_connection_card(
        {"id": "weather", "configured": True, "configuration_source": "stored", "has_key": True, "health_ok": False, "connected": False}
    )
    assert stored_failed["badge"] == "Needs attention"
    assert "need attention" in stored_failed["summary"]


def test_home_readiness_uses_configured_and_unverified_provider_truth():
    stored_unverified = _evaluate_setup_readiness(
        {
            "loaded": True,
            "savedCount": 1,
            "configuredCount": 1,
            "connectedCount": 0,
            "failedCount": 0,
            "unverifiedCount": 1,
        }
    )
    assert stored_unverified["status"] == "1 configured; 1 not verified"
    assert "not verified" in stored_unverified["copy"]
    assert "healthy" not in stored_unverified["copy"]

    environment_only = _evaluate_setup_readiness(
        {
            "loaded": True,
            "savedCount": 0,
            "configuredCount": 1,
            "connectedCount": 0,
            "failedCount": 0,
            "unverifiedCount": 1,
        }
    )
    assert environment_only["status"] == "1 configured; 1 not verified"
    assert environment_only["status"] != "Optional"
    assert "healthy" not in environment_only["copy"]

def test_current_focus_only_changes_for_a_manual_request_response():
    control = _read(STATIC / "dashboard-control-center.js")

    assert 'if (!clean || !workflowFocusState.awaitingResponse) return;' in control
    assert 'workflowFocusState.status = "Response ready";' in control
    assert 'workflowFocusState.status = "Ready for review";' not in control


def test_disconnected_news_and_home_copy_do_not_claim_live_or_connected_work():
    index = _read(STATIC / "index.html")

    assert ">Live briefing<" not in index
    assert ">Briefing<" in index
    assert "Nova will show starting points that are available on this device and its connected services." in index


def test_remote_bridge_separates_permission_from_runtime_availability():
    control = _read(STATIC / "dashboard-control-center.js")

    assert '["Permission", permissionEnabled ? "Enabled" : "Paused"]' in control
    assert '["Availability", availabilityLabel]' in control
    assert '"Unavailable — token not configured"' in control
    assert '["Remote permission", setup.remote_bridge_enabled ? "Enabled" : "Paused"]' in control
    assert '["Remote availability", setup.remote_bridge_enabled && setup.remote_bridge_token_configured' in control
    assert 'Permission: ${item.enabled ? "Enabled" : "Paused"} · Availability: ${availability}' in control
    assert "Permission does not make the bridge available without its token." in control


def test_home_filters_internal_paths_and_stale_dated_watch_copy():
    workspace = _read(STATIC / "dashboard-workspace.js")

    assert 'text.includes("local_project_structure_map")' in workspace
    assert "userFacingWorkspaceValue" in workspace
    assert "isStaleDatedWatch" in workspace
    assert "No current assistive notices." in workspace
    assert "No project thread is active right now." in workspace
    assert "const homeRows = hasProjectContext" in workspace


def test_settings_html_does_not_present_wake_word_as_live():
    index = _read(STATIC / "index.html")

    assert "Hey Nova" not in index
    assert "wake phrase" not in index.lower()
    assert "live screen help" not in index.lower()

def test_existing_goals_and_disconnected_service_truth_remain_visible():
    index = _read(STATIC / "index.html")
    awareness_brief = _read(ROOT / "nova_backend" / "src" / "brief" / "awareness_brief.py")

    assert "Goals track visible work. They do not run tasks." in index
    assert "Shopify not connected. Add your store in Settings." in awareness_brief
    assert "Printify integration is not built yet." in awareness_brief
