# SQL-Driven Testing - Troubleshooting Guide

## Overview

This guide provides solutions for common problems encountered when using the SQL-driven testing system. Issues are organized by category with step-by-step troubleshooting procedures.

## Database Connection Issues

### Problem: "Can't connect to MySQL server"

**Symptoms:**
```
❌ Database connection failed
🔍 Error: Can't connect to MySQL server on 'localhost:3306'
```

**Troubleshooting Steps:**

1. **Check if database server is running:**
   ```bash
   # For Docker Compose
   docker-compose ps database
   
   # For system MySQL
   sudo systemctl status mysql
   # or
   brew services list | grep mysql
   ```

2. **Start database if not running:**
   ```bash
   # Docker Compose
   docker-compose up -d database
   
   # System MySQL
   sudo systemctl start mysql
   # or
   brew services start mysql
   ```

3. **Verify connection parameters:**
   ```bash
   # Check environment variables
   echo $DB_HOST
   echo $DB_PORT
   echo $DB_USER
   echo $DB_NAME
   
   # Test manual connection
   mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "SELECT 1"
   ```

4. **Check firewall and network:**
   ```bash
   # Test port connectivity
   telnet localhost 3306
   # or
   nc -zv localhost 3306
   ```

**Common Solutions:**
- Update environment variables with correct values
- Ensure database container is running
- Check Docker network configuration
- Verify user permissions in MySQL

### Problem: "Access denied for user"

**Symptoms:**
```
❌ Database connection failed
🔍 Error: Access denied for user 'ong_user'@'localhost'
```

**Troubleshooting Steps:**

1. **Verify user credentials:**
   ```bash
   # Test with correct password
   mysql -h localhost -u ong_user -p
   ```

2. **Check user permissions:**
   ```sql
   -- Connect as root
   mysql -u root -p
   
   -- Check user exists
   SELECT User, Host FROM mysql.user WHERE User = 'ong_user';
   
   -- Check permissions
   SHOW GRANTS FOR 'ong_user'@'localhost';
   ```

3. **Create or fix user permissions:**
   ```sql
   -- Create user if doesn't exist
   CREATE USER 'ong_user'@'localhost' IDENTIFIED BY 'ong_password';
   
   -- Grant necessary permissions
   GRANT SELECT, INSERT, UPDATE, DELETE ON ong_sistema.* TO 'ong_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Problem: "Unknown database"

**Symptoms:**
```
❌ Database connection failed
🔍 Error: Unknown database 'ong_sistema'
```

**Solution:**
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE ong_sistema CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Initialize schema
mysql -u root -p ong_sistema < database/init/01-create-tables.sql
mysql -u root -p ong_sistema < database/init/02-test-cases.sql
```

## Test Data Issues

### Problem: "No test users found"

**Symptoms:**
```
❌ Test data validation failed
🔍 Missing test users:
  - No users found with nombre_usuario starting with 'test_'
```

**Troubleshooting Steps:**

1. **Check if test data exists:**
   ```sql
   SELECT COUNT(*) FROM usuarios WHERE nombre_usuario LIKE 'test_%';
   ```

2. **Initialize test data:**
   ```bash
   mysql -h localhost -u ong_user -p ong_sistema < database/init/02-test-cases.sql
   ```

3. **Verify test data structure:**
   ```sql
   SELECT nombre_usuario, rol, activo FROM usuarios WHERE nombre_usuario LIKE 'test_%';
   ```

4. **Check for required roles:**
   ```sql
   SELECT rol, COUNT(*) as count 
   FROM usuarios 
   WHERE nombre_usuario LIKE 'test_%' 
   GROUP BY rol;
   ```

**Expected Output:**
```
+-------------+-------+
| rol         | count |
+-------------+-------+
| PRESIDENTE  |     4 |
| VOCAL       |     6 |
| COORDINADOR |     8 |
| VOLUNTARIO  |    12 |
+-------------+-------+
```

### Problem: "Missing donation categories"

