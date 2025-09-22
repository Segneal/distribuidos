# SQL-Driven Testing - Usage Guide

## Main Command Line Script

The `generate-testing-configs.py` script is the main entry point for the SQL-driven testing system.

### Basic Usage

```bash
# Generate all configurations (Postman, Swagger, Kafka)
python scripts/generate-testing-configs.py --all

# Generate specific configurations
python scripts/generate-testing-configs.py --postman --swagger
python scripts/generate-testing-configs.py --kafka

# Generate with options
python scripts/generate-testing-configs.py --all --no-backup
python scripts/generate-testing-configs.py --postman --no-validate
python scripts/generate-testing-configs.py --all --verbose
```

### Advanced Options

```bash
# Validation only (no generation)
python scripts/generate-testing-configs.py --validate-only

# Dry run (simulate without changes)
python scripts/generate-testing-configs.py --all --dry-run

# Custom configuration file
python scripts/generate-testing-configs.py --all --config custom-config.json

# Verbose output
python scripts/generate-testing-configs.py --all --verbose
```

### Backup Management

```bash
# List available backups
python scripts/generate-testing-configs.py --list-backups

# Restore from specific backup
python scripts/generate-testing-configs.py --restore-backup 2024-01-15_10-30-00
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--all` | Generate all configurations (Postman, Swagger, Kafka) |
| `--postman` | Generate Postman collections only |
| `--swagger` | Update Swagger examples only |
| `--kafka` | Generate Kafka scenarios only |
| `--no-backup` | Skip creating backup before generation |
| `--no-validate` | Skip data validation |
| `--validate-only` | Only validate data without generating |
| `--list-backups` | List available backups |
| `--restore-backup TIMESTAMP` | Restore from specific backup |
| `--config FILE` | Use custom configuration file |
| `--verbose, -v` | Enable verbose output |
| `--dry-run` | Simulate execution without making changes |

### Configuration File

The script uses `scripts/sql-driven-testing/config.json` by default. You can specify a custom configuration file with `--config`.

Example configuration:

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "sistema_ong"
  },
  "backup": {
    "enabled": true,
    "retention_days": 30,
    "directory": "backups/testing-configs"
  },
  "validation": {
    "enabled": true,
    "strict_mode": false
  }
}
```

### Environment Variables

You can also configure the database connection using environment variables:

- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 3306)
- `DB_USER` - Database user (default: root)
- `DB_PASSWORD` - Database password
- `DB_NAME` - Database name (default: sistema_ong)

### Output Files

The script generates:

1. **Postman Collections**: `api-gateway/postman/*.postman_collection.json`
2. **Swagger Examples**: Updates `api-gateway/src/config/swagger.js`
3. **Kafka Scenarios**: `scripts/sql-driven-testing/kafka_scenarios.json`
4. **Generation Report**: `logs/generation_report_TIMESTAMP.json`
5. **Backups**: `backups/testing-configs/backup_TIMESTAMP/`

### Exit Codes

- `0` - Success
- `1` - Error or failure

### Examples

#### Complete Regeneration
```bash
# Full regeneration with backup and validation
python scripts/generate-testing-configs.py --all --verbose
```

#### Quick Postman Update
```bash
# Update only Postman collections without backup
python scripts/generate-testing-configs.py --postman --no-backup
```

#### Validate Data Only
```bash
# Check data integrity without generating anything
python scripts/generate-testing-configs.py --validate-only --verbose
```

#### Restore Previous Configuration
```bash
# List backups and restore
python scripts/generate-testing-configs.py --list-backups
python scripts/generate-testing-configs.py --restore-backup 2024-01-15_10-30-00
```

### Troubleshooting

1. **Database Connection Issues**
   - Check database credentials in config file or environment variables
   - Ensure database server is running
   - Verify database name exists

2. **Permission Issues**
   - Ensure write permissions to output directories
   - Check backup directory permissions

3. **Validation Failures**
   - Run with `--validate-only` to see specific issues
   - Check SQL test data completeness
   - Verify foreign key relationships

4. **Generation Errors**
   - Use `--verbose` for detailed error information
   - Check log files in `logs/` directory
   - Verify template files exist and are readable

### Integration with Development Workflow

```bash
# After updating SQL test data
python scripts/generate-testing-configs.py --all

# Before running tests
python scripts/generate-testing-configs.py --validate-only

# After major changes (with backup)
python scripts/generate-testing-configs.py --all --verbose

# Quick iteration (no backup)
python scripts/generate-testing-configs.py --postman --no-backup
```