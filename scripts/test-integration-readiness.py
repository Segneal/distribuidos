#!/usr/bin/env python3
"""
Integration Readiness Test
This script verifies that all components are ready for SQL-driven testing integration.
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a required file exists."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} missing: {file_path}")
        return False

def check_directory_exists(dir_path, description):
    """Check if a required directory exists."""
    if Path(dir_path).exists() and Path(dir_path).is_dir():
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description} missing: {dir_path}")
        return False

def check_docker_compose_config():
    """Check docker-compose configuration for MySQL initialization."""
    print("🔍 Checking docker-compose configuration...")
    
    docker_compose_file = Path("docker-compose.yml")
    if not docker_compose_file.exists():
        print("❌ docker-compose.yml not found")
        return False
    
    try:
        with open(docker_compose_file, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading docker-compose.yml: {e}")
        return False
    
    # Check for MySQL service
    if 'mysql:' not in content:
        print("❌ MySQL service not found in docker-compose.yml")
        return False
    
    # Check for volume mount
    if './database/init:/docker-entrypoint-initdb.d' not in content:
        print("❌ Database initialization volume mount not found")
        return False
    
    print("✅ Docker-compose configuration is correct")
    return True

def check_database_files():
    """Check that all required database files exist."""
    print("🔍 Checking database initialization files...")
    
    required_files = [
        ("database/init/00-create-database.sql", "Database creation script"),
        ("database/init/01-create-tables.sql", "Table creation script"),
        ("database/init/02-test-cases.sql", "Test cases script")
    ]
    
    results = []
    for file_path, description in required_files:
        results.append(check_file_exists(file_path, description))
    
    return all(results)

def check_sql_driven_testing_components():
    """Check that all SQL-driven testing components exist."""
    print("🔍 Checking SQL-driven testing components...")
    
    required_files = [
        ("scripts/sql-driven-testing/data_extractor.py", "Data extractor"),
        ("scripts/sql-driven-testing/postman_generator.py", "Postman generator"),
        ("scripts/sql-driven-testing/swagger_generator.py", "Swagger generator"),
        ("scripts/sql-driven-testing/kafka_generator.py", "Kafka generator"),
        ("scripts/sql-driven-testing/orchestrator.py", "Orchestrator"),
        ("scripts/generate-testing-configs.py", "Main configuration generator")
    ]
    
    results = []
    for file_path, description in required_files:
        results.append(check_file_exists(file_path, description))
    
    return all(results)

def check_configuration_files():
    """Check configuration files."""
    print("🔍 Checking configuration files...")
    
    config_file = Path("scripts/sql-driven-testing/config.json")
    if not config_file.exists():
        print("❌ Configuration file missing: scripts/sql-driven-testing/config.json")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Check required configuration sections
        required_sections = ['database', 'postman', 'swagger', 'kafka']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing configuration section: {section}")
                return False
        
        print("✅ Configuration file is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading configuration file: {e}")
        return False

def check_python_dependencies():
    """Check if required Python packages are available."""
    print("🔍 Checking Python dependencies...")
    
    required_packages = [
        ('mysql.connector', 'mysql-connector-python'),
        ('json', 'built-in'),
        ('pathlib', 'built-in'),
        ('datetime', 'built-in')
    ]
    
    missing_packages = []
    for package, install_name in required_packages:
        try:
            if package == 'mysql.connector':
                import mysql.connector
            else:
                __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} not available")
            if install_name != 'built-in':
                missing_packages.append(install_name)
    
    if missing_packages:
        print(f"📦 Install missing packages: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_output_directories():
    """Check that output directories exist or can be created."""
    print("🔍 Checking output directories...")
    
    directories = [
        ("api-gateway/postman", "Postman collections directory"),
        ("scripts/sql-driven-testing/backups", "Backups directory"),
        ("scripts/sql-driven-testing/kafka_scenarios", "Kafka scenarios directory")
    ]
    
    results = []
    for dir_path, description in directories:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {description}: {dir_path}")
            results.append(True)
        else:
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"✅ {description} created: {dir_path}")
                results.append(True)
            except Exception as e:
                print(f"❌ Cannot create {description}: {e}")
                results.append(False)
    
    return all(results)

def check_integration_documentation():
    """Check that integration documentation exists."""
    print("🔍 Checking integration documentation...")
    
    docs = [
        ("database/INTEGRATION_NOTES.md", "Integration notes"),
        ("database/MIGRATION_GUIDE.md", "Migration guide"),
        ("scripts/sql-driven-testing/README.md", "SQL-driven testing README"),
        ("scripts/sql-driven-testing/USAGE.md", "Usage guide")
    ]
    
    results = []
    for doc_path, description in docs:
        results.append(check_file_exists(doc_path, description))
    
    return all(results)

def main():
    """Main readiness check function."""
    print("🚀 Checking SQL-driven testing integration readiness...")
    print("=" * 70)
    
    # Run all readiness checks
    checks = [
        ("Docker Compose Configuration", check_docker_compose_config),
        ("Database Files", check_database_files),
        ("SQL-Driven Testing Components", check_sql_driven_testing_components),
        ("Configuration Files", check_configuration_files),
        ("Python Dependencies", check_python_dependencies),
        ("Output Directories", check_output_directories),
        ("Integration Documentation", check_integration_documentation)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 50)
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} readiness checks passed!")
        print("✅ System is ready for SQL-driven testing integration.")
        print("\n📋 Next steps:")
        print("   1. Start the database: docker-compose up -d mysql")
        print("   2. Wait for initialization to complete")
        print("   3. Verify integration: python scripts/verify-sql-integration.py")
        print("   4. Generate configurations: python scripts/generate-testing-configs.py --all")
        print("   5. Start all services: docker-compose up -d")
        print("\n🔧 Troubleshooting:")
        print("   - Check logs: docker-compose logs mysql")
        print("   - Validate SQL: python scripts/test-sql-syntax.py")
        print("   - Test extraction: python scripts/sql-driven-testing/example_usage.py")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} out of {total} readiness checks failed.")
        print("🔧 Please fix the issues above before proceeding with integration.")
        
        if passed > 0:
            print(f"\n✅ {passed} checks passed - you're {passed/total*100:.0f}% ready!")
        
        sys.exit(1)

if __name__ == "__main__":
    main()