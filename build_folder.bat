@echo off
cd /d "%~dp0"

if not defined SKIP_PIP (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

echo Fetching bundled ffmpeg ^(pinned LGPL build, SHA-256 checked^)...
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\fetch_ffmpeg.ps1"
if errorlevel 1 (
    echo ffmpeg download or checksum verification failed.
    if not defined NO_PAUSE pause
    exit /b 1
)

echo Building AudiobookForge...
echo Preferred mode: --onedir
if exist "dist\AudiobookForge" rmdir /s /q "dist\AudiobookForge"
python -m PyInstaller --clean --noconfirm AudiobookForge_onedir.spec
if errorlevel 1 (
    echo PyInstaller build failed.
    if not defined NO_PAUSE pause
    exit /b 1
)

echo Adding bundled ffmpeg and license notices...
mkdir "dist\AudiobookForge\ffmpeg"
copy /y "vendor\ffmpeg\ffmpeg.exe" "dist\AudiobookForge\ffmpeg\" >nul || exit /b 1
copy /y "vendor\ffmpeg\LICENSE.txt" "dist\AudiobookForge\ffmpeg\" >nul || exit /b 1
copy /y "vendor\ffmpeg\VERSION.txt" "dist\AudiobookForge\ffmpeg\" >nul || exit /b 1
copy /y "LICENSE" "dist\AudiobookForge\LICENSE.txt" >nul || exit /b 1
copy /y "THIRD_PARTY_NOTICES.md" "dist\AudiobookForge\" >nul || exit /b 1

echo.
echo Build finished. Output folder: dist\AudiobookForge
if not defined NO_PAUSE pause
exit /b 0
