# Packages dist\AudiobookForge as a portable zip and writes release\SHA256SUMS.txt
# for the installer and the zip. Run after build_installer.bat.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$versionLine = Get-Content "version.py" | Where-Object { $_ -match '__version__\s*=\s*"([^"]+)"' } | Select-Object -First 1
if (-not $versionLine) { throw "__version__ not found in version.py" }
$version = $Matches[1]

$dist = Join-Path $root "dist\AudiobookForge"
$release = Join-Path $root "release"
foreach ($required in @("AudiobookForge.exe", "ffmpeg\ffmpeg.exe", "ffmpeg\LICENSE.txt", "THIRD_PARTY_NOTICES.md")) {
    if (-not (Test-Path (Join-Path $dist $required))) { throw "Missing $required in $dist" }
}
$setup = Join-Path $release "AudiobookForgeSetup.exe"
if (-not (Test-Path $setup)) { throw "Missing $setup (run build_installer.bat first)" }

$zipName = "AudiobookForge-$version-win64-portable.zip"
$zip = Join-Path $release $zipName
if (Test-Path $zip) { Remove-Item -Force $zip }
Write-Host "Creating $zipName"
# Zip root folder is AudiobookForge\ so extracting gives AudiobookForge\AudiobookForge.exe
& tar.exe -a -c -f $zip -C (Join-Path $root "dist") "AudiobookForge"
if ($LASTEXITCODE -ne 0) { throw "tar failed with exit code $LASTEXITCODE" }

$lines = foreach ($file in @($setup, $zip)) {
    "{0}  {1}" -f (Get-FileHash -Algorithm SHA256 -LiteralPath $file).Hash.ToLowerInvariant(), (Split-Path -Leaf $file)
}
$sums = Join-Path $release "SHA256SUMS.txt"
[IO.File]::WriteAllText($sums, (($lines -join "`n") + "`n"), (New-Object Text.UTF8Encoding $false))
Get-Content $sums
