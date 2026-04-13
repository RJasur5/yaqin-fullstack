@echo off
setlocal

:: Call the PowerShell script to handle everything (IP detection, backend, frontend)
powershell -ExecutionPolicy Bypass -File "%~dp0run_all.ps1"

endlocal
pause
