@echo off
cd /d "C:\Users\Admin\OneDrive\Documents\cAlgo"
call mamba env update -f Requirements.yml --prune
if %ERRORLEVEL% NEQ 0 (
    cmd /k
) else (
    timeout /t 60 >nul
)