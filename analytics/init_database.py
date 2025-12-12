#!/usr/bin/env python3
"""
Initialize Electoral Database
==============================

This script initializes the SQLite database for electoral data.

The database is created automatically in: data/processed/electoral_data.db

Usage:
    # Using uv
    uv run python analytics/init_database.py
    
    # Or with custom path
    uv run python analytics/init_database.py --db-path custom/path/elections.db
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analytics.clean_votes import ElectoralDatabase, get_default_db_path


def initialize_database(db_path: str = None):
    """
    Initialize the electoral database.
    
    Args:
        db_path: Path to database file (optional)
    """
    if db_path is None:
        db_path = str(get_default_db_path())
    
    print("="*60)
    print("ELECTORAL DATABASE INITIALIZATION")
    print("="*60)
    
    # Resolve path
    db_path_obj = Path(db_path).resolve()
    
    print(f"\nDatabase location: {db_path_obj}")
    print(f"Parent directory: {db_path_obj.parent}")
    
    # Check if database already exists
    if db_path_obj.exists():
        print(f"\n⚠️  Database already exists!")
        print(f"   File size: {db_path_obj.stat().st_size:,} bytes")
        
        # Ask user if they want to continue
        response = input("\nDo you want to re-initialize (keeps existing data)? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("\n✓ Keeping existing database")
            return
    
    # Initialize database
    print("\n[1/2] Creating database and directories...")
    db = ElectoralDatabase(str(db_path))
    print(f"✓ Database created at: {db.db_path}")
    
    # Verify structure
    print("\n[2/2] Verifying database structure...")
    try:
        elections = db.list_elections()
        print(f"✓ Metadata table exists")
        print(f"✓ Current elections in database: {len(elections)}")
        
        if len(elections) > 0:
            print("\nExisting elections:")
            print(elections[['election_name', 'entidad_id', 'row_count', 'created_at']].to_string(index=False))
    except Exception as e:
        print(f"✗ Error verifying database: {e}")
        return
    
    print("\n" + "="*60)
    print("✅ DATABASE READY!")
    print("="*60)
    print(f"\nYou can now process electoral data:")
    print(f"\n  from analytics.clean_votes import CleanVotesOrchestrator")
    print(f"  orchestrator = CleanVotesOrchestrator()")
    print(f"  orchestrator.process_electoral_file('data/raw/electoral/2024/PRES_2024.csv')")
    print("\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Initialize electoral SQLite database'
    )
    
    parser.add_argument(
        '--db-path',
        help='Path to database file (default: data/processed/electoral_data.db)',
        default=None
    )
    
    parser.add_argument(
        '--show-path',
        action='store_true',
        help='Show default database path and exit'
    )
    
    args = parser.parse_args()
    
    if args.show_path:
        default_path = get_default_db_path()
        print(f"Default database path: {default_path}")
        print(f"Absolute path: {default_path.resolve()}")
        return
    
    initialize_database(args.db_path)


if __name__ == '__main__':
    main()

