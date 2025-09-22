#!/usr/bin/env python3
"""
Example Usage of SwaggerGenerator
Sistema ONG - SQL Driven Testing

This script demonstrates how to use the SwaggerGenerator to update
Swagger documentation examples with real data from the SQL database.
"""

import os
import sys
import json
from data_extractor import SQLDataExtractor, create_db_config_from_env
from swagger_generator import SwaggerGenerator

def main():
    """Example usage of SwaggerGenerator with real database data"""
    
    print("=== Swagger Examples Generator - Example Usage ===\n")
    
    # Step 1: Extract data from SQL database
    print("1. Extracting test data from SQL database...")
    
    try:
        # Create database configuration
        db_config = create_db_config_from_env()
        print(f"   Database: {db_config.host}:{db_config.port}/{db_config.database}")
        
        # Extract test data
        extractor = SQLDataExtractor(db_config)
        extracted_data = extractor.extract_test_data()
        
        print(f"   ✓ Extracted data from {len(extracted_data)} categories")
        print(f"   ✓ Users: {sum(len(users) for users in extracted_data['users'].values())} across {len(extracted_data['users'])} roles")
        print(f"   ✓ Inventory: {len(extracted_data['inventory'])} categories")
        print(f"   ✓ Events: {len(extracted_data['events']['all'])} total events")
        print(f"   ✓ Network: {len(extracted_data['network']['external_requests'])} external requests")
        
    except Exception as e:
        print(f"   ✗ Error extracting data: {e}")
        print("   Make sure the database is running and populated with test data")
        return False
    finally:
        extractor.disconnect()
    
    # Step 2: Generate Swagger examples
    print("\n2. Generating Swagger examples from extracted data...")
    
    try:
        # Create SwaggerGenerator
        generator = SwaggerGenerator(extracted_data)
        
        # Check if Swagger config exists
        if not os.path.exists(generator.swagger_config_path):
            print(f"   ✗ Swagger config not found: {generator.swagger_config_path}")
            print("   Make sure the API Gateway is properly set up")
            return False
        
        print(f"   ✓ Found Swagger config: {generator.swagger_config_path}")
        
        # Generate examples for each category
        print("   Generating examples by category:")
        
        auth_examples = generator.generate_auth_examples()
        print(f"     - Authentication: {len(auth_examples)} examples")
        
        users_examples = generator.generate_users_examples()
        print(f"     - Users: {len(users_examples)} examples")
        
        inventory_examples = generator.generate_inventory_examples()
        print(f"     - Inventory: {len(inventory_examples)} examples")
        
        events_examples = generator.generate_events_examples()
        print(f"     - Events: {len(events_examples)} examples")
        
        network_examples = generator.generate_network_examples()
        print(f"     - Network: {len(network_examples)} examples")
        
        total_examples = (len(auth_examples) + len(users_examples) + 
                         len(inventory_examples) + len(events_examples) + 
                         len(network_examples))
        print(f"   ✓ Generated {total_examples} total examples")
        
    except Exception as e:
        print(f"   ✗ Error generating examples: {e}")
        return False
    
    # Step 3: Show sample examples
    print("\n3. Sample generated examples:")
    
    try:
        # Show authentication example
        login_example = auth_examples['LoginRequest']
        print(f"\n   Authentication Example:")
        print(f"   Summary: {login_example['summary']}")
        print(f"   Username: {login_example['value']['identificador']}")
        print(f"   Password: {login_example['value']['clave']}")
        
        # Show inventory example
        donation_example = inventory_examples['DonacionStockAlto']
        print(f"\n   High Stock Donation Example:")
        print(f"   Summary: {donation_example['summary']}")
        print(f"   ID: {donation_example['value']['id']}")
        print(f"   Category: {donation_example['value']['categoria']}")
        print(f"   Description: {donation_example['value']['descripcion']}")
        print(f"   Quantity: {donation_example['value']['cantidad']}")
        
        # Show event example
        if 'EventoFuturo' in events_examples and events_examples['EventoFuturo']['value']:
            event_example = events_examples['EventoFuturo']
            print(f"\n   Future Event Example:")
            print(f"   Summary: {event_example['summary']}")
            print(f"   ID: {event_example['value']['id']}")
            print(f"   Name: {event_example['value']['nombre']}")
            print(f"   Date: {event_example['value']['fechaHora']}")
        
    except Exception as e:
        print(f"   ✗ Error displaying examples: {e}")
        return False
    
    # Step 4: Update Swagger configuration (optional)
    print("\n4. Update Swagger configuration? (y/n): ", end="")
    
    try:
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            print("   Updating Swagger configuration...")
            
            # Perform the update
            result = generator.update_swagger_examples()
            
            print(f"   ✓ Updated {result['total_examples']} examples")
            print(f"   ✓ Backup created: {result['backup_created']}")
            print(f"   ✓ Validation passed: {result['validation_passed']}")
            
            if result['validation_passed']:
                print("   ✓ Swagger configuration updated successfully!")
                print(f"   Updated categories: {', '.join(result['examples_updated'])}")
            else:
                print("   ⚠ Validation warnings found, but update completed")
            
        else:
            print("   Skipping Swagger configuration update")
            
    except KeyboardInterrupt:
        print("\n   Update cancelled by user")
        return False
    except Exception as e:
        print(f"   ✗ Error updating Swagger configuration: {e}")
        return False
    
    # Step 5: Save examples to file for inspection
    print("\n5. Saving examples to file for inspection...")
    
    try:
        all_examples = {
            'authentication': auth_examples,
            'users': users_examples,
            'inventory': inventory_examples,
            'events': events_examples,
            'network': network_examples
        }
        
        output_file = "scripts/sql-driven-testing/generated_swagger_examples.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_examples, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ Examples saved to: {output_file}")
        print(f"   File size: {os.path.getsize(output_file)} bytes")
        
    except Exception as e:
        print(f"   ✗ Error saving examples: {e}")
        return False
    
    print("\n=== Swagger Examples Generation Complete ===")
    print("\nNext steps:")
    print("1. Review the generated examples in the JSON file")
    print("2. Test the updated Swagger documentation")
    print("3. Verify examples work with the actual API")
    print("4. Run integration tests to validate functionality")
    
    return True

def show_help():
    """Show help information"""
    print("Swagger Examples Generator - Help")
    print("=" * 40)
    print()
    print("This script generates Swagger documentation examples using real data")
    print("from the SQL database populated by the test cases.")
    print()
    print("Prerequisites:")
    print("1. Database must be running and populated with test data")
    print("2. Environment variables must be set for database connection:")
    print("   - DB_HOST (default: localhost)")
    print("   - DB_PORT (default: 3306)")
    print("   - DB_NAME (default: ong_sistema)")
    print("   - DB_USER (default: ong_user)")
    print("   - DB_PASSWORD (default: ong_password)")
    print("3. API Gateway Swagger configuration must exist")
    print()
    print("Usage:")
    print("  python example_swagger_usage.py        # Run interactive example")
    print("  python example_swagger_usage.py --help # Show this help")
    print()
    print("The script will:")
    print("1. Extract test data from the SQL database")
    print("2. Generate Swagger examples for all API categories")
    print("3. Optionally update the Swagger configuration file")
    print("4. Save generated examples to a JSON file for review")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        show_help()
    else:
        success = main()
        sys.exit(0 if success else 1)