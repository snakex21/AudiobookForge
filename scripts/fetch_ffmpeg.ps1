# Downloads the pinned LGPL ffmpeg build and places ffmpeg.exe + its license in vendor\ffmpeg.
# The archive and the extracted exe are both checked against pinned SHA-256 values;
# any mismatch aborts the build. The binaries are never committed to git (vendor/ is ignored).
#
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File scripts\fetch_ffmpeg.ps1 [-Destination vendor\ffmpeg]

param(
    [string]$Destination = (Join-Path (Split-Path -Parent $PSScriptRoot) "vendor\ffmpeg")
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

# --- pinned build (keep in sync with THIRD_PARTY_NOTICES.md) ---
$FfmpegVersion = "n9.0.2-39-g7adfbe40dc-20261031"
$ArchiveName   = "ffmpeg-n9.0.2-39-g7adfbe40dc-win64-lgpl-9.0"
$ArchiveUrl    = "https://github.com/FFmpeg-Builds/FFmpeg-Builds/releases/download/autobuild-2026-10-31-12-59/$ArchiveName.zip"
$ArchiveSha256 = "9d37c564e0d01c18cde184a079fa6ef04d7d2783ada41da81d04165cc8f1a650"
$ExeSha256     = "d03c858a130cae1382902925d9f46eb15d7de42e025d34cc29b7ddca6cfb4c62"

function Get-Sha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

$exeTarget = Join-Path $Destination "ffmpeg.exe"
$licenseTarget = Join-Path $Destination "LICENSE.txt"
if ((Test-Path $exeTarget) -and (Test-Path $licenseTarget) -and ((Get-Sha256 $exeTarget) -eq $ExeSha256)) {
    Write-Host "ffmpeg $FfmpegVersion already present in $Destination (SHA-256 OK)"
    exit 0
}

$work = Join-Path ([IO.Path]::GetTempPath()) ("abf-ffmpeg-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $work | Out-Null
try {
    $zip = Join-Path $work "$ArchiveName.zip"
    Write-Host "Downloading $ArchiveUrl"
    Invoke-WebRequest -Uri $ArchiveUrl -OutFile $zip -UseBasicParsing

    $actual = Get-Sha256 $zip
    if ($actual -ne $ArchiveSha256) {
        throw "ffmpeg archive SHA-256 mismatch: expected $ArchiveSha256, got $actual"
    }
    Write-Host "Archive SHA-256 OK: $actual"

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::OpenRead($zip)
    try {
        $staging = Join-Path $work "out"
        New-Item -ItemType Directory -Path $staging | Out-Null
        foreach ($pair in @(@("bin/ffmpeg.exe", "ffmpeg.exe"), @("LICENSE.txt", "LICENSE.txt"))) {
            $entry = $archive.GetEntry("$ArchiveName/" + $pair[0])
            if ($null -eq $entry) { throw "Entry $($pair[0]) not found in archive" }
            [IO.Compression.ZipFileExtensions]::ExtractToFile($entry, (Join-Path $staging $pair[1]), $true)
        }
    } finally {
        $archive.Dispose()
    }

    $exeHash = Get-Sha256 (Join-Path $staging "ffmpeg.exe")
    if ($exeHash -ne $ExeSha256) {
        throw "ffmpeg.exe SHA-256 mismatch: expected $ExeSha256, got $exeHash"
    }

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    Copy-Item -Force (Join-Path $staging "ffmpeg.exe") $exeTarget
    Copy-Item -Force (Join-Path $staging "LICENSE.txt") $licenseTarget
    Set-Content -Encoding ASCII -Path (Join-Path $Destination "VERSION.txt") -Value @(
        "ffmpeg $FfmpegVersion (LGPL v3 build, no GPL or nonfree components)",
        "Source archive: $ArchiveUrl",
        "Archive SHA-256: $ArchiveSha256",
        "ffmpeg.exe SHA-256: $ExeSha256",
        "FFmpeg source: https://github.com/FFmpeg/FFmpeg/tree/7adfbe40dc (release/9.0 branch)",
        "Build scripts: https://github.com/FFmpeg-Builds/FFmpeg-Builds (formerly BtbN/FFmpeg-Builds)"
    )
    Write-Host "ffmpeg $FfmpegVersion -> $Destination (ffmpeg.exe SHA-256 OK)"
} finally {
    Remove-Item -Recurse -Force -LiteralPath $work -ErrorAction SilentlyContinue
}
