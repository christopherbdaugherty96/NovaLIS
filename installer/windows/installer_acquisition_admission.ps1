Set-StrictMode -Version Latest

$script:NovaAcquisitionPolicyVersion = "installer-acquisition-admission-v1"
$script:NovaForbiddenChildEnvironment = @(
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
    "PIP_INDEX_URL", "PIP_EXTRA_INDEX_URL", "PIP_TRUSTED_HOST",
    "PIP_CERT", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "NETRC"
)

function Get-NovaSha256Text {
    param([Parameter(Mandatory = $true)][string]$Value)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function Get-NovaFileSha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Write-NovaAcquisitionEvidence {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Record,
        [Parameter(Mandatory = $true)][string]$EvidencePath
    )
    $parent = Split-Path -Parent $EvidencePath
    if (-not $parent) { throw "Acquisition evidence requires a parent directory." }
    [System.IO.Directory]::CreateDirectory($parent) | Out-Null
    $json = ($Record | ConvertTo-Json -Compress -Depth 5) + [Environment]::NewLine
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $stream = [System.IO.FileStream]::new(
        $EvidencePath,
        [System.IO.FileMode]::Append,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::Read
    )
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    } finally {
        $stream.Dispose()
    }
}

function New-NovaAcquisitionPlan {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("winget_python", "winget_ollama", "pip_upgrade", "pip_install_nova")]
        [string]$Operation,
        [Parameter(Mandatory = $true)][string]$ExecutablePath,
        [Parameter(Mandatory = $true)][string]$InstallDir,
        [Parameter(Mandatory = $true)][string]$CorrelationId,
        [Parameter(Mandatory = $true)][bool]$ExplicitConsent
    )
    if (-not $ExplicitConsent) { throw "Online acquisition requires explicit authorization." }
    if ([string]::IsNullOrWhiteSpace($CorrelationId) -or $CorrelationId.Length -gt 160) {
        throw "A bounded acquisition correlation ID is required."
    }
    $executable = (Resolve-Path -LiteralPath $ExecutablePath -ErrorAction Stop).Path
    if (-not [System.IO.File]::Exists($executable)) {
        throw "The exact acquisition executable was not found."
    }
    $resolvedInstallDir = (Resolve-Path -LiteralPath $InstallDir -ErrorAction Stop).Path

    switch ($Operation) {
        "winget_python" {
            $arguments = @("install", "--exact", "--id", "Python.Python.3.12", "--source", "winget", "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity")
            $sourcePolicy = "winget:Python.Python.3.12"
        }
        "winget_ollama" {
            $arguments = @("install", "--exact", "--id", "Ollama.Ollama", "--source", "winget", "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity")
            $sourcePolicy = "winget:Ollama.Ollama"
        }
        "pip_upgrade" {
            $arguments = @("-I", "-m", "pip", "--isolated", "install", "--index-url", "https://pypi.org/simple", "--disable-pip-version-check", "--no-input", "--no-cache-dir", "--upgrade", "pip", "--quiet")
            $sourcePolicy = "pypi:https://pypi.org/simple"
        }
        "pip_install_nova" {
            $arguments = @("-I", "-m", "pip", "--isolated", "install", "--index-url", "https://pypi.org/simple", "--disable-pip-version-check", "--no-input", "--no-cache-dir", "-e", $resolvedInstallDir, "--quiet")
            $sourcePolicy = "pypi:https://pypi.org/simple"
        }
    }

    $fingerprintInput = @($executable, $Operation, $sourcePolicy) + $arguments
    return [ordered]@{
        operation = $Operation
        executable = $executable
        executable_fingerprint = Get-NovaFileSha256 -Path $executable
        arguments = $arguments
        source_policy = $sourcePolicy
        command_fingerprint = Get-NovaSha256Text -Value ($fingerprintInput -join "`0")
        correlation_id = $CorrelationId
    }
}

