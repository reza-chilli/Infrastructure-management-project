import streamlit as st
from streamlit_option_menu import option_menu

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

        selected_page = option_menu(
            menu_title=None,
            options=[
                "Bridge Network Assessment", 
                "Developement of a Prioritization Framework", 
                "Maintenance and Rehabilitation Strategy", 
                "Budget Scenario Analysis",
                "Communication of Results"
            ],
            icons=[
                "diagram-3",
                "ui-checks-grid",
                "tools",
                "cash-stack",
                "clipboard-data",
            ],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {
                    "padding": "0!important",
                    "background-color": "transparent",
                },
                "icon": {
                    "color": "#4F8BF9",
                    "font-size": "18px",
                },
                "nav-link": {
                    "font-size": "15px",
                    "text-align": "left",
                    "margin": "6px 0",
                    "padding": "10px 14px",
                    "border-radius": "10px",
                    "--hover-color": "#f0f2f6",
                },
                "nav-link-selected": {
                    "background-color": "#4F8BF9",
                    "color": "white",
                },
            },
        )

    return selected_page


def render_linear_output(results):
    print('hello from python')