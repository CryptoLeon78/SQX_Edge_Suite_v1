[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$CloudflaredPath = $env:CLOUDFLARED_EXE,
    [switch]$StartOnOpen,
    [switch]$StopOnOpen
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$healthUrl = "http://127.0.0.1:5050/api/health"
$startScript = Join-Path $repo "tools\remote_operator_start.ps1"
$stopScript = Join-Path $repo "tools\remote_operator_stop.ps1"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Get-BackendStatus {
    try {
        $payload = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2
        return [ordered]@{
            ok = [bool]$payload.ok
            text = if ($payload.ok) { "OK - backend activo en 127.0.0.1:5050" } else { "NO-GO - backend responde sin OK" }
        }
    } catch {
        return [ordered]@{
            ok = $false
            text = "NO-GO - backend no responde"
        }
    }
}

function Get-TunnelStatus {
    $proc = Get-CimInstance Win32_Process -Filter "Name = 'cloudflared.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine -like "*cloudflared-config.local.yml*" } |
        Select-Object -First 1

    return [ordered]@{
        ok = [bool]$proc
        processId = if ($proc) { [int]$proc.ProcessId } else { $null }
        text = if ($proc) { "OK - tunel Cloudflare activo (PID $($proc.ProcessId))" } else { "NO-GO - tunel no detectado" }
    }
}

function Get-OllamaStatus {
    try {
        $payload = Invoke-RestMethod -Uri "http://127.0.0.1:5050/api/agent/status" -TimeoutSec 8
        $provider = $payload.provider
        $model = if ($provider -and $provider.model) { [string]$provider.model } elseif ($provider -and $provider.configuredModel) { [string]$provider.configuredModel } else { "modelo local" }
        return [ordered]@{
            ok = [bool]$payload.active
            model = $model
            text = if ([bool]$payload.active) { "OK - Ollama activo ($model)" } else { "NO-GO - Ollama no disponible ($model)" }
        }
    } catch {
        return [ordered]@{
            ok = $false
            model = $null
            text = "NO-GO - backend requerido para comprobar Ollama"
        }
    }
}

function Get-SQXCompatStatus {
    try {
        $payload = Invoke-RestMethod -Uri "http://127.0.0.1:5050/api/sqx142/compat/status" -TimeoutSec 4
        $java = $payload.java
        $active = if ($java -and $java.active -and $java.active.label) { [string]$java.active.label } else { "runtime desconocido" }
        $procCount = if ($payload.processes -and $null -ne $payload.processes.count) { [int]$payload.processes.count } else { 0 }
        $state = if ($payload.status) { [string]$payload.status } else { "unknown" }
        return [ordered]@{
            ok = [bool]$payload.ok
            status = $state
            text = if ([bool]$payload.ok) { "OK - SQX 142 runtime alineado ($active)" } else { "WARN - SQX 142 $state - procesos: $procCount" }
        }
    } catch {
        return [ordered]@{
            ok = $false
            status = "pending"
            text = "Pendiente - backend requerido para comprobar SQX 142"
        }
    }
}

function Get-SQXPerformanceStatus {
    try {
        $payload = Invoke-RestMethod -Uri "http://127.0.0.1:5050/api/sqx142/performance/status" -TimeoutSec 6
        $profile = if ($payload.activeProfile -and $payload.activeProfile.id) { [string]$payload.activeProfile.id } else { "unknown" }
        $disk = if ($payload.resources -and $payload.resources.disk) { $payload.resources.disk } else { $null }
        $diskText = if ($disk -and $disk.freeHuman) { "$($disk.freeHuman) libre" } else { "disco desconocido" }
        $intelligence = if ($payload.intelligence) { $payload.intelligence } else { $null }
        $views = if ($intelligence -and $intelligence.views) { $intelligence.views } else { $null }
        $latest = if ($intelligence -and $intelligence.latestEvidence) { $intelligence.latestEvidence } elseif ($payload.latestEvidence) { $payload.latestEvidence } else { $null }
        $recommendation = if ($intelligence -and $intelligence.recommendation) { $intelligence.recommendation } else { $null }
        $liveGuard = if ($intelligence -and $intelligence.liveGuard) { $intelligence.liveGuard } else { $null }
        $viewsText = if ($views -and $null -ne $views.presentCount -and $null -ne $views.expectedCount) { "views $($views.presentCount)/$($views.expectedCount)" } else { "views ?" }
        $latestEvidence = if ($latest -and $latest.filename) { [string]$latest.filename } else { "sin evidencia" }
        $next = if ($recommendation -and $recommendation.label) { [string]$recommendation.label } else { "sin recomendacion" }
        $guardText = if ($liveGuard -and $liveGuard.state) { "guard $($liveGuard.state)/alerts:$($liveGuard.alertCount)" } else { "guard ?" }
        $state = if ($payload.status) { [string]$payload.status } else { "unknown" }
        return [ordered]@{
            ok = [bool]$payload.ok
            status = $state
            profile = $profile
            liveGuard = $guardText
            recommendation = $next
            text = if ([bool]$payload.ok) { "OK - Performance $profile - $diskText`n$viewsText - $guardText - evidencia: $latestEvidence`nNext: $next" } else { "WARN - Performance $state - $profile - $diskText`n$viewsText - $guardText - evidencia: $latestEvidence`nNext: $next" }
        }
    } catch {
        return [ordered]@{
            ok = $false
            status = "pending"
            profile = "unknown"
            liveGuard = "guard ?"
            recommendation = "backend requerido"
            text = "Pendiente - backend requerido para comprobar rendimiento SQX 142"
        }
    }
}

function Start-HiddenPowerShell {
    param(
        [string]$ScriptPath,
        [string[]]$ExtraArgs = @()
    )
    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$ScriptPath`"",
        "-RepoRoot", "`"$repo`""
    ) + $ExtraArgs
    Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -WorkingDirectory $repo -WindowStyle Hidden | Out-Null
}

