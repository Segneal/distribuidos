# Task 3.3 Implementation Summary: Autenticación y Autorización

## Resumen de Implementación

Se ha implementado exitosamente el sistema completo de autenticación y autorización para el servicio de usuarios, cumpliendo con todos los requerimientos especificados en la tarea 3.3.

## Funcionalidades Implementadas

### 1. Autenticación de Usuarios

#### Método `AutenticarUsuario`
- **Funcionalidad**: Valida credenciales de usuario y genera token JWT
- **Entrada**: Identificador (nombre de usuario o email) y contraseña
- **Validaciones**:
  - Usuario existe en el sistema
  - Usuario está activo
  - Contraseña es correcta (usando bcrypt)
- **Salida**: Token JWT con información del usuario
- **Manejo de errores específicos**:
  - "Usuario/email inexistente"
  - "Usuario inactivo"
  - "Credenciales incorrectas"

#### Generación de Tokens JWT
- **Algoritmo**: HS256
- **Payload incluye**:
  - `user_id`: ID del usuario
  - `username`: Nombre de usuario
  - `email`: Email del usuario
  - `role`: Rol del usuario
  - `exp`: Fecha de expiración (configurable, default 24 horas)
  - `iat`: Fecha de emisión
- **Configuración**: Secret key y tiempo de expiración via variables de entorno

### 2. Validación de Tokens

#### Método `ValidarToken`
- **Funcionalidad**: Valida tokens JWT y retorna información del usuario
- **Validaciones**:
  - Token tiene formato válido
  - Token no ha expirado
  - Usuario asociado existe y está activo
- **Manejo de errores específicos**:
  - "Token inválido"
  - "Token expirado"
  - "Usuario no válido"

### 3. Autorización por Roles

#### Método `ValidarPermisos`
- **Funcionalidad**: Valida si un usuario tiene permisos para una operación específica
- **Entrada**: Token JWT y nombre de operación
- **Operaciones soportadas**:
  - `usuarios`: Gestión de usuarios (solo PRESIDENTE)
  - `inventario`: Gestión de inventario (PRESIDENTE, VOCAL)
  - `eventos`: Gestión de eventos (PRESIDENTE, COORDINADOR)
  - `participar_eventos`: Participación en eventos (todos los roles)
  - `auto_asignar_eventos`: Auto-asignación a eventos (solo VOLUNTARIO)
  - `gestionar_participantes`: Gestión de participantes (PRESIDENTE, COORDINADOR)

#### Métodos de Autorización en Modelo Usuario
- `tiene_permiso_para_usuarios()`: Solo PRESIDENTE
- `tiene_permiso_para_inventario()`: PRESIDENTE, VOCAL
- `tiene_permiso_para_eventos()`: PRESIDENTE, COORDINADOR
- `puede_participar_en_eventos()`: Todos los roles
- `es_voluntario()`: Solo VOLUNTARIO
- `puede_auto_asignarse_eventos()`: Solo VOLUNTARIO
- `puede_gestionar_participantes()`: PRESIDENTE, COORDINADOR
- `validar_permisos_operacion()`: Método estático para validación

### 4. Manejo de Errores

#### Errores de Autenticación
- Códigos gRPC apropiados (UNAUTHENTICATED, PERMISSION_DENIED, INTERNAL)
- Mensajes específicos para cada tipo de error
- Logging detallado para debugging
- Manejo de excepciones de base de datos

#### Errores de Autorización
- Validación de permisos antes de operaciones
- Mensajes descriptivos de permisos faltantes
- Manejo de tokens inválidos o expirados

## Estructura de Archivos Modificados/Creados

```
grpc/services/user-service/
├── src/
│   ├── models/usuario.py                    # ✓ Métodos de autorización agregados
│   ├── service/usuario_service.py           # ✓ Métodos de autenticación implementados
│   └── repositories/usuario_repository.py   # ✓ Ya tenía método obtener_por_identificador
├── tests/
│   └── test_autenticacion.py               # ✓ Tests completos de autenticación/autorización
├── demo_autenticacion.py                   # ✓ Demo funcional del sistema
└── TASK_3.3_IMPLEMENTATION_SUMMARY.md     # ✓ Este documento
```

## Archivos Proto Actualizados

```
grpc/proto/user.proto                       # ✓ Agregado método ValidarPermisos
```

## Requerimientos Cumplidos

