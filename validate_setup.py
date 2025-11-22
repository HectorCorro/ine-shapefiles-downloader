#!/usr/bin/env python3
"""
Validation script for Mexico Electoral Analytics workspace
Run this after setting up the project to verify everything is configured correctly.
"""

import os
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists and print result"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists


def check_directory_exists(dirpath, description):
    """Check if a directory exists and print result"""
    exists = os.path.isdir(dirpath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {dirpath}")
    return exists


def main():
    print("🔍 Validating Mexico Electoral Analytics Workspace Setup\n")
    print("=" * 70)
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    all_checks = []
    
    # Check root configuration
    print("\n📄 Root Configuration Files:")
    all_checks.append(check_file_exists("pyproject.toml", "Root pyproject.toml"))
    all_checks.append(check_file_exists(".gitignore", "Git ignore file"))
    all_checks.append(check_file_exists("PROJECT_README.md", "Main documentation"))
    all_checks.append(check_file_exists("QUICKSTART.md", "Quick start guide"))
    
    # Check module structures
    print("\n📦 Ingestion Module:")
    all_checks.append(check_directory_exists("ingestion", "Ingestion directory"))
    all_checks.append(check_file_exists("ingestion/pyproject.toml", "Ingestion pyproject.toml"))
    all_checks.append(check_file_exists("ingestion/src/ingestion/__init__.py", "Ingestion __init__.py"))
    all_checks.append(check_file_exists("ingestion/src/ingestion/download_nacional.py", "Nacional scraper"))
    all_checks.append(check_file_exists("ingestion/src/ingestion/download_peepjf.py", "PEEPJF scraper"))
    all_checks.append(check_file_exists("ingestion/src/ingestion/utils/s3_utils.py", "S3 utilities"))
    
    print("\n📊 Analytics Module:")
    all_checks.append(check_directory_exists("analytics", "Analytics directory"))
    all_checks.append(check_file_exists("analytics/pyproject.toml", "Analytics pyproject.toml"))
    all_checks.append(check_file_exists("analytics/src/analytics/__init__.py", "Analytics __init__.py"))
    all_checks.append(check_file_exists("analytics/clean_votes.ipynb", "Vote cleaning notebook"))
    
    print("\n📈 Dashboard Module:")
    all_checks.append(check_directory_exists("dashboard", "Dashboard directory"))
    all_checks.append(check_file_exists("dashboard/pyproject.toml", "Dashboard pyproject.toml"))
    all_checks.append(check_file_exists("dashboard/src/dashboard/__init__.py", "Dashboard __init__.py"))
    all_checks.append(check_file_exists("dashboard/src/dashboard/kepler_visualization.py", "Kepler visualization"))
    
    print("\n🔧 Shared Configuration:")
    all_checks.append(check_directory_exists("shared", "Shared directory"))
    all_checks.append(check_file_exists("shared/config/estados.py", "Estados configuration"))
    
    print("\n💾 Data Directories:")
    all_checks.append(check_directory_exists("data", "Data root directory"))
    all_checks.append(check_directory_exists("data/raw", "Raw data directory"))
    all_checks.append(check_directory_exists("data/processed", "Processed data directory"))
    all_checks.append(check_directory_exists("data/insights", "Insights directory"))
    all_checks.append(check_directory_exists("data/geo", "Geo data directory"))
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(all_checks)
    total = len(all_checks)
    
    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        print("\n🎉 Your workspace is correctly configured!")
        print("\n📚 Next steps:")
        print("   1. Run: uv sync")
        print("   2. Read: cat QUICKSTART.md")
        print("   3. Test ingestion: cd ingestion && uv run python -m ingestion.download_peepjf")
    else:
        print(f"⚠️  Some checks failed: {passed}/{total} passed")
        print("\n🔧 To fix issues:")
        print("   1. Make sure you're in the project root directory")
        print("   2. Re-run the setup if needed")
        print("   3. Check PROJECT_README.md for manual setup instructions")
        return 1
    
    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())


