@echo off
REM Sistema ONG Backend - Stop Script (Windows)
REM This script stops all services gracefully

setlocal enabledelayedexpansion

set COMPOSE_FILE=docker-compose.yml

echo ==========================================
echo    Sistema ONG Backend - Stop Services
echo ==========================================
echo.

echo [INFO] Stopping all services...
docker-compose -f %COMPOSE_FILE% down
if errorlevel 1 (
    echo [ERROR] Failed to stop services
    exit /b 1
)

if "%1"=="clean" (
    echo [INFO] Cleaning up resources...
    docker-compose -f %COMPOSE_FILE% down --remove-orphans
    docker network prune -f >nul 2>&1
    echo [SUCCESS] Resources cleaned up
)

echo.
echo [SUCCESS] 🛑 Services stopped successfully!
echo.

echo [INFO] Current status:
docker-compose -f %COMPOSE_FILE% ps

echo.
echo [INFO] To start services again, run: scripts\deploy.bat

pause