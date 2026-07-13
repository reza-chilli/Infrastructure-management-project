import streamlit as st
from streamlit_option_menu import option_menu

from src.plots import (
    plot_age_distribution,
    plot_age_vs_bci,
    plot_bci_distribution,
    plot_bridge_category_distribution,
    plot_current_condition_ratings,
)

def render_sidebar():
    with st.sidebar:
        st.title("Bridge Analysis")
        with st.sidebar.expander("BCI Weight Settings", expanded=False):
            st.caption("Set the relative weights used to calculate the Bridge Condition Index (BCI).")
            deck_w_pct = st.slider("Deck Weight %", min_value=0, max_value=100, value=30, step=5)
            super_w_pct = st.slider("Superstructure Weight %", min_value=0, max_value=100, value=35, step=5)
            sub_w_pct = st.slider("Substructure Weight %", min_value=0, max_value=100, value=35, step=5)

            bridge_deck_weight = deck_w_pct / 100
            bridge_super_structure_weight = super_w_pct / 100
            bridge_sub_structure_weight = sub_w_pct / 100

            total_weight = round((bridge_deck_weight + bridge_super_structure_weight + bridge_sub_structure_weight) * 100, 2)

            if total_weight == 100:
                
                if st.button("Apply BCI Changes", type="primary"):
                    st.session_state['bci_weights'] = {
                        'deck': bridge_deck_weight,
                        'super': bridge_super_structure_weight,
                        'sub': bridge_sub_structure_weight
                    }
                    st.toast("Weights Applied Successfully!", icon="✅") 
                    st.rerun()
            else:
                st.error(f"Total: {total_weight}% (Must be 100%)")
                st.button("Apply BCI Changes", disabled=True)
        with st.sidebar.expander("Prioritization Weight Settings", expanded=False):
            st.caption("Adjust the weights used to calculate the overall bridge investment priority score.")
            bci_w = st.slider("BCI Weight %", min_value=0, max_value=100, value=50, step=5)
            traffic_w = st.slider("Traffic Volume Weight %", min_value=0, max_value=100, value=30, step=5)
            replacement_cost_w = st.slider("Replacement Cost Weight %", min_value=0, max_value=100, value=20, step=5)
            total_weight = bci_w + traffic_w + replacement_cost_w
            if total_weight == 100:
                if st.button("Apply PI Changes", type="primary"):
                    st.session_state['Priority_Weights'] = {
                        'bci': bridge_deck_weight / 100,
                        'traffic': bridge_super_structure_weight / 100,
                        'Replacement_Cost': bridge_sub_structure_weight / 100
                    }
                    st.toast("Weights Applied Successfully!", icon="✅") 
                    st.rerun()
            else:
                st.error(f"Total: {total_weight}% (Must be 100%)")
                st.button("Apply PI Changes", disabled=True)



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