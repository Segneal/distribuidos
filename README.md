# Sistema ONG Backend - 'Empuje Comunitario'

Sistema backend distribuido para la gestión de ONGs 'Empuje Comunitario' con arquitectura de microservicios, comunicación gRPC y red de colaboración entre organizaciones vía Kafka.

## Arquitectura

Este sistema sigue una arquitectura de microservicios con los siguientes componentes:

- **API Gateway** (Node.js + Express): expone endpoints REST y enruta solicitudes.
- **User Service** (Python + gRPC): administración de usuarios y autenticación.
- **Inventory Service** (Python + gRPC): gestión del inventario de donaciones.
- **Events Service** (Python + gRPC): gestión de eventos solidarios.
- **Base de datos MySQL**: persistencia de la información.
- **Apache Kafka**: mensajería entre ONGs y publicación de eventos.

## Características

### Características principales
- **Gestión de usuarios**: control de acceso por roles (Presidente, Vocal, Coordinador, Voluntario).
- **Inventario de donaciones**: seguimiento por categorías (ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES).
- **Gestión de eventos**: creación de eventos solidarios con asignación de participantes.
- **Red inter-ONG**: solicitud, oferta y transferencia de donaciones entre organizaciones.
- **Participación en eventos externos**: voluntarios pueden sumarse a eventos de otras ONGs.

### Reglas de negocio clave
- Todas las operaciones requieren autorización según el rol.
- Se registran auditorías para operaciones críticas.
- Se prefiere la baja lógica sobre la eliminación física.
- Solo se permiten eventos futuros.
- Se valida el stock antes de transferir donaciones.

## 🚀 Inicio rápido

> **¿Eres nuevo en el proyecto?** 👉 Lee la [**Guía de Inicio Rápido**](GETTING_STARTED.md) para tener todo funcionando en 5 minutos.

### Para personas nuevas

**1. Desplegar en 3 comandos:**
```bash
git clone <repository-url>
cd distribuidos
scripts\deploy.bat    # Windows
# o ./scripts/deploy.sh  # Linux/Mac
```

**2. Verificar que funciona:**
```bash
python quick-start-check.py
```

**3. Acceder al sistema:**
- 🌐 **API**: http://localhost:3000
- 📚 **Documentación**: http://localhost:3000/api-docs
- 🔐 **Login**: `admin@ong.com` / `password123`

### Documentación Completa
- 📖 [**Guía de Inicio Rápido**](GETTING_STARTED.md) - Para nuevos usuarios
- 📋 [**Resumen de Despliegue**](DEPLOYMENT_SUMMARY.md) - Estado del sistema
- 🔧 [**Scripts de Utilidad**](scripts/README.md) - Comandos disponibles

### Configuración para desarrollo

#### Configuración rápida (recomendada)
```bash
# Configurar todo el entorno gRPC
grpc/scripts/setup.bat          # Windows
./grpc/scripts/setup.sh         # Linux/Mac

# Iniciar todos los servicios gRPC
grpc/scripts/start-services.bat # Windows
./grpc/scripts/start-services.sh # Linux/Mac

# Iniciar el API Gateway (en otra terminal)
cd api-gateway && npm install && npm start
```

#### Configuración manual
Cada servicio puede ejecutarse de manera individual durante el desarrollo. Revisa los README específicos de cada servicio para instrucciones detalladas.

## Estructura del proyecto

