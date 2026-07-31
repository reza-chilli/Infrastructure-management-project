import pandas as pd
import streamlit as st

from pathlib import Path

from src.five_year_plan import DEFAULT_HORIZON_YEARS
from src.plots import plot_annual_costs_vs_budget


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
    annualBudgetSettings = st.session_state.get(
      "five_year_plan_settings",
    )
    detailedPlan = st.session_state.get(
      "five_year_plan_detail",
    )
    detailedPlan = pd.DataFrame(detailedPlan)
    baseLineBudgetCol, constrainedBudgetCol = st.columns(2)
    with baseLineBudgetCol:
      st.subheader("Base Budget Scenario")
      totalAnnualBudget = annualBudgetSettings["baseline_budget"]
      st.write(f"Annual Budget: {totalAnnualBudget} USD")
      detailedBaselineBudgetPlan = detailedPlan.query("Scenario == 'Baseline Budget'")

      fundedPlans = detailedBaselineBudgetPlan.query("Funded")
      annual_funded_costs_series = fundedPlans.groupby("Plan_Year")["Treatment_Cost"].sum()
      annual_funded_costs_list = annual_funded_costs_series.tolist()
      annual_funded_costs_list = annual_funded_costs_series.tolist()
      fig1 = plot_annual_costs_vs_budget(
        annual_funded_costs_list,
        totalAnnualBudget
      )
      st.pyplot(fig1, use_container_width=False)
    with constrainedBudgetCol:
      st.subheader("Constrained Budget Scenario")
      totalAnnualBudget = annualBudgetSettings["baseline_budget"] * (100 - annualBudgetSettings["constrained_reduction_pct"]) / 100
      st.write(f"Annual Budget: {totalAnnualBudget} USD")
      detailedConstrainedBudgetPlan = detailedPlan.query("Scenario == 'Constrained Budget'")

      fundedPlans = detailedConstrainedBudgetPlan.query("Funded")
      annual_funded_costs_series = fundedPlans.groupby("Plan_Year")["Treatment_Cost"].sum()
      annual_funded_costs_list = annual_funded_costs_series.tolist()
      fig1 = plot_annual_costs_vs_budget(
        annual_funded_costs_list,
        totalAnnualBudget
      )
      st.pyplot(fig1, use_container_width=False)