@echo off
cd /d "%~dp0"

echo Installing PyInstaller...
python -m pip install pyinstaller

echo Building AudiobookForge...
echo Preferred mode: --onedir
pyinstaller --onedir --windowed --name AudiobookForge app.py

echo.
echo Build finished. Output folder: dist\AudiobookForge
pause
