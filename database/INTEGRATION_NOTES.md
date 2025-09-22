# SQL-Driven Testing Integration Notes

## Overview
This document describes the integration of the SQL-driven testing system with the existing database infrastructure.

## Current Database Setup

### Initialization Process
The system uses Docker's MySQL initialization feature through volume mounting:
```yaml
volumes:
  - ./database/init:/docker-entrypoint-initdb.d
```

### Execution Order
MySQL executes SQL files in alphabetical order:
1. `00-create-database.sql` - Creates the `ong_sistema` database
2. `01-create-tables.sql` - Creates all required tables and indexes
3. `02-test-cases.sql` - Populates comprehensive test data

## Integration Status

### ✅ Schema Compatibility
- All tables referenced in test cases exist in the main schema
- Column names and types match perfectly
- Foreign key relationships are maintained
- No ID conflicts with existing data

### ✅ Table Mapping Verification
Test cases populate the following tables:
- `usuarios` - Test users for all roles
- `donaciones` - Sample donations across all categories
- `eventos` - Future and past events for testing
- `evento_participantes` - Event participation data
- `donaciones_repartidas` - Historical distribution data
- `solicitudes_externas` - External donation requests
- `ofertas_externas` - External donation offers
- `eventos_externos` - External solidarity events
- `solicitudes_propias` - Own donation requests
- `ofertas_propias` - Own donation offers
- `transferencias_enviadas` - Sent transfers audit
- `transferencias_recibidas` - Received transfers audit
- `adhesiones_eventos_externos` - External event participations
- `auditoria_stock` - Stock change tracking
- `test_case_mapping` - Test case metadata (new table)

### ✅ Docker Integration
- No changes needed to docker-compose.yml
- Initialization happens automatically on container startup
- Test data is loaded after schema creation
- All services can access populated test data immediately

## Migration from Current System

### Before Integration
- Database was initialized with basic schema only
- No standardized test data
- Manual data creation for testing
- Inconsistent test scenarios across different tools

### After Integration
- Comprehensive test data loaded automatically
- Consistent test scenarios across all tools
- Automated generation of testing configurations
- Single source of truth for all test cases

## Compatibility Notes

### Existing migrate.sql
- The `database/migrate.sql` file is not used by docker-compose
- It contains a standalone migration with admin user creation
- No conflicts with the new test data (admin user gets auto-incremented ID)
- Can be kept for manual migration scenarios

### Test Data Characteristics
- Test users have predictable IDs (1-10) and known passwords
- Donations cover all categories with various stock levels
- Events include past, present, and future scenarios
- Inter-ONG data simulates realistic network interactions
- All test data is clearly marked with 'test_' prefixes

## Validation Results

### Schema Validation
- All INSERT statements match table definitions
- Foreign key constraints are satisfied
- Enum values are valid
- Data types are compatible

### Data Integrity
- No duplicate primary keys
- All foreign key references exist
- Timestamps use appropriate functions (NOW(), DATE_ADD, etc.)
- JSON fields contain valid JSON structures

## Next Steps

1. ✅ Verify docker-compose initialization works
2. ✅ Test data extraction functionality
3. ✅ Validate generated configurations
4. ✅ Document usage procedures

## Troubleshooting

### Common Issues
- **Container startup fails**: Check SQL syntax in test cases file
- **Foreign key errors**: Verify referenced IDs exist in parent tables
- **Duplicate key errors**: Check for ID conflicts with existing data

### Verification Commands
```bash
# Check if test data was loaded
docker exec ong-mysql mysql -u ong_user -pong_password ong_sistema -e "SELECT COUNT(*) FROM usuarios WHERE nombre_usuario LIKE 'test_%';"

# Verify test case mappings
docker exec ong-mysql mysql -u ong_user -pong_password ong_sistema -e "SELECT COUNT(*) FROM test_case_mapping;"

# Check inter-ONG data
docker exec ong-mysql mysql -u ong_user -pong_password ong_sistema -e "SELECT COUNT(*) FROM solicitudes_externas;"
```