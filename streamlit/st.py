import streamlit as st
import pandas as pd
from query import get_connection

st.title("App Streamlit + Azure PostgreSQL com SSL 🔐")

engine = get_connection()

query = "SELECT * FROM tb_sensor"

with engine.connect() as conn:
    df = pd.read_sql(query, conn)

st.dataframe(df)
