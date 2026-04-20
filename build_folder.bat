@echo off
cd /d "%~dp0"

echo Installing PyInstaller...
python -m pip install pyinstaller

echo Building AudiobookForge...
echo Preferred mode: --onedir
if exist "dist\AudiobookForge" rmdir /s /q "dist\AudiobookForge"
pyinstaller --clean AudiobookForge_onedir.spec

echo.
echo Build finished. Output folder: dist\AudiobookForge
if not defined NO_PAUSE pause
