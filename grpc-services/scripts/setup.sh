#!/bin/bash

echo "========================================"
echo "   Setup Sistema ONG - Servicios gRPC"
echo "========================================"
echo ""

# Verificar que Python está instalado
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python no está instalado o no está en el PATH"
    exit 1
fi

echo "✅ Python detectado"
echo ""

# Instalar dependencias de gRPC
echo "📦 Instalando dependencias de gRPC..."
pip install grpcio grpcio-tools

if [ $? -ne 0 ]; then
    echo "❌ Error instalando dependencias de gRPC"
    exit 1
fi

echo "✅ Dependencias de gRPC instaladas"
echo ""

# Instalar dependencias de cada servicio
echo "📦 Instalando dependencias de servicios..."

if [ -f "grpc/services/user-service/requirements.txt" ]; then
    echo "Instalando dependencias de user-service..."
    pip install -r grpc/services/user-service/requirements.txt
fi

if [ -f "grpc/services/inventory-service/requirements.txt" ]; then
    echo "Instalando dependencias de inventory-service..."
    pip install -r grpc/services/inventory-service/requirements.txt
fi

if [ -f "grpc/services/events-service/requirements.txt" ]; then
    echo "Instalando dependencias de events-service..."
    pip install -r grpc/services/events-service/requirements.txt
fi

echo "✅ Dependencias de servicios instaladas"
echo ""

# Generar código proto
echo "🔧 Generando código Python desde archivos .proto..."
chmod +x grpc/scripts/generate-proto.sh
./grpc/scripts/generate-proto.sh

echo ""
echo "========================================"
echo "   ✅ Setup completado exitosamente!"
echo "========================================"
echo ""
echo "Próximos pasos:"
echo "1. Configurar la base de datos MySQL"
echo "2. Iniciar los servicios: ./grpc/scripts/start-services.sh"
echo "3. Iniciar el API Gateway: cd api-gateway && npm start"
echo ""