# Servicios backend gRPC

Este directorio agrupa todos los componentes gRPC del Sistema ONG Backend.

## Estructura

```
grpc/
├── proto/                      # Definiciones Protocol Buffers
│   ├── user.proto             # Servicio de usuarios
│   ├── inventory.proto        # Servicio de inventario
│   ├── events.proto           # Servicio de eventos
│   └── README.md
├── services/                   # Microservicios Python + gRPC
│   ├── user-service/          # Servicio de gestión de usuarios
│   ├── inventory-service/     # Servicio de inventario de donaciones
│   ├── events-service/        # Servicio de eventos solidarios
│   └── README.md
└── scripts/                   # Scripts de utilidades
    ├── generate-proto.sh      # Generación de código Python
    ├── start-services.sh      # Inicio de todos los servicios
    └── README.md
```

## Servicios gRPC

### Servicio de usuarios
- **Puerto**: 50051
- **Responsabilidades**: autenticación, gestión de usuarios, validación de tokens.

### Servicio de inventario
- **Puerto**: 50052
- **Responsabilidades**: gestión de donaciones y control de stock.

### Servicio de eventos
- **Puerto**: 50053
- **Responsabilidades**: gestión de eventos, participantes y donaciones repartidas.

## Comandos rápidos

```bash
# Generar código Python desde los archivos .proto
./grpc/scripts/generate-proto.sh

# Iniciar todos los servicios gRPC
./grpc/scripts/start-services.sh

# Iniciar un servicio individual
cd grpc/services/user-service && python src/main.py
```
