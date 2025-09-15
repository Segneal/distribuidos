# gRPC Backend Services

Este directorio contiene todos los componentes relacionados con gRPC del Sistema ONG Backend.

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

### UsuarioService
- **Puerto**: 50051
- **Responsabilidades**: Autenticación, gestión de usuarios, validación de tokens

### InventarioService  
- **Puerto**: 50052
- **Responsabilidades**: Gestión de donaciones, control de stock

### EventoService
- **Puerto**: 50053
- **Responsabilidades**: Gestión de eventos, participantes, donaciones repartidas

## Comandos Rápidos

```bash
# Generar código Python desde proto files
./grpc/scripts/generate-proto.sh

# Iniciar todos los servicios gRPC
./grpc/scripts/start-services.sh

# Iniciar servicio individual
cd grpc/services/user-service && python src/main.py
```