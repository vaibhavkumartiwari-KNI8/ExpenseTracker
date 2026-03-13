@echo off
echo Starting Smart Expense Tracker...
echo.

cd /d %~dp0

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Checking dependencies...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting application...
echo.
streamlit run expense_tracker.py

pause