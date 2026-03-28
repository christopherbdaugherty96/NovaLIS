from __future__ import annotations

from tests.adversarial._helpers import SRC_ROOT, read_text


EXECUTOR_CONSTRUCTORS = (
    "WebSearchExecutor(",
    "WebpageLaunchExecutor(",
    "VolumeExecutor(",
    "MediaExecutor(",
    "BrightnessExecutor(",
    "OpenFolderExecutor(",
    "OSDiagnosticsExecutor(",
    "MultiSourceReportingExecutor(",
    "NewsIntelligenceExecutor(",
    "StoryTrackerExecutor(",
    "AnalysisDocumentExecutor(",
    "ResponseVerificationExecutor(",
)
ALLOWED_EXECUTOR_CALLER = SRC_ROOT / "governor" / "governor.py"
ALLOWED_EXECUTOR_COMPOSERS = {
    SRC_ROOT / "executors" / "external_reasoning_executor.py",
}



def test_executor_instantiation_only_in_governor():
    offenders: list[str] = []
    for py in SRC_ROOT.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        text = read_text(py)
        if any(token in text for token in EXECUTOR_CONSTRUCTORS):
            if py != ALLOWED_EXECUTOR_CALLER and py not in ALLOWED_EXECUTOR_COMPOSERS and "class Web" not in text:
                offenders.append(str(py))

    assert not offenders, "Executor instantiation found outside governor:\n" + "\n".join(offenders)



def test_no_direct_network_request_calls_outside_mediator_and_executors():
    allowed_dirs = {
        str(SRC_ROOT / "governor"),
        str(SRC_ROOT / "executors"),
    }
    allowed_files = {
        str(SRC_ROOT / "conversation" / "deepseek_bridge.py"),
        str(SRC_ROOT / "providers" / "openai_responses_lane.py"),
        str(SRC_ROOT / "services" / "weather_service.py"),
        str(SRC_ROOT / "tools" / "rss_fetch.py"),
    }
    offenders: list[str] = []

    for py in SRC_ROOT.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        text = read_text(py)
        if ".request(" in text and "network_mediator" in text:
            in_allowed = any(str(py).startswith(prefix) for prefix in allowed_dirs)
            if not in_allowed and str(py) not in allowed_files:
                offenders.append(str(py))

    assert not offenders, "Potential direct network request surfaces detected:\n" + "\n".join(offenders)
