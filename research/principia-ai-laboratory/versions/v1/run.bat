@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
    py -3 main.py %*
    goto :end
)
where python >nul 2>&1
if not errorlevel 1 (
    python main.py %*
    goto :end
)
echo Python 3.10 or later was not found.
echo Install Python from python.org and enable the PATH option, then try again.
:end
if errorlevel 1 pause
endlocal
