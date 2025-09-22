# SQL-Driven Testing System

Sistema ONG - SQL Driven Testing

## Overview

The SQL-Driven Testing System centralizes all test cases in SQL scripts and automatically generates testing configurations for Postman, Swagger, and Kafka scenarios. This system eliminates the need to maintain multiple complex data generation systems by using the populated SQL database as the single source of truth for all testing data.

## 📚 Complete Documentation

This README provides a technical overview of the system. For comprehensive documentation, see:

- **[📋 Documentation Index](DOCUMENTATION_INDEX.md)** - Complete guide to all documentation
- **[🗃️ SQL Test Cases Guide](SQL_TEST_CASES_GUIDE.md)** - How to structure and add test cases in SQL
- **[⚙️ System Usage Guide](SYSTEM_USAGE_GUIDE.md)** - Complete usage guide for all scenarios
- **[💻 Command Examples](COMMAND_EXAMPLES.md)** - Practical command examples and scenarios
- **[🔧 Troubleshooting Guide](TROUBLESHOOTING.md)** - Solutions for common problems
- **[🧪 Testing Guide](TESTING_GUIDE.md)** - Validation and testing framework
- **[📖 Usage Reference](USAGE.md)** - Command line reference

## Quick Start

```bash
# 1. Install dependencies
pip install -r scripts/sql-driven-testing/requirements.txt

# 2. Set up environment
export DB_HOST=localhost DB_PORT=3306 DB_NAME=ong_sistema DB_USER=ong_user DB_PASSWORD=ong_password

# 3. Initialize test data
mysql -h localhost -u ong_user -p ong_sistema < database/init/02-test-cases.sql

# 4. Generate all configurations
python scripts/generate-testing-configs.py --all --verbose
```

For detailed setup instructions, see the [System Usage Guide](SYSTEM_USAGE_GUIDE.md).

### Components

- **SQL Data Extractor**: Extracts test data from the populated SQL database
- **Postman Generator**: Generates Postman collections with real data from SQL
- **Swagger Generator**: Updates Swagger documentation examples with real data (planned)
- **Kafka Generator**: Generates inter-NGO messaging test scenarios (planned)
- **Testing Orchestrator**: Coordinates the entire generation process (planned)

## Features

- **User Data Extraction**: Extracts test users organized by role (PRESIDENTE, VOCAL, COORDINADOR, VOLUNTARIO)
- **Inventory Data Extraction**: Extracts donations organized by category and stock levels
- **Event Data Extraction**: Extracts events organized by temporal status (future, past, current)
- **Network Data Extraction**: Extracts inter-NGO communication data (requests, offers, transfers, events)
- **Test Case Mappings**: Extracts endpoint test case mappings with expected results
- **Data Integrity Validation**: Validates foreign key relationships and data completeness
- **Audit Data**: Extracts stock change audit trails for testing traceability

## Installation

1. Install Python dependencies:
```bash
pip install -r scripts/sql-driven-testing/requirements.txt
```

2. Set up environment variables (or use .env file):
```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=ong_sistema
export DB_USER=ong_user
export DB_PASSWORD=ong_password
```

## Usage

### Basic Usage

```python
from scripts.sql_driven_testing import SQLDataExtractor, create_db_config_from_env

# Create database configuration from environment variables
db_config = create_db_config_from_env()

# Create extractor instance
extractor = SQLDataExtractor(db_config)

try:
    # Extract all test data
    test_data = extractor.extract_test_data()
    
    # Access specific data
    users = test_data['users']
    inventory = test_data['inventory']
    events = test_data['events']
    network = test_data['network']
    test_mappings = test_data['test_mappings']
    
    print(f"Extracted {len(test_mappings)} test cases")
    
finally:
    extractor.disconnect()
```

### Advanced Usage

```python
# Extract specific data types
extractor.connect()

# Get users by role
users_by_role = extractor.extract_users_by_role()
presidente = users_by_role['PRESIDENTE'][0]

# Get inventory by category and stock level
inventory = extractor.extract_inventory_by_category()
high_stock_food = inventory['ALIMENTOS']['high_stock']
zero_stock_items = []
for category in inventory.values():
    zero_stock_items.extend(category['zero_stock'])

# Get events by status
events = extractor.extract_events_by_status()
future_events = events['future']
past_events = events['past']

# Get test cases for specific endpoints
auth_test_cases = extractor.get_test_cases_by_category('authentication')
inventory_test_cases = extractor.get_test_cases_by_endpoint('/api/inventario/donaciones')

extractor.disconnect()
```

