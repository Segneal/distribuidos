# SQL-Driven Testing - Command Examples and Scenarios

## Overview

This document provides practical command examples for different scenarios when using the SQL-driven testing system. Each example includes the command, expected output, and use case explanation.

## Basic Commands

### Generate All Configurations

```bash
# Generate all testing configurations with default settings
python scripts/generate-testing-configs.py --all
```

**Expected Output:**
```
🔄 Starting SQL-driven testing configuration generation...
📊 Extracting test data from database...
✅ Extracted 25 test users, 40 donations, 15 events
🔧 Generating Postman collections...
✅ Generated 5 Postman collections
📝 Updating Swagger examples...
✅ Updated 45 Swagger examples
🚀 Generating Kafka scenarios...
✅ Generated 12 Kafka scenarios
📋 Generation completed successfully in 15.3 seconds
```

**Use Case:** Daily development workflow, complete configuration refresh.

### Generate Specific Configurations

```bash
# Generate only Postman collections
python scripts/generate-testing-configs.py --postman
```

**Expected Output:**
```
🔄 Starting Postman collection generation...
📊 Extracting test data from database...
✅ Extracted test data successfully
🔧 Generating Postman collections...
  ✅ 01-Autenticacion.postman_collection.json
  ✅ 02-Usuarios.postman_collection.json
  ✅ 03-Inventario.postman_collection.json
  ✅ 04-Eventos.postman_collection.json
  ✅ 05-Red-ONGs.postman_collection.json
  ✅ Sistema-ONG-Environment.postman_environment.json
📋 Postman generation completed in 8.2 seconds
```

**Use Case:** Quick Postman update during API development.

```bash
# Generate Postman and Swagger (skip Kafka)
python scripts/generate-testing-configs.py --postman --swagger
```

**Use Case:** Update API testing and documentation, skip inter-NGO scenarios.

## Advanced Options

### Verbose Output

```bash
# Generate with detailed logging
python scripts/generate-testing-configs.py --all --verbose
```

**Expected Output:**
```
🔄 Starting SQL-driven testing configuration generation...
🔍 Loading configuration from environment variables...
🔗 Connecting to database: localhost:3306/ong_sistema
📊 Extracting test data from database...
  🔍 Extracting users by role...
    ✅ Found 4 PRESIDENTE users
    ✅ Found 6 VOCAL users
    ✅ Found 8 COORDINADOR users
    ✅ Found 12 VOLUNTARIO users
  🔍 Extracting inventory by category...
    ✅ ALIMENTOS: 15 items (3 high stock, 5 medium, 4 low, 3 zero)
    ✅ ROPA: 12 items (2 high stock, 4 medium, 3 low, 3 zero)
    ✅ JUGUETES: 8 items (1 high stock, 2 medium, 3 low, 2 zero)
    ✅ UTILES_ESCOLARES: 5 items (0 high stock, 1 medium, 2 low, 2 zero)
  🔍 Extracting events by status...
    ✅ Found 8 future events, 4 past events, 1 current event
  🔍 Extracting network data...
    ✅ Found 4 external organizations, 6 requests, 4 offers
  🔍 Extracting test case mappings...
    ✅ Found 45 test case mappings across 5 categories
🔧 Generating Postman collections...
  🔍 Processing authentication test cases...
    ✅ Generated 8 login scenarios
  🔍 Processing user management test cases...
    ✅ Generated 12 user CRUD scenarios
  🔍 Processing inventory test cases...
    ✅ Generated 15 inventory scenarios
  🔍 Processing event test cases...
    ✅ Generated 10 event scenarios
  🔍 Processing network test cases...
    ✅ Generated 8 inter-NGO scenarios
  ✅ Saved 5 Postman collections to api-gateway/postman/
📝 Updating Swagger examples...
  🔍 Loading existing Swagger configuration...
  🔍 Generating authentication examples...
    ✅ Updated 6 authentication examples
  🔍 Generating user management examples...
    ✅ Updated 8 user examples
  🔍 Generating inventory examples...
    ✅ Updated 12 inventory examples
  🔍 Generating event examples...
    ✅ Updated 7 event examples
  🔍 Generating network examples...
    ✅ Updated 12 network examples
  ✅ Updated Swagger configuration at api-gateway/src/config/swagger.js
🚀 Generating Kafka scenarios...
  🔍 Generating donation request scenarios...
    ✅ Generated 3 solicitud-donaciones scenarios
  🔍 Generating donation offer scenarios...
    ✅ Generated 2 oferta-donaciones scenarios
  🔍 Generating transfer scenarios...
    ✅ Generated 4 transferencia-donaciones scenarios
  🔍 Generating external event scenarios...
    ✅ Generated 3 eventos-solidarios scenarios
  ✅ Saved Kafka scenarios to scripts/sql-driven-testing/kafka_scenarios.json
📋 Generation completed successfully in 18.7 seconds
📊 Summary:
  - Postman collections: 5 generated
  - Swagger examples: 45 updated
  - Kafka scenarios: 12 generated
  - Total test cases: 53 processed
  - Database queries: 12 executed
  - Files modified: 7
```

