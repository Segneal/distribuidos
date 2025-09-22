#!/usr/bin/env python3
"""
Example usage of PostmanGenerator with SQLDataExtractor
Sistema ONG - SQL Driven Testing

This script demonstrates how to use the PostmanGenerator with real data
extracted from the SQL database.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_extractor import SQLDataExtractor, create_db_config_from_env
from postman_generator import PostmanGenerator

def generate_postman_collections_from_sql():
    """Generate Postman collections using real SQL data"""
    print("=== Generating Postman Collections from SQL Data ===\n")
    
    try:
        # 1. Create database configuration
        print("1. Creating database configuration...")
        db_config = create_db_config_from_env()
        print(f"   Database: {db_config.database} at {db_config.host}:{db_config.port}")
        
        # 2. Extract test data from SQL
        print("\n2. Extracting test data from SQL database...")
        extractor = SQLDataExtractor(db_config)
        
        try:
            test_data = extractor.extract_test_data()
            print(f"   ✓ Extracted data for {len(test_data['users'])} user roles")
            print(f"   ✓ Extracted {len(test_data['inventory'])} inventory categories")
            print(f"   ✓ Extracted {len(test_data['events']['all'])} events")
            print(f"   ✓ Extracted {len(test_data['test_mappings'])} test case mappings")
            
        finally:
            extractor.disconnect()
        
        # 3. Generate Postman collections
        print("\n3. Generating Postman collections...")
        generator = PostmanGenerator(test_data)
        
        results = generator.generate_all_collections()
        
        print(f"   ✓ Generated {len(results)} Postman collections:")
        for filename, filepath in results.items():
            print(f"     - {filename}")
        
        # 4. Generate summary report
        print("\n4. Generating summary report...")
        summary = generator.generate_collection_summary()
        
        print(f"\n=== Generation Summary ===")
        print(f"Timestamp: {summary['generation_timestamp']}")
        print(f"Total collections: {summary['total_collections']}")
        
        print(f"\nCollections generated:")
        for collection_name, details in summary['collections'].items():
            print(f"  {collection_name}:")
            print(f"    - Requests: {details['requests_count']}")
            print(f"    - Scenarios: {', '.join(details['test_scenarios'])}")
        
        print(f"\nData sources used:")
        print(f"  - Users by role: {summary['data_sources']['users_by_role']}")
        print(f"  - Inventory categories: {len(summary['data_sources']['inventory_categories'])}")
        print(f"  - Total events: {summary['data_sources']['events_total']}")
        print(f"  - Test mappings: {summary['data_sources']['test_mappings']}")
        
        print(f"\nEnvironment variables configured:")
        print(f"  - Role tokens: {len(summary['environment_variables']['role_tokens'])}")
        print(f"  - Resource IDs: {len(summary['environment_variables']['resource_ids'])}")
        print(f"  - Dynamic IDs: {len(summary['environment_variables']['dynamic_ids'])}")
        
        print("\n✅ Postman collections generated successfully!")
        print("\nNext steps:")
        print("1. Import the generated collections into Postman")
        print("2. Import the updated environment file")
        print("3. Run the authentication collection first to get tokens")
        print("4. Execute other collections to test the API with real data")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to generate Postman collections: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_usage_instructions():
    """Show instructions for using the generated collections"""
    print("\n=== Usage Instructions ===")
    print("\n1. Database Setup:")
    print("   - Ensure the database is running and populated with test data")
    print("   - Set environment variables: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
    print("   - Run the SQL scripts to populate test cases")
    
    print("\n2. Generate Collections:")
    print("   - Run this script to generate collections from current SQL data")
    print("   - Collections will be saved to api-gateway/postman/")
    print("   - Environment file will be updated with real IDs")
    
    print("\n3. Import to Postman:")
    print("   - Import all .postman_collection.json files")
    print("   - Import the Sistema-ONG-Environment.postman_environment.json file")
    print("   - Select the environment in Postman")
    
    print("\n4. Execute Tests:")
    print("   - Start with 01-Autenticacion to get authentication tokens")
    print("   - Run other collections in order")
    print("   - All requests use real IDs and data from your database")
    
    print("\n5. Regenerate When Needed:")
    print("   - Re-run this script whenever SQL test data changes")
    print("   - Collections will be updated with new real data")
    print("   - Previous versions are automatically backed up")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_usage_instructions()
    else:
        success = generate_postman_collections_from_sql()
        if not success:
            print("\nFor usage instructions, run: python example_postman_usage.py --help")
        sys.exit(0 if success else 1)