### Utility Methods

```python
# Get specific entities by ID
user = extractor.get_user_by_id(1)  # Get user with ID 1
donation = extractor.get_donation_by_id(101)  # Get donation with ID 101

# Filter test cases
auth_cases = extractor.get_test_cases_by_category('authentication')
login_cases = extractor.get_test_cases_by_endpoint('/api/auth/login')
```

## Data Structure

The extracted data follows this structure:

```python
{
    'users': {
        'PRESIDENTE': [user_objects],
        'VOCAL': [user_objects],
        'COORDINADOR': [user_objects],
        'VOLUNTARIO': [user_objects]
    },
    'inventory': {
        'ALIMENTOS': {
            'high_stock': [donations with cantidad > 50],
            'medium_stock': [donations with 10 <= cantidad <= 50],
            'low_stock': [donations with 1 <= cantidad < 10],
            'zero_stock': [donations with cantidad = 0],
            'all': [all donations in category]
        },
        # ... other categories
    },
    'events': {
        'future': [future_events],
        'past': [past_events],
        'current': [current_events],
        'all': [all_events]
    },
    'network': {
        'external_requests': [external_donation_requests],
        'external_offers': [external_donation_offers],
        'external_events': [external_events],
        'own_requests': [own_donation_requests],
        'own_offers': [own_donation_offers],
        'transfers_sent': [sent_transfers],
        'transfers_received': [received_transfers],
        'event_adhesions': [event_adhesions]
    },
    'test_mappings': [test_case_mappings],
    'audit_data': {
        'stock_changes': [audit_records]
    }
}
```

## Test Case Mapping Structure

Each test case mapping contains:

```python
{
    'endpoint': '/api/auth/login',
    'method': 'POST',
    'test_type': 'success',  # success, error, validation, authorization, edge_case
    'user_id': 1,  # Reference to test user
    'resource_id': None,  # Reference to test resource (donation, event, etc.)
    'description': 'Login exitoso - Presidente',
    'expected_status': 200,
    'request_body': {'nombreUsuario': 'test_presidente', 'clave': 'test123'},
    'expected_response_fields': ['token', 'usuario', 'rol'],
    'test_category': 'authentication'  # authentication, users, inventory, events, network
}
```

## Data Integrity Validation

The extractor automatically validates:

- **Completeness**: All required data categories are present
- **User Coverage**: At least one user per role exists
- **Category Coverage**: All donation categories are present
- **Foreign Keys**: Event participants reference valid users
- **Test Mappings**: Test cases reference valid users and resources

## Error Handling

The extractor includes comprehensive error handling:

- Database connection errors
- SQL execution errors
- Data integrity validation errors
- JSON parsing errors for stored JSON fields

## Testing

Run the test suite to verify functionality:

```bash
python scripts/sql-driven-testing/test_data_extractor.py
```

The test suite includes:
- User data extraction tests
- Inventory data extraction tests
- Test case mapping extraction tests
- Data integrity validation tests
- Utility method tests

## Postman Generator

The Postman Generator creates complete Postman collections using real data extracted from the SQL database.

### Features

- **Automatic Collection Generation**: Creates 5 complete Postman collections (Auth, Users, Inventory, Events, Network)
- **Real Data Integration**: Uses actual IDs, usernames, and data from the populated database
- **Role-Based Testing**: Generates tests for all user roles with proper authorization scenarios
- **Environment Variables**: Updates Postman environment with real IDs and tokens
- **Test Validation**: Includes comprehensive test scripts that validate responses against known SQL data
- **Backup Management**: Automatically backs up existing collections before updating

### Usage

