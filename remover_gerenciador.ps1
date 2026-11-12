# Central Robotica - remove o gerenciador automatico do Agendador de Tarefas do Windows.
$nome = "Central Robotica - Atualizar noticias"
Unregister-ScheduledTask -TaskName $nome -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Gerenciador removido: '$nome'."
