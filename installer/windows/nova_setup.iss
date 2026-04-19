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
DefaultDirName={commonpf64}\Nova
DefaultGroupName=Nova
OutputDir=..\..\dist
OutputBaseFilename=NovaSetup-0.1.0
Compression=lzma2
SolidCompression=yes
; Require 64-bit Windows
ArchitecturesAllowed=x64compatible
; Require admin — writing to Program Files needs elevation
PrivilegesRequired=admin
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
; Bundled Python installer — used by bootstrap if Python is not found
Source: "deps\python-3.12.8-amd64.exe"; DestDir: "{app}\installer\windows\deps"; Flags: ignoreversion

[Icons]
; Shortcuts use start_daemon.py via system python as fallback — the script
; itself will find nova-start or uvicorn and launch properly.
Name: "{group}\Nova"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -WindowStyle Hidden -Command ""& '{app}\nova_backend\venv\Scripts\python.exe' '{app}\scripts\start_daemon.py'"""; WorkingDir: "{app}"; Comment: "Launch Nova"; IconFilename: "{app}\nova_backend\static\favicon.ico"
Name: "{group}\Nova (Stop)"; Filename: "{app}\stop_nova.bat"; WorkingDir: "{app}"; Comment: "Stop Nova server"
Name: "{group}\Uninstall Nova"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Nova"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -WindowStyle Hidden -Command ""& '{app}\nova_backend\venv\Scripts\python.exe' '{app}\scripts\start_daemon.py'"""; WorkingDir: "{app}"; Comment: "Launch Nova"; IconFilename: "{app}\nova_backend\static\favicon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
; Run the bootstrap script after files are copied.
; Log output to a file so failures are diagnosable even when runhidden.
; Note: logging is handled inside the script via Start-Transcript → {app}\bootstrap.log
; Do NOT add shell-redirect operators here — Inno Setup uses CreateProcess, not CMD,
; so *> would be passed as a literal argument to PowerShell and break parameter binding.
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\installer\windows\nova_bootstrap.ps1"" -InstallDir ""{app}"" -NonInteractive -NoLaunch -SkipShortcut"; StatusMsg: "Setting up Nova (Python, Ollama, model)..."; Flags: runhidden waituntilterminated

[UninstallRun]
; Stop Nova before uninstalling
Filename: "{app}\stop_nova.bat"; RunOnceId: "StopNova"; Flags: runhidden waituntilterminated

[UninstallDelete]
; Clean up the venv and caches that weren't in the original install
Type: filesandordirs; Name: "{app}\nova_backend\venv"
Type: filesandordirs; Name: "{app}\nova_backend\__pycache__"
Type: files; Name: "{app}\bootstrap.log"
Type: dirifempty; Name: "{app}"

[Code]
// After bootstrap runs, check if it succeeded. If not, show the user
// a helpful message with log location. Only offer to launch if venv exists.
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  VenvPython: String;
  LogFile: String;
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    VenvPython := ExpandConstant('{app}\nova_backend\venv\Scripts\python.exe');
    LogFile := ExpandConstant('{app}\bootstrap.log');
    if not FileExists(VenvPython) then
    begin
      MsgBox('Nova files were installed, but the setup script did not complete successfully.' + #13#10 +
             'The Python virtual environment was not created.' + #13#10#13#10 +
             'Check the log at:' + #13#10 + LogFile + #13#10#13#10 +
             'To retry manually, open PowerShell and run:' + #13#10 +
             'powershell -File "' + ExpandConstant('{app}') + '\installer\windows\nova_bootstrap.ps1"',
             mbError, MB_OK);
    end
    else if not FileExists(ExpandConstant('{app}\nova_backend\venv\Scripts\nova-start.exe')) then
    begin
      MsgBox('Nova was installed but nova-start was not found in the virtual environment.' + #13#10 +
             'pip install may have failed. Check:' + #13#10 + LogFile + #13#10#13#10 +
             'To retry: open PowerShell and run:' + #13#10 +
             'powershell -File "' + ExpandConstant('{app}') + '\installer\windows\nova_bootstrap.ps1"',
             mbInformation, MB_OK);
    end
    else
    begin
      // Bootstrap succeeded — offer to launch
      if MsgBox('Nova is ready! Would you like to launch it now?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        Exec(VenvPython, '"' + ExpandConstant('{app}\scripts\start_daemon.py') + '"',
             ExpandConstant('{app}'), SW_HIDE, ewNoWait, ResultCode);
      end;
    end;
  end;
end;