```python
from postman_generator import PostmanGenerator
from data_extractor import SQLDataExtractor, create_db_config_from_env

# Extract data from SQL
db_config = create_db_config_from_env()
extractor = SQLDataExtractor(db_config)
test_data = extractor.extract_test_data()
extractor.disconnect()

# Generate Postman collections
generator = PostmanGenerator(test_data)
results = generator.generate_all_collections()

print(f"Generated {len(results)} collections:")
for filename, filepath in results.items():
    print(f"  - {filename}")
```

### Generated Collections

1. **01-Autenticacion.postman_collection.json**
   - Login tests for all user roles with real credentials
   - Profile access and logout tests
   - Error scenarios with invalid credentials

2. **02-Usuarios.postman_collection.json**
   - User CRUD operations with real user IDs
   - Authorization testing (role-based access control)
   - Error scenarios (non-existent users, insufficient permissions)

3. **03-Inventario.postman_collection.json**
   - Donation CRUD operations with real donation IDs
   - Category filtering with actual categories
   - Stock level testing with real quantities

4. **04-Eventos.postman_collection.json**
   - Event CRUD operations with real event IDs
   - Participation management with actual user IDs
   - Date validation with future/past events

5. **05-Red-ONGs.postman_collection.json**
   - Inter-NGO communication with real organization data
   - Donation requests, offers, and transfers
   - External event participation

### Environment Variables

The generator updates the Postman environment with:

- **Role-specific tokens**: `presidente_token`, `vocal_token`, `coordinador_token`, `voluntario_token`
- **Real user IDs**: `presidente_id`, `vocal_id`, `coordinador_id`, `voluntario_id`
- **Sample resource IDs**: `sample_donation_id`, `sample_event_id`
- **Dynamic IDs**: `created_user_id`, `created_donation_id`, `created_event_id`

### Test Validation Scripts

Each request includes comprehensive test scripts that:

- Validate HTTP status codes
- Check response structure and required fields
- Verify data matches SQL database values
- Store tokens and IDs for subsequent requests
- Test business logic and authorization rules

### Quick Start

1. **Run the example script**:
```bash
python scripts/sql-driven-testing/example_postman_usage.py
```

2. **Import to Postman**:
   - Import all generated `.postman_collection.json` files
   - Import the updated `Sistema-ONG-Environment.postman_environment.json`
   - Select the environment in Postman

3. **Execute tests**:
   - Start with the Authentication collection to get tokens
   - Run other collections in order
   - All requests use real data from your database

### Testing the Generator

```bash
python scripts/sql-driven-testing/test_postman_generator.py
```

## Swagger Examples Generator

The Swagger Examples Generator updates Swagger documentation with real data extracted from the SQL database, ensuring documentation always reflects valid, executable examples.

### Features

- **Real Data Examples**: Updates all Swagger examples with actual data from the populated database
- **Comprehensive Coverage**: Generates examples for authentication, users, inventory, events, and network operations
- **Backup Management**: Creates automatic backups before updating configuration
- **Validation**: Validates updated configuration for syntax errors and completeness
- **Preservation**: Preserves existing documentation while updating only example sections
- **Stock-aware Examples**: Includes examples for different stock levels (high, medium, low, zero)

### Usage

```python
from swagger_generator import SwaggerGenerator

# With extracted data from SQLDataExtractor
generator = SwaggerGenerator(extracted_data)
result = generator.update_swagger_examples()

print(f"Updated {result['total_examples']} examples")
print(f"Backup created: {result['backup_created']}")
print(f"Validation passed: {result['validation_passed']}")
```

### Generated Example Categories

**Authentication Examples:**
- `LoginRequest` - Login with Presidente credentials
- `LoginRequestVocal` - Login with Vocal credentials  
- `LoginRequestCoordinador` - Login with Coordinador credentials
- `LoginRequestVoluntario` - Login with Voluntario credentials
- `LoginResponse` - Successful login response with real user data
- `LoginError` - Invalid credentials error

**User Management Examples:**
- `UsuariosList` - List of users with real data
- `UsuarioDetalle` - Detailed user information
- `CrearUsuario` - Create new user request
- `ActualizarUsuario` - Update existing user

**Inventory Examples:**
- `DonacionesList` - List of donations across categories
- `DonacionDetalle` - Detailed donation information
- `DonacionStockAlto` - High stock donation (>50 items)
- `DonacionStockBajo` - Low stock donation (<10 items)
- `DonacionSinStock` - Zero stock donation
- `CrearDonacion` - Create new donation
- `ActualizarDonacion` - Update existing donation

