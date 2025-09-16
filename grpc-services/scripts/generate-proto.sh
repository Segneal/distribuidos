#!/bin/bash

echo "Generando código Python desde archivos .proto..."

# Crear directorios si no existen
mkdir -p grpc/services/user-service/src/grpc
mkdir -p grpc/services/inventory-service/src/grpc
mkdir -p grpc/services/events-service/src/grpc

# Generar código para user-service
echo "Generando user-service..."
python -m grpc_tools.protoc -I./grpc/proto --python_out=./grpc/services/user-service/src/grpc --grpc_python_out=./grpc/services/user-service/src/grpc grpc/proto/user.proto

# Generar código para inventory-service
echo "Generando inventory-service..."
python -m grpc_tools.protoc -I./grpc/proto --python_out=./grpc/services/inventory-service/src/grpc --grpc_python_out=./grpc/services/inventory-service/src/grpc grpc/proto/inventory.proto

# Generar código para events-service
echo "Generando events-service..."
python -m grpc_tools.protoc -I./grpc/proto --python_out=./grpc/services/events-service/src/grpc --grpc_python_out=./grpc/services/events-service/src/grpc grpc/proto/events.proto

# Crear archivos __init__.py si no existen
[ ! -f "grpc/services/user-service/src/grpc/__init__.py" ] && echo "# gRPC generated files for user service" > grpc/services/user-service/src/grpc/__init__.py
[ ! -f "grpc/services/inventory-service/src/grpc/__init__.py" ] && echo "# gRPC generated files for inventory service" > grpc/services/inventory-service/src/grpc/__init__.py
[ ! -f "grpc/services/events-service/src/grpc/__init__.py" ] && echo "# gRPC generated files for events service" > grpc/services/events-service/src/grpc/__init__.py

echo ""
echo "✅ Código Python generado exitosamente!"
echo ""
echo "Archivos generados:"
echo "- grpc/services/user-service/src/grpc/user_pb2.py"
echo "- grpc/services/user-service/src/grpc/user_pb2_grpc.py"
echo "- grpc/services/inventory-service/src/grpc/inventory_pb2.py"
echo "- grpc/services/inventory-service/src/grpc/inventory_pb2_grpc.py"
echo "- grpc/services/events-service/src/grpc/events_pb2.py"
echo "- grpc/services/events-service/src/grpc/events_pb2_grpc.py"