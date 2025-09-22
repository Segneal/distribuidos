# SQL-Driven Testing System - Complete Usage Guide

## Overview

The SQL-Driven Testing System is a comprehensive solution that centralizes all test cases in SQL scripts and automatically generates testing configurations for Postman, Swagger documentation, and Kafka inter-NGO messaging scenarios. This guide provides complete instructions for using the system in different scenarios.

## Quick Start

### 1. Initial Setup

```bash
# Install Python dependencies
pip install -r scripts/sql-driven-testing/requirements.txt

# Set up environment variables
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=ong_sistema
export DB_USER=ong_user
export DB_PASSWORD=ong_password

# Or create a .env file in the project root
echo "DB_HOST=localhost" >> .env
echo "DB_PORT=3306" >> .env
echo "DB_NAME=ong_sistema" >> .env
echo "DB_USER=ong_user" >> .env
echo "DB_PASSWORD=ong_password" >> .env
```

### 2. Populate Test Data

```bash
# Initialize database with test cases
docker-compose up -d database
mysql -h localhost -u ong_user -p ong_sistema < database/init/00-create-database.sql
mysql -h localhost -u ong_user -p ong_sistema < database/init/01-create-tables.sql
mysql -h localhost -u ong_user -p ong_sistema < database/init/02-test-cases.sql
```

### 3. Generate All Configurations

```bash
# Generate all testing configurations
python scripts/generate-testing-configs.py --all --verbose
```

### 4. Use Generated Configurations

- **Postman**: Import collections from `api-gateway/postman/`
- **Swagger**: View updated examples at `/api-docs`
- **Kafka**: Use scenarios from `scripts/sql-driven-testing/kafka_scenarios.json`

## Command Line Interface

### Main Script: `generate-testing-configs.py`

The main entry point for the SQL-driven testing system.

#### Basic Commands

```bash
# Generate all configurations (recommended)
python scripts/generate-testing-configs.py --all

# Generate specific configurations
python scripts/generate-testing-configs.py --postman
python scripts/generate-testing-configs.py --swagger
python scripts/generate-testing-configs.py --kafka

# Combine multiple configurations
python scripts/generate-testing-configs.py --postman --swagger
```

#### Advanced Options

```bash
# Skip backup creation (faster execution)
python scripts/generate-testing-configs.py --all --no-backup

# Skip data validation (faster execution, use with caution)
python scripts/generate-testing-configs.py --all --no-validate

# Verbose output for debugging
python scripts/generate-testing-configs.py --all --verbose

# Dry run (simulate without making changes)
python scripts/generate-testing-configs.py --all --dry-run

# Use custom configuration file
python scripts/generate-testing-configs.py --all --config my-config.json
```

#### Validation and Maintenance

```bash
# Validate data without generating configurations
python scripts/generate-testing-configs.py --validate-only

# List available backups
python scripts/generate-testing-configs.py --list-backups

# Restore from specific backup
python scripts/generate-testing-configs.py --restore-backup 2024-01-15_10-30-00

# Check system status
python scripts/generate-testing-configs.py --status
```

### Component-Specific Scripts

#### Data Extraction

```bash
# Test data extraction
python scripts/sql-driven-testing/test_data_extractor.py

# Extract data interactively
python scripts/sql-driven-testing/example_usage.py
```

#### Postman Generation

```bash
# Generate Postman collections
python scripts/sql-driven-testing/example_postman_usage.py

# Test Postman generator
python scripts/sql-driven-testing/test_postman_generator.py
```

#### Swagger Examples

```bash
# Generate Swagger examples
python scripts/sql-driven-testing/example_swagger_usage.py

# Test Swagger generator
python scripts/sql-driven-testing/test_swagger_generator.py
```

#### Kafka Scenarios

```bash
# Generate Kafka scenarios
python scripts/sql-driven-testing/example_kafka_usage.py

# Test Kafka generator
python scripts/sql-driven-testing/test_kafka_generator.py
```

#### Orchestration

```bash
# Run orchestrator directly
python scripts/sql-driven-testing/orchestrator.py

# Test orchestrator
python scripts/sql-driven-testing/test_orchestrator.py
```

## Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_HOST` | Database host | `localhost` | Yes |
| `DB_PORT` | Database port | `3306` | Yes |
| `DB_NAME` | Database name | `ong_sistema` | Yes |
| `DB_USER` | Database user | `ong_user` | Yes |
| `DB_PASSWORD` | Database password | - | Yes |
| `BACKUP_ENABLED` | Enable automatic backups | `true` | No |
| `VALIDATION_ENABLED` | Enable data validation | `true` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

### Configuration File

