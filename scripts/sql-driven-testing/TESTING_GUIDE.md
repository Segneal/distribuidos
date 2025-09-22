# SQL-Driven Testing - Validation and Testing System Guide

## Overview

The SQL-Driven Testing system includes a comprehensive validation and testing framework that ensures the quality and correctness of all generated configurations. This guide explains how to use the testing system and interpret the results.

## Testing Architecture

The testing system is organized into four main categories:

### 1. Unit Tests
Test individual components in isolation:
- **Data Extractor Tests** (`test_data_extractor.py`) - Validates SQL data extraction logic
- **Postman Generator Tests** (`test_postman_generator.py`) - Tests Postman collection generation
- **Swagger Generator Tests** (`test_swagger_generator.py`) - Tests Swagger example generation
- **Kafka Generator Tests** (`test_kafka_generator.py`) - Tests Kafka scenario generation
- **Orchestrator Tests** (`test_orchestrator.py`) - Tests the main orchestration logic

### 2. Integration Tests
Test component interactions and data flow:
- **SQL to Configuration Integration** (`test_integration.py`) - Tests complete data flow
- **Cross-Component Validation** - Ensures data consistency across generators
- **End-to-End Pipeline Testing** - Validates the complete generation pipeline

### 3. End-to-End Tests
Test against real services:
- **API Integration Tests** (`test_end_to_end.py`) - Execute Postman collections against real API
- **Database Integration Tests** - Validate test data exists in database
- **Kafka Integration Tests** - Test message publishing to real Kafka

### 4. Validation Tests
Comprehensive configuration validation:
- **Configuration Validators** (`validators.py`) - Validate generated configurations
- **Cross-Configuration Consistency** - Ensure consistency between Postman, Swagger, and Kafka
- **Coverage Analysis** - Analyze test coverage and completeness

## Running Tests

### Quick Test Run
```bash
# Run all basic tests
python scripts/sql-driven-testing/run_tests.py
```

### Comprehensive Test Run
```bash
# Run full test suite with detailed reporting
python scripts/sql-driven-testing/test_runner.py
```

### Specific Test Categories
```bash
# Run only unit tests
python scripts/sql-driven-testing/test_runner.py --categories unit

# Run unit and integration tests
python scripts/sql-driven-testing/test_runner.py --categories unit integration

# Run in CI mode (excludes end-to-end tests)
python scripts/sql-driven-testing/test_runner.py --ci
```

### Individual Component Tests
```bash
# Test specific components
python scripts/sql-driven-testing/test_data_extractor.py
python scripts/sql-driven-testing/test_postman_generator.py
python scripts/sql-driven-testing/test_swagger_generator.py
python scripts/sql-driven-testing/test_kafka_generator.py
python scripts/sql-driven-testing/test_orchestrator.py
```

## Test Results and Reporting

### Test Output Structure
```
📊 TEST SUMMARY
==================================================
Unit Tests: 4/5 passed
  ✅ Data Extractor
  ✅ Postman Generator
  ✅ Swagger Generator
  ❌ Kafka Generator
  ✅ Orchestrator
Validation Tests: ✅
Integration Tests: ✅

Overall: 6/7 test categories passed
```

### Detailed Reports
Test results are saved to JSON files in the `test_results/` directory:
```json
{
  "start_time": "2024-01-15T10:30:00",
  "end_time": "2024-01-15T10:32:30",
  "total_duration": 150.5,
  "summary": {
    "total_tests": 25,
    "passed_tests": 23,
    "failed_tests": 2,
    "skipped_tests": 0,
    "success_rate": 92.0
  },
  "categories": {
    "unit": { /* detailed results */ },
    "integration": { /* detailed results */ },
    "validation": { /* detailed results */ }
  }
}
```

## Validation System

### Configuration Validators

#### Postman Validator
Validates Postman collections for:
- ✅ Required collections exist
- ✅ Request structure is correct
- ✅ Test scripts are present
- ✅ Variables are properly used
- ✅ Authentication methods are configured

#### Swagger Validator
Validates Swagger documentation for:
- ✅ Examples are present and valid
- ✅ Required categories are covered
- ✅ Response structures match expectations
- ✅ Real data is used in examples

#### Kafka Validator
Validates Kafka scenarios for:
- ✅ Required topics are covered
- ✅ Message structure is correct
- ✅ Pre/post conditions are defined
- ✅ Test assertions are meaningful

#### Integration Validator
Validates cross-configuration consistency:
- ✅ User data consistency across all configurations
- ✅ Endpoint coverage between Postman and Swagger
- ✅ Test data alignment across generators
- ✅ Overall coverage analysis

### Running Validation
```bash
# Run comprehensive validation
python -c "
from validators import run_comprehensive_validation
result = run_comprehensive_validation(
    postman_path='api-gateway/postman',
    swagger_path='api-gateway/src/config/swagger.js',
    kafka_scenarios=kafka_scenarios,
    extracted_data=extracted_data
)
print(f'Validation Result: {result[\"overall_valid\"]}')
"
```

