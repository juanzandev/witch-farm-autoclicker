@echo off
setlocal

cd /d "%~dp0\.."

set "EXE="
for /f "delims=" %%f in ('dir /b /a:-d /o:-d "dist\WitchFarmAutoClicker*.exe" 2^>nul') do (
  if not defined EXE set "EXE=dist\%%f"
)

if not defined EXE (
  for /f "delims=" %%f in ('dir /b /a:-d /o:-d "WitchFarmAutoClicker*.exe" 2^>nul') do (
    if not defined EXE set "EXE=%%f"
  )
)

if not defined EXE (
  echo Could not find WitchFarmAutoClicker*.exe in dist\ or project root.
  echo Build first with: build_exe.bat
  pause
  exit /b 1
)

set "INSTALL_DIR=%LOCALAPPDATA%\Programs\WitchFarmAutoClicker"
set "START_MENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
set "SHORTCUT=%START_MENU_DIR%\Witch Farm Autoclicker.lnk"

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
copy /Y "%EXE%" "%INSTALL_DIR%\WitchFarmAutoClicker.exe" >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath='%INSTALL_DIR%\WitchFarmAutoClicker.exe'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.IconLocation='%INSTALL_DIR%\WitchFarmAutoClicker.exe,0'; $s.Save()"

if errorlevel 1 (
  echo Installed EXE, but could not create shortcut.
  echo Run directly from: %INSTALL_DIR%\WitchFarmAutoClicker.exe
  pause
  exit /b 1
)

echo Installed to: %INSTALL_DIR%
echo Start menu shortcut: Witch Farm Autoclicker
pause
