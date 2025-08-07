# Import python packages
import streamlit as st
import altair as alt
import pandas as pd
from snowflake.snowpark.context import get_active_session

# Write directly to the app
st.title(f"Downloadable Objects")

# Get the current credentials
session = get_active_session()

# Altair chart
st.write("Chart to Image")
data = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 15]})
chart = alt.Chart(data).mark_bar().encode(x='x', y='y')
st.altair_chart(chart, use_container_width=True)

st.write("Table to CSV")
df_display = st.data_editor(data)
