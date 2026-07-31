import pandas as pd
import streamlit as st

from pathlib import Path


def render_budget_scenario_page(
    df_processed: pd.DataFrame,
    current_year: int,
    workbook_path: str | Path,
) -> None:
    """Render budget scenario analysis based on budget."""

    st.title("Budget Scenario Analysis")
    st.caption(
        "Current recommendations show unconstrained engineering need. "
        "The five-year plan then determines which actions can actually be "
        "programmed under baseline and constrained annual budgets."
    )
    baseLineBudgetCol, constrainedBudgetCol = st.columns(2)
    with baseLineBudgetCol:
      st.subheader("Base Budget Scenario")
    with constrainedBudgetCol:
      st.subheader("Constrained Budget Scenario")