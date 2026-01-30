#!/usr/bin/env python3
"""
Auto-Inference Example
======================

Demonstrates automatic election name and date inference from file paths.

This script shows how the system automatically extracts:
- Election type (PRES, DIP_FED, SEN, GOB)
- Year
- Full date (if available in path)

from file paths like:
- data/raw/electoral/2024/PRES_2024.csv
- data/raw/electoral/2021/DIP_FED_2021.xlsx
- data/raw/electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv

Usage:
    uv run python analytics/examples/auto_infer_example.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))

from analytics.clean_votes import CleanVotesOrchestrator, infer_election_metadata


def demo_inference():
    """Demonstrate automatic inference of election metadata."""
    
    print("="*70)
    print("AUTOMATIC ELECTION METADATA INFERENCE")
    print("="*70)
    
    # Example file paths
    test_paths = [
        "data/raw/electoral/2024/PRES_2024.csv",
        "data/raw/electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv",
        "data/raw/electoral/2021/DIP_FED_2021.csv",
        "data/raw/electoral/2018/SEN_2018.xlsx",
        "data/raw/electoral/2021/GOB_2021.parquet",
        "electoral/2024/PRESIDENTE_2024.csv",
        "2024/DIPUTADOS_FEDERALES.csv",
    ]
    
    print("\n" + "─"*70)
    print(f"{'FILE PATH':<50} {'INFERRED NAME':<15} DATE")
    print("─"*70)
    
    for path in test_paths:
        election_name, election_date = infer_election_metadata(path)
        print(f"{path:<50} {election_name or 'N/A':<15} {election_date or 'N/A'}")
    
    print("─"*70)
    
    # Show how it works in practice
    print("\n" + "="*70)
    print("PRACTICAL USAGE")
    print("="*70)
    
    print("\n# Without inference (old way):")
    print("─"*70)
    print("""
orchestrator.process_electoral_file(
    file_path='data/raw/electoral/2024/PRES_2024.csv',
    election_name='PRES_2024',      # ← Had to specify manually
    election_date='2024-06-03'       # ← Had to specify manually
)
""")
    
    print("\n# With automatic inference (new way):")
    print("─"*70)
    print("""
orchestrator.process_electoral_file(
    'data/raw/electoral/2024/PRES_2024.csv'  # ← That's it! Auto-detects name & date
)
""")
    
    print("\n" + "="*70)
    print("✅ The system automatically extracts election metadata from paths!")
    print("="*70)


def demo_processing():
    """Demonstrate actual processing with auto-inference."""
    
    print("\n\n" + "="*70)
    print("DEMO: PROCESSING WITH AUTO-INFERENCE")
    print("="*70)
    
    # This would be a real example if the file exists
    example_path = "data/raw/electoral/2024/PRES_2024.csv"
    
    print(f"\nSuppose you have: {example_path}")
    print("\nOld way (manual):")
    print("─"*70)
    print("""
orchestrator = CleanVotesOrchestrator()
result = orchestrator.process_electoral_file(
    file_path='data/raw/electoral/2024/PRES_2024.csv',
    election_name='PRES_2024',
    election_date='2024-06-03',
    include_geometry=True,
    save_to_db=True
)
""")
    
    print("\nNew way (automatic):")
    print("─"*70)
    print("""
orchestrator = CleanVotesOrchestrator()
result = orchestrator.process_electoral_file(
    'data/raw/electoral/2024/PRES_2024.csv',  # ← Only need the path!
    include_geometry=True,
    save_to_db=True
)
# Automatically infers: election_name='PRES_2024', election_date='2024'
""")
    
    print("\n" + "="*70)
    print("💡 TIP: You can still override by providing explicit parameters")
    print("="*70)
    print("""
# Override automatic inference if needed
result = orchestrator.process_electoral_file(
    'data/raw/electoral/2024/some_weird_name.csv',
    election_name='CUSTOM_NAME_2024',  # ← Explicit override
    election_date='2024-01-15'          # ← Explicit override
)
""")


def show_supported_patterns():
    """Show supported file path patterns."""
    
    print("\n\n" + "="*70)
    print("SUPPORTED FILE PATH PATTERNS")
    print("="*70)
    
    patterns = {
        "Presidential Elections": [
            "data/raw/electoral/2024/PRES_2024.csv",
            "electoral/2024/PRESIDENTE_2024.xlsx",
            "2024/PRESIDENTIAL_2024.parquet",
        ],
        "Federal Deputies": [
            "data/raw/electoral/2021/DIP_FED_2021.csv",
            "electoral/2021/DIPUTADOS_2021.csv",
            "2021/DIP_2021.xlsx",
        ],
        "Senators": [
            "data/raw/electoral/2018/SEN_2018.csv",
            "electoral/2018/SENADORES_2018.csv",
        ],
        "Governors": [
            "data/raw/electoral/2021/GOB_2021.csv",
            "electoral/2021/GOBERNADOR_2021.csv",
        ],
        "With Full Date": [
            "electoral/2024/20240603_2005_PREP_PRES/PRES_2024.csv",
            "data/raw/electoral/2024/20240603_PRES/data.csv",
        ]
    }
    
    for category, paths in patterns.items():
        print(f"\n{category}:")
        print("─"*70)
        for path in paths:
            name, date = infer_election_metadata(path)
            print(f"  {path}")
            print(f"    → Name: {name}, Date: {date}")


def main():
    """Run all demonstrations."""
    demo_inference()
    demo_processing()
    show_supported_patterns()
    
    print("\n\n" + "="*70)
    print("🎉 SUMMARY")
    print("="*70)
    print("""
The system now automatically:
✅ Extracts election type from filename (PRES, DIP_FED, SEN, GOB, etc.)
✅ Extracts year from file path (looks for YYYY in path)
✅ Extracts full date if available (YYYYMMDD pattern in directory name)
✅ Creates intelligent election names (e.g., 'PRES_2024', 'DIP_FED_2021')

You no longer need to manually specify election_name or election_date!
Just provide the file path and let the system do the rest.
""")


if __name__ == '__main__':
    main()




