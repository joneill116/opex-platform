"""Run all tests for the orchestration service"""
import subprocess
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    print("Running Orchestration Service Tests...\n")
    
    # Change to the orchestration service directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests directly with python
    test_files = [
        "tests/engine/core/test_event_store_simple.py",
    ]
    
    failed = False
    
    for test_file in test_files:
        print(f"Running {test_file}...")
        result = subprocess.run([sys.executable, test_file])
        
        if result.returncode != 0:
            failed = True
            print(f"❌ {test_file} failed\n")
        else:
            print(f"✅ {test_file} passed\n")
    
    if failed:
        print("❌ Some tests failed")
        sys.exit(1)
    else:
        print("✅ All tests passed!")

if __name__ == "__main__":
    run_tests()
