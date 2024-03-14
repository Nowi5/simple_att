@echo off

:: Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please right-click and select "Run as administrator".
    pause
    exit
)

:: Check for Python installation
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 goto installpython
echo Python is already installed.
goto installpackages

:installpython
echo Python is not installed. Installing Python...
:: Download Python installer (change URL to your preferred version)
curl -o python_installer.exe https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe
:: Run installer - adjust the install parameters as needed
start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
del python_installer.exe
echo Python installed successfully.

:installpackages
echo Installing required Python packages...
python -m pip install psutil pywin32
echo Package installation complete.

:installservice
cd %~dp0
echo Installing the service using main.py...
python main.py install

if %ERRORLEVEL% neq 0 (
    echo Failed to install the service. Please check the error message above.
)

pause