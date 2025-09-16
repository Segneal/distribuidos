@echo off
REM Sistema ONG Backend - Deployment Script (Windows)
REM This script automates the deployment of the complete system

setlocal enabledelayedexpansion

REM Configuration
set COMPOSE_FILE=docker-compose.yml
set ENV_FILE=.env

echo ==========================================
echo   🚀 Sistema ONG Backend - Deployment
echo ==========================================
echo.
echo 📋 Este script desplegará automáticamente:
echo    ✅ API Gateway (Node.js)
echo    ✅ User Service (Python gRPC)
echo    ✅ Events Service (Python gRPC) 
echo    ✅ Inventory Service (Python gRPC)
echo    ✅ MySQL Database
echo    ✅ Apache Kafka + Zookeeper
echo.

REM Check Docker
echo 🔍 Verificando prerrequisitos...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado.
    echo 💡 Descarga Docker Desktop desde: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no está instalado.
    echo 💡 Docker Compose viene incluido con Docker Desktop
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está corriendo.
    echo 💡 Inicia Docker Desktop y espera a que esté listo
    pause
    exit /b 1
)

echo ✅ Prerrequisitos verificados correctamente

REM Setup environment
echo [INFO] Setting up environment...
if not exist "%ENV_FILE%" (
    echo [WARNING] .env file not found. Creating from .env.example...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [WARNING] Please edit .env file with your configuration before running again.
        echo [WARNING] Especially change JWT_SECRET and database passwords!
        pause
        exit /b 1
    ) else (
        echo [ERROR] .env.example file not found. Cannot create environment file.
        exit /b 1
    )
)

echo [SUCCESS] Environment setup completed

REM Cleanup
echo [INFO] Cleaning up existing containers...
docker-compose -f %COMPOSE_FILE% down --remove-orphans >nul 2>&1

echo [SUCCESS] Cleanup completed

REM Build services
echo [INFO] Building services...
docker-compose -f %COMPOSE_FILE% build --no-cache
if errorlevel 1 (
    echo [ERROR] Failed to build services
    exit /b 1
)

echo [SUCCESS] Services built successfully

REM Start infrastructure
echo [INFO] Starting infrastructure services...
docker-compose -f %COMPOSE_FILE% up -d mysql zookeeper kafka
if errorlevel 1 (
    echo [ERROR] Failed to start infrastructure services
    exit /b 1
)

echo [INFO] Waiting for infrastructure services to be ready...
timeout /t 30 /nobreak >nul

REM Start microservices
echo [INFO] Starting microservices...
docker-compose -f %COMPOSE_FILE% up -d user-service inventory-service events-service
if errorlevel 1 (
    echo [ERROR] Failed to start microservices
    exit /b 1
)

echo [INFO] Waiting for microservices to be ready...
timeout /t 20 /nobreak >nul

REM Start API Gateway
echo [INFO] Starting API Gateway...
docker-compose -f %COMPOSE_FILE% up -d api-gateway
if errorlevel 1 (
    echo [ERROR] Failed to start API Gateway
    exit /b 1
)

echo [INFO] Waiting for API Gateway to be ready...
timeout /t 15 /nobreak >nul

echo.
echo 🎉 ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!
echo.

REM Show status
echo 📊 Estado de los servicios:
echo.
docker-compose -f %COMPOSE_FILE% ps
echo.
echo 🌐 URLs del sistema:
echo   ┌─ API Principal: http://localhost:3000
echo   ├─ Documentación: http://localhost:3000/api-docs  
echo   ├─ Health Check: http://localhost:3000/health
echo   ├─ MySQL: localhost:3308
echo   └─ Kafka: localhost:9092
echo.
echo 🔐 Credenciales por defecto:
echo   ┌─ Usuario: admin@ong.com
echo   └─ Contraseña: password123
echo.
echo 🛠️  Comandos útiles:
echo   ┌─ Ver logs: docker-compose logs [servicio]
echo   ├─ Reiniciar: docker-compose restart
echo   ├─ Detener: docker-compose stop
echo   └─ Verificar: python quick-start-check.py
echo.
echo 📚 Próximos pasos:
echo   1. Abre http://localhost:3000/api-docs en tu navegador
echo   2. Prueba el login con las credenciales por defecto
echo   3. Explora la documentación interactiva
echo   4. Ejecuta: python quick-start-check.py para verificar todo
echo.
echo 🚀 ¡Tu sistema está listo para usar!

pause