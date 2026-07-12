import streamlit as st
from src.calculations import run_all_calculations
from src.plots import plot_bridge_category_distribution, plot_age_distribution
from src.data import get_current_year, load_and_preprocess_data
from src.ui import render_linear_output, render_sidebar

st.set_page_config(page_title="Bridge Analysis", layout="wide")

current_year = get_current_year()
st.write(f"Current Year: {current_year}")

EXCEL_PATH = "ToR Structures_Data_Updated- bahman 1405.xlsx"

df = load_and_preprocess_data(EXCEL_PATH)

df_processed, summary, top10, lowest_bci, kpiCardInfo = run_all_calculations(df, current_year=current_year)

page = render_sidebar()
if page == "Bridge Network Assessment":
    st.title("Bridge Network Assessment")
    with st.container(border=True):
      st.subheader("Network Overview KPIs")
      kpiC1, kpiC2 = st.columns(2)
      kpiC1.metric("Bridges", kpiCardInfo['totalBridgeCount'])
      kpiC1.metric("Asset Value", f"{kpiCardInfo['totalCost']:,.0f}")
      kpiC1.metric("Average Age", f"{kpiCardInfo['averageAge']:,.0f}")
      kpiC2.metric("Average Health Index", f"{kpiCardInfo['averageConditionRating']:,.1f}")
      kpiC2.metric("Total Daily Traffic", f"{kpiCardInfo['totalDailyTraffic']:,.0f}")
    col1, col2 = st.columns(2)
    with col1:
      fig1 = plot_bridge_category_distribution(
        df_processed,
        figsize=(2.8, 2.8),
        title_fontsize=9,
        label_fontsize=7,
        pct_fontsize=6,
      )
      st.pyplot(fig1, use_container_width=False)
    with col2:
      fig2 = plot_age_distribution(
        df_processed,
      )
      st.pyplot(fig2, use_container_width=False)


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
