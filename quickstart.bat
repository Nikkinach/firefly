@echo off
echo ============================================
echo    FIREFLY MENTAL HEALTH PLATFORM
echo    Phase 1 - Quick Start
echo ============================================
echo.

:: Check if PostgreSQL is running
echo [1/5] Checking PostgreSQL...
sc query postgresql-x64-15 | find "RUNNING" >nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: PostgreSQL is not running!
    echo Please start PostgreSQL service first.
    pause
    exit /b 1
)
echo PostgreSQL: RUNNING

:: Check if Redis/Memurai is running
echo [2/5] Checking Redis...
sc query Memurai | find "RUNNING" >nul
if %ERRORLEVEL% neq 0 (
    echo WARNING: Redis/Memurai is not running.
    echo Some features may not work.
)
echo Redis/Memurai: RUNNING

:: Seed database if needed
echo.
echo [3/5] Checking database...
cd backend
call venv\Scripts\activate.bat
python -c "from app.core.database import engine; engine.connect(); print('Database connection: OK')"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Cannot connect to database!
    echo Please check backend/.env DATABASE_URL setting.
    pause
    exit /b 1
)
cd ..

:: Start Backend
echo.
echo [4/5] Starting Backend API...
start "Firefly Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3 >nul

:: Start Frontend
echo.
echo [5/5] Starting Frontend...
start "Firefly Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 3 >nul

echo.
echo ============================================
echo    FIREFLY IS STARTING UP!
echo ============================================
echo.
echo Frontend:       http://localhost:5173
echo Backend API:    http://localhost:8000
echo API Docs:       http://localhost:8000/docs
echo.
echo To seed the intervention library:
echo   cd backend ^&^& seed_db.bat
echo.
echo Press any key to close this window...
pause >nul