**Symptoms:**
```
❌ Test data validation failed
🔍 Missing donation categories: JUGUETES, UTILES_ESCOLARES
```

**Solution:**
```sql
-- Check current categories
SELECT categoria, COUNT(*) as count 
FROM donaciones 
WHERE usuario_alta LIKE 'test_%' 
GROUP BY categoria;

-- Add missing test donations
INSERT INTO donaciones (categoria, descripcion, cantidad, usuario_alta, fecha_alta) VALUES
('JUGUETES', 'Test Juguetes', 10, 'test_vocal', NOW()),
('UTILES_ESCOLARES', 'Test Útiles', 15, 'test_vocal', NOW());
```

### Problem: "Foreign key constraint violations"

**Symptoms:**
```
❌ Data integrity validation failed
🔍 Error: Foreign key constraint fails
```

**Troubleshooting Steps:**

1. **Check event participants:**
   ```sql
   -- Find orphaned participants
   SELECT ep.* FROM evento_participantes ep
   LEFT JOIN usuarios u ON ep.usuario_id = u.id
   WHERE u.id IS NULL;
   
   -- Fix orphaned participants
   DELETE FROM evento_participantes 
   WHERE usuario_id NOT IN (SELECT id FROM usuarios);
   ```

2. **Check donation references:**
   ```sql
   -- Find donations with invalid usuario_alta
   SELECT d.* FROM donaciones d
   LEFT JOIN usuarios u ON d.usuario_alta = u.nombre_usuario
   WHERE u.nombre_usuario IS NULL AND d.usuario_alta LIKE 'test_%';
   ```

3. **Check test case mappings:**
   ```sql
   -- Find mappings with invalid user references
   SELECT tcm.* FROM test_case_mapping tcm
   LEFT JOIN usuarios u ON tcm.user_id = u.id
   WHERE tcm.user_id IS NOT NULL AND u.id IS NULL;
   ```

## Generation Issues

### Problem: "Postman collection generation failed"

**Symptoms:**
```
❌ Postman generation failed
🔍 Error: KeyError: 'password_plain'
```

**Cause:** Test users missing the `password_plain` field needed for Postman authentication.

**Solution:**
```sql
-- Add password_plain field to test users
ALTER TABLE usuarios ADD COLUMN password_plain VARCHAR(255) DEFAULT NULL;

-- Update test users with known passwords
UPDATE usuarios 
SET password_plain = 'test123' 
WHERE nombre_usuario LIKE 'test_%';
```

**Alternative Solution (modify extractor):**
```python
# In data_extractor.py, modify the query to include a default password
query = """
SELECT id, nombre_usuario, nombre, apellido, email, rol, activo,
       'test123' as password_plain  -- Default password for testing
FROM usuarios 
WHERE nombre_usuario LIKE 'test_%'
ORDER BY rol, id
"""
```

### Problem: "Swagger examples generation failed"

**Symptoms:**
```
❌ Swagger generation failed
🔍 Error: FileNotFoundError: swagger.js not found
```

**Solution:**
```bash
# Check if Swagger config exists
ls -la api-gateway/src/config/swagger.js

# Create directory if missing
mkdir -p api-gateway/src/config

# Create basic Swagger config if missing
cat > api-gateway/src/config/swagger.js << 'EOF'
const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Sistema ONG API',
      version: '1.0.0',
      description: 'API para gestión de ONGs'
    },
    servers: [
      {
        url: 'http://localhost:3000',
        description: 'Development server'
      }
    ]
  },
  apis: ['./src/routes/*.js']
};

const specs = swaggerJsdoc(options);
module.exports = specs;
EOF
```

### Problem: "Kafka scenarios generation failed"

**Symptoms:**
```
❌ Kafka generation failed
🔍 Error: Invalid JSON in donaciones_solicitadas field
```

**Troubleshooting Steps:**

1. **Check JSON fields in database:**
   ```sql
   -- Validate JSON fields
   SELECT id, id_organizacion, 
          JSON_VALID(donaciones_solicitadas) as valid_json,
          donaciones_solicitadas
   FROM solicitudes_externas 
   WHERE JSON_VALID(donaciones_solicitadas) = 0;
   ```