### Requerimiento 3.1 - Gestión de Roles y Autenticación
✅ **Cumplido**: Sistema valida roles y permisos específicos para cada operación

### Requerimiento 3.2 - Sistema de Autenticación  
✅ **Cumplido**: Login con nombreUsuario o email, mensajes específicos de error

### Requerimiento 3.3 - Autenticación con Credenciales
✅ **Cumplido**: Validación completa de credenciales y generación de tokens

### Requerimiento 3.4 - Manejo de Errores Específicos
✅ **Cumplido**: Mensajes específicos para cada tipo de error de autenticación

### Requerimiento 3.5 - Validación de Usuario Activo
✅ **Cumplido**: Sistema verifica que el usuario esté activo antes de autenticar

### Requerimiento 3.6 - Generación de Token de Sesión
✅ **Cumplido**: Tokens JWT con información completa del usuario y expiración

### Requerimiento 15.3 - Tokens con Tiempo de Expiración
✅ **Cumplido**: Tokens JWT configurables con validación de expiración

## Matriz de Permisos Implementada

| Operación | PRESIDENTE | VOCAL | COORDINADOR | VOLUNTARIO |
|-----------|------------|-------|-------------|------------|
| usuarios | ✅ | ❌ | ❌ | ❌ |
| inventario | ✅ | ✅ | ❌ | ❌ |
| eventos | ✅ | ❌ | ✅ | ❌ |
| participar_eventos | ✅ | ✅ | ✅ | ✅ |
| auto_asignar_eventos | ❌ | ❌ | ❌ | ✅ |
| gestionar_participantes | ✅ | ❌ | ✅ | ❌ |

## Tests Implementados

### TestAutenticacion (10 tests)
- ✅ Autenticación exitosa con generación de token
- ✅ Usuario inexistente
- ✅ Usuario inactivo  
- ✅ Contraseña incorrecta
- ✅ Validación de token válido
- ✅ Token expirado
- ✅ Token inválido
- ✅ Validación de permisos exitosa
- ✅ Validación de permisos denegada
- ✅ Diferentes roles y operaciones

### TestAutorizacion (13 tests)
- ✅ Permisos por rol para cada operación
- ✅ Métodos de autorización en modelo Usuario
- ✅ Validación estática de permisos
- ✅ Auto-asignación de eventos por voluntarios
- ✅ Gestión de participantes por roles autorizados

### TestManejadorErroresAutenticacion (3 tests)
- ✅ Manejo de errores de base de datos en autenticación
- ✅ Manejo de errores de base de datos en validación de token
- ✅ Manejo de errores de base de datos en validación de permisos

**Total: 26 tests - Todos PASANDO ✅**

## Demo Funcional

El archivo `demo_autenticacion.py` proporciona una demostración completa del sistema:

1. **Creación de usuarios de prueba** para todos los roles
2. **Pruebas de autenticación** exitosa y fallida
3. **Validación de tokens** válidos, inválidos y expirados
4. **Pruebas de autorización** para diferentes operaciones y roles
5. **Matriz de permisos** visual mostrando qué rol puede hacer qué operación

## Configuración Requerida

### Variables de Entorno
```bash
JWT_SECRET=your-secret-key-here          # Clave secreta para JWT
JWT_EXPIRATION_HOURS=24                  # Horas de expiración del token
```

### Dependencias
- `PyJWT`: Para generación y validación de tokens JWT
- `bcrypt`: Para encriptación y verificación de contraseñas (ya implementado)
- `grpcio`: Para comunicación gRPC (ya implementado)

## Integración con API Gateway

El sistema está listo para integrarse con el API Gateway mediante:

1. **Endpoint de login**: Llamada a `AutenticarUsuario`
2. **Middleware de autenticación**: Llamada a `ValidarToken`
3. **Middleware de autorización**: Llamada a `ValidarPermisos`

## Conclusión

La implementación de autenticación y autorización está **COMPLETA** y cumple con todos los requerimientos especificados. El sistema proporciona:

- ✅ Autenticación segura con JWT
- ✅ Autorización granular por roles
- ✅ Manejo robusto de errores
- ✅ Validación completa de permisos
- ✅ Tests exhaustivos (26 tests pasando)
- ✅ Documentación y demo funcional

El sistema está listo para ser utilizado por el API Gateway y otros servicios que requieran autenticación y autorización de usuarios.