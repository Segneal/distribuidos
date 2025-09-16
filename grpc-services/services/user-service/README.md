# User Service - Sistema ONG Backend

## Propósito y Funcionalidades

### Propósito Principal
El servicio de usuarios es un microservicio gRPC que gestiona la autenticación, autorización y operaciones CRUD de usuarios para el sistema ONG "Empuje Comunitario". Actúa como el núcleo de seguridad del sistema, proporcionando control de acceso basado en roles y gestión completa del ciclo de vida de usuarios.

### Arquitectura del Servicio
- **Protocolo**: gRPC para comunicación de alta performance
- **Base de Datos**: MySQL con pool de conexiones
- **Autenticación**: JWT tokens con expiración configurable
- **Notificaciones**: SMTP para envío de credenciales
- **Seguridad**: Encriptación bcrypt para contraseñas

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
Crea un nuevo usuario con contraseña aleatoria y envío de email automático.

**Entrada:**
```python
request = CrearUsuarioRequest(
    nombreUsuario="nuevo_usuario",
    nombre="Juan",
    apellido="Pérez",
    telefono="123-456-7890",
    email="juan@example.com",
    rol="VOLUNTARIO",  # PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO
    usuarioCreador="admin"
)
```

**Salida:**
```python
response = UsuarioResponse(
    exitoso=True,
    usuario=Usuario(...),
    mensaje="Usuario creado exitosamente. Email enviado."
)
```

#### ObtenerUsuario
Recupera información de un usuario específico por ID.

**Entrada:**
```python
request = ObtenerUsuarioRequest(id=1)
```

#### ListarUsuarios
Lista usuarios con paginación y filtros opcionales.

**Entrada:**
```python
request = ListarUsuariosRequest(
    pagina=1,
    tamanoPagina=10,
    incluirInactivos=False,
    filtroRol="VOLUNTARIO"  # Opcional
)
```

#### ActualizarUsuario
Modifica información de usuario (excepto contraseña y nombreUsuario).

**Entrada:**
```python
request = ActualizarUsuarioRequest(
    id=1,
    nombre="Juan Carlos",
    apellido="Pérez González",
    telefono="987-654-3210",
    email="juan.carlos@example.com",
    rol="COORDINADOR",
    usuarioModificacion="admin"
)
```

#### EliminarUsuario
Realiza baja lógica del usuario (marca como inactivo).

**Entrada:**
```python
request = EliminarUsuarioRequest(
    id=1,
    usuarioEliminacion="admin"
)
```

#### AutenticarUsuario
Autentica usuario y genera token JWT.

**Entrada:**
```python
request = AutenticarRequest(
    identificador="usuario@email.com",  # nombreUsuario o email
    clave="contraseña_temporal"
)
```

**Salida:**
```python
response = AutenticarResponse(
    exitoso=True,
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    usuario=Usuario(...),
    mensaje="Autenticación exitosa"
)
```

#### ValidarToken
Verifica la validez de un token JWT y retorna información del usuario.

**Entrada:**
```python
request = ValidarTokenRequest(
    token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
)
```

**Salida:**
```python
response = ValidarTokenResponse(
    valido=True,
    usuario=Usuario(...),
    mensaje="Token válido"
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

### Ejemplos de Uso Completos

#### Ejemplo 1: Cliente gRPC Básico

```python
import grpc
import sys
import os

# Agregar el directorio src al path para importar los módulos generados
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from grpc import user_pb2, user_pb2_grpc