2. **Fix invalid JSON:**
   ```sql
   -- Update invalid JSON
   UPDATE solicitudes_externas 
   SET donaciones_solicitadas = '[{"categoria":"ALIMENTOS","descripcion":"Arroz"}]'
   WHERE JSON_VALID(donaciones_solicitadas) = 0;
   ```

3. **Verify JSON structure:**
   ```sql
   -- Check JSON structure
   SELECT JSON_EXTRACT(donaciones_solicitadas, '$[0].categoria') as categoria
   FROM solicitudes_externas 
   LIMIT 1;
   ```

## File Permission Issues

### Problem: "Permission denied writing files"

**Symptoms:**
```
❌ File permission error
🔍 Error: Permission denied writing to 'api-gateway/postman/01-Autenticacion.postman_collection.json'
```

**Solutions:**

1. **Fix file permissions:**
   ```bash
   # Fix directory permissions
   chmod 755 api-gateway/postman/
   
   # Fix file permissions
   chmod 644 api-gateway/postman/*.json
   
   # Fix ownership if needed
   sudo chown -R $USER:$USER api-gateway/postman/
   ```

2. **Create missing directories:**
   ```bash
   mkdir -p api-gateway/postman
   mkdir -p scripts/sql-driven-testing
   mkdir -p backups/testing-configs
   ```

3. **Check disk space:**
   ```bash
   df -h .
   ```

### Problem: "Backup creation failed"

**Symptoms:**
```
❌ Backup creation failed
🔍 Error: No space left on device
```

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h
   du -sh backups/
   ```

2. **Clean old backups:**
   ```bash
   # Remove backups older than 30 days
   find backups/testing-configs -name "backup_*" -mtime +30 -exec rm -rf {} \;
   
   # Or use the built-in cleanup
   python scripts/generate-testing-configs.py --cleanup-backups --older-than 30
   ```

3. **Disable backups temporarily:**
   ```bash
   python scripts/generate-testing-configs.py --all --no-backup
   ```

## Validation Issues

### Problem: "Data integrity validation failed"

**Symptoms:**
```
❌ Data integrity validation failed
🔍 Inconsistent data found:
  - Events with no participants
  - Donations with zero quantity
```

**Troubleshooting Steps:**

1. **Check data consistency:**
   ```sql
   -- Events without participants
   SELECT e.id, e.nombre 
   FROM eventos e
   LEFT JOIN evento_participantes ep ON e.id = ep.evento_id
   WHERE ep.evento_id IS NULL AND e.usuario_alta LIKE 'test_%';
   
   -- Add participants to lonely events
   INSERT INTO evento_participantes (evento_id, usuario_id)
   SELECT e.id, 4  -- test_voluntario
   FROM eventos e
   LEFT JOIN evento_participantes ep ON e.id = ep.evento_id
   WHERE ep.evento_id IS NULL AND e.usuario_alta LIKE 'test_%';
   ```

2. **Fix stock level distribution:**
   ```sql
   -- Check stock distribution
   SELECT 
     categoria,
     SUM(CASE WHEN cantidad > 50 THEN 1 ELSE 0 END) as high_stock,
     SUM(CASE WHEN cantidad BETWEEN 10 AND 50 THEN 1 ELSE 0 END) as medium_stock,
     SUM(CASE WHEN cantidad BETWEEN 1 AND 9 THEN 1 ELSE 0 END) as low_stock,
     SUM(CASE WHEN cantidad = 0 THEN 1 ELSE 0 END) as zero_stock
   FROM donaciones 
   WHERE usuario_alta LIKE 'test_%'
   GROUP BY categoria;
   ```

### Problem: "Test case mapping validation failed"

**Symptoms:**
```
❌ Test case mapping validation failed
🔍 Invalid references found:
  - user_id 999 does not exist
  - resource_id 888 does not exist
