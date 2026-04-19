# Nova Installer

## Windows

### Option A: Run the .exe installer (recommended for end users)

1. Download `NovaSetup-0.1.0.exe` from [GitHub Releases](https://github.com/christopherbdaugherty96/NovaLIS/releases).
2. Double-click to run. Follow the wizard.
3. The installer handles Python, Ollama, model download, and shortcuts.
4. If setup fails, inspect `C:\Program Files\Nova\bootstrap.log` for the failing step and rerun the installer after fixing that dependency.
5. If Nova starts but then immediately closes, inspect `C:\Program Files\Nova\scripts\pids\nova.log` for the server startup error.

### Option B: Run the bootstrap script directly (for developers)

```powershell
powershell -ExecutionPolicy Bypass -File installer\windows\nova_bootstrap.ps1
```

The bootstrap script now exits with explicit errors for failed venv creation,
`pip install -e .`, and Nova startup, so `bootstrap.log` should show the exact
step that failed.

### Building the .exe from source

1. Install [Inno Setup 6+](https://jrsoftware.org/isinfo.php).
2. Open `installer/windows/nova_setup.iss` in the Inno Setup Compiler.
3. Press Ctrl+F9. The output lands in `dist/NovaSetup-0.1.0.exe`.

## macOS

Not yet available. See the [roadmap](../4-15-26%20NEW%20ROADMAP/MasterRoadMap.md) — macOS `.app` bundle is planned after Windows installer is validated.

## Manual install (any platform)

```bash
pip install -e .
python scripts/fetch_models.py
nova-start
```
