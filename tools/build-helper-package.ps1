$ErrorActionPreference = "Stop"

$root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$packageName = "OCR_Helper_Setup.zip"
$packagePath = Join-Path $root $packageName
$stagingRoot = Join-Path $env:TEMP ("ocr-helper-package-" + [guid]::NewGuid().ToString("N"))
$stagingApp = Join-Path $stagingRoot "OCR_Helper"

$includeFiles = @(
    "index.html",
    "install_helper_protocol.cmd",
    "start_ocr_app.cmd",
    "start_ocr_app.ps1",
    "start_ocr_protocol.cmd",
    "start_local_parser.ps1",
    "pyproject.toml",
    "README.md"
)

$includeDirs = @(
    "src",
    "tools"
)

try {
    New-Item -ItemType Directory -Path $stagingApp -Force | Out-Null

    foreach ($file in $includeFiles) {
        $source = Join-Path $root $file
        if (Test-Path -LiteralPath $source) {
            Copy-Item -LiteralPath $source -Destination (Join-Path $stagingApp $file) -Force
        }
    }

    foreach ($dir in $includeDirs) {
        $source = Join-Path $root $dir
        if (Test-Path -LiteralPath $source) {
            Copy-Item -LiteralPath $source -Destination (Join-Path $stagingApp $dir) -Recurse -Force
        }
    }

    Get-ChildItem -LiteralPath $stagingApp -Recurse -Directory -Filter "__pycache__" |
        Remove-Item -Recurse -Force

    if (Test-Path -LiteralPath $packagePath) {
        Remove-Item -LiteralPath $packagePath -Force
    }

    Compress-Archive -Path (Join-Path $stagingRoot "OCR_Helper") -DestinationPath $packagePath -Force
    Write-Host "Built helper package: $packagePath"
} finally {
    if (Test-Path -LiteralPath $stagingRoot) {
        Remove-Item -LiteralPath $stagingRoot -Recurse -Force
    }
}
