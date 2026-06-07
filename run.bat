@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel%==0 (
    set PYTHON=python
    goto :setup
)

if exist ".python\python.exe" (
    set PYTHON=.python\python.exe
    set PATH=%CD%\.python;%CD%\.python\Scripts;%PATH%
    goto :run
)

echo Python not found. Install Python 3.12+ from https://www.python.org/downloads/
echo Check "Add Python to PATH" during installation.
exit /b 1

:setup
if not exist "venv" (
    echo Creating virtual environment...
    %PYTHON% -m venv venv
)
call venv\Scripts\activate.bat
set PYTHON=python

:run
echo Installing dependencies...
%PYTHON% -m pip install -r requirements.txt -q

echo Generating dataset...
%PYTHON% data\generate_dataset.py

echo Training ML models...
%PYTHON% ml\train_model.py

echo.
echo ========================================
echo  Server running at http://127.0.0.1:8000
echo  Press Ctrl+C to stop
echo ========================================
%PYTHON% -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
