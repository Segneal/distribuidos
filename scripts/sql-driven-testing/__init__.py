"""
SQL-Driven Testing Package
Sistema ONG - Testing Configuration Generation

This package provides tools for extracting test data from SQL databases
and generating testing configurations for Postman, Swagger, and Kafka.
"""

# Import modules when used as a package
try:
    from .data_extractor import SQLDataExtractor, DatabaseConfig, create_db_config_from_env
except ImportError:
    # When running tests directly, imports may not work
    pass

__version__ = "1.0.0"
__author__ = "Sistema ONG Development Team"

__all__ = [
    'SQLDataExtractor',
    'DatabaseConfig', 
    'create_db_config_from_env'
]