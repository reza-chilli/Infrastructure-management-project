import streamlit as st
from src.calculations import run_all_calculations
from src.data import get_current_year, load_and_preprocess_data
from src.ui import render_linear_output, render_sidebar

st.set_page_config(page_title="Bridge Analysis", layout="wide")

current_year = get_current_year()
st.write(f"Current Year: {current_year}")

EXCEL_PATH = "ToR Structures_Data_Updated- bahman 1405.xlsx"

df = load_and_preprocess_data(EXCEL_PATH)

results = run_all_calculations(df, current_year=current_year)

page = render_sidebar()
if page == "Bridge Network Assessment":
    st.title("Bridge Network Assessment")
    st.write("This is the Bridge Network Assessment page.")

elif page == "Developement of a Prioritization Framework":
    st.title("Developement of a Prioritization Framework")
    st.write("This is the Developement of a Prioritization Framework page.")

elif page == "Maintenance and Rehabilitation Strategy":
    st.title("Maintenance and Rehabilitation Strategy")
    st.write("This is the Maintenance and Rehabilitation Strategy page.")

elif page == "Budget Scenario Analysis":
    st.title("Budget Scenario Analysis")
    st.write("This is the Budget Scenario Analysis page.")

elif page == "Communication of Results":
    st.title("Communication of Results")
    st.write("This is the Communication of Results page.")
# render_linear_output(results)
