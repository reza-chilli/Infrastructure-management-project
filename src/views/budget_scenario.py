import pandas as pd
import streamlit as st

from pathlib import Path

from src.five_year_plan import DEFAULT_HORIZON_YEARS, DEFAULT_DISCOUNT_RATE
from src.plots import plot_annual_costs_vs_budget, plot_condition_category_distribution_end_of_program
from src.calculations import calculate_pv


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
    if (
        "five_year_plan_settings" not in st.session_state
        or "five_year_plan_detail" not in st.session_state
    ):
      st.warning("Please execute the budget scenarios first.")
      st.stop()
    detailedPlan = pd.DataFrame(detailedPlan)
    baseLineBudgetCol, constrainedBudgetCol = st.columns(2)
    with baseLineBudgetCol:
      st.subheader("Base Budget Scenario")
      totalAnnualBudget = annualBudgetSettings["baseline_budget"]
      st.write(f"Annual Budget: {totalAnnualBudget:,.0f} USD")
      detailedBaselineBudgetPlan = detailedPlan.query("Scenario == 'Baseline Budget'")

      fundedPlans = detailedBaselineBudgetPlan.query("Funded")
      annual_funded_costs_series = fundedPlans.groupby("Plan_Year")["Treatment_Cost"].sum()
      annual_funded_costs_list = annual_funded_costs_series.tolist()
      # calculate costs PV
      baseLineBudgetPv = calculate_pv(annual_funded_costs_list, DEFAULT_DISCOUNT_RATE)
      st.write(f"Total Costs PV: ${baseLineBudgetPv:,.0f} USD")
      # calculate remaining budget PV
      remaining_budget = [totalAnnualBudget - cost for cost in annual_funded_costs_list]
      remainingBudgetPv = calculate_pv(remaining_budget, DEFAULT_DISCOUNT_RATE)
      st.write(f"Remaining Budget PV: ${remainingBudgetPv:,.0f} USD")
      endOfProgramBridgeData = detailedBaselineBudgetPlan.query(f"Plan_Year == {DEFAULT_HORIZON_YEARS}")
      average_bci = endOfProgramBridgeData["BCI_End_of_Year"].mean(skipna=True)
      st.write(f"Average Network BCI: {average_bci:,.0f} %")
      fig1 = plot_annual_costs_vs_budget(
        annual_funded_costs_list,
        totalAnnualBudget
      )
      st.pyplot(fig1, use_container_width=False)
      col11, col22 = st.columns([7, 3])
      with col11:
        fig2 = plot_condition_category_distribution_end_of_program(endOfProgramBridgeData, "Baseline Network Condition")
        st.pyplot(fig2, use_container_width=False)
    with constrainedBudgetCol:
      st.subheader("Constrained Budget Scenario")
      totalAnnualBudget = annualBudgetSettings["baseline_budget"] * (100 - annualBudgetSettings["constrained_reduction_pct"]) / 100
      st.write(f"Annual Budget: {totalAnnualBudget:,.0f} USD")
      detailedConstrainedBudgetPlan = detailedPlan.query("Scenario == 'Constrained Budget'")

      fundedPlans = detailedConstrainedBudgetPlan.query("Funded")
      annual_funded_costs_series = fundedPlans.groupby("Plan_Year")["Treatment_Cost"].sum()
      annual_funded_costs_list = annual_funded_costs_series.tolist()
      # calculate costs PV
      constrainedBudgetPv = calculate_pv(annual_funded_costs_list, DEFAULT_DISCOUNT_RATE)
      st.write(f"Total Costs PV: ${constrainedBudgetPv:,.0f} USD")
      remaining_budget = [totalAnnualBudget - cost for cost in annual_funded_costs_list]
      # calculate remaining budget PV
      remainingBudgetPv = calculate_pv(remaining_budget, DEFAULT_DISCOUNT_RATE)
      st.write(f"Remaining Budget PV: ${remainingBudgetPv:,.0f} USD")
      endOfProgramBridgeData = detailedConstrainedBudgetPlan.query(f"Plan_Year == {DEFAULT_HORIZON_YEARS}")
      average_bci = endOfProgramBridgeData["BCI_End_of_Year"].mean(skipna=True)
      st.write(f"Average Network BCI: {average_bci:,.0f} %")
      fig1 = plot_annual_costs_vs_budget(
        annual_funded_costs_list,
        totalAnnualBudget
      )
      st.pyplot(fig1, use_container_width=False)
      col11, col22 = st.columns([7, 3])
      with col11:
        fig2 = plot_condition_category_distribution_end_of_program(endOfProgramBridgeData, "Constrained Budget Network Condition")
        st.pyplot(fig2, use_container_width=False)
      with col22:
        st.markdown("""
          <div style="
              height: 400px;
              display: flex;
              align-items: center;
          ">
              <div style="
                  width: 100%;
                  background-color: #f8f9fa;
                  padding: 18px;
                  border-radius: 12px;
                  border-left: 5px solid #6c757d;
                  font-size: 12px;
                  line-height: 1.8;
              ">
                  <b>Condition Category Guide</b><br><br>
                  <span style="color:#198754;"><b>Good:</b></span> BCI ≥ 70<br>
                  <span style="color:#ffc107;"><b>Fair:</b></span> 50 ≤ BCI &lt; 70<br>
                  <span style="color:#dc3545;"><b>Poor:</b></span> BCI &lt; 50
              </div>
          </div>
        """, unsafe_allow_html=True)