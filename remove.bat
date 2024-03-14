@echo off

:: Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please right-click and select "Run as administrator".
    pause
    exit
)

:: Stop and remove the service
echo Stopping and removing the service...
cd %~dp0
python main.py stop
python main.py remove
echo Service has been removed.

pause
