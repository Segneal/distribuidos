# User Service - Sistema ONG Backend

## Propósito

El servicio de usuarios es un microservicio gRPC que gestiona la autenticación, autorización y operaciones CRUD de usuarios para el sistema ONG "Empuje Comunitario". Proporciona funcionalidades para crear, leer, actualizar y eliminar usuarios, así como autenticación con tokens JWT y envío de emails con contraseñas temporales.

## Funcionalidades

### Gestión de Usuarios
- **Crear Usuario**: Crea nuevos usuarios con generación automática de contraseña y envío por email
- **Obtener Usuario**: Recupera información de un usuario por ID
- **Listar Usuarios**: Lista usuarios con paginación y filtros
- **Actualizar Usuario**: Modifica información de usuario (excepto contraseña)
- **Eliminar Usuario**: Baja lógica de usuarios

### Autenticación y Autorización
- **Autenticar Usuario**: Valida credenciales y genera tokens JWT
- **Validar Token**: Verifica validez de tokens JWT
- **Roles de Usuario**: PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO
- **Encriptación**: Contraseñas encriptadas con bcrypt

### Notificaciones
- **Envío de Emails**: Notificación automática con contraseñas temporales usando Ethereal SMTP

## Instalación

### Prerrequisitos
- Python 3.8+
- MySQL 8.0+
- Acceso a servidor SMTP (Ethereal para testing)

### Pasos de Instalación

1. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Generar código gRPC**:
```bash
python generate_proto.py
```

4. **Configurar base de datos**:
Asegúrate de que MySQL esté ejecutándose y la base de datos `ong_sistema` esté creada con las tablas correspondientes.

## Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y configura las siguientes variables:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ong_sistema
DB_USER=ong_user
DB_PASSWORD=ong_password
DB_POOL_SIZE=5

# gRPC Configuration
GRPC_PORT=50051

# JWT Configuration
JWT_SECRET=your_jwt_secret_change_in_production
JWT_EXPIRATION_HOURS=24

# Email Configuration (Ethereal for testing)
SMTP_SERVER=smtp.ethereal.email
SMTP_PORT=587
SMTP_USER=ethereal.user@ethereal.email
SMTP_PASSWORD=ethereal.password
FROM_EMAIL=noreply@empujecomunitario.org
FROM_NAME=Sistema ONG

# Logging
LOG_LEVEL=INFO
```

### Configuración de Email con Ethereal

Para testing, puedes usar Ethereal Email:

1. Ve a [https://ethereal.email/](https://ethereal.email/)
2. Crea una cuenta de testing
3. Usa las credenciales proporcionadas en tu archivo `.env`

## Uso

### Iniciar el Servicio

```bash
# Desde el directorio del servicio
python src/main.py

# O usando el servidor directamente
python src/grpc/server.py
```

El servicio se iniciará en el puerto configurado (por defecto 50051).

### Métodos gRPC Disponibles

#### CrearUsuario
Crea un nuevo usuario con contraseña aleatoria y envío de email.

```python
request = CrearUsuarioRequest(
    nombreUsuario="nuevo_usuario",
    nombre="Juan",
    apellido="Pérez",
    telefono="123-456-7890",
    email="juan@example.com",
    rol="VOLUNTARIO",
    usuarioCreador="admin"
)
```

#### AutenticarUsuario
Autentica usuario y genera token JWT.

```python
request = AutenticarRequest(
    identificador="usuario@email.com",  # o nombre de usuario
    clave="contraseña"
)
```

#### ListarUsuarios
Lista usuarios con paginación.

```python
request = ListarUsuariosRequest(
    pagina=1,
    tamanoPagina=10,
    incluirInactivos=False
)
```

## Testing

### Ejecutar Pruebas Unitarias

```bash
# Ejecutar todas las pruebas
python -m pytest tests/ -v

# Ejecutar pruebas específicas
python -m pytest tests/test_usuario_model.py -v

# Ejecutar con cobertura
python -m pytest tests/ --cov=src --cov-report=html
```

### Pruebas de Integración

Para probar el servicio completo:

1. **Asegúrate de que MySQL esté ejecutándose**
2. **Configura las variables de entorno correctamente**
3. **Ejecuta el servicio**:
```bash
python src/main.py
```

4. **Usa un cliente gRPC para probar los endpoints**

### Ejemplo de Cliente gRPC

```python
import grpc
import user_pb2
import user_pb2_grpc

