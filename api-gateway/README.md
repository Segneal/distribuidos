# API Gateway - Sistema ONG Backend

API Gateway para el Sistema de Gestión de ONG "Empuje Comunitario" construido con Node.js y Express. Este componente actúa como punto único de entrada para todas las peticiones REST del frontend, enrutándolas a los microservicios gRPC correspondientes y manejando autenticación, autorización y validación de manera centralizada.

## Propósito y Funcionalidades

### Propósito Principal
El API Gateway sirve como la puerta de entrada unificada para el sistema distribuido de la ONG, proporcionando una interfaz REST consistente que abstrae la complejidad de los microservicios internos basados en gRPC.

### Funcionalidades Principales

#### Gestión de Usuarios
- Autenticación con JWT tokens
- Control de acceso basado en roles (Presidente, Vocal, Coordinador, Voluntario)
- CRUD completo de usuarios (solo para Presidente)
- Validación de permisos por endpoint

#### Gestión de Inventario
- CRUD de donaciones por categoría (ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES)
- Control de stock y validaciones
- Acceso restringido a Presidente y Vocal

#### Gestión de Eventos
- CRUD de eventos solidarios
- Gestión de participantes
- Registro de donaciones repartidas
- Permisos diferenciados por rol

#### Red de ONGs (Kafka Integration)
- Solicitudes de donaciones entre organizaciones
- Ofertas de donaciones disponibles
- Transferencias de recursos
- Eventos externos y adhesiones
- Comunicación asíncrona via Apache Kafka

#### Características Técnicas
- **Arquitectura de Microservicios**: Gateway que conecta con servicios gRPC
- **Seguridad**: Helmet, CORS, Rate Limiting, JWT Authentication
- **Documentación**: Swagger/OpenAPI integrado
- **Validación**: Express Validator para entrada de datos
- **Logging**: Registro completo de requests y errores
- **Error Handling**: Manejo centralizado de errores

## Estructura del Proyecto

```
api-gateway/
├── src/
│   ├── config/
│   │   ├── grpc.js              # Configuración gRPC moderna
│   │   ├── grpc-simple.js       # Configuración simplificada para desarrollo
│   │   └── swagger.js           # Configuración de Swagger
│   ├── grpc-clients/
│   │   ├── usuarioClient.js     # Cliente gRPC para servicio de usuarios
│   │   ├── inventarioClient.js  # Cliente gRPC para servicio de inventario
│   │   └── eventoClient.js      # Cliente gRPC para servicio de eventos
│   ├── middleware/
│   │   ├── cors.js              # Configuración CORS
│   │   └── security.js          # Middleware de seguridad y rate limiting
│   ├── routes/
│   │   ├── index.js             # Rutas principales
│   │   ├── auth.js              # Rutas de autenticación
│   │   ├── usuarios.js          # Rutas de usuarios
│   │   ├── inventario.js        # Rutas de inventario
│   │   ├── eventos.js           # Rutas de eventos
│   │   └── red.js               # Rutas de red de ONGs
│   ├── tests/
│   │   └── app.test.js          # Pruebas básicas
│   ├── app.js                   # Aplicación principal (completa)
│   └── app-working.js           # Aplicación simplificada (funcional)
├── package.json
├── .env.example
└── README.md
```

## Instalación y Configuración

### Prerrequisitos
- Node.js 16+ 
- npm o yarn
- Servicios gRPC ejecutándose (user-service, inventory-service, events-service)
- MySQL database configurada
- Apache Kafka (para funcionalidades de red de ONGs)

### Pasos de Instalación

1. **Clonar el repositorio y navegar al directorio:**
```bash
cd api-gateway
```

2. **Instalar dependencias:**
```bash
npm install
```

3. **Configurar variables de entorno:**
```bash
cp .env.example .env
```

Editar el archivo `.env` con las configuraciones específicas de tu entorno:

```env
# Servidor
PORT=3000
NODE_ENV=development

# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_change_in_production
JWT_EXPIRES_IN=24h

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ong_sistema
DB_USER=ong_user
DB_PASSWORD=ong_password

# gRPC Services Configuration
USER_SERVICE_HOST=localhost
USER_SERVICE_PORT=50051
INVENTORY_SERVICE_HOST=localhost
INVENTORY_SERVICE_PORT=50052
EVENTS_SERVICE_HOST=localhost
EVENTS_SERVICE_PORT=50053

# Frontend Configuration
FRONTEND_URL=http://localhost:3001

# Organization Configuration
ORGANIZATION_ID=ong-empuje-comunitario

# Kafka Configuration
KAFKA_BROKERS=localhost:9092
```

4. **Verificar servicios dependientes:**
Asegúrate de que los siguientes servicios estén ejecutándose:
- MySQL database (puerto 3306)
- User Service gRPC (puerto 50051)
- Inventory Service gRPC (puerto 50052)
- Events Service gRPC (puerto 50053)
- Apache Kafka (puerto 9092)

5. **Ejecutar en modo desarrollo:**
```bash
npm run dev
```

6. **Ejecutar en producción:**
```bash
npm start
```

