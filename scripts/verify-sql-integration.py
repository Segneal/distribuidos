#!/usr/bin/env python3
"""
Verification script for SQL-driven testing integration.
This script verifies that the test data was loaded correctly and the system is ready for testing.
"""

import mysql.connector
import json
import sys
from datetime import datetime

def get_db_connection():
    """Get database connection using docker-compose configuration."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3308,  # Docker mapped port
            database='ong_sistema',
            user='ong_user',
            password='ong_password'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        return None

def verify_test_users(cursor):
    """Verify test users were created correctly."""
    print("🔍 Verifying test users...")
    
    cursor.execute("""
        SELECT rol, COUNT(*) as count, GROUP_CONCAT(nombre_usuario) as users
        FROM usuarios 
        WHERE nombre_usuario LIKE 'test_%' 
        GROUP BY rol
        ORDER BY rol
    """)
    
    results = cursor.fetchall()
    if not results:
        print("❌ No test users found!")
        return False
    
    expected_roles = {'PRESIDENTE': 1, 'VOCAL': 2, 'COORDINADOR': 2, 'VOLUNTARIO': 2}
    actual_roles = {row[0]: row[1] for row in results}
    
    success = True
    for role, expected_count in expected_roles.items():
        actual_count = actual_roles.get(role, 0)
        if actual_count >= expected_count:
            print(f"✅ {role}: {actual_count} users")
        else:
            print(f"❌ {role}: Expected at least {expected_count}, got {actual_count}")
            success = False
    
    return success

def verify_test_donations(cursor):
    """Verify test donations were created correctly."""
    print("🔍 Verifying test donations...")
    
    cursor.execute("""
        SELECT categoria, COUNT(*) as count, SUM(cantidad) as total_stock
        FROM donaciones 
        WHERE usuario_alta LIKE 'test_%' 
        GROUP BY categoria
        ORDER BY categoria
    """)
    
    results = cursor.fetchall()
    if not results:
        print("❌ No test donations found!")
        return False
    
    expected_categories = ['ALIMENTOS', 'ROPA', 'JUGUETES', 'UTILES_ESCOLARES']
    actual_categories = [row[0] for row in results]
    
    success = True
    for category in expected_categories:
        if category in actual_categories:
            row = next(r for r in results if r[0] == category)
            print(f"✅ {category}: {row[1]} items, {row[2]} total stock")
        else:
            print(f"❌ Missing category: {category}")
            success = False
    
    return success

def verify_test_events(cursor):
    """Verify test events were created correctly."""
    print("🔍 Verifying test events...")
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN fecha_hora > NOW() THEN 'future'
                WHEN fecha_hora < NOW() THEN 'past'
                ELSE 'present'
            END as time_category,
            COUNT(*) as count
        FROM eventos 
        WHERE usuario_alta LIKE 'test_%' 
        GROUP BY time_category
        ORDER BY time_category
    """)
    
    results = cursor.fetchall()
    if not results:
        print("❌ No test events found!")
        return False
    
    time_categories = {row[0]: row[1] for row in results}
    
    success = True
    if time_categories.get('future', 0) > 0:
        print(f"✅ Future events: {time_categories['future']}")
    else:
        print("❌ No future events found")
        success = False
    
    if time_categories.get('past', 0) > 0:
        print(f"✅ Past events: {time_categories['past']}")
    else:
        print("⚠️  No past events found")
    
    return success

def verify_inter_ong_data(cursor):
    """Verify inter-ONG network data was created correctly."""
    print("🔍 Verifying inter-ONG network data...")
    
    tables = [
        ('solicitudes_externas', 'External donation requests'),
        ('ofertas_externas', 'External donation offers'),
        ('eventos_externos', 'External events')
    ]
    
    success = True
    for table, description in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ {description}: {count} records")
        else:
            print(f"❌ {description}: No records found")
            success = False
    
    return success

def verify_test_case_mapping(cursor):
    """Verify test case mapping table was created and populated."""
    print("🔍 Verifying test case mapping...")
    
    cursor.execute("""
        SELECT test_category, COUNT(*) as count
        FROM test_case_mapping 
        GROUP BY test_category
        ORDER BY test_category
    """)
    
    results = cursor.fetchall()
    if not results:
        print("❌ No test case mappings found!")
        return False
    
    expected_categories = ['auth', 'users', 'inventory', 'events', 'network']
    actual_categories = [row[0] for row in results]
    
    success = True
    for category in expected_categories:
        if category in actual_categories:
            row = next(r for r in results if r[0] == category)
            print(f"✅ {category}: {row[1]} test cases")
        else:
            print(f"⚠️  Missing test category: {category}")
    
    total_cases = sum(row[1] for row in results)
    print(f"📊 Total test cases: {total_cases}")
    
    return success

def verify_data_integrity(cursor):
    """Verify data integrity and foreign key relationships."""
    print("🔍 Verifying data integrity...")
    
    # Check foreign key relationships
    integrity_checks = [
        ("evento_participantes -> usuarios", """
            SELECT COUNT(*) FROM evento_participantes ep 
            LEFT JOIN usuarios u ON ep.usuario_id = u.id 
            WHERE u.id IS NULL
        """),
        ("evento_participantes -> eventos", """
            SELECT COUNT(*) FROM evento_participantes ep 
            LEFT JOIN eventos e ON ep.evento_id = e.id 
            WHERE e.id IS NULL
        """),
        ("donaciones_repartidas -> eventos", """
            SELECT COUNT(*) FROM donaciones_repartidas dr 
            LEFT JOIN eventos e ON dr.evento_id = e.id 
            WHERE e.id IS NULL
        """),
        ("donaciones_repartidas -> donaciones", """
            SELECT COUNT(*) FROM donaciones_repartidas dr 
            LEFT JOIN donaciones d ON dr.donacion_id = d.id 
            WHERE d.id IS NULL
        """)
    ]
    
    success = True
    for check_name, query in integrity_checks:
        cursor.execute(query)
        orphaned_count = cursor.fetchone()[0]
        
        if orphaned_count == 0:
            print(f"✅ {check_name}: No orphaned records")
        else:
            print(f"❌ {check_name}: {orphaned_count} orphaned records")
            success = False
    
    return success

def main():
    """Main verification function."""
    print("🚀 Starting SQL-driven testing integration verification...")
    print("=" * 60)
    
    # Connect to database
    connection = get_db_connection()
    if not connection:
        print("❌ Cannot connect to database. Make sure MySQL container is running.")
        sys.exit(1)
    
    cursor = connection.cursor()
    
    # Run all verification checks
    checks = [
        verify_test_users,
        verify_test_donations,
        verify_test_events,
        verify_inter_ong_data,
        verify_test_case_mapping,
        verify_data_integrity
    ]
    
    results = []
    for check in checks:
        try:
            result = check(cursor)
            results.append(result)
            print()  # Add spacing between checks
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            results.append(False)
            print()
    
    # Close connection
    cursor.close()
    connection.close()
    
    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} verification checks passed!")
        print("✅ SQL-driven testing integration is working correctly.")
        print("\n📋 Next steps:")
        print("   1. Generate testing configurations: python scripts/generate-testing-configs.py --all")
        print("   2. Run integration tests: python scripts/sql-driven-testing/run_tests.py")
        print("   3. Start using the generated Postman collections and Swagger examples")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} out of {total} checks failed.")
        print("🔧 Please review the errors above and fix the issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()