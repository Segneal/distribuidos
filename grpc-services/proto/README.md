# Protocol Buffers Definitions

Este directorio contiene las definiciones de protocolo gRPC compartidas para todos los microservicios del Sistema ONG Backend.

## Archivos

- `user.proto` - Definiciones del servicio de gestión de usuarios (UsuarioService)
- `inventory.proto` - Definiciones del servicio de inventario/donaciones (InventarioService)  
- `events.proto` - Definiciones del servicio de gestión de eventos (EventoService)

## Servicios Definidos

### UsuarioService (user.proto)
- CrearUsuario, ObtenerUsuario, ListarUsuarios
- ActualizarUsuario, EliminarUsuario
- AutenticarUsuario, ValidarToken

### InventarioService (inventory.proto)
- CrearDonacion, ObtenerDonacion, ListarDonaciones
- ActualizarDonacion, EliminarDonacion
- ActualizarStock, ValidarStock

### EventoService (events.proto)
- CrearEvento, ObtenerEvento, ListarEventos
- ActualizarEvento, EliminarEvento
- AgregarParticipante, QuitarParticipante
- RegistrarDonacionesRepartidas

## Generación de Código

Para generar código Python desde los archivos proto:

```bash
# Desde el directorio raíz del proyecto
python -m grpc_tools.protoc -I./grpc/proto --python_out=./grpc/services/user-service/src/grpc --grpc_python_out=./grpc/services/user-service/src/grpc grpc/proto/user.proto
python -m grpc_tools.protoc -I./grpc/proto --python_out=./grpc/services/inventory-service/src/grpc --grpc_python_out=./grpc/services/inventory-service/src/grpc grpc/proto/inventory.proto
python -m grpc_tools.protoc -I./grpc/proto --python_out=./grpc/services/events-service/src/grpc --grpc_python_out=./grpc/services/events-service/src/grpc grpc/proto/events.proto
```

## Uso

Estos archivos proto definen el contrato entre el API Gateway y los microservicios, asegurando comunicación consistente a través del sistema distribuido.

## Características

- **Nomenclatura en español**: Todos los servicios, métodos y campos están en español según el diseño
- **Campos de auditoría**: Incluye fechaHoraAlta, usuarioAlta, fechaHoraModificacion, usuarioModificacion
- **Validaciones**: Campos para validación de stock, fechas futuras, roles, etc.
- **Paginación**: Soporte para paginación en operaciones de listado
- **Respuestas consistentes**: Todas las respuestas incluyen exitoso, mensaje y datos