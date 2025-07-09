import streamlit as st
import pydeck as pdk
from src.fire_alerts import load_firms_data, build_fire_layer

st.set_page_config(page_title="Northwatch | FIRMS", layout="wide")
st.title("🔥 Northwatch – NASA Fire Alerts")
st.caption("Live MODIS data, updated every 15 minutes.")

df = load_firms_data()
fire_layer = build_fire_layer(df)

view_state = pdk.ViewState(
    latitude=60, longitude=-100,
    zoom=4,
    pitch=30
)

r = pdk.Deck(
    layers=[fire_layer],
    initial_view_state=view_state,
    map_style="light",
    tooltip={"text": "🔥 Brightness: {brightness}\nDate: {acq_date}"}
)

st.pydeck_chart(r, use_container_width=True, height=1800)
