#!/usr/bin/env python3
"""
Moran's Spatial Autocorrelation Analysis Example
=================================================

This script demonstrates how to load data from the database and perform
Moran's spatial autocorrelation analysis, as shown in clean_votes.ipynb.

The pipeline (run_pipeline.py) prepares the data with geometry.
This script performs the spatial analysis.

Usage:
    uv run python analytics/examples/moran_analysis_example.py
    
    # Analyze specific election and state
    uv run python analytics/examples/moran_analysis_example.py --election PRES_2024 --entidad 1
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))

import geopandas as gpd
import matplotlib.pyplot as plt
from libpysal.weights import Queen
from esda.moran import Moran
from splot.esda import moran_scatterplot

from analytics.clean_votes import CleanVotesOrchestrator


def perform_moran_analysis(
    gdf: gpd.GeoDataFrame,
    variable: str = 'MORENA_PCT',
    entidad_name: str = 'Unknown'
) -> dict:
    """
    Perform Moran's I spatial autocorrelation analysis.
    
    Args:
        gdf: GeoDataFrame with electoral data and geometries
        variable: Variable to analyze (default: MORENA_PCT)
        entidad_name: Name of the state
        
    Returns:
        Dictionary with analysis results
    """
    print(f"\n{'='*70}")
    print(f"MORAN'S SPATIAL AUTOCORRELATION ANALYSIS")
    print(f"{'='*70}")
    print(f"Entity: {entidad_name}")
    print(f"Variable: {variable}")
    print(f"Observations: {len(gdf)}")
    
    # Check for missing values
    missing = gdf[variable].isna().sum()
    if missing > 0:
        print(f"\n⚠️  Removing {missing} observations with missing values")
        gdf = gdf.dropna(subset=[variable]).copy()
    
    # Create spatial weights matrix (Queen contiguity)
    print(f"\n[1/3] Creating spatial weights matrix...")
    w_queen = Queen.from_dataframe(gdf)
    
    print(f"  Observations: {w_queen.n}")
    print(f"  Non-zero weights: {w_queen.nonzero}")
    print(f"  Average neighbors: {w_queen.mean_neighbors:.2f}")
    
    # Check for islands
    islands = w_queen.islands
    if islands:
        print(f"  ⚠️  Islands (no neighbors): {len(islands)}")
    else:
        print(f"  ✓ No islands - all observations connected")
    
    # Calculate Moran's I
    print(f"\n[2/3] Calculating Moran's I...")
    moran = Moran(gdf[variable], w_queen)
    
    print(f"\n  Moran's I: {moran.I:.4f}")
    print(f"  Expected I: {moran.EI:.4f}")
    print(f"  Z-score: {moran.z_norm:.4f}")
    print(f"  P-value: {moran.p_sim:.6f}")
    
    # Interpretation
    print(f"\n[3/3] Interpretation:")
    if moran.I > moran.EI:
        print(f"  ✓ Positive spatial autocorrelation detected")
        print(f"    → Similar {variable} values cluster together")
    else:
        print(f"  ⚠️  Negative spatial autocorrelation detected")
        print(f"    → Dissimilar {variable} values are neighbors")
    
    if moran.p_sim < 0.05:
        print(f"  ✓ Statistically significant (p < 0.05)")
        print(f"    → Pattern unlikely due to chance")
    else:
        print(f"  ⚠️  Not statistically significant (p >= 0.05)")
        print(f"    → Pattern could be random")
    
    # Variable statistics
    print(f"\n{variable} Statistics:")
    print(f"  Mean: {gdf[variable].mean():.2f}")
    print(f"  Median: {gdf[variable].median():.2f}")
    print(f"  Std: {gdf[variable].std():.2f}")
    print(f"  Min: {gdf[variable].min():.2f}")
    print(f"  Max: {gdf[variable].max():.2f}")
    
    return {
        'variable': variable,
        'moran_i': moran.I,
        'expected_i': moran.EI,
        'z_score': moran.z_norm,
        'p_value': moran.p_sim,
        'n_observations': len(gdf),
        'mean_neighbors': w_queen.mean_neighbors,
        'significant': moran.p_sim < 0.05,
        'moran_object': moran,
        'weights': w_queen
    }


def create_moran_plots(
    gdf: gpd.GeoDataFrame,
    moran: Moran,
    variable: str,
    entidad_name: str,
    output_dir: str = 'data/insights/moran_plots'
):
    """
    Create Moran's I visualization plots.
    
    Args:
        gdf: GeoDataFrame with data
        moran: Moran object from analysis
        variable: Variable analyzed
        entidad_name: State name
        output_dir: Directory to save plots
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left: Moran scatterplot
    moran_scatterplot(moran, ax=axes[0], zstandard=True)
    axes[0].set_title(f"Moran Scatterplot: {variable}\n{entidad_name}", 
                      fontsize=12, fontweight='bold')
    
    # Right: Choropleth map
    gdf_plot = gdf.to_crs(epsg=3857) if gdf.crs != 'EPSG:3857' else gdf
    gdf_plot.plot(
        column=variable,
        ax=axes[1],
        cmap='Reds',
        legend=True,
        edgecolor='black',
        linewidth=0.3
    )
    axes[1].set_title(f'{variable} Distribution\n{entidad_name}',
                      fontsize=12, fontweight='bold')
    axes[1].set_axis_off()
    
    plt.suptitle(
        f"Moran's I = {moran.I:.4f} (p = {moran.p_sim:.4f})",
        fontsize=14, fontweight='bold', y=1.02
    )
    
    plt.tight_layout()
    
    # Save plot
    safe_name = entidad_name.replace(' ', '_').lower()
    safe_var = variable.lower()
    output_file = output_path / f'moran_{safe_var}_{safe_name}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n  ✓ Plot saved: {output_file}")
    
    plt.close()


