@echo off
echo Starting Firefly Backend API...
echo.

cd /d "%~dp0"

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Set environment variables
set PYTHONPATH=%cd%

:: Install any missing dependencies
echo Checking dependencies...
pip install -r requirements.txt -q

:: Run the server
echo.
echo Starting FastAPI server on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