# Conectar al servicio
channel = grpc.insecure_channel('localhost:50051')
stub = user_pb2_grpc.UsuarioServiceStub(channel)

# Crear usuario
request = user_pb2.CrearUsuarioRequest(
    nombreUsuario="test_user",
    nombre="Test",
    apellido="User",
    email="test@example.com",
    rol="VOLUNTARIO",
    usuarioCreador="admin"
)

response = stub.CrearUsuario(request)
print(f"Usuario creado: {response.exitoso}")
```

## Estructura del Proyecto

```
user-service/
├── src/
│   ├── config/
│   │   ├── database.py      # Configuración de base de datos
│   │   └── email.py         # Configuración de email
│   ├── models/
│   │   └── usuario.py       # Modelo de datos Usuario
│   ├── repositories/
│   │   └── usuario_repository.py  # Acceso a datos
│   ├── grpc/
│   │   ├── server.py        # Servidor gRPC
│   │   ├── usuario_service.py  # Implementación del servicio
│   │   ├── user_pb2.py      # Código generado protobuf
│   │   └── user_pb2_grpc.py # Código generado gRPC
│   └── main.py              # Punto de entrada
├── tests/
│   └── test_usuario_model.py  # Pruebas unitarias
├── requirements.txt         # Dependencias Python
├── .env.example            # Ejemplo de configuración
├── generate_proto.py       # Script para generar código gRPC
└── README.md              # Esta documentación
```

## Dependencias

- **grpcio**: Framework gRPC para Python
- **grpcio-tools**: Herramientas para generar código gRPC
- **mysql-connector-python**: Conector MySQL
- **bcrypt**: Encriptación de contraseñas
- **PyJWT**: Manejo de tokens JWT
- **python-dotenv**: Carga de variables de entorno
- **pytest**: Framework de testing

## Logs y Monitoreo

El servicio genera logs estructurados que incluyen:
- Inicio y parada del servicio
- Operaciones de base de datos
- Errores de autenticación
- Envío de emails
- Errores del sistema

Los logs se configuran mediante la variable `LOG_LEVEL` en el archivo `.env`.

## Seguridad

### Mejores Prácticas Implementadas

1. **Encriptación de Contraseñas**: Uso de bcrypt con salt automático
2. **Tokens JWT**: Autenticación stateless con expiración configurable
3. **Validación de Entrada**: Validación exhaustiva de todos los campos
4. **Baja Lógica**: Los usuarios se marcan como inactivos en lugar de eliminarse
5. **Pool de Conexiones**: Gestión eficiente de conexiones a base de datos
6. **Manejo de Errores**: Respuestas de error que no revelan información sensible

### Consideraciones de Producción

- Cambiar `JWT_SECRET` por un valor seguro y único
- Usar HTTPS para todas las comunicaciones
- Configurar un servidor SMTP real para producción
- Implementar rate limiting
- Configurar monitoreo y alertas
- Usar conexiones SSL para MySQL

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a MySQL**:
   - Verificar que MySQL esté ejecutándose
   - Comprobar credenciales en `.env`
   - Verificar que la base de datos existe

2. **Error al enviar emails**:
   - Verificar configuración SMTP en `.env`
   - Comprobar conectividad de red
   - Para Ethereal, verificar que las credenciales sean válidas

3. **Error al generar código gRPC**:
   - Verificar que `grpcio-tools` esté instalado
   - Comprobar que el archivo `.proto` existe
   - Verificar permisos de escritura en el directorio

4. **Errores de importación**:
   - Verificar que todas las dependencias estén instaladas
   - Comprobar que el código gRPC se haya generado correctamente
   - Verificar la estructura de directorios

## Contribución

Para contribuir al desarrollo:

1. Seguir las convenciones de código Python (PEP 8)
2. Escribir pruebas para nuevas funcionalidades
3. Actualizar la documentación según sea necesario
4. Usar commits descriptivos

## Licencia

Este proyecto es parte del Sistema ONG Backend y está sujeto a las mismas condiciones de licencia del proyecto principal.