function Set-PanelState {
    param(
        [System.Windows.Forms.Label]$Label,
        [System.Windows.Forms.Panel]$Panel,
        [bool]$Ok,
        [string]$Text
    )
    $Label.Text = $Text
    if ($Ok) {
        $Panel.BackColor = [System.Drawing.Color]::FromArgb(17, 69, 49)
        $Label.ForeColor = [System.Drawing.Color]::FromArgb(159, 255, 202)
    } else {
        $Panel.BackColor = [System.Drawing.Color]::FromArgb(79, 35, 38)
        $Label.ForeColor = [System.Drawing.Color]::FromArgb(255, 183, 183)
    }
}

$form = New-Object System.Windows.Forms.Form
$form.Text = "SQX Edge Suite - Remote Status"
$form.Size = New-Object System.Drawing.Size(640, 660)
$form.StartPosition = "CenterScreen"
$form.TopMost = $true
$form.BackColor = [System.Drawing.Color]::FromArgb(9, 16, 30)
$form.ForeColor = [System.Drawing.Color]::White
$form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
$form.MaximizeBox = $false

$title = New-Object System.Windows.Forms.Label
$title.Text = "SQX Edge Suite"
$title.Font = New-Object System.Drawing.Font("Segoe UI", 22, [System.Drawing.FontStyle]::Bold)
$title.ForeColor = [System.Drawing.Color]::FromArgb(238, 245, 255)
$title.Location = New-Object System.Drawing.Point(24, 20)
$title.Size = New-Object System.Drawing.Size(500, 44)
$form.Controls.Add($title)

$subtitle = New-Object System.Windows.Forms.Label
$subtitle.Text = "Control local Backend/Tunnel/Ollama para el portatil operador"
$subtitle.Font = New-Object System.Drawing.Font("Segoe UI", 10)
$subtitle.ForeColor = [System.Drawing.Color]::FromArgb(180, 195, 215)
$subtitle.Location = New-Object System.Drawing.Point(27, 66)
$subtitle.Size = New-Object System.Drawing.Size(500, 24)
$form.Controls.Add($subtitle)

$backendPanel = New-Object System.Windows.Forms.Panel
$backendPanel.Location = New-Object System.Drawing.Point(28, 108)
$backendPanel.Size = New-Object System.Drawing.Size(500, 56)
$backendPanel.BackColor = [System.Drawing.Color]::FromArgb(30, 42, 64)
$form.Controls.Add($backendPanel)

$backendLabel = New-Object System.Windows.Forms.Label
$backendLabel.Text = "Comprobando backend..."
$backendLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$backendLabel.Location = New-Object System.Drawing.Point(14, 17)
$backendLabel.Size = New-Object System.Drawing.Size(470, 24)
$backendPanel.Controls.Add($backendLabel)

$tunnelPanel = New-Object System.Windows.Forms.Panel
$tunnelPanel.Location = New-Object System.Drawing.Point(28, 176)
$tunnelPanel.Size = New-Object System.Drawing.Size(500, 56)
$tunnelPanel.BackColor = [System.Drawing.Color]::FromArgb(30, 42, 64)
$form.Controls.Add($tunnelPanel)

