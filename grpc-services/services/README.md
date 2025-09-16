# Microservicios gRPC - Sistema ONG

Este directorio contiene los tres microservicios Python que implementan la lógica de negocio del Sistema ONG Backend.

## Servicios

### user-service (Puerto 50051)
**Responsabilidades:**
- Gestión CRUD de usuarios
- Autenticación y generación de tokens JWT
- Encriptación de contraseñas con bcrypt
- Validación de roles y permisos

**Endpoints gRPC:**
- `CrearUsuario` - Crear nuevo usuario
- `ObtenerUsuario` - Obtener usuario por ID
- `ListarUsuarios` - Listar usuarios con paginación
- `ActualizarUsuario` - Actualizar datos de usuario
- `EliminarUsuario` - Baja lógica de usuario
- `AutenticarUsuario` - Login con credenciales
- `ValidarToken` - Validar token JWT

### inventory-service (Puerto 50052)
**Responsabilidades:**
- Gestión CRUD de donaciones
- Control de stock y validaciones de cantidad
- Auditoría de operaciones
- Integración con Kafka para transferencias entre ONGs

**Endpoints gRPC:**
- `CrearDonacion` - Registrar nueva donación
- `ObtenerDonacion` - Obtener donación por ID
- `ListarDonaciones` - Listar donaciones con filtros
- `ActualizarDonacion` - Actualizar datos de donación
- `EliminarDonacion` - Baja lógica de donación
- `ActualizarStock` - Modificar cantidad en stock
- `ValidarStock` - Verificar disponibilidad de stock

### events-service (Puerto 50053)
**Responsabilidades:**
- Gestión CRUD de eventos solidarios
- Manejo de participantes y asignaciones
- Validación de fechas futuras
- Registro de donaciones repartidas
- Integración con Kafka para eventos externos

**Endpoints gRPC:**
- `CrearEvento` - Crear nuevo evento
- `ObtenerEvento` - Obtener evento por ID
- `ListarEventos` - Listar eventos con filtros
- `ActualizarEvento` - Actualizar datos de evento
- `EliminarEvento` - Eliminar evento
- `AgregarParticipante` - Asignar participante a evento
- `QuitarParticipante` - Remover participante de evento
- `RegistrarDonacionesRepartidas` - Registrar donaciones distribuidas

## Estructura de Cada Servicio

```
{service-name}/
├── src/
│   ├── grpc/                  # Código generado desde .proto
│   │   ├── __init__.py
│   │   ├── {service}_pb2.py   # Mensajes Protocol Buffer
│   │   └── {service}_pb2_grpc.py # Servicios gRPC
│   ├── handlers/              # Lógica de negocio
│   ├── models/                # Modelos de datos
│   ├── config/                # Configuración
│   └── main.py               # Punto de entrada del servicio
├── tests/                     # Tests unitarios
├── requirements.txt           # Dependencias Python
├── Dockerfile                # Imagen Docker
├── .env.example              # Variables de entorno ejemplo
└── README.md                 # Documentación específica
```

## Desarrollo

### Generar Código Proto
```bash
# Desde el directorio raíz
grpc/scripts/generate-proto.bat  # Windows
./grpc/scripts/generate-proto.sh # Linux/Mac
```

### Ejecutar Servicio Individual
```bash
# Ejemplo: user-service
cd grpc/services/user-service
python src/main.py
```

### Ejecutar Todos los Servicios
```bash
# Desde el directorio raíz
grpc/scripts/start-services.bat  # Windows
./grpc/scripts/start-services.sh # Linux/Mac
```

### Tests
```bash
# Ejecutar tests de un servicio
cd grpc/services/user-service
python -m pytest tests/

# Ejecutar tests con coverage
python -m pytest tests/ --cov=src
```

## Dependencias Comunes

Todos los servicios utilizan:
- `grpcio` - Framework gRPC para Python
- `grpcio-tools` - Herramientas de compilación proto
- `mysql-connector-python` - Conector MySQL
- `bcrypt` - Encriptación de contraseñas
- `PyJWT` - Manejo de tokens JWT
- `python-dotenv` - Variables de entorno
- `pytest` - Framework de testing

## Configuración

Cada servicio requiere las siguientes variables de entorno:

```env
# Base de datos
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ong_sistema
DB_USER=root
DB_PASSWORD=password

# gRPC
GRPC_PORT=50051  # Varía por servicio

# JWT (solo user-service)
JWT_SECRET=your-secret-key
JWT_EXPIRATION=3600

# Kafka (para servicios que lo requieran)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

## Comunicación

- **Interna**: Los servicios se comunican entre sí via gRPC
- **Externa**: El API Gateway se conecta a los servicios via gRPC
- **Kafka**: Para eventos asíncronos entre ONGs
- **Base de datos**: Cada servicio accede directamente a MySQL