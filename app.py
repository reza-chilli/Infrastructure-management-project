import streamlit as st
from src.calculations import run_all_calculations
from src.data import get_current_year, load_and_preprocess_data
from src.ui import render_linear_output

st.set_page_config(page_title="Bridge Analysis", layout="wide")

current_year = get_current_year()
st.write(f"Current Year: {current_year}")

EXCEL_PATH = "ToR Structures_Data_Updated- bahman 1405.xlsx"

df = load_and_preprocess_data(EXCEL_PATH)

results = run_all_calculations(df, current_year=current_year)

render_linear_output(results)