**Use Case:** Debugging, detailed progress monitoring, troubleshooting.

### Skip Backup

```bash
# Generate without creating backup (faster)
python scripts/generate-testing-configs.py --all --no-backup
```

**Expected Output:**
```
⚠️  Backup creation disabled - existing configurations will be overwritten
🔄 Starting SQL-driven testing configuration generation...
📊 Extracting test data from database...
✅ Extracted test data successfully
🔧 Generating configurations...
✅ All configurations generated successfully in 12.1 seconds
```

**Use Case:** Rapid iteration during development, when backups aren't needed.

### Dry Run

```bash
# Simulate generation without making changes
python scripts/generate-testing-configs.py --all --dry-run
```

**Expected Output:**
```
🔍 DRY RUN MODE - No files will be modified
🔄 Starting SQL-driven testing configuration generation...
📊 Extracting test data from database...
✅ Would extract test data successfully
🔧 Would generate Postman collections...
  📄 Would create: api-gateway/postman/01-Autenticacion.postman_collection.json
  📄 Would create: api-gateway/postman/02-Usuarios.postman_collection.json
  📄 Would create: api-gateway/postman/03-Inventario.postman_collection.json
  📄 Would create: api-gateway/postman/04-Eventos.postman_collection.json
  📄 Would create: api-gateway/postman/05-Red-ONGs.postman_collection.json
  📄 Would update: api-gateway/postman/Sistema-ONG-Environment.postman_environment.json
📝 Would update Swagger examples...
  📄 Would update: api-gateway/src/config/swagger.js
🚀 Would generate Kafka scenarios...
  📄 Would create: scripts/sql-driven-testing/kafka_scenarios.json
📋 Dry run completed - no files were modified
```

**Use Case:** Testing configuration changes, previewing what would be generated.

## Validation Commands

### Validate Data Only

```bash
# Validate test data without generating configurations
python scripts/generate-testing-configs.py --validate-only
```

**Expected Output:**
```
🔍 Validating test data integrity...
✅ Database connection successful
✅ Test users validation passed
  - Found users for all required roles
  - All test users have valid credentials
  - User hierarchy is properly structured
✅ Test inventory validation passed
  - All donation categories are represented
  - Stock levels are properly distributed
  - Foreign key relationships are valid
✅ Test events validation passed
  - Future and past events are present
  - Event participants are properly linked
  - Temporal data is consistent
✅ Test network data validation passed
  - External organizations are properly configured
  - Request/offer data is well-formed
  - JSON fields are valid
✅ Test case mappings validation passed
  - All endpoints have test coverage
  - Test types are properly distributed
  - User and resource references are valid
📋 Data validation completed successfully
```

**Use Case:** Verify test data integrity before generation, troubleshoot data issues.

### Validate with Verbose Details

```bash
# Detailed validation with specific checks
python scripts/generate-testing-configs.py --validate-only --verbose
```