$tunnelLabel = New-Object System.Windows.Forms.Label
$tunnelLabel.Text = "Comprobando tunel..."
$tunnelLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$tunnelLabel.Location = New-Object System.Drawing.Point(14, 17)
$tunnelLabel.Size = New-Object System.Drawing.Size(470, 24)
$tunnelPanel.Controls.Add($tunnelLabel)

$ollamaPanel = New-Object System.Windows.Forms.Panel
$ollamaPanel.Location = New-Object System.Drawing.Point(28, 244)
$ollamaPanel.Size = New-Object System.Drawing.Size(500, 56)
$ollamaPanel.BackColor = [System.Drawing.Color]::FromArgb(30, 42, 64)
$form.Controls.Add($ollamaPanel)

$ollamaLabel = New-Object System.Windows.Forms.Label
$ollamaLabel.Text = "Comprobando Ollama..."
$ollamaLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$ollamaLabel.Location = New-Object System.Drawing.Point(14, 17)
$ollamaLabel.Size = New-Object System.Drawing.Size(470, 24)
$ollamaPanel.Controls.Add($ollamaLabel)

$sqxPanel = New-Object System.Windows.Forms.Panel
$sqxPanel.Location = New-Object System.Drawing.Point(28, 312)
$sqxPanel.Size = New-Object System.Drawing.Size(500, 56)
$sqxPanel.BackColor = [System.Drawing.Color]::FromArgb(30, 42, 64)
$form.Controls.Add($sqxPanel)

$sqxLabel = New-Object System.Windows.Forms.Label
$sqxLabel.Text = "Comprobando SQX 142..."
$sqxLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$sqxLabel.Location = New-Object System.Drawing.Point(14, 17)
$sqxLabel.Size = New-Object System.Drawing.Size(470, 24)
$sqxPanel.Controls.Add($sqxLabel)

$perfPanel = New-Object System.Windows.Forms.Panel
$perfPanel.Location = New-Object System.Drawing.Point(28, 380)
$perfPanel.Size = New-Object System.Drawing.Size(580, 92)
$perfPanel.BackColor = [System.Drawing.Color]::FromArgb(30, 42, 64)
$form.Controls.Add($perfPanel)

$perfLabel = New-Object System.Windows.Forms.Label
$perfLabel.Text = "Comprobando rendimiento SQX 142..."
$perfLabel.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$perfLabel.Location = New-Object System.Drawing.Point(14, 17)
$perfLabel.Size = New-Object System.Drawing.Size(550, 64)
$perfPanel.Controls.Add($perfLabel)

$overall = New-Object System.Windows.Forms.Label
$overall.Text = "Estado: iniciando comprobacion..."
$overall.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$overall.ForeColor = [System.Drawing.Color]::FromArgb(255, 218, 77)
$overall.Location = New-Object System.Drawing.Point(30, 488)
$overall.Size = New-Object System.Drawing.Size(580, 40)
$form.Controls.Add($overall)

$startButton = New-Object System.Windows.Forms.Button
$startButton.Text = "Arrancar"
$startButton.Location = New-Object System.Drawing.Point(28, 548)
$startButton.Size = New-Object System.Drawing.Size(110, 32)
$form.Controls.Add($startButton)

$stopButton = New-Object System.Windows.Forms.Button
$stopButton.Text = "Detener"
$stopButton.Location = New-Object System.Drawing.Point(150, 548)
$stopButton.Size = New-Object System.Drawing.Size(110, 32)
$form.Controls.Add($stopButton)

$refreshButton = New-Object System.Windows.Forms.Button
$refreshButton.Text = "Refrescar"
$refreshButton.Location = New-Object System.Drawing.Point(272, 548)
$refreshButton.Size = New-Object System.Drawing.Size(110, 32)
$form.Controls.Add($refreshButton)

$closeButton = New-Object System.Windows.Forms.Button
$closeButton.Text = "Cerrar monitor"
$closeButton.Location = New-Object System.Drawing.Point(394, 548)
$closeButton.Size = New-Object System.Drawing.Size(134, 32)
$form.Controls.Add($closeButton)

$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.Visible = $true
$notify.Text = "SQX Edge Suite Remote"
$script:lastOk = $false
$script:isBusy = $false

function Set-ButtonsForState {
    param(
        [bool]$BackendOk,
        [bool]$TunnelOk,
        [bool]$OllamaOk,
        [bool]$Busy
    )
    $anyRunning = $BackendOk -or $TunnelOk
    $allOk = $BackendOk -and $TunnelOk -and $OllamaOk

    $startButton.Enabled = -not $Busy -and -not $allOk
    $stopButton.Enabled = -not $Busy -and $anyRunning
    $refreshButton.Enabled = -not $Busy
    $closeButton.Enabled = -not $Busy

    if ($Busy) {
        $startButton.Text = "Espere..."
        $stopButton.Text = "Espere..."
    } else {
        $startButton.Text = if ($allOk) { "En marcha" } else { "Arrancar" }
        $stopButton.Text = if ($anyRunning) { "Detener" } else { "Detenido" }
    }
}

