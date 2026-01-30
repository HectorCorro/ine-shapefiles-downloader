"""
Labexandria Corporate Design System
====================================

Official color palette and design tokens based on the Labexandria brand identity.
Colors extracted from the lighthouse logo with complementary palette.
"""

# ============================================================================
# PRIMARY COLORS - Core Brand Identity
# ============================================================================

LABEX_TEAL_PRIMARY = "#1B9A8E"      # Main brand color - lighthouse teal
LABEX_TEAL_LIGHT = "#4DBDAF"        # Lighter teal for highlights
LABEX_TEAL_DARK = "#0F6E64"         # Darker teal for depth
LABEX_TEAL_PALE = "#E0F4F2"         # Very light teal for backgrounds

# ============================================================================
# SECONDARY COLORS - Complementary Palette
# ============================================================================

LABEX_NAVY = "#1A3A52"              # Deep navy for headers/text
LABEX_OCEAN_BLUE = "#2E7D9A"        # Ocean blue for accents
LABEX_SKY_BLUE = "#5AB7D8"          # Sky blue for interactive elements
LABEX_CORAL = "#FF6B6B"             # Coral for warnings/alerts

# ============================================================================
# NEUTRAL COLORS - Interface Elements
# ============================================================================

LABEX_CHARCOAL = "#2C3E50"          # Dark charcoal for primary text
LABEX_SLATE = "#7F8C8D"             # Medium gray for secondary text
LABEX_SILVER = "#BDC3C7"            # Light gray for borders
LABEX_CLOUD = "#ECF0F1"             # Very light gray for backgrounds
LABEX_WHITE = "#FFFFFF"             # Pure white for surfaces

# ============================================================================
# ACCENT COLORS - Data Visualization
# ============================================================================

# Electoral Party Colors (keeping existing)
PARTY_MORENA = "#8B4513"            # Brown
PARTY_PAN = "#0066CC"               # Blue
PARTY_PRI = "#ED1C24"               # Red
PARTY_PRD = "#FFD700"               # Yellow/Gold
PARTY_PVEM = "#00A651"              # Green
PARTY_PT = "#DC143C"                # Crimson
PARTY_MC = "#FF6600"                # Orange

# Semantic Colors
SUCCESS_GREEN = "#27AE60"           # Success states
WARNING_AMBER = "#F39C12"           # Warning states
ERROR_RED = "#E74C3C"               # Error states
INFO_BLUE = "#3498DB"               # Information

# ============================================================================
# GRADIENT DEFINITIONS
# ============================================================================

GRADIENT_TEAL = f"linear-gradient(135deg, {LABEX_TEAL_LIGHT} 0%, {LABEX_TEAL_PRIMARY} 100%)"
GRADIENT_OCEAN = f"linear-gradient(135deg, {LABEX_TEAL_PRIMARY} 0%, {LABEX_OCEAN_BLUE} 100%)"
GRADIENT_SKY = f"linear-gradient(135deg, {LABEX_SKY_BLUE} 0%, {LABEX_TEAL_LIGHT} 100%)"

# ============================================================================
# COLOR PALETTES BY USE CASE
# ============================================================================

# Sequential palette for choropleth maps (light to dark)
SEQUENTIAL_TEAL = [
    LABEX_TEAL_PALE,    # Lightest
    "#A8E6E0",
    "#70D4C8",
    LABEX_TEAL_LIGHT,
    LABEX_TEAL_PRIMARY,
    LABEX_TEAL_DARK,    # Darkest
]

# Diverging palette for comparison visualizations
DIVERGING_TEAL_CORAL = [
    ERROR_RED,          # Negative extreme
    "#FF9999",
    LABEX_CLOUD,        # Neutral middle
    LABEX_TEAL_LIGHT,
    LABEX_TEAL_PRIMARY, # Positive extreme
]

# Categorical palette for multi-party comparisons
CATEGORICAL_VIBRANT = [
    LABEX_TEAL_PRIMARY,
    LABEX_OCEAN_BLUE,
    LABEX_CORAL,
    LABEX_SKY_BLUE,
    "#9B59B6",          # Purple
    "#E67E22",          # Orange
    "#1ABC9C",          # Turquoise
    "#34495E",          # Dark gray-blue
]

# ============================================================================
# STREAMLIT THEME CONFIGURATION
# ============================================================================

STREAMLIT_THEME = {
    "primaryColor": LABEX_TEAL_PRIMARY,
    "backgroundColor": LABEX_WHITE,
    "secondaryBackgroundColor": LABEX_CLOUD,
    "textColor": LABEX_CHARCOAL,
    "font": "sans-serif"
}

# ============================================================================
# PLOTLY TEMPLATE COLORS
# ============================================================================

PLOTLY_COLORS = {
    "primary": LABEX_TEAL_PRIMARY,
    "secondary": LABEX_OCEAN_BLUE,
    "accent": LABEX_SKY_BLUE,
    "background": LABEX_WHITE,
    "grid": LABEX_SILVER,
    "text": LABEX_CHARCOAL,
}

# ============================================================================
# MATPLOTLIB STYLE COLORS
# ============================================================================

MPL_COLORS = {
    "axes.facecolor": LABEX_WHITE,
    "axes.edgecolor": LABEX_SILVER,
    "axes.labelcolor": LABEX_CHARCOAL,
    "xtick.color": LABEX_CHARCOAL,
    "ytick.color": LABEX_CHARCOAL,
    "grid.color": LABEX_CLOUD,
    "figure.facecolor": LABEX_WHITE,
    "text.color": LABEX_CHARCOAL,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_sequential_palette(n_colors: int = 6, reverse: bool = False):
    """Get a sequential color palette with n colors."""
    from matplotlib.colors import LinearSegmentedColormap
    import numpy as np
    
    colors = SEQUENTIAL_TEAL if not reverse else SEQUENTIAL_TEAL[::-1]
    if n_colors <= len(colors):
        return colors[:n_colors]
    
    # Interpolate for more colors
    cmap = LinearSegmentedColormap.from_list("labex_teal", colors)
    return [cmap(i) for i in np.linspace(0, 1, n_colors)]


def get_party_color(party_name: str) -> str:
    """Get the official color for a political party."""
    party_colors = {
        "MORENA": PARTY_MORENA,
        "PAN": PARTY_PAN,
        "PRI": PARTY_PRI,
        "PRD": PARTY_PRD,
        "PVEM": PARTY_PVEM,
        "PT": PARTY_PT,
        "MC": PARTY_MC,
    }
    return party_colors.get(party_name.upper(), LABEX_TEAL_PRIMARY)


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex color."""
    return '#%02x%02x%02x' % rgb
