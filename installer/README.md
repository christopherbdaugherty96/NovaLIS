# Nova Installer

## Windows

### Option A: Run the .exe installer (recommended for end users)

1. Download `NovaSetup-0.1.0.exe` from [GitHub Releases](https://github.com/christopherbdaugherty96/NovaLIS/releases).
2. Double-click to run. Follow the wizard.
3. The installer handles Python, Ollama, model download, and shortcuts.
4. If setup fails, inspect `C:\Program Files\Nova\bootstrap.log` for the failing step and rerun the installer after fixing that dependency.
5. If Nova starts but then immediately closes, inspect `C:\Program Files\Nova\scripts\pids\nova.log` for the server startup error.
6. On a successful first launch, wait up to 90 seconds for local services to start, then try `daily brief`, `news`, or `system status`.

### Option B: Run the bootstrap script directly (for developers)

```powershell
powershell -ExecutionPolicy Bypass -File installer\windows\nova_bootstrap.ps1
```

The bootstrap script now exits with explicit errors for failed venv creation,
`pip install -e .`, and Nova startup, so `bootstrap.log` should show the exact
step that failed.

### Runtime state location

Nova stores changing runtime state outside the protected installer directory.

When Nova runs from a writable source checkout, such as `C:\Nova-Project`,
runtime state stays with that checkout. When Nova runs from a protected Windows
install location, such as `C:\Program Files\Nova`, runtime state is written to:

```text
%LOCALAPPDATA%\Nova
```

This includes the ledger, model version lock, settings, memory state, usage
tracking, profiles, policies, OpenClaw runtime state, notifications, and screen
captures. Installer validation should confirm that the installed app does not
attempt to write mutable state into `C:\Program Files\Nova`.

### Installer validation checklist

After installing or rebuilding the Windows package:

1. Start Nova from the shortcut or `start_nova.bat`.
2. Confirm `http://127.0.0.1:8000/phase-status` responds.
3. Open Settings and confirm the local model reports as available.
4. If prompted, confirm the model update and restart Nova.
5. Confirm `current_model_hash.txt` is written under `%LOCALAPPDATA%\Nova\models`.
6. Trigger a governed action or status check and confirm `ledger.jsonl` is written under `%LOCALAPPDATA%\Nova\data`.
7. Save a memory or setting, restart Nova, and confirm it persists.
8. Check `scripts\pids\nova.log` for startup errors.

### Building the .exe from source

1. Install [Inno Setup 6+](https://jrsoftware.org/isinfo.php).
2. Open `installer/windows/nova_setup.iss` in the Inno Setup Compiler.
3. Press Ctrl+F9. The output lands in `dist/NovaSetup-0.1.0.exe`.

Important: the existing `dist\NovaSetup-0.1.0.exe` may predate source changes.
After runtime-state or startup changes, rebuild the installer before treating
the packaged app as fixed.

## macOS

Not yet available. See the [roadmap](../4-15-26%20NEW%20ROADMAP/MasterRoadMap.md) — macOS `.app` bundle is planned after Windows installer is validated.

## Manual install (any platform)

```bash
pip install -e .
python scripts/fetch_models.py
nova-start
```
