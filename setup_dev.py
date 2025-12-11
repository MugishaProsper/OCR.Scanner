#!/usr/bin/env python3
"""
Development setup script for OCR Scanner.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("OCR Scanner - Development Environment Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("⚠ Warning: Not in a virtual environment")
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() not in ['y', 'yes']:
            print("Please create and activate a virtual environment first:")
            print("  python -m venv venv")
            print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
            sys.exit(1)
    else:
        print("✓ Virtual environment detected")
    
    # Install development dependencies
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -e .", "Installing package in development mode"),
        ("pip install -r requirements-dev.txt", "Installing development dependencies"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print(f"Setup failed at: {desc}")
            sys.exit(1)
    
    # Run initial tests
    print("\nRunning initial tests...")
    if run_command("python -m pytest tests/ -v", "Running test suite"):
        print("✓ All tests passed")
    else:
        print("⚠ Some tests failed - this might be expected for a new setup")
    
    # Check code quality
    print("\nChecking code quality...")
    run_command("python -m flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics", "Basic syntax check")
    
    print("\n" + "=" * 50)
    print("Development environment setup completed!")
    print("\nAvailable commands:")
    print("  make test          - Run tests")
    print("  make lint          - Run linting")
    print("  make format        - Format code")
    print("  make run           - Run application")
    print("  ocr-scanner        - Run installed application")
    print("\nHappy coding! 🚀")


if __name__ == "__main__":
    main()