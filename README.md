# Sistema ONG Backend - "Empuje Comunitario"

Sistema backend distribuido para la gestión de ONGs "Empuje Comunitario" con arquitectura de microservicios, comunicación gRPC y red de colaboración entre organizaciones via Kafka.

## Architecture

This system follows a microservices architecture with the following components:

- **API Gateway** (Node.js + Express): REST API endpoints and request routing
- **User Service** (Python + gRPC): User management and authentication
- **Inventory Service** (Python + gRPC): Donation inventory management
- **Events Service** (Python + gRPC): Solidarity events management
- **MySQL Database**: Data persistence
- **Apache Kafka**: Inter-NGO messaging and event streaming

## Features

### Core Features
- **User Management**: Role-based access control (Presidente, Vocal, Coordinador, Voluntario)
- **Donation Inventory**: Track and manage donations by category (ROPA, ALIMENTOS, JUGUETES, UTILES_ESCOLARES)
- **Event Management**: Create and manage solidarity events with participant assignment
- **Inter-NGO Network**: Request, offer, and transfer donations between organizations
- **External Event Participation**: Allow volunteers to join events from other NGOs

### Key Business Rules
- All operations require proper role-based authorization
- Audit trails are mandatory for all critical operations
- Logical deletion is preferred over physical deletion
- Future events only (no past event creation)
- Stock validation for donation transfers

## 🚀 Inicio Rápido

> **¿Eres nuevo en el proyecto?** 👉 Lee la [**Guía de Inicio Rápido**](GETTING_STARTED.md) para tener todo funcionando en 5 minutos.

### Para Usuarios Nuevos

**1. Desplegar en 3 comandos:**
```bash
git clone <repository-url>
cd sistema-ong-backend
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

### Development Setup

#### Quick Setup (Recommended)
```bash
# Setup complete gRPC environment
grpc/scripts/setup.bat          # Windows
./grpc/scripts/setup.sh         # Linux/Mac

# Start all gRPC services
grpc/scripts/start-services.bat # Windows
./grpc/scripts/start-services.sh # Linux/Mac

# Start API Gateway (in separate terminal)
cd api-gateway && npm install && npm start
```

#### Manual Setup
Each service can be run individually for development. See individual README files in each service directory for specific setup instructions.

## Project Structure

```
sistema-ong-backend/
├── api-gateway/                 # Node.js Express API Gateway
│   ├── src/                    # Source code
│   ├── package.json           # Dependencies
│   └── README.md              # Gateway documentation
├── grpc/                       # gRPC Backend Services
│   ├── proto/                 # Protocol Buffer definitions
│   │   ├── user.proto         # User service definitions
│   │   ├── inventory.proto    # Inventory service definitions
│   │   └── events.proto       # Events service definitions
│   ├── services/              # Python gRPC microservices
│   │   ├── user-service/      # User management service
│   │   ├── inventory-service/ # Donation inventory service
│   │   └── events-service/    # Events management service
│   ├── scripts/               # Utility scripts
│   │   ├── generate-proto.bat # Generate Python code from .proto
│   │   ├── start-services.bat # Start all gRPC services
│   │   └── setup.bat          # Complete environment setup
│   └── README.md              # gRPC services documentation
├── database/                   # Database schemas and migrations
│   ├── init/                  # Initialization scripts
│   ├── migrate.sql            # Complete migration script
│   └── README.md              # Database documentation
├── docs/                       # API documentation
├── tests/                      # Integration tests
├── scripts/                    # General utility scripts
├── docker-compose.yml          # Full system orchestration
└── README.md                   # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User authentication
- `GET /api/auth/perfil` - Get user profile

### Users (Presidente only)
- `GET /api/usuarios` - List all users
- `POST /api/usuarios` - Create new user
- `PUT /api/usuarios/:id` - Update user
- `DELETE /api/usuarios/:id` - Delete user

### Inventory (Presidente, Vocal)
- `GET /api/inventario` - List donations
- `POST /api/inventario` - Add donation
- `PUT /api/inventario/:id` - Update donation
- `DELETE /api/inventario/:id` - Delete donation

### Events (Presidente, Coordinador, Voluntario)
- `GET /api/eventos` - List events
- `POST /api/eventos` - Create event
- `PUT /api/eventos/:id` - Update event
- `DELETE /api/eventos/:id` - Delete event
- `POST /api/eventos/:id/participantes` - Add participant
- `DELETE /api/eventos/:id/participantes/:usuarioId` - Remove participant

### Inter-NGO Network
- `GET /api/red/solicitudes-donaciones` - List donation requests
- `POST /api/red/solicitudes-donaciones` - Create donation request
- `GET /api/red/ofertas-donaciones` - List donation offers
- `POST /api/red/ofertas-donaciones` - Create donation offer
- `POST /api/red/transferencias-donaciones` - Transfer donations
- `GET /api/red/eventos-externos` - List external events
- `POST /api/red/eventos-externos/adhesion` - Join external event

## Kafka Topics

- `/solicitud-donaciones` - Donation requests between NGOs
- `/transferencia-donaciones/{orgId}` - Donation transfers
- `/oferta-donaciones` - Donation offers
- `/baja-solicitud-donaciones` - Request cancellations
- `/eventos-solidarios` - External events publication
- `/baja-evento-solidario` - Event cancellations
- `/adhesion-evento/{orgId}` - Event participation

## Testing

Run tests for individual services:

```bash
# API Gateway
cd api-gateway && npm test

# gRPC Python services
cd grpc/services/user-service && python -m pytest
cd grpc/services/inventory-service && python -m pytest
cd grpc/services/events-service && python -m pytest
```

## Contributing

1. Follow the established project structure
2. Each service must have its own README.md
3. All endpoints require proper authentication and authorization
4. Include unit tests for new functionality
5. Update API documentation when adding new endpoints

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or support, please contact the development team.