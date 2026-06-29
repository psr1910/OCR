@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\register-ocr-protocol.ps1"
echo.
echo OCR helper launch protocol setup finished.
pause
