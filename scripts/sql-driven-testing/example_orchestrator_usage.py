#!/usr/bin/env python3
"""
Example usage of the Testing Orchestrator
Sistema ONG - SQL Driven Testing

This script demonstrates how to use the TestingOrchestrator to generate
all testing configurations from SQL data.
"""

import json
import logging
from orchestrator import TestingOrchestrator

# Configure logging to see the orchestrator's progress
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Example usage of the Testing Orchestrator"""
    print("=" * 60)
    print("SQL-Driven Testing Orchestrator - Example Usage")
    print("=" * 60)
    
    try:
        # Create orchestrator instance
        # It will automatically load configuration from environment variables
        orchestrator = TestingOrchestrator()
        
        # Option 1: Generate all configurations with default settings
        print("\n1. Generating all configurations with default settings...")
        report = orchestrator.generate_all_testing_configs()
        
        if report.get('success', False):
            print("\n✅ Generation completed successfully!")
            print_summary(report)
        else:
            print("\n❌ Generation failed!")
            print(f"Error: {report.get('error', 'Unknown error')}")
            return
        
        # Option 2: Check current status
        print("\n2. Checking current status of generated configurations...")
        status = orchestrator.get_generation_status()
        print_status(status)
        
        # Option 3: Generate with custom options
        print("\n3. Example: Generate only Postman collections (no Swagger or Kafka)...")
        custom_options = {
            'postman': True,
            'swagger': False,
            'kafka': False,
            'backup': True,
            'validate': True
        }
        
        custom_report = orchestrator.generate_all_testing_configs(custom_options)
        if custom_report.get('success', False):
            print("✅ Custom generation completed!")
            print(f"Generated: {', '.join(custom_report['summary']['configurations_generated'])}")
        
    except Exception as e:
        print(f"\n❌ Error during orchestrator usage: {e}")
        import traceback
        traceback.print_exc()

def print_summary(report):
    """Print a summary of the generation report"""
    summary = report.get('summary', {})
    
    print(f"\n📊 Generation Summary:")
    print(f"   Configurations: {', '.join(summary.get('configurations_generated', []))}")
    print(f"   Postman collections: {summary.get('total_postman_collections', 0)}")
    print(f"   Swagger examples: {summary.get('total_swagger_examples', 0)}")
    print(f"   Kafka scenarios: {summary.get('total_kafka_scenarios', 0)}")
    print(f"   Validation passed: {'✅' if summary.get('validation_passed', False) else '❌'}")
    print(f"   Validation errors: {summary.get('total_validation_errors', 0)}")
    print(f"   Validation warnings: {summary.get('total_validation_warnings', 0)}")
    
    if report.get('backup_path'):
        print(f"   Backup created: {report['backup_path']}")
    
    # Show data extraction details
    data_extraction = report.get('data_extraction', {})
    if data_extraction:
        print(f"\n📈 Data Extraction Details:")
        print(f"   Total users: {data_extraction.get('total_users', 0)}")
        print(f"   User roles: {', '.join(data_extraction.get('user_roles', []))}")
        print(f"   Inventory categories: {', '.join(data_extraction.get('inventory_categories', []))}")
        print(f"   Total donations: {data_extraction.get('total_donations', 0)}")
        print(f"   Total events: {data_extraction.get('total_events', 0)} ({data_extraction.get('future_events', 0)} future)")
        print(f"   Test mappings: {data_extraction.get('test_mappings', 0)}")
        print(f"   External requests: {data_extraction.get('external_requests', 0)}")

def print_status(status):
    """Print current status of configurations"""
    print(f"\n📋 Current Configuration Status:")
    
    # Postman status
    postman = status.get('postman', {})
    print(f"   Postman: {postman.get('collections_found', 0)}/{postman.get('collections_expected', 0)} collections")
    print(f"            Environment: {'✅' if postman.get('environment_exists', False) else '❌'}")
    
    # Swagger status
    swagger = status.get('swagger', {})
    if swagger.get('exists', False):
        print(f"   Swagger: ✅ Configuration exists")
        print(f"            Examples: {'✅' if swagger.get('has_examples_section', False) else '❌'}")
    else:
        print(f"   Swagger: ❌ Configuration not found")
    
    # Kafka status
    kafka = status.get('kafka', {})
    if kafka.get('exists', False):
        print(f"   Kafka: ✅ {kafka.get('total_scenarios', 0)} scenarios across {len(kafka.get('topics', []))} topics")
    else:
        print(f"   Kafka: ❌ Scenarios not found")
    
    # Backup status
    backups = status.get('backups', {})
    if backups.get('backup_dir_exists', False):
        print(f"   Backups: {backups.get('total_backups', 0)} available")
        if backups.get('latest_backup'):
            latest = backups['latest_backup']
            print(f"            Latest: {latest.get('timestamp', 'unknown')} ({latest.get('files_backed_up', 0)} files)")
    else:
        print(f"   Backups: ❌ No backup directory found")

def demonstrate_advanced_usage():
    """Demonstrate advanced orchestrator features"""
    print("\n" + "=" * 60)
    print("Advanced Orchestrator Features")
    print("=" * 60)
    
    orchestrator = TestingOrchestrator()
    
    # Custom configuration example
    custom_config = {
        'database': {
            'host': 'localhost',
            'port': 3306,
            'database': 'ong_sistema',
            'user': 'ong_user',
            'password': 'ong_password'
        },
        'generation': {
            'postman': True,
            'swagger': True,
            'kafka': True,
            'backup': True,
            'validate': True
        },
        'output': {
            'save_extracted_data': True,
            'extracted_data_file': 'custom_extracted_data.json',
            'report_file': 'custom_generation_report.json'
        }
    }
    
    print("1. Custom configuration loaded")
    
    # Generate with specific options
    options = {
        'postman': True,
        'swagger': False,  # Skip Swagger for this example
        'kafka': True,
        'backup': False,   # Skip backup for this example
        'validate': True
    }
    
    print("2. Generating with custom options...")
    report = orchestrator.generate_all_testing_configs(options)
    
    if report.get('success', False):
        print("✅ Advanced generation completed!")
        
        # Show detailed results
        if 'postman_details' in report:
            postman_details = report['postman_details']
            print(f"   Postman collections: {len(postman_details.get('collections_generated', []))}")
            for collection in postman_details.get('collections_generated', []):
                print(f"     - {collection}")
        
        if 'kafka_details' in report:
            kafka_details = report['kafka_details']
            print(f"   Kafka topics: {len(kafka_details.get('topics_covered', []))}")
            for topic, count in kafka_details.get('scenarios_by_topic', {}).items():
                print(f"     - {topic}: {count} scenarios")

if __name__ == "__main__":
    main()
    
    # Uncomment to see advanced features
    # demonstrate_advanced_usage()