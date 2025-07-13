import streamlit as st
import pydeck as pdk
from src.fire_alerts import load_combined_fire_data, build_fire_layers
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="Northwatch | FIRMS", layout="wide")
st.title("🔥 Northwatch – MODIS & VIIRS Fire Alerts")
st.caption("Live 24h fire detections from NASA FIRMS")

# --- Load Data ---
df = load_combined_fire_data()

# --- Sidebar Filters ---
st.sidebar.header("🔥 Filter Settings")

brightness_threshold = st.sidebar.slider(
    "Brightness threshold",
    min_value=250.0,
    max_value=500.0,
    value=350.0,
    step=1.0
)

# Confidence mapping (MODIS = int, VIIRS = str)
def map_confidence(val):
    try:
        # Clean up whitespace and lowercase string values
        val_str = str(val).strip().lower()

        if val_str in {"low", "nominal", "high"}:
            return val_str

        # Try numeric interpretation (for MODIS)
        val_float = float(val_str)
        if val_float >= 80:
            return "high"
        elif val_float >= 40:
            return "nominal"
        else:
            return "low"

    except:
        return "unknown"


df["confidence_label"] = df["confidence"].apply(map_confidence)

confidence_options = st.sidebar.multiselect(
    "Confidence levels",
    options=["low", "nominal", "high"],
    default=["high", "nominal"]
)



# --- Apply Filters ---
filtered_df = df[
    (df["brightness"] >= brightness_threshold) &
    (df["confidence_label"].isin(confidence_options))
]

# --- Map View ---
view_state = pdk.ViewState(
    latitude=60,
    longitude=-100,
    zoom=4,
    pitch=30
)

fire_layers = build_fire_layers(filtered_df)

r = pdk.Deck(
    layers=fire_layers,
    initial_view_state=view_state,
    map_style="light",
    tooltip={"text": "🔥 {source} Fire\nBrightness: {brightness}\nDate: {acq_date}"}
)

st.pydeck_chart(r, use_container_width=True, height=900)

# --- Legend ---
st.markdown("### 🔥 Legend")
st.markdown("""
- <span style="color:rgb(255,50,50)">●</span> MODIS Fires  
- <span style="color:rgb(255,140,140)">●</span> VIIRS Fires
""", unsafe_allow_html=True)

# --- Fire Count Summary ---
st.sidebar.markdown(f"**Total fires shown:** `{len(filtered_df)}`")
