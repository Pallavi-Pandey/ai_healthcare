#!/usr/bin/env python3
"""
Simple Code Coverage Runner for Healthcare AI Project
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run tests with code coverage"""
    print("🏥 Healthcare AI - Code Coverage Analysis")
    print("=" * 50)
    
    # Simple coverage command
    cmd = [
        sys.executable, "-m", "pytest",
        "--cov=main",
        "--cov=models", 
        "--cov=schemas",
        "--cov=database",
        "--cov=utils",
        "--cov=routes",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v"
    ]
    
    print("Running tests with coverage...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ Coverage analysis completed successfully!")
            print("📊 HTML report generated: htmlcov/index.html")
            print("🎯 Focus on improving coverage for critical healthcare functions")
        else:
            print("\n❌ Coverage analysis failed")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running coverage: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