### Verificación de Instalación

Una vez iniciado el servidor, puedes verificar que todo funciona correctamente:

1. **Health Check:**
```bash
curl http://localhost:3000/health
```

2. **Documentación API:**
Visita `http://localhost:3000/api-docs` en tu navegador

3. **Información del API:**
```bash
curl http://localhost:3000/api
```

## Endpoints Disponibles

### Información General
- `GET /` - Información del API Gateway
- `GET /health` - Health check
- `GET /api` - Información de endpoints disponibles
- `GET /api-docs` - Documentación Swagger

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/perfil` - Obtener perfil del usuario

### Usuarios (Solo Presidente)
- `GET /api/usuarios` - Listar usuarios
- `POST /api/usuarios` - Crear usuario
- `PUT /api/usuarios/:id` - Actualizar usuario
- `DELETE /api/usuarios/:id` - Eliminar usuario

### Inventario (Presidente, Vocal)
- `GET /api/inventario` - Listar donaciones
- `POST /api/inventario` - Crear donación
- `PUT /api/inventario/:id` - Actualizar donación
- `DELETE /api/inventario/:id` - Eliminar donación

### Eventos
- `GET /api/eventos` - Listar eventos
- `POST /api/eventos` - Crear evento (Presidente, Coordinador)
- `PUT /api/eventos/:id` - Actualizar evento (Presidente, Coordinador)
- `DELETE /api/eventos/:id` - Eliminar evento (Presidente, Coordinador)
- `POST /api/eventos/:id/participantes` - Agregar participante
- `DELETE /api/eventos/:id/participantes/:usuarioId` - Quitar participante

### Red de ONGs
- `GET /api/red/solicitudes-donaciones` - Listar solicitudes externas
- `POST /api/red/solicitudes-donaciones` - Crear solicitud de donaciones
- `GET /api/red/ofertas-donaciones` - Listar ofertas externas
- `POST /api/red/ofertas-donaciones` - Crear oferta de donaciones
- `POST /api/red/transferencias-donaciones` - Transferir donaciones
- `GET /api/red/eventos-externos` - Listar eventos externos
- `POST /api/red/eventos-externos/adhesion` - Adherirse a evento externo

## Tecnologías Utilizadas

### Core
- **Node.js** - Runtime de JavaScript
- **Express.js** - Framework web
- **@grpc/grpc-js** - Cliente gRPC moderno (puro JavaScript)
- **@grpc/proto-loader** - Cargador de archivos .proto

### Seguridad
- **Helmet** - Headers de seguridad
- **CORS** - Cross-Origin Resource Sharing
- **express-rate-limit** - Rate limiting
- **jsonwebtoken** - JWT tokens
- **bcrypt** - Hashing de contraseñas

### Documentación y Testing
- **swagger-ui-express** - Interfaz Swagger
- **swagger-jsdoc** - Generación de documentación
- **jest** - Framework de testing
- **supertest** - Testing de APIs HTTP

### Desarrollo
- **nodemon** - Auto-reload en desarrollo
- **dotenv** - Variables de entorno

## Configuración de gRPC

El API Gateway se conecta a tres servicios gRPC:

- **Usuario Service**: `localhost:50051`
- **Inventario Service**: `localhost:50052`
- **Eventos Service**: `localhost:50053`

### Características gRPC Modernas

- Uso de `@grpc/grpc-js` (puro JavaScript, sin dependencias C++)
- Configuración de keepalive para conexiones estables
- Manejo de credenciales SSL/TLS para producción
- Reconexión automática en caso de fallos

## Testing y Ejemplos de Uso

### Ejecutar Pruebas

**Pruebas unitarias:**
```bash
npm test
```

**Pruebas con cobertura:**
```bash
npm run test:coverage
```

**Pruebas en modo watch:**
```bash
npm run test:watch
```

### Tipos de Pruebas Incluidas
- **Pruebas de Endpoints**: Verificación de todos los endpoints REST
- **Pruebas de Middleware**: Autenticación, autorización y validación
- **Pruebas de Integración**: Comunicación con servicios gRPC
- **Pruebas de Red de ONGs**: Funcionalidades de Kafka
- **Pruebas de Seguridad**: Validación de tokens JWT y permisos

### Colecciones Postman

El proyecto incluye colecciones Postman completas para testing manual:

```bash
# Ejecutar todas las colecciones
npm run test:postman

# Ejecutar colección específica
npx newman run postman/01-Autenticacion.postman_collection.json
npx newman run postman/02-Usuarios.postman_collection.json
npx newman run postman/03-Inventario.postman_collection.json
npx newman run postman/04-Eventos.postman_collection.json
npx newman run postman/05-Red-ONGs.postman_collection.json
```

### Ejemplos de Uso

#### 1. Autenticación
```bash
# Login con usuario Presidente
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identificador": "presidente@ong.com",
    "clave": "password123"
  }'

