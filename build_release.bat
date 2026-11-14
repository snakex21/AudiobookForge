@echo off
cd /d "%~dp0"

rem Full release: onedir build with bundled ffmpeg, installer, portable zip and SHA256SUMS.txt in release\
set "NO_PAUSE=1"
call "%~dp0build_installer.bat"
if errorlevel 1 exit /b 1

powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\package_release.ps1"
if errorlevel 1 exit /b 1

echo.
echo Release files are in release\
exit /b 0
