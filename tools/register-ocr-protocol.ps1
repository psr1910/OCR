$ErrorActionPreference = "Stop"

$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$launcher = Join-Path $root "start_ocr_protocol.cmd"

if (-not (Test-Path -LiteralPath $launcher)) {
    throw "Launcher not found: $launcher"
}

$protocolRoot = "HKCU:\Software\Classes\ocr-parser"
$commandRoot = Join-Path $protocolRoot "shell\open\command"
$command = "`"$launcher`" `"%1`""

New-Item -Path $protocolRoot -Force | Out-Null
Set-Item -Path $protocolRoot -Value "URL:OCR Parser Protocol"
New-ItemProperty -Path $protocolRoot -Name "URL Protocol" -Value "" -PropertyType String -Force | Out-Null
New-Item -Path $commandRoot -Force | Out-Null
Set-Item -Path $commandRoot -Value $command

Write-Host "Registered ocr-parser:// launch protocol."
Write-Host "Command: $command"