**Expected Output:**
```
🔍 Validating test data integrity...
🔗 Connecting to database: localhost:3306/ong_sistema
✅ Database connection successful

🔍 Validating test users...
  ✅ PRESIDENTE role: 4 users found
    - test_presidente (ID: 1, Active: true)
    - test_presidente_2 (ID: 8, Active: true)
    - test_presidente_inactive (ID: 15, Active: false)
    - test_presidente_edge (ID: 22, Active: true)
  ✅ VOCAL role: 6 users found
  ✅ COORDINADOR role: 8 users found
  ✅ VOLUNTARIO role: 12 users found
  ✅ All users have valid password hashes
  ✅ User hierarchy validation passed

🔍 Validating test inventory...
  ✅ ALIMENTOS category: 15 donations
    - High stock (>50): 3 items
    - Medium stock (10-50): 5 items
    - Low stock (1-9): 4 items
    - Zero stock: 3 items
  ✅ ROPA category: 12 donations
  ✅ JUGUETES category: 8 donations
  ✅ UTILES_ESCOLARES category: 5 donations
  ✅ All donations have valid usuario_alta references

🔍 Validating test events...
  ✅ Future events: 8 found
  ✅ Past events: 4 found
  ✅ Current events: 1 found
  ✅ Event participants: 25 relationships validated
  ✅ All events have valid usuario_alta references

🔍 Validating network data...
  ✅ External organizations: 4 found (3 active, 1 inactive)
  ✅ External requests: 6 found (5 active, 1 inactive)
  ✅ External offers: 4 found (all active)
  ✅ External events: 3 found (2 active, 1 inactive)
  ✅ All JSON fields are valid

🔍 Validating test case mappings...
  ✅ Authentication category: 8 test cases
  ✅ Users category: 12 test cases
  ✅ Inventory category: 15 test cases
  ✅ Events category: 10 test cases
  ✅ Network category: 8 test cases
  ✅ All user references are valid
  ✅ All resource references are valid
  ✅ Expected status codes are reasonable

📋 Comprehensive validation completed successfully
  - Total test users: 30
  - Total donations: 40
  - Total events: 13
  - Total test cases: 53
  - Validation checks: 47 passed, 0 failed
```

**Use Case:** Detailed troubleshooting, comprehensive data analysis.

## Backup Management

### List Available Backups

```bash
# Show all available backups
python scripts/generate-testing-configs.py --list-backups
```

**Expected Output:**
```
📦 Available backups:

2024-01-15_14-30-25 (2 hours ago)
  📄 5 Postman collections
  📄 1 Swagger configuration
  📄 1 Kafka scenarios file
  📄 1 environment file
  💾 Size: 2.3 MB

2024-01-15_10-15-42 (6 hours ago)
  📄 5 Postman collections
  📄 1 Swagger configuration
  📄 1 Kafka scenarios file
  📄 1 environment file
  💾 Size: 2.1 MB

2024-01-14_16-45-18 (1 day ago)
  📄 4 Postman collections
  📄 1 Swagger configuration
  💾 Size: 1.8 MB

📋 Total: 3 backups, 6.2 MB
```

**Use Case:** Review backup history, select backup for restoration.

### Restore from Backup

```bash
# Restore from specific backup
python scripts/generate-testing-configs.py --restore-backup 2024-01-15_14-30-25
```

**Expected Output:**
```
🔄 Restoring from backup: 2024-01-15_14-30-25
📦 Loading backup manifest...
✅ Backup manifest loaded successfully

🔄 Restoring files...
  📄 Restoring api-gateway/postman/01-Autenticacion.postman_collection.json
  📄 Restoring api-gateway/postman/02-Usuarios.postman_collection.json
  📄 Restoring api-gateway/postman/03-Inventario.postman_collection.json
  📄 Restoring api-gateway/postman/04-Eventos.postman_collection.json
  📄 Restoring api-gateway/postman/05-Red-ONGs.postman_collection.json
  📄 Restoring api-gateway/postman/Sistema-ONG-Environment.postman_environment.json
  📄 Restoring api-gateway/src/config/swagger.js
  📄 Restoring scripts/sql-driven-testing/kafka_scenarios.json

✅ Restoration completed successfully
📋 Restored 8 files from backup 2024-01-15_14-30-25
```

**Use Case:** Rollback after problematic generation, recover from errors.

## Status and Monitoring

### Check System Status

```bash
# Get current system status
python scripts/generate-testing-configs.py --status
```

