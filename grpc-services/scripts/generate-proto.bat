@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..
set PROTO_DIR=%ROOT_DIR%\proto
set USER_OUT=%ROOT_DIR%\services\user-service\src
set INVENTORY_OUT=%ROOT_DIR%\services\inventory-service\src
set EVENTS_OUT=%ROOT_DIR%\services\events-service\src

if not exist "%USER_OUT%" mkdir "%USER_OUT%"
if not exist "%INVENTORY_OUT%" mkdir "%INVENTORY_OUT%"
if not exist "%EVENTS_OUT%" mkdir "%EVENTS_OUT%"

echo Generating gRPC stubs...
python -m grpc_tools.protoc -I"%PROTO_DIR%" --python_out="%USER_OUT%" --grpc_python_out="%USER_OUT%" "%PROTO_DIR%\user.proto"
python -m grpc_tools.protoc -I"%PROTO_DIR%" --python_out="%INVENTORY_OUT%" --grpc_python_out="%INVENTORY_OUT%" "%PROTO_DIR%\inventory.proto"
python -m grpc_tools.protoc -I"%PROTO_DIR%" --python_out="%EVENTS_OUT%" --grpc_python_out="%EVENTS_OUT%" "%PROTO_DIR%\events.proto"

echo.
echo gRPC Python stubs generated successfully.