Create a JSON configuration file for custom settings:

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "user": "ong_user",
    "password": "ong_password",
    "database": "ong_sistema"
  },
  "generation": {
    "postman": true,
    "swagger": true,
    "kafka": true,
    "backup": true,
    "validate": true
  },
  "output": {
    "postman_path": "api-gateway/postman",
    "swagger_path": "api-gateway/src/config/swagger.js",
    "kafka_scenarios_file": "scripts/sql-driven-testing/kafka_scenarios.json",
    "save_extracted_data": true,
    "extracted_data_file": "extracted_test_data.json",
    "report_file": "generation_report.json"
  },
  "backup": {
    "enabled": true,
    "retention_days": 30,
    "directory": "backups/testing-configs"
  },
  "validation": {
    "enabled": true,
    "strict_mode": false,
    "check_foreign_keys": true,
    "validate_json_fields": true
  },
  "logging": {
    "level": "INFO",
    "file": "logs/sql-driven-testing.log",
    "console": true
  }
}
```

Use the configuration file:

```bash
python scripts/generate-testing-configs.py --all --config custom-config.json
```

## Usage Scenarios

### Scenario 1: Daily Development Workflow

**Situation**: You're actively developing and need up-to-date test configurations.

```bash
# Quick update without backup (faster)
python scripts/generate-testing-configs.py --postman --no-backup

# Import updated Postman collections
# Run tests in Postman to verify API changes
```

**Best for**: Frequent updates during active development.

### Scenario 2: Pre-Release Testing

**Situation**: Preparing for a release and need comprehensive testing configurations.

```bash
# Full generation with validation and backup
python scripts/generate-testing-configs.py --all --verbose

# Run comprehensive validation
python scripts/sql-driven-testing/test_runner.py

# Execute end-to-end tests
python scripts/sql-driven-testing/test_end_to_end.py
```

**Best for**: Release preparation and quality assurance.

### Scenario 3: New Team Member Onboarding

**Situation**: New developer needs complete testing setup.

```bash
# Generate all configurations with documentation
python scripts/generate-testing-configs.py --all --verbose

# Validate setup
python scripts/generate-testing-configs.py --validate-only

# Run example scripts to understand the system
python scripts/sql-driven-testing/example_usage.py
python scripts/sql-driven-testing/example_postman_usage.py
```

**Best for**: Team onboarding and training.

### Scenario 4: CI/CD Pipeline Integration

**Situation**: Automated testing in continuous integration.

```bash
# CI-friendly generation (no interactive prompts)
python scripts/generate-testing-configs.py --all --no-backup --ci

# Run validation tests
python scripts/sql-driven-testing/test_runner.py --ci

# Generate machine-readable reports
python scripts/generate-testing-configs.py --all --report-format json
```

**Best for**: Automated pipelines and continuous integration.

### Scenario 5: Debugging and Troubleshooting

**Situation**: Something isn't working and you need to debug.

```bash
# Enable verbose logging
python scripts/generate-testing-configs.py --all --verbose --debug

# Validate data integrity
python scripts/generate-testing-configs.py --validate-only --verbose

# Test individual components
python scripts/sql-driven-testing/test_data_extractor.py
python scripts/sql-driven-testing/test_postman_generator.py

# Check system status
python scripts/generate-testing-configs.py --status
```

**Best for**: Troubleshooting and debugging issues.

### Scenario 6: Selective Updates

**Situation**: You only need to update specific configurations.

```bash
# Update only Postman collections
python scripts/generate-testing-configs.py --postman

# Update only Swagger documentation
python scripts/generate-testing-configs.py --swagger

# Update only Kafka scenarios
python scripts/generate-testing-configs.py --kafka

# Update Postman and Swagger (skip Kafka)
python scripts/generate-testing-configs.py --postman --swagger
```

**Best for**: Targeted updates and specific use cases.

## Working with Generated Configurations

### Postman Collections

#### Import Process

1. **Open Postman**
2. **Import Collections**:
   - Click "Import" button
   - Select all `.postman_collection.json` files from `api-gateway/postman/`
   - Import the environment file: `Sistema-ONG-Environment.postman_environment.json`

3. **Select Environment**:
   - Choose "Sistema-ONG-Environment" from the environment dropdown

#### Collection Structure

- **01-Autenticacion**: Login tests for all user roles
- **02-Usuarios**: User management operations
- **03-Inventario**: Donation inventory operations
- **04-Eventos**: Event management operations
- **05-Red-ONGs**: Inter-NGO communication

#### Execution Order

1. **Start with Authentication** to get tokens
2. **Run other collections** in any order
3. **Check environment variables** are populated correctly

#### Test Validation

Each request includes test scripts that:
- Validate HTTP status codes
- Check response structure
- Store tokens and IDs for subsequent requests
- Verify business logic

### Swagger Documentation

#### Accessing Updated Examples

1. **Start the API Gateway**:
   ```bash
   cd api-gateway
   npm start
   ```

2. **Open Swagger UI**:
   - Navigate to `http://localhost:3000/api-docs`
   - All examples now use real data from your database

#### Example Categories

- **Authentication**: Login examples for all user roles
- **Users**: CRUD operations with real user data
- **Inventory**: Donation management with actual stock levels
- **Events**: Event operations with future/past scenarios
- **Network**: Inter-NGO communication examples

### Kafka Test Scenarios

#### Generated Scenarios File

The system generates `scripts/sql-driven-testing/kafka_scenarios.json` with:

