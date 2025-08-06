import streamlit as st
import folium
from streamlit_folium import st_folium
from src.fire_alerts import load_combined_fire_data
import pandas as pd

# ---------- Page Setup ----------
st.set_page_config(page_title="Northwatch | FIRMS", layout="wide")
st.title("🔥 Northwatch – MODIS & VIIRS Fire Alerts")
st.caption("Live 24h fire detections from NASA FIRMS")

# ---------- Load Data ----------
df = load_combined_fire_data()

# ---------- Sidebar: Filters ----------
st.sidebar.header("🔥 Filter Settings")
brightness_threshold = st.sidebar.slider(
    "Brightness threshold",
    min_value=250.0, max_value=500.0, value=350.0, step=1.0
)

def map_confidence(val):
    try:
        val_str = str(val).strip().lower()
        if val_str in {"low", "nominal", "high"}:
            return val_str
        val_float = float(val_str)
        if val_float >= 80:
            return "high"
        elif val_float >= 40:
            return "nominal"
        else:
            return "low"
    except Exception:
        return "unknown"

df["confidence_label"] = df["confidence"].apply(map_confidence)
confidence_options = st.sidebar.multiselect(
    "Confidence levels", options=["low", "nominal", "high"],
    default=["high", "nominal"]
)

# ---------- Apply Filters ----------
filtered_df = df[
    (df["brightness"] >= brightness_threshold) &
    (df["confidence_label"].isin(confidence_options))
]

# ---------- Basemap chooser ----------
st.sidebar.subheader("🗺️ Basemap")
basemap = st.sidebar.radio(
    "Choose basemap",
    ["Sentinel-2 Satellite", "OpenStreetMap", "CartoDB Positron", "CartoDB Dark", "Terrain"],
    index=0
)

# ---------- Create Folium Map ----------
# Initialize map centered on Canada
m = folium.Map(
    location=[60, -100], 
    zoom_start=6,
    tiles=None  # We'll add custom tiles
)

# Add basemap layers based on selection
if basemap == "Sentinel-2 Satellite":
    # Sentinel-2 cloudless imagery from EOX
    folium.TileLayer(
        tiles='https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/default/GoogleMapsCompatible/{z}/{y}/{x}.jpg',
        attr='Sentinel-2 cloudless - https://s2maps.eu by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2020)',
        name='Sentinel-2 Cloudless',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Add labels/borders overlay for better context
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Labels & Borders',
        overlay=True,
        control=True,
        opacity=0.7
    ).add_to(m)
    
    st.caption("🛰️ Basemap: Sentinel-2 Cloudless (2020) with borders & labels")
    
elif basemap == "OpenStreetMap":
    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name='OpenStreetMap',
        overlay=False,
        control=True
    ).add_to(m)
    st.caption("🗺️ Basemap: OpenStreetMap")
    
elif basemap == "CartoDB Positron":
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name='CartoDB Positron',
        overlay=False,
        control=True
    ).add_to(m)
    st.caption("🗺️ Basemap: Light (CartoDB Positron)")
    
elif basemap == "CartoDB Dark":
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name='CartoDB Dark Matter',
        overlay=False,
        control=True
    ).add_to(m)
    st.caption("🗺️ Basemap: Dark (CartoDB Dark Matter)")
    
elif basemap == "Terrain":
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri &mdash; Source: USGS, Esri, TANA, DeLorme, and NPS',
        name='ESRI World Terrain',
        overlay=False,
        control=True
    ).add_to(m)
    st.caption("🏔️ Basemap: ESRI World Terrain")

