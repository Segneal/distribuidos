# Tests

This directory contains integration tests for the Sistema ONG Backend.

## Structure

- `integration/` - Integration tests between services
- `e2e/` - End-to-end tests for complete workflows
- `postman/` - Postman collections for API testing
- `fixtures/` - Test data and fixtures

## Running Tests

### Integration Tests
```bash
# Run all integration tests
python -m pytest tests/integration/

# Run specific test file
python -m pytest tests/integration/test_user_service_integration.py
```

### API Tests with Postman
```bash
# Install Newman (Postman CLI)
npm install -g newman

# Run Postman collection
newman run tests/postman/sistema-ong-collection.json
```

### End-to-End Tests
```bash
# Run E2E tests (requires running system)
python -m pytest tests/e2e/
```

## Test Data

Test fixtures are located in the `fixtures/` directory and include:
- Sample users with different roles
- Sample donations and inventory items
- Sample events and participants
- Sample inter-NGO messages

## Coverage

To generate test coverage reports:
```bash
# Python services
python -m pytest --cov=src tests/

# Node.js API Gateway
cd api-gateway && npm run test:coverage
```

## Guidelines

1. Write integration tests for service-to-service communication
2. Include API tests for all endpoints
3. Test authentication and authorization scenarios
4. Test error handling and edge cases
5. Keep test data isolated and clean up after tests