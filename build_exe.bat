@echo off
setlocal

cd /d "%~dp0"

echo Stopping running app instances if present...
taskkill /IM WitchFarmAutoClicker.exe /F >nul 2>&1

echo Installing dependencies...
py -m pip install --upgrade pip
py -m pip install -r requirements.txt -r requirements-dev.txt

echo Generating witch icon...
py generate_witch_icon.py

set "APP_NAME=WitchFarmAutoClicker"

echo Building executable...
py -m PyInstaller --noconfirm --onefile --windowed --clean --name %APP_NAME% --icon assets\witch.ico --add-data "assets;assets" autoclicker.py

if errorlevel 1 (
	echo Primary build failed. Retrying with timestamped executable name...
	for /f %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "TS=%%i"
	set "APP_NAME=WitchFarmAutoClicker_%TS%"
	py -m PyInstaller --noconfirm --onefile --windowed --clean --name %APP_NAME% --icon assets\witch.ico --add-data "assets;assets" autoclicker.py
	if errorlevel 1 (
		echo Build failed.
		pause
		exit /b 1
	)
)

echo.
echo Build complete.
echo EXE path: dist\%APP_NAME%.exe
pause
