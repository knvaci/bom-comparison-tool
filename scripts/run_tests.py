#!/usr/bin/env python3
"""
Test runner for BOM Comparison Tool QA testing
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_unit_tests():
    """Run unit tests"""
    print("Running unit tests...")
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/unit/", "-v"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running unit tests: {e}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("Running integration tests...")
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/integration/", "-v"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running integration tests: {e}")
        return False

def run_qa_tests():
    """Run QA test scenarios"""
    print("Running QA test scenarios...")
    
    # Test file upload functionality
    print("Testing file upload...")
    # Add specific QA test scenarios here
    
    return True

def test_application_startup():
    """Test if the application can start properly"""
    print("Testing application startup...")
    try:
        # Import the app to check for syntax errors
        import sys
        sys.path.append('.')
        from app import app
        print("✓ Application imports successfully")
        return True
    except Exception as e:
        print(f"✗ Application startup failed: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("Testing dependencies...")
    required_packages = [
        'flask', 'pandas', 'openpyxl', 'xlrd', 
        'sqlalchemy', 'psycopg2', 'werkzeug'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {missing_packages}")
        return False
    return True

def generate_test_report(results):
    """Generate a test report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
=== BOM Comparison Tool Test Report ===
Generated: {timestamp}

Test Results:
- Dependencies: {'PASS' if results['dependencies'] else 'FAIL'}
- Application Startup: {'PASS' if results['startup'] else 'FAIL'}
- Unit Tests: {'PASS' if results['unit_tests'] else 'FAIL'}
- Integration Tests: {'PASS' if results['integration_tests'] else 'FAIL'}
- QA Tests: {'PASS' if results['qa_tests'] else 'FAIL'}

Overall Status: {'ALL TESTS PASSED' if all(results.values()) else 'SOME TESTS FAILED'}
"""
    
    # Save report to file
    with open('test_report.txt', 'w') as f:
        f.write(report)
    
    print(report)
    return all(results.values())

def main():
    """Main test runner"""
    print("Starting BOM Comparison Tool QA Testing...")
    print("=" * 50)
    
    results = {}
    
    # Run tests
    results['dependencies'] = test_dependencies()
    results['startup'] = test_application_startup()
    results['unit_tests'] = run_unit_tests()
    results['integration_tests'] = run_integration_tests()
    results['qa_tests'] = run_qa_tests()
    
    # Generate report
    success = generate_test_report(results)
    
    if success:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main() 