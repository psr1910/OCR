param(
    [switch]$WaitForUnlock,
    [int]$RetrySeconds = 5,
    [int]$MaxWaitMinutes = 360
)

$ErrorActionPreference = "Stop"

$canonicalRoot = "C:\Users\user\Documents\My Works\OCR"
$legacyRoot = "C:\Users\user\Documents\OCR"
$excludePattern = "\\.git\\|\\downloads\\"
$logPath = Join-Path $canonicalRoot "downloads\workspace-delete.log"

function Write-DeleteLog {
    param([string]$Message)

    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Write-Host $line

    $logDir = Split-Path -Parent $logPath
    if (-not (Test-Path -LiteralPath $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
}

function Get-ComparableFileHashes {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    Get-ChildItem -LiteralPath $Root -Recurse -File -Force |
        Where-Object { $_.FullName -notmatch $excludePattern } |
        ForEach-Object {
            [pscustomobject]@{
                RelativePath = $_.FullName.Substring($Root.Length + 1)
                Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
            }
        } |
        Sort-Object RelativePath
}

function Test-ReadyForDelete {
    if (-not (Test-Path -LiteralPath (Join-Path $canonicalRoot "index.html"))) {
        throw "Canonical workspace is missing index.html: $canonicalRoot"
    }

    if (-not (Test-Path -LiteralPath $legacyRoot)) {
        Write-DeleteLog "Legacy workspace already removed: $legacyRoot"
        return $false
    }

    $legacyItem = Get-Item -LiteralPath $legacyRoot -Force
    if (($legacyItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Remove-Item -LiteralPath $legacyRoot -Force
        Write-DeleteLog "Removed legacy reparse point: $legacyRoot"
        return $false
    }

    $legacyHashes = Get-ComparableFileHashes -Root $legacyRoot
    $canonicalHashes = Get-ComparableFileHashes -Root $canonicalRoot
    $diff = Compare-Object $legacyHashes $canonicalHashes -Property RelativePath, Hash

    if ($diff) {
        $diff | Format-Table -AutoSize
        throw "Workspace files differ. Refusing to delete legacy workspace."
    }

    return $true
}

function Remove-LegacyWorkspace {
    if (-not (Test-ReadyForDelete)) {
        return $true
    }

    $resolvedLegacy = (Resolve-Path -LiteralPath $legacyRoot).Path
    $documentsRoot = (Resolve-Path -LiteralPath "C:\Users\user\Documents").Path

    if ($resolvedLegacy -ne $legacyRoot -or -not $resolvedLegacy.StartsWith($documentsRoot)) {
        throw "Refusing to remove unexpected path: $resolvedLegacy"
    }

    Remove-Item -LiteralPath $resolvedLegacy -Recurse -Force
    Write-DeleteLog "Removed legacy workspace: $resolvedLegacy"
    return $true
}

if (-not $WaitForUnlock) {
    Remove-LegacyWorkspace | Out-Null
    exit 0
}

$deadline = (Get-Date).AddMinutes($MaxWaitMinutes)
Write-DeleteLog "Waiting to remove legacy workspace: $legacyRoot"

while ((Get-Date) -lt $deadline) {
    try {
        if (Remove-LegacyWorkspace) {
            exit 0
        }
    } catch [System.IO.IOException] {
        Write-DeleteLog "Still locked. Retry in $RetrySeconds seconds."
        Start-Sleep -Seconds $RetrySeconds
    }
}

throw "Timed out waiting to remove legacy workspace: $legacyRoot"
