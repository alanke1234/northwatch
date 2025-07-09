import pandas as pd
import folium
from datetime import datetime
import streamlit as st

FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_24h.csv"


@st.cache_data(ttl=900)  # refresh every 15 min
def load_firms_data():
    df = pd.read_csv(FIRMS_URL)
    df = df[df['latitude'].between(40, 90) & df['longitude'].between(-140, -50)]
    df = df.rename(columns={"latitude": "lat", "longitude": "lon"})
    return df

def build_fire_map(df):
    m = m = folium.Map(location=[56, -106], zoom_start=4, tiles="OpenStreetMap")

    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=4,
            popup=f"🔥 {row['acq_date']}, Brightness: {row['brightness']}",
            color="red",
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

    return m._repr_html_()  # returns raw HTML for Streamlit