```

**Solution:**
```sql
-- Find and fix invalid user references
UPDATE test_case_mapping tcm
LEFT JOIN usuarios u ON tcm.user_id = u.id
SET tcm.user_id = 1  -- Default to test_presidente
WHERE tcm.user_id IS NOT NULL AND u.id IS NULL;

-- Find and fix invalid resource references
UPDATE test_case_mapping tcm
LEFT JOIN donaciones d ON tcm.resource_id = d.id
SET tcm.resource_id = NULL
WHERE tcm.resource_id IS NOT NULL AND d.id IS NULL;
```

## Performance Issues

### Problem: "Generation takes too long"

**Symptoms:**
```
🔄 Generation running for more than 5 minutes...
```

**Optimization Steps:**

1. **Skip unnecessary operations:**
   ```bash
   # Skip backup for faster execution
   python scripts/generate-testing-configs.py --all --no-backup
   
   # Skip validation for faster execution
   python scripts/generate-testing-configs.py --all --no-validate
   ```

2. **Generate only what you need:**
   ```bash
   # Generate only Postman (fastest)
   python scripts/generate-testing-configs.py --postman
   ```

3. **Optimize database queries:**
   ```sql
   -- Add indexes for faster extraction
   CREATE INDEX idx_usuarios_test ON usuarios(nombre_usuario);
   CREATE INDEX idx_donaciones_test ON donaciones(usuario_alta);
   CREATE INDEX idx_eventos_test ON eventos(usuario_alta);
   CREATE INDEX idx_test_mapping_endpoint ON test_case_mapping(endpoint, method);
   ```

4. **Check database performance:**
   ```sql
   -- Check slow queries
   SHOW PROCESSLIST;
   
   -- Analyze table statistics
   ANALYZE TABLE usuarios, donaciones, eventos, test_case_mapping;
   ```

### Problem: "Memory usage too high"

**Symptoms:**
```
🔍 Warning: High memory usage detected (>1GB)
```

**Solutions:**

1. **Reduce data extraction size:**
   ```python
   # In data_extractor.py, add LIMIT clauses
   query = """
   SELECT * FROM usuarios 
   WHERE nombre_usuario LIKE 'test_%'
   ORDER BY id
   LIMIT 100  -- Limit for testing
   """
   ```

2. **Process data in chunks:**
   ```python
   # Process large datasets in smaller chunks
   def extract_large_dataset(self, chunk_size=1000):
       offset = 0
       while True:
           chunk = self.extract_chunk(offset, chunk_size)
           if not chunk:
               break
           yield chunk
           offset += chunk_size
   ```

## Configuration Issues

### Problem: "Invalid configuration file"

**Symptoms:**
```
❌ Configuration error
🔍 Error: Invalid JSON in config file
```

**Solution:**
```bash
# Validate JSON syntax
python -m json.tool custom-config.json

# Fix common JSON issues
# - Remove trailing commas
# - Use double quotes for strings
# - Escape backslashes in paths
```

**Example valid configuration:**
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
    "kafka": true
  }
}
```

### Problem: "Environment variables not loaded"

**Symptoms:**
```
❌ Configuration error
🔍 Error: DB_HOST environment variable not set
```

**Solutions:**

1. **Check environment variables:**
   ```bash
   env | grep DB_
   ```

2. **Load from .env file:**
   ```bash
   # Create .env file
   cat > .env << EOF
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=ong_user
   DB_PASSWORD=ong_password
   DB_NAME=ong_sistema
   EOF
   
   # Load environment variables
   export $(cat .env | xargs)
   ```

3. **Set variables manually:**
   ```bash
   export DB_HOST=localhost
   export DB_PORT=3306
   export DB_USER=ong_user
   export DB_PASSWORD=ong_password
   export DB_NAME=ong_sistema
   ```

## Integration Issues

### Problem: "Postman import fails"

**Symptoms:**
- Collections don't import correctly in Postman
- Environment variables not working
- Tests fail with authentication errors

**Solutions:**

