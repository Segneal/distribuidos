@echo off
echo Generando codigo Python desde archivos .proto...

REM Crear directorios si no existen
if not exist "grpc\services\user-service\src\grpc" mkdir grpc\services\user-service\src\grpc
if not exist "grpc\services\inventory-service\src\grpc" mkdir grpc\services\inventory-service\src\grpc
if not exist "grpc\services\events-service\src\grpc" mkdir grpc\services\events-service\src\grpc

REM Generar codigo para user-service
echo Generando user-service...
python -m grpc_tools.protoc -I./grpc/proto --python_out=./grpc/services/user-service/src/grpc --grpc_python_out=./grpc/services/user-service/src/grpc grpc/proto/user.proto

REM Generar codigo para inventory-service
echo Generando inventory-service...
python -m grpc_tools.protoc -I./grpc/proto --python_out=./grpc/services/inventory-service/src/grpc --grpc_python_out=./grpc/services/inventory-service/src/grpc grpc/proto/inventory.proto

REM Generar codigo para events-service
echo Generando events-service...
python -m grpc_tools.protoc -I./grpc/proto --python_out=./grpc/services/events-service/src/grpc --grpc_python_out=./grpc/services/events-service/src/grpc grpc/proto/events.proto

REM Crear archivos __init__.py si no existen
if not exist "grpc\services\user-service\src\grpc\__init__.py" echo # gRPC generated files for user service > grpc\services\user-service\src\grpc\__init__.py
if not exist "grpc\services\inventory-service\src\grpc\__init__.py" echo # gRPC generated files for inventory service > grpc\services\inventory-service\src\grpc\__init__.py
if not exist "grpc\services\events-service\src\grpc\__init__.py" echo # gRPC generated files for events service > grpc\services\events-service\src\grpc\__init__.py

echo.
echo ✅ Codigo Python generado exitosamente!
echo.
echo Archivos generados:
echo - grpc/services/user-service/src/grpc/user_pb2.py
echo - grpc/services/user-service/src/grpc/user_pb2_grpc.py
echo - grpc/services/inventory-service/src/grpc/inventory_pb2.py
echo - grpc/services/inventory-service/src/grpc/inventory_pb2_grpc.py
echo - grpc/services/events-service/src/grpc/events_pb2.py
echo - grpc/services/events-service/src/grpc/events_pb2_grpc.py
pause