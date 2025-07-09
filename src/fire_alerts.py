import pandas as pd
#import folium
import pydeck as pdk
from datetime import datetime
import streamlit as st

FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_24h.csv"


@st.cache_data(ttl=900)  # refresh every 15 min
def load_firms_data():
    df = pd.read_csv(FIRMS_URL)
    df = df[df['latitude'].between(40, 90) & df['longitude'].between(-140, -50)]
    df = df.rename(columns={"latitude": "lat", "longitude": "lon"})
    return df

def build_fire_layer(df):
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lon, lat]',
        get_radius=3000,
        get_fill_color='[255, 0, 0, 140]',
        pickable=True,
        tooltip=True
    )
