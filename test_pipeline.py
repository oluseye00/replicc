#!/usr/bin/env python
"""
RepliC Pipeline Testing Script

This script runs all the tests that would run in the CI/CD pipeline.
Use this for local development to ensure your code will pass CI.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*50}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)
        return False
    
    return True

def main():
    """Run all pipeline tests"""
    print("🚀 RepliC Pipeline Tests")
    print("This runs the same checks as the CI/CD pipeline")
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    tests = [
        ("python -m py_compile manage.py", "Python Syntax Check"),
        ("python manage.py check", "Django System Check"),
        ("python manage.py check --deploy", "Django Deployment Check"),
        ("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Flake8 Critical Errors"),
        ("black --check . --diff", "Black Code Formatting"),
        ("isort --check-only . --diff", "Import Sorting"),
        ("bandit -r . -x '*/migrations/*,*/venv/*,*/node_modules/*'", "Security Scan"),
        ("python manage.py test --keepdb --verbosity=2", "Django Tests"),
    ]
    
    results = []
    
    for cmd, description in tests:
        success = run_command(cmd, description)
        results.append((description, success))
    
    # Summary
    print(f"\n{'='*50}")
    print("PIPELINE TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n❌ Some tests failed. Fix these issues before pushing to Git.")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! Your code is ready for the pipeline.")
        sys.exit(0)

if __name__ == "__main__":
    main()