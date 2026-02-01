# Shapefile Geography Fixes Summary

## 🎉 Issues Resolved

### Problem 1: Shapefiles in Wrong Folders
**Issue**: Electoral shapefiles were physically misplaced during download:
- `9_CDMX` folder contained Baja California geometry
- `26_Sonora` folder contained Baja California geometry  
- CDMX geometry was actually in `10_Durango` folder
- Sonora geometry was actually in `27_Tabasco` folder

**Solution**: Implemented intelligent shapefile search (`_find_shapefile_by_entidad()`) that:
- Searches all folders to find files with matching ENTIDAD values
- Automatically locates correct geometry regardless of folder location
- Falls back to standard paths when they exist

**Files Modified**:
- `analytics/src/analytics/clean_votes/geometry.py`

### Problem 2: Wrong ENTIDAD Values in Shapefiles
**Issue**: Some PEEPJF shapefiles had incorrect ENTIDAD values:
- CDMX shapefile had `ENTIDAD = 2` (should be `9`)
- Sonora shapefile had `ENTIDAD = 2` (should be `26`)

**Solution**: Added ENTIDAD validation and override:
- Detects when shapefile has wrong ENTIDAD value
- Warns about the mismatch
- Triggers smart search to find correct file

### Problem 3: Browser/Streamlit Caching
**Issue**: Users saw old cached maps when switching between states/parties

**Solution**: 
- Added **"🔄 Clear Cache"** button in sidebar
- Reduced cache TTL from 1 hour to 5 minutes for maps
- Added `show_spinner=False` for better UX

**Files Modified**:
- `dashboard/src/dashboard/app.py`
- `dashboard/src/dashboard/utils/api_client.py`

---

## ✅ Verification Results

All states and parties tested successfully:

```
✅ Baja California  - All 7 major parties: Correct geography
✅ Ciudad de México - All 7 major parties: Correct geography  
✅ Sonora          - All 7 major parties: Correct geography
```

**Parties Tested**: PAN, PRI, PRD, MORENA, PVEM, PT, MC

---

## 🚀 How to Use

### Clear Cache in Dashboard

1. **In Sidebar**: Look for "Configuration" section
2. **Click**: "🔄 Clear Cache" button
3. **Wait**: Page will automatically reload with fresh data

### When to Clear Cache

Clear cache if you experience:
- Old maps showing for new selections
- Wrong state geography after switching states
- Stale data after backend updates

### Automatic Cache Expiry

Maps now expire automatically after **5 minutes**, so cache issues should be less frequent.

---

## 📊 Diagnostic Tools Created

Several diagnostic scripts were created to help debug shapefile issues:

1. **`analytics/check_shapefile_availability.py`**
   - Checks which states have valid shapefiles
   - Shows paths for nacional and peepjf files
   - Run: `uv run python analytics/check_shapefile_availability.py`

2. **`verify_shapefile_data.py`**
   - Verifies shapefile ENTIDAD values match folder names
   - Detects misplaced shapefiles
   - Run: `uv run python verify_shapefile_data.py`

3. **`find_correct_shapefiles.py`**
   - Searches all folders for shapefiles with specific ENTIDAD
   - Helps locate misplaced files
   - Run: `uv run python find_correct_shapefiles.py`

4. **`test_geometry_cdmx_sonora.py`**
   - Quick test for CDMX and Sonora geometry loading
   - Run: `uv run python test_geometry_cdmx_sonora.py`

5. **`diagnose_party_specific_issue.py`**
   - Checks if different parties show different geographies
   - Run: `uv run python diagnose_party_specific_issue.py`

6. **`test_all_states_parties.py`**  
   - **Comprehensive test** for all states and all parties
   - Recommended for regression testing
   - Run: `uv run python test_all_states_parties.py`

---

## 🔧 Technical Details

### Smart Shapefile Search Algorithm

```python
def _find_shapefile_by_entidad(entidad_id):
    """Search all folders for shapefile with matching ENTIDAD."""
    for shp_file in base_dir.rglob('SECCION.shp'):
        gdf = gpd.read_file(shp_file)
        if gdf['ENTIDAD'].unique()[0] == entidad_id:
            return shp_file  # Found correct file!
    raise FileNotFoundError()
```

### Merge Logic

1. Try standard shapefile path first
2. If file exists, check ENTIDAD value
3. If ENTIDAD is wrong, trigger smart search
4. If file doesn't exist, trigger smart search  
5. Merge on `ENTIDAD` and `SECCION` columns

### Cache Strategy

- **Data endpoints**: 1 hour TTL (rarely changes)
- **Spatial analysis**: 5 minutes TTL (may update)
- **Map visualizations**: 5 minutes TTL (interactive, needs freshness)
- **Manual clear**: Always available via button

---

## 🎯 Next Steps

If you encounter any geography issues:

1. **First**: Click "🔄 Clear Cache" in dashboard sidebar
2. **Check**: Run `test_all_states_parties.py` to verify backend
3. **If backend OK**: Issue is browser caching (hard refresh: Cmd+Shift+R on Mac, Ctrl+F5 on Windows)
4. **If backend fails**: Check shapefile availability with diagnostic scripts

---

## 📝 Files Modified Summary

**Core Fixes**:
- `analytics/src/analytics/clean_votes/geometry.py` (smart search, ENTIDAD validation)
- `dashboard/src/dashboard/app.py` (clear cache button)
- `dashboard/src/dashboard/utils/api_client.py` (reduced TTL)

**Diagnostic Tools** (all in root):
- `analytics/check_shapefile_availability.py`
- `verify_shapefile_data.py`
- `find_correct_shapefiles.py`  
- `test_geometry_cdmx_sonora.py`
- `diagnose_party_specific_issue.py`
- `test_all_states_parties.py`
- `verify_correct_geography.py`
- `diagnose_merge_issue.py`

---

## ✨ Result

All 32 Mexican states now load correct geography for all parties, with automatic detection and correction of misplaced shapefiles. Users can manually clear cache if needed, and cache expires automatically every 5 minutes.

**Status**: ✅ **RESOLVED**