# Respuesta esperada:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": 1,
    "nombreUsuario": "presidente",
    "nombre": "Juan",
    "apellido": "Pérez",
    "rol": "PRESIDENTE"
  }
}
```

#### 2. Gestión de Usuarios (Solo Presidente)
```bash
# Crear nuevo usuario
curl -X POST http://localhost:3000/api/usuarios \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombreUsuario": "nuevo_voluntario",
    "nombre": "María",
    "apellido": "González",
    "telefono": "123456789",
    "email": "maria@email.com",
    "rol": "VOLUNTARIO"
  }'

# Listar usuarios
curl -X GET http://localhost:3000/api/usuarios \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 3. Gestión de Inventario (Presidente/Vocal)
```bash
# Crear donación
curl -X POST http://localhost:3000/api/inventario \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "categoria": "ALIMENTOS",
    "descripcion": "Arroz integral 1kg",
    "cantidad": 50
  }'

# Listar inventario
curl -X GET http://localhost:3000/api/inventario \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 4. Gestión de Eventos
```bash
# Crear evento (Presidente/Coordinador)
curl -X POST http://localhost:3000/api/eventos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Entrega de Alimentos",
    "descripcion": "Distribución mensual en el barrio",
    "fechaHora": "2024-02-15T10:00:00Z"
  }'

# Agregar participante (Voluntarios pueden auto-asignarse)
curl -X POST http://localhost:3000/api/eventos/1/participantes \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "usuarioId": 2
  }'
```

#### 5. Red de ONGs
```bash
# Solicitar donaciones
curl -X POST http://localhost:3000/api/red/solicitudes-donaciones \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "donaciones": [
      {
        "categoria": "ROPA",
        "descripcion": "Ropa de abrigo para niños"
      }
    ]
  }'

# Ver eventos externos
curl -X GET http://localhost:3000/api/red/eventos-externos \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Testing de Desarrollo

Para desarrollo y debugging, puedes usar los scripts de testing incluidos:

```bash
# Test simple del servidor
node test-server-simple.js

# Test de endpoints específicos
node test-adhesion-simple.js
node test-ofertas-simple.js
node test-baja-solicitudes-simple.js
```

## Variables de Entorno

```env
# Servidor
PORT=3000
NODE_ENV=development

# JWT
JWT_SECRET=your_jwt_secret_change_in_production
JWT_EXPIRES_IN=24h

# Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ong_sistema
DB_USER=ong_user
DB_PASSWORD=ong_password

# Servicios gRPC
USER_SERVICE_HOST=localhost
USER_SERVICE_PORT=50051
INVENTORY_SERVICE_HOST=localhost
INVENTORY_SERVICE_PORT=50052
EVENTS_SERVICE_HOST=localhost
EVENTS_SERVICE_PORT=50053

# CORS
FRONTEND_URL=http://localhost:3001

# Organización
ORGANIZATION_ID=ong-empuje-comunitario

# Kafka (uso futuro)
KAFKA_BROKERS=localhost:9092
```

## Estado de Implementación

### ✅ Completado
- [x] **Tarea 6.1**: Estructura base del API Gateway
- [x] **Tarea 6.2**: Middleware de autenticación y autorización
- [x] **Tarea 6.3**: Endpoints REST para usuarios
- [x] **Tarea 6.4**: Endpoints REST para inventario
- [x] **Tarea 6.5**: Endpoints REST para eventos
- [x] **Tarea 7.1**: Configuración de Kafka
- [x] **Tarea 7.2**: Funcionalidades de solicitud de donaciones
- [x] **Tarea 7.3**: Funcionalidades de transferencia de donaciones
- [x] **Tarea 7.4**: Funcionalidades de oferta de donaciones
- [x] **Tarea 7.5**: Funcionalidades de baja de solicitudes
- [x] **Tarea 7.6**: Funcionalidades de eventos externos
- [x] **Tarea 7.7**: Funcionalidades de adhesión a eventos externos
- [x] **Tarea 8.1**: Documentación Swagger
- [x] **Tarea 8.2**: Pruebas unitarias
- [x] **Tarea 8.3**: Colecciones Postman

### Funcionalidades Implementadas

#### Core Features
- ✅ Autenticación JWT completa
- ✅ Autorización basada en roles
- ✅ CRUD completo de usuarios
- ✅ CRUD completo de inventario
- ✅ CRUD completo de eventos
- ✅ Gestión de participantes en eventos

#### Red de ONGs (Kafka Integration)
- ✅ Solicitudes de donaciones
- ✅ Ofertas de donaciones
- ✅ Transferencias de donaciones
- ✅ Baja de solicitudes
- ✅ Eventos externos
- ✅ Adhesión a eventos externos

#### Testing y Documentación
- ✅ Documentación Swagger completa
- ✅ Pruebas unitarias con Jest
- ✅ Colecciones Postman
- ✅ Scripts de testing de desarrollo

## Notas de Desarrollo

- Se utiliza `app-working.js` como versión funcional simplificada
- Los archivos proto deben estar disponibles en `../grpc/proto/` para la configuración completa
- La configuración `grpc-simple.js` permite desarrollo sin dependencias de archivos proto
- Todos los endpoints están documentados con Swagger/OpenAPI
- Rate limiting configurado para diferentes tipos de endpoints