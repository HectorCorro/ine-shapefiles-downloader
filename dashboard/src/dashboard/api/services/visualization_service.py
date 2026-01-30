"""
Visualization Service
=====================

Service for creating static and interactive visualizations.
"""

import io
import base64
import logging
from typing import Literal, Optional, Tuple, Dict, Any
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import plotly.express as px
import plotly.graph_objects as go
from dashboard.config import PARTY_COLORS, PLOT_CRS

logger = logging.getLogger(__name__)


class VisualizationService:
    """
    Service for creating visualizations.
    
    Supports both static (matplotlib) and interactive (plotly) styles.
    """
    
    @staticmethod
    def create_spatial_lag_comparison(
        gdf: gpd.GeoDataFrame,
        variable: str,
        lag_variable: str,
        style: Literal["static", "interactive"] = "static",
        title: Optional[str] = None
    ) -> str:
        """
        Create side-by-side comparison of original values and spatial lag.
        
        Args:
            gdf: GeoDataFrame with data and spatial lag
            variable: Original variable column name
            lag_variable: Spatial lag column name
            style: Visualization style ('static' or 'interactive')
            title: Optional title for the plot
            
        Returns:
            Base64 encoded image (static) or HTML (interactive)
        """
        logger.info(f"Creating spatial lag comparison: {variable} vs {lag_variable}, style={style}")
        
        if style == "static":
            return VisualizationService._create_static_lag_comparison(
                gdf, variable, lag_variable, title
            )
        else:
            return VisualizationService._create_interactive_lag_comparison(
                gdf, variable, lag_variable, title
            )
    
    @staticmethod
    def _create_static_lag_comparison(
        gdf: gpd.GeoDataFrame,
        variable: str,
        lag_variable: str,
        title: Optional[str] = None
    ) -> str:
        """Create static matplotlib comparison."""
        fig, axes = plt.subplots(1, 2, figsize=(20, 10))
        
        # Convert to Web Mercator for better visualization
        gdf_plot = gdf.to_crs(epsg=3857) if gdf.crs and str(gdf.crs) != 'EPSG:3857' else gdf
        
        # Left plot: Original values
        gdf_plot.plot(
            column=variable,
            ax=axes[0],
            cmap='Reds',
            legend=True,
            edgecolor='black',
            linewidth=0.3,
            legend_kwds={'label': variable, 'shrink': 0.8}
        )
        axes[0].set_title(f'{variable} (Original Values)', 
                         fontsize=14, fontweight='bold', pad=15)
        axes[0].set_axis_off()
        
        # Right plot: Spatial Lag
        gdf_plot.plot(
            column=lag_variable,
            ax=axes[1],
            cmap='Reds',
            legend=True,
            edgecolor='black',
            linewidth=0.3,
            legend_kwds={'label': lag_variable, 'shrink': 0.8}
        )
        axes[1].set_title(f'{lag_variable} (Average of Neighbors)', 
                         fontsize=14, fontweight='bold', pad=15)
        axes[1].set_axis_off()
        
        if title:
            plt.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        return image_base64
    
    @staticmethod
    def _create_interactive_lag_comparison(
        gdf: gpd.GeoDataFrame,
        variable: str,
        lag_variable: str,
        title: Optional[str] = None
    ) -> str:
        """Create interactive folium map with spatial lag comparison."""
        try:
            # Convert to WGS84 for web mapping
            gdf_wgs84 = gdf.to_crs(epsg=4326) if gdf.crs and str(gdf.crs) != 'EPSG:4326' else gdf.copy()
            
            # Prepare tooltip columns
            tooltip_cols = []
            
            # Add SECCION if available
            if 'SECCION' in gdf_wgs84.columns:
                tooltip_cols.append('SECCION')
            
            # Add ENTIDAD if available
            if 'ENTIDAD' in gdf_wgs84.columns:
                tooltip_cols.append('ENTIDAD')
            
            # Add variable and lag
            if variable in gdf_wgs84.columns:
                tooltip_cols.append(variable)
            if lag_variable in gdf_wgs84.columns:
                tooltip_cols.append(lag_variable)
            
            # Add total votes if available
            if 'TOTAL_VOTOS_SUM' in gdf_wgs84.columns:
                tooltip_cols.append('TOTAL_VOTOS_SUM')
            elif 'TOTAL_VOTOS' in gdf_wgs84.columns:
                tooltip_cols.append('TOTAL_VOTOS')
            
            logger.info(f"Creating map with tooltip columns: {tooltip_cols}")
            
            # Create interactive map using GeoPandas explore (built on folium)
            m = gdf_wgs84.explore(
                column=lag_variable,
                cmap='Reds',
                legend=True,
                tooltip=tooltip_cols if tooltip_cols else True,
                popup=tooltip_cols if tooltip_cols else True,
                tiles='CartoDB positron',
                style_kwds={'fillOpacity': 0.7},
                legend_kwds={
                    'caption': f'{lag_variable} (Spatial Lag - Average of Neighbors)',
                    'scale': True
                }
            )
            
            # Return as HTML
            from io import BytesIO
            buffer = BytesIO()
            m.save(buffer, close_file=False)
            buffer.seek(0)
            html_content = buffer.getvalue().decode()
            logger.info(f"Map HTML generated, length: {len(html_content)}")
            return html_content
            
        except Exception as e:
            logger.error(f"Error creating interactive map: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    @staticmethod
    def create_choropleth_map(
        gdf: gpd.GeoDataFrame,
        variable: str,
        style: Literal["static", "interactive"] = "static",
        title: Optional[str] = None,
        color_scale: str = "Reds"
    ) -> str:
        """
        Create a choropleth map of a variable.
        
        Args:
            gdf: GeoDataFrame with data
            variable: Variable to map
            style: Visualization style
            title: Plot title
            color_scale: Color scale name
            
        Returns:
            Base64 encoded image or HTML
        """
        logger.info(f"Creating choropleth map for {variable}, style={style}")
        
        if style == "static":
            return VisualizationService._create_static_choropleth(
                gdf, variable, title, color_scale
            )
        else:
            return VisualizationService._create_interactive_choropleth(
                gdf, variable, title, color_scale
            )
    
    @staticmethod
    def _create_static_choropleth(
        gdf: gpd.GeoDataFrame,
        variable: str,
        title: Optional[str] = None,
        color_scale: str = "Reds"
    ) -> str:
        """Create static matplotlib choropleth."""
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Convert to Web Mercator
        gdf_plot = gdf.to_crs(epsg=3857) if gdf.crs and str(gdf.crs) != 'EPSG:3857' else gdf
        
        gdf_plot.plot(
            column=variable,
            ax=ax,
            cmap=color_scale,
            legend=True,
            edgecolor='black',
            linewidth=0.3,
            legend_kwds={'label': variable, 'shrink': 0.8}
        )
        
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        
        ax.set_axis_off()
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        return image_base64
    
    @staticmethod
    def _create_interactive_choropleth(
        gdf: gpd.GeoDataFrame,
        variable: str,
        title: Optional[str] = None,
        color_scale: str = "Reds"
    ) -> str:
        """Create interactive plotly choropleth."""
        gdf_wgs84 = gdf.to_crs(epsg=4326) if gdf.crs and str(gdf.crs) != 'EPSG:4326' else gdf
        
        fig = px.choropleth(
            gdf_wgs84,
            geojson=gdf_wgs84.__geo_interface__,
            locations=gdf_wgs84.index,
            color=variable,
            color_continuous_scale=color_scale,
            title=title
        )
        
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=600, margin={"r": 0, "t": 50, "l": 0, "b": 0})
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    @staticmethod
    def create_bar_chart(
        df: pd.DataFrame,
        x: str,
        y: str,
        style: Literal["static", "interactive"] = "static",
        title: Optional[str] = None,
        color: Optional[str] = None
    ) -> str:
        """
        Create a bar chart.
        
        Args:
            df: DataFrame with data
            x: Column for x-axis
            y: Column for y-axis
            style: Visualization style
            title: Chart title
            color: Column for color encoding (optional)
            
        Returns:
            Base64 encoded image or HTML
        """
        logger.info(f"Creating bar chart: x={x}, y={y}, style={style}")
        
        if style == "static":
            return VisualizationService._create_static_bar(df, x, y, title, color)
        else:
            return VisualizationService._create_interactive_bar(df, x, y, title, color)
    
    @staticmethod
    def _create_static_bar(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: Optional[str] = None,
        color: Optional[str] = None
    ) -> str:
        """Create static matplotlib bar chart."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if color:
            # Group by color column
            for name, group in df.groupby(color):
                ax.bar(group[x], group[y], label=name, alpha=0.8)
            ax.legend()
        else:
            ax.bar(df[x], df[y], alpha=0.8)
        
        ax.set_xlabel(x, fontsize=12)
        ax.set_ylabel(y, fontsize=12)
        
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        return image_base64
    
    @staticmethod
    def _create_interactive_bar(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: Optional[str] = None,
        color: Optional[str] = None
    ) -> str:
        """Create interactive plotly bar chart."""
        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color,
            title=title,
            height=500
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            margin={"r": 0, "t": 50, "l": 0, "b": 100}
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    @staticmethod
    def create_line_chart(
        df: pd.DataFrame,
        x: str,
        y: str,
        style: Literal["static", "interactive"] = "static",
        title: Optional[str] = None,
        color: Optional[str] = None
    ) -> str:
        """
        Create a line chart for temporal analysis.
        
        Args:
            df: DataFrame with data
            x: Column for x-axis (usually election or time)
            y: Column for y-axis
            style: Visualization style
            title: Chart title
            color: Column for color encoding (optional)
            
        Returns:
            Base64 encoded image or HTML
        """
        logger.info(f"Creating line chart: x={x}, y={y}, style={style}")
        
        if style == "static":
            return VisualizationService._create_static_line(df, x, y, title, color)
        else:
            return VisualizationService._create_interactive_line(df, x, y, title, color)
    
    @staticmethod
    def _create_static_line(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: Optional[str] = None,
        color: Optional[str] = None
    ) -> str:
        """Create static matplotlib line chart."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if color:
            for name, group in df.groupby(color):
                ax.plot(group[x], group[y], marker='o', label=name, linewidth=2)
            ax.legend()
        else:
            ax.plot(df[x], df[y], marker='o', linewidth=2)
        
        ax.set_xlabel(x, fontsize=12)
        ax.set_ylabel(y, fontsize=12)
        ax.grid(True, alpha=0.3)
        
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        return image_base64
    
    @staticmethod
    def _create_interactive_line(
        df: pd.DataFrame,
        x: str,
        y: str,
        title: Optional[str] = None,
        color: Optional[str] = None
    ) -> str:
        """Create interactive plotly line chart."""
        fig = px.line(
            df,
            x=x,
            y=y,
            color=color,
            markers=True,
            title=title,
            height=500
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            margin={"r": 0, "t": 50, "l": 0, "b": 100}
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
