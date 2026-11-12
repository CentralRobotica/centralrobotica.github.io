# Central Robotica - instala o gerenciador automatico no Agendador de Tarefas do Windows.
# Roda a coleta de hora em hora, sem abrir janela. Se o PC estiver desligado no horario,
# a coleta roda assim que ele ligar. Para remover: remover_gerenciador.ps1
$ErrorActionPreference = "Stop"
$site = $PSScriptRoot
$script = Join-Path $site "coletor\gerenciador.py"

$pythonw = $null
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
    $candidato = Join-Path (Split-Path $py.Source) "pythonw.exe"
    if (Test-Path $candidato) { $pythonw = $candidato }
}
if (-not $pythonw) { throw "Nao encontrei o pythonw.exe. Instale o Python 3 (python.org) e tente de novo." }

$nome = "Central Robotica - Atualizar noticias"
$acao = New-ScheduledTaskAction -Execute $pythonw -Argument ('"' + $script + '"') -WorkingDirectory $site
$gatilho = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Hours 1)
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 50) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName $nome -Action $acao -Trigger $gatilho -Settings $ajustes `
    -Description "Coleta automatica das noticias de robotica do mundo para o site Central Robotica (de hora em hora)." -Force | Out-Null

Write-Host "Gerenciador instalado: '$nome' (de hora em hora)."
Write-Host "Logs: $site\logs"