**Expected Output:**
```
📊 SQL-Driven Testing System Status

🔗 Database Connection:
  ✅ Connected to localhost:3306/ong_sistema
  ✅ Test data tables exist
  ✅ Test users: 30 found
  ✅ Test donations: 40 found
  ✅ Test events: 13 found
  ✅ Test mappings: 53 found

📄 Configuration Files:
  ✅ Postman collections: 5 files, last updated 2 hours ago
  ✅ Swagger configuration: exists, last updated 2 hours ago
  ✅ Kafka scenarios: exists, last updated 2 hours ago
  ✅ Environment file: exists, last updated 2 hours ago

📦 Backups:
  ✅ 3 backups available
  ✅ Latest backup: 2024-01-15_14-30-25 (2 hours ago)
  ✅ Backup directory: backups/testing-configs/

🔍 Last Generation:
  ✅ Completed: 2024-01-15 14:30:25
  ✅ Duration: 15.3 seconds
  ✅ Status: Success
  ✅ Configurations: Postman, Swagger, Kafka

📋 System Status: Healthy ✅
```

**Use Case:** Health check, monitoring system state, troubleshooting.

## Testing and Validation

### Run Component Tests

```bash
# Test data extraction
python scripts/sql-driven-testing/test_data_extractor.py
```

**Expected Output:**
```
🧪 Testing SQL Data Extractor...

test_extract_users_by_role ✅
test_extract_inventory_by_category ✅
test_extract_events_by_status ✅
test_extract_network_data ✅
test_extract_test_case_mappings ✅
test_data_integrity_validation ✅
test_get_user_by_id ✅
test_get_donation_by_id ✅

📋 All tests passed (8/8)
```

```bash
# Test Postman generation
python scripts/sql-driven-testing/test_postman_generator.py
```

**Expected Output:**
```
🧪 Testing Postman Generator...

test_generate_auth_collection ✅
test_generate_users_collection ✅
test_generate_inventory_collection ✅
test_generate_events_collection ✅
test_generate_network_collection ✅
test_environment_variables ✅
test_test_scripts_generation ✅

📋 All tests passed (7/7)
```

### Run Comprehensive Test Suite

```bash
# Run all tests
python scripts/sql-driven-testing/test_runner.py
```

**Expected Output:**
```
🧪 SQL-Driven Testing - Comprehensive Test Suite

📊 Unit Tests:
  ✅ Data Extractor: 8/8 tests passed
  ✅ Postman Generator: 7/7 tests passed
  ✅ Swagger Generator: 6/6 tests passed
  ✅ Kafka Generator: 5/5 tests passed
  ✅ Orchestrator: 9/9 tests passed

📊 Integration Tests:
  ✅ SQL to Postman Integration: 4/4 tests passed
  ✅ SQL to Swagger Integration: 3/3 tests passed
  ✅ SQL to Kafka Integration: 3/3 tests passed
  ✅ Cross-Component Consistency: 5/5 tests passed

📊 Validation Tests:
  ✅ Configuration Validators: 6/6 tests passed
  ✅ Data Integrity Validators: 4/4 tests passed

📊 End-to-End Tests:
  ⏭️  Skipped (requires running services)

📋 Test Summary:
  - Total Tests: 60
  - Passed: 60
  - Failed: 0
  - Skipped: 8
  - Success Rate: 100%
  - Duration: 45.2 seconds

✅ All tests passed successfully!
```

**Use Case:** Quality assurance, pre-release validation, CI/CD integration.

## Error Scenarios and Troubleshooting

### Database Connection Error

```bash
python scripts/generate-testing-configs.py --all
```

**Error Output:**
```
❌ Database connection failed
🔍 Error: Can't connect to MySQL server on 'localhost:3306'
💡 Troubleshooting steps:
  1. Check if database server is running
  2. Verify connection parameters in environment variables
  3. Test connection manually: mysql -h localhost -u ong_user -p
  4. Check firewall settings

🔧 Current configuration:
  Host: localhost
  Port: 3306
  Database: ong_sistema
  User: ong_user
```

**Solution:**
```bash
# Check database status
docker-compose ps database

# Start database if not running
docker-compose up -d database

# Test connection
mysql -h localhost -u ong_user -p ong_sistema -e "SELECT 1"
```

### Missing Test Data

```bash
python scripts/generate-testing-configs.py --validate-only
```

**Error Output:**
```
❌ Test data validation failed
🔍 Missing test users:
  - No users found with nombre_usuario starting with 'test_'
  - Required roles missing: PRESIDENTE, VOCAL

💡 Solution:
  Run the test data initialization script:
  mysql -h localhost -u ong_user -p ong_sistema < database/init/02-test-cases.sql
```

**Solution:**
```bash
# Initialize test data
mysql -h localhost -u ong_user -p ong_sistema < database/init/02-test-cases.sql

# Verify test data
python scripts/generate-testing-configs.py --validate-only
```