function Invoke-NovaInstallerAcquisition {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("winget_python", "winget_ollama", "pip_upgrade", "pip_install_nova")]
        [string]$Operation,
        [Parameter(Mandatory = $true)][string]$ExecutablePath,
        [Parameter(Mandatory = $true)][string]$InstallDir,
        [Parameter(Mandatory = $true)][string]$EvidencePath,
        [Parameter(Mandatory = $true)][string]$CorrelationId,
        [Parameter(Mandatory = $true)][bool]$ExplicitConsent
    )
    $plan = New-NovaAcquisitionPlan -Operation $Operation -ExecutablePath $ExecutablePath -InstallDir $InstallDir -CorrelationId $CorrelationId -ExplicitConsent $ExplicitConsent
    $admissionRecord = @{
        record_kind = "installer_acquisition_admission"
        policy_version = $script:NovaAcquisitionPolicyVersion
        operation = $plan.operation
        source_policy = $plan.source_policy
        command_fingerprint = $plan.command_fingerprint
        executable_fingerprint = $plan.executable_fingerprint
        correlation_id = Get-NovaSha256Text -Value $plan.correlation_id
        explicit_consent = $true
        evidence_locality = "installer_selected_unverified"
        recorded_at_utc = [DateTime]::UtcNow.ToString("o")
    }
    Write-NovaAcquisitionEvidence -Record $admissionRecord -EvidencePath $EvidencePath

    $savedEnvironment = @{}
    foreach ($entry in [Environment]::GetEnvironmentVariables("Process").GetEnumerator()) {
        $savedEnvironment[[string]$entry.Key] = [string]$entry.Value
    }
    $processStarted = $false
    try {
        foreach ($key in @($savedEnvironment.Keys)) {
            [Environment]::SetEnvironmentVariable($key, $null, "Process")
        }
        foreach ($key in @("SystemRoot", "WINDIR", "ComSpec", "TEMP", "TMP", "LOCALAPPDATA", "USERPROFILE", "ProgramFiles", "ProgramFiles(x86)", "ProgramData")) {
            if ($savedEnvironment.ContainsKey($key) -and -not [string]::IsNullOrWhiteSpace($savedEnvironment[$key])) {
                [Environment]::SetEnvironmentVariable($key, $savedEnvironment[$key], "Process")
            }
        }
        # NUL is pip's documented Windows null-device value. Unlike an empty
        # file, it disables global/site config files as well as user config.
        [Environment]::SetEnvironmentVariable("PIP_CONFIG_FILE", "NUL", "Process")
        foreach ($forbidden in $script:NovaForbiddenChildEnvironment) {
            if ($forbidden -ne "PIP_CONFIG_FILE") {
                [Environment]::SetEnvironmentVariable($forbidden, $null, "Process")
            }
        }

        $executable = [string]$plan.executable
        $arguments = [string[]]$plan.arguments
        $processStarted = $true
        # Consume native output through the host stream so this function's
        # success stream contains only the numeric exit code returned below.
        & $executable @arguments 2>&1 | Out-Host
        $exitCode = $LASTEXITCODE
        $outcomeRecord = @{
            record_kind = "delegated_process_outcome"
            policy_version = $script:NovaAcquisitionPolicyVersion
            operation = $plan.operation
            command_fingerprint = $plan.command_fingerprint
            executable_fingerprint = $plan.executable_fingerprint
            correlation_id = Get-NovaSha256Text -Value $plan.correlation_id
            process_started = $true
            exit_code = $exitCode
            installation_verified = $false
            recorded_at_utc = [DateTime]::UtcNow.ToString("o")
        }
        Write-NovaAcquisitionEvidence -Record $outcomeRecord -EvidencePath $EvidencePath
        return $exitCode
    } catch {
        $outcomeRecord = @{
            record_kind = "delegated_process_outcome"
            policy_version = $script:NovaAcquisitionPolicyVersion
            operation = $plan.operation
            command_fingerprint = $plan.command_fingerprint
            executable_fingerprint = $plan.executable_fingerprint
            correlation_id = Get-NovaSha256Text -Value $plan.correlation_id
            process_started = $processStarted
            exit_code = $null
            installation_verified = $false
            outcome = "process_error"
            recorded_at_utc = [DateTime]::UtcNow.ToString("o")
        }
        Write-NovaAcquisitionEvidence -Record $outcomeRecord -EvidencePath $EvidencePath
        throw
    } finally {
        foreach ($key in @([Environment]::GetEnvironmentVariables("Process").Keys)) {
            [Environment]::SetEnvironmentVariable([string]$key, $null, "Process")
        }
        foreach ($key in $savedEnvironment.Keys) {
            [Environment]::SetEnvironmentVariable($key, $savedEnvironment[$key], "Process")
        }
    }
}
