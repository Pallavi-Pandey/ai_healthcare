#!/usr/bin/env python3
"""
Code Coverage Runner for Healthcare AI Project
Provides detailed coverage analysis and reporting
"""

import subprocess
import sys
import os
from pathlib import Path
import webbrowser

def run_coverage_command(cmd, description):
    """Run a coverage command and handle output"""
    print(f"\n{'='*60}")
    print(f"📊 {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main coverage runner"""
    print("🏥 Healthcare AI - Code Coverage Analysis")
    print("=" * 60)
    
    # Step 1: Install dependencies
    print("\n📦 Installing coverage dependencies...")
    install_cmd = [sys.executable, "-m", "pip", "install", "pytest-cov", "coverage"]
    if not run_coverage_command(install_cmd, "Installing coverage tools"):
        print("❌ Failed to install coverage dependencies")
        return 1
    
    # Step 2: Run tests with coverage
    print("\n🧪 Running tests with coverage analysis...")
    test_cmd = [
        sys.executable, "-m", "pytest",
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "-v"
    ]
    
    if not run_coverage_command(test_cmd, "Running tests with coverage"):
        print("❌ Tests failed or coverage analysis incomplete")
        return 1
    
    # Step 3: Generate detailed coverage report
    print("\n📈 Generating detailed coverage report...")
    report_cmd = [sys.executable, "-m", "coverage", "report", "--show-missing"]
    run_coverage_command(report_cmd, "Generating coverage report")
    
    # Step 4: Coverage summary
    print("\n" + "="*60)
    print("📊 COVERAGE ANALYSIS COMPLETE")
    print("="*60)
    
    # Check if HTML report was generated
    html_report = Path("htmlcov/index.html")
    if html_report.exists():
        print(f"✅ HTML Coverage Report: {html_report.absolute()}")
        print("   Open in browser to view detailed line-by-line coverage")
        
        # Ask if user wants to open in browser
        try:
            response = input("\n🌐 Open HTML coverage report in browser? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                webbrowser.open(f"file://{html_report.absolute()}")
                print("🚀 Coverage report opened in browser!")
        except KeyboardInterrupt:
            print("\n👋 Coverage analysis complete!")
    
    # Coverage targets for healthcare applications
    print("\n🎯 COVERAGE TARGETS FOR HEALTHCARE AI:")
    print("   • Critical paths (auth, data): 95%+")
    print("   • Business logic: 90%+") 
    print("   • Overall application: 85%+")
    print("   • Utilities and helpers: 80%+")
    
    print("\n📋 FILES ANALYZED:")
    print("   • main.py - FastAPI application")
    print("   • models.py - Database models")
    print("   • schemas.py - Pydantic schemas")
    print("   • database.py - Database configuration")
    print("   • routes/auth_routes.py - Authentication endpoints")
    print("   • utils/auth.py - Authentication utilities")
    
    print("\n🔍 COVERAGE REPORTS GENERATED:")
    print("   • Terminal output (above)")
    print("   • HTML report: htmlcov/index.html")
    print("   • XML report: coverage.xml (for CI/CD)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
