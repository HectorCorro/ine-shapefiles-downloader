"""
Electoral Dashboard - Streamlit Frontend
=========================================

Interactive dashboard for visualizing Mexican electoral data with spatial analysis.
"""

import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import sys
from pathlib import Path

# Add dashboard to path
dashboard_path = Path(__file__).parent
sys.path.insert(0, str(dashboard_path))

from config import (
    STREAMLIT_PAGE_TITLE,
    STREAMLIT_PAGE_ICON,
    STREAMLIT_LAYOUT,
    STREAMLIT_INITIAL_SIDEBAR_STATE,
    MAJOR_PARTIES,
    API_BASE_URL
)
from utils.api_client import APIClient

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_PAGE_TITLE,
    page_icon=STREAMLIT_PAGE_ICON,
    layout=STREAMLIT_LAYOUT,
    initial_sidebar_state=STREAMLIT_INITIAL_SIDEBAR_STATE
)

# Apply Labexandria corporate styling
st.markdown("""
<style>
    /* Labexandria Corporate Design System */
    
    /* Primary buttons and interactive elements */
    .stButton>button {
        background: linear-gradient(135deg, #4DBDAF 0%, #1B9A8E 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #1B9A8E 0%, #0F6E64 100%);
        box-shadow: 0 4px 12px rgba(27, 154, 142, 0.3);
        transform: translateY(-2px);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F8F9FA;
        padding: 8px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 8px;
        padding: 8px 16px;
        border: 2px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #1B9A8E 0%, #2E7D9A 100%);
        color: white;
        border-color: #1B9A8E;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        color: #1B9A8E;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1A3A52;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8F9FA 0%, #FFFFFF 100%);
    }
    
    /* Success/Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #1B9A8E;
    }
    
    /* Selectbox and multiselect */
    .stSelectbox, .stMultiSelect {
        border-radius: 8px;
    }
    
    /* Data tables */
    .dataframe {
        border: 1px solid #ECF0F1;
        border-radius: 8px;
    }
    
    .dataframe thead {
        background-color: #1B9A8E;
        color: white;
    }
    
    /* Logo container */
    .logo-container {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API client
@st.cache_resource
def get_api_client():
    """Get or create API client singleton."""
    return APIClient(base_url=API_BASE_URL)

api = get_api_client()


# Helper functions

def display_html_visualization(viz_response, height=650):
    """Display HTML visualization from API response."""
    if viz_response.get("content_type") == "text/html":
        st.components.v1.html(viz_response["content"], height=height, scrolling=True)
    elif viz_response.get("content_type") == "image/png":
        # Decode base64 image
        image_data = base64.b64decode(viz_response["content"])
        st.image(image_data)


def format_party_name(party: str) -> str:
    """Format party name for display."""
    return party.replace("_PCT", "").replace("_", " ")


def get_party_pct_column(party: str) -> str:
    """Get the percentage column name for a party."""
    return f"{party}_PCT"


# Main app

def main():
    # Header with logo
    col_logo, col_title = st.columns([1, 4])
    
    with col_logo:
        # Display company logo - use absolute path from home directory
        import os
        home_dir = os.path.expanduser("~")
        logo_path = Path(home_dir) / ".cursor" / "projects" / "Users-hectorcorro-Documents-Labex-ine-shapefiles-downloader" / "assets" / "LABEXANDRIA_COLOR_2-be18fa22-b1d5-4cd2-8e38-c0f8edb6daa4.png"
        
        if logo_path.exists():
            st.image(str(logo_path), width=150)
        else:
            # Fallback: try alternate logo emoji
            st.markdown("# 🏢")
    
    with col_title:
        st.title("📊 Electoral Data Dashboard")
        st.markdown("Interactive visualization and analysis of Mexican electoral data")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # Check API health
    try:
        summary = api.get_elections_summary()
        st.sidebar.success("✅ API Connected")
        st.sidebar.info(f"**{summary['unique_elections']}** elections available")
    except Exception as e:
        st.sidebar.error("❌ API Connection Failed")
        st.sidebar.error(f"Error: {str(e)}")
        st.error("Cannot connect to the API. Please ensure the FastAPI server is running.")
        st.info("Start the API with: `cd dashboard && uv run uvicorn dashboard.api.main:app --reload`")
        return
    
    # Cache controls
    st.sidebar.divider()
    if st.sidebar.button("🔄 Clear Cache", help="Clear all cached data and refresh visualizations"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.sidebar.success("✅ Cache cleared! Page will reload...")
        st.rerun()
    
    # Get available elections
    try:
        elections_list = api.get_elections_summary()["elections"]
        election_names = [e["election_name"] for e in elections_list]
    except Exception as e:
        st.error(f"Error loading elections: {e}")
        return
    
    # Election selector
    selected_election = st.sidebar.selectbox(
        "Select Election",
        options=election_names,
        index=0 if election_names else None
    )
    
    # Visualization style
    viz_style = st.sidebar.radio(
        "Visualization Style",
        options=["interactive", "static"],
        index=0,
        help="Interactive uses Plotly/Folium, Static uses Matplotlib"
    )
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Spatial Analysis",
        "🌍 Interactive Map Explorer",
        "🔄 Cross-State Comparison",
        "📈 Temporal Analysis"
    ])
    
    # Tab 1: Spatial Analysis
    with tab1:
        spatial_analysis_tab(api, selected_election, viz_style)
    
    # Tab 2: Interactive Map Explorer
    with tab2:
        interactive_map_tab(api, selected_election)
    
    # Tab 3: Cross-State Comparison
    with tab3:
        cross_state_comparison_tab(api, selected_election, viz_style)
    
    # Tab 4: Temporal Analysis
    with tab4:
        temporal_analysis_tab(api, selected_election, viz_style)


def spatial_analysis_tab(api, selected_election, viz_style):
    """Spatial analysis tab content."""
    st.header("Spatial Analysis - Moran's I & Spatial Lag")
    st.markdown("Analyze spatial autocorrelation and visualize how electoral patterns cluster geographically.")
    
    # Get available states for election
    try:
        states = api.get_states_for_election(selected_election)
        state_options = {s["entidad_name"]: s["entidad_id"] for s in states}
    except Exception as e:
        st.error(f"Error loading states: {e}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_state_name = st.selectbox(
            "Select State",
            options=list(state_options.keys())
        )
        selected_state_id = state_options[selected_state_name]
    
    with col2:
        # Get available variables
        try:
            variables_info = api.get_available_variables(selected_election, selected_state_id)
            available_vars = variables_info.get("percentage_variables", [])
            
            if not available_vars:
                st.warning("No percentage variables found")
                return
            
            selected_variable = st.selectbox(
                "Select Variable",
                options=available_vars,
                format_func=format_party_name
            )
        except Exception as e:
            st.error(f"Error loading variables: {e}")
            return
    
    if st.button("🔍 Analyze", type="primary", use_container_width=True):
        with st.spinner("Computing spatial analysis..."):
            try:
                # Compute Moran's I
                moran_result = api.compute_moran_i(
                    election_name=selected_election,
                    entidad_id=selected_state_id,
                    variable=selected_variable
                )
                
                # Display Moran's I results
                st.subheader("Moran's I Spatial Autocorrelation")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Moran's I", f"{moran_result['moran_i']:.4f}")
                
                with col2:
                    st.metric("Z-Score", f"{moran_result['z_score']:.4f}")
                
                with col3:
                    st.metric("P-Value", f"{moran_result['p_value']:.4f}")
                
                with col4:
                    significance = "✅ Significant" if moran_result['significant'] else "❌ Not Significant"
                    st.metric("Significance", significance)
                
                # Interpretation
                st.info(f"**Interpretation:** {moran_result['interpretation']}")
                
                # Additional info
                with st.expander("📊 Technical Details"):
                    st.write(f"- **Observations:** {moran_result['n_observations']:,}")
                    st.write(f"- **Average Neighbors:** {moran_result['mean_neighbors']:.2f}")
                    st.write(f"- **Islands (no neighbors):** {moran_result['islands']}")
                    st.write(f"- **Expected I:** {moran_result['expected_i']:.4f}")
                
                st.divider()
                
                # Generate spatial lag visualization
                st.subheader("Spatial Lag Visualization")
                st.markdown("Compare original values with the average of neighboring areas")
                
                with st.spinner("Generating maps..."):
                    viz_response = api.create_spatial_lag_map(
                        election_name=selected_election,
                        entidad_id=selected_state_id,
                        variable=selected_variable,
                        style=viz_style
                    )
                    
                    # Use larger height for better map navigation
                    display_html_visualization(viz_response, height=750)
                
                # Compute spatial lag data
                lag_result = api.compute_spatial_lag(
                    election_name=selected_election,
                    entidad_id=selected_state_id,
                    variable=selected_variable
                )
                
                # Display statistics
                st.subheader("Statistics")
                stats = lag_result["statistics"]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Original Mean", f"{stats['mean_original']:.2f}")
                
                with col2:
                    st.metric("Spatial Lag Mean", f"{stats['mean_lag']:.2f}")
                
                with col3:
                    st.metric("Correlation", f"{stats['correlation']:.4f}")
                
            except Exception as e:
                st.error(f"Error performing spatial analysis: {e}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())


def interactive_map_tab(api, selected_election):
    """Interactive map explorer with spatial lag visualization."""
    st.header("🌍 Interactive Map Explorer")
    st.markdown("Explore electoral data with interactive maps showing original values and spatial lag (average of neighbors)")
    
    # Get available states for election
    try:
        states = api.get_states_for_election(selected_election)
        state_options = {s["entidad_name"]: s["entidad_id"] for s in states}
    except Exception as e:
        st.error(f"Error loading states: {e}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_state_name = st.selectbox(
            "Select State",
            options=list(state_options.keys()),
            key="map_state"
        )
        selected_state_id = state_options[selected_state_name]
    
    with col2:
        # Get available variables
        try:
            variables_info = api.get_available_variables(selected_election, selected_state_id)
            available_vars = variables_info.get("percentage_variables", [])
            
            if not available_vars:
                st.warning("No percentage variables found")
                return
            
            selected_variable = st.selectbox(
                "Select Variable (Political Party)",
                options=available_vars,
                format_func=format_party_name,
                key="map_variable"
            )
        except Exception as e:
            st.error(f"Error loading variables: {e}")
            return
    
    # Display info
    st.info(f"**State:** {selected_state_name} | **Variable:** {format_party_name(selected_variable)}")
    
    if st.button("🗺️ Generate Maps", type="primary", use_container_width=True):
        with st.spinner("Loading election data and generating interactive maps..."):
            try:
                # Get the election data with spatial lag
                lag_result = api.compute_spatial_lag(
                    election_name=selected_election,
                    entidad_id=selected_state_id,
                    variable=selected_variable
                )
                
                # Display statistics first
                st.subheader("📊 Summary Statistics")
                stats = lag_result["statistics"]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Original Mean", f"{stats['mean_original']:.2f}%")
                
                with col2:
                    st.metric("Spatial Lag Mean", f"{stats['mean_lag']:.2f}%")
                
                with col3:
                    st.metric("Correlation", f"{stats['correlation']:.4f}")
                
                with col4:
                    st.metric("Observations", f"{stats['n_observations']:,}")
                
                st.divider()
                
                # Generate the interactive map
                st.subheader("🗺️ Interactive Spatial Lag Map")
                st.markdown(f"""
                **How to use:**
                - 🖱️ Click and drag to pan
                - 🔍 Scroll to zoom in/out
                - 👆 Click on regions to see details
                - 📊 Tooltips show: SECCION, ENTIDAD, {format_party_name(selected_variable)}, Spatial Lag, and Total Votes
                """)
                
                # Generate visualization
                viz_response = api.create_spatial_lag_map(
                    election_name=selected_election,
                    entidad_id=selected_state_id,
                    variable=selected_variable,
                    style="interactive"  # Force interactive for this tab
                )
                
                # Display with larger height for better navigation
                display_html_visualization(viz_response, height=800)
                
                # Additional technical info
                with st.expander("🔍 Technical Details"):
                    st.write("**Spatial Lag** represents the average value of neighboring areas.")
                    st.write(f"- **Correlation:** {stats['correlation']:.4f} indicates how similar each area is to its neighbors")
                    st.write(f"- **Mean difference:** {abs(stats['mean_original'] - stats['mean_lag']):.2f}%")
                    st.write(f"- A high correlation suggests spatial clustering of similar values")
                
            except Exception as e:
                st.error(f"Error generating maps: {e}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())


def cross_state_comparison_tab(api, selected_election, viz_style):
    """Cross-state comparison tab content."""
    st.header("Cross-State Comparison")
    st.markdown("Compare electoral performance across multiple states for the same election.")
    
    # Get available states
    try:
        states = api.get_states_for_election(selected_election)
        state_options = {s["entidad_name"]: s["entidad_id"] for s in states}
    except Exception as e:
        st.error(f"Error loading states: {e}")
        return
    
    # Multi-select for states
    selected_state_names = st.multiselect(
        "Select States to Compare",
        options=list(state_options.keys()),
        default=list(state_options.keys())[:4] if len(state_options) > 4 else list(state_options.keys())[:2]
    )
    
    if not selected_state_names:
        st.warning("Please select at least 2 states to compare")
        return
    
    selected_state_ids = [state_options[name] for name in selected_state_names]
    
    # Party selection
    selected_parties = st.multiselect(
        "Select Parties",
        options=MAJOR_PARTIES,
        default=["MORENA", "PAN", "PRI"]
    )
    
    if not selected_parties:
        st.warning("Please select at least one party")
        return
    
    if st.button("📊 Compare", type="primary", use_container_width=True):
        with st.spinner("Loading comparison data..."):
            try:
                # Get comparison data
                party_variables = [get_party_pct_column(p) for p in selected_parties]
                
                comparison_result = api.compare_cross_state(
                    election_name=selected_election,
                    entidad_ids=selected_state_ids,
                    variables=party_variables
                )
                
                # Display summary
                st.subheader("Summary")
                summary = comparison_result["summary"]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("States Compared", summary["total_states"])
                
                with col2:
                    st.metric("Total Sections", f"{summary['total_sections']:,}")
                
                with col3:
                    st.metric("Total Votes", f"{summary['total_votes']:,.0f}")
                
                st.divider()
                
                # Create DataFrame for display
                data = comparison_result["data"]
                df = pd.DataFrame(data)
                
                # Display table
                st.subheader("Detailed Metrics")
                
                # Select columns to display
                display_cols = ["entidad_name", "sections", "total_votes"] + party_variables
                display_cols = [col for col in display_cols if col in df.columns]
                
                df_display = df[display_cols].copy()
                
                # Format numbers
                df_display["sections"] = df_display["sections"].apply(lambda x: f"{x:,}")
                df_display["total_votes"] = df_display["total_votes"].apply(lambda x: f"{x:,.0f}")
                
                # Format percentages
                for var in party_variables:
                    if var in df_display.columns:
                        df_display[var] = df_display[var].apply(lambda x: f"{x:.2f}%")
                
                # Rename columns for display
                df_display = df_display.rename(columns={
                    "entidad_name": "State",
                    "sections": "Sections",
                    "total_votes": "Total Votes"
                })
                
                for var in party_variables:
                    party_name = format_party_name(var)
                    if var in df_display.columns:
                        df_display = df_display.rename(columns={var: f"{party_name} %"})
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"cross_state_comparison_{selected_election}.csv",
                    mime="text/csv"
                )
                
                st.divider()
                
                # Visualizations
                st.subheader("Visualizations")
                
                # Prepare data for charts
                chart_data = []
                for row in data:
                    for party in selected_parties:
                        var = get_party_pct_column(party)
                        if var in row:
                            chart_data.append({
                                "State": row["entidad_name"],
                                "Party": party,
                                "Percentage": row[var]
                            })
                
                # Create bar chart
                with st.spinner("Generating chart..."):
                    chart_response = api.create_bar_chart(
                        data=chart_data,
                        x="State",
                        y="Percentage",
                        color="Party",
                        style=viz_style,
                        title=f"Party Performance by State - {selected_election}"
                    )
                    
                    display_html_visualization(chart_response)
                
            except Exception as e:
                st.error(f"Error performing comparison: {e}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())


def temporal_analysis_tab(api, selected_election, viz_style):
    """Temporal analysis tab content."""
    st.header("Temporal Analysis")
    st.markdown("Analyze voting trends over time for a single state across multiple elections.")
    
    # Get available elections
    try:
        elections_summary = api.get_elections_summary()
        all_elections = [e["election_name"] for e in elections_summary["elections"]]
    except Exception as e:
        st.error(f"Error loading elections: {e}")
        return
    
    # Get available states
    try:
        states = api.get_states()
        state_options = {s["entidad_name"]: s["entidad_id"] for s in states}
    except Exception as e:
        st.error(f"Error loading states: {e}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_state_name = st.selectbox(
            "Select State",
            options=list(state_options.keys()),
            key="temporal_state"
        )
        selected_state_id = state_options[selected_state_name]
    
    with col2:
        # Filter to elections that have data for this state
        available_elections_for_state = []
        for election in all_elections:
            try:
                states_in_election = api.get_states_for_election(election)
                if any(s["entidad_id"] == selected_state_id for s in states_in_election):
                    available_elections_for_state.append(election)
            except:
                continue
        
        selected_elections = st.multiselect(
            "Select Elections to Compare",
            options=available_elections_for_state,
            default=available_elections_for_state[:3] if len(available_elections_for_state) >= 3 else available_elections_for_state
        )
    
    if not selected_elections or len(selected_elections) < 2:
        st.warning("Please select at least 2 elections to compare")
        return
    
    # Party selection
    selected_parties = st.multiselect(
        "Select Parties",
        options=MAJOR_PARTIES,
        default=["MORENA", "PAN", "PRI"],
        key="temporal_parties"
    )
    
    if not selected_parties:
        st.warning("Please select at least one party")
        return
    
    if st.button("📈 Analyze Trends", type="primary", use_container_width=True):
        with st.spinner("Loading temporal data..."):
            try:
                # Get comparison data
                party_variables = [get_party_pct_column(p) for p in selected_parties]
                
                comparison_result = api.compare_temporal(
                    entidad_id=selected_state_id,
                    election_names=selected_elections,
                    variables=party_variables
                )
                
                # Display summary
                st.subheader("Summary")
                summary = comparison_result["summary"]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("State", summary["entidad_name"])
                
                with col2:
                    st.metric("Elections Analyzed", summary["total_elections"])
                
                st.divider()
                
                # Create DataFrame
                data = comparison_result["data"]
                df = pd.DataFrame(data)
                
                # Display table
                st.subheader("Detailed Metrics")
                
                display_cols = ["election_name", "sections", "total_votes"] + party_variables
                display_cols = [col for col in display_cols if col in df.columns]
                
                df_display = df[display_cols].copy()
                
                # Format numbers
                df_display["sections"] = df_display["sections"].apply(lambda x: f"{x:,}")
                df_display["total_votes"] = df_display["total_votes"].apply(lambda x: f"{x:,.0f}")
                
                # Format percentages
                for var in party_variables:
                    if var in df_display.columns:
                        df_display[var] = df_display[var].apply(lambda x: f"{x:.2f}%")
                
                # Rename columns
                df_display = df_display.rename(columns={
                    "election_name": "Election",
                    "sections": "Sections",
                    "total_votes": "Total Votes"
                })
                
                for var in party_variables:
                    party_name = format_party_name(var)
                    if var in df_display.columns:
                        df_display = df_display.rename(columns={var: f"{party_name} %"})
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"temporal_analysis_{selected_state_name}_{'-'.join(selected_elections)}.csv",
                    mime="text/csv"
                )
                
                st.divider()
                
                # Visualizations
                st.subheader("Trends Over Time")
                
                # Prepare data for line chart
                chart_data = []
                for row in data:
                    for party in selected_parties:
                        var = get_party_pct_column(party)
                        if var in row:
                            chart_data.append({
                                "Election": row["election_name"],
                                "Party": party,
                                "Percentage": row[var]
                            })
                
                # Create line chart
                with st.spinner("Generating chart..."):
                    chart_response = api.create_line_chart(
                        data=chart_data,
                        x="Election",
                        y="Percentage",
                        color="Party",
                        style=viz_style,
                        title=f"Party Performance Over Time - {selected_state_name}"
                    )
                    
                    display_html_visualization(chart_response)
                
            except Exception as e:
                st.error(f"Error performing temporal analysis: {e}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())


# Footer
def display_footer():
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray; padding: 20px;'>
            Electoral Data Dashboard | Built with Streamlit + FastAPI + GeoPandas
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
    display_footer()
