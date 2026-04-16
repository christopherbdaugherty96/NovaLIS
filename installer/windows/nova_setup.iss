; Nova Windows Installer — Inno Setup Script
; ============================================
;
; Builds a standard Windows .exe installer that:
;   1. Copies the Nova source tree to {app}
;   2. Runs the PowerShell bootstrap (Python, Ollama, venv, pip, model)
;   3. Creates Start Menu shortcuts
;   4. Registers an uninstaller
;
; To compile:
;   1. Install Inno Setup 6+ from https://jrsoftware.org/isinfo.php
;   2. Open this file in Inno Setup Compiler
;   3. Press Ctrl+F9 to build the .exe
;
; The resulting NovaSetup.exe is self-contained (no network needed if
; Python + Ollama are already installed and the model is sideloaded).
;
; NOTE: This script assumes it is compiled from the repo root, with
; the source tree available at the paths below. Adjust SourceDir if
; compiling from a different location.

[Setup]
AppName=Nova
AppVersion=0.1.0
AppPublisher=Christopher Daugherty
AppPublisherURL=https://github.com/christopherbdaugherty96/NovaLIS
DefaultDirName={autopf}\Nova
DefaultGroupName=Nova
OutputDir=..\..\dist
OutputBaseFilename=NovaSetup-0.1.0
Compression=lzma2
SolidCompression=yes
; Require 64-bit Windows
ArchitecturesAllowed=x64compatible
ArchitecturesInstallMode=x64compatible
; Don't require admin unless the user picks Program Files
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; Uninstall
UninstallDisplayName=Nova
UninstallDisplayIcon={app}\nova_backend\static\favicon.ico
; Misc
WizardStyle=modern
SetupIconFile=..\..\nova_backend\static\favicon.ico
LicenseFile=..\..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
; Copy the entire source tree minus git, caches, venv, and build artifacts.
; The bootstrap script will create the venv and install deps.
Source: "..\..\nova_backend\*"; DestDir: "{app}\nova_backend"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "venv\*,__pycache__\*,*.pyc,*.egg-info\*,.env"
Source: "..\..\scripts\*"; DestDir: "{app}\scripts"; Flags: ignoreversion recursesubdirs
Source: "..\..\pyproject.toml"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\start_nova.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\stop_nova.bat"; DestDir: "{app}"; Flags: ignoreversion
; Include the bootstrap script itself
Source: "nova_bootstrap.ps1"; DestDir: "{app}\installer\windows"; Flags: ignoreversion

[Icons]
Name: "{group}\Nova"; Filename: "{app}\nova_backend\venv\Scripts\python.exe"; Parameters: """{app}\scripts\start_daemon.py"""; WorkingDir: "{app}"; Comment: "Launch Nova"; IconFilename: "{app}\nova_backend\static\favicon.ico"
Name: "{group}\Nova (Stop)"; Filename: "{app}\stop_nova.bat"; WorkingDir: "{app}"; Comment: "Stop Nova server"
Name: "{group}\Uninstall Nova"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Nova"; Filename: "{app}\nova_backend\venv\Scripts\python.exe"; Parameters: """{app}\scripts\start_daemon.py"""; WorkingDir: "{app}"; Comment: "Launch Nova"; IconFilename: "{app}\nova_backend\static\favicon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
; Run the bootstrap script after files are copied.
; -ExecutionPolicy Bypass is needed because the user may not have run
; Set-ExecutionPolicy previously. The bootstrap is local, signed by us.
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\installer\windows\nova_bootstrap.ps1"" -InstallDir ""{app}"""; StatusMsg: "Setting up Nova (Python, Ollama, model)..."; Flags: runhidden waituntilterminated
; Offer to launch Nova after install
Filename: "{app}\nova_backend\venv\Scripts\python.exe"; Parameters: """{app}\scripts\start_daemon.py"""; Description: "Launch Nova now"; Flags: postinstall nowait skipifsilent

[UninstallRun]
; Stop Nova before uninstalling
Filename: "{app}\stop_nova.bat"; Flags: runhidden waituntilterminated

[UninstallDelete]
; Clean up the venv and caches that weren't in the original install
Type: filesandordirs; Name: "{app}\nova_backend\venv"
Type: filesandordirs; Name: "{app}\nova_backend\__pycache__"
Type: dirifempty; Name: "{app}"

[Code]
// Show a friendly message if the bootstrap fails
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if not FileExists(ExpandConstant('{app}\nova_backend\venv\Scripts\nova-start.exe')) then
    begin
      MsgBox('Nova was installed but the setup script may not have completed successfully.' + #13#10 +
             'You can re-run the bootstrap manually:' + #13#10#13#10 +
             'powershell -File "' + ExpandConstant('{app}') + '\installer\windows\nova_bootstrap.ps1"',
             mbInformation, MB_OK);
    end;
  end;
end;
