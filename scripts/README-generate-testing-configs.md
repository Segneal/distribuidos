# Generate Testing Configurations Script

## Overview

The `generate-testing-configs.py` script is the main command-line interface for the SQL-driven testing system. It coordinates the extraction of test data from the SQL database and automatically generates testing configurations for Postman, Swagger, and Kafka.

## Features

- **Centralized Test Data**: Uses SQL scripts as the single source of truth for all test cases
- **Automatic Generation**: Creates Postman collections, Swagger examples, and Kafka scenarios
- **Backup Management**: Automatically backs up existing configurations before changes
- **Comprehensive Validation**: Validates both extracted data and generated configurations
- **Flexible Options**: Generate specific configurations or all at once
- **Restore Capability**: Restore from previous backups when needed

## Quick Start

```bash
# Generate all configurations
python scripts/generate-testing-configs.py --all

# Generate only Postman collections
python scripts/generate-testing-configs.py --postman

# Dry run to see what would be generated
python scripts/generate-testing-configs.py --all --dry-run
```

## Requirements

- Python 3.7+
- MySQL database with test data populated
- Required Python packages (see requirements.txt)

## Configuration

The script uses `scripts/sql-driven-testing/config.json` for configuration, or you can specify a custom config file with `--config`.

### Database Configuration

Set up your database connection in the config file or using environment variables:

```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=your_user
export DB_PASSWORD=your_password
export DB_NAME=sistema_ong
```

## Generated Files

The script generates:

1. **Postman Collections**: `api-gateway/postman/*.postman_collection.json`
2. **Swagger Examples**: Updates `api-gateway/src/config/swagger.js`
3. **Kafka Scenarios**: `scripts/sql-driven-testing/kafka_scenarios.json`
4. **Reports**: `logs/generation_report_*.json`
5. **Backups**: `backups/testing-configs/backup_*/`

## Common Use Cases

### Development Workflow
```bash
# After updating SQL test data
python scripts/generate-testing-configs.py --all

# Quick Postman update during development
python scripts/generate-testing-configs.py --postman --no-backup
```

### CI/CD Integration
```bash
# Validate test data in CI
python scripts/generate-testing-configs.py --validate-only

# Generate configurations for testing
python scripts/generate-testing-configs.py --all --no-backup
```

### Backup and Restore
```bash
# List available backups
python scripts/generate-testing-configs.py --list-backups

# Restore from specific backup
python scripts/generate-testing-configs.py --restore-backup 2024-01-15_10-30-00
```

## Troubleshooting

### Database Connection Issues
- Verify database credentials in config file
- Ensure database server is running
- Check that the database contains test data

### Permission Issues
- Ensure write permissions to output directories
- Check that backup directory is writable

### Validation Failures
- Run with `--validate-only` to see specific issues
- Check that SQL test data is complete
- Verify foreign key relationships in test data

## Testing

Run the test suite to verify the script works correctly:

```bash
python scripts/test-generate-configs.py
```

## Support

For detailed usage information, see:
- `scripts/sql-driven-testing/USAGE.md` - Comprehensive usage guide
- `scripts/sql-driven-testing/README.md` - Technical documentation
- Run `python scripts/generate-testing-configs.py --help` for command-line help