# Scripts de Utilidades gRPC

Este directorio contiene scripts para automatizar tareas comunes relacionadas con los servicios gRPC.

## Scripts Disponibles

### `generate-proto.sh` / `generate-proto.bat`
Genera código Python desde los archivos .proto para todos los servicios.

**Uso:**
```bash
# Linux/Mac
./grpc/scripts/generate-proto.sh

# Windows
grpc\scripts\generate-proto.bat
```

### `start-services.sh` / `start-services.bat`
Inicia todos los servicios gRPC en paralelo.

**Uso:**
```bash
# Linux/Mac
./grpc/scripts/start-services.sh

# Windows
grpc\scripts\start-services.bat
```

### `setup.sh` / `setup.bat`
Configura el entorno completo: instala dependencias, genera proto files y prepara los servicios.

**Uso:**
```bash
# Linux/Mac
./grpc/scripts/setup.sh

# Windows
grpc\scripts\setup.bat
```

## Puertos de Servicios

- **user-service**: 50051
- **inventory-service**: 50052  
- **events-service**: 50053