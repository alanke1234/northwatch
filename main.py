import streamlit as st
from src.fire_alerts import load_firms_data, build_fire_map

st.set_page_config(page_title="Northwatch | FIRMS", layout="wide")
st.title("🔥 Northwatch – NASA Fire Alerts")
st.caption("Live MODIS data, updated every 15 minutes.")

df = load_firms_data()
html_map = build_fire_map(df)

st.components.v1.html(html_map,
    height=1900,  # or try 1000
    width=3200,  # forces horizontal scaling too
    scrolling=True)