def analyze_all_entidades(
    orchestrator: CleanVotesOrchestrator,
    election_name: str,
    variable: str = 'MORENA_PCT'
):
    """
    Perform Moran's analysis for all entidades in an election.
    
    Args:
        orchestrator: CleanVotesOrchestrator instance
        election_name: Election to analyze
        variable: Variable to analyze
    """
    print(f"\n{'='*70}")
    print(f"ANALYZING ALL ENTIDADES: {election_name}")
    print(f"{'='*70}")
    
    # Get list of elections
    elections = orchestrator.list_available_elections()
    election_data = elections[elections['election_name'] == election_name]
    
    if len(election_data) == 0:
        print(f"✗ Election not found: {election_name}")
        return
    
    print(f"\nFound {len(election_data)} entidades for {election_name}")
    
    results = []
    
    for _, row in election_data.iterrows():
        entidad_id = row['entidad_id']
        entidad_name = row['entidad_name']
        
        try:
            print(f"\n{'─'*70}")
            print(f"Processing: {entidad_name} (ID: {entidad_id})")
            print(f"{'─'*70}")
            
            # Load data
            gdf = orchestrator.load_election_data(
                election_name=election_name,
                entidad_id=entidad_id,
                as_geodataframe=True
            )
            
            # Check for geometry
            if 'geometry' not in gdf.columns:
                print(f"  ✗ No geometry available for {entidad_name}")
                continue
            
            # Check for variable
            if variable not in gdf.columns:
                print(f"  ✗ Variable {variable} not found")
                continue
            
            # Perform analysis
            result = perform_moran_analysis(gdf, variable, entidad_name)
            result['entidad_id'] = entidad_id
            result['entidad_name'] = entidad_name
            results.append(result)
            
            # Create plots
            create_moran_plots(
                gdf,
                result['moran_object'],
                variable,
                entidad_name
            )
            
        except Exception as e:
            print(f"  ✗ Error processing {entidad_name}: {e}")
            continue
    
    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY: {election_name}")
    print(f"{'='*70}")
    print(f"\nAnalyzed {len(results)} entidades")
    
    if results:
        import pandas as pd
        summary = pd.DataFrame([{
            'Entidad': r['entidad_name'],
            'Moran I': f"{r['moran_i']:.4f}",
            'P-value': f"{r['p_value']:.4f}",
            'Significant': '✓' if r['significant'] else '✗',
            'N': r['n_observations']
        } for r in results])
        
        print("\n" + summary.to_string(index=False))
        
        # Save summary
        output_path = Path('data/insights/moran_plots')
        output_path.mkdir(parents=True, exist_ok=True)
        summary_file = output_path / f'moran_summary_{election_name.lower()}.csv'
        summary.to_csv(summary_file, index=False)
        print(f"\n✓ Summary saved: {summary_file}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Perform Moran\'s spatial autocorrelation analysis on electoral data'
    )
    
    parser.add_argument(
        '--election',
        default='PRES_2024',
        help='Election to analyze (default: PRES_2024)'
    )
    
    parser.add_argument(
        '--entidad',
        type=int,
        help='Specific entidad ID to analyze (1-32). If not provided, analyzes all.'
    )
    
    parser.add_argument(
        '--variable',
        default='MORENA_PCT',
        help='Variable to analyze (default: MORENA_PCT)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available elections and exit'
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = CleanVotesOrchestrator()
    
    # List elections if requested
    if args.list:
        elections = orchestrator.list_available_elections()
        print("\n" + "="*70)
        print("AVAILABLE ELECTIONS")
        print("="*70)
        
        if len(elections) > 0:
            unique_elections = elections['election_name'].unique()
            for election in unique_elections:
                election_data = elections[elections['election_name'] == election]
                entidades = len(election_data)
                with_geom = election_data['has_geometry'].sum()
                print(f"\n{election}:")
                print(f"  Entidades: {entidades}")
                print(f"  With geometry: {with_geom}")
        else:
            print("\nNo elections found in database.")
            print("Run the pipeline first: uv run python analytics/run_pipeline.py")
        
        return
    
    # Analyze specific entidad or all
    if args.entidad:
        # Single entidad
        print(f"Loading data: {args.election}, Entidad {args.entidad}")
        gdf = orchestrator.load_election_data(
            election_name=args.election,
            entidad_id=args.entidad,
            as_geodataframe=True
        )
        
        # Get entidad name
        entidad_name = gdf['ENTIDAD'].iloc[0] if 'ENTIDAD' in gdf.columns else f'Entidad {args.entidad}'
        
        # Perform analysis
        result = perform_moran_analysis(gdf, args.variable, entidad_name)
        
        # Create plots
        create_moran_plots(
            gdf,
            result['moran_object'],
            args.variable,
            entidad_name
        )
    else:
        # All entidades
        analyze_all_entidades(orchestrator, args.election, args.variable)
    
    print(f"\n{'='*70}")
    print("✅ ANALYSIS COMPLETE!")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()


