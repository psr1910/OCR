param(
    [switch]$RemoveBackup,
    [switch]$WaitForUnlock,
    [int]$RetrySeconds = 5,
    [int]$MaxWaitMinutes = 360
)

$ErrorActionPreference = "Stop"

$canonicalRoot = "C:\Users\user\Documents\My Works\OCR"
$legacyRoot = "C:\Users\user\Documents\OCR"
$excludePattern = "\\.git\\|\\downloads\\"
$logPath = Join-Path $canonicalRoot "downloads\workspace-cleanup.log"

function Write-CleanupLog {
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

if (-not (Test-Path -LiteralPath (Join-Path $canonicalRoot "index.html"))) {
    throw "Canonical workspace is missing index.html: $canonicalRoot"
}

if (-not (Test-Path -LiteralPath $legacyRoot)) {
    New-Item -ItemType Junction -Path $legacyRoot -Target $canonicalRoot | Out-Null
    Write-Host "Created junction: $legacyRoot -> $canonicalRoot"
    exit 0
}

$legacyItem = Get-Item -LiteralPath $legacyRoot -Force
if (($legacyItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    Write-Host "Legacy path is already a reparse point: $legacyRoot"
    exit 0
}

$legacyHashes = Get-ComparableFileHashes -Root $legacyRoot
$canonicalHashes = Get-ComparableFileHashes -Root $canonicalRoot
$diff = Compare-Object $legacyHashes $canonicalHashes -Property RelativePath, Hash

if ($diff) {
    $diff | Format-Table -AutoSize
    throw "Workspace files differ. Sync or review the differences before creating the junction."
}

function Convert-LegacyWorkspace {
    $stamp = Get-Date -Format "yyMMdd_HHmmss"
    $backupRoot = "C:\Users\user\Documents\OCR_duplicate_backup_$stamp"

    Rename-Item -LiteralPath $legacyRoot -NewName (Split-Path -Leaf $backupRoot)
    New-Item -ItemType Junction -Path $legacyRoot -Target $canonicalRoot | Out-Null
    Write-CleanupLog "Created junction: $legacyRoot -> $canonicalRoot"
    Write-CleanupLog "Backup retained: $backupRoot"

    if ($RemoveBackup) {
        $resolvedBackup = (Resolve-Path -LiteralPath $backupRoot).Path
        $documentsRoot = (Resolve-Path -LiteralPath "C:\Users\user\Documents").Path

        if (-not $resolvedBackup.StartsWith($documentsRoot)) {
            throw "Refusing to remove unexpected backup path: $resolvedBackup"
        }

        Remove-Item -LiteralPath $resolvedBackup -Recurse -Force
        Write-CleanupLog "Removed backup: $backupRoot"
    }
}

if (-not $WaitForUnlock) {
    Convert-LegacyWorkspace
    exit 0
}

$deadline = (Get-Date).AddMinutes($MaxWaitMinutes)
Write-CleanupLog "Waiting for legacy workspace unlock: $legacyRoot"

while ((Get-Date) -lt $deadline) {
    try {
        Convert-LegacyWorkspace
        exit 0
    } catch [System.IO.IOException] {
        Write-CleanupLog "Still locked. Retry in $RetrySeconds seconds."
        Start-Sleep -Seconds $RetrySeconds
    }
}

throw "Timed out waiting for legacy workspace unlock: $legacyRoot"
