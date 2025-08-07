#!/usr/bin/env python3
"""
Test script to verify Alembic configuration is working correctly.
Run this from the orchestration service directory to test the migration setup.
"""

import sys
import os
import subprocess

def test_alembic_config():
    """Test that alembic configuration is valid"""
    print("🧪 Testing Alembic configuration...")
    
    try:
        # Test alembic can find our models
        result = subprocess.run(['alembic', 'check'], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print("✅ Alembic configuration is valid!")
            return True
        else:
            print(f"❌ Alembic configuration error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Alembic not found. Make sure it's installed: pip install alembic")
        return False

def test_migration_files():
    """Test that migration files exist and are valid"""
    print("🧪 Testing migration files...")
    
    versions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alembic', 'versions')
    
    if not os.path.exists(versions_dir):
        print(f"❌ Versions directory not found: {versions_dir}")
        return False
    
    migration_files = [f for f in os.listdir(versions_dir) if f.endswith('.py')]
    
    if not migration_files:
        print("❌ No migration files found in versions directory")
        return False
    
    print(f"✅ Found {len(migration_files)} migration files:")
    for f in migration_files:
        print(f"   - {f}")
    
    return True

def test_models_import():
    """Test that our models can be imported"""
    print("🧪 Testing model imports...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))
        from database.models import Base, WorkflowEvent, ExecutionSnapshot
        print("✅ Successfully imported database models!")
        print(f"   - Base metadata has {len(Base.metadata.tables)} tables")
        print(f"   - Tables: {list(Base.metadata.tables.keys())}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import models: {e}")
        return False

def main():
    print("🚀 Testing Alembic setup for orchestration service...\n")
    
    tests = [
        ("Model imports", test_models_import),
        ("Migration files", test_migration_files),
        ("Alembic configuration", test_alembic_config),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Alembic setup is ready.")
        print("💡 You can now run: alembic upgrade head")
        return 0
    else:
        print("\n💥 Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
