@echo off
setlocal

cd /d "%~dp0"

echo Stopping running app instances if present...
taskkill /IM WitchFarmAutoClicker.exe /F >nul 2>&1

echo Installing dependencies...
py -m pip install --upgrade pip
py -m pip install -r requirements.txt -r requirements-dev.txt
py -m pip install -e .

echo Generating witch icon...
py generate_witch_icon.py

echo Building portable executable...
py -m PyInstaller --noconfirm --onefile --windowed --clean --paths src --name WitchFarmAutoClicker_latest --icon assets\witch.ico --add-data "assets;assets" autoclicker.py
if errorlevel 1 (
  echo Failed to build portable executable.
  exit /b 1
)

set "ISCC=ISCC.exe"
where %ISCC% >nul 2>&1
if errorlevel 1 (
  set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)

if not exist "%ISCC%" (
  set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not exist "%ISCC%" (
  set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)

if not exist "%ISCC%" (
  echo Inno Setup compiler not found. Install Inno Setup 6 first.
  exit /b 1
)

echo Building setup wizard installer...
"%ISCC%" installers\WitchFarmAutoClicker.iss
if errorlevel 1 (
  echo Failed to build setup installer.
  exit /b 1
)

if not exist docs\downloads mkdir docs\downloads

copy /Y dist\WitchFarmAutoClicker_latest.exe docs\downloads\WitchFarmAutoClicker_latest.exe >nul
copy /Y dist\WitchFarmAutoClickerSetup_latest.exe docs\downloads\WitchFarmAutoClickerSetup_latest.exe >nul

for %%F in (WitchFarmAutoClicker_latest.exe WitchFarmAutoClickerSetup_latest.exe) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "(Get-FileHash -Algorithm SHA256 'docs/downloads/%%F').Hash.ToLower()" > "docs/downloads/%%F.sha256"
)

echo.
echo Release artifacts updated in docs\downloads:
echo - WitchFarmAutoClicker_latest.exe
echo - WitchFarmAutoClicker_latest.exe.sha256
echo - WitchFarmAutoClickerSetup_latest.exe
echo - WitchFarmAutoClickerSetup_latest.exe.sha256
