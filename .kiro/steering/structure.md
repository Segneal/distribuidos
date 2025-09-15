# Project Structure

## Recommended Directory Layout

```
sistema-ong-backend/
├── api-gateway/                 # Node.js Express API Gateway
│   ├── src/
│   │   ├── routes/             # REST endpoint definitions
│   │   ├── middleware/         # Auth, validation, logging
│   │   └── config/             # Gateway configuration
│   ├── package.json
│   └── README.md
├── services/
│   ├── user-service/           # Python gRPC - User management
│   │   ├── src/
│   │   │   ├── grpc/          # gRPC service definitions
│   │   │   ├── models/        # Data models
│   │   │   └── handlers/      # Business logic
│   │   ├── requirements.txt
│   │   └── README.md
│   ├── inventory-service/      # Python gRPC - Donation inventory
│   │   ├── src/
│   │   │   ├── grpc/
│   │   │   ├── models/
│   │   │   └── handlers/
│   │   ├── requirements.txt
│   │   └── README.md
│   └── events-service/         # Python gRPC - Events management
│       ├── src/
│       │   ├── grpc/
│       │   ├── models/
│       │   └── handlers/
│       ├── requirements.txt
│       └── README.md
├── kafka/                      # Kafka configuration and topics
│   ├── topics/                 # Topic definitions
│   └── docker-compose.kafka.yml
├── proto/                      # Shared gRPC protocol definitions
│   ├── user.proto
│   ├── inventory.proto
│   └── events.proto
├── docs/                       # API documentation
│   ├── swagger/
│   └── postman/
├── tests/                      # Integration tests
├── docker-compose.yml          # Full system orchestration
└── README.md                   # Main project documentation
```

## Service Organization

### Microservices Separation
- **user-service**: Authentication, authorization, user CRUD
- **inventory-service**: Donation management, stock control
- **events-service**: Event creation, participation, external events

### Kafka Topics Structure
- `/solicitud-donaciones` - Donation requests
- `/transferencia-donaciones/{orgId}` - Donation transfers
- `/oferta-donaciones` - Donation offers
- `/baja-solicitud-donaciones` - Request cancellations
- `/eventos-solidarios` - External events publication
- `/baja-evento-solidario` - Event cancellations
- `/adhesion-evento/{orgId}` - Event participation

## Code Organization Patterns

### Each Service Should Include
- `README.md` - Service-specific documentation
- `src/grpc/` - gRPC service implementation
- `src/models/` - Data models and validation
- `src/handlers/` - Business logic handlers
- `tests/` - Unit tests for the service

### Naming Conventions
- Services: kebab-case (user-service, inventory-service)
- Python modules: snake_case
- gRPC methods: PascalCase
- Database tables: snake_case
- API endpoints: kebab-case with REST conventions

### Documentation Requirements
- Each module must have a README.md in its root directory
- README must include: purpose, installation steps, usage examples
- Keep documentation updated with code changes