function Update-Status {
    $backend = Get-BackendStatus
    $tunnel = Get-TunnelStatus
    $ollama = if ($backend.ok) { Get-OllamaStatus } else { [ordered]@{ ok = $false; text = "Pendiente - backend requerido para comprobar Ollama" } }
    $sqxCompat = if ($backend.ok) { Get-SQXCompatStatus } else { [ordered]@{ ok = $false; status = "pending"; text = "Pendiente - backend requerido para comprobar SQX 142" } }
    $sqxPerf = if ($backend.ok) { Get-SQXPerformanceStatus } else { [ordered]@{ ok = $false; status = "pending"; profile = "unknown"; text = "Pendiente - backend requerido para comprobar rendimiento SQX 142" } }
    Set-PanelState -Label $backendLabel -Panel $backendPanel -Ok $backend.ok -Text $backend.text
    Set-PanelState -Label $tunnelLabel -Panel $tunnelPanel -Ok $tunnel.ok -Text $tunnel.text
    Set-PanelState -Label $ollamaLabel -Panel $ollamaPanel -Ok $ollama.ok -Text $ollama.text
    Set-PanelState -Label $sqxLabel -Panel $sqxPanel -Ok $sqxCompat.ok -Text $sqxCompat.text
    Set-PanelState -Label $perfLabel -Panel $perfPanel -Ok $sqxPerf.ok -Text $sqxPerf.text
    Set-ButtonsForState -BackendOk $backend.ok -TunnelOk $tunnel.ok -OllamaOk $ollama.ok -Busy $script:isBusy

    if ($backend.ok -and $tunnel.ok -and $ollama.ok) {
        $overall.Text = "Estado: OK todo en marcha. SQX 142: $($sqxCompat.status). Perf: $($sqxPerf.profile)/$($sqxPerf.status) - $($sqxPerf.recommendation)."
        $overall.ForeColor = [System.Drawing.Color]::FromArgb(159, 255, 202)
        if (-not $script:lastOk) {
            $notify.ShowBalloonTip(2500, "SQX Edge Suite", "Backend, Tunnel y Ollama estan OK.", [System.Windows.Forms.ToolTipIcon]::Info)
        }
        $script:lastOk = $true
    } else {
        $overall.Text = "Estado: pendiente. Usa Arrancar o revisa los logs locales."
        $overall.ForeColor = [System.Drawing.Color]::FromArgb(255, 218, 77)
        $script:lastOk = $false
    }
}

function Invoke-RemoteOperation {
    param(
        [string]$Message,
        [scriptblock]$Operation
    )
    if ($script:isBusy) { return }
    $script:isBusy = $true
    Set-ButtonsForState -BackendOk $false -TunnelOk $false -OllamaOk $false -Busy $true
    $overall.Text = $Message
    $overall.ForeColor = [System.Drawing.Color]::FromArgb(255, 218, 77)
    & $Operation
    Start-Sleep -Milliseconds 900
    $script:isBusy = $false
    Update-Status
}

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 5000
$timer.Add_Tick({ Update-Status })

$startButton.Add_Click({
    Invoke-RemoteOperation -Message "Estado: arrancando backend, tunel y Ollama..." -Operation {
        Start-HiddenPowerShell -ScriptPath $startScript -ExtraArgs @("-CloudflaredPath", "`"$CloudflaredPath`"")
    }
})

$stopButton.Add_Click({
    Invoke-RemoteOperation -Message "Estado: deteniendo servicios..." -Operation {
        Start-HiddenPowerShell -ScriptPath $stopScript
    }
})

$refreshButton.Add_Click({ Update-Status })
$closeButton.Add_Click({ $form.Close() })

$form.Add_FormClosed({
    $timer.Stop()
    $notify.Visible = $false
    $notify.Dispose()
})

$form.Add_Shown({
    if ($StartOnOpen) {
        $overall.Text = "Estado: arrancando backend, tunel y Ollama..."
        Start-HiddenPowerShell -ScriptPath $startScript -ExtraArgs @("-CloudflaredPath", "`"$CloudflaredPath`"")
    } elseif ($StopOnOpen) {
        $overall.Text = "Estado: deteniendo servicios..."
        Start-HiddenPowerShell -ScriptPath $stopScript
    }
    Update-Status
    $timer.Start()
})

[void]$form.ShowDialog()
