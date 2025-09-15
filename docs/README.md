# Documentation

This directory contains all documentation for the Sistema ONG Backend project.

## Structure

- `api/` - API documentation and specifications
- `architecture/` - System architecture diagrams and documentation
- `deployment/` - Deployment guides and configuration
- `development/` - Development setup and guidelines

## API Documentation

The API documentation is automatically generated using Swagger/OpenAPI and is available at:
- Development: http://localhost:3000/api-docs
- Production: [Production URL]/api-docs

## Architecture Overview

The system follows a microservices architecture with:
- API Gateway (Node.js + Express)
- User Service (Python + gRPC)
- Inventory Service (Python + gRPC)
- Events Service (Python + gRPC)
- MySQL Database
- Apache Kafka for messaging

## Getting Started

1. See the main [README.md](../README.md) for quick start instructions
2. Check individual service README files for detailed setup
3. Review the API documentation for endpoint specifications
4. Follow the development guidelines for contributing

## Support

For questions about the documentation or system architecture, please contact the development team.