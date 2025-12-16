@echo off
echo Seeding Firefly Database...
echo.

cd /d "%~dp0"

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Set environment variables
set PYTHONPATH=%cd%

:: Run seed script
python seed_interventions.py

echo.
echo Database seeding complete!
pause
