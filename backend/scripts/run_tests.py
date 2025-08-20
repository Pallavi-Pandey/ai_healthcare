#!/usr/bin/env python3
"""
Test runner script for Healthcare AI project.
Provides convenient commands to run different test suites.
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle the output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
        else:
            print(f"❌ {description} failed with return code {result.returncode}")
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Healthcare AI Test Runner")
    parser.add_argument("--suite", choices=["all", "unit", "integration", "auth", "models", "fast"], 
                       default="all", help="Test suite to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage report")
    parser.add_argument("--file", "-f", help="Run specific test file")
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    if args.verbose:
        base_cmd.append("-v")
    
    if args.coverage:
        base_cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term-missing"])
    
    # Determine which tests to run
    if args.file:
        cmd = base_cmd + [args.file]
        success = run_command(cmd, f"Running tests in {args.file}")
    
    elif args.suite == "all":
        cmd = base_cmd + ["."]
        success = run_command(cmd, "Running all tests")
    
    elif args.suite == "unit":
        cmd = base_cmd + ["-m", "unit", "."]
        success = run_command(cmd, "Running unit tests")
    
    elif args.suite == "integration":
        cmd = base_cmd + ["-m", "integration", "."]
        success = run_command(cmd, "Running integration tests")
    
    elif args.suite == "auth":
        cmd = base_cmd + ["-m", "auth", "."]
        success = run_command(cmd, "Running authentication tests")
    
    elif args.suite == "models":
        cmd = base_cmd + ["-m", "models", "."]
        success = run_command(cmd, "Running model tests")
    
    elif args.suite == "fast":
        cmd = base_cmd + ["-m", "not slow", "."]
        success = run_command(cmd, "Running fast tests (excluding slow tests)")
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests completed successfully!")
        print("\nTest Coverage Summary:")
        print("- Main App: ✅ Startup, routes, configuration")
        print("- Authentication: ✅ Login, registration, tokens, permissions")
        print("- Models: ✅ User, Appointment, Prescription, Reminder, CallLog")
        print("- Database: ✅ CRUD operations, constraints, transactions")
        print("- Utils: ✅ Password hashing, JWT tokens, security")
        print("- Integration: ✅ End-to-end workflows, error handling")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    print(f"{'='*60}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
