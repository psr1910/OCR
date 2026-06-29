$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$downloads = Join-Path $root "downloads"
$appUrl = "http://127.0.0.1:8765/"
$serverUrl = "http://127.0.0.1:8765/health"
$outLog = Join-Path $downloads "local-parser.out.log"
$errLog = Join-Path $downloads "local-parser.err.log"
$runnerCmd = Join-Path $downloads "local-parser-runner.cmd"

if (-not (Test-Path -LiteralPath $downloads)) {
    New-Item -ItemType Directory -Path $downloads -Force | Out-Null
}

function Get-ProjectPython {
    $candidates = @(
        (Join-Path $root ".venv\Scripts\python.exe"),
        "C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    try {
        return (Get-Command python -ErrorAction Stop).Source
    } catch {
        throw "Python was not found. Create .venv or install Python first."
    }
}

function Test-LocalParser {
    $client = $null
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $async = $client.BeginConnect("127.0.0.1", 8765, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne(500)) {
            return $false
        }
        $client.EndConnect($async)
        return $true
    } catch {
        return $false
    } finally {
        if ($client -ne $null) {
            $client.Close()
        }
    }
}

if (-not (Test-LocalParser)) {
    $python = Get-ProjectPython
    if (Test-Path -LiteralPath $outLog) { Remove-Item -LiteralPath $outLog -Force }
    if (Test-Path -LiteralPath $errLog) { Remove-Item -LiteralPath $errLog -Force }

    $srcPath = ([string](Join-Path $root "src")).Trim()
    $pythonPath = ([string]$python).Trim()
    $outLogPath = ([string]$outLog).Trim()
    $errLogPath = ([string]$errLog).Trim()
    $runnerText = @"
@echo off
title OCR Local Parser Service
echo OCR Local Parser Service
echo.
echo Keep this window open while using the OCR parser.
echo App URL: http://127.0.0.1:8765/
echo Save folder: $downloads
echo.
set "PYTHONPATH=$srcPath"
"$pythonPath" -m ocr_parser.local_server --host 127.0.0.1 --port 8765
echo.
echo OCR Local Parser Service stopped.
pause
"@
    Set-Content -LiteralPath $runnerCmd -Value $runnerText -Encoding ASCII

    & $env:ComSpec /c start "OCR Local Parser Service" /D "$root" $env:ComSpec /k "`"$runnerCmd`""

    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt += 1) {
        Start-Sleep -Milliseconds 500
        if (Test-LocalParser) {
            $ready = $true
            break
        }
    }

    if (-not $ready) {
        throw "Local parser service did not start. Check $errLog"
    }
}

try {
    Start-Process -FilePath $appUrl
} catch {
    Write-Warning "Could not open the OCR app automatically. Open it manually: $appUrl"
}
Write-Host "OCR app is ready: $appUrl"
Write-Host "Local parser service: http://127.0.0.1:8765"
Write-Host "Codex package folder: $downloads"