```json
{
  "solicitud-donaciones": [
    {
      "scenario_name": "Solicitud de Alimentos - Caso Exitoso",
      "topic": "solicitud-donaciones",
      "message": { /* real data from SQL */ },
      "expected_external_response": true,
      "test_assertions": [...]
    }
  ],
  "transferencia-donaciones": [...],
  "eventos-solidarios": [...]
}
```

#### Using Kafka Scenarios

1. **Load scenarios in your Kafka testing tool**
2. **Publish messages** to the specified topics
3. **Validate responses** against the assertions
4. **Check pre/post conditions** as specified

## Integration with Development Workflow

### Git Integration

```bash
# Add generated configurations to version control
git add api-gateway/postman/*.json
git add api-gateway/src/config/swagger.js
git add scripts/sql-driven-testing/kafka_scenarios.json

# Commit with descriptive message
git commit -m "Update testing configurations from SQL test cases"
```

### Docker Integration

```bash
# Generate configurations in Docker environment
docker-compose exec api-gateway python /app/scripts/generate-testing-configs.py --all

# Or run as a separate service
docker-compose run --rm testing-generator python scripts/generate-testing-configs.py --all
```

### IDE Integration

Most IDEs can be configured to run the generation as a build task:

**VS Code tasks.json**:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate Testing Configs",
      "type": "shell",
      "command": "python",
      "args": ["scripts/generate-testing-configs.py", "--all"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    }
  ]
}
```

## Monitoring and Maintenance

### Regular Maintenance Tasks

#### Weekly
```bash
# Update test configurations
python scripts/generate-testing-configs.py --all

# Run comprehensive validation
python scripts/sql-driven-testing/test_runner.py

# Clean old backups (optional)
python scripts/generate-testing-configs.py --cleanup-backups --older-than 30
```

#### Monthly
```bash
# Review and update test cases in SQL
# Check for new endpoints that need test coverage
# Update documentation if needed

# Full system validation
python scripts/generate-testing-configs.py --validate-only --verbose
python scripts/sql-driven-testing/test_runner.py --comprehensive
```

### Monitoring System Health

#### Check System Status
```bash
python scripts/generate-testing-configs.py --status
```

This provides:
- Database connectivity status
- Last generation timestamp
- Configuration file status
- Backup availability
- Validation results summary

#### Performance Monitoring

```bash
# Time the generation process
time python scripts/generate-testing-configs.py --all

# Monitor resource usage
python scripts/generate-testing-configs.py --all --profile
```

### Backup Management

#### Automatic Backups

Backups are created automatically before each generation:
- **Location**: `backups/testing-configs/backup_TIMESTAMP/`
- **Contents**: All existing configurations
- **Manifest**: JSON file describing backup contents

#### Manual Backup Operations

```bash
# List available backups
python scripts/generate-testing-configs.py --list-backups

# Create manual backup
python scripts/generate-testing-configs.py --create-backup

# Restore from backup
python scripts/generate-testing-configs.py --restore-backup 2024-01-15_10-30-00

# Clean old backups
python scripts/generate-testing-configs.py --cleanup-backups --older-than 30
```

## Performance Optimization

### Faster Generation

```bash
# Skip backup for faster execution
python scripts/generate-testing-configs.py --all --no-backup

# Skip validation for faster execution (use with caution)
python scripts/generate-testing-configs.py --all --no-validate

# Generate only what you need
python scripts/generate-testing-configs.py --postman  # Fastest single option
```

### Database Optimization

```sql
-- Add indexes for faster data extraction
CREATE INDEX idx_usuarios_test ON usuarios(nombre_usuario);
CREATE INDEX idx_donaciones_test ON donaciones(usuario_alta);
CREATE INDEX idx_eventos_test ON eventos(usuario_alta);
CREATE INDEX idx_test_mapping_endpoint ON test_case_mapping(endpoint, method);
```

### Caching

The system includes intelligent caching:
- **Data extraction results** are cached during generation
- **Configuration templates** are cached for reuse
- **Validation results** are cached to avoid re-validation

## Security Considerations

### Database Access

- Use dedicated database user with minimal required permissions
- Store database credentials in environment variables, not in code
- Use connection pooling for better security and performance

### Generated Configurations

- Review generated configurations before committing to version control
- Ensure no sensitive data (real passwords, tokens) is included
- Use test-specific credentials that don't work in production

### Backup Security

- Backups may contain sensitive configuration data
- Store backups in secure locations
- Implement backup retention policies
- Consider encrypting backup files

## Extending the System

### Adding New Generators

1. **Create generator class** following existing patterns
2. **Add to orchestrator** configuration
3. **Create tests** for the new generator
4. **Update documentation**

### Adding New Test Categories

1. **Add test cases** to SQL scripts
2. **Update test case mappings** with new category
3. **Modify generators** to handle new category
4. **Add validation** for new category

### Custom Validation Rules

1. **Create validator class** in `validators.py`
2. **Add to comprehensive validation**
3. **Write tests** for new validator
4. **Document validation rules**

This comprehensive usage guide should help you effectively use the SQL-driven testing system in various scenarios and workflows. The system is designed to be flexible and adaptable to different development practices while maintaining consistency and reliability.