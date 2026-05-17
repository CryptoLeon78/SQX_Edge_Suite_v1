[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [string]$CloudflaredPath = "C:\Tools\cloudflared\cloudflared.exe",
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
$form.Size = New-Object System.Drawing.Size(560, 360)
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
$subtitle.Text = "Control remoto Backend/Tunnel para el portatil operador"
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

$overall = New-Object System.Windows.Forms.Label
$overall.Text = "Estado: iniciando comprobacion..."
$overall.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$overall.ForeColor = [System.Drawing.Color]::FromArgb(255, 218, 77)
$overall.Location = New-Object System.Drawing.Point(30, 244)
$overall.Size = New-Object System.Drawing.Size(500, 24)
$form.Controls.Add($overall)

$startButton = New-Object System.Windows.Forms.Button
$startButton.Text = "Arrancar"
$startButton.Location = New-Object System.Drawing.Point(28, 280)
$startButton.Size = New-Object System.Drawing.Size(110, 32)
$form.Controls.Add($startButton)

$stopButton = New-Object System.Windows.Forms.Button
$stopButton.Text = "Detener"
$stopButton.Location = New-Object System.Drawing.Point(150, 280)
$stopButton.Size = New-Object System.Drawing.Size(110, 32)
$form.Controls.Add($stopButton)

$refreshButton = New-Object System.Windows.Forms.Button
$refreshButton.Text = "Refrescar"
$refreshButton.Location = New-Object System.Drawing.Point(272, 280)
$refreshButton.Size = New-Object System.Drawing.Size(110, 32)
$form.Controls.Add($refreshButton)

$closeButton = New-Object System.Windows.Forms.Button
$closeButton.Text = "Cerrar monitor"
$closeButton.Location = New-Object System.Drawing.Point(394, 280)
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
        [bool]$Busy
    )
    $anyRunning = $BackendOk -or $TunnelOk
    $allOk = $BackendOk -and $TunnelOk

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
    Set-PanelState -Label $backendLabel -Panel $backendPanel -Ok $backend.ok -Text $backend.text
    Set-PanelState -Label $tunnelLabel -Panel $tunnelPanel -Ok $tunnel.ok -Text $tunnel.text
    Set-ButtonsForState -BackendOk $backend.ok -TunnelOk $tunnel.ok -Busy $script:isBusy

    if ($backend.ok -and $tunnel.ok) {
        $overall.Text = "Estado: OK todo en marcha. Puedes abrir el enlace protegido."
        $overall.ForeColor = [System.Drawing.Color]::FromArgb(159, 255, 202)
        if (-not $script:lastOk) {
            $notify.ShowBalloonTip(2500, "SQX Edge Suite", "Backend y Tunnel estan OK.", [System.Windows.Forms.ToolTipIcon]::Info)
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
    Set-ButtonsForState -BackendOk $false -TunnelOk $false -Busy $true
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
    Invoke-RemoteOperation -Message "Estado: arrancando backend y tunel..." -Operation {
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
        $overall.Text = "Estado: arrancando backend y tunel..."
        Start-HiddenPowerShell -ScriptPath $startScript -ExtraArgs @("-CloudflaredPath", "`"$CloudflaredPath`"")
    } elseif ($StopOnOpen) {
        $overall.Text = "Estado: deteniendo servicios..."
        Start-HiddenPowerShell -ScriptPath $stopScript
    }
    Update-Status
    $timer.Start()
})

[void]$form.ShowDialog()
