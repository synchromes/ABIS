@echo off
echo ================================================
echo   ABIS Interview Assistant - Backend Server
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python environment...
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

echo [2/3] Verifying AI packages...
venv\Scripts\python.exe -c "import faster_whisper, deepface, transformers, cv2; print('AI packages: OK')" 2>nul
if errorlevel 1 (
    echo WARNING: Some AI packages may not be installed correctly
    echo But continuing anyway...
)

echo [3/3] Starting FastAPI server...
echo.
echo Backend will run at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --log-level info

pause