def main():
    # Conectar al servicio
    channel = grpc.insecure_channel('localhost:50051')
    stub = user_pb2_grpc.UsuarioServiceStub(channel)
    
    try:
        # 1. Crear usuario
        print("=== Creando Usuario ===")
        create_request = user_pb2.CrearUsuarioRequest(
            nombreUsuario="test_user",
            nombre="Test",
            apellido="User",
            telefono="123-456-7890",
            email="test@example.com",
            rol="VOLUNTARIO",
            usuarioCreador="admin"
        )
        
        create_response = stub.CrearUsuario(create_request)
        print(f"Usuario creado: {create_response.exitoso}")
        print(f"Mensaje: {create_response.mensaje}")
        
        if create_response.exitoso:
            user_id = create_response.usuario.id
            print(f"ID del usuario: {user_id}")
            
            # 2. Autenticar usuario (necesitarás la contraseña del email)
            print("\n=== Autenticando Usuario ===")
            auth_request = user_pb2.AutenticarRequest(
                identificador="test@example.com",
                clave="contraseña_del_email"  # Obtener del email enviado
            )
            
            auth_response = stub.AutenticarUsuario(auth_request)
            if auth_response.exitoso:
                print(f"Token JWT: {auth_response.token[:50]}...")
                
                # 3. Validar token
                print("\n=== Validando Token ===")
                validate_request = user_pb2.ValidarTokenRequest(
                    token=auth_response.token
                )
                
                validate_response = stub.ValidarToken(validate_request)
                print(f"Token válido: {validate_response.valido}")
                
                # 4. Listar usuarios
                print("\n=== Listando Usuarios ===")
                list_request = user_pb2.ListarUsuariosRequest(
                    pagina=1,
                    tamanoPagina=10,
                    incluirInactivos=False
                )
                
                list_response = stub.ListarUsuarios(list_request)
                print(f"Total usuarios: {list_response.total}")
                for usuario in list_response.usuarios:
                    print(f"- {usuario.nombreUsuario} ({usuario.rol})")
            
    except grpc.RpcError as e:
        print(f"Error gRPC: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        channel.close()

if __name__ == "__main__":
    main()
```

#### Ejemplo 2: Testing de Autenticación

```python
import grpc
from grpc import user_pb2, user_pb2_grpc

def test_authentication_flow():
    """Prueba el flujo completo de autenticación"""
    channel = grpc.insecure_channel('localhost:50051')
    stub = user_pb2_grpc.UsuarioServiceStub(channel)
    
    # Casos de prueba
    test_cases = [
        {
            "identificador": "admin@ong.com",
            "clave": "admin123",
            "expected": True,
            "description": "Login con email válido"
        },
        {
            "identificador": "admin",
            "clave": "admin123", 
            "expected": True,
            "description": "Login con nombreUsuario válido"
        },
        {
            "identificador": "admin@ong.com",
            "clave": "wrong_password",
            "expected": False,
            "description": "Login con contraseña incorrecta"
        },
        {
            "identificador": "nonexistent@ong.com",
            "clave": "any_password",
            "expected": False,
            "description": "Login con usuario inexistente"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nProbando: {test_case['description']}")
        
        request = user_pb2.AutenticarRequest(
            identificador=test_case["identificador"],
            clave=test_case["clave"]
        )
        
        try:
            response = stub.AutenticarUsuario(request)
            success = response.exitoso
            print(f"Resultado: {'✓' if success == test_case['expected'] else '✗'}")
            print(f"Mensaje: {response.mensaje}")
            
            if success and test_case['expected']:
                print(f"Token generado: {response.token[:30]}...")
                print(f"Usuario: {response.usuario.nombreUsuario} ({response.usuario.rol})")
                
        except grpc.RpcError as e:
            print(f"Error gRPC: {e.details()}")
    
    channel.close()

if __name__ == "__main__":
    test_authentication_flow()
```

#### Ejemplo 3: Gestión Completa de Usuarios

```python
import grpc
from grpc import user_pb2, user_pb2_grpc
import time

def demo_user_management():
    """Demuestra la gestión completa de usuarios"""
    channel = grpc.insecure_channel('localhost:50051')
    stub = user_pb2_grpc.UsuarioServiceStub(channel)
    
    try:
        # 1. Crear múltiples usuarios
        usuarios_test = [
            {
                "nombreUsuario": "coordinador1",
                "nombre": "María",
                "apellido": "González",
                "telefono": "111-222-3333",
                "email": "maria@ong.com",
                "rol": "COORDINADOR"
            },
            {
                "nombreUsuario": "voluntario1", 
                "nombre": "Carlos",
                "apellido": "López",
                "telefono": "444-555-6666",
                "email": "carlos@ong.com",
                "rol": "VOLUNTARIO"
            }
        ]
        
        created_users = []
        
        for user_data in usuarios_test:
            print(f"\nCreando usuario: {user_data['nombreUsuario']}")
            
            request = user_pb2.CrearUsuarioRequest(
                nombreUsuario=user_data["nombreUsuario"],
                nombre=user_data["nombre"],
                apellido=user_data["apellido"],
                telefono=user_data["telefono"],
                email=user_data["email"],
                rol=user_data["rol"],
                usuarioCreador="admin"
            )
            
            response = stub.CrearUsuario(request)
            if response.exitoso:
                created_users.append(response.usuario.id)
                print(f"✓ Usuario creado con ID: {response.usuario.id}")
            else:
                print(f"✗ Error: {response.mensaje}")
        
        # 2. Listar usuarios creados
        print("\n=== Listando todos los usuarios ===")
        list_request = user_pb2.ListarUsuariosRequest(
            pagina=1,
            tamanoPagina=20,
            incluirInactivos=False
        )
        
        list_response = stub.ListarUsuarios(list_request)
        print(f"Total de usuarios activos: {list_response.total}")
        
        for usuario in list_response.usuarios:
            print(f"- ID: {usuario.id}, Usuario: {usuario.nombreUsuario}, "
                  f"Nombre: {usuario.nombre} {usuario.apellido}, Rol: {usuario.rol}")
        
        # 3. Actualizar un usuario
        if created_users:
            user_id = created_users[0]
            print(f"\n=== Actualizando usuario ID: {user_id} ===")
            
            update_request = user_pb2.ActualizarUsuarioRequest(
                id=user_id,
                nombre="María Elena",
                apellido="González Rodríguez",
                telefono="111-222-4444",
                email="maria.elena@ong.com",
                rol="COORDINADOR",
                usuarioModificacion="admin"
            )
            
            update_response = stub.ActualizarUsuario(update_request)
            if update_response.exitoso:
                print("✓ Usuario actualizado exitosamente")
                print(f"Nuevo nombre: {update_response.usuario.nombre} {update_response.usuario.apellido}")
            else:
                print(f"✗ Error al actualizar: {update_response.mensaje}")
        
        # 4. Eliminar usuario (baja lógica)
        if len(created_users) > 1:
            user_id = created_users[1]
            print(f"\n=== Eliminando usuario ID: {user_id} ===")
            
            delete_request = user_pb2.EliminarUsuarioRequest(
                id=user_id,
                usuarioEliminacion="admin"
            )
            
            delete_response = stub.EliminarUsuario(delete_request)
            if delete_response.exitoso:
                print("✓ Usuario eliminado (baja lógica) exitosamente")
            else:
                print(f"✗ Error al eliminar: {delete_response.mensaje}")
        
        # 5. Verificar usuarios activos vs inactivos
        print("\n=== Verificando usuarios activos vs inactivos ===")
        
        # Solo activos
        active_request = user_pb2.ListarUsuariosRequest(
            pagina=1,
            tamanoPagina=20,
            incluirInactivos=False
        )
        active_response = stub.ListarUsuarios(active_request)
        print(f"Usuarios activos: {active_response.total}")
        
        # Incluyendo inactivos
        all_request = user_pb2.ListarUsuariosRequest(
            pagina=1,
            tamanoPagina=20,
            incluirInactivos=True
        )
        all_response = stub.ListarUsuarios(all_request)
        print(f"Total usuarios (activos + inactivos): {all_response.total}")
        
    except grpc.RpcError as e:
        print(f"Error gRPC: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        channel.close()

if __name__ == "__main__":
    demo_user_management()
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