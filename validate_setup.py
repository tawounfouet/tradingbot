#!/usr/bin/env python3
"""
Crypto Trading Bot - Installation and Setup Validation Script

This script validates that the project has been set up correctly with all
dependencies, configuration files, and basic functionality working.
"""

import sys
import subprocess
import importlib
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11+"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(
            f"   ❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.11+"
        )
        return False


def check_required_files():
    """Check if all required configuration files exist"""
    print("\n📁 Checking required files...")
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        "Makefile",
        "Dockerfile",
        "docker-compose.yml",
        ".env",
        ".flake8",
        ".pre-commit-config.yaml",
        "src/tradingbot/main.py",
        "src/tradingbot/config/settings.py",
    ]

    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Missing")
            all_exist = False

    return all_exist


def check_dependencies():
    """Check if key dependencies can be imported"""
    print("\n📦 Checking key dependencies...")
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "pandas",
        "numpy",
    ]

    all_imported = True
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Not installed")
            all_imported = False

    return all_imported


def check_project_structure():
    """Check if the project structure is correct"""
    print("\n🏗️ Checking project structure...")
    required_dirs = [
        "src/tradingbot",
        "src/tradingbot/config",
        "src/tradingbot/models",
        "src/tradingbot/schemas",
        "src/tradingbot/services",
        "src/tradingbot/routers",
        "src/tradingbot/strategies",
        "src/tradingbot/database",
    ]

    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ - Missing")
            all_exist = False

    return all_exist


def check_app_import():
    """Check if the main application can be imported"""
    print("\n🚀 Checking application import...")
    try:
        # Test import via subprocess to avoid import path issues
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; import os; os.chdir('src/tradingbot'); import main; print('Import successful')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=".",
        )

        if result.returncode == 0 and "Import successful" in result.stdout:
            print("   ✅ FastAPI app imported successfully")
            return True
        else:
            print(
                f"   ❌ Failed to import app: {result.stderr.strip() if result.stderr else 'Unknown error'}"
            )
            return False
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        return False


def run_basic_tests():
    """Run basic functionality tests"""
    print("\n🧪 Running basic tests...")
    try:
        # Try to run a quick test
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; sys.path.insert(0, 'src'); from tradingbot.config.settings import get_settings; settings = get_settings(); print('Settings loaded successfully')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("   ✅ Configuration loading test passed")
            return True
        else:
            print(f"   ❌ Configuration test failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Test execution failed: {e}")
        return False


def main():
    """Main validation function"""
    print("🔍 Crypto Trading Bot - Setup Validation")
    print("=" * 50)

    tests = [
        check_python_version,
        check_required_files,
        check_project_structure,
        check_dependencies,
        check_app_import,
        run_basic_tests,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    if all(results):
        print("🎉 ALL TESTS PASSED! Your setup is ready to go!")
        print("\n🚀 Quick Start Commands:")
        print("   make run          # Start the development server")
        print("   make test         # Run tests")
        print("   make docker-up    # Start with Docker")
        print("   make help         # Show all commands")
        return 0
    else:
        print(f"❌ {total - passed} out of {total} tests failed.")
        print("\n🔧 Please fix the issues above and run the validation again.")
        return 1


if __name__ == "__main__":
    exit(main())