**Event Examples:**
- `EventosList` - List of solidarity events
- `EventoDetalle` - Detailed event information
- `EventoFuturo` - Future event (valid for participation)
- `EventoPasado` - Past event (read-only)
- `CrearEvento` - Create new future event
- `UnirseEvento` - Join event as participant

**Network Examples:**
- `SolicitudesExternas` - External donation requests
- `CrearSolicitudDonaciones` - Create donation request
- `OfertasExternas` - External donation offers
- `CrearOfertaDonaciones` - Create donation offer
- `TransferirDonaciones` - Transfer donations to another NGO
- `EventosExternos` - External solidarity events
- `AdhesionEventoExterno` - Join external event

### Quick Start

1. **Run the example script**:
   ```bash
   python example_swagger_usage.py
   ```

2. **Follow the interactive prompts** to:
   - Extract data from your database
   - Generate examples for all categories
   - Optionally update the Swagger configuration
   - Review generated examples in JSON format

3. **Verify the results**:
   - Check the updated Swagger documentation at `/api-docs`
   - All examples use real data from your database
   - Examples are executable against the actual API

### Testing the Generator

```bash
python test_swagger_generator.py
```

## Testing Orchestrator

The Testing Orchestrator coordinates the entire SQL-driven testing configuration generation process, managing data extraction, configuration generation, backups, and validation in a single coordinated workflow.

### Features

- **Coordinated Generation**: Orchestrates data extraction and all configuration generation in sequence
- **Automatic Backups**: Creates backups of existing configurations before making changes
- **Comprehensive Validation**: Validates both extracted data and generated configurations
- **Error Recovery**: Provides backup restoration capabilities if generation fails
- **Flexible Options**: Allows selective generation of specific configuration types
- **Detailed Reporting**: Generates comprehensive reports of the entire process
- **Status Monitoring**: Provides current status of all generated configurations

### Usage

```python
from orchestrator import TestingOrchestrator

# Create orchestrator (loads config from environment variables)
orchestrator = TestingOrchestrator()

# Generate all configurations with default settings
report = orchestrator.generate_all_testing_configs()

if report['success']:
    print(f"✅ Generated {len(report['summary']['configurations_generated'])} configuration types")
    print(f"Postman collections: {report['summary']['total_postman_collections']}")
    print(f"Swagger examples: {report['summary']['total_swagger_examples']}")
    print(f"Kafka scenarios: {report['summary']['total_kafka_scenarios']}")
else:
    print(f"❌ Generation failed: {report['error']}")
```

### Command Line Usage

```bash
# Generate all configurations
python scripts/sql-driven-testing/orchestrator.py

# Generate only specific configurations
python scripts/sql-driven-testing/orchestrator.py --no-swagger --no-kafka

# Skip backups and validation (faster)
python scripts/sql-driven-testing/orchestrator.py --no-backup --no-validate

# Check current status
python scripts/sql-driven-testing/orchestrator.py --status

# Restore from backup
python scripts/sql-driven-testing/orchestrator.py --restore /path/to/backup
```

### Custom Configuration

