$ErrorActionPreference = "Stop"

$pythonCandidates = @(
    ".\.venv\Scripts\python.exe",
    "C:\Users\user\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    "python"
)

$python = $null
foreach ($candidate in $pythonCandidates) {
    try {
        if ($candidate -eq "python") {
            $command = Get-Command python -ErrorAction Stop
            $python = $command.Source
        } elseif (Test-Path -LiteralPath $candidate) {
            $python = (Resolve-Path -LiteralPath $candidate).Path
        }
    } catch {
        $python = $null
    }

    if ($python) {
        break
    }
}

if (-not $python) {
    throw "Python was not found. Create .venv or install Python first."
}

$env:PYTHONPATH = Join-Path (Resolve-Path .).Path "src"
& $python -m ocr_parser.local_server --host 127.0.0.1 --port 8765
