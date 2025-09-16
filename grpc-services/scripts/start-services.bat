@echo off
echo Iniciando servicios gRPC...

REM Verificar que los servicios existen
if not exist "grpc\services\user-service\src\main.py" (
    echo ❌ Error: grpc\services\user-service\src\main.py no encontrado
    pause
    exit /b 1
)

if not exist "grpc\services\inventory-service\src\main.py" (
    echo ❌ Error: grpc\services\inventory-service\src\main.py no encontrado
    pause
    exit /b 1
)

if not exist "grpc\services\events-service\src\main.py" (
    echo ❌ Error: grpc\services\events-service\src\main.py no encontrado
    pause
    exit /b 1
)

echo.
echo 🚀 Iniciando servicios en paralelo...
echo.
echo - User Service (Puerto 50051)
echo - Inventory Service (Puerto 50052)  
echo - Events Service (Puerto 50053)
echo.

REM Iniciar servicios en paralelo
start "User Service" cmd /k "cd grpc\services\user-service && python src\main.py"
start "Inventory Service" cmd /k "cd grpc\services\inventory-service && python src\main.py"
start "Events Service" cmd /k "cd grpc\services\events-service && python src\main.py"

echo ✅ Servicios iniciados!
echo.
echo Para detener los servicios, cierra las ventanas de comando que se abrieron.
echo.
pause