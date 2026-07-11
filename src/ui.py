import streamlit as st

from src.plots import (
    plot_age_distribution,
    plot_age_vs_bci,
    plot_bci_distribution,
    plot_bridge_category_distribution,
    plot_condition_distribution,
    plot_current_condition_ratings,
)

def render_sidebar():
    with st.sidebar:
        st.title("Bridge Analysis")
        st.caption("Navigation")

        page = st.radio(
            "Go to",
            [
                "Bridge Network Assessment", 
                "Developement of a Prioritization Framework", 
                "Maintenance and Rehabilitation Strategy", 
                "Budget Scenario Analysis",
                "Communication of Results"
            ],
            index=0
        )

    return page


def render_linear_output(results):
    print('hello from python')