Create a JSON configuration file:

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "database": "ong_sistema",
    "user": "ong_user",
    "password": "ong_password"
  },
  "generation": {
    "postman": true,
    "swagger": true,
    "kafka": true,
    "backup": true,
    "validate": true
  },
  "output": {
    "save_extracted_data": true,
    "extracted_data_file": "extracted_test_data.json",
    "report_file": "generation_report.json"
  }
}
```

Then use it:

```bash
python scripts/sql-driven-testing/orchestrator.py --config my_config.json
```

### Generation Process

The orchestrator follows this systematic process:

1. **Backup Creation**: Creates timestamped backups of existing configurations
2. **Data Extraction**: Extracts test data from the populated SQL database
3. **Data Validation**: Validates data integrity and completeness
4. **Configuration Generation**: Generates Postman, Swagger, and Kafka configurations
5. **Configuration Validation**: Validates generated configurations for correctness
6. **Report Generation**: Creates comprehensive report with statistics and status
7. **Output Saving**: Saves extracted data and reports to specified files

### Backup Management

The orchestrator includes comprehensive backup management:

- **Automatic Backups**: Created before any modifications
- **Timestamped Directories**: Each backup has a unique timestamp
- **Backup Manifests**: JSON files describing what was backed up
- **Easy Restoration**: Simple command-line restoration from any backup
- **Status Tracking**: Monitor available backups and their contents

### Validation System

The orchestrator includes multi-level validation:

**Data Validation:**
- Completeness checks (all required data present)
- Foreign key integrity (references are valid)
- Role coverage (users for all roles exist)
- Category coverage (all donation categories present)

**Configuration Validation:**
- File existence and accessibility
- JSON structure validity
- Required sections present
- Syntax correctness

### Error Handling and Recovery

- **Graceful Failure**: Continues processing even if individual components fail
- **Detailed Error Reporting**: Comprehensive error messages and stack traces
- **Backup Restoration**: Easy recovery from backups if generation fails
- **Partial Success**: Reports what was successfully generated even on partial failures

### Quick Start

1. **Run the example script**:
   ```bash
   python scripts/sql-driven-testing/example_orchestrator_usage.py
   ```

2. **Generate all configurations**:
   ```bash
   python scripts/sql-driven-testing/orchestrator.py
   ```

3. **Check the results**:
   - Postman collections in `api-gateway/postman/`
   - Updated Swagger configuration at `api-gateway/src/config/swagger.js`
   - Kafka scenarios in `scripts/sql-driven-testing/kafka_scenarios.json`
   - Generation report in `scripts/sql-driven-testing/generation_report.json`

### Testing the Orchestrator

```bash
python scripts/sql-driven-testing/test_orchestrator.py
```

## Integration with Other Components

This system is designed with the following integration points:

- **SQL Data Extractor**: ✅ **Implemented** - Provides the foundation data for all generators
- **Postman Generator**: ✅ **Implemented** - Generates realistic API test collections
- **Swagger Examples Generator**: ✅ **Implemented** - Updates documentation with real data examples
- **Kafka Generator**: ✅ **Implemented** - Generates inter-NGO messaging test scenarios
- **Testing Orchestrator**: ✅ **Implemented** - Coordinates the entire generation process

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `3306` |
| `DB_NAME` | Database name | `ong_sistema` |
| `DB_USER` | Database user | `ong_user` |
| `DB_PASSWORD` | Database password | `ong_password` |

## Logging

The extractor uses Python's logging module. Set the log level as needed:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # For detailed output
logging.basicConfig(level=logging.INFO)   # For normal output
logging.basicConfig(level=logging.ERROR)  # For errors only
```

## Requirements

- Python 3.7+
- mysql-connector-python 8.2.0+
- Access to populated ONG database with test data

## Complete Documentation

This README provides a technical overview of the system components. For comprehensive documentation covering all aspects of the SQL-driven testing system, see:

### 📚 Main Documentation
- **[Documentation Index](DOCUMENTATION_INDEX.md)** - Complete guide to all documentation
- **[SQL Test Cases Guide](SQL_TEST_CASES_GUIDE.md)** - How to structure test cases in SQL and add new ones
- **[System Usage Guide](SYSTEM_USAGE_GUIDE.md)** - Complete usage guide for all scenarios and workflows

### 🛠️ Practical Guides
- **[Command Examples](COMMAND_EXAMPLES.md)** - Practical command examples with expected output
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Solutions for common problems and debugging
- **[Testing Guide](TESTING_GUIDE.md)** - Validation and testing framework documentation
- **[Usage Reference](USAGE.md)** - Command line interface reference

### 🎯 Quick Navigation
- **New to the system?** Start with [Documentation Index](DOCUMENTATION_INDEX.md)
- **Need to add test cases?** See [SQL Test Cases Guide](SQL_TEST_CASES_GUIDE.md#adding-new-test-cases)
- **Having issues?** Check [Troubleshooting Guide](TROUBLESHOOTING.md)
- **Setting up CI/CD?** See [Command Examples - CI/CD Integration](COMMAND_EXAMPLES.md#cicd-integration-examples)

## License

This module is part of the Sistema ONG project.