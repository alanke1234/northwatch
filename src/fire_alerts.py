import pandas as pd
import pydeck as pdk
from datetime import datetime
import streamlit as st

MODIS_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_24h.csv"
VIIRS_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_24h.csv"

@st.cache_data(ttl=900)
def load_combined_fire_data():
    def load_fire_data(url, source_label):
        try:
            df = pd.read_csv(url)
            df = df.rename(columns={"latitude": "lat", "longitude": "lon"})
            df = df[df["lat"].between(40, 90) & df["lon"].between(-140, -50)]
            df["source"] = source_label
            st.success(f"{source_label} rows loaded: {len(df)}")
            return df
        except Exception as e:
            st.error(f"Failed to load {source_label}: {e}")
            return pd.DataFrame()

    modis_df = load_fire_data(MODIS_URL, "MODIS")
    viirs_df = load_fire_data(VIIRS_URL, "VIIRS")
    viirs_df["brightness"] = viirs_df["bright_ti4"]

    combined_df = pd.concat([modis_df, viirs_df], ignore_index=True)
    st.info(f"Total combined fire detections: {len(combined_df)}")
    st.dataframe(combined_df.head())

    st.write("🔥 MODIS count:", len(modis_df))
    st.write("🔥 VIIRS count:", len(viirs_df))
    st.write("Unique sources:", combined_df['source'].unique())

    return combined_df

def build_fire_layers(df):
    modis = df[df["source"] == "MODIS"]
    viirs = df[df["source"] == "VIIRS"]

    layer_modis = pdk.Layer(
        "ScatterplotLayer",
        data=modis,
        get_position='[lon, lat]',
        get_radius=3000,
        get_fill_color='[255, 0, 0, 140]',
        pickable=True
    )

    layer_viirs = pdk.Layer(
        "ScatterplotLayer",
        data=viirs,
        get_position='[lon, lat]',
        get_radius=4000,
        get_fill_color='[255, 100, 0, 140]',
        pickable=True
    )

    return [layer_modis, layer_viirs]
