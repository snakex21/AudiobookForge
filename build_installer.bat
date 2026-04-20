@echo off
cd /d "%~dp0"

set "NO_PAUSE=1"
call build_folder.bat
if errorlevel 1 exit /b 1

set "ISCC="
where iscc >nul 2>nul
if not errorlevel 1 set "ISCC=iscc"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not defined ISCC (
    echo Inno Setup compiler not found.
    echo Install Inno Setup 6 or add ISCC.exe to PATH.
    if not defined NO_PAUSE pause
    exit /b 1
)

"%ISCC%" "AudiobookForge.iss"
if errorlevel 1 exit /b 1

echo.
echo Installer finished. Output file: release\AudiobookForgeSetup.exe
if not defined NO_PAUSE pause
