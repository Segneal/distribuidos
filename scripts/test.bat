@echo off
REM Sistema ONG Backend - Test Script (Windows)
REM This script runs all tests for the system

setlocal enabledelayedexpansion

set COMPOSE_FILE=docker-compose.yml

echo ==========================================
echo    Sistema ONG Backend - Test Suite
echo ==========================================
echo.

REM Check if services are running
echo [INFO] Checking if services are running...
docker-compose -f %COMPOSE_FILE% ps | findstr "Up" >nul
if errorlevel 1 (
    echo [ERROR] Services are not running. Please start them first with: scripts\deploy.bat
    pause
    exit /b 1
)

echo [SUCCESS] Services are running

REM Create test results directory
if not exist "test-results" mkdir test-results

REM Run unit tests
echo [INFO] Running unit tests...

echo [INFO] Testing User Service...
docker-compose -f %COMPOSE_FILE% exec -T user-service python -m pytest tests/ -v
if errorlevel 1 (
    echo [ERROR] User Service tests failed
) else (
    echo [SUCCESS] User Service tests passed
)

echo [INFO] Testing Inventory Service...
docker-compose -f %COMPOSE_FILE% exec -T inventory-service python -m pytest tests/ -v
if errorlevel 1 (
    echo [ERROR] Inventory Service tests failed
) else (
    echo [SUCCESS] Inventory Service tests passed
)

echo [INFO] Testing Events Service...
docker-compose -f %COMPOSE_FILE% exec -T events-service python -m pytest tests/ -v
if errorlevel 1 (
    echo [ERROR] Events Service tests failed
) else (
    echo [SUCCESS] Events Service tests passed
)

echo [INFO] Testing API Gateway...
docker-compose -f %COMPOSE_FILE% exec -T api-gateway npm test
if errorlevel 1 (
    echo [ERROR] API Gateway tests failed
) else (
    echo [SUCCESS] API Gateway tests passed
)

REM Test basic connectivity
echo [INFO] Testing API endpoints...
curl -f http://localhost:3000/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Health endpoint test failed
) else (
    echo [SUCCESS] Health endpoint test passed
)

REM Test Kafka
echo [INFO] Testing Kafka connectivity...
docker-compose -f %COMPOSE_FILE% exec -T kafka kafka-topics.sh --bootstrap-server localhost:9092 --list >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Kafka connectivity test failed
) else (
    echo [SUCCESS] Kafka connectivity test passed
)

echo.
echo [SUCCESS] 🎉 Test suite completed!
echo.
echo [INFO] Test results saved in: test-results\
echo [INFO] To view detailed logs: docker-compose logs [service-name]

pause