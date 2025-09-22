#!/usr/bin/env python3
"""
Example Usage of SQL Data Extractor
Sistema ONG - SQL Driven Testing

This script demonstrates how to use the SQLDataExtractor to extract
test data from the database and use it for testing configuration generation.
"""

import json
import os
from data_extractor import SQLDataExtractor, create_db_config_from_env

def demonstrate_basic_usage():
    """Demonstrate basic data extraction"""
    print("=== Basic Data Extraction ===")
    
    # Create database configuration from environment variables
    db_config = create_db_config_from_env()
    print(f"Connecting to database: {db_config.host}:{db_config.port}/{db_config.database}")
    
    # Create extractor instance
    extractor = SQLDataExtractor(db_config)
    
    try:
        # Extract all test data
        print("Extracting test data...")
        test_data = extractor.extract_test_data()
        
        # Print summary
        print("\n--- Extraction Summary ---")
        print(f"Users by role: {list(test_data['users'].keys())}")
        for role, users in test_data['users'].items():
            print(f"  {role}: {len(users)} users")
        
        print(f"\nInventory categories: {list(test_data['inventory'].keys())}")
        for category, data in test_data['inventory'].items():
            total = len(data['all'])
            high = len(data['high_stock'])
            low = len(data['low_stock'])
            zero = len(data['zero_stock'])
            print(f"  {category}: {total} total ({high} high stock, {low} low stock, {zero} zero stock)")
        
        print(f"\nEvents: {len(test_data['events']['all'])} total")
        print(f"  Future: {len(test_data['events']['future'])}")
        print(f"  Past: {len(test_data['events']['past'])}")
        print(f"  Current: {len(test_data['events']['current'])}")
        
        print(f"\nTest mappings: {len(test_data['test_mappings'])} cases")
        categories = {}
        for mapping in test_data['test_mappings']:
            cat = mapping['test_category']
            categories[cat] = categories.get(cat, 0) + 1
        for category, count in categories.items():
            print(f"  {category}: {count} test cases")
        
        print(f"\nNetwork data:")
        network = test_data['network']
        print(f"  External requests: {len(network['external_requests'])}")
        print(f"  External offers: {len(network['external_offers'])}")
        print(f"  External events: {len(network['external_events'])}")
        print(f"  Own requests: {len(network['own_requests'])}")
        print(f"  Transfers sent: {len(network['transfers_sent'])}")
        
        return test_data
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        raise
    finally:
        extractor.disconnect()

def demonstrate_specific_extractions(test_data):
    """Demonstrate how to work with specific extracted data"""
    print("\n=== Working with Specific Data ===")
    
    # Work with users
    print("\n--- User Data ---")
    if 'PRESIDENTE' in test_data['users']:
        presidente = test_data['users']['PRESIDENTE'][0]
        print(f"Test President: {presidente['nombre']} {presidente['apellido']} ({presidente['nombre_usuario']})")
        print(f"  Email: {presidente['email']}")
        print(f"  Password: {presidente['password_plain']}")
    
    # Work with inventory
    print("\n--- Inventory Data ---")
    if 'ALIMENTOS' in test_data['inventory']:
        alimentos = test_data['inventory']['ALIMENTOS']
        if alimentos['high_stock']:
            high_stock_item = alimentos['high_stock'][0]
            print(f"High stock food item: {high_stock_item['descripcion']} (Qty: {high_stock_item['cantidad']})")
        
        if alimentos['zero_stock']:
            zero_stock_item = alimentos['zero_stock'][0]
            print(f"Zero stock food item: {zero_stock_item['descripcion']} (Qty: {zero_stock_item['cantidad']})")
    
    # Work with events
    print("\n--- Event Data ---")
    if test_data['events']['future']:
        future_event = test_data['events']['future'][0]
        print(f"Future event: {future_event['nombre']}")
        print(f"  Date: {future_event['fecha_hora']}")
        print(f"  Participants: {len(future_event['participantes'])}")
    
    # Work with test mappings
    print("\n--- Test Case Examples ---")
    auth_cases = [m for m in test_data['test_mappings'] if m['test_category'] == 'authentication']
    if auth_cases:
        login_case = auth_cases[0]
        print(f"Authentication test: {login_case['description']}")
        print(f"  Endpoint: {login_case['method']} {login_case['endpoint']}")
        print(f"  Expected status: {login_case['expected_status']}")
        if login_case['request_body']:
            print(f"  Request body: {json.dumps(login_case['request_body'], indent=2)}")

def demonstrate_utility_methods():
    """Demonstrate utility methods"""
    print("\n=== Utility Methods ===")
    
    db_config = create_db_config_from_env()
    extractor = SQLDataExtractor(db_config)
    
    try:
        extractor.connect()
        
        # Get specific user
        user = extractor.get_user_by_id(1)
        if user:
            print(f"User ID 1: {user['nombre']} {user['apellido']} ({user['rol']})")
        
        # Get specific donation
        donation = extractor.get_donation_by_id(101)
        if donation:
            print(f"Donation ID 101: {donation['descripcion']} (Qty: {donation['cantidad']})")
        
        # Get test cases by category
        auth_cases = extractor.get_test_cases_by_category('authentication')
        print(f"Authentication test cases: {len(auth_cases)}")
        
        # Get test cases by endpoint
        login_cases = extractor.get_test_cases_by_endpoint('/api/auth/login')
        print(f"Login endpoint test cases: {len(login_cases)}")
        
    except Exception as e:
        print(f"Error in utility methods: {e}")
    finally:
        extractor.disconnect()

def save_sample_data(test_data):
    """Save sample extracted data to file for inspection"""
    print("\n=== Saving Sample Data ===")
    
    # Create a sample with limited data for readability
    sample_data = {
        'users': {
            role: users[:1] for role, users in test_data['users'].items()  # First user of each role
        },
        'inventory': {
            category: {
                'high_stock': data['high_stock'][:1],
                'low_stock': data['low_stock'][:1],
                'zero_stock': data['zero_stock'][:1],
                'total_count': len(data['all'])
            }
            for category, data in test_data['inventory'].items()
        },
        'events': {
            'future': test_data['events']['future'][:2],
            'past': test_data['events']['past'][:1],
            'total_count': len(test_data['events']['all'])
        },
        'test_mappings': test_data['test_mappings'][:5],  # First 5 test cases
        'network_summary': {
            'external_requests_count': len(test_data['network']['external_requests']),
            'external_offers_count': len(test_data['network']['external_offers']),
            'external_events_count': len(test_data['network']['external_events']),
            'sample_external_request': test_data['network']['external_requests'][0] if test_data['network']['external_requests'] else None
        }
    }
    
    output_file = "sample_extracted_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print(f"Sample data saved to: {output_file}")

def main():
    """Main demonstration function"""
    print("SQL Data Extractor - Example Usage")
    print("=" * 50)
    
    try:
        # Basic extraction
        test_data = demonstrate_basic_usage()
        
        # Work with specific data
        demonstrate_specific_extractions(test_data)
        
        # Utility methods
        demonstrate_utility_methods()
        
        # Save sample data
        save_sample_data(test_data)
        
        print("\n✅ Example completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())