```
sistema-ong-backend/
├── api-gateway/                 # API Gateway en Node.js y Express
│   ├── src/                    # Código fuente
│   ├── package.json           # Dependencias
│   └── README.md              # Documentación del gateway
├── grpc/                       # Servicios backend gRPC
│   ├── proto/                 # Definiciones Protocol Buffer
│   │   ├── user.proto         # Definiciones del servicio de usuarios
│   │   ├── inventory.proto    # Definiciones del servicio de inventario
│   │   └── events.proto       # Definiciones del servicio de eventos
│   ├── services/              # Microservicios gRPC en Python
│   │   ├── user-service/      # Servicio de gestión de usuarios
│   │   ├── inventory-service/ # Servicio de inventario de donaciones
│   │   └── events-service/    # Servicio de gestión de eventos
│   ├── scripts/               # Scripts de utilidad
│   │   ├── generate-proto.bat # Generar código Python a partir de .proto
│   │   ├── start-services.bat # Iniciar todos los servicios gRPC
│   │   └── setup.bat          # Configuración del entorno
│   └── README.md              # Documentación de los servicios gRPC
├── database/                   # Esquemas y migraciones de base de datos
│   ├── init/                  # Scripts de inicialización
│   ├── migrate.sql            # Script de migración completa
│   └── README.md              # Documentación de la base de datos
├── docs/                       # Documentación de la API
├── tests/                      # Pruebas de integración
├── scripts/                    # Scripts generales de utilidad
├── docker-compose.yml          # Orquestación del sistema completo
└── README.md                   # Este archivo
```

## Endpoints de la API

### Autenticación
- `POST /api/auth/login` - Autentica usuarios.
- `GET /api/auth/perfil` - Obtiene el perfil del usuario autenticado.

### Usuarios (solo Presidente)
- `GET /api/usuarios` - Lista usuarios.
- `POST /api/usuarios` - Crea un usuario.
- `PUT /api/usuarios/:id` - Actualiza un usuario.
- `DELETE /api/usuarios/:id` - Elimina un usuario.

### Inventario (Presidente, Vocal)
- `GET /api/inventario` - Lista donaciones.
- `POST /api/inventario` - Agrega una donación.
- `PUT /api/inventario/:id` - Actualiza una donación.
- `DELETE /api/inventario/:id` - Elimina una donación.

### Eventos (Presidente, Coordinador, Voluntario)
- `GET /api/eventos` - Lista eventos.
- `POST /api/eventos` - Crea un evento.
- `PUT /api/eventos/:id` - Actualiza un evento.
- `DELETE /api/eventos/:id` - Elimina un evento.
- `POST /api/eventos/:id/participantes` - Agrega un participante.
- `DELETE /api/eventos/:id/participantes/:usuarioId` - Quita un participante.

### Red inter-ONG
- `GET /api/red/solicitudes-donaciones` - Lista solicitudes de donaciones.
- `POST /api/red/solicitudes-donaciones` - Crea una solicitud de donaciones.
- `GET /api/red/ofertas-donaciones` - Lista ofertas de donaciones.
- `POST /api/red/ofertas-donaciones` - Crea una oferta de donaciones.
- `POST /api/red/transferencias-donaciones` - Registra una transferencia de donaciones.
- `GET /api/red/eventos-externos` - Lista eventos externos.
- `POST /api/red/eventos-externos/adhesion` - Adhiere a un evento externo.

## Temas de Kafka

- `/solicitud-donaciones` - Solicitudes de donaciones entre ONGs.
- `/transferencia-donaciones/{orgId}` - Transferencias de donaciones.
- `/oferta-donaciones` - Ofertas de donaciones.
- `/baja-solicitud-donaciones` - Bajas de solicitudes.
- `/eventos-solidarios` - Publicación de eventos solidarios.
- `/baja-evento-solidario` - Bajas de eventos.
- `/adhesion-evento/{orgId}` - Adhesiones a eventos.

## Pruebas

Para ejecutar pruebas por servicio:

```bash
# API Gateway
cd api-gateway && npm test

# Servicios gRPC en Python
cd grpc/services/user-service && python -m pytest
cd grpc/services/inventory-service && python -m pytest
cd grpc/services/events-service && python -m pytest
```

## Contribuciones

1. Respeta la estructura del proyecto.
2. Cada servicio debe tener su propio README.md.
3. Todos los endpoints requieren autenticación y autorización.
4. Incluye pruebas unitarias para la funcionalidad nueva.
5. Actualiza la documentación de la API al agregar endpoints.

## Licencia

Este proyecto está licenciado bajo MIT. Consultá el archivo LICENSE para más detalles.

## Soporte

Para consultas o soporte, contactá al equipo de desarrollo.