### Permission Error

```bash
python scripts/generate-testing-configs.py --all
```

**Error Output:**
```
❌ File permission error
🔍 Error: Permission denied writing to 'api-gateway/postman/01-Autenticacion.postman_collection.json'

💡 Solutions:
  1. Check file permissions: ls -la api-gateway/postman/
  2. Fix permissions: chmod 644 api-gateway/postman/*.json
  3. Check directory permissions: chmod 755 api-gateway/postman/
  4. Run with appropriate user permissions
```

**Solution:**
```bash
# Fix permissions
chmod 755 api-gateway/postman/
chmod 644 api-gateway/postman/*.json

# Or create directory if missing
mkdir -p api-gateway/postman
```

## Custom Configuration Examples

### Custom Database Configuration

```bash
# Create custom config file
cat > custom-config.json << EOF
{
  "database": {
    "host": "db.example.com",
    "port": 3306,
    "user": "custom_user",
    "password": "custom_password",
    "database": "custom_db"
  },
  "generation": {
    "postman": true,
    "swagger": false,
    "kafka": true
  }
}
EOF

# Use custom configuration
python scripts/generate-testing-configs.py --all --config custom-config.json
```

### Environment-Specific Generation

```bash
# Development environment
export DB_HOST=localhost
export DB_NAME=ong_sistema_dev
python scripts/generate-testing-configs.py --all --no-backup

# Staging environment
export DB_HOST=staging-db.example.com
export DB_NAME=ong_sistema_staging
python scripts/generate-testing-configs.py --all --verbose

# Production-like testing
export DB_HOST=prod-replica.example.com
export DB_NAME=ong_sistema_prod_replica
python scripts/generate-testing-configs.py --validate-only
```

## CI/CD Integration Examples

### GitHub Actions

```yaml
# .github/workflows/update-testing-configs.yml
name: Update Testing Configurations
on:
  push:
    paths:
      - 'database/init/02-test-cases.sql'
      - 'scripts/sql-driven-testing/**'

jobs:
  update-configs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r scripts/sql-driven-testing/requirements.txt
      - name: Start database
        run: docker-compose up -d database
      - name: Wait for database
        run: sleep 30
      - name: Initialize test data
        run: |
          mysql -h localhost -u root -proot -e "CREATE DATABASE IF NOT EXISTS ong_sistema"
          mysql -h localhost -u root -proot ong_sistema < database/init/01-create-tables.sql
          mysql -h localhost -u root -proot ong_sistema < database/init/02-test-cases.sql
      - name: Generate configurations
        run: python scripts/generate-testing-configs.py --all --no-backup
        env:
          DB_HOST: localhost
          DB_USER: root
          DB_PASSWORD: root
          DB_NAME: ong_sistema
      - name: Commit updated configurations
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add api-gateway/postman/*.json
          git add api-gateway/src/config/swagger.js
          git add scripts/sql-driven-testing/kafka_scenarios.json
          git commit -m "Auto-update testing configurations" || exit 0
          git push
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        DB_HOST = 'localhost'
        DB_USER = 'jenkins'
        DB_PASSWORD = credentials('db-password')
        DB_NAME = 'ong_sistema_test'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r scripts/sql-driven-testing/requirements.txt'
                sh 'docker-compose up -d database'
                sh 'sleep 30'
            }
        }
        
        stage('Initialize Test Data') {
            steps {
                sh 'mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME"'
                sh 'mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < database/init/01-create-tables.sql'
                sh 'mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < database/init/02-test-cases.sql'
            }
        }
        
        stage('Validate Data') {
            steps {
                sh 'python scripts/generate-testing-configs.py --validate-only --verbose'
            }
        }
        
        stage('Generate Configurations') {
            steps {
                sh 'python scripts/generate-testing-configs.py --all --no-backup'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'python scripts/sql-driven-testing/test_runner.py --ci'
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'api-gateway/postman/*.json', fingerprint: true
                archiveArtifacts artifacts: 'scripts/sql-driven-testing/kafka_scenarios.json', fingerprint: true
            }
        }
    }
    
    post {
        always {
            sh 'docker-compose down'
        }
    }
}
```

These command examples provide practical guidance for using the SQL-driven testing system in various scenarios, from basic usage to advanced CI/CD integration.