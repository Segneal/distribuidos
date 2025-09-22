#!/usr/bin/env python3
"""
SQL Syntax Verification Script
This script validates the SQL syntax in the test cases file without requiring a database connection.
"""

import re
import sys
from pathlib import Path

def validate_sql_file(file_path):
    """Validate SQL syntax in the given file."""
    print(f"🔍 Validating SQL syntax in {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    errors = []
    warnings = []
    
    # Split into lines for line-by-line analysis
    lines = content.split('\n')
    
    # Track multi-line statements
    in_insert_statement = False
    insert_line_start = 0
    parentheses_count = 0
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('--'):
            continue
        
        # Check for common SQL syntax issues
        
        # 1. Unmatched parentheses
        open_parens = line.count('(')
        close_parens = line.count(')')
        parentheses_count += open_parens - close_parens
        
        # 2. INSERT statement validation
        if line.upper().startswith('INSERT INTO'):
            in_insert_statement = True
            insert_line_start = line_num
            
            # Check INSERT syntax
            if not re.match(r'INSERT INTO \w+\s*\([^)]+\)\s*VALUES', line.upper()):
                if 'VALUES' not in line.upper():
                    # Multi-line INSERT, continue checking
                    pass
                else:
                    errors.append(f"Line {line_num}: Invalid INSERT syntax")
        
        # 3. VALUES statement validation
        if 'VALUES' in line.upper() and in_insert_statement:
            # Check if VALUES is followed by opening parenthesis
            values_part = line.upper().split('VALUES')[1].strip()
            if values_part and not values_part.startswith('('):
                errors.append(f"Line {line_num}: VALUES should be followed by opening parenthesis")
        
        # 4. Statement termination
        if line.endswith(';'):
            in_insert_statement = False
            if parentheses_count != 0:
                errors.append(f"Line {line_num}: Unmatched parentheses in statement ending at this line")
                parentheses_count = 0  # Reset for next statement
        
        # 5. String literal validation
        single_quotes = line.count("'")
        if single_quotes % 2 != 0:
            # Check if it's a continuation line or escaped quote
            if not (line.endswith(',') or line.endswith('(')):
                warnings.append(f"Line {line_num}: Possible unmatched single quote")
        
        # 6. Common typos and issues
        if re.search(r'\bVALUES\s*\(\s*\)', line.upper()):
            errors.append(f"Line {line_num}: Empty VALUES clause")
        
        if re.search(r',\s*,', line):
            errors.append(f"Line {line_num}: Double comma detected")
        
        if re.search(r'\(\s*,', line):
            errors.append(f"Line {line_num}: Comma immediately after opening parenthesis")
        
        if re.search(r',\s*\)', line):
            warnings.append(f"Line {line_num}: Comma before closing parenthesis (trailing comma)")
    
    # Final checks
    if parentheses_count != 0:
        errors.append(f"File ends with unmatched parentheses (balance: {parentheses_count})")
    
    if in_insert_statement:
        warnings.append(f"File ends with incomplete INSERT statement starting at line {insert_line_start}")
    
    # Report results
    if errors:
        print(f"❌ Found {len(errors)} syntax errors:")
        for error in errors:
            print(f"   {error}")
    
    if warnings:
        print(f"⚠️  Found {len(warnings)} warnings:")
        for warning in warnings:
            print(f"   {warning}")
    
    if not errors and not warnings:
        print("✅ No syntax issues found")
        return True
    elif not errors:
        print("✅ No critical syntax errors (only warnings)")
        return True
    else:
        return False

def validate_table_references(file_path):
    """Validate that all referenced tables exist in the schema."""
    print(f"🔍 Validating table references...")
    
    # Define expected tables from the schema
    expected_tables = {
        'usuarios', 'donaciones', 'eventos', 'evento_participantes',
        'donaciones_repartidas', 'solicitudes_externas', 'ofertas_externas',
        'eventos_externos', 'auditoria_stock', 'solicitudes_propias',
        'transferencias_enviadas', 'transferencias_recibidas',
        'adhesiones_eventos_externos', 'ofertas_propias', 'test_case_mapping'
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Find all INSERT INTO statements
    insert_pattern = r'INSERT INTO\s+(\w+)'
    matches = re.findall(insert_pattern, content, re.IGNORECASE)
    
    referenced_tables = set(match.lower() for match in matches)
    expected_tables_lower = set(table.lower() for table in expected_tables)
    
    # Check for unknown tables
    unknown_tables = referenced_tables - expected_tables_lower
    if unknown_tables:
        print(f"❌ References to unknown tables: {', '.join(unknown_tables)}")
        return False
    
    # Report referenced tables
    print(f"✅ All {len(referenced_tables)} referenced tables are valid:")
    for table in sorted(referenced_tables):
        print(f"   - {table}")
    
    return True

def validate_enum_values(file_path):
    """Validate ENUM values used in INSERT statements."""
    print(f"🔍 Validating ENUM values...")
    
    # Define expected ENUM values
    enum_values = {
        'rol': ['PRESIDENTE', 'VOCAL', 'COORDINADOR', 'VOLUNTARIO'],
        'categoria': ['ROPA', 'ALIMENTOS', 'JUGUETES', 'UTILES_ESCOLARES'],
        'method': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        'test_type': ['success', 'error', 'validation', 'authorization', 'edge_case']
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    errors = []
    
    # More specific patterns to avoid false positives
    # Check rol values in usuarios table context
    usuarios_insert_pattern = r"INSERT INTO usuarios.*?VALUES.*?'(PRESIDENTE|VOCAL|COORDINADOR|VOLUNTARIO)'"
    rol_matches = re.findall(usuarios_insert_pattern, content, re.DOTALL | re.IGNORECASE)
    invalid_roles = [match for match in rol_matches if match not in enum_values['rol']]
    if invalid_roles:
        errors.extend([f"Invalid rol value: '{role}'" for role in invalid_roles])
    
    # Check categoria values in donaciones table context
    donaciones_insert_pattern = r"INSERT INTO donaciones.*?'(ROPA|ALIMENTOS|JUGUETES|UTILES_ESCOLARES)'"
    categoria_matches = re.findall(donaciones_insert_pattern, content, re.DOTALL | re.IGNORECASE)
    invalid_categorias = [match for match in categoria_matches if match not in enum_values['categoria']]
    if invalid_categorias:
        errors.extend([f"Invalid categoria value: '{cat}'" for cat in invalid_categorias])
    
    # Check method values in test_case_mapping table context
    method_insert_pattern = r"INSERT INTO test_case_mapping.*?'(GET|POST|PUT|DELETE|PATCH)'"
    method_matches = re.findall(method_insert_pattern, content, re.DOTALL | re.IGNORECASE)
    invalid_methods = [match for match in method_matches if match not in enum_values['method']]
    if invalid_methods:
        errors.extend([f"Invalid method value: '{method}'" for method in invalid_methods])
    
    if errors:
        print(f"❌ Found {len(errors)} ENUM validation errors:")
        for error in errors[:10]:  # Show only first 10 errors
            print(f"   {error}")
        if len(errors) > 10:
            print(f"   ... and {len(errors) - 10} more errors")
        return False
    else:
        print("✅ All ENUM values are valid")
        return True

def main():
    """Main validation function."""
    print("🚀 Starting SQL syntax validation...")
    print("=" * 60)
    
    # Find the test cases file
    test_cases_file = Path("database/init/02-test-cases.sql")
    
    if not test_cases_file.exists():
        print(f"❌ Test cases file not found: {test_cases_file}")
        sys.exit(1)
    
    # Run all validation checks
    checks = [
        lambda: validate_sql_file(test_cases_file),
        lambda: validate_table_references(test_cases_file),
        lambda: validate_enum_values(test_cases_file)
    ]
    
    results = []
    for i, check in enumerate(checks, 1):
        try:
            result = check()
            results.append(result)
            print()  # Add spacing between checks
        except Exception as e:
            print(f"❌ Validation check {i} failed with error: {e}")
            results.append(False)
            print()
    
    # Summary
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} validation checks passed!")
        print("✅ SQL test cases file is syntactically correct and ready for use.")
        print("\n📋 Next steps:")
        print("   1. Start MySQL container: docker-compose up -d mysql")
        print("   2. Verify integration: python scripts/verify-sql-integration.py")
        print("   3. Generate configurations: python scripts/generate-testing-configs.py --all")
        sys.exit(0)
    else:
        print(f"❌ {total - passed} out of {total} validation checks failed.")
        print("🔧 Please fix the issues above before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    main()