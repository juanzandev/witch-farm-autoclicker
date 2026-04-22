@echo off
setlocal

cd /d "%~dp0\.."

if not exist .venv\Scripts\python.exe (
  echo Missing virtual environment. Run scripts\install_source.bat first.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
python autoclicker.py
