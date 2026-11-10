Set-StrictMode -Version Latest

$script:NovaAcquisitionPolicyVersion = "installer-acquisition-admission-v2"
$script:NovaCanonicalWingetSource = [ordered]@{
    Name = "winget"
    Arg = "https://cdn.winget.microsoft.com/cache"
    Identifier = "Microsoft.Winget.Source_8wekyb3d8bbwe"
    Type = "Microsoft.PreIndexed.Package"
    TrustLevel = @("StoreOrigin", "Trusted")
}
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
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
    } finally {
        $stream.Dispose()
        $sha.Dispose()
    }
}

function Resolve-NovaAcquisitionExecutable {
    param([Parameter(Mandatory = $true)][string]$ExecutablePath)

    $resolved = (Resolve-Path -LiteralPath $ExecutablePath -ErrorAction Stop).Path
    if (-not [System.IO.File]::Exists($resolved)) {
        throw "The exact acquisition executable was not found."
    }

    # WinGet is commonly exposed through a zero-length App Execution Alias.
    # That alias can be launched but cannot be opened for hashing. Resolve only
    # this exact alias to the Store-signed DesktopAppInstaller package binary;
    # all other executables retain their literal resolved path.
    $localAppData = [Environment]::GetFolderPath([Environment+SpecialFolder]::LocalApplicationData)
    $expectedAlias = Join-Path $localAppData "Microsoft\WindowsApps\winget.exe"
    if (-not [string]::Equals($resolved, $expectedAlias, [StringComparison]::OrdinalIgnoreCase)) {
        return $resolved
    }
    $alias = Get-Item -LiteralPath $resolved -Force -ErrorAction Stop
    if ($alias.Length -ne 0 -or -not ($alias.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        throw "The WinGet app execution alias has an unexpected form."
    }

    $packages = @(Get-AppxPackage -Name "Microsoft.DesktopAppInstaller" -ErrorAction Stop |
        Where-Object {
            -not $_.IsFramework -and
            -not $_.IsResourcePackage -and
            [string]$_.PackageFamilyName -ceq "Microsoft.DesktopAppInstaller_8wekyb3d8bbwe" -and
            [string]$_.PublisherId -ceq "8wekyb3d8bbwe" -and
            [string]$_.SignatureKind -ceq "Store" -and
            [string]$_.Status -ceq "Ok"
        } |
        Sort-Object Version -Descending)
    if ($packages.Count -lt 1) {
        throw "A trusted DesktopAppInstaller package could not be established."
    }
    $packageRoot = (Resolve-Path -LiteralPath $packages[0].InstallLocation -ErrorAction Stop).Path
    $candidate = (Resolve-Path -LiteralPath (Join-Path $packageRoot "winget.exe") -ErrorAction Stop).Path
    $requiredPrefix = $packageRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $candidate.StartsWith($requiredPrefix, [StringComparison]::OrdinalIgnoreCase) -or
        -not [System.IO.File]::Exists($candidate)) {
        throw "The trusted WinGet package executable could not be established."
    }
    return $candidate
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

function Get-NovaWingetSourceIdentity {
    param([Parameter(Mandatory = $true)][string]$ExecutablePath)

    $executable = Resolve-NovaAcquisitionExecutable -ExecutablePath $ExecutablePath

    $savedErrorActionPreference = $ErrorActionPreference
    try {
        # Windows PowerShell 5.1 can surface native stderr as an error record.
        # Source export is a local configuration read; evaluate its exit code
        # and parse only stdout.
        $ErrorActionPreference = "Continue"
        $output = & $executable source export winget --disable-interactivity 2>$null
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $savedErrorActionPreference
    }
    if ($exitCode -ne 0) {
        throw "The effective WinGet source identity could not be read."
    }

    try {
        $source = (($output | Out-String).Trim() | ConvertFrom-Json -ErrorAction Stop)
    } catch {
        throw "The effective WinGet source identity was malformed."
    }
    return [ordered]@{
        Name = [string]$source.Name
        Arg = [string]$source.Arg
        Identifier = [string]$source.Identifier
        Type = [string]$source.Type
        TrustLevel = @($source.TrustLevel | ForEach-Object { [string]$_ })
    }
}

function Assert-NovaCanonicalWingetSourceIdentity {
    param(
        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$Identity
    )

    foreach ($field in @("Name", "Arg", "Identifier", "Type")) {
        if ([string]$Identity[$field] -cne [string]$script:NovaCanonicalWingetSource[$field]) {
            throw "The effective WinGet source identity is not canonical."
        }
    }
    $actualTrust = @($Identity["TrustLevel"] | ForEach-Object { [string]$_ } | Sort-Object)
    $expectedTrust = @($script:NovaCanonicalWingetSource.TrustLevel | Sort-Object)
    if ($actualTrust.Count -ne $expectedTrust.Count -or
        (Compare-Object -ReferenceObject $expectedTrust -DifferenceObject $actualTrust)) {
        throw "The effective WinGet source trust level is not canonical."
    }

    $identityInput = @(
        [string]$Identity["Name"],
        [string]$Identity["Arg"],
        [string]$Identity["Identifier"],
        [string]$Identity["Type"]
    ) + $actualTrust
    return Get-NovaSha256Text -Value ($identityInput -join "`0")
}

function New-NovaAcquisitionPlan {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("winget_python", "winget_ollama", "pip_upgrade", "pip_install_nova")]
        [string]$Operation,
        [Parameter(Mandatory = $true)][string]$ExecutablePath,
        [Parameter(Mandatory = $true)][string]$InstallDir,
        [Parameter(Mandatory = $true)][string]$CorrelationId,
        [Parameter(Mandatory = $true)][bool]$ExplicitConsent,
        [System.Collections.IDictionary]$WingetSourceIdentity
    )
    if (-not $ExplicitConsent) { throw "Online acquisition requires explicit authorization." }
    if ([string]::IsNullOrWhiteSpace($CorrelationId) -or $CorrelationId.Length -gt 160) {
        throw "A bounded acquisition correlation ID is required."
    }
    $executable = Resolve-NovaAcquisitionExecutable -ExecutablePath $ExecutablePath
    $resolvedInstallDir = (Resolve-Path -LiteralPath $InstallDir -ErrorAction Stop).Path
    $sourceIdentityFingerprint = $null

    switch ($Operation) {
        "winget_python" {
            if ($null -eq $WingetSourceIdentity) {
                throw "WinGet acquisition requires a verified source identity."
            }
            $sourceIdentityFingerprint = Assert-NovaCanonicalWingetSourceIdentity -Identity $WingetSourceIdentity
            $arguments = @("install", "--exact", "--id", "Python.Python.3.12", "--source", "winget", "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity")
            $sourcePolicy = "winget-canonical:Python.Python.3.12"
        }
        "winget_ollama" {
            if ($null -eq $WingetSourceIdentity) {
                throw "WinGet acquisition requires a verified source identity."
            }
            $sourceIdentityFingerprint = Assert-NovaCanonicalWingetSourceIdentity -Identity $WingetSourceIdentity
            $arguments = @("install", "--exact", "--id", "Ollama.Ollama", "--source", "winget", "--accept-source-agreements", "--accept-package-agreements", "--disable-interactivity")
            $sourcePolicy = "winget-canonical:Ollama.Ollama"
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

    $fingerprintInput = @($executable, $Operation, $sourcePolicy, $sourceIdentityFingerprint) + $arguments
    return [ordered]@{
        operation = $Operation
        executable = $executable
        executable_fingerprint = Get-NovaFileSha256 -Path $executable
        arguments = $arguments
        source_policy = $sourcePolicy
        source_identity_fingerprint = $sourceIdentityFingerprint
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
    $admissionExecutable = Resolve-NovaAcquisitionExecutable -ExecutablePath $ExecutablePath
    $wingetSourceIdentity = $null
    if ($Operation -in @("winget_python", "winget_ollama")) {
        if (-not $ExplicitConsent) { throw "Online acquisition requires explicit authorization." }
        if ([string]::IsNullOrWhiteSpace($CorrelationId) -or $CorrelationId.Length -gt 160) {
            throw "A bounded acquisition correlation ID is required."
        }
        $verificationExecutable = $admissionExecutable
        $verificationExecutableFingerprint = Get-NovaFileSha256 -Path $verificationExecutable
        $verificationRecord = @{
            record_kind = "installer_source_identity_verification_admission"
            policy_version = $script:NovaAcquisitionPolicyVersion
            operation = $Operation
            verification_operation = "winget_source_export"
            executable_fingerprint = $verificationExecutableFingerprint
            correlation_id = Get-NovaSha256Text -Value $CorrelationId
            explicit_consent = $true
            evidence_locality = "installer_selected_unverified"
            recorded_at_utc = [DateTime]::UtcNow.ToString("o")
        }
        Write-NovaAcquisitionEvidence -Record $verificationRecord -EvidencePath $EvidencePath
        try {
            $wingetSourceIdentity = Get-NovaWingetSourceIdentity -ExecutablePath $verificationExecutable
        } catch {
            $denialRecord = @{
                record_kind = "installer_acquisition_denial"
                policy_version = $script:NovaAcquisitionPolicyVersion
                operation = $Operation
                reason = "source_identity_unverifiable"
                executable_fingerprint = $verificationExecutableFingerprint
                correlation_id = Get-NovaSha256Text -Value $CorrelationId
                process_started = $false
                recorded_at_utc = [DateTime]::UtcNow.ToString("o")
            }
            Write-NovaAcquisitionEvidence -Record $denialRecord -EvidencePath $EvidencePath
            throw
        }
    }
    try {
        $plan = New-NovaAcquisitionPlan -Operation $Operation -ExecutablePath $admissionExecutable -InstallDir $InstallDir -CorrelationId $CorrelationId -ExplicitConsent $ExplicitConsent -WingetSourceIdentity $wingetSourceIdentity
    } catch {
        if ($Operation -in @("winget_python", "winget_ollama")) {
            $denialRecord = @{
                record_kind = "installer_acquisition_denial"
                policy_version = $script:NovaAcquisitionPolicyVersion
                operation = $Operation
                reason = "source_identity_mismatch"
                executable_fingerprint = $verificationExecutableFingerprint
                correlation_id = Get-NovaSha256Text -Value $CorrelationId
                process_started = $false
                recorded_at_utc = [DateTime]::UtcNow.ToString("o")
            }
            Write-NovaAcquisitionEvidence -Record $denialRecord -EvidencePath $EvidencePath
        }
        throw
    }
    $admissionRecord = @{
        record_kind = "installer_acquisition_admission"
        policy_version = $script:NovaAcquisitionPolicyVersion
        operation = $plan.operation
        source_policy = $plan.source_policy
        source_identity_fingerprint = $plan.source_identity_fingerprint
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

        if ($Operation -in @("winget_python", "winget_ollama")) {
            $finalSourceIdentity = Get-NovaWingetSourceIdentity -ExecutablePath $admissionExecutable
            $finalSourceFingerprint = Assert-NovaCanonicalWingetSourceIdentity -Identity $finalSourceIdentity
            if ($finalSourceFingerprint -cne $plan.source_identity_fingerprint) {
                throw "The effective WinGet source identity changed before delegation."
            }
        }

        $executable = [string]$plan.executable
        $arguments = [string[]]$plan.arguments
        $processStarted = $true
        # Windows PowerShell 5.1 converts redirected native stderr into a
        # NativeCommandError. Temporarily keep that record non-terminating,
        # consume both streams through the host, and preserve the real exit.
        $savedErrorActionPreference = $ErrorActionPreference
        try {
            $ErrorActionPreference = "Continue"
            & $executable @arguments 2>&1 | Out-Host
            $exitCode = $LASTEXITCODE
        } finally {
            $ErrorActionPreference = $savedErrorActionPreference
        }
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
