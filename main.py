import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Brazos River Flow", page_icon="🛶", layout="wide")

st.title("🛶 Brazos River Flow Monitor")
st.caption("Highway 16 (PK Dam) to Highway 4 (Palo Pinto)")

# Fetch last 7 days of data from USGS
url = "https://waterservices.usgs.gov/nwis/iv/?format=json&sites=08088610,08089000&period=P7D&parameterCd=00060"

try:
    res = requests.get(url, timeout=10).json()
    records = []

    for ts in res['value']['timeSeries']:
        site_name = "Hwy 16 (Graford)" if "08088610" in ts['name'] else "Hwy 4 (Palo Pinto)"
        for val in ts['values'][0]['value']:
            records.append({
                "Location": site_name,
                "DateTime": pd.to_datetime(val['dateTime']),
                "Flow (cfs)": float(val['value'])
            })

    df = pd.DataFrame(records)

    # Key Metrics at top
    col1, col2 = st.columns(2)
    for idx, loc in enumerate(["Hwy 16 (Graford)", "Hwy 4 (Palo Pinto)"]):
        loc_df = df[df["Location"] == loc]
        if not loc_df.empty:
            latest = loc_df.iloc[-1]["Flow (cfs)"]
            target_col = col1 if idx == 0 else col2
            target_col.metric(
                label=f"Current Flow @ {loc}", 
                value=f"{latest:.0f} cfs"
            )

    st.markdown("---")

    # Interactive Graph
    fig = px.line(
        df, 
        x="DateTime", 
        y="Flow (cfs)", 
        color="Location", 
        title="7-Day Historical Flow Hydrograph",
        labels={"DateTime": "Date & Time", "Flow (cfs)": "Discharge (cfs)"}
    )
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching USGS river data: {e}")
