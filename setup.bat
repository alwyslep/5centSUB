@echo off
rem Recreate the project-local virtualenv. Location-independent: run it after
rem moving or copying this folder anywhere. Uses only the standard library
rem (python -m venv). The package itself needs no install step: conftest.py
rem and 5centsub.py run the source tree directly.
rem
rem Usage: setup.bat

setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo [setup] ERROR: no 'python' on PATH. Install Python 3.12+ first.
  exit /b 1
)

for /f "tokens=1" %%v in ('python -c "import sys; print(sys.version_info[0]*100+sys.version_info[1])"') do set PYVER=%%v
if %PYVER% LSS 312 (
  echo [setup] ERROR: Python 3.12+ required, found %PYVER%.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [setup] creating .venv ...
  python -m venv .venv
  if errorlevel 1 (
    echo [setup] ERROR: venv creation failed.
    exit /b 1
  )
) else (
  echo [setup] .venv already present.
)

echo [setup] installing pytest into .venv ^(needs network once^) ...
.venv\Scripts\python.exe -m pip install -q pytest
if errorlevel 1 (
  echo [setup] WARNING: pytest install failed. CLI still runs ^(stdlib only^):
  echo [setup]   .venv\Scripts\python.exe 5centsub.py demo
  exit /b 0
)

echo [setup] verifying ...
.venv\Scripts\python.exe -m pytest -q
if errorlevel 1 (
  echo [setup] ERROR: tests failed.
  exit /b 1
)

echo [setup] OK. Run: .venv\Scripts\python.exe 5centsub.py demo
