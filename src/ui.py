import streamlit as st

from src.plots import (
    plot_age_distribution,
    plot_age_vs_bci,
    plot_bci_distribution,
    plot_bridge_category_distribution,
    plot_condition_distribution,
    plot_current_condition_ratings,
)


def render_linear_output(results):
    print('hello from python')