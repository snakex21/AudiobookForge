@echo off
cd /d "%~dp0"

echo Installing PyInstaller...
python -m pip install pyinstaller

echo Building AudiobookForge...
echo Preferred mode: --onefile
if exist "dist\AudiobookForge" rmdir /s /q "dist\AudiobookForge"
if exist "dist\AudiobookForge.exe" del /q "dist\AudiobookForge.exe"
pyinstaller --clean AudiobookForge.spec

echo.
echo Build finished. Output file: dist\AudiobookForge.exe
if not defined NO_PAUSE pause
