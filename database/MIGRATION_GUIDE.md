# Migration Guide: SQL-Driven Testing Integration

## Overview
This guide helps you migrate from the current manual testing data setup to the new SQL-driven testing system.

## Pre-Migration Checklist

### 1. Backup Current Data
If you have existing test data you want to preserve:
```bash
# Backup current database
docker exec ong-mysql mysqldump -u ong_user -pong_password ong_sistema > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Stop Current Services
```bash
docker-compose down
```

### 3. Clean Volumes (Optional)
If you want a completely fresh start:
```bash
docker volume rm $(docker volume ls -q | grep mysql)
```

## Migration Process

### Step 1: Update Database Initialization
The new system is already integrated! The database initialization process now includes:

1. **00-create-database.sql** - Database creation
2. **01-create-tables.sql** - Schema creation  
3. **02-test-cases.sql** - Test data population

### Step 2: Restart Services
```bash
docker-compose up -d mysql
```

Wait for MySQL to be healthy:
```bash
docker-compose logs -f mysql
```

Look for: `MySQL init process done. Ready for start up.`

### Step 3: Verify Integration
```bash
# Check test users were created
docker exec ong-mysql mysql -u ong_user -pong_password ong_sistema -e "
SELECT id, nombre_usuario, rol, activo 
FROM usuarios 
WHERE nombre_usuario LIKE 'test_%' 
ORDER BY id;"

# Check test donations
docker exec ong-mysql mysql -u ong_user -pong_password ong_sistema -e "
SELECT categoria, COUNT(*) as cantidad, SUM(cantidad) as stock_total 
FROM donaciones 
WHERE usuario_alta LIKE 'test_%' 
GROUP BY categoria;"

# Check test case mappings
docker exec ong-mysql mysql -u ong_user -pong_password ong_sistema -e "
SELECT test_category, COUNT(*) as casos 
FROM test_case_mapping 
GROUP BY test_category;"
```

### Step 4: Start All Services
```bash
docker-compose up -d
```

### Step 5: Generate Testing Configurations
```bash
# Generate all testing configurations from the new test data
python scripts/generate-testing-configs.py --all

# Or generate specific configurations
python scripts/generate-testing-configs.py --postman
python scripts/generate-testing-configs.py --swagger  
python scripts/generate-testing-configs.py --kafka
```

## Verification Steps

### 1. Database Verification
```bash
# Verify all expected tables exist and have data
docker exec ong-mysql mysql -u ong_user -pong_password ong_sistema -e "
SELECT 
    table_name,
    table_rows
FROM information_schema.tables 
WHERE table_schema = 'ong_sistema' 
    AND table_name IN (
        'usuarios', 'donaciones', 'eventos', 'evento_participantes',
        'solicitudes_externas', 'ofertas_externas', 'eventos_externos',
        'test_case_mapping'
    )
ORDER BY table_name;"
```

### 2. Test Data Verification
```bash
# Check test users by role
docker exec ong-mysql mysql -u ong_user -pong_password ong_sistema -e "
SELECT rol, COUNT(*) as usuarios, GROUP_CONCAT(nombre_usuario) as nombres
FROM usuarios 
WHERE nombre_usuario LIKE 'test_%' 
GROUP BY rol;"

# Check donation categories and stock levels
docker exec ong-mysql mysql -u ong_user -pong_password ong_sistema -e "
SELECT 
    categoria,
    COUNT(*) as items,
    MIN(cantidad) as stock_min,
    MAX(cantidad) as stock_max,
    AVG(cantidad) as stock_promedio
FROM donaciones 
WHERE usuario_alta LIKE 'test_%'
GROUP BY categoria;"
```

### 3. Configuration Generation Test
```bash
# Test the data extraction
python scripts/sql-driven-testing/example_usage.py

# Test Postman generation
python scripts/sql-driven-testing/example_postman_usage.py

# Test Swagger generation  
python scripts/sql-driven-testing/example_swagger_usage.py

# Test Kafka generation
python scripts/sql-driven-testing/example_kafka_usage.py
```

## Rollback Procedure

If you need to rollback to the previous system:

### 1. Stop Services
```bash
docker-compose down
```

### 2. Remove Test Data
```bash
# Remove only test data, keep schema
docker exec ong-mysql mysql -u ong_user -pong_password ong_sistema -e "
DELETE FROM usuarios WHERE nombre_usuario LIKE 'test_%';
DELETE FROM donaciones WHERE usuario_alta LIKE 'test_%';
DELETE FROM eventos WHERE usuario_alta LIKE 'test_%';
DELETE FROM solicitudes_externas WHERE id_organizacion LIKE 'ong-%';
DELETE FROM ofertas_externas WHERE id_organizacion LIKE 'ong-%';
DELETE FROM eventos_externos WHERE id_organizacion LIKE 'ong-%';
DROP TABLE IF EXISTS test_case_mapping;
"
```

### 3. Restore Backup (if available)
```bash
# Restore from backup
docker exec -i ong-mysql mysql -u ong_user -pong_password ong_sistema < your_backup.sql
```

## Post-Migration Benefits

### 1. Automated Test Data
- Consistent test scenarios across all tools
- No manual data creation needed
- Realistic inter-ONG network simulation

### 2. Configuration Generation
- Postman collections with real data
- Swagger examples with actual values
- Kafka test scenarios with consistent IDs

### 3. Maintenance
- Single source of truth for test cases
- Easy to add new test scenarios
- Automatic backup and restore capabilities

## Troubleshooting

### Issue: MySQL Container Won't Start
**Symptoms**: Container exits immediately or shows initialization errors
**Solution**: 
1. Check SQL syntax in `database/init/02-test-cases.sql`
2. Verify no duplicate IDs or constraint violations
3. Check container logs: `docker-compose logs mysql`

### Issue: Test Data Not Loading
**Symptoms**: Tables exist but no test data
**Solution**:
1. Verify file permissions on `database/init/` directory
2. Check if files are being mounted: `docker exec ong-mysql ls -la /docker-entrypoint-initdb.d/`
3. Restart with clean volumes: `docker-compose down -v && docker-compose up -d`

### Issue: Foreign Key Constraint Errors
**Symptoms**: INSERT statements fail with FK violations
**Solution**:
1. Verify execution order (files run alphabetically)
2. Check that referenced IDs exist in parent tables
3. Ensure test data maintains referential integrity

### Issue: Configuration Generation Fails
**Symptoms**: Python scripts can't extract data
**Solution**:
1. Verify database connection in `scripts/sql-driven-testing/config.json`
2. Check if test data was loaded properly
3. Ensure all required Python dependencies are installed

## Support

For additional help:
1. Check the integration notes: `database/INTEGRATION_NOTES.md`
2. Review the SQL-driven testing documentation: `scripts/sql-driven-testing/README.md`
3. Run the test suite: `python scripts/sql-driven-testing/run_tests.py`