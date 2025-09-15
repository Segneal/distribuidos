# Technology Stack

## Architecture
- **Microservices Architecture**: Distributed system with service separation
- **API Gateway**: Node.js with Express for REST endpoints
- **Internal Communication**: gRPC between microservices
- **Message Broker**: Apache Kafka for inter-NGO communication
- **Containerization**: Docker for deployment

## Tech Stack
- **Backend Services**: Python with gRPC
- **API Gateway**: Node.js + Express
- **Message Queue**: Apache Kafka
- **Database**: Not specified in requirements (recommend PostgreSQL)
- **Authentication**: JWT tokens with configurable expiration
- **Password Encryption**: bcrypt or similar secure algorithm

## Development Tools
- **API Documentation**: Swagger/OpenAPI
- **Testing**: Postman collections + unit tests
- **Container Orchestration**: Docker Compose

## Common Commands
```bash
# Docker services
docker-compose up -d kafka
docker-compose up -d api-gateway
docker-compose up -d user-service
docker-compose up -d inventory-service
docker-compose up -d events-service

# Testing
# Run unit tests for each service
python -m pytest tests/
npm test

# API testing
postman run collection.json
```

## Service Communication
- **External API**: REST through API Gateway
- **Internal Services**: gRPC protocol
- **Inter-NGO**: Kafka topics for async messaging

## Security Requirements
- All endpoints require authentication validation
- Role-based authorization on all operations
- Audit logging for all critical operations
- Secure password hashing (bcrypt minimum)