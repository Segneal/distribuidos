@echo off
echo ========================================
echo   Setup Sistema ONG - Servicios gRPC
echo ========================================
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

echo ✅ Python detectado
echo.

REM Instalar dependencias de gRPC
echo 📦 Instalando dependencias de gRPC...
pip install grpcio grpcio-tools

if errorlevel 1 (
    echo ❌ Error instalando dependencias de gRPC
    pause
    exit /b 1
)

echo ✅ Dependencias de gRPC instaladas
echo.

REM Instalar dependencias de cada servicio
echo 📦 Instalando dependencias de servicios...

if exist "grpc\services\user-service\requirements.txt" (
    echo Instalando dependencias de user-service...
    pip install -r grpc\services\user-service\requirements.txt
)

if exist "grpc\services\inventory-service\requirements.txt" (
    echo Instalando dependencias de inventory-service...
    pip install -r grpc\services\inventory-service\requirements.txt
)

if exist "grpc\services\events-service\requirements.txt" (
    echo Instalando dependencias de events-service...
    pip install -r grpc\services\events-service\requirements.txt
)

echo ✅ Dependencias de servicios instaladas
echo.

REM Generar código proto
echo 🔧 Generando código Python desde archivos .proto...
call grpc\scripts\generate-proto.bat

echo.
echo ========================================
echo   ✅ Setup completado exitosamente!
echo ========================================
echo.
echo Próximos pasos:
echo 1. Configurar la base de datos MySQL
echo 2. Iniciar los servicios: grpc\scripts\start-services.bat
echo 3. Iniciar el API Gateway: cd api-gateway ^&^& npm start
echo.
pause