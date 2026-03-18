@echo off
REM RAG System v1.5 - Quick Start Automation Testing (Windows)
REM Run: run_tests.bat

setlocal enabledelayedexpansion

color 0A
cls

echo ===============================================
echo RAG System v1.5
echo Automated Testing Suite (Windows)
echo ===============================================
echo.

REM Configuration
set BACKEND_URL=http://localhost:8000
set PYTHON_CMD=python

echo Checking prerequisites...
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python found
    set PYTHON_CMD=python
) else (
    echo [ERROR] Python not found
    exit /b 1
)

REM Check Backend
echo Checking Backend...
powershell -Command "try {$result = Invoke-WebRequest -Uri %BACKEND_URL%/health -ErrorAction Stop; Write-Host '[OK] Backend running'} catch {Write-Host '[ERROR] Backend not running'; exit 1}"
if %errorlevel% equ 1 (
    echo.
    echo Start backend with:
    echo   python -m uvicorn src.api.main:app --reload
    echo.
    exit /b 1
)

echo.
echo Installing test dependencies...
pip install pytest requests locust --quiet
echo [OK] Dependencies installed
echo.

REM Run tests
echo Running automated tests...
echo.

python automated_tests.py

echo.
echo Test run complete!
echo Check test_reports/ for detailed reports
echo.
pause
