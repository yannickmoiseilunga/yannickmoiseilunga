@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (set "PY=py -3") else (set "PY=python")
%PY% --version || (echo Install Python 3.10 or newer & pause & exit /b 1)
if not exist ".venv\Scripts\python.exe" (%PY% -m venv .venv || (pause & exit /b 1))
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements-research.txt
if errorlevel 1 (echo Dependency installation failed. Check connection, disk space and Python version. & pause & exit /b 1)
echo Installation completed. Run run.bat to open the dashboard.
pause
endlocal