# ---------- Add Fire Data Points ----------
if len(filtered_df) > 0:
    # Debug: Show column names
    st.sidebar.write("**DataFrame columns:**", list(filtered_df.columns))
    
    # Find latitude and longitude columns (common variations)
    lat_col = None
    lon_col = None
    
    for col in filtered_df.columns:
        col_lower = col.lower()
        if col_lower in ['latitude', 'lat', 'y']:
            lat_col = col
        elif col_lower in ['longitude', 'lng', 'lon', 'long', 'x']:
            lon_col = col
    
    if lat_col is None or lon_col is None:
        st.error(f"Could not find latitude/longitude columns. Available columns: {list(filtered_df.columns)}")
        st.stop()
    
    # Create separate feature groups for MODIS and VIIRS
    modis_group = folium.FeatureGroup(name='MODIS Fires', show=True)
    viirs_group = folium.FeatureGroup(name='VIIRS Fires', show=True)
    
    for idx, row in filtered_df.iterrows():
        # Get coordinates
        try:
            lat = float(row[lat_col])
            lon = float(row[lon_col])
        except (ValueError, TypeError):
            continue  # Skip invalid coordinates
        
        # Determine color and group based on source
        if 'source' in row and str(row['source']).upper() == 'MODIS':
            color = '#FF3232'  # Bright red for MODIS
            group = modis_group
            source_name = 'MODIS'
        else:
            color = '#FF8C8C'  # Light red for VIIRS  
            group = viirs_group
            source_name = 'VIIRS'
        
        # Create popup content
        popup_content = f"""
        <b>🔥 {source_name} Fire Alert</b><br>
        <b>Brightness:</b> {row.get('brightness', 'N/A')}<br>
        <b>Confidence:</b> {row.get('confidence', 'N/A')}<br>
        <b>Date:</b> {row.get('acq_date', 'N/A')}<br>
        <b>Time:</b> {row.get('acq_time', 'N/A')}<br>
        <b>Location:</b> {lat:.3f}, {lon:.3f}
        """
        
        # Add circle marker
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=f"{source_name} Fire - Brightness: {row.get('brightness', 'N/A')}",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(group)
    
    # Add feature groups to map
    modis_group.add_to(m)
    viirs_group.add_to(m)

# Add layer control
folium.LayerControl(collapsed=False).add_to(m)

# ---------- Display Map ----------
st.sidebar.markdown(f"**Total fires shown:** `{len(filtered_df)}`")

# Render the folium map
map_data = st_folium(m, width=None, height=600, returned_objects=["last_object_clicked"])

# ---------- Legend ----------
st.markdown("### 🔥 Legend")
col1, col2 = st.columns(2)
with col1:
    st.markdown('<span style="color:#FF3232; font-size: 20px;">●</span> **MODIS Fires**', unsafe_allow_html=True)
with col2:
    st.markdown('<span style="color:#FF8C8C; font-size: 20px;">●</span> **VIIRS Fires**', unsafe_allow_html=True)

# ---------- Display clicked fire info ----------
if map_data['last_object_clicked']:
    clicked = map_data['last_object_clicked']
    st.markdown("### 📍 Last Clicked Fire")
    st.json(clicked)

# ---------- Summary Stats ----------
st.markdown("### 📊 Summary Statistics")
col1, col2, col3 = st.columns(3)

if len(filtered_df) > 0:
    with col1:
        st.metric("Total Fires", len(filtered_df))
    
    with col2:
        if 'source' in filtered_df.columns:
            modis_count = len(filtered_df[filtered_df['source'].str.upper() == 'MODIS'])
            st.metric("MODIS Fires", modis_count)
        else:
            st.metric("MODIS Fires", "N/A")
    
    with col3:
        if 'source' in filtered_df.columns:
            viirs_count = len(filtered_df[filtered_df['source'].str.upper() != 'MODIS'])
            st.metric("VIIRS Fires", viirs_count)
        else:
            st.metric("VIIRS Fires", "N/A")
            
    # Confidence breakdown
    if 'confidence_label' in filtered_df.columns:
        st.markdown("#### Confidence Distribution")
        conf_counts = filtered_df['confidence_label'].value_counts()
        st.bar_chart(conf_counts)
else:
    st.warning("No fires match your current filter criteria. Try adjusting the brightness threshold or confidence levels.")