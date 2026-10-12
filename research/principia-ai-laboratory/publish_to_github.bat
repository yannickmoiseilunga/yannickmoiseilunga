@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Principia AI Laboratory - GitHub Publisher

echo ==============================================================
echo    PRINCIPIA AI LAB - PUBLIC GITHUB PUBLISHER (WINDOWS)
echo ==============================================================
echo.
echo This uses Windows PowerShell, NOT WSL or Bash.
echo The window will stay open so you can see errors.
echo.

if not exist "%~dp0publish_to_github.ps1" (
  echo ERROR: publish_to_github.ps1 was not found beside this file.
  echo Extract the entire ZIP before running this launcher.
  goto failed
)

"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0publish_to_github.ps1"
set "RESULT=%ERRORLEVEL%"
echo.
if "%RESULT%"=="0" (
  echo SUCCESS - see the GitHub URL displayed above.
) else (
  echo ERROR - publishing did not complete. Exit code: %RESULT%
  echo Review the message above and the local publication log.
)
echo.
pause
exit /b %RESULT%

:failed
echo.
pause
exit /b 1
