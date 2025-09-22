#!/usr/bin/env python3
"""
Test script for generate-testing-configs.py
Verifies basic functionality without requiring database connection
"""

import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path

def test_help_option():
    """Test that help option works"""
    print("Testing --help option...")
    result = subprocess.run([
        sys.executable, 
        "scripts/generate-testing-configs.py", 
        "--help"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Help option works")
        return True
    else:
        print(f"✗ Help option failed: {result.stderr}")
        return False

def test_list_backups_empty():
    """Test list backups with no backups"""
    print("Testing --list-backups with no backups...")
    result = subprocess.run([
        sys.executable,
        "scripts/generate-testing-configs.py",
        "--list-backups"
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and "No hay backups disponibles" in result.stdout:
        print("✓ List backups works (empty)")
        return True
    else:
        print(f"✗ List backups failed: {result.stderr}")
        return False

def test_dry_run():
    """Test dry run mode"""
    print("Testing --dry-run mode...")
    
    result = subprocess.run([
        sys.executable,
        "scripts/generate-testing-configs.py",
        "--all",
        "--dry-run"
    ], capture_output=True, text=True)
    
    # Dry run should work even without database connection
    # because it should skip database validation in dry-run mode
    if result.returncode == 0 and ("Modo dry-run" in result.stdout or "Modo dry-run" in result.stderr):
        print("✓ Dry run mode works")
        return True
    else:
        print(f"✗ Dry run failed. Return code: {result.returncode}")
        print(f"Output: {result.stdout}")
        print(f"Error: {result.stderr}")
        return False

def test_invalid_option():
    """Test invalid option handling"""
    print("Testing invalid option handling...")
    result = subprocess.run([
        sys.executable,
        "scripts/generate-testing-configs.py",
        "--invalid-option"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("✓ Invalid option properly rejected")
        return True
    else:
        print("✗ Invalid option not rejected")
        return False

def test_config_file_creation():
    """Test that default config file can be created"""
    print("Testing config file handling...")
    
    config_path = Path("scripts/sql-driven-testing/config.json")
    if config_path.exists():
        print("✓ Config file exists")
        
        # Validate JSON
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("✓ Config file is valid JSON")
            
            # Check required sections
            required_sections = ['database', 'backup', 'validation', 'generation']
            missing = [section for section in required_sections if section not in config]
            if not missing:
                print("✓ Config file has all required sections")
                return True
            else:
                print(f"✗ Config file missing sections: {missing}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"✗ Config file invalid JSON: {e}")
            return False
    else:
        print("✗ Config file does not exist")
        return False

def main():
    """Run all tests"""
    print("Testing generate-testing-configs.py script")
    print("=" * 50)
    
    tests = [
        test_help_option,
        test_list_backups_empty,
        test_dry_run,
        test_invalid_option,
        test_config_file_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == '__main__':
    sys.exit(main())