#!/bin/bash

echo "Iniciando servicios gRPC..."

# Verificar que los servicios existen
if [ ! -f "grpc/services/user-service/src/main.py" ]; then
    echo "❌ Error: grpc/services/user-service/src/main.py no encontrado"
    exit 1
fi

if [ ! -f "grpc/services/inventory-service/src/main.py" ]; then
    echo "❌ Error: grpc/services/inventory-service/src/main.py no encontrado"
    exit 1
fi

if [ ! -f "grpc/services/events-service/src/main.py" ]; then
    echo "❌ Error: grpc/services/events-service/src/main.py no encontrado"
    exit 1
fi

echo ""
echo "🚀 Iniciando servicios en paralelo..."
echo ""
echo "- User Service (Puerto 50051)"
echo "- Inventory Service (Puerto 50052)"  
echo "- Events Service (Puerto 50053)"
echo ""

# Función para manejar la señal de interrupción
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $USER_PID $INVENTORY_PID $EVENTS_PID 2>/dev/null
    exit 0
}

# Configurar trap para manejar Ctrl+C
trap cleanup SIGINT

# Iniciar servicios en background
cd grpc/services/user-service && python src/main.py &
USER_PID=$!

cd ../inventory-service && python src/main.py &
INVENTORY_PID=$!

cd ../events-service && python src/main.py &
EVENTS_PID=$!

cd ../../..

echo "✅ Servicios iniciados!"
echo ""
echo "PIDs de los procesos:"
echo "- User Service: $USER_PID"
echo "- Inventory Service: $INVENTORY_PID"
echo "- Events Service: $EVENTS_PID"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios"

# Esperar a que terminen los procesos
wait