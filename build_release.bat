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

echo Publishing release artifacts to docs\downloads...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Stop';" ^
  "$pairs = @(" ^
  "  @{ Source = 'dist\WitchFarmAutoClicker_latest.exe'; Target = 'docs\downloads\WitchFarmAutoClicker_latest.exe' }," ^
  "  @{ Source = 'dist\WitchFarmAutoClickerSetup_latest.exe'; Target = 'docs\downloads\WitchFarmAutoClickerSetup_latest.exe' }" ^
  ");" ^
  "foreach ($pair in $pairs) {" ^
  "  if (-not (Test-Path $pair.Source)) { throw \"Missing built artifact: $($pair.Source)\" }" ^
  "  $targetDir = Split-Path -Parent $pair.Target;" ^
  "  if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir | Out-Null }" ^
  "  $tmp = \"$($pair.Target).new\";" ^
  "  $published = $false;" ^
  "  for ($i = 1; $i -le 8; $i++) {" ^
  "    try {" ^
  "      Copy-Item -LiteralPath $pair.Source -Destination $tmp -Force;" ^
  "      Move-Item -LiteralPath $tmp -Destination $pair.Target -Force;" ^
  "      $published = $true;" ^
  "      break;" ^
  "    } catch {" ^
  "      if (Test-Path $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }" ^
  "      Start-Sleep -Milliseconds (250 * $i);" ^
  "    }" ^
  "  }" ^
  "  if (-not $published) { throw \"Unable to publish artifact after retries: $($pair.Target). Close any app/process using this file and rerun build_release.bat.\" }" ^
  "  $srcHash = (Get-FileHash -Algorithm SHA256 $pair.Source).Hash.ToLower();" ^
  "  $dstHash = (Get-FileHash -Algorithm SHA256 $pair.Target).Hash.ToLower();" ^
  "  if ($srcHash -ne $dstHash) { throw \"Hash mismatch after publish: $($pair.Target)\" }" ^
  "  Set-Content -Path ($pair.Target + '.sha256') -Value $dstHash -NoNewline;" ^
  "}"
if errorlevel 1 (
  echo Failed to publish verified release artifacts.
  exit /b 1
)

echo.
echo Release artifacts updated in docs\downloads:
echo - WitchFarmAutoClicker_latest.exe
echo - WitchFarmAutoClicker_latest.exe.sha256
echo - WitchFarmAutoClickerSetup_latest.exe
echo - WitchFarmAutoClickerSetup_latest.exe.sha256