## Test Data Requirements

### Database Test Data
The testing system requires specific test data in the database:
- Test users with usernames starting with `test_`
- Test donations with `usuario_alta` starting with `test_`
- Test events created by test users
- Test case mappings in `test_case_mapping` table

### Mock Data Structure
For unit tests, mock data should include:
```python
{
    'users': {
        'PRESIDENTE': [{'id': 1, 'nombre_usuario': 'test_presidente', ...}],
        'VOCAL': [{'id': 2, 'nombre_usuario': 'test_vocal', ...}],
        # ... other roles
    },
    'inventory': {
        'ALIMENTOS': {
            'high_stock': [...],
            'medium_stock': [...],
            'low_stock': [...],
            'zero_stock': [...],
            'all': [...]
        },
        # ... other categories
    },
    'events': {
        'future': [...],
        'past': [...],
        'current': [...],
        'all': [...]
    },
    'network': {
        'external_requests': [...],
        'external_offers': [...],
        'external_events': [...],
        # ... other network data
    },
    'test_mappings': [
        {'endpoint': '/api/auth/login', 'test_category': 'authentication', ...},
        # ... other mappings
    ]
}
```

## Continuous Integration

### CI Configuration
For CI/CD pipelines, use the CI mode:
```bash
# In CI environment
python scripts/sql-driven-testing/test_runner.py --ci
```

This mode:
- Skips end-to-end tests that require external services
- Focuses on unit, integration, and validation tests
- Provides clear exit codes for CI systems
- Generates machine-readable reports

### Environment Variables
Set these environment variables for testing:
```bash
# Database connection (for end-to-end tests)
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=ong_sistema
export DB_USER=test_user
export DB_PASSWORD=test_password

# Enable Kafka tests (optional)
export KAFKA_TESTS_ENABLED=true

# Test output directory
export TEST_OUTPUT_DIR=test_results
```

## Troubleshooting

### Common Issues

#### "No test users found in database"
- Ensure test data is populated in the database
- Run the SQL scripts in `database/init/02-test-cases.sql`
- Check that users have `nombre_usuario` starting with `test_`

#### "Postman collection generation failed"
- Check that test data includes all required fields
- Verify that `password_plain` field exists for test users
- Ensure inventory data has proper structure

#### "Swagger examples validation failed"
- Check that Swagger config file exists
- Verify that examples are properly formatted
- Ensure real data is being used in examples

#### "Kafka scenarios validation failed"
- Verify message structure includes required fields
- Check that timestamps are in ISO format
- Ensure organization IDs follow proper format

#### "Integration tests failed"
- Check data consistency across components
- Verify that all generators use the same data source
- Ensure proper error handling for missing data

### Debug Mode
Enable verbose logging for debugging:
```bash
python scripts/sql-driven-testing/test_runner.py --verbose
```

### Manual Validation
For manual validation of specific components:
```python
# Test data extraction
from data_extractor import SQLDataExtractor
extractor = SQLDataExtractor(db_config)
data = extractor.extract_test_data()

# Test Postman generation
from postman_generator import PostmanGenerator
generator = PostmanGenerator(data)
collections = generator.generate_all_collections()

# Test validation
from validators import run_comprehensive_validation
result = run_comprehensive_validation(...)
```

## Best Practices

### Writing Tests
1. **Use realistic test data** - Mirror production data structure
2. **Test error conditions** - Include negative test cases
3. **Validate data consistency** - Ensure cross-component consistency
4. **Mock external dependencies** - Use mocks for database/API calls
5. **Clear assertions** - Write descriptive test assertions

### Maintaining Tests
1. **Update tests with code changes** - Keep tests synchronized
2. **Regular test data refresh** - Update test data periodically
3. **Monitor test performance** - Keep tests fast and reliable
4. **Document test scenarios** - Explain complex test cases

### CI/CD Integration
1. **Fast feedback** - Run unit tests first
2. **Parallel execution** - Run test categories in parallel
3. **Clear reporting** - Provide actionable test reports
4. **Fail fast** - Stop on critical failures

## Extending the Testing System

### Adding New Tests
1. Create test file following naming convention: `test_<component>.py`
2. Inherit from `unittest.TestCase`
3. Add to appropriate test category in `test_runner.py`
4. Update documentation

### Adding New Validators
1. Create validator class in `validators.py`
2. Implement validation logic with clear error messages
3. Add to comprehensive validation function
4. Write unit tests for the validator

### Custom Test Scenarios
1. Create scenario data following existing patterns
2. Add scenario to appropriate generator tests
3. Validate scenario in integration tests
4. Document scenario purpose and expected results

## Support and Maintenance

For issues with the testing system:
1. Check this guide for common solutions
2. Review test logs for specific error messages
3. Validate test data structure and completeness
4. Ensure all dependencies are properly installed
5. Check environment configuration

The testing system is designed to be comprehensive yet maintainable. Regular execution helps ensure the quality and reliability of the SQL-driven testing framework.