1. **Verify JSON structure:**
   ```bash
   # Validate Postman collection JSON
   python -m json.tool api-gateway/postman/01-Autenticacion.postman_collection.json
   ```

2. **Check Postman version compatibility:**
   - Ensure using Postman v2.1 collection format
   - Update collection format if needed

3. **Import environment first:**
   - Import `Sistema-ONG-Environment.postman_environment.json` before collections
   - Select the environment in Postman

4. **Run authentication collection first:**
   - Execute authentication collection to populate tokens
   - Check that environment variables are set correctly

### Problem: "Swagger documentation not updating"

**Symptoms:**
- Examples in Swagger UI don't reflect generated data
- Swagger UI shows old examples

**Solutions:**

1. **Restart API server:**
   ```bash
   cd api-gateway
   npm restart
   ```

2. **Clear browser cache:**
   - Hard refresh (Ctrl+F5 or Cmd+Shift+R)
   - Clear browser cache for localhost

3. **Verify Swagger config:**
   ```bash
   # Check if config file was updated
   ls -la api-gateway/src/config/swagger.js
   
   # Verify syntax
   node -c api-gateway/src/config/swagger.js
   ```

## Debugging Techniques

### Enable Debug Logging

```bash
# Enable verbose logging
python scripts/generate-testing-configs.py --all --verbose --debug

# Set log level in environment
export LOG_LEVEL=DEBUG
python scripts/generate-testing-configs.py --all
```

### Manual Data Inspection

```python
# Interactive debugging
python3 -i scripts/sql-driven-testing/data_extractor.py

# In Python shell:
from data_extractor import SQLDataExtractor, create_db_config_from_env
db_config = create_db_config_from_env()
extractor = SQLDataExtractor(db_config)
extractor.connect()

# Inspect data manually
users = extractor.extract_users_by_role()
print(f"Found {len(users)} user categories")
for role, user_list in users.items():
    print(f"  {role}: {len(user_list)} users")
```

### Step-by-Step Debugging

```bash
# Test each component individually
python scripts/sql-driven-testing/test_data_extractor.py
python scripts/sql-driven-testing/test_postman_generator.py
python scripts/sql-driven-testing/test_swagger_generator.py
python scripts/sql-driven-testing/test_kafka_generator.py

# Run with dry-run to see what would be generated
python scripts/generate-testing-configs.py --all --dry-run --verbose
```

## Getting Help

### Log Analysis

Check log files for detailed error information:
```bash
# Check system logs
tail -f logs/sql-driven-testing.log

# Check generation reports
cat scripts/sql-driven-testing/generation_report.json | jq .
```

### System Information

Gather system information for support:
```bash
# System status
python scripts/generate-testing-configs.py --status

# Environment information
python --version
mysql --version
docker --version
docker-compose --version

# Database information
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT VERSION()"
```

### Common Support Questions

**Q: How do I reset everything and start fresh?**
```bash
# Stop all services
docker-compose down

# Remove generated files
rm -rf api-gateway/postman/*.json
rm -f api-gateway/src/config/swagger.js
rm -f scripts/sql-driven-testing/kafka_scenarios.json

# Reinitialize database
docker-compose up -d database
sleep 30
mysql -h localhost -u root -proot -e "DROP DATABASE IF EXISTS ong_sistema"
mysql -h localhost -u root -proot -e "CREATE DATABASE ong_sistema"
mysql -h localhost -u root -proot ong_sistema < database/init/01-create-tables.sql
mysql -h localhost -u root -proot ong_sistema < database/init/02-test-cases.sql

# Regenerate everything
python scripts/generate-testing-configs.py --all --verbose
```

**Q: How do I add custom test cases?**
See the [SQL Test Cases Guide](SQL_TEST_CASES_GUIDE.md) for detailed instructions.

**Q: How do I modify the generated configurations?**
The system is designed to regenerate configurations from SQL data. Modify the SQL test cases instead of the generated files directly.

This troubleshooting guide should help resolve most common issues with the SQL-driven testing system. For additional support, check the system logs and run diagnostic commands to gather more information